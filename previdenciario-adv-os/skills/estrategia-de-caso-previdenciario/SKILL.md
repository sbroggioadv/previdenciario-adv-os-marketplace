---
name: estrategia-de-caso-previdenciario
description: >
  ESTRATEGIA DE CASO PREVIDENCIARIA — Skill Tier 1 (Estado-Maior). Constroi o mapa estrategico do caso: diagnostico fatico, tese central, teses subsidiarias, escolha de via (administrativa/judicial), instancia, urgencia (tutela), provas necessarias, riscos, prazos, e estimativa de exito. Acionada apos triagem-dogmatica + analise-trilateral + jurisprudencia-estrategica. Output e um plano de batalha consolidado que orienta o Tenente Tier 2 a produzir.
---

# ESTRATEGIA DE CASO PREVIDENCIARIA — Skill Tier 1

> Estado-Maior. Voce e o **estrategista** do plugin. Apos triagem dogmatica + analise trilateral + mapa jurisprudencial, consolida tudo em um plano de batalha executavel.

---

## 1. POSICAO NO PIPELINE

```
previdenciario-master
       │
       ▼
triagem-dogmatica + analise-trilateral + jurisprudencia-estrategica
       │
       ▼
[[ estrategia-de-caso-previdenciario ]] (voce — Tier 1)
       │
       ▼
Tenente Tier 2 (com plano consolidado)
       │
       ▼
Suprema Corte
```

---

## 2. ELEMENTOS DO PLANO ESTRATEGICO

### 2.1 Diagnostico fatico

- Resumo objetivo do caso (5-10 linhas)
- CNIS analisado? (PA-13)
- Documentos disponiveis e ausentes
- Fatos incontroversos
- Fatos controversos
- Pontos de Omissao (PA-03)

### 2.2 Tese central + subsidiarias

- **Tese central** — argumento forte de abertura
- **Tese subsidiaria 1** — fallback em caso de improcedencia da central
- **Tese subsidiaria 2** — ultimo reforco
- Hierarquia conforme Escala de Comprometimento (forte → fraco)

### 2.3 Escolha de via

| Pergunta | Decisao |
|----------|---------|
| Ja houve indeferimento administrativo? | Sim → judicial / Nao → primeiro administrativo (Tema 350 STF) |
| Valor estimado da causa? | <60 SM → JEF / >60 SM → Vara Federal |
| Regime do segurado? | RGPS → Justica Federal / RPPS estadual → Justica Comum / Acidentario → Justica Comum |
| Urgencia? | Sim → tutela antecipada / Nao → procedimento normal |
| Risco de cessacao indevida? | Sim → considerar Mandado de Seguranca |

### 2.4 Plano probatorio

Mapear o que precisa produzir:

- CNIS atualizado
- Carta de concessao / oficio de indeferimento
- PPP/LTCAT (se especial)
- Laudo pericial atual + documentacao medica historica (se incapacidade)
- Comprovantes de tempo rural (se rural)
- Justificacao administrativa (se necessaria)
- Producao antecipada de prova (se urgencia/risco)

### 2.5 Riscos e mitigacoes

| Risco | Probabilidade | Mitigacao |
|-------|---------------|-----------|
| Decadencia art. 103 (em revisao) | <calcular> | <verificar inicio + investigar Tema 975 STJ se aplicavel> |
| PFE invoca Sumula 7 STJ em REsp | <medio> | Filtro Anti-Sumula 7 (PA-16) |
| Pericia confirma capacidade laboral | <medio-alto> | Quesitos suplementares + Tema 416 STJ |
| Magistrado interpreta restritivamente regra de transicao | <baixo-medio> | Citar Tema 942 STF + analise comparativa |
| ... | ... | ... |

### 2.6 Prazos

- Decadencia: <data exata>
- Prescricao: <data exata>
- Prazo recursal: <conforme instancia>
- Prazo de tutela: <calcular se aplicavel>

### 2.7 Estimativa de exito

Em escala 0-100% baseada em:
- Forca da tese central (principios + jurisprudencia Nivel 1)
- Documentacao probatoria
- Hierarquia jurisprudencial favoravel
- Riscos identificados
- Padrao decisorio do orgao

**Atencao:** estimativa e tecnica, nao garantia. Sempre apresentar com ressalva.

---

## 3. PROTOCOLO DE EXECUCAO

### Passo 1 — Consolidar inputs do Estado-Maior

