#!/usr/bin/env python3
"""Tempo de contribuição: comum, especial convertido até 13/11/2019 e concomitância.

Conta aberta e CAMPOS: context/calculo-tempo.md. Convenção (IN 128, arts. 206,
207 e 265; parecer M1 do F1):

  F1  até 13/11/2019 .... dias de data a data, inclusivos; especial convertido
                          pelo multiplicador do Decreto 3.048, art. 188-P, §5º
  F2  competência 11/2019  integral (30 dias); acresce o que falta aos dias de
                          01 a 13/11 já contados em F1, sem conversão
  F3  desde 12/2019 ..... cada competência com salário >= mínimo vale 1 mês

Entrada JSON por --entrada ou stdin. Saída JSON no stdout.
Exit: 0 calculado · 2 entrada inválida · 3 competência 11/2019 só em parte ou total que muda com a
normalização das competências desde 12/2019 (devolve as duas contas e a fórmula aberta, sem escolher).
Só biblioteca padrão, sem rede.
"""

import argparse
import bisect
import datetime as dt
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

VERSAO = "2.0.3"
EXIT_OK, EXIT_ENTRADA, EXIT_FALTA = 0, 2, 3

MARCO_EC103 = dt.date(2019, 11, 13)
DATA_MINIMA, DATA_MAXIMA = dt.date(1900, 1, 1), dt.date(2100, 12, 31)
DIAS_ANO, DIAS_MES = 365, 30
TABELA_CONVERSAO = Path(__file__).resolve().parent.parent / "data" / "conversao-especial.json"

TIPOS = ("comum", "especial-15", "especial-20", "especial-25")
FONTES = ("CNIS", "CTPS", "sentenca", "PPP")
ANOS_ESPECIAL = {"especial-15": 15, "especial-20": 20, "especial-25": 25}

# Contrato da entrada (context/calculo-tempo.md, seção 5). As skills declaram o
# mesmo conteúdo no bloco ```campos```; tests/test_contrato_flags.py compara.
CAMPOS = {
    "sexo": {"tipo": "enum", "obrigatorio": "sim", "valores": ["M", "F"]},
    "periodos": {"tipo": "lista", "obrigatorio": "sim", "valores": "ao menos 1 periodo"},
    "periodos[].inicio": {"tipo": "data", "obrigatorio": "sim"},
    "periodos[].fim": {"tipo": "data", "obrigatorio": "sim"},
    "periodos[].tipo": {"tipo": "enum", "obrigatorio": "sim", "valores": list(TIPOS)},
    "periodos[].fonte": {"tipo": "enum", "obrigatorio": "sim", "valores": list(FONTES)},
    "periodos[].competencias_abaixo_do_minimo": {
        "tipo": "lista de competencia", "obrigatorio": "nao", "padrao": [],
        "valores": "so competencias de 11/2019 em diante"},
    "novembro_2019_integral": {
        "tipo": "bool", "obrigatorio": "condicional",
        "valores": "sim quando algum periodo abrange 13/11/2019 e continua depois; false leva a exit 3"},
}

FONTE_REGRAS = {
    "F1": "IN 128, art. 206, §§1º e 3º; EC 103, art. 25, §2º",
    "F2": "IN 128, art. 206, §§2º e 4º; art. 207, parágrafo único",
    "F3": "IN 128, art. 206, caput e §2º",
    "conversao": "Decreto 3.048, art. 188-P, §5º (context/lei/decreto-3048-art188p-tabela.md)",
    "representacao": "IN 128, art. 207, parágrafo único",
    "concomitancia_especial": "IN 128, art. 265",
    "concomitancia_comum": "IN 128, art. 206",
}


# r12 (revisão r11, BLOCKER 2: regime histórico). COBERTURA: intervalo em que a regra implementada é a vigente, com a
# fonte de cada borda (notas de redação de context/lei/). Este script não recebe a data do requerimento: a linha é
# verificada por quem usa o tempo convertido numa data (calc_previdenciario_transicao.py, pela DER), que abre a conta
# fora do intervalo. A conversão em si já é fatiada pela data do trabalho (só até 13/11/2019: EC 103, art. 25, §2º).
CONVERSAO_188P_DESDE = dt.date(2020, 6, 30)
COBERTURA = (
    {"id": "conversao-188P", "chave": "der", "fora": "aberta",
     "regra": "multiplicadores do Decreto 3.048, art. 188-P, §5º (2,00/2,33; 1,50/1,75; 1,20/1,40), ao trabalho "
              "prestado até 13/11/2019",
     "desde": CONVERSAO_188P_DESDE,
     "fonte_desde": "art. 188-P, §5º, incluído pelo Decreto 10.410, de 30/06/2020 "
                    "(decreto-3048-art188p-tabela.md:74-78)",
     "ate": None, "fonte_ate": "art. 188-P, §5º, em vigor (sem nota de alteração)",
     "historica": "requerimento anterior a 30/06/2020: multiplicadores do art. 70 do Decreto 3.048, revogado pelo "
                  "Decreto 10.410/2020 (decreto-3048-1999.md:1677), texto não capturado em context/lei/"},
)


class EntradaInvalida(Exception):
    pass


class TabelaIndisponivel(Exception):
    """Tabela de scripts/data/ ausente ou ilegível: falta de tabela é exit 3 com a conta aberta (DESIGN-SPEC §3.2),
    nunca entrada inválida."""

    def __init__(self, arquivo, err):
        super().__init__(f"{arquivo}: {type(err).__name__}")
        self.arquivo = arquivo


# ------------------------------------------------------------ utilidades

def dec(x):
    return x if isinstance(x, Decimal) else Decimal(str(x))


def txt(x):
    """Decimal em texto, sem zeros à direita inúteis ("2489.2", "1934")."""
    d = dec(x)
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


def num(x):
    """Inteiro quando inteiro; texto decimal quando há fração."""
    d = dec(x)
    return int(d) if d == d.to_integral_value() else txt(d)


def mes(d):
    return (d.year, d.month)


def mes_txt(m):
    return f"{m[0]:04d}-{m[1]:02d}"


def mes_seguinte(m):
    return (m[0] + (m[1] == 12), 1 if m[1] == 12 else m[1] + 1)


def primeiro_dia(m):
    return dt.date(m[0], m[1], 1)


def ultimo_dia(m):
    return primeiro_dia(mes_seguinte(m)) - dt.timedelta(days=1)


