---
name: analise-carta-concessao-indeferimento
description: >
  ANALISE DE CARTA DE CONCESSAO / INDEFERIMENTO — Skill Tier 2 C. Le e diagnostica documento administrativo do INSS (carta de concessao com calculo da RMI ou oficio de indeferimento com fundamentos da negativa). Output: extracao estruturada (DIB, RMI, especie, fundamentos, base de calculo) + diagnostico de erros + sugestao de via (revisao administrativa, recurso CRPS, acao judicial). Acionada apos receber documento administrativo. PA-14 — sem este documento (oficio de indeferimento), nao se ajuiza acao judicial (Tema 350 STF).
---

# ANALISE DE CARTA DE CONCESSAO / INDEFERIMENTO — Skill Tier 2 C

> Le o ato administrativo do INSS, extrai dados, identifica erros, sugere via.

---

## 1. CARTA DE CONCESSAO — DADOS A EXTRAIR

```
CABECALHO:
- NIT do segurado
- Numero do beneficio (NB)
- Especie SAB (41, 42, 91, 32, 21, 87, 88, etc.)

DATAS:
- DER (Data de Entrada do Requerimento)
- DIB (Data de Inicio do Beneficio)
- DIP (Data de Inicio do Pagamento)
- DCB (Data de Cessacao, se aplicavel)

CALCULO:
- PBC (Periodo Basico de Calculo): inicio e fim
- Salarios-de-contribuicao utilizados
- Salario-de-beneficio
- Fator previdenciario aplicado (se houver)
- RMI (Renda Mensal Inicial)

ENQUADRAMENTO:
- Regra aplicada (anterior a EC 103/2019? regra de transicao? qual?)
- Fundamento legal (art. da Lei 8.213/91)
- Tempo de contribuicao computado
- Carencia computada
```

---

## 2. OFICIO DE INDEFERIMENTO — DADOS A EXTRAIR

```
CABECALHO:
- NIT
- DER
- Especie pleiteada

FUNDAMENTOS DA NEGATIVA (reproduzir literalmente):
- Tempo insuficiente?
- Carencia nao atendida?
- Idade insuficiente?
- Ausencia de incapacidade (em BPI)?
- Renda familiar acima do limite (em BPC)?
- Documentacao incompleta?
- Outros?

PROVAS NECESSARIAS PARA CONTESTAR:
- Conforme fundamento da negativa
```

---

## 3. ERROS COMUNS NA CARTA DE CONCESSAO

| Erro | Como detectar | Estrategia |
|------|---------------|------------|
| PBC incorreto | Confrontar com regra aplicavel a DIB | Revisao com calculo correto |
| Periodos nao computados | Confrontar com CNIS | Inclusao via revisao |
| Tempo especial nao reconhecido | Confrontar com PPP/LTCAT | Acao de reconhecimento + conversao |
| Fator previdenciario aplicado erroneamente | Verificar regra | Revisao |
| Indice de correcao errado | Conferir IPCA-E vs SELIC | Revisao |
| RMI menor que minimo legal | Verificar Lei 8.213/91 art. 33 | Revisao por garantia minimo |
| DIB equivocada (deveria ser anterior) | Verificar art. 49 + 54 | Revisao de DIB |

---

## 4. ERROS COMUNS EM OFICIO DE INDEFERIMENTO

| Argumento do INSS | Defesa |
|-------------------|--------|
| "Carencia nao atendida" | Verificar se ha tempo nao computado / vinculo PVI sanavel |
| "Tempo insuficiente" | Verificar tempo especial / rural / por equiparacao |
| "Ausencia de incapacidade" | Submeter laudo a Protocolo 2.3 + Tema 416 STJ |
| "Renda familiar acima" (BPC) | Tema 1023 STF — comprovacao in concreto + miserabilidade |
| "Documentacao incompleta" | Apresentar prova material + testemunhal |
| "Sem nexo causal" (acidentario) | NTEP + pericia tecnica especializada |

---

## 5. PROTOCOLO DE EXECUCAO

### Passo 1 — Identificar tipo do documento
Carta de concessao OU oficio de indeferimento.

### Passo 2 — Extrair dados estruturados
Conforme Secao 1 ou 2.

### Passo 3 — Confrontar
- Carta concessao: confrontar calculo com CNIS + regra aplicavel
- Oficio indeferimento: confrontar fundamentos da negativa com documentacao

### Passo 4 — Identificar erros / oportunidades
Conforme Secao 3 ou 4.

### Passo 5 — Sugerir via processual

| Caso | Via |
|------|-----|
| Concessao com erro de calculo dentro do prazo decadencial | Acao revisional (PA-09) |
| Concessao com erro grosseiro detectado em <60 dias | Reconsideracao administrativa (mais rapido) |
| Indeferimento, prazo administrativo aberto | Recurso a Junta de Recursos do CRPS (30d) |
| Indeferimento, prazo administrativo encerrado | Acao judicial direta |
| Indeferimento por mora administrativa | MS por mora |

### Passo 6 — Reportar

```
ANALISE DE DOCUMENTO ADMINISTRATIVO — RELATORIO
══════════════════════════════════════════════

TIPO: Carta de Concessao / Oficio de Indeferimento
DATA: <data>
SEGURADO: <nome>, NB <numero>

DADOS EXTRAIDOS:
  [tabela conforme tipo]

ERROS DETECTADOS:
  🔴 <erro grave> — fundamentar
  🟡 <erro moderado> — sustentar

OPORTUNIDADES (caso indeferimento):
  - <argumento de defesa 1>
  - <argumento de defesa 2>

VIA SUGERIDA:
  <revisao administrativa / CRPS / acao judicial / MS>

PROXIMO PASSO:
  Acionar skill <nome especifico — peticao-inicial-previdenciaria,
  recurso-junta-recursos-crps, acao-revisional-rmi, etc.>

══════════════════════════════════════════════
```

---

## 6. PAS APLICAVEIS

- **PA-03** — extracao fiel, sem invencao
- **PA-09** — em revisao, verificar decadencia
- **PA-13** — confronto com CNIS obrigatorio
- **PA-14** — oficio de indeferimento e prova essencial para Tema 350 STF

---

## 7. PROTOCOLOS ACIONADOS

- **2.4** Protocolo de Calculos (se carta de concessao com erro de calculo)

---

*Pronto.*