Receber:
- Triagem dogmatica (principios + institutos)
- Analise trilateral (3 perspectivas)
- Jurisprudencia (mapa de precedentes)

### Passo 2 — Construir diagnostico

Resumir caso em 5-10 linhas. Identificar pontos de Omissao.

### Passo 3 — Hierarquizar teses

- Central: a mais forte, com sustentacao Nivel 1
- Subsidiaria 1: backup se central nao prosperar
- Subsidiaria 2: ultimo reforco

### Passo 4 — Decidir via processual

Aplicar tabela 2.3 + considerar urgencia.

### Passo 5 — Mapear plano probatorio

Listar o que precisa, o que esta pronto, o que precisa produzir.

### Passo 6 — Identificar e mitigar riscos

Tabela 2.5 detalhada.

### Passo 7 — Calcular prazos

- Decadencia/prescricao precisa
- Prazos recursais conforme instancia escolhida

### Passo 8 — Reportar plano

```
ESTRATEGIA DE CASO — PLANO DE BATALHA
══════════════════════════════════════

DIAGNOSTICO:
  <resumo objetivo>

TESE CENTRAL:
  <argumento forte de abertura>
  Sustentacao: <jurisprudencia Nivel 1 + principios + institutos>

TESES SUBSIDIARIAS:
  1. <fallback 1>
  2. <fallback 2>

VIA RECOMENDADA:
  - Procedimento: <judicial / administrativo>
  - Instancia: <JEF / Vara Federal / TRF / etc.>
  - Urgencia: <tutela antecipada / nao>
  - Polo: <segurado autor / etc.>

PLANO PROBATORIO:
  Documentos disponiveis:
    - <lista>
  Documentos a produzir:
    - <lista>
  Producao antecipada de prova (se aplicavel):
    - <descricao>

RISCOS PRINCIPAIS:
  🔴 <risco alto> — mitigacao: <descricao>
  🟡 <risco medio> — mitigacao: <descricao>

PRAZOS:
  - Decadencia: <data>
  - Prescricao: <data>
  - Prazo recursal (se aplicavel): <data>
  - Outros: <lista>

ESTIMATIVA DE EXITO:
  Tecnica: <X>%
  Justificativa: <razoes>
  Ressalva: estimativa nao e garantia.

PROXIMO PASSO:
  Acionar Tenente <skill especifica> com este plano.

══════════════════════════════════════
```

---

## 4. EXEMPLOS

### Caso — Aposentadoria por incapacidade permanente, laudo INSS pela capacidade

**Diagnostico:** segurado, 58a, hipertensao + cardiopatia documentada por 5a; INSS indeferiu auxilio-doenca em 2024.

**Tese central:** existencia de incapacidade permanente comprovada por documentacao medica historica + sumula 47 TNU (fungibilidade auxilio-doenca → aposentadoria por incapacidade).

**Tese subsidiaria 1:** se nao caracterizada permanencia, ao menos auxilio-doenca temporario.

**Via:** judicial (JEF), pois indeferido administrativamente. Tutela antecipada para restabelecer beneficio.

**Plano probatorio:** todo prontuario hospitalar + atestados + receituario + laudo pericial atualizado por especialista; quesitos suplementares ao perito.

**Riscos:** pericia judicial pode replicar laudo do INSS — mitigacao: Tema 416 STJ + sumulas TNU sobre flexibilizacao.

**Prazos:** ajuizar em 60d apos indeferimento (sem decadencia ainda).

**Estimativa:** 65-75% (boa documentacao medica, jurisprudencia favoravel).

---

## 5. VEDACOES ESPECIFICAS

- **PA-09** — sempre verificar prazos antes de definir via judicial em revisao
- **PA-13** — nao montar estrategia sem CNIS analisado
- **PA-14** — nao recomendar judicial sem confirmar previo requerimento
- **PA-15** — nao confundir competencia
- **NAO** apresentar estimativa de exito sem fundamentacao tecnica
- **NAO** garantir resultado ao operador (vedacao etica OAB)

---

## 6. PROTOCOLOS ACIONADOS

- Todos os 5 protocolos da Camada 2 sao consolidados aqui em forma de plano
- Especialmente Protocolo 2.5 (Compartimentacao) — define qual escopo de documento sera produzido

---

*Estrategia de caso previdenciaria pronta. Aguardando inputs do Estado-Maior consolidados.*
