#!/usr/bin/env python3
"""calc_previdenciario_rpv.py — atrasados, honorários, RPV × precatório e regime de atualização.

Conta aberta, fontes e CAMPOS: context/calculo-rpv.md.

USO:
    python3 calc_previdenciario_rpv.py --entrada caso.json
    echo '{...}' | python3 calc_previdenciario_rpv.py
    python3 calc_previdenciario_rpv.py --versao

Saída: JSON no stdout. Exit 0 = calculado; 2 = entrada inválida;
3 = falta dado ou tabela, ou há trecho em fatias_em_aberto (devolve a
fórmula aberta e a lista completa de dados_faltantes, nunca estima).

Só biblioteca padrão, Python 3.9+, sem rede. Tabela e motores são achados pela
pasta deste arquivo: ../data/salario-minimo.json, o motor de atualização
(calc_previdenciario_atualizacao.py: R1 pelo Manual CJF 2026 e R2 pela Res.
CJF 983/2026) e o motor de prazos (calc_previdenciario_prazo.py: 5º dia útil e
prazo de pagamento da RPV).
"""

import argparse
import calendar
import datetime as dt
import importlib.util
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

VERSAO = "2.0.0"
EXIT_OK, EXIT_ENTRADA, EXIT_FALTA = 0, 2, 3

PASTA = Path(__file__).resolve().parent
MOTOR_ATUALIZACAO = PASTA / "calc_previdenciario_atualizacao.py"
MOTOR_PRAZO = PASTA / "calc_previdenciario_prazo.py"
TABELA_SALARIO_MINIMO = PASTA.parent / "data" / "salario-minimo.json"

# Contrato da entrada (context/calculo-rpv.md, seção 8). A skill declara o mesmo conjunto no
# bloco ```campos```; tests/test_contrato_flags.py compara os dois.
CAMPOS = {
    "natureza": {"tipo": "enum", "obrigatorio": "sim", "valores": "previdenciaria|assistencial"},
    "rito": {"tipo": "enum", "obrigatorio": "sim", "valores": "JEF|comum"},
    "parcelas": {"tipo": "lista", "obrigatorio": "uma das formas de atrasados (1)",
                 "valores": "uma entrada por competência"},
    "parcelas[].competencia": {"tipo": "competencia", "obrigatorio": "sim", "valores": "-"},
    "parcelas[].devido": {"tipo": "decimal", "obrigatorio": "sim", "valores": "-"},
    "parcelas[].pago": {"tipo": "decimal", "obrigatorio": "nao", "valores": "padrão \"0.00\""},
    "diferenca_mensal": {"tipo": "decimal", "obrigatorio": "uma das formas de atrasados (2)",
                         "valores": "com competencia_inicial e competencia_final"},
    "competencia_inicial": {"tipo": "competencia", "obrigatorio": "com diferenca_mensal", "valores": "-"},
    "competencia_final": {"tipo": "competencia", "obrigatorio": "com diferenca_mensal", "valores": "-"},
    "data_citacao": {"tipo": "data", "obrigatorio": "sim quando há atrasados",
                     "valores": "termo inicial dos juros"},
    "data_sentenca": {"tipo": "data", "obrigatorio": "sim quando há honorários sucumbenciais por percentual",
                      "valores": "corte da Súmula 111"},
    "data_base_conta": {"tipo": "competencia", "obrigatorio": "sim quando há atrasados",
                        "valores": "data-base informada pelo juízo (fim de R1, início de R2)"},
    "valor_consolidado_12_2021": {"tipo": "decimal", "obrigatorio": "nao",
                                  "valores": "principal consolidado em dez./2021, quando já apurado"},
    "juros_consolidados_12_2021": {"tipo": "decimal", "obrigatorio": "nao",
                                   "valores": "juros até 12/2021, com valor_consolidado_12_2021"},
    "data_expedicao": {"tipo": "data", "obrigatorio": "nao", "valores": "expedição do requisitório"},
    "data_apresentacao": {"tipo": "data", "obrigatorio": "nao",
                          "valores": "apresentação/entrega ao tribunal; define o corte, o prazo e a graça"},
    "data_transmissao": {"tipo": "data", "obrigatorio": "sim quando há valor_atualizado_ate_transmissao",
                         "valores": "marco do limite da RPV (M4)"},
    "data_pagamento": {"tipo": "data", "obrigatorio": "nao",
                       "valores": "sem ela, R2 sai em fórmula com a lista de faltantes"},
    "valor_atualizado_ate_transmissao": {"tipo": "decimal", "obrigatorio": "nao",
                                         "valores": "valor do motor de atualização até a transmissão"},
    "honorarios_percentual": {"tipo": "decimal", "obrigatorio": "nao",
                              "valores": "percentual dos sucumbenciais sobre a base da Súmula 111"},
    "honorarios_sucumbenciais": {"tipo": "decimal", "obrigatorio": "nao",
                                 "valores": "valor já fixado (alternativa ao percentual)"},
    "honorarios_contratuais": {"tipo": "decimal", "obrigatorio": "nao",
                               "valores": "valor destacado; integra o crédito na classificação"},
    "renunciar_excedente": {"tipo": "bool", "obrigatorio": "nao", "valores": "padrão false"},
    "titulo_com_criterio_proprio": {"tipo": "texto", "obrigatorio": "nao",
                                    "valores": "se houver, o script alerta que o título prevalece"},
    "salario_minimo": {"tipo": "decimal", "obrigatorio": "nao",
                       "valores": "ausente = tabela pela data da transmissão"},
    "datas_vencimento": {"tipo": "objeto", "obrigatorio": "nao",
                         "valores": "{\"AAAA-MM\": \"AAAA-MM-DD\"}: vencimento individual devido da competência "
                                    "(data em que deveria ter sido paga, Lei 8.213, art. 103, parágrafo único; CPC, "
                                    "art. 292, §1º), não a do pagamento realizado; fecha a base dos honorários quando "
                                    "a janela do art. 41-A cruza a sentença"},
    "honorarios_atualizados_ate_transmissao": {
        "tipo": "decimal", "obrigatorio": "sim para classificar os sucumbenciais (sem ele, a via deles sai em fórmula)",
        "valores": "honorários sucumbenciais atualizados até a transmissão (Res. CJF 983/2026, arts. 3º, §4º, e 16)"},
}
CAMPOS_PARCELA = ("competencia", "devido", "pago")
NATUREZAS = ("previdenciaria", "assistencial")
RITOS = ("JEF", "comum")

LIMITE_SM = Decimal(60)
CEM = Decimal(100)
ZERO = Decimal(0)
DATA_MIN, DATA_MAX = dt.date(1900, 1, 1), dt.date(2100, 12, 31)
LIMITE_MAGNITUDE = Decimal("1e15")
COMP_CONSOLIDACAO = (2021, 12)
FIM_CONSOLIDACAO = dt.date(2021, 12, 31)     # "prestações devidas até dez./2021" (Manual 2026, 4.3.1.1, Nota 5)
COMP_FIM_SELIC = (2025, 8)
COMP_INICIO_TEMA_1419 = (2025, 9)
COMP_ULTIMA_TAXA_LEGAL_INPC = (2026, 5)      # Manual 2026, item 4.3.2, Nota 3 (aplicada em jun./2026)
VIGENCIA_EC136 = dt.date(2025, 9, 10)        # EC 136/2025, art. 9º (context/lei/ec-113-2021.md, nota)

FONTE = {
    "r1_prev": "Manual de Cálculos da Justiça Federal, ed. jul./2026, itens 4.1.3, 4.3.1.1 e 4.3.2 "
               "(context/lei/manual-cjf-2026-calculos-prev.md); STJ Tema 905 e STF Tema 1.419 "
               "(context/lei/temas-sumulas-prev.md)",
    "r1_assist": "Manual de Cálculos da Justiça Federal, ed. jul./2026, item 4.3.1.1, Nota 3, e itens 4.2.1.1 "
                 "e 4.2.2 (context/lei/manual-cjf-2026-calculos-prev.md)",
    "tema_1207": "Manual de Cálculos da Justiça Federal, ed. jul./2026, item 4.3, Nota 6 (STJ Tema 1.207: "
                 "compensação mês a mês, sem valor mensal negativo) (context/lei/manual-cjf-2026-calculos-prev.md)",
    "r2": "Res. CJF 983/2026, art. 7º, §§2º a 4º e 6º (context/lei/res-cjf-983-2026.md); EC 113/2021, art. 3º, "
          "redação da EC 136/2025 (context/lei/ec-113-2021.md)",
    "sumula_111": "STJ Súmula 111 (context/lei/temas-sumulas-prev.md); Manual 2026, Notas 1 e 2 sobre "
                  "honorários: vencida a parcela cujo vencimento é anterior à sentença "
                  "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "vencimento": "Lei 8.213/1991, art. 41-A, §§2º a 4º, redação da Lei 11.665/2008 (context/lei/lei-8213-1991.md): "
                  "janela de pagamento distribuída entre os beneficiários, não um vencimento único",
    "base_pago": "Manual 2026, Nota 4 sobre honorários: pagamento administrativo, total ou parcial, após a citação "
                 "válida não altera a base dos honorários, que abrange a totalidade dos valores devidos "
                 "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "renuncia": "Res. CJF 983/2026, arts. 4º e 16, §3º: com a renúncia, o crédito requisitado fica no limite "
                "(context/lei/res-cjf-983-2026.md)",
    "honorarios_requisicao": "Res. CJF 983/2026, art. 16, §§1º a 3º (context/lei/res-cjf-983-2026.md)",
    "limite": "Res. CJF 983/2026, art. 3º, I e §4º (context/lei/res-cjf-983-2026.md); Lei 10.259/2001, art. 17, "
              "§1º, c/c art. 3º (context/lei/lei-10259-2001-jef.md)",
    "via": "Res. CJF 983/2026, art. 4º (context/lei/res-cjf-983-2026.md); Lei 10.259/2001, art. 17, §4º "
           "(context/lei/lei-10259-2001-jef.md)",
    "fracionar": "CF, art. 100, §8º (context/lei/cf88-seguridade.md); Lei 10.259/2001, art. 17, §3º "
                 "(context/lei/lei-10259-2001-jef.md)",
    "prazo_rpv_jef": "Lei 10.259/2001, art. 17, caput (context/lei/lei-10259-2001-jef.md)",
    "prazo_rpv_comum": "CPC, art. 535, §3º, II (context/lei/cpc-excertos-prev.md)",
    "prazo_precatorio": "CF, art. 100, §5º, redação da EC 136/2025 (context/lei/cf88-seguridade.md); Manual "
                        "2026, cap. 5, Nota 1 (corte de 2 de abril de 2022 até a EC 136) "
                        "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "graca_precatorio": "Res. CJF 983/2026, art. 7º, §2º (context/lei/res-cjf-983-2026.md); EC 113/2021, art. 3º, "
                        "§3º, redação da EC 136/2025 (context/lei/ec-113-2021.md); Manual 2026, cap. 5, Nota 1 "
                        "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "graca_rpv": "Manual 2026, cap. 5, Nota 2: sem juros nos 60 dias da apresentação "
                 "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "jef_sem_prazo_diferenciado": "Lei 10.259/2001, art. 9º (context/lei/lei-10259-2001-jef.md)",
    "titulo": "Manual 2026, item 4.1 (o título prevalece) (context/lei/manual-cjf-2026-calculos-prev.md)",
    "fronteira_selic": "Manual 2026, item 4.3.1.1, Nota 4, \"b\": Selic aplicada no mês posterior ao da competência "
                       "(context/lei/manual-cjf-2026-calculos-prev.md); Res. CJF 983/2026, art. 7º, §3º, II "
                       "(context/lei/res-cjf-983-2026.md)",
    "graca_tema_1335": "STF Tema 1.335 e ADI 4.425-QO (context/lei/temas-sumulas-prev.md): no prazo do art. 100, §5º, "
                       "sem Selic, só correção monetária pelo IPCA-E; LDO 2025 (Lei 15.080/2024), art. 37, §1º, a que a "
                       "Res. CJF 983/2026, art. 7º, caput, remete",
    "tensao_indice": "Res. CJF 983/2026, art. 7º, §3º, III (IPCA) × LDO 2025 (Lei 15.080/2024), art. 37, §1º, e LDO "
                     "2026 (Lei 15.321/2025), art. 41, §1º (IPCA-E \"exclusivamente\" no período do art. 100, §5º)",
}
INICIO_EC136_SET = dt.date(2025, 9, 1)
# QA final r7 M1: sem afirmar que a ação segue pendente (alinhado a skills/cumprimento-sentenca-inss)
ALERTA_ADI = "[VERIFICAR] ADI 7.873: andamento não certificado; reverificar"
AVISO_FIXO = ("Validar contra a fonte oficial antes de protocolar; o número não substitui a conferência "
              "do advogado.")


class EntradaInvalida(Exception):
    pass


# ---------------------------------------------------------------- leitura da entrada

def _data(campo, valor):
    if not isinstance(valor, str):
        raise EntradaInvalida(f"{campo}: esperado texto AAAA-MM-DD")
    try:
        d = dt.date.fromisoformat(valor)
    except ValueError:
        raise EntradaInvalida(f"{campo}: data inválida '{valor}' (use AAAA-MM-DD)")
    if not DATA_MIN <= d <= DATA_MAX:
        raise EntradaInvalida(f"{campo}: data fora do intervalo suportado (1900-01-01 a 2100-12-31)")
    return d


def _comp(campo, valor):
    if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}", valor):
        raise EntradaInvalida(f"{campo}: competência inválida '{valor}' (use AAAA-MM)")
    a, m = int(valor[:4]), int(valor[5:])
    if not 1 <= m <= 12:
        raise EntradaInvalida(f"{campo}: mês inválido em '{valor}'")
    if not 1900 <= a <= 2100:
        raise EntradaInvalida(f"{campo}: competência fora do intervalo suportado (1900-01 a 2100-12)")
    return (a, m)


