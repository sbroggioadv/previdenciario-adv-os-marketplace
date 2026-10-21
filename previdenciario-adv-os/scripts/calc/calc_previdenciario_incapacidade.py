#!/usr/bin/env python3
"""calc_previdenciario_incapacidade.py — RMI dos benefícios por incapacidade e do auxílio-acidente.

Conta a renda mensal inicial do auxílio por incapacidade temporária, da
aposentadoria por incapacidade permanente (com o acréscimo de 25%) e do
auxílio-acidente, e a DIB do auxílio temporário. Conta aberta e lista de
CAMPOS em context/calculo-incapacidade.md.

USO:
    python3 calc_previdenciario_incapacidade.py --entrada caso.json
    echo '{...}' | python3 calc_previdenciario_incapacidade.py
    python3 calc_previdenciario_incapacidade.py --versao

Saída: JSON no stdout. Exit 0 = calculado; 2 = entrada inválida; 3 = falta
dado ou tabela (devolve a fórmula aberta, nunca estima).

Só biblioteca padrão, Python 3.9+, sem rede. As tabelas ficam em
../data/ relativo a este arquivo (CLAUDE_PLUGIN_ROOT chega vazio no Cowork).
Carência e qualidade de segurado são de calc_previdenciario_cnis.py: aqui
só ecoam em alerta. Nunca chamado por hook.
"""

import argparse
import datetime as dt
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

VERSAO = "2.0.2"
NOME = "calc_previdenciario_incapacidade"
EXIT_OK, EXIT_ENTRADA, EXIT_FALTA = 0, 2, 3

DIR_DADOS = Path(__file__).resolve().parent.parent / "data"
ARQ_SALARIO_MINIMO = DIR_DADOS / "salario-minimo.json"
ARQ_TETO = DIR_DADOS / "teto-rgps.json"

EC103 = dt.date(2019, 11, 13)            # publicação da EC 103/2019
MARCO_9876 = dt.date(1999, 11, 29)       # publicação da Lei 9.876/1999 (IN 128, art. 221)
MARCO_29_10 = dt.date(2015, 3, 1)        # IN 128, art. 233, I, "b": pelo fato gerador, não pela DIB
CENTAVO = Decimal("0.01")

ESPECIES = ("temporaria", "permanente", "auxilio-acidente")
SEXOS = ("M", "F")
CARENCIAS = ("sim", "nao", "indeterminada", "dispensada")
QUALIDADES = ("mantida", "perdida", "indeterminada")

# Contrato de entrada (context/calculo-incapacidade.md, seção 5). O teste de
# paridade compara este dicionário com o bloco ```campos``` das skills.
CAMPOS = {
    "especie": {"tipo": "enum", "obrigatorio": "sim", "valores": list(ESPECIES)},
    "acidentaria": {"tipo": "bool", "obrigatorio": "sim", "valores": None},
    "sexo": {"tipo": "enum", "obrigatorio": "sim", "valores": list(SEXOS)},
    "media_100": {"tipo": "decimal", "obrigatorio": "sim", "valores": None},
    "media_12_ultimos": {"tipo": "decimal", "obrigatorio": "especie=temporaria", "valores": None},
    "tempo_contribuicao_anos": {"tipo": "inteiro", "obrigatorio": "especie=permanente e acidentaria=false",
                                "valores": None},
    "dii": {"tipo": "data", "obrigatorio": "especie=permanente, ou especie=temporaria e empregado=false",
            "valores": None},
    "dib": {"tipo": "data", "obrigatorio": "especie=permanente ou auxilio-acidente, salvo teto e salario_minimo "
                                           "informados", "valores": None},
    "dat": {"tipo": "data", "obrigatorio": "especie=temporaria", "valores": None},
    "der": {"tipo": "data", "obrigatorio": "especie=temporaria", "valores": None},
    "empregado": {"tipo": "bool", "obrigatorio": "especie=temporaria", "valores": None},
    "assistencia_permanente": {"tipo": "bool", "obrigatorio": "nao", "valores": None},
    "salario_minimo": {"tipo": "decimal", "obrigatorio": "nao", "valores": None},
    "teto": {"tipo": "decimal", "obrigatorio": "nao", "valores": None},
    "carencia": {"tipo": "enum", "obrigatorio": "nao", "valores": list(CARENCIAS)},
    "qualidade_segurado": {"tipo": "enum", "obrigatorio": "nao", "valores": list(QUALIDADES)},
}

AVISO_FIXO = ("Conferir o resultado contra a carta de concessão e o CNIS antes do protocolo. "
              "Carência e qualidade de segurado não são decididas por este script.")

# Cobertura temporal (brief r13; revisão r12, BLOCKER 1: auxílio-acidente da MP 905/2019 saía em 50% do SB). Para cada
# regra, os intervalos de data em que a redação implementada é a vigente, com a fonte de cada borda. Fora de segmento
# 'coberto', o script NÃO calcula aquela regra: exit 3 com a regra histórica e a fonte. 'ramo' = o texto da regra já
# sai pelo ramo existente de _calcula (antes_9876, historico); 'linha' = texto acrescentado à fórmula aberta. As bordas
# saem da varredura das notas "Redação dada", "Incluído" e "Revogado" dos artigos aplicados (relatório da lane, r13).
#   temporaria, permanente: marco = fato gerador (DII).
#   temporaria-dib: marco = DII; sem DII, o período da DAT à DER.
#   auxilio-acidente: marco = da DII (ou da DIB) à DIB; sem DIB, sem limite superior (a consolidação das lesões, fato
#   gerador, fica entre as duas — Lei 8.213, art. 86, caput e §2º).
_LEI_9032 = "Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171)"
_LEI_9876 = "Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md)"
_EC_103 = "EC 103/2019, publicada em 13/11/2019 (IN 128, art. 233, II, \"a\" e \"b\")"
_MP_905 = ("MP 905/2019, de 11/11/2019, revogada pela MP 955/2020, de 20/04/2020 (redação riscada com \"Vigência "
           "encerrada\" em context/lei/lei-8213-1991.md:1942; as datas de publicação não estão capturadas em "
           "context/lei/ — [VERIFICAR]: a janela vai do dia da MP 905 ao da MP 955, inclusive, a maior possível)")
