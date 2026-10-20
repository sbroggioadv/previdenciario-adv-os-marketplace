#!/usr/bin/env python3
"""CNIS: carência, qualidade de segurado e indicadores.

Conta aberta e CAMPOS: context/calculo-cnis.md. Regras:
  carência ........ Lei 8.213, arts. 24 a 27-A (atraso: art. 27, II; após a perda: art. 27-A);
                    recolhimento posterior ao fato gerador: IN PRES/INSS 128, art. 189, §§4º e 5º
  qualidade ....... Lei 8.213, art. 15; Decreto 3.048, art. 14; Lei 8.212, art. 30, II e §2º, I
  indicadores ..... Portaria DIRBEN/INSS 990/2022, Anexo V (scripts/data/indicadores-cnis.json)

Entrada JSON por --entrada ou stdin. Saída JSON no stdout.
Exit: 0 calculado · 2 entrada inválida · 3 carência indeterminada ou regra fora da COBERTURA (devolve a fórmula
aberta com a regra histórica e a fonte).
Só biblioteca padrão, sem rede.
"""

import argparse
import datetime as dt
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSAO = "2.0.0"
EXIT_OK, EXIT_ENTRADA, EXIT_FALTA = 0, 2, 3

AQUI = Path(__file__).resolve().parent
TABELA_INDICADORES = AQUI.parent / "data" / "indicadores-cnis.json"
TABELA_SALARIO_MINIMO = AQUI.parent / "data" / "salario-minimo.json"
TABELA_FERIADOS = AQUI / "data" / "feriados-nacionais.json"   # tabela do motor de prazos (Engine B)
DATA_MINIMA, DATA_MAXIMA = dt.date(1900, 1, 1), dt.date(2100, 12, 31)

BENEFICIOS = ("idade", "tempo", "especial", "incapacidade", "salario-maternidade", "auxilio-reclusao",
              "pensao", "auxilio-acidente", "bpc")
ORIGENS = ("empregado", "contribuinte-individual", "facultativo", "especial", "domestico", "avulso")
ORIGENS_ATRASO = ("contribuinte-individual", "facultativo", "especial")   # Lei 8.213, art. 27, II
BENEFICIOS_27A = ("incapacidade", "salario-maternidade", "auxilio-reclusao")
APOSENTADORIAS = ("idade", "tempo", "especial")

CAMPOS = {
    "beneficio": {"tipo": "enum", "obrigatorio": "sim", "valores": list(BENEFICIOS)},
    "data_referencia": {"tipo": "data", "obrigatorio": "sim", "valores": "DER, DII ou data do obito"},
    "vinculos": {"tipo": "lista", "obrigatorio": "condicional",
                 "valores": "sim, exceto beneficio = bpc: ao menos 1 vinculo; no BPC a lei nao exige vinculo "
                            "(LOAS, art. 20)"},
    "vinculos[].origem": {"tipo": "enum", "obrigatorio": "sim", "valores": list(ORIGENS)},
    "vinculos[].inicio": {"tipo": "data", "obrigatorio": "sim"},
    "vinculos[].fim": {"tipo": "data", "obrigatorio": "nao", "valores": "ausente = vinculo sem data de fim"},
    "vinculos[].indicadores": {"tipo": "lista de texto", "obrigatorio": "nao", "padrao": []},
    "vinculos[].competencias": {"tipo": "lista", "obrigatorio": "sim"},
    "vinculos[].competencias[].mes": {"tipo": "competencia", "obrigatorio": "sim"},
    "vinculos[].competencias[].valor": {"tipo": "decimal", "obrigatorio": "nao"},
    "vinculos[].competencias[].recolhido_em": {"tipo": "data", "obrigatorio": "nao"},
    "vinculos[].competencias[].indicadores": {"tipo": "lista de texto", "obrigatorio": "nao", "padrao": []},
    "vinculos[].filiacao_domestica_comprovada": {
        "tipo": "bool", "obrigatorio": "nao",
        "valores": "so origem domestico; true = filiacao como empregado domestico comprovada (IN 128, art. 190, "
                   "par. 1o, e art. 223, par. 5o); ausente = nao informado (conta aberta se decidir)"},
    "historico_anterior_informado": {"tipo": "bool", "obrigatorio": "sim"},
    "inscrito_ate_24_07_1991": {
        "tipo": "bool", "obrigatorio": "nao",
        "valores": "aposentadorias: inscricao na Previdencia Social Urbana ate 24/07/1991 ou trabalhador/empregador "
                   "rural coberto pela Previdencia Social Rural (Lei 8.213, art. 142); ausente = inferido dos "
                   "vinculos"},
    "ano_implementacao_requisitos": {
        "tipo": "inteiro", "obrigatorio": "nao",
        "valores": "aposentadorias com art. 142: ano em que o segurado implementou todas as condicoes; ausente = "
                   "conta aberta se a tabela decidir"},
    "desemprego_registrado": {"tipo": "bool", "obrigatorio": "nao", "padrao": False},
    "acidente_ou_doenca_dispensa": {"tipo": "bool", "obrigatorio": "nao", "padrao": False},
    "dias_sem_expediente_bancario": {"tipo": "lista de data", "obrigatorio": "nao",
                                     "valores": "ausente = feriados nacionais do motor de prazos, com alerta"},
}
# As hipóteses do art. 15, I e III a V, não têm campo (context/calculo-cnis.md, seções 1.2 e 7): a graça do script é
# a dos incisos II e VI e a saída avisa quando a qualidade sai perdida.
AVISO_ART15 = ("[VERIFICAR] A qualidade foi apurada só pela graça dos incisos II e VI do art. 15 da Lei 8.213. Benefício "
               "em manutenção (I), segregação (III), reclusão (IV) ou serviço militar (V) mudam o marco e entram na "
               "conta do advogado (context/calculo-cnis.md, seção 1.2).")
PRESUMIDO = "IN PRES/INSS 128, art. 189, §§1º e 2º"

FUND = {
    "carencia": "Lei 8.213, arts. 24 e 25 (I, II e IV)",
    "dispensa": "Lei 8.213, art. 26 (I e II) e art. 151",
    "maternidade": "Lei 8.213, art. 25, III, julgado inconstitucional (ADI 2.110)",
    "atraso": "Lei 8.213, art. 27, II",
    "apos_fato_gerador": "IN PRES/INSS 128, art. 189, §§4º e 5º",
    "perda": "Lei 8.213, art. 27-A; Decreto 3.048, art. 27-A",
    "graca": "Lei 8.213, art. 15 (II, VI, §§1º e 2º)",
    "graca_anterior": "IN PRES/INSS 128, art. 184, §7º",
    "reaquisicao": "IN PRES/INSS 128, art. 184, §4º, segunda parte",
    "perda_data": "Lei 8.213, art. 15, §4º; Decreto 3.048, art. 14",
    "vencimento": "Lei 8.212, art. 30, II e §2º, I",
    "indicadores": "Portaria DIRBEN/INSS 990/2022, Anexo V",
    "iean": "Lei 8.213, art. 57, §§3º e 4º",
    "qualidade_atraso": "IN PRES/INSS 128, art. 185 (caput, §§1º, 2º, 6º e 7º)",
    "minimo": "IN PRES/INSS 128, art. 189, caput e §§7º a 9º",
    "prestador": "IN PRES/INSS 128, arts. 185, §5º, 189, §1º, 191, parágrafo único, 192, §1º, e 193, II",
    "domestico": "IN PRES/INSS 128, art. 189, §2º, e art. 190",
    "domestico_comprovado": "IN PRES/INSS 128, art. 190, §1º, e art. 223, §5º",
    "somatorio": "Decreto 3.048, art. 19-E, §1º; IN PRES/INSS 128, art. 209, §1º",
    "art142": "Lei 8.213, art. 142",
}
# Lei 8.213, art. 142 (context/lei/lei-8213-1991.md): carência das aposentadorias por idade, tempo e especial do
# inscrito até 24/07/1991, pelo ano em que implementou todas as condições.
TABELA_142 = {1991: 60, 1992: 60, 1993: 66, 1994: 72, 1995: 78, 1996: 90, 1997: 96, 1998: 102, 1999: 108,
              2000: 114, 2001: 120, 2002: 126, 2003: 132, 2004: 138, 2005: 144, 2006: 150, 2007: 156, 2008: 162,
              2009: 168, 2010: 174, 2011: 180}
INSCRICAO_142 = dt.date(1991, 7, 24)


def exigidas_142(ano):
    """Meses da tabela do art. 142 para o ano; None antes de 1991 (fora da tabela)."""
    if ano < 1991:
        return None
    return TABELA_142[min(ano, 2011)]
# Doméstico: recolhimento presumido só desde a competência 06/2015 (IN 128, art. 189, §2º); filiado de 25/07/1991 a
# 31/05/2015, a carência corre da 1ª contribuição sem atraso (IN 128, art. 190). O vencimento do doméstico só está
# fechado em context/lei/ desde a Lei 8.620/1993 (Lei 8.212, art. 30, V, remetendo ao inciso II: dia 15).
DOMESTICO_PRESUMIDO_DESDE = (2015, 6)
DOMESTICO_ATRASO_FILIACAO = (dt.date(1991, 7, 25), dt.date(2015, 5, 31))
DOMESTICO_VENCIMENTO_DESDE = (1993, 1)
MARCO_MINIMO = dt.date(2019, 11, 14)   # IN 128, art. 189, §§7º e 8º