def representar(dias):
    """IN 128, art. 207, parágrafo único: ano de 365 dias, mês de 30."""
    d = dec(dias)
    anos = int(d // DIAS_ANO)
    resto = d - anos * DIAS_ANO
    meses = int(resto // DIAS_MES)
    sobra = resto - meses * DIAS_MES
    texto = f"{anos}a {meses}m {txt(sobra).replace('.', ',')}d"
    return {"anos": anos, "meses": meses, "dias": num(sobra), "texto": texto,
            "dias_totais": num(d), "representacao": "IN 128, art. 207"}


def f3_dias(n, normalizacao="padrao"):
    """Competências desde 12/2019 em dias. Padrão: 12 competências = 365 dias."""
    if normalizacao == "padrao":
        return (n // 12) * DIAS_ANO + (n % 12) * DIAS_MES
    return n * DIAS_MES


# ------------------------------------------------------------ validação

def _data(campo, v):
    if not isinstance(v, str):
        raise EntradaInvalida(f"{campo}: esperado texto AAAA-MM-DD")
    try:
        d = dt.date.fromisoformat(v)
    except ValueError:
        raise EntradaInvalida(f"{campo}: data inválida '{v}' (formato AAAA-MM-DD)")
    if not DATA_MINIMA <= d <= DATA_MAXIMA:
        raise EntradaInvalida(f"{campo}: fora do intervalo suportado ({DATA_MINIMA} a {DATA_MAXIMA})")
    return d


def _competencia(campo, v):
    if not isinstance(v, str) or len(v) != 7 or v[4] != "-":
        raise EntradaInvalida(f"{campo}: esperado texto AAAA-MM")
    try:
        m = (int(v[:4]), int(v[5:]))
    except ValueError:
        raise EntradaInvalida(f"{campo}: competência inválida '{v}'")
    if not 1 <= m[1] <= 12 or not 1900 <= m[0] <= 2100:
        raise EntradaInvalida(f"{campo}: competência inválida '{v}'")
    return m


def _sem_comentarios(obj):
    return {k: v for k, v in obj.items() if not (isinstance(k, str) and k.startswith("_"))}


def _chaves(obj, permitidas, onde):
    extras = sorted(set(obj) - set(permitidas))
    if extras:
        raise EntradaInvalida(f"{onde}: campo desconhecido {extras[0]!r}")


def _obrig(obj, campo, onde):
    if obj.get(campo) is None:
        raise EntradaInvalida(f"{onde}: campo obrigatório '{campo}' ausente ou null")
    return obj[campo]


def validar_periodos(lista, onde="periodos"):
    if not isinstance(lista, list) or not lista:
        raise EntradaInvalida(f"{onde}: esperada lista com ao menos 1 período")
    saida = []
    for i, p in enumerate(lista):
        rot = f"{onde}[{i}]"
        if not isinstance(p, dict):
            raise EntradaInvalida(f"{rot}: esperado objeto")
        p = _sem_comentarios(p)
        _chaves(p, ("inicio", "fim", "tipo", "fonte", "competencias_abaixo_do_minimo"), rot)
        ini = _data(f"{rot}.inicio", _obrig(p, "inicio", rot))
        fim = _data(f"{rot}.fim", _obrig(p, "fim", rot))
        if fim < ini:
            raise EntradaInvalida(f"{rot}: fim {fim} anterior ao início {ini}")
        tipo = _obrig(p, "tipo", rot)
        if tipo not in TIPOS:
            raise EntradaInvalida(f"{rot}.tipo: '{tipo}' fora de {list(TIPOS)}")
        fonte = _obrig(p, "fonte", rot)
        if fonte not in FONTES:
            raise EntradaInvalida(f"{rot}.fonte: '{fonte}' fora de {list(FONTES)}")
        abaixo = p.get("competencias_abaixo_do_minimo")
        abaixo = [] if abaixo is None else abaixo
        if not isinstance(abaixo, list):
            raise EntradaInvalida(f"{rot}.competencias_abaixo_do_minimo: esperada lista")
        meses_abaixo = set()
        for j, c in enumerate(abaixo):
            m = _competencia(f"{rot}.competencias_abaixo_do_minimo[{j}]", c)
            if m < (2019, 11):
                raise EntradaInvalida(
                    f"{rot}.competencias_abaixo_do_minimo[{j}]: só competências de 11/2019 em diante "
                    "(antes, o tempo é contado de data a data)")
            # r13 (revisão r12, MAJOR 2): competência fora do período é cronologia impossível, recusada.
            if not (mes(ini) <= m <= mes(fim)):
                raise EntradaInvalida(
                    f"{rot}.competencias_abaixo_do_minimo[{j}]: competência {m[1]:02d}/{m[0]} fora do período "
                    f"{ini} a {fim}")
            meses_abaixo.add(m)
        saida.append({"inicio": ini, "fim": fim, "tipo": tipo, "fonte": fonte, "abaixo": meses_abaixo})
    return saida


def validar(bruto):
    if not isinstance(bruto, dict):
        raise EntradaInvalida("entrada: esperado objeto JSON")
    e = _sem_comentarios(bruto)
    _chaves(e, ("sexo", "periodos", "novembro_2019_integral"), "entrada")
    sexo = _obrig(e, "sexo", "entrada")
    if sexo not in ("M", "F"):
        raise EntradaInvalida(f"sexo: '{sexo}' fora de ['M', 'F']")
    periodos = validar_periodos(_obrig(e, "periodos", "entrada"))
    nov = e.get("novembro_2019_integral")
    if nov is not None and not isinstance(nov, bool):
        raise EntradaInvalida("novembro_2019_integral: esperado true ou false")
    return {"sexo": sexo, "periodos": periodos, "novembro_2019_integral": nov}


# ------------------------------------------------------------ tabela

def carregar_multiplicadores(caminho=None):
    caminho = TABELA_CONVERSAO if caminho is None else caminho
    try:
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        mult = {}
        for linha in dados["linhas"]:
            tipo = f"especial-{linha['tempo_a_converter_anos']}"
            mult[tipo] = {"F": Decimal(linha["multiplicador"]["mulher"]),
                          "M": Decimal(linha["multiplicador"]["homem"])}
        if set(mult) != set(ANOS_ESPECIAL):
            raise KeyError("linhas incompletas")
        fonte = {"arquivo": "scripts/data/conversao-especial.json",
                 "data_captura": dados.get("data_captura"),
                 "norma": dados["fonte"][0]["norma"]}
    except (OSError, ValueError, KeyError, TypeError, IndexError, ArithmeticError) as err:
        raise TabelaIndisponivel("scripts/data/conversao-especial.json", err)
    return mult, fonte


def tabela_ausente(versao, err, parametros, expressao, instrucao, regra):
    """Saída de exit 3 quando falta a tabela: conta aberta, sem número (DESIGN-SPEC §3.2)."""
    return {"versao": versao, "parametros_usados": parametros, "regra": regra,
            "fonte": {"tabela_ausente": err.arquivo},
            "memoria": [f"Tabela {err.arquivo} indisponível ({err}): a conta não é fechada por script."],
            "alertas": [f"[VERIFICAR] Tabela {err.arquivo} ausente ou ilegível: a conta sai aberta, sem número."],
            "formula_aberta": {"expressao": expressao, "faltando": [err.arquivo], "instrucao": instrucao}}


# ------------------------------------------------------------ núcleo

def _classe_dia(tipos):
    """Tipo que vale num dia coberto por mais de um período (IN 128, art. 265)."""
    especiais = sorted(t for t in tipos if t != "comum")
    if not especiais:
        return "comum"
    # Mais de um especial no mesmo dia: o de menor tempo exigido (maior multiplicador).
    return especiais[0]


def _classe_dia_alt(tipos):
    """Leitura alternativa do dia com dois especiais: o de maior tempo exigido (menor multiplicador). A escolha
    entre eles é a da atividade preponderante (Decreto 3.048, art. 66), que a entrada não informa: as duas
    leituras saem e, se o total muda, a conta fica aberta."""
    especiais = sorted(t for t in tipos if t != "comum")
    return especiais[-1] if especiais else "comum"


class Apuracao:
    """Mapa diário dos períodos, para contar tempo em qualquer data de corte.

    Usado também por calc_previdenciario_transicao.py (mesma pasta), que importa
    este arquivo por caminho relativo.
    """

    def __init__(self, periodos, sexo, multiplicadores, classe=_classe_dia):
        self.periodos = periodos
        self.sexo = sexo
        self.mult = multiplicadores
        self.classe = classe   # tipo que vale no dia com 2+ períodos (_classe_dia ou _classe_dia_alt)
        self.dia = {}          # data -> set de tipos (só até 13/11/2019 e de 14 a 30/11/2019)
        self.meses_f3 = {}     # competência >= 12/2019 -> primeiro dia coberto
        self.meses_f3_tipos = {}
        # competência -> {tipo: primeiro dia coberto POR ESSE TIPO}. Cada tipo conta do seu próprio início
        # dentro da competência: o início de outro vínculo não antecipa a exposição (EC 103, art. 21; IN 128,
        # art. 265).
        self.meses_f3_por_tipo = {}
        self.f3_abaixo = []    # competências excluídas por salário abaixo do mínimo
        # As mesmas, quando 2+ vínculos cobrem o mês: o mínimo é conferido no somatório das remunerações do mês
        # (Decreto 3.048, art. 19-E, §1º; IN 128, art. 209, §1º), que a entrada não traz.
        self.f3_abaixo_concomitante = []
        self.nov_cobertos = set()   # dias de 14 a 30/11/2019 cobertos
        self.nov_validos = set()    # os mesmos dias, cobertos por vínculo sem 11/2019 abaixo do mínimo
        self.nov_abaixo = False     # 11/2019 abaixo do mínimo em TODOS os vínculos que a cobrem
        # O mesmo, com 2+ vínculos cobrindo 11/2019 depois de 13/11: o somatório do mês pode alcançar o mínimo
        # (Decreto 3.048, art. 19-E, §1º; IN 128, art. 209, §1º), como em F3.
        self.nov_abaixo_concomitante = False
        self.sobreposicao = {}      # data -> set de tipos, dias com 2+ períodos (até 13/11/2019)
        self.uniao_pos_ec = set()   # dias corridos depois de 13/11/2019 (dias trabalhados, informativo)
        # Os mesmos dias, só de vínculo com a competência válida (sensibilidade civil): competência abaixo do
        # mínimo não conta tempo (IN 128, art. 206, §2º).
        self.uniao_pos_ec_validos = set()
        self._montar()

    def _montar(self):
        contagem = {}
        f3_cobertura = {}
        nov_periodos = set()
        for p in self.periodos:
            d = p["inicio"]
            while d <= p["fim"]:
                if d <= MARCO_EC103:
                    self.dia.setdefault(d, set()).add(p["tipo"])
                    contagem[d] = contagem.get(d, 0) + 1
                else:
                    self.uniao_pos_ec.add(d)
                    if mes(d) not in p["abaixo"]:
                        self.uniao_pos_ec_validos.add(d)
                    if d.year == 2019 and d.month == 11:
                        self.nov_cobertos.add(d)
                        nov_periodos.add(id(p))
                        if (2019, 11) not in p["abaixo"]:
                            self.nov_validos.add(d)
                    else:
                        m = mes(d)
                        f3_cobertura.setdefault(m, []).append((d, p))
                d += dt.timedelta(days=1)
        # A competência abaixo do mínimo sai por vínculo, não para todos (IN 128, art. 206, §2º):
        # 11/2019 só deixa de acrescer se nenhum vínculo que a cobre depois de 13/11 a tem válida.
        self.nov_abaixo = bool(self.nov_cobertos) and not self.nov_validos
        self.nov_abaixo_concomitante = self.nov_abaixo and len(nov_periodos) > 1
        for d, n in contagem.items():
            if n > 1:
                self.sobreposicao[d] = self.dia[d]
        for m, itens in sorted(f3_cobertura.items()):
            periodos_do_mes = {id(p): p for _, p in itens}.values()
            # Fora só se todos os períodos que cobrem o mês declararam o mês abaixo do mínimo.
            if all(m in p["abaixo"] for p in periodos_do_mes):
                self.f3_abaixo.append(m)
                if len(periodos_do_mes) > 1:
                    self.f3_abaixo_concomitante.append(m)
                continue
            # Só os vínculos com a competência válida: o vínculo excluído por salário abaixo do mínimo não
            # antecipa o primeiro dia do mês nem empresta o seu tipo (IN 128, art. 206, §2º).
            por_tipo = {}
            for d, p in itens:
                if m not in p["abaixo"]:
                    por_tipo[p["tipo"]] = min(por_tipo.get(p["tipo"], d), d)
            self.meses_f3_por_tipo[m] = por_tipo
            self.meses_f3[m] = min(por_tipo.values())
            self.meses_f3_tipos[m] = set(por_tipo)
        self._dias_f1 = sorted(self.dia)

    # ---- F1
    def f1(self, ate=MARCO_EC103, so_tipo=None):
        """Dias de F1 até a data (inclusive), por tipo, e o total convertido."""
        limite = min(ate, MARCO_EC103)
        por_tipo = {}
        for d in self._dias_f1:
            if d > limite:
                break
            t = self.classe(self.dia[d])
            if so_tipo is not None and t != so_tipo:
                continue
            por_tipo[t] = por_tipo.get(t, 0) + 1
        convertido = Decimal(0)
        for t, n in por_tipo.items():
            convertido += n if t == "comum" else n * self.mult[t][self.sexo]
        return por_tipo, convertido

    # ---- F2
    def f2_contas(self, so_tipos=None):
        """As duas contas da competência 11/2019: data a data e competência integral."""
        f1_nov = sum(1 for d in self._dias_f1 if d.year == 2019 and d.month == 11
                     and (so_tipos is None or self.classe(self.dia[d]) in so_tipos))
        def do_tipo(dias, so_validos):
            if so_tipos is None and not so_validos:
                return dias
            return {d for d in dias if any(
                p["inicio"] <= d <= p["fim"] and (so_tipos is None or p["tipo"] in so_tipos)
                and not (so_validos and (2019, 11) in p["abaixo"]) for p in self.periodos)}
        cobertos = do_tipo(self.nov_cobertos, False)
        validos = do_tipo(self.nov_validos, True)
        return {"data_a_data": len(validos), "competencia_integral": DIAS_MES - f1_nov,
                "dias_01_a_13_em_f1": f1_nov, "tem_novembro_pos_ec": bool(cobertos),
                "tem_novembro_valido": bool(validos)}

    def f2(self, nov_integral, so_tipos=None):
        c = self.f2_contas(so_tipos)
        if not c["tem_novembro_valido"]:
            return 0
        return c["competencia_integral"] if nov_integral else c["data_a_data"]

    # ---- F3
    def meses_f3_ate(self, ate, so_tipos=None):
        """Competências desde 12/2019 até a competência de `ate` (inclusive), já iniciadas por vínculo válido."""
        idx = IndicePosEC(self, False, so_tipos)
        return [m for m, primeiro in zip(idx.chaves, idx.primeiros) if m <= mes(ate) and primeiro <= ate]

    def indice(self, nov_integral, so_tipos=None):
        """Índice do tempo depois de 13/11/2019 numa data qualquer (ver IndicePosEC)."""
        return IndicePosEC(self, nov_integral, so_tipos)

    def abrange_marco_e_continua(self):
        return any(p["inicio"] <= MARCO_EC103 < p["fim"] for p in self.periodos)

    def tem_pos_ec(self):
        return bool(self.uniao_pos_ec)

    def civil_pos_ec(self, ate):
        return sum(1 for d in self.uniao_pos_ec_validos if d <= ate)


class IndicePosEC:
    """Tempo depois de 13/11/2019 apurado ATÉ uma data, por tipo de atividade e só com vínculos válidos.

    É a única conta do F2 e do F3 numa data de corte; calc_previdenciario_transicao.py a consome para o tempo e
    para a exposição especial. Três invariantes (testados por propriedade):
      - nada depois da data apurada entra (período futuro não muda o resultado na data);
      - vínculo com a competência abaixo do mínimo não conta nem antecipa o início do mês (IN 128, art. 206, §2º);
      - a exposição de um tipo só olha os períodos desse tipo (EC 103, art. 21: exposição efetiva; IN 128,
        art. 265): o início de um vínculo comum nunca a muda.
    F2: a competência 11/2019 integral (declarada) vale para o conjunto de tipos que tem período válido abrangendo
    13/11/2019 e continuando, desde o primeiro dia válido de 14 a 30/11; o tipo que só começa depois conta data a
    data, até a data apurada. F3: a competência conta quando o primeiro dia válido do tipo nela já passou.
    """

    def __init__(self, ap, nov_integral, so_tipos=None):
        tipos = None if so_tipos is None else set(so_tipos)

        def vale(p):
            return (tipos is None or p["tipo"] in tipos) and (2019, 11) not in p["abaixo"]

        self.f2_dias = sorted(d for d in ap.nov_validos
                              if any(vale(p) and p["inicio"] <= d <= p["fim"] for p in ap.periodos))
        cruza = any(vale(p) and p["inicio"] <= MARCO_EC103 < p["fim"] for p in ap.periodos)
        self.f2_integral = None
        if self.f2_dias and nov_integral and (tipos is None or cruza):
            self.f2_integral = ap.f2_contas(so_tipos)["competencia_integral"]
        itens = []
        for m, por in sorted(ap.meses_f3_por_tipo.items()):
            primeiros = [d for t, d in por.items() if tipos is None or t in tipos]
            if primeiros:
                itens.append((m, min(primeiros)))
        self.chaves = [m for m, _ in itens]
        self.primeiros = [d for _, d in itens]

    def f2_em(self, d):
        """Dias da competência 11/2019 (14 a 30/11) contados até d."""
        if d <= MARCO_EC103 or not self.f2_dias or self.f2_dias[0] > d:
            return 0
        if self.f2_integral is not None:
            return self.f2_integral
        return bisect.bisect_right(self.f2_dias, d)

    def n_f3_em(self, d):
        """Competências desde 12/2019 já iniciadas (por vínculo válido do tipo) até d (IN 128, art. 206)."""
        if d <= MARCO_EC103:
            return 0
        i = bisect.bisect_left(self.chaves, mes(d))
        if i < len(self.chaves) and self.chaves[i] == mes(d) and self.primeiros[i] <= d:
            i += 1
        return i

    def pos_em(self, d, norm="padrao"):
        """F2 + F3 em dias até d."""
        return self.f2_em(d) + f3_dias(self.n_f3_em(d), norm)


def calcular(bruto, multiplicadores=None):
    try:
        e = validar(bruto)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}
    if multiplicadores is None:
        try:
            mult, fonte_tab = carregar_multiplicadores()
        except TabelaIndisponivel as err:
            parametros = {"sexo": e["sexo"], "novembro_2019_integral": e["novembro_2019_integral"],
                          "periodos": [{"inicio": p["inicio"].isoformat(), "fim": p["fim"].isoformat(),
                                        "tipo": p["tipo"], "fonte": p["fonte"],
                                        "competencias_abaixo_do_minimo": sorted(mes_txt(m) for m in p["abaixo"])}
                                       for p in e["periodos"]]}
            return EXIT_FALTA, tabela_ausente(
                VERSAO, err, parametros,
                "total = F1 (dias comuns + Σ dias especiais × multiplicador do Decreto 3.048, art. 188-P, §5º) + "
                "F2 + F3 (IN 128, arts. 206 e 207)",
                "Conta não conferida por script: aplique os multiplicadores do context/lei/decreto-3048-art188p-"
                "tabela.md e some à mão (context/calculo-tempo.md, seção 3).",
                "Tempo em três fatias (IN 128, art. 206); sem a tabela de conversão, a conta fica aberta.")
    else:
        mult, fonte_tab = multiplicadores
    codigo, saida, n_comp = _apurar(e, mult, fonte_tab)
    if n_comp < 12:
        # Menos de 12 competências desde 12/2019 (somadas as do somatório aberto): as duas normalizações são a
        # mesma conta (f3_dias idêntica para n < 12).
        return codigo, saida
    _, alt, _ = _apurar(e, mult, fonte_tab, "30d")
    return _sensibilidade_normalizacao(codigo, saida, alt)


def _apurar(e, mult, fonte_tab, norma="padrao"):
    """Conta inteira com `norma` para as competências desde 12/2019 (padrão: 12 = 365 dias; "30d": 30 por
    competência). Devolve (exit, saída, competências que podem entrar na F3 até a data máxima)."""
    ap = Apuracao(e["periodos"], e["sexo"], mult)
    alertas, memoria = [], []
    nov = e["novembro_2019_integral"]
    nov_contas = ap.f2_contas()
    if nov_contas["tem_novembro_pos_ec"] and nov is None and ap.abrange_marco_e_continua():
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "versao": VERSAO,
                              "detalhe": "novembro_2019_integral: obrigatório quando um período "
                                         "abrange 13/11/2019 e continua depois"}, 0

    # F1
    por_tipo, convertido = ap.f1()
    f1_bruto = sum(por_tipo.values())
    linhas_f1 = []
    for t in TIPOS:
        if t not in por_tipo:
            continue
        m = Decimal(1) if t == "comum" else mult[t][e["sexo"]]
        linhas_f1.append({"tipo": t, "dias": por_tipo[t], "multiplicador": str(m.quantize(Decimal("0.01"))),
                          "convertido_dias": num(por_tipo[t] * m)})
        memoria.append(f"F1 {t}: {por_tipo[t]} dias × {txt(m)} = {txt(por_tipo[t] * m)} dias "
                       f"({FONTE_REGRAS['conversao'] if t != 'comum' else FONTE_REGRAS['F1']})")
    especiais_f1 = [l for l in linhas_f1 if l["tipo"] != "comum"]
    fatias = []
    if f1_bruto:
        fatia1 = {"fatia": "F1", "ate": "2019-11-13", "dias": f1_bruto,
                  "convertido_dias": num(convertido), "por_tipo": linhas_f1,
                  "fundamento": FONTE_REGRAS["F1"]}
        if len(linhas_f1) == 1 and especiais_f1:
            fatia1["multiplicador"] = especiais_f1[0]["multiplicador"]
        fatias.append(fatia1)

    # F2
    codigo = EXIT_OK
    formula_aberta = None
    f2 = 0
    if nov_contas["tem_novembro_pos_ec"]:
        if not ap.nov_abaixo and any((2019, 11) in p["abaixo"] for p in e["periodos"]):
            memoria.append("Competência 11/2019 abaixo do mínimo em parte dos vínculos: sai só desses; o vínculo "
                           "válido mantém a competência (IN 128, art. 206, §2º).")
        if ap.nov_abaixo:
            alertas.append("Competência 11/2019 declarada abaixo do mínimo: não acresce dias (IN 128, art. 206, §2º).")
        elif nov is True:
            f2 = nov_contas["competencia_integral"]
        else:
            codigo = EXIT_FALTA
            f2 = None
            alertas.append("[VERIFICAR] Competência 11/2019 trabalhada só em parte: a IN 128 (art. 206, "
                           "§§1º e 2º) não diz como juntar a contagem data a data até 13/11 com a "
                           "competência integral. Saem as duas contas; o advogado escolhe.")
            formula_aberta = {
                "expressao": "total = F1_convertido + F2 + F3, com F2 = dias trabalhados de 14 a 30/11/2019 "
                             "(data a data) OU 30 - dias de 01 a 13/11 já em F1 (competência integral)",
                "contas_novembro_2019": {"data_a_data": nov_contas["data_a_data"],
                                         "competencia_integral": nov_contas["competencia_integral"]},
                "faltando": ["critério para a competência 11/2019 trabalhada só em parte (item I-5)"],
                "instrucao": "Conta não conferida por script: escolha a leitura e some à mão "
                             "(context/calculo-tempo.md, seção 3).",
            }
        fatias.append({"fatia": "F2", "competencia": "2019-11", "dias_acrescidos": f2,
                       "conversao": False, "fundamento": FONTE_REGRAS["F2"]})
        if f2 is not None:
            memoria.append(f"F2 competência 11/2019 integral: 30 - {nov_contas['dias_01_a_13_em_f1']} "
                           f"dias de 01 a 13/11 já em F1 = {f2} dias, sem conversão ({FONTE_REGRAS['F2']})")

    # F3
    meses3 = ap.meses_f3_ate(DATA_MAXIMA)
    n3 = len(meses3)
    if meses3:
        fatias.append({"fatia": "F3", "competencias": f"{mes_txt(meses3[0])}..{mes_txt(meses3[-1])}",
                       "meses": n3, "conversao": False, "fundamento": FONTE_REGRAS["F3"]})
        memoria.append(f"F3: {n3} competências desde 12/2019 com salário igual ou superior ao mínimo "
                       f"({FONTE_REGRAS['F3']})")
    if ap.f3_abaixo:
        alertas.append("Competências fora por salário abaixo do mínimo: "
                       + ", ".join(mes_txt(m) for m in ap.f3_abaixo) + " (IN 128, art. 206, §2º).")

    # Concomitância
    conc = None
    if ap.sobreposicao:
        dias_sob = sorted(ap.sobreposicao)
        classes = {_classe_dia(ap.sobreposicao[d]) for d in dias_sob}
        com_especial = any(t != "comum" for t in classes)
        intervalos, ini, ant = [], dias_sob[0], dias_sob[0]
        for d in dias_sob[1:] + [None]:
            if d is None or d - ant > dt.timedelta(days=1) or _classe_dia(ap.sobreposicao[d]) != _classe_dia(ap.sobreposicao[ant]):
                intervalos.append({"inicio": ini.isoformat(), "fim": ant.isoformat(),
                                   "dias": (ant - ini).days + 1,
                                   "contado_como": _classe_dia(ap.sobreposicao[ant])})
                if d is not None:
                    ini = d
            if d is not None:
                ant = d
        conc = {"dias": len(dias_sob), "dias_descontados": len(dias_sob),
                "periodo": "; ".join(f"{dt.date.fromisoformat(x['inicio']).strftime('%d/%m/%Y')} a "
                                     f"{dt.date.fromisoformat(x['fim']).strftime('%d/%m/%Y')}" for x in intervalos),
                "contado_como": classes.pop() if len(classes) == 1 else "misto",
                "fundamento": FONTE_REGRAS["concomitancia_especial" if com_especial else "concomitancia_comum"],
                "intervalos": intervalos}
        memoria.append(f"Concomitância: {len(dias_sob)} dias em mais de um período, contados uma vez"
                       + (" como especial (IN 128, art. 265)" if com_especial else " (IN 128, art. 206)"))
    dois_especiais = sorted(d for d, ts in ap.sobreposicao.items() if len([t for t in ts if t != "comum"]) > 1)
    convertido_alt = None
    if dois_especiais:
        # Regra 2 ("na dúvida, fórmula aberta"): no dia com dois especiais, qual deles vale é a atividade
        # preponderante (Decreto 3.048, art. 66), dado que a entrada não traz. Saem as duas leituras.
        _, convertido_alt = Apuracao(e["periodos"], e["sexo"], mult, classe=_classe_dia_alt).f1()
        alertas.append("[VERIFICAR] Dois tipos de especial no mesmo dia (" + _faixa_txt(dois_especiais) + "): "
                       "qual vale é a atividade preponderante (Decreto 3.048, art. 66), que a entrada não informa. "
                       f"F1 convertido: {txt(convertido)} dias (o de menor tempo exigido) × {txt(convertido_alt)} "
                       "dias (o de maior tempo exigido).")

    tempo_comum = por_tipo.get("comum", 0)
    pos_ec = (f2 or 0) + f3_dias(n3, norma)
    especial_bruto = sum(n for t, n in por_tipo.items() if t != "comum")
    especial_conv = sum((n * mult[t][e["sexo"]] for t, n in por_tipo.items() if t != "comum"), Decimal(0))

    saida = {
        "versao": VERSAO,
        "parametros_usados": {"sexo": e["sexo"], "novembro_2019_integral": nov,
                              "periodos": [{"inicio": p["inicio"].isoformat(), "fim": p["fim"].isoformat(),
                                            "tipo": p["tipo"], "fonte": p["fonte"],
                                            "competencias_abaixo_do_minimo": sorted(mes_txt(m) for m in p["abaixo"])}
                                           for p in e["periodos"]],
                              "convencao": "IN 128, arts. 206 e 207 (M1): data a data até 13/11/2019; "
                                           "11/2019 integral; competências integrais desde 12/2019; 365/30"},
        "fatias": fatias,
        "tempo_comum": representar(tempo_comum),
        "tempo_pos_ec_sem_conversao": representar(pos_ec),
        "tempo_especial_bruto": representar(especial_bruto),
        "tempo_especial_convertido": representar(especial_conv),
        "convertido_dias": num(especial_conv),
        "convertido": _parcela_convertida(ap, especial_bruto, especial_conv, especiais_f1),
        "sem_conversao": _parcela_sem_conversao(ap),
        "comum_adicional_dias": tempo_comum,
        "representacao": "IN 128, art. 207",
        "concomitancia": conc,
        "regra": "Tempo em três fatias (IN 128, art. 206): F1 data a data até 13/11/2019 com conversão; "
                 "F2 competência 11/2019 integral; F3 competências desde 12/2019; representação 365/30.",
        "fonte": {"fatias": FONTE_REGRAS, "tabela": fonte_tab},
        "cobertura": [{k: (v.isoformat() if isinstance(v, dt.date) else v) for k, v in l.items()} for l in COBERTURA],
        "alertas": alertas,
        "memoria": memoria,
        "formula_aberta": formula_aberta,
    }

    if f2 is None:
        # Exit 3: total nas duas leituras da competência 11/2019, sem escolher.
        totais = {}
        for nome, v in (("data_a_data", nov_contas["data_a_data"]),
                        ("competencia_integral", nov_contas["competencia_integral"])):
            totais[nome] = representar(convertido + v + f3_dias(n3, norma))
        saida["total_por_leitura_novembro_2019"] = totais
        if convertido_alt is not None and convertido_alt != convertido:
            saida["formula_aberta"]["faltando"].append(
                "atividade preponderante nos dias com dois especiais (Decreto 3.048, art. 66): F1 convertido "
                f"{txt(convertido)} × {txt(convertido_alt)} dias")
        saida["dias"] = None
        saida["total_dias"] = None
        saida["tempo_total"] = None
        return codigo, saida, n3 + len(ap.f3_abaixo_concomitante)

    total = convertido + f2 + f3_dias(n3, norma)
    saida["dias"] = num(total)
    saida["total_dias"] = num(total)
    saida["tempo_total"] = representar(total)
    saida["tempo_total"]["f1_f2_dias"] = num(convertido + f2)
    saida["tempo_total"]["f3_competencias"] = n3
    memoria.append(f"Total: {txt(convertido)} (F1 convertido) + {f2} (F2) + {f3_dias(n3, norma)} (F3, padrão) "
                   f"= {txt(total)} dias = {saida['tempo_total']['texto']} ({FONTE_REGRAS['representacao']})")

    saida["normalizacao"] = None
    saida["leituras"] = None
    saida["sensibilidade_normalizacao_30d_dias"] = None
    # As duas normalizações valem também quando só há competências: o anexo só exclui o caso em que todo o tempo
    # é anterior a 13/11/2019 (context/calculo-tempo.md, seção 3). 12 competências = 365 × 360 dias.
    if n3:
        alt = convertido + f2 + f3_dias(n3, "30d")
        saida["normalizacao"] = "12 competências = 365 dias (padrão)"
        saida["leituras"] = {
            "padrao_12_competencias_365": {
                "regra": "⌊n/12⌋ × 365 + (n mod 12) × 30 (IN 128, art. 207, parágrafo único: ano de 365 dias, "
                         "composto pelos 12 meses)",
                "fatias": fatias, "f3_dias": f3_dias(n3), "total_dias": num(total),
                "tempo_total": representar(total)["texto"], "normalizacao": saida["normalizacao"]},
            "alternativa_30d_por_competencia": {
                "regra": "n × 30", "f3_dias": f3_dias(n3, "30d"), "total_dias": num(alt),
                "tempo_total": representar(alt)["texto"]},
        }
        if alt != total:
            saida["sensibilidade_normalizacao_30d_dias"] = num(alt)
            alertas.append(f"[VERIFICAR] Normalização das {n3} competências desde 12/2019: padrão "
                           f"{f3_dias(n3)} dias (12 = 365); alternativa {f3_dias(n3, '30d')} dias (30 por "
                           "competência). A IN 128 não decide; o tempo total muda "
                           f"({txt(total)} × {txt(alt)} dias).")
            # O total não fecha numa leitura só (IN 128, art. 207, não decide a soma de dias com competências):
            # exit 3 com as duas contas, sem escolher (BUILD-CONTRACT do W0-golden; regra "na dúvida, fórmula
            # aberta"). O total padrão continua em `leituras` e em `tempo_total`, rotulado como uma das leituras.
            codigo = EXIT_FALTA
            saida["formula_aberta"] = {
                "expressao": "total = F1_convertido + F2 + F3, com F3 = ⌊n/12⌋ × 365 + (n mod 12) × 30 (padrão) "
                             "OU n × 30 (alternativa)",
                "contas": {"f1_f2_dias": num(convertido + f2), "f3_competencias": n3,
                           "total_padrao_dias": num(total), "total_alternativa_30d_dias": num(alt)},
                "faltando": ["operação que junta os dias de F1/F2 com as competências de F3 (IN 128, art. 207; "
                             "context/calculo-tempo.md, seção 3)"],
                "instrucao": "Conta não conferida por script: escolha a normalização e use o total dela "
                             "(context/calculo-tempo.md, seção 3).",
            }
    if convertido_alt is not None and convertido_alt != convertido:
        codigo = EXIT_FALTA
        aberta = saida["formula_aberta"] or {}
        aberta["dois_especiais_no_mesmo_dia"] = {
            "expressao": "F1_convertido = Σ dias × multiplicador do tipo que vale no dia; com dois especiais no "
                         "mesmo dia, vale o da atividade preponderante (Decreto 3.048, art. 66)",
            "contas": {"f1_convertido_menor_tempo_exigido": num(convertido),
                       "f1_convertido_maior_tempo_exigido": num(convertido_alt),
                       "total_menor_tempo_exigido_dias": num(total),
                       "total_maior_tempo_exigido_dias": num(convertido_alt + f2 + f3_dias(n3, norma))},
            "dias": _faixa_txt(dois_especiais),
            "faltando": ["atividade preponderante nos dias com dois especiais (Decreto 3.048, art. 66)"],
            "instrucao": "Conta não conferida por script: escolha o tipo preponderante e refaça o F1 "
                         "(context/calculo-tempo.md).",
        }
        saida["formula_aberta"] = aberta
    if ap.f3_abaixo_concomitante:
        # Regra 2: o mês declarado abaixo do mínimo em cada um de 2+ vínculos concomitantes pode alcançar o mínimo
        # no somatório das remunerações (Decreto 3.048, art. 19-E, §1º; IN 128, art. 209, §1º).
        k = len(ap.f3_abaixo_concomitante)
        com = convertido + f2 + f3_dias(n3 + k, norma)
        codigo = EXIT_FALTA
        alertas.append("[VERIFICAR] Competências declaradas abaixo do mínimo em cada um de dois ou mais vínculos "
                       "concomitantes (" + ", ".join(mes_txt(m) for m in ap.f3_abaixo_concomitante) + "): o mínimo "
                       "é conferido no somatório das remunerações do mês (Decreto 3.048, art. 19-E, §1º; IN 128, "
                       "art. 209, §1º), que a entrada não traz.")
        aberta = saida["formula_aberta"] or {}
        aberta["somatorio_concomitante"] = {
            "expressao": "competência conta se a soma das remunerações do mês em todos os vínculos >= mínimo",
            "contas": {"competencias": [mes_txt(m) for m in ap.f3_abaixo_concomitante],
                       "total_sem_elas_dias": num(total), "total_com_elas_dias": num(com)},
            "faltando": ["somatório das remunerações do mês nos vínculos concomitantes"],
            "instrucao": "Some as remunerações de cada mês listado; se alcançam o mínimo, retire o mês de "
                         "competencias_abaixo_do_minimo (context/calculo-tempo.md, seção 3).",
        }
        saida["formula_aberta"] = aberta
    if ap.nov_abaixo_concomitante:
        # Regra 2 (revisão r7, MAJOR 3): 11/2019 abaixo do mínimo em cada um de 2+ vínculos concomitantes. O
        # somatório das remunerações do mês pode alcançar o mínimo (Decreto 3.048, art. 19-E, §1º; IN 128, art.
        # 209, §1º); sem os valores, F2 fica entre 0 e o que a competência acresceria, e o total entre os dois.
        f2_com = nov_contas["competencia_integral"] if nov is True else len(ap.nov_cobertos)
        sem = convertido + f3_dias(n3, norma)
        com = sem + f2_com
        codigo = EXIT_FALTA
        alertas.append("[VERIFICAR] Competência 11/2019 declarada abaixo do mínimo em cada um dos vínculos "
                       "concomitantes: o mínimo é conferido no somatório das remunerações do mês (Decreto 3.048, "
                       f"art. 19-E, §1º; IN 128, art. 209, §1º), que a entrada não traz. Total entre {txt(sem)} e "
                       f"{txt(com)} dias.")
        aberta = saida["formula_aberta"] or {}
        aberta["somatorio_concomitante_novembro_2019"] = {
            "expressao": "F2 conta se a soma das remunerações de 11/2019 em todos os vínculos >= mínimo; "
                         "total = F1_convertido + F2 + F3",
            "contas": {"competencia": "2019-11", "f2_sem_ela_dias": 0, "f2_com_ela_dias": f2_com,
                       "total_sem_ela_dias": num(sem), "total_com_ela_dias": num(com)},
            "faltando": ["somatório das remunerações de 11/2019 nos vínculos concomitantes"],
            "instrucao": "Some as remunerações de 11/2019; se alcançam o mínimo, retire 2019-11 de "
                         "competencias_abaixo_do_minimo (context/calculo-tempo.md, seção 3).",
        }
        saida["formula_aberta"] = aberta
    saida["sensibilidade_civil_dias"] = None
    if ap.tem_pos_ec():
        civil = convertido + ap.civil_pos_ec(DATA_MAXIMA)
        if civil != total:
            saida["sensibilidade_civil_dias"] = num(civil)
            memoria.append(f"Sensibilidade civil (não é a saída): F1 convertido + {ap.civil_pos_ec(DATA_MAXIMA)} "
                           f"dias corridos depois de 13/11/2019 = {txt(civil)} dias")
    return codigo, saida, n3 + len(ap.f3_abaixo_concomitante)


# r11: o que a conta fecha. Fora ficam os textos (fundamento, regra, instrução) e os campos que só exibem as duas
# normalizações lado a lado, refeitos pela leitura alternativa.
SO_TEXTO = frozenset({"alertas", "memoria", "regra", "fonte", "fundamento", "motivo", "formula", "coeficiente_regra",
                      "metodologia", "tempo_no_calculo", "faltando", "instrucao", "expressao", "legenda", "aviso",
                      "convencao", "representacao", "texto"})
_SO_EXIBICAO = frozenset({"leituras", "normalizacao", "sensibilidade_normalizacao_30d_dias"})


def projecao_da_conta(v, excluir):
    """Valores da saída (números, datas, vereditos), sem as chaves em `excluir`, em qualquer nível."""
    if isinstance(v, dict):
        return {k: projecao_da_conta(x, excluir) for k, x in v.items() if k not in excluir}
    if isinstance(v, list):
        return [projecao_da_conta(x, excluir) for x in v]
    return v


def diferencas(a, b, caminho=""):
    """Caminhos em que duas projeções divergem."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diferencas(a.get(k), b.get(k), f"{caminho}.{k}" if caminho else k)
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diferencas(x, y, f"{caminho}[{i}]")
        return out
    return [] if a == b else [caminho or "."]


def _sensibilidade_normalizacao(codigo, saida, alt):
    """r11, mesma regra do CNIS na r10: a saída inteira refeita com 30 dias por competência desde 12/2019 é
    comparada à padrão (12 = 365 dias) em todos os valores; qualquer diferença dá exit 3 com as duas leituras."""
    excluir = SO_TEXTO | _SO_EXIBICAO
    proj_p, proj_30 = projecao_da_conta(saida, excluir), projecao_da_conta(alt, excluir)
    dif = diferencas(proj_p, proj_30)
    if not dif:
        return codigo, saida
    saida["alertas"].append("[VERIFICAR] Normalização das competências desde 12/2019: refeita a conta inteira com "
                            "30 dias por competência, o resultado muda (" + ", ".join(dif[:12])
                            + (", …" if len(dif) > 12 else "") + "). As duas leituras saem em "
                            "formula_aberta.saida_depende_da_normalizacao.")
    aberta = saida["formula_aberta"] or {}
    aberta["saida_depende_da_normalizacao"] = {
        "expressao": "competências desde 12/2019 em dias: ⌊n/12⌋ × 365 + (n mod 12) × 30 (padrão) OU n × 30, "
                     "aplicada à conta inteira",
        "diferencas": dif,
        "leituras": {"padrao_12_competencias_365": proj_p, "alternativa_30d_por_competencia": proj_30},
        "faltando": ["operação que junta dias e competências (IN 128, art. 207; context/calculo-tempo.md, seção 3)"],
        "instrucao": "Conta não conferida por script: escolha a normalização e use a leitura dela "
                     "(context/calculo-tempo.md, seção 3)."}
    saida["formula_aberta"] = aberta
    return EXIT_FALTA, saida


def _faixa_txt(dias):
    """Datas em faixas contínuas, em texto ("01/01/2010 a 31/12/2010; ...")."""
    faixas, ini, ant = [], dias[0], dias[0]
    for d in dias[1:] + [None]:
        if d is None or d - ant > dt.timedelta(days=1):
            faixas.append(f"{ini.strftime('%d/%m/%Y')} a {ant.strftime('%d/%m/%Y')}")
            ini = d
        ant = d if d is not None else ant
    return "; ".join(faixas)


def _faixa(dias):
    if not dias:
        return {}
    if len(dias) == 1:
        return {"data": dias[0].isoformat()}
    return {"inicio": dias[0].isoformat(), "fim": dias[-1].isoformat()}


def _parcela_convertida(ap, bruto, convertido, especiais_f1):
    """Parte especial de F1 (até 13/11/2019), a única que se converte."""
    dias = [d for d in ap._dias_f1 if _classe_dia(ap.dia[d]) != "comum"]
    item = {"texto": representar(convertido)["texto"], "dias": bruto, "convertido_dias": num(convertido),
            "fundamento": FONTE_REGRAS["conversao"]}
    if len(especiais_f1) == 1:
        item["multiplicador"] = especiais_f1[0]["multiplicador"]
    item.update(_faixa(dias))
    return item


def _parcela_sem_conversao(ap):
    """Dias trabalhados depois de 13/11/2019, data a data: nunca se convertem (EC 103, art. 25, §2º)."""
    dias = sorted(ap.uniao_pos_ec)
    item = {"dias": len(dias), "fundamento": "EC 103, art. 25, §2º; IN 128, art. 206, §4º"}
    item.update(_faixa(dias))
    return item


# ------------------------------------------------------------ CLI

def build_parser():
    ap = argparse.ArgumentParser(
        prog="calc_previdenciario_tempo.py",
        description="Tempo de contribuição (comum, especial convertido até 13/11/2019, concomitância). "
                    "Entrada JSON por --entrada ou stdin; campos em context/calculo-tempo.md.")
    ap.add_argument("--entrada", help="arquivo JSON de entrada (sem ele, lê o stdin)")
    ap.add_argument("--versao", action="version", version=VERSAO, help="mostra a versão e sai")
    return ap


def _executar(args):
    try:
        texto = Path(args.entrada).read_text(encoding="utf-8") if args.entrada else sys.stdin.read()
        bruto = json.loads(texto)
    except (OSError, ValueError, RecursionError) as err:
        # ValueError cobre o JSON malformado, o arquivo binário ou fora do UTF-8 (UnicodeDecodeError) e o
        # inteiro gigante; RecursionError, o aninhamento patológico. Tudo é entrada inválida: exit 2.
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": f"JSON ilegível: "
                              f"{type(err).__name__}: {err}"[:500], "versao": VERSAO}
    return calcular(bruto)


def _emitir(codigo, saida):
    """Emite em ASCII (ensure_ascii=True): surrogate solto vindo da entrada não derruba a saída."""
    try:
        texto = json.dumps(saida, ensure_ascii=True, indent=2)
    except Exception as err:   # saída não serializável: vira erro íntegro, nunca traceback
        codigo = EXIT_ENTRADA
        saida = {"erro": "entrada_invalida", "versao": VERSAO,
                 "detalhe": f"saída não serializável: {type(err).__name__}"}
        texto = json.dumps(saida, ensure_ascii=True, indent=2)
    try:
        sys.stdout.write(texto + "\n")
        sys.stdout.flush()
        if codigo == EXIT_ENTRADA:
            detalhe = str(saida.get("detalhe", "")).encode("ascii", "backslashreplace").decode("ascii")
            sys.stderr.write(f"entrada invalida: {detalhe}\n")
    except Exception:
        pass
    return codigo


def main(argv=None):
    # Proteção total: argumentos, leitura, validação, cálculo e emissão. Tabela ausente é exit 3 com a conta
    # aberta; qualquer outra exceção não prevista é exit 2 com JSON de erro, nunca exit 1 com traceback.
    try:
        args = build_parser().parse_args(argv)
        codigo, saida = _executar(args)
    except TabelaIndisponivel as err:
        codigo, saida = EXIT_FALTA, tabela_ausente(
            VERSAO, err, None, "total = F1 convertido + F2 + F3 (IN 128, arts. 206 e 207)",
            "Conta não conferida por script (context/calculo-tempo.md, seção 3).",
            "Sem a tabela, a conta fica aberta.")
    except Exception as err:
        try:
            msg = f"{type(err).__name__}: {err}"
        except Exception:
            msg = type(err).__name__
        codigo, saida = EXIT_ENTRADA, {"erro": "entrada_invalida", "versao": VERSAO,
                                       "detalhe": f"falha não prevista ao processar a entrada ({msg})"[:500]}
    return _emitir(codigo, saida)


if __name__ == "__main__":
    sys.exit(main())
