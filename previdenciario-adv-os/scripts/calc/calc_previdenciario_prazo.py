#!/usr/bin/env python3
"""calc_prazo.py — Engine B: prazo processual (CPC, CLT, JEC, penal).

Conta a data-limite de um prazo a partir do marco (disponibilização no DJe,
consulta ou envio no portal, juntada do AR ou do mandado, edital, ciência
expressa), excluindo fins de semana, feriados nacionais, recesso e suspensões
informadas. Fontes e convenções em scripts/calc/README.md.

USO:
    python3 calc_prazo.py --entrada caso.json
    echo '{...}' | python3 calc_prazo.py

Saída: JSON no stdout. Exit 0 = calculado; 2 = entrada inválida.

Só biblioteca padrão, Python 3.9+, sem rede. Os feriados fixos vêm de
data/feriados-nacionais.json relativo a este arquivo (CLAUDE_PLUGIN_ROOT chega
vazio no Cowork); os móveis saem da Páscoa, calculada aqui. Feriado estadual,
municipal ou do tribunal é sempre entrada do usuário. --feriados troca o
arquivo; existe para os testes.
"""

import argparse
import calendar
import datetime as dt
import json
import sys
from pathlib import Path

VERSAO = "0.1.0"
EXIT_OK, EXIT_ENTRADA = 0, 2

ARQ_FERIADOS_PADRAO = Path(__file__).resolve().parent / "data" / "feriados-nacionais.json"

MEIOS = ("dje", "sistema", "ar", "oficial", "edital", "ciencia-expressa")
UNIDADES = ("uteis", "corridos", "meses", "anos")
RITOS = ("cpc", "clt", "jec", "penal")
MOTIVOS_DOBRO = ("fazenda", "mp", "defensoria", "litisconsortes-procuradores-distintos")
MARCOS_PORTAL = ("consulta", "envio")
NATUREZAS = ("processual", "material")
EXCECOES_RECESSO_PENAL = {   # CPP art. 798-A, incisos I a III (Lei 14.365/2022)
    "reu-preso": "inciso I: réu preso, nos processos vinculados à prisão",
    "maria-da-penha": "inciso II: procedimento regido pela Lei 11.340/2006 (Lei Maria da Penha)",
    "medida-urgente": "inciso III: medida considerada urgente por despacho fundamentado do juízo",
}
CAMPOS = {
    "marco", "meio", "prazo", "unidade", "rito", "dobro", "feriados_locais",
    "suspensoes", "uf", "incluir_pontos_forenses", "marco_portal", "processo_eletronico",
    "natureza", "excecao_recesso_penal",
}
OBRIGATORIOS = ("marco", "meio", "prazo", "unidade", "rito")

UM_DIA = dt.timedelta(days=1)
DIAS_SEMANA = ("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo")

VIGENCIA_CPC_2015 = dt.date(2016, 3, 18)
VIGENCIA_CLT_775_UTEIS = dt.date(2017, 11, 11)     # Lei 13.467/2017
VIGENCIA_JEC_12A = dt.date(2018, 11, 1)            # Lei 13.728/2018 (aprox., ver alerta)

ALERTA_FIXO = (
    "Conferir feriados locais e atos do tribunal (feriado estadual, municipal ou forense, "
    "suspensão de expediente, indisponibilidade do sistema — CPC art. 224 §1º) antes de "
    "confiar na data-limite."
)
ALERTA_LEI_14939 = (
    "Lei 14.939/2024 (CPC art. 1.003 §6º): o feriado local deve ser comprovado no ato de "
    "interposição do recurso; se não for, o tribunal manda corrigir o vício ou o desconsidera "
    "se a informação já constar do processo eletrônico. Junte o ato que o comprova."
)

FUNDAMENTO_COMECO = {
    "cpc": "CPC art. 224 caput: exclui o dia do começo e inclui o do vencimento",
    "jec": "CPC art. 224 caput: exclui o dia do começo e inclui o do vencimento",
    "clt": "CLT art. 775 caput: exclui o dia do começo e inclui o do vencimento",
    "penal": "CPP art. 798 §1º: não se computa o dia do começo; inclui-se o do vencimento",
}
FUNDAMENTO_CP_10 = (
    "CP art. 10: o dia do começo inclui-se no cômputo do prazo; contam-se os dias, os meses e os anos "
    "pelo calendário comum, sem prorrogação do vencimento e sem suspensão no recesso")
FUNDAMENTO_MEIO = {
    "ar": "CPC art. 231 I: dia do começo = juntada do aviso de recebimento",
    "oficial": "CPC art. 231 II: dia do começo = juntada do mandado cumprido",
    "edital": "CPC art. 231 IV: dia do começo = dia útil seguinte ao fim da dilação (o marco informado já é esse dia)",
    "ciencia-expressa": "CPC art. 231 (inciso conforme o ato; VIII na retirada dos autos): dia do começo = dia da ciência",
}