# r12 (revisão r11, BLOCKER 2: requisito de 2019 aplicado a fato de 2018). COBERTURA: intervalo de datas em que a regra
# que o script implementa é a vigente, com a fonte de cada borda, levantado das notas de redação ("Redação dada",
# "Incluído", "Revogado") dos dispositivos aplicados (context/lei/) e das tabelas por fato gerador da IN 128. Fora do
# intervalo a conta sai aberta (exit 3) com a regra histórica e a fonte; nunca veredito fechado pela regra posterior.
# 'chave': data_referencia (fato gerador) ou, nas linhas de qualidade e vencimento, a perda e a competência seguinte
# de cada perda apurada (_fora_da_perda). Dia não capturado em context/lei/ vira borda no ano da nota (conservadora).
VIGENCIA_8213 = dt.date(1991, 7, 25)
LEI_9876 = dt.date(1999, 11, 29)                 # DOU de 29.11.1999 (context/lei/lei-9876-1999.md:337)
VENCIMENTO_DIA_15_DESDE = (1993, 1)              # Lei 8.620, de 5.1.1993 (competência de janeiro em diante)
JANELA_MP905 = (dt.date(2019, 1, 1), dt.date(2020, 12, 31))
_F_8213 = "IN 128, art. 199, II (\"25 de julho de 1991, data de vigência da Lei nº 8.213\"; in-128-2022-inss.md:1754)"
_F_CLPS = "antes da Lei 8.213: regime anterior (CLPS), não capturado em context/lei/"
COBERTURA = (
    {"id": "carencia-incapacidade", "chave": "data_referencia", "beneficios": ("incapacidade",),
     "regra": "12 contribuições (Lei 8.213, art. 25, I) ou dispensa (art. 26, II)",
     "desde": VIGENCIA_8213, "fonte_desde": _F_8213 + "; art. 25, I, na redação original (lei-8213-1991.md:715)",
     "ate": None, "fonte_ate": "art. 25, I, sem nota de alteração em lei-8213-1991.md",
     "historica": _F_CLPS},
    {"id": "carencia-aposentadorias", "chave": "data_referencia", "beneficios": ("idade", "tempo", "especial"),
     "regra": "180 contribuições (art. 25, II) ou a tabela do art. 142 pelo ano em que o segurado implementou todas "
              "as condições",
     "desde": dt.date(1995, 4, 29),
     "fonte_desde": "Lei 8.213, art. 142, redação da Lei 9.032/1995 (\"ano em que o segurado implementou todas as "
                    "condições\"; lei-8213-1991.md:2843), publicada em 29/04/1995 (IN 128, art. 261, I: \"até 28 de "
                    "abril de 1995, véspera da publicação da Lei nº 9.032\"; in-128-2022-inss.md:2411)",
     "ate": None, "fonte_ate": "arts. 25, II (redação da Lei 8.870/1994), e 142 sem alteração posterior em "
                               "lei-8213-1991.md",
     "historica": "de 25/07/1991 a 28/04/1995: art. 142 na redação original, tabela pelo ano da entrada do "
                  "requerimento, com outros números de 1996 em diante (lei-8213-1991.md:2786-2841, redação revogada); "
                  + _F_CLPS},
    {"id": "carencia-auxilio-reclusao", "chave": "data_referencia", "beneficios": ("auxilio-reclusao",),
     "regra": "24 contribuições (Lei 8.213, art. 25, IV)",
     "desde": dt.date(2019, 1, 18),
     "fonte_desde": "art. 25, IV, incluído pela MP 871/2019 (lei-8213-1991.md:727-729), publicada em 18/01/2019 "
                    "(lei-13846-2019.md:968); IN 128, art. 198, II (in-128-2022-inss.md:1750)",
     "ate": None, "fonte_ate": "art. 25, IV, na redação da Lei 13.846/2019, sem alteração posterior",
     "historica": "fato gerador até 17/01/2019: auxílio-reclusão isento de carência (IN 128, art. 198, I, "
                  "in-128-2022-inss.md:1749; Lei 8.213, art. 26, I, redação da Lei 9.876/1999, lei-8213-1991.md:737)"},
    {"id": "carencia-salario-maternidade", "chave": "data_referencia", "beneficios": ("salario-maternidade",),
     "regra": "sem carência: art. 25, III, julgado inconstitucional (ADI 2.110)",
     "desde": dt.date(2024, 4, 5),
     "fonte_desde": "ADI 2.110, ata do julgamento publicada em 5/4/24 (temas-sumulas-prev.md:22); IN 128, art. 200, "
                    "tabela, linha \"05/04/2024 em diante ... ADI nº 2.110\" (in-128-2022-inss.md:1795-1800)",
     "ate": None, "fonte_ate": "linha final da tabela da IN 128, art. 200",
     "historica": "antes de 05/04/2024: isentas a empregada, a avulsa e a doméstica (Lei 8.213, art. 26, VI, Lei "
                  "9.876/1999); 10 contribuições da contribuinte individual, da facultativa e da segurada especial "
                  "(art. 25, III), como a IN 128, art. 200, aplica até 04/04/2024; o efeito da ADI 2.110 sobre fato "
                  "anterior não está fechado em context/"},
    {"id": "carencia-pensao-auxilio-acidente", "chave": "data_referencia",
     "beneficios": ("pensao", "auxilio-acidente"), "regra": "sem carência (Lei 8.213, art. 26, I)",
     "desde": VIGENCIA_8213, "fonte_desde": _F_8213 + "; art. 26, I, já na redação original dispensa pensão e "
                                                      "auxílio-acidente (lei-8213-1991.md:735)",
     "ate": None, "fonte_ate": "art. 26, I, redação da Lei 13.846/2019, mantém os dois", "historica": _F_CLPS},
    {"id": "carencia-bpc", "chave": "data_referencia", "beneficios": ("bpc",),
     "regra": "benefício assistencial sem carência (LOAS, art. 20)", "desde": dt.date(1993, 12, 7),
     "fonte_desde": "Lei 8.742, de 7 de dezembro de 1993 (lei-8742-1993-loas.md:16); dia da publicação não capturado",
     "ate": None, "fonte_ate": "LOAS, art. 20, em vigor", "historica": "antes da LOAS não havia o BPC"},
    {"id": "perda-27A", "chave": "data_referencia", "beneficios": BENEFICIOS_27A,
     "regra": "após a perda, as contribuições anteriores voltam quando as novas alcançam a fração da carência do "
              "regime do fato gerador (REGIMES_27A)",
     "desde": VIGENCIA_8213, "fonte_desde": "IN 128, art. 200, caput (\"benefícios requeridos a partir de 25 de "
                                           "julho de 1991\"; in-128-2022-inss.md:1758)",
     "ate": None, "fonte_ate": "IN 128, art. 200, tabela, linha \"05/04/2024 em diante\"", "historica": _F_CLPS},
    {"id": "qualidade-art15-ate-2018", "chave": "perda", "beneficios": None,
     "regra": "graça do art. 15, II e VI, §§1º, 2º e 4º, da Lei 8.213, na redação original",
     "desde": VIGENCIA_8213, "fonte_desde": _F_8213,
     "ate": JANELA_MP905[0] - dt.timedelta(days=1),
     "fonte_ate": "MP 905/2019 deu ao art. 15, II, redação que conta a graça também do fim do seguro-desemprego, e o "
                  "fez salário de contribuição (Lei 8.212, art. 28, §12); revogada pela MP 955/2020 "
                  "(lei-8213-1991.md:447-449; lei-8212-1991.md:1015). Dias não capturados: a borda é o fim de 2018",
     "historica": "art. 15, II, redação da MP 905/2019: graça também a contar de quando o segurado deixar de receber o "
                  "seguro-desemprego, cuja parcela era salário de contribuição; só prorroga a qualidade, por isso só a "
                  "perda apurada fica aberta"},
    {"id": "qualidade-art15-desde-2021", "chave": "perda", "beneficios": None,
     "regra": "graça do art. 15, II e VI, §§1º, 2º e 4º, da Lei 8.213, na redação original",
     "desde": JANELA_MP905[1] + dt.timedelta(days=1),
     "fonte_desde": "revogação da MP 905/2019 pela MP 955/2020 (lei-8213-1991.md:447-449); dia não capturado: a "
                    "borda é o início de 2021",
     "ate": None, "fonte_ate": "art. 15, II, na redação original, em vigor", "historica": "ver qualidade-art15-ate-2018"},
    {"id": "vencimento-dia-15", "chave": "competencia", "beneficios": None,
     "regra": "vencimento do CI, do facultativo e do doméstico no dia 15 do mês seguinte (Lei 8.212, art. 30, II e "
              "V); sem expediente bancário, dia útil anterior até 28/11/1999 (§2º, Lei 8.620/1993) e posterior desde "
              "29/11/1999 (§2º, Lei 9.876/1999)",
     "desde": VENCIMENTO_DIA_15_DESDE,
     "fonte_desde": "art. 30, II, redação da Lei 8.620, de 5.1.1993, e §2º incluído por ela (lei-8212-1991.md:1232)",
     "ate": None, "fonte_ate": "art. 30, §2º, I, redação da Lei 13.202/2015 (lei-8212-1991.md:1246)",
     "historica": "competências anteriores a 01/1993: prazo da alínea b do inciso I do art. 30 da Lei 8.212 em "
                  "redações sucessivas (dia 8, depois dia 2) cujas datas não estão capturadas"},
)
# Regime da perda da qualidade por fato gerador (IN 128, art. 200, tabela; in-128-2022-inss.md:1760-1800; redações
# do art. 24, parágrafo único, e do art. 27-A da Lei 8.213, lei-8213-1991.md:707-779). 'fracao' da carência integral
# que as novas contribuições alcançam para as anteriores voltarem.
REGIMES_27A = (
    (dt.date(1991, 7, 25), dt.date(2016, 7, 7), (1, 3), "1/3", "redação original (art. 24, parágrafo único)"),
    (dt.date(2016, 7, 8), dt.date(2016, 11, 4), (1, 1), "total", "MP 739/2016"),
    (dt.date(2016, 11, 5), dt.date(2017, 1, 5), (1, 3), "1/3", "redação original"),
    (dt.date(2017, 1, 6), dt.date(2017, 6, 26), (1, 1), "total", "MP 767/2017"),
    (dt.date(2017, 6, 27), dt.date(2019, 1, 17), (1, 2), "1/2", "Lei 13.457/2017"),
    (dt.date(2019, 1, 18), dt.date(2019, 6, 17), (1, 1), "total", "MP 871/2019"),
    (dt.date(2019, 6, 18), None, (1, 2), "1/2", "Lei 13.846/2019 (art. 27-A vigente)"),
)


def regime_27a(d):
    for ini, fim, fracao, rotulo, norma in REGIMES_27A:
        if ini <= d and (fim is None or d <= fim):
            return {"fracao": fracao, "rotulo": rotulo, "norma": norma, "desde": ini, "ate": fim}
    return None


def coberta(linha, d):
    """True se a data (ou a competência, na linha de vencimento) está no intervalo da linha."""
    if d is None:
        return True
    return d >= linha["desde"] and (linha["ate"] is None or d <= linha["ate"])


def linha_cobertura(lid):
    return next(l for l in COBERTURA if l["id"] == lid)


def descrever_fora(linha, d, onde):
    return {"linha": linha["id"], onde: d if isinstance(d, str) else (mes_txt(d) if isinstance(d, tuple)
                                                                      else d.isoformat()),
            "regra_implementada": linha["regra"],
            "cobertura": {"desde": mes_txt(linha["desde"]) if isinstance(linha["desde"], tuple)
                          else linha["desde"].isoformat(), "fonte_desde": linha["fonte_desde"],
                          "ate": linha["ate"].isoformat() if linha["ate"] else None, "fonte_ate": linha["fonte_ate"]},
            "regra_historica": linha["historica"]}
ORIGENS_SEM_MINIMO_ATE_2019 = ("empregado", "domestico", "avulso")   # IN 128, art. 189, §8º
EFEITO_IEAN = "possível enquadramento especial; exige PPP/LTCAT; sem conversão automática"


class EntradaInvalida(Exception):
    pass


# ------------------------------------------------------------ datas e meses

def mes(d):
    return (d.year, d.month)


def mes_txt(m):
    return f"{m[0]:04d}-{m[1]:02d}"


