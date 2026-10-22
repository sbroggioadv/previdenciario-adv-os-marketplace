#!/usr/bin/env python3
"""Direito adquirido, transições da EC 103 (arts. 15 a 18, 20 e 21) e regra permanente (art. 19).

Conta aberta e CAMPOS: context/calculo-transicao.md. O tempo segue a convenção de
context/calculo-tempo.md e é apurado pelo calc_previdenciario_tempo.py da mesma
pasta (carregado por caminho relativo a este arquivo). Requisitos ano a ano:
scripts/data/transicoes-ec103.json.

Toda conta é em dias (P5). Duas escolhas ficam abertas e saem lado a lado:
  normalização das competências desde 12/2019: padrão (12 = 365 dias) × 30 por competência;
  pontos (arts. 15 e 21): leitura B, idade e tempo em dias; a leitura A (componentes a/m/d) não é a
  operação do texto (F1, M1) e sai só como sensibilidade, fora do veredito.
Se a normalização muda o veredito na DER, a regra sai sem veredito e o script devolve exit 3.

Entrada JSON por --entrada ou stdin. Saída JSON no stdout.
Exit: 0 calculado · 2 entrada inválida · 3 veredito depende da leitura, 11/2019 só em parte ou
regra cumprida na DER que depende do fator previdenciário (tábua do IBGE ausente) ou regra verificada fora da
COBERTURA (intervalo em que é a vigente; a fórmula aberta traz a regra histórica e a fonte).
Só biblioteca padrão, sem rede.
"""

import argparse
import bisect
import datetime as dt
import importlib.util
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSAO = "2.0.3"
EXIT_OK, EXIT_ENTRADA, EXIT_FALTA = 0, 2, 3

AQUI = Path(__file__).resolve().parent
TABELA_TRANSICOES = AQUI.parent / "data" / "transicoes-ec103.json"


