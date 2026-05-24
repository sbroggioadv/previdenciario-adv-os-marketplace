---
name: calculos-previdenciarios
description: >
  CALCULOS PREVIDENCIARIOS — Skill consolidada que cobre tempo de contribuicao, RMI (Renda Mensal Inicial) e liquidacao de sentenca. Aplica Protocolo 2.4 INTEGRAL (5 etapas: mapear regime + apurar tempo/carencia + salario-de-beneficio + memoria detalhada + auto-ataque). Cobre regras pre-Lei 13.846/2019, pos-Lei 13.846, regras de transicao EC 103/2019 (pedagio 50%, pedagio 100%, pontos, idade minima progressiva, professores), Tema 1102 STF (vida toda), Tema 1041 STJ (conversao especial pos-EC 103), liquidacao com IPCA-E ate 12/2021 + SELIC pos (Lei 14.439/2022), Sumula 111 STJ (honorarios), RPV vs precatorio (Lei 10.259/2001 art. 17). Use para qualquer calculo previdenciario.
---

# CALCULOS PREVIDENCIARIOS — Skill Tier 2 D (consolidada)

> Aplica Protocolo 2.4 integral. **PA-20:** sem dado, parar — nunca estimar silenciosamente.

---

## 1. PROTOCOLO 2.4 — 5 ETAPAS

### Etapa 1 — Mapear regime e marco temporal
- Regime: RGPS / RPPS / Complementar (PA-06 — nao misturar)
- Data de filiacao do segurado
- DER, DIB, DCB
- Regra aplicavel: pre-EC 103/2019? regra de transicao? regra permanente?

### Etapa 2 — Apurar tempo + carencia (separadamente)
- Tempo bruto + tempo especial convertido + concomitancia + tempo rural + justificacao
- Carencia (meses com contribuicao OK) — separadamente do tempo

### Etapa 3 — Salario-de-beneficio + RMI
- Aplicar regra correta (Secao 2 desta skill)
- Aplicar fator previdenciario se cabivel
- Aplicar coeficiente

### Etapa 4 — Memoria de calculo detalhada
- Fundamento legal de cada parcela
- Base de calculo com valor utilizado
- Indices de correcao (IPCA-E ate 12/2021, SELIC apos)
- Juros conforme decisao
- Subtotais e total geral

### Etapa 5 — Auto-ataque (assumir papel da PFE/INSS)
- Algum salario fora do PBC?
- Indice de correcao incorreto?
- Fator previdenciario aplicavel mesmo?
- Regra de transicao mais benefica preterida?
- Compensacao com pagamentos administrativos?

---

## 2. CALCULO DE TEMPO DE CONTRIBUICAO

### 2.1 Tempo bruto

Para cada vinculo do CNIS:
- Tempo = data fim - data inicio
- Em meses (com casas decimais)

### 2.2 Tempo especial convertido

Apos analise PPP/LTCAT:
- Tempo especial × fator = tempo comum equivalente
- Fatores: Homem 1.4, Mulher 1.2

**Tema 1041 STJ pos-EC 103/2019:**
- Filiacao pre-EC 103 -> conversao OK
- Filiacao pos-EC 103 -> aposentadoria especial direta (sem conversao)

### 2.3 Concomitancia

Sobreposicao de vinculos:
- Tempo NAO se duplica
- Subtrair de um dos vinculos (manter o que oferece melhor calculo)
- Aplicar art. 32 Decreto 3.048/99

### 2.4 Tempo rural

Pre-11/1991: inicio de prova material + testemunhas. Computa para tempo, NAO para carencia.
Pos-11/1991: contribuicao OU comprovacao especifica. Pode computar para carencia (segurado especial).

### 2.5 Carencia (separadamente)

```
Lei 8.213/91 art. 24:
  Aposentadoria por idade: 180 meses
  BPI / aposentadoria por incapacidade: 12 meses (com excecoes art. 26)
  Pensao por morte (Lei 13.135/15): 18 contribuicoes
  Salario-maternidade: 10 (segurada especial / individual)
  BPC: NAO exige carencia (Lei 8.742/93)
```

Cada competencia com contribuicao OK = 1 mes de carencia.

---

## 3. CALCULO DE RMI

### 3.1 Evolucao das regras

| Periodo | PBC | Salario-de-beneficio | Fator | Coeficiente |
|---------|-----|---------------------|-------|-------------|
| Pre-Lei 9.876/99 | 36 ultimas contribuicoes | media | n/a | conforme regra |
| Lei 9.876/99 (1999) ate Lei 13.846/2019 (07/2019) | 07/1994 a DIB | media dos **80% maiores SC** | aplicado em algumas | conforme regra |
| Lei 13.846/2019 ate EC 103/2019 (11/2019) | 07/1994 a DIB | media de **100% das contribuicoes** | mesmo | conforme regra |
| EC 103/2019 (regra permanente) | TODAS as contribuicoes desde 07/1994 | media simples | n/a (nem fator) | 60% + 2% por ano alem de 20 (H) ou 15 (M) |

### 3.2 Regras de transicao EC 103/2019

| Regra | Tempo necessario | Idade minima | Pedagio | Calculo |
|-------|------------------|--------------|---------|---------|
| Pedagio 50% (faltava ate 2 anos) | original + 50% sobre faltante | (variavel) | 50% sobre tempo faltante | 60% + 2% por ano alem de 20 |
| Pedagio 100% | original + 100% sobre faltante | (variavel) | 100% sobre faltante | media salarial integral |
| Pontos | tempo + idade = pontuacao progressiva (105/100) | n/a | n/a | media + redutor |
| Idade minima progressiva | tempo + idade minima crescente | progressao anual | n/a | 60% + 2% por ano alem de 20 |
| Professores | reducao de 5 anos sobre tempo/idade | conforme | conforme | conforme regra escolhida |