def somar_meses(m, n):
    t = m[0] * 12 + m[1] - 1 + n
    return (t // 12, t % 12 + 1)


def ultimo_dia(m):
    p = somar_meses(m, 1)
    return dt.date(p[0], p[1], 1) - dt.timedelta(days=1)


def pascoa(ano):
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    mes_, dia = divmod(h + l_ - 7 * m + 114, 31)
    return dt.date(ano, mes_, dia + 1)


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


def _limpo(obj, permitidas, onde):
    if not isinstance(obj, dict):
        raise EntradaInvalida(f"{onde}: esperado objeto")
    obj = {k: v for k, v in obj.items() if not (isinstance(k, str) and k.startswith("_"))}
    extras = sorted(set(obj) - set(permitidas))
    if extras:
        raise EntradaInvalida(f"{onde}: campo desconhecido {extras[0]!r}")
    return obj


def _obrig(obj, campo, onde):
    if obj.get(campo) is None:
        raise EntradaInvalida(f"{onde}: campo obrigatório '{campo}' ausente ou null")
    return obj[campo]


def _bool(obj, campo, padrao=None):
    v = obj.get(campo)
    if v is None:
        return padrao
    if not isinstance(v, bool):
        raise EntradaInvalida(f"{campo}: esperado true ou false")
    return v


def _siglas(v, onde):
    v = [] if v is None else v
    if not isinstance(v, list) or not all(isinstance(s, str) and s.strip() for s in v):
        raise EntradaInvalida(f"{onde}: esperada lista de siglas (texto)")
    return [s.strip() for s in v]


def validar(bruto):
    e = _limpo(bruto, [k for k in CAMPOS if "[]" not in k], "entrada")
    beneficio = _obrig(e, "beneficio", "entrada")
    if beneficio not in BENEFICIOS:
        raise EntradaInvalida(f"beneficio: '{beneficio}' fora de {list(BENEFICIOS)}")
    ref = _data("data_referencia", _obrig(e, "data_referencia", "entrada"))
    hist = _obrig(e, "historico_anterior_informado", "entrada")
    if not isinstance(hist, bool):
        raise EntradaInvalida("historico_anterior_informado: esperado true ou false")
    if beneficio == "bpc" and e.get("vinculos") is None:
        vinculos = []   # D2: o BPC é assistencial e não exige vínculo (LOAS, art. 20)
    else:
        vinculos = _obrig(e, "vinculos", "entrada")
        if not isinstance(vinculos, list) or (not vinculos and beneficio != "bpc"):
            raise EntradaInvalida("vinculos: esperada lista com ao menos 1 vínculo (só o BPC dispensa)")
    vs = []
    for i, v in enumerate(vinculos):
        rot = f"vinculos[{i}]"
        v = _limpo(v, ("origem", "inicio", "fim", "indicadores", "competencias", "filiacao_domestica_comprovada"), rot)
        origem = _obrig(v, "origem", rot)
        if origem not in ORIGENS:
            raise EntradaInvalida(f"{rot}.origem: '{origem}' fora de {list(ORIGENS)}")
        ini = _data(f"{rot}.inicio", _obrig(v, "inicio", rot))
        fim = _data(f"{rot}.fim", v["fim"]) if v.get("fim") is not None else None
        if fim and fim < ini:
            raise EntradaInvalida(f"{rot}: fim {fim} anterior ao início {ini}")
        comps = _obrig(v, "competencias", rot)
        if not isinstance(comps, list):
            raise EntradaInvalida(f"{rot}.competencias: esperada lista")
        cs = []
        for j, c in enumerate(comps):
            rc = f"{rot}.competencias[{j}]"
            c = _limpo(c, ("mes", "valor", "recolhido_em", "indicadores"), rc)
            m = _competencia(f"{rc}.mes", _obrig(c, "mes", rc))
            valor = None
            if c.get("valor") is not None:
                try:
                    valor = Decimal(str(c["valor"]))
                except InvalidOperation:
                    raise EntradaInvalida(f"{rc}.valor: decimal inválido {c['valor']!r}")
                if isinstance(c["valor"], bool) or not valor.is_finite() or valor < 0:
                    raise EntradaInvalida(f"{rc}.valor: decimal inválido {c['valor']!r}")
            # r13 (revisão r12, MAJOR 2): competência anterior ao mês de início do vínculo é cronologia impossível,
            # recusada. A posterior ao fim e a posterior à data de referência são permitidas: a conta as exclui com
            # motivo (fora das datas do vínculo; IN 128, art. 189, §§4º e 5º).
            if m < mes(ini):
                raise EntradaInvalida(f"{rc}.mes: competência {m[1]:02d}/{m[0]} anterior ao início do vínculo {ini}")
            rec = _data(f"{rc}.recolhido_em", c["recolhido_em"]) if c.get("recolhido_em") is not None else None
            if any(x["mes"] == m for x in cs):
                # Competência repetida no mesmo vínculo dobraria o somatório mensal da contribuição mínima
                # (Decreto 3.048, art. 19-E, §1º): entrada ambígua, recusada.
                raise EntradaInvalida(f"{rc}.mes: competência {m[1]:02d}/{m[0]} repetida no mesmo vínculo")
            cs.append({"mes": m, "valor": valor, "recolhido_em": rec,
                       "indicadores": _siglas(c.get("indicadores"), f"{rc}.indicadores")})
        dom_comp = _bool(v, "filiacao_domestica_comprovada")
        if dom_comp is not None and origem != "domestico":
            raise EntradaInvalida(f"{rot}.filiacao_domestica_comprovada: só no vínculo de origem domestico")
        vs.append({"i": i, "origem": origem, "inicio": ini, "fim": fim, "dom_comp": dom_comp,
                   "indicadores": _siglas(v.get("indicadores"), f"{rot}.indicadores"), "competencias": cs})
    dias_sem = e.get("dias_sem_expediente_bancario")
    if dias_sem is not None:
        if not isinstance(dias_sem, list):
            raise EntradaInvalida("dias_sem_expediente_bancario: esperada lista de datas")
        dias_sem = {_data(f"dias_sem_expediente_bancario[{k}]", d) for k, d in enumerate(dias_sem)}
    ano_impl = e.get("ano_implementacao_requisitos")
    if ano_impl is not None and (isinstance(ano_impl, bool) or not isinstance(ano_impl, int)
                                 or not 1900 <= ano_impl <= 2100):
        raise EntradaInvalida("ano_implementacao_requisitos: esperado ano inteiro de 1900 a 2100")
    if ano_impl is not None and ano_impl > ref.year:
        raise EntradaInvalida("ano_implementacao_requisitos: posterior ao ano da data de referência")
    # r15 (revisão r14, MAJOR 2): inscrição declarada depois de 24/07/1991 contra vínculo de segurado obrigatório
    # iniciado até essa data é contraditória: a filiação dele decorre do exercício da atividade (IN 128, art. 3º, §1º).
    # O facultativo fica de fora: a filiação dele depende da inscrição e do primeiro recolhimento sem atraso (art. 4º).
    if _bool(e, "inscrito_ate_24_07_1991") is False:
        for v in vs:
            if v["origem"] != "facultativo" and v["inicio"] <= INSCRICAO_142:
                raise EntradaInvalida(
                    f"vinculos[{v['i']}]: {v['origem']} iniciado em {v['inicio']}, até 24/07/1991, com "
                    f"inscrito_ate_24_07_1991 = false; a filiação do segurado obrigatório decorre do exercício da "
                    f"atividade (IN 128, art. 3º, §1º)")
    return {"beneficio": beneficio, "data_referencia": ref, "vinculos": vs, "historico": hist,
            "inscrito_1991": _bool(e, "inscrito_ate_24_07_1991"), "ano_impl": ano_impl,
            "desemprego": _bool(e, "desemprego_registrado", False),
            "dispensa": _bool(e, "acidente_ou_doenca_dispensa", False), "dias_sem": dias_sem}


# ------------------------------------------------------------ tabelas

class TabelaIndisponivel(Exception):
    """Tabela de scripts/data/ ausente ou ilegível: exit 3 com a conta aberta (DESIGN-SPEC §3.2), nunca exit 2."""

    def __init__(self, arquivo, err):
        super().__init__(f"{arquivo}: {type(err).__name__}")
        self.arquivo = arquivo


def carregar_indicadores():
    try:
        dados = json.loads(TABELA_INDICADORES.read_text(encoding="utf-8"))
        por_sigla = {}
        for linha in dados["linhas"]:
            por_sigla.setdefault(linha["sigla"], []).append(linha)
        fonte = {"arquivo": "scripts/data/indicadores-cnis.json", "data_captura": dados.get("data_captura"),
                 "norma": dados["fonte"][0]["norma"]}
    except (OSError, ValueError, KeyError, TypeError, IndexError) as err:
        raise TabelaIndisponivel("scripts/data/indicadores-cnis.json", err)
    return por_sigla, fonte


def salario_minimo(m):
    """Salários mínimos vigentes em algum dia da competência, como (menor, maior), ou None quando algum dia do mês
    não tem valor na tabela (tabela ausente ou ilegível, lacuna com valor null, fora do intervalo). Em 04/2000, por
    exemplo, o mínimo mudou em 03/04 (R$ 136 → R$ 151): a competência tem dois valores. A competência que depende
    do valor ausente ou que fica entre os dois fica incerta e, se decidir, a conta sai aberta (exit 3)."""
    ini_m, fim_m = dt.date(m[0], m[1], 1), ultimo_dia(m)
    try:
        dados = json.loads(TABELA_SALARIO_MINIMO.read_text(encoding="utf-8"))
        valores, cobertos = set(), set()
        for linha in dados["linhas"]:
            ini = dt.date.fromisoformat(linha["vigencia_inicio"])
            fim = dt.date.fromisoformat(linha["vigencia_fim"]) if linha.get("vigencia_fim") else dt.date(2026, 12, 31)
            a, b = max(ini, ini_m), min(fim, fim_m)
            if a > b:
                continue
            if not linha.get("valor"):
                return None   # lacuna (null) dentro da competência
            valores.add(Decimal(linha["valor"]))
            cobertos.update(a + dt.timedelta(days=k) for k in range((b - a).days + 1))
    except (OSError, ValueError, KeyError, TypeError, ArithmeticError):
        return None
    if not valores or len(cobertos) != (fim_m - ini_m).days + 1:
        return None
    return min(valores), max(valores)


def domestico_sujeito_atraso(v):
    """Doméstico filiado (início do vínculo) de 25/07/1991 a 31/05/2015: carência da 1ª contribuição sem atraso."""
    return DOMESTICO_ATRASO_FILIACAO[0] <= v["inicio"] <= DOMESTICO_ATRASO_FILIACAO[1]


def tabela_ausente(err, e=None):
    parametros = None
    if e is not None:
        parametros = {"beneficio": e["beneficio"], "data_referencia": e["data_referencia"].isoformat()}
    return EXIT_FALTA, {
        "versao": VERSAO, "parametros_usados": parametros,
        "regra": "Sem a tabela, carência e qualidade de segurado não são apuradas por script.",
        "fonte": {"tabela_ausente": err.arquivo},
        "memoria": [f"Tabela {err.arquivo} indisponível ({err}): a conta não é fechada por script."],
        "alertas": [f"[VERIFICAR] Tabela {err.arquivo} ausente ou ilegível: a conta sai aberta, sem número."],
        "carencia": None, "qualidade_segurado": None,
        "formula_aberta": {"expressao": "carência = competências válidas ≥ exigidas (Lei 8.213, arts. 24 a 27-A); "
                                        "qualidade pela graça do art. 15 desde a última competência válida",
                           "faltando": [err.arquivo],
                           "instrucao": "Conta não conferida por script (context/calculo-cnis.md, seção 3)."}}


class Calendario:
    """Dias sem expediente bancário para o vencimento do dia 15 (Lei 8.212, art. 30, §2º, I)."""

    def __init__(self, dias_informados, alternativo=False):
        self.informados = dias_informados
        self.alternativo = alternativo   # dias incertos tratados como sem expediente (sensibilidade, regra 2)
        self.fixos, self.moveis, self.ok = {}, [], False
        if dias_informados is None:
            try:
                dados = json.loads(TABELA_FERIADOS.read_text(encoding="utf-8"))
                fixos = {}
                for f in dados.get("fixos", []):
                    if f.get("tipo") == "nacional":
                        if f.get("vigencia_desde"):
                            dt.date.fromisoformat(f["vigencia_desde"])
                        fixos[f["mes_dia"]] = f
                moveis = [mv for mv in dados.get("moveis", []) if isinstance(mv["dias_da_pascoa"], int)]
                self.fixos, self.moveis, self.ok = fixos, moveis, True
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                # Tabela do motor de prazos ausente ou ilegível: só fins de semana, com alerta (já previsto).
                self.fixos, self.moveis, self.ok = {}, [], False

    def sem_expediente(self, d, alertas):
        if d.weekday() >= 5:
            return True
        if self.informados is not None:
            return d in self.informados
        f = self.fixos.get(d.strftime("%m-%d"))
        if f and (not f.get("vigencia_desde") or d >= dt.date.fromisoformat(f["vigencia_desde"])):
            return True
        if self.alternativo and not self.ok and d.day in (15, 16):
            return True   # sem a tabela do motor de prazos, qualquer dia 15 ou 16 pode ser feriado
        for mv in self.moveis:
            if pascoa(d.year) + dt.timedelta(days=mv["dias_da_pascoa"]) == d:
                if self.alternativo:
                    return True
                alertas.append(f"[VERIFICAR] O vencimento cai em {d.isoformat()} ({mv['nome']}): sem o calendário "
                               "bancário do caso, o dia foi tratado como útil.")
        return False

    def proximo_util(self, d, alertas):
        while self.sem_expediente(d, alertas):
            d += dt.timedelta(days=1)
        return d

    def anterior_util(self, d, alertas):
        while self.sem_expediente(d, alertas):
            d -= dt.timedelta(days=1)
        return d

    def vencimento(self, nominal, alertas):
        """Dia 15 sem expediente bancário: dia útil anterior até a Lei 9.876/1999 (Lei 8.212, art. 30, §2º, redação da
        Lei 8.620/1993) e posterior desde ela (§2º, redação da Lei 9.876/1999; hoje §2º, I). r12, COBERTURA."""
        if nominal < LEI_9876:
            return self.anterior_util(nominal, alertas)
        return self.proximo_util(nominal, alertas)


# ------------------------------------------------------------ núcleo

def calcular(bruto):
    try:
        e = validar(bruto)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}
    try:
        codigo, saida = _com_sensibilidade(e)
        if codigo == EXIT_OK:
            codigo, saida = _prestador(e, saida)
        if codigo == EXIT_OK:
            codigo, saida = _domestico(e, saida)
        if codigo == EXIT_OK:
            codigo, saida = _calendario(e, saida)
        codigo, saida = _cobertura(e, codigo, saida)
    except TabelaIndisponivel as err:
        return tabela_ausente(err, e)
    qs =saida.get("qualidade_segurado") or {}
    if qs and qs.get("mantem_qualidade_na_data_referencia") is not True:
        saida["alertas"].append(AVISO_ART15)
    return codigo, saida


