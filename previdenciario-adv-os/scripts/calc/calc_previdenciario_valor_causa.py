#!/usr/bin/env python3
"""calc_previdenciario_valor_causa.py — valor da causa e alçada do JEF (previdenciário e BPC).

Conta aberta, fontes e CAMPOS: context/calculo-valor-causa.md.

USO:
    python3 calc_previdenciario_valor_causa.py --entrada caso.json
    echo '{...}' | python3 calc_previdenciario_valor_causa.py
    python3 calc_previdenciario_valor_causa.py --versao

Saída: JSON no stdout. Exit 0 = calculado; 2 = entrada inválida (inclusive
vencimento informado fora da janela legal); 3 = falta dado ou tabela (devolve a
fórmula aberta, nunca estima), competência de fronteira (leituras com e sem ela),
BPC com o mínimo mudando entre as competências (conta por competência) ou leitura
indeterminada M6 (abono nas vincendas: devolve as duas contas completas, e a
escolha é do advogado).

Só biblioteca padrão, Python 3.9+, sem rede. Tabelas e motores são achados
pela pasta deste arquivo: ../data/salario-minimo.json, o motor de atualização
(calc_previdenciario_atualizacao.py, só com corrigir_vencidas) e o motor de
prazos (calc_previdenciario_prazo.py, feriados nacionais das janelas de
pagamento do art. 41-A da Lei 8.213).
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
# QA final r7 C1: reajuste anual da renda (Lei 8.213, art. 41-A) e teto do RGPS por competência
TABELA_REAJUSTES = PASTA.parent / "data" / "reajustes-rgps.json"
TABELA_TETO = PASTA.parent / "data" / "teto-rgps.json"
# Desde 2004 o reajuste é na data do reajuste do salário mínimo (Lei 8.213, art. 41, redação da Lei 10.699/2003; art.
# 41-A, caput); antes, data e fator não capturados.
INICIO_REGIME_REAJUSTE = dt.date(2004, 1, 1)
# W3-reajustes r2 (decisão 1): a tabela de reajustes é a fonte única de QUANDO o benefício acima do mínimo é reajustado.
# Data em que só o mínimo ou o teto mudam, num ano que tem linha de reajuste, não pede fator: a renda se mantém e só o
# piso passa ao mínimo novo (Lei 8.213, art. 41-A e art. 33). Ano sem linha e as datas abaixo continuam abrindo a conta.
LACUNAS_REAJUSTE = {
    dt.date(2006, 8, 1): "Portaria MPS 342/2006, art. 1º, e MP 316/2006, art. 4º: 5,01% sobre a renda de março/2006, em "
                         "substituição aos 5,00% de 01/04/2006 — não é fator sobre a renda vigente (lacuna declarada em "
                         "scripts/data/reajustes-rgps.json)",
}


def so_piso_e_teto(d, datas_reajuste):
    """True se em d só mudam o mínimo ou o teto: d não tem linha de reajuste, não é lacuna declarada e o ano de d tem
    a sua linha de reajuste (o reajuste anual do ano está capturado em outra data)."""
    return d not in LACUNAS_REAJUSTE and d not in datas_reajuste and any(x.year == d.year for x in datas_reajuste)

# Contrato da entrada (context/calculo-valor-causa.md, seção 6). A skill declara o mesmo
# conjunto no bloco ```campos```; tests/test_contrato_flags.py compara os dois.
CAMPOS = {
    "data_ajuizamento": {"tipo": "data", "obrigatorio": "sim", "valores": "data da distribuição"},
    "valor_da_causa_informado": {
        "tipo": "decimal", "obrigatorio": "nao",
        "valores": "total já formado; dispensa os campos de RMI (só alçada e renúncia)"},
    "rmi_pretendida": {"tipo": "decimal", "obrigatorio": "sim, salvo com valor_da_causa_informado",
                       "valores": "-"},
    "dib": {"tipo": "data", "obrigatorio": "sim, salvo com valor_da_causa_informado",
            "valores": "DIB pretendida (ou a DER)"},
    "natureza": {"tipo": "enum", "obrigatorio": "sim, salvo com valor_da_causa_informado",
                 "valores": "previdenciaria|assistencial"},
    "abono": {"tipo": "bool", "obrigatorio": "sim, salvo com valor_da_causa_informado",
              "valores": "false obrigatório quando natureza = assistencial"},
    "incluir_abono_nas_vincendas": {"tipo": "bool", "obrigatorio": "nao",
                                    "valores": "padrão true (M6); ignorado quando abono = false"},
    "corrigir_vencidas": {"tipo": "bool", "obrigatorio": "nao",
                          "valores": "padrão false; true chama o motor de atualização"},
    "renunciar_excedente": {"tipo": "bool", "obrigatorio": "nao", "valores": "padrão false"},
    "salario_minimo": {"tipo": "decimal", "obrigatorio": "nao",
                       "valores": "ausente = tabela pela data do ajuizamento"},
    "datas_vencimento": {"tipo": "objeto", "obrigatorio": "nao",
                         "valores": "{\"AAAA-MM\": \"AAAA-MM-DD\"}: vencimento individual devido da competência "
                                    "(data em que deveria ter sido paga, Lei 8.213, art. 103, parágrafo único; CPC, "
                                    "art. 292, §1º), não a do pagamento realizado; fecha a competência cuja janela do "
                                    "art. 41-A (art. 41, §4º, até a competência 02/2004) cruza o ajuizamento; data fora da "
                                    "janela legal (antes da MP 404/2007, sempre no mês seguinte) ou em dia sem "
                                    "expediente bancário = exit 2; data antecipada em competência de 2007 (MP 404 sem "
                                    "data capturada) = exit 3"},
    # QA final r5 A01: regime prescricional do caso (Lei 8.213, art. 103, parágrafo único; CPC, art. 292, §§1º a 3º)
    "prescricao": {"tipo": "enum", "obrigatorio": "nao",
                   "valores": "regular|nao_corre|interrompida"},
    "marco_prescricional": {"tipo": "data", "obrigatorio": "sim quando prescricao = interrompida",
                            "valores": "data em que a prescrição deixou de correr (ato interruptivo ou suspensivo "
                                       "informado pelo advogado); o corte quinquenal conta 5 anos para trás dela"},
    # QA final r7 C1: incorporação ao reajuste da diferença entre a média e o teto (Portaria do reajuste, art. 6º)
    "media_acima_do_teto": {"tipo": "bool",
                            "obrigatorio": "condicional: dib no período de incorporação do teto de um reajuste da conta",
                            "valores": "true/false: a média dos salários de contribuição superou o teto da DIB; true "
                                       "abre a evolução da renda (exit 3)"},
}
NATUREZAS = ("previdenciaria", "assistencial")
REGIMES_PRESCRICAO = ("regular", "nao_corre", "interrompida")
CAMPOS_RMI = ("rmi_pretendida", "dib", "natureza", "abono")

ALCADA_SM = Decimal(60)
DOZE = Decimal(12)
ZERO = Decimal(0)
DATA_MIN, DATA_MAX = dt.date(1900, 1, 1), dt.date(2100, 12, 31)
LIMITE_MAGNITUDE = Decimal("1e15")

FONTE = {
    "vencidas_vincendas": "CPC, art. 292, §§1º e 2º (context/lei/cpc-excertos-prev.md); Lei 10.259/2001, "
                          "art. 3º, §2º (context/lei/lei-10259-2001-jef.md)",
    "vencimento_devido": "Lei 8.213/1991, art. 103, parágrafo único (context/lei/lei-8213-1991.md): prestação "
                         "vencida é a que deveria ter sido paga; CPC, art. 292, §1º (context/lei/cpc-excertos-prev.md)",
    "vencimento": "Lei 8.213/1991, art. 41-A, §§2º e 3º, redação da Lei 11.665/2008 "
                  "(context/lei/lei-8213-1991.md): janela de pagamento distribuída entre os beneficiários — acima "
                  "de um salário mínimo, do 1º ao 5º dia útil do mês seguinte ao da competência; até um salário "
                  "mínimo, do 5º dia útil que antecede o fim do mês da competência ao 5º dia útil do mês seguinte",
    "vencimento_historico": "Lei 8.213/1991, art. 41, §4º, redação original (\"até o 10º (décimo) dia útil do mês "
                            "seguinte\") e da Lei 8.444/1992 (\"do primeiro ao décimo dia útil do mês seguinte\"), e "
                            "redação da Lei 10.699/2003 (\"A partir de abril de 2004 ... do primeiro ao quinto dia útil\"), "
                            "e art. 41-A, §2º, redação da Lei 11.430/2006 (\"do 1o (primeiro) ao 5o (quinto) dia útil do mês "
                            "seguinte\"): pagamento sempre no mês seguinte até a antecipação do §3º pela MP 404, \"de "
                            "2007\"; redações históricas riscadas em context/lei/lei-8213-1991.md, lidas só para o "
                            "período delas",
    "bpc_minimo": "Lei 8.742/1993, art. 20, caput (context/lei/lei-8742-1993-loas.md): um salário mínimo mensal; CPC, "
                  "art. 292, §§1º e 2º (context/lei/cpc-excertos-prev.md): vencidas pelo valor de cada competência e "
                  "prestação anual vincenda pelo valor na propositura",
    "abono": "Lei 8.213/1991, art. 40 (context/lei/lei-8213-1991.md): abono anual, 1/12 por mês",
    "abono_calendario": "Decreto 3.048/1999, art. 120, §1º (context/lei/decreto-3048-1999.md) e IN PRES/INSS "
                        "128/2022, art. 619, §§1º, 2º e 6º (context/lei/in-128-2022-inss.md): regra geral desde "
                        "2021, 1ª parcela (até 50%) paga com a competência de agosto e 2ª com a de novembro; fração "
                        "de 15 dias conta como mês. Calendário por ato do ano: 2021, Decreto 10.695/2021, art. 1º "
                        "(context/lei/decreto-10695-2021-abono.md), maio e junho; 2022, Decreto 10.999/2022, art. 1º "
                        "(context/lei/decreto-10999-2022-abono.md), abril e maio; 2023, Decreto 11.517/2023, art. 1º "
                        "(context/lei/decreto-11517-2023-abono.md), maio e junho; 2024, Decreto 11.947/2024, art. 1º "
                        "(context/lei/decreto-11947-2024-abono.md), abril e maio; 2025, Decreto 12.425/2025, art. 1º "
                        "(context/lei/decreto-12425-2025-abono.md), abril e maio; 2026, Decreto 12.884/2026, art. 1º "
                        "(context/lei/decreto-12884-2026-abono.md), abril e maio; demais anos, ato próprio não "
                        "capturado (Lei 8.213/1991, art. 40, notas \"Vide\", context/lei/lei-8213-1991.md)",
    "bpc_sem_abono": "Lei 8.742/1993, art. 20 (context/lei/lei-8742-1993-loas.md); o art. 40 da Lei "
                     "8.213/1991 não abrange o BPC",
    "abono_excluido_na_entrada": "abono=false informado: parâmetro da entrada, sem fonte normativa que o exclua; "
                                 "a incidência do abono no benefício previdenciário segue a espécie, pela Lei "
                                 "8.213/1991, art. 40 (context/lei/lei-8213-1991.md); CPC, art. 292 "
                                 "(context/lei/cpc-excertos-prev.md)",
    "alcada": "Lei 10.259/2001, art. 3º, caput (context/lei/lei-10259-2001-jef.md): 60 salários mínimos",
    "congelamento": "CPC, art. 43 (context/lei/cpc-excertos-prev.md): competência fixada na distribuição",
    "renuncia": "STJ Tema 1.030 (context/lei/temas-sumulas-prev.md): renúncia expressa, inclusive das "
                "vincendas",
    "correcao": "Manual de Cálculos da Justiça Federal, ed. jul./2026, itens 4.3.1.1 (Nota 2: termo "
                "inicial = mês de competência) e 4.3.2; 4.2.1.1 no assistencial "
                "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "sem_juros": "Manual de Cálculos da Justiça Federal, ed. jul./2026, item 4.3.2: juros desde a citação "
                 "(context/lei/manual-cjf-2026-calculos-prev.md)",
    "jef_sem_prazo_diferenciado": "Lei 10.259/2001, art. 9º (context/lei/lei-10259-2001-jef.md)",
    "prescricao": "Lei 8.213/1991, art. 103, parágrafo único (context/lei/lei-8213-1991.md): prescreve em cinco "
                  "anos, a contar da data em que deveriam ter sido pagas, a ação para haver prestações vencidas, salvo "
                  "o direito dos menores, incapazes e ausentes; CPC, art. 292, §§1º a 3º "
                  "(context/lei/cpc-excertos-prev.md): o valor da causa corresponde ao conteúdo patrimonial em discussão",
    "reajuste": "Lei 8.213/1991, art. 41-A, caput (context/lei/lei-8213-1991.md): reajuste anual da renda na data do "
                "reajuste do salário mínimo, pro rata no primeiro pela DIB; Portarias Interministeriais MPS/MF 6/2025 "
                "e 13/2026, art. 1º, §1º, art. 6º e Anexo I (context/lei/portaria-interministerial-mps-mf-6-2025.md, "
                "context/lei/portaria-interministerial-mps-mf-13-2026.md); piso de um salário mínimo (CF, art. 201, "
                "§2º) e teto vigentes na competência; CPC, art. 292, §§1º e 2º (context/lei/cpc-excertos-prev.md): "
                "vencidas pela renda de cada competência, vincendas pela renda da propositura",
    "prazo_em_anos": "Código Civil, art. 132, caput e §§1º e 3º (context/lei/cc-excertos-prev.md): prazo em anos "
                     "expira no dia de igual número do de início, ou no imediato; vencimento em feriado prorroga até o "
                     "dia útil seguinte",
}
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


def _bool(campo, valor):
    if not isinstance(valor, bool):
        raise EntradaInvalida(f"{campo}: esperado true ou false")
    return valor


def _comp(campo, valor):
    if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}", valor) or not 1 <= int(valor[5:]) <= 12:
        raise EntradaInvalida(f"{campo}: competência inválida (use AAAA-MM)")
    return int(valor[:4]), int(valor[5:])


def _datas_vencimento(bruto, dib, ajuizamento):
    """{competência: vencimento individual devido}, só para competências da DIB ao mês do ajuizamento."""
    if bruto is None:
        return {}
    if not isinstance(bruto, dict):
        raise EntradaInvalida("datas_vencimento: esperado objeto {\"AAAA-MM\": \"AAAA-MM-DD\"}")
    out = {}
    for k, v in bruto.items():
        c = _comp(f"datas_vencimento[{k!r}]", k)
        if not (dib.year, dib.month) <= c <= (ajuizamento.year, ajuizamento.month):
            raise EntradaInvalida(f"datas_vencimento: competência {k} fora do período da DIB ao ajuizamento")
        d = _data(f"datas_vencimento[{k}]", v)
        if d < dt.date(c[0], c[1], 1):
            raise EntradaInvalida(f"datas_vencimento: {k} vence em {v}, antes do próprio mês da competência")
        out[c] = d
    return out


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
    extras = sorted(k for k in bruto if k not in CAMPOS and not k.startswith("_"))
    if extras:
        raise EntradaInvalida(f"campos desconhecidos: {', '.join(extras)}")
    if bruto.get("data_ajuizamento") is None:
        raise EntradaInvalida("campo obrigatório ausente ou nulo: data_ajuizamento")
    e = {"data_ajuizamento": _data("data_ajuizamento", bruto["data_ajuizamento"])}
    if bruto.get("valor_da_causa_informado") is not None:
        presentes = [c for c in CAMPOS_RMI + ("incluir_abono_nas_vincendas", "corrigir_vencidas", "datas_vencimento",
                                              "prescricao", "marco_prescricional", "media_acima_do_teto")
                     if bruto.get(c) is not None]
        if presentes:
            raise EntradaInvalida("valor_da_causa_informado dispensa os campos de RMI; informe um ou outro "
                                  f"(veio também: {', '.join(presentes)})")
        e["valor_da_causa_informado"] = _dec("valor_da_causa_informado", bruto["valor_da_causa_informado"])
    else:
        for c in CAMPOS_RMI:
            if bruto.get(c) is None:
                raise EntradaInvalida(f"campo obrigatório ausente ou nulo: {c} (ou informe "
                                      "valor_da_causa_informado)")
        e["rmi_pretendida"] = _dec("rmi_pretendida", bruto["rmi_pretendida"])
        if e["rmi_pretendida"] == 0:
            raise EntradaInvalida("rmi_pretendida: zero")
        e["dib"] = _data("dib", bruto["dib"])
        if bruto["natureza"] not in NATUREZAS:
            raise EntradaInvalida(f"natureza: use um de {', '.join(NATUREZAS)}")
        e["natureza"] = bruto["natureza"]
        e["abono"] = _bool("abono", bruto["abono"])
        if e["natureza"] == "assistencial" and e["abono"]:
            raise EntradaInvalida("abono = true com natureza assistencial: o BPC não tem abono anual "
                                  "(LOAS, art. 20; Lei 8.213, art. 40)")
        if e["dib"] > e["data_ajuizamento"]:
            raise EntradaInvalida("dib posterior a data_ajuizamento")
        e["incluir_abono_nas_vincendas"] = _bool(
            "incluir_abono_nas_vincendas", bruto.get("incluir_abono_nas_vincendas", True))
        e["corrigir_vencidas"] = _bool("corrigir_vencidas", bruto.get("corrigir_vencidas", False))
        e["datas_vencimento"] = _datas_vencimento(bruto.get("datas_vencimento"), e["dib"], e["data_ajuizamento"])
        if bruto.get("media_acima_do_teto") is not None:
            e["media_acima_do_teto"] = _bool("media_acima_do_teto", bruto["media_acima_do_teto"])
        if bruto.get("prescricao") is not None:
            if bruto["prescricao"] not in REGIMES_PRESCRICAO:
                raise EntradaInvalida(f"prescricao: use um de {', '.join(REGIMES_PRESCRICAO)}")
            e["prescricao"] = bruto["prescricao"]
        if bruto.get("marco_prescricional") is not None:
            if e.get("prescricao") != "interrompida":
                raise EntradaInvalida("marco_prescricional só com prescricao = interrompida")
            e["marco_prescricional"] = _data("marco_prescricional", bruto["marco_prescricional"])
            if e["marco_prescricional"] > e["data_ajuizamento"]:
                raise EntradaInvalida("marco_prescricional posterior a data_ajuizamento")
        elif e.get("prescricao") == "interrompida":
            raise EntradaInvalida("campo obrigatório ausente ou nulo: marco_prescricional (prescricao = interrompida)")
    e["renunciar_excedente"] = _bool("renunciar_excedente", bruto.get("renunciar_excedente", False))
    if bruto.get("salario_minimo") is not None:
        e["salario_minimo"] = _dec("salario_minimo", bruto["salario_minimo"])
        if e["salario_minimo"] == 0:
            raise EntradaInvalida("salario_minimo: zero")
    return e


def eco(e):
    out = {}
    for k, v in e.items():
        if k == "datas_vencimento":
            out[k] = {comp_txt(c): d.isoformat() for c, d in sorted(v.items())}
        else:
            out[k] = v.isoformat() if isinstance(v, dt.date) else (str(v) if isinstance(v, Decimal) else v)
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


def carregar_motor(caminho, nome):
    """Importa um motor vendorizado pelo caminho; None se o arquivo não existe."""
    caminho = Path(caminho)
    if not caminho.is_file():
        return None
    spec = importlib.util.spec_from_file_location(f"_prev_{nome}_{abs(hash(str(caminho)))}", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ler_tabela_sm(tabela):
    """Conteúdo de scripts/data/salario-minimo.json, ou o erro de leitura."""
    try:
        return json.loads(Path(tabela).read_text(encoding="utf-8")), None
    except (OSError, ValueError) as err:
        return None, err


def sm_na_data(dados, d):
    """(valor, fonte) do salário mínimo vigente em d pela tabela; None fora dela."""
    for ln in (dados or {}).get("linhas", []):
        ini = dt.date.fromisoformat(ln["vigencia_inicio"])
        fim = dt.date.fromisoformat(ln["vigencia_fim"]) if ln.get("vigencia_fim") else None
        if ini <= d and (fim is None or d <= fim) and ln.get("valor") is not None:
            if fim is None and d.year > ini.year:
                return None   # vigência aberta: só vale no ano do decreto capturado
            return Decimal(ln["valor"]), f"{ln['norma']} ({ln['arquivo']}); tabela capturada em " \
                                          f"{dados.get('data_captura')}"
    return None


def salario_minimo(e, tabela, faltas):
    """(valor, fonte) do salário mínimo da distribuição; (None, ...) com falta registrada."""
    if "salario_minimo" in e:
        return e["salario_minimo"], "informado na entrada (salario_minimo)"
    d = e["data_ajuizamento"]
    dados, err = ler_tabela_sm(tabela)
    if dados is None:
        faltas.append({"item": "tabela do salário mínimo", "motivo": f"scripts/data/salario-minimo.json "
                       f"ilegível ou ausente ({err})", "fonte": FONTE["alcada"]})
        return None, None
    achado = sm_na_data(dados, d)
    if achado:
        return achado
    faltas.append({"item": "salário mínimo da data da distribuição",
                   "motivo": f"{d.isoformat()} fora da tabela scripts/data/salario-minimo.json "
                             f"(intervalo {dados.get('intervalo')}); informe salario_minimo pelo decreto "
                             "vigente na distribuição",
                   "fonte": FONTE["alcada"]})
    return None, None


# ---------------------------------------------------------------- janela de pagamento (art. 41-A)

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


def pago_antes(ini, fim, marco):
    """True se a janela inteira acaba antes do marco; False se começa no marco ou depois; None no meio."""
    if fim < marco:
        return True
    if ini >= marco:
        return False
    return None


# ---------------------------------------------------------------- prescrição quinquenal (QA final r5 A01)

def menos_cinco_anos(d):
    """Dia de igual número cinco anos antes; sem correspondência (29/02), o imediato, 01/03 (CC, art. 132, §3º): a
    prestação vencida em 28/02 expira em 28/02 e já prescreveu numa ação de 29/02; a vencida em 01/03, não."""
    try:
        return d.replace(year=d.year - 5)
    except ValueError:
        return dt.date(d.year - 5, 3, 1)


def cortes_prescricionais(marco, janelas):
    """(corte, corte_cedo) do marco (ajuizamento, ou marco_prescricional na interrupção).

    Prescreve a competência cujo vencimento devido V, mais cinco anos, cai antes do marco: V < corte (Lei 8.213, art.
    103, parágrafo único; CC, art. 132, caput e §3º). Com a prorrogação do §1º, o prazo que expira nos dias não úteis
    imediatamente anteriores ao marco só termina no marco, e essas prestações não prescrevem: a prescrição só é certa
    para V < corte_cedo. Entre os dois, a competência fica em aberto (exit 3), como a janela que cruza o ajuizamento.
    Dia não útil na leitura mais larga (feriados nacionais e pontos facultativos do motor de prazos); sem o motor, só
    sábado e domingo, com a faixa alargada em MARGEM_SEM_MOTOR."""
    corte = menos_cinco_anos(marco)
    d = marco - dt.timedelta(days=1)
    while not janelas._util(d, True):
        d -= dt.timedelta(days=1)
    cedo = menos_cinco_anos(d + dt.timedelta(days=1))
    if janelas.motor is None:
        cedo -= JanelaPagamento.MARGEM_SEM_MOTOR
    return corte, cedo


def situacao_prescricao(ln, corte, cedo):
    """True = prescrita; False = não prescrita; None = em aberto (janela ou dia que cruza o corte, ou sem janela)."""
    if ln.get("vencimento_informado") and ln.get("vencimento") is not None:
        v = dt.date.fromisoformat(ln["vencimento"])
        return True if v < cedo else (False if v >= corte else None)
    if ln.get("janela"):
        ini, fim = dt.date.fromisoformat(ln["janela"]["inicio"]), dt.date.fromisoformat(ln["janela"]["fim"])
        return True if fim < cedo else (False if ini >= corte else None)
    return None


def aplica_prescricao(linhas, corte, cedo):
    """(linhas da conta, prescritas, em aberto, situação por competência). A competência prescrita sai da conta; a
    vencida cujo vencimento cruza o corte fica em aberto (vencida = None), com as leituras com e sem ela."""
    conta, prescritas, aberto, situacao = [], [], [], {}
    for ln in linhas:
        c = (int(ln["competencia"][:4]), int(ln["competencia"][5:]))
        if ln["vencida"] is False:
            situacao[c] = False
            conta.append(ln)
            continue
        s = situacao_prescricao(ln, corte, cedo)
        situacao[c] = s
        ln = dict(ln, prescrita=s)
        if s is True:
            prescritas.append(ln)
            continue
        if s is None and ln["vencida"] is True:
            ln.update(vencida=None, prescricao_incerta=True)
            aberto.append(ln)
        conta.append(ln)
    return conta, prescritas, aberto, situacao


def prescreve_abonos(abonos, situacao, corte):
    """(mantidos, prescritos, em aberto [(ano, motivo)]). Cada parcela do abono prescreve com a competência que a
    carrega; sem o calendário do ano, só prescreve o abono cujas competências possíveis de pagamento prescreveram."""
    def st(c):
        return situacao.get(c, False)

    mantidos, prescritos, abertos = [], [], []
    for a in abonos:
        if a["parcelas"] is not None:
            sts = [st(c) for c, _ in a["parcelas"]]
            if None in sts:
                abertos.append((a["ano"], f"parcela paga com competência cujo vencimento cruza o corte quinquenal "
                                          f"({corte.isoformat()}): {a['calendario']}; informe datas_vencimento"))
                continue
            cortadas = [(c, v) for c, v in a["parcelas"] if st(c) is True]
            resto = [(c, v) for c, v in a["parcelas"] if st(c) is False]
            if not cortadas:
                mantidos.append(a)
                continue
            prescritos.append({"ano": a["ano"], "parcelas": [comp_txt(c) for c, _ in cortadas],
                               "valor": s2(sum((v for _, v in cortadas), ZERO))})
            if resto:
                mantidos.append(dict(a, valor=sum((v for _, v in resto), ZERO), parcelas=resto,
                                     candidatas=[c for c, _ in resto],
                                     calendario=f"{a['calendario']}; prescrita a parcela de "
                                                f"{', '.join(comp_txt(c) for c, _ in cortadas)}"))
            continue
        sts = {st(c) for c in a["candidatas"]}
        if sts == {False}:
            mantidos.append(a)
        elif sts == {True}:
            prescritos.append({"ano": a["ano"], "parcelas": None, "valor": s2(a["valor"])})
        else:
            abertos.append((a["ano"], f"o abono de {a['ano']} ({a['valor']}) pode ter sido pago com competência "
                                      f"anterior ou posterior ao corte quinquenal ({corte.isoformat()}): "
                                      f"{a['calendario']}; informe o ato do ano ou confira o extrato do INSS"))
    return mantidos, prescritos, abertos


def classifica_vencidas(e, janelas, dados_sm, renda_c=None):
    """Competências da DIB ao mês do ajuizamento: janela de pagamento e se venceram (eram devidas) antes do
    ajuizamento."""
    aj, rmi = e["data_ajuizamento"], e["rmi_pretendida"]
    c, fim = (e["dib"].year, e["dib"].month), (aj.year, aj.month)
    linhas = []
    while c <= fim:
        # parágrafo pelo valor da própria competência (art. 41-A, §§2º e 3º): no BPC, o mínimo do mês (LOAS, art. 20),
        # que nunca está acima de um mínimo, ainda que a rmi_pretendida seja o mínimo de outra competência
        if e["natureza"] == "assistencial":
            ate_um = True
        else:
            sm = sm_na_data(dados_sm, dt.date(c[0], c[1], 1))
            # QA final r7 C1: renda da própria competência (reajustada); sem ela, a rmi_pretendida
            renda = renda_c(c) if renda_c else None
            ate_um = None if sm is None else (rmi if renda is None else renda) <= sm[0]
        jan = janelas.janela(c, ate_um)
        janela = None if jan is None else {"inicio": jan[0].isoformat(), "fim": jan[1].isoformat(), "paragrafo": jan[2]}
        if c in e["datas_vencimento"]:
            vc = e["datas_vencimento"][c]
            # QA final A01: o vencimento individual devido cai dentro da janela legal (art. 41-A, §§2º a 4º, ou art. 41,
            # §4º, histórico); data fora dela não é vencimento devido e não substitui a classificação. QA final r2
            # A-01: antes da MP 404/2007 a janela começa no mês seguinte, e data no próprio mês da competência é exit 2
            if jan is not None and not jan[0] <= vc <= jan[1]:
                raise EntradaInvalida(
                    f"datas_vencimento: {comp_txt(c)} vence em {vc.isoformat()}, fora da janela de pagamento "
                    f"({jan[0].isoformat()} a {jan[1].isoformat()}, {jan[2]}); o campo é o vencimento individual "
                    "devido, não a data do pagamento realizado")
            expediente, motivo_exp = (True, None) if jan is None else janelas.expediente_bancario(vc)
            if expediente is False:
                # art. 41-A, §4º: dia útil da janela é o de expediente bancário normal (QA final r4 A01: inclusive as
                # datas móveis — Carnaval, Paixão, Corpus Christi —, que o calendário forense só trata como ponto)
                raise EntradaInvalida(
                    f"datas_vencimento: {comp_txt(c)} vence em {vc.isoformat()} ({vc.strftime('%d/%m/%Y')}), dia sem "
                    f"expediente bancário normal ({motivo_exp}; art. 41-A, §4º)")
            linha = {"competencia": comp_txt(c), "janela": janela, "vencimento_informado": vc.isoformat(),
                     "vencimento": vc.isoformat(), "vencida": vc < aj}
            if expediente is None:
                # QA final r4 A01: o calendário não decide o dia (fonte insuficiente): nem vale nem é recusado
                linha.update(vencimento=None, vencida=None, expediente_incerto=motivo_exp)
            if jan is not None and jan[3] is not None and vc < jan[3]:
                # QA final r2 A-01: data só possível com a antecipação do §3º, cuja vigência (MP 404/2007) não tem dia
                # capturado: nem vale como vencimento devido nem é recusada; a competência fica em aberto
                linha.update(vencimento=None, vencida=None, antecipacao_incerta=True)
        elif jan is None:
            linha = {"competencia": comp_txt(c), "janela": None, "vencimento": None, "vencida": None,
                     "fora_dos_regimes": True}
        else:
            linha = {"competencia": comp_txt(c), "janela": janela,
                     "vencimento": janela["fim"], "vencida": pago_antes(jan[0], jan[1], aj)}
        if c < fim or linha["vencida"] is not False:     # a do mês do ajuizamento só aparece se pode ter vencido
            linhas.append(linha)
        c = comp_seguinte(c)
    return linhas


# ---------------------------------------------------------------- abono anual vencido

# Calendário do abono por ato do ano, capturado em context/lei/: (competência da 1ª parcela, da 2ª, ato). A 1ª parcela
# é 50% do benefício devido na competência dela; a 2ª, a diferença até o abono anual. Ano fora desta tabela não tem
# calendário capturado e não se presume (a regra geral de agosto e novembro dá a 1ª parcela como "até" 50%, e as notas
# "Vide" do art. 40 da Lei 8.213 não esgotam os atos: não citam os Decretos 12.425/2025 nem 12.884/2026).
CALENDARIO_ABONO = {
    2021: ((2021, 5), (2021, 6), "Decreto 10.695/2021, art. 1º"),
    2022: ((2022, 4), (2022, 5), "Decreto 10.999/2022, art. 1º"),
    2023: ((2023, 5), (2023, 6), "Decreto 11.517/2023, art. 1º"),
    2024: ((2024, 4), (2024, 5), "Decreto 11.947/2024, art. 1º"),
    2025: ((2025, 4), (2025, 5), "Decreto 12.425/2025, art. 1º"),
    2026: ((2026, 4), (2026, 5), "Decreto 12.884/2026, art. 1º"),
}
# Atos de antecipação citados nas notas "Vide" do art. 40 da Lei 8.213 (captura de 2026-10-14), não capturados.
ATO_ABONO_NAO_CAPTURADO = {2008: "Decreto 6.525/2008", 2009: "Decreto 6.927/2009", 2012: "Decreto 7.782/2012",
                           2013: "Decreto 8.064/2013", 2018: "Decreto 9.447/2018"}
# Regra geral em duas parcelas, a 2ª com a competência de novembro, desde 2021 (IN 128, art. 619, §6º; Decreto 3.048,
# art. 120, §1º, II). Antes, só a competência de dezembro (base do abono, art. 120, §1º) fecha o ano.
ANO_SEGUNDA_PARCELA_NOVEMBRO = 2021


def ato_que_falta(ano):
    if ano in ATO_ABONO_NAO_CAPTURADO:
        return f"{ATO_ABONO_NAO_CAPTURADO[ano]}, citado nas notas \"Vide\" do art. 40 da Lei 8.213 e não capturado"
    return (f"ato de antecipação do abono de {ano}, se houver, não capturado em context/lei/ (as notas \"Vide\" do "
            "art. 40 da Lei 8.213 não esgotam os atos)")


def abonos_vencidos(e, linhas, comps_vencidas, renda_c=None):
    """([{ano, meses, valor, parcelas, calendario}], [(ano, motivo)]): abono anual vencido de cada ano com vencidas.

    parcelas: [(competência, valor)] de cada parcela vencida, ou None quando o calendário do ano não está capturado
    (o valor nominal fecha, a competência de cada parcela não). O abono vence com as competências que carregam as
    parcelas; sem calendário do ano, só fecha quando a última competência possível de pagamento venceu.
    """
    dib = e["dib"]
    dib_c = (dib.year, dib.month)
    aj_c = (e["data_ajuizamento"].year, e["data_ajuizamento"].month)
    status = {(int(ln["competencia"][:4]), int(ln["competencia"][5:])): ln["vencida"] for ln in linhas}

    def st(c):
        """True/False/None da competência; fora do período da DIB ao ajuizamento, não recebida ou não vencida."""
        return status.get(c, False) if c >= dib_c else False

    abonos, abertos = [], []
    for ano in sorted({c[0] for c in comps_vencidas}):
        ini = max(dib_c, (ano, 1))
        meses = 12 - ini[1] + 1
        if ini == dib_c and dib.day != 1:
            dias = calendar.monthrange(dib.year, dib.month)[1] - dib.day + 1
            if dias < 15:                                 # IN 128, art. 619, §1º: 15 dias ou mais contam como mês
                meses -= 1
        # QA final r7 C1: base = renda do ano (a de dezembro, Lei 8.213, art. 40, parágrafo único), reajustada; o
        # reajuste é em janeiro, e renda que muda dentro do ano ou que não se conhece deixa o abono do ano em aberto
        ate = min((ano, 12), aj_c)
        rendas = {renda_c(c) if renda_c else e["rmi_pretendida"]
                  for c in ((ano, m) for m in range(ini[1], ate[1] + 1))} if ini <= ate else {None}
        if None in rendas or len(rendas) != 1:
            abertos.append((ano, f"renda de {ano} (base do abono, Lei 8.213, art. 40, parágrafo único) não fechada "
                                 "pela evolução da renda (reajuste anual)"))
            continue
        rmi = rendas.pop()
        valor = q2(rmi * meses / DOZE)
        faixa = f"abono vencido entre 0,00 e {valor} ({meses}/12 × {q2(rmi)})"
        cal = CALENDARIO_ABONO.get(ano)
        if cal and dib_c <= cal[0]:
            p1, p2, ato = cal
            v1 = q2(rmi / 2)
            # DIB no meio do mês da 1ª parcela: 50% do benefício integral ou do proporcional (valor da competência da
            # DIB em aberto); o total do ano não muda, a divisão entre as parcelas sim.
            divide = not (dib_c == p1 and dib.day != 1)
            s1, s2_ = st(p1), st(p2)
            if s2_ is True:
                abonos.append({"ano": ano, "meses": meses, "base": rmi, "valor": valor, "calendario": ato,
                               "parcelas": [(p1, v1), (p2, valor - v1)] if divide else None, "candidatas": [p1, p2]})
            elif s1 is False:
                continue                                  # nenhuma parcela venceu antes do ajuizamento
            elif s1 is True and s2_ is False and divide:
                abonos.append({"ano": ano, "meses": meses, "base": rmi, "valor": v1, "parcelas": [(p1, v1)], "candidatas": [p1],
                               "calendario": f"{ato} (só a 1ª parcela, 50% de {q2(rmi)})"})
            else:
                abertos.append((ano, f"{ato}: 1ª parcela (50% do benefício de {comp_txt(p1)}) paga com essa competência "
                                     f"e a 2ª com a {comp_txt(p2)}; "
                                + ("a 1ª venceu antes do ajuizamento, mas a DIB no meio do mês não fixa o valor dela"
                                   if s1 is True and s2_ is False else
                                   "a janela de pagamento cruza o ajuizamento")
                                + f", e o {faixa}; informe datas_vencimento de {comp_txt(p1)} e {comp_txt(p2)}"))
            continue
        motivo_cal = (ato_que_falta(ano) if not cal else
                      f"DIB depois de {comp_txt(cal[0])}: fora da antecipação do {cal[2]}, e o pagamento de quem "
                      "começou a receber depois não está nele")
        ultima = (ano, 11) if ano >= ANO_SEGUNDA_PARCELA_NOVEMBRO else (ano, 12)
        if st(ultima) is True or st((ano, 12)) is True:
            # sem calendário, a parcela pode ter sido paga com qualquer competência do ano (QA final r5 A01: a
            # prescrição só corta o abono do ano quando todas elas prescreveram)
            candidatas = [c for c in ((ano, m) for m in range(1, 13)) if c >= dib_c]
            abonos.append({"ano": ano, "meses": meses, "base": rmi, "valor": valor, "parcelas": None, "candidatas": candidatas,
                           "calendario": f"sem calendário capturado ({motivo_cal}); a competência {comp_txt(ultima)} "
                                         "venceu antes do ajuizamento, e o abono já foi pago inteiro"})
            continue
        abertos.append((ano, f"[VERIFICAR] calendário de pagamento do abono de {ano} não capturado ({motivo_cal}); "
                             f"a competência {comp_txt(ultima)} não venceu antes do ajuizamento, e o {faixa}; informe o "
                             "ato do ano ou confira o extrato do INSS"))
    return abonos, abertos


# ---------------------------------------------------------------- evolução da renda (QA final r7 C1)

def _vigente(dados, d, chave):
    """Valor da linha da tabela (salário mínimo, teto) vigente em d; None fora dela."""
    for ln in (dados or {}).get("linhas", []):
        ini = dt.date.fromisoformat(ln["vigencia_inicio"])
        fim = dt.date.fromisoformat(ln["vigencia_fim"]) if ln.get("vigencia_fim") else None
        if ini <= d and (fim is None or d <= fim) and ln.get(chave) is not None:
            return Decimal(ln[chave])
    return None


def evolucao_renda(e, fim, dados_sm, pasta_dados=None):
    """Renda do benefício previdenciário da DIB a 'fim' (último dia do mês do ajuizamento), reajustada em cada data de
    reajuste (Lei 8.213, art. 41-A, caput: a do salário mínimo desde 2004), pelo fator integral ou, no primeiro
    reajuste, pelo pro rata da DIB (Portaria do ano, art. 1º, §1º, e Anexo I), com o piso de um salário mínimo (CF,
    art. 201, §2º) e o teto vigentes na data. {segmentos: [(desde, renda)], limite, motivo, passos, normas, sem_piso}:
    da data 'limite' em diante a renda não se conhece (ano sem fator, pro rata ausente, tabela que acaba, incorporação
    do teto sem a média) e 'motivo' diz o que falta. Nunca estima: renda congelada não fecha conta."""
    dib, rmi = e["dib"], e["rmi_pretendida"]
    info = {"segmentos": [(dib, rmi)], "limite": None, "motivo": None, "passos": [], "normas": [], "sem_piso": False}

    def abre(d, motivo):
        info["limite"], info["motivo"] = d, motivo
        return info

    if dib < INICIO_REGIME_REAJUSTE:
        return abre(dib + dt.timedelta(days=1),
                    f"data e fator dos reajustes da renda até 2003 não capturados (Lei 8.213, art. 41, redações "
                    f"anteriores à Lei 10.699/2003, context/lei/lei-8213-1991.md); DIB {dib.isoformat()}")
    try:
        # mesma pasta da tabela do salário mínimo recebida (a de dados do plugin, por padrão)
        arq_r, arq_t = ((TABELA_REAJUSTES, TABELA_TETO) if pasta_dados is None else
                        (Path(pasta_dados) / TABELA_REAJUSTES.name, Path(pasta_dados) / TABELA_TETO.name))
        reaj = json.loads(Path(arq_r).read_text(encoding="utf-8"))
        teto = json.loads(Path(arq_t).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        return abre(dib + dt.timedelta(days=1), f"tabela de reajustes ou de teto ilegível em scripts/data/ ({err})")
    if not dados_sm:
        return abre(dib + dt.timedelta(days=1), "tabela do salário mínimo ilegível: sem o piso, a renda não se confere")
    linhas = {dt.date.fromisoformat(ln["vigencia_inicio"]): ln for ln in reaj["linhas"]}
    datas = set(linhas)
    for t in (dados_sm, teto):
        datas |= {dt.date.fromisoformat(ln["vigencia_inicio"]) for ln in t["linhas"]}
    cobertura = min(dt.date.fromisoformat(t["intervalo"]["fim"]) for t in (reaj, teto, dados_sm))
    sm_dib, teto_dib = _vigente(dados_sm, dib, "valor"), _vigente(teto, dib, "teto")
    if sm_dib is None or teto_dib is None:
        return abre(dib + dt.timedelta(days=1), f"salário mínimo ou teto da DIB ({dib.isoformat()}) fora de scripts/data/")
    piso = rmi >= sm_dib
    info["sem_piso"] = not piso
    renda = rmi
    for d in sorted(x for x in datas if dib < x <= fim):
        if d > cobertura:
            break
        ln = linhas.get(d)
        if ln is None and so_piso_e_teto(d, linhas):
            # só o mínimo ou o teto mudam: renda mantida; o piso sobe ao mínimo novo (o teto nunca baixou)
            sm_d, teto_d = _vigente(dados_sm, d, "valor"), _vigente(teto, d, "teto")
            if sm_d is None or teto_d is None:
                return abre(d, f"salário mínimo ou teto de {d.isoformat()} fora de scripts/data/")
            if piso and renda < sm_d:
                info["passos"].append(f"{d.isoformat()}: só o salário mínimo muda (sem reajuste acima do mínimo); "
                                      f"{q2(renda)} < salário mínimo {sm_d} → {sm_d} (CF, art. 201, §2º)")
                renda = sm_d
                info["segmentos"].append((d, renda))
            continue
        if ln is None:
            motivo = LACUNAS_REAJUSTE.get(d, "sem fator capturado em context/lei/ (scripts/data/reajustes-rgps.json)")
            return abre(d, f"reajuste anual de {d.isoformat()} (Lei 8.213, art. 41-A, caput: na data do reajuste do "
                           f"salário mínimo, que muda nessa data em scripts/data/) {motivo}; sem ele, a renda dali em "
                           "diante não fecha")
        if rmi > teto_dib:
            return abre(d, f"rmi_pretendida {rmi} acima do teto da DIB ({teto_dib}): a renda acima do teto depende da "
                           "espécie (por exemplo, o acréscimo de 25% da Lei 8.213, art. 45, recalculado sobre a "
                           "base reajustada e limitada ao teto), e a entrada não separa base e parcela excedente; "
                           f"o reajuste de {d.isoformat()} não se confere")
        if dib >= dt.date.fromisoformat(ln["pro_rata_desde"]):
            pct = ln["pro_rata"].get(f"{dib.year:04d}-{dib.month:02d}")
            if pct is None:
                return abre(d, f"fator pro rata do reajuste de {d.isoformat()} para DIB em {dib.month:02d}/{dib.year} "
                               f"ausente do Anexo I capturado ({ln['norma']})")
            rotulo = f"pro rata da DIB em {dib.month:02d}/{dib.year}"
        else:
            pct, rotulo = ln["integral"], "integral"
        inc = ln.get("incorporacao_teto")
        if inc and dt.date.fromisoformat(inc["dib_de"]) <= dib <= dt.date.fromisoformat(inc["dib_ate"]):
            media = e.get("media_acima_do_teto")
            if media is None:
                return abre(d, f"media_acima_do_teto: DIB em {dib.isoformat()} → no reajuste de {d.isoformat()} "
                               "incorpora-se à renda a diferença percentual entre a média e o teto, quando positiva "
                               f"({inc['norma']}); informe se a média superou o teto da DIB")
            if media:
                return abre(d, f"incorporação do teto no reajuste de {d.isoformat()} ({inc['norma']}): o percentual é "
                               "a diferença entre a média e o teto da DIB, que o valor da causa não recebe")
        fator = 1 + Decimal(pct) / 100
        nova = q2(renda * fator)
        passo = f"reajuste de {d.isoformat()}: {q2(renda)} × {fator} ({rotulo}; {ln['norma']}) = {nova}"
        sm_d, teto_d = _vigente(dados_sm, d, "valor"), _vigente(teto, d, "teto")
        if sm_d is None or teto_d is None:
            return abre(d, f"salário mínimo ou teto de {d.isoformat()} fora de scripts/data/")
        if piso and nova < sm_d:
            passo += f" < salário mínimo {sm_d} → {sm_d} (CF, art. 201, §2º)"
            nova = sm_d
        if nova > teto_d:
            passo += f" > teto {teto_d} → {teto_d}"
            nova = teto_d
        renda = nova
        info["segmentos"].append((d, renda))
        info["passos"].append(passo)
        if ln["norma"] not in info["normas"]:
            info["normas"].append(ln["norma"])
    if fim > cobertura:
        return abre(cobertura + dt.timedelta(days=1),
                    f"salário mínimo, teto e fator de reajuste depois de {cobertura.isoformat()} fora de scripts/data/ "
                    "(recapturar com a portaria do ano)")
    return info


def renda_na_data(info, d):
    """Renda vigente na data d (a da propositura nas vincendas, sem antecipar o reajuste seguinte); None a partir do
    limite."""
    if info["limite"] is not None and d >= info["limite"]:
        return None
    return [r for desde, r in info["segmentos"] if desde <= d][-1]


def renda_da_competencia(info, e, c):
    """Renda devida na competência c; None se o mês alcança o limite ou um reajuste cai no meio dele (dois valores)."""
    ini = max(dt.date(c[0], c[1], 1), e["dib"])
    fim = dt.date(c[0], c[1], calendar.monthrange(c[0], c[1])[1])
    if info["limite"] is not None and fim >= info["limite"]:
        return None
    if any(ini < desde <= fim for desde, _ in info["segmentos"]):
        return None
    return renda_na_data(info, ini)


def _tupla(txt):
    return int(txt[:4]), int(txt[5:7])


# ---------------------------------------------------------------- correção das vencidas (motor)

def corrigir(motor, valor, comp, e, faltas, alertas_motor):
    """Corrige uma vencida do mês da competência até o ajuizamento, sem juros (citação = ajuizamento)."""
    entrada = {
        "valor": str(valor),
        "data_inicial": f"{comp_txt(comp)}-01",
        "data_final": e["data_ajuizamento"].isoformat(),
        "data_citacao": e["data_ajuizamento"].isoformat(),
        "regime": "fazenda-ec113",
        "natureza": e["natureza"],
    }
    codigo, saida = motor.calcular(entrada)
    if codigo == EXIT_ENTRADA:
        raise EntradaInvalida(f"motor de atualização recusou a competência {comp_txt(comp)}: "
                              f"{saida.get('detalhe')}")
    for a in saida.get("alertas", []):
        if a not in alertas_motor:
            alertas_motor.append(a)
    registro = {"competencia": comp_txt(comp), "valor_nominal": s2(valor), "motor_exit": codigo,
                "valor_corrigido": saida.get("valor_final"), "componentes": saida.get("componentes"),
                "fonte_indice": saida.get("fonte_indice")}
    if codigo != EXIT_OK:
        fa = saida.get("formula_aberta") or {}
        faltas.append({"item": f"correção da competência {comp_txt(comp)}",
                       "motivo": "; ".join(str(x) for x in fa.get("faltando", [])) or "motor sem número",
                       "fonte": FONTE["correcao"]})
        registro["formula_aberta"] = fa
        return None, registro
    return Decimal(saida["valor_final"]), registro


# ---------------------------------------------------------------- BPC: mínimo por competência (QA final B-01)

def conta_bpc_por_competencia(e, linhas, dados_sm, sm_propositura):
    """(valor_comp, conta) do BPC. valor_comp(competência AAAA-MM) devolve o mínimo da competência (None fora da tabela).
    conta = None quando todas as vencidas, as de fronteira e a propositura têm o mínimo igual à rmi_pretendida (a conta
    constante do motor é a da lei); senão, a conta nominal por competência para valor_da_causa_informado."""
    def valor_comp(txt):
        achado = sm_na_data(dados_sm, dt.date(int(txt[:4]), int(txt[5:]), 1))
        return None if achado is None else achado[0]

    rmi = e["rmi_pretendida"]
    consideradas = [ln for ln in linhas if ln["vencida"] is not False]
    valores = {ln["competencia"]: valor_comp(ln["competencia"]) for ln in consideradas}
    if sm_propositura is not None and sm_propositura == rmi and all(v == rmi for v in valores.values()):
        return valor_comp, None
    vencidas = [ln["competencia"] for ln in linhas if ln["vencida"] is True]
    pendentes = [ln["competencia"] for ln in linhas if ln["vencida"] is None]
    sem_valor = [c for c, v in valores.items() if v is None]
    soma = None if any(valores[c] is None for c in vencidas) else sum((valores[c] for c in vencidas), ZERO)
    vinc = None if sm_propositura is None else sm_propositura * DOZE
    total = None if soma is None or vinc is None else soma + vinc
    detalhe = ", ".join(f"{c}: {s2(v) if v is not None else 'fora da tabela'}" for c, v in valores.items())
    motivo = (f"o BPC vale o salário mínimo de cada competência ({detalhe}) e as 12 vincendas o da propositura "
              f"({s2(sm_propositura) if sm_propositura is not None else 'fora da tabela'}); a rmi_pretendida "
              f"{s2(rmi)} não é o mínimo de todas elas, e o motor só multiplica um valor constante")
    if sem_valor:
        motivo += f"; mínimo fora de scripts/data/salario-minimo.json em {', '.join(sem_valor)}"
    if total is not None and pendentes:
        # sem total único enquanto houver competência de vencimento em aberto (CPC, art. 292, §1º): a reentrada com um
        # valor só apagaria a pendência
        motivo += (f". Sem as competências pendentes ({', '.join(pendentes)}), a conta nominal seria {s2(soma)} + "
                   f"{s2(vinc)} = {s2(total)}, mas não há total único: informe datas_vencimento delas (as leituras com "
                   "e sem cada uma saem em formula_aberta.leituras) e só então use valor_da_causa_informado")
    elif total is not None:
        # a recomendação de reentrada só sai em recomendacao_reentrada(), depois de todas as pendências conhecidas
        motivo += f". Conta nominal por competência: {s2(soma)} + {s2(vinc)} = {s2(total)}"
    conta = {"vencidas": [{"competencia": c, "salario_minimo": s2(valores[c])} for c in vencidas],
             "competencias_pendentes": pendentes,
             "vencidas_nominal": s2(soma), "salario_minimo_propositura": s2(sm_propositura), "vincendas_12": s2(vinc),
             "valor_da_causa_nominal": None if pendentes else s2(total),
             "valor_sem_competencias_pendentes": s2(total) if pendentes else None, "total_unico": False,
             "motivo": motivo,
             "memoria": f"BPC por competência: vencidas {' + '.join(s2(valores[c]) or '?' for c in vencidas) or '0'} "
                        f"= {s2(soma)}; 12 × {s2(sm_propositura)} = {s2(vinc)}; total nominal {s2(total)}"}
    return valor_comp, conta


def recomendacao_reentrada(conta, falta_bpc, faltas):
    """Fecha o motivo da conta do BPC. A reentrada com valor_da_causa_informado apagaria qualquer pendência que mude o
    valor (competência de fronteira, valor da competência da DIB, abono, correção, mínimo): só é recomendada quando a
    conta nominal existe e não há nenhuma outra pendência (QA final r3)."""
    total = conta["valor_da_causa_nominal"]
    if total is None:
        return
    outras = [f["item"] for f in faltas if f is not falta_bpc]
    if outras:
        extra = (f"; sem total único enquanto houver pendência que mude o valor ({'; '.join(outras)}): resolva-as "
                 "antes de usar valor_da_causa_informado")
    else:
        conta["total_unico"] = True
        extra = f"; rode de novo com valor_da_causa_informado = {total} para a alçada"
    conta["motivo"] += extra
    falta_bpc["motivo"] = conta["motivo"]


# ---------------------------------------------------------------- conta principal

def competencia_jef(total, alcada, renunciar):
    if total <= alcada:
        return "JEF", total, ZERO
    if renunciar:
        return "JEF-com-renuncia", alcada, total - alcada
    return "vara-federal", total, ZERO


def calcular(bruto, motor_atualizacao=MOTOR_ATUALIZACAO, motor_prazo=MOTOR_PRAZO,
             tabela_salario_minimo=TABELA_SALARIO_MINIMO):
    """Devolve (codigo_de_saida, dict_de_saida)."""
    try:
        texto_valido(bruto)
        e = normaliza(bruto)
        return _calcular(e, motor_atualizacao, motor_prazo, tabela_salario_minimo)
    except EntradaInvalida as err:
        return EXIT_ENTRADA, {"erro": "entrada_invalida", "detalhe": str(err), "versao": VERSAO}


def _calcular(e, motor_atualizacao, motor_prazo, tabela_salario_minimo):
    """Regime prescricional (QA final r5 A01): regular corta pelo ajuizamento, interrompida pelo marco_prescricional,
    nao_corre não corta. Sem o regime, as contas sem e com o corte regular: se o corte não alcança nada, a conta segue
    como sempre; se alcança, exit 3 com as duas, nunca o total sem o corte fechado."""
    args = (e, motor_atualizacao, motor_prazo, tabela_salario_minimo)
    regime = e.get("prescricao")
    if "valor_da_causa_informado" in e or regime == "nao_corre":
        return _conta(*args)
    if regime == "regular":
        return _conta(*args, marco_presc=e["data_ajuizamento"])
    if regime == "interrompida":
        return _conta(*args, marco_presc=e["marco_prescricional"])
    cod_com, s_com = _conta(*args, marco_presc=e["data_ajuizamento"])
    cod_sem, s_sem = _conta(*args)
    p = s_com["prescricao"]
    alcance = p["competencias_prescritas"] or p["competencias_em_aberto"] or p["abono_prescrito"] or p["abono_em_aberto"]
    s_sem["prescricao"] = dict(p, regime="nao_informado", aplicado=False)
    if not alcance:
        s_sem["prescricao"]["efeito"] = ("regime não informado; o corte quinquenal regular não alcança nenhuma "
                                         "competência nem abono: o regime não muda o total")
        return cod_sem, s_sem
    return _abre_prescricao(e, cod_sem, s_sem, cod_com, s_com)


def _leitura_prescricao(codigo, s, renunciar):
    apurado = s["valor_da_causa_apurado"]
    lt = {"exit": codigo, "valor_da_causa_apurado": apurado, "competencia": None,
          "pendencias": [f["item"] for f in s["dados_faltantes"]]}
    if apurado is not None and s["alcada_jef"] is not None:
        lt["competencia"] = competencia_jef(Decimal(apurado), Decimal(s["alcada_jef"]), renunciar)[0]
    alt = s.get("alternativa_m6")
    if alt:
        lt["alternativa_m6"] = {"criterio": alt["criterio"], "valor_da_causa_apurado": alt["valor_da_causa_apurado"],
                                "competencia": alt.get("competencia")}
    if s.get("formula_aberta") and s["formula_aberta"].get("leituras"):
        lt["leituras"] = s["formula_aberta"]["leituras"]
    return lt


def _abre_prescricao(e, cod_sem, s_sem, cod_com, s_com):
    """Exit 3: regime não informado e o corte regular muda o total. A saída é a da conta sem corte, sem nenhum total
    fechado; as duas contas completas saem em formula_aberta.leituras."""
    p = s_com["prescricao"]
    leituras = {
        "sem_corte_prescricional": dict(_leitura_prescricao(cod_sem, s_sem, e["renunciar_excedente"]),
                                        hipotese="prescrição não corre (prescricao = nao_corre: menor, incapaz ou "
                                                 "ausente)"),
        "com_corte_quinquenal_regular": dict(_leitura_prescricao(cod_com, s_com, e["renunciar_excedente"]),
                                             hipotese="prescricao = regular", corte=p["corte"],
                                             corte_com_prorrogacao=p["corte_com_prorrogacao"],
                                             competencias_prescritas=p["competencias_prescritas"],
                                             competencias_em_aberto=p["competencias_em_aberto"],
                                             abono_prescrito=p["abono_prescrito"]),
    }
    n = len(p["competencias_prescritas"])
    resumo = (f"{n} competência(s) prescrita(s) ({p['competencias_prescritas'][0]} a {p['competencias_prescritas'][-1]})"
              if n else "nenhuma competência prescrita por inteiro")
    if p["competencias_em_aberto"]:
        resumo += f", em aberto {', '.join(p['competencias_em_aberto'])}"
    if p["abono_prescrito"] or p["abono_em_aberto"]:
        resumo += f", abono alcançado ({', '.join(str(a['ano']) for a in p['abono_prescrito'])}" \
                  f"{'; em aberto ' + ', '.join(map(str, p['abono_em_aberto'])) if p['abono_em_aberto'] else ''})"
    falta = {"item": "regime prescricional",
             "motivo": f"prescricao não informada, e o corte quinquenal regular (vencimento devido antes de "
                       f"{p['corte']}, cinco anos antes do ajuizamento) muda o total: {resumo}. Informe prescricao "
                       "(regular; nao_corre para menor, incapaz ou ausente; interrompida com marco_prescricional); "
                       "as contas sem e com o corte saem em formula_aberta.leituras",
             "fonte": FONTE["prescricao"]}
    s_sem["dados_faltantes"].append(falta)
    for k in ("valor_da_causa", "competencia", "valor_renunciado", "valor_da_causa_apurado", "alternativa_m6",
              "alternativa_sem_abono_vincendas", "alternativa_com_abono_vincendas"):
        if k in s_sem:
            s_sem[k] = None
    s_sem["prescricao"]["efeito"] = f"regime não informado; o corte regular mudaria o total ({resumo}): exit 3"
    for f in (FONTE["prescricao"], FONTE["prazo_em_anos"]):
        if f not in s_sem["fundamento"]:
            s_sem["fundamento"].append(f)
    s_sem["fonte"] = sorted({m for f in s_sem["fundamento"] for m in re.findall(r"context/[\w/.-]+\.md", f)})
    s_sem["alertas"].insert(len(s_sem["alertas"]) - 1,
                            "[VERIFICAR] Prescrição quinquenal (Lei 8.213, art. 103, parágrafo único): o regime não veio "
                            f"na entrada e o corte regular muda o total ({resumo}); nenhum total foi fechado.")
    s_sem["memoria"].append(f"prescrição não informada: sem corte = {leituras['sem_corte_prescricional']['valor_da_causa_apurado']}; "
                            f"com o corte regular em {p['corte']} = "
                            f"{leituras['com_corte_quinquenal_regular']['valor_da_causa_apurado']}")
    s_sem["formula_aberta"] = {
        "expressao": _formula(e) + "; com prescricao = regular ou interrompida, só as competências e parcelas de abono "
                                   "com vencimento devido a partir do corte quinquenal (marco − 5 anos)",
        "faltando": [f["item"] for f in s_sem["dados_faltantes"]],
        "leituras": leituras,
        "instrucao": "Regime prescricional não informado e capaz de mudar o total: o script não fecha o total sem o "
                     "corte. Informe prescricao; as contas sem e com o corte quinquenal regular saem em leituras.",
    }
    return EXIT_FALTA, s_sem


def _abre_renda(e, motores, marco_presc, info, sem_renda, renda_prop):
    """Exit 3 (QA final r7 C1): a renda reajustada não se conhece em competência da conta (ano sem fator capturado,
    pro rata ausente, tabela que acaba, incorporação do teto sem a média). Nunca fecha com a renda congelada: as contas
    sem e com reajuste saem em formula_aberta.leituras, a primeira só como referência, sem total fechado."""
    cod_c, s = _conta(e, *motores, marco_presc=marco_presc, congelada=True)
    lt_cong = {"exit": cod_c, "valor_da_causa_apurado": s["valor_da_causa_apurado"], "competencia": s["competencia"],
               "aviso": "renda constante = rmi_pretendida, sem o reajuste anual (Lei 8.213, art. 41-A): não é o valor "
                        "da causa; serve só de referência"}
    if s.get("alternativa_m6"):
        lt_cong["alternativa_m6"] = {k: s["alternativa_m6"].get(k) for k in ("criterio", "valor_da_causa_apurado",
                                                                              "competencia")}
    if s.get("formula_aberta") and s["formula_aberta"].get("leituras"):
        lt_cong["leituras"] = s["formula_aberta"]["leituras"]
    segmentos = [{"desde": d.isoformat(), "renda": s2(r)} for d, r in info["segmentos"]]
    lt_reaj = {"valor_da_causa_apurado": None, "segmentos_conhecidos": segmentos,
               "renda_desconhecida_desde": info["limite"].isoformat() if info["limite"] else None,
               "competencias_sem_renda": sem_renda, "renda_na_propositura": s2(renda_prop), "motivo": info["motivo"]}
    s["evolucao_renda"] = {"segmentos": segmentos, "passos": info["passos"], "normas": info["normas"],
                           "limite": lt_reaj["renda_desconhecida_desde"], "motivo": info["motivo"],
                           "renda_na_propositura": s2(renda_prop)}
    falta = {"item": "evolução da renda (reajuste anual)",
             "motivo": f"{info['motivo']}; sem a renda reajustada: "
                       + (f"competências {', '.join(sem_renda)}" if sem_renda else "")
                       + ("; " if sem_renda and renda_prop is None else "")
                       + ("renda na propositura (12 vincendas)" if renda_prop is None else "")
                       + ". A conta com a renda congelada não é o valor da causa; as contas sem e com reajuste saem "
                         "em formula_aberta.leituras",
             "fonte": FONTE["reajuste"]}
    # a falta M6 da conta congelada diz "as duas contas estão completas": aqui nenhuma está
    s["dados_faltantes"] = [f for f in s["dados_faltantes"] if not f["item"].startswith("critério do abono")] + [falta]
    for k in ("valor_da_causa", "competencia", "valor_renunciado", "valor_da_causa_apurado", "alternativa_m6",
              "alternativa_sem_abono_vincendas", "alternativa_com_abono_vincendas", "vincendas_12", "abono_vincendo",
              "abono_vencidas"):
        if k in s:
            s[k] = None
    if s.get("vencidas"):
        s["vencidas"].update(valor=None, valor_nominal=None, correcao=None)
        for c in s["vencidas"]["competencias"]:
            c["valor"] = s2(renda_da_competencia(info, e, _tupla(c["competencia"])))
    if s.get("abono_vencidas_detalhe"):
        s["abono_vencidas_detalhe"] = None
    if FONTE["reajuste"] not in s["fundamento"]:
        s["fundamento"].append(FONTE["reajuste"])
    s["fonte"] = sorted({m for f in s["fundamento"] for m in re.findall(r"context/[\w/.-]+\.md", f)})
    s["alertas"].insert(len(s["alertas"]) - 1,
                        "[VERIFICAR] Reajuste anual da renda (Lei 8.213, art. 41-A) não fechado: "
                        f"{info['motivo']}; nenhum total foi fechado com a renda congelada.")
    s["memoria"].append(f"evolução da renda aberta: {info['motivo']}; com a renda congelada (só referência) = "
                        f"{lt_cong['valor_da_causa_apurado']}")
    s["formula_aberta"] = {
        "expressao": _formula(e),
        "faltando": [f["item"] for f in s["dados_faltantes"]],
        "leituras": {"sem_reajuste_renda_congelada": lt_cong, "com_reajuste": lt_reaj},
        "instrucao": "Renda reajustada desconhecida em competência da conta: o script não fecha o total com a renda "
                     "congelada. Aplique o fator do reajuste pela Portaria do ano (Anexo I no primeiro) e confira.",
    }
    return EXIT_FALTA, s


def _conta(e, motor_atualizacao, motor_prazo, tabela_salario_minimo, marco_presc=None, congelada=False):
    """congelada=True: renda constante = rmi_pretendida (só a leitura 'sem reajuste' de _abre_renda, QA r7 C1)."""
    faltas, alertas, memoria, fundamento = [], [], [], []
    saida = {
        "versao": VERSAO,
        "parametros_usados": eco(e),
        "vencidas": None, "abono_vencidas": None, "abono_vencidas_detalhe": None, "vincendas_12": None, "abono_vincendo": None,
        "valor_da_causa_apurado": None, "valor_da_causa": None,
        "criterio_abono_vincendas": None, "alternativa_m6": None,
        "alcada_jef": None, "salario_minimo": None, "competencia": None, "valor_renunciado": None,
        "fundamento": fundamento, "alertas": alertas, "regra": None, "fonte": [], "memoria": memoria,
        "dados_faltantes": faltas, "formula_aberta": None, "prescricao": None, "evolucao_renda": None,
    }
    sm, sm_fonte = salario_minimo(e, tabela_salario_minimo, faltas)
    alcada = q2(ALCADA_SM * sm) if sm is not None else None
    saida["salario_minimo"] = {"valor": s2(sm), "fonte": sm_fonte,
                               "data_referencia": e["data_ajuizamento"].isoformat()}
    saida["alcada_jef"] = s2(alcada)
    fundamento += [FONTE["alcada"], FONTE["congelamento"]]
    if alcada is not None:
        memoria.append(f"alçada = 60 × {sm} (salário mínimo da distribuição) = {q2(alcada)}")

    if "valor_da_causa_informado" in e:
        total = e["valor_da_causa_informado"]
        saida["regra"] = "alçada do JEF sobre total já formado"
        saida["valor_da_causa_apurado"] = s2(total)
        memoria.append(f"valor da causa informado = {q2(total)}")
        _fecha(saida, total, alcada, e, memoria, alertas, fundamento)
        return _finaliza(saida, faltas, "alcada = 60 × salario_minimo(data_ajuizamento); competencia = JEF "
                         "se valor_da_causa <= alcada, senão vara-federal ou JEF-com-renuncia")

    # --- com RMI
    rmi, nat = e["rmi_pretendida"], e["natureza"]
    # QA final r4 A04: vencida é a prestação devida (vencimento devido) antes do ajuizamento, não a paga
    saida["regra"] = ("vencidas (competências vencidas, isto é, devidas antes do ajuizamento: Lei 8.213, art. 103, "
                      "parágrafo único; CPC, art. 292, §1º) + abonos vencidos + 12 vincendas "
                      "[+ abono vincendo, M6]; alçada de 60 salários mínimos da distribuição")
    fundamento += [FONTE["vencidas_vincendas"], FONTE["vencimento"]]
    # QA final r4 A03: a fonte do BPC (LOAS, art. 20) só na natureza assistencial; abono=false em benefício
    # previdenciário é parâmetro da entrada, não hipótese normativa do BPC
    if e["abono"]:
        fundamento.append(FONTE["abono"])
    elif nat == "assistencial":
        fundamento.append(FONTE["bpc_sem_abono"])
    else:
        fundamento.append(FONTE["abono_excluido_na_entrada"])
        alertas.append("[VERIFICAR] abono=false em benefício previdenciário: o abono anual ficou fora por parâmetro "
                       "da entrada, não por regra do BPC; confira pela espécie se incide o art. 40 da Lei 8.213/1991 "
                       "(CPC, art. 292).")
    motor_b = carregar_motor(motor_prazo, "prazo")
    dados_sm, _ = ler_tabela_sm(tabela_salario_minimo)
    # QA final r7 C1: renda reajustada por competência (Lei 8.213, art. 41-A), nunca a RMI congelada; no BPC, o mínimo
    # de cada competência (conta_bpc_por_competencia)
    aj = e["data_ajuizamento"]
    renda_info = None
    if nat == "previdenciaria" and not congelada:
        renda_info = evolucao_renda(e, dt.date(aj.year, aj.month, calendar.monthrange(aj.year, aj.month)[1]), dados_sm,
                                    Path(tabela_salario_minimo).parent)

        def renda_c(c):
            return renda_da_competencia(renda_info, e, c)
        renda_prop = renda_na_data(renda_info, aj)
    else:
        def renda_c(c):
            return rmi
        renda_prop = rmi
    janelas = JanelaPagamento(motor_b)
    linhas = classifica_vencidas(e, janelas, dados_sm, renda_c if renda_info is not None else None)
    if janelas.motor is None:
        alertas.append(f"[VERIFICAR] {janelas.sem_calendario}: dias úteis contados só sem sábado e domingo "
                       f"(sem feriados nacionais); janelas alargadas em {JanelaPagamento.MARGEM_SEM_MOTOR.days} "
                       "dias.")
    if any(regime_janela((int(ln["competencia"][:4]), int(ln["competencia"][5:]))) not in (None, JANELAS[-1])
           for ln in linhas):
        fundamento.append(FONTE["vencimento_historico"])
    # QA final r5 A01: prescrição quinquenal pelo vencimento devido (Lei 8.213, art. 103, parágrafo único)
    linhas_orig = linhas
    comps_orig = [(int(ln["competencia"][:4]), int(ln["competencia"][5:])) for ln in linhas if ln["vencida"] is True]
    regime = e.get("prescricao", "nao_informado")
    presc = {"regime": regime, "aplicado": marco_presc is not None, "marco": None, "corte": None,
             "corte_com_prorrogacao": None, "competencias_prescritas": [], "valor_prescrito_nominal": None,
             "competencias_em_aberto": [], "abono_prescrito": [], "abono_em_aberto": []}
    situacao, corte = {}, None
    if marco_presc is not None:
        corte, cedo = cortes_prescricionais(marco_presc, janelas)
        linhas, prescritas, abertas_presc, situacao = aplica_prescricao(linhas, corte, cedo)
        fundamento += [FONTE["prescricao"], FONTE["prazo_em_anos"]]
        valores_presc = [renda_c(_tupla(ln["competencia"])) if nat != "assistencial" else
                         (lambda a: None if a is None else a[0])(sm_na_data(dados_sm, dt.date(
                             int(ln["competencia"][:4]), int(ln["competencia"][5:]), 1))) for ln in prescritas]
        presc.update(marco=marco_presc.isoformat(), corte=corte.isoformat(),
                     corte_com_prorrogacao=cedo.isoformat() if cedo != corte else None,
                     competencias_prescritas=[ln["competencia"] for ln in prescritas],
                     valor_prescrito_nominal=None if any(v is None for v in valores_presc)
                     else s2(sum(valores_presc, ZERO)),
                     competencias_em_aberto=[ln["competencia"] for ln in abertas_presc])
        memoria.append(f"prescrição ({regime}): corte quinquenal em {corte.isoformat()} (5 anos antes de "
                       f"{marco_presc.isoformat()}); {len(prescritas)} competência(s) com vencimento devido anterior, "
                       "fora da conta" + (f": {prescritas[0]['competencia']} a {prescritas[-1]['competencia']}"
                                          if prescritas else ""))
        if abertas_presc:
            faltas.append({"item": "prescrição da competência de fronteira do corte quinquenal",
                           "motivo": f"corte em {corte.isoformat()}"
                                     + (f" (com a prorrogação do Código Civil, art. 132, §1º, só é certa a prescrição "
                                        f"antes de {cedo.isoformat()})" if cedo != corte else "")
                                     + ": o vencimento devido de "
                                     + "; ".join(f"{ln['competencia']} ({ln.get('vencimento_informado') or (ln['janela']['inicio'] + ' a ' + ln['janela']['fim'] if ln.get('janela') else 'sem janela')})"
                                                 for ln in abertas_presc)
                                     + " cruza o corte e o dia individual decide; informe datas_vencimento ou confira "
                                       "cada competência; as leituras com e sem a competência saem em "
                                       "formula_aberta.leituras",
                           "fonte": FONTE["prescricao"]})
        if nat == "assistencial":
            alertas.append("[VERIFICAR] BPC: o corte quinquenal segue o art. 103, parágrafo único, da Lei 8.213, única "
                           "regra de prescrição capturada em context/lei/; confira a fonte do prazo no benefício "
                           "assistencial.")
    elif regime == "nao_corre":
        fundamento.append(FONTE["prescricao"])
        alertas.append("[VERIFICAR] prescricao = nao_corre: a entrada declara menor, incapaz ou ausente (Lei 8.213, art. "
                       "103, parágrafo único, na forma do Código Civil); nenhuma competência foi cortada. Confira a "
                       "causa e se ela cobre todo o período desde a DIB.")
    saida["prescricao"] = presc
    indeterminadas = [ln for ln in linhas if ln["vencida"] is None and not ln.get("fora_dos_regimes")]
    fora_regimes = [ln for ln in linhas if ln.get("fora_dos_regimes")]
    antecipadas = [ln for ln in indeterminadas if ln.get("antecipacao_incerta")]
    sem_calendario = [ln for ln in indeterminadas if ln.get("expediente_incerto") and not ln.get("antecipacao_incerta")]
    fronteira = [ln for ln in indeterminadas if not ln.get("antecipacao_incerta") and not ln.get("expediente_incerto")
                 and not ln.get("prescricao_incerta")]
    if sem_calendario:
        faltas.append({"item": "expediente bancário do vencimento informado",
                       "motivo": "o calendário bancário não decide o dia ("
                                 + "; ".join(f"{ln['competencia']}: {ln['vencimento_informado']}" for ln in sem_calendario)
                                 + f"): {sem_calendario[0]['expediente_incerto']}; o vencimento devido só vale em dia "
                                   "de expediente bancário normal (art. 41-A, §4º); confira o calendário oficial de "
                                   "pagamentos do INSS; as leituras com e sem a competência saem em "
                                   "formula_aberta.leituras",
                       "fonte": FONTE["vencimento"]})
    if antecipadas:
        faltas.append({"item": "antecipação do §3º sem data de vigência",
                       "motivo": "vencimento informado antes do mês seguinte ("
                                 + "; ".join(f"{ln['competencia']}: {ln['vencimento_informado']}" for ln in antecipadas)
                                 + "): só a antecipação do art. 41-A, §3º, o admite, e a MP 404/2007 que a criou não "
                                   "tem dia nem mês capturados em context/lei/lei-8213-1991.md; antes dela o pagamento "
                                   "era no mês seguinte (art. 41-A, §2º, redação da Lei 11.430/2006); confira a data de "
                                   "vigência da MP 404 e a do vencimento; as leituras com e sem a competência saem em "
                                   "formula_aberta.leituras",
                       "fonte": FONTE["vencimento_historico"]})
    if fronteira:
        faltas.append({"item": "vencimento da competência de fronteira",
                       "motivo": "janela de pagamento cruza o ajuizamento ("
                                 + "; ".join(f"{ln['competencia']}: {ln['janela']['inicio']} a {ln['janela']['fim']}, "
                                             f"{ln['janela']['paragrafo']}" for ln in fronteira)
                                 + "): o pagamento é distribuído entre os beneficiários e o dia individual não "
                                   "foi informado; informe datas_vencimento (vencimento individual devido) ou "
                                   "confira cada competência; as leituras com e sem a competência saem em "
                                   "formula_aberta.leituras",
                       "fonte": FONTE["vencimento"]})
    if fora_regimes:
        faltas.append({"item": "janela de pagamento anterior à Lei 8.213",
                       "motivo": f"competências {', '.join(ln['competencia'] for ln in fora_regimes)} anteriores a "
                                 f"{comp_txt(JANELAS[0]['desde'])}: regime de pagamento anterior (CLPS) não capturado em "
                                 "context/lei/; informe datas_vencimento",
                       "fonte": FONTE["vencimento_historico"]})
    indeterminadas = indeterminadas + fora_regimes
    vencidas = [ln for ln in linhas if ln["vencida"] is True]
    comps_vencidas = [(int(ln["competencia"][:4]), int(ln["competencia"][5:])) for ln in vencidas]
    if renda_info is not None:
        sem_renda = [ln["competencia"] for ln in vencidas + indeterminadas if renda_c(_tupla(ln["competencia"])) is None]
        if sem_renda or renda_prop is None:
            return _abre_renda(e, (motor_atualizacao, motor_prazo, tabela_salario_minimo), marco_presc, renda_info,
                               sem_renda, renda_prop)
    if e["dib"].day != 1 and (e["dib"].year, e["dib"].month) in comps_vencidas:
        # Integral × proporcional aos dias: nenhum anexo de context/lei/ resolve o valor do mês da DIB; a conta
        # fica aberta com as duas leituras (decisão de produto: na dúvida, fórmula aberta).
        dias_mes = calendar.monthrange(e["dib"].year, e["dib"].month)[1]
        prop = q2(rmi * (dias_mes - e["dib"].day + 1) / dias_mes)
        faltas.append({"item": "valor da competência da DIB",
                       "motivo": f"DIB no meio do mês ({e['dib'].isoformat()}): a competência "
                                 f"{comp_txt((e['dib'].year, e['dib'].month))} vale {q2(rmi)} se integral ou {prop} "
                                 f"se proporcional aos dias (diferença {q2(rmi - prop)}); o critério vem do título "
                                 "ou do pagamento do INSS, não informado",
                       "fonte": FONTE["vencidas_vincendas"]})
        alertas.append(f"[VERIFICAR] DIB no meio do mês ({e['dib'].isoformat()}): a competência "
                       f"{comp_txt((e['dib'].year, e['dib'].month))} entra integral ({q2(rmi)}) na conta exibida; "
                       f"proporcional aos dias, ela vale {prop} (diferença {q2(rmi - prop)}).")

    # QA final B-01: o BPC é um salário mínimo mensal (LOAS, art. 20): cada vencida vale o mínimo da própria competência
    # e as 12 vincendas o da propositura (CPC, art. 292, §§1º e 2º). O motor só aceita RMI constante: se o mínimo muda
    # entre as competências, ou difere da rmi_pretendida, a conta sai aberta com os valores por competência, nunca
    # congelada num único valor.
    valor_comp, conta_bpc, falta_bpc = None, None, None
    if nat == "assistencial":
        valor_comp, conta_bpc = conta_bpc_por_competencia(e, linhas, dados_sm, sm)
        if conta_bpc is not None:
            falta_bpc = {"item": "BPC: salário mínimo por competência",
                         "motivo": conta_bpc["motivo"], "fonte": FONTE["bpc_minimo"]}
            faltas.append(falta_bpc)
            fundamento.append(FONTE["bpc_minimo"])

    # abonos vencidos pelo calendário de pagamento das parcelas (Decreto 3.048, art. 120, §1º; IN 128, art. 619)
    abonos = []
    if e["abono"]:
        # o calendário do abono lê as competências antes do corte; a prescrição corta depois, parcela a parcela
        abonos, abertos = abonos_vencidos(e, linhas_orig, comps_orig, renda_c)
        if corte is not None:
            abonos, abono_prescrito, abertos_presc = prescreve_abonos(abonos, situacao, corte)
            presc["abono_prescrito"] = abono_prescrito
            presc["abono_em_aberto"] = [ano for ano, _ in abertos_presc]
            abertos = abertos + [(ano, f"prescrição: {m}") for ano, m in abertos_presc]
            if abono_prescrito:
                memoria.append("abono prescrito, fora da conta: " + "; ".join(
                    f"{a['ano']} = {a['valor']}" + (f" (parcelas {', '.join(a['parcelas'])})" if a["parcelas"] else "")
                    for a in abono_prescrito))
        for ano, motivo in abertos:
            faltas.append({"item": f"abono anual vencido de {ano}", "motivo": motivo, "fonte": FONTE["abono_calendario"]})
        if abonos or abertos:
            fundamento.append(FONTE["abono_calendario"])
    if e["datas_vencimento"]:
        fundamento.append(FONTE["vencimento_devido"])
    rendas_venc = [renda_c(c) for c in comps_vencidas]
    soma_venc_nom = sum(rendas_venc, ZERO)
    soma_abono_nom = sum((a["valor"] for a in abonos), ZERO)
    if renda_info is not None:
        saida["evolucao_renda"] = {"segmentos": [{"desde": d.isoformat(), "renda": s2(r)}
                                                 for d, r in renda_info["segmentos"]],
                                   "passos": renda_info["passos"], "normas": renda_info["normas"],
                                   "renda_na_propositura": s2(renda_prop)}
        memoria.extend(renda_info["passos"])
        if renda_info["passos"]:
            fundamento.append(FONTE["reajuste"])
        if renda_info["sem_piso"]:
            alertas.append("[VERIFICAR] rmi_pretendida abaixo do salário mínimo da DIB: renda sem o piso (benefício que "
                           "não substitui a renda, como o auxílio-acidente — Decreto 3.048, art. 42); confira a espécie.")
    grupos = {}
    for r in rendas_venc:
        grupos[r] = grupos.get(r, 0) + 1
    memoria.append(f"competências vencidas antes de {e['data_ajuizamento'].isoformat()}: "
                   + (" + ".join(f"{n} × {q2(r)}" for r, n in grupos.items()) or "0")
                   + f" = {q2(soma_venc_nom)}")
    for a in abonos:
        memoria.append(f"abono de {a['ano']} vencido = {a['valor']} ({a['meses']}/12 × {q2(a['base'])} no ano; "
                       f"{a['calendario']}"
                       + (f"; parcelas {', '.join(f'{comp_txt(c)}: {v}' for c, v in a['parcelas'])}"
                          if a["parcelas"] else "") + ")")

    # correção (motor de atualização)
    corrigido = e["corrigir_vencidas"]
    registros, soma_venc, soma_abono = [], soma_venc_nom, soma_abono_nom
    if corrigido:
        fundamento += [FONTE["correcao"], FONTE["sem_juros"]]
        motor_a = carregar_motor(motor_atualizacao, "atualizacao")
        if motor_a is None:
            faltas.append({"item": "motor de atualização",
                           "motivo": f"{Path(motor_atualizacao).name} não encontrado na pasta do script; "
                                     "sem ele, as vencidas não são corrigidas",
                           "fonte": FONTE["correcao"]})
            soma_venc = soma_abono = None
        else:
            alertas_motor, soma_venc, soma_abono = [], ZERO, ZERO
            for c in comps_vencidas:
                v, reg = corrigir(motor_a, renda_c(c), c, e, faltas, alertas_motor)
                registros.append(reg)
                soma_venc = None if (v is None or soma_venc is None) else soma_venc + v
            for a in abonos:
                if a["parcelas"] is None:
                    # cada parcela se corrige da própria competência (Manual 2026, 4.3.1.1, Nota 2), nunca de dezembro
                    # por padrão; sem o calendário do ano, a competência das parcelas não é conhecida
                    faltas.append({"item": f"correção do abono vencido de {a['ano']}",
                                   "motivo": f"valor nominal {a['valor']} fechado, mas a competência de cada parcela "
                                             f"não ({a['calendario']}); a correção parte da competência da parcela",
                                   "fonte": FONTE["abono_calendario"]})
                    soma_abono = None
                    continue
                for c, valor in a["parcelas"]:
                    v, reg = corrigir(motor_a, valor, c, e, faltas, alertas_motor)
                    reg["parcela"] = f"abono {a['ano']}"
                    registros.append(reg)
                    soma_abono = None if (v is None or soma_abono is None) else soma_abono + v
            alertas.extend(f"[motor de atualização] {a}" for a in alertas_motor)
            selic = sorted({r["competencia"] for r in registros if r["fonte_indice"]
                            and any(f.get("indice") == "SELIC" for f in r["fonte_indice"])})
            if selic:
                # a Selic engloba correção e juros (Manual 2026, 4.3.1.1, Nota 2), e o Manual não diz se, antes da
                # citação, entra inteira: regra que o context/lei/ não resolve, então a conta fica aberta
                faltas.append({"item": "Selic antes da citação nas vencidas corrigidas",
                               "motivo": f"competências com Selic ({', '.join(selic)}): a Selic engloba correção e "
                                         "juros, e o Manual não diz se, antes da citação (aqui, o ajuizamento), entra "
                                         "inteira ou só a parte de correção; o valor exibido em vencidas usa a Selic "
                                         "inteira (resultado do motor). Escolher e declarar o critério",
                               "fonte": FONTE["correcao"]})
            memoria.append("correção de cada vencida do mês da competência até o ajuizamento, sem juros "
                           "(citação = ajuizamento), pelo motor de atualização (regime fazenda-ec113, "
                           f"natureza {nat})")
    else:
        alertas.append("Valor nominal: falta a correção das vencidas (corrigir_vencidas = false).")

    saida["vencidas"] = {
        "quantidade": len(comps_vencidas),
        "competencias": [{"competencia": ln["competencia"], "vencimento": ln["vencimento"],
                          "janela": ln["janela"], "valor": s2(renda_c(_tupla(ln["competencia"])))}
                         for ln in vencidas],
        "competencias_nao_vencidas": [ln["competencia"] for ln in linhas if ln["vencida"] is False],
        "competencias_indeterminadas": [ln["competencia"] for ln in indeterminadas],
        "valor_nominal": s2(soma_venc_nom),
        "valor": s2(soma_venc),
        "corrigido": corrigido,
        "correcao": registros or None,
    }
    saida["abono_vencidas"] = s2(soma_abono)
    saida["abono_vencidas_detalhe"] = {"por_ano": [{"ano": a["ano"], "meses": a["meses"], "valor": str(a["valor"])}
                                                   for a in abonos],
                                       "valor_nominal": s2(soma_abono_nom), "corrigido": corrigido}
    vinc = renda_prop * DOZE
    saida["vincendas_12"] = s2(vinc)
    memoria.append(f"12 vincendas = 12 × {q2(renda_prop)} (renda na propositura, sem antecipar o reajuste seguinte) "
                   f"= {q2(vinc)}")

    if not e["abono"]:
        criterio = "não se aplica: sem abono anual" + (" (BPC)" if nat == "assistencial" else "")
        leituras = {"padrao": (ZERO, criterio)}
    else:
        inc = (renda_prop, "incluir (padrão, interpretação do CPC 292 §2º)")
        exc = (ZERO, "excluir (alternativa M6)")
        leituras = {"padrao": inc, "alternativa": exc} if e["incluir_abono_nas_vincendas"] else \
            {"padrao": (ZERO, "excluir (escolha da entrada; o padrão M6 é incluir)"),
             "alternativa": (renda_prop, "incluir (padrão, interpretação do CPC 292 §2º)")}
    abono_vinc, criterio = leituras["padrao"]
    saida["abono_vincendo"] = s2(abono_vinc)
    saida["criterio_abono_vincendas"] = criterio
    if e["abono"]:
        alertas.append("M6: o abono nas 12 vincendas é interpretação declarada do CPC, art. 292, §2º "
                       "(\"prestação anual\"), não pacificada; a outra conta sai em alternativa_m6.")

    if conta_bpc is not None:
        recomendacao_reentrada(conta_bpc, falta_bpc, faltas)
        saida["conta_bpc_por_competencia"] = conta_bpc
        memoria.append(conta_bpc["memoria"])
    if soma_venc is None or soma_abono is None:
        return _finaliza(saida, faltas, _formula(e))
    total = soma_venc + soma_abono + vinc + abono_vinc
    leituras_fronteira = None
    if indeterminadas and not fora_regimes:
        # QA final A02: sem o vencimento individual, as duas leituras (com e sem as competências de fronteira), no
        # valor nominal da competência (o mínimo de cada uma no BPC)
        if conta_bpc:
            txt = conta_bpc["valor_da_causa_nominal"] or conta_bpc["valor_sem_competencias_pendentes"]
            base = None if txt is None else Decimal(txt)
        else:
            base = soma_venc_nom + soma_abono_nom + vinc + abono_vinc
        # valores conferidos antes da soma: sem o mínimo de alguma competência, a leitura fica sem número (exit 3)
        valores_extra = [valor_comp(ln["competencia"]) if valor_comp else renda_c(_tupla(ln["competencia"]))
                         for ln in indeterminadas]
        extra = None if any(v is None for v in valores_extra) else sum(valores_extra, ZERO)
        leituras_fronteira = {}
        for nome, valor in (("sem_competencias_de_fronteira", base),
                            ("com_competencias_de_fronteira", None if extra is None or base is None else base + extra)):
            lt = {"competencias": [ln["competencia"] for ln in indeterminadas], "valor_da_causa_nominal": s2(valor)}
            if valor is not None and alcada is not None:
                lt["competencia"] = competencia_jef(q2(valor), alcada, e["renunciar_excedente"])[0]
            leituras_fronteira[nome] = lt
        memoria.append("fronteira: " + "; ".join(f"{k} = {v['valor_da_causa_nominal']}"
                                                 for k, v in leituras_fronteira.items()))
    memoria.append(f"valor da causa = {q2(soma_venc)} + {q2(soma_abono)} + {q2(vinc)} + {q2(abono_vinc)} "
                   f"= {q2(total)} ({criterio})")
    saida["valor_da_causa_apurado"] = s2(total)
    _fecha(saida, total, alcada, e, memoria, alertas, fundamento)

    if "alternativa" in leituras:
        alt_abono, alt_crit = leituras["alternativa"]
        alt_total = soma_venc + soma_abono + vinc + alt_abono
        alt = {"criterio": alt_crit, "abono_vincendo": s2(alt_abono), "valor_da_causa_apurado": s2(alt_total)}
        if alcada is not None:
            comp_alt, valor_alt, ren_alt = competencia_jef(q2(alt_total), alcada, e["renunciar_excedente"])
            alt.update({"competencia": comp_alt, "valor_da_causa": s2(valor_alt),
                        "valor_renunciado": s2(ren_alt)})
            if comp_alt != saida["competencia"]:
                alertas.append(f"[VERIFICAR] M6 muda a competência: {saida['competencia']} com o critério "
                               f"padrão × {comp_alt} com a alternativa. Levar as duas contas ao advogado.")
        saida["alternativa_m6"] = alt
        chave = "alternativa_sem_abono_vincendas" if alt_abono == 0 else "alternativa_com_abono_vincendas"
        saida[chave] = s2(alt_total)
        memoria.append(f"alternativa M6 ({alt_crit}) = {q2(alt_total)}")
    return _finaliza(saida, faltas, _formula(e), m6="alternativa" in leituras, leituras_fronteira=leituras_fronteira)


def _fecha(saida, total, alcada, e, memoria, alertas, fundamento):
    if alcada is None:
        return
    total = q2(total)   # política única de centavos (igual à RPV): classifica o valor exibido, 2 casas, meio para cima
    comp, valor, renunciado = competencia_jef(total, alcada, e["renunciar_excedente"])
    saida["competencia"], saida["valor_da_causa"], saida["valor_renunciado"] = comp, s2(valor), s2(renunciado)
    memoria.append(f"{total} {'<=' if total <= alcada else '>'} {alcada} → {comp}"
                   + (f"; renúncia expressa ao excedente de {q2(renunciado)}" if renunciado else ""))
    if comp == "JEF-com-renuncia":
        fundamento.append(FONTE["renuncia"])
        alertas.append("Renúncia expressa, inclusive de vincendas (STJ Tema 1.030); quem decide renunciar é "
                       "o advogado com o cliente.")
    elif comp == "vara-federal":
        alertas.append(f"Acima da alçada: vara federal, ou JEF com renúncia expressa de {q2(total - alcada)} "
                       "(STJ Tema 1.030).")
    if comp != "vara-federal":
        fundamento.append(FONTE["jef_sem_prazo_diferenciado"])
        alertas.append("No JEF não há prazo diferenciado para o INSS (Lei 10.259, art. 9º).")
    alertas.append("A alçada fica congelada na distribuição: o reajuste do mínimo não desloca o processo "
                   "(CPC, art. 43).")


def _formula(e):
    base = ("valor_da_causa = Σ renda(c) (competências cuja janela de pagamento do art. 41-A termina antes do "
            "ajuizamento, ou com vencimento devido informado antes dele) + Σ abono vencido (parcelas do calendário do "
            "ano: 50% × renda na 1ª e meses/12 × renda do ano − 1ª na 2ª) + 12 × renda(propositura); renda(c) = rmi "
            "reajustada em cada janeiro (Lei 8.213, art. 41-A; Portaria do ano, pro rata no 1º pelo Anexo I), com o "
            "piso de um salário mínimo e o teto da competência; no BPC, o mínimo da competência")
    if e.get("abono"):
        base += " [+ renda(propositura) de abono vincendo, padrão M6]"
    if e.get("prescricao") in ("regular", "interrompida"):
        base += ("; fora as competências e parcelas de abono prescritas: vencimento devido antes do corte quinquenal "
                 "(marco − 5 anos; marco = " + ("ajuizamento" if e["prescricao"] == "regular" else "marco_prescricional")
                 + "; Lei 8.213, art. 103, parágrafo único)")
    if e.get("corrigir_vencidas"):
        base += ("; cada vencida e cada parcela do abono corrigida do mês da própria competência ao ajuizamento "
                 "(Manual CJF 2026, 4.3.1.1)")
    return base + "; alcada = 60 × salario_minimo(data_ajuizamento)"


def _finaliza(saida, faltas, formula, m6=False, leituras_fronteira=None):
    """Exit 3 quando falta dado (números nulos) ou quando a leitura M6 fica em aberto (as duas contas saem
    completas: BUILD-CONTRACT, W0-golden, "caso indeterminado entra com as duas leituras e exit 3")."""
    saida["fonte"] = sorted({m for f in saida["fundamento"] for m in re.findall(r"context/[\w/.-]+\.md", f)})
    saida["alertas"].append(AVISO_FIXO)
    if not faltas and m6:
        alt = saida["alternativa_m6"]
        faltas.append({"item": "critério do abono nas 12 vincendas (M6)",
                       "motivo": "interpretação não pacificada do CPC, art. 292, §2º; as duas contas estão "
                                 "completas e a escolha é do advogado",
                       "fonte": FONTE["vencidas_vincendas"]})
        saida["formula_aberta"] = {
            "expressao": formula,
            "faltando": [f["item"] for f in faltas],
            "leituras": {
                "padrao": {"criterio": saida["criterio_abono_vincendas"], "valor_da_causa": saida["valor_da_causa"],
                           "competencia": saida["competencia"]},
                "alternativa": {"criterio": alt["criterio"], "valor_da_causa": alt.get("valor_da_causa"),
                                "competencia": alt.get("competencia")}},
            "instrucao": "Leitura indeterminada (M6): valor_da_causa traz o padrão e alternativa_m6 a outra conta. "
                         "Escolher e declarar o critério na petição.",
        }
        return EXIT_FALTA, saida
    if faltas:
        saida["valor_da_causa"] = saida["competencia"] = saida["valor_renunciado"] = None
        saida["formula_aberta"] = {
            "expressao": formula,
            "faltando": [f["item"] for f in faltas],
            "instrucao": "Número não fechado: preencha os termos faltantes pela fonte oficial. Conta aberta em "
                         "context/calculo-valor-causa.md. O script nunca estima.",
        }
        if leituras_fronteira:
            saida["formula_aberta"]["leituras"] = leituras_fronteira
        return EXIT_FALTA, saida
    return EXIT_OK, saida


# ---------------------------------------------------------------- CLI

def build_parser():
    ap = argparse.ArgumentParser(
        prog="calc_previdenciario_valor_causa.py",
        description="Valor da causa (vencidas + 12 vincendas + abono) e alçada do JEF. Entrada JSON por "
                    "--entrada ou stdin; campos em context/calculo-valor-causa.md, seção 6.")
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
        print(json.dumps({"script": "calc_previdenciario_valor_causa.py", "versao": VERSAO}))
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