def _dec(campo, valor):
    if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
        raise EntradaInvalida(f"{campo}: esperado número decimal em texto, com ponto")
    try:
        v = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError):          # ValueError: inteiro acima do limite de dígitos do str()
        raise EntradaInvalida(f"{campo}: número inválido")
    # copy_abs() não arredonda pelo contexto; abs() de '1e1000000' estoura (decimal.Overflow)
    if not v.is_finite() or v.copy_abs() > LIMITE_MAGNITUDE or -v.as_tuple().exponent > 6:
        raise EntradaInvalida(f"{campo}: fora da capacidade suportada (até 1e15, até 6 casas)")
    if v < 0:
        raise EntradaInvalida(f"{campo}: valor negativo")
    return v


def texto_valido(bruto):
    """Recusa surrogate UTF-16 solto (\\ud800) em chave ou valor: não se codifica em UTF-8 na saída."""
    pilha = [bruto]
    while pilha:
        x = pilha.pop()
        if isinstance(x, dict):
            pilha.extend(x.keys())
            pilha.extend(x.values())
        elif isinstance(x, list):
            pilha.extend(x)
        elif isinstance(x, str):
            try:
                x.encode("utf-8")
            except UnicodeEncodeError:
                raise EntradaInvalida("texto com caractere inválido (surrogate UTF-16 solto) em chave ou valor")


def normaliza(bruto):
    if not isinstance(bruto, dict):
        raise EntradaInvalida("a entrada deve ser um objeto JSON")
    validos = {k for k in CAMPOS if "[]" not in k}
    extras = sorted(k for k in bruto if k not in validos and not k.startswith("_"))
    if extras:
        raise EntradaInvalida(f"campos desconhecidos: {', '.join(extras)}")
    for c in ("natureza", "rito"):
        if bruto.get(c) is None:
            raise EntradaInvalida(f"campo obrigatório ausente ou nulo: {c}")
    if bruto["natureza"] not in NATUREZAS:
        raise EntradaInvalida(f"natureza: use um de {', '.join(NATUREZAS)}")
    if bruto["rito"] not in RITOS:
        raise EntradaInvalida(f"rito: use um de {', '.join(RITOS)}")
    e = {"natureza": bruto["natureza"], "rito": bruto["rito"]}
    for c in ("data_citacao", "data_sentenca", "data_expedicao", "data_apresentacao", "data_transmissao",
              "data_pagamento"):
        if bruto.get(c) is not None:
            e[c] = _data(c, bruto[c])
    for c in ("valor_consolidado_12_2021", "juros_consolidados_12_2021", "valor_atualizado_ate_transmissao",
              "honorarios_percentual", "honorarios_sucumbenciais", "honorarios_contratuais", "salario_minimo",
              "honorarios_atualizados_ate_transmissao"):
        if bruto.get(c) is not None:
            e[c] = _dec(c, bruto[c])
    if bruto.get("data_base_conta") is not None:
        e["data_base_conta"] = _comp("data_base_conta", bruto["data_base_conta"])
    rn = bruto.get("renunciar_excedente", False)
    if not isinstance(rn, bool):
        raise EntradaInvalida("renunciar_excedente: esperado true ou false")
    e["renunciar_excedente"] = rn
    if bruto.get("titulo_com_criterio_proprio") is not None:
        if not isinstance(bruto["titulo_com_criterio_proprio"], str):
            raise EntradaInvalida("titulo_com_criterio_proprio: esperado texto")
        e["titulo_com_criterio_proprio"] = bruto["titulo_com_criterio_proprio"]

    # atrasados: parcelas ou diferença mensal, nunca as duas
    tem_parc = bruto.get("parcelas") is not None
    tem_dif = any(bruto.get(c) is not None for c in ("diferenca_mensal", "competencia_inicial", "competencia_final"))
    if tem_parc and tem_dif:
        raise EntradaInvalida("duas formas de atrasados: use parcelas OU diferenca_mensal com o período")
    parcelas = []
    if tem_parc:
        if not isinstance(bruto["parcelas"], list) or not bruto["parcelas"]:
            raise EntradaInvalida("parcelas: esperada lista não vazia")
        vistos = set()
        for i, p in enumerate(bruto["parcelas"]):
            rot = f"parcelas[{i}]"
            if not isinstance(p, dict):
                raise EntradaInvalida(f"{rot}: esperado objeto")
            ex = sorted(k for k in p if k not in CAMPOS_PARCELA and not k.startswith("_"))
            if ex:
                raise EntradaInvalida(f"{rot}: campos desconhecidos: {', '.join(ex)}")
            for c in ("competencia", "devido"):
                if p.get(c) is None:
                    raise EntradaInvalida(f"{rot}: campo obrigatório ausente ou nulo: {c}")
            comp = _comp(f"{rot}.competencia", p["competencia"])
            if comp in vistos:
                raise EntradaInvalida(f"{rot}: competência {p['competencia']} repetida")
            vistos.add(comp)
            parcelas.append({"competencia": comp, "devido": _dec(f"{rot}.devido", p["devido"]),
                             "pago": _dec(f"{rot}.pago", p.get("pago", "0.00"))})
    elif tem_dif:
        for c in ("diferenca_mensal", "competencia_inicial", "competencia_final"):
            if bruto.get(c) is None:
                raise EntradaInvalida(f"diferenca_mensal exige diferenca_mensal, competencia_inicial e "
                                      f"competencia_final (falta {c})")
        dif = _dec("diferenca_mensal", bruto["diferenca_mensal"])
        ini = _comp("competencia_inicial", bruto["competencia_inicial"])
        fim = _comp("competencia_final", bruto["competencia_final"])
        if fim < ini:
            raise EntradaInvalida("competencia_final anterior a competencia_inicial")
        c = ini
        while c <= fim:
            parcelas.append({"competencia": c, "devido": dif, "pago": ZERO})
            c = comp_seguinte(c)
    e["parcelas"] = sorted(parcelas, key=lambda p: p["competencia"])
    e["datas_vencimento"] = {}
    if bruto.get("datas_vencimento") is not None:
        dp = bruto["datas_vencimento"]
        if not isinstance(dp, dict):
            raise EntradaInvalida("datas_vencimento: esperado objeto {\"AAAA-MM\": \"AAAA-MM-DD\"}")
        comps = {p["competencia"] for p in e["parcelas"]}
        for k, v in dp.items():
            c = _comp(f"datas_vencimento[{k!r}]", k)
            if c not in comps:
                raise EntradaInvalida(f"datas_vencimento: competência {k} sem parcela correspondente")
            d = _data(f"datas_vencimento[{k}]", v)
            if d < dt.date(c[0], c[1], 1):
                raise EntradaInvalida(f"datas_vencimento: {k} vence em {v}, antes do próprio mês da competência")
            e["datas_vencimento"][c] = d

    tem_atrasados = bool(e["parcelas"])
    if not tem_atrasados and "valor_atualizado_ate_transmissao" not in e:
        raise EntradaInvalida("sem atrasados (parcelas ou diferenca_mensal) e sem "
                              "valor_atualizado_ate_transmissao: nada a calcular")
    if tem_atrasados:
        for c in ("data_citacao", "data_base_conta"):
            if c not in e:
                raise EntradaInvalida(f"{c} é obrigatório quando há atrasados")
        if e["parcelas"][-1]["competencia"] > e["data_base_conta"]:
            raise EntradaInvalida("há parcela com competência posterior à data_base_conta")
    if "juros_consolidados_12_2021" in e and "valor_consolidado_12_2021" not in e:
        raise EntradaInvalida("juros_consolidados_12_2021 exige valor_consolidado_12_2021")
    if "valor_consolidado_12_2021" in e:
        if not tem_atrasados:
            raise EntradaInvalida("valor_consolidado_12_2021 exige atrasados (parcelas ou diferenca_mensal)")
        if e["data_base_conta"] < COMP_CONSOLIDACAO:
            raise EntradaInvalida("valor_consolidado_12_2021 com data_base_conta anterior a 2021-12")
    if "honorarios_percentual" in e and "honorarios_sucumbenciais" in e:
        raise EntradaInvalida("honorarios_percentual e honorarios_sucumbenciais juntos: informe um ou outro")
    if "honorarios_percentual" in e:
        if not tem_atrasados:
            raise EntradaInvalida("honorarios_percentual exige atrasados (a base é a soma das vencidas)")
        if "data_sentenca" not in e:
            raise EntradaInvalida("data_sentenca é obrigatória com honorarios_percentual (Súmula 111)")
        if e["honorarios_percentual"] > CEM:
            raise EntradaInvalida("honorarios_percentual acima de 100")
    if "honorarios_atualizados_ate_transmissao" in e:
        if "honorarios_percentual" not in e and "honorarios_sucumbenciais" not in e:
            raise EntradaInvalida("honorarios_atualizados_ate_transmissao sem honorários sucumbenciais (percentual ou "
                                  "valor fixado)")
        if "valor_atualizado_ate_transmissao" not in e:
            raise EntradaInvalida("honorarios_atualizados_ate_transmissao exige valor_atualizado_ate_transmissao (a "
                                  "classificação é feita na transmissão)")
    if "valor_atualizado_ate_transmissao" in e and "data_transmissao" not in e:
        raise EntradaInvalida("data_transmissao é obrigatória com valor_atualizado_ate_transmissao (M4)")
    if "honorarios_contratuais" in e and "valor_atualizado_ate_transmissao" in e \
            and q2(e["honorarios_contratuais"]) > q2(e["valor_atualizado_ate_transmissao"]):
        raise EntradaInvalida("honorarios_contratuais maiores que o crédito da parte "
                              "(valor_atualizado_ate_transmissao, que já os inclui)")
    if "salario_minimo" in e and e["salario_minimo"] == 0:
        raise EntradaInvalida("salario_minimo: zero")
    if "data_pagamento" in e and "data_apresentacao" in e and e["data_pagamento"] < e["data_apresentacao"]:
        raise EntradaInvalida("data_pagamento anterior a data_apresentacao")
    if "data_pagamento" in e and tem_atrasados and \
            (e["data_pagamento"].year, e["data_pagamento"].month) < e["data_base_conta"]:
        raise EntradaInvalida("data_pagamento anterior a data_base_conta")
    return e


def eco(e):
    out = {}
    for k, v in e.items():
        if k == "datas_vencimento":
            out[k] = {comp_txt(c): d.isoformat() for c, d in sorted(v.items())}
        elif k == "parcelas":
            out[k] = [{"competencia": comp_txt(p["competencia"]), "devido": str(p["devido"]),
                       "pago": str(p["pago"])} for p in v]
        elif k == "data_base_conta":
            out[k] = comp_txt(v)
        elif isinstance(v, dt.date):
            out[k] = v.isoformat()
        elif isinstance(v, Decimal):
            out[k] = str(v)
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------- utilidades

def q2(v):
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def s2(v):
    return None if v is None else str(q2(v))


def comp_txt(c):
    return f"{c[0]:04d}-{c[1]:02d}"


def comp_seguinte(c):
    return (c[0] + 1, 1) if c[1] == 12 else (c[0], c[1] + 1)


def comp_anterior(c):
    return (c[0] - 1, 12) if c[1] == 1 else (c[0], c[1] - 1)


def mes_de(d):
    return (d.year, d.month)


