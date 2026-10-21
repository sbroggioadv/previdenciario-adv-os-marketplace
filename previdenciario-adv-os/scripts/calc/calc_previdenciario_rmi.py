#!/usr/bin/env python3
"""calc_previdenciario_rmi.py — RMI de concessão e de revisão, decadência e prescrição.

Concessão: média de 100% desde 07/1994 (com o divisor mínimo de 108 do art.
135-A quando cabe) ou, na incapacidade permanente com fato gerador até
13/11/2019, média dos 80% maiores (Lei 8.213, art. 29, II; IN 128, art. 229).
Fato gerador ou DIB possível antes de 29/11/1999 (Lei 9.876) fica fora do
cálculo automático: exit 3 com a regra dos 36 em 48 meses (IN 128, art. 221,
II, "b"). Sem 'dib', a aposentadoria conta a DIB na DER e no desligamento até
90 dias antes (Lei 8.213, arts. 49, I, "a", e 54) e só fecha se as leituras
coincidem;
limite ao teto, coeficiente da regra, piso e teto, e o teste do descarte
(EC 103, art. 26, §6º; IN 128, art. 228, §§1º e 2º — só aposentadorias com
tempo mínimo de contribuição, nunca a incapacidade permanente). Revisão: diferença mensal,
decadência de 10 anos, parcelas e abonos não prescritos e total nominal.
Conta aberta e lista de CAMPOS em context/calculo-rmi.md.

USO:
    python3 calc_previdenciario_rmi.py --entrada caso.json
    echo '{...}' | python3 calc_previdenciario_rmi.py
    python3 calc_previdenciario_rmi.py --versao

Saída: JSON no stdout. Exit 0 = calculado; 2 = entrada inválida; 3 = falta
dado ou tabela (devolve a fórmula aberta, nunca estima).

Só biblioteca padrão, Python 3.9+, sem rede. Tabelas em ../data/ relativo a
este arquivo. Os dias úteis do art. 41-A vêm do motor de prazos
(calc_previdenciario_prazo.py, cópia do Engine B conferida por sha256), na
mesma pasta deste script: dele se usam só a tabela de feriados nacionais e o
cálculo da Páscoa. Sem o motor, o modo revisão sai em exit 3. O vencimento
de cada competência é a janela de pagamento do regime vigente NELA (não um
dia único; REGIMES_JANELA: 1º ao 10º dia útil até 2004-03, 1º ao 5º até 2006,
faixas do art. 41-A, §§2º e 3º, depois); a renda muda só nas datas de
reajuste do regime (REGIMES_DATA_REAJUSTE: a do salário mínimo desde 2004;
antes, não capturada → exit 3); o vencimento individual devido (a data em que a prestação deveria
ter sido paga, não a do pagamento realizado) entra por `datas_vencimento`. Nunca chamado
por hook.
"""

import argparse
import calendar
import datetime as dt
import importlib.util
import json
import re
import sys
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, Decimal
from pathlib import Path

VERSAO = "2.0.2"
NOME = "calc_previdenciario_rmi"
EXIT_OK, EXIT_ENTRADA, EXIT_FALTA = 0, 2, 3

AQUI = Path(__file__).resolve().parent
DIR_DADOS = AQUI.parent / "data"
ARQ_SALARIO_MINIMO = DIR_DADOS / "salario-minimo.json"
ARQ_TETO = DIR_DADOS / "teto-rgps.json"
ARQ_REAJUSTES = DIR_DADOS / "reajustes-rgps.json"
ARQ_MOTOR_PRAZO = AQUI / "calc_previdenciario_prazo.py"

EC103 = dt.date(2019, 11, 13)
MARCO_9876 = dt.date(1999, 11, 29)             # publicação da Lei 9.876/1999 (IN 128, art. 221)
MARCO_135A_FILIACAO = dt.date(1994, 7, 31)     # filiado até julho de 1994
MARCO_135A_FATO = dt.date(2022, 5, 5)          # IN 128, art. 228, §4º (Lei 14.331/2022)
DIVISOR_MINIMO = 108
JANELA_DESLIGAMENTO = 90                      # Lei 8.213, art. 49, I, "a" (e art. 54): DIB no desligamento
CENTAVO = Decimal("0.01")

MODOS = ("concessao", "revisao")
ESPECIES = ("aposentadoria", "incapacidade-permanente", "outra")
REGRAS = ("art15", "art16", "art17", "art18", "art19", "art19-especial", "art20", "art21",
          "adquirido-anterior", "incapacidade-permanente", "incapacidade-permanente-acidentaria")
SEXOS = ("M", "F")
ATIVIDADES = (15, 20, 25)

# Abono anual com ato próprio capturado em context/lei/. Ano fora daqui: só limites.
ATOS_ABONO = {
    2021: {
        "parcelas": [{"competencia": (2021, 5), "fracao": Decimal("0.5")},
                     {"competencia": (2021, 6), "fracao": None}],
        "fonte": "Decreto 10.695/2021, art. 1º, I e II (context/lei/decreto-10695-2021-abono.md)",
    },
    2022: {
        "parcelas": [{"competencia": (2022, 4), "fracao": Decimal("0.5")},
                     {"competencia": (2022, 5), "fracao": None}],
        "fonte": "Decreto 10.999/2022, art. 1º, I e II (context/lei/decreto-10999-2022-abono.md)",
    },
    2023: {
        "parcelas": [{"competencia": (2023, 5), "fracao": Decimal("0.5")},
                     {"competencia": (2023, 6), "fracao": None}],
        "fonte": "Decreto 11.517/2023, art. 1º, I e II (context/lei/decreto-11517-2023-abono.md)",
    },
    2024: {
        "parcelas": [{"competencia": (2024, 4), "fracao": Decimal("0.5")},
                     {"competencia": (2024, 5), "fracao": None}],
        "fonte": "Decreto 11.947/2024, art. 1º, I e II (context/lei/decreto-11947-2024-abono.md)",
    },
    2025: {
        "parcelas": [{"competencia": (2025, 4), "fracao": Decimal("0.5")},
                     {"competencia": (2025, 5), "fracao": None}],
        "fonte": "Decreto 12.425/2025, art. 1º, I e II (context/lei/decreto-12425-2025-abono.md)",
    },
    2026: {
        "parcelas": [{"competencia": (2026, 4), "fracao": Decimal("0.5")},
                     {"competencia": (2026, 5), "fracao": None}],
        "fonte": "Decreto 12.884/2026, art. 1º, I e II (context/lei/decreto-12884-2026-abono.md)",
    },
}

# Regimes por vigência (revisão r11, MAJORs 1 e 2: regra atual aplicada a período em que vigorava outra). Tudo que
# muda no tempo e mexe na revisão, com a fonte de cada linha; cada parcela usa o regime vigente na SUA competência.
# Fora de toda linha, a parcela fica em aberto (exit 3) com o dado faltante nomeado: nunca a regra de outra época,
# nem para fechar o total nem para recusar a entrada. Piso e teto: scripts/data/salario-minimo.json e teto-rgps.json,
# por competência (renda_da_competencia). Fator do reajuste: scripts/data/reajustes-rgps.json.
#
# Data do reajuste anual da renda. 'datas' = "limites": a renda só muda numa data em que o salário mínimo mudou;
# entram também as do teto, que as portarias de reajuste fixam junto (ex.: Portaria 13/2026, art. 2º; a de 08/2006
# acompanha a MP 316/2006). Qualquer dessas datas sem fator capturado fecha a renda dali em diante.
# W3-reajustes r2 (decisão 1): a tabela de reajustes é a fonte única de QUANDO o benefício acima do mínimo é reajustado.
# Data em que só o mínimo ou o teto mudam, num ano que tem linha de reajuste, não pede fator: a renda se mantém e o piso
# e o teto da competência valem (Lei 8.213, art. 41-A e art. 33). Ano sem linha e as datas abaixo continuam abrindo.
# 2.0.1: 01/08/2006 saiu daqui — a linha tem 'sobre_renda_de' (5,01% sobre a renda de março/2006, substituindo os
# 5,00% de 01/04/2006: Lei 11.430/2006, art. 3º; Portaria MPS 342/2006, art. 1º), aplicada em evolucao_renda.
LACUNAS_REAJUSTE = {}


def so_piso_e_teto(d, datas_reajuste):
    """True se em d só mudam o mínimo ou o teto: d não tem linha de reajuste, não é lacuna declarada e o ano de d tem
    a sua linha de reajuste (o reajuste anual do ano está capturado em outra data)."""
    return d not in LACUNAS_REAJUSTE and d not in datas_reajuste and any(x.year == d.year for x in datas_reajuste)


REGIMES_DATA_REAJUSTE = [
    {"desde": None, "ate": dt.date(2003, 12, 31), "datas": None,
     "fonte": "Lei 8.213, art. 41, redações da MP 2.187-13/2001 (\"a partir de 1º de junho de 2001\", percentual de "
              "regulamento) e anteriores (context/lei/lei-8213-1991.md:1079-1081): data e fator de cada reajuste até "
              "2003 não capturados"},
    {"desde": dt.date(2004, 1, 1), "ate": None, "datas": "limites",
     "fonte": "Lei 8.213, art. 41, caput, redação da Lei 10.699/2003 (\"a partir de 2004, na mesma data de reajuste "
              "do salário mínimo\"; context/lei/lei-8213-1991.md:1083), mantida no art. 41-A, caput (Lei 11.430/2006; "
              "lei-8213-1991.md:1121)"},
]

# Janela de pagamento de cada competência, pela competência (de, até inclusive). 'tipo': "1a10" = do 1º ao 10º dia
# útil do mês seguinte; "1a5" = do 1º ao 5º; "faixa" = §2º (acima do mínimo, 1º ao 5º) ou §3º (até o mínimo, do 5º
# dia útil antes do fim do mês ao 5º do seguinte). Antes de 1993 a redação aplicável não se data pela captura.
REGIMES_JANELA = [
    {"de": (1993, 1), "ate": (2004, 3), "tipo": "1a10",
     "fonte": "Lei 8.213, art. 41, §4º, redação da Lei 8.444/1992: do primeiro ao décimo dia útil do mês seguinte "
              "(context/lei/lei-8213-1991.md:1103). Competência 2004-03, paga em abril/2004, cabe também na leitura do "
              "§4º da Lei 10.699/2003 (\"a partir de abril de 2004\", linha 1105): a janela do 1º ao 10º contém a dela"},
    {"de": (2004, 4), "ate": (2007, 11), "tipo": "1a5",
     "fonte": "Lei 8.213, art. 41, §4º, redação da Lei 10.699/2003 (\"a partir de abril de 2004\", do primeiro ao quinto "
              "dia útil do mês seguinte; context/lei/lei-8213-1991.md:1105), e art. 41-A, §2º, redação da Lei 11.430/2006 "
              "(linha 1125), sem distinção de faixa, até a MPv 404, de 11/12/2007, em vigor na publicação (art. 2º; DOU "
              "12/12/2007; context/lei/mp-404-2007.md): a competência 11/2007, paga em dezembro do 1º ao 5º dia útil, é "
              "a última sem faixa"},
    {"de": (2007, 12), "ate": (2008, 12), "tipo": "faixa",
     "fonte": "Lei 8.213, art. 41-A, §§2º a 4º: faixas da MPv 404/2007 (em vigor desde 12/12/2007, art. 2º; context/lei/"
              "mp-404-2007.md), mantidas pela Lei 11.665/2008 (context/lei/lei-11665-2008.md; context/lei/lei-8213-1991.md:"
              "1131-1145)"},
    {"de": (2009, 1), "ate": None, "tipo": "faixa",
     "fonte": "Lei 8.213, art. 41-A, §§2º a 4º, redação da Lei 11.665/2008 (context/lei/lei-8213-1991.md:1141-1145)"},
]


# Cobertura temporal (brief r13; revisão r12, BLOCKER 2: decadência de benefício anterior a 1997 pelo marco atual). Para
# cada regra, os intervalos de data em que a redação implementada é a vigente, com a fonte de cada borda; fora de
# segmento 'coberto' a regra não é calculada: exit 3 com a regra histórica e a fonte. Reajuste e janela de pagamento
# têm as tabelas próprias acima (REGIMES_DATA_REAJUSTE, REGIMES_JANELA). Marcos:
#   concessao/aposentadoria: fato gerador (DER).
#   concessao/incapacidade-permanente: do fato gerador (ou da primeira DIB possível) à DIB.
#   revisao/decadencia: data do primeiro pagamento (a concessão é anterior ou igual a ela). O Tema 313 olha a data da
#   CONCESSÃO, que a entrada não traz (revisão r13, MAJOR): DIB e primeiro pagamento do mesmo lado de 28/06/1997
#   decidem o lado; em lados opostos a concessão é indeterminável e prazo e booleano ficam em aberto (decadencia()).
EDICAO_MP_1523_9 = dt.date(1997, 6, 28)        # brief r13 (Tema 313); a data não está capturada em context/lei/
INICIO_TEMA_313 = dt.date(1997, 8, 1)          # STF Tema 313, tese II
_LEI_9876 = "Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221, II)"
_EC_103 = "EC 103/2019, publicada em 13/11/2019 (EC 103, arts. 3º e 36, III; IN 128, art. 233)"
_TEMA_313 = ("STF Tema 313, tese II (context/lei/temas-sumulas-prev.md:83-89): benefícios concedidos antes do advento "
             "da MP 1.523/1997 contam os 10 anos de 01/08/1997; o advento em 28/06/1997 (edição de 1997 da MP) vem do "
             "brief r13 e não está capturado em context/lei/ — a IN 128 só registra a MP 1.523 original, de 14/10/1996 "
             "(in-128-2022-inss.md:1305), que não trazia a decadência [VERIFICAR]")
_LEI_10839 = ("Lei 10.839, \"de 2004\" (redação do art. 103 em context/lei/lei-8213-1991.md:2192): o dia de início "
              "(MP 138/2003) não está capturado; a borda é 01/01/2005, primeiro dia certamente sob o texto dela")
COBERTURA = {
    "concessao/aposentadoria": [
        {"de": None, "ate": dt.date(1999, 11, 28), "coberto": False, "fonte_ate": _LEI_9876,
         "regra": "requisitos até 28/11/1999: últimos 36 salários em até 48 meses (IN 128, art. 221, II, \"b\")"},
        {"de": dt.date(1999, 11, 29), "ate": EC103, "coberto": False, "fonte_de": _LEI_9876, "fonte_ate": _EC_103,
         "regra": "direito adquirido até 13/11/2019 (EC 103, art. 3º): 80% maiores salários, coeficiente e fator da "
                  "modalidade (FORMULA_ADQUIRIDO)"},
        {"de": EC103 + dt.timedelta(days=1), "ate": None, "coberto": True, "fonte_de": _EC_103,
         "regra": "EC 103, arts. 15 a 21 e 26 (média de 100% desde 07/1994; divisor mínimo do art. 135-A para fato "
                  "gerador desde 05/05/2022 — Lei 14.331/2022, IN 128, art. 228, §4º — implementado dos dois lados)"},
    ],
    "concessao/incapacidade-permanente": [
        {"de": None, "ate": dt.date(1999, 11, 28), "coberto": False, "fonte_ate": _LEI_9876,
         "regra": "últimos 36 salários em até 48 meses (IN 128, art. 221, II, \"b\"); até 28/04/1995, coeficiente de 80% "
                  "+ 1% por grupo de 12 contribuições, até 100% (Lei 8.213, art. 44, redação original — "
                  "context/lei/lei-8213-1991.md:1199-1203); de 29/04/1995 (Lei 9.032 — IN 128, art. 352, §1º), 100%"},
        {"de": dt.date(1999, 11, 29), "ate": EC103, "coberto": True, "fonte_de": _LEI_9876, "fonte_ate": _EC_103,
         "regra": "100% da média dos 80% maiores (Lei 8.213, arts. 29, II, redação da Lei 9.876/1999, e 44, redação da "
                  "Lei 9.032/1995; IN 128, arts. 229 e 233, II, \"a\")"},
        {"de": EC103 + dt.timedelta(days=1), "ate": None, "coberto": True, "fonte_de": _EC_103,
         "regra": "EC 103, art. 26, §§2º, 3º, II, e 5º (média de 100%; sem o divisor mínimo do art. 135-A)"},
    ],
    "revisao/decadencia": [
        {"de": None, "ate": EDICAO_MP_1523_9 - dt.timedelta(days=1), "coberto": True, "fonte_ate": _TEMA_313,
         "regra": "10 anos contados de 01/08/1997 (STF Tema 313, tese II)"},
        {"de": EDICAO_MP_1523_9, "ate": dt.date(2004, 12, 31), "coberto": False, "fonte_de": _TEMA_313,
         "fonte_ate": _LEI_10839,
         "regra": "três redações do art. 103 em sequência — 10 anos (Lei 9.528/1997), 5 anos (Lei 9.711, de 20/11/1998) e "
                  "10 anos (Lei 10.839/2004)",
         "linha": "[VERIFICAR] decadência de benefício com primeiro pagamento de 28/06/1997 a 31/12/2004: o art. 103 teve "
                  "três redações nesse período — 10 anos (Lei 9.528/1997), 5 anos (Lei 9.711, de 20/11/1998) e de novo 10 "
                  "anos (Lei 10.839/2004), todas do dia 1º do mês seguinte ao do primeiro pagamento (context/lei/"
                  "lei-8213-1991.md:2188-2192); qual prazo rege o benefício concedido sob uma delas e alcançado pela "
                  "seguinte não está em context/lei/ (o STF Tema 313 só trata dos anteriores à MP 1.523/1997): decida à mão"},
        {"de": dt.date(2005, 1, 1), "ate": None, "coberto": True, "fonte_de": _LEI_10839,
         "regra": "10 anos do dia 1º do mês seguinte ao do primeiro pagamento (Lei 8.213, art. 103, redação da Lei "
                  "10.839/2004, mantida no art. 103, I, pela Lei 13.846/2019 — lei-8213-1991.md:2192-2200)"},
    ],
}