COBERTURA = {
    "temporaria": [
        {"de": None, "ate": dt.date(1995, 4, 28), "coberto": False, "ramo": "antes_9876",
         "fonte_ate": _LEI_9032,
         "regra": "art. 61, redação original: 80% do SB + 1% por grupo de 12 contribuições, até 92% (92% no acidente do "
                  "trabalho); SB pelos últimos 36 salários em até 48 meses",
         "linha": "[VERIFICAR] fato gerador até 28/04/1995 (antes da Lei 9.032): percentual = 80% + 1% por grupo de 12 "
                  "contribuições, até 92%, ou 92% no acidente do trabalho (Lei 8.213, art. 61, redação original — "
                  "context/lei/lei-8213-1991.md:1501-1505)"},
        {"de": dt.date(1995, 4, 29), "ate": dt.date(1999, 11, 28), "coberto": False, "ramo": "antes_9876",
         "fonte_de": _LEI_9032, "fonte_ate": _LEI_9876,
         "regra": "91% (art. 61, Lei 9.032/1995); SB pelos últimos 36 salários em até 48 meses (IN 128, art. 221, II, \"b\")",
         "linha": None},
        {"de": dt.date(1999, 11, 29), "ate": dt.date(2015, 2, 28), "coberto": False, "ramo": "historico",
         "fonte_de": _LEI_9876, "fonte_ate": "MP 664/2014, vigente desde 01/03/2015 (IN 128, art. 233, I, \"b\")",
         "regra": "91% da média dos 80% maiores (art. 29, II), sem o limite do art. 29, §10", "linha": None},
        {"de": dt.date(2015, 3, 1), "ate": dt.date(2019, 11, 13), "coberto": False, "ramo": "historico",
         "fonte_de": "IN 128, art. 233, I, \"b\"", "fonte_ate": _EC_103,
         "regra": "91% da média dos 80% maiores, limitado pelo art. 29, §10 (redações da MP 664/2014 e da Lei 13.135/2015, "
                  "de mesmo teor — lei-8213-1991.md:841-843)", "linha": None},
        {"de": dt.date(2019, 11, 14), "ate": None, "coberto": True, "fonte_de": _EC_103,
         "regra": "91% (art. 61) da média de 100% desde 07/1994 (EC 103, art. 26; Decreto 3.048, art. 32, redação do "
                  "Decreto 10.410/2020), limitado pelo art. 29, §10"},
    ],
    "temporaria-dib": [
        {"de": None, "ate": dt.date(1999, 11, 28), "coberto": False, "fonte_ate": _LEI_9876,
         "regra": "art. 60, redação original: empregado e empresário do 16º dia, demais da DII",
         "linha": "[VERIFICAR] DIB pela redação original do art. 60 (fato gerador até 28/11/1999): ao empregado e ao "
                  "empresário, do 16º dia do afastamento; aos demais, da DII; requerido depois de 30 dias de "
                  "afastamento, da DER (Lei 8.213, art. 60, caput e §1º — context/lei/lei-8213-1991.md:1403 e 1413)"},
        {"de": dt.date(1999, 11, 29), "ate": dt.date(2015, 2, 28), "coberto": True, "fonte_de": _LEI_9876,
         "fonte_ate": "MP 664/2014, vigente desde 01/03/2015 (IN 128, art. 375 — in-128-2022-inss.md:3383)",
         "regra": "art. 60, redação da Lei 9.876/1999 (lei-8213-1991.md:1411-1413)"},
        {"de": dt.date(2015, 3, 1), "ate": dt.date(2015, 6, 18), "coberto": False,
         "fonte_de": "MP 664/2014, vigente desde 01/03/2015 (IN 128, art. 375 — in-128-2022-inss.md:3383)",
         "fonte_ate": "Lei 13.135, de 18/06/2015 (IN 128, art. 375): o dia 18 entra na janela, as duas leituras valem",
         "regra": "art. 60 na redação da MP 664/2014",
         "linha": "[VERIFICAR] DIB pela MP 664/2014 (fato gerador de 01/03/2015 a 18/06/2015): ao empregado, do 31º dia do "
                  "afastamento, ou da DER se entre o afastamento e a DER decorrerem mais de 45 dias; aos demais, da DII, ou "
                  "da DER se entre elas decorrerem mais de 30 dias (Lei 8.213, art. 60, I e II, redação da MP 664/2014 — "
                  "context/lei/lei-8213-1991.md:1405-1409); regra fora do cálculo automático"},
        {"de": dt.date(2015, 6, 19), "ate": None, "coberto": True,
         "fonte_de": "Lei 13.135/2015 (IN 128, art. 375): volta a redação da Lei 9.876/1999",
         "regra": "art. 60, caput e §1º, redação da Lei 9.876/1999; IN 128, art. 336"},
    ],
    "permanente": [
        {"de": None, "ate": dt.date(1995, 4, 28), "coberto": False, "ramo": "antes_9876", "fonte_ate": _LEI_9032,
         "regra": "art. 44, redação original: 80% do SB + 1% por grupo de 12 contribuições, até 100%",
         "linha": "[VERIFICAR] fato gerador até 28/04/1995 (antes da Lei 9.032): percentual = 80% + 1% por grupo de 12 "
                  "contribuições, até 100%, ou 100% no acidente do trabalho (Lei 8.213, art. 44, redação original — "
                  "context/lei/lei-8213-1991.md:1199-1203)"},
        {"de": dt.date(1995, 4, 29), "ate": dt.date(1999, 11, 28), "coberto": False, "ramo": "antes_9876",
         "fonte_de": _LEI_9032, "fonte_ate": _LEI_9876,
         "regra": "100% (art. 44, Lei 9.032/1995) dos últimos 36 salários em até 48 meses", "linha": None},
        {"de": dt.date(1999, 11, 29), "ate": dt.date(2019, 11, 13), "coberto": False, "ramo": "historico",
         "fonte_de": _LEI_9876, "fonte_ate": _EC_103,
         "regra": "100% da média dos 80% maiores (arts. 29, II, e 44)", "linha": None},
        {"de": dt.date(2019, 11, 14), "ate": None, "coberto": True, "fonte_de": _EC_103,
         "regra": "EC 103, art. 26, §§2º, III, 3º, II, e 5º, sobre a média de 100% desde 07/1994"},
    ],
    "auxilio-acidente": [
        {"de": None, "ate": dt.date(1995, 4, 28), "coberto": False, "ramo": "antes_9876", "fonte_ate": _LEI_9032,
         "regra": "art. 86, §1º, redação original: 30%, 40% ou 60% do salário de contribuição do dia do acidente",
         "linha": "[VERIFICAR] fato gerador até 28/04/1995 (antes da Lei 9.032): 30%, 40% ou 60% do salário de "
                  "contribuição vigente no dia do acidente, conforme a redução, não inferior a esse percentual do SB "
                  "(Lei 8.213, art. 86, §1º, redação original — context/lei/lei-8213-1991.md:1936)"},
        {"de": dt.date(1995, 4, 29), "ate": dt.date(1999, 11, 28), "coberto": False, "ramo": "antes_9876",
         "fonte_de": _LEI_9032, "fonte_ate": _LEI_9876,
         "regra": "50% do SB (art. 86, §1º, Leis 9.032/1995 e 9.528/1997) dos últimos 36 salários", "linha": None},
        {"de": dt.date(1999, 11, 29), "ate": dt.date(2019, 11, 10), "coberto": False, "ramo": "historico",
         "fonte_de": _LEI_9876, "fonte_ate": _MP_905,
         "regra": "50% do SB pela média dos 80% maiores (art. 86, §1º, Lei 9.528/1997)", "linha": None},
        {"de": dt.date(2019, 11, 11), "ate": dt.date(2020, 4, 20), "coberto": False, "fonte_de": _MP_905,
         "fonte_ate": _MP_905,
         "regra": "art. 86, §1º, redação da MP 905/2019: 50% da aposentadoria por invalidez a que o segurado teria direito",
         "linha": "[VERIFICAR] fato gerador (consolidação das lesões) de 11/11/2019 a 20/04/2020, na vigência da MP "
                  "905/2019: RMI = 50% da aposentadoria por invalidez a que o segurado teria direito — o SB × o "
                  "coeficiente da incapacidade permanente na data (EC 103, art. 26: 60% + 2% por ano acima de 20 anos, "
                  "homem, ou 15, mulher; 100% se acidentária) — e não 50% do SB (Lei 8.213, art. 86, §1º, redação da MP "
                  "905/2019 — context/lei/lei-8213-1991.md:1942); regra fora do cálculo automático, faça a conta à mão"},
        {"de": dt.date(2020, 4, 21), "ate": None, "coberto": True, "fonte_de": _MP_905,
         "regra": "50% do SB (art. 86, §1º, redação da Lei 9.528/1997, restabelecida pela MP 955/2020; IN 128, art. 233, "
                  "X), SB pela média de 100% desde 07/1994"},
    ],
}


