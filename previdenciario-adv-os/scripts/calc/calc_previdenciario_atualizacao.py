#!/usr/bin/env python3
"""calc_atualizacao.py — Engine A: atualização de débito judicial por regime.

Regimes: civil-cc406 · selic-integral-privado · fazenda-ec113 ·
fazenda-requisitorio-ec136 · trabalhista-adc58. Fontes e convenções em
scripts/calc/README.md.

USO:
    python3 calc_atualizacao.py --entrada caso.json
    echo '{...}' | python3 calc_atualizacao.py

Saída: JSON no stdout. Exit 0 = calculado; 2 = entrada inválida;
3 = falta índice no cache (devolve a fórmula aberta, nunca estima).

Só biblioteca padrão, Python 3.9+, sem rede. O cache de índices é lido de
../data/indices/ relativo a este arquivo (CLAUDE_PLUGIN_ROOT chega vazio no
Cowork). --indices-dir troca a pasta; existe para os testes.
"""

import argparse
import calendar
import datetime as dt
import json
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, getcontext
from pathlib import Path

getcontext().prec = 50

VERSAO = "0.3.0"
EXIT_OK, EXIT_ENTRADA, EXIT_FORA_DO_CACHE = 0, 2, 3

DIR_INDICES_PADRAO = Path(__file__).resolve().parent.parent / "data" / "indices"
ARQUIVOS = {
    "IPCA": "ipca-mensal.json",
    "IPCA-E": "ipca-e-mensal.json",
    "IPCA-15": "ipca15-mensal.json",
    "INPC": "inpc-mensal.json",
    "IGP-DI": "igpdi-mensal.json",
    "SELIC": "selic-mensal.json",
    "TAXA_LEGAL": "taxa-legal-cc406.json",
    "TAXA_LEGAL_INPC": "taxa-legal-inpc-previdenciaria.json",
    "TR": "tr-mensal.json",
}

REGIMES = (
    "civil-cc406",
    "selic-integral-privado",
    "fazenda-ec113",
    "fazenda-requisitorio-ec136",
    "trabalhista-adc58",
)
CAMPOS = {
    "valor", "data_inicial", "data_final", "regime", "data_citacao",
    "data_expedicao", "data_ajuizamento", "ente", "natureza_tributaria",
    "acumulacao_selic", "valor_consolidado_12_2021", "juros_consolidados_12_2021",
    "valor_juros", "valor_juros_selic", "periodo_graca", "natureza", "taxa_titulo",
}

MANUAL = "Manual CJF (ed. jul./2026)"     # Res. CJF 990/2026
MARCO_LEI_14905 = dt.date(2024, 8, 30)   # vigência da Lei 14.905/2024
MES_CONSOLIDACAO_EC113 = (2021, 12)      # Manual CJF (ed. jul./2026), item 4.2.1.1, Nota 5 a
INICIO_EC136 = {"federal": (2025, 9), "estadual": (2025, 8), "municipal": (2025, 8)}
# Fase pré-requisitório contra a Fazenda: a Selic da EC 113 vai até a competência 08/2025
# (computada em 09/2025); da competência 09/2025 em diante, correção + taxa legal (ARE
# 1.557.312/SP, Tema 1.419 do STF; Manual CJF ed. jul./2026, itens 4.2.1.1, 4.2.2, 4.3.1.1, 4.3.2).
INICIO_TEMA_1419 = (2025, 9)
# IPCA-E mensal = IPCA-15/IBGE a partir de 01/2001 (Manual CJF ed. jul./2026, item 4.2.1.1); antes, fórmula.
INICIO_IPCA_E = (2001, 1)
MOTIVO_IPCA_E = ("mês sem IPCA-E mensal no cache: a série é o IPCA-15/IBGE (SGS 7478) de 01/2001 em "
                 "diante (Manual CJF ed. jul./2026, item 4.2.1.1); antes de 01/2001 ou depois do range_final, "
                 "critérios do título ou fonte oficial")
# Previdenciária (Manual CJF ed. jul./2026, item 4.3.1.1): INPC de 09/2006 a 11/2021, IGP-DI de
# 05/1996 a 08/2006; antes, a tabela histórica abaixo (indexadores fora do cache, exceto o INPC
# quando o mês estiver nele).
INICIO_INPC_PREV = (2006, 9)
INICIO_IGPDI_PREV = (1996, 5)
TABELA_PREV_HISTORICA = (
    ((1964, 1), (1986, 2), "ORTN", "Lei 4.357/1964"),
    ((1986, 3), (1988, 12), "OTN", "Lei 6.899/1981; Decreto 86.649/1981 (débitos anteriores a 01/1989 x 6,17)"),
    ((1989, 1), (1989, 1), "IPC/IBGE 42,72%", "expurgo, em substituição ao BTN"),
    ((1989, 2), (1989, 2), "IPC/IBGE 10,14%", "expurgo, em substituição ao BTN"),
    ((1989, 3), (1990, 2), "BTN", "Lei 7.730/1989"),
    ((1990, 3), (1991, 2), "IPC/IBGE", "expurgo, em substituição ao BTN e ao INPC de 02/1991"),
    ((1991, 3), (1992, 12), "INPC", "Lei 8.213/1991 art. 41 §6º"),
    ((1993, 1), (1994, 2), "IRSM", "Lei 8.542/1992 art. 9º §2º"),
    ((1994, 3), (1994, 6), "URV (46,0150%, 42,1964%, 44,1627%, 44,0846%)",
     "MP 434/1994; Lei 8.880/1994 art. 20 §5º"),
    ((1994, 7), (1995, 6), "IPC-R", "Lei 8.880/1994 art. 20 §6º"),
    ((1995, 7), (1996, 4), "INPC", "MP 1.053/1995 art. 8º §3º; Lei 10.192/2001"),
)
# Juros da previdenciária antes da poupança (Manual CJF ed. jul./2026, item 4.3.2).
FIM_JUROS_1PCT_PREV = (2009, 6)     # 1% a.m. simples (DL 2.322/1987)
FIM_JUROS_05 = (2012, 4)            # 0,5% a.m. simples (Lei 9.494/97 art. 1º-F, red. Lei 11.960/2009)

# STJ Tema 905 (REsp 1.495.146): critérios até 12/2021, por natureza da condenação.
TEMA_905 = {
    "previdenciaria": (
        "INPC + JUROS DA POUPANCA",
        "INPC desde 09/2006 (Lei 8.213/91 art. 41-A, incluído pela Lei 11.430/2006), IGP-DI de 05/1996 a "
        "08/2006 e, antes, a tabela histórica (Manual CJF ed. jul./2026, item 4.3.1.1); juros de 1% a.m. "
        "até 06/2009 (DL 2.322/1987), 0,5% a.m. de 07/2009 a 04/2012 e da poupança de 05/2012 em diante "
        "(Lei 9.494/97 art. 1º-F, redação da Lei 11.960/2009; item 4.3.2)",
        "principal_12_2021 = valor x produto(1 + indice_m/100); juros_ate_12_2021 = "
        "principal_12_2021 x soma(juros_m) desde a citação",
    ),
    "assistencial": (
        "IPCA-E + JUROS DA POUPANCA",
        "IPCA-E + juros da poupança (Lei 9.494/97 art. 1º-F, redação da Lei 11.960/2009)",
        "principal_12_2021 = valor x produto(1 + IPCA-E_m/100); juros_ate_12_2021 = "
        "principal_12_2021 x juros da poupança desde a citação",
    ),
    "administrativa": (
        "IPCA-E + JUROS DA POUPANCA",
        "IPCA-E + juros da poupança (Lei 9.494/97 art. 1º-F, redação da Lei 11.960/2009)",
        "principal_12_2021 = valor x produto(1 + IPCA-E_m/100); juros_ate_12_2021 = "
        "principal_12_2021 x juros da poupança desde a citação",
    ),
    "tributaria": (
        "SELIC (TEMA 905, TRIBUTARIA)",
        "Selic, a mesma dos créditos tributários da Fazenda, vedada a cumulação com juros e "
        "correção (no âmbito federal, Lei 9.250/95 art. 39 §4º)",
        "valor_12_2021 = valor x (1 + soma Selic_m/100), desde o recolhimento indevido "
        "(critérios do título)",
    ),
}
NATUREZAS = tuple(TEMA_905)

# A partir de 09/2025 (pré-requisitório): correção e taxa legal por natureza.
POS_TEMA_1419 = {
    "previdenciaria": (
        "INPC", "TAXA_LEGAL_INPC",
        "ARE 1.557.312/SP (Tema 1.419 do STF); Lei 8.213/91 art. 41-A (Lei 11.430/2006); Manual CJF "
        "(ed. jul./2026), item 4.3.1.1 (INPC a partir de 09/2025)",
        "ARE 1.557.312/SP (Tema 1.419 do STF); CC art. 406 (Lei 14.905/2024); Manual CJF (ed. jul./2026), "
        "item 4.3.2 e Nota 3 (taxa legal com dedução do INPC, metodologia similar à da Res. CMN 5.171/2024; "
        "a de cada competência computada no mês seguinte)",
    ),
    "assistencial": (
        "IPCA-15", "TAXA_LEGAL",
        "ARE 1.557.312/SP (Tema 1.419 do STF); CC art. 389, parágrafo único (Lei 14.905/2024); Manual CJF "
        "(ed. jul./2026), item 4.3.1.1, Nota 3, que remete ao item 4.2.1.1 (IPCA-15 a partir de 09/2025)",
        "ARE 1.557.312/SP (Tema 1.419 do STF); CC art. 406 (Lei 14.905/2024); Res. CMN 5.171/2024 (SGS "
        "29543); Manual CJF (ed. jul./2026), item 4.2.2 e Nota 7 (taxa legal com dedução do IPCA-15, a de "
        "cada competência computada no mês seguinte)",
    ),
}
POS_TEMA_1419["administrativa"] = (
    "IPCA-15", "TAXA_LEGAL",
    "ARE 1.557.312/SP (Tema 1.419 do STF); CC art. 389, parágrafo único (Lei 14.905/2024); Manual CJF "
    "(ed. jul./2026), item 4.2.1.1 (IPCA-15 a partir de 09/2025)",
    POS_TEMA_1419["assistencial"][3],
)


def formula_ate_data_final(formula):
    """Fórmula do Tema 905 com nomes de período neutros, para período que termina antes de 12/2021.

    Usa os mesmos nomes dos componentes desse caso (principal_corrigido, juros_ate_data_final).
    """
    return (formula.replace("principal_12_2021", "principal_corrigido")
            .replace("juros_ate_12_2021", "juros_ate_data_final")
            .replace("valor_12_2021", "valor_data_final"))

CEM = Decimal(100)
UM = Decimal(1)
ZERO = Decimal(0)