def fora_da_cobertura(chave, ini, fim):
    """Segmentos NÃO cobertos de COBERTURA[chave] que o intervalo [ini, fim] alcança (fim None = sem limite)."""
    return [s for s in COBERTURA[chave] if not s["coberto"]
            and (s["ate"] is None or ini <= s["ate"]) and (fim is None or s["de"] is None or s["de"] <= fim)]


# CC, art. 132, §1º: o termo que cai em feriado prorroga-se ao seguinte dia útil (QA final r6, C1: primeiro pagamento
# 15/04/2016 → termo nominal 01/05/2026, feriado da Lei 662/1949, art. 1º → 04/05/2026). Sem o calendário do motor de
# prazos, a maior sequência de dias sem expediente que ele conhece (sábado a terça de carnaval, 4 dias) cabe com folga
# nesta janela, em que o booleano fica em aberto — nunca True.
PRORROGACAO_MAX_DIAS = 7
FUND_PRORROGACAO = "CC, art. 132, §1º; feriados nacionais: Lei 662/1949, art. 1º"
VEREDITO_DECADENCIA = {True: "decadente", False: "não decadente", None: "decadência em aberto"}


def termo_efetivo(nominal, ref, cal):
    """(fim, decadente, pendência) do termo decadencial nominal (CC, art. 132, §3º) com a prorrogação do §1º, pelo
    calendário do motor de prazos nas duas leituras de DiasBancarios: 'estrita' (só feriados nacionais) e 'ampla'
    (também carnaval, Paixão e Corpus Christi, que não são feriados nacionais por lei). Leituras divergentes, ou sem
    calendário (cal None): fim None, pendência em texto e booleano só fora da janela que depende do calendário."""
    if cal is None:
        ate = nominal + dt.timedelta(days=PRORROGACAO_MAX_DIAS)
        return None, (False if ref <= nominal else True if ref > ate else None), (
            f"termo nominal {br(nominal)} sem o calendário do motor de prazos: em dia sem expediente prorroga-se ao "
            f"seguinte dia útil ({FUND_PRORROGACAO}); confira o calendário — até {br(ate)} não se declara a decadência")
    fins = []
    for ampla in (False, True):
        d = nominal
        while not cal.util(d, ampla):
            d += dt.timedelta(days=1)
        fins.append(d)
    estrita, larga = fins
    decadente = False if ref <= estrita else True if ref > larga else None
    if estrita == larga:
        return estrita, decadente, None
    return None, decadente, (
        f"termo nominal {br(nominal)} prorroga-se a {br(estrita)} contando só os feriados nacionais, ou a {br(larga)} "
        f"fechando também carnaval, Paixão e Corpus Christi ({FUND_PRORROGACAO}): confira o expediente do dia")


def _leitura_termo(nominal, ref, cal):
    """Texto 'fim D, veredito no marco R' de uma leitura do termo decadencial, com a prorrogação do §1º."""
    fim, decadente, pendencia = termo_efetivo(nominal, ref, cal)
    veredito = f"{VEREDITO_DECADENCIA[decadente]} no marco {br(ref)}"
    if pendencia:
        return f"{pendencia}; {veredito}"
    if fim != nominal:
        return f"fim {br(fim)} (termo nominal {br(nominal)} sem expediente, prorrogado: {FUND_PRORROGACAO}), {veredito}"
    return f"fim {br(fim)}, {veredito}"


def decadencia(pp, ref, dib, cal):
    """(início, termo nominal, fim, decadente, fora) do prazo de decadência (Lei 8.213, art. 103; CC, art. 132, §§1º e
    3º). Concessão anterior à MP 1.523/1997: 10 anos de 01/08/1997 (STF Tema 313); posterior: pelo primeiro pagamento,
    dentro da COBERTURA. A concessão fica entre a DIB e o primeiro pagamento; se os dois caem em lados opostos de
    28/06/1997, o lado é indeterminável (r14): (None, None, None, None, [segmento com as duas leituras]). Fora da
    COBERTURA, idem. O fim é o termo nominal prorrogado ao seguinte dia útil (termo_efetivo); se depender do calendário,
    fim None e `fora` traz um segmento 'calendario' com a pendência."""
    antes = pp < EDICAO_MP_1523_9
    if (dib < EDICAO_MP_1523_9) != antes:
        return None, None, None, None, [concessao_indeterminavel(pp, ref, dib, cal)]
    a, m = mes_seguinte(pp.year, pp.month)
    inicio = dt.date(a, m, 1)
    if antes:
        inicio = INICIO_TEMA_313
    else:
        fora = fora_da_cobertura("revisao/decadencia", pp, pp)
        if fora:
            return None, None, None, None, fora
    fim = soma_anos(inicio, 10)
    efetivo, decadente, pendencia = termo_efetivo(fim, ref, cal)
    if pendencia is None:
        return inicio, fim, efetivo, decadente, []
    return inicio, fim, None, decadente, [{"regra": pendencia, "calendario": True, "fonte_ate": FUND_PRORROGACAO,
                                           "linha": f"[VERIFICAR] decadência: {pendencia}"}]


def concessao_indeterminavel(pp, ref, dib, cal):
    """Segmento-pseudo de COBERTURA para DIB antes e primeiro pagamento a partir de 28/06/1997 (revisão r13, MAJOR):
    concessão antiga paga tarde e concessão posterior com efeitos retroativos não se distinguem pela entrada."""
    fim_a = soma_anos(INICIO_TEMA_313, 10)
    leitura_a = ("concessão antes de 28/06/1997 → 10 anos de 01/08/1997 (STF Tema 313, tese II) → "
                 + _leitura_termo(fim_a, ref, cal))
    fora = fora_da_cobertura("revisao/decadencia", pp, pp)
    if fora:
        leitura_b = ("concessão a partir de 28/06/1997 → primeiro pagamento " + br(pp) + " fora da cobertura: "
                     + "; ".join(s["regra"] for s in fora))
    else:
        a, m = mes_seguinte(pp.year, pp.month)
        fim_b = soma_anos(dt.date(a, m, 1), 10)
        leitura_b = (f"concessão a partir de 28/06/1997 → 10 anos do dia 1º do mês seguinte ao primeiro pagamento "
                     f"{br(pp)} (Lei 8.213, art. 103) → " + _leitura_termo(fim_b, ref, cal))
    return {"regra": (f"concessão indeterminável: DIB {br(dib)} antes e primeiro pagamento {br(pp)} a partir de "
                      "28/06/1997 (advento da MP 1.523/1997); o STF Tema 313 olha a data da concessão, que a entrada "
                      "não traz — informe-a à mão (carta de concessão, data do despacho)"),
            "fonte_ate": _TEMA_313, "indeterminavel": True,
            "linha": f"[VERIFICAR] decadência com concessão indeterminável — (a) {leitura_a}; (b) {leitura_b}"}


def regime_data_reajuste(d):
    for r in REGIMES_DATA_REAJUSTE:
        if (r["desde"] is None or r["desde"] <= d) and (r["ate"] is None or d <= r["ate"]):
            return r
    return None


def regime_janela(comp):
    for r in REGIMES_JANELA:
        if r["de"] <= comp and (r["ate"] is None or comp <= r["ate"]):
            return r
    return None


# Contrato de entrada (context/calculo-rmi.md, seção 6). O teste de paridade
# compara este dicionário com o bloco ```campos``` das skills.
CAMPOS = {
    "modo": {"tipo": "enum", "obrigatorio": "sim", "valores": list(MODOS)},
    "especie": {"tipo": "enum", "obrigatorio": "sim", "valores": list(ESPECIES)},
    "regra": {"tipo": "enum", "obrigatorio": "modo=concessao", "valores": list(REGRAS)},
    "sexo": {"tipo": "enum", "obrigatorio": "sim", "valores": list(SEXOS)},
    "data_filiacao": {"tipo": "data", "obrigatorio": "sim", "valores": None},
    "fato_gerador": {"tipo": "data", "obrigatorio": "sim", "valores": None},
    "salarios_contribuicao": {"tipo": "lista de decimal", "obrigatorio": "uma das tres formas de media",
                              "valores": None},
    "media": {"tipo": "decimal", "obrigatorio": "uma das tres formas de media", "valores": None},
    "soma": {"tipo": "decimal", "obrigatorio": "uma das tres formas de media, com quantidade", "valores": None},
    "quantidade": {"tipo": "inteiro", "obrigatorio": "com soma", "valores": None},
    "tempo_contribuicao_anos": {"tipo": "inteiro", "obrigatorio": "modo=concessao", "valores": None},
    "tempo_contribuicao_meses": {"tipo": "inteiro", "obrigatorio": "nao", "valores": None},
    "atividade_especial_anos": {"tipo": "enum", "obrigatorio": "regra=art19-especial ou art21",
                                "valores": list(ATIVIDADES)},
    "descartar": {"tipo": "bool", "obrigatorio": "nao", "valores": None},
    "tempo_minimo_da_regra_anos": {"tipo": "inteiro", "obrigatorio": "descartar=true", "valores": None},
    "fator": {"tipo": "decimal", "obrigatorio": "nao", "valores": None},
    "teto": {"tipo": "decimal", "obrigatorio": "nao", "valores": None},
    "salario_minimo": {"tipo": "decimal", "obrigatorio": "nao", "valores": None},
    "rmi_paga": {"tipo": "decimal", "obrigatorio": "modo=revisao", "valores": None},
    "rmi_devida": {"tipo": "decimal", "obrigatorio": "modo=revisao", "valores": None},
    "dib": {"tipo": "data", "obrigatorio": "modo=revisao; em concessao, quando os limites do art. 29, §2º, mudam "
                                           "conforme a DIB", "valores": None},
    "data_primeiro_pagamento": {"tipo": "data", "obrigatorio": "modo=revisao", "valores": None},
    "data_ajuizamento": {"tipo": "data", "obrigatorio": "modo=revisao, salvo data_requerimento_revisao",
                         "valores": None},
    "data_requerimento_revisao": {"tipo": "data", "obrigatorio": "alternativa a data_ajuizamento",
                                  "valores": None},
    "abono": {"tipo": "bool", "obrigatorio": "modo=revisao", "valores": None},
    "media_acima_do_teto": {"tipo": "bool", "obrigatorio": "modo=revisao com DIB no período de incorporação do "
                                                         "teto de um reajuste capturado", "valores": None},
    "datas_vencimento": {"tipo": "objeto", "obrigatorio": "nao", "valores": None},
}

AVISO_FIXO = ("Conferir o resultado contra a carta de concessão, o CNIS e o histórico de créditos antes "
              "do protocolo. Valores nominais: a correção das diferenças é outra conta (context/calculo-rpv.md).")

# Requisitos até 28/11/1999: fora do cálculo automático (decisão do coordenador, brief r7). Só a regra é descrita.
REGRA_ANTERIOR_9876 = (
    "[VERIFICAR] regra anterior à Lei 9.876/1999 (requisitos ou DIB até 28/11/1999): salário de benefício = média dos "
    "últimos 36 salários de contribuição, apurados em período não superior a 48 meses imediatamente anteriores (IN 128, "
    "art. 221, II, \"b\"; Lei 8.213, art. 29, redação original, revogada pela Lei 9.876/1999); RMI = salário de "
    "benefício × coeficiente da espécie na legislação da data dos requisitos, conferido à mão")

# Direito adquirido até 13/11/2019: a modalidade não vem na entrada, então todas as fórmulas são expostas (revisão r6,
# MAJOR 3: antes só a da aposentadoria por tempo).
FORMULA_ADQUIRIDO = (
    "[VERIFICAR] direito adquirido até 13/11/2019 (EC 103, art. 3º): SB = média dos 80% maiores salários desde 07/1994 "
    "(Lei 8.213, art. 29, I e II; IN 128, arts. 221, II, \"a\", e 229), com o divisor mínimo do art. 3º, §2º, da Lei "
    "9.876 para o filiado até 28/11/1999 (IN 128, art. 230); RMI conforme a modalidade, que a entrada não informa: "
    "aposentadoria por idade = SB × (70% + 1% por grupo de 12 contribuições, até 100%), sem fator, salvo opção pelo fator "
    "se mais vantajoso (IN 128, arts. 229, §2º, I, e 233, III, \"a\"); aposentadoria especial = SB × 100%, sem fator "
    "(IN 128, art. 233, V, \"a\"); por tempo de contribuição integral = SB × fator previdenciário × 100%, ou sem fator "
    "quando idade + tempo atingem os pontos do art. 29-C da Lei 8.213 (IN 128, arts. 229, §§1º e 2º, III, e 233, IV, "
    "\"a\"); por tempo proporcional = SB × fator × (70% + 5% por grupo de 12 contribuições além do período adicional, até "
    "100%) (IN 128, art. 233, IV, \"b\"); requisitos até 28/11/1999: regra anterior à Lei 9.876 (IN 128, art. 221, II, "
    "\"b\")")


class EntradaInvalida(Exception):
    pass


def minimo_legal(e):
    """Tempo de contribuição mínimo da regra (EC 103, arts. 15 a 21): (geral, professor ou None, há pedágio,
    fundamento), em anos; None fora das regras de aposentadoria da EC 103. Revisão r7, MAJOR 1: o campo informado
    nunca afasta o requisito legal, e o descarte (art. 26, §6º) tem de manter esse mínimo."""
    regra, mulher = e["regra"], e["sexo"] == "F"
    geral = 30 if mulher else 35
    if regra == "art15":
        return geral, geral - 5, False, "EC 103, art. 15, I (professor: §3º)"
    if regra == "art16":
        return geral, geral - 5, False, "EC 103, art. 16, I (professor: §2º)"
    if regra == "art17":
        return geral, None, True, "EC 103, art. 17, I e II (período adicional de 50%)"
    if regra == "art18":
        return 15, None, False, "EC 103, art. 18, II"
    if regra == "art19":
        return (15 if mulher else 20), 25, False, "EC 103, art. 19, caput (professor: §1º, II)"
    if regra in ("art19-especial", "art21"):
        fund = "EC 103, art. 19, §1º, I" if regra == "art19-especial" else "EC 103, art. 21, I a III"
        return e["atividade_especial_anos"], None, False, f"{fund} (tempo de efetiva exposição)"
    if regra == "art20":
        return geral, geral - 5, True, "EC 103, art. 20, II e IV (professor: §1º)"
    return None


def confere_minimos(e):
    """Recusa (exit 2) tempo de contribuição abaixo do mínimo da regra e tempo mínimo informado fora do que a lei
    admite. Regras sem pedágio: o mínimo é o da lei (o geral, ou o do professor); maior que ele corta descarte que a
    lei permite. Com pedágio (arts. 17 e 20) o mínimo soma o período adicional, que a entrada não traz: só o piso é
    conferido (e, no art. 17, o teto de um ano: mais de 28/33 anos em 13/11/2019 deixam menos de 2 a cumprir, cuja
    metade é menos de 1)."""
    if e["regra"] in ("art15", "art16", "art17", "art18", "art20", "art21", "adquirido-anterior") \
            and e["data_filiacao"] > EC103:
        raise EntradaInvalida(f"regra '{e['regra']}' exige filiação ao RGPS até 13/11/2019 (EC 103, arts. 3º, 15 a 18, 20 "
                              f"e 21); com filiação em {br(e['data_filiacao'])} só vale a permanente, 'art19'")
    m = minimo_legal(e)
    if m is None:
        return
    geral, prof, pedagio, fund = m
    piso = min(geral, prof) if prof is not None else geral
    tempo = e["tempo_contribuicao_anos"]
    if tempo is not None and tempo < piso:
        raise EntradaInvalida(f"tempo_contribuicao_anos {tempo} abaixo do mínimo da regra '{e['regra']}' ({piso} anos — "
                              f"{fund}): sem ele não há direito à aposentadoria por essa regra")
    informado = e["tempo_minimo_da_regra_anos"]
    if informado is None:
        return
    if pedagio:
        teto_min = geral + 1 if e["regra"] == "art17" else None
        aceito = informado >= piso and (teto_min is None or informado <= teto_min)
        legal = f"de {piso}" + (f" a {teto_min}" if teto_min else "") + " anos, somado o período adicional"
    else:
        aceito = informado in {geral, prof}
        legal = " ou ".join(str(x) for x in sorted({geral} | ({prof} if prof is not None else set())))
        legal += " anos"
    if not aceito:
        raise EntradaInvalida(f"tempo_minimo_da_regra_anos {informado} incompatível com a regra '{e['regra']}': o mínimo "
                              f"legal é {legal} ({fund}); o descarte só pode excluir contribuições mantido esse "
                              "mínimo (EC 103, art. 26, §6º)")