def fora_da_cobertura(chave, ini, fim):
    """Segmentos NÃO cobertos de COBERTURA[chave] que o intervalo [ini, fim] alcança (fim None = sem limite)."""
    return [s for s in COBERTURA[chave] if not s["coberto"]
            and (s["ate"] is None or ini <= s["ate"]) and (fim is None or s["de"] is None or s["de"] <= fim)]


def alcanca_coberto(chave, ini, fim):
    return any(s["coberto"] and (s["ate"] is None or ini <= s["ate"]) and (fim is None or s["de"] is None or s["de"] <= fim)
               for s in COBERTURA[chave])


def intervalo_do_marco(e, chave):
    """(início, fim) do marco da regra na entrada, ou None se a entrada não o traz (o ramo sem_fato cuida)."""
    if chave == "auxilio-acidente":
        ini = e["dii"] or e["dib"]
        return None if ini is None else (ini, e["dib"])
    if chave == "temporaria-dib" and e["dii"] is None:
        return e["dat"], e["der"]
    return None if e["dii"] is None else (e["dii"], e["dii"])


class EntradaInvalida(Exception):
    pass


class FaltaDado(Exception):
    def __init__(self, motivo, faltantes):
        super().__init__(motivo)
        self.faltantes = faltantes


# ------------------------------------------------------------------ entrada

# Até 12 dígitos inteiros e 8 decimais: cabe na precisão de 28 dígitos do Decimal, e o quantize ao
# centavo nunca chega a decimal.InvalidOperation (que sairia em exit 1, sem JSON).
# Só algarismos ASCII e fullmatch: \d aceitaria dígitos de outras escritas e "$" um "\n" no fim.
RE_DECIMAL = re.compile(r"-?[0-9]{1,12}(\.[0-9]{1,8})?")
RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _mostra(valor):
    """Valor recebido, curto e só ASCII, para mensagem de erro (nunca falha: entrada pode ser qualquer coisa)."""
    try:
        texto = ascii(valor)
    except Exception:                      # aninhamento profundo, objeto exótico
        texto = f"<{type(valor).__name__}>"
    return texto if len(texto) <= 60 else texto[:57] + "..."