**PA-08:** analisar TODAS as 5 regras de transicao e indicar a MAIS BENEFICA ao segurado.

### 3.3 Fator previdenciario

Formula: `f = (Tc × a) / Es × [1 + (Id + Tc × a) / 100]`

Onde:
- Tc = tempo de contribuicao
- a = aliquota (0.31)
- Es = expectativa de sobrevida (tabela IBGE)
- Id = idade

**Aplicacao:** apenas em alguns casos (aposentadoria por tempo na regra anterior, opcionalmente).

### 3.4 Tema 1102 STF — Vida toda

Para beneficios concedidos pre-Lei 9.876/99 com PBC restritivo, possibilidade de incluir salarios pre-julho/1994 no calculo.

**Atencao modulacao:** verificar acordao atualizado.

### 3.5 Calculo passo-a-passo

```
1. Identificar regra aplicavel (Secao 3.1 + 3.2)
2. Listar PBC (CNIS)
3. Corrigir salarios por competencia
4. Calcular media (80% ou 100% ou simples conforme regra)
5. Aplicar fator previdenciario (se cabivel)
6. Aplicar coeficiente (% sobre SB = RMI)
7. Comparar com piso (1 SM) e teto previdenciario
```

---

## 4. LIQUIDACAO DE SENTENCA

### 4.1 Periodo

DIB ate data da liquidacao.

### 4.2 Parcelas vencidas mes a mes

Aplicar reajuste anual (Lei 8.213/91 art. 41-A).

### 4.3 Correcao monetaria

```
IPCA-E: jun/2009 ate 12/2021 (Tema 905 STJ)
SELIC: 01/2022 em diante (Lei 14.439/2022 — substitui IPCA-E + juros)
Pre-jun/2009: variacao conforme entendimento jurisprudencial vigente
```

### 4.4 Juros

Pre-2022 (IPCA-E): juros separados (ex: 0.5% am ou taxa basica)
Pos-2022 (SELIC): juros JA INCLUSOS (nao acumular)

### 4.5 Honorarios sucumbenciais

```
Sumula 111 STJ:
  Honorarios em previdenciario incidem APENAS sobre as prestacoes
  VENCIDAS ATE A SENTENCA, NAO sobre as vincendas.
```

### 4.6 Custas

Sumula 105 STJ — custas pelo INSS.

### 4.7 RPV vs Precatorio

```
Lei 10.259/2001 art. 17:
  Limite RPV = 60 SM × <SM atual>

Total <= limite -> RPV (~60 dias)
Total > limite -> precatorio (proximo ciclo)

Cisao possivel: renunciar excedente para RPV.
```

---

## 5. RELATORIO FINAL

```
═══════════════════════════════════════════════════
CALCULO PREVIDENCIARIO — RELATORIO
═══════════════════════════════════════════════════

SEGURADO: <nome> (NIT)
TIPO: <tempo / RMI / liquidacao / comparativo>
REGIME: <RGPS / RPPS / Complementar>

ETAPA 1 — REGIME E MARCO TEMPORAL
   Filiacao: <data>
   Regra aplicavel: <descrever>

ETAPA 2 — TEMPO + CARENCIA
   Tempo bruto: <X> anos, <Y> meses
   Tempo especial convertido: <X>
   Tempo rural: <X>
   TEMPO TOTAL: <X> anos, <Y> meses
   Carencia (meses): <N> / <M> exigidos -> ATENDE / NAO ATENDE

ETAPA 3 — SALARIO-DE-BENEFICIO + RMI
   PBC: <inicio> a <fim>
   Total contribuicoes: <N>
   Salario-de-beneficio: R$ <SB>
   Fator previdenciario: <fator ou n/a>
   Coeficiente: <%>
   RMI: R$ <valor>

ETAPA 4 — MEMORIA DETALHADA
   <tabela mes a mes com indice + correcao>

ETAPA 5 — AUTO-ATAQUE
   - Verificacao 1: <descricao>
   - Verificacao 2: <descricao>
   - Fragilidades detectadas: <listar>

LIQUIDACAO (se cabivel):
   Parcelas vencidas: R$ <X>
   Correcao IPCA-E + SELIC: R$ <Y>
   Juros (pre-2022): R$ <Z>
   Honorarios (Sumula 111): R$ <W>
   TOTAL: R$ <total>

   Via: RPV (<= R$ <limite>) / PRECATORIO (> R$ <limite>) / RPV com cisao

PONTOS DE OMISSAO (PA-20):
   - <listar lacunas>
═══════════════════════════════════════════════════
```

---

## 6. PAS APLICAVEIS

- **PA-03** — sem invencao de valores
- **PA-06** — nao misturar regimes
- **PA-07** — nao aplicar EC 103 retroativamente
- **PA-08** — todas as 5 regras de transicao
- **PA-13** — sem CNIS, paralisar
- **PA-20** — sem dado, sinalizar e parar
- **PA-22** — Suprema Corte

---

## 7. PROTOCOLOS ACIONADOS

- **2.4** Calculos integral (Etapas 1 a 5)
- **2.1** Jurisprudencial (Tema 1102 STF, Tema 1041 STJ, Tema 999 STJ, Sumula 111 STJ)

---

*Skill calculos unificada. Cobre tempo + RMI + liquidacao.*