# Fronteira de entrada (README, "Fronteira de entrada"): datas e competências de 1900 a 2100;
# números com módulo até 1e15 e no máximo 6 casas decimais. Fora disso, exit 2 antes de qualquer conta.
DATA_MINIMA, DATA_MAXIMA = dt.date(1900, 1, 1), dt.date(2100, 12, 31)
VALOR_MAXIMO, PASSO_MINIMO = Decimal("1e15"), Decimal("0.000001")

ALERTA_ADI_7873 = (
    "[VERIFICAR] ADI 7873 pendente (rel. Fux): o regime da EC 136/2025 pode ser "
    "alterado pelo STF; conferir o andamento antes de protocolar."
)


class EntradaInvalida(Exception):
    pass


# ---------------------------------------------------------------- datas/meses

def _data(campo, texto):
    if not isinstance(texto, str):
        raise EntradaInvalida(f"{campo}: esperado texto AAAA-MM-DD")
    try:
        d = dt.date.fromisoformat(texto)
    except ValueError:
        raise EntradaInvalida(f"{campo}: data inválida '{texto}' (formato AAAA-MM-DD)")
    if not DATA_MINIMA <= d <= DATA_MAXIMA:
        raise EntradaInvalida(f"{campo}: fora do intervalo suportado ({DATA_MINIMA} a {DATA_MAXIMA})")
    return d


def mes(d):
    return (d.year, d.month)


def mes_txt(m):
    return f"{m[0]:04d}-{m[1]:02d}"