# ------------------------------------------------------------------ entrada

# Até 12 dígitos inteiros e 8 decimais: a soma de 1.200 salários cabe na precisão de 28 dígitos do
# Decimal, e nenhuma operação chega a decimal.InvalidOperation (que sairia em exit 1, sem JSON).
# Só algarismos ASCII e fullmatch: \d aceitaria dígitos de outras escritas e "$" um "\n" no fim.
RE_DECIMAL = re.compile(r"-?[0-9]{1,12}(\.[0-9]{1,8})?")
RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
RE_COMP = re.compile(r"([0-9]{4})-([0-9]{2})")
ANO_MIN, ANO_MAX = 1960, 2100


def _mostra(valor):
    """Valor recebido, curto e só ASCII, para mensagem de erro (nunca falha: entrada pode ser qualquer coisa)."""
    try:
        texto = ascii(valor)
    except Exception:                      # aninhamento profundo, objeto exótico
        texto = f"<{type(valor).__name__}>"
    return texto if len(texto) <= 60 else texto[:57] + "..."


def _decimal(campo, valor):
    if not isinstance(valor, str) or not RE_DECIMAL.fullmatch(valor):
        raise EntradaInvalida(f"{campo}: esperado decimal como texto com ponto (ex.: \"5000.00\"), com no "
                              "máximo 12 dígitos inteiros e 8 decimais")
    d = Decimal(valor)
    if d < 0:
        raise EntradaInvalida(f"{campo}: não pode ser negativo")
    return d


def _data(campo, valor):
    if not isinstance(valor, str):
        raise EntradaInvalida(f"{campo}: esperado texto AAAA-MM-DD")
    try:
        if not RE_DATA.fullmatch(valor):     # fromisoformat do Python 3.11+ aceita também 20260101 e 2026-W01-1
            raise ValueError
        d = dt.date.fromisoformat(valor)
    except ValueError:
        raise EntradaInvalida(f"{campo}: data inválida {_mostra(valor)} (formato AAAA-MM-DD)")
    if not dt.date(ANO_MIN, 1, 1) <= d <= dt.date(ANO_MAX, 12, 31):
        raise EntradaInvalida(f"{campo}: fora do intervalo 1960–2100")
    return d


def _bool(campo, valor):
    if not isinstance(valor, bool):
        raise EntradaInvalida(f"{campo}: esperado true ou false")
    return valor


def _inteiro(campo, valor, maximo=80):
    if isinstance(valor, bool) or not isinstance(valor, int) or not 0 <= valor <= maximo:
        raise EntradaInvalida(f"{campo}: inteiro entre 0 e {maximo}")
    return valor


def _lista_decimal(campo, valor):
    if not isinstance(valor, list) or not valor:
        raise EntradaInvalida(f"{campo}: lista não vazia de decimais em texto")
    if len(valor) > 1200:
        raise EntradaInvalida(f"{campo}: mais de 1.200 salários")
    return [_decimal(f"{campo}[{i}]", v) for i, v in enumerate(valor)]


def _enum(campo, valor, opcoes):
    if valor not in opcoes:
        raise EntradaInvalida(f"{campo}: {_mostra(valor)} fora de {list(opcoes)}")
    return valor


def _comp(campo, valor):
    """(ano, mês) de 'AAAA-MM'. O ano fica no intervalo das datas (1960–2100): com '0000', dt.date(0, …) quebraria
    na comparação com o pagamento (ValueError fora da validação, exit 1 sem JSON — revisão r4, achado 2)."""
    m = RE_COMP.fullmatch(valor) if isinstance(valor, str) else None
    if not m or not 1 <= int(m.group(2)) <= 12 or not ANO_MIN <= int(m.group(1)) <= ANO_MAX:
        raise EntradaInvalida(f"{campo}: competência inválida (use AAAA-MM, ano entre {ANO_MIN} e {ANO_MAX})")
    return int(m.group(1)), int(m.group(2))


def _datas_vencimento(valor):
    """{competência: vencimento devido}: a data em que a prestação DEVERIA ter sido paga (Lei 8.213, art. 103,
    parágrafo único; IN 128, art. 595, §§1º e 2º: a primeira data de validade do crédito emitido), nunca a do
    pagamento realizado, que não muda a prescrição. O período é conferido em normaliza()."""
    if not isinstance(valor, dict):
        raise EntradaInvalida("datas_vencimento: esperado objeto {\"AAAA-MM\": \"AAAA-MM-DD\"}")
    out = {}
    for k, v in valor.items():
        c = _comp(f"datas_vencimento[{_mostra(k)}]", k)
        d = _data(f"datas_vencimento[{k}]", v)
        if d < dt.date(c[0], c[1], 1):
            raise EntradaInvalida(f"datas_vencimento: {k} com vencimento em {v}, antes do próprio mês da competência")
        out[c] = d
    return out


def normaliza(bruto):
    if not isinstance(bruto, dict):
        raise EntradaInvalida("a entrada deve ser um objeto JSON")
    e = {k: v for k, v in bruto.items() if not k.startswith("_")}
    desconhecidos = sorted(set(e) - set(CAMPOS))
    if desconhecidos:
        raise EntradaInvalida(f"campo(s) desconhecido(s): {desconhecidos}")
    out = {}
    for campo, spec in CAMPOS.items():
        v = e.get(campo)
        if v is None:
            out[campo] = None
        elif spec["tipo"] == "enum":
            out[campo] = _enum(campo, v, spec["valores"])
        elif spec["tipo"] == "decimal":
            out[campo] = _decimal(campo, v)
        elif spec["tipo"] == "data":
            out[campo] = _data(campo, v)
        elif spec["tipo"] == "bool":
            out[campo] = _bool(campo, v)
        elif spec["tipo"] == "inteiro":
            out[campo] = _inteiro(campo, v, 1200 if campo in ("quantidade", "tempo_contribuicao_meses") else 80)
        elif spec["tipo"] == "objeto":
            out[campo] = _datas_vencimento(v)
        else:
            out[campo] = _lista_decimal(campo, v)

    for campo in ("modo", "especie", "sexo", "data_filiacao", "fato_gerador"):
        if out[campo] is None:
            raise EntradaInvalida(f"{campo}: obrigatório")
    formas = [f for f, presente in (("salarios_contribuicao", out["salarios_contribuicao"] is not None),
                                    ("media", out["media"] is not None),
                                    ("soma+quantidade", out["soma"] is not None or out["quantidade"] is not None))
              if presente]
    if len(formas) > 1:
        raise EntradaInvalida(f"use uma só forma de média; vieram {formas}")
    if (out["soma"] is None) != (out["quantidade"] is None):
        raise EntradaInvalida("soma e quantidade vêm juntas")
    if out["quantidade"] == 0:
        raise EntradaInvalida("quantidade: ao menos 1 salário")

    if out["modo"] == "concessao":
        if out["datas_vencimento"] is not None:
            raise EntradaInvalida("datas_vencimento: só no modo revisao")
        if out["media_acima_do_teto"] is not None:
            raise EntradaInvalida("media_acima_do_teto: só no modo revisao")
        meses, anos = out["tempo_contribuicao_meses"], out["tempo_contribuicao_anos"]
        if meses is not None and anos is not None and not anos * 12 <= meses <= anos * 12 + 11:
            raise EntradaInvalida(f"tempo_contribuicao_meses {meses} incompatível com tempo_contribuicao_anos {anos} "
                                  f"(anos completos: de {anos * 12} a {anos * 12 + 11} meses)")
        if out["dib"] is not None:
            fg = out["fato_gerador"]
            if out["especie"] == "incapacidade-permanente" and out["dib"] < fg:
                raise EntradaInvalida("dib: anterior ao fato gerador (a DIB da incapacidade permanente não antecede "
                                      "a DII — Lei 8.213, art. 43)")
            if out["especie"] == "aposentadoria" and not (
                    fg - dt.timedelta(days=JANELA_DESLIGAMENTO) <= out["dib"] <= fg):
                raise EntradaInvalida("dib: fora de [DER − 90 dias, DER] (a aposentadoria começa na DER ou no "
                                      "desligamento requerido até 90 dias depois dele — Lei 8.213, arts. 49 e 54)")
        for campo in ("regra", "tempo_contribuicao_anos"):
            if out[campo] is None:
                raise EntradaInvalida(f"{campo}: obrigatório no modo concessao")
        regra = out["regra"]
        if regra.startswith("incapacidade") and out["especie"] != "incapacidade-permanente":
            raise EntradaInvalida(f"regra '{regra}' exige especie 'incapacidade-permanente'")
        if not regra.startswith("incapacidade") and out["especie"] != "aposentadoria":
            raise EntradaInvalida(
                f"regra '{regra}' é de aposentadoria: especie tem de ser 'aposentadoria' (auxílios: "
                "calc_previdenciario_incapacidade.py)")
        if regra in ("art19-especial", "art21") and out["atividade_especial_anos"] is None:
            raise EntradaInvalida(f"atividade_especial_anos: obrigatório na regra '{regra}' (15, 20 ou 25)")
        if out["descartar"]:
            if out["especie"] == "incapacidade-permanente":
                raise EntradaInvalida(
                    "descartar = true não se aplica à aposentadoria por incapacidade permanente: a exclusão de "
                    "contribuições é só das aposentadorias para as quais se exige tempo mínimo de contribuição "
                    "(EC 103, art. 26, §6º; IN 128, art. 228, §§1º e 2º)")
            if out["salarios_contribuicao"] is None:
                raise EntradaInvalida("descartar = true exige salarios_contribuicao (o descarte é salário a salário)")
            if out["tempo_minimo_da_regra_anos"] is None:
                raise EntradaInvalida("tempo_minimo_da_regra_anos: obrigatório com descartar = true")
    else:
        if out["tempo_contribuicao_meses"] is not None:
            raise EntradaInvalida("tempo_contribuicao_meses: só no modo concessao")
        for campo in ("rmi_paga", "rmi_devida", "dib", "data_primeiro_pagamento", "abono"):
            if out[campo] is None:
                raise EntradaInvalida(f"{campo}: obrigatório no modo revisao")
        if out["data_ajuizamento"] is None and out["data_requerimento_revisao"] is None:
            raise EntradaInvalida("data_ajuizamento (ou data_requerimento_revisao): obrigatória no modo revisao")
        if out["data_ajuizamento"] is not None and out["data_requerimento_revisao"] is not None:
            raise EntradaInvalida("informe só um marco: data_ajuizamento ou data_requerimento_revisao")
        if out["data_primeiro_pagamento"] < out["dib"]:
            raise EntradaInvalida("data_primeiro_pagamento: anterior à dib")
        ref = out["data_ajuizamento"] or out["data_requerimento_revisao"]
        for c in out["datas_vencimento"] or {}:
            if not (out["dib"].year, out["dib"].month) <= c <= (ref.year, ref.month):
                raise EntradaInvalida(f"datas_vencimento: competência {c[0]:04d}-{c[1]:02d} fora do período da DIB "
                                      "ao marco")
    # Limites contraditórios são entrada inválida, não cálculo (revisão r6, MAJOR 4): teto 100,00 com salário mínimo
    # 1.621,00 saía em exit 0 com RMI 100,00.
    for campo in ("teto", "salario_minimo", "fator"):
        if out[campo] is not None and out[campo] == 0:
            raise EntradaInvalida(f"{campo}: tem de ser maior que zero")
    if out["teto"] is not None and out["salario_minimo"] is not None and out["salario_minimo"] > out["teto"]:
        raise EntradaInvalida(f"salario_minimo {out['salario_minimo']} acima do teto {out['teto']}: limites "
                              "contraditórios (o piso do salário de benefício não supera o teto — Lei 8.213, art. 29, §2º)")
    if (out["tempo_minimo_da_regra_anos"] is not None and out["tempo_contribuicao_anos"] is not None
            and out["tempo_minimo_da_regra_anos"] > out["tempo_contribuicao_anos"]):
        raise EntradaInvalida("tempo_minimo_da_regra_anos acima de tempo_contribuicao_anos: sem o tempo mínimo a regra "
                              "não se aplica, e não há o que descartar (EC 103, art. 26, §6º)")
    if out["modo"] == "concessao":
        confere_minimos(out)
    if out["datas_vencimento"] is None:
        out["datas_vencimento"] = {}
    if out["descartar"] is None:
        out["descartar"] = False
    return out


# ------------------------------------------------------------------ utilidades

def q(v):
    return v.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def br(d):
    return d.strftime("%d/%m/%Y")


def soma_anos(d, anos):
    """CC art. 132 §3º: vence no dia de igual número; sem ele, no primeiro dia seguinte."""
    try:
        return d.replace(year=d.year + anos)
    except ValueError:                 # 29/02 em ano não bissexto
        return dt.date(d.year + anos, 3, 1)


def mes_seguinte(ano, mes):
    return (ano + 1, 1) if mes == 12 else (ano, mes + 1)


def competencias(de, ate):
    """Competências (ano, mês) de 'de' a 'ate', inclusive."""
    a, m = de
    while (a, m) <= ate:
        yield a, m
        a, m = mes_seguinte(a, m)


def _consulta_tabela(arq, data, chave):
    tabela = json.loads(Path(arq).read_text(encoding="utf-8"))
    ini = dt.date.fromisoformat(tabela["intervalo"]["inicio"])
    fim = dt.date.fromisoformat(tabela["intervalo"]["fim"])
    fonte = {"arquivo": f"scripts/data/{Path(arq).name}", "data_captura": tabela.get("data_captura")}
    if not ini <= data <= fim:
        return None, fonte
    for linha in tabela["linhas"]:
        a = dt.date.fromisoformat(linha["vigencia_inicio"])
        b = dt.date.fromisoformat(linha["vigencia_fim"]) if linha.get("vigencia_fim") else fim
        if a <= data <= b and linha.get(chave) is not None:
            fonte["norma"] = linha.get("norma")
            fonte["arquivo_lei"] = linha.get("arquivo")
            return Decimal(linha[chave]), fonte
    return None, fonte


def parametro(e, campo, arq, chave, rotulo, data, faltantes, alternativa=""):
    if e[campo] is not None:
        return e[campo], {"origem": "informado na entrada"}
    valor, fonte = _consulta_tabela(arq, data, chave)
    if valor is None:
        msg = (f"{rotulo} de {data.year}: fora de scripts/data/{Path(arq).name} (valor não verificado em "
               f"context/lei/); informe '{campo}'{alternativa}")
        if msg not in faltantes:
            faltantes.append(msg)
    return valor, fonte


def _marcos(arq):
    """Datas em que a tabela muda de valor (início de linha, dia seguinte ao fim de linha e ao fim do intervalo)."""
    tabela = json.loads(Path(arq).read_text(encoding="utf-8"))
    um = dt.timedelta(days=1)
    marcos = {dt.date.fromisoformat(tabela["intervalo"]["inicio"]),
              dt.date.fromisoformat(tabela["intervalo"]["fim"]) + um}
    for linha in tabela["linhas"]:
        marcos.add(dt.date.fromisoformat(linha["vigencia_inicio"]))
        if linha.get("vigencia_fim"):
            marcos.add(dt.date.fromisoformat(linha["vigencia_fim"]) + um)
    return marcos