def _decimal(campo, valor):
    if not isinstance(valor, str) or not RE_DECIMAL.fullmatch(valor):
        raise EntradaInvalida(f"{campo}: esperado decimal como texto com ponto (ex.: \"1900.00\"), com no "
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
    if not dt.date(1960, 1, 1) <= d <= dt.date(2100, 12, 31):
        raise EntradaInvalida(f"{campo}: fora do intervalo 1960–2100")
    return d


def _bool(campo, valor):
    if not isinstance(valor, bool):
        raise EntradaInvalida(f"{campo}: esperado true ou false")
    return valor


def _inteiro(campo, valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or not 0 <= valor <= 80:
        raise EntradaInvalida(f"{campo}: inteiro entre 0 e 80")
    return valor


def _enum(campo, valor, opcoes):
    if valor not in opcoes:
        raise EntradaInvalida(f"{campo}: {_mostra(valor)} fora de {list(opcoes)}")
    return valor


CONVERSORES = {"decimal": _decimal, "data": _data, "bool": _bool, "inteiro": _inteiro}


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
            continue
        if spec["tipo"] == "enum":
            out[campo] = _enum(campo, v, spec["valores"])
        else:
            out[campo] = CONVERSORES[spec["tipo"]](campo, v)

    for campo in ("especie", "acidentaria", "sexo", "media_100"):
        if out[campo] is None:
            raise EntradaInvalida(f"{campo}: obrigatório")
    esp = out["especie"]
    if out["dib"] is not None:
        if esp == "temporaria":
            raise EntradaInvalida("dib: na temporária a DIB é calculada pelo script a partir de DAT, DER e DII "
                                  "(Lei 8.213, art. 60; IN 128, art. 336)")
        if out["dii"] is not None and out["dib"] < out["dii"]:
            raise EntradaInvalida("dib: anterior à dii (a DIB não antecede o fato gerador — Lei 8.213, arts. 43 e 86, "
                                  "§2º)")
    if esp == "temporaria":
        for campo in ("media_12_ultimos", "dat", "der", "empregado"):
            if out[campo] is None:
                raise EntradaInvalida(f"{campo}: obrigatório quando especie = temporaria")
        if out["der"] < out["dat"]:
            raise EntradaInvalida("der: anterior à dat")
        if out["empregado"] is False and out["dii"] is None:
            raise EntradaInvalida(
                "dii: obrigatória na temporária do segurado que não é empregado — a DIB é a DII "
                "(Lei 8.213, art. 60, caput; IN 128, art. 336, II); a DAT não a substitui")
    if esp == "permanente":
        if out["dii"] is None:
            raise EntradaInvalida("dii: obrigatória quando especie = permanente (fato gerador)")
        if not out["acidentaria"] and out["tempo_contribuicao_anos"] is None:
            raise EntradaInvalida(
                "tempo_contribuicao_anos: obrigatório na permanente previdenciária (coeficiente da EC 103, art. 26)")
    if out["assistencia_permanente"] and esp != "permanente":
        raise EntradaInvalida(
            "assistencia_permanente: o acréscimo de 25% só existe na aposentadoria por incapacidade "
            "permanente (Lei 8.213, art. 45)")
    if out["assistencia_permanente"] is None:
        out["assistencia_permanente"] = False
    # Limites contraditórios são entrada inválida, não cálculo (revisão r6, MAJOR 4): teto 100,00 com salário mínimo
    # 1.621,00 saía em exit 0 com RMI 100,00.
    for campo in ("teto", "salario_minimo"):
        if out[campo] is not None and out[campo] == 0:
            raise EntradaInvalida(f"{campo}: tem de ser maior que zero")
    contraditorios(out["salario_minimo"], out["teto"])
    return out


def contraditorios(sm, teto, origem="informados"):
    if sm is not None and teto is not None and sm > teto:
        raise EntradaInvalida(f"salario_minimo {sm} acima do teto {teto} ({origem}): limites contraditórios (o piso do "
                              "salário de benefício não supera o teto — Lei 8.213, art. 29, §2º)")


# ------------------------------------------------------------------ tabelas

def _consulta_tabela(arq, data, chave):
    """(valor Decimal ou None, fonte) da linha que contém a data; None fora do intervalo ou com null."""
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


def confere_limite_informado(e, dib):
    """Com a DIB fechada e coberta pela tabela capturada, teto ou salário mínimo informado diferente do vigente nela
    contraria a lei (Lei 8.213, art. 29, §2º; CF, art. 201, §2º): exit 2. Sem DIB fechada, ou fora da tabela, o
    informado é aceito — é para isso que o campo existe."""
    if dib is None:
        return
    for arq, campo, chave, rotulo in ((ARQ_TETO, "teto", "teto", "teto do RGPS"),
                                      (ARQ_SALARIO_MINIMO, "salario_minimo", "valor", "salário mínimo")):
        vigente = _consulta_tabela(arq, dib, chave)[0] if e[campo] is not None else None
        if vigente is not None and vigente != e[campo]:
            raise EntradaInvalida(f"{campo} {e[campo]} não é o {rotulo} vigente na DIB {br(dib)} ({vigente}, "
                                  f"scripts/data/{arq.name}): confira o valor informado ou a data")


def parametro(entrada, campo, arq, chave, data, rotulo, faltantes):
    if entrada[campo] is not None:
        return entrada[campo], {"origem": "informado na entrada"}
    if data is None:
        return None, None
    valor, fonte = _consulta_tabela(arq, data, chave)
    if valor is None:
        faltantes.append(f"{rotulo} de {data.year}: fora de scripts/data/{Path(arq).name} (valor não "
                         f"verificado em context/lei/); informe '{campo}'")
    return valor, fonte


def final_rmi(rmi, esp, sm, teto):
    """RMI depois do piso (exceto auxílio-acidente) e do teto, sem efeitos colaterais."""
    if esp != "auxilio-acidente" and rmi < sm:
        rmi = sm
    return min(rmi, teto)


def q(v):
    return v.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def br(d):
    return d.strftime("%d/%m/%Y")


# ------------------------------------------------------------------ conta

def calcula_dib(e, regras, memoria, alertas):
    """(DIB, DIB mínima, fundamento). Sem DII (empregado), a DIB fica em aberto: é o 16º dia ou a DER, salvo DII
    posterior (IN 128, art. 336, I), e a DII não se presume."""
    dat, der, dii = e["dat"], e["der"], e["dii"]
    dias = (der - dat).days + 1                     # contagem inclusiva da DAT à DER
    memoria.append(f"DAT {br(dat)}; DER {br(der)}; {dias} dia(s) de afastamento até a DER (contagem inclusiva)")
    if e["empregado"]:
        d16 = dat + dt.timedelta(days=15)
        memoria.append(f"16º dia do afastamento = {br(d16)}")
        if dias <= 30:
            dib, fund = d16, "Lei 8.213, art. 60, caput; IN 128, art. 336, I, \"a\""
            if dii and dii > d16:
                dib, fund = dii, "IN 128, art. 336, I, \"a\": DII posterior ao 16º dia"
        else:
            dib, fund = der, "Lei 8.213, art. 60 §1º; IN 128, art. 336, I, \"b\""
            if dii and dii > der:
                dib, fund = dii, "IN 128, art. 336, I, \"b\": DII posterior à DER"
        if dii is None:
            memoria.append(f"sem DII: DIB = {br(dib)} ({fund}) ou a DII, se posterior — [VERIFICAR], a DII não se "
                           "presume")
            regras.append(fund)
            return None, dib, fund
    else:
        if dias <= 30:
            dib, fund = dii, "Lei 8.213, art. 60, caput; IN 128, art. 336, II, \"a\""
        else:
            dib, fund = der, "Lei 8.213, art. 60 §1º; IN 128, art. 336, II, \"b\""
            if dii > der:
                dib, fund = dii, "IN 128, art. 336, II, \"b\": DII posterior à DER"
        if dii < dat:
            alertas.append("[VERIFICAR] DII anterior à DAT: confira o marco de 30 dias (DAT ou cessação das "
                           "contribuições, IN 128, art. 336, II).")
    memoria.append(f"DIB = {br(dib)} ({fund})")
    regras.append(fund)
    return dib, dib, fund


PISO_SB = "piso do SB, Lei 8.213 art. 29 §2º"


def conta(media, pct, m12, sm, teto, esp, memoria):
    """RMI e limitador. Ordem: SB entre o salário mínimo e o teto; percentual; art. 29 §10 (m12, quando incide);
    piso da renda (exceto auxílio-acidente); teto. O auxílio-acidente não tem piso de RENDA, mas o SALÁRIO DE
    BENEFÍCIO sobre o qual incidem os 50% tem (Lei 8.213, art. 29, §2º; Decreto 3.048, art. 32, §3º)."""
    limitador = "nenhum"
    sb = media
    if sb > teto:
        memoria.append(f"SB {sb} limitado ao teto {teto} (EC 103, art. 26, §1º)")
        sb, limitador = teto, "teto"
    elif sb < sm:
        memoria.append(f"SB {sb} < salário mínimo {sm} → SB = {sm} (Lei 8.213, art. 29, §2º; Decreto 3.048, "
                       "art. 32, §3º)")
        sb, limitador = sm, PISO_SB
    rmi = q(sb * pct)
    memoria.append(f"RMI bruta = {sb} × {pct} = {rmi}")
    if m12 is not None:
        if rmi > m12:
            memoria.append(f"{rmi} > média dos 12 últimos {m12} → limita a {m12} (Lei 8.213, art. 29, §10)")
            rmi, limitador = q(m12), "art. 29 §10"
        else:
            memoria.append(f"{rmi} ≤ média dos 12 últimos {m12} → não limita")
    if esp != "auxilio-acidente":
        if rmi < sm:
            memoria.append(f"{rmi} < salário mínimo {sm} → piso (CF, art. 201, §2º)")
            rmi, limitador = sm, "piso, CF art. 201 §2º"
        else:
            memoria.append(f"{rmi} ≥ salário mínimo {sm} → piso não atua")
    else:
        memoria.append("auxílio-acidente: sem piso da renda (Decreto 3.048, art. 42, parágrafo único)")
    if rmi > teto:
        memoria.append(f"{rmi} > teto {teto} → teto")
        rmi, limitador = teto, "teto"
    return rmi, limitador


BASE_80 = "média dos 80% maiores salários de contribuição (Lei 8.213, art. 29, II; IN 128, art. 229)"
# Fato gerador antes da Lei 9.876/1999: fora do cálculo automático (brief r7; revisão r6, BLOCKER 1). Só a regra.
BASE_36 = ("média dos últimos 36 salários de contribuição, apurados em período não superior a 48 meses imediatamente "
           "anteriores (IN 128, art. 221, II, \"b\"; Lei 8.213, art. 29, redação original, revogada pela Lei 9.876/1999)")
REGRA_36 = (f"[VERIFICAR] regra anterior à Lei 9.876/1999, fora do cálculo automático: SB = {BASE_36}, entre o salário "
            "mínimo e o teto da DIB; RMI = SB × percentual da espécie na legislação da data do fato gerador, conferido à "
            "mão; sem o limite do art. 29, §10 (fato gerador anterior a 01/03/2015)")


def calcular(bruto):
    try:
        e = normaliza(bruto)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}
    try:
        return _calcula(e)
    except OSError as err:             # tabela de scripts/data/ ausente ou ilegível: falta tabela, exit 3 (r8, MINOR 5)
        arquivo = Path(getattr(err, "filename", None) or str(err)).name
        # Contrato completo também aqui (revisão r9, MINOR 3): parametros_usados, regra, fonte e memoria.
        return EXIT_FALTA, {
            "versao": VERSAO, "script": NOME, "especie": e["especie"],
            "parametros_usados": {k: (str(v) if isinstance(v, (Decimal, dt.date)) else v) for k, v in e.items()},
            "regra": [], "fundamento": [], "fonte": {},
            "memoria": [f"cálculo interrompido: tabela {arquivo} ausente ou ilegível em scripts/data/"],
            "dados_faltantes": [f"tabela {arquivo} ausente ou ilegível em scripts/data/ ({type(err).__name__}): "
                                "reinstale o plugin; sem ela o piso e o teto da DIB não se conferem"],
            "formula_aberta": ("[VERIFICAR] RMI = salário de benefício (média, limitada ao teto e com o piso de um "
                               "salário mínimo da DIB — Lei 8.213, art. 29, §2º) × percentual da espécie, com os "
                               "limitadores na ordem do contexto e o acréscimo de 25% por último e sem teto (Lei "
                               "8.213, art. 45). Conta aberta em context/calculo-incapacidade.md."),
            "alertas": [AVISO_FIXO]}


def _calcula(e):

    esp, sexo, dii = e["especie"], e["sexo"], e["dii"]
    regras, memoria, alertas, fundamento, faltantes = [], [], [], [], []
    fonte = {}
    dib = dib_minima = fund_dib = None
    # Cobertura temporal (COBERTURA): segmentos fora dela que a entrada alcança, na regra do valor e na da DIB.
    marco = intervalo_do_marco(e, esp)
    fora = fora_da_cobertura(esp, *marco) if marco else []
    marco_dib = intervalo_do_marco(e, "temporaria-dib") if esp == "temporaria" else None
    fora_dib = fora_da_cobertura("temporaria-dib", *marco_dib) if marco_dib else []
    if esp == "temporaria" and fora_dib and dii is not None:
        # A redação vigente do art. 60 não vigia no fato gerador: a DIB não é calculada (nem os limites da DIB).
        dib_minima = data_ref = None
        fund_dib = "fora da cobertura temporal do art. 60 implementado (ver formula_aberta)"
        fundamento.append(f"DIB: {fund_dib}")
        memoria.append(f"DII {br(dii)}: a DIB segue a redação do art. 60 vigente nessa data, fora do cálculo automático")
    elif esp == "temporaria":
        dib, dib_minima, fund_dib = calcula_dib(e, regras, memoria, alertas)
        fundamento.append(f"DIB: {fund_dib}" + ("" if dib else " — [VERIFICAR] ou a DII, se posterior"))
        data_ref = dib_minima
    else:
        # Limites do salário de benefício na DATA DE INÍCIO DO BENEFÍCIO (Lei 8.213, art. 29, §2º). A DII decide o
        # regime (fato gerador), mas não é a DIB: na permanente e no auxílio-acidente a DIB é posterior a ela (Lei
        # 8.213, arts. 43 e 86, §2º) e pode cair em ano de outro piso ou teto. Sem dib, só fecha com os dois limites
        # informados (revisão r5, MAJOR 3).
        dib = data_ref = e["dib"]
        if dib is not None:
            fund_dib = "informada na entrada"
        if data_ref is None and (e["teto"] is None or e["salario_minimo"] is None):
            faltantes.append("dib: o piso e o teto do salário de benefício são os da data de início do benefício "
                             "(Lei 8.213, art. 29, §2º), que a DII não substitui (a DIB lhe é posterior — arts. 43 e "
                             "86, §2º); informe dib, ou teto e salario_minimo")
            memoria.append("sem 'dib': o teto e o salário mínimo vigentes na data da DIB (este, piso do salário de "
                           "benefício) têm de vir na entrada")

    teto, fonte_teto = parametro(e, "teto", ARQ_TETO, "teto", data_ref, "teto do RGPS", faltantes)
    # Em toda espécie, inclusive no auxílio-acidente: o salário mínimo é o piso do salário de benefício (Lei 8.213,
    # art. 29, §2º); no auxílio-acidente só não é piso da renda (Decreto 3.048, art. 42, parágrafo único).
    sm, fonte_sm = parametro(e, "salario_minimo", ARQ_SALARIO_MINIMO, "valor", data_ref, "salário mínimo", faltantes)
    fonte["salario_minimo"] = fonte_sm
    try:
        contraditorios(sm, teto, "um informado e o outro da tabela vigente na data da DIB")
        confere_limite_informado(e, dib)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}

    # Percentual da espécie
    if esp == "temporaria":
        pct = Decimal("0.91")
        fundamento.append("Lei 8.213, art. 61: 91% do salário de benefício")
        regras.append("Lei 8.213, art. 61; IN 128, art. 233, I, \"a\"")
    elif esp == "permanente":
        if e["acidentaria"]:
            pct = Decimal("1.00")
            fundamento.append("EC 103, art. 26, §3º, II: 100% (acidente do trabalho, doença profissional ou do trabalho)")
            regras.append("EC 103, art. 26, §3º, II; IN 128, art. 233, II, \"c\"")
            if dii <= EC103:
                regras[-1] = "Lei 8.213, art. 44; IN 128, art. 233, II, \"a\""
        elif dii <= EC103:
            pct = Decimal("1.00")
            fundamento.append("regra anterior à EC 103 (fato gerador até 13/11/2019): 100%")
            regras.append("Lei 8.213, art. 44; IN 128, art. 233, II, \"a\"")
            alertas.append("DII até 13/11/2019: regra anterior, 100% do salário de benefício (IN 128, art. 233, II, \"a\").")
        else:
            base = 20 if sexo == "M" else 15
            anos = e["tempo_contribuicao_anos"]
            excedente = max(0, anos - base)
            pct = Decimal("0.60") + Decimal("0.02") * excedente
            fundamento.append(f"EC 103, art. 26, §2º, III (e §5º para a mulher): 60% + 2% × {excedente} ano(s) "
                              f"acima de {base}")
            regras.append("EC 103, art. 26, §§2º, III, e 5º; IN 128, art. 233, II, \"b\"")
            memoria.append(f"coeficiente: 60% + 2% × ({anos} − {base}, mínimo 0) = {pct * 100:.0f}%")
            alertas.append("STF Tema 1.300: constitucional para incapacidade constatada após a EC 103 — o cálculo "
                           "do art. 26, §2º, III (fato gerador = DII, não a DER).")
        if not e["acidentaria"]:
            alertas.append("Acidente sem nexo com o trabalho não é acidentário: entra na regra de 60% + 2% "
                           "(EC 103, art. 26, §3º, II, só para acidente do trabalho e doenças profissional ou do trabalho).")
    else:
        pct = Decimal("0.50")
        fundamento.append("Lei 8.213, art. 86, §1º: 50% do salário de benefício")
        regras.append("Lei 8.213, art. 86, §1º")
        alertas.append("[VERIFICAR] Auxílio-acidente: vedada a acumulação com qualquer aposentadoria (Lei 8.213, "
                       "art. 86, §§1º e 2º); com outro benefício a acumulação é aceita aqui, mas origem da "
                       "incapacidade e reabertura (IN 128, art. 233, §7º) ficam para o advogado.")

    fonte["percentual"] = regras[-1] if esp != "temporaria" else "Lei 8.213, art. 61"
    if esp == "temporaria":
        carencia, fund_car = (0, "Lei 8.213, art. 26, II") if e["acidentaria"] else \
            (12, "Lei 8.213, art. 25, I")
    elif esp == "permanente":
        carencia, fund_car = (0, "Lei 8.213, art. 26, II") if e["acidentaria"] else \
            (12, "Lei 8.213, art. 25, I")
    else:
        carencia, fund_car = 0, "Lei 8.213, art. 26, I"
    if carencia:
        alertas.append("Carência de 12 contribuições (Lei 8.213, art. 25, I), dispensada em acidente de qualquer "
                       "natureza ou doença da lista (art. 26, II): a dispensa é marcada pelo advogado.")
    for campo, ruim, texto in (("carencia", ("nao", "indeterminada"), "carência"),
                               ("qualidade_segurado", ("perdida", "indeterminada"), "qualidade de segurado")):
        if e[campo] in ruim:
            alertas.append(f"[VERIFICAR] {texto} informada como '{e[campo]}' (calc_previdenciario_cnis.py): "
                           "o valor abaixo não decide o direito ao benefício.")

    parametros = {k: (str(v) if isinstance(v, (Decimal, dt.date)) else v) for k, v in e.items()}
    base_saida = {
        "versao": VERSAO,
        "script": NOME,
        "especie": esp,
        "parametros_usados": parametros,
        "carencia_exigida": carencia,
        "dib": dib.isoformat() if dib else None,
        "percentual": str(pct),
        "regra": regras,
        "fundamento": fundamento,
        "alertas": alertas,
        "memoria": memoria,
    }
    fonte["carencia_exigida"] = fund_car
    if dib:
        fonte["dib"] = fund_dib
    fonte["teto"] = fonte_teto

    # Fato gerador = DII. Até 13/11/2019 o salário de benefício é a média dos 80% maiores (Lei 8.213, art. 29, II;
    # IN 128, arts. 229 e 233), que a media_100 não é; sem DII o fato gerador não se presume (nem pela DAT).
    historico = dii is not None and dii <= EC103
    antes_9876 = any(d is not None and d < MARCO_9876 for d in (dii, e["dib"]))
    sem_fato = dii is None
    m12 = e["media_12_ultimos"] if esp == "temporaria" else None
    # Regime fora da cobertura que nenhum ramo abaixo descreve (ex.: MP 905/2019 no auxílio-acidente): falta dado.
    novos = [s for s in fora if s.get("ramo") is None]
    for s in novos:
        faltantes.append(f"fato gerador na vigência de regra que o script não implementa ({s['regra']}; borda: "
                         f"{s.get('fonte_de') or s.get('fonte_ate')}): fora da cobertura temporal, faça a conta à mão")
    if fora_dib and dii is not None:
        faltantes.append(f"DIB: fato gerador (DII {br(dii)}) fora da cobertura do art. 60 implementado ("
                         + "; ".join(s["regra"] for s in fora_dib) + ")")
    if (fora or fora_dib) and not faltantes and not historico:     # guarda: fora da cobertura nunca fecha
        faltantes.append("data fora da cobertura temporal do script (COBERTURA)")
    if faltantes or historico or sem_fato:
        sm_txt = str(sm) if sm is not None else "SM[ano]"
        teto_txt = str(teto) if teto is not None else "TETO[ano]"

        def ramo(base_txt, limite):
            passos = [f"SB = min(max({base_txt}, {sm_txt}), {teto_txt}) — Lei 8.213, art. 29, §2º",
                      f"RMI bruta = SB × {pct}"]
            if limite:
                passos.append(f"limite art. 29 §10: RMI = min(RMI bruta, {m12})")
            passos.append(f"piso: RMI = max(RMI, {sm_txt}) — CF, art. 201, §2º" if esp != "auxilio-acidente"
                          else "sem piso da renda (Decreto 3.048, art. 42, parágrafo único)")
            passos.append(f"teto: RMI = min(RMI, {teto_txt})")
            return passos

        formula = []
        if esp == "temporaria" and fora_dib and dii is not None:
            formula += [s["linha"] for s in fora_dib]
            formula.append("[VERIFICAR] piso e teto: os vigentes na data da DIB assim apurada (Lei 8.213, art. 29, §2º)")
        elif esp == "temporaria" and dib is None:
            formula.append(f"[VERIFICAR] DIB = {br(dib_minima)} ({fund_dib}) ou a DII, se posterior (IN 128, art. 336, "
                           "I); informe a DII")
            if e["teto"] is None or e["salario_minimo"] is None:
                formula.append(f"[VERIFICAR] piso e teto consultados na DIB mínima ({br(dib_minima)}); com DIB "
                               "posterior, os vigentes na data da DIB (o mínimo e o teto mudam dentro do ano — ex.: mínimo de "
                               "R$ 1.320,00 desde 01/05/2023)")
            # Sem DII, a DIB pode seguir outra redação do art. 60 se a DII cair num segmento fora da cobertura.
            formula += [f"se a DII cair nesse período: {s['linha']}" for s in fora_dib]
        elif dib:
            formula.append(f"DIB = {br(dib)} ({fund_dib})")
        if antes_9876:
            marco = ", ".join(f"{n} {br(d)}" for n, d in (("DII", dii), ("DIB", e["dib"])) if d is not None)
            faltantes.append(
                f"fato gerador ou DIB antes de 29/11/1999 ({marco}; publicação da Lei 9.876): o salário de benefício é "
                "a média dos últimos 36 salários de contribuição em até 48 meses (IN 128, art. 221, II, \"b\"), regra "
                "fora do cálculo automático deste script; faça a conta à mão")
            formula.append(REGRA_36)
        elif historico:
            faltantes.append(
                f"média dos 80% maiores salários de contribuição: fato gerador (DII {br(dii)}) até 13/11/2019 → é ela o "
                "salário de benefício (Lei 8.213, arts. 29, II, e 44; IN 128, art. 229 e art. 233, II, \"a\"), não a "
                "media_100; apure-a pela lista de salários (calc_previdenciario_rmi.py, salarios_contribuicao)")
            limite = esp == "temporaria" and dii >= MARCO_29_10
            formula += ramo(BASE_80, limite)
            if esp == "temporaria" and not limite:
                formula.append(f"sem o limite do art. 29, §10: fato gerador (DII {br(dii)}) anterior a 01/03/2015 "
                               "(IN 128, art. 233, I, \"b\")")
        elif sem_fato:
            faltantes.append(
                "dii: sem ela não se sabe o fato gerador, que decide a base do salário de benefício (média dos 80% "
                "maiores com fato gerador até 13/11/2019 — Lei 8.213, art. 29, II; IN 128, art. 229)"
                + (", o limite do art. 29, §10 (fato gerador desde 01/03/2015 — IN 128, art. 233, I, \"b\") e a DIB "
                   "(IN 128, art. 336, I)" if esp == "temporaria" else ""))
            atual = "DII a partir de 14/11/2019"
            if esp == "auxilio-acidente":     # COBERTURA: a regra atual só vale fora da janela da MP 905/2019
                atual = "fato gerador a partir de 21/04/2020"
            if teto is not None and sm is not None:
                passos = []
                valor, _ = conta(e["media_100"], pct, m12, sm, teto, esp, passos)
                formula.append(f"[VERIFICAR] {atual} (base media_100): " + "; ".join(passos)
                               + f" → RMI {valor}")
            else:
                formula.append(f"[VERIFICAR] {atual}: " + "; ".join(ramo(e["media_100"], m12 is not None)))
            if esp == "auxilio-acidente":
                formula.append(COBERTURA["auxilio-acidente"][3]["linha"])
            formula.append("[VERIFICAR] DII de 29/11/1999 a 13/11/2019: " + "; ".join(ramo(BASE_80, False))
                           + ("; limite do art. 29, §10 só com DII desde 01/03/2015" if esp == "temporaria" else ""))
            formula.append("[VERIFICAR] DII até 28/11/1999: " + REGRA_36[len("[VERIFICAR] "):])
        elif novos:
            # Só a regra histórica; a atual entra apenas se o marco também alcança período coberto.
            if alcanca_coberto(esp, *marco):
                formula.append("[VERIFICAR] fato gerador fora desse período (regra atual): "
                               + "; ".join(ramo(e["media_100"], m12 is not None)))
        else:
            formula += ramo(e["media_100"], m12 is not None)
        # Regras históricas da COBERTURA alcançadas pelo marco (o ramo de cima não as descreve).
        formula += [s["linha"] for s in fora if s.get("linha") and s["linha"] not in formula]
        if e["assistencia_permanente"]:
            formula.append("acréscimo de 25% sobre a RMI, ainda que acima do teto (Lei 8.213, art. 45)")
        if fora:      # fora da cobertura nenhum valor da regra sai fechado, nem o percentual
            base_saida["percentual"] = None
        saida = dict(base_saida, rmi=None, limitador_aplicado=None, acrescimo_25=None,
                     dados_faltantes=faltantes,
                     formula_aberta="; ".join(formula) + ". Conta aberta em context/calculo-incapacidade.md.",
                     fonte=fonte)
        saida["alertas"].append(AVISO_FIXO)
        return EXIT_FALTA, saida

    # Daqui em diante o fato gerador (DII) é posterior a 13/11/2019 e, portanto, a 01/03/2015: na temporária o
    # limite do art. 29, §10 sempre incide (IN 128, art. 233, I, "b").
    if m12 is not None:
        memoria.append(f"fato gerador = DII {br(dii)}, desde 01/03/2015: limite do art. 29, §10 "
                       "(IN 128, art. 233, I, \"b\")")
    rmi, limitador = conta(e["media_100"], pct, m12, sm, teto, esp, memoria)

    acrescimo = None
    if e["assistencia_permanente"]:
        valor = q(rmi * Decimal("0.25"))
        acrescimo = {
            "devido": True,
            "valor": str(valor),
            "rmi_com_acrescimo": str(rmi + valor),
            "inicio": "desde a DIB, se a necessidade de assistência foi constatada na perícia da concessão; "
                      "senão, desde o pedido (IN 128, art. 328)",
            "fundamento": "Lei 8.213, art. 45 e parágrafo único, \"a\": devido ainda que ultrapasse o teto",
        }
        memoria.append(f"acréscimo de 25% = {rmi} × 0,25 = {valor}; total {rmi + valor}")
        fonte["acrescimo_25"] = "Lei 8.213, art. 45; IN 128, art. 328"

    fonte["rmi"] = "; ".join(regras)
    fonte["limitador_aplicado"] = {
        "nenhum": "—", "teto": "EC 103, art. 26, §1º",
        "art. 29 §10": "Lei 8.213, art. 29, §10; IN 128, art. 233, I, \"b\"",
        "piso, CF art. 201 §2º": "CF, art. 201, §2º; Decreto 3.048, art. 35",
        PISO_SB: "Lei 8.213, art. 29, §2º; Decreto 3.048, art. 32, §3º"}[limitador]
    saida = dict(base_saida, rmi=str(rmi), limitador_aplicado=limitador, acrescimo_25=acrescimo,
                 dados_faltantes=[], formula_aberta=None, fonte=fonte)
    saida["alertas"].append(AVISO_FIXO)
    return EXIT_OK, saida


def build_parser():
    ap = argparse.ArgumentParser(
        prog=NOME,
        description="RMI do auxílio por incapacidade temporária, da aposentadoria por incapacidade "
                    "permanente e do auxílio-acidente; DIB do auxílio temporário. Entrada JSON por "
                    "--entrada ou stdin (campos em context/calculo-incapacidade.md, seção 5).")
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
                            "context/calculo-incapacidade.md"}
        try:
            _emite(EXIT_ENTRADA, saida)
        except Exception:
            pass
        return EXIT_ENTRADA


if __name__ == "__main__":
    sys.exit(main())