def mes_soma(m, n):
    total = m[0] * 12 + (m[1] - 1) + n
    return (total // 12, total % 12 + 1)


def meses(ini, fim_excl):
    """Meses de ini (inclusive) a fim_excl (exclusive)."""
    out, m = [], ini
    while m < fim_excl:
        out.append(m)
        m = mes_soma(m, 1)
    return out


def dias_por_mes(ini, fim_excl):
    """Dias corridos do intervalo [ini, fim_excl) agrupados por mês civil."""
    out = []
    d = ini
    while d < fim_excl:
        ultimo = calendar.monthrange(d.year, d.month)[1]
        prox = dt.date(d.year, d.month, ultimo) + dt.timedelta(days=1)
        corte = min(prox, fim_excl)
        out.append((mes(d), (corte - d).days, ultimo))
        d = corte
    return out


# ---------------------------------------------------------------- números

def _dec(campo, texto, negativo=False):
    if isinstance(texto, bool) or not isinstance(texto, (str, int)):
        raise EntradaInvalida(f"{campo}: esperado número em texto, ex. \"1000.00\"")
    try:
        v = Decimal(str(texto).strip())
    except InvalidOperation:
        raise EntradaInvalida(f"{campo}: número inválido '{texto}' (use ponto decimal)")
    if not v.is_finite() or (v < 0 and not negativo):
        raise EntradaInvalida(f"{campo}: valor deve ser finito e não negativo")
    if abs(v) > VALOR_MAXIMO or v.quantize(PASSO_MINIMO) != v:
        raise EntradaInvalida(f"{campo}: fora da capacidade suportada (módulo até 1e15, no máximo 6 casas decimais)")
    return v


def q2(v):
    return str(v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def q6(v):
    return str(v.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))


def q10(v):
    return str(v.quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------- cache

class Cache:
    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self._dados = {}
        self.usados = []

    def serie(self, nome):
        if nome not in self._dados:
            caminho = self.pasta / ARQUIVOS[nome]
            with open(caminho, encoding="utf-8") as f:
                bruto = json.load(f, parse_float=Decimal)
            self._dados[nome] = bruto
        bruto = self._dados[nome]
        if nome not in [u["indice"] for u in self.usados]:
            # Metadados canônicos (data_captura, intervalo); os legados ficam como fallback.
            intervalo = bruto.get("intervalo") or {}
            ini = intervalo.get("inicial", bruto.get("range_inicial"))
            fim = intervalo.get("final", bruto.get("range_final"))
            self.usados.append({
                "indice": nome,
                "arquivo": f"scripts/data/indices/{ARQUIVOS[nome]}",
                "fonte": bruto.get("fonte"),
                "data_extracao": bruto.get("data_captura", bruto.get("data_extracao")),
                "range": f"{ini}..{fim}",
            })
        return bruto["valores"]

    def taxa(self, nome, m):
        """Taxa do mês como Decimal, ou None se o mês não estiver no cache."""
        v = self.serie(nome).get(mes_txt(m))
        if v is None:
            return None
        return Decimal(str(v)) if not isinstance(v, Decimal) else v


class Faltas:
    """Meses que faltam no cache, por índice. Qualquer falta leva ao exit 3."""

    def __init__(self):
        self.itens = {}

    def add(self, indice, m, motivo):
        chave = (indice, motivo)
        self.itens.setdefault(chave, []).append(mes_txt(m))

    def __bool__(self):
        return bool(self.itens)

    def lista(self):
        return [{"indice": i, "meses": ms, "motivo": mot} for (i, mot), ms in self.itens.items()]


# ---------------------------------------------------------------- blocos de conta

def correcao(cache, faltas, indice, ini, fim_excl, motivo=None):
    """Fator de correção = produto(1 + taxa/100) dos meses [ini, fim_excl)."""
    fator, memoria = UM, []
    if indice == "IPCA-E" and motivo is None:
        motivo = MOTIVO_IPCA_E
    for m in meses(ini, fim_excl):
        t = cache.taxa(indice, m)
        if t is None:
            faltas.add(indice, m, motivo or "mês fora do intervalo do cache ou sem valor")
            memoria.append({"mes": mes_txt(m), "taxa": None})
            continue
        fator *= UM + t / CEM
        memoria.append({"mes": mes_txt(m), "taxa": str(t), "fator_acumulado": q10(fator)})
    return fator, memoria


def acumula(taxas, acumulacao):
    """Percentual acumulado. Simples = soma; composta = produto(1 + t/100) - 1."""
    if acumulacao == "composta":
        f = UM
        for t in taxas:
            f *= UM + t / CEM
        return (f - UM) * CEM
    return sum(taxas, ZERO)


def selic_mensal(cache, faltas, ini, fim_excl, acumulacao, aplicada_no_mes_seguinte=False, indice="SELIC"):
    """Taxa mensal de meses inteiros [ini, fim_excl): Selic, ou outra série (taxa legal) por `indice`."""
    taxas, memoria = [], []
    for m in meses(ini, fim_excl):
        t = cache.taxa(indice, m)
        item = {"mes": mes_txt(m), "taxa": None if t is None else str(t)}
        if aplicada_no_mes_seguinte:
            item["computada_em"] = mes_txt(mes_soma(m, 1))
        memoria.append(item)
        if t is None:
            faltas.add(indice, m, "mês fora do intervalo do cache")
            continue
        taxas.append(t)
    return acumula(taxas, acumulacao), memoria


def taxa_fixa_mensal(taxa, ini, fim_excl):
    """Juros simples de taxa fixa por mês inteiro [ini, fim_excl): soma = taxa x meses."""
    ms = meses(ini, fim_excl)
    return taxa * len(ms), [{"mes": mes_txt(m), "taxa": str(taxa)} for m in ms]


def juros_pro_rata(cache, faltas, indice, ini, fim_excl, acumulacao="simples", taxa_fixa=None):
    """Taxa do mês / dias corridos do mês x dias apropriados (Res. CMN 5.171, art. 6º).

    Mês inteiro entra com a taxa cheia. indice=None usa taxa_fixa (1% a.m.).
    """
    parcelas, memoria = [], []
    for m, dias, dias_mes in dias_por_mes(ini, fim_excl):
        t = taxa_fixa if indice is None else cache.taxa(indice, m)
        if t is None:
            faltas.add(indice, m, "mês fora do intervalo do cache")
            memoria.append({"mes": mes_txt(m), "taxa": None, "dias": dias, "dias_mes": dias_mes})
            continue
        contrib = t * Decimal(dias) / Decimal(dias_mes)
        parcelas.append(contrib)
        memoria.append({
            "mes": mes_txt(m), "taxa": str(t), "dias": dias, "dias_mes": dias_mes,
            "contribuicao": q6(contrib),
        })
    return acumula(parcelas, acumulacao), memoria


NUMERICOS = ("fator", "percentual", "percentual_juros", "percentual_selic_periodo")


def fatia(regime, ini, fim, indice, tipo, fundamento, memoria, formula, **extra):
    f = {
        "regime": regime,
        "periodo": {"inicio": ini, "fim": fim},
        "indice": indice,
        "tipo": tipo,
        "formula": formula,
        "fundamento": fundamento,
    }
    incompleta = any(
        item.get(k, "") is None for item in memoria for k in ("taxa", "ipca", "selic")
    )
    if incompleta:
        for k in NUMERICOS:
            if k in extra:
                extra[k] = None
        extra["completa"] = False
    f.update(extra)
    f["memoria"] = memoria
    return f


def fim_txt(d_excl):
    return (d_excl - dt.timedelta(days=1)).isoformat()


def meses_txt(ini, fim_excl):
    return f"{mes_txt(ini)}..{mes_txt(mes_soma(fim_excl, -1))}" if ini < fim_excl else "(nenhum)"


# ---------------------------------------------------------------- regimes

def regime_civil_cc406(e, cache, faltas, alertas):
    valor, d0, d1 = e["valor"], e["data_inicial"], e["data_final"]
    cit = e.get("data_citacao")
    dj = max(d0, cit) if cit else d0
    if not cit:
        alertas.append(
            "Juros contados desde data_inicial (mora desde o vencimento). Se a mora "
            "começa na citação (CC 405), informe data_citacao."
        )
    tt = e.get("taxa_titulo")
    if tt is not None and dj >= MARCO_LEI_14905:
        alertas.append("taxa_titulo ignorada: os juros só começam em 30/08/2024 ou depois, na taxa legal.")
    if dj < MARCO_LEI_14905 and dj < d1 and tt is None:
        return _civil_selic_tema_1368(e, dj, cache, faltas, alertas)
    if d0 < MARCO_LEI_14905:
        alertas.append(
            "[VERIFICAR] Correção pelo IPCA no período todo, como pede o regime. Antes de "
            "30/08/2024 o índice do título ou da tabela do tribunal pode ser outro."
        )
    out = []
    fator, mem = correcao(cache, faltas, "IPCA", mes(d0), mes(d1))
    out.append(fatia(
        "civil-cc406", d0.isoformat(), d1.isoformat(), "IPCA", "correcao",
        "CC art. 389, parágrafo único (Lei 14.905/2024)", mem,
        f"fator = produto(1 + IPCA_m/100), m = {meses_txt(mes(d0), mes(d1))}",
        fator=q10(fator), percentual=q6((fator - UM) * CEM),
    ))
    p1 = p2 = ZERO
    if dj < MARCO_LEI_14905 and dj < d1:
        fim = min(MARCO_LEI_14905, d1)
        p1, mem = juros_pro_rata(cache, faltas, None, dj, fim, taxa_fixa=tt)
        alertas.append(
            f"[TÍTULO] Juros de {tt}% a.m. até 29/08/2024 pela taxa do título ou do contrato "
            "(taxa_titulo), no lugar da Selic do STJ Tema 1.368; conferir a cláusula."
        )
        out.append(fatia(
            "civil-cc406", dj.isoformat(), fim_txt(fim), f"{tt}% a.m. (título)", "juros",
            "Taxa do título ou do contrato (CC art. 406, redação anterior à Lei 14.905/2024; "
            "STJ Tema 1.368: a Selic só cede à taxa pactuada); juros simples", mem,
            f"percentual = soma({tt}% x dias_apropriados/dias_do_mes)", percentual=q6(p1),
            taxa_titulo=True,
        ))
    if d1 > MARCO_LEI_14905 and dj < d1:
        ini = max(dj, MARCO_LEI_14905)
        p2, mem = juros_pro_rata(cache, faltas, "TAXA_LEGAL", ini, d1)
        out.append(fatia(
            "civil-cc406", ini.isoformat(), fim_txt(d1), "TAXA_LEGAL", "juros",
            "CC art. 406 §§1º e 3º (Lei 14.905/2024); Res. CMN 5.171/2024 arts. 6º e 7º; "
            "soma simples, pro rata pelos dias corridos do mês", mem,
            "percentual = soma(taxa_legal_m / dias_do_mes x dias_apropriados)",
            percentual=q6(p2),
        ))
    corrigido = valor * fator
    juros = corrigido * (p1 + p2) / CEM
    comp = {
        "principal_corrigido": corrigido,
        "juros_taxa_titulo": corrigido * p1 / CEM,
        "juros_taxa_legal": corrigido * p2 / CEM,
    }
    formula = "valor_final = valor x fator_IPCA x (1 + (pct_taxa_titulo + pct_taxa_legal)/100)"
    return corrigido + juros, out, comp, formula


def _civil_selic_tema_1368(e, dj, cache, faltas, alertas):
    """Mora antes de 30/08/2024 sem taxa no título: Selic integral até 29/08/2024 (Tema 1.368)."""
    valor, d0, d1 = e["valor"], e["data_inicial"], e["data_final"]
    acum = e["acumulacao_selic"]
    out = []
    f1 = UM
    if mes(d0) < mes(dj):
        f1, mem = correcao(cache, faltas, "IPCA", mes(d0), mes(dj))
        out.append(fatia(
            "civil-cc406", d0.isoformat(), fim_txt(dj), "IPCA", "correcao",
            "CC art. 389, parágrafo único; correção só até o início dos juros, quando a Selic a "
            "absorve (STJ Tema 1.368)", mem,
            f"fator = produto(1 + IPCA_m/100), m = {meses_txt(mes(d0), mes(dj))}",
            fator=q10(f1), percentual=q6((f1 - UM) * CEM),
        ))
        alertas.append(
            "[VERIFICAR] Correção pelo IPCA de data_inicial até a citação; a tabela do tribunal ou "
            "o título pode indicar outro índice para esse trecho."
        )
    fim2 = min(MARCO_LEI_14905, d1)
    p2, mem = juros_pro_rata(cache, faltas, "SELIC", dj, fim2, acum)
    out.append(fatia(
        "civil-cc406", dj.isoformat(), fim_txt(fim2), "SELIC", "selic",
        "CC art. 406 (redação anterior à Lei 14.905/2024); STJ Corte Especial, Tema 1.368 "
        "(reafirma o REsp 1.795.982): Selic, que abrange juros e correção, sem IPCA cumulado", mem,
        "percentual = soma(Selic_m / dias_do_mes x dias_apropriados)",
        percentual=q6(p2), acumulacao=acum,
    ))
    alertas.append(
        "Tema 1.368 STJ: antes de 30/08/2024 a taxa do art. 406 é a Selic (sem IPCA). Se o título ou "
        "o contrato fixar outra taxa, informe taxa_titulo (% a.m.)."
    )
    alertas.append(
        "[VERIFICAR] Selic pro rata pelos dias corridos do mês do início da mora e do marco; conferir "
        "a convenção da tabela do tribunal."
    )
    f3, p3 = UM, ZERO
    if d1 > MARCO_LEI_14905:
        # Agosto/2024 já está na fase Selic: o IPCA começa em 09/2024.
        m_ipca = mes_soma(mes(MARCO_LEI_14905), 1)
        f3, mem = correcao(cache, faltas, "IPCA", m_ipca, mes(d1))
        out.append(fatia(
            "civil-cc406", MARCO_LEI_14905.isoformat(), d1.isoformat(), "IPCA", "correcao",
            "CC art. 389, parágrafo único (Lei 14.905/2024)", mem,
            f"fator = produto(1 + IPCA_m/100), m = {meses_txt(m_ipca, mes(d1))}",
            fator=q10(f3), percentual=q6((f3 - UM) * CEM),
        ))
        p3, mem = juros_pro_rata(cache, faltas, "TAXA_LEGAL", MARCO_LEI_14905, d1)
        out.append(fatia(
            "civil-cc406", MARCO_LEI_14905.isoformat(), fim_txt(d1), "TAXA_LEGAL", "juros",
            "CC art. 406 §§1º e 3º (Lei 14.905/2024); Res. CMN 5.171/2024 arts. 6º e 7º", mem,
            "percentual = soma(taxa_legal_m / dias_do_mes x dias_apropriados)", percentual=q6(p3),
        ))
    v1 = valor * f1
    v2 = v1 * (UM + p2 / CEM)
    v3 = v2 * f3
    juros3 = v3 * p3 / CEM
    comp = {"valor_corrigido_ate_citacao": v1, "valor_no_marco_selic": v2,
            "valor_corrigido_ipca": v3, "juros_taxa_legal": juros3}
    return v3 + juros3, out, comp, \
        "valor_final = valor x fator_IPCA_ate_citacao x (1 + pct_Selic/100) x fator_IPCA x (1 + pct_taxa_legal/100)"


def regime_selic_privado(e, cache, faltas, alertas):
    valor, d0, d1 = e["valor"], e["data_inicial"], e["data_final"]
    if not e.get("data_citacao"):
        raise EntradaInvalida("selic-integral-privado exige data_citacao")
    c, p = mes(e["data_citacao"]), mes(d1)
    acum = e["acumulacao_selic"]
    out = []
    fator = UM
    if mes(d0) < c:
        fator, mem_c = correcao(cache, faltas, "IPCA-E", mes(d0), c)
        out.append(fatia(
            "selic-integral-privado", d0.isoformat(), fim_txt(e["data_citacao"]), "IPCA-E", "correcao",
            "Manual CJF (ed. jul./2026), item 4.2.1.1, Nota 2 (correção até a citação, quando a Selic passa "
            "a abranger juros e correção); IPCA-E mensal = IPCA-15/IBGE desde 01/2001 (mesmo item)",
            mem_c, f"fator = produto(1 + IPCA-E_m/100), m = {meses_txt(mes(d0), c)} (valor no mês da citação)",
            fator=q10(fator), percentual=q6((fator - UM) * CEM),
        ))
        alertas.append(
            "[VERIFICAR] Correção de data_inicial até a citação pelo IPCA-E (Manual CJF); o título "
            "pode fixar outro índice para esse trecho."
        )
    else:
        alertas.append(
            "[VERIFICAR] valor tomado como já corrigido até a citação; a Selic corre do "
            "mês seguinte (Manual CJF ed. jul./2026, item 4.2.1.1, Nota 4 b)."
        )
    pct, mem = selic_mensal(cache, faltas, mes_soma(c, 1), p, acum)
    um_pct = UM if p > c else ZERO
    if acum == "composta":
        pct = ((UM + pct / CEM) * (UM + um_pct / CEM) - UM) * CEM
    else:
        pct = pct + um_pct
    if p > c:
        mem.append({"mes": mes_txt(p), "taxa": "1", "observacao": "1% no mês do pagamento"})
    else:
        alertas.append("Pagamento no mês da citação: não corre Selic nem o 1% do mês do pagamento.")
    out.append(fatia(
        "selic-integral-privado", e["data_citacao"].isoformat(), d1.isoformat(), "SELIC", "selic",
        "Manual CJF (ed. jul./2026), item 4.2.1.1, Nota 4 a e b; CC art. 406 (redação anterior), "
        "STJ Tema 1.368 e REsp 1.795.982 (Selic engloba juros e correção)", mem,
        f"percentual = soma(Selic_m), m = {meses_txt(mes_soma(c, 1), p)}, + 1% no mês do pagamento",
        percentual=q6(pct), acumulacao=acum,
    ))
    base = valor * fator
    comp = {"principal": valor, "juros_selic": base * pct / CEM}
    if fator != UM:
        comp = {"principal": valor, "principal_corrigido_ate_citacao": base, "juros_selic": base * pct / CEM}
    return base * (UM + pct / CEM), out, comp, \
        "valor_final = valor x fator_IPCA-E_ate_citacao x (1 + (soma Selic + 1)/100)"


def regime_fazenda_ec113(e, cache, faltas, alertas):
    valor, d0, d1 = e["valor"], e["data_inicial"], e["data_final"]
    exp = e.get("data_expedicao")
    encadeia = exp is not None and exp < d1
    fim = d1
    if encadeia:
        if exp < d0:
            raise EntradaInvalida(
                "data_expedicao anterior a data_inicial: o período todo é posterior à expedição; "
                "use o regime fazenda-requisitorio-ec136")
        if e.get("ente") not in INICIO_EC136:
            raise EntradaInvalida(
                "fazenda-ec113 com data_expedicao anterior a data_final exige ente (federal, estadual "
                "ou municipal): o trecho depois da expedição segue a EC 136/2025")
        _veda_selic_composta(e)
        fim = exp
    natureza = e.get("natureza")
    cons = e.get("valor_consolidado_12_2021")
    m0 = mes(d0)
    out = []
    juros_ate = ZERO
    # Período que termina antes de 12/2021: a consolidação para no mês de data_final (correção
    # até o mês anterior, convenção dos coeficientes) e não há fatia Selic.
    antes_12_2021 = mes(fim) < MES_CONSOLIDACAO_EC113
    fim_cons = mes(fim) if antes_12_2021 else MES_CONSOLIDACAO_EC113
    data_cons = fim if antes_12_2021 else dt.date(2021, 12, 31)
    if antes_12_2021 and cons is not None:
        raise EntradaInvalida(
            "valor_consolidado_12_2021 informado, mas o período termina antes de 12/2021 "
            f"({fim.isoformat()}): não há consolidação a aplicar")
    if m0 <= MES_CONSOLIDACAO_EC113 and cons is not None:
        inicio_selic = MES_CONSOLIDACAO_EC113
        principal, juros_ate = cons
        if principal != valor:
            alertas.append(
                f"valor ({q2(valor)}) substituído pelo principal consolidado em 12/2021 "
                f"({q2(principal)}), informado em valor_consolidado_12_2021.")
        fund = f"{MANUAL}, item 4.2.1.1, Nota 5 a a c; valor consolidado informado na entrada"
        if natureza:
            fund += f"; critérios até 12/2021 (STJ Tema 905, {natureza}): {TEMA_905[natureza][1]}"
        out.append(fatia(
            "fazenda-ec113", d0.isoformat(), "2021-12-31", "consolidado em 12/2021 (entrada)",
            "consolidacao", fund,
            [{"principal_12_2021": q2(principal), "juros_ate_12_2021": q2(juros_ate),
              "origem": "dado de entrada (valor_consolidado_12_2021 e juros_consolidados_12_2021)"}],
            "principal_12_2021 e juros_ate_12_2021 informados; não recalculados por este script",
        ))
    elif m0 < MES_CONSOLIDACAO_EC113 and natureza in ("previdenciaria", "assistencial", "administrativa"):
        inicio_selic = MES_CONSOLIDACAO_EC113
        principal, juros_ate = _consolida_tema_905(e, natureza, cache, faltas, alertas, out,
                                                   fim_cons, data_cons)
    elif m0 < MES_CONSOLIDACAO_EC113:
        inicio_selic = MES_CONSOLIDACAO_EC113
        principal = None
        if natureza:
            indice, fund, formula = TEMA_905[natureza]
        else:
            indice = "INDICE DO TEMA 905 (natureza não informada)"
            fund = ("; ".join(f"{k}: {v[1]}" for k, v in TEMA_905.items()))
            formula = "depende da natureza: " + " | ".join(f"{k}: {v[2]}" for k, v in TEMA_905.items())
            alertas.append(
                "Informe natureza (previdenciaria, assistencial, administrativa ou tributaria): ela "
                f"define o índice até {'data_final' if antes_12_2021 else '12/2021'} (STJ Tema 905).")
        if antes_12_2021:
            formula = formula_ate_data_final(formula)
            faltas.add(indice, m0,
                       f"atualização até o fim do período ({fim.isoformat()}) pelos critérios do STJ Tema 905 "
                       f"({fund}), não calculada por este script; calcule-a pela fonte oficial (o período "
                       "termina antes de 12/2021, sem consolidação nem Selic da EC 113)")
        else:
            faltas.add(indice, m0,
                       f"consolidação até 12/2021 pelos critérios do STJ Tema 905 ({fund}), não calculada "
                       "por este script; informe valor_consolidado_12_2021 e juros_consolidados_12_2021")
        out.append(fatia(
            "fazenda-ec113", d0.isoformat(), data_cons.isoformat(), indice, "consolidacao",
            f"STJ Tema 905 (REsp 1.495.146): {fund}; {MANUAL}, item 4.2.1.1, Nota 5 a", [],
            f"{formula}, m = {meses_txt(m0, fim_cons)}",
        ))
    else:
        inicio_selic = m0
        if cons is not None:
            alertas.append("valor_consolidado_12_2021 ignorado: data_inicial é posterior a 12/2021.")
        principal = valor
        if m0 == MES_CONSOLIDACAO_EC113 and e.get("data_citacao") and mes(e["data_citacao"]) <= m0:
            alertas.append(
                "[VERIFICAR] parcela de 12/2021 com citação anterior: a consolidação inclui os "
                "juros de dez./2021 (0,4412%, Nota 5 a), não somados aqui; use "
                "valor_consolidado_12_2021 e juros_consolidados_12_2021 para incluí-los."
            )
    if antes_12_2021:
        alertas.append(
            f"[VERIFICAR] Período termina antes de 12/2021 ({fim.isoformat()}): só os critérios do "
            "STJ Tema 905 até data_final, sem Selic da EC 113.")
        if juros_ate is None:
            principal = None
        formula = "valor_final = principal_corrigido + juros_ate_data_final (critérios do Tema 905)"
        if not encadeia:
            if principal is None:
                return None, out, {}, formula
            return principal + juros_ate, out, {"principal_corrigido": principal,
                                                "juros_ate_data_final": juros_ate}, formula
        j_exp = None if principal is None else juros_ate
        v, fat, comp136, f136 = trecho_ec136(e, cache, faltas, alertas, principal, j_exp, ZERO, exp, d1)
        out.extend(fat)
        comp = {}
        if principal is not None:
            comp = {"principal_na_expedicao": principal, "juros_na_expedicao": j_exp}
            comp.update(comp136)
        return v, out, comp, f"principal e juros na expedição: {formula}; depois, {f136}"
    if juros_ate is None:
        principal = None  # juros até 12/2021 desconhecidos: sem número final
    fase = _fase_pos_12_2021(e, cache, faltas, alertas, out, principal, juros_ate, ZERO,
                             inicio_selic, fim, encadeia)
    if e.get("natureza_tributaria"):
        alertas.append("Natureza tributária: Selic da Lei 9.430/96 art. 61 §3º, mesma forma de cálculo.")
    formula = fase["formula"]
    if not encadeia:
        if fase["principal"] is None:
            return None, out, {}, fase["formula_aberta"]
        return fase["total"], out, fase["componentes"], formula
    # Na expedição, a Selic da EC 113 entra como juros (Nota 5: "Juros Selic" em coluna própria).
    alertas.append(
        "[VERIFICAR] Na expedição, principal = principal corrigido e juros = juros até 12/2021 + "
        "juros Selic (+ taxa legal desde 09/2025), separação da Nota 5; daí em diante, EC 136/2025.")
    p_exp, jns_exp, js_exp = fase["principal"], fase["juros_nao_selic"], fase["juros_selic"]
    v, fat, comp136, f136 = trecho_ec136(e, cache, faltas, alertas, p_exp, jns_exp, js_exp, exp, d1)
    out.extend(fat)
    comp = {}
    if p_exp is not None:
        comp = dict(fase["componentes"])
        comp.pop("principal_corrigido", None)
        comp.update({"principal_na_expedicao": p_exp, "juros_na_expedicao": jns_exp + js_exp})
        comp.update(comp136)
    return v, out, comp, f"principal e juros na expedição: {formula}; depois, {f136}"


def _fase_pos_12_2021(e, cache, faltas, alertas, out, principal, juros_ns, juros_s, inicio_selic, fim,
                      encadeia, regime="fazenda-ec113"):
    """Fase pré-requisitório da competência `inicio_selic` (>= 12/2021) até `fim` (data).

    Selic da EC 113 (soma simples, a de cada competência computada no mês seguinte) até a
    competência 08/2025; da 09/2025 em diante, salvo natureza tributária, correção + taxa legal
    pela natureza (Manual CJF ed. jul./2026; Tema 1.419 do STF). `principal` None = desconhecido.
    Devolve dict com principal, juros_nao_selic, juros_selic, total, componentes e fórmulas.
    """
    acum = e["acumulacao_selic"]
    tributaria = bool(e.get("natureza_tributaria"))
    m_fim = mes(fim)
    corte = m_fim if tributaria else min(m_fim, INICIO_TEMA_1419)
    conhecido = principal is not None
    base_selic = None if not conhecido else principal + juros_ns
    pct_selic = ZERO
    if inicio_selic < INICIO_TEMA_1419 or tributaria:
        pct_selic, mem = selic_mensal(cache, faltas, inicio_selic, max(inicio_selic, corte), acum,
                                      aplicada_no_mes_seguinte=True)
        cortada = corte < m_fim
        fim_fatia = ("2025-08-31" if cortada else (fim_txt(fim) if encadeia else fim.isoformat()))
        out.append(fatia(
            regime, f"{mes_txt(inicio_selic)}-01", fim_fatia, "SELIC", "selic",
            f"EC 113/2021 art. 3º (redação original); {MANUAL}, item 4.2.1.1, Notas 4 a e c e 5 a a c "
            "(item 4.3.1.1, Notas 4 e 5, na previdenciária); Res. CNJ 303/2019 art. 22 §1º", mem,
            f"juros_selic = (principal + juros_ate_12_2021) x soma(Selic_m)/100, m = "
            f"{meses_txt(inicio_selic, max(inicio_selic, corte))} (Selic de cada mês computada no mês seguinte, "
            + ("até a competência 08/2025, computada em 09/2025; daí em diante, Tema 1.419 do STF)" if cortada
               else "até o mês da expedição)" if encadeia else "inclusive no do pagamento)"),
            percentual=q6(pct_selic), acumulacao=acum,
        ))
    juros_selic_novos = None if not conhecido else base_selic * pct_selic / CEM
    js = None if not conhecido else juros_s + juros_selic_novos
    formula_selic = "valor_final = principal + juros_ate_12_2021 + juros_selic"
    res = {"principal": principal, "juros_nao_selic": juros_ns, "juros_selic": js,
           "formula": formula_selic,
           "formula_aberta": "valor_final = (principal_12_2021 + juros_ate_12_2021) x (1 + soma Selic/100)"}
    if conhecido:
        res["total"] = principal + juros_ns + js
        res["componentes"] = {"principal_corrigido": principal, "juros_ate_12_2021": juros_ns,
                              "juros_selic": juros_selic_novos}
        if juros_s:
            res["componentes"]["juros_selic_anteriores"] = juros_s
    if tributaria or m_fim <= INICIO_TEMA_1419:
        return res

    # Da competência 09/2025 em diante (Tema 1.419 do STF).
    m2 = max(INICIO_TEMA_1419, inicio_selic)
    natureza = e.get("natureza")
    formula = ("valor_final = principal x fator + (juros_ate_12_2021 + juros_selic) x fator + "
               "principal x fator x soma(taxa_legal_m)/100")
    res["formula"] = res["formula_aberta"] = formula
    if natureza not in POS_TEMA_1419:
        # meses(m2, m_fim) vazio (fim no próprio mês m2): registra m2, senão o principal None sai sem falta.
        for m in meses(m2, m_fim) or [m2]:
            faltas.add("NATUREZA (A PARTIR DE 09/2025)", m,
                       "a partir de 09/2025 a correção e a taxa legal dependem da natureza (previdenciária: "
                       f"INPC + taxa legal com dedução do INPC, {MANUAL}, itens 4.3.1.1 e 4.3.2; assistencial e "
                       "administrativa: IPCA-15 + taxa legal com dedução do IPCA-15, itens 4.2.1.1 e 4.2.2): "
                       "informe natureza")
        out.append(fatia(
            regime, f"{mes_txt(m2)}-01", fim.isoformat(), "CORRECAO + TAXA LEGAL (natureza não informada)",
            "correcao_e_juros", f"ARE 1.557.312/SP (Tema 1.419 do STF); {MANUAL}, itens 4.2.1.1, 4.2.2, "
            "4.3.1.1 e 4.3.2", [], f"{formula}, m = {meses_txt(m2, m_fim)}",
        ))
        alertas.append("Informe natureza: a partir de 09/2025 ela define a correção e a taxa legal "
                       f"({MANUAL}; Tema 1.419 do STF).")
        res.update(principal=None, juros_selic=None)
        return res
    idx, serie_tl, fund_corr, fund_tl = POS_TEMA_1419[natureza]
    fator, mem = correcao(cache, faltas, idx, m2, m_fim)
    out.append(fatia(
        regime, f"{mes_txt(m2)}-01", fim.isoformat(), idx, "correcao", fund_corr, mem,
        f"fator = produto(1 + {idx}_m/100), m = {meses_txt(m2, m_fim)}; corrige o principal e os juros "
        "acumulados até 08/2025",
        fator=q10(fator), percentual=q6((fator - UM) * CEM),
    ))
    cit = e.get("data_citacao")
    mj = max(m2, mes(cit)) if cit else m2
    if not cit:
        alertas.append(
            f"[VERIFICAR] Taxa legal desde {mes_txt(m2)} sem data_citacao: se a citação (início dos juros) "
            "for posterior, informe-a.")
    pct_tl, mem = selic_mensal(cache, faltas, mj, max(mj, m_fim), "simples",
                               aplicada_no_mes_seguinte=True, indice=serie_tl)
    out.append(fatia(
        regime, f"{mes_txt(mj)}-01", fim_txt(fim) if encadeia else fim.isoformat(), serie_tl, "juros",
        fund_tl, mem,
        f"juros_taxa_legal = principal x fator x soma(taxa_legal_m)/100, m = {meses_txt(mj, max(mj, m_fim))} "
        "(a de cada competência computada no mês seguinte"
        + (", até o mês da expedição)" if encadeia else ", inclusive no do pagamento)"),
        percentual=q6(pct_tl), acumulacao="simples",
    ))
    if natureza != "previdenciaria":
        alertas.append(
            f"[VERIFICAR] Natureza {natureza} desde 09/2025: IPCA-15 + taxa legal com dedução do IPCA-15 "
            f"(SGS 29543), como nas ações condenatórias em geral ({MANUAL}, itens 4.2.1.1 e 4.2.2).")
    if not conhecido:
        return res
    p_fim = principal * fator
    jns_corr, js_corr = juros_ns * fator, js * fator
    juros_tl = p_fim * pct_tl / CEM
    comp = {"principal_corrigido": p_fim, "juros_ate_12_2021_corrigidos": jns_corr,
            "juros_selic_corrigidos": js_corr, "juros_taxa_legal": juros_tl}
    res.update(principal=p_fim, juros_nao_selic=jns_corr + juros_tl, juros_selic=js_corr,
               total=p_fim + jns_corr + js_corr + juros_tl, componentes=comp)
    return res


def _correcao_previdenciaria(e, cache, faltas, out, fim, fund_tema):
    """Correção previdenciária de data_inicial ao mês anterior a `fim`, pela tabela do item 4.3.1.1.

    Fatias: histórica (antes de 05/1996, fora do cache salvo o INPC), IGP-DI (05/1996 a 08/2006) e
    INPC (09/2006 em diante). Devolve o fator (produto das fatias; as faltas vão para `faltas`).
    """
    d0 = e["data_inicial"]
    m0 = mes(d0)
    fator_total = UM
    rotulo_fim = "12_2021" if fim == MES_CONSOLIDACAO_EC113 else "corrigido"
    trechos = []
    if m0 < INICIO_IGPDI_PREV:
        trechos.append(("historica", m0, min(INICIO_IGPDI_PREV, fim)))
    if m0 < INICIO_INPC_PREV and fim > INICIO_IGPDI_PREV:
        trechos.append(("IGP-DI", max(m0, INICIO_IGPDI_PREV), min(INICIO_INPC_PREV, fim)))
    if fim > INICIO_INPC_PREV or m0 >= INICIO_INPC_PREV:
        trechos.append(("INPC", max(m0, INICIO_INPC_PREV), fim))
    for tipo, ini, fim_excl in trechos:
        if ini >= fim_excl and len(trechos) > 1:
            continue
        p_ini = dt.date(ini[0], ini[1], 1) if ini != m0 else d0
        p_fim = (dt.date(fim_excl[0], fim_excl[1], 1) - dt.timedelta(days=1)).isoformat()
        if tipo == "historica":
            mem = []
            for m in meses(ini, fim_excl):
                linha = next((t for t in TABELA_PREV_HISTORICA if t[0] <= m <= t[1]), None)
                if linha and linha[2] == "INPC" and cache.taxa("INPC", m) is not None:
                    t = cache.taxa("INPC", m)
                    fator_total *= UM + t / CEM
                    mem.append({"mes": mes_txt(m), "taxa": str(t), "indexador": "INPC"})
                    continue
                nome = linha[2] if linha else "sem indexador no Manual (anterior a 1964)"
                fund = linha[3] if linha else ""
                faltas.add(f"CORRECAO HISTORICA ({nome})", m,
                           f"previdenciária: {nome} ({fund}; {MANUAL}, item 4.3.1.1), indexador fora do cache; "
                           "aplique a tabela do Manual ou os critérios do título")
                mem.append({"mes": mes_txt(m), "taxa": None, "indexador": nome})
            out.append(fatia(
                "fazenda-ec113", p_ini.isoformat(), p_fim, "TABELA HISTORICA (item 4.3.1.1)", "correcao",
                f"{MANUAL}, item 4.3.1.1 (indexadores anteriores a 05/1996: ORTN, OTN, IPC, BTN, INPC, IRSM, "
                "URV, IPC-R e INPC); STJ Tema 905", mem,
                f"fator = produto(1 + indexador_m/100), m = {meses_txt(ini, fim_excl)}",
                fator=None, completa=False,
            ))
            continue
        fund = (f"MP 1.415/1996 e Lei 10.192/2001 (IGP-DI de 05/1996 a 08/2006); {MANUAL}, item 4.3.1.1"
                if tipo == "IGP-DI" else fund_tema)
        fator, mem = correcao(cache, faltas, tipo, ini, fim_excl)
        fator_total *= fator
        out.append(fatia(
            "fazenda-ec113", p_ini.isoformat(), p_fim, tipo, "correcao", fund, mem,
            f"principal_{rotulo_fim} = valor x produto(1 + {tipo}_m/100), m = {meses_txt(ini, fim_excl)}"
            + (" (com as fatias anteriores)" if len(trechos) > 1 else ""),
            fator=q10(fator), percentual=q6((fator - UM) * CEM),
        ))
    return fator_total


def _consolida_tema_905(e, natureza, cache, faltas, alertas, out,
                        fim=MES_CONSOLIDACAO_EC113, data_fim=dt.date(2021, 12, 31)):
    """Consolidação em 12/2021 pelo STJ Tema 905, sem valor consolidado na entrada.

    Correção: previdenciária pela tabela do item 4.3.1.1 do Manual CJF (ed. jul./2026) (INPC desde
    09/2006, IGP-DI de 05/1996 a 08/2006, histórica antes); assistencial e administrativa pelo IPCA-E.
    Meses de data_inicial ao anterior a `fim` (11/2021, convenção dos coeficientes da Nota 5; ou o
    mês anterior ao de data_final, se o período termina antes de 12/2021).
    Juros, por mês inteiro, até o mês de `data_fim`, inclusive; na previdenciária, excluído o mês da
    citação (ou do vencimento, se posterior), pelo item 4.1.3, Nota 5: previdenciária 1% a.m. até 06/2009 e 0,5% a.m. de 07/2009 a 04/2012 (item 4.3.2); juros da
    poupança (sem série no cache) em fórmula. Devolve (principal, juros), juros None se em fórmula.
    """
    valor, d0 = e["valor"], e["data_inicial"]
    m0 = mes(d0)
    fund_tema = "STJ Tema 905 (REsp 1.495.146): " + TEMA_905[natureza][1]
    if natureza == "previdenciaria":
        fator = _correcao_previdenciaria(e, cache, faltas, out, fim, fund_tema)
    else:
        fund_corr = (fund_tema + f"; {MANUAL}, item 4.2.1.1, Nota 5 a; IPCA-E mensal = IPCA-15/IBGE desde "
                     "01/2001")
        fator, mem = correcao(cache, faltas, "IPCA-E", m0, fim)
        fim_corr = dt.date(fim[0], fim[1], 1) - dt.timedelta(days=1)
        out.append(fatia(
            "fazenda-ec113", d0.isoformat(), fim_corr.isoformat(), "IPCA-E", "correcao", fund_corr, mem,
            f"principal_{'12_2021' if fim == MES_CONSOLIDACAO_EC113 else 'corrigido'} = valor x "
            f"produto(1 + IPCA-E_m/100), m = {meses_txt(m0, fim)}",
            fator=q10(fator), percentual=q6((fator - UM) * CEM),
        ))
    principal = valor * fator
    cit = e.get("data_citacao")
    ate_12_2021 = fim == MES_CONSOLIDACAO_EC113
    if cit is not None and cit > data_fim:
        if ate_12_2021:
            alertas.append(
                "[VERIFICAR] Citação posterior a 12/2021: sem juros da poupança até 12/2021 (juros só "
                "desde a citação); daí em diante, Selic da EC 113.")
        else:
            alertas.append(
                "[VERIFICAR] Citação posterior a data_final: sem juros da poupança no período (juros "
                "só desde a citação).")
        return principal, ZERO
    m_juros = max(m0, mes(cit)) if cit is not None else m0
    m_fim_j = mes_soma(mes(data_fim), 1)       # juros até o mês de data_fim, inclusive
    pedido = ("informe valor_consolidado_12_2021 e juros_consolidados_12_2021" if ate_12_2021 else
              "calcule-os pela fonte oficial (o período termina antes de 12/2021, sem consolidação)")
    juros_formula = ("juros_ate_12_2021 = principal_12_2021" if ate_12_2021 else
                     "juros_ate_data_final = principal_corrigido")
    juros_fixos = ZERO
    inicio_poupanca = m_juros
    if natureza == "previdenciaria":
        # Item 4.1.3, Nota 5 (remetida pelo 4.3.2): exclui-se o mês de início, inclui-se o da conta.
        m_juros = mes_soma(m_juros, 1)
        inicio_poupanca = max(m_juros, mes_soma(FIM_JUROS_05, 1))
        trechos = (
            (m_juros, min(mes_soma(FIM_JUROS_1PCT_PREV, 1), m_fim_j), Decimal(1),
             "1% a.m.", "Decreto-Lei 2.322/1987 (até 06/2009)"),
            (max(m_juros, mes_soma(FIM_JUROS_1PCT_PREV, 1)), min(mes_soma(FIM_JUROS_05, 1), m_fim_j),
             Decimal("0.5"), "0,5% a.m.",
             "Lei 9.494/97 art. 1º-F, redação da Lei 11.960/2009, c/c Lei 8.177/1991 (07/2009 a 04/2012)"),
        )
        for ini, fim_excl, taxa, rotulo, fund in trechos:
            if ini >= fim_excl:
                continue
            pct, mem = taxa_fixa_mensal(taxa, ini, fim_excl)
            juros_fixos += pct
            out.append(fatia(
                "fazenda-ec113", dt.date(ini[0], ini[1], 1).isoformat(),
                (dt.date(fim_excl[0], fim_excl[1], 1) - dt.timedelta(days=1)).isoformat(), rotulo, "juros",
                f"{fund}; {MANUAL}, item 4.3.2 c/c item 4.1.3, Nota 5; juros simples, por mês inteiro, "
                "excluído o mês de início e incluído o da conta", mem,
                f"{juros_formula} x soma({rotulo} por mês), m = {meses_txt(ini, fim_excl)}",
                percentual=q6(pct), acumulacao="simples",
            ))
        if juros_fixos:
            alertas.append(
                "[VERIFICAR] Juros previdenciários por mês inteiro, excluído o mês da citação (ou do "
                "vencimento, se posterior) e incluído o mês final "
                f"({MANUAL}, item 4.3.2 c/c item 4.1.3, Nota 5)."
                + ("" if cit else " data_citacao não informada: juros contados desde data_inicial."))
    if inicio_poupanca >= m_fim_j:
        return principal, principal * juros_fixos / CEM
    faltas.add("JUROS DA POUPANCA", inicio_poupanca,
               f"juros da poupança até {mes_txt(mes(data_fim))} (Lei 9.494/97 art. 1º-F, redação da Lei "
               f"11.960/2009 e Lei 12.703/2012; {MANUAL}, item "
               f"{'4.3.2' if natureza == 'previdenciaria' else '4.2.2'}) não estão no cache; {pedido}")
    if cit is not None and mes(cit) == inicio_poupanca:
        ini_poupanca = cit
    elif inicio_poupanca == m0:
        ini_poupanca = d0
    else:
        ini_poupanca = dt.date(inicio_poupanca[0], inicio_poupanca[1], 1)
    out.append(fatia(
        "fazenda-ec113", ini_poupanca.isoformat(),
        data_fim.isoformat(), "JUROS DA POUPANCA", "juros",
        f"STJ Tema 905; Lei 9.494/97 art. 1º-F (redação da Lei 11.960/2009); {MANUAL}, item 4.2.1.1, Nota 5 a",
        [],
        f"{juros_formula} x soma(juros da poupança_m), m = {mes_txt(inicio_poupanca)}.."
        f"{mes_txt(mes(data_fim))}"
        + ("" if cit else " (desde a citação; data_citacao não informada)"),
        percentual=None, completa=False,
    ))
    if ate_12_2021:
        alertas.append(
            "[FÓRMULA] Juros da poupança até 12/2021 sem série no cache: o principal de 12/2021 sai "
            "calculado na fatia, mas o valor final depende desses juros (informe juros_consolidados_12_2021 "
            "com valor_consolidado_12_2021).")
    else:
        alertas.append(
            "[FÓRMULA] Juros da poupança sem série no cache: o principal corrigido até data_final sai "
            "calculado na fatia, mas o valor final depende desses juros (da citação a data_final).")
    return principal, None


def _veda_selic_composta(e):
    if e["acumulacao_selic"] == "composta":
        raise EntradaInvalida(
            "acumulacao_selic 'composta' é vedada no requisitório: a Selic não se capitaliza sobre os juros "
            "Selic (Res. CJF 983/2026 art. 7º §4º)")


def trecho_ec136(e, cache, faltas, alertas, principal, juros, juros_selic, d_ini, d1):
    """Requisitório pela EC 136/2025 e pela Res. CJF 983/2026, de d_ini (expedição ou data-base) até d1.

    juros = juros não Selic (até 12/2021, do título, taxa legal); juros_selic = juros Selic já apurados.
    A Selic nunca incide sobre juros Selic (art. 7º §4º). principal/juros = None quando o valor na
    expedição não é conhecido: as fatias saem sem número e o chamador devolve fórmula.
    """
    _veda_selic_composta(e)
    ente = e["ente"]
    acum = e["acumulacao_selic"]
    conhecido = principal is not None
    js = juros_selic if conhecido else None
    alertas.append(ALERTA_ADI_7873)
    alertas.append("Limite de RPV: verificar pelo valor atualizado até a data de transmissão ao tribunal "
                   "(Res. CJF 983/2026 art. 3º §4º).")
    out = []
    p_fim = mes(d1)
    if e.get("natureza_tributaria"):
        pct, mem = selic_mensal(cache, faltas, mes(d_ini), p_fim, acum, aplicada_no_mes_seguinte=True)
        out.append(fatia(
            "fazenda-requisitorio-ec136", d_ini.isoformat(), d1.isoformat(), "SELIC", "selic",
            "EC 113/2021 art. 3º §2º (EC 136/2025); Provimento CNJ 207/2025 art. 4º; Res. CJF 983/2026 "
            "art. 7º §4º e art. 8º §1º", mem,
            f"percentual = soma(Selic_m), m = {meses_txt(mes(d_ini), p_fim)}",
            percentual=q6(pct), acumulacao=acum,
        ))
        formula = "valor_final = (valor + valor_juros) x (1 + soma Selic/100) + valor_juros_selic"
        if not conhecido:
            return None, out, {}, formula
        base = principal + juros
        comp = {"principal": principal, "juros_anteriores": juros, "atualizacao_selic": base * pct / CEM}
        if js:
            comp["juros_selic_anteriores"] = js
        return base * (UM + pct / CEM) + js, out, comp, formula

    inicio = INICIO_EC136[ente]
    if ente == "federal":
        fund = ("EC 113/2021 art. 3º caput e §§1º e 3º (redação da EC 136/2025); Res. CJF 983/2026 art. 7º "
                "§§2º a 4º; Provimento CNJ 207/2025 art. 2º, I, II e §2º")
    else:
        fund = ("ADCT art. 97 §§16 e 16-A (EC 136/2025); EC 113/2021 art. 3º §3º; Res. CJF 983/2026 art. 7º "
                "§7º III e art. 8º n; Provimento CNJ 207/2025 art. 3º, §1º, a e b, e §3º")
        alertas.append(
            "[VERIFICAR] Estados, DF e Municípios: a Selic do teto incide sobre o valor consolidado (principal "
            "e juros), como na Res. CJF 983/2026 art. 7º §7º III e art. 8º n. O Provimento CNJ 207/2025 art. 3º "
            "§1º c manda aplicar a Selic \"em substituição\" quando o IPCA somado aos juros a supera \"no mês da "
            "atualização\", e o §5º, no precatório não quitado no prazo do art. 100 §5º da CF, \"sobre o valor "
            "principal\"; na Justiça estadual, conferir qual regra o tribunal segue."
        )
    m_ini = mes(d_ini)
    if m_ini < inicio:
        # O trecho anterior à EC 136 nunca passa de data_final (Res. CJF 983/2026 art. 7º: até o depósito).
        corte = min(inicio, p_fim)
        fim_trecho = fim_txt(dt.date(inicio[0], inicio[1], 1)) if corte == inicio else d1.isoformat()
        pre_calculado = ente == "federal" and m_ini >= MES_CONSOLIDACAO_EC113
        if pre_calculado:
            # Res. CJF 983/2026 art. 7º §3º II: data-base entre 12/2021 e 08/2025, Selic só sobre o
            # principal e os juros não Selic, somada aos juros Selic da requisição.
            pct, mem = selic_mensal(cache, faltas, m_ini, corte, acum, aplicada_no_mes_seguinte=True)
            out.append(fatia(
                "fazenda-requisitorio-ec136", d_ini.isoformat(), fim_trecho, "SELIC", "selic",
                "Res. CJF 983/2026 art. 7º §3º II e §4º; EC 113/2021 art. 3º (redação original); "
                f"{MANUAL}, item 4.2.1.1, Nota 4 c", mem,
                f"juros_selic += (valor + valor_juros) x soma(Selic_m)/100, m = {meses_txt(m_ini, corte)} "
                "(computada no mês seguinte; nunca sobre os juros Selic)",
                percentual=q6(pct), acumulacao=acum,
            ))
            if conhecido:
                js = js + (principal + juros) * pct / CEM
        else:
            motivo = ("data-base anterior a 12/2021: Selic sobre o valor consolidado em 12/2021 (Res. CJF "
                      "983/2026 art. 7º §3º I), consolidação não feita aqui" if ente == "federal" else
                      f"expedição ou data-base anterior a {mes_txt(inicio)}: até "
                      f"{mes_txt(mes_soma(inicio, -1))} valem os critérios da Res. CNJ 303/2019, não "
                      "implementados")
            # Período dentro de um só mês (m_ini == corte): o intervalo mensal é vazio, mas o trecho
            # continua sem cálculo; sem esta falta o valor ficaria None sem formula_aberta (exit 1).
            for m in meses(m_ini, corte) or [m_ini]:
                faltas.add("RES_CNJ_303", m, motivo)
            fund_303 = ("Res. CJF 983/2026 art. 7º §3º I; Provimento CNJ 207/2025 art. 2º §1º" if ente == "federal"
                        else "Provimento CNJ 207/2025 art. 3º §2º; Res. CNJ 303/2019 arts. 21 a 25")
            out.append(fatia(
                "fazenda-requisitorio-ec136", d_ini.isoformat(), fim_trecho,
                "critérios da Res. CNJ 303/2019", "correcao", fund_303, [],
                f"valor_em_{mes_txt(corte)} = valor atualizado pelos critérios anteriores à EC 136",
            ))
        if p_fim <= inicio:
            # data_final até 09/2025: não há trecho da EC 136 a correr (nem fatia invertida).
            formula = ("valor_final = valor + valor_juros + valor_juros_selic + (valor + valor_juros) x "
                       "soma(Selic_m)/100 (sem trecho da EC 136)" if pre_calculado else
                       f"valor_final = valor atualizado pelos critérios anteriores à EC 136 até {mes_txt(p_fim)}")
            if not (conhecido and pre_calculado):
                return None, out, {}, formula
            comp = {"principal": principal, "juros_anteriores": juros, "juros_selic": js}
            return principal + juros + js, out, comp, formula
        m_ini = inicio

    graca = e.get("periodo_graca")
    mem, fator, j_pct, s_taxas, teto_mensal = [], UM, ZERO, [], []
    j_mes = Decimal(2) / Decimal(12)
    for m in meses(m_ini, p_fim):
        ti, ts = cache.taxa("IPCA", m), cache.taxa("SELIC", m)
        em_graca = bool(graca) and graca[0] <= m <= graca[1]
        jm = ZERO if em_graca else j_mes
        if ti is None:
            faltas.add("IPCA", m, "mês fora do intervalo do cache")
        else:
            fator *= UM + ti / CEM
        if ts is None:
            faltas.add("SELIC", m, "mês fora do intervalo do cache")
        else:
            s_taxas.append(ts)
        j_pct += jm
        item = {"mes": mes_txt(m), "ipca": None if ti is None else str(ti),
                "juros_2aa": q6(jm), "selic": None if ts is None else str(ts)}
        if em_graca:
            item["observacao"] = "período do art. 100 §5º da CF: sem juros (Res. CJF 983/2026 art. 7º §2º)"
        if ti is not None and ts is not None and ti + jm > ts:
            teto_mensal.append(mes_txt(m))
        mem.append(item)
    selic_pct = acumula(s_taxas, acum)
    pct_ec136 = (fator - UM) * CEM + fator * j_pct
    if conhecido:
        v_ipca = (principal + juros + js) * fator + principal * fator * j_pct / CEM
        v_selic = (principal + juros) * (UM + selic_pct / CEM) + js
        teto = v_selic < v_ipca
    else:
        teto = pct_ec136 > selic_pct
    out.append(fatia(
        "fazenda-requisitorio-ec136", f"{mes_txt(m_ini)}-01", d1.isoformat(), "IPCA + 2% a.a.",
        "correcao_e_juros", fund, mem,
        "V_ipca = (principal + juros) x fator_IPCA + principal x fator_IPCA x soma(2/12 por mês fora do "
        "período de graça)/100; V_selic = (principal + juros não Selic) x (1 + soma(Selic_m)/100) + juros "
        f"Selic; vale o menor (Res. CJF 983/2026 art. 7º §3º III), m = {meses_txt(m_ini, p_fim)}",
        fator=q10(fator), percentual_juros=q6(j_pct), percentual=q6(pct_ec136),
        percentual_selic_periodo=q6(selic_pct), acumulacao=acum,
        teto_selic_aplicado=teto, meses_com_teto_mensal_prov207=teto_mensal,
    ))
    if teto_mensal and not teto:
        alertas.append(
            "[VERIFICAR] Em " + ", ".join(teto_mensal) + " o IPCA + juros do mês passou da Selic do "
            "mês. O Provimento CNJ 207/2025 compara \"no mês da atualização\" (art. 2º III; art. 3º §1º c) e, "
            "no federal, aplica a Selic \"exclusivamente sobre o principal\" (art. 2º III); a EC (art. 3º §1º) "
            "e a Res. CJF 983/2026 (art. 7º §3º III) falam no menor valor do período, com a Selic sobre o "
            "valor consolidado. O script segue a Res. CJF 983/2026."
        )
    if teto:
        alertas.append(
            "Teto aplicado: a Selic sobre o valor consolidado (principal e juros) ficou abaixo de IPCA + 2% "
            "a.a.; vale a Selic (Res. CJF 983/2026 art. 7º §3º III), sem incidir sobre os juros Selic (§4º).")
        formula = ("valor_final = (valor + valor_juros) x (1 + soma Selic/100) + valor_juros_selic "
                   "(o menor: Selic sobre o consolidado)")
        if not conhecido:
            return None, out, {}, formula
        comp = {"principal_atualizado_selic": principal * (UM + selic_pct / CEM),
                "juros_anteriores_atualizados_selic": juros * (UM + selic_pct / CEM)}
        if js:
            comp["juros_selic_anteriores"] = js
        return v_selic, out, comp, formula
    formula = ("valor_final = (valor + valor_juros + valor_juros_selic) x fator_IPCA + valor x fator_IPCA x "
               "pct_juros/100 (o menor: IPCA + 2% a.a.)")
    if not conhecido:
        return None, out, {}, formula
    principal_corr = principal * fator
    juros_ant_corr = (juros + js) * fator
    juros_novos = principal_corr * j_pct / CEM
    comp = {"principal_corrigido": principal_corr, "juros_anteriores_corrigidos": juros_ant_corr,
            "juros_2aa": juros_novos}
    return v_ipca, out, comp, formula


def regime_ec136(e, cache, faltas, alertas):
    valor, d0, d1 = e["valor"], e["data_inicial"], e["data_final"]
    if e.get("ente") not in INICIO_EC136:
        raise EntradaInvalida("fazenda-requisitorio-ec136 exige ente: federal, estadual ou municipal")
    if not e.get("data_expedicao"):
        raise EntradaInvalida("fazenda-requisitorio-ec136 exige data_expedicao")
    exp = e["data_expedicao"]
    if d1 <= exp:
        raise EntradaInvalida(
            "data_final não passa da data_expedicao: a EC 136/2025 só corre da expedição em diante; "
            "para o período anterior use fazenda-ec113")
    _veda_selic_composta(e)
    vj = e.get("valor_juros") or ZERO
    vjs = e.get("valor_juros_selic") or ZERO
    out, comp_pre = [], {}
    principal, juros, juros_s, d_ini = valor, vj, vjs, d0
    if d0 < exp:
        if mes(d0) < MES_CONSOLIDACAO_EC113:
            raise EntradaInvalida(
                "data_inicial anterior a 12/2021 e à expedição: use fazenda-ec113 com "
                "valor_consolidado_12_2021 e data_expedicao, que fatia até a expedição")
        # Antes da expedição corre a fase pré-requisitório (EC 113 até 08/2025; Tema 1.419 depois),
        # nunca a EC 136.
        fase = _fase_pos_12_2021(e, cache, faltas, alertas, out, valor, vj, vjs, mes(d0), exp, True)
        principal, juros, juros_s = fase["principal"], fase["juros_nao_selic"], fase["juros_selic"]
        d_ini = exp
        if principal is not None:
            comp_pre = {k + "_ate_expedicao": v for k, v in fase["componentes"].items()}
            comp_pre["juros_na_expedicao"] = juros + juros_s
        alertas.append(
            "[VERIFICAR] data_inicial (data-base) anterior à expedição: até a expedição vale a fase "
            "pré-requisitório (EC 113 original até 08/2025, Nota 4 c; Tema 1.419 do STF desde 09/2025), e "
            "os juros do trecho entram como juros na expedição (separação da Nota 5); a EC 136 só corre "
            "da expedição em diante."
        )
    v, fat, comp, formula = trecho_ec136(e, cache, faltas, alertas, principal, juros, juros_s, d_ini, d1)
    out.extend(fat)
    comp_pre.update(comp)
    return v, out, comp_pre, formula


def regime_trabalhista(e, cache, faltas, alertas):
    valor, d0, d1 = e["valor"], e["data_inicial"], e["data_final"]
    if not e.get("data_ajuizamento"):
        raise EntradaInvalida("trabalhista-adc58 exige data_ajuizamento")
    da = e["data_ajuizamento"]
    acum = e["acumulacao_selic"]
    out = []
    inicio_judicial = max(da, d0)

    f1, p_trd = UM, ZERO
    # Convenção [início, fim): a fase pré-judicial vai até o ajuizamento, mas nunca além da data_final.
    fim_pre = min(da, d1)
    if d0 < fim_pre:  # datas, não meses: ajuizamento no mesmo mês ainda tem fase pré-judicial
        if d1 < da:
            alertas.append(
                "[VERIFICAR] data_final anterior ao ajuizamento: só há fase pré-judicial, encerrada na "
                "data_final (IPCA-E e TRD até o dia anterior a ela).")
        motivo = MOTIVO_IPCA_E
        if mes(d0) < mes(fim_pre):
            f1, mem = correcao(cache, faltas, "IPCA-E", mes(d0), mes(fim_pre), motivo)
            formula_ipcae = f"fator = produto(1 + IPCA-E_m/100), m = {meses_txt(mes(d0), mes(fim_pre))}"
        else:
            # Mês único e parcial: IPCA-E do mês pro rata pelos dias corridos.
            dias = (fim_pre - d0).days
            dias_mes = calendar.monthrange(d0.year, d0.month)[1]
            t = cache.taxa("IPCA-E", mes(d0))
            if t is None:
                faltas.add("IPCA-E", mes(d0), motivo)
                mem = [{"mes": mes_txt(mes(d0)), "taxa": None, "dias": dias, "dias_mes": dias_mes}]
            else:
                f1 = UM + t * Decimal(dias) / Decimal(dias_mes) / CEM
                mem = [{"mes": mes_txt(mes(d0)), "taxa": str(t), "dias": dias, "dias_mes": dias_mes,
                        "fator_acumulado": q10(f1)}]
            formula_ipcae = (f"fator = 1 + IPCA-E_{mes_txt(mes(d0))}/100 x {dias}/{dias_mes} "
                             "(mês parcial, pro rata)")
            alertas.append(
                "[VERIFICAR] Início e fim da fase pré-judicial no mesmo mês: IPCA-E do mês pro rata pelos dias "
                "corridos; conferir a convenção do PJe-Calc.")
        out.append(fatia(
            "trabalhista-adc58", d0.isoformat(), fim_txt(fim_pre), "IPCA-E", "correcao",
            "STF ADC 58/59 (fase pré-judicial); IPCA-E mensal = IPCA-15/IBGE desde 01/2001 "
            "(Manual CJF ed. jul./2026, item 4.2.1.1)", mem, formula_ipcae,
            fator=None if any(x["taxa"] is None for x in mem) else q10(f1),
        ))
        p_trd, mem = juros_pro_rata(cache, faltas, "TR", d0, fim_pre, "composta")
        out.append(fatia(
            "trabalhista-adc58", d0.isoformat(), fim_txt(fim_pre), "TR", "juros",
            "Lei 8.177/91 art. 39 caput (juros pela TRD acumulada); STF ADC 58/59; TST SDI-1, "
            "E-ED-RR-713-03.2010.5.04.0029", mem,
            "percentual = (produto(1 + TR_m/100 x dias_apropriados/dias_do_mes) - 1) x 100",
            percentual=q6(p_trd), acumulacao="composta",
        ))
        alertas.append(
            "[VERIFICAR] Juros pré-judiciais pela TRD acumulada (Lei 8.177/91 art. 39 caput): TR mensal "
            "(SGS 7811) composta, pro rata no mês parcial, sobre o valor corrigido pelo IPCA-E (Súmula 200 "
            "TST); somados ao final pelo valor do ajuizamento, sem Selic nem IPCA posterior.")

    p2 = ZERO
    if inicio_judicial < MARCO_LEI_14905 and inicio_judicial < d1:
        fim2 = min(MARCO_LEI_14905, d1)
        p2, mem = juros_pro_rata(cache, faltas, "SELIC", inicio_judicial, fim2, acum)
        out.append(fatia(
            "trabalhista-adc58", inicio_judicial.isoformat(), fim_txt(fim2), "SELIC", "selic",
            "STF ADC 58/59 (do ajuizamento em diante, Selic sem cumulação)", mem,
            "percentual = soma(Selic_m / dias_do_mes x dias_apropriados)",
            percentual=q6(p2), acumulacao=acum,
        ))
        alertas.append(
            "[VERIFICAR] Selic da fase judicial pro rata pelos dias corridos do mês do ajuizamento e "
            "do marco; conferir a convenção do PJe-Calc."
        )
    f3, p3 = UM, ZERO
    if d1 > MARCO_LEI_14905 and inicio_judicial < d1:
        ini3 = max(inicio_judicial, MARCO_LEI_14905)
        # Com fase Selic antes do marco, ago/2024 já está nela: o IPCA começa em 09/2024.
        m_ipca = mes_soma(mes(MARCO_LEI_14905), 1) if inicio_judicial < MARCO_LEI_14905 else mes(ini3)
        f3, mem = correcao(cache, faltas, "IPCA", m_ipca, mes(d1))
        out.append(fatia(
            "trabalhista-adc58", ini3.isoformat(), d1.isoformat(), "IPCA", "correcao",
            "CC art. 389, parágrafo único (Lei 14.905/2024); TST, E-ED-RR-713-03.2010.5.04.0029", mem,
            f"fator = produto(1 + IPCA_m/100), m = {meses_txt(m_ipca, mes(d1))}",
            fator=q10(f3), percentual=q6((f3 - UM) * CEM),
        ))
        p3, mem = juros_pro_rata(cache, faltas, "TAXA_LEGAL", ini3, d1)
        out.append(fatia(
            "trabalhista-adc58", ini3.isoformat(), fim_txt(d1), "TAXA_LEGAL", "juros",
            "CC art. 406 §§1º e 3º (Lei 14.905/2024); Res. CMN 5.171/2024 arts. 6º e 7º", mem,
            "percentual = soma(taxa_legal_m / dias_do_mes x dias_apropriados)", percentual=q6(p3),
        ))
    v1 = valor * f1
    juros_pre = v1 * p_trd / CEM
    v2 = v1 * (UM + p2 / CEM)
    v3 = v2 * f3
    juros3 = v3 * p3 / CEM
    comp = {"valor_pre_judicial_corrigido": v1, "juros_pre_judiciais_trd": juros_pre,
            "valor_no_marco_selic": v2, "valor_corrigido_ipca": v3, "juros_taxa_legal": juros3}
    return v3 + juros3 + juros_pre, out, comp, \
        ("valor_final = valor x fator_IPCA-E x (1 + pct_Selic/100) x fator_IPCA x (1 + pct_taxa_legal/100)"
         " + valor x fator_IPCA-E x pct_TRD/100"
         + (f" (pct_TRD = {q6(p_trd)})" if d0 < fim_pre else ""))


EXECUTORES = {
    "civil-cc406": regime_civil_cc406,
    "selic-integral-privado": regime_selic_privado,
    "fazenda-ec113": regime_fazenda_ec113,
    "fazenda-requisitorio-ec136": regime_ec136,
    "trabalhista-adc58": regime_trabalhista,
}


# ---------------------------------------------------------------- entrada

def normaliza(bruto):
    if not isinstance(bruto, dict):
        raise EntradaInvalida("a entrada deve ser um objeto JSON")
    extras = [k for k in bruto if k not in CAMPOS and not k.startswith("_")]
    if extras:
        raise EntradaInvalida(f"campos desconhecidos: {', '.join(sorted(extras))}")
    for obrig in ("valor", "data_inicial", "data_final", "regime"):
        if bruto.get(obrig) is None:
            raise EntradaInvalida(f"campo obrigatório ausente ou nulo: {obrig}")
    if bruto["regime"] not in REGIMES:
        raise EntradaInvalida(f"regime desconhecido '{bruto['regime']}'; use um de: {', '.join(REGIMES)}")
    e = {"regime": bruto["regime"], "valor": _dec("valor", bruto["valor"])}
    for campo in ("data_inicial", "data_final", "data_citacao", "data_expedicao", "data_ajuizamento"):
        if bruto.get(campo) is not None:
            e[campo] = _data(campo, bruto[campo])
    if e["data_final"] < e["data_inicial"]:
        raise EntradaInvalida("data_final anterior a data_inicial")
    acum = bruto.get("acumulacao_selic", "simples")
    if acum not in ("simples", "composta"):
        raise EntradaInvalida("acumulacao_selic: use 'simples' ou 'composta'")
    e["acumulacao_selic"] = acum
    if "ente" in bruto:
        if bruto["ente"] not in INICIO_EC136:
            raise EntradaInvalida("ente: use federal, estadual ou municipal")
        e["ente"] = bruto["ente"]
    nt = bruto.get("natureza_tributaria", False)
    if not isinstance(nt, bool):
        raise EntradaInvalida("natureza_tributaria: esperado true ou false")
    nat = bruto.get("natureza")
    if nat is not None:
        if nat not in NATUREZAS:
            raise EntradaInvalida(f"natureza: use um de {', '.join(NATUREZAS)}")
        if nt and nat != "tributaria":
            raise EntradaInvalida("natureza_tributaria true contradiz natureza '%s'" % nat)
        e["natureza"] = nat
        nt = nt or nat == "tributaria"
    e["natureza_tributaria"] = nt
    if bruto.get("taxa_titulo") is not None:
        if bruto["regime"] != "civil-cc406":
            raise EntradaInvalida("taxa_titulo só se aplica ao regime civil-cc406")
        e["taxa_titulo"] = _dec("taxa_titulo", bruto["taxa_titulo"])
    if bruto.get("valor_juros") is not None:
        e["valor_juros"] = _dec("valor_juros", bruto["valor_juros"])
    if bruto.get("valor_juros_selic") is not None:
        if bruto["regime"] != "fazenda-requisitorio-ec136":
            raise EntradaInvalida("valor_juros_selic só se aplica ao regime fazenda-requisitorio-ec136")
        e["valor_juros_selic"] = _dec("valor_juros_selic", bruto["valor_juros_selic"])
    vc = bruto.get("valor_consolidado_12_2021")
    jc = bruto.get("juros_consolidados_12_2021")
    if jc is not None and vc is None:
        raise EntradaInvalida("juros_consolidados_12_2021 exige valor_consolidado_12_2021")
    if vc is not None:
        if isinstance(vc, dict):
            if "principal" not in vc:
                raise EntradaInvalida("valor_consolidado_12_2021: falta 'principal'")
            if jc is not None and vc.get("juros") is not None:
                raise EntradaInvalida("juros consolidados informados duas vezes: use só "
                                      "juros_consolidados_12_2021")
            juros_c = vc.get("juros") if vc.get("juros") is not None else jc
            e["valor_consolidado_12_2021"] = (
                _dec("valor_consolidado_12_2021.principal", vc["principal"]),
                _dec("juros_consolidados_12_2021", juros_c if juros_c is not None else "0"),
            )
            if juros_c is None:
                e["_consolidado_sem_separacao"] = True
        else:
            e["valor_consolidado_12_2021"] = (
                _dec("valor_consolidado_12_2021", vc),
                _dec("juros_consolidados_12_2021", jc) if jc is not None else ZERO,
            )
            if jc is None:
                e["_consolidado_sem_separacao"] = True
    pg = bruto.get("periodo_graca")
    if pg is not None:
        if not isinstance(pg, dict) or "inicio" not in pg or "fim" not in pg:
            raise EntradaInvalida("periodo_graca: esperado {\"inicio\": AAAA-MM-DD, \"fim\": AAAA-MM-DD}")
        gi, gf = _data("periodo_graca.inicio", pg["inicio"]), _data("periodo_graca.fim", pg["fim"])
        if gf < gi:
            raise EntradaInvalida("periodo_graca: fim anterior ao início")
        e["periodo_graca"] = (mes(gi), mes(gf))
    return e


def eco(e):
    out = {}
    for k, v in e.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dt.date):
            out[k] = v.isoformat()
        elif isinstance(v, Decimal):
            out[k] = str(v)
        elif k == "valor_consolidado_12_2021":
            out[k] = {"principal": str(v[0]), "juros": str(v[1])}
        elif k == "periodo_graca":
            out[k] = {"inicio": mes_txt(v[0]), "fim": mes_txt(v[1])}
        else:
            out[k] = v
    return out


def calcular(bruto, pasta_indices=DIR_INDICES_PADRAO):
    """Devolve (codigo_de_saida, dict_de_saida)."""
    try:
        e = normaliza(bruto)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err)}
    cache, faltas, alertas = Cache(pasta_indices), Faltas(), []
    try:
        valor_final, fatias_, comp, formula = EXECUTORES[e["regime"]](e, cache, faltas, alertas)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err)}
    if e.get("_consolidado_sem_separacao"):
        alertas.append(
            "valor_consolidado_12_2021 veio sem separar principal e juros: tudo tratado como "
            "principal e 'Juros até 12/2021' = 0 (a Nota 5 c do item 4.2.1.1 separa as duas parcelas)."
        )
    if e["acumulacao_selic"] == "composta":
        alertas.append(
            "[ATENÇÃO] Selic acumulada de forma COMPOSTA por escolha explícita; a regra é a soma "
            "simples (Manual CJF ed. jul./2026, item 4.2.1.1, Nota 4 a)."
        )
    saida = {
        "versao": VERSAO,
        "regime": e["regime"],
        "entrada": eco(e),
        "valor_final": None,
        "acumulacao_selic": e["acumulacao_selic"],
        "fatias": fatias_,
        "componentes": {},
        "fonte_indice": cache.usados,
        "alertas": alertas,
        "formula_aberta": None,
    }
    if valor_final is None and not faltas:
        # Rede de segurança: executor sem número e sem falta registrada. Nunca exit 1 sem JSON;
        # o marcador MOTOR_SEM_VALOR é falha de teste (tests/test_calc_atualizacao.py).
        faltas.add("MOTOR_SEM_VALOR", mes(e["data_final"]),
                   "o motor não chegou a um número nem registrou o termo faltante; calcule pela fonte "
                   "oficial e reporte o caso")
    if faltas:
        saida["formula_aberta"] = {
            "expressao": formula,
            "faltando": faltas.lista(),
            "instrucao": "Número não calculado: preencha os termos faltantes pela fonte oficial "
                         "ou pelos critérios do título. O script nunca estima índice.",
        }
        return EXIT_FORA_DO_CACHE, saida
    saida["valor_final"] = q2(valor_final)
    saida["componentes"] = {k: q2(v) for k, v in comp.items()}
    return EXIT_OK, saida


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Engine A: atualização de débito judicial por regime "
                    f"({', '.join(REGIMES)}). Entrada JSON por --entrada ou stdin.")
    ap.add_argument("--entrada", help="arquivo JSON de entrada (sem ele, lê o stdin)")
    ap.add_argument("--indices-dir", default=str(DIR_INDICES_PADRAO),
                    help="pasta do cache de índices (padrão: ../data/indices; uso em testes)")
    args = ap.parse_args(argv)
    try:
        texto = Path(args.entrada).read_text(encoding="utf-8") if args.entrada else sys.stdin.read()
        bruto = json.loads(texto)
    except (OSError, json.JSONDecodeError) as err:
        codigo, saida = EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": f"JSON ilegível: {err}"}
    else:
        codigo, saida = calcular(bruto, args.indices_dir)
    json.dump(saida, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if codigo == EXIT_ENTRADA:
        print(f"entrada inválida: {saida['detalhe']}", file=sys.stderr)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