def carregar_motor(caminho, nome):
    """Importa um motor vendorizado pelo caminho; None se o arquivo não existe."""
    caminho = Path(caminho)
    if not caminho.is_file():
        return None
    spec = importlib.util.spec_from_file_location(f"_prev_{nome}_{abs(hash(str(caminho)))}", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def falta(faltas, item, motivo, fonte):
    if not any(f["item"] == item and f["motivo"] == motivo for f in faltas):
        faltas.append({"item": item, "motivo": motivo, "fonte": fonte})


def salario_minimo(e, tabela, faltas):
    """(valor, fonte) do salário mínimo vigente na transmissão (M4)."""
    if "salario_minimo" in e:
        return e["salario_minimo"], "informado na entrada (salario_minimo)"
    d = e["data_transmissao"]
    try:
        dados = json.loads(Path(tabela).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        falta(faltas, "tabela do salário mínimo", f"scripts/data/salario-minimo.json ilegível ou ausente ({err})",
              FONTE["limite"])
        return None, None
    for ln in dados.get("linhas", []):
        ini = dt.date.fromisoformat(ln["vigencia_inicio"])
        fim = dt.date.fromisoformat(ln["vigencia_fim"]) if ln.get("vigencia_fim") else None
        if ini <= d and (fim is None or d <= fim) and ln.get("valor") is not None:
            if fim is None and d.year > ini.year:
                break   # vigência aberta: só vale no ano do decreto capturado
            return Decimal(ln["valor"]), f"{ln['norma']} ({ln['arquivo']}); tabela capturada em " \
                                          f"{dados.get('data_captura')}"
    falta(faltas, "salário mínimo da data da transmissão",
          f"{d.isoformat()} fora da tabela scripts/data/salario-minimo.json (intervalo {dados.get('intervalo')}); "
          "informe salario_minimo pelo decreto vigente na transmissão", FONTE["limite"])
    return None, None


# QA final r3 A-01: cópia literal de JANELAS, regime_janela e JanelaPagamento de calc_previdenciario_valor_causa.py
# (os scripts são autocontidos, sem import entre eles; mantenha as duas cópias iguais). Aqui a renda em manutenção
# não é conhecida (as parcelas trazem diferença ou devido), então janela(comp, None): a do §3º, que contém a do §2º,
# e, antes da MP 404/2007, só o mês seguinte.
#
# Regimes da janela de pagamento por competência, no padrão da COBERTURA dos outros scripts (QA final A02): intervalo
# de competências, regra e fonte de cada borda, todas em context/lei/lei-8213-1991.md (art. 41, §4º, e art. 41-A,
# §§2º a 4º, nas redações de cada período). Competência anterior ao primeiro regime: sem janela capturada, a vencida
# só fecha com datas_vencimento. Dia não capturado vira borda conservadora (janela mais larga).
#
# QA final r2 A-01: a antecipação do §3º (até um mínimo, pagamento desde o fim do próprio mês da competência) entrou
# pela MP 404/2007 e não vale para trás. Até ela, o pagamento é sempre no mês seguinte ao da competência (art. 41, §4º,
# redações original, da Lei 8.444/1992 e da Lei 10.699/2003; art. 41-A, §2º, redação da Lei 11.430/2006). A captura
# só data a MP como "de 2007": as competências de 2007 são a fronteira, e nelas a parte antecipada da janela não fecha
# nada (exit 3), nunca a regra posterior. "antecipacao": False = só mês seguinte; None = incerta; True = §3º em vigor.
JANELAS = (
    {"id": "art41-original-ou-8444", "desde": (1991, 7), "ate": (1992, 12), "dias": None, "fim_dia_util": 10,
     "antecipacao": False, "paragrafo": "art. 41, §4º, redação original ou da Lei 8.444/1992",
     "regra": "até o 10º dia útil do mês seguinte (art. 41, §4º, redação original) ou do 1º ao 10º (redação da Lei "
              "8.444/1992); sem o dia da Lei 8.444 capturado, a janela vai do 1º dia do mês seguinte ao 10º dia útil "
              "dele",
     "fonte_desde": "Lei 8.213/1991, art. 41, §4º, redação original (context/lei/lei-8213-1991.md); vigência em "
                    "25/07/1991 (IN 128, art. 199, II; context/lei/in-128-2022-inss.md)",
     "fonte_ate": "Lei 8.444, \"de 1992\" (nota de redação do art. 41, §4º, em context/lei/lei-8213-1991.md); dia não "
                  "capturado: a borda é o fim de 1992"},
    {"id": "art41-8444", "desde": (1993, 1), "ate": (2004, 2), "dias": (1, 10), "fim_dia_util": 10,
     "antecipacao": False, "paragrafo": "art. 41, §4º, redação da Lei 8.444/1992",
     "regra": "do 1º ao 10º dia útil do mês seguinte (art. 41, §4º, redação da Lei 8.444/1992)",
     "fonte_desde": "Lei 8.444/1992 (nota de redação do art. 41, §4º, em context/lei/lei-8213-1991.md)",
     "fonte_ate": "Lei 10.699/2003: \"A partir de abril de 2004, os pagamentos ... do primeiro ao quinto dia útil do mês "
                  "seguinte\" (art. 41, §4º): a regra é do pagamento, e a competência de fevereiro/2004, paga em março, é "
                  "a última da janela de 10 dias"},
    {"id": "art41-10699", "desde": (2004, 3), "ate": (2006, 12), "dias": (1, 5), "fim_dia_util": 5,
     "antecipacao": False, "paragrafo": "art. 41, §4º, redação da Lei 10.699/2003, ou art. 41-A, §2º, redação da Lei "
                                         "11.430/2006",
     "regra": "do 1º ao 5º dia útil do mês seguinte, para todo benefício (sem antecipação para quem recebe até um "
              "mínimo)",
     "fonte_desde": "Lei 10.699/2003 (art. 41, §4º, em context/lei/lei-8213-1991.md: pagamentos a partir de abril/2004, "
                    "logo desde a competência de março/2004)",
     "fonte_ate": "Lei 11.430/2006 (art. 41-A, §2º, mesma janela) até a MP 404, \"de 2007\" (nota de redação do art. "
                  "41-A, §§2º e 3º, em context/lei/lei-8213-1991.md): sem dia nem mês capturados, a borda é o fim de 2006"},
    {"id": "art41A-fronteira-mp404", "desde": (2007, 1), "ate": (2007, 12), "dias": (1, 5), "fim_dia_util": 5,
     "antecipacao": None, "paragrafo": "§2º",
     "regra": "acima de um mínimo, do 1º ao 5º dia útil do mês seguinte (art. 41-A, §2º, nas duas redações); até um "
              "mínimo, a antecipação do §3º depende da data da MP 404/2007, não capturada: a parte antecipada da "
              "janela fica em aberto",
     "fonte_desde": "MP 404, \"de 2007\" (nota de redação do art. 41-A, §§2º e 3º, em context/lei/lei-8213-1991.md); "
                    "dia e mês não capturados",
     "fonte_ate": "MP 404, \"de 2007\": em vigor, no mais tardar, ao fim de 2007"},
    {"id": "art41A", "desde": (2008, 1), "ate": None, "dias": (1, 5), "fim_dia_util": 5,
     "antecipacao": True, "paragrafo": "§2º",
     "regra": "do 1º ao 5º dia útil do mês seguinte acima de um mínimo (§2º); até um mínimo, do 5º dia útil que "
              "antecede o fim do mês da competência ao 5º dia útil do seguinte (§3º)",
     "fonte_desde": "MP 404/2007 (nota de redação do art. 41-A, §§2º e 3º, em context/lei/lei-8213-1991.md), com o texto "
                    "mantido pela Lei 11.665/2008",
     "fonte_ate": "art. 41-A, §§2º a 4º, redação da Lei 11.665/2008, em vigor"},
)


def regime_janela(comp):
    for r in JANELAS:
        if comp >= r["desde"] and (r["ate"] is None or comp <= r["ate"]):
            return r
    return None


class JanelaPagamento:
    """Janelas de pagamento por competência (JANELAS): art. 41, §4º, nas redações históricas, e art. 41-A, §§2º a 4º,
    da Lei 8.213/1991; a antecipação do §3º só desde a MP 404/2007.

    A lei não fixa um vencimento único: distribui os beneficiários entre os dias da janela, e o dia útil é o
    de expediente bancário normal (§4º). Sem a data individual, a competência só é vencida se a janela inteira
    termina antes do marco, e só não é vencida se ela começa no marco ou depois; no meio, é indeterminada.

    Dia útil das bordas da janela: sábado, domingo e feriados nacionais do motor de prazos; os pontos facultativos
    (Carnaval, Corpus Christi) entram como segunda leitura e a janela cobre as duas. Sem o motor, só sábado e
    domingo, com a janela alargada em MARGEM_SEM_MOTOR para não fechar o que um feriado mudaria; o início da janela
    no mês seguinte nunca recua para o mês da competência (o 1º dia útil não cai antes do dia 1).

    O DIA do vencimento informado é conferido no calendário BANCÁRIO (expediente_bancario), separado do forense
    (QA final r4 A01): estar entre as bordas da união das leituras não prova expediente bancário normal no dia.
    """

    MARGEM_SEM_MOTOR = dt.timedelta(days=7)

    # Anos que a tabela de feriados tem de cobrir para o calendário valer (datas da entrada até 2100 e o mês seguinte).
    ANOS_TABELA = range(1990, 2102)

    def __init__(self, motor_prazo):
        self.motor = None
        self.calendarios = {}
        self._bancarios = {}
        self.tabela = None
        self.sem_calendario = None if motor_prazo is not None else "motor de prazos ausente"
        if motor_prazo is not None:
            # QA final r4 r2 (revisão Codex, MAJOR): motor presente com a tabela ausente, ilegível ou sem algum ano
            # coberto é fonte insuficiente, não entrada inválida: o calendário cai no modo sem motor (janelas
            # alargadas; dia de semana informado fica em aberto, exit 3), nunca fecha nem vira exit 2.
            try:
                tabela = json.loads(Path(motor_prazo.ARQ_FERIADOS_PADRAO).read_text(encoding="utf-8"))
                calendarios = {incluir: motor_prazo.Calendario(tabela, {
                    "feriados_locais": {}, "suspensoes": [], "incluir_pontos_forenses": incluir,
                    "natureza": "material", "excecao_recesso_penal": None, "rito": "cpc"}) for incluir in (False, True)}
                self.motor, self.tabela, self.calendarios = motor_prazo, tabela, calendarios
                for ano in self.ANOS_TABELA:
                    self._feriados_bancarios(ano)
                    for cal in calendarios.values():
                        cal.nao_util(dt.date(ano, 1, 1))
            except Exception as exc:      # noqa: BLE001 — qualquer falha da tabela é fonte insuficiente
                self.motor, self.tabela, self.calendarios, self._bancarios = None, None, {}, {}
                self.sem_calendario = (f"tabela de feriados do motor de prazos indisponível ou ilegível "
                                       f"({type(exc).__name__})")

    def _util(self, d, pontos):
        return d.weekday() < 5 if self.motor is None else not self.calendarios[pontos].nao_util(d)

    def _enesimo(self, ano, mes, n, pontos):
        """n-ésimo dia útil do mês, contado do dia 1."""
        d = dt.date(ano, mes, 1)
        while True:
            if self._util(d, pontos):
                n -= 1
                if n == 0:
                    return d
            d += dt.timedelta(days=1)

    def _enesimo_antes_do_fim(self, ano, mes, n, pontos):
        """n-ésimo dia útil que antecede o último dia do mês (o último dia não conta: leitura mais cedo)."""
        d = dt.date(ano, mes, calendar.monthrange(ano, mes)[1]) - dt.timedelta(days=1)
        while True:
            if self._util(d, pontos):
                n -= 1
                if n == 0:
                    return d
            d -= dt.timedelta(days=1)

    def _feriados_bancarios(self, ano):
        """Datas da tabela do motor sem expediente bancário normal no ano: os fixos (com a vigência de cada um) e
        TODAS as datas móveis — segunda e terça de Carnaval, Sexta-feira da Paixão e Corpus Christi —, que no
        calendário forense são só ponto facultativo ou feriado religioso, mas não têm expediente bancário com
        horário normal de atendimento (Lei 8.213, art. 41-A, §4º; o calendário oficial de pagamentos do INSS não
        paga nelas). Cópia do tratamento de calc_previdenciario_rmi.py (DiasBancarios, leitura ampla), sem import."""
        if ano not in self._bancarios:
            dias = {}
            for f in self.tabela["fixos"]:
                d = dt.date(ano, *(int(x) for x in f["mes_dia"].split("-")))
                if f.get("vigencia_desde") and d < dt.date.fromisoformat(f["vigencia_desde"]):
                    continue
                dias[d] = f["nome"]
            p = self.motor.pascoa(ano)
            for f in self.tabela["moveis"]:
                dias[p + dt.timedelta(days=f["dias_da_pascoa"])] = f["nome"]
            self._bancarios[ano] = dias
        return self._bancarios[ano]

    def expediente_bancario(self, d):
        """Calendário bancário do art. 41-A, §4º (dia útil = expediente bancário com horário normal), separado do
        forense. Devolve (True, None) com expediente; (False, motivo) sem ele — sábado, domingo, feriado nacional
        ou data móvel da tabela (Carnaval, Paixão, Corpus Christi) → exit 2; (None, motivo) quando o calendário não
        decide o dia — sem o motor de prazos ou com a tabela de feriados indisponível, dia de semana fica em aberto
        (exit 3), nunca fechado."""
        if d.weekday() == 5:
            return False, "sábado"
        if d.weekday() == 6:
            return False, "domingo"
        if self.motor is None:
            return None, (f"{self.sem_calendario}: sem a tabela de feriados, o calendário bancário não decide se o "
                          "dia teve expediente bancário normal")
        nome = self._feriados_bancarios(d.year).get(d)
        return (True, None) if nome is None else (False, nome)

    def janela(self, comp, ate_um_minimo):
        """(início mais cedo, fim mais tarde, parágrafo, início no mês seguinte) da janela de pagamento da competência;
        None antes do primeiro regime de JANELAS.

        ate_um_minimo: True (§3º), False (§2º) ou None (mínimo da competência fora da tabela: usa a janela do
        §3º, que contém a do §2º). Antes da MP 404/2007 não há distinção pelo valor. O 4º elemento só vem preenchido
        na fronteira da MP 404 (antecipação incerta): é o início da parte da janela que vale nas duas leituras.
        """
        regime = regime_janela(comp)
        if regime is None:
            return None
        prox = comp_seguinte(comp)
        leituras = (False, True) if self.motor is not None else (False,)
        fim = max(self._enesimo(*prox, regime["fim_dia_util"], p) for p in leituras)
        if self.motor is None:
            fim += self.MARGEM_SEM_MOTOR
        if regime["dias"]:
            ini_seguinte = min(self._enesimo(*prox, regime["dias"][0], p) for p in leituras)
        else:
            ini_seguinte = dt.date(prox[0], prox[1], 1)
        if regime["antecipacao"] is False or ate_um_minimo is False:
            return ini_seguinte, fim, regime["paragrafo"], None
        ini = min(self._enesimo_antes_do_fim(*comp, 5, p) for p in leituras)
        if self.motor is None:
            ini -= self.MARGEM_SEM_MOTOR
        if regime["antecipacao"] is None:
            return ini, fim, ("§2º, ou §3º se já em vigor a MP 404/2007 (data não capturada: antecipação em aberto)"
                              if ate_um_minimo else "§2º ou §3º (mínimo fora da tabela; MP 404/2007 sem data "
                              "capturada: antecipação em aberto)"), ini_seguinte
        par = "§3º" if ate_um_minimo else "§2º ou §3º (mínimo da competência fora da tabela)"
        return ini, fim, par, None


def dez_2021_no_consolidado(e, incertas=()):
    """Parcela da competência 12/2021 diante do consolidado informado: True se o vencimento devido cai até
    31/12/2021 (prestação "devida até dez./2021", Manual 2026, item 4.3.1.1, Nota 5; F1 §7), False se cai depois,
    None sem datas_vencimento['2021-12'] (a janela do art. 41-A dela sempre cruza a virada do ano) ou com a data em
    aberto (incertas: o calendário bancário não decide o dia)."""
    venc = e["datas_vencimento"].get(COMP_CONSOLIDACAO)
    return None if venc is None or COMP_CONSOLIDACAO in incertas else venc <= FIM_CONSOLIDACAO


def pago_antes(ini, fim, marco):
    """True se a janela inteira acaba antes do marco; False se começa no marco ou depois; None no meio."""
    if fim < marco:
        return True
    if ini >= marco:
        return False
    return None


def valida_vencimentos(e, janelas):
    """QA final r3 A-01: datas_vencimento só vale como vencimento individual devido se cair na janela legal da
    competência (JANELAS: art. 41, §4º, histórico, e art. 41-A, §§2º a 4º) e em dia de expediente bancário (§4º),
    como no valor da causa; fora disso, exit 2, nunca uma data que exclua a parcela da base dos honorários.

    Devolve {competência: motivo} das datas que não valem como vencimento devido nem são recusadas (o vencimento
    fica em aberto, exit 3): a que só cabe com a antecipação do §3º na fronteira da MP 404/2007 (sem data de
    vigência capturada) e a de dia que o calendário bancário não decide (QA final r4 A01: sem o motor de prazos).
    Competência anterior ao primeiro regime de JANELAS não tem janela capturada: a data informada é usada como está.
    """
    incertas = {}
    for c, vc in sorted(e["datas_vencimento"].items()):
        jan = janelas.janela(c, None)
        if jan is None:
            continue
        if not jan[0] <= vc <= jan[1]:
            # a cópia do valor da causa chama o None de "mínimo fora da tabela"; aqui é a renda que não vem na entrada
            par = re.sub(r"m[íi]nimo( da competência)? fora da tabela", "renda em manutenção não informada", jan[2])
            raise EntradaInvalida(
                f"datas_vencimento: {comp_txt(c)} vence em {vc.isoformat()}, fora da janela de pagamento "
                f"({jan[0].isoformat()} a {jan[1].isoformat()}, {par}); o campo é o vencimento individual "
                "devido, não a data do pagamento realizado")
        expediente, motivo_exp = janelas.expediente_bancario(vc)
        if expediente is False:
            # art. 41-A, §4º, no calendário bancário (QA final r4 A01: Carnaval, Paixão e Corpus Christi inclusive)
            raise EntradaInvalida(
                f"datas_vencimento: {comp_txt(c)} vence em {vc.isoformat()} ({vc.strftime('%d/%m/%Y')}), dia sem "
                f"expediente bancário normal ({motivo_exp}; art. 41-A, §4º)")
        if jan[3] is not None and vc < jan[3]:
            incertas[c] = ("só cabe com a antecipação do §3º, cuja vigência pela MP 404/2007 não tem data "
                           "capturada")
        elif expediente is None:
            incertas[c] = f"{motivo_exp}; confira o calendário oficial de pagamentos do INSS"
    return incertas


# ---------------------------------------------------------------- R1 — condenação até a data-base

def r1(e, motor_a, faltas, alertas, memoria, incertas=()):
    """Atualiza os atrasados até a data-base pelo motor (regime fazenda-ec113). Devolve o resumo."""
    base = e["data_base_conta"]
    difs, negativos = [], []
    for p in e["parcelas"]:
        d = p["devido"] - p["pago"]
        if d < 0:
            negativos.append(comp_txt(p["competencia"]))
            d = ZERO
        difs.append({"competencia": p["competencia"], "valor": d})
    if negativos:
        alertas.append(f"Competências com pago maior que o devido ({', '.join(negativos)}) entram com zero: "
                       "compensação mês a mês, sem valor mensal negativo (STJ Tema 1.207; Manual 2026, item 4.3, "
                       "Nota 6).")
    chamadas, fronteira_dez = [], None
    if "valor_consolidado_12_2021" in e:
        dez = next((x for x in difs if x["competencia"] == COMP_CONSOLIDACAO and x["valor"] != 0), None)
        dentro = dez_2021_no_consolidado(e, incertas)
        if dez is not None and dentro is None:
            fronteira_dez = dez
        no_consolidado = {x["competencia"] for x in difs if x["competencia"] < COMP_CONSOLIDACAO}
        if dez is not None and dentro is True:
            no_consolidado.add(COMP_CONSOLIDACAO)
        antes = [x for x in difs if x["competencia"] in no_consolidado]
        chamadas.append({
            "rotulo": "consolidado 12/2021",
            "competencias": [comp_txt(x["competencia"]) for x in antes],
            "entrada": {"valor": str(e["valor_consolidado_12_2021"]),
                        "valor_consolidado_12_2021": {
                            "principal": str(e["valor_consolidado_12_2021"]),
                            "juros": str(e.get("juros_consolidados_12_2021", ZERO))},
                        "data_inicial": "2021-12-01"}})
        if "juros_consolidados_12_2021" not in e:
            # Juros zero é premissa, não dado: a conta exibida usa zero e fica aberta (na dúvida, fórmula aberta).
            falta(faltas, "juros_consolidados_12_2021",
                  "valor_consolidado_12_2021 sem os juros até 12/2021, que compõem o consolidado (Manual 2026, item "
                  "4.3.1.1, Nota 5) e mudam o total; informe 0 se não houver",
                  FONTE["r1_prev"])
            alertas.append("[VERIFICAR] valor_consolidado_12_2021 sem juros_consolidados_12_2021: a conta exibida usa "
                           "'juros até 12/2021' zero (Manual 2026, item 4.3.1.1, Nota 5).")
        difs = [x for x in difs if x["competencia"] not in no_consolidado]
        memoria.append(f"parcelas {'até 12/2021' if COMP_CONSOLIDACAO in no_consolidado else 'até 11/2021'} "
                       f"substituídas pelo consolidado de 12/2021 informado ({e['valor_consolidado_12_2021']} + juros "
                       f"{e.get('juros_consolidados_12_2021', ZERO)})"
                       + ("; a de 12/2021, com vencimento devido em "
                          f"{e['datas_vencimento'][COMP_CONSOLIDACAO].isoformat()}, fica fora e segue à parte"
                          if dez is not None and dentro is False else ""))
    for x in difs:
        if x["valor"] == 0:
            continue
        chamadas.append({"rotulo": comp_txt(x["competencia"]), "competencias": [comp_txt(x["competencia"])],
                         "entrada": {"valor": str(x["valor"]),
                                     "data_inicial": f"{comp_txt(x['competencia'])}-01"}})
    registros, componentes, total, ok = [], {}, ZERO, True
    alertas_motor = []
    for ch in chamadas:
        entrada = dict(ch["entrada"], **_params_r1(e))
        codigo, saida = motor_a.calcular(entrada)
        if codigo == EXIT_ENTRADA:
            raise EntradaInvalida(f"motor de atualização recusou {ch['rotulo']}: {saida.get('detalhe')}")
        for a in saida.get("alertas", []):
            if a not in alertas_motor:
                alertas_motor.append(a)
        reg = {"parcela": ch["rotulo"], "competencias": ch["competencias"], "valor": ch["entrada"]["valor"],
               "motor_exit": codigo, "valor_atualizado": saida.get("valor_final"),
               "componentes": saida.get("componentes") or {},
               "fatias": [{"periodo": f.get("periodo"), "indice": f.get("indice"), "tipo": f.get("tipo"),
                           "fator": f.get("fator"), "percentual": f.get("percentual")}
                          for f in saida.get("fatias", [])],
               "fonte_indice": saida.get("fonte_indice")}
        if codigo != EXIT_OK:
            ok = False
            fa = saida.get("formula_aberta") or {}
            reg["formula_aberta"] = fa
            for item in fa.get("faltando", []):
                txt = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
                falta(faltas, "índice ou série ausente na fase R1", _sem_competencia(txt), FONTE["r1_prev"])
        else:
            total += Decimal(saida["valor_final"])
            for k, v in reg["componentes"].items():
                k = _chave(k)
                componentes[k] = componentes.get(k, ZERO) + Decimal(v)
            if "principal_corrigido" not in reg["componentes"]:
                ok = False
                falta(faltas, "decomposição do motor", f"{ch['rotulo']}: o motor não devolveu principal_corrigido",
                      FONTE["r1_prev"])
        registros.append(reg)
    alertas.extend(f"[motor de atualização, R1] {a}" for a in alertas_motor)
    if fronteira_dez is not None:
        # A parcela de 12/2021 entra no consolidado só se devida até dez./2021 (Manual 2026, item 4.3.1.1, Nota 5;
        # F1 §7). Sem o vencimento, as duas leituras: dentro (o consolidado informado já a contém) ou fora (à parte).
        ok = False
        reg = next(r for r in registros if r["parcela"] == comp_txt(COMP_CONSOLIDACAO))
        leituras = ""
        if reg["motor_exit"] == EXIT_OK and all(r["motor_exit"] == EXIT_OK for r in registros):
            fora_total = total
            leituras = (f" Total na data-base: {q2(fora_total - Decimal(reg['valor_atualizado']))} se dentro do "
                        f"consolidado; {q2(fora_total)} se fora.")
        falta(faltas, "vencimento devido da competência 12/2021 (datas_vencimento)",
              "com valor_consolidado_12_2021, a parcela de 12/2021 entra no consolidado se devida até dez./2021 e "
              "fica fora se o vencimento devido cai em jan./2022 (Manual 2026, item 4.3.1.1, Nota 5); sem "
              "datas_vencimento['2021-12'], a fronteira fica aberta." + leituras, FONTE["r1_prev"])
        alertas.append("[VERIFICAR] competência 12/2021 sem vencimento devido: dentro ou fora do consolidado de "
                       "12/2021 informado; total da parte não fechado.")

    if e["natureza"] == "previdenciaria" and comp_anterior(base) > COMP_ULTIMA_TAXA_LEGAL_INPC:
        ok = False
        falta(faltas, "taxa legal com dedução do INPC sem tabela do CJF",
              f"a data-base {comp_txt(base)} usa competências posteriores a "
              f"{comp_txt(COMP_ULTIMA_TAXA_LEGAL_INPC)} (aplicadas depois de jun./2026); a tabela do Manual 2026 "
              "(item 4.3.2, Nota 3) termina aí, e a série do cache do motor é derivada, não publicada pelo CJF",
              FONTE["r1_prev"])
    memoria.append(f"R1: {len(chamadas)} chamada(s) ao motor de atualização (fazenda-ec113, natureza "
                   f"{e['natureza']}), do mês de cada competência até {comp_txt(base)}, juros desde a citação "
                   f"({e['data_citacao'].isoformat()})")
    # A Selic nunca incide sobre juros Selic (Res. CJF 983/2026, art. 7º, §4º): separa os juros Selic; o resto
    # do total, fora o principal, são juros não Selic (até 12/2021 e taxa legal).
    principal = componentes.get("principal_corrigido", ZERO)
    juros_s = componentes.get("juros_selic", ZERO)
    juros_ns = total - principal - juros_s
    return {
        "ok": ok,
        "total": total if ok else None,
        "principal": principal if ok else None,
        "juros_nao_selic": juros_ns if ok else None,
        "juros_selic": juros_s if ok else None,
        "componentes": {k: s2(v) for k, v in componentes.items()} if ok else None,
        "registros": registros,
    }


def _params_r1(e):
    """Parâmetros comuns de toda chamada de R1 ao motor (do mês da competência até a data-base)."""
    return {"data_final": f"{comp_txt(e['data_base_conta'])}-01", "data_citacao": e["data_citacao"].isoformat(),
            "regime": "fazenda-ec113", "natureza": e["natureza"]}


def _chave(k):
    """O motor nomeia o mesmo componente com e sem o sufixo '_corrigidos' conforme a fatia."""
    return k[:-len("_corrigidos")] if k.endswith("_corrigidos") else k


def _sem_competencia(txt):
    """Junta as faltas repetidas por parcela: tira o período do texto do motor."""
    return re.sub(r"\b\d{4}-\d{2}(\.\.\d{4}-\d{2})?\b", "AAAA-MM", txt)


def fatias_r1(e, res):
    """Resumo por marco: consolidação 12/2021, Selic até 08/2025, Tema 1.419 desde 09/2025, data-base."""
    comp = res["componentes"] or {}
    return [
        {"marco": "competência 12/2021 (consolidação)", "componente": "juros até 12/2021",
         "valor": comp.get("juros_ate_12_2021"),
         "regra": "correção INPC (IPCA-E no BPC) e juros da poupança desde a citação; consolidação com INPC de "
                  "nov./2021 (0,84%) e juros de dez./2021 (0,4412%)"},
        {"marco": "competências 12/2021 a 08/2025", "componente": "juros Selic",
         "valor": comp.get("juros_selic"),
         "regra": "Selic simples sobre o consolidado; a de ago./2025 computada em set./2025"},
        {"marco": "competências 09/2025 até a data-base", "componente": "juros da taxa legal",
         "valor": comp.get("juros_taxa_legal"),
         "regra": "INPC + taxa legal com dedução do INPC (previdenciário); IPCA-15 + taxa legal com dedução do "
                  "IPCA-15 (assistencial); a de cada competência aplicada no mês seguinte"},
        {"marco": f"data-base {comp_txt(e['data_base_conta'])}", "componente": "principal corrigido",
         "valor": comp.get("principal_corrigido"), "regra": "fim de R1; início de R2 (Res. CJF 983/2026, art. 7º)"},
    ]


# ---------------------------------------------------------------- honorários (Súmula 111)

def honorarios(e, res, janelas, incertas, motor_a, faltas, alertas, memoria):
    if "honorarios_sucumbenciais" in e:
        memoria.append(f"honorários sucumbenciais fixados = {q2(e['honorarios_sucumbenciais'])}")
        return None, e["honorarios_sucumbenciais"]
    if "honorarios_percentual" not in e:
        return None, None
    sent = e["data_sentenca"]
    if not res["ok"]:
        falta(faltas, "base dos honorários", "depende do valor atualizado das vencidas (R1 sem número)",
              FONTE["sumula_111"])
        return None, None

    def vencida(comp):
        """(antes da sentença: True/False/None, descrição do vencimento) — Manual 2026, honorários, Nota 2."""
        if comp in incertas:
            return None, f"{e['datas_vencimento'][comp].isoformat()} (informada; {incertas[comp]})"
        if comp in e["datas_vencimento"]:
            d = e["datas_vencimento"][comp]
            return d < sent, f"{d.isoformat()} (informada)"
        jan = janelas.janela(comp, None)
        if jan is None:
            return None, "competência anterior a 07/1991, sem janela de pagamento capturada"
        a, b = jan[0], jan[1]
        return pago_antes(a, b, sent), f"janela {a.isoformat()} a {b.isoformat()}"

    base, fora, abertas = ZERO, [], []
    for reg in res["registros"]:
        if reg["parcela"] == "consolidado 12/2021":
            # a competência mais recente do consolidado decide (12/2021 só quando devida até dez./2021)
            antes, _ = vencida(COMP_CONSOLIDACAO if dez_2021_no_consolidado(e, incertas) is True else (2021, 11))
            if antes is True:
                base += Decimal(reg["valor_atualizado"])
            else:
                falta(faltas, "base dos honorários",
                      "o consolidado de 12/2021 mistura parcelas anteriores e posteriores à sentença; informe "
                      "as parcelas em vez do consolidado ou os honorários já fixados", FONTE["sumula_111"])
                return None, None
            continue
        c = (int(reg["parcela"][:4]), int(reg["parcela"][5:]))
        antes, desc = vencida(c)
        if antes is True:
            base += Decimal(reg["valor_atualizado"])
        elif antes is False:
            fora.append(reg["parcela"])
        else:
            abertas.append((reg["parcela"], desc, Decimal(reg["valor_atualizado"])))
    if abertas:
        com = base + sum((v for _, _, v in abertas), ZERO)
        falta(faltas, "base dos honorários",
              "vencimento da competência cruza a sentença (art. 41-A: pagamento distribuído na janela; Manual "
              "2026, Nota 2 sobre honorários: vencida = vencimento anterior à sentença): "
              + "; ".join(f"{p} ({d})" for p, d, _ in abertas)
              + f". Base sem elas {q2(base)}; com elas {q2(com)}. Informe datas_vencimento ou os honorários já "
                "fixados", FONTE["sumula_111"])
        memoria.append(f"base dos honorários em aberto: {q2(base)} (sem {', '.join(p for p, _, _ in abertas)}) ou "
                       f"{q2(com)} (com)")

    # Base sucumbencial separada do crédito da parte (Manual 2026, Nota 4 sobre honorários): o R1 é líquido de
    # parcelas[].pago, mas o pagamento administrativo feito após a citação não reduz a base. A entrada não traz a
    # data nem a natureza do pago (pagamento administrativo do benefício pedido × benefício já em manutenção antes da
    # ação, como na revisão), então a base com pago não fecha: saem as duas leituras.
    liquido = {(int(r["parcela"][:4]), int(r["parcela"][5:])): Decimal(r["valor_atualizado"])
               for r in res["registros"] if r["parcela"] != "consolidado 12/2021"}
    com_pago, base_bruta, fronteira_pago = [], base, []
    for p in e["parcelas"]:
        c = p["competencia"]
        if p["pago"] == 0:
            continue
        if "valor_consolidado_12_2021" in e and (c < COMP_CONSOLIDACAO or (
                c == COMP_CONSOLIDACAO and dez_2021_no_consolidado(e, incertas) is not False)):
            falta(faltas, "base dos honorários",
                  f"pagamento administrativo (parcelas[].pago) em {comp_txt(c)}, dentro do consolidado de 12/2021 "
                  "(ou, em 12/2021 sem vencimento devido, possivelmente dentro): o "
                  "consolidado não separa o pago, e a base dos honorários não se reduz pelo pagamento feito após a "
                  "citação; informe as parcelas em vez do consolidado ou os honorários já fixados", FONTE["base_pago"])
            return None, None
        antes, desc = vencida(c)
        if antes is None:
            # Parcela com pago cuja janela cruza a sentença: se o pago a quitou inteira, ela nem aparece nos
            # registros de R1 (diferença zero), e o vencimento continua em aberto (Manual 2026, Notas 2 e 4).
            fronteira_pago.append(f"{comp_txt(c)} ({desc}; devido {q2(p['devido'])}, pago {q2(p['pago'])})")
            continue
        if antes is False:
            continue
        codigo, out = motor_a.calcular(dict({"valor": str(p["devido"]), "data_inicial": f"{comp_txt(c)}-01"},
                                            **_params_r1(e)))
        if codigo != EXIT_OK:
            falta(faltas, "base dos honorários", f"{comp_txt(c)}: o motor não atualizou o devido integral (exit "
                  f"{codigo})", FONTE["base_pago"])
            return None, None
        bruto = Decimal(out["valor_final"])
        com_pago.append(comp_txt(c))
        base_bruta += bruto - liquido.get(c, ZERO)
    if com_pago:
        falta(faltas, "base dos honorários",
              f"pagamento administrativo (parcelas[].pago) em competência da base ({', '.join(com_pago)}): feito após "
              "a citação, não altera a base dos honorários, que abrange a totalidade dos valores devidos; benefício "
              "já pago antes da ação fica fora. A entrada não diz a data nem a natureza do pago. Base líquida do "
              f"pago {q2(base)}; base com o devido integral {q2(base_bruta)}. Informe os honorários já fixados ou, se "
              "o pago é anterior à ação, a parcela pela diferença (devido − pago, sem pago)", FONTE["base_pago"])
        memoria.append(f"base dos honorários em aberto pelo pago de {', '.join(com_pago)}: {q2(base)} (líquida) ou "
                       f"{q2(base_bruta)} (devido integral, Manual 2026, Nota 4)")
    novas = [f for f in fronteira_pago if f.split(" ")[0] not in {p for p, _, _ in abertas}]
    if novas:
        falta(faltas, "base dos honorários",
              "competência com pagamento administrativo (parcelas[].pago) cujo vencimento cruza a sentença (art. "
              "41-A: pagamento distribuído na janela; Manual 2026, Nota 2 sobre honorários): " + "; ".join(novas)
              + ". O pagamento, ainda que integral, não diz se ela venceu antes da sentença nem a natureza do pago "
                "(Nota 4: o pago após a citação não reduz a base). Informe datas_vencimento ou os honorários já "
                "fixados", FONTE["base_pago"])
        memoria.append(f"base dos honorários em aberto pela fronteira de {', '.join(f.split(' ')[0] for f in novas)} "
                       "(competência com pago)")
    if abertas or com_pago or fronteira_pago:
        return None, None
    valor = q2(base * e["honorarios_percentual"] / CEM)
    memoria.append(f"base dos honorários (vencidas com toda a janela de pagamento antes de {sent.isoformat()}, "
                   f"atualizadas) = {q2(base)}; fora da base: {', '.join(fora) or 'nenhuma'}; honorários = "
                   f"{e['honorarios_percentual']}% × {q2(base)} = {valor}")
    if janelas.motor is None:
        alertas.append(f"[VERIFICAR] {janelas.sem_calendario}: dias úteis contados só sem sábado e domingo na base "
                       "dos honorários (janelas alargadas).")
    return base, valor


# ---------------------------------------------------------------- via, prazo e graça

def ciclo_precatorio(d):
    """(corte, ano_limite_pagamento, aviso) do precatório apresentado em d."""
    def corte(ano):
        if ano <= 2021:
            return dt.date(ano, 7, 1)
        if ano <= 2025:
            return dt.date(ano, 4, 2)
        return dt.date(ano, 2, 1)
    c = corte(d.year)
    aviso = None
    if d <= c:
        ano = d.year
    else:
        ano = d.year + 1
        c = corte(ano)
        if d < VIGENCIA_EC136 and ano >= 2026:
            aviso = (f"[VERIFICAR] apresentado em {d.isoformat()}, antes da EC 136 e depois do corte de 2 de abril: "
                     f"o ciclo seguinte usa o corte de 1º de fevereiro de {ano} (EC 136); pela regra anterior seria "
                     f"2 de abril. O exercício de pagamento não muda; muda o início da graça.")
    return c, ano + 1, aviso


def prazo_rpv(e, motor_b, faltas, alertas):
    """Data-limite da RPV pelo motor de prazos (CC 132), da apresentação."""
    if e["rito"] == "JEF":
        texto = "60 dias da entrega da requisição (Lei 10.259, art. 17)"
        entrada = {"prazo": 60, "unidade": "corridos"}
    else:
        texto = "2 meses da entrega da requisição (CPC, art. 535, §3º, II)"
        entrada = {"prazo": 2, "unidade": "meses"}
    if "data_apresentacao" not in e:
        return texto, None
    if motor_b is None:
        falta(faltas, "motor de prazos", f"{MOTOR_PRAZO.name} não encontrado na pasta do script; a data-limite "
              "da RPV sai em fórmula: apresentação + " + texto.split(" da ")[0], FONTE["prazo_rpv_jef"])
        return texto, None
    entrada.update({"marco": e["data_apresentacao"].isoformat(), "meio": "ciencia-expressa", "rito": "cpc",
                    "natureza": "material"})
    codigo, saida = motor_b.calcular(entrada)
    if codigo != EXIT_OK:
        raise EntradaInvalida(f"motor de prazos recusou a data de apresentação: {saida.get('detalhe')}")
    alertas.append("[VERIFICAR] data-limite da RPV contada como prazo de direito material (CC, art. 132: exclui o "
                   "dia da apresentação; vencimento em dia não útil passa ao seguinte), pelo motor de prazos.")
    return texto, dt.date.fromisoformat(saida["data_limite"])


def mm_aaaa(c):
    return f"{c[1]:02d}/{c[0]:04d}"


def precatorio_graca(e, inicio, fim, saida, faltas, alertas, fundamento):
    """Graça do precatório (04, RPV-06, item 3 a 7): fronteira da Selic na fatia 3, graça antes de set./2025 (Tema
    1.335, só IPCA-E), tensão IPCA × IPCA-E desde set./2025 e as séries que faltam. Nenhuma escolha de leitura."""
    base = e.get("data_base_conta")
    series = [{"dado": "saldos_por_fatia", "alternativa_as_series": True}]
    if e["parcelas"] and any(p["competencia"] not in e["datas_vencimento"] for p in e["parcelas"]):
        series.append({"dado": "principal_por_competencia", "com_data_devida": True})
    primeira = e["parcelas"][0]["competencia"] if e["parcelas"] else None
    if primeira and primeira < COMP_CONSOLIDACAO and "valor_consolidado_12_2021" not in e:
        cit = mes_de(e["data_citacao"])
        if cit < COMP_CONSOLIDACAO:
            series.append({"dado": "juros_poupanca", "de": comp_txt(cit), "ate": "2021-11"})
        series.append({"dado": "INPC" if e["natureza"] == "previdenciaria" else "IPCA-E",
                       "de": comp_txt(primeira), "ate": "2021-11"})
    g = mes_de(inicio)
    fronteira, sel = None, None
    if base is not None and e["parcelas"] and inicio < INICIO_EC136_SET:
        f = comp_anterior(g)
        if base <= f <= COMP_FIM_SELIC:
            fronteira = f
            fixas, c = [], base
            while c < f:
                fixas.append(c)
                c = comp_seguinte(c)
            termos = " + ".join(f"Selic_comp_{mm_aaaa(x)}" for x in fixas)
            saida["fronteira_graca_selic"] = "[VERIFICAR]"
            saida["formula_fronteira_graca_selic"] = (f"juros_selic_fatia3 = consolidado × ("
                                                      + (termos + " + " if termos else "")
                                                      + f"δ × Selic_comp_{mm_aaaa(f)})")
            saida["leituras_fronteira_graca_selic"] = {
                "leitura_a_periodo_remunerado": {"delta": 1,
                                                 "competencias_selic_fatia3": [comp_txt(x) for x in fixas + [f]]},
                "leitura_b_mes_de_aplicacao": {"delta": 0, "competencias_selic_fatia3": [comp_txt(x) for x in fixas]}}
            saida["padrao_fronteira_graca_selic"] = None
            saida["rateio_diario_fronteira_graca"] = False   # o corpus não traz rateio do dia anterior à graça
            fundamento.append(FONTE["fronteira_selic"])
            falta(faltas, "fronteira da graça na Selic (fatia 3)",
                  f"a Selic da competência {comp_txt(f)} é aplicada em {comp_txt(g)}, mês em que a graça começa "
                  f"({inicio.isoformat()}), e remunera {comp_txt(f)}, anterior a ela: leitura A (período remunerado, "
                  "δ = 1) ou B (mês de aplicação, δ = 0); o Manual 2026 (item 4.3.1.1, Nota 4, \"b\") fixa só a "
                  "defasagem mensal, e nenhuma fonte do corpus escolhe. Sem padrão, sem rateio diário",
                  FONTE["fronteira_selic"])
            alertas.append(f"[VERIFICAR] fronteira da graça na Selic: competência {comp_txt(f)} entra na leitura A "
                           "(período remunerado) e sai na B (mês de aplicação); as duas contas, sem padrão.")
        sel_fim = comp_anterior(fronteira) if fronteira else min(comp_anterior(g), COMP_FIM_SELIC)
        sel_ini = max(COMP_CONSOLIDACAO, primeira) if primeira else COMP_CONSOLIDACAO
        if sel_ini <= sel_fim:
            sel = (sel_ini, sel_fim)
            series.append({"dado": "Selic", "competencias_de": comp_txt(sel_ini), "competencias_ate": comp_txt(sel_fim)})
        if fronteira:
            series.append({"dado": "Selic", "competencias_de": comp_txt(fronteira), "competencias_ate": comp_txt(fronteira),
                           "so_leitura": "A"})
        fim_pre = min(fim, INICIO_EC136_SET - dt.timedelta(days=1))
        saida["graca_antes_set_2025"] = {
            "inicio": inicio.isoformat(), "fim": fim_pre.isoformat(), "selic": False, "juros": False,
            "indice": "IPCA-E",
            "formula": f"principal_e_juros_em_{inicio.strftime('%d/%m/%Y')} × fator_IPCA-E({mm_aaaa(g)}–"
                       f"{mm_aaaa(mes_de(fim_pre))})",
            "calculada_nas_duas_leituras_da_fronteira": fronteira is not None,
            "fonte": "STF Tema 1.335; ADI 4.425-QO; LDO 2025, art. 37, §1º"}
        fundamento.append(FONTE["graca_tema_1335"])
        series.append({"dado": "IPCA-E", "de": comp_txt(g), "ate": comp_txt(mes_de(fim_pre))})
        falta(faltas, "série do IPCA-E do período de graça",
              f"de {inicio.isoformat()} a {fim_pre.isoformat()} a graça afasta a Selic e os juros, só correção pelo "
              "IPCA-E (STF Tema 1.335; ADI 4.425-QO; LDO 2025, art. 37, §1º); a série mensal não está no corpus",
              FONTE["graca_tema_1335"])
    if fim >= INICIO_EC136_SET:
        de = max(mes_de(INICIO_EC136_SET), g)
        ate = comp_txt(mes_de(e["data_pagamento"])) if "data_pagamento" in e else "pagamento"
        ate_txt = mm_aaaa(mes_de(e["data_pagamento"])) if "data_pagamento" in e else "pagamento"
        saldo = f"saldo_01/{mm_aaaa(de)}"

        def conta(indice):
            return {"indice": indice, "juros_2_aa": False, "limite_selic_consolidado": True,
                    # Res. CJF 983/2026, art. 7º, §4º: a Selic do limite não incide sobre os juros Selic anteriores
                    "formula": f"min(lado_indice, {saldo} + base_elegivel_selic × Σ Selic({mm_aaaa(de)}–{ate_txt}))",
                    "calculada_nas_duas_leituras_da_fronteira": fronteira is not None,
                    "lado_indice": lado_indice(indice, de, ate_txt)}
        saida["leituras_set_2025_pagamento"] = {"conta_ipca": conta("IPCA"), "conta_ipca_e": conta("IPCA-E")}
        saida[f"composicao_{saldo.replace('/', '_')}"] = {
            "formula_saldo": f"{saldo} = principal_corrigido + juros_consolidados_dez_2021 + juros_selic_anteriores",
            "formula_base_elegivel_selic": "base_elegivel_selic = principal_corrigido + juros_consolidados_dez_2021",
            "juros_selic_anteriores_recebem_nova_selic": False,
            "fonte": "Res. CJF 983/2026, art. 7º, §§3º, II e III, e 4º",
            "parcelas": composicao_saldo(e, base, inicio, de, sel, fronteira, saida.get("graca_antes_set_2025"))}
        if e["parcelas"]:
            juros_anteriores_no_indice(e, saida, faltas, alertas, de, ate_txt)
        saida["padrao_set_2025_pagamento"] = None
        fundamento.append(FONTE["tensao_indice"])
        alertas.append("[VERIFICAR] tensão de índice na graça desde set./2025: a Res. CJF 983/2026, art. 7º, §3º, III, "
                       "nomeia o IPCA; as LDOs 2025 (art. 37, §1º) e 2026 (art. 41, §1º) mandam o IPCA-E "
                       "\"exclusivamente\". Duas contas, sem os 2% a.a., com o limite da Selic sobre a base elegível (principal e juros "
                       "consolidados em dez./2021; nunca sobre os juros Selic anteriores, art. 7º, §4º); "
                       "sem padrão.")
        if e["parcelas"]:            # sem atrasados não há conta a atualizar: a tensão não muda nenhum número da saída
            falta(faltas, "índice da graça desde set./2025 (IPCA × IPCA-E)",
                  "nenhum texto do corpus concilia a Res. CJF 983/2026 (IPCA) com as LDOs (IPCA-E); as duas contas saem "
                  "em leituras_set_2025_pagamento, sem padrão", FONTE["tensao_indice"])
        for dado in ("IPCA", "IPCA-E", "Selic"):
            series.append({"dado": dado, "de": comp_txt(de), "ate": ate})
    if "data_pagamento" in e:
        series.append({"dado": "data_efetivo_deposito", "se_diferente_de": e["data_pagamento"].isoformat()})
    saida["dados_faltantes_series"] = series
    motivos = ["dados_faltantes_series"] + (["fronteira_graca_selic"] if fronteira else []) \
        + [m for m in saida.get("exit_3_por", []) if m not in ("dados_faltantes_series", "fronteira_graca_selic")]
    saida["exit_3_por"] = motivos


def composicao_saldo(e, base, inicio, de, sel, fronteira, graca_pre):
    """Cada parcela do saldo do início do ramo do índice, com data e posição (04, RPV-06; golden r4)."""
    pos = f"{de[0]:04d}-{de[1]:02d}-01"
    na_graca = (f" × fator_IPCA-E({mm_aaaa(mes_de(inicio))}–{mm_aaaa(mes_de(dt.date.fromisoformat(graca_pre['fim'])))}) "
                "na graça") if graca_pre else ""
    out = []
    if base is not None:
        out.append({"parcela": "principal_corrigido", "posicao_em": pos,
                    "composicao": f"principal até a data-base {mm_aaaa(base)}"
                                  + (f", mantido até {(inicio - dt.timedelta(days=1)).strftime('%d/%m/%Y')} e" if graca_pre
                                     else ", atualizado até a posição") + na_graca})
    primeira = e["parcelas"][0]["competencia"] if e["parcelas"] else None
    if "valor_consolidado_12_2021" in e or (primeira and primeira < COMP_CONSOLIDACAO):
        out.append({"parcela": "juros_consolidados_dez_2021", "consolidados_em": "2021-12", "posicao_em": pos,
                    "composicao": "juros da fatia 1 consolidados em 12/2021, sem novos juros desde então"
                                  + ("," + na_graca if na_graca else "")})
    if sel:
        j = {"parcela": "juros_selic_anteriores", "competencias_de": comp_txt(sel[0]), "competencias_ate": comp_txt(sel[1])}
        if fronteira:
            j["competencia_adicional_leitura_a"] = comp_txt(fronteira)
        j.update({"aplicadas_de": comp_txt(comp_seguinte(sel[0])), "aplicadas_ate": comp_txt(comp_seguinte(sel[1]))})
        if fronteira:
            j["aplicada_adicional_leitura_a"] = comp_txt(comp_seguinte(fronteira))
        j.update({"posicao_em": pos,
                  "composicao": "soma simples da Selic sobre a base elegível, sem Selic sobre Selic (§4º)"
                                + ("," + na_graca if na_graca else "")})
        out.append(j)
    return out


def lado_indice(indice, de, ate_txt):
    """As duas hipóteses do lado do índice desde set./2025 (juros anteriores corrigidos ou não pelo índice)."""
    periodo = f"{mm_aaaa(de)}–{ate_txt}"
    return {"hipotese_1_saldo_inteiro": f"saldo_01/{mm_aaaa(de)} × fator_{indice}({periodo})",
            "hipotese_2_so_principal": f"principal_corrigido × fator_{indice}({periodo}) + juros_consolidados_dez_2021 + "
                                       "juros_selic_anteriores"}


def juros_anteriores_no_indice(e, saida, faltas, alertas, de, ate_txt):
    """Ramo do índice (IPCA/IPCA-E) desde set./2025: a Res. CJF 983/2026, art. 7º, §3º, III, não diz se os juros
    anteriores (até dez./2021 e Selic) recebem a correção do índice. Duas hipóteses, sem padrão, e a conta fica aberta."""
    saida["tratamento_juros_anteriores_indice"] = "indeterminado"
    saida["padrao_tratamento_juros_anteriores_indice"] = None
    saida["fundamento_juros_anteriores_indice"] = (
        "Res. CJF 983/2026, art. 7º, §3º, III, manda o IPCA 'sobre o valor principal atualizado' e não diz se os juros "
        "anteriores, já no saldo, são corrigidos pelo índice: falta de fundamento no corpus, sem padrão")
    if not saida.get("leituras_set_2025_pagamento"):
        # fora do precatório com graça, as hipóteses saem à parte, pelo índice da Res. 983 (IPCA)
        saida["hipoteses_juros_anteriores_indice"] = lado_indice("IPCA", de, ate_txt)
    if not any(a.startswith("[VERIFICAR] juros anteriores no índice: indeterminado") for a in alertas):
        alertas.append("[VERIFICAR] juros anteriores no índice: indeterminado. A Res. CJF 983/2026, art. 7º, §3º, III, "
                       "não diz se os juros até dez./2021 e os juros Selic recebem o IPCA (ou IPCA-E) desde set./2025; "
                       "duas hipóteses (saldo inteiro × fator; principal × fator + juros anteriores), sem padrão.")
    falta(faltas, "tratamento dos juros anteriores no índice desde set./2025",
          "falta fundamento: a Res. CJF 983/2026, art. 7º, §3º, III, manda o IPCA sobre o valor principal atualizado e "
          "não diz se os juros anteriores (consolidados em dez./2021 e juros Selic) recebem a correção do índice ou "
          "entram sem ela; nenhum texto do corpus decide. As duas hipóteses saem sem padrão", FONTE["r2"])
    motivos = saida.setdefault("exit_3_por", [])
    if "tratamento_juros_anteriores_indice" not in motivos:
        motivos.append("tratamento_juros_anteriores_indice")


def via_e_prazos(e, res, hon_sucumb, motor_b, tabela_sm, faltas, alertas, memoria, fundamento, saida):
    tem_atrasados = bool(e["parcelas"])
    especie, graca = None, None
    if "valor_atualizado_ate_transmissao" not in e:
        if tem_atrasados:
            falta(faltas, "valor atualizado até a transmissão ao tribunal",
                  "sem ele a via (RPV × precatório) não fecha: o valor da data da conta não basta "
                  "(Res. CJF 983/2026, art. 3º, §4º); a espécie decide a graça e o prazo de pagamento",
                  FONTE["limite"])
        return None, None
    fundamento += [FONTE["limite"], FONTE["via"], FONTE["honorarios_requisicao"]]
    sm, sm_fonte = salario_minimo(e, tabela_sm, faltas)
    # Política única de centavos (igual ao valor da causa): o valor classificado é o exibido, arredondado a 2 casas,
    # meio para cima, antes de comparar com o limite; nunca a fração de centavo da entrada.
    v = q2(e["valor_atualizado_ate_transmissao"])
    saida["valor_verificado"] = saida["valor_classificado"] = s2(v)
    saida["marco_verificacao"] = "transmissão ao tribunal (Res. CJF 983/2026, art. 3º §4º)"
    saida["salario_minimo_do_limite"] = "vigente na transmissão (interpretação declarada, M4)"
    saida["salario_minimo"] = {"valor": s2(sm), "fonte": sm_fonte,
                               "data_referencia": e["data_transmissao"].isoformat()}
    contr = e.get("honorarios_contratuais")
    saida["classificacao_honorarios"] = {
        "contratuais": None if contr is None else
        {"valor": s2(contr), "regra": "destacados do crédito da parte e incluídos no valor classificado "
                                      "(Res. CJF 983/2026, art. 16, §§2º e 3º)"},
        "sucumbenciais": None if hon_sucumb is None else
        {"valor": s2(hon_sucumb), "valor_na_transmissao": s2(e.get("honorarios_atualizados_ate_transmissao")),
         "regra": "requisição própria, classificada pelo valor atualizado até a transmissão; não entram no valor "
                  "da parte para classificar (Res. CJF 983/2026, arts. 3º, §4º, e 16, §1º)"},
    }
    if sm is None:
        return None, None
    limite = q2(LIMITE_SM * sm)
    saida["limite_rpv"] = s2(limite)
    memoria.append(f"limite da RPV = 60 × {sm} (mínimo vigente na transmissão, M4) = {limite}")
    if v <= limite:
        via, renunciado = "RPV", ZERO
        memoria.append(f"{q2(v)} <= {limite} → RPV; margem {q2(limite - v)}")
        saida["margem"] = s2(limite - v)
    elif e["renunciar_excedente"] and contr is not None and q2(contr) > limite:
        # Art. 16, §3º: com renúncia, beneficiário + contratuais <= limite. A renúncia sai do crédito do beneficiário
        # (v − contratuais); se os contratuais sozinhos já passam do limite, nem a renúncia de todo o crédito do
        # beneficiário fecha a conta: só reduzindo o destaque, decisão do advogado. Composição incompatível → conta
        # aberta, nunca exit 0. QA final r4 A02: contratuais IGUAIS ao limite cabem (soma = limite, parte líquida
        # zero); o art. 16, §3º, não exige desigualdade estrita nem saldo positivo da parte.
        c2 = q2(contr)
        via, renunciado = None, None
        saida["composicao_renuncia"] = {
            "credito_beneficiario_antes": s2(v - c2), "honorarios_contratuais_informados": s2(c2),
            "limite": s2(limite), "excesso_dos_contratuais_sobre_o_limite": s2(c2 - limite),
            "compativel": False}
        memoria.append(f"{q2(v)} > {limite}; renúncia pedida, mas contratuais {c2} > limite {limite}: beneficiário "
                       f"+ contratuais não cabem no limite nem com renúncia de todo o crédito do beneficiário "
                       f"({q2(v - c2)})")
        falta(faltas, "honorários contratuais destacados após a renúncia",
              f"com renúncia, beneficiário + contratuais não podem passar do limite (Res. CJF 983/2026, art. 16, §3º). "
              f"Fórmula: beneficiário_pós = {limite} − contratuais_pós, com 0 < contratuais_pós <= {limite} "
              f"(na igualdade, beneficiário_pós = 0); os contratuais informados ({c2}) passam do limite. Quanto "
              f"destacar após a renúncia é decisão do advogado: informe honorarios_contratuais compatíveis (até "
              f"{limite}) ou retire a renúncia (→ precatório)", FONTE["renuncia"])
        fundamento.append(FONTE["renuncia"])
        saida.setdefault("exit_3_por", []).append("composicao_renuncia_incompativel")
    elif e["renunciar_excedente"]:
        via, renunciado = "RPV-com-renuncia", v - limite
        memoria.append(f"{q2(v)} > {limite}; renúncia expressa ao excedente de {q2(renunciado)} → RPV")
        alertas.append("Renúncia expressa ao excedente: crédito e contratuais destacados não passam do limite "
                       "(Res. CJF 983/2026, art. 16, §3º); quem decide renunciar é o advogado com o cliente.")
        if contr is not None:
            c2 = q2(contr)
            saida["composicao_renuncia"] = {
                "credito_beneficiario_antes": s2(v - c2), "honorarios_contratuais": s2(c2),
                "credito_beneficiario_apos": s2(limite - c2), "total_requisitado": s2(limite), "compativel": True}
            memoria.append(f"art. 16, §3º: beneficiário {q2(v - c2)} − renúncia {q2(renunciado)} = {q2(limite - c2)}; "
                           f"+ contratuais {c2} = {limite} (cabe no limite)")
            alertas.append("Renúncia com contratuais destacados: a renúncia sai do crédito do beneficiário e o destaque "
                           "fica no valor informado; se o contrato prevê percentual sobre o que o cliente recebe, "
                           "refazer o destaque e conferir de novo o art. 16, §3º.")
            if c2 == limite:
                # QA final r4 A02: igualdade é composição válida, com parte líquida zero (art. 16, §3º)
                memoria.append(f"contratuais {c2} = limite {limite}: composição válida pelo art. 16, §3º, com crédito "
                               "líquido do beneficiário zero após a renúncia")
                alertas.append("[VERIFICAR] Contratuais iguais ao limite: a soma cabe no art. 16, §3º, mas o "
                               "beneficiário não recebe nada após a renúncia; a validade do contrato e da renúncia "
                               "não é conferida por este cálculo.")
    else:
        via, renunciado = "precatorio", ZERO
        memoria.append(f"{q2(v)} > {limite} → precatório (ou RPV com renúncia expressa de {q2(v - limite)})")
    saida["via"], saida["valor_renunciado"] = via, (None if renunciado is None else s2(renunciado))
    if via != "RPV":
        fundamento.append(FONTE["fracionar"])
        alertas.append("Vedado fracionar: parte RPV e parte precatório (CF, art. 100, §8º; Lei 10.259, art. 17, §3º).")
    if "honorarios_percentual" in e or "honorarios_sucumbenciais" in e:
        # Requisição própria, classificada pelo crédito atualizado até a transmissão (Res. CJF 983/2026, arts. 3º, §4º,
        # e 16): o valor da data-base (percentual) ou da fixação não classifica, nem com alerta.
        hon_t = e.get("honorarios_atualizados_ate_transmissao")
        hon_t = None if hon_t is None else q2(hon_t)
        if hon_t is None:
            saida["via_honorarios_sucumbenciais"] = None
            falta(faltas, "honorários sucumbenciais atualizados até a transmissão",
                  "a via dos sucumbenciais (requisição própria) se classifica pelo valor atualizado até a transmissão; "
                  + (f"o valor calculado ({q2(hon_sucumb)}) é da data-base ou da fixação"
                     if hon_sucumb is not None else "os honorários não fecharam")
                  + f". Fórmula: via = RPV se honorários atualizados até {e['data_transmissao'].isoformat()} <= "
                    f"{limite}, senão precatório; informe honorarios_atualizados_ate_transmissao",
                  FONTE["honorarios_requisicao"])
        else:
            via_h = "RPV" if hon_t <= limite else "precatorio"
            saida["via_honorarios_sucumbenciais"] = via_h
            saida["honorarios_classificados"] = s2(hon_t)
            saida["valores_classificados"] = [s2(v), s2(hon_t)]
            memoria.append(f"honorários sucumbenciais atualizados até a transmissão {q2(hon_t)} classificados à "
                           f"parte → {via_h}")

    if via is None:
        return None, None
    # prazo de pagamento e período de graça
    if via.startswith("RPV"):
        especie = "RPV"
        texto, limite_pag = prazo_rpv(e, motor_b, faltas, alertas)
        fundamento.append(FONTE["prazo_rpv_jef"] if e["rito"] == "JEF" else FONTE["prazo_rpv_comum"])
        fundamento.append(FONTE["graca_rpv"])
        saida["prazo_pagamento"] = texto
        if "data_apresentacao" in e:
            g_fim = e["data_apresentacao"] + dt.timedelta(days=60)
            graca = (e["data_apresentacao"], g_fim)
            saida["periodo_graca"] = {"inicio": graca[0].isoformat(), "fim": g_fim.isoformat(),
                                      "fonte": "Manual 2026, cap. 5, Nota 2 (60 dias da apresentação)"}
            if e["rito"] == "comum":
                alertas.append("[VERIFICAR] rito comum: o prazo legal da RPV é de 2 meses (CPC, art. 535, §3º, II), "
                               "mas a graça sem juros do Manual 2026 (cap. 5, Nota 2) é de 60 dias.")
        saida["data_limite_pagamento"] = limite_pag.isoformat() if limite_pag else None
    else:
        especie = "precatorio"
        fundamento += [FONTE["prazo_precatorio"], FONTE["graca_precatorio"]]
        saida["prazo_pagamento"] = ("até 31/12 do exercício seguinte se apresentado até o corte constitucional "
                                    "(1º de fevereiro desde a EC 136; 2 de abril de 2022 até a EC 136)")
        if "data_apresentacao" in e:
            corte, ano_pag, aviso = ciclo_precatorio(e["data_apresentacao"])
            limite_pag = dt.date(ano_pag, 12, 31)
            graca = (corte, limite_pag)
            saida["data_limite_pagamento"] = saida["prazo_pagamento"] = limite_pag.isoformat()
            saida["nota"] = "sem juros no período do art. 100 §5º (EC 113 art. 3º §3º, red. EC 136)"
            saida["periodo_graca"] = {"inicio": corte.isoformat(), "fim": limite_pag.isoformat(),
                                      "fonte": "Manual 2026, cap. 5, Nota 1 (a graça começa no corte constitucional)"}
            saida["inicio_graca"] = corte.isoformat()
            saida["fonte_inicio_graca"] = "Manual 2026, cap. 5, Nota 1"
            memoria.append(f"precatório apresentado em {e['data_apresentacao'].isoformat()}; corte {corte.isoformat()}"
                           f" → pagamento até {limite_pag.isoformat()}; sem juros de mora de {corte.isoformat()} a "
                           f"{limite_pag.isoformat()} se pago no prazo")
            alertas.append("Sem juros de mora no período do art. 100, §5º, da CF (EC 113, art. 3º, §3º, redação da "
                           "EC 136), só se o pagamento for tempestivo; não afasta os juros do resto do crédito.")
            precatorio_graca(e, corte, limite_pag, saida, faltas, alertas, fundamento)
            if aviso:
                alertas.append(aviso)
                falta(faltas, "início da graça do precatório",
                      f"{aviso} Duas leituras do início da graça: {corte.isoformat()} (EC 136) ou "
                      f"{dt.date(corte.year, 4, 2).isoformat()} (regra anterior); a regra de transição não está em "
                      "context/lei/", FONTE["graca_precatorio"])
    if "data_pagamento" in e and saida.get("data_limite_pagamento"):
        no_prazo = e["data_pagamento"] <= dt.date.fromisoformat(saida["data_limite_pagamento"])
        saida["pagamento_no_prazo_constitucional"] = no_prazo
    return especie, graca


# ---------------------------------------------------------------- R2 — da data-base ao pagamento

def r2(e, res, especie, graca, motor_a, faltas, alertas, memoria, fundamento, saida):
    base = e["data_base_conta"]
    fundamento.append(FONTE["r2"])
    alertas.append(ALERTA_ADI)
    pre = True
    for campo, motivo in (
            ("data_expedicao", "expedição do requisitório: marco do motor de atualização (com expedição posterior à "
                               "data-base, o trecho entre as duas fica em aberto)"),
            ("data_apresentacao", "apresentação da requisição ao tribunal: marco da graça e, no precatório, do "
                                  "exercício de pagamento (CF, art. 100, §5º)"),
            ("data_pagamento", "data do efetivo depósito (Manual 2026, cap. 5, Nota 6): fim da conta e teste de "
                               "tempestividade; com ela, as séries do IPCA e da Selic até o depósito")):
        if campo not in e:
            falta(faltas, campo, motivo, FONTE["r2"])
            pre = False
    if especie is None:
        pre = False
    if base < COMP_CONSOLIDACAO:
        falta(faltas, "regra de R2 sem motor",
              "data-base até 11/2021: Selic sobre o consolidado em dez./2021 (Res. CJF 983/2026, art. 7º, §3º, I); "
              "o motor de atualização não cobre esse trecho", FONTE["r2"])
        pre = False

    # trecho em aberto (I-6): graça dentro da faixa Selic do §3º, II
    if graca is not None and base <= COMP_FIM_SELIC and especie != "precatorio":
        ini = max(mes_de(graca[0]), base)
        if ini <= COMP_FIM_SELIC:
            saida["fatias_em_aberto"].append({
                "trecho": f"{comp_txt(ini)} a {comp_txt(COMP_FIM_SELIC)}",
                "motivo": "a graça sem juros (Res. CJF 983/2026, art. 7º, §2º; Manual 2026, cap. 5, Notas 1 e 2) "
                          "cai na faixa da Selic do art. 7º, §3º, II, que engloba juros e não ressalva a graça; o "
                          "texto não concilia",
                "contas_possiveis": [
                    "(a) Selic do inciso II sobre principal e juros consolidados em dez./2021 (base elegível), somada "
                    "aos juros Selic anteriores sem nova Selic sobre eles (art. 7º, §4º)",
                    "(b) atualização sem juros no trecho"],
                "fonte": FONTE["r2"]})
    if "data_pagamento" in e and saida.get("pagamento_no_prazo_constitucional") is False:
        saida["fatias_em_aberto"].append({
            "trecho": f"depois de {saida['data_limite_pagamento']}",
            "motivo": "pagamento depois do prazo: a Res. CJF 983/2026, art. 7º, §6º, posiciona a conta na inscrição; "
                      "o motor de atualização não faz esse posicionamento",
            "contas_possiveis": ["até ago./2025: Selic sobre a base elegível (principal e juros consolidados em "
                                 "dez./2021) posicionada na inscrição, mais os juros Selic anteriores sem nova Selic "
                                 "(art. 7º, §4º)",
                                 "desde set./2025: a comparação do §3º, III, posicionada na inscrição, com o limite "
                                 "saldo + base_elegivel_selic × Σ Selic"],
            "fonte": FONTE["r2"]})
    # Regime entre a data-base e a expedição (I-7): a Res. CJF 983/2026, art. 7º, caput, e o F1 (03, §7) põem a R2
    # desde a data-base; o motor canônico aplica, da data-base à expedição, a fase pré-requisitório (EC 113 original
    # e Tema 1.419) e só depois a EC 136. Enquanto o motor não for conciliado com a regra, o trecho fica em aberto e
    # nenhum número sai dele: repassar o [VERIFICAR] do motor com exit 0 entregaria a conta pela regra divergente.
    inicio_r2 = dt.date(base[0], base[1], 1)
    if "data_expedicao" in e and e["data_expedicao"] > inicio_r2:
        saida["fatias_em_aberto"].append({
            "trecho": f"{comp_txt(base)} (data-base) a {e['data_expedicao'].isoformat()} (expedição)",
            "motivo": "a Res. CJF 983/2026, art. 7º, caput, manda a atualização da requisição correr da data-base "
                      "informada pelo juízo até o efetivo depósito; o motor de atualização aplica nesse trecho a fase "
                      "pré-requisitório (EC 113, redação original, até 08/2025; Tema 1.419 depois) e só da expedição "
                      "em diante a Res. 983. Divergência de regime não conciliada com o dono do motor",
            "contas_possiveis": [
                "(a) Res. CJF 983/2026, art. 7º, §3º, desde a data-base (regra do F1, 03 §7, e de context/calculo-rpv.md)",
                "(b) fase pré-requisitório até a expedição e Res. CJF 983/2026 depois (motor canônico)"],
            "fonte": FONTE["r2"]})
        pre = False
    # ramo do índice desde set./2025 (qualquer espécie): os juros anteriores recebem o índice? indeterminado
    # juros anteriores = até dez./2021 + Selic; os da taxa legal (desde set./2025, antes da requisição) não entram
    if res["ok"]:
        comp_j = res["componentes"] or {}
        tem_juros = any(Decimal(comp_j.get(k) or 0) != 0 for k in ("juros_ate_12_2021", "juros_selic"))
    else:
        tem_juros = "valor_consolidado_12_2021" in e or e["parcelas"][0]["competencia"] <= COMP_FIM_SELIC
    if tem_juros and ("data_pagamento" not in e or e["data_pagamento"] >= INICIO_EC136_SET):
        de = max(mes_de(INICIO_EC136_SET), base)
        ate_txt = mm_aaaa(mes_de(e["data_pagamento"])) if "data_pagamento" in e else "pagamento"
        juros_anteriores_no_indice(e, saida, faltas, alertas, de, ate_txt)
    if saida.get("graca_antes_set_2025"):
        # Tema 1.335: na graça antes de set./2025, só IPCA-E, sem Selic; o motor não faz essa conta, e a fronteira da
        # fatia 3 não tem padrão: nenhum número de R2 sai por uma regra que a conta não fixou
        pre = False
    if not pre or not res["ok"]:
        if not res["ok"]:
            memoria.append("R2 não calculado: R1 sem número")
        else:
            memoria.append("R2 não calculado: falta dado ou há trecho em aberto")
        return None
    if e["data_pagamento"] <= e["data_expedicao"]:
        falta(faltas, "data_pagamento", "pagamento não posterior à expedição", FONTE["r2"])
        return None
    principal, juros_ns, juros_s = res["principal"], res["juros_nao_selic"], res["juros_selic"]
    if saida.get("via") == "RPV-com-renuncia":
        # Com a renúncia, o crédito requisitado é o limite (Res. CJF 983/2026, arts. 4º e 16, §3º): a redução vai aos
        # componentes antes da atualização de R2, senão o pagamento devolve o que foi renunciado.
        fator = Decimal(saida["limite_rpv"]) / q2(e["valor_atualizado_ate_transmissao"])
        principal, juros_ns, juros_s = (x * fator for x in (principal, juros_ns, juros_s))
        fundamento.append(FONTE["renuncia"])
        saida["reducao_renuncia"] = {
            "fator": str(fator.quantize(Decimal("1e-10"), rounding=ROUND_HALF_UP)),
            "regra": "limite ÷ valor na transmissão, aplicado a principal e juros da data-base",
            "principal": s2(principal), "juros_nao_selic": s2(juros_ns), "juros_selic": s2(juros_s)}
        memoria.append(f"renúncia: componentes da data-base × {saida['limite_rpv']} ÷ "
                       f"{q2(e['valor_atualizado_ate_transmissao'])} antes de R2 → principal {q2(principal)}, juros "
                       f"não Selic {q2(juros_ns)}, juros Selic {q2(juros_s)}")
        alertas.append("[VERIFICAR] renúncia aplicada antes de R2 na proporção limite ÷ valor na transmissão, igual "
                       "para principal e juros; se a requisição discriminar o crédito reduzido de outra forma, refazer "
                       "R2 por ela.")
    entrada = {
        "valor": str(q2(principal)), "valor_juros": str(q2(juros_ns)),
        "valor_juros_selic": str(q2(juros_s)),
        "data_inicial": f"{comp_txt(base)}-01", "data_expedicao": e["data_expedicao"].isoformat(),
        "data_final": e["data_pagamento"].isoformat(), "regime": "fazenda-requisitorio-ec136", "ente": "federal",
        "natureza": e["natureza"],
    }
    if graca is not None:
        entrada["periodo_graca"] = {"inicio": graca[0].isoformat(), "fim": graca[1].isoformat()}
    codigo, out = motor_a.calcular(entrada)
    if codigo == EXIT_ENTRADA:
        raise EntradaInvalida(f"motor de atualização recusou a fase R2: {out.get('detalhe')}")
    for a in out.get("alertas", []):
        if a != ALERTA_ADI and not a.startswith(("[VERIFICAR] ADI 7873", "[VERIFICAR] ADI 7.873")):
            alertas.append(f"[motor de atualização, R2] {a}")
    memoria.append(f"R2: motor de atualização (fazenda-requisitorio-ec136, federal) da data-base {comp_txt(base)} "
                   f"ao pagamento {e['data_pagamento'].isoformat()}, expedição {e['data_expedicao'].isoformat()}, "
                   f"graça {entrada.get('periodo_graca')}; vale o menor entre IPCA + 2% a.a. e Selic (art. 7º, §3º, III)")
    detalhe = {"entrada_motor": entrada, "motor_exit": codigo, "valor_final": out.get("valor_final"),
               "componentes": out.get("componentes"),
               "fatias": [{"periodo": f.get("periodo"), "indice": f.get("indice"), "tipo": f.get("tipo"),
                           "fator": f.get("fator"), "percentual": f.get("percentual")} for f in out.get("fatias", [])],
               "fonte_indice": out.get("fonte_indice")}
    if codigo != EXIT_OK:
        fa = out.get("formula_aberta") or {}
        detalhe["formula_aberta"] = fa
        for item in fa.get("faltando", []):
            txt = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
            falta(faltas, "índice ou série ausente na fase R2", txt, FONTE["r2"])
    return detalhe


# ---------------------------------------------------------------- conta principal

def calcular(bruto, motor_atualizacao=MOTOR_ATUALIZACAO, motor_prazo=MOTOR_PRAZO,
             tabela_salario_minimo=TABELA_SALARIO_MINIMO):
    """Devolve (codigo_de_saida, dict_de_saida)."""
    try:
        texto_valido(bruto)
        e = normaliza(bruto)
        return _calcular(e, motor_atualizacao, motor_prazo, tabela_salario_minimo)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}


def _calcular(e, motor_atualizacao, motor_prazo, tabela_sm):
    faltas, alertas, memoria, fundamento = [], [], [], []
    saida = {
        "versao": VERSAO, "parametros_usados": eco(e),
        "regra": "R1 (condenação até a data-base, Manual CJF 2026) → via pelo valor até a transmissão "
                 "(Res. CJF 983/2026, art. 3º, §4º) → prazo e graça → R2 (data-base ao pagamento, Res. CJF "
                 "983/2026, art. 7º)",
        "principal_corrigido": None, "juros": None, "fatias": None, "fatias_em_aberto": [],
        "total_parte": None, "base_honorarios": None, "honorarios": None, "classificacao_honorarios": None,
        "limite_rpv": None, "valor_verificado": None, "via": None, "valor_renunciado": None,
        "prazo_pagamento": None, "data_limite_pagamento": None, "pagamento_no_prazo_constitucional": None,
        "valor_no_pagamento": None, "dados_faltantes": faltas, "alertas": alertas,
        "fundamento": fundamento, "fonte": [], "memoria": memoria, "formula_aberta": None,
    }
    if e.get("titulo_com_criterio_proprio"):
        fundamento.append(FONTE["titulo"])
        alertas.append(f"[VERIFICAR] título com critério próprio ('{e['titulo_com_criterio_proprio']}'): o título "
                       "prevalece sobre o Manual (item 4.1); a conta abaixo segue o Manual e precisa ser refeita "
                       "pelo critério do título.")
        falta(faltas, "critério do título", "o título tem critério próprio, que prevalece sobre o Manual (item "
              "4.1); a conta exibida segue o Manual e não fecha antes de refeita pelo critério do título",
              FONTE["titulo"])
    if e["rito"] == "JEF":
        fundamento.append(FONTE["jef_sem_prazo_diferenciado"])
        alertas.append("No JEF não há prazo diferenciado para o INSS (Lei 10.259, art. 9º); o motor de prazos não "
                       "tem rito JEF: impugnação contada no rito cpc, com esse aviso.")
    alertas.append("Custas do INSS na Justiça Federal: indeterminado (Lei 9.289/1996 não capturada); não afirmar "
                   "isenção nem cobrança.")
    motor_b = carregar_motor(motor_prazo, "prazo")
    janelas = JanelaPagamento(motor_b)
    incertas = valida_vencimentos(e, janelas)
    tem_atrasados = bool(e["parcelas"])
    res = {"ok": False, "registros": [], "componentes": None}
    hon_sucumb = None
    if tem_atrasados:
        fundamento += [FONTE["r1_prev"] if e["natureza"] == "previdenciaria" else FONTE["r1_assist"],
                       FONTE["tema_1207"]]
        motor_a = carregar_motor(motor_atualizacao, "atualizacao")
        if motor_a is None:
            falta(faltas, "motor de atualização", f"{Path(motor_atualizacao).name} não encontrado na pasta do "
                  "script; R1 e R2 saem em fórmula (conta aberta em context/calculo-rpv.md)", FONTE["r1_prev"])
            res["total"] = None
        else:
            res = r1(e, motor_a, faltas, alertas, memoria, incertas)
        saida["fatias"] = fatias_r1(e, res) if res.get("componentes") else None
        saida["memoria_r1"] = res["registros"]
        if res["ok"]:
            saida["total_parte"] = s2(res["total"])
            saida["principal_corrigido"] = s2(res["principal"])
            saida["juros"] = {"nao_selic": s2(res["juros_nao_selic"]), "selic": s2(res["juros_selic"])}
            memoria.append(f"total da parte na data-base {comp_txt(e['data_base_conta'])} = {q2(res['total'])}")
        if "honorarios_percentual" in e or "honorarios_sucumbenciais" in e:
            fundamento.append(FONTE["sumula_111"])
            base_h, hon_sucumb = honorarios(e, res, janelas, incertas, motor_a, faltas, alertas, memoria)
            saida["base_honorarios"], saida["honorarios"] = s2(base_h), s2(hon_sucumb)
    elif "honorarios_sucumbenciais" in e:
        hon_sucumb = e["honorarios_sucumbenciais"]
        saida["honorarios"] = s2(hon_sucumb)

    especie, graca = via_e_prazos(e, res, hon_sucumb, motor_b, tabela_sm, faltas, alertas, memoria, fundamento,
                                  saida)
    if tem_atrasados:
        motor_a = carregar_motor(motor_atualizacao, "atualizacao")
        det = None
        if motor_a is not None:
            det = r2(e, res, especie, graca, motor_a, faltas, alertas, memoria, fundamento, saida)
        saida["r2"] = det
        if det and det["motor_exit"] == EXIT_OK and not saida["fatias_em_aberto"]:
            saida["valor_no_pagamento"] = det["valor_final"]
        elif det and det.get("valor_final") and not saida.get("tratamento_juros_anteriores_indice"):
            # com a tensão IPCA × IPCA-E, o motor faz só a conta do IPCA (Res. 983); nome próprio, nunca o valor final
            chave = "valor_no_pagamento_conta_ipca" if saida.get("leituras_set_2025_pagamento") else \
                "valor_no_pagamento_conta_a"
            saida[chave] = det["valor_final"]
    return _finaliza(saida, faltas)


def _finaliza(saida, faltas):
    saida["fonte"] = sorted({m for f in saida["fundamento"] for m in re.findall(r"context/[\w/.-]+\.md", f)})
    saida["fundamento"] = list(dict.fromkeys(saida["fundamento"]))
    saida["alertas"].append(AVISO_FIXO)
    if faltas or saida["fatias_em_aberto"]:
        saida["valor_no_pagamento"] = None
        saida["formula_aberta"] = {
            "expressao": "R1: Σ parcela × fator (INPC ou IPCA-E; IPCA-15 no BPC desde 09/2025) + juros por fatia "
                         "(Manual CJF 2026, itens 4.3.1.1 e 4.3.2); R2: min(V_ipca, V_selic), V_ipca = (principal + "
                         "juros) × fator_IPCA + principal × fator_IPCA × 2% a.a. fora da graça, V_selic = (principal "
                         "+ juros não Selic) × (1 + Σ Selic) + juros Selic (Res. CJF 983/2026, art. 7º, §§3º, III, e 4º)",
            "faltando": [f["item"] for f in faltas] + [f"trecho em aberto: {t['trecho']}"
                                                       for t in saida["fatias_em_aberto"]],
            "instrucao": "Valor até o pagamento não fechado: preencha os termos faltantes. Conta aberta em "
                         "context/calculo-rpv.md. O script nunca estima.",
        }
        return EXIT_FALTA, saida
    return EXIT_OK, saida


# ---------------------------------------------------------------- CLI

def build_parser():
    ap = argparse.ArgumentParser(
        prog="calc_previdenciario_rpv.py",
        description="Atrasados contra o INSS (R1 e R2), honorários da Súmula 111, RPV × precatório, prazo e graça. "
                    "Entrada JSON por --entrada ou stdin; campos em context/calculo-rpv.md, seção 8.")
    ap.add_argument("--entrada", help="arquivo JSON de entrada (sem ele, lê o stdin)")
    ap.add_argument("--versao", action="store_true", help="mostra a versão e sai")
    return ap


def emite(saida, codigo):
    """JSON no stdout e motivo no stderr, sempre em UTF-8 válido (sem traceback por caractere não codificável)."""
    texto = json.dumps(saida, ensure_ascii=False, indent=2)
    try:
        dados = (texto + "\n").encode("utf-8")
    except UnicodeEncodeError:
        dados = (json.dumps(saida, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    sys.stdout.buffer.write(dados)
    sys.stdout.flush()
    if codigo == EXIT_ENTRADA:
        sys.stderr.buffer.write(f"entrada inválida: {saida['detalhe']}\n".encode("utf-8", "backslashreplace"))
        sys.stderr.flush()


def _main(argv):
    args = build_parser().parse_args(argv)
    if args.versao:
        print(json.dumps({"script": "calc_previdenciario_rpv.py", "versao": VERSAO}))
        return EXIT_OK
    try:
        dados = Path(args.entrada).read_bytes() if args.entrada else sys.stdin.buffer.read()
        bruto = json.loads(dados.decode("utf-8"))
    except (OSError, ValueError, RecursionError) as err:   # ValueError: JSON, UTF-8 e inteiro gigante
        codigo, saida = EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": f"JSON ilegível: {err}",
                                       "versao": VERSAO}
    else:
        codigo, saida = calcular(bruto)
    emite(saida, codigo)
    return codigo


def main(argv=None):
    """Exit 1 nunca: exceção não prevista em qualquer etapa (leitura, validação, cálculo, emissão) vira exit 2 com
    JSON de erro em ASCII; argparse (--help, argumento inválido) segue com o próprio código."""
    try:
        return _main(argv)
    except SystemExit:
        raise
    except Exception as err:                                # noqa: BLE001 — fronteira do processo
        saida = {"erro": "entrada_invalida", "detalhe": f"falha não prevista ({type(err).__name__}): {err!r}",
                 "versao": VERSAO}
        try:
            sys.stdout.buffer.write((json.dumps(saida, ensure_ascii=True) + "\n").encode("ascii"))
            sys.stdout.flush()
            sys.stderr.buffer.write(f"entrada inválida: {saida['detalhe']}\n".encode("ascii", "backslashreplace"))
            sys.stderr.flush()
        except Exception:                                   # noqa: BLE001 — saída fechada: só resta o código
            pass
        return EXIT_ENTRADA


if __name__ == "__main__":
    sys.exit(main())