def _carregar_tempo():
    spec = importlib.util.spec_from_file_location("calc_previdenciario_tempo", AQUI / "calc_previdenciario_tempo.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _carregar_tempo()
MARCO = T.MARCO_EC103
# EC 20/1998: publicada e vigente em 16/12/1998 (IN 128, art. 5º, IV; in-128-2022-inss.md:53).
PUBLICACAO_EC20 = dt.date(1998, 12, 16)
UM_DIA = dt.timedelta(days=1)
INICIO_PAR8 = dt.date(2019, 11, 14)   # IN 128, art. 189, §8º: atividade iniciada antes de 14/11/2019

CAMPOS = {
    "nascimento": {"tipo": "data", "obrigatorio": "sim"},
    "sexo": {"tipo": "enum", "obrigatorio": "sim", "valores": ["M", "F"]},
    "data_filiacao": {"tipo": "data", "obrigatorio": "sim", "valores": "primeira filiacao ao RGPS"},
    "der": {"tipo": "data", "obrigatorio": "sim", "valores": "data em que se verifica cada regra"},
    "periodos": {"tipo": "lista", "obrigatorio": "sim", "valores": "mesmo formato de context/calculo-tempo.md"},
    "periodos[].inicio": T.CAMPOS["periodos[].inicio"],
    "periodos[].fim": T.CAMPOS["periodos[].fim"],
    "periodos[].tipo": T.CAMPOS["periodos[].tipo"],
    "periodos[].fonte": T.CAMPOS["periodos[].fonte"],
    "periodos[].competencias_abaixo_do_minimo": T.CAMPOS["periodos[].competencias_abaixo_do_minimo"],
    "novembro_2019_integral": T.CAMPOS["novembro_2019_integral"],
    "professor": {"tipo": "bool", "obrigatorio": "nao", "padrao": False,
                  "valores": "true declara que todo o tempo informado e de magisterio exclusivo"},
    "projecao_continua": {"tipo": "bool", "obrigatorio": "nao", "padrao": False,
                          "valores": "true projeta competencias mensais validas depois do ultimo periodo"},
    "projecao_ate": {"tipo": "data", "obrigatorio": "condicional",
                     "valores": "sim quando projecao_continua = true; limite da projecao"},
}

FUND = {
    "adquirido-tc": "EC 103, art. 3º; Lei 8.213, arts. 29 e 29-C; Lei 9.876, art. 3º; IN 128, art. 229",
    "adquirido-idade": "EC 103, art. 3º; Lei 8.213, arts. 25, II, 48, 50 e 142",
    "art15": "EC 103, art. 15 (I, II, §§1º e 2º); art. 26, §§2º e 5º",
    "art16": "EC 103, art. 16 (I, II e §1º); art. 26, §§2º e 5º",
    "art17": "EC 103, art. 17 (caput, I, II e parágrafo único)",
    "art18": "EC 103, art. 18 (I, II e §1º); art. 26, §§2º e 5º",
    "art19": "EC 103, art. 19, caput (filiado depois de 13/11/2019); filiado até essa data, por opção: Decreto "
             "3.048, arts. 51 e 188-H a 188-L, e IN 128, art. 249, §1º; art. 26, §2º, IV, e §5º",
    "art19-professor": "EC 103, art. 19, §1º, II; Decreto 3.048, art. 54 (filiado até 13/11/2019, por opção: arts. "
                       "188-M a 188-O); IN 128, arts. 250 e 233, VI",
    "art19-especial": "EC 103, art. 19, §1º, I, a a c; Decreto 3.048, art. 64 (filiado até 13/11/2019, por opção: art. "
                      "188-P, caput); IN 128, art. 260; EC 103, art. 26, §§2º e 5º",
    "art20": "EC 103, art. 20 (I, II e IV); art. 26, §3º, I",
    "art21": "EC 103, art. 21 (caput e §1º); Decreto 3.048, art. 188-P (caput e §1º); art. 26, §§2º e 5º",
}
FUND_CARENCIA = "Lei 8.213, arts. 24, 25, II, e 142"
# Lei 8.213, art. 142 (context/lei/lei-8213-1991.md): carência das aposentadorias do inscrito até 24/07/1991 pelo
# ano em que implementou todas as condições; 180 meses do art. 25, II, a partir de 2011 e para os demais.
TABELA_142 = {1991: 60, 1992: 60, 1993: 66, 1994: 72, 1995: 78, 1996: 90, 1997: 96, 1998: 102, 1999: 108,
              2000: 114, 2001: 120, 2002: 126, 2003: 132, 2004: 138, 2005: 144, 2006: 150, 2007: 156, 2008: 162,
              2009: 168, 2010: 174, 2011: 180}
INSCRICAO_142 = dt.date(1991, 7, 24)
# r11: tabela de requisitos. Uma regra só é reconhecida quando TODOS os requisitos da sua linha são verificados no
# mesmo dia (reconhecer); requisito que o script não consegue verificar deixa a regra indeterminada (exit 3). A
# carência entra em toda linha de aposentadoria: 180 competências ou, para o inscrito até 24/07/1991, a linha do
# art. 142 do ano em que TODAS as condições se implementam (Carencia.exigidas no dia verificado). O coeficiente
# (EC 103, art. 26; Lei 8.213, art. 50; EC 20, art. 9º, §1º, II) só é apurado para a regra reconhecida.
FONTE_REQ_CARENCIA = ("Lei 8.213, art. 25, II (180 competências); art. 142, no ano em que o segurado implementou "
                      "todas as condições, para o inscrito até 24/07/1991")
REQUISITOS = {
    "adquirido-tc": (
        ("filiacao", "filiação ao RGPS até a data da apuração (EC 103, art. 3º)"),
        ("tempo", "35 anos de contribuição (H) / 30 (M) (CF, art. 201, §7º, I, na redação da EC 20/1998; EC 103, "
                  "art. 3º); 30/25 do professor"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "adquirido-idade": (
        ("filiacao", "filiação ao RGPS até a data da apuração (EC 103, art. 3º)"),
        ("idade", "65 anos (H) / 60 (M) (Lei 8.213, art. 48)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "adquirido-especial": (
        ("filiacao", "filiação ao RGPS até a data da apuração (EC 103, art. 3º)"),
        ("exposicao", "15, 20 ou 25 anos de exposição (Lei 8.213, art. 57, caput); soma de tipos diferentes só pela "
                      "conversão do Decreto 3.048, art. 66: indeterminada"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "adquirido-proporcional-ec20": (
        ("filiacao_ate_publicacao", "filiado ao RGPS até a publicação da EC 20/1998 (art. 9º, caput)"),
        ("idade", "53 anos (H) / 48 (M) (EC 20/1998, art. 9º, I)"),
        ("tempo", "30 anos (H) / 25 (M) + 40% do que faltava na publicação (EC 20/1998, art. 9º, §1º, I, 'a' e 'b')"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art15": (
        ("filiacao", "filiado até 13/11/2019 (EC 103, art. 15, caput)"),
        ("tempo", "35 anos (H) / 30 (M) (art. 15, I); 30/25 do professor (§3º)"),
        ("pontos", "idade + tempo em dias, pontos do ano (art. 15, II, §§1º e 2º; §3º do professor)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art16": (
        ("filiacao", "filiado até 13/11/2019 (EC 103, art. 16, caput)"),
        ("tempo", "35 anos (H) / 30 (M) (art. 16, I); menos 5 do professor (§2º)"),
        ("idade", "idade do ano (art. 16, II e §1º; §2º do professor)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art17": (
        ("filiacao", "filiado até 13/11/2019 (EC 103, art. 17, caput)"),
        ("tempo_em_13_11_2019", "mais de 33 anos (H) / 28 (M) em 13/11/2019 (art. 17, caput)"),
        ("tempo", "35 anos (H) / 30 (M) (art. 17, I)"),
        ("pedagio", "período adicional de 50% do que faltava em 13/11/2019 (art. 17, II)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art18": (
        ("filiacao", "filiado até 13/11/2019 (EC 103, art. 18, caput)"),
        ("idade", "65 anos (H) / 60 (M) + 6 meses por ano desde 2020 até 62 (art. 18, I e §1º)"),
        ("tempo", "15 anos de contribuição (art. 18, II)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art19": (
        ("filiacao", "filiado ao RGPS até a data verificada: depois de 13/11/2019 pelo art. 19, caput, da EC 103; até "
                     "essa data, por opção (Decreto 3.048, arts. 51 e 188-H a 188-L; IN 128, art. 249, §1º)"),
        ("idade", "65 anos (H) / 62 (M) (EC 103, art. 19, caput)"),
        ("tempo", "20 anos (H) / 15 (M) (EC 103, art. 19, caput)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art19-professor": (
        ("filiacao", "filiado ao RGPS até a data verificada (EC 103, art. 19, §1º, II, sem distinção de filiação; "
                     "Decreto 3.048, art. 54, e opção dos arts. 188-M a 188-O)"),
        ("idade", "60 anos (H) / 57 (M) (EC 103, art. 19, §1º, II)"),
        ("tempo", "25 anos de contribuição em magistério exclusivo (EC 103, art. 19, §1º, II)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art19-especial": (
        ("filiacao", "filiado ao RGPS até a data verificada (EC 103, art. 19, §1º, I, sem distinção de filiação; "
                     "Decreto 3.048, art. 64, e opção do art. 188-P)"),
        ("exposicao", "15, 20 ou 25 anos de efetiva exposição (EC 103, art. 19, §1º, I); soma de tipos diferentes só "
                      "pela conversão do Decreto 3.048, art. 66: indeterminada"),
        ("idade", "55, 58 ou 60 anos, conforme a atividade de 15, 20 ou 25 anos (EC 103, art. 19, §1º, I, a a c)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art20": (
        ("filiacao", "filiado até 13/11/2019 (EC 103, art. 20, caput)"),
        ("idade", "60 anos (H) / 57 (M) (art. 20, I); menos 5 do professor (§1º)"),
        ("tempo", "35 anos (H) / 30 (M) (art. 20, II); menos 5 do professor (§1º)"),
        ("pedagio", "período adicional igual ao que faltava em 13/11/2019 (art. 20, IV)"),
        ("carencia", FONTE_REQ_CARENCIA)),
    "art21": (
        ("filiacao", "filiado até 13/11/2019 (EC 103, art. 21, caput)"),
        ("exposicao", "15, 20 ou 25 anos de efetiva exposição (art. 21, I a III)"),
        ("pontos", "66, 76 ou 86 pontos, idade + tempo (art. 21, I a III e §1º; Decreto 3.048, art. 188-P)"),
        ("carencia", FONTE_REQ_CARENCIA)),
}
_REQ_NOMES = {rid: tuple(nome for nome, _ in linha) for rid, linha in REQUISITOS.items()}
PROP = "adquirido-proporcional-ec20"
ORDEM = ("adquirido-tc", "adquirido-idade", "art15", "art16", "art17", "art18", "art19", "art19-professor",
         "art19-especial", "art20", "art21")
# r12 (revisão r11, BLOCKER 1: alternativa legal omitida). Toda alternativa de aposentadoria que a lei dá a cada perfil
# da entrada. Um perfil soma as suas regras às dos outros perfis em que a entrada também se enquadra (perfis_da_entrada);
# cada regra exigida tem de sair avaliada (alternativas.avaliadas), nunca descartada por um requisito de OUTRA regra.
# A regra permanente vale para todos: o caput do art. 19 da EC 103 é do filiado depois de 13/11/2019, e o filiado até
# essa data tem a mesma regra por opção ressalvada (Decreto 3.048, arts. 51, 54 e 64, ressalvados nos arts. 188-H a
# 188-P; IN 128, art. 249, §1º); os §§1º, I e II, do art. 19 não distinguem a filiação. Modalidade do professor nas
# transições (arts. 15, §3º; 16, §2º; 20, §1º) é a própria linha da regra, com os requisitos reduzidos.
ALTERNATIVAS = (
    {"perfil": "filiado_ate_13_11_2019", "descricao": "filiado ao RGPS até 13/11/2019",
     "regras": ("adquirido-tc", "adquirido-idade", "art15", "art16", "art17", "art18", "art19", "art20")},
    {"perfil": "filiado_ate_ec20", "descricao": "filiado até a publicação da EC 20/1998 (16/12/1998)",
     "regras": ("adquirido-proporcional-ec20",)},
    {"perfil": "filiado_depois_13_11_2019", "descricao": "filiado ao RGPS depois de 13/11/2019",
     "regras": ("art19",)},
    {"perfil": "professor", "descricao": "magistério exclusivo (professor = true)", "regras": ("art19-professor",)},
    {"perfil": "especial_filiado_ate_13_11_2019", "descricao": "período especial, filiado até 13/11/2019",
     "regras": ("adquirido-especial", "art21", "art19-especial")},
    {"perfil": "especial_filiado_depois", "descricao": "período especial, filiado depois de 13/11/2019",
     "regras": ("art19-especial",)},
)
NAO_SUPORTADAS = (
    {"perfil": "pessoa com deficiência", "regra": "LC 142/2013 (aposentadoria da pessoa com deficiência)",
     "motivo": "sem script na versão 2.0.3 (gap declarado no CLAUDE.md do plugin): a entrada não tem campo de "
               "deficiência e nenhuma conta é feita"},
)


def perfis_da_entrada(e):
    filiado_antes = e["data_filiacao"] <= MARCO
    especial = any(p["tipo"] != "comum" for p in e["periodos"])
    out = ["filiado_ate_13_11_2019" if filiado_antes else "filiado_depois_13_11_2019"]
    if e["data_filiacao"] <= PUBLICACAO_EC20:
        out.append("filiado_ate_ec20")
    if e["professor"]:
        out.append("professor")
    if especial:
        out.append("especial_filiado_ate_13_11_2019" if filiado_antes else "especial_filiado_depois")
    return out


def alternativas_exigidas(e):
    perfis = perfis_da_entrada(e)
    return perfis, [rid for a in ALTERNATIVAS if a["perfil"] in perfis for rid in a["regras"]]


# r12 (revisão r11, BLOCKER 2: regime histórico). COBERTURA: intervalo em que a regra implementada é a vigente, com a
# fonte de cada borda (notas de redação de context/lei/ e IN 128). 'chave': a data em que a regra é verificada (DER ou
# data da apuração do direito adquirido). 'fora': "aberta" = fora do intervalo a conta sai aberta (exit 3) com a regra
# histórica, nunca veredito fechado pela regra posterior; "inexistente" = antes do intervalo a regra não existia e a
# regra anterior é a de outra linha implementada (direito adquirido): a linha sai inaplicável, sem veredito.
COBERTURA = (
    {"id": "ec103", "chave": "der", "fora": "inexistente",
     "regras": ("art15", "art16", "art17", "art18", "art19", "art19-professor", "art19-especial", "art20", "art21"),
     "desde": dt.date(2019, 11, 13),
     "fonte_desde": "EC 103, art. 36, III (vigência na publicação; ec-103-2019.md:705); publicada em 13/11/2019 (IN "
                    "128, art. 249, §1º, in-128-2022-inss.md:2307)",
     "ate": None, "fonte_ate": "sem nota de alteração ou revogação dos arts. 15 a 21 em ec-103-2019.md",
     "historica": "antes de 13/11/2019 a regra não existia: vale o direito adquirido (linhas adquirido-*)"},
    {"id": "adquirido-tempo", "chave": "data_da_apuracao", "fora": "aberta",
     "regras": ("adquirido-tc", "adquirido-proporcional-ec20"),
     "desde": PUBLICACAO_EC20,
     "fonte_desde": "EC 20/1998, de 15/12/1998 (ec-20-1998.md:18): 35/30 anos (CF, art. 201, §7º, I) e proporcional do "
                    "art. 9º; publicada e vigente em 16/12/1998 (IN 128, art. 5º, IV: \"16 de dezembro de 1998, data "
                    "da publicação e vigência da Emenda Constitucional nº 20\"; in-128-2022-inss.md:53)",
     "ate": MARCO, "fonte_ate": "EC 103, art. 3º (direito adquirido até a entrada em vigor)",
     "historica": "aposentadoria por tempo de serviço da Lei 8.213, arts. 52 e 53 (25 anos M / 30 H, 70% + 6% por "
                  "ano até 100% aos 30/35; lei-8213-1991.md:1279-1285), com o salário de benefício do art. 29 na "
                  "redação original (média dos últimos 36 salários em até 48 meses; lei-8213-1991.md:801)"},
    {"id": "adquirido-rmi-lei-9876", "chave": "data_da_apuracao", "fora": "aberta",
     "regras": ("adquirido-tc", "adquirido-proporcional-ec20"),
     "desde": dt.date(1999, 11, 29),
     "fonte_desde": "Lei 9.876/1999: art. 29 da Lei 8.213 na redação dela (média e fator; lei-8213-1991.md:803), DOU "
                    "de 29.11.1999 (lei-9876-1999.md:337)",
     "ate": MARCO, "fonte_ate": "EC 103, art. 3º",
     "historica": "de 16/12/1998 a 28/11/1999: salário de benefício do art. 29 da Lei 8.213 na redação original "
                  "(média dos últimos 36 salários em até 48 meses, sem fator previdenciário; lei-8213-1991.md:801)"},
    {"id": "adquirido-carencia-142", "chave": "data_da_apuracao", "fora": "aberta",
     "regras": ("adquirido-tc", "adquirido-idade", "adquirido-proporcional-ec20", "adquirido-especial"),
     "desde": dt.date(1995, 4, 29),
     "fonte_desde": "Lei 8.213, art. 142, redação da Lei 9.032/1995 (\"ano em que o segurado implementou todas as "
                    "condições\"; lei-8213-1991.md:2843), publicada em 29/04/1995 (IN 128, art. 261, I, "
                    "in-128-2022-inss.md:2411)",
     "ate": MARCO, "fonte_ate": "EC 103, art. 3º",
     "historica": "de 25/07/1991 a 28/04/1995: art. 142 na redação original, tabela pelo ano da entrada do "
                  "requerimento (lei-8213-1991.md:2786-2841); antes, regime anterior à Lei 8.213 (CLPS, não "
                  "capturada)"},
    # Tabela de conversão do especial em comum (COBERTURA do calc_previdenciario_tempo.py): verificada pela DER,
    # data do requerimento em que o tempo convertido é usado.
    {**{k: v for k, v in T.COBERTURA[0].items() if k != "regra"},
     "regras": ("adquirido-tc", "adquirido-proporcional-ec20", "art15", "art16", "art17", "art18", "art19",
                "art19-professor", "art20")},
    {"id": "art29C", "chave": "data_da_apuracao", "fora": "aberta", "regras": ("adquirido-tc",),
     "desde": dt.date(2016, 1, 1),
     "fonte_desde": "art. 29-C incluído pela MP 676/2015 e pela Lei 13.183/2015 (lei-8213-1991.md:869-889); dia de "
                    "vigência não datado em context/lei/: o primeiro dia certo é 01/01/2016",
     "ate": MARCO, "fonte_ate": "EC 103, art. 3º",
     "historica": "sem a opção do art. 29-C: média × fator previdenciário (Lei 8.213, art. 29, I)"},
)


def cobertura(lid):
    return next(l for l in COBERTURA if l["id"] == lid)


def coberta(lid, d):
    l = cobertura(lid)
    return d >= l["desde"] and (l["ate"] is None or d <= l["ate"])


def descrever_fora(lid, d):
    l = cobertura(lid)
    return {"linha": lid, l["chave"]: d.isoformat(), "regras": list(l["regras"]),
            "cobertura": {"desde": l["desde"].isoformat(), "fonte_desde": l["fonte_desde"],
                          "ate": l["ate"].isoformat() if l["ate"] else None, "fonte_ate": l["fonte_ate"]},
            "regra_historica": l["historica"]}
LEITURAS = (("padrao", "B"), ("padrao", "A"), ("30d", "B"), ("30d", "A"))
HORIZONTE_ANOS = 30


class EntradaInvalida(Exception):
    pass


# ------------------------------------------------------------ datas

def somar_anos_meses(nasc, anos, meses=0):
    """Aniversário de `anos` e `meses` (CC, art. 132, §3º: sem dia igual, o dia seguinte)."""
    total = nasc.month - 1 + meses
    ano, m = nasc.year + anos + total // 12, total % 12 + 1
    try:
        return dt.date(ano, m, nasc.day)
    except ValueError:
        return dt.date(ano + (m == 12), 1 if m == 12 else m + 1, 1)


def idade_componentes(nasc, d):
    anos = d.year - nasc.year - ((d.month, d.day) < (nasc.month, nasc.day))
    base = somar_anos_meses(nasc, anos)
    meses = 0
    while somar_anos_meses(nasc, anos, meses + 1) <= d:
        meses += 1
    dias = (d - somar_anos_meses(nasc, anos, meses)).days
    return anos, meses, dias


def representar_texto(anos, meses, dias):
    return f"{anos}a {meses}m {T.txt(dias).replace('.', ',')}d"


# ------------------------------------------------------------ validação

def validar(bruto):
    if not isinstance(bruto, dict):
        raise EntradaInvalida("entrada: esperado objeto JSON")
    e = T._sem_comentarios(bruto)
    T._chaves(e, [k for k in CAMPOS if "[]" not in k], "entrada")
    try:
        nasc = T._data("nascimento", T._obrig(e, "nascimento", "entrada"))
        filiacao = T._data("data_filiacao", T._obrig(e, "data_filiacao", "entrada"))
        der = T._data("der", T._obrig(e, "der", "entrada"))
        sexo = T._obrig(e, "sexo", "entrada")
        if sexo not in ("M", "F"):
            raise EntradaInvalida(f"sexo: '{sexo}' fora de ['M', 'F']")
        periodos = T.validar_periodos(T._obrig(e, "periodos", "entrada"))
    except T.EntradaInvalida as err:
        raise EntradaInvalida(str(err))
    for campo in ("novembro_2019_integral", "professor", "projecao_continua"):
        if e.get(campo) is not None and not isinstance(e[campo], bool):
            raise EntradaInvalida(f"{campo}: esperado true ou false")
    proj = bool(e.get("projecao_continua"))
    proj_ate = None
    if proj:
        try:
            proj_ate = T._data("projecao_ate", T._obrig(e, "projecao_ate", "entrada"))
        except T.EntradaInvalida as err:
            raise EntradaInvalida(str(err) + " (obrigatório com projecao_continua = true)")
    elif e.get("projecao_ate") is not None:
        raise EntradaInvalida("projecao_ate: só com projecao_continua = true")
    if der < nasc or filiacao < nasc:
        raise EntradaInvalida("der e data_filiacao não podem ser anteriores ao nascimento")
    # r13 (revisão r12, MAJOR 2): cronologia impossível é recusada antes de qualquer contagem. Período anterior ao
    # nascimento não existe. A idade mínima de filiação não é barreira: o art. 5º da IN 128 a fixa por época, mas o
    # art. 5º-A (ACP do art. 5º-A, ver context/lei/in-128-2022-inss.md; IN 188/2025) manda computar a atividade
    # exercida abaixo dela; o nascimento é o único limite. Início depois do fim já é recusado em T.validar_periodos.
    # Período posterior à DER é permitido: a transição procura a data em que cada regra se cumpre depois dela (planejamento).
    # r15 (revisão r14, MAJOR 2): a primeira filiação não pode ser posterior ao início de período de atividade. Para o
    # segurado obrigatório a filiação decorre automaticamente do exercício da atividade remunerada (IN 128, art. 3º,
    # §1º): período de CTPS, PPP, sentença ou especial é atividade, e começar antes da filiação declarada é entrada
    # contraditória. O período comum do CNIS pode ser de facultativo, filiado pelo primeiro recolhimento sem atraso
    # (art. 4º, parágrafo único), que é pago até o vencimento no mês seguinte à competência: ali a tolerância é de uma
    # competência, nunca mais.
    for i, p in enumerate(periodos):
        if p["inicio"] < nasc:
            raise EntradaInvalida(f"periodos[{i}]: início {p['inicio']} anterior ao nascimento {nasc}")
        atividade = p["fonte"] != "CNIS" or p["tipo"] != "comum"
        limite = filiacao if atividade else (dt.date(filiacao.year - 1, 12, 1) if filiacao.month == 1
                                             else dt.date(filiacao.year, filiacao.month - 1, 1))
        if p["inicio"] < limite:
            raise EntradaInvalida(
                f"periodos[{i}]: início {p['inicio']} anterior à data_filiacao {filiacao}; a filiação do segurado "
                f"obrigatório decorre do exercício da atividade (IN 128, art. 3º, §1º): informe a primeira filiação")
    if proj_ate is not None and proj_ate < nasc:
        raise EntradaInvalida(f"projecao_ate: {proj_ate} anterior ao nascimento {nasc}")
    return {"nascimento": nasc, "sexo": sexo, "data_filiacao": filiacao, "der": der, "periodos": periodos,
            "novembro_2019_integral": e.get("novembro_2019_integral"), "professor": bool(e.get("professor")),
            "projecao_continua": proj, "projecao_ate": proj_ate}


# ------------------------------------------------------------ tabela

def carregar_tabela(caminho=None):
    caminho = TABELA_TRANSICOES if caminho is None else caminho
    try:
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        regras = {r["id"]: r for r in dados["regras"]}
        anual = {linha["ano"]: linha for linha in dados["anual"]}
    except (OSError, ValueError, KeyError, TypeError, IndexError) as err:
        raise T.TabelaIndisponivel("scripts/data/transicoes-ec103.json", err)
    return dados, regras, anual


def _tabela_ausente(err, e=None):
    """Exit 3: sem a tabela de requisitos ou a de conversão, nenhuma regra fecha por script (DESIGN-SPEC §3.2)."""
    parametros = None
    if e is not None:
        parametros = {"nascimento": e["nascimento"].isoformat(), "sexo": e["sexo"], "der": e["der"].isoformat(),
                      "data_filiacao": e["data_filiacao"].isoformat()}
    saida = T.tabela_ausente(
        VERSAO, err, parametros,
        "cada regra: idade ≥ requisito do ano E tempo (ou pontos) ≥ requisito do ano, na DER (EC 103, arts. 15 a 21)",
        "Conta não conferida por script: confira os requisitos ano a ano no context/calculo-transicao.md e o "
        "tempo pelo calc_previdenciario_tempo.py.",
        "Sem a tabela, nenhuma regra é verificada por script.")
    saida["regras"] = None
    return EXIT_FALTA, saida


def chave_sexo(sexo):
    return "homem" if sexo == "M" else "mulher"


# ------------------------------------------------------------ tempo em qualquer data

class Linha:
    """Tempo em dias em qualquer data de corte, com somas prefixadas (bisect)."""

    def __init__(self, ap, nov_integral, norma=None):
        # r11: `norma` fixa a normalização das competências desde 12/2019 em toda a conta (qualquer `norm` pedido
        # vira ela): é assim que a saída inteira é refeita na leitura alternativa (_sensibilidade_normalizacao).
        self.norma = norma
        self.ap = ap
        dias = ap._dias_f1
        self.f1_dias = dias
        # "*" = exposição a qualquer especial (cada dia uma vez): só para medir se a soma de tipos diferentes,
        # que depende da conversão e da atividade preponderante (Decreto 3.048, art. 66), mudaria o veredito.
        chaves = list(T.ANOS_ESPECIAL) + ["*"]
        self.conv, self.bruto, self.por_esp = [], [], {t: [] for t in chaves}
        c = b = Decimal(0)
        cont = {t: 0 for t in chaves}
        for d in dias:
            t = ap.classe(ap.dia[d])
            b += 1
            c += 1 if t == "comum" else ap.mult[t][ap.sexo]
            if t != "comum":
                cont[t] += 1
                cont["*"] += 1
            self.conv.append(c)
            self.bruto.append(b)
            for k in cont:
                self.por_esp[k].append(cont[k])
        # F2 e F3 numa data qualquer: o índice único do calc_previdenciario_tempo.py, calculado até a data apurada,
        # por tipo de atividade e só com vínculos válidos (IN 128, art. 206, §2º). A exposição de cada tipo conta do
        # seu próprio início e só até a data (EC 103, art. 21: efetiva exposição; IN 128, art. 265).
        self.idx = ap.indice(nov_integral)
        self.idx_esp = {t: ap.indice(nov_integral, {t}) for t in T.ANOS_ESPECIAL}
        self.idx_esp["*"] = ap.indice(nov_integral, set(T.ANOS_ESPECIAL))
        self.pos_ec = sorted(ap.uniao_pos_ec_validos)

    def _f1(self, d, serie):
        i = bisect.bisect_right(self.f1_dias, min(d, MARCO))
        return serie[i - 1] if i else 0

    def n_f3(self, d):
        return self.idx.n_f3_em(d)

    def pos(self, d, norm):
        """Acumulado depois de 13/11/2019 (F2 + F3) até d, em dias."""
        return self.idx.pos_em(d, self.norma or norm)

    def conv_em(self, d, norm="padrao"):
        return self._f1(d, self.conv) + self.pos(d, norm)

    def bruto_em(self, d, norm="padrao"):
        return self._f1(d, self.bruto) + self.pos(d, norm)

    def exposicao_em(self, d, tipo, norm="padrao"):
        return self._f1(d, self.por_esp[tipo]) + self.idx_esp[tipo].pos_em(d, self.norma or norm)

    def civil_conv(self, d):
        return self._f1(d, self.conv) + bisect.bisect_right(self.pos_ec, d)

    def civil_bruto(self, d):
        return self._f1(d, self.bruto) + bisect.bisect_right(self.pos_ec, d)


# ------------------------------------------------------------ núcleo

def coeficiente(tempo_dias, sexo, base_especial=None):
    anos = int(Decimal(tempo_dias) // T.DIAS_ANO)
    base = base_especial if base_especial is not None else (20 if sexo == "M" else 15)
    return Decimal("0.60") + Decimal("0.02") * max(0, anos - base), anos


def pontos_ok(leitura, nasc, d, tempo_dias, pontos):
    if leitura == "B":
        return (d - nasc).days + Decimal(tempo_dias) >= pontos * T.DIAS_ANO
    a, m, dd = idade_componentes(nasc, d)
    rep = T.representar(tempo_dias)
    total = (a + rep["anos"]) * 360 + (m + rep["meses"]) * 30 + dd + Decimal(str(rep["dias"]))
    return total >= pontos * 360


def pontos_medida(leitura, nasc, d, tempo_dias):
    if leitura == "B":
        return T.num((d - nasc).days + Decimal(tempo_dias))
    a, m, dd = idade_componentes(nasc, d)
    rep = T.representar(tempo_dias)
    dias = dd + Decimal(str(rep["dias"]))
    meses = m + rep["meses"] + int(dias // 30)
    dias -= int(dias // 30) * 30
    anos = a + rep["anos"] + meses // 12
    return representar_texto(anos, meses % 12, dias)


def coef_numerico(c):
    """Coeficiente numérico ("0.72", "1.00") ou None quando é fórmula em texto ("70% + 1% ...", "media x fator")."""
    if not isinstance(c, str):
        return None
    try:
        v = Decimal(c)
    except InvalidOperation:
        return None
    return v if v.is_finite() else None


def depende_do_fator(c):
    """Coeficiente que multiplica pelo fator previdenciário (sem a tábua do IBGE não há número)."""
    return isinstance(c, str) and c.startswith("media x fator")


def dias_dos_anos_civis(d, anos):
    """Dias dos `anos` anos civis que terminam em d: de (d + 1) − anos até d (CC, art. 132, §3º)."""
    fim = d + UM_DIA
    try:
        ini = dt.date(fim.year - anos, fim.month, fim.day)
    except ValueError:   # 29/02 em ano não bissexto: o dia seguinte
        ini = dt.date(fim.year - anos, 3, 1)
    return (fim - ini).days


def isencao_par8(p, m):
    """Regra própria da CARÊNCIA, separada da do tempo (IN 128, art. 189, §§7º a 9º): o empregado, o doméstico e o
    avulso com atividade iniciada antes de 14/11/2019 contam para carência as competências até 11/2019 mesmo abaixo
    do mínimo; o contribuinte individual e o facultativo, nunca. A exclusão de 11/2019 do TEMPO (IN 128, art. 206)
    não se aplica aqui. Devolve True (conta), False (não conta) ou None (categoria não conferível pela fonte).
    Os períodos não trazem a categoria: a CTPS só registra empregado e doméstico, ambos no §8º; CNIS, sentença e PPP
    podem ser de contribuinte individual (o PPP também do cooperado), e a competência fica incerta."""
    if m > (2019, 11) or p["inicio"] >= INICIO_PAR8:
        return False
    return True if p["fonte"] == "CTPS" else None


class Carencia:
    """Competências de carência que os períodos podem dar: meses com ao menos um dia coberto por período em que a
    competência não foi declarada abaixo do mínimo, ressalvada a isenção do §8º do art. 189 da IN 128 para 11/2019
    (isencao_par8). É o teto da carência (Lei 8.213, art. 24): nenhum mês sem período conta; o recolhimento em dia do
    contribuinte individual e do facultativo (art. 27, II) não vem nos períodos e é conferido pelo
    calc_previdenciario_cnis.py. presumir_par8=True conta as competências de categoria não conferível, só para medir
    se mudam o resultado (regra 2)."""

    def __init__(self, periodos, data_filiacao, presumir_par8=False):
        primeiro = {}
        self.incertas_par8 = set()
        for p in periodos:
            m = (p["inicio"].year, p["inicio"].month)
            while m <= (p["fim"].year, p["fim"].month):
                conta = m not in p["abaixo"]
                if not conta:
                    isento = isencao_par8(p, m)
                    if isento is None:
                        self.incertas_par8.add(m)
                    conta = isento is True or (isento is None and presumir_par8)
                if conta:
                    d = max(p["inicio"], dt.date(m[0], m[1], 1))
                    primeiro[m] = min(primeiro.get(m, d), d)
                m = (m[0] + (m[1] == 12), 1 if m[1] == 12 else m[1] + 1)
        self.incertas_par8 -= set(primeiro)   # outro período cobre o mês sem estar abaixo do mínimo
        self.dias = sorted(primeiro.values())
        self.tabela = data_filiacao <= INSCRICAO_142

    def ate(self, d):
        return bisect.bisect_right(self.dias, d)

    def exigidas(self, d):
        """180 (art. 25, II); para o inscrito até 24/07/1991, a linha do art. 142 do ano em que as condições se
        completam (anterior a 1991 não está na tabela: 180, o conservador)."""
        if self.tabela and 1991 <= d.year < 2011:
            return TABELA_142[d.year]
        return 180

    def ok(self, d):
        return self.ate(d) >= self.exigidas(d)


def reconhecer(rid, verificados):
    """r11: veredito de uma regra num dia, pela linha de REQUISITOS. `verificados` mapeia cada requisito da linha
    para True, False, None (não verificável) ou uma função sem argumento que devolve um deles (avaliada só se
    preciso). True só com TODOS os requisitos True; False se algum é False; senão None (requisito ausente ou não
    verificável: regra indeterminada, exit 3). Requisito fora da linha é erro de montagem."""
    nomes = _REQ_NOMES[rid]
    extras = set(verificados) - set(nomes)
    if extras:
        raise ValueError(f"{rid}: requisitos fora da tabela: {sorted(extras)}")
    incerto = False
    for nome in nomes:
        v = verificados.get(nome)
        if callable(v):
            v = v()
        if v is False:
            return False
        if v is not True:
            incerto = True
    return None if incerto else True


def varrer(rid, requisitos, inicio, fim):
    """Primeiro dia de [inicio, fim] em que a regra é reconhecida (requisitos(d) pela tabela) e o primeiro dia, antes
    dele, em que ela ficou indeterminada. (None, None): nenhum requisito indeterminado e a regra não se cumpre."""
    d, incerto = inicio, None
    while d <= fim:
        r = reconhecer(rid, requisitos(d))
        if r is True:
            return d, incerto
        if r is None and incerto is None:
            incerto = d
        d += UM_DIA
    return None, incerto


def status_ate(data, incerto, ref):
    """Veredito na data de referência: True (reconhecida até ref), None (indeterminada até ref) ou False."""
    if data is not None and data <= ref:
        return True
    if incerto is not None and incerto <= ref:
        return None
    return False


def primeira_data(cond, inicio, fim):
    d = inicio
    while d <= fim:
        if cond(d):
            return d
        d += UM_DIA
    return None


def calcular(bruto):
    try:
        e = validar(bruto)
    except (EntradaInvalida, T.EntradaInvalida) as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}
    try:
        codigo, saida, ap = _calcular(e, T._classe_dia)
    except T.TabelaIndisponivel as err:
        return _tabela_ausente(err, e)
    if ap is None:
        return codigo, saida
    codigo = _sensibilidade_normalizacao(e, codigo, saida, ap)
    codigo = _sensibilidade_par8(e, codigo, saida)
    dias = sorted(d for d, ts in ap.dia.items() if len([t for t in ts if t != "comum"]) > 1)
    if not dias:
        return codigo, saida
    # Regra 2: no dia com dois especiais, qual deles vale é a atividade preponderante (Decreto 3.048, art. 66),
    # que a entrada não traz. Refaz tudo com o outro tipo; se alguma regra muda, a conta fica aberta.
    _, alt, _ = _calcular(e, T._classe_dia_alt)
    campos = CAMPOS_SENSIVEIS
    mudou = {rid: {"menor_tempo_exigido": {k: saida[rid].get(k) for k in campos},
                   "maior_tempo_exigido": {k: alt[rid].get(k) for k in campos}}
             for rid in ORDEM if rid in saida and rid in alt
             and any(saida[rid].get(k) != alt[rid].get(k) for k in campos)}
    faixa = T._faixa_txt(dias)
    if not mudou:
        saida["alertas"].append(f"Dois tipos de especial no mesmo dia ({faixa}): o veredito, as datas e os "
                                "coeficientes são os mesmos com qualquer dos dois (Decreto 3.048, art. 66).")
        return codigo, saida
    saida["alertas"].append(f"[VERIFICAR] Dois tipos de especial no mesmo dia ({faixa}): qual vale é a atividade "
                            "preponderante (Decreto 3.048, art. 66), que a entrada não informa; muda "
                            + ", ".join(mudou) + ".")
    aberta = saida["formula_aberta"] or {}
    aberta["dois_especiais_no_mesmo_dia"] = {
        "dias": faixa, "regras_que_mudam": mudou,
        "faltando": ["atividade preponderante nos dias com dois especiais (Decreto 3.048, art. 66)"],
        "instrucao": "Escolha o tipo preponderante e refaça o tempo pelo calc_previdenciario_tempo.py "
                     "(context/calculo-transicao.md)."}
    saida["formula_aberta"] = aberta
    return EXIT_FALTA, saida


CAMPOS_SENSIVEIS = ("cumprida_na_der", "data_em_que_cumpre", "coeficiente")

# r11: o que a conta fecha, sem os campos que só exibem as duas normalizações lado a lado (refeitos pela leitura
# alternativa) e sem os textos de fundamento, regra e instrução, que não são valor da conta.
_SO_EXIBICAO = frozenset({"leituras", "sensibilidade_leitura_A", "veredito_por_leitura", "acumulado_na_der_dias",
                          "sensibilidade_normalizacao_30d", "data_depende_da_normalizacao",
                          "veredito_depende_da_leitura", "instrucao_veredito"})


def _projecao(saida):
    return T.projecao_da_conta(saida, _SO_EXIBICAO | T.SO_TEXTO)


def _sensibilidade_normalizacao(e, codigo, saida, ap):
    """r11, mesma regra do CNIS na r10: a conta inteira é refeita com 30 dias por competência desde 12/2019 e
    comparada à padrão (12 competências = 365 dias) em TODOS os valores (vereditos, datas, coeficientes, tempos,
    requisitos e contas abertas). Qualquer diferença: exit 3 com as duas leituras. Com menos de 12 competências
    até o horizonte, as duas normalizações são a mesma conta (f3_dias idêntica para n < 12) e nada é refeito."""
    if ap.n_f3_horizonte < 12:
        return codigo
    _, alt, _ = _calcular(e, T._classe_dia, norma="30d")
    proj_p, proj_30 = _projecao(saida), _projecao(alt)
    dif = T.diferencas(proj_p, proj_30)
    if not dif:
        return codigo
    saida["alertas"].append("[VERIFICAR] Normalização das competências desde 12/2019: refeita a conta inteira com "
                            "30 dias por competência, o resultado muda (" + ", ".join(dif[:12])
                            + (", …" if len(dif) > 12 else "") + "). A IN 128 não decide; as duas leituras saem em "
                            "formula_aberta.saida_depende_da_normalizacao.")
    aberta = saida["formula_aberta"] or {}
    aberta["saida_depende_da_normalizacao"] = {
        "expressao": "competências desde 12/2019 em dias: ⌊n/12⌋ × 365 + (n mod 12) × 30 (padrão) OU n × 30, "
                     "aplicada à conta inteira",
        "diferencas": dif,
        "leituras": {"padrao_12_competencias_365": proj_p, "alternativa_30d_por_competencia": proj_30},
        "faltando": ["operação que junta dias e competências (IN 128, art. 207; context/calculo-tempo.md, seção 3)"],
        "instrucao": "Escolha a normalização e use a leitura dela (context/calculo-transicao.md, seção 3)."}
    saida["formula_aberta"] = aberta
    return EXIT_FALTA


def _sensibilidade_par8(e, codigo, saida):
    """Regra 2: competência 11/2019 abaixo do mínimo em período de categoria não conferível (isencao_par8 = None).
    Refaz a conta contando-a; se alguma regra muda, a carência fica aberta (exit 3)."""
    periodos = list(e["periodos"])
    incertas = Carencia(periodos, e["data_filiacao"]).incertas_par8
    if not incertas:
        return codigo
    _, alt, _ = _calcular(e, T._classe_dia, presumir_par8=True)
    mudou = {rid: {"sem_as_incertas": {k: saida[rid].get(k) for k in CAMPOS_SENSIVEIS},
                   "com_as_incertas": {k: alt[rid].get(k) for k in CAMPOS_SENSIVEIS}}
             for rid in ORDEM if rid in saida and rid in alt
             and any(saida[rid].get(k) != alt[rid].get(k) for k in CAMPOS_SENSIVEIS)}
    meses = ", ".join(T.mes_txt(m) for m in sorted(incertas))
    if not mudou:
        saida["alertas"].append(f"Carência: competência {meses} abaixo do mínimo, de categoria não conferível pela "
                                "fonte; o resultado é o mesmo contando-a ou não (IN 128, art. 189, §§8º e 9º).")
        return codigo
    saida["alertas"].append(f"[VERIFICAR] Carência: competência {meses} abaixo do mínimo em período cuja fonte não "
                            "mostra a categoria. Empregado, doméstico e avulso com atividade iniciada antes de "
                            "14/11/2019 a contam (IN 128, art. 189, §8º); contribuinte individual e facultativo, não "
                            "(§9º). Muda " + ", ".join(mudou) + ".")
    aberta = saida["formula_aberta"] or {}
    aberta["carencia_novembro_2019"] = {
        "competencias": [T.mes_txt(m) for m in sorted(incertas)], "regras_que_mudam": mudou,
        "faltando": ["categoria do segurado no período (empregado, doméstico ou avulso × contribuinte individual ou "
                     "facultativo) — IN 128, art. 189, §§8º e 9º"],
        "instrucao": "Confirme a categoria; empregado, doméstico e avulso contam a competência (informe a fonte CTPS "
                     "ou confira pelo calc_previdenciario_cnis.py) — context/calculo-transicao.md."}
    saida["formula_aberta"] = aberta
    return EXIT_FALTA


def _calcular(e, classe, presumir_par8=False, norma=None):
    """Conta inteira com a leitura `classe` do dia coberto por 2+ períodos (e, com `norma`, numa normalização só das
    competências desde 12/2019). Devolve (exit, saída, apuração)."""
    dados, R, ANUAL = carregar_tabela()
    mult, fonte_tab_conv = T.carregar_multiplicadores()
    sexo, nasc, der = e["sexo"], e["nascimento"], e["der"]
    sx = chave_sexo(sexo)
    alertas, memoria = [], []
    premissas = []

    periodos = list(e["periodos"])
    limite = max([der] + [p["fim"] for p in periodos])
    if e["projecao_continua"]:
        ultimo = max(periodos, key=lambda p: p["fim"])
        if e["projecao_ate"] > ultimo["fim"]:
            periodos.append({"inicio": ultimo["fim"] + UM_DIA, "fim": e["projecao_ate"], "tipo": ultimo["tipo"],
                             "fonte": ultimo["fonte"], "abaixo": set()})
            premissas.append(f"Projeção: competências mensais válidas de {(ultimo['fim'] + UM_DIA).isoformat()} "
                             f"a {e['projecao_ate'].isoformat()}, mesmo tipo do último período ({ultimo['tipo']}), "
                             "salário de contribuição igual ou superior ao mínimo. Não garante legislação futura.")
        limite = max(limite, e["projecao_ate"])

    ultimo_fim = max(p["fim"] for p in periodos)
    # Horizonte de busca das datas: além da DER e do último período, sem novas contribuições
    # (o tempo fica parado; a idade continua). Só com projecao_continua entram competências novas.
    horizonte = min(T.DATA_MAXIMA, somar_anos_meses(max(limite, der), HORIZONTE_ANOS))
    ap = T.Apuracao(periodos, sexo, mult, classe=classe)
    nov_contas = ap.f2_contas()
    nov = e["novembro_2019_integral"]
    if nov_contas["tem_novembro_pos_ec"] and nov is None and ap.abrange_marco_e_continua():
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "versao": VERSAO,
                              "detalhe": "novembro_2019_integral: obrigatório quando um período abrange "
                                         "13/11/2019 e continua depois"}, None
    parametros = {"nascimento": nasc.isoformat(), "sexo": sexo, "data_filiacao": e["data_filiacao"].isoformat(),
                  "der": der.isoformat(), "novembro_2019_integral": nov, "professor": e["professor"],
                  "projecao_continua": e["projecao_continua"],
                  "projecao_ate": e["projecao_ate"].isoformat() if e["projecao_ate"] else None,
                  "periodos": [{"inicio": p["inicio"].isoformat(), "fim": p["fim"].isoformat(), "tipo": p["tipo"],
                                "fonte": p["fonte"],
                                "competencias_abaixo_do_minimo": sorted(T.mes_txt(m) for m in p["abaixo"])}
                               for p in e["periodos"]],
                  "premissas": premissas}
    fonte = {"regras": FUND,
             "tabela": {"arquivo": "scripts/data/transicoes-ec103.json", "data_captura": dados.get("data_captura")},
             "conversao": fonte_tab_conv,
             "tempo": "scripts/calc/calc_previdenciario_tempo.py (IN 128, arts. 206, 207 e 265)"}
    if nov_contas["tem_novembro_pos_ec"] and nov is not True and not ap.nov_abaixo:
        return EXIT_FALTA, {
            "versao": VERSAO, "parametros_usados": parametros, "regras": None,
            "regra": "Competência 11/2019 trabalhada só em parte: o tempo não fecha numa leitura só.",
            "fonte": fonte, "memoria": [],
            "alertas": ["[VERIFICAR] Competência 11/2019 trabalhada só em parte (item I-5): rode o "
                        "calc_previdenciario_tempo.py, escolha a leitura e refaça as regras à mão."],
            "formula_aberta": {"expressao": "tempo = F1 + F2 + F3; F2 = data a data OU competência integral",
                               "contas_novembro_2019": {"data_a_data": nov_contas["data_a_data"],
                                                        "competencia_integral": nov_contas["competencia_integral"]},
                               "faltando": ["critério para a competência 11/2019 trabalhada só em parte"],
                               "instrucao": "context/calculo-transicao.md, seções 3 e 4."}}, None

    L = Linha(ap, nov is True, norma)
    CAR = Carencia(periodos, e["data_filiacao"], presumir_par8)
    ap.n_f3_horizonte = L.n_f3(horizonte)   # competências desde 12/2019 até o horizonte (_sensibilidade_normalizacao)
    # As duas normalizações das competências desde 12/2019 (context/calculo-tempo.md, seção 3) valem também
    # para quem só tem competências: o anexo só exclui o caso em que todo o tempo é anterior a 13/11/2019 (aí as
    # duas coincidem). Com 240 competências, 20 anos na leitura padrão; 7.200 dias na de 30 por competência.
    NORMAS = ("padrao", "30d")
    filiado_antes = e["data_filiacao"] <= MARCO
    prof = e["professor"]
    if prof:
        alertas.append("[VERIFICAR] professor = true: todo o tempo informado foi tratado como magistério exclusivo "
                       "na educação infantil e no ensino fundamental e médio (EC 103, arts. 15, §3º; 16, §2º; "
                       "19, §1º, II; 20, §1º).")
    t13 = L.conv_em(MARCO)
    anos_tc = R["art15_par3" if prof else "art15"]["tempo_contribuicao_anos"][sx]
    exig_tc = anos_tc * T.DIAS_ANO
    falta = max(Decimal(0), Decimal(exig_tc) - t13)
    inicio_trans = max(MARCO, e["data_filiacao"])
    memoria.append(f"Tempo em 13/11/2019 (F1 convertido): {T.txt(t13)} dias = {T.representar(t13)['texto']}")
    memoria.append(f"Déficit para {anos_tc} anos: {exig_tc} − {T.txt(t13)} = {T.txt(falta)} dias "
                   "(uma unidade só, 365/30; IN 128, art. 207)")

    def ano_tab(d):
        return ANUAL[min(max(d.year, 2019), 2033)]

    def idade_ok(d, req):
        return d >= somar_anos_meses(nasc, req["anos"], req["meses"])

    # ---- definição de cada regra: (aplicável, motivo, condição(d, norm, leitura), base do coeficiente)
    def cond_tempo(norm, exig):
        return lambda d: L.conv_em(d, norm) >= exig

    regras = {}

    def montar(rid, aplicavel, motivo, inicio, requisitos, tempo_cond_por_norm=None,
               coef_fn=None, extra=None, usa_pontos=False):
        """`requisitos(d, norm, leitura)` devolve a linha de REQUISITOS[rid] (carência inclusive) no dia d: a regra
        se cumpre no primeiro dia em que reconhecer() a dá por inteiro."""
        if aplicavel and rid in cobertura("ec103")["regras"] and not coberta("ec103", der):
            # r12, COBERTURA ec103: antes de 13/11/2019 a regra não existia; vale o direito adquirido (outra linha).
            aplicavel, motivo = False, (f"DER {der.isoformat()} anterior à vigência da EC 103 (13/11/2019): a regra "
                                        "não existia na DER; vale o direito adquirido (COBERTURA, linha ec103)")
        linha = {"regra": rid, "aplicavel": aplicavel, "fundamento": FUND[rid]}
        if not aplicavel:
            linha.update({"motivo": motivo, "cumprida_na_der": False, "data_em_que_cumpre": None,
                          "competencia_em_que_cumpre": None, "coeficiente": None})
            regras[rid] = linha
            return linha
        leituras = [(n, l) for n, l in (LEITURAS if usa_pontos else (("padrao", "B"), ("30d", "B")))
                    if n in NORMAS]
        datas, incertos = {}, {}
        for norm, lei in leituras:
            datas[(norm, lei)], incertos[(norm, lei)] = varrer(
                rid, lambda d, n=norm, lt=lei: requisitos(d, n, lt), inicio, horizonte)
        principal = datas[("padrao", "B")]
        # D5 (F1, tabela M, M1): a soma em anos, meses e dias (leitura A) "não é a operação do texto": sai do
        # veredito e fica só como sensibilidade. O veredito vem da leitura B nas duas normalizações; requisito não
        # verificável até a DER (sem a regra já reconhecida) deixa o veredito indeterminado.
        veredito = {k: status_ate(v, incertos[k], der) for k, v in datas.items() if k[1] == "B"}
        indeterminado = {f"{n}/{lt}": incertos[(n, lt)].isoformat() for (n, lt), v in veredito.items() if v is None}
        if indeterminado:
            linha["requisito_indeterminado_desde"] = indeterminado
        linha["data_em_que_cumpre"] = principal.isoformat() if principal else None
        linha["primeira_der"] = linha["data_em_que_cumpre"]
        if tempo_cond_por_norm:
            dt_tempo = primeira_data(tempo_cond_por_norm("padrao"), inicio, horizonte)
            linha["data_tempo"] = dt_tempo.isoformat() if dt_tempo else None
            linha["competencia_em_que_cumpre_tempo"] = (T.mes_txt(T.mes(dt_tempo))
                                                       if dt_tempo and dt_tempo > MARCO else None)
            ligado_ao_tempo = principal is not None and dt_tempo == principal and principal > MARCO
        else:
            ligado_ao_tempo = False
        linha["competencia_em_que_cumpre"] = T.mes_txt(T.mes(principal)) if ligado_ao_tempo else None
        if len(set(veredito.values())) > 1 or indeterminado:
            linha["cumprida_na_der"] = None
            linha["veredito_por_leitura"] = {f"{n}/{l}": v for (n, l), v in veredito.items()}
            linha["indeterminada"] = True
        else:
            linha["cumprida_na_der"] = veredito[("padrao", "B")]
        variantes = {f"{n}/{l}": (v.isoformat() if v else None) for (n, l), v in datas.items()}
        if len(set(variantes.values())) > 1:
            linha["leituras"] = {"datas": variantes,
                                 "legenda": "normalização (padrao = 12 competências = 365 dias; 30d = 30 por "
                                            "competência) / pontos (B = idade e tempo em dias; A = componentes "
                                            "a/m/d somados com 30 dias = 1 mês e 12 meses = 1 ano; só "
                                            "sensibilidade, fora do veredito: F1, M1)",
                                 "aviso": "[VERIFICAR] as leituras dão datas diferentes"}
            sens_a = {k: v for k, v in variantes.items() if k.endswith("/A")}
            if sens_a and set(sens_a.values()) - {variantes.get("padrao/B"), variantes.get("30d/B")}:
                linha["sensibilidade_leitura_A"] = sens_a
        quando = der if linha["cumprida_na_der"] else principal
        if coef_fn and quando:
            linha.update(coef_fn(quando))
            if principal and quando != principal:
                linha["coeficiente_na_data_em_que_cumpre"] = coef_fn(principal)["coeficiente"]
        elif coef_fn:
            linha["coeficiente"] = None
        if extra:
            linha.update(extra)
        regras[rid] = linha
        return linha

    def coef_padrao(tempo_fn, base=None):
        def f(d):
            c, anos = coeficiente(tempo_fn(d), sexo, base)
            return {"coeficiente": str(c.quantize(Decimal("0.01"))), "anos_completos_no_calculo": anos,
                    "coeficiente_regra": "60% + 2% por ano acima de "
                                         f"{base if base is not None else (20 if sexo == 'M' else 15)} (EC 103, art. 26)"}
        return f

    # ---- direito adquirido (regra anterior). Toda apuração se limita à DER: com DER anterior a 13/11/2019 a
    # conta é na DER, nunca em 13/11/2019 (EC 103, art. 3º: requisitos cumpridos até a entrada em vigor).
    ref_adq = min(der, MARCO)
    t_adq = L.conv_em(ref_adq)
    filiado_adq = filiado_antes and e["data_filiacao"] <= ref_adq
    abertas_adq = {}
    fora_cob, avaliadas = [], {}   # r12: pontos fora da COBERTURA; alternativas avaliadas fora de regras

    def marcar_fora(lid, d):
        item = descrever_fora(lid, d)
        if item not in fora_cob:
            fora_cob.append(item)

    def sem_veredito(linha_, lid, d):
        """r12 (revisão r11, BLOCKER 2): regra verificada fora da COBERTURA não fecha veredito; a regra histórica, com
        a fonte, vai para formula_aberta.fora_da_cobertura."""
        marcar_fora(lid, d)
        linha_.update({"cumprida_na_der": None, "indeterminada": True, "data_em_que_cumpre": None,
                       "veredito_por_leitura": {"fora_da_cobertura": lid},
                       "motivo": f"fora da cobertura ({lid}) em {d.isoformat()}: {cobertura(lid)['historica']}"})
        for k in ("coeficiente", "rmi", "formula", "art29C", "faltando", "primeira_der", "competencia_em_que_cumpre",
                  "competencia_em_que_cumpre_tempo", "data_tempo", "coeficiente_na_data_em_que_cumpre",
                  "sensibilidade_civil"):
            if k in linha_:
                linha_[k] = None
        for k in ("leituras", "sensibilidade_leitura_A"):
            linha_.pop(k, None)
    if der < MARCO:
        alertas.append(f"DER {der.isoformat()} anterior a 13/11/2019: o direito adquirido foi apurado na DER "
                       f"({T.txt(t_adq)} dias), não em 13/11/2019; as regras da EC 103 não vigoravam na DER.")
    adq_tc_tempo = filiado_adq and t_adq >= exig_tc

    def req_adq_tc(d):
        return {"filiacao": lambda: filiado_antes and e["data_filiacao"] <= d,
                "tempo": lambda: L.conv_em(d) >= exig_tc,
                "carencia": lambda: CAR.ok(d)}

    # Reconhecido no primeiro dia até a data da apuração em que tempo, filiação e carência (do ano desse dia,
    # art. 142) se cumprem juntos.
    d_adq, inc_adq = (varrer("adquirido-tc", req_adq_tc, max(e["data_filiacao"], nasc), ref_adq) if filiado_adq
                      else (None, None))
    st_adq_tc = status_ate(d_adq, inc_adq, ref_adq)
    adq_tc_ok = st_adq_tc is True
    linha = {"regra": "adquirido-tc", "aplicavel": filiado_antes, "fundamento": FUND["adquirido-tc"],
             "cumprida_na_der": st_adq_tc, "data_em_que_cumpre": None, "competencia_em_que_cumpre": None,
             "requisitos": {"tempo_exigido_dias": exig_tc, "tempo_em_13_11_2019_dias": T.num(t13),
                            "data_da_apuracao": ref_adq.isoformat(), "tempo_na_data_da_apuracao_dias": T.num(t_adq),
                            "carencia_exigida_competencias": CAR.exigidas(ref_adq),
                            "competencias_de_carencia_na_data_da_apuracao": CAR.ate(ref_adq),
                            "fundamento_carencia": FUND_CARENCIA}}
    if st_adq_tc is None:
        linha["indeterminada"] = True
        linha["veredito_por_leitura"] = {"requisito_nao_verificavel_desde": inc_adq.isoformat()}
    elif adq_tc_tempo and not adq_tc_ok:
        linha["motivo"] = (f"tempo cumprido, mas os períodos dão {CAR.ate(ref_adq)} competências de carência, menos "
                           f"que as {CAR.exigidas(ref_adq)} exigidas ({FUND_CARENCIA})")
    if adq_tc_ok:
        linha["data_em_que_cumpre"] = d_adq.isoformat()
        # §3º: magistério exclusivo soma cinco pontos (o tempo mínimo de 30/25 anos já é o exig_tc do professor).
        bonus29c = 5 if prof else 0

        def pontos29c(d):
            """Idade + tempo em d, frações em meses completos (art. 29-C, §1º), em meses."""
            a_, m_, _ = idade_componentes(nasc, d)
            r_ = T.representar(L.conv_em(d))
            return (a_ + r_["anos"] + bonus29c) * 12 + m_ + r_["meses"]

        # Art. 29-C, §2º, I: 95/85 até 30/12/2018; 96/86 desde 31/12/2018 (até 13/11/2019 não há outra majoração).
        majoracao = dt.date(2018, 12, 31)
        exig29c = (96 if sexo == "M" else 86) if ref_adq >= majoracao else (95 if sexo == "M" else 85)
        meses_tot = pontos29c(ref_adq)
        cumpre29c, data29c, exig_usado = meses_tot >= exig29c * 12, ref_adq, exig29c
        # §4º: quem alcançou a pontuação e não requereu conserva a opção com a pontuação exigida na data em que a
        # cumpriu. Antes de 31/12/2018 (§2º, I, primeira majoração) a exigência era 95/85. Os pontos só crescem
        # com o tempo, então basta o último dia anterior: 30/12/2018, com o tempo mínimo já cumprido nessa data.
        vespera = dt.date(2018, 12, 30)
        if not cumpre29c and ref_adq >= majoracao and d_adq and d_adq <= vespera:
            antes = pontos29c(vespera)
            if antes >= (exig29c - 1) * 12:
                cumpre29c, data29c, exig_usado, meses_tot = True, vespera, exig29c - 1, antes
        linha["art29C"] = {"cumpre": cumpre29c,
                           "pontos": f"{meses_tot // 12}a {meses_tot % 12}m",
                           "exigidos": exig_usado,
                           "data_da_pontuacao": data29c.isoformat(),
                           "acrescimo_professor": bonus29c,
                           "regra": "idade + tempo, frações em meses completos (Lei 8.213, art. 29-C, §1º), em "
                                    "13/11/2019 ou, se antes alcançada, na data em que a pontuação exigida foi "
                                    "cumprida (art. 29-C, §4º; 95/85 até 30/12/2018, §2º, I)"
                                    + ("; + 5 pontos e tempo mínimo de 30/25 anos do professor (art. 29-C, §3º)"
                                       if prof else "")}
        if not coberta("art29C", ref_adq):
            # O art. 29-C entrou pela MP 676/2015 e pela Lei 13.183/2015; a data de vigência não está datada em
            # context/lei/: antes de 2016 a opção sem fator não fecha (regra 2).
            abertas_adq["art29C_vigencia"] = {
                "linha_cobertura": "art29C",
                "expressao": "opção sem fator (art. 29-C) só se vigente na DER; senão, média × fator",
                "contas": {"pontos": f"{meses_tot // 12}a {meses_tot % 12}m", "exigidos": exig_usado,
                           "der": der.isoformat()},
                "faltando": ["data de vigência do art. 29-C da Lei 8.213 (MP 676/2015; Lei 13.183/2015), não "
                             "datada em context/lei/"]}
            alertas.append("[VERIFICAR] DER anterior a 2016: a vigência do art. 29-C (MP 676/2015; Lei "
                           "13.183/2015) não está datada em context/lei/; a opção sem fator fica aberta.")
        if data29c != ref_adq:
            memoria.append(f"Art. 29-C, §4º: em 30/12/2018 a soma era {meses_tot // 12}a {meses_tot % 12}m ≥ "
                           f"{exig_usado} pontos, com o tempo mínimo já cumprido: opção sem fator preservada.")
        a, m, _ = idade_componentes(nasc, ref_adq)
        rep = T.representar(t_adq)
        linha["coeficiente"] = "media x fator" if not linha["art29C"]["cumpre"] else "media (sem fator, art. 29-C)"
        linha["rmi"] = ("media_80_maiores x fator" if not linha["art29C"]["cumpre"]
                        else "media_80_maiores (sem fator)")
        # r14: com a opção do art. 29-C reconhecida, a conta não pede fator nem tábua do IBGE.
        if linha["art29C"]["cumpre"]:
            linha["formula"] = ("RMI = média dos 80% maiores salários de contribuição desde 07/1994, sem fator "
                                "previdenciário (opção do art. 29-C da Lei 8.213)")
            linha["faltando"] = ["salários de contribuição"]
        else:
            linha["formula"] = ("RMI = média dos 80% maiores salários de contribuição desde 07/1994 × fator "
                                "previdenciário (idade, expectativa de sobrevida e tempo em 13/11/2019; IN 128, "
                                "art. 229, §3º)")
            linha["faltando"] = ["tábua de mortalidade do IBGE (expectativa de sobrevida)",
                                 "salários de contribuição"]
        if prof and data29c == ref_adq:
            memoria.append(f"Art. 29-C, §3º (professor): idade {a}a {m}m + tempo {rep['anos']}a {rep['meses']}m "
                           f"+ 5 pontos = {meses_tot // 12}a {meses_tot % 12}m; exigidos {exig29c}; tempo mínimo "
                           f"{anos_tc} anos")
    elif not filiado_antes:
        linha["motivo"] = "filiação depois de 13/11/2019"
    regras["adquirido-tc"] = linha
    # r12: a regra dos 35/30 anos (EC 20) só vale desde 16/12/1998 e a média com fator (Lei 9.876) desde 29/11/1999.
    # A data verificada é a em que o direito se cumpre ou, sem ele, a da apuração.
    tc_fora = False
    if filiado_adq:
        chave_tc = d_adq if adq_tc_ok else ref_adq
        if not coberta("adquirido-tempo", chave_tc):
            sem_veredito(linha, "adquirido-tempo", chave_tc)
            tc_fora, adq_tc_ok = True, False
        elif adq_tc_ok and not coberta("adquirido-rmi-lei-9876", d_adq):
            marcar_fora("adquirido-rmi-lei-9876", d_adq)
            linha.update({"rmi": None, "formula": None, "coeficiente": None,
                          "rmi_fora_da_cobertura": "adquirido-rmi-lei-9876"})

    # Aposentadoria por idade (Lei 8.213, art. 48): idade + carência (art. 25, II; art. 142 para o inscrito até
    # 24/07/1991, pelo ano em que as duas condições se completam). Carência são competências, não tempo em dias.
    idade_adq = {"anos": 65 if sexo == "M" else 60, "meses": 0}
    def req_adq_id(d):
        return {"filiacao": lambda: filiado_antes and e["data_filiacao"] <= d,
                "idade": lambda: idade_ok(d, idade_adq),
                "carencia": lambda: CAR.ok(d)}

    d_id, inc_id = (varrer("adquirido-idade", req_adq_id, max(e["data_filiacao"], nasc), ref_adq) if filiado_adq
                    else (None, None))
    st_adq_id = status_ate(d_id, inc_id, ref_adq)
    adq_id_ok = st_adq_id is True
    # r12: a carência pela tabela do art. 142 (ano de implementação das condições) só vale desde a Lei 9.032/1995.
    chave_id = d_id if adq_id_ok else ref_adq
    id_fora = filiado_adq and not coberta("adquirido-carencia-142", chave_id)
    regras["adquirido-idade"] = {
        "regra": "adquirido-idade", "aplicavel": filiado_antes, "fundamento": FUND["adquirido-idade"],
        "cumprida_na_der": st_adq_id, "data_em_que_cumpre": d_id.isoformat() if adq_id_ok else None,
        "competencia_em_que_cumpre": None,
        "requisitos": {"idade_exigida": f"{idade_adq['anos']} anos",
                       "carencia_exigida_competencias": CAR.exigidas(d_id or ref_adq),
                       "competencias_de_carencia_na_data_da_apuracao": CAR.ate(ref_adq),
                       "tabela_art_142": CAR.tabela, "fundamento_carencia": FUND_CARENCIA,
                       "tempo_em_13_11_2019_dias": T.num(t13), "data_da_apuracao": ref_adq.isoformat(),
                       "tempo_na_data_da_apuracao_dias": T.num(t_adq)},
        "coeficiente": "70% + 1% por grupo de 12 contribuições, até 100% (Lei 8.213, art. 50)" if adq_id_ok else None,
    }
    if id_fora:
        sem_veredito(regras["adquirido-idade"], "adquirido-carencia-142", chave_id)
        adq_id_ok = False
    elif st_adq_id is None:
        regras["adquirido-idade"]["indeterminada"] = True
        regras["adquirido-idade"]["veredito_por_leitura"] = {"requisito_nao_verificavel_desde": inc_id.isoformat()}
    elif filiado_adq and idade_ok(ref_adq, idade_adq) and not adq_id_ok:
        regras["adquirido-idade"]["motivo"] = (
            f"idade cumprida, mas os períodos dão {CAR.ate(ref_adq)} competências de carência, menos que as "
            f"{CAR.exigidas(ref_adq)} exigidas ({FUND_CARENCIA})")
    if adq_id_ok:
        alertas.append("Direito adquirido à aposentadoria por idade: idade e competências de carência pelos "
                       "períodos informados (Lei 8.213, arts. 25, II, 48 e 142). O recolhimento em dia do "
                       "contribuinte individual e do facultativo (art. 27, II) é conferido pelo "
                       "calc_previdenciario_cnis.py.")
    # Proporcional da EC 20/1998 (art. 9º, §1º; revogada pela EC 103, aplicada pelo direito adquirido até 13/11/2019,
    # EC 103, art. 3º): filiado até a publicação, 53 (H) / 48 (M) anos, tempo de 30 (H) / 25 (M) anos mais 40% do
    # que faltava na publicação. r9: o texto está em context/lei/ec-20-1998.md; a conta sai fechada. QA final A04: a
    # publicação é 16/12/1998 (IN 128, art. 5º, IV; in-128-2022-inss.md:53), uma leitura só (PUBLICACAO_EC20).
    piso_prop = (30 if sexo == "M" else 25) * T.DIAS_ANO
    prop_possivel = (filiado_adq and not adq_tc_ok and not tc_fora and e["data_filiacao"] <= PUBLICACAO_EC20
                     and t_adq >= piso_prop)
    if e["data_filiacao"] <= PUBLICACAO_EC20:
        avaliadas["adquirido-proporcional-ec20"] = (
            "fora_da_cobertura (adquirido-tempo)" if tc_fora else
            "inaplicavel: sem filiação na data da apuração" if not filiado_adq else
            "nao_exigida: integral cumprida" if adq_tc_ok else
            f"nao_cumprida: tempo na apuração ({T.txt(t_adq)} dias) abaixo do piso de {piso_prop}" if not prop_possivel
            else None)
    prop_aberta = None
    if prop_possivel:
        idade_prop = {"anos": 53 if sexo == "M" else 48, "meses": 0}
        leituras = {}
        t_ref = Decimal(str(T.num(t_adq)))
        for pub in (PUBLICACAO_EC20,):
            t_pub = Decimal(str(T.num(L.conv_em(pub))))
            exigido = piso_prop + Decimal("0.4") * max(Decimal(0), piso_prop - t_pub)

            def req_prop(d, pub=pub, exigido=exigido):
                return {"filiacao_ate_publicacao": lambda: e["data_filiacao"] <= pub,
                        "idade": lambda: idade_ok(d, idade_prop),
                        "tempo": lambda: Decimal(str(T.num(L.conv_em(d)))) >= exigido,
                        "carencia": lambda: CAR.ok(d)}

            # r11: idade, tempo e carência no mesmo dia, entre a publicação e a data da apuração; a carência é a do
            # ano desse dia (art. 142 para o inscrito até 24/07/1991).
            d_prop, inc_prop = varrer("adquirido-proporcional-ec20", req_prop, pub, ref_adq)
            ok = status_ate(d_prop, inc_prop, ref_adq)
            # Ano em que idade e tempo se completam, para mostrar a carência exigida quando só ela falta.
            d_demais = primeira_data(lambda d, pub=pub, exigido=exigido: e["data_filiacao"] <= pub
                                     and idade_ok(d, idade_prop) and Decimal(str(T.num(L.conv_em(d)))) >= exigido,
                                     pub, ref_adq) if ok is False else None
            anos_alem = int((t_ref - exigido) // T.DIAS_ANO) if ok else None
            d_car = d_prop or d_demais or ref_adq
            leituras[pub.isoformat()] = {
                "tempo_na_publicacao_dias": T.num(t_pub), "tempo_exigido_dias": T.num(exigido),
                "tempo_na_data_da_apuracao_dias": T.num(t_ref), "cumprida": ok,
                "data_em_que_cumpre": d_prop.isoformat() if ok else None,
                "carencia_exigida_competencias": CAR.exigidas(d_car),
                "competencias_de_carencia": CAR.ate(d_prop or ref_adq),
                "carencia_cumprida": CAR.ok(d_prop) if d_prop else (CAR.ok(d_demais) if d_demais else None),
                "coeficiente": str(min(Decimal(100), 70 + 5 * Decimal(anos_alem)) / 100) if ok else None}
            if inc_prop is not None and ok is None:
                leituras[pub.isoformat()]["requisito_nao_verificavel_desde"] = inc_prop.isoformat()
        vereditos = {lt["cumprida"] for lt in leituras.values()}
        for lt in leituras.values():
            if lt["cumprida"] and not coberta("adquirido-rmi-lei-9876", dt.date.fromisoformat(lt["data_em_que_cumpre"])):
                marcar_fora("adquirido-rmi-lei-9876", dt.date.fromisoformat(lt["data_em_que_cumpre"]))
        avaliadas["adquirido-proporcional-ec20"] = ("indeterminada" if None in vereditos
                                                    else "cumprida" if True in vereditos else "nao_cumprida")
        idade_txt = f"{idade_prop['anos']} anos em {ref_adq.isoformat()}: {idade_ok(ref_adq, idade_prop)}"
        memoria.append("Proporcional da EC 20/1998 (art. 9º, I, e §1º, I, 'a' e 'b'): " + idade_txt + "; " + "; ".join(
            f"publicação em {k}: exigidos {v['tempo_exigido_dias']} dias, tinha {v['tempo_na_data_da_apuracao_dias']}"
            f" → {({True: 'cumprida', False: 'não cumprida'}).get(v['cumprida'], 'indeterminada')}" for k, v in leituras.items()))
        conta = {"expressao": "EC 20/1998, art. 9º, I, e §1º: idade 53 H / 48 M; tempo >= piso (30 H / 25 M anos) "
                              "+ 40% × (piso − tempo na publicação), até a data da apuração (EC 103, art. 3º); "
                              "coeficiente 70% + 5% por ano além do exigido, até 100% (§1º, II), multiplicado pelo "
                              "fator previdenciário (IN 128, art. 233, IV, 'b')",
                 "contas": {"data_da_apuracao": ref_adq.isoformat(), "idade_exigida": f"{idade_prop['anos']} anos",
                            "idade_cumprida": idade_ok(ref_adq, idade_prop), "piso_de_tempo_dias": piso_prop,
                            "leituras_da_publicacao": leituras}}
        if None in vereditos:
            # r11: requisito não verificável: a proporcional fica aberta qualquer que seja o resto da conta.
            conta["faltando"] = ["requisito da proporcional da EC 20/1998 não verificável pelos períodos informados"]
            abertas_adq["adquirido_proporcional_ec20"] = conta
            alertas.append("[VERIFICAR] Proporcional da EC 20/1998: requisito não verificável pelos períodos "
                           "informados; conta aberta.")
        elif True in vereditos:
            conta["faltando"] = ["fator previdenciário da DIB (IN 128, art. 233, IV, 'b'): sem a tábua do IBGE não "
                                 "há fator numérico"]
            prop_aberta = conta
            alertas.append("Direito adquirido à aposentadoria proporcional da EC 20/1998 (art. 9º, §1º): coeficiente "
                           + " / ".join(sorted({v["coeficiente"] for v in leituras.values()}))
                           + ", multiplicado pelo fator previdenciário (IN 128, art. 233, IV, 'b').")
        else:
            alertas.append("Proporcional da EC 20/1998 (art. 9º, I, e §1º, I) não cumprida até "
                           f"{ref_adq.strftime('%d/%m/%Y')}: " + "; ".join(
                               f"exigidos {v['tempo_exigido_dias']} dias (publicação em {k}), tinha "
                               f"{v['tempo_na_data_da_apuracao_dias']}"
                               + (f"; carência {v['competencias_de_carencia']} de {v['carencia_exigida_competencias']}"
                                  f" competências ({FUND_CARENCIA})" if v["carencia_cumprida"] is False else "")
                               for k, v in leituras.items())
                           + ("" if idade_ok(ref_adq, idade_prop) else f"; idade de {idade_prop['anos']} anos não "
                              "alcançada") + ".")

    # ---- art. 15 (pontos)
    r15 = R["art15_par3" if prof else "art15"]
    chave15 = "art15_par3_pontos_professor" if prof else "art15_pontos"

    def c15(d, norm, lei):
        return {"filiacao": filiado_antes,
                "tempo": lambda: L.conv_em(d, norm) >= exig_tc,
                "pontos": lambda: pontos_ok(lei, nasc, d, L.conv_em(d, norm), ano_tab(d)[chave15][sx]),
                "carencia": lambda: CAR.ok(d)}

    l15 = montar("art15", filiado_antes, "filiação depois de 13/11/2019", inicio_trans, c15,
                 tempo_cond_por_norm=lambda n: cond_tempo(n, exig_tc),
                 coef_fn=coef_padrao(lambda d: L.conv_em(d)), usa_pontos=True)
    if l15["aplicavel"]:
        dref = der
        l15["requisitos"] = {"tempo_exigido_dias": exig_tc, "pontos_exigidos_no_ano_da_der": ano_tab(dref)[chave15][sx],
                             "limiar_dias_na_der": ano_tab(dref)[chave15][sx] * T.DIAS_ANO,
                             "tempo_na_der_dias": T.num(L.conv_em(dref)),
                             "idade_na_der_dias": (dref - nasc).days,
                             "soma_dias_na_der": pontos_medida("B", nasc, dref, L.conv_em(dref)),
                             "soma_componentes_na_der": pontos_medida("A", nasc, dref, L.conv_em(dref))}

    # ---- art. 16 (idade progressiva)
    chave16 = "art16_par2_idade_professor" if prof else "art16_idade"

    def c16(d, norm, lei):
        return {"filiacao": filiado_antes,
                "tempo": lambda: L.conv_em(d, norm) >= exig_tc,
                "idade": lambda: idade_ok(d, ano_tab(d)[chave16][sx]),
                "carencia": lambda: CAR.ok(d)}

    l16 = montar("art16", filiado_antes, "filiação depois de 13/11/2019", inicio_trans, c16,
                 tempo_cond_por_norm=lambda n: cond_tempo(n, exig_tc),
                 coef_fn=coef_padrao(lambda d: L.conv_em(d)))
    if l16["aplicavel"]:
        req = ano_tab(der)[chave16][sx]
        l16["requisitos"] = {"tempo_exigido_dias": exig_tc,
                             "idade_exigida_no_ano_da_der": f"{req['anos']}a {req['meses']}m",
                             "idade_na_der": representar_texto(*idade_componentes(nasc, der)),
                             "tempo_na_der_dias": T.num(L.conv_em(der))}

    # ---- pedágios (arts. 17 e 20): falta medida em dias, adicional com a fração
    # O art. 17 não reduz nada para o professor: requisito (I) e déficit (II) são 30/35 anos
    # (EC 103, art. 17, I e II), mesmo com professor = true.
    mais_de = R["art17"]["tempo_em_13_11_2019_mais_de_anos"][sx] * T.DIAS_ANO
    exig_tc17 = R["art17"]["tempo_contribuicao_anos"][sx] * T.DIAS_ANO
    falta17 = max(Decimal(0), Decimal(exig_tc17) - t13)
    elegivel17 = filiado_antes and t13 > mais_de
    exig17 = falta17 * Decimal("1.5")

    def pedagio17(d, norm):
        return (d > MARCO and L.pos(d, norm) >= exig17) or (falta17 == 0 and d >= MARCO)

    def c17(d, norm, lei):
        return {"filiacao": filiado_antes,
                "tempo_em_13_11_2019": t13 > mais_de,
                "tempo": lambda: L.conv_em(d, norm) >= exig_tc17,
                "pedagio": lambda: pedagio17(d, norm),
                "carencia": lambda: CAR.ok(d)}

    motivo17 = ("filiação depois de 13/11/2019" if not filiado_antes else
                f"tempo em 13/11/2019 ({T.txt(t13)} dias) não é mais de {mais_de // T.DIAS_ANO} anos "
                f"({mais_de} dias): exigido 'mais de' (EC 103, art. 17, caput)")
    l17 = montar("art17", elegivel17, motivo17, MARCO, c17,
                 tempo_cond_por_norm=lambda n: (lambda d: pedagio17(d, n)))
    l17.update({"tempo_exigido_dias": exig_tc17, "deficit_dias": T.num(falta17),
                "adicional_dias": T.num(falta17 / 2), "acumulo_exigido_dias": T.num(exig17),
                "tempo_mais_de_exigido_dias": mais_de})
    if l17["aplicavel"]:
        l17["competencia_em_que_cumpre"] = l17.get("competencia_em_que_cumpre_tempo")
        l17["coeficiente"] = "media x fator"
        l17["formula"] = ("RMI = média × fator previdenciário (Lei 8.213, art. 29, §§7º a 9º); sem a tábua do "
                          "IBGE não há número (M7)")
        l17["faltando"] = ["tábua de mortalidade do IBGE (expectativa de sobrevida)", "média dos salários"]
        l17["acumulado_na_der_dias"] = {"padrao": L.pos(der, "padrao"), "30d": L.pos(der, "30d")}
        if prof:
            alertas.append(f"art. 17 sem regra própria de professor: déficit medido até {exig_tc17} dias "
                           f"({R['art17']['tempo_contribuicao_anos'][sx]} anos), sem a redução do magistério "
                           "(EC 103, art. 17, I e II).")

    # ---- art. 18 (idade)
    exig18 = R["art18"]["tempo_contribuicao_anos"][sx] * T.DIAS_ANO

    def c18(d, norm, lei):
        return {"filiacao": filiado_antes,
                "idade": lambda: idade_ok(d, ano_tab(d)["art18_idade"][sx]),
                "tempo": lambda: L.conv_em(d, norm) >= exig18,
                "carencia": lambda: CAR.ok(d)}

    l18 = montar("art18", filiado_antes, "filiação depois de 13/11/2019", inicio_trans, c18,
                 tempo_cond_por_norm=lambda n: cond_tempo(n, exig18),
                 coef_fn=coef_padrao(lambda d: L.conv_em(d)))
    if l18["aplicavel"]:
        req = ano_tab(der)["art18_idade"][sx]
        l18["requisitos"] = {"tempo_exigido_dias": exig18,
                             "idade_exigida_no_ano_da_der": f"{req['anos']}a {req['meses']}m",
                             "idade_na_der": representar_texto(*idade_componentes(nasc, der))}

    # ---- art. 19 (permanente) — r12 (revisão r11, BLOCKER 1): caput, §1º, II (professor) e §1º, I (especial) para
    # TODA filiação. O caput é do filiado depois de 13/11/2019; o filiado até essa data tem a mesma regra por opção
    # (Decreto 3.048, arts. 51, 54 e 64, ressalvados nos arts. 188-H a 188-P; IN 128, art. 249, §1º). Os §§1º, I e II,
    # não distinguem a filiação. A aplicabilidade de cada modalidade é dela, não do caput.
    def opcao(arts):
        return ({"opcao_do_filiado_ate_13_11_2019": f"Decreto 3.048, {arts}, ressalvado nos arts. 188-H a 188-P; "
                                                    "IN 128, art. 249, §1º"} if filiado_antes else None)

    r19 = R["art19"]
    exig19 = r19["tempo_contribuicao_anos"][sx] * T.DIAS_ANO

    def c19(d, norm, lei):
        return {"filiacao": e["data_filiacao"] <= d,
                "idade": lambda: idade_ok(d, r19["idade"][sx]),
                "tempo": lambda: L.conv_em(d, norm) >= exig19,
                "carencia": lambda: CAR.ok(d)}

    l19 = montar("art19", True, None, inicio_trans, c19, tempo_cond_por_norm=lambda n: cond_tempo(n, exig19),
                 coef_fn=coef_padrao(lambda d: L.conv_em(d)), extra=opcao("art. 51"))
    if l19["aplicavel"]:
        l19["requisitos"] = {"tempo_exigido_dias": exig19,
                             "idade_exigida": f"{r19['idade'][sx]['anos']}a {r19['idade'][sx]['meses']}m",
                             "idade_completa_em": somar_anos_meses(nasc, r19["idade"][sx]["anos"],
                                                                   r19["idade"][sx]["meses"]).isoformat()}

    r19p = R["art19_par1_II"]
    exig19p = r19p["tempo_contribuicao_anos"][sx] * T.DIAS_ANO

    def c19p(d, norm, lei):
        return {"filiacao": e["data_filiacao"] <= d,
                "idade": lambda: idade_ok(d, r19p["idade"][sx]),
                "tempo": lambda: L.conv_em(d, norm) >= exig19p,
                "carencia": lambda: CAR.ok(d)}

    l19p = montar("art19-professor", prof, "professor = false: nenhum tempo de magistério declarado", inicio_trans,
                  c19p, tempo_cond_por_norm=lambda n: cond_tempo(n, exig19p),
                  coef_fn=coef_padrao(lambda d: L.conv_em(d)), extra=opcao("art. 54"))
    if l19p["aplicavel"]:
        l19p["requisitos"] = {"tempo_exigido_dias": exig19p,
                              "idade_exigida": f"{r19p['idade'][sx]['anos']}a {r19p['idade'][sx]['meses']}m",
                              "idade_completa_em": somar_anos_meses(nasc, r19p["idade"][sx]["anos"],
                                                                    r19p["idade"][sx]["meses"]).isoformat()}

    # Especial permanente: por tipo, exposição do tipo + idade da atividade + carência, sem somar tipos diferentes
    # (a soma depende da conversão do Decreto 3.048, art. 66: aberta). Coeficiente do art. 26, §§2º e 5º.
    tipos_esp = sorted({p["tipo"] for p in periodos if p["tipo"] != "comum"}, key=lambda t: T.ANOS_ESPECIAL[t])
    idade19e = {x["atividade_anos"]: x["idade_anos"] for x in R["art19_par1_I"]["idade_por_atividade"]}
    melhores19e = []
    for tipo in tipos_esp:
        anos_exp = T.ANOS_ESPECIAL[tipo]
        exig_exp = anos_exp * T.DIAS_ANO
        idade_req = {"anos": idade19e[anos_exp], "meses": 0}

        def c19e(d, norm, lei, tipo=tipo, exig_exp=exig_exp, idade_req=idade_req):
            return {"filiacao": e["data_filiacao"] <= d,
                    "exposicao": lambda: L.exposicao_em(d, tipo, norm) >= exig_exp,
                    "idade": lambda: idade_ok(d, idade_req),
                    "carencia": lambda: CAR.ok(d)}

        regras.pop("art19-especial", None)
        l19e = montar("art19-especial", True, None, inicio_trans, c19e,
                      coef_fn=coef_padrao(lambda d: L.bruto_em(d), 15 if anos_exp == 15 else
                                          (20 if sexo == "M" else 15)), extra=opcao("art. 64"))
        l19e.update({"tipo_especial": tipo, "exposicao_exigida_dias": exig_exp,
                     "idade_exigida": f"{idade_req['anos']}a 0m",
                     "idade_completa_em": somar_anos_meses(nasc, idade_req["anos"], 0).isoformat(),
                     "tempo_no_calculo": "tempo de contribuição sem conversão (aposentadoria especial)"})
        melhores19e.append(dict(l19e))
    if melhores19e:
        cumpridas19e = [x for x in melhores19e if x.get("data_em_que_cumpre")]
        regras["art19-especial"] = (min(cumpridas19e, key=lambda x: x["data_em_que_cumpre"]) if cumpridas19e
                                    else melhores19e[0])
        if len(melhores19e) > 1:
            regras["art19-especial"]["por_tipo"] = [{"tipo_especial": x["tipo_especial"],
                                                    "data_em_que_cumpre": x["data_em_que_cumpre"]} for x in melhores19e]
        l19e = regras["art19-especial"]
        if len(tipos_esp) > 1 and l19e["aplicavel"] and not l19e.get("cumprida_na_der"):
            somado19 = [t for t in tipos_esp if L.exposicao_em(der, "*") >= T.ANOS_ESPECIAL[t] * T.DIAS_ANO
                        and idade_ok(der, {"anos": idade19e[T.ANOS_ESPECIAL[t]], "meses": 0}) and CAR.ok(der)]
            if somado19:
                l19e.update({"cumprida_na_der": None, "indeterminada": True,
                             "veredito_por_leitura": {"por_tipo_sem_somar": False, "exposicoes_somadas": True}})
                abertas_adq["art19_especial_soma_de_especiais"] = {
                    "expressao": "exposição = Σ períodos de cada especial convertidos para o tipo da atividade "
                                 "preponderante (Decreto 3.048, art. 66, §2º); cumpre se exposição ≥ anos do tipo, "
                                 "idade da atividade e carência (EC 103, art. 19, §1º, I)",
                    "contas": {"exposicao_somada_na_der_dias": T.num(L.exposicao_em(der, "*")),
                               "tipos_que_cumpririam": somado19},
                    "faltando": ["atividade preponderante e conversão entre especiais (Decreto 3.048, art. 66)"]}
    else:
        montar("art19-especial", False, "nenhum período especial informado", inicio_trans,
               lambda d, n, lt: {}, extra=opcao("art. 64"))

    # ---- art. 20 (pedágio de 100%)
    r20 = R["art20_par1" if prof else "art20"]
    exig20 = falta * 2

    def c20_tempo(d, norm):
        return (d > MARCO and L.pos(d, norm) >= exig20) or (falta == 0 and d >= MARCO)

    def c20(d, norm, lei):
        return {"filiacao": filiado_antes,
                "idade": lambda: idade_ok(d, r20["idade"][sx]),
                "tempo": lambda: L.conv_em(d, norm) >= exig_tc,
                "pedagio": lambda: c20_tempo(d, norm),
                "carencia": lambda: CAR.ok(d)}

    l20 = montar("art20", filiado_antes, "filiação depois de 13/11/2019", MARCO, c20,
                 tempo_cond_por_norm=lambda n: (lambda d: c20_tempo(d, n)))
    l20.update({"deficit_dias": T.num(falta), "adicional_dias": T.num(falta),
                "acumulo_exigido_dias": T.num(exig20)})
    if l20["aplicavel"]:
        l20["coeficiente"] = "1.00"
        l20["coeficiente_regra"] = "100% da média (EC 103, art. 26, §3º, I)"
        l20["idade_completa_em"] = somar_anos_meses(nasc, r20["idade"][sx]["anos"], r20["idade"][sx]["meses"]).isoformat()
        l20["acumulado_na_der_dias"] = {"padrao": L.pos(der, "padrao"), "30d": L.pos(der, "30d")}

    # ---- art. 21 (especial por pontos)
    if filiado_antes and tipos_esp:
        if len(tipos_esp) > 1:
            alertas.append("[VERIFICAR] Mais de um tipo de especial: o art. 21 foi verificado por tipo, sem somar "
                           "exposições de tipos diferentes (a soma depende da conversão e da atividade "
                           "preponderante do Decreto 3.048, art. 66).")
        melhores = []
        for tipo in tipos_esp:
            anos_exp = T.ANOS_ESPECIAL[tipo]
            pts = {15: 66, 20: 76, 25: 86}[anos_exp]
            for linha_t in R["art21"]["pontos_por_exposicao"]:
                if linha_t["exposicao_anos"] == anos_exp:
                    pts = linha_t["pontos"]
            exig_exp = anos_exp * T.DIAS_ANO

            def c21(d, norm, lei, tipo=tipo, pts=pts, exig_exp=exig_exp):
                return {"filiacao": filiado_antes,
                        "exposicao": lambda: L.exposicao_em(d, tipo, norm) >= exig_exp,
                        "pontos": lambda: pontos_ok(lei, nasc, d, L.bruto_em(d, norm), pts),
                        "carencia": lambda: CAR.ok(d)}

            regras.pop("art21", None)
            l21 = montar("art21", True, None, MARCO, c21,
                         coef_fn=coef_padrao(lambda d: L.bruto_em(d), 15 if anos_exp == 15 else
                                             (20 if sexo == "M" else 15)), usa_pontos=True)
            d_exp = primeira_data(lambda d, tipo=tipo, exig_exp=exig_exp: L.exposicao_em(d, tipo) >= exig_exp,
                                  min(L.f1_dias) if L.f1_dias else MARCO, horizonte)
            l21.update({"tipo_especial": tipo, "pontos_exigidos": pts, "limiar_dias": pts * T.DIAS_ANO,
                        "exposicao_exigida_dias": exig_exp,
                        "exposicao_completa_em": d_exp.isoformat() if d_exp else None,
                        "exposicao_completa_na_competencia": T.mes_txt(T.mes(d_exp)) if d_exp else None,
                        f"exposicao_{anos_exp}_anos_na_competencia": T.mes_txt(T.mes(d_exp)) if d_exp else None})
            dc = l21["data_em_que_cumpre"]
            if dc:
                d0 = dt.date.fromisoformat(dc)
                l21["soma_dias"] = pontos_medida("B", nasc, d0, L.bruto_em(d0))
                l21["vespera_soma_dias"] = pontos_medida("B", nasc, d0 - UM_DIA, L.bruto_em(d0 - UM_DIA))
                l21["sensibilidade_normalizacao_30d"] = l21.get("leituras", {}).get("datas", {}).get("30d/B")
                civ = primeira_data(lambda d, tipo=tipo, exig_exp=exig_exp, pts=pts:
                                    CAR.ok(d) and L.exposicao_em(d, tipo) >= exig_exp
                                    and (d - nasc).days + L.civil_bruto(d) >= pts * T.DIAS_ANO, MARCO, horizonte)
                l21["sensibilidade_civil"] = civ.isoformat() if civ and civ != d0 else None
            l21["tempo_no_calculo"] = "tempo de contribuição sem conversão (aposentadoria especial)"
            l21["metodologia"] = "competência integral, IN 128 art. 206 §2º, aplicada à exposição"
            melhores.append(dict(l21))
        cumpridas = [x for x in melhores if x.get("data_em_que_cumpre")]
        regras["art21"] = min(cumpridas, key=lambda x: x["data_em_que_cumpre"]) if cumpridas else melhores[0]
        if len(melhores) > 1:
            regras["art21"]["por_tipo"] = [{"tipo_especial": x["tipo_especial"],
                                            "data_em_que_cumpre": x["data_em_que_cumpre"]} for x in melhores]
        if len(tipos_esp) > 1 and regras["art21"]["aplicavel"] and not regras["art21"].get("cumprida_na_der"):
            # Regra 2: nenhum tipo sozinho cumpre na DER; somadas as exposições (cada dia uma vez), algum
            # cumpriria? Se sim, o veredito depende da conversão do Decreto 3.048, art. 66, que exige a
            # atividade preponderante: conta aberta.
            somado = [t for t in tipos_esp
                      if L.exposicao_em(der, "*") >= T.ANOS_ESPECIAL[t] * T.DIAS_ANO
                      and pontos_ok("B", nasc, der, L.bruto_em(der), {15: 66, 20: 76, 25: 86}[T.ANOS_ESPECIAL[t]])]
            if somado:
                regras["art21"]["cumprida_na_der"] = None
                regras["art21"]["indeterminada"] = True
                regras["art21"]["veredito_por_leitura"] = {"por_tipo_sem_somar": False,
                                                           "exposicoes_somadas": True}
                abertas_adq["art21_soma_de_especiais"] = {
                    "expressao": "exposição = Σ períodos de cada especial convertidos para o tipo da atividade "
                                 "preponderante (Decreto 3.048, art. 66, §2º); cumpre se exposição ≥ anos do tipo "
                                 "e idade + tempo ≥ pontos (EC 103, art. 21)",
                    "contas": {"exposicao_somada_na_der_dias": T.num(L.exposicao_em(der, "*")),
                               "tipos_que_cumpririam": somado},
                    "faltando": ["atividade preponderante e conversão entre especiais (Decreto 3.048, art. 66)"]}
                alertas.append("[VERIFICAR] Art. 21: nenhum tipo de especial cumpre sozinho na DER, mas a soma das "
                               "exposições cumpriria (" + ", ".join(somado) + "): depende da conversão do "
                               "Decreto 3.048, art. 66.")
        # Regra 2: aposentadoria especial do art. 57 da Lei 8.213 por direito adquirido (EC 103, art. 3º):
        # exposição completa até a DER (ou 13/11/2019). O script não a calcula: se pode estar cumprida, aberta.
        if filiado_adq:
            esp_adq = [t for t in tipos_esp if L.exposicao_em(ref_adq, t) >= T.ANOS_ESPECIAL[t] * T.DIAS_ANO]
            soma_adq = (len(tipos_esp) > 1 and not esp_adq
                        and L.exposicao_em(ref_adq, "*") >= min(T.ANOS_ESPECIAL[t] for t in tipos_esp) * T.DIAS_ANO)

            def exposicao_adq(d):
                if any(L.exposicao_em(d, t) >= T.ANOS_ESPECIAL[t] * T.DIAS_ANO for t in tipos_esp):
                    return True
                if len(tipos_esp) > 1 and L.exposicao_em(d, "*") >= min(T.ANOS_ESPECIAL[t] for t in tipos_esp) \
                        * T.DIAS_ANO:
                    return None   # só somando tipos diferentes: depende da conversão (Decreto 3.048, art. 66)
                return False

            def req_adq_esp(d):
                return {"filiacao": lambda: e["data_filiacao"] <= d, "exposicao": lambda: exposicao_adq(d),
                        "carencia": lambda: CAR.ok(d)}

            # r11: exposição e carência (do ano em que se completam, art. 142) no mesmo dia, até a apuração.
            d_esp, inc_esp = varrer("adquirido-especial", req_adq_esp, max(e["data_filiacao"], nasc), ref_adq)
            st_esp = status_ate(d_esp, inc_esp, ref_adq)
            # r12: carência pela tabela do art. 142 só desde a Lei 9.032/1995 (COBERTURA adquirido-carencia-142).
            chave_esp = d_esp if st_esp else ref_adq
            esp_fora = not coberta("adquirido-carencia-142", chave_esp)
            if esp_fora:
                marcar_fora("adquirido-carencia-142", chave_esp)
            avaliadas["adquirido-especial"] = ("fora_da_cobertura (adquirido-carencia-142)" if esp_fora else
                                               {True: "aberta: requisitos verificados (renda não calculada)",
                                                None: "indeterminada", False: "nao_cumprida"}[st_esp])
            if (esp_adq or soma_adq) and st_esp is False and not esp_fora:
                alertas.append("Exposição especial completa até " + ref_adq.strftime("%d/%m/%Y") + ", mas os "
                               f"períodos dão {CAR.ate(ref_adq)} competências de carência, menos que as exigidas "
                               f"({FUND_CARENCIA}): sem direito adquirido à aposentadoria especial (Lei 8.213, "
                               "art. 57).")
            if st_esp is not False or esp_fora:
                abertas_adq["adquirido_especial"] = {
                    "expressao": "aposentadoria especial: 15, 20 ou 25 anos de exposição cumpridos até "
                                 f"{ref_adq.isoformat()}, carência cumprida; renda de 100% do salário de "
                                 "benefício (Lei 8.213, art. 57, caput e §1º; EC 103, art. 3º)",
                    "contas": {"data_da_apuracao": ref_adq.isoformat(),
                               "exposicao_por_tipo_dias": {t: T.num(L.exposicao_em(ref_adq, t)) for t in tipos_esp},
                               "tipos_com_exposicao_completa": esp_adq,
                               "requisitos": ("fora da cobertura (adquirido-carencia-142)" if esp_fora else
                                              ("verificados em " + d_esp.isoformat()) if st_esp
                                              else "indeterminados desde " + inc_esp.isoformat()),
                               "carencia_exigida_competencias": CAR.exigidas(d_esp or ref_adq),
                               "competencias_de_carencia_na_data_da_apuracao": CAR.ate(ref_adq)},
                    "faltando": ["aposentadoria especial do art. 57 (direito adquirido) não calculada por este "
                                 "script", "recolhimento em dia do contribuinte individual e do facultativo (Lei "
                                 "8.213, art. 27, II; calc_previdenciario_cnis.py)"]
                                + (["conversão entre especiais (Decreto 3.048, art. 66)"] if soma_adq else [])}
                alertas.append("[VERIFICAR] Exposição especial completa até " + ref_adq.strftime("%d/%m/%Y")
                               + ": possível direito adquirido à aposentadoria especial (Lei 8.213, art. 57; EC 103, "
                               "art. 3º), que este script não calcula.")
    else:
        regras["art21"] = {"regra": "art21", "aplicavel": False, "fundamento": FUND["art21"],
                           "motivo": "filiação depois de 13/11/2019" if not filiado_antes
                           else "nenhum período especial informado",
                           "cumprida_na_der": False, "data_em_que_cumpre": None,
                           "competencia_em_que_cumpre": None, "coeficiente": None}

    # ---- sensibilidade civil das datas (não é saída): tempo data a data também depois da EC, e os anos
    # contados pelo calendário (CC, art. 132, §3º): N anos fecham no dia d quando o tempo cobre todos os dias
    # dos N anos civis que terminam em d (anos bissextos inclusive), não N × 365 dias.
    for rid, exig in (("art19", exig19), ("art18", exig18)):
        lr = regras[rid]
        if lr.get("aplicavel") and lr.get("data_em_que_cumpre"):
            req_idade = r19["idade"][sx] if rid == "art19" else None
            anos_exig = exig // T.DIAS_ANO
            civ = primeira_data(lambda d: CAR.ok(d) and L.civil_conv(d) >= dias_dos_anos_civis(d, anos_exig) and
                                (idade_ok(d, req_idade) if req_idade else idade_ok(d, ano_tab(d)["art18_idade"][sx])),
                                inicio_trans if rid == "art18" else e["data_filiacao"], horizonte)
            if civ and civ.isoformat() != lr["data_em_que_cumpre"]:
                lr["sensibilidade_civil"] = civ.isoformat()

    if filiado_antes and tipos_esp and not filiado_adq:
        avaliadas["adquirido-especial"] = "inaplicavel: sem filiação na data da apuração"
    # r12: tempo com especial convertido usado num requerimento anterior à tabela do art. 188-P, §5º (Decreto 10.410,
    # de 30/06/2020): os multiplicadores eram os do art. 70, revogado e não capturado. Toda regra que mede tempo
    # convertido fica sem veredito (COBERTURA conversao-188P).
    convertido = any(p["tipo"] != "comum" and p["inicio"] <= MARCO for p in periodos)
    if convertido and not coberta("conversao-188P", der):
        for rid in cobertura("conversao-188P")["regras"]:
            if rid in regras and regras[rid].get("aplicavel"):
                sem_veredito(regras[rid], "conversao-188P", der)
            elif rid == "adquirido-proporcional-ec20" and avaliadas.get(rid) and "fora" not in avaliadas[rid]:
                marcar_fora("conversao-188P", der)
                avaliadas[rid] = "fora_da_cobertura (conversao-188P)"
    if fora_cob:
        abertas_adq["fora_da_cobertura"] = {
            "expressao": "a regra vigente na data verificada decide; a implementada só vale dentro da cobertura",
            "pontos": fora_cob,
            "faltando": ["regra vigente na data de cada ponto listado (regra_historica), fora da cobertura do script"],
            "instrucao": "Refazer a regra pela regra histórica indicada, com a fonte de cada borda (COBERTURA do "
                         "script)."}
        alertas.append("[VERIFICAR] Regra verificada fora do intervalo em que é a vigente: "
                       + "; ".join(f"{x['linha']} ({x.get('data_da_apuracao') or x.get('der')})" for x in fora_cob)
                       + ". Sem veredito pela regra posterior: veja formula_aberta.fora_da_cobertura.")

    # ---- ordem, resumo, mais vantajosa
    regras = {k: regras[k] for k in ORDEM}
    perfis, exigidas_alt = alternativas_exigidas(e)
    for rid in exigidas_alt:
        if rid in regras:
            lr = regras[rid]
            avaliadas[rid] = (("indeterminada" if lr.get("indeterminada") else
                               "cumprida" if lr.get("cumprida_na_der") else "nao_cumprida_na_der")
                              if lr.get("aplicavel") else f"inaplicavel: {lr.get('motivo')}")
    alternativas = {"perfis": perfis, "exigidas": exigidas_alt,
                    "avaliadas": {rid: avaliadas.get(rid) for rid in exigidas_alt},
                    "nao_avaliadas": [rid for rid in exigidas_alt if avaliadas.get(rid) is None],
                    "nao_suportadas": list(NAO_SUPORTADAS)}
    if CAR.ate(der) < CAR.exigidas(der):
        alertas.append(f"Carência: os períodos dão {CAR.ate(der)} competências até a DER, menos que as "
                       f"{CAR.exigidas(der)} exigidas ({FUND_CARENCIA}). Nenhuma aposentadoria se cumpre antes de "
                       "completá-las; as datas futuras já contam com elas.")
    memoria.append(f"Carência: {CAR.ate(der)} competências cobertas pelos períodos até a DER; exigidas "
                   f"{CAR.exigidas(der)} ({FUND_CARENCIA}" + ("; tabela do art. 142 para o inscrito até 24/07/1991"
                                                             if CAR.tabela else "") + ")")
    tempo_der = L.conv_em(der)
    saida_norm30 = None
    if T.f3_dias(L.n_f3(der)) != T.f3_dias(L.n_f3(der), "30d"):
        t30 = L.conv_em(der, "30d")
        saida_norm30 = {"tempo_na_der_dias": T.num(t30), "anos_completos": int(t30 // T.DIAS_ANO),
                        "tempo_na_der": T.representar(t30)["texto"]}
        for rid in ("art15", "art16", "art18", "art19", "art19-professor"):
            lr = regras[rid]
            if lr.get("aplicavel") and lr.get("cumprida_na_der"):
                c, _ = coeficiente(t30, sexo)
                saida_norm30[rid] = str(c.quantize(Decimal("0.01")))
        alertas.append("[VERIFICAR] Normalização das competências desde 12/2019: padrão (12 = 365 dias) × 30 por "
                       f"competência; tempo na DER {T.txt(tempo_der)} × {T.txt(L.conv_em(der, '30d'))} dias. "
                       "A IN 128 não decide; as duas saem.")

    numericas = {k: coef_numerico(v.get("coeficiente")) for k, v in regras.items()
                 if v.get("cumprida_na_der") and coef_numerico(v.get("coeficiente")) is not None}
    com_fator = [k for k, v in regras.items() if v.get("cumprida_na_der") and depende_do_fator(v.get("coeficiente"))]
    por_formula = [k for k, v in regras.items() if v.get("cumprida_na_der") and v.get("coeficiente")
                   and coef_numerico(v["coeficiente"]) is None and k not in com_fator]
    indeterminadas = [k for k, v in regras.items() if v.get("indeterminada")]
    # r13 (revisão r12, MAJOR 1): a proporcional da EC 20/1998 preservada pelo direito adquirido (EC 103, art. 3º) é
    # alternativa como as outras. O coeficiente menor não prova renda menor: ele multiplica o fator previdenciário
    # (IN 128, art. 233, IV, 'b'), sem número sem a tábua do IBGE (M7). Cumprida, entra na comparação como regra com
    # fator; com requisito não verificável, como indeterminada. Nunca sai da saída.
    prop_status = avaliadas.get(PROP) if prop_aberta else None
    prop_indeterminada = [PROP] if prop_status == "indeterminada" else []
    alternativas_cumpridas = {k: v.get("coeficiente") for k, v in regras.items() if v.get("cumprida_na_der")}
    if prop_status == "cumprida":
        com_fator.append(PROP)
        coef_prop = sorted({lt["coeficiente"] for lt in prop_aberta["contas"]["leituras_da_publicacao"].values()
                            if lt.get("coeficiente")})
        alternativas_cumpridas[PROP] = " / ".join(coef_prop) + " x fator"
    if numericas:
        maior = max(numericas.values())
        topo = [k for k, v in numericas.items() if v == maior]
    else:
        maior, topo = None, []
    if com_fator or por_formula or prop_indeterminada:
        mais_vantajosa = {"tipo": "comparacao_aberta", "maior_coeficiente": topo,
                          "coeficiente": str(maior) if maior is not None else None, "com_fator": com_fator,
                          "coeficiente_por_formula": por_formula,
                          "motivo": "sem a tábua do IBGE não há fator previdenciário numérico (M7); coeficiente "
                                    "por fórmula depende das contribuições (CNIS)"}
    elif topo:
        mais_vantajosa = {"tipo": "por_coeficiente", "regras": topo, "coeficiente": str(maior)}
    else:
        mais_vantajosa = {"tipo": "nenhuma_cumprida_na_der", "regras": []}
    mais_vantajosa["alternativas_cumpridas"] = alternativas_cumpridas
    if indeterminadas or prop_indeterminada:
        mais_vantajosa["indeterminadas"] = indeterminadas + prop_indeterminada

    if prop_aberta:
        abertas_adq["adquirido_proporcional_ec20"] = prop_aberta
    if com_fator or prop_indeterminada:
        # Exit 3 (F1/M7): a mais vantajosa não fecha; cada alternativa cumprida sai com a sua fórmula.
        abertas_adq["mais_vantajosa"] = {
            "expressao": "mais vantajosa = maior renda entre as alternativas cumpridas; coeficiente x média, e x "
                         "fator previdenciário onde a regra o exige",
            "alternativas_cumpridas": alternativas_cumpridas,
            "indeterminadas": indeterminadas + prop_indeterminada,
            "faltando": ["tábua de mortalidade do IBGE (fator previdenciário)", "salários de contribuição"],
            "instrucao": "Comparar a renda de cada alternativa listada; nenhuma é descartada pelo coeficiente."}
    memoria.append(f"Tempo na DER {der.isoformat()}: {T.txt(tempo_der)} dias = {T.representar(tempo_der)['texto']} "
                   "(padrão)")
    for rid, lr in regras.items():
        if lr.get("aplicavel"):
            memoria.append(f"{rid}: cumprida na DER = {lr.get('cumprida_na_der')}; data em que cumpre = "
                           f"{lr.get('data_em_que_cumpre')}; coeficiente = {lr.get('coeficiente')}")
        else:
            memoria.append(f"{rid}: inaplicável ({lr.get('motivo')})")

    # O coeficiente por fórmula (art. 50, direito adquirido sem fator) sai como fórmula em formula_aberta, sem
    # abrir o exit: context/calculo-transicao.md lista o exit 3 e não o inclui. As contas abertas acima, sim.
    # 11/2019 entra na mesma conta (revisão r7, MAJOR 3): o tempo da F2 também depende do somatório.
    abaixo_conc = ([(2019, 11)] if ap.nov_abaixo_concomitante else []) + list(ap.f3_abaixo_concomitante)
    if abaixo_conc:
        # Regra 2: mês abaixo do mínimo em cada um de 2+ vínculos concomitantes pode alcançar o mínimo no somatório
        # (Decreto 3.048, art. 19-E, §1º; IN 128, art. 209, §1º): o tempo e as datas não fecham numa leitura só.
        abertas_adq["somatorio_concomitante"] = {
            "expressao": "competência conta se a soma das remunerações do mês em todos os vínculos >= mínimo",
            "contas": {"competencias": [T.mes_txt(m) for m in abaixo_conc]},
            "faltando": ["somatório das remunerações do mês nos vínculos concomitantes"]}
        alertas.append("[VERIFICAR] Competências abaixo do mínimo em cada um de dois ou mais vínculos concomitantes ("
                       + ", ".join(T.mes_txt(m) for m in abaixo_conc) + "): o somatório das "
                       "remunerações do mês pode alcançar o mínimo (Decreto 3.048, art. 19-E, §1º).")
    codigo = EXIT_FALTA if indeterminadas or com_fator or abertas_adq else EXIT_OK
    formula_aberta = None
    if abertas_adq:
        formula_aberta = dict(abertas_adq)
    if indeterminadas or com_fator:
        formula_aberta = formula_aberta or {}
        if indeterminadas:
            formula_aberta["veredito_depende_da_leitura"] = {
                k: regras[k].get("veredito_por_leitura") for k in indeterminadas}
            formula_aberta["instrucao_veredito"] = ("A escolha entre as leituras muda o veredito na DER: o advogado "
                                                    "decide (context/calculo-transicao.md, seção 3).")
        if com_fator:
            formula_aberta["fator_previdenciario"] = {
                "expressao": "RMI = média × fator (Lei 8.213, art. 29, §§7º a 9º; Lei 9.876, Anexo)",
                "faltando": ["tábua de mortalidade do IBGE", "salários de contribuição"],
                "regras": com_fator}
    if por_formula:
        formula_aberta = formula_aberta or {}
        formula_aberta["coeficiente_por_formula"] = {
            k: {"expressao": regras[k]["coeficiente"], "faltando": ["número de contribuições (CNIS)"]}
            for k in por_formula}
    if premissas:
        alertas.extend(premissas)
    depois = [k for k, v in regras.items() if v.get("data_em_que_cumpre")
              and dt.date.fromisoformat(v["data_em_que_cumpre"]) > ultimo_fim]
    if depois and not e["projecao_continua"]:
        alertas.append("Datas depois do último período informado (" + ", ".join(depois) + ") supõem que não há "
                       "contribuição nova: só a idade avança. Para projetar contribuições, use projecao_continua.")

    # Resumo no topo: a primeira regra com coeficiente numérico a se cumprir (empate: maior coeficiente).
    # A mais vantajosa na DER é outra pergunta e sai em mais_vantajosa.
    candidatas = [(v["data_em_que_cumpre"], -coef_numerico(v.get("coeficiente")), k) for k, v in regras.items()
                  if v.get("aplicavel") and v.get("data_em_que_cumpre")
                  and coef_numerico(v.get("coeficiente")) is not None]
    principal = min(candidatas)[2] if candidatas else None
    lp = regras.get(principal, {}) if principal else {}
    datas_l = (lp.get("leituras") or {}).get("datas", {})
    leituras_topo = None
    if lp:
        leituras_topo = {"regra": principal,
                         "padrao_12_competencias_365": {k: lp.get(k) for k in ("data_em_que_cumpre", "soma_dias",
                                                                                "vespera_soma_dias") if k in lp},
                         "alternativa_30d_por_competencia": {"data_em_que_cumpre": datas_l.get("30d/B",
                                                                                                lp.get("data_em_que_cumpre"))}}
        if "padrao/A" in datas_l:
            leituras_topo["pontos_por_componentes"] = {"data_em_que_cumpre": datas_l.get("padrao/A")}
    # Regra 2: a data em que a regra se cumpre (a da regra principal e a de cada regra cumprida na DER) não pode
    # depender da normalização das competências, que o anexo deixa aberta: se muda, exit 3 com as duas.
    por_norma = {}
    for k, v in regras.items():
        ds = (v.get("leituras") or {}).get("datas", {})
        if v.get("aplicavel") and (k == principal or v.get("cumprida_na_der")) and "30d/B" in ds \
                and ds.get("padrao/B") != ds["30d/B"]:
            por_norma[k] = {"padrao_12_competencias_365": ds.get("padrao/B"), "alternativa_30d_por_competencia": ds["30d/B"]}
    if por_norma:
        codigo = EXIT_FALTA
        formula_aberta = formula_aberta or {}
        formula_aberta["data_depende_da_normalizacao"] = {
            "expressao": "competências desde 12/2019 em dias: ⌊n/12⌋ × 365 + (n mod 12) × 30 (padrão) OU n × 30",
            "datas": por_norma,
            "faltando": ["operação que junta dias e competências (IN 128, art. 207; context/calculo-tempo.md, "
                         "seção 3)"]}
        if saida_norm30 is not None and principal in por_norma:
            d30 = dt.date.fromisoformat(por_norma[principal]["alternativa_30d_por_competencia"]) \
                if por_norma[principal]["alternativa_30d_por_competencia"] else None
            saida_norm30.update({"regra": principal, "primeira_der": d30.isoformat() if d30 else None,
                                 "competencia_em_que_cumpre": T.mes_txt(T.mes(d30)) if d30 else None})
    adq = regras["adquirido-tc"]
    saida_tipo = "fórmula sem a tábua" if com_fator and not numericas else ("calculado" if numericas else
                                                                            "nenhuma regra cumprida na DER")

    saida = {
        "versao": VERSAO,
        "parametros_usados": parametros,
        "transicoes_aplicavel": filiado_antes,
        "adquirido_tc": bool(adq.get("cumprida_na_der")),
        "art29C": adq.get("art29C"),
        "rmi": adq.get("rmi"),
        "saida": saida_tipo,
        "regra_principal": principal,
        "coeficiente": lp.get("coeficiente") if lp else None,
        "leituras": leituras_topo,
        "sensibilidade_civil": lp.get("sensibilidade_civil") if lp else None,
        "tempo_em_2019_11_13": T.representar(t13)["texto"],
        "tempo_em_13_11_2019_dias": T.num(t13),
        "tempo_em_13_11_2019": T.representar(t13)["texto"],
        "deficit_dias": T.num(falta),
        "tempo_na_der_dias": T.num(tempo_der),
        "tempo_na_der": T.representar(tempo_der)["texto"],
        "idade_na_der": representar_texto(*idade_componentes(nasc, der)),
        "regras": list(regras),
        **regras,
        "sensibilidade_normalizacao_30d": saida_norm30,
        "alternativas": alternativas,
        "mais_vantajosa": mais_vantajosa,
        "regra": "Cada regra verificada dia a dia desde 13/11/2019 (ou desde a filiação, no art. 19); "
                 "tempo em dias pela IN 128 (arts. 206 e 207); requisitos ano a ano de transicoes-ec103.json; "
                 "coeficiente sem teto de 100% (M3); pedágio com a fração, cumprido por inteiro (M2).",
        "fonte": fonte,
        "alertas": alertas,
        "memoria": memoria,
        "formula_aberta": formula_aberta,
    }
    return codigo, saida, ap


# ------------------------------------------------------------ CLI

def build_parser():
    ap = argparse.ArgumentParser(
        prog="calc_previdenciario_transicao.py",
        description="Direito adquirido, transições da EC 103 e regra permanente. Entrada JSON por --entrada "
                    "ou stdin; campos em context/calculo-transicao.md.")
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
    except T.TabelaIndisponivel as err:
        codigo, saida = _tabela_ausente(err)
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