def janela_dib(e):
    """(primeira DIB possível, última ou None se sem limite, descrição). Os limites do salário de benefício são os
    da DATA DE INÍCIO DO BENEFÍCIO (Lei 8.213, art. 29, §2º), não os do fato gerador (revisão r5, MAJOR 3)."""
    fg = e["fato_gerador"]
    if e["dib"] is not None:
        return e["dib"], e["dib"], f"DIB informada ({br(e['dib'])})"
    if e["especie"] == "incapacidade-permanente":
        return fg, None, "DIB não informada: na incapacidade permanente é posterior à DII (Lei 8.213, art. 43)"
    # Aposentadoria: o contrato (context/calculo-rmi.md, seção 6) define fato_gerador = DER. A DIB é a DER (Lei 8.213,
    # art. 49, I, "b", e II; art. 54) ou, para o empregado que requereu até 90 dias depois do desligamento, o
    # desligamento (art. 49, I, "a"). Sem 'dib' a janela inteira é contada e, se as leituras divergem, exit 3 com as
    # duas contas (revisão r6, MAJOR 2: antes a DIB era presumida na DER e o alerta não resolvia R$ 103 de RMI).
    ini = fg - dt.timedelta(days=JANELA_DESLIGAMENTO)
    return ini, fg, (f"DIB não informada: a DER ({br(fg)}; Lei 8.213, arts. 49, I, \"b\", e II, e 54) ou o desligamento "
                     f"do emprego requerido até 90 dias depois dele (art. 49, I, \"a\"), de {br(ini)} a {br(fg)}")


def limites(e, faltantes):
    """([(salário mínimo, teto, desde)], fontes, descrição, abertos): um par por vigência distinta dentro da janela da
    DIB. Data da janela anterior à última sem o limite na tabela entra com (None, None) e o motivo em 'abertos': a conta
    das outras leituras continua, e a RMI sai em exit 3 (revisão r6, MAJOR 2)."""
    ini, fim, rotulo = janela_dib(e)
    fontes = {}
    if fim is None:
        if e["teto"] is None or e["salario_minimo"] is None:
            faltantes.append("dib: o piso e o teto do salário de benefício são os da data de início do benefício "
                             "(Lei 8.213, art. 29, §2º); na incapacidade permanente a DIB é posterior à DII (art. 43) e "
                             "pode cair em ano de outros limites: informe dib, ou teto e salario_minimo")
            return [], fontes, rotulo, []
        fim = ini
    alternativa = "" if ini == fim else " ou 'dib' (a janela da DIB alcança essa data)"
    datas = {ini}
    for arq, campo in ((ARQ_TETO, "teto"), (ARQ_SALARIO_MINIMO, "salario_minimo")):
        if e[campo] is None:
            datas |= {d for d in _marcos(arq) if ini < d <= fim}
    pares, abertos = [], []
    for d in sorted(datas):
        destino = faltantes if d == fim else []
        teto, f_teto = parametro(e, "teto", ARQ_TETO, "teto", "teto do RGPS", d, destino, alternativa)
        sm, f_sm = parametro(e, "salario_minimo", ARQ_SALARIO_MINIMO, "valor", "salário mínimo", d, destino,
                             alternativa)
        if d != fim and destino:
            abertos += [m for m in destino if m not in abertos]
            pares.append((None, None, d))
            continue
        fontes.setdefault("teto", f_teto)
        fontes.setdefault("salario_minimo", f_sm)
        if teto is not None and sm is not None and sm > teto:
            # Um limite informado e o outro da tabela também podem se contradizer (revisão r6, MAJOR 4).
            raise EntradaInvalida(f"limites contraditórios na DIB de {br(d)}: salário mínimo {sm} acima do teto {teto} "
                                  "(confira teto e salario_minimo informados)")
        if teto is not None and sm is not None and all((sm, teto) != (a, b) for a, b, _ in pares):
            pares.append((sm, teto, d))
    if not (e["dib"] is None and e["especie"] == "incapacidade-permanente"):   # DIB sem limite posterior (art. 43)
        confere_limite_informado(e, ini, fim)
    return pares, fontes, rotulo, abertos


def confere_limite_informado(e, ini, fim):
    """Teto ou salário mínimo informado é o da lei na DIB (Lei 8.213, art. 29, §2º; CF, art. 201, §2º): com a janela da
    DIB inteira coberta pela tabela capturada, valor que não é o de nenhuma data dela contraria a lei (exit 2). Fora da
    tabela o informado é aceito: é para isso que o campo existe."""
    for arq, campo, chave, rotulo in ((ARQ_TETO, "teto", "teto", "teto do RGPS"),
                                      (ARQ_SALARIO_MINIMO, "salario_minimo", "valor", "salário mínimo")):
        if e[campo] is None:
            continue
        datas = {ini} | {d for d in _marcos(arq) if ini < d <= fim}
        vigentes = {d: _consulta_tabela(arq, d, chave)[0] for d in datas}
        if None in vigentes.values() or e[campo] in vigentes.values():
            continue
        lista = "; ".join(f"{v} desde {br(d)}" for d, v in sorted(vigentes.items()))
        raise EntradaInvalida(f"{campo} {e[campo]} não é o {rotulo} vigente na DIB ({lista}, scripts/data/{arq.name}): "
                              f"confira o valor informado ou a data")


# ------------------------------------------------------------------ dias úteis (art. 41-A)

class DiasBancarios:
    """Dia útil = expediente bancário (Lei 8.213, art. 41-A, §4º). Duas leituras: 'estrita' fecha só
    os feriados nacionais da tabela do motor; 'ampla' fecha também carnaval, Sexta-feira da Paixão e
    Corpus Christi, que não são feriados nacionais por lei. A janela de pagamento cobre as duas."""

    def __init__(self):
        if not ARQ_MOTOR_PRAZO.is_file():
            raise FileNotFoundError(str(ARQ_MOTOR_PRAZO))
        spec = importlib.util.spec_from_file_location("calc_previdenciario_prazo", ARQ_MOTOR_PRAZO)
        motor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(motor)
        self.pascoa = motor.pascoa
        self.arq_feriados = Path(motor.ARQ_FERIADOS_PADRAO)
        self.tabela = json.loads(self.arq_feriados.read_text(encoding="utf-8"))
        self.versao_motor = getattr(motor, "VERSAO", None)
        self._anos = {}

    def _do_ano(self, ano):
        if ano not in self._anos:
            dias = {}
            for f in self.tabela["fixos"]:
                d = dt.date(ano, *(int(x) for x in f["mes_dia"].split("-")))
                if f.get("vigencia_desde") and d < dt.date.fromisoformat(f["vigencia_desde"]):
                    continue
                dias[d] = f
            p = self.pascoa(ano)
            for f in self.tabela["moveis"]:
                dias[p + dt.timedelta(days=f["dias_da_pascoa"])] = f
            self._anos[ano] = dias
        return self._anos[ano]

    def util(self, d, ampla):
        if d.weekday() >= 5:
            return False
        f = self._do_ano(d.year).get(d)
        if not f:
            return True
        return False if f["tipo"] == "nacional" else not ampla

    def enesimo_util(self, ano, mes, n, ampla):
        """n-ésimo dia útil do mês, contado do dia 1."""
        d = dt.date(ano, mes, 1)
        while True:
            if self.util(d, ampla):
                n -= 1
                if n == 0:
                    return d
            d += dt.timedelta(days=1)

    def enesimo_antes_do_fim(self, ano, mes, n, ampla):
        """n-ésimo dia útil que antecede o fim do mês (o último dia não conta: leitura mais cedo)."""
        d = dt.date(ano, mes, calendar.monthrange(ano, mes)[1]) - dt.timedelta(days=1)
        while True:
            if self.util(d, ampla):
                n -= 1
                if n == 0:
                    return d
            d -= dt.timedelta(days=1)

    def janela(self, competencia):
        """(primeiro, último) dia possível de pagamento da competência (Lei 8.213, art. 41-A, §§2º a 4º).

        A lei distribui os beneficiários por dias de uma janela; não fixa um vencimento único. Acima de um salário
        mínimo: do 1º ao 5º dia útil do mês seguinte (§2º); até um salário mínimo: do 5º dia útil que antecede o fim
        do mês da competência ao 5º dia útil do seguinte (§3º). A faixa do benefício em cada competência não chega
        pelos CAMPOS: vale a janela do §3º, que contém a do §2º, nas duas leituras do dia útil bancário (§4º)."""
        prox = mes_seguinte(*competencia)
        ini = min(self.enesimo_antes_do_fim(*competencia, 5, a) for a in (False, True))
        fim = max(self.enesimo_util(*prox, 5, a) for a in (False, True))
        return ini, fim

    def janela_acima_do_minimo(self, competencia):
        """(primeiro, último) dia de pagamento da renda acima de um salário mínimo: do 1º ao 5º dia útil do mês
        seguinte ao da competência (Lei 8.213, art. 41-A, §2º), nas duas leituras do dia útil bancário (§4º)."""
        prox = mes_seguinte(*competencia)
        ini = min(self.enesimo_util(*prox, 1, a) for a in (False, True))
        fim = max(self.enesimo_util(*prox, 5, a) for a in (False, True))
        return ini, fim

    def janela_ate_o_decimo(self, competencia):
        """(primeiro, último) dia de pagamento até a competência 2004-03: do 1º ao 10º dia útil do mês seguinte (Lei
        8.213, art. 41, §4º, redação da Lei 8.444/1992). Sem definição legal de dia útil antes da MPv 404/2007, valem as
        duas leituras."""
        prox = mes_seguinte(*competencia)
        ini = min(self.enesimo_util(*prox, 1, a) for a in (False, True))
        fim = max(self.enesimo_util(*prox, 10, a) for a in (False, True))
        return ini, fim

    def fonte(self):
        return {"motor": ARQ_MOTOR_PRAZO.name, "versao_motor": self.versao_motor,
                "feriados": self.arq_feriados.name, "data_revisao": self.tabela.get("data_revisao")}


# ------------------------------------------------------------------ concessão

def coeficiente(e, anos):
    """(coeficiente, fundamento) da regra; None quando a regra usa fator ou conta própria."""
    regra, sexo = e["regra"], e["sexo"]
    if regra.startswith("incapacidade") and e["fato_gerador"] <= EC103:
        return Decimal("1.00"), "Lei 8.213, art. 44; IN 128, art. 233, II, \"a\" (fato gerador até 13/11/2019)"
    if regra in ("art20", "incapacidade-permanente-acidentaria"):
        fund = ("EC 103, art. 26, §3º, I (art. 20)" if regra == "art20"
                else "EC 103, art. 26, §3º, II; IN 128, art. 233, II, \"c\"")
        return Decimal("1.00"), fund
    if regra in ("art17", "adquirido-anterior"):
        return None, None
    base = 15 if sexo == "F" else 20
    if regra in ("art19-especial", "art21") and e["atividade_especial_anos"] == 15:
        base = 15
    excedente = max(0, anos - base)
    fund = (f"EC 103, art. 26, §2º{', §5º' if base == 15 else ''}: 60% + 2% × {excedente} ano(s) acima de {base}"
            " (sem teto de 100% no percentual)")
    return Decimal("0.60") + Decimal("0.02") * excedente, fund


def conta_concessao(e, regras, memoria, alertas, fonte):
    faltantes = []
    pares, fontes_lim, rotulo_dib, abertos = limites(e, faltantes)
    fonte.update(fontes_lim)
    sm, teto = (pares[0][0], pares[0][1]) if len(pares) == 1 and not faltantes else (None, None)
    regra = e["regra"]
    if e["fato_gerador"] <= EC103 and regra.startswith("art"):
        # Antes de 13/11/2019 a EC 103 não existia; no próprio dia, a EC 103, art. 3º, assegura os critérios da
        # legislação anterior a quem cumpriu os requisitos até a entrada em vigor. Nenhum dos dois fecha a conta
        # pelas regras de transição: fórmula do direito adquirido.
        faltantes.append(f"regra '{regra}' (transição da EC 103) com fato gerador (DER) {br(e['fato_gerador'])}, até "
                         "13/11/2019: valem os critérios da legislação da data dos requisitos (EC 103, arts. 3º e 36, "
                         "III); confira a DER ou use a regra 'adquirido-anterior'")
    # Antes da Lei 9.876/1999 a média era a dos últimos 36 salários em até 48 meses (IN 128, art. 221, II, "b"), não a
    # dos 80% maiores: fora do cálculo automático (revisão r6, BLOCKER 1 — DII em 1998 fechava R$ 480 pelos 40 maiores,
    # e a regra da época dava R$ 200). Vale a data mais cedo possível: fato gerador ou a primeira DIB da janela.
    minimo = minimo_legal(e)
    if minimo is not None:
        geral, prof, pedagio, fund_min = minimo
        if prof is not None and prof < geral and e["tempo_contribuicao_anos"] < geral:
            alertas.append(f"[VERIFICAR] tempo de contribuição de {e['tempo_contribuicao_anos']} anos abaixo do mínimo "
                           f"geral de {geral}: a regra só se aplica com o mínimo do professor, de {prof} anos de "
                           f"magistério exclusivo ({fund_min}), condição que não é campo desta conta.")
        if pedagio:
            alertas.append(f"[VERIFICAR] o direito pela regra '{regra}' exige também o período adicional ({fund_min}), "
                           "contado em dias sobre o tempo que faltava em 13/11/2019, e a idade; nenhum dos dois é campo "
                           "desta conta: confira pela conta aberta de context/calculo-transicao.md.")
    primeira = min(e["fato_gerador"], janela_dib(e)[0])
    antes_9876 = primeira < MARCO_9876
    if antes_9876:
        faltantes.append(f"fato gerador ou DIB possível em {br(primeira)}, antes de 29/11/1999 (publicação da Lei 9.876): "
                         "o período básico de cálculo é o dos últimos 36 salários de contribuição em até 48 meses (IN 128, "
                         "art. 221, II, \"b\"), regra fora do cálculo automático deste script; faça a conta à mão")

    # Guarda da COBERTURA: data em segmento não coberto nunca fecha (os faltantes acima já descrevem cada regime).
    fim_marco = e["fato_gerador"] if e["especie"] == "aposentadoria" else janela_dib(e)[1]
    ini_marco = e["fato_gerador"] if e["especie"] == "aposentadoria" else primeira
    fora = fora_da_cobertura(f"concessao/{e['especie']}", ini_marco, fim_marco)
    if fora and not faltantes:
        faltantes.append("data fora da cobertura temporal do script (" + "; ".join(s["regra"] for s in fora) + ")")

    aplica_135a = (e["especie"] == "aposentadoria" and e["data_filiacao"] <= MARCO_135A_FILIACAO
                   and e["fato_gerador"] >= MARCO_135A_FATO)
    if aplica_135a:
        memoria.append("filiado até 07/1994, aposentadoria que não é por incapacidade permanente, fato gerador "
                       "desde 05/05/2022 → divisor mínimo de 108 (Lei 8.213, art. 135-A; IN 128, art. 228, §4º)")
    elif e["especie"] == "incapacidade-permanente" and e["data_filiacao"] <= MARCO_135A_FILIACAO:
        memoria.append("aposentadoria por incapacidade permanente: exceção expressa do art. 135-A → divisor = "
                       "número de salários")

    # Incapacidade permanente com fato gerador até 13/11/2019: média dos 80% maiores salários (Lei 8.213,
    # art. 29, II; IN 128, art. 229). O arredondamento da quantidade não está em context/lei/: com 80% de n
    # fracionário, as duas leituras (para baixo e para cima) são contadas e, se divergirem, sai em exit 3.
    oitenta = e["especie"] == "incapacidade-permanente" and e["fato_gerador"] <= EC103
    salarios = e["salarios_contribuicao"]
    selecoes = None
    if oitenta:
        regras.append("Lei 8.213, art. 29, II; IN 128, art. 229: média dos 80% maiores salários (fato gerador "
                      "até 13/11/2019)")
    if salarios is not None:
        soma, quantidade = sum(salarios, Decimal("0")), len(salarios)
        if oitenta:
            exato = Decimal(quantidade) * Decimal("0.8")
            ks = sorted({max(1, int(exato.to_integral_value(rounding=ROUND_FLOOR))),
                         max(1, int(exato.to_integral_value(rounding=ROUND_CEILING)))})
            desc = sorted(salarios, reverse=True)
            selecoes = [(k, sum(desc[:k], Decimal("0"))) for k in ks]
            memoria.append(f"80% de {quantidade} salários = {exato}"
                           + ("" if len(ks) == 1 else f" (fracionário: testadas as leituras {ks[0]} e {ks[1]})"))
    else:
        soma, quantidade = e["soma"], e["quantidade"]
    if oitenta and soma is not None and salarios is None:
        faltantes.append("salarios_contribuicao: soma e quantidade não permitem escolher os 80% maiores salários "
                         "(Lei 8.213, art. 29, II; IN 128, art. 229); informe a lista ou a média já apurada")
    if oitenta and e["media"] is not None:
        alertas.append("[VERIFICAR] média informada: na incapacidade permanente com fato gerador até 13/11/2019 "
                       "ela tem de ser a dos 80% maiores salários (Lei 8.213, art. 29, II; IN 128, art. 229).")
    if soma is None and e["media"] is None:
        faltantes.append("média: sem salarios_contribuicao, media ou soma+quantidade (nunca RMI de cabeça)")
    if soma is None and e["media"] is not None and aplica_135a:
        faltantes.append("soma e quantidade dos salários: a média informada não permite aplicar o divisor "
                         "mínimo de 108 do art. 135-A")
    if regra == "art17" and e["fator"] is None:
        faltantes.append("fator previdenciário (art. 17, parágrafo único): sem a tábua do IBGE capturada, "
                         "informe 'fator' já apurado")
    if regra == "adquirido-anterior":
        faltantes.append("conta do direito adquirido (80% maiores salários, divisor do art. 3º, §2º, da Lei 9.876, "
                         "coeficiente e fator conforme a modalidade — idade, especial ou tempo de contribuição, com a "
                         "opção do art. 29-C —, que a entrada não informa): fora deste script")
    if e["descartar"] and regra == "art17":
        faltantes.append("descarte com fator previdenciário: o fator muda com o tempo descartado; refaça o fator")

    def media_de(s, n):
        div = max(n, DIVISOR_MINIMO) if aplica_135a else n
        return q(s / div), div

    if faltantes:
        adquirido = regra == "adquirido-anterior" or (e["fato_gerador"] <= EC103 and regra.startswith("art"))
        partes = [("média = soma dos 80% maiores salários desde 07/1994, corrigidos ÷ número desses salários "
                   "(Lei 8.213, art. 29, II; IN 128, art. 229)") if oitenta else
                  "média = soma dos salários desde 07/1994, corrigidos ÷ divisor"
                  + (" (divisor = max(quantidade, 108), art. 135-A)" if aplica_135a else " (divisor = quantidade)"),
                  f"média limitada = min(média, {teto if teto is not None else 'TETO[DIB]'})"]
        if antes_9876:
            partes = [REGRA_ANTERIOR_9876]
        elif adquirido:
            partes = [FORMULA_ADQUIRIDO]
        elif regra == "art17":
            partes.append("RMI = média limitada × fator previdenciário (EC 103, art. 17, parágrafo único)")
        else:
            c, f = coeficiente(e, e["tempo_contribuicao_anos"])
            partes.append(f"SB = max(média limitada, {sm if sm is not None else 'SM[DIB]'}) (Lei 8.213, art. 29, §2º)")
            partes.append(f"RMI = SB × {c} ({f})")
        partes.append(f"piso {sm if sm is not None else 'SM[DIB]'} e teto {teto if teto is not None else 'TETO[DIB]'}"
                      f" ({rotulo_dib})")
        return EXIT_FALTA, {"dados_faltantes": faltantes + [m for m in abertos if m not in faltantes],
                            "formula_aberta": "; ".join(partes) + ". Conta aberta em context/calculo-rmi.md."}

    resultados = []
    for sm, teto, desde in pares:
        locais = (list(regras), list(memoria), list(alertas), dict(fonte))
        if sm is None:
            resultados.append((desde, "não capturado", "não capturado", EXIT_FALTA, {"rmi": None}, locais))
            continue
        codigo, res = fecha(e, sm, teto, oitenta, aplica_135a, salarios, soma, quantidade, selecoes, media_de, *locais)
        resultados.append((desde, sm, teto, codigo, res, locais))
    chaves = {(c, r.get("rmi"), json.dumps(r.get("descarte"), sort_keys=True, default=str),
               r.get("formula_aberta") if c else None) for _, _, _, c, r, _ in resultados}
    if len(chaves) > 1 or abertos:
        return EXIT_FALTA, {
            "dados_faltantes": [f"dib: {rotulo_dib}; os limites do salário de benefício e da renda (Lei 8.213, art. 29, "
                                "§2º; CF, art. 201, §2º) mudam dentro dessa janela e mudam a RMI: informe dib"] + abertos,
            "formula_aberta": "[VERIFICAR] " + "; ".join(
                f"DIB desde {br(d)}: salário mínimo {sm}, teto {teto} → RMI {r.get('rmi') or 'em aberto'}"
                for d, sm, teto, _, r, _ in resultados)
                + (f" (a última leitura é a da DIB na DER, {br(e['fato_gerador'])}; as anteriores, a do desligamento — "
                   "Lei 8.213, art. 49, I, \"a\"; com o desligamento muda também o período básico de cálculo, que a média "
                   "informada fixou)" if e["dib"] is None and e["especie"] == "aposentadoria" else "")
                + ". Conta aberta em context/calculo-rmi.md."}
    desde, sm, teto, codigo, res, (r, m, a, f) = resultados[0]
    regras[:], memoria[:], alertas[:] = r, m, a
    fonte.clear()
    fonte.update(f)
    memoria.append(f"limites da DIB: salário mínimo {sm}, teto {teto} ({rotulo_dib})")
    if e["dib"] is None and e["especie"] == "aposentadoria":
        alertas.append("[VERIFICAR] DIB não informada: na DER ou no desligamento requerido até 90 dias depois dele (Lei "
                       "8.213, art. 49, I, \"a\") os limites dão a mesma RMI; o desligamento muda também o período "
                       "básico de cálculo, que a média informada já fixou: confira.")
    if len(resultados) > 1:
        alertas.append(f"[VERIFICAR] {rotulo_dib}: {len(resultados)} vigências de piso e teto na janela, mesma RMI "
                       "em todas.")
    res["limites_na_dib"] = {"salario_minimo": str(sm), "teto": str(teto), "dib": rotulo_dib}
    return codigo, res


