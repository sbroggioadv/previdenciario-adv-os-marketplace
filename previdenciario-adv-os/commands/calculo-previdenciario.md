---
description: Produz calculo previdenciario completo (RMI, tempo de contribuicao, liquidacao) com auto-ataque (Protocolo 2.4).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
argument-hint: [tipo opcional: rmi | tempo | liquidacao]
---

Voce foi acionado pelo comando `/calculo-previdenciario` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** produzir calculo previdenciario com Protocolo 2.4 integral (5 etapas) e auto-ataque (assumir papel da PFE/INSS).

## PROTOCOLO DE EXECUCAO

### 1. Verificar plugin ativo

`previdenciario/cowork-state.json` existe? Se nao, sugerir `/start-previdenciario`.

### 2. Identificar tipo de calculo

Pelo argumento OU perguntar:

```
Que tipo de calculo?

1. RMI (Renda Mensal Inicial)
   - Aposentadoria por idade
   - Aposentadoria por tempo de contribuicao
   - Aposentadoria especial
   - Aposentadoria por incapacidade permanente
   - BPI temporario / BPC

2. Tempo de contribuicao
   - Tempo bruto + especial convertido
   - Concomitancia
   - Tempo rural
   - Carencia (separadamente)

3. Liquidacao de sentenca
   - Atrasados + correcao + juros
   - Subdivisao RPV / precatorio
   - Honorarios sucumbenciais (Sumula 111 STJ)

4. Comparativo de regras (transicao EC 103/2019)
   - Pedagio 50% + 100%
   - Pontos
   - Idade minima progressiva
   - Professores
   - Indica MAIS BENEFICA (PA-08)
```

### 3. Coleta de dados (Protocolo 2.4 Etapa 1)

**ATENCAO PA-20:** sem dado, NAO estimar silenciosamente.

Verificar:
- **Regime:** RGPS / RPPS / Complementar (PA-06 — nao misturar)
- **Data de filiacao** ao sistema
- **DER** (data de entrada do requerimento)
- **DIB** (data de inicio do beneficio)
- **CNIS completo** (PA-13)
- **Salarios-de-contribuicao** mes a mes (ou pelo menos PBC)
- **Regra aplicavel:**
  - Direito adquirido ate 12/11/2019? → regra anterior (PA-07)
  - Pos-EC 103/2019? → fórmula nova ou transicao mais benefica

Se faltar dado: parar, sinalizar, pedir ao operador.

### 4. Etapas do Protocolo 2.4

```
ETAPA 1 — Mapear regime e marco temporal
   ✓ regime identificado
   ✓ marco temporal (filiacao + DER + DIB)
   ✓ regra aplicavel definida

ETAPA 2 — Apurar tempo e carencia
   ✓ tempo bruto
   ✓ tempo especial convertido (se PPP/LTCAT)
   ✓ concomitancia tratada
   ✓ carencia apurada SEPARADAMENTE

ETAPA 3 — Salario-de-beneficio e RMI
   ✓ regra correta:
       - pre-Lei 13.846/2019: PBC 80% maiores
       - pos-Lei 13.846/2019: 100% das contribuicoes do PBC
       - pos-EC 103/2019: formula especifica
   ✓ fator previdenciario (se aplicavel)

ETAPA 4 — Memoria de calculo detalhada
   ✓ fundamento legal de cada parcela
   ✓ base de calculo com valor utilizado
   ✓ indice de correcao:
       - IPCA-E ate 2021
       - SELIC pos-2021 (Lei 14.439/2022)
   ✓ juros conforme decisao
   ✓ subtotal + total geral

ETAPA 5 — Auto-ataque (revisao implacavel)
   Assuma papel da PFE/INSS e ataque o proprio calculo:
   - valores alem do titulo executivo?
   - periodos errados?
   - indices contestaveis?
   - compensacao com pagamentos administrativos?
   - Sumula 111 STJ na sucumbencia?
   - RPV vs precatorio?
   Reportar fragilidades encontradas.
```

### 5. Cadeia de skills

```
1. analise-cnis (Tier 2 C) — sempre que houver CNIS
2. analise-ppp-ltcat-aposentadoria-especial (T2 C) — se especial
3. calculo-tempo-contribuicao (T2 D)
4. calculo-rmi (T2 D)
5. liquidacao-sentenca-previdenciaria (T2 D) — se liquidacao
6. visual-law-previdenciario (transversal) — para tabela final
7. suprema-corte-previdenciario (R1-R4)
```

### 6. Entrega

```
[NOME CLIENTE] — Calculo Previdenciario

REGIME: <RGPS / RPPS>
TIPO: <RMI / tempo / liquidacao / comparativo>
REGRA APLICAVEL: <pre-EC 103 / EC 103 + transicao X>

ETAPA 1: <tabela>
ETAPA 2: <tabela>
ETAPA 3: <tabela>
ETAPA 4: MEMORIA DE CALCULO
   <linha a linha com fundamento>

TOTAL: R$ <valor>

AUTO-ATAQUE (Etapa 5):
   - Fragilidade 1: <descricao + mitigacao>
   - Fragilidade 2: ...

OBSERVACOES:
   - <decadencia/prescricao verificada>
   - <Sumula aplicavel>
```

**Skill a acionar:** `previdenciario-master` + `calculo-rmi` (ou skill especifica).