class EntradaInvalida(Exception):
    pass


# ------------------------------------------------------------------ entrada

def _data(campo, texto):
    if not isinstance(texto, str):
        raise EntradaInvalida(f"{campo}: esperado texto AAAA-MM-DD")
    try:
        return dt.date.fromisoformat(texto)
    except ValueError:
        raise EntradaInvalida(f"{campo}: data inválida '{texto}' (formato AAAA-MM-DD)")


def _opcao(campo, valor, opcoes):
    if valor not in opcoes:
        raise EntradaInvalida(f"{campo}: '{valor}' fora de {list(opcoes)}")
    return valor


def normaliza(bruto):
    if not isinstance(bruto, dict):
        raise EntradaInvalida("a entrada deve ser um objeto JSON")
    e = {k: v for k, v in bruto.items() if not k.startswith("_")}
    desconhecidos = sorted(set(e) - CAMPOS)
    if desconhecidos:
        raise EntradaInvalida(f"campo(s) desconhecido(s): {desconhecidos}")
    for k in OBRIGATORIOS:
        if e.get(k) is None:
            raise EntradaInvalida(f"{k}: obrigatório")

    out = {
        "marco": _data("marco", e["marco"]),
        "meio": _opcao("meio", e["meio"], MEIOS),
        "unidade": _opcao("unidade", e["unidade"], UNIDADES),
        "rito": _opcao("rito", e["rito"], RITOS),
    }
    if not dt.date(1990, 1, 1) <= out["marco"] <= dt.date(2100, 12, 31):
        raise EntradaInvalida("marco: fora do intervalo 1990–2100")
    prazo = e["prazo"]
    if isinstance(prazo, bool) or not isinstance(prazo, int) or not 1 <= prazo <= 3650:
        raise EntradaInvalida("prazo: inteiro entre 1 e 3650")
    out["prazo"] = prazo

    if out["rito"] == "penal" and out["unidade"] == "uteis":
        raise EntradaInvalida("rito penal conta em dias corridos (CPP art. 798 caput); use unidade 'corridos'")

    out["natureza"] = _opcao("natureza", e.get("natureza", "processual"), NATUREZAS)
    if out["natureza"] == "material" and out["unidade"] == "uteis":
        raise EntradaInvalida(
            "natureza 'material' não conta em dias úteis: o art. 219 do CPC (e o CLT art. 775, a Lei "
            "9.099 art. 12-A) só alcança prazo processual; prazo material conta em 'corridos', 'meses' ou 'anos'")
    if out["natureza"] == "processual" and out["unidade"] == "corridos" and out["rito"] != "penal":
        raise EntradaInvalida(
            f"rito '{out['rito']}' com unidade 'corridos' e natureza processual: prazo processual em dias "
            "conta só dias úteis (CPC art. 219; CLT art. 775; Lei 9.099 art. 12-A). Use 'uteis'; se o prazo "
            "for material (decadência, prescrição, prazo de direito material), informe natureza 'material'")

    exc = e.get("excecao_recesso_penal")
    if exc is not None:
        if out["rito"] != "penal":
            raise EntradaInvalida("excecao_recesso_penal: só se usa com rito 'penal' (CPP art. 798-A)")
        out["excecao_recesso_penal"] = _opcao("excecao_recesso_penal", exc, tuple(EXCECOES_RECESSO_PENAL))
    else:
        out["excecao_recesso_penal"] = None

    mp = e.get("marco_portal")
    if out["meio"] == "sistema":
        if mp is None:
            raise EntradaInvalida(
                "marco_portal: obrigatório no meio 'sistema' — 'consulta' (marco = dia da consulta) "
                "ou 'envio' (marco = dia do envio; ciência ao fim de 10 dias corridos, Lei 11.419 art. 5º §3º)")
        out["marco_portal"] = _opcao("marco_portal", mp, MARCOS_PORTAL)
    elif mp is not None:
        raise EntradaInvalida("marco_portal: só se usa com meio 'sistema'")

    dobro = e.get("dobro")
    if dobro is not None:
        if not isinstance(dobro, dict) or set(dobro) - {"motivo"} or "motivo" not in dobro:
            raise EntradaInvalida("dobro: esperado {\"motivo\": ...}")
        out["dobro"] = _opcao("dobro.motivo", dobro["motivo"], MOTIVOS_DOBRO)
    else:
        out["dobro"] = None

    pe = e.get("processo_eletronico")
    if pe is not None and not isinstance(pe, bool):
        raise EntradaInvalida("processo_eletronico: true ou false")
    out["processo_eletronico"] = pe
    if out["dobro"] == "litisconsortes-procuradores-distintos" and out["rito"] == "cpc" and pe is None:
        raise EntradaInvalida(
            "processo_eletronico: obrigatório com dobro de litisconsortes no CPC "
            "(art. 229 §2º: não há dobro em processo eletrônico)")

    ipf = e.get("incluir_pontos_forenses", True)
    if not isinstance(ipf, bool):
        raise EntradaInvalida("incluir_pontos_forenses: true ou false")
    out["incluir_pontos_forenses"] = ipf

    locais = {}
    fl = e.get("feriados_locais") or []
    if not isinstance(fl, list):
        raise EntradaInvalida("feriados_locais: lista de datas")
    for i, item in enumerate(fl):
        if isinstance(item, dict):
            if set(item) - {"data", "motivo"} or "data" not in item:
                raise EntradaInvalida(f"feriados_locais[{i}]: esperado data ou {{data, motivo}}")
            d = _data(f"feriados_locais[{i}].data", item["data"])
            motivo = str(item.get("motivo") or "feriado local informado")
        else:
            d = _data(f"feriados_locais[{i}]", item)
            motivo = "feriado local informado"
        locais[d] = motivo
    out["feriados_locais"] = locais

    susp = []
    sl = e.get("suspensoes") or []
    if not isinstance(sl, list):
        raise EntradaInvalida("suspensoes: lista de intervalos [inicio, fim]")
    for i, item in enumerate(sl):
        if isinstance(item, dict):
            if set(item) - {"inicio", "fim", "motivo"} or not {"inicio", "fim"} <= set(item):
                raise EntradaInvalida(f"suspensoes[{i}]: esperado [inicio, fim] ou {{inicio, fim, motivo}}")
            ini, fim, motivo = item["inicio"], item["fim"], item.get("motivo")
        elif isinstance(item, list) and len(item) == 2:
            ini, fim, motivo = item[0], item[1], None
        else:
            raise EntradaInvalida(f"suspensoes[{i}]: esperado [inicio, fim]")
        a, b = _data(f"suspensoes[{i}][0]", ini), _data(f"suspensoes[{i}][1]", fim)
        if b < a:
            raise EntradaInvalida(f"suspensoes[{i}]: fim antes do início")
        susp.append((a, b, str(motivo or "suspensão informada")))
    out["suspensoes"] = susp

    uf = e.get("uf")
    if uf is not None and (not isinstance(uf, str) or len(uf) != 2 or not uf.isalpha()):
        raise EntradaInvalida("uf: sigla de 2 letras")
    out["uf"] = uf.upper() if uf else None
    return out