def fecha(e, sm, teto, oitenta, aplica_135a, salarios, soma, quantidade, selecoes, media_de,
          regras, memoria, alertas, fonte):
    """Conta da concessão com os limites (salário mínimo e teto) de uma DIB."""
    regra = e["regra"]

    def rmi_de(media, anos, passos):
        lim = min(media, teto)
        if lim < media:
            passos.append(f"média {media} limitada ao teto {teto} ("
                          + ("Lei 8.213, art. 29, II; IN 128, art. 229" if oitenta else "EC 103, art. 26, §1º") + ")")
        if regra == "art17":
            bruto, coef = q(lim * e["fator"]), None
            passos.append(f"RMI = {lim} × fator {e['fator']} = {bruto}")
        else:
            # Piso do salário de benefício ANTES do coeficiente (Lei 8.213, art. 29, §2º; Portaria Interministerial
            # MPS/MF 13/2026, art. 2º), como no calc_previdenciario_incapacidade.py (revisão r5, BLOCKER 1).
            sb = lim
            if sb < sm:
                passos.append(f"SB {lim} < salário mínimo {sm} → SB = {sm} (Lei 8.213, art. 29, §2º)")
                sb = sm
            coef, _ = coeficiente(e, anos)
            bruto = q(sb * coef)
            passos.append(f"RMI = {sb} × {coef} = {bruto}")
        rmi = bruto
        if rmi < sm:
            passos.append(f"{rmi} < salário mínimo {sm} → piso (CF, art. 201, §2º)")
            rmi = sm
        if rmi > teto:
            passos.append(f"{rmi} > teto {teto} → teto")
            rmi = teto
        return lim, coef, rmi

    fund_media = "EC 103, art. 26, caput"
    if selecoes is not None:
        anos = e["tempo_contribuicao_anos"]
        contas = []
        for k, s80 in selecoes:
            m80 = q(s80 / k)
            contas.append((k, s80, m80, rmi_de(m80, anos, [])[2]))
        if len({c[3] for c in contas}) > 1:
            return EXIT_FALTA, {
                "dados_faltantes": [f"arredondamento da quantidade dos 80% maiores de {quantidade} salários "
                                    "(número fracionário) não capturado em context/lei/; as duas leituras dão RMI "
                                    "diferentes"],
                "formula_aberta": "; ".join(f"com {k} maiores: média {s} ÷ {k} = {m}, RMI {r}" for k, s, m, r in contas)
                                  + ". Conta aberta em context/calculo-rmi.md."}
        k, soma, media, _ = contas[-1]
        divisor = k
        memoria.append(f"média dos {k} maiores = {soma} ÷ {k} = {media}"
                       + ("" if len(contas) == 1 else " (as duas leituras dão a mesma RMI)"))
        fund_div = "Lei 8.213, art. 29, II; IN 128, art. 229: número dos 80% maiores salários"
        fund_media = "Lei 8.213, art. 29, II; IN 128, art. 229"
        if len(contas) > 1:
            alertas.append(f"[VERIFICAR] 80% de {quantidade} salários é fracionário; o arredondamento não está em "
                           "context/lei/, mas as duas leituras dão a mesma RMI.")
    elif soma is not None:
        media, divisor = media_de(soma, quantidade)
        memoria.append(f"média = {soma} ÷ {divisor} = {media}")
        fund_div = ("Lei 8.213, art. 135-A; IN 128, art. 228, §4º" if aplica_135a and divisor != quantidade
                    else "EC 103, art. 26, caput: número de salários")
    else:
        media, divisor = e["media"], None
        fund_div = "média informada na entrada"
        memoria.append(f"média informada = {media}")
    anos = e["tempo_contribuicao_anos"]
    passos = []
    lim, coef, rmi = rmi_de(media, anos, passos)
    memoria.extend(passos)
    if regra == "art17" and e["fator"] < 1 and media > teto:
        # Duas leituras sem dispositivo que as concilie em context/lei/: a EC 103, art. 26, §1º, limita a MÉDIA ao
        # teto e o art. 17, parágrafo único, multiplica pelo fator (teto × fator); a Lei 8.213, art. 29, I e §2º,
        # limita o SALÁRIO DE BENEFÍCIO, que já é média × fator (min(média × fator, teto)).
        alt = max(min(q(media * e["fator"]), teto), sm)
        if alt != rmi:
            return EXIT_FALTA, {
                "dados_faltantes": [f"ordem entre o teto e o fator previdenciário com média {media} acima do teto "
                                    f"{teto} e fator {e['fator']} < 1: a EC 103 (art. 26, §1º, e art. 17, parágrafo "
                                    "único) dá uma RMI e a Lei 8.213 (art. 29, I e §2º) outra; nenhuma regra capturada "
                                    "em context/lei/ decide"],
                "formula_aberta": (f"[VERIFICAR] RMI = min(média, teto) × fator = {rmi} (EC 103, arts. 17, parágrafo "
                                   f"único, e 26, §1º) ou min(média × fator, teto) = {alt} (Lei 8.213, art. 29, I e "
                                   "§2º). Conta aberta em context/calculo-rmi.md.")}
    _, fund_coef = coeficiente(e, anos) if coef is not None else (None, "EC 103, art. 17, parágrafo único (fator)")
    regras.append(fund_coef)
    # Fato gerador até 13/11/2019 na incapacidade permanente: a base é a do regime anterior, não a EC 103.
    fund_hist = "Lei 8.213, art. 29, II; IN 128, art. 229"
    fonte.update({"media": fund_hist if oitenta else fund_media, "divisor_aplicado": fund_div,
                  "media_limitada_teto": fund_hist if oitenta else "EC 103, art. 26, §1º",
                  "coeficiente": fund_coef,
                  "rmi": (fund_hist if oitenta else "EC 103, art. 26") + "; Lei 8.213, art. 29, §2º (piso do SB); "
                         "CF, art. 201, §2º (piso)"})
    resultado = {
        "media": str(media),
        "divisor_aplicado": divisor,
        "fundamento": [f"divisor: {fund_div}", f"coeficiente: {fund_coef}"],
        "media_limitada_teto": str(lim),
        "coeficiente": str(coef) if coef is not None else None,
        "sem_descarte_rmi": str(rmi),
        "rmi": str(rmi),
        "descarte": None,
    }

    if e["descartar"]:
        minimo_meses = e["tempo_minimo_da_regra_anos"] * 12
        ordenados = sorted(salarios)

        def melhor_descarte(tempo_meses, minimo=minimo_meses):
            """(RMI, k, média, coeficiente, divisor) do melhor descarte e o k máximo permitido."""
            k_max = min(tempo_meses - minimo, len(salarios) - 1)
            melhor, restante = (rmi, 0, media, coef, divisor), soma
            for k in range(1, max(k_max, 0) + 1):
                restante -= ordenados[k - 1]
                m, div = media_de(restante, len(salarios) - k)
                _, c, r = rmi_de(m, (tempo_meses - k) // 12, [])
                if r > melhor[0]:
                    melhor = (r, k, m, c, div)
            return melhor, k_max

        # tempo_contribuicao_anos são anos completos: o tempo real vai de anos × 12 a anos × 12 + 11 meses, e os
        # meses a mais deixam descartar mais salários sem perder ano do coeficiente. Se o melhor descarte muda nessa
        # faixa, a RMI depende de dado que não chegou: exit 3 (o descarte abaixo é o do tempo em anos exatos). Com
        # tempo_contribuicao_meses (r9, item S da triagem R-B/RMI-03) o tempo é exato e o descarte fecha.
        meses_informados = e["tempo_contribuicao_meses"]
        tempo_meses = anos * 12 if meses_informados is None else meses_informados
        (r, k, m, c, div), k_max = melhor_descarte(tempo_meses)
        (r_mais, k_mais, _, _, _), _ = melhor_descarte(tempo_meses if meses_informados is not None else tempo_meses + 11)
        if meses_informados is not None:
            memoria.append(f"descarte com o tempo informado de {meses_informados} meses (EC 103, art. 26, §6º)")
        if r_mais != r:
            memoria.append(f"descarte com {anos} anos exatos: RMI {r} ({k} salário(s)); com até 11 meses além dos anos "
                           f"completos: RMI {r_mais} ({k_mais} salário(s))")
            resultado["descarte_em_aberto"] = {
                "tempo_em_anos_exatos": {"saiu": k, "rmi": str(r)},
                "tempo_com_11_meses_a_mais": {"saiu": k_mais, "rmi": str(r_mais)}}
        if k_max < 1:
            resultado["descarte"] = {"saiu": 0, "compensou": False,
                                     "motivo": "tempo mínimo da regra não deixa descartar nenhum salário"}
        else:
            resultado["descarte"] = {
                "saiu": k,
                "salarios_descartados": [str(x) for x in ordenados[:k]],
                "media_nova": str(m),
                "divisor_novo": div,
                "tempo_restante_anos": (tempo_meses - k) // 12,
                "coeficiente_novo": str(c) if c is not None else None,
                "rmi": str(r),
                "compensou": k > 0,
                "fundamento": "EC 103, art. 26, §6º; IN 128, art. 228, §1º: o tempo descartado não conta para "
                              "nada, nem para o acréscimo de 2%" + ("; divisor mínimo de 108 mantido (art. 135-A)"
                                                                     if aplica_135a else ""),
            }
            if k:
                memoria.append(f"descarte: sem os {k} menor(es) salário(s), média {m} (divisor {div}), "
                               f"{(tempo_meses - k) // 12} anos, coeficiente {c} → RMI {r} > {rmi}: descartar")
                resultado["rmi"] = str(r)
            else:
                memoria.append(f"descarte testado de 1 a {k_max} salário(s): nenhuma RMI acima de {rmi}; não descartar")
            fonte["descarte"] = resultado["descarte"]["fundamento"]
        # O mínimo também pode depender de dado que a entrada não traz (revisão r7, MAJOR 1; "na dúvida, fórmula
        # aberta"): o pedágio dos arts. 17, II, e 20, IV, conta-se em dias e o campo é em anos completos (até 11 meses
        # a mais); o mínimo reduzido do professor exige magistério exclusivo, condição que não é campo.
        geral, prof, pedagio, fund_min = minimo_legal(e)
        informado = e["tempo_minimo_da_regra_anos"]
        leituras = []
        if pedagio:
            leituras.append(("minimo_com_pedagio_em_meses", f"mínimo com até 11 meses de período adicional além de "
                             f"{informado} anos ({fund_min})", minimo_meses + 11))
        if prof is not None and prof != geral and informado == prof:
            leituras.append(("minimo_geral_sem_magisterio", f"mínimo geral de {geral} anos, sem magistério exclusivo "
                             f"({fund_min})", geral * 12))
        dados = []
        if "descarte_em_aberto" in resultado:
            dados.append(f"tempo de contribuição em meses além dos {anos} anos completos: o melhor descarte (EC 103, "
                         f"art. 26, §6º) dá RMI {r} com {anos} anos exatos e até {r_mais} com 11 meses a mais; o tempo "
                         "em meses não veio: confira no CNIS e informe tempo_contribuicao_meses")
        for chave, rotulo_min, minimo in leituras:
            (r_min, k_min, _, _, _), _ = melhor_descarte(tempo_meses, minimo)
            if r_min != r:
                memoria.append(f"descarte com o mínimo de {informado} anos: RMI {r} ({k} salário(s)); {rotulo_min}: "
                               f"RMI {r_min} ({k_min} salário(s))")
                resultado.setdefault("descarte_em_aberto", {})[chave] = {"saiu": k_min, "rmi": str(r_min)}
                dados.append(f"tempo mínimo que o descarte tem de manter (EC 103, art. 26, §6º): com {informado} anos "
                             f"a RMI é {r}; na leitura '{rotulo_min}', {r_min}; confira no CNIS e na carta e decida à mão")
        if dados:
            resultado["rmi"] = None
            faixa = {r} | {Decimal(v["rmi"]) for v in resultado["descarte_em_aberto"].values()}
            return EXIT_FALTA, dict(resultado, dados_faltantes=dados, formula_aberta=(
                f"[VERIFICAR] RMI de {min(faixa)} a {max(faixa)} (com {anos} anos exatos e o mínimo de {informado} anos: {r}): para cada k menores salários descartados, "
                "média dos restantes × coeficiente do tempo restante em anos completos, mantido o tempo mínimo da regra "
                "(com o período adicional do pedágio, contado em dias, e o mínimo do professor só com magistério "
                "exclusivo); vale o maior. Conta aberta em context/calculo-rmi.md."))
    return EXIT_OK, resultado


# ------------------------------------------------------------------ revisão

ACRESCIMO_45 = Decimal("1.25")
FUND_45 = "Lei 8.213, art. 45, parágrafo único, \"a\" e \"b\""


def base_do_acrescimo(renda):
    """Base (centavos) cuja renda com o acréscimo de 25% (Lei 8.213, art. 45) é exatamente 'renda', ou None. Como a
    base anda de 1,25 em 1,25 centavo, há no máximo uma."""
    base = q(renda / ACRESCIMO_45)
    return base if q(base * ACRESCIMO_45) == renda else None


def leituras_da_renda(e, nome, renda, teto_dib, sm_dib=None):
    """[(com_acrescimo, base)] possíveis da renda informada (revisão r8, MAJOR 1). Só a incapacidade permanente tem o
    acréscimo de 25% do art. 45, devido ainda que o total supere o teto e recalculado sobre a base a cada reajuste
    (parágrafo único, "a" e "b"); a entrada não diz se a renda o inclui. Acima do teto da DIB, inclui (art. 33);
    até ele, as duas leituras valem, salvo se nenhuma base dá a renda com o acréscimo, ou se a base fica abaixo do
    salário mínimo da DIB (o piso do art. 33 é da base, não do acréscimo — r11). Lista vazia: acima do teto sem base
    que a explique."""
    if e["especie"] != "incapacidade-permanente":
        return [(False, renda)]
    base = base_do_acrescimo(renda)
    if teto_dib is not None and renda > teto_dib:
        return [] if base is None else [(True, base)]
    if base is not None and sm_dib is not None and base < sm_dib:
        base = None
    return [(False, renda)] + ([(True, base)] if base is not None else [])


def datas_de_reajuste(dib, fim):
    """(datas, limite, motivo): datas em (DIB, fim] em que a renda pode ter sido reajustada, pelo regime vigente em
    cada uma (REGIMES_DATA_REAJUSTE), e 'limite', o primeiro dia de período sem regime capturado (None se não há),
    com o motivo. Revisão r11, MAJOR 1: antes o reajuste era presumido em janeiro, e o de maio/2005 (DIB em 01/2005)
    sumia da conta."""
    if regime_data_reajuste(dib)["datas"] is None:
        return [], dib + dt.timedelta(days=1), (
            f"data e fator dos reajustes posteriores à DIB ({br(dib)}) não capturados: "
            f"{regime_data_reajuste(dib)['fonte']}; sem eles, a renda depois da DIB não fecha")
    tabela = json.loads(ARQ_REAJUSTES.read_text(encoding="utf-8"))
    datas = {dt.date.fromisoformat(l["vigencia_inicio"]) for l in tabela["linhas"]}
    fins = []
    for arq in (ARQ_SALARIO_MINIMO, ARQ_TETO):
        t = json.loads(Path(arq).read_text(encoding="utf-8"))
        datas |= {dt.date.fromisoformat(l["vigencia_inicio"]) for l in t["linhas"]}
        fins.append(dt.date.fromisoformat(t["intervalo"]["fim"]))
    limite, motivo = None, None
    if min(fins) < fim:
        limite = min(fins) + dt.timedelta(days=1)
        motivo = (f"salário mínimo e teto depois de {br(min(fins))} fora de scripts/data/: a data do reajuste (a do "
                  "salário mínimo — Lei 8.213, art. 41-A, caput) e o fator dali em diante não se conhecem")
    return sorted(d for d in datas if dib < d <= fim and (limite is None or d < limite)), limite, motivo


def evolucao_renda(e, fim, memoria):
    """(segmentos, limite, motivo, fonte): as duas rendas reajustadas em cada data de reajuste do regime vigente
    (datas_de_reajuste; Lei 8.213, art. 41-A; EC 103, art. 26, §7º), pro rata no primeiro reajuste pela DIB, com o
    piso de um salário mínimo (CF, art. 201, §2º). 'segmentos' = [(desde, {nome: [(com_acrescimo, base)]})], a
    partir da DIB, sobre os quais renda_da_competencia aplica o piso e o teto vigentes em cada competência (revisão
    r10). Da primeira data sem fator (ou sem dado que o fecha) em diante a renda não se conhece: 'limite' é essa data
    e 'motivo' diz o que falta (revisão r5, MAJOR 2: antes a diferença ficava congelada na da DIB)."""
    dib = e["dib"]
    tabela = json.loads(ARQ_REAJUSTES.read_text(encoding="utf-8"))
    linhas = {dt.date.fromisoformat(l["vigencia_inicio"]): l for l in tabela["linhas"]}
    fonte = {"arquivo": f"scripts/data/{ARQ_REAJUSTES.name}", "data_captura": tabela.get("data_captura"), "normas": [],
             "regime_da_data": [regime_data_reajuste(dib)["fonte"]]}
    paga, devida = e["rmi_paga"], e["rmi_devida"]
    segmentos = []
    teto_dib = _consulta_tabela(ARQ_TETO, dib, "teto")[0]
    sm_dib = _consulta_tabela(ARQ_SALARIO_MINIMO, dib, "valor")[0]
    leituras = {}
    for nome, v in (("paga", paga), ("devida", devida)):
        leituras[nome] = leituras_da_renda(e, nome, v, teto_dib, sm_dib)
        if not leituras[nome]:
            return segmentos, dib, (f"rmi_{nome} {v} acima do teto da DIB ({teto_dib}): só cabe com o acréscimo de 25% "
                                    f"({FUND_45}), mas nenhuma base dá {v} com ele; informe a renda com o acréscimo "
                                    "exato, para separar a base (reajustada e limitada ao teto) do acréscimo "
                                    "(recalculado sobre ela)"), fonte
        if leituras[nome][0][0]:
            memoria.append(f"rmi_{nome} {v} acima do teto da DIB ({teto_dib}): base {leituras[nome][0][1]} + "
                           f"acréscimo de 25% ({FUND_45}); a base é reajustada e limitada ao teto, o acréscimo é "
                           "recalculado sobre ela e o total pode superar o teto")
    segmentos.append((dib, {nome: list(leituras[nome]) for nome in ("paga", "devida")}))
    datas, limite, motivo = datas_de_reajuste(dib, fim)
    for d in datas:
        linha = linhas.get(d)
        if linha is None and so_piso_e_teto(d, linhas):
            # W3-reajustes r2 (decisão 1): só o mínimo ou o teto mudam; a renda se mantém e o piso e o teto vigentes
            # entram por competência (renda_da_competencia)
            memoria.append(f"{br(d)}: só o salário mínimo ou o teto mudam (sem reajuste acima do mínimo): renda "
                           "mantida; piso e teto da competência")
            continue
        if linha is not None and linha.get("dib_ate") and dib > dt.date.fromisoformat(linha["dib_ate"]):
            # 01/08/2006: só os benefícios mantidos em 31/03/2006 (Lei 11.430/2006, art. 3º); DIB posterior mantém a
            # renda, com o piso e o teto da competência
            memoria.append(f"{br(d)}: DIB posterior a {linha['dib_ate']}, sem o reajuste da data ({linha['norma']}): "
                           "renda mantida; piso e teto da competência")
            continue
        if linha is None:
            falta = LACUNAS_REAJUSTE.get(d, f"sem fator capturado em context/lei/ (scripts/data/{ARQ_REAJUSTES.name})")
            return segmentos, d, (f"possível reajuste em {br(d)} (Lei 8.213, art. 41-A, caput: na data do reajuste do "
                                  "salário mínimo; o mínimo ou o teto mudam nessa data em scripts/data/) "
                                  f"{falta}; sem ele, a renda de {br(d)} em diante não fecha"), fonte
        if dib >= dt.date.fromisoformat(linha["pro_rata_desde"]):
            pct = linha["pro_rata"].get(f"{dib.year:04d}-{dib.month:02d}")
            if pct is None:
                return segmentos, d, f"fator pro rata do reajuste de {br(d)} para DIB em {dib.month:02d}/{dib.year} ausente", fonte
            rotulo = f"pro rata da DIB em {dib.month:02d}/{dib.year}"
        else:
            pct, rotulo = linha["integral"], "integral"
        inc = linha.get("incorporacao_teto")
        if inc and dt.date.fromisoformat(inc["dib_de"]) <= dib <= dt.date.fromisoformat(inc["dib_ate"]):
            if e["media_acima_do_teto"] is None:
                return segmentos, d, (f"media_acima_do_teto: DIB em {br(dib)} → no reajuste de {br(d)} incorpora-se à "
                                      "renda a diferença percentual entre a média e o teto, quando positiva "
                                      f"({inc['norma']}); informe se a média de alguma das duas RMIs superou o teto da "
                                      "DIB"), fonte
            if e["media_acima_do_teto"]:
                return segmentos, d, (f"incorporação do teto no reajuste de {br(d)} ({inc['norma']}): o percentual é a "
                                      "diferença entre a média e o teto vigente na DIB, que a revisão não recebe"), fonte
        fator = 1 + Decimal(pct) / 100
        sm, _ = _consulta_tabela(ARQ_SALARIO_MINIMO, d, "valor")
        teto, _ = _consulta_tabela(ARQ_TETO, d, "teto")
        if sm is None or teto is None:
            return segmentos, d, (f"piso e teto de {br(d)} (CF, art. 201, §2º) fora de scripts/data/: sem eles a renda "
                                  "reajustada não se confere"), fonte
        novos, base, sobre = [], leituras, ""
        if linha.get("sobre_renda_de"):
            # o fator incide sobre a renda da competência indicada (a de março/2006) e substitui o reajuste de
            # linha["substitui"] (Lei 11.430/2006, art. 3º, caput e §4º)
            a, mes = (int(x) for x in linha["sobre_renda_de"].split("-"))
            ref = dt.date(a, mes, calendar.monthrange(a, mes)[1])
            base = [seg for desde, seg in segmentos if desde <= ref][-1]
            sobre = f" sobre a renda de {mes:02d}/{a}, em substituição ao reajuste de {linha['substitui']}"
        for nome in ("paga", "devida"):
            reajustadas, totais, passos = [], set(), []
            for com, v in base[nome]:
                r = q(v * fator)
                passo = f"{'base da ' if com else ''}RMI {nome} {v} × {fator} ({rotulo}{sobre}) = {r}"
                if r < sm:
                    if e["especie"] == "outra":
                        return segmentos, d, (f"RMI {nome} reajustada em {br(d)} ({r}) abaixo do salário mínimo {sm}: "
                                              "o piso da renda depende da espécie (o auxílio-acidente não o tem — "
                                              "Decreto 3.048, art. 42, parágrafo único); 'outra' não decide"), fonte
                    passo += f" < salário mínimo {sm} → {sm} (CF, art. 201, §2º)"
                    r = sm
                if r > teto:
                    passo += f" > teto {teto} → {teto}"
                    r = teto
                total = q(r * ACRESCIMO_45) if com else r
                if com:
                    passo += f"; + 25% recalculado sobre a base ({FUND_45}) = {total}"
                reajustadas.append((com, r))
                totais.add(total)
                passos.append(passo)
            if len(totais) > 1:
                return segmentos, d, (f"rmi_{nome}: na incapacidade permanente a renda pode incluir o acréscimo de 25% "
                                      f"({FUND_45}), que a entrada não separa; no reajuste de {br(d)} a renda reajustada "
                                      f"é {min(totais)} ou {max(totais)} ({' | '.join(passos)}): confira na carta de "
                                      "concessão a base e o acréscimo"), fonte
            leituras[nome] = reajustadas
            novos.append(totais.pop())
            memoria.append(f"reajuste de {br(d)}: " + (passos[0] if len(passos) == 1 else
                                                       " | ".join(passos) + " (as leituras coincidem)"))
        segmentos.append((d, {nome: list(leituras[nome]) for nome in ("paga", "devida")}))
        if linha["norma"] not in fonte["normas"]:
            fonte["normas"].append(linha["norma"])
    return segmentos, limite, motivo, fonte


def renda_da_competencia(e, renda_info, comp):
    """((paga, devida), None) devidas na competência, ou (None, motivo). A base do segmento de reajuste vigente na
    competência recebe o piso de um salário mínimo e o teto VIGENTES NA COMPETÊNCIA (Lei 8.213, art. 33; CF, art. 201,
    §2º), não os da data do reajuste (revisão r10, MAJOR). Competência que alcança a data sem regime ou sem fator
    ('limite') fica sem renda; reajuste no meio da competência dá dois valores ao mês (revisão r11, MAJOR 1). Na
    incapacidade permanente o limite é da base e o acréscimo de 25% é recalculado sobre ela (art. 45, parágrafo
    único)."""
    segmentos, limite, motivo = renda_info
    ano, mes = comp
    # Primeiro e último dia da competência (desde a DIB): o limite pode mudar no meio do mês (ex.: mínimo de
    # R$ 151,00 desde 03/04/2000); aí a renda que ele alcança não fecha sem proporcionalizar.
    dias = (max(dt.date(ano, mes, 1), e["dib"]), dt.date(ano, mes, calendar.monthrange(ano, mes)[1]))
    if limite is not None and dias[1] >= limite:
        return None, motivo
    i = max(k for k, (desde, _) in enumerate(segmentos) if desde <= dias[0])
    if i + 1 < len(segmentos) and segmentos[i + 1][0] <= dias[1]:
        return None, (f"reajuste em {br(segmentos[i + 1][0])}, no meio da competência: a renda do mês tem dois "
                      "valores; proporcionalize à mão (Lei 8.213, art. 41-A)")
    base_do_mes = segmentos[i][1]
    sms = [_consulta_tabela(ARQ_SALARIO_MINIMO, d, "valor")[0] for d in dias]
    tetos = [_consulta_tabela(ARQ_TETO, d, "teto")[0] for d in dias]
    if None in sms or None in tetos:
        return None, ("piso e teto da competência (Lei 8.213, art. 33) fora de scripts/data/: sem eles a renda da "
                      "competência não se confere")
    sm, teto = sms[1], tetos[1]
    rendas = []
    for nome in ("paga", "devida"):
        totais = set()
        for com, v in base_do_mes[nome]:
            r = v
            if (sms[0] != sms[1] and r < max(sms)) or (tetos[0] != tetos[1] and r > min(tetos)):
                return None, (f"limite que muda dentro da competência (salário mínimo {sms[0]} → {sms[1]}; teto "
                              f"{tetos[0]} → {tetos[1]}) alcança a RMI {nome} ({v}): a renda do mês tem dois valores; "
                              "proporcionalize à mão (Lei 8.213, art. 33)")
            if v < sm:
                if e["especie"] == "outra":
                    return None, (f"RMI {nome} ({v}) abaixo do salário mínimo vigente na competência ({sm}): "
                                  "o piso da renda depende da espécie (o auxílio-acidente não o tem — Decreto 3.048, "
                                  "art. 42, parágrafo único); 'outra' não decide")
                r = sm
            r = min(r, teto)
            totais.add(q(r * ACRESCIMO_45) if com else r)
        if len(totais) != 1:
            return None, (f"rmi_{nome}: na incapacidade permanente a renda pode incluir o acréscimo de 25% ({FUND_45}), "
                          f"que a entrada não separa; com o piso {sm} e o teto {teto} vigentes na competência, a "
                          f"renda é {min(totais)} ou {max(totais)}: confira na carta de concessão a base e o "
                          "acréscimo")
        rendas.append(totais.pop())
    return tuple(rendas), None


def conta_revisao(e, regras, memoria, alertas, fonte):
    ref = e["data_ajuizamento"] or e["data_requerimento_revisao"]
    rotulo_ref = "ajuizamento" if e["data_ajuizamento"] else "requerimento de revisão"
    premissas = []
    if e["data_requerimento_revisao"]:
        # Que o pedido administrativo suspenda ou interrompa a prescrição não está em context/lei/ (a IN 128, art. 595,
        # §4º, trata do crédito do INSS): a conta abaixo é condicional a essa premissa.
        premissas.append("efeito do pedido administrativo de revisão sobre a prescrição: a conta toma o pedido como "
                         "marco, premissa sem dispositivo em context/lei/; decida, ou informe data_ajuizamento no "
                         "lugar dele")
    # Renda fora do piso e do teto da DIB contraria a Lei 8.213, art. 33 (varredura r8): na aposentadoria, exit 2; na
    # incapacidade permanente acima do teto pode ser o acréscimo do art. 45, e em 'outra' o piso depende da espécie
    # (o auxílio-acidente não o tem — Decreto 3.048, art. 42, parágrafo único): alerta.
    sm_dib = _consulta_tabela(ARQ_SALARIO_MINIMO, e["dib"], "valor")[0]
    teto_dib = _consulta_tabela(ARQ_TETO, e["dib"], "teto")[0]
    for campo in ("rmi_paga", "rmi_devida"):
        v = e[campo]
        abaixo = sm_dib is not None and v < sm_dib
        acima = teto_dib is not None and v > teto_dib
        if not (abaixo or acima):
            continue
        limite = f"salário mínimo {sm_dib}" if abaixo else f"teto {teto_dib}"
        if (e["especie"] == "aposentadoria" or (e["especie"] == "incapacidade-permanente" and abaixo)
                or (e["especie"] == "incapacidade-permanente" and v > q(teto_dib * ACRESCIMO_45))):
            if not abaixo and e["especie"] == "incapacidade-permanente":
                limite = f"teto {teto_dib} acrescido de 25% ({q(teto_dib * ACRESCIMO_45)}; {FUND_45})"
            raise EntradaInvalida(f"{campo} {v} {'abaixo do' if abaixo else 'acima do'} {limite} vigente na DIB "
                                  f"{br(e['dib'])}: a renda não fica fora desses limites (Lei 8.213, art. 33)")
        alertas.append(f"[VERIFICAR] {campo} {v} {'abaixo do' if abaixo else 'acima do'} {limite} da DIB: só cabe "
                       + ("com o acréscimo de 25% (Lei 8.213, art. 45)" if acima and e["especie"] != "outra" else
                          "em espécie sem esse limite (Lei 8.213, art. 33; Decreto 3.048, art. 42, parágrafo único)")
                       + "; confira na carta de concessão.")
    dif = e["rmi_devida"] - e["rmi_paga"]
    if dif <= 0:
        alertas.append("rmi_devida não supera rmi_paga: não há diferença a favor do segurado.")

    # Decadência (Lei 8.213, art. 103; CC, art. 132, §§1º e 3º). O calendário do motor de prazos dá a prorrogação do
    # termo em dia sem expediente (QA final r6, C1); sem ele, a decadência só fecha fora da janela da prorrogação.
    pp = e["data_primeiro_pagamento"]
    try:
        cal, erro_cal = DiasBancarios(), None
    except Exception as err:          # motor ausente, ilegível ou de outra versão: fórmula, não exit 2
        cal, erro_cal = None, err
    inicio_dec, nominal_dec, fim_dec, decadente, dec_fora = decadencia(pp, ref, e["dib"], cal)
    dec_calendario = bool(dec_fora) and bool(dec_fora[0].get("calendario"))
    dec_faltantes = []
    if dec_fora and not dec_calendario:
        # COBERTURA: redação do art. 103 que o script não implementa; nem prazo nem booleano (brief r13).
        indet = any(s.get("indeterminavel") for s in dec_fora)
        memoria.append(f"decadência: primeiro pagamento {br(pp)} "
                       + ("com DIB anterior a 28/06/1997: concessão indeterminável, duas leituras"
                          if indet else "fora da cobertura temporal do art. 103 implementado") + " (ver formula_aberta)")
        dec_faltantes = [f"decadência: {dec_fora[0]['regra']} (fonte: {_TEMA_313})" if indet else
                         f"decadência: primeiro pagamento em {br(pp)}, na vigência de "
                         + "; ".join(s["regra"] for s in dec_fora) + ": fora do cálculo automático (borda: "
                         + "; ".join(s.get("fonte_de") or s.get("fonte_ate") for s in dec_fora) + ")"]
    else:
        tema = " (STF Tema 313: concessão anterior à MP 1.523/1997)" if pp < EDICAO_MP_1523_9 else ""
        termo = (f"termo nominal {br(nominal_dec)} (dia de igual número, CC, art. 132, §3º)"
                 + ("; " + dec_fora[0]["regra"] if dec_calendario else
                    f" → fim {br(fim_dec)}" + (" (prorrogado do dia sem expediente ao seguinte dia útil, "
                                                 f"{FUND_PRORROGACAO})" if fim_dec != nominal_dec else "")))
        memoria.append(f"decadência: primeiro pagamento {br(pp)} → início {br(inicio_dec)}{tema} → {termo}; "
                       f"{rotulo_ref} {br(ref)} → "
                       + {True: "DECADENTE", False: "não decadente", None: "decadência em aberto"}[decadente])
        regras.append("Lei 8.213, art. 103, caput; CC, art. 132, §§1º e 3º; Lei 662/1949, art. 1º"
                      + ("; STF Tema 313" if tema else ""))
        if dec_calendario:
            dec_faltantes = [f"decadência ({VEREDITO_DECADENCIA[decadente]} no marco {br(ref)}): {dec_fora[0]['regra']}"]
    if decadente:
        alertas.append("Decadência consumada (Lei 8.213, art. 103): a revisão do ato de concessão está "
                       "impedida; as diferenças abaixo só valem se a tese não for revisão do ato.")
        base = fim_dec or nominal_dec
        if base and ref <= base + dt.timedelta(days=PRORROGACAO_MAX_DIAS):
            alertas.append(f"[VERIFICAR] decadência consumada há poucos dias (fim {br(base)}, {rotulo_ref} {br(ref)}): "
                           "feriado estadual ou municipal no termo não consta da tabela do motor e o prorrogaria "
                           f"({FUND_PRORROGACAO}); confira o calendário do local antes de dar a revisão por impedida.")

    if cal is None:
        err = erro_cal
        return EXIT_FALTA, {
            "decadente": decadente, "prazo_decadencial_final": fim_dec.isoformat() if fim_dec else None,
            "diferenca_mensal": str(dif),
            "dados_faltantes": dec_faltantes + [f"motor de prazos (calc_previdenciario_prazo.py) indisponível ao lado deste "
                                f"script: {err}; sem ele não há dia útil bancário para a janela de pagamento "
                                "(Lei 8.213, art. 41-A, §§2º a 4º)"],
            "formula_aberta": ("parcela prescrita se ajuizamento > (último dia da janela de pagamento da competência, "
                               "pelo regime vigente nela — Lei 8.213, art. 41, §4º, até 2006, e art. 41-A, §§2º e 3º — "
                               "+ 5 anos); devidas = competências não prescritas cuja janela "
                               "acaba antes do ajuizamento; janela que cruza um dos marcos fica em aberto; "
                               "total = Σ (renda devida − renda paga de cada competência, reajustadas na data de cada "
                               "reajuste do salário mínimo — Lei 8.213, art. 41-A, caput — e com o piso e o teto vigentes na competência — Lei 8.213, art. 33) + abonos não "
                               "prescritos" + ("; " + "; ".join(s["linha"] for s in dec_fora) if dec_fora else "")
                               + ". Conta aberta em context/calculo-rmi.md."),
        }
    fonte["dias_uteis"] = cal.fonte()
    # Diferença de cada competência = renda devida − renda paga vigentes nela, ambas reajustadas em cada data de reajuste
    # do regime (Lei 8.213, art. 41-A; revisão r11, MAJOR 1); a diferença da DIB não se congela (revisão r5, MAJOR 2).
    fim_ref = dt.date(ref.year, ref.month, calendar.monthrange(ref.year, ref.month)[1])
    segmentos, limite_renda, motivo_reajuste, fonte_reajuste = evolucao_renda(e, fim_ref, memoria)
    renda_info = (segmentos, limite_renda, motivo_reajuste)
    regras.append("Lei 8.213, art. 41-A (reajuste anual da renda, na data do reajuste do salário mínimo)")
    regras.append("Lei 8.213, art. 33 (piso e teto vigentes em cada competência)")
    fonte["reajustes"] = fonte_reajuste
    _rendas = {}

    def renda(comp):
        if comp not in _rendas:
            _rendas[comp] = renda_da_competencia(e, renda_info, comp)
        return _rendas[comp]

    def dif_comp(comp):
        v = renda(comp)[0]
        return None if v is None else v[1] - v[0]

    def janela_legal(comp):
        """(início, fim, dispositivo) da janela de pagamento da competência, pelo regime vigente NELA (REGIMES_JANELA;
        revisão r11, MAJOR 2: a do 1º ao 5º dia útil era aplicada a 2003). Competência sem regime capturado: (None,
        None, motivo). No regime das faixas, com as duas rendas conhecidas e acima do salário mínimo, a do §2º (1º ao
        5º dia útil do mês seguinte); até o mínimo, ou com a faixa indeterminável (renda não fechada, mínimo fora da
        tabela, uma renda de cada lado), a do §3º, que contém a do §2º (revisão r8, MAJOR 2)."""
        reg = regime_janela(comp)
        if reg is None:
            return None, None, ("janela de pagamento de competência anterior a 1993 não capturada (Lei 8.213, art. 41, "
                                "§4º: as redações originais e da Lei 8.444/1992 sem data de início em context/lei/): o "
                                "vencimento da competência não se confere")
        if reg["tipo"] == "1a10":
            return (*cal.janela_ate_o_decimo(comp), reg["fonte"])
        if reg["tipo"] == "1a5":
            return (*cal.janela_acima_do_minimo(comp), reg["fonte"])
        v = renda(comp)[0]
        sm = _consulta_tabela(ARQ_SALARIO_MINIMO, dt.date(comp[0], comp[1], 1), "valor")[0]
        if v is not None and sm is not None and min(v) > sm:
            return (*cal.janela_acima_do_minimo(comp), f"Lei 8.213, art. 41-A, §2º: renda acima do salário mínimo "
                                                       f"({sm}) nas duas RMIs; §4º; {reg['fonte']}")
        return (*cal.janela(comp), f"Lei 8.213, art. 41-A, §3º, que contém o §2º: faixa até o mínimo ou "
                                   f"indeterminável; §4º; {reg['fonte']}")

    # O vencimento informado só escolhe o dia DENTRO da janela legal da competência; fora dela contraria a lei e
    # deslocaria a prescrição (revisão r7, MAJOR 2: jan./2026 vencendo em 01/07/2026 virava vincenda, exit 0).
    for comp, venc in sorted(e["datas_vencimento"].items()):
        ini_l, fim_l, disp = janela_legal(comp)
        if ini_l is None:            # sem regime capturado não há regra para recusar: a competência fica em aberto
            continue
        if not ini_l <= venc <= fim_l:
            raise EntradaInvalida(
                f"datas_vencimento: {comp[0]:04d}-{comp[1]:02d} com vencimento em {br(venc)}, fora da janela de pagamento "
                f"de {br(ini_l)} a {br(fim_l)} ({disp}): o vencimento devido dessa competência "
                "não pode cair fora dela")
        # Dentro da janela, só dia útil com expediente bancário normal (art. 41-A, §§2º e 4º; revisão r9, MAJOR):
        # sábado, domingo e qualquer feriado da tabela do motor, inclusive carnaval, Paixão e Corpus Christi.
        if not cal.util(venc, True):
            raise EntradaInvalida(
                f"datas_vencimento: {comp[0]:04d}-{comp[1]:02d} com vencimento em {br(venc)}, que não é dia útil com "
                "expediente bancário normal (sábado, domingo ou feriado do calendário do motor de prazos; Lei 8.213, "
                "art. 41-A, §§2º e 4º): informe o dia útil em que a competência deveria ter sido paga")
    regras.append("Lei 8.213, art. 103, parágrafo único; art. 41-A, §§2º a 4º")
    memoria.append("vencimento de cada competência = janela de pagamento do art. 41-A, §§2º e 3º (do 5º dia útil "
                   "bancário antes do fim do mês da competência ao 5º do mês seguinte, que contém a do §2º), salvo "
                   "vencimento devido informado em datas_vencimento, conferido contra a janela da faixa da renda "
                   "da competência (§2º acima do mínimo, quando as duas RMIs o superam); prescrita se o "
                   f"{rotulo_ref} for posterior ao último dia da janela + 5 anos; devida se a janela inteira acaba "
                   "antes do marco e o primeiro dia + 5 anos o alcança; no meio, em aberto")
    if e["datas_vencimento"]:
        fonte["datas_vencimento"] = ("informados na entrada: vencimento devido de cada competência (Lei 8.213, art. 103, parágrafo "
                                     "único; IN 128, art. 595, §§1º e 2º), não a data do pagamento realizado")

    def janela(comp):
        if janela_legal(comp)[0] is None:
            return None, None, False
        if comp in e["datas_vencimento"]:
            d = e["datas_vencimento"][comp]
            return d, d, True
        # Sem vencimento informado, a janela da faixa da renda quando identificável (§2º acima do mínimo), não a
        # ampla do §3º (revisão r9, MINOR 2).
        return (*janela_legal(comp)[:2], False)

    def status(ini_j, fim_j):
        """'prescrita', 'devida', 'nao_vencida' ou None (a janela cruza o corte da prescrição ou o marco, ou a
        competência não tem regime de janela capturado)."""
        if ini_j is None:
            return None
        if ref > soma_anos(fim_j, 5):
            return "prescrita"
        if ref <= soma_anos(ini_j, 5) and fim_j < ref:
            return "devida"
        if ini_j >= ref:
            return "nao_vencida"
        return None

    def motivo_janela(ini_j, fim_j, comp):
        if ini_j is None:
            return janela_legal(comp)[2]
        corte = "o corte da prescrição (marco − 5 anos)" if ref > soma_anos(ini_j, 5) else f"o {rotulo_ref}"
        return (f"janela de pagamento {br(ini_j)} a {br(fim_j)} ({janela_legal(comp)[2]}; com e sem carnaval, "
                f"Paixão e Corpus Christi como dia útil bancário) cruza {corte}; informe o vencimento devido (data em "
                "que deveria ter sido paga) em datas_vencimento")

    devidas, em_aberto, prescritas = [], [], 0
    dib = e["dib"]
    for comp in competencias((dib.year, dib.month), (ref.year, ref.month)):
        ini_j, fim_j, informada = janela(comp)
        s1 = status(ini_j, fim_j)
        rot = f"{comp[0]:04d}-{comp[1]:02d}"
        if s1 is None:
            em_aberto.append({"competencia": rot, "motivo": motivo_janela(ini_j, fim_j, comp)})
            continue
        if s1 == "prescrita":
            prescritas += 1
            continue
        if s1 == "nao_vencida":
            continue
        if comp == (dib.year, dib.month) and dib.day != 1:
            em_aberto.append({"competencia": rot, "motivo": f"competência da DIB ({br(dib)}) é fração de mês: "
                              "proporcionalizar à mão"})
            continue
        devidas.append(rot)


    def comp_de(rot):
        return int(rot[:4]), int(rot[5:7])

    sem_reajuste = [c for c in devidas if dif_comp(comp_de(c)) is None]
    motivos_sem = {}
    for c in sem_reajuste:
        motivos_sem.setdefault(renda(comp_de(c))[1], []).append(c)
    total_mensal = Decimal("0")
    memoria.append(f"{prescritas} competência(s) prescrita(s); {len(devidas)} devida(s)"
                   + (f" ({devidas[0]} a {devidas[-1]})" if devidas else ""))
    # Uma linha por trecho de competências seguidas com as mesmas rendas (o piso ou o teto da competência pode mudar
    # a renda no meio do ano).
    trechos = []
    for c in devidas:
        v = renda(comp_de(c))[0]
        if trechos and trechos[-1][2] == v and comp_de(c) == mes_seguinte(*comp_de(trechos[-1][1])):
            trechos[-1][1] = c
            trechos[-1][3] += 1
        else:
            trechos.append([c, c, v, 1])
    for de, ate, v, n in trechos:
        faixa = de if de == ate else f"{de} a {ate}"
        if v is None:
            memoria.append(f"{faixa}: {n} competência(s) sem a renda da competência fechada (fora do total)")
            continue
        d = v[1] - v[0]
        total_mensal += d * n
        memoria.append(f"{faixa}: {n} competência(s) × ({v[1]} − {v[0]}) = {d * n} (renda devida e paga com o piso e o "
                       "teto vigentes na competência)")

    # Abono anual (Lei 8.213, art. 40). Todo abono cujo pagamento não se sabe se caiu antes do marco e depois do
    # corte da prescrição fica em abonos_em_aberto e leva a conta a exit 3: altera o total (DESIGN-SPEC §3).
    abonos, abonos_aberto = [], []
    if e["abono"]:
        regras.append("Lei 8.213, art. 40 e parágrafo único (base: dezembro); IN 128, art. 619, §§1º e 2º")
        for ano in range(dib.year, ref.year + 1):
            meses = 12
            if ano == dib.year:
                # IN 128, art. 619, §§1º e 2º: proporcional aos meses; 15 dias ou mais no mês contam o mês inteiro.
                dias_dib = calendar.monthrange(dib.year, dib.month)[1] - dib.day + 1
                meses = 12 - dib.month + (1 if dias_dib >= 15 else 0)
                if dib.day != 1:
                    memoria.append(f"abono {ano}: mês da DIB com {dias_dib} dia(s) de benefício → "
                                   f"{'conta' if dias_dib >= 15 else 'não conta'} (IN 128, art. 619, §1º); {meses}/12")
            # Base: a renda de dezembro do ano (Lei 8.213, art. 40, parágrafo único), com o piso e o teto de dezembro.
            d_ano = dif_comp((ano, 12))
            motivo_dez = renda((ano, 12))[1]
            valor = q(d_ano * meses / 12) if d_ano is not None else None
            ato = ATOS_ABONO.get(ano)
            motivo = ("sem ato de pagamento do abono do ano capturado em context/lei/ (o Decreto 3.048, art. 120, §1º, "
                      "fixa as competências de agosto e novembro, mas decretos anuais o antecipam — Lei 8.213, art. 40, "
                      "\"Vide\")")
            if ato:
                # O calendário do ato só vale nas competências em que o benefício existia (Decreto 10.695/2021,
                # art. 1º, I e II: parcelas pagas com os benefícios das competências de maio e junho).
                antes = [p["competencia"] for p in ato["parcelas"] if p["competencia"] < (dib.year, dib.month)]
                if antes:
                    motivo = (f"benefício com DIB em {br(dib)}: não existia na(s) competência(s) "
                              + ", ".join(f"{c[0]:04d}-{c[1]:02d}" for c in antes)
                              + f" do calendário do {ato['fonte'].split(' (')[0]}; o pagamento do abono de {ano} desse "
                              "benefício não está em ato capturado em context/lei/")
                else:
                    parcelas, resto = [], valor
                    for p in ato["parcelas"]:
                        ini_j, fim_j, _ = janela(p["competencia"])
                        st = status(ini_j, fim_j)
                        if valor is None:
                            parcelas.append((Decimal("0") if st in ("prescrita", "nao_vencida") else None, st))
                            continue
                        pv = q(d_ano * p["fracao"]) if p["fracao"] is not None else resto
                        resto -= pv if p["fracao"] is not None else 0
                        parcelas.append((pv, st))
                    if any(pv is None for pv, _ in parcelas):
                        abonos_aberto.append({"ano": ano, "valor": None, "motivo": motivo_dez})
                        continue
                    if any(pv < 0 for pv, _ in parcelas):
                        abonos_aberto.append({"ano": ano, "valor": str(valor), "motivo": (
                            "parcela do calendário do ato ficaria negativa: o abono do ano não cabe nas parcelas do ato")})
                        continue
                    if any(st is None for _, st in parcelas):
                        abonos_aberto.append({"ano": ano, "valor": str(valor), "motivo": (
                            "janela de pagamento de uma parcela do ato cruza o corte da prescrição ou o marco; "
                            "informe o vencimento devido em datas_vencimento")})
                        continue
                    devido = sum((pv for pv, st in parcelas if st == "devida"), Decimal("0"))
                    if any(st == "nao_vencida" for _, st in parcelas):
                        memoria.append(f"abono {ano}: parcela do ato paga depois do marco (vincenda, fora do total)")
                    if devido:
                        abonos.append({"ano": ano, "valor": str(devido), "fonte": ato["fonte"]})
                    memoria.append(f"abono {ano}: datas do {ato['fonte'].split(' (')[0]}; devido {devido}")
                    continue
            # Sem calendário aplicável: limites. Mais cedo, 01/01 do ano (nunca antes da DIB); mais tarde, o fim da
            # janela de pagamento da competência de dezembro (art. 41-A, §§2º e 3º).
            cedo = max(dt.date(ano, 1, 1), dib)
            tarde = janela((ano, 12))[1]
            if tarde is None:
                abonos_aberto.append({"ano": ano, "valor": None if valor is None else str(valor),
                                      "motivo": janela_legal((ano, 12))[2]})
            elif ref > soma_anos(tarde, 5):
                memoria.append(f"abono {ano}: pago no mais tardar com a competência de dezembro ({br(tarde)}) → prescrito")
            elif cedo >= ref:
                memoria.append(f"abono {ano}: nenhum pagamento possível antes do marco (vincendo, fora do total)")
            elif valor is None:
                abonos_aberto.append({"ano": ano, "valor": None, "motivo": motivo_dez})
            elif ref <= soma_anos(cedo, 5) and tarde < ref:
                abonos.append({"ano": ano, "valor": str(valor),
                               "fonte": "Lei 8.213, art. 40; pago entre 01/01 do ano e o fim da janela de pagamento "
                                        "da competência de dezembro (art. 41-A, §§2º e 3º): não prescrito e vencido "
                                        "no marco"})
                memoria.append(f"abono {ano}: {meses}/12 × {d_ano} = {valor}, não prescrito")
            else:
                abonos_aberto.append({"ano": ano, "valor": str(valor), "motivo": (
                    f"{motivo}; pagável de {br(cedo)} a {br(tarde)}, intervalo que não fica inteiro antes do "
                    f"{rotulo_ref} ({br(ref)}) e depois do corte da prescrição (marco − 5 anos): informe a data do "
                    "pagamento do abono do ano")})
        if abonos_aberto:
            alertas.append("[VERIFICAR] abono anual de ano(s) sem data de pagamento decidida "
                           f"({', '.join(str(x['ano']) for x in abonos_aberto)}): fora do total e conta em exit 3; "
                           "o calendário de 2021 (Decreto 10.695/2021) não se generaliza a outros anos nem a benefício "
                           "iniciado depois das competências dele.")
    total_abono = sum((Decimal(x["valor"]) for x in abonos), Decimal("0"))
    total = total_mensal + total_abono
    memoria.append(f"diferença nominal = {total_mensal} + abonos {total_abono} = {total}")
    fonte.update({"prazo_decadencial_final": (("concessão indeterminável (duas leituras): " if any(
                      s.get("indeterminavel") for s in dec_fora) else "fora da cobertura temporal: ") + "; ".join(
                      s.get("fonte_de") or s.get("fonte_ate") for s in dec_fora)) if dec_fora and not dec_calendario
                  else "Lei 8.213, art. 103, caput; CC, art. 132, §§1º e 3º; Lei 662/1949, art. 1º"
                  + ("; termo em aberto pelo calendário" if dec_calendario else "")
                  + ("; STF Tema 313, tese II" if pp < EDICAO_MP_1523_9 else ""),
                  "parcelas_nao_prescritas": "Lei 8.213, art. 103, parágrafo único; art. 41-A, §§2º a 4º",
                  "diferenca_nominal": "soma nominal; correção pelo regime de context/calculo-rpv.md"})
    por_comp = {f"{c[0]:04d}-{c[1]:02d}": (str(dif_comp(c)) if dif_comp(c) is not None else None)
                for c in competencias((dib.year, dib.month), (ref.year, ref.month))}
    por_ano = {}
    for a in range(dib.year, ref.year + 1):
        difs = {v for k, v in por_comp.items() if int(k[:4]) == a}
        por_ano[str(a)] = (None if None in difs or not difs else difs.pop() if len(difs) == 1
                           else "variável no ano (piso ou teto da competência): ver diferencas_por_competencia")
    resultado = {
        "diferenca_mensal": str(dif),
        "diferencas_por_ano": por_ano,
        "diferencas_por_competencia": por_comp,
        "competencias_sem_reajuste": sem_reajuste,
        "prazo_decadencial_final": fim_dec.isoformat() if fim_dec else None,
        "decadente": decadente,
        "parcelas_nao_prescritas": {"quantidade": len(devidas),
                                    "de": devidas[0] if devidas else None,
                                    "ate": devidas[-1] if devidas else None,
                                    "competencias": devidas},
        "parcelas_prescritas": prescritas,
        "abonos_nao_prescritos": abonos,
        "abonos_em_aberto": abonos_aberto,
        "competencias_em_aberto": em_aberto,
        "diferenca_nominal": str(total),
    }
    if em_aberto or abonos_aberto or premissas or sem_reajuste or dec_fora:
        resultado["dados_faltantes"] = dec_faltantes + (
            [f"competência {x['competencia']}: {x['motivo']}" for x in em_aberto]
            + [f"competências {cs[0]} a {cs[-1]}: {m}" if len(cs) > 1 else f"competência {cs[0]}: {m}"
               for m, cs in motivos_sem.items()]
            + [f"abono {x['ano']}: {x['motivo']}" for x in abonos_aberto] + premissas)
        partes = [f"{total} (fechado: parcelas e abonos acima"
                  + (", com o pedido administrativo como marco da prescrição" if premissas else "") + ")"]
        if em_aberto:
            partes.append(f"Σ das competências em aberto ({', '.join(x['competencia'] for x in em_aberto)}): até a "
                          "diferença do ano de cada uma, conforme a data de pagamento ou a fração do mês")
        if sem_reajuste:
            partes.append(f"Σ das competências {sem_reajuste[0]} a {sem_reajuste[-1]} × [(RMI devida − RMI paga), "
                          "cada uma reajustada na data de cada reajuste, a do salário mínimo, pelo fator dele, pro rata "
                          "no primeiro (Lei 8.213, art. 41-A, caput; até 2003, art. 41), com o piso de um salário mínimo e o teto vigentes em cada competência (Lei 8.213, art. 33)]"
                          + (f"; na incapacidade permanente com o acréscimo de 25% ({FUND_45}), reajusta-se a base, "
                             "limitada ao teto, e o acréscimo é recalculado sobre ela, podendo o total superar o teto"
                             if e["especie"] == "incapacidade-permanente" else ""))
        if abonos_aberto:
            partes.append("abonos em aberto, se vencidos e não prescritos no marco ("
                          + ", ".join(f"{x['ano']}: {x['valor'] or 'diferença reajustada de dezembro × meses/12'}"
                                      for x in abonos_aberto) + ")")
        resultado["formula_aberta"] = ("[VERIFICAR] diferença nominal = " + " + ".join(partes)
                                       + "".join(f"; {s['linha']}" for s in dec_fora)
                                       + ". Conta aberta em context/calculo-rmi.md.")
        return EXIT_FALTA, resultado
    return EXIT_OK, resultado


# ------------------------------------------------------------------ principal

def _parametros(e):
    return {k: ([str(x) for x in v] if isinstance(v, list) else
                {f"{c[0]:04d}-{c[1]:02d}": d.isoformat() for c, d in v.items()} if isinstance(v, dict) else
                str(v) if isinstance(v, (Decimal, dt.date)) else v) for k, v in e.items()}


def tabela_ausente(e, err, regras, memoria, fonte):
    """Saída de exit 3 quando uma tabela de scripts/data/ falta (o contrato: falta de tabela devolve a fórmula,
    com todas as chaves da saída — revisão r9, MINOR 3)."""
    arquivo = Path(getattr(err, "filename", None) or str(err)).name
    if e["modo"] == "concessao":
        formula = ("[VERIFICAR] RMI = média dos salários de contribuição desde 07/1994 (divisor mínimo de 108 quando "
                   "cabe — Lei 8.213, art. 135-A), limitada ao teto da DIB, × coeficiente da regra (EC 103, art. 26), "
                   "com o piso do salário de benefício e da renda na DIB (Lei 8.213, art. 29, §2º; CF, art. 201, §2º)")
    else:
        formula = ("[VERIFICAR] diferença nominal = Σ das competências não prescritas (Lei 8.213, art. 103, parágrafo "
                   "único) × (RMI devida − RMI paga da competência, ambas reajustadas na data de cada reajuste do salário mínimo — art. 41-A — com piso de "
                   "um salário mínimo e o teto, salvo o acréscimo de 25% do art. 45) + abonos não prescritos")
    memoria.append(f"cálculo interrompido: tabela {arquivo} ausente ou ilegível em scripts/data/")
    return {"versao": VERSAO, "script": NOME, "modo": e["modo"], "parametros_usados": _parametros(e),
            "regra": regras, "fundamento": list(regras), "fonte": fonte, "memoria": memoria,
            "dados_faltantes": [f"tabela {arquivo} ausente ou ilegível em scripts/data/ ({type(err).__name__}): "
                                "reinstale o plugin; sem ela o piso, o teto e os reajustes não se conferem"],
            "formula_aberta": formula + ". Conta aberta em context/calculo-rmi.md.",
            "alertas": [AVISO_FIXO]}


def calcular(bruto):
    try:
        e = normaliza(bruto)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}
    regras, memoria, alertas, fonte = [], [], [], {}
    try:
        if e["modo"] == "concessao":
            codigo, resultado = conta_concessao(e, regras, memoria, alertas, fonte)
        else:
            codigo, resultado = conta_revisao(e, regras, memoria, alertas, fonte)
    except EntradaInvalida as err:     # contradição só visível com a tabela (limites da DIB)
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}
    except OSError as err:             # tabela de scripts/data/ ausente ou ilegível: falta tabela, exit 3 (r8, MINOR 5)
        return EXIT_FALTA, tabela_ausente(e, err, regras, memoria, fonte)
    parametros = _parametros(e)
    alertas.append(AVISO_FIXO)
    saida = {
        "versao": VERSAO,
        "script": NOME,
        "modo": e["modo"],
        "parametros_usados": parametros,
        **resultado,
        "regra": regras,
        "fonte": fonte,
        "alertas": alertas,
        "memoria": memoria,
    }
    saida.setdefault("fundamento", list(regras))
    saida.setdefault("dados_faltantes", [])
    saida.setdefault("formula_aberta", None)
    return codigo, saida