def _veredito(saida):
    car = saida["carencia"]["cumprida"]
    q = (saida["qualidade_segurado"] or {}).get("mantem_qualidade_na_data_referencia", False)
    return car, q


def _projecao(saida):
    """r10: tudo o que a conta fecha (números, datas e vereditos da carência e da qualidade), sem os textos de
    fundamento e sem a lista de excluídas, cujos motivos mudam com a leitura sem mudar a conta."""
    car = {k: v for k, v in (saida.get("carencia") or {}).items()
           if k != "excluidas" and not k.startswith("fundamento")}
    qs = {k: v for k, v in (saida.get("qualidade_segurado") or {}).items() if k != "fundamento"}
    return {"carencia": car, "qualidade_segurado": qs or None}


def _diferencas(a, b, caminho=""):
    """Caminhos em que duas projeções divergem."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += _diferencas(a.get(k), b.get(k), f"{caminho}.{k}" if caminho else k)
        return out
    return [] if a == b else [caminho]


def _leituras(saida, alt, rotulos, alerta, expressao, faltando, instrucao, contas):
    """r10, regra única das sensibilidades: duas leituras da mesma entrada que divergem em QUALQUER número, data ou
    veredito da projeção não fecham a conta (exit 3), e a saída devolve as duas."""
    proj_b, proj_a = _projecao(saida), _projecao(alt)
    dif = _diferencas(proj_b, proj_a)
    if not dif:
        return EXIT_OK, saida
    (car_b, q_b), (car_a, q_a) = _veredito(saida), _veredito(alt)
    car = saida["carencia"]
    if car_b != car_a:
        car["cumprida"] = "indeterminada"
        car["faltam"] = max(0, car["exigidas"] - car["contadas"])
    if q_b != q_a:
        if saida["qualidade_segurado"] is None:
            saida["qualidade_segurado"] = {}
        saida["qualidade_segurado"]["mantem_qualidade_na_data_referencia"] = "indeterminada"
    saida["alertas"].append(f"{alerta} As duas leituras divergem em: {', '.join(dif)}.")
    saida["formula_aberta"] = {"expressao": expressao, "contas": contas,
                               "leituras": {rotulos[0]: proj_b, rotulos[1]: proj_a}, "diferencas": dif,
                               "faltando": faltando, "instrucao": instrucao}
    saida["memoria"].append(f"Leituras {rotulos[0]} × {rotulos[1]}: carência {car_b} × {car_a}; qualidade mantida "
                            f"{q_b} × {q_a}; divergem em {', '.join(dif)}. Conta aberta.")
    return EXIT_FALTA, saida


def _perda(saida):
    return (saida["qualidade_segurado"] or {}).get("data_perda")


def _calendario(e, saida):
    """Regra 2: sem dias_sem_expediente_bancario, o vencimento do dia 15 sai do calendário de feriados nacionais (ou,
    sem a tabela do motor de prazos, só dos fins de semana). Refaz a conta com os dias incertos tratados como sem
    expediente (feriados móveis; sem a tabela, os dias 15 e 16 de cada mês). Se a conta muda, conta aberta."""
    if e["dias_sem"] is not None:
        return EXIT_OK, saida
    _, alt, _ = _apurar(e, presumir=False, cal_alt=True)
    (car_b, q_b), (car_a, q_a) = _veredito(saida), _veredito(alt)
    return _leituras(
        saida, alt, ("calendario_usado", "dias_incertos_sem_expediente"),
        "[VERIFICAR] O vencimento do dia 15 depende do calendário bancário, que a entrada não traz: tratados como "
        "sem expediente os dias incertos, a conta muda. Informe dias_sem_expediente_bancario.",
        "vencimento = dia 15 do mês seguinte, prorrogado para o dia útil seguinte sem expediente bancário (Lei 8.212, "
        "art. 30, II e §2º, I); em dia = recolhido até o vencimento",
        ["dias_sem_expediente_bancario (calendário bancário dos vencimentos do caso)"],
        "context/calculo-cnis.md, seção 1.2 (vencimento e data da perda).",
        {"cumprida_calendario_usado": car_b, "cumprida_dias_incertos_sem_expediente": car_a,
         "mantem_qualidade_calendario_usado": q_b, "mantem_qualidade_dias_incertos_sem_expediente": q_a,
         "data_perda_calendario_usado": _perda(saida), "data_perda_dias_incertos_sem_expediente": _perda(alt)})


def _prestador(e, saida):
    """A2: o CI prestador de serviço a pessoa jurídica, desde a competência 04/2003, tem o recolhimento presumido e
    a atividade comprovada computada ainda que sem contribuição (IN 128, arts. 189, §1º, e 193, II); por isso não se
    sujeita ao filtro do recolhimento depois do fato gerador (art. 189, §4º), à regra do atraso na carência (art.
    191, parágrafo único; art. 192, §1º) nem ao deslocamento da qualidade para a data do recolhimento (art. 185,
    §5º). A CAMPOS não diz se o CI é prestador: refaz a conta nessa leitura e, se qualquer número, data ou veredito
    muda (r10), o caso não fecha (exit 3)."""
    if not any(v["origem"] == "contribuinte-individual" for v in e["vinculos"]):
        return EXIT_OK, saida
    _, alt, _ = _apurar(e, presumir=False, prestador=True)
    (car_p, q_p), (car_a, q_a) = _veredito(saida), _veredito(alt)
    return _leituras(
        saida, alt, ("ci_proprio", "ci_prestador"),
        "[VERIFICAR] Contribuinte individual: se for prestador de serviço a pessoa jurídica (competências desde "
        "04/2003), o recolhimento é presumido e a atividade comprovada conta ainda que paga depois do fato gerador ou "
        f"em atraso, sem deslocar a qualidade para a data do pagamento ({FUND['prestador']}).",
        "CI por conta própria: recolhimento depois do fato gerador fora da carência, atraso fora da carência antes do "
        "1º recolhimento em dia e qualidade pela data do pagamento; CI prestador a PJ desde 04/2003: competência da "
        "atividade comprovada, sem essas regras",
        ["se o contribuinte individual presta serviço a pessoa jurídica (e desde quando)"],
        "context/calculo-cnis.md, seções 1.1 e 1.2; " + FUND["prestador"] + ".",
        {"contadas_ci_proprio": saida["carencia"]["contadas"], "contadas_ci_prestador": alt["carencia"]["contadas"],
         "exigidas": saida["carencia"]["exigidas"], "cumprida_ci_proprio": car_p, "cumprida_ci_prestador": car_a,
         "mantem_qualidade_ci_proprio": q_p, "mantem_qualidade_ci_prestador": q_a,
         "data_perda_ci_proprio": _perda(saida), "data_perda_ci_prestador": _perda(alt)})


def _domestico(e, saida):
    """IN 128, art. 190, §1º, e art. 223, §5º: com a filiação doméstica comprovada, o período conta sem a prova do
    recolhimento e sem a 1ª contribuição sem atraso, qualquer que seja a categoria no requerimento. Sem o campo
    filiacao_domestica_comprovada, refaz a conta nessa leitura; se a conta muda, exit 3."""
    if not any(v["origem"] == "domestico" and v["dom_comp"] is None and v["inicio"] < dt.date(2015, 6, 1)
               for v in e["vinculos"]):
        return EXIT_OK, saida
    _, alt, _ = _apurar(e, presumir=False, dom_alt=True)
    (car_n, q_n), (car_c, q_c) = _veredito(saida), _veredito(alt)
    return _leituras(
        saida, alt, ("sem_comprovacao", "com_comprovacao"),
        "[VERIFICAR] Vínculo doméstico anterior a 06/2015 sem filiacao_domestica_comprovada: com a filiação "
        "comprovada, o período conta sem a prova do recolhimento e sem a 1ª contribuição sem atraso "
        f"({FUND['domestico_comprovado']}).",
        "doméstico filiado de 25/07/1991 a 31/05/2015: carência da 1ª contribuição sem atraso (IN 128, art. 190); "
        "com a filiação doméstica comprovada, o período de filiação conta (art. 190, §1º)",
        ["vinculos[].filiacao_domestica_comprovada (filiação como empregado doméstico comprovada)"],
        "context/calculo-cnis.md, seção 1.1; " + FUND["domestico_comprovado"] + ".",
        {"contadas_sem_comprovacao": saida["carencia"]["contadas"],
         "contadas_com_comprovacao": alt["carencia"]["contadas"], "exigidas": saida["carencia"]["exigidas"],
         "cumprida_sem_comprovacao": car_n, "cumprida_com_comprovacao": car_c,
         "mantem_qualidade_sem_comprovacao": q_n, "mantem_qualidade_com_comprovacao": q_c})


def _com_sensibilidade(e):
    codigo, saida, incertas = _apurar(e, presumir=False)
    # r10: a leitura presumida roda sempre que houver contribuição incerta, ainda que outro vínculo cubra o mês.
    if codigo != EXIT_OK or not any(x.get("classe") == "incerta" for x in saida["carencia"]["excluidas"]):
        return codigo, saida
    # Sensibilidade: as competências incertas (dado ausente ou não conferível) ficaram fora. Refaz a conta
    # presumindo-as válidas; se qualquer número, data ou veredito muda (r10), o caso não fecha (exit 3).
    _, otim, _ = _apurar(e, presumir=True)
    (car_p, q_p), (car_o, q_o) = _veredito(saida), _veredito(otim)
    return _leituras(
        saida, otim, ("sem_incertas", "com_incertas"),
        "[VERIFICAR] Competências incertas (fora da conta) mudariam a conta: "
        + "; ".join(f"{mes_txt(m)}: {mot}" for m, mot in sorted(incertas.items())) + ".",
        "cumprida = contadas >= exigidas; qualidade pela graça do art. 15 a partir da última competência válida; as "
        "incertas entram só depois de conferidas",
        sorted(set(incertas.values())),
        "Conferir as competências incertas listadas em carencia.excluidas e refazer a conta (context/calculo-cnis.md, "
        "seção 3).",
        {"contadas_sem_incertas": saida["carencia"]["contadas"], "contadas_com_incertas": otim["carencia"]["contadas"],
         "incertas": len(incertas), "exigidas": saida["carencia"]["exigidas"],
         "cumprida_sem_incertas": car_p, "cumprida_com_incertas": car_o,
         "mantem_qualidade_sem_incertas": q_p, "mantem_qualidade_com_incertas": q_o,
         "data_perda_sem_incertas": _perda(saida), "data_perda_com_incertas": _perda(otim)})


def _apurar(e, presumir, prestador=False, cal_alt=False, dom_alt=False):
    """Conta do CNIS. presumir=False tira da conta as competências incertas (devolvidas no 3º valor);
    presumir=True as trata como válidas e em dia, só para medir se mudam o veredito. prestador=True lê o CI como
    prestador de serviço a PJ desde 04/2003; cal_alt=True trata os dias incertos do calendário como sem
    expediente; dom_alt=True lê como comprovada a filiação doméstica não informada (IN 128, art. 190, §1º). As três
    últimas só medem sensibilidade (regra 2)."""
    tab_ind, fonte_ind = carregar_indicadores()
    pendencias = {s for s, linhas in tab_ind.items() if any(l["tipo"] == "CsPendencia" for l in linhas)}
    ref, ben = e["data_referencia"], e["beneficio"]
    alertas, memoria, excluidas, lacunas = [], [], [], []
    fora = []   # r12: pontos da conta fora da COBERTURA (vencimento e perda); o gate fica em _cobertura

    def marcar_fora(lid, d, onde, afeta=("carencia", "qualidade")):
        item = {**descrever_fora(linha_cobertura(lid), d, onde), "afeta": list(afeta)}
        if item not in fora:
            fora.append(item)

    # Vencimento do CI/facultativo: dia 15 do mês seguinte, prorrogado para o dia útil seguinte
    # se não houver expediente bancário (Lei 8.212, art. 30, II e §2º, I).
    cal = Calendario(e["dias_sem"], alternativo=cal_alt)

    def vencimento(m):
        return cal.vencimento(dt.date(*somar_meses(m, 1), 15), alertas)

    def em_dia(c):
        if c["recolhido_em"] is None:   # só no modo presumir: a incerta conta como paga em dia
            return True
        return c["recolhido_em"] <= vencimento(c["mes"])

    def apos_fato_gerador(c):
        """IN 128, art. 189, §4º: recolhido depois da data de referência não conta, ainda que de competência
        anterior; §5º: salvo o da competência do fato gerador pago até o vencimento."""
        if c["recolhido_em"] is None:
            return False
        return c["recolhido_em"] > ref and not (c["mes"] == mes(ref) and em_dia(c))

    def inicio_efetivo(v, m):
        """Data em que a competência começa a valer: o ingresso, se o vínculo começa no mês (art. 27-A)."""
        return max(dt.date(m[0], m[1], 1), v["inicio"])

    def dom_comprovado(v):
        """Filiação doméstica comprovada (IN 128, art. 190, §1º, e art. 223, §5º): o período conta sem a prova do
        recolhimento e sem a 1ª contribuição sem atraso."""
        return v["origem"] == "domestico" and (v["dom_comp"] is True or (dom_alt and v["dom_comp"] is None))

    # ---- r10: competências em duas fases (IN 128, art. 189, caput e §§4º, 5º e 7º a 9º; Decreto 3.048, art. 19-E,
    # §1º; IN 128, art. 209, §1º).
    # Fase 1: cada contribuição recebe UMA classe, "elegivel", "excluida" ou "incerta", por todos os filtros que não
    # dependem do somatório: datas e ingresso no vínculo, competência até o fato gerador, data do recolhimento (§§4º
    # e 5º), pendência, doméstico anterior a 06/2015 e a exceção do CI prestador. Um filtro que exclui vence um que
    # deixa incerta.
    # Fase 2: a contribuição mínima do mês (§7º) soma só as elegíveis; se só se atinge contando uma incerta (ou um
    # recolhimento em atraso, que o art. 27, II, pode tirar da carência), a competência fica incerta; uma excluída
    # nunca entra em soma alguma.
    validas, incertas, data_car, eventos = {}, {}, {}, []

    def incerta(m, rot, motivo):
        """Competência que depende de dado ausente ou não conferível. Fora da conta, salvo no modo presumir."""
        if presumir:
            return False
        incertas.setdefault(m, motivo)
        excluidas.append({**rot, "motivo": motivo, "classe": "incerta"})
        return True

    def classificar(v, c, pend_vinc):
        """Fase 1: (classe, motivo) da contribuição, sem olhar o somatório do mês."""
        m = c["mes"]
        fim_v = v["fim"] or ref
        if not (mes(v["inicio"]) <= m <= mes(fim_v)):
            return "excluida", "fora das datas do vínculo"
        # Filiação: a competência não vale antes do ingresso na atividade (Lei 8.213, arts. 15 e 27, I).
        if inicio_efetivo(v, m) > ref:
            return "excluida", (f"ingresso no vínculo em {v['inicio'].isoformat()}, depois da data de referência "
                                f"({ref.isoformat()}): sem filiação no fato gerador (Lei 8.213, arts. 15 e 27, I)")
        if c.get("lacuna"):
            return "incerta", (f"[VERIFICAR] competência {mes_txt(m)} do vínculo sem registro na entrada: "
                               f"recolhimento presumido ({PRESUMIDO}), salário de contribuição não informado")
        duvidas = []
        # D1: o efeito do indicador vem dos esclarecimentos da sigla no Anexo V, não do tipo CsPendencia.
        pend = [s for s in c["indicadores"] if s in pendencias] + pend_vinc
        if pend:
            duvidas.append(f"[VERIFICAR] indicador {', '.join(pend)} (CsPendencia): o efeito na carência é o dos "
                           f"esclarecimentos da sigla no Anexo V, não fechado no script ({FUND['indicadores']}; "
                           "IN 128, art. 185, §3º)")
        # CI prestador a PJ desde 04/2003 (leitura alternativa): recolhimento presumido e cômputo da atividade
        # comprovada ainda que sem contribuição (IN 128, arts. 189, §1º, e 193, II): nem a data ausente nem o
        # pagamento depois do fato gerador o excluem.
        prest = prestador and v["origem"] == "contribuinte-individual" and m >= (2003, 4)
        if v["origem"] in ORIGENS_ATRASO and not prest:
            if apos_fato_gerador(c):
                return "excluida", (f"recolhida em {c['recolhido_em'].isoformat()}, depois da data de referência "
                                    f"({FUND['apos_fato_gerador']})")
            if c["recolhido_em"] is None:
                duvidas.append("[VERIFICAR] data de recolhimento ausente: atraso não conferido (art. 27, II)")
            elif m < VENCIMENTO_DIA_15_DESDE:
                marcar_fora("vencimento-dia-15", m, "competencia")
                duvidas.append(f"[VERIFICAR] competência {mes_txt(m)} anterior a 01/1993: vencimento anterior à Lei "
                               "8.620/1993 fora da cobertura do script (COBERTURA, vencimento-dia-15); atraso não "
                               "conferido")
        if v["origem"] == "domestico" and m < DOMESTICO_PRESUMIDO_DESDE and not dom_comprovado(v):
            # Antes de 06/2015 o recolhimento do doméstico não é presumido (IN 128, art. 189, §2º); filiado de
            # 25/07/1991 a 31/05/2015, a carência só corre da 1ª contribuição sem atraso (art. 190).
            if apos_fato_gerador(c):
                return "excluida", (f"recolhida em {c['recolhido_em'].isoformat()}, depois da data de referência "
                                    f"({FUND['apos_fato_gerador']})")
            if c["recolhido_em"] is None:
                duvidas.append(f"[VERIFICAR] doméstico, competência {mes_txt(m)} anterior a 06/2015: recolhimento "
                               f"não presumido e data de recolhimento ausente; 1ª contribuição sem atraso não "
                               f"conferida ({FUND['domestico']})")
            elif domestico_sujeito_atraso(v) and m < DOMESTICO_VENCIMENTO_DESDE:
                marcar_fora("vencimento-dia-15", m, "competencia")
                duvidas.append(f"[VERIFICAR] doméstico, competência {mes_txt(m)}: vencimento anterior à Lei "
                               f"8.620/1993 não fechado em context/lei/; atraso não conferido ({FUND['domestico']})")
        if duvidas:
            return "incerta", duvidas[0]
        return "elegivel", None

    def em_atraso(v, c):
        """Recolhimento em atraso que o art. 27, II (ou o art. 190 do doméstico) pode tirar da carência."""
        if c["recolhido_em"] is None or em_dia(c):
            return False
        if v["origem"] in ORIGENS_ATRASO:
            return not (prestador and v["origem"] == "contribuinte-individual" and c["mes"] >= (2003, 4))
        return (v["origem"] == "domestico" and c["mes"] < DOMESTICO_PRESUMIDO_DESDE and domestico_sujeito_atraso(v)
                and not dom_comprovado(v))

    # Fase 1.
    classificadas, por_mes = [], {}
    for v in e["vinculos"]:
        pend_vinc = [s for s in v["indicadores"] if s in pendencias]
        fim_v = v["fim"] or ref
        # Regra 2: mês do vínculo sem competência na entrada. Para o empregado e o avulso (e o doméstico desde
        # 06/2015) o recolhimento é presumido (IN 128, art. 189, §§1º e 2º): o mês fica incerto, não ausente.
        informados = {c["mes"] for c in v["competencias"]}
        sinteticas = []
        m_, ate_ = mes(v["inicio"]), mes(min(fim_v, ref))
        while m_ <= ate_:
            if m_ not in informados and (v["origem"] in ("empregado", "avulso")
                                         or (v["origem"] == "domestico" and (m_ >= (2015, 6) or dom_comprovado(v)))):
                sinteticas.append({"mes": m_, "valor": None, "recolhido_em": None, "indicadores": [],
                                   "lacuna": True})
            m_ = somar_meses(m_, 1)
        for c in sorted(v["competencias"] + sinteticas, key=lambda c: c["mes"]):
            if c["mes"] > mes(ref):
                continue
            classe, motivo = classificar(v, c, pend_vinc)
            if classe == "incerta" and presumir:
                classe = "elegivel"   # só no modo presumir: a incerta conta como válida e em dia
            item = {"v": v, "c": c, "rot": {"competencia": mes_txt(c["mes"]), "vinculo": v["i"]},
                    "classe": classe, "motivo": motivo,
                    # Entra no somatório regular só a elegível com valor e sem atraso; a incerta e a atrasada ficam
                    # em soma à parte, que nunca completa o mínimo em silêncio.
                    "regular": classe == "elegivel" and (presumir or not em_atraso(v, c))}
            classificadas.append(item)
            if classe != "excluida":
                por_mes.setdefault(c["mes"], []).append(item)

    # Fase 2: somatório e contribuição mínima.
    aceitas = []
    for it in classificadas:
        v, c, rot, m = it["v"], it["c"], it["rot"], it["c"]["mes"]
        if it["classe"] == "excluida":
            excluidas.append({**rot, "motivo": it["motivo"], "classe": "excluida"})
            continue
        if it["classe"] == "incerta":
            incerta(m, rot, it["motivo"])
            continue
        if c.get("lacuna"):
            aceitas.append((v, c, rot))   # só no modo presumir: válida e em dia
            continue
        # Contribuição mínima (IN 128, art. 189, caput e §7º): o empregado, o doméstico e o avulso com atividade
        # iniciada antes de 14/11/2019 contam até 11/2019 mesmo abaixo do mínimo (§8º); o CI e o facultativo, nunca
        # (§9º). Valor ausente não prova o mínimo; mínimo ausente da tabela não o confere.
        isento = v["origem"] in ORIGENS_SEM_MINIMO_ATE_2019 and m <= (2019, 11) and v["inicio"] < MARCO_MINIMO
        if not isento:
            sm = salario_minimo(m)
            outros = [o for o in por_mes.get(m, []) if o is not it]
            total = (c["valor"] or Decimal(0)) + sum((o["c"]["valor"] for o in outros
                                                      if o["regular"] and o["c"]["valor"] is not None), Decimal(0))
            pendente = sum((o["c"]["valor"] for o in outros if not o["regular"] and o["c"]["valor"] is not None),
                           Decimal(0))
            aberto = (" (há vínculo concomitante sem valor no mês)"
                      if any(o["c"]["valor"] is None and not o["c"].get("lacuna") for o in outros) else "")
            if c["valor"] is None:
                if incerta(m, rot, f"[VERIFICAR] salário de contribuição de {mes_txt(m)} não informado: "
                                   f"contribuição mínima não conferida ({FUND['minimo']})"):
                    continue
            elif sm is None:
                if incerta(m, rot, f"[VERIFICAR] salário mínimo de {mes_txt(m)} ausente de "
                                   f"scripts/data/salario-minimo.json: valor {c['valor']} não conferido "
                                   f"contra a contribuição mínima ({FUND['minimo']})"):
                    continue
            elif total < sm[1] and pendente and total + pendente >= sm[1]:
                if incerta(m, rot, f"[VERIFICAR] remunerações regulares de {mes_txt(m)} somam {total}, abaixo do "
                                   f"mínimo {sm[1]}; só com {pendente} de contribuição incerta (pendência, "
                                   f"recolhimento não conferido ou em atraso do art. 27, II) o mínimo se atinge "
                                   f"({FUND['indicadores']}; IN 128, arts. 17, 18 e 189, §§4º e 5º; "
                                   f"{FUND['somatorio']})"):
                    continue
            elif total < sm[0]:
                if incerta(m, rot, f"[VERIFICAR] remunerações de {mes_txt(m)} somam {total}, abaixo do mínimo "
                                   f"{sm[0]}{aberto}, sem complementação informada ({FUND['minimo']}; "
                                   f"{FUND['somatorio']})"):
                    continue
            elif total < sm[1]:
                if incerta(m, rot, f"[VERIFICAR] salário mínimo mudou dentro de {mes_txt(m)} ({sm[0]} → {sm[1]}) e "
                                   f"as remunerações do mês somam {total}, entre os dois{aberto}: contribuição "
                                   f"mínima não conferida ({FUND['minimo']}; {FUND['somatorio']})"):
                    continue
        aceitas.append((v, c, rot))

    # 2ª passada: eventos da qualidade. O atraso é analisado pela data do recolhimento (IN 128, art. 185, §6º,
    # e art. 192, §3º).
    for v, c, rot in aceitas:
        m = c["mes"]
        atrasada = v["origem"] in ORIGENS_ATRASO and not em_dia(c)
        if prestador and v["origem"] == "contribuinte-individual" and m >= (2003, 4):
            atrasada = False   # leitura do CI prestador a PJ (IN 128, arts. 185, §5º, e 191, parágrafo único)
        # Carência do doméstico filiado de 25/07/1991 a 31/05/2015: da 1ª contribuição sem atraso (IN 128, art. 190).
        # A qualidade dele não se desloca para a data do pagamento (é empregado: Lei 8.213, art. 27, I).
        dom = (v["origem"] == "domestico" and m < DOMESTICO_PRESUMIDO_DESDE and domestico_sujeito_atraso(v)
               and not dom_comprovado(v))
        eventos.append({"competencia": m, "vinculo": v["i"], "origem": v["origem"], "por_pagamento": atrasada,
                        "grupo_atraso": "ci" if v["origem"] in ORIGENS_ATRASO else ("dom" if dom else None),
                        "atraso_carencia": atrasada or (dom and not em_dia(c)),
                        "data": c["recolhido_em"] if atrasada else inicio_efetivo(v, m),
                        "mes": mes(c["recolhido_em"]) if atrasada else m, "v": v, "rot": rot, "cadeia": None})

    for v in e["vinculos"]:
        fim_v = v["fim"] or ref
        meses_v = {c["mes"] for c in v["competencias"]}
        # lacunas: meses do vínculo sem competência informada
        m, ate = mes(v["inicio"]), mes(min(fim_v, ref))
        sem = []
        while m <= ate:
            if m not in meses_v:
                sem.append(mes_txt(m))
            m = somar_meses(m, 1)
        if sem:
            lacunas.append({"vinculo": v["i"], "meses_sem_competencia": sem})
        if v["fim"] is None:
            lacunas.append({"vinculo": v["i"], "sem_data_de_fim": True})

    # ---- graça e perda da qualidade (Lei 8.213, art. 15; Decreto 3.048, art. 14)
    if e["dias_sem"] is None:
        alertas.append("Vencimento pelo calendário de feriados nacionais" + ("" if cal.ok else " (tabela do motor "
                       "de prazos ausente: só fins de semana)") + "; feriado local e dia sem expediente bancário "
                       "não foram considerados. Informe dias_sem_expediente_bancario se houver.")

    # r8 (QA final, A01) — IN 128, art. 184, §4º: a prorrogação de +12 exige MAIS de 120 contribuições sem perda na
    # primeira aquisição; adquirida em bloco anterior e perdida a qualidade, volta na outra oportunidade com 120 NOVAS
    # contribuições sem perda (segunda parte). `reaq` diz se o bloco é essa outra oportunidade.
    def prorroga(n_sem_perda, reaq):
        return n_sem_perda >= 120 if reaq else n_sem_perda > 120

    def perda_apos(c, n_sem_perda, desemprego, facultativo, alertas_, reaq=False):
        graca = 6 if facultativo else 12
        if not facultativo:
            graca += 12 if prorroga(n_sem_perda, reaq) else 0
            graca += 12 if desemprego else 0
        fim_graca = somar_meses(c, graca)
        seguinte = somar_meses(fim_graca, 1)
        venc_nom = dt.date(*somar_meses(seguinte, 1), 15)
        venc = cal.vencimento(venc_nom, alertas_)
        return graca, fim_graca, seguinte, venc_nom, venc, venc + dt.timedelta(days=1)

    # Cadeias sem perda da qualidade, pela data efetiva de cada evento: o ingresso no vínculo (não o 1º dia
    # da competência, art. 27-A) ou, no atraso, a data do recolhimento (IN 128, art. 185, §6º).
    # r9 — IN 128, art. 184, §7º: o segurado obrigatório que passa a facultativo durante a graça usufrui a graça
    # da condição anterior, se mais vantajosa. A cadeia guarda cada estado (último mês, facultativo, contribuições
    # sem perda) já garantido; a perda é a do estado mais vantajoso, nunca encurtada pela mudança de categoria.
    class Cadeia:
        def __init__(self, reaq=False):
            self.eventos, self.comps, self.ultimo, self.fac = [], set(), None, True
            self.estados = []
            self.reaq = reaq   # prorrogação já adquirida em bloco anterior, seguida de perda (art. 184, §4º)

        def adquiriu(self):
            """O bloco completou as contribuições que dão a prorrogação (mais de 120; 120 novas na reaquisição)."""
            return prorroga(len(self.comps), self.reaq)

        def add(self, ev):
            self.eventos.append(ev)
            self.comps.add(ev["competencia"])
            fac = ev["origem"] == "facultativo"
            if self.ultimo is None or ev["mes"] > self.ultimo:
                self.ultimo, self.fac = ev["mes"], fac
            elif ev["mes"] == self.ultimo:
                self.fac = self.fac and fac
            self.estados.append((self.ultimo, self.fac, len(self.comps)))

        def melhor(self, desemprego=False):
            """(último mês, facultativo, contribuições sem perda) do estado de perda mais tardia (§7º)."""
            return max(self.estados, key=lambda st: (perda_apos(st[0], st[2], desemprego, st[1], [], self.reaq)[-1],
                                                     st == self.estados[-1]))

        def perda(self):
            u, f, n = self.melhor()
            return perda_apos(u, n, False, f, [], self.reaq)[-1]

    def fora_da_perda(c_, n_, fac_, desemprego_, perdeu, afeta, reaq_=False):
        """r12, COBERTURA: a perda (ou a graça) apurada por regra fora do intervalo vigente. A competência seguinte ao
        fim da graça anterior a 01/1993 tem vencimento fora da cobertura; a perda cuja graça alcança a janela da MP
        905/2019 pode não ter ocorrido pela redação daquela MP (que só prorrogava a qualidade)."""
        _, _, seguinte_, _, _, perda_ = perda_apos(c_, n_, desemprego_, fac_, [], reaq_)
        if seguinte_ < VENCIMENTO_DIA_15_DESDE:
            marcar_fora("vencimento-dia-15", seguinte_, "competencia", afeta)
        inicio_graca = dt.date(*somar_meses(c_, 1), 1)
        if perdeu and inicio_graca <= JANELA_MP905[1] and perda_ >= JANELA_MP905[0]:
            marcar_fora("qualidade-art15-ate-2018", perda_, "perda", afeta)

    cadeias, atual = [], Cadeia()
    for ev in sorted(eventos, key=lambda x: (x["data"], x["competencia"])):
        quebra = bool(atual.eventos) and ev["data"] >= atual.perda()
        if quebra:
            u_, f_, n_ = atual.melhor()
            # Quebra de cadeia: decide só a carência (art. 27-A); a qualidade na referência é a da última cadeia.
            fora_da_perda(u_, n_, f_, False, True, ("carencia",), atual.reaq)
        if (quebra or not atual.eventos) and ev["por_pagamento"] and ev["origem"] == "facultativo":
            # r15 — IN 128, art. 4º, parágrafo único: a filiação do facultativo decorre do primeiro recolhimento SEM
            # atraso. Sem qualidade em curso (nenhum bloco ainda, ou depois da perda, art. 185, §2º), o pagamento em
            # atraso não filia: não conta para a qualidade nem para a carência.
            momento = "depois da perda da qualidade" if quebra else "sem filiação anterior (primeiro recolhimento)"
            excluidas.append({"competencia": mes_txt(ev["competencia"]), "vinculo": ev["vinculo"],
                              "motivo": f"facultativo: recolhida em atraso em {ev['data'].isoformat()}, {momento}; "
                                        f"o recolhimento em atraso não gera filiação nem conta para a qualidade ou a "
                                        f"carência (IN 128, art. 4º, parágrafo único, e art. 185, §2º)",
                              "classe": "fora_da_qualidade"})
            ev["sem_filiacao"] = True
            continue
        if quebra:
            cadeias.append(atual)
            # Depois da perda, o bloco seguinte é a "outra oportunidade" se a prorrogação já foi adquirida em algum
            # bloco anterior; adquirida uma vez, toda reaquisição posterior pede 120 novas (art. 184, §4º).
            atual = Cadeia(atual.reaq or atual.adquiriu())
        ev["cadeia"] = len(cadeias)
        atual.add(ev)
    if atual.eventos:
        cadeias.append(atual)

    # ---- competências da carência. Art. 27, II, da Lei 8.213 e IN 128, arts. 191 e 192: para o CI, o
    # facultativo e o especial que contribui, a carência corre do primeiro recolhimento sem atraso; depois da
    # perda da qualidade, de nova contribuição sem atraso. O marco é do segurado em cada bloco sem perda, nunca
    # de cada vínculo do JSON: dividir os mesmos recolhimentos em vínculos não muda a carência.
    # O doméstico tem marco próprio (grupo "dom"): o recolhimento em dia do CI não abre a carência dele.
    primeiro_em_dia = {}
    for ev in eventos:
        if ev["cadeia"] is not None and ev["grupo_atraso"] and not ev["atraso_carencia"]:
            k = (ev["cadeia"], ev["grupo_atraso"])
            primeiro_em_dia[k] = min(primeiro_em_dia.get(k, ev["competencia"]), ev["competencia"])
    houve_atraso = False
    for ev in eventos:
        m, v, rot = ev["competencia"], ev["v"], ev["rot"]
        if ev.get("sem_filiacao"):
            continue   # já excluída acima: o atraso do facultativo sem qualidade em curso não filia (r15)
        if ev["atraso_carencia"]:
            marco = (primeiro_em_dia.get((ev["cadeia"], ev["grupo_atraso"])) if ev["cadeia"] is not None
                     else None)
            if marco is None or m < marco:
                houve_atraso = houve_atraso or ev["origem"] == "contribuinte-individual"
                excluidas.append({**rot, "motivo": "recolhida com atraso, anterior ao primeiro pagamento "
                                                   f"sem atraso do bloco sem perda ({FUND['atraso']}; IN 128, arts. "
                                                   f"191 e 192); conta só para a qualidade de segurado "
                                                   f"({FUND['qualidade_atraso']})",
                                  "classe": "so_qualidade"})
                continue
        validas.setdefault(m, v)
        data_car[m] = min(data_car.get(m, inicio_efetivo(v, m)), inicio_efetivo(v, m))
    for m in list(incertas):
        if m in validas:   # outro vínculo cobre o mês com competência válida
            incertas.pop(m)
    if houve_atraso:
        alertas.append("[VERIFICAR] Competências de contribuinte individual excluídas por atraso: a conta presume "
                       "recolhimento por conta própria. O CI prestador de serviço a pessoa jurídica desde 04/2003 "
                       "não se sujeita à regra (IN 128, art. 191, parágrafo único, e art. 192, §1º); a leitura dele "
                       "é refeita à parte e, se mudar o veredito, a conta sai aberta.")
    meses = sorted(validas)

    qualidade = None
    qual_aberta = None
    perdeu_antes_da_ref = False
    if cadeias:
        ultima = cadeias[-1]
        c, fac, n_sem_perda = ultima.melhor(e["desemprego"])
        if (c, fac, n_sem_perda) != (ultima.ultimo, ultima.fac, len(ultima.comps)):
            memoria.append(f"Qualidade: a graça da condição anterior (última competência obrigatória {mes_txt(c)}) "
                           f"é mais vantajosa que a do facultativo de {mes_txt(ultima.ultimo)} e prevalece "
                           f"({FUND['graca_anterior']}).")
        reaq = ultima.reaq
        graca, fim_graca, seguinte, venc_nom, venc, data_perda = perda_apos(c, n_sem_perda, e["desemprego"], fac,
                                                                           alertas, reaq)
        mantem = ref < data_perda
        fora_da_perda(c, n_sem_perda, fac, e["desemprego"], not mantem, ("qualidade",), reaq)
        if not e["historico"] and len(cadeias) == 1 and not mantem and not fac and n_sem_perda <= 120:
            # Regra 2: sem o histórico anterior, contribuições não informadas antes do 1º bloco podem somar mais de
            # 120 sem perda e dar +12 meses de graça (Lei 8.213, art. 15, §1º). Se isso mantém a qualidade, aberta.
            perda_120 = perda_apos(c, 121, e["desemprego"], fac, [])[-1]
            if ref < perda_120:
                mantem = "indeterminada"
                qual_aberta = {
                    "expressao": "graça = 12 meses (+12 se mais de 120 contribuições sem perda, §1º; +12 com "
                                 "desemprego registrado, §2º); perda no dia seguinte ao vencimento da competência "
                                 "seguinte ao fim da graça",
                    "contas": {"contribuicoes_sem_perda_informadas": n_sem_perda, "data_perda_ate_120": data_perda.isoformat(),
                               "data_perda_mais_de_120": perda_120.isoformat()},
                    "faltando": ["competências anteriores ao primeiro bloco informado (historico_anterior_informado = "
                                 "false): se somam mais de 120 contribuições sem perda ou, com prorrogação adquirida "
                                 "em bloco anterior e perdida a qualidade, se o bloco informado tem 120 novas "
                                 "(IN 128, art. 184, §4º)"],
                    "instrucao": "context/calculo-cnis.md, seção 1.2."}
                alertas.append("[VERIFICAR] Histórico anterior não informado: com mais de 120 contribuições sem perda "
                               "(art. 15, §1º) a qualidade se manteria até " + perda_120.isoformat() + ".")
        pagas = [ev for ev in ultima.eventos if ev["por_pagamento"]]
        if pagas:
            memoria.append("Qualidade: recolhimento em atraso antes do fato gerador conta pela data do pagamento "
                           f"({FUND['qualidade_atraso']}): " + "; ".join(
                               f"{mes_txt(ev['competencia'])} paga em {ev['data'].isoformat()}" for ev in pagas))
        qualidade = {"ultima_competencia": mes_txt(c), "contribuicoes_sem_perda": n_sem_perda,
                     "graca_meses": graca, "fim_da_graca": mes_txt(fim_graca),
                     "competencia_seguinte": mes_txt(seguinte), "vencimento_nominal": venc_nom.isoformat(),
                     "vencimento": venc.isoformat(), "data_perda": data_perda.isoformat(),
                     "mantem_qualidade_na_data_referencia": mantem,
                     "recolhimentos_em_atraso_pela_data": [{"competencia": mes_txt(ev["competencia"]),
                                                            "recolhido_em": ev["data"].isoformat()} for ev in pagas],
                     "prorrogacao_reaquisicao": reaq,
                     "fundamento": f"{FUND['graca']}; {FUND['perda_data']}; {FUND['vencimento']}"
                                   + (f"; {FUND['reaquisicao']}" if reaq else "")
                                   + (f"; {FUND['qualidade_atraso']}" if pagas else "")}
        regra_120 = ("reaquisição, prorrogação adquirida em bloco anterior: 120 novas bastam, "
                     f"{FUND['reaquisicao']}" if reaq else "primeira aquisição: exige mais de 120")
        memoria.append(f"Qualidade: último mês considerado {mes_txt(c)}; {n_sem_perda} contribuições sem perda "
                       f"({regra_120}; {'+12' if prorroga(n_sem_perda, reaq) and not fac else 'sem +12'}); "
                       f"desemprego registrado = {e['desemprego']}; graça {graca} meses até {mes_txt(fim_graca)}; "
                       f"competência seguinte {mes_txt(seguinte)}; vencimento {venc.isoformat()}"
                       f"{' (dia 15 sem expediente)' if venc != venc_nom else ''}; perda em {data_perda.isoformat()}")
        if len(cadeias) > 1:
            perdeu_antes_da_ref = True
            memoria.append(f"Perda da qualidade no histórico: {len(cadeias)} blocos de contribuição; o último começa "
                           f"em {ultima.eventos[0]['data'].isoformat()} (data efetiva de ingresso ou de recolhimento, "
                           f"{FUND['perda']})")
            if e["desemprego"]:
                alertas.append("[VERIFICAR] desemprego_registrado foi aplicado só à última cessação; nas perdas "
                               "anteriores do histórico a graça foi contada sem ele.")
        if not mantem:
            alertas.append(f"Na data de referência ({ref.isoformat()}) a qualidade de segurado já estava perdida "
                           f"desde {data_perda.isoformat()}.")
        if incertas:
            alertas.append("[VERIFICAR] Competências incertas também ficaram fora da qualidade de segurado: "
                           + ", ".join(mes_txt(m) for m in sorted(incertas)) + ".")
    elif ben == "bpc":
        alertas.append("BPC: benefício assistencial, sem carência e sem exigir vínculo nem qualidade de segurado "
                       "(LOAS, art. 20).")
    else:
        alertas.append("Nenhuma competência válida: qualidade de segurado não apurada.")

    # ---- carência exigida
    if ben in ("pensao", "auxilio-acidente", "bpc"):
        exigidas, fund_ex = 0, (FUND["dispensa"] if ben != "bpc" else "Lei 8.742, art. 20 (assistencial)")
    elif ben == "salario-maternidade":
        exigidas, fund_ex = 0, FUND["maternidade"]
    elif ben == "incapacidade":
        exigidas, fund_ex = (0, FUND["dispensa"]) if e["dispensa"] else (12, "Lei 8.213, art. 25, I")
    elif ben == "auxilio-reclusao":
        exigidas, fund_ex = 24, "Lei 8.213, art. 25, IV"
    else:
        exigidas, fund_ex = 180, "Lei 8.213, art. 25, II"
    # Art. 142: inscrito até 24/07/1991 (ou rural da Previdência Social Rural) tem a carência da tabela pelo ano em
    # que implementou todas as condições. Sem a inscrição ou sem o ano, os candidatos possíveis vão para a conta e,
    # se mudam o veredito, ela sai aberta (regra 2).
    cand142, info142 = {exigidas}, None
    if ben in APOSENTADORIAS:
        inscrito = e["inscrito_1991"]
        origem_inscrito = "informado"
        if inscrito is None:
            if any(v["inicio"] <= INSCRICAO_142 for v in e["vinculos"]):
                inscrito, origem_inscrito = True, "vínculo iniciado até 24/07/1991"
            elif e["historico"] and e["vinculos"]:
                inscrito, origem_inscrito = False, "inferido do histórico completo (1º vínculo depois de 24/07/1991)"
            else:
                origem_inscrito = "não informado (histórico anterior não informado)"
        # Sem o ano, qualquer linha é possível: as condições (a idade, por exemplo) podem ser implementadas depois
        # da data de referência, e o ano mais recente da tabela (2011 em diante) exige 180.
        anos = ([e["ano_impl"]] if e["ano_impl"] is not None
                else (list(range(1991, max(ref.year, 2011) + 1)) if ref.year >= 1991 else [ref.year]))
        tabela = {a: exigidas_142(a) for a in anos}
        # r14: lista própria; `fora` acumula a COBERTURA de todos os ramos e não pode ser sobrescrita aqui.
        anos_fora142 = [a for a, x in tabela.items() if x is None]
        if inscrito is True:
            cand142 = {x for x in tabela.values() if x is not None}
        elif inscrito is None:
            cand142 = {180} | {x for x in tabela.values() if x is not None}
        if inscrito is False and e["inscrito_1991"] is None:
            alertas.append("Carência de 180 (art. 25, II): o histórico informado começa depois de 24/07/1991. "
                           "Trabalhador ou empregador rural coberto pela Previdência Social Rural antes disso tem "
                           f"a tabela do {FUND['art142']}: informe inscrito_ate_24_07_1991 se for o caso.")
        if inscrito is not False:
            info142 = {"inscrito_ate_24_07_1991": inscrito, "origem": origem_inscrito,
                       "ano_implementacao_requisitos": e["ano_impl"], "fora_da_tabela": anos_fora142,
                       "candidatos": sorted(cand142)}
        if len(cand142) == 1 and not anos_fora142:
            exigidas = next(iter(cand142))
            if inscrito is True:
                fund_ex = f"{FUND['art142']} (inscrito até 24/07/1991; condições implementadas em {e['ano_impl']})"
        else:
            exigidas = max(cand142) if cand142 else 180
    if e["dispensa"] and ben != "incapacidade":
        alertas.append("acidente_ou_doenca_dispensa só tem efeito no benefício por incapacidade (art. 26, II).")

    # ---- carência contada
    total = len(meses)
    # Novas: competências da carência que começam a valer na última refiliação ou depois (art. 27-A).
    inicio_ultima = cadeias[-1].eventos[0]["data"] if cadeias else None
    novas = sum(1 for m in meses if inicio_ultima and data_car[m] >= inicio_ultima) if perdeu_antes_da_ref else total
    anteriores = total - novas
    carencia = {"exigidas": exigidas, "fundamento_exigidas": fund_ex}
    cumprida, codigo, formula = None, EXIT_OK, None

    def veredito(n):
        return "sim" if n >= exigidas else "nao"

    if exigidas == 0:
        contadas, cumprida = total, "sim"
        memoria.append(f"Carência dispensada ou inexistente ({fund_ex}).")
    elif perdeu_antes_da_ref and ben in BENEFICIOS_27A and regime_27a(ref):
        # r12: a fração é a do regime do fato gerador (REGIMES_27A; IN 128, art. 200), não a metade de 2019 aplicada
        # a fato anterior.
        reg = regime_27a(ref)
        metade = Decimal(exigidas * reg["fracao"][0]) / reg["fracao"][1]
        metade_out = int(metade) if metade == int(metade) else str(metade)
        carencia.update({"novas_desde_refiliacao": novas, "limiar_exigido": metade_out,
                         "regime_perda": {"fracao": reg["rotulo"], "norma": reg["norma"],
                                          "desde": reg["desde"].isoformat(),
                                          "ate": reg["ate"].isoformat() if reg["ate"] else None,
                                          "fonte": "IN 128, art. 200, tabela por fato gerador"},
                         "anteriores": anteriores, "fundamento_perda": FUND["perda"]})
        if reg["rotulo"] == "1/2":
            carencia["metade_exigida"] = metade_out
        if novas >= metade:
            contadas = novas + anteriores
            carencia["anteriores_reaproveitadas"] = anteriores
        else:
            contadas = novas
            carencia["anteriores_reaproveitadas"] = 0
        cumprida = "sim" if novas >= metade and contadas >= exigidas else "nao"
        memoria.append(f"Após a perda ({reg['norma']}, fração {reg['rotulo']}): novas {novas} "
                       f"{'≥' if novas >= metade else '<'} {metade_out}; contadas {contadas} de {exigidas}")
    elif ben in APOSENTADORIAS:
        contadas = total

        def cump_apos(x):
            if perdeu_antes_da_ref and (total >= x) != (novas >= x):
                return "indeterminada"
            return "sim" if total >= x else "nao"

        por_exig = {x: cump_apos(x) for x in sorted(cand142)}
        if "indeterminada" in por_exig.values():
            alertas.append("[VERIFICAR] Perda da qualidade antes da data de referência numa aposentadoria: o "
                           "art. 27-A não alcança o art. 25, II, e a regra da perda nessas espécies não está em "
                           "context/lei/. Contando tudo cumpre; contando só as novas, não. O advogado decide.")
            formula = {"expressao": "cumprida = contadas >= exigidas; contadas = todas as válidas OU só as "
                                    "posteriores à última perda",
                       "contas": {"todas": total, "so_novas": novas, "exigidas": exigidas},
                       "faltando": ["regra da perda da qualidade nas aposentadorias do art. 25, II"],
                       "instrucao": "context/calculo-cnis.md, seção 3."}
        fora142 = bool(info142 and info142["fora_da_tabela"])
        if len(set(por_exig.values())) == 1 and not fora142:
            cumprida = next(iter(por_exig.values()))
            if cumprida == "indeterminada":
                codigo = EXIT_FALTA
        else:
            cumprida, codigo = "indeterminada", EXIT_FALTA
            faltando = []
            if info142["inscrito_ate_24_07_1991"] is None:
                faltando.append("inscrito_ate_24_07_1991 (inscrição na Previdência Social Urbana até 24/07/1991 "
                                "ou rural coberto pela Previdência Social Rural)")
            if e["ano_impl"] is None:
                faltando.append("ano_implementacao_requisitos (ano em que o segurado implementou todas as "
                                "condições do benefício)")
            if fora142:
                faltando.append("regra anterior à Lei 8.213 (condições implementadas antes de 1991, fora da tabela "
                                "do art. 142)")
            alertas.append(f"[VERIFICAR] Carência da aposentadoria pela tabela do {FUND['art142']}: com {total} "
                           "competências o veredito depende da inscrição até 24/07/1991 e do ano em que as "
                           "condições foram implementadas, que a entrada não fecha. A conta sai aberta.")
            formula = {**(formula or {}), "art142": {
                "expressao": "inscrito até 24/07/1991 (ou rural): exigidas = tabela do art. 142 pelo ano de "
                             "implementação de todas as condições; senão, 180 (art. 25, II); cumprida = contadas "
                             ">= exigidas",
                "contas": {"contadas": total, "veredito_por_exigidas": {str(x): v for x, v in por_exig.items()},
                           "tabela_art_142": {str(a): x for a, x in TABELA_142.items()}},
                "faltando": faltando,
                "instrucao": "context/lei/lei-8213-1991.md, art. 142; context/calculo-cnis.md, seção 3."}}
        if info142:
            carencia["art142"] = info142
        if perdeu_antes_da_ref:
            carencia.update({"novas_desde_refiliacao": novas, "anteriores": anteriores})
    else:
        contadas = total
        cumprida = veredito(total)

    if not e["historico"] and cumprida == "nao":
        cumprida, codigo = "indeterminada", EXIT_FALTA
        alertas.append("Carência indeterminada: informe o CNIS anterior à perda da qualidade (o histórico anterior "
                       "não foi informado e as competências da entrada não bastam). O script não presume histórico.")
        formula = {"expressao": "contadas = novas + anteriores (se novas >= metade, art. 27-A) ; "
                                "cumprida = contadas >= exigidas",
                   "contas": {"novas": novas, "exigidas": exigidas},
                   "faltando": ["competências anteriores à perda da qualidade (CNIS completo)"],
                   "instrucao": "context/calculo-cnis.md, seções 1.1 e 4."}

    if qual_aberta:
        codigo = EXIT_FALTA
        formula = {**(formula or {}), "qualidade_mais_de_120_contribuicoes": qual_aberta}
    carencia.update({"contadas": contadas, "cumprida": cumprida,
                     "faltam": max(0, exigidas - contadas) if cumprida != "sim" else 0,
                     "excluidas": excluidas})
    memoria.append(f"Carência: {contadas} contadas de {exigidas} exigidas → {cumprida} ({FUND['carencia']})")

    # ---- indicadores
    indicadores, vistos = [], {}
    for v in e["vinculos"]:
        ocorr = [(s, None) for s in v["indicadores"]] + [(s, mes_txt(c["mes"])) for c in v["competencias"]
                                                         for s in c["indicadores"]]
        for s, comp in ocorr:
            chave = (s, v["i"])
            if chave in vistos:
                if comp:
                    vistos[chave]["competencias"].append(comp)
                continue
            linhas = tab_ind.get(s)
            if not linhas:
                item = {"sigla": s, "vinculo": v["i"], "tipo": None,
                        "descricao": "sigla não localizada no Anexo V", "efeito": "sem efeito automático; conferir "
                        "a sigla no extrato e no Anexo V", "competencias": [comp] if comp else []}
            else:
                desc = linhas[0]["descricao"] if len(linhas) == 1 else [l["descricao"] for l in linhas]
                tipo = linhas[0]["tipo"]
                if s == "IEAN":
                    efeito = EFEITO_IEAN
                elif tipo == "CsPendencia":
                    efeito = ("efeito na carência pelos esclarecimentos da sigla no Anexo V; sem efeito fechado "
                              "no script, a competência sai incerta com [VERIFICAR]")
                else:
                    efeito = "sem efeito automático na conta; ver esclarecimentos do Anexo V"
                item = {"sigla": s, "vinculo": v["i"], "tipo": tipo, "descricao": desc, "efeito": efeito,
                        "esclarecimentos": [l["esclarecimentos"] for l in linhas],
                        "pagina_pdf": [p for l in linhas for p in l.get("pagina_pdf", [])],
                        "competencias": [comp] if comp else []}
            vistos[chave] = item
            indicadores.append(item)
    tem_iean = any(i["sigla"] == "IEAN" for i in indicadores)
    if tem_iean:
        alertas.append("Alerta pedindo PPP e LTCAT do período: o indicador IEAN aponta possível enquadramento "
                       f"especial, mas não converte o tempo sozinho ({FUND['iean']}; Anexo V, esclarecimentos do "
                       "IEAN). Sem a prova técnica, o tempo do vínculo é comum. Sufixos 15/20/25 não têm âncora "
                       "no Anexo V: não automatizar.")

    saida = {
        "versao": VERSAO,
        "parametros_usados": {
            "beneficio": ben, "data_referencia": ref.isoformat(), "historico_anterior_informado": e["historico"],
            "desemprego_registrado": e["desemprego"], "acidente_ou_doenca_dispensa": e["dispensa"],
            "dias_sem_expediente_bancario": (sorted(d.isoformat() for d in e["dias_sem"])
                                             if e["dias_sem"] is not None else None),
            "vinculos": [{"origem": v["origem"], "inicio": v["inicio"].isoformat(),
                          "fim": v["fim"].isoformat() if v["fim"] else None, "indicadores": v["indicadores"],
                          "competencias_informadas": len(v["competencias"])} for v in e["vinculos"]]},
        "carencia": carencia,
        "qualidade_segurado": qualidade,
        "indicadores": indicadores,
        "tempo_do_vinculo": "comum",
        "lacunas": lacunas,
        "regra": "Carência por competências válidas (sem pendência, sem atraso do art. 27, II, sem recolhimento "
                 "posterior à data de referência, IN 128, art. 189, §§4º e 5º), com a regra da "
                 "metade do art. 27-A após a perda; qualidade pela graça do art. 15 e perda no dia seguinte ao "
                 "vencimento do dia 15 (dia útil seguinte sem expediente).",
        "fonte": {"regras": FUND, "indicadores": fonte_ind,
                  "salario_minimo": "scripts/data/salario-minimo.json",
                  "feriados": "scripts/calc/data/feriados-nacionais.json (motor de prazos)"
                  if cal.ok else ("dias_sem_expediente_bancario da entrada" if e["dias_sem"] is not None
                                  else "ausente: só fins de semana")},
        "alertas": list(dict.fromkeys(alertas)),
        "memoria": memoria,
        "formula_aberta": formula,
        "_fora_da_cobertura": fora,
        "_perdeu_antes_da_ref": perdeu_antes_da_ref,
    }
    return codigo, saida, incertas


def _cobertura(e, codigo, saida):
    """r12 (revisão r11, BLOCKER 2): regra aplicada fora do intervalo em que é a vigente (COBERTURA) não fecha
    veredito. A carência e a qualidade ficam indeterminadas, o número exigido pela regra implementada sai à parte e a
    regra histórica, com a fonte, vai para formula_aberta.fora_da_cobertura (exit 3)."""
    fora = list(saida.pop("_fora_da_cobertura", []) or [])
    perdeu = saida.pop("_perdeu_antes_da_ref", False)
    ref, ben = e["data_referencia"], e["beneficio"]
    for linha in COBERTURA:
        if linha["chave"] != "data_referencia" or ben not in linha["beneficios"]:
            continue
        if linha["id"] == "perda-27A" and not perdeu:
            continue
        if not coberta(linha, ref):
            fora.append({**descrever_fora(linha, ref, "data_referencia"),
                         "afeta": ["carencia"] if linha["id"].startswith(("carencia-", "perda-")) else ["qualidade"]})
    if not fora:
        return codigo, saida
    car = saida["carencia"]
    car_fora = [x for x in fora if "carencia" in x["afeta"]]
    qual_fora = [x for x in fora if "qualidade" in x["afeta"]]
    if car_fora:
        car["exigidas_pela_regra_implementada"] = car.get("exigidas")
        car.update({"exigidas": None, "cumprida": "indeterminada", "faltam": None})
    qs = saida.get("qualidade_segurado")
    if qual_fora and qs:
        qs["data_perda_pela_regra_implementada"] = qs.get("data_perda")
        qs.update({"data_perda": None, "mantem_qualidade_na_data_referencia": "indeterminada"})
    aberta = dict(saida.get("formula_aberta") or {})
    aberta["fora_da_cobertura"] = {
        "expressao": "a regra vigente no fato gerador (ou na competência) decide; a implementada só vale dentro da "
                     "cobertura",
        "pontos": fora,
        "faltando": ["regra vigente na data de cada ponto listado (regra_historica), fora da cobertura do script"],
        "instrucao": "Refazer a conta pela regra histórica indicada, com a fonte de cada borda (COBERTURA do script)."}
    saida["formula_aberta"] = aberta
    saida["alertas"].append("[VERIFICAR] Regra aplicada fora do intervalo em que é a vigente: "
                            + "; ".join(f"{x['linha']} ({x.get('data_referencia') or x.get('perda') or x.get('competencia')})"
                                        for x in fora)
                            + ". A conta não fecha pela regra posterior: veja formula_aberta.fora_da_cobertura.")
    saida["memoria"].append("Fora da cobertura: " + ", ".join(x["linha"] for x in fora))
    return EXIT_FALTA, saida


# ------------------------------------------------------------ CLI

def build_parser():
    ap = argparse.ArgumentParser(
        prog="calc_previdenciario_cnis.py",
        description="CNIS: carência, qualidade de segurado e indicadores. Entrada JSON por --entrada ou stdin; "
                    "campos em context/calculo-cnis.md.")
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
        codigo, saida = tabela_ausente(err)
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