# ------------------------------------------------------------------ calendário

def pascoa(ano):
    """Domingo de Páscoa (computus gregoriano anônimo, Meeus/Jones/Butcher)."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes_ = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(ano, mes_, dia)


class Calendario:
    def __init__(self, tabela, e):
        self.tabela = tabela
        self.locais = e["feriados_locais"]
        self.suspensoes = e["suspensoes"]
        self.incluir_pontos = e["incluir_pontos_forenses"]
        # Recesso de 20/12 a 20/01: CPC art. 220 e CLT art. 775-A em qualquer prazo processual (dias,
        # meses ou anos); no penal, CPP art. 798-A, salvo as exceções dos incisos I a III. Prazo
        # material não se suspende.
        self.aplica_recesso = e["natureza"] == "processual" and not e["excecao_recesso_penal"]
        self.fund_recesso = ("CPP art. 798-A (Lei 14.365/2022)" if e["rito"] == "penal"
                             else tabela["recesso"]["fundamento"])
        self.rec_ini = tuple(int(x) for x in tabela["recesso"]["inicio"].split("-"))
        self.rec_fim = tuple(int(x) for x in tabela["recesso"]["fim"].split("-"))
        self._anos = {}
        self.pontos_ignorados = {}    # ponto forense contado como útil (incluir_pontos_forenses=false)
        self.vistos = {}              # feriados efetivamente pulados: data -> registro

    def _do_ano(self, ano):
        if ano not in self._anos:
            dias = {}
            for f in self.tabela["fixos"]:
                vig = f.get("vigencia_desde")
                d = dt.date(ano, *(int(x) for x in f["mes_dia"].split("-")))
                if vig and d < dt.date.fromisoformat(vig):
                    continue
                dias[d] = f
            p = pascoa(ano)
            for f in self.tabela["moveis"]:
                dias[p + dt.timedelta(days=f["dias_da_pascoa"])] = f
            self._anos[ano] = dias
        return self._anos[ano]

    def feriado(self, d):
        """Motivo do feriado que fecha o dia, ou None."""
        if d in self.locais:
            self.vistos[d] = {"tipo": "local", "nome": self.locais[d]}
            return f"{self.locais[d]} (feriado local informado)"
        f = self._do_ano(d.year).get(d)
        if not f:
            return None
        if f["tipo"] in ("ponto-forense", "religioso") and not self.incluir_pontos:
            self.pontos_ignorados[d] = f
            return None
        self.vistos[d] = f
        return f"{f['nome']} — {f['fundamento']}"

    def nao_util(self, d):
        if d.weekday() == 5:
            return "sábado"
        if d.weekday() == 6:
            return "domingo"
        return self.feriado(d)

    def no_recesso(self, d):
        md = (d.month, d.day)
        return md >= self.rec_ini or md <= self.rec_fim

    def suspenso(self, d):
        for a, b, motivo in self.suspensoes:
            if a <= d <= b:
                return f"{motivo} (suspensão informada)"
        if self.aplica_recesso and self.no_recesso(d):
            return f"recesso forense 20/12 a 20/01 — {self.fund_recesso}"
        return None

    def bloqueio(self, d):
        """Motivo para não contar d como dia útil de prazo (suspensão ou não útil)."""
        motivos = [m for m in (self.suspenso(d), self.nao_util(d)) if m]
        return " + ".join(motivos) if motivos else None

    def util_ou_seguinte(self, d):
        while self.nao_util(d):
            d += UM_DIA
        return d

    def util_seguinte(self, d):
        return self.util_ou_seguinte(d + UM_DIA)


def soma_meses(d, meses):
    """CC art. 132 §3º e Lei 810/1949 art. 3º: dia de igual número; sem ele, o primeiro dia seguinte."""
    total = d.month - 1 + meses
    ano, mes_ = d.year + total // 12, total % 12 + 1
    ultimo = calendar.monthrange(ano, mes_)[1]
    if d.day <= ultimo:
        return dt.date(ano, mes_, d.day)
    return dt.date(ano, mes_, ultimo) + UM_DIA


def br(d):
    return d.strftime("%d/%m/%Y")


# ------------------------------------------------------------------ regras

def dia_do_comeco(e, cal, regras, alertas):
    """Dia excluído da contagem (intimação ou publicação considerada feita) e marcos."""
    marco, meio, rito = e["marco"], e["meio"], e["rito"]
    marcos = {"marco_informado": marco.isoformat(), "meio": meio}
    if meio == "dje":
        pub = cal.util_seguinte(marco)
        marcos["data_disponibilizacao"] = marco.isoformat()
        marcos["data_publicacao"] = pub.isoformat()
        regras.append(
            "Lei 11.419/2006 art. 4º §3º e CPC art. 224 §2º: considera-se publicado no primeiro dia "
            "útil seguinte ao da disponibilização no DJe")
        regras.append(
            "Lei 11.419/2006 art. 4º §4º e CPC art. 224 §3º: o prazo começa no primeiro dia útil "
            "seguinte ao da publicação")
        comeco = pub
    elif meio == "sistema":
        if e["marco_portal"] == "consulta":
            comeco = cal.util_ou_seguinte(marco)
            regras.append(
                "Lei 11.419/2006 art. 5º §§1º e 2º: intimação feita no dia da consulta ao portal; "
                "consulta em dia não útil vale no primeiro dia útil seguinte")
        else:
            fim10 = marco + dt.timedelta(days=10)
            comeco = cal.util_ou_seguinte(fim10)
            marcos["data_envio"] = marco.isoformat()
            marcos["fim_dos_10_dias"] = fim10.isoformat()
            regras.append(
                "Lei 11.419/2006 art. 5º §3º: sem consulta, a intimação se considera feita ao término "
                "de 10 dias corridos contados do envio")
            if comeco != fim10:
                alertas.append(
                    f"[VERIFICAR] o 10º dia após o envio ({br(fim10)}) não é útil; a intimação foi "
                    f"considerada feita em {br(comeco)} (Lei 11.419 art. 5º §2º por analogia e CPC "
                    f"art. 224 §1º). Confira o entendimento do tribunal.")
        regras.append("CPC art. 231 V: citação ou intimação eletrônica pelo portal")
    elif rito == "penal":
        comeco = marco
        regras.append(
            "CPP art. 798 §5º: o prazo corre da intimação, da audiência ou sessão em que proferida a "
            "decisão (presente a parte) ou do dia da ciência inequívoca")
        if meio in ("ar", "oficial"):
            alertas.append(
                "[VERIFICAR] Súmula 710 STF: no processo penal o prazo conta da data da intimação, "
                "não da juntada do mandado ou da carta. O marco deve ser a data da intimação.")
    elif e["natureza"] == "material":
        comeco = marco
        regras.append(FUNDAMENTO_MEIO[meio])
        regras.append(
            "CC art. 132 caput: no prazo material o dia do começo é o do fato, ainda que não útil; não se "
            "aplica a protração do CPC art. 224 §1º, regra do prazo processual")
    else:
        comeco = cal.util_ou_seguinte(marco)
        regras.append(FUNDAMENTO_MEIO[meio])
        if comeco != marco:
            regras.append(
                "CPC art. 224 §1º: o dia do começo que cai em dia sem expediente é protraído para o "
                "primeiro dia útil seguinte")
        if rito == "clt" and meio == "ar":
            alertas.append(
                "[VERIFICAR] Súmula 16 TST: a notificação postal presume-se recebida 48 horas depois "
                "da postagem; o marco deve ser a data do recebimento.")
    marcos["dia_do_comeco"] = comeco.isoformat()
    return comeco, marcos


def regra_dobro(e, regras, alertas):
    """Devolve (fator, registro_do_dobro)."""
    motivo, rito = e["dobro"], e["rito"]
    if motivo is None:
        return 1, None
    aplicado, fund = True, None
    if rito == "penal":
        if motivo != "defensoria":
            raise EntradaInvalida(
                f"dobro '{motivo}' não existe no processo penal: o CPP não prevê prazo em dobro para "
                "MP, Fazenda ou litisconsortes; só a Defensoria tem (LC 80/1994 arts. 44 I, 89 I e 128 I)")
        fund = "LC 80/1994 arts. 44 I, 89 I e 128 I: prazo em dobro da Defensoria Pública"
    elif rito == "cpc":
        if motivo == "fazenda":
            fund = "CPC art. 183: prazo em dobro da Fazenda Pública (União, Estados, DF, Municípios, autarquias e fundações)"
        elif motivo == "mp":
            fund = "CPC art. 180: prazo em dobro do Ministério Público"
        elif motivo == "defensoria":
            fund = "CPC art. 186: prazo em dobro da Defensoria Pública"
        elif e["processo_eletronico"]:
            aplicado = False
            fund = "CPC art. 229 §2º: o dobro dos litisconsortes com procuradores distintos não se aplica a processo eletrônico"
        else:
            fund = "CPC art. 229 caput: prazo em dobro dos litisconsortes com procuradores distintos, de escritórios diferentes, em autos físicos"
            alertas.append(
                "[VERIFICAR] CPC art. 229 §1º: cessa o dobro se, havendo só dois réus, apenas um "
                "apresentar defesa.")
        if motivo in ("fazenda", "mp", "defensoria"):
            alertas.append(
                "[VERIFICAR] CPC arts. 180 §2º, 183 §2º e 186 §4º: não há dobro quando a lei fixa "
                "prazo próprio para o ente.")
    elif rito == "clt":
        if motivo == "fazenda":
            fund = "Decreto-Lei 779/1969 art. 1º III: prazo em dobro para recurso da Fazenda na Justiça do Trabalho"
            alertas.append(
                "[VERIFICAR] o DL 779/1969 dá dobro só para recurso (art. 1º III); a defesa tem "
                "quádruplo contado da audiência (art. 1º II). Para outros atos, confira o entendimento do TST.")
        elif motivo == "mp":
            fund = "CPC art. 180, aplicado pelo CLT art. 769: prazo em dobro do Ministério Público"
            alertas.append("[VERIFICAR] aplicação do CPC art. 180 ao processo do trabalho.")
        elif motivo == "defensoria":
            fund = "CPC art. 186 e LC 80/1994: prazo em dobro da Defensoria Pública"
            alertas.append("[VERIFICAR] aplicação do dobro da Defensoria ao processo do trabalho.")
        else:
            aplicado = False
            fund = "TST OJ 310 SBDI-1: o dobro dos litisconsortes (CPC art. 229) não se aplica ao processo do trabalho"
    else:  # jec
        if motivo == "fazenda":
            aplicado = False
            fund = ("Lei 12.153/2009 art. 7º e Lei 10.259/2001 art. 9º: nos Juizados não há prazo "
                    "diferenciado para pessoa jurídica de direito público")
        elif motivo == "litisconsortes-procuradores-distintos":
            aplicado = False
            fund = "CPC art. 229 não aplicado ao Juizado"
            alertas.append(
                "[VERIFICAR] o FONAJE entende que o CPC art. 229 não se aplica aos Juizados; "
                "confira o enunciado e a turma recursal.")
        else:
            fund = ("CPC art. 180 (MP)" if motivo == "mp" else "CPC art. 186 (Defensoria)") + \
                ": prazo em dobro aplicado ao Juizado"
            alertas.append(f"[VERIFICAR] prazo em dobro ({motivo}) no Juizado: confira a turma recursal.")
    regras.append(fund)
    return (2 if aplicado else 1), {"motivo": motivo, "aplicado": aplicado, "fundamento": fund}


def conta_dias(e, cal, comeco, n, regras, alertas, excluidos):
    """Úteis ou corridos. Devolve (inicio, limite, contagem)."""
    corridos = e["unidade"] == "corridos"
    material = e["natureza"] == "material"
    rito = e["rito"]
    penal_material = material and rito == "penal"
    # CP art. 10: o dia do começo entra na conta, então a contagem parte dele mesmo.
    d, contagem, inicio = (comeco - UM_DIA if penal_material else comeco), [], None
    while len(contagem) < n:
        d += UM_DIA
        if corridos and (inicio is not None or material):
            motivo = cal.suspenso(d)       # em corridos só a suspensão para a contagem
        else:
            motivo = cal.bloqueio(d)       # úteis; e o primeiro dia dos corridos processuais tem de ser útil
        if motivo:
            if corridos and inicio is None:
                motivo = f"{motivo} — início protraído para dia útil"
            excluidos.append({"data": d.isoformat(), "motivo": motivo})
            continue
        if inicio is None:
            inicio = d
        contagem.append({"n": len(contagem) + 1, "data": d.isoformat(), "dia_semana": DIAS_SEMANA[d.weekday()]})
    limite = d
    if corridos and not penal_material:
        while cal.bloqueio(limite):
            excluidos.append({"data": limite.isoformat(),
                              "motivo": f"{cal.bloqueio(limite)} — vencimento protraído"})
            limite += UM_DIA
    if penal_material:
        regras.append(FUNDAMENTO_CP_10)
    elif material:
        regras.append(
            "CC art. 132 caput e §1º: prazo material em dias corridos, excluído o dia do começo e incluído o "
            "do vencimento; vencimento em feriado passa ao dia útil seguinte")
    elif rito == "penal":
        regras.append("CPP art. 798 caput: prazos contínuos, sem interrupção por férias, domingo ou feriado")
        regras.append(
            "Súmula 310 STF e CPP art. 798 §1º: a contagem começa no primeiro dia útil seguinte ao da intimação")
        if limite != d:
            regras.append(
                "CPP art. 798 §3º: o prazo que termina em dia sem expediente prorroga-se até o dia útil imediato")
    elif corridos:
        regras.append("CPC art. 224 §3º: a contagem começa no primeiro dia útil")
        if limite != d:
            regras.append("CPC art. 224 §1º: o vencimento em dia sem expediente é protraído para o primeiro dia útil")
    return inicio, limite, contagem


def conta_meses(e, cal, comeco, n, regras, alertas, excluidos):
    """Meses ou anos: dia de igual número, prorrogado por dia suspenso (recesso, se processual, e suspensão informada) e por dia não útil."""
    meses = n if e["unidade"] == "meses" else 12 * n
    penal_material = e["natureza"] == "material" and e["rito"] == "penal"
    if penal_material:
        # CP art. 10: incluído o dia do começo, o prazo acaba na véspera do dia de igual número.
        limite = soma_meses(comeco, meses) - UM_DIA
        primeiro = 0
        regras.append(FUNDAMENTO_CP_10)
    else:
        limite = soma_meses(comeco, meses)
        primeiro = 1
        regras.append(
            "CC art. 132 §3º e Lei 810/1949 arts. 1º a 3º: prazo em meses ou anos vence no dia de igual "
            "número ao do começo; se faltar esse dia, no primeiro dia seguinte")
    ja, extra = set(), 0
    while True:
        pendentes = [comeco + dt.timedelta(days=i) for i in range(primeiro, (limite - comeco).days + 1)]
        novos = [d for d in pendentes if d not in ja and cal.suspenso(d)]
        if not novos:
            break
        for d in novos:
            ja.add(d)
            excluidos.append({"data": d.isoformat(), "motivo": cal.suspenso(d)})
        extra += len(novos)
        limite += dt.timedelta(days=len(novos))
    if extra:
        regras.append("Suspensão (recesso ou informada): o vencimento avança um dia por dia suspenso")
    if penal_material:
        return comeco, limite, []
    venc = limite
    while cal.bloqueio(limite):
        excluidos.append({"data": limite.isoformat(), "motivo": f"{cal.bloqueio(limite)} — vencimento protraído"})
        limite += UM_DIA
    if limite != venc:
        regras.append(
            "CC art. 132 §1º e CPC art. 224 §1º (CPP art. 798 §3º no penal): vencimento em dia sem "
            "expediente passa ao primeiro dia útil")
    return comeco + UM_DIA, limite, []


def calcular(bruto, arq_feriados=ARQ_FERIADOS_PADRAO):
    """Devolve (codigo_de_saida, dict_de_saida)."""
    try:
        e = normaliza(bruto)
        tabela = json.loads(Path(arq_feriados).read_text(encoding="utf-8"))
        cal = Calendario(tabela, e)
        regras, alertas, excluidos = [], [], []
        fator, dobro = regra_dobro(e, regras, alertas)
        comeco, marcos = dia_do_comeco(e, cal, regras, alertas)
        n = e["prazo"] * fator
        if e["natureza"] != "material":
            regras.insert(0, FUNDAMENTO_COMECO[e["rito"]])
        elif e["rito"] != "penal":
            regras.insert(0, "CC art. 132 caput: exclui o dia do começo e inclui o do vencimento")
        if e["unidade"] == "uteis":
            regras.insert(0, {
                "cpc": "CPC art. 219: na contagem de prazo em dias só se computam os dias úteis",
                "clt": "CLT art. 775 caput: prazos contados em dias úteis",
                "jec": "Lei 9.099/1995 art. 12-A: na contagem de prazo em dias só se computam os dias úteis",
            }[e["rito"]])
        if e["unidade"] in ("uteis", "corridos"):
            inicio, limite, contagem = conta_dias(e, cal, comeco, n, regras, alertas, excluidos)
        else:
            inicio, limite, contagem = conta_meses(e, cal, comeco, n, regras, alertas, excluidos)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err)}
    except (OSError, ValueError, KeyError) as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": f"tabela de feriados ilegível: {err}"}

    rito, unidade = e["rito"], e["unidade"]
    if cal.aplica_recesso and any("recesso forense" in x["motivo"] for x in excluidos):
        regras.append({
            "cpc": "CPC art. 220: suspende-se o curso do prazo de 20/12 a 20/01, inclusive",
            "clt": "CLT art. 775-A: suspende-se o curso do prazo de 20/12 a 20/01, inclusive",
            "jec": "CPC art. 220 (recesso de 20/12 a 20/01) aplicado ao Juizado",
            "penal": "CPP art. 798-A (Lei 14.365/2022): suspende-se o curso do prazo de 20/12 a 20/01, inclusive",
        }[rito])
        if rito == "penal":
            alertas.append(
                "[VERIFICAR] CPP art. 798-A: o recesso suspendeu o prazo penal. Não suspende se houver réu "
                "preso no processo vinculado à prisão (I), procedimento da Lei Maria da Penha (II) ou medida "
                "urgente por despacho fundamentado (III); nesses casos informe 'excecao_recesso_penal'.")
        if rito == "jec":
            alertas.append("[VERIFICAR] aplicação do recesso do CPC art. 220 ao Juizado: confira o ato do tribunal.")
    if any(x.get("tipo") in ("nacional", "religioso", "ponto-forense") for x in cal.vistos.values()):
        regras.append(
            "Feriados nacionais: Lei 662/1949 (redação da Lei 10.607/2002), Lei 6.802/1980 (12/10) e "
            "Lei 14.759/2023 (20/11, desde 2024); Sexta-feira da Paixão só como feriado religioso declarado em lei municipal (Lei 9.093/1995 art. 2º)")
    exc = e["excecao_recesso_penal"]
    if exc:
        regras.append(
            f"CPP art. 798-A, {EXCECOES_RECESSO_PENAL[exc]}: o prazo corre no recesso de 20/12 a 20/01")
        if any(cal.no_recesso(comeco + dt.timedelta(days=i)) for i in range((limite - comeco).days + 1)):
            alertas.append(
                f"[VERIFICAR] exceção do CPP art. 798-A ({exc}) informada: o prazo correu no recesso. "
                "Confirme o enquadramento no processo; se o tribunal não teve expediente em algum dia "
                "(na Justiça Federal, Lei 5.010/1966 art. 62 I: 20/12 a 06/01), informe-o em 'feriados_locais'.")
    if e["natureza"] == "material":
        alertas.append(
            "[VERIFICAR] prazo de natureza material: sem recesso e sem dias úteis (CC art. 132). Confirme "
            "que o prazo é mesmo material; prazo processual informado como material fica errado.")
        if rito == "penal":
            alertas.append(
                "[VERIFICAR] prazo penal material (decadência, prescrição) contado pelo CP art. 10: inclui "
                "o dia do começo, corre em dias corridos e vence ainda que em dia sem expediente. Se o ato "
                "tiver de ser praticado em juízo, confira se o tribunal admite prorrogação.")
    if rito == "clt":
        alertas.append(
            "[VERIFICAR] Justiça do Trabalho: feriados e suspensões do TRT/TST (por exemplo os dias da "
            "Lei 5.010/1966 art. 62, se adotados pelo tribunal) entram por 'feriados_locais'.")
    vig = {"cpc": (VIGENCIA_CPC_2015, "o CPC/2015 (art. 219) vale desde 18/03/2016; antes, o CPC/1973 contava dias corridos"),
           "clt": (VIGENCIA_CLT_775_UTEIS, "o CLT art. 775 em dias úteis vale desde a Lei 13.467/2017 (11/11/2017); antes, dias corridos"),
           "jec": (VIGENCIA_JEC_12A, "o art. 12-A da Lei 9.099 foi incluído pela Lei 13.728/2018; antes dela os Juizados contavam dias corridos")}
    if rito in vig and unidade == "uteis" and e["marco"] < vig[rito][0]:
        alertas.append(f"[VERIFICAR] marco anterior à regra de dias úteis: {vig[rito][1]}.")
    if dobro and e["dobro"] == "litisconsortes-procuradores-distintos" and rito == "cpc" \
            and e["processo_eletronico"] is False and e["meio"] in ("dje", "sistema"):
        alertas.append(
            "[VERIFICAR] meio eletrônico com processo_eletronico=false: o dobro do art. 229 vale só "
            "para autos físicos.")

    pontos = []
    for d, f in sorted(cal.vistos.items()):
        if f.get("tipo") == "ponto-forense":
            pontos.append({"data": d.isoformat(), "nome": f["nome"], "excluido": True})
            alertas.append(
                f"[VERIFICAR] ponto facultativo/forense: {f['nome']} ({br(d)}) foi excluído da contagem; "
                f"confirme o ato do tribunal (incluir_pontos_forenses=false o conta como útil).")
        elif f.get("tipo") == "religioso":
            pontos.append({"data": d.isoformat(), "nome": f["nome"], "excluido": True})
            alertas.append(
                f"[VERIFICAR] {f['nome']} ({br(d)}) excluída: não é feriado nacional por lei; é feriado "
                "religioso da Lei 9.093/1995 art. 2º, que depende de lei municipal (na Justiça Federal, Lei "
                "5.010/1966 art. 62 II). Confira a comarca e o tribunal (incluir_pontos_forenses=false a "
                "conta como útil).")
    for d, f in sorted(cal.pontos_ignorados.items()):
        if comeco < d <= limite:
            pontos.append({"data": d.isoformat(), "nome": f["nome"], "excluido": False})
            if f["tipo"] == "religioso":
                alertas.append(
                    f"[VERIFICAR] {f['nome']} ({br(d)}) foi contada como dia útil "
                    "(incluir_pontos_forenses=false): só é feriado se declarada por lei municipal (Lei "
                    "9.093/1995 art. 2º) ou se o tribunal fechar; havendo, informe-a em 'feriados_locais'.")
            else:
                alertas.append(
                    f"[VERIFICAR] ponto facultativo/forense: {f['nome']} ({br(d)}) foi contado como dia útil "
                    f"(incluir_pontos_forenses=false); confirme se o tribunal teve expediente.")
    if any(x.get("tipo") == "local" for x in cal.vistos.values()):
        regras.append("Feriado local informado pelo usuário: dia sem expediente forense (CPC art. 216)")
        alertas.append(ALERTA_LEI_14939)
    alertas.append(ALERTA_FIXO)

    excluidos_unicos, ja = [], set()
    for x in excluidos:
        if x["data"] not in ja:
            ja.add(x["data"])
            excluidos_unicos.append(x)

    saida = {
        "versao": VERSAO,
        "rito": rito,
        "meio": e["meio"],
        "unidade": unidade,
        "natureza": e["natureza"],
        "excecao_recesso_penal": e["excecao_recesso_penal"],
        "uf": e["uf"],
        "marcos": marcos,
        "prazo_informado": e["prazo"],
        "dobro": dobro,
        "prazo_contado": n,
        "data_inicio_contagem": inicio.isoformat(),
        "data_limite": limite.isoformat(),
        "dia_semana_limite": DIAS_SEMANA[limite.weekday()],
        "contagem": contagem,
        "dias_excluidos": excluidos_unicos,
        "pontos_forenses": {"incluidos": e["incluir_pontos_forenses"], "no_periodo": pontos},
        "regra_aplicada": regras,
        "alertas": alertas,
        "fonte_feriados": {"arquivo": Path(arq_feriados).name, "data_revisao": tabela.get("data_revisao")},
    }
    return EXIT_OK, saida


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Engine B: prazo processual (ritos "
                    f"{', '.join(RITOS)}; meios {', '.join(MEIOS)}). Entrada JSON por --entrada ou stdin.")
    ap.add_argument("--entrada", help="arquivo JSON de entrada (sem ele, lê o stdin)")
    ap.add_argument("--feriados", default=str(ARQ_FERIADOS_PADRAO),
                    help="tabela de feriados nacionais (padrão: data/feriados-nacionais.json; uso em testes)")
    args = ap.parse_args(argv)
    try:
        texto = Path(args.entrada).read_text(encoding="utf-8") if args.entrada else sys.stdin.read()
        bruto = json.loads(texto)
    except (OSError, json.JSONDecodeError) as err:
        codigo, saida = EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": f"JSON ilegível: {err}"}
    else:
        codigo, saida = calcular(bruto, args.feriados)
    json.dump(saida, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if codigo == EXIT_ENTRADA:
        print(f"entrada inválida: {saida['detalhe']}", file=sys.stderr)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