def build_parser():
    ap = argparse.ArgumentParser(
        prog=NOME,
        description="RMI de concessão (média, divisor mínimo, coeficiente, descarte) e de revisão "
                    "(decadência, prescrição, diferenças nominais). Entrada JSON por --entrada ou stdin "
                    "(campos em context/calculo-rmi.md, seção 6).")
    ap.add_argument("--entrada", help="arquivo JSON de entrada (sem ele, lê o stdin)")
    ap.add_argument("--versao", action="store_true", help="mostra a versão do script e sai")
    return ap


def _rejeita_constante(nome):
    raise ValueError(f"{nome} não é número JSON válido")


def _executa(args):
    try:
        dados = Path(args.entrada).read_bytes() if args.entrada else sys.stdin.buffer.read()
        bruto = json.loads(dados.decode("utf-8"), parse_constant=_rejeita_constante)
    except (OSError, ValueError, RecursionError) as err:   # ValueError: JSON, UTF-8, inteiro gigante, NaN
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": f"JSON ilegível: {err}", "versao": VERSAO}
    return calcular(bruto)


def _emite(codigo, saida):
    # ensure_ascii=True: a entrada pode trazer surrogate solto, que o stdout em UTF-8 não codifica.
    sys.stdout.write(json.dumps(saida, ensure_ascii=True, indent=2) + "\n")
    if codigo == EXIT_ENTRADA:
        linha = f"entrada inválida: {saida['detalhe']}\n".encode("utf-8", "backslashreplace")
        sys.stderr.flush()
        sys.stderr.buffer.write(linha)
        sys.stderr.buffer.flush()


def main(argv=None):
    # Nenhuma exceção sai em exit 1 sem JSON: argumentos, leitura, validação, conta e emissão ficam sob a mesma guarda;
    # o que escapar vira exit 2 com o tipo do erro (só --help e --versao saem em 0, como manda o argparse).
    try:
        try:
            args = build_parser().parse_args(argv)
        except SystemExit as fim:
            if fim.code in (0, None):
                raise
            raise ValueError("argumentos de linha de comando inválidos (use --entrada ou --versao)")
        if args.versao:
            print(f"{NOME} {VERSAO}")
            return EXIT_OK
        codigo, saida = _executa(args)
        _emite(codigo, saida)
        return codigo
    except SystemExit:
        raise
    except Exception as err:
        saida = {"erro": "entrada_invalida", "versao": VERSAO,
                 "detalhe": f"entrada não processável ({type(err).__name__}); confira os CAMPOS em "
                            "context/calculo-rmi.md"}
        try:
            _emite(EXIT_ENTRADA, saida)
        except Exception:
            pass
        return EXIT_ENTRADA


if __name__ == "__main__":
    sys.exit(main())
