---
description: Orquestra producao de recurso previdenciario. Identifica instancia automaticamente pelo contexto. Aciona analise da decisao recorrida + skill recursal + Suprema Corte.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
argument-hint: [instancia opcional: jef | trf | resp | re | pedilef | crps]
---

Voce foi acionado pelo comando `/recurso-previdenciario` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** produzir recurso previdenciario na instancia correta com governance completa.

## PROTOCOLO DE EXECUCAO

### 1. Verificar plugin ativo

`previdenciario/cowork-state.json` existe? Se nao, sugerir `/start-previdenciario`.

### 2. Identificar instancia recursal

Se argumento fornecido, usar. Caso contrario, analisar contexto:
- Decisao do JEF? → Recurso a Turma Recursal (JEF)
- Sentenca de Vara Federal? → Apelacao ao TRF
- Acordao de Turma Recursal? → REsp (se materia constitucional → RE)
- Acordao de TRF? → REsp / RE / Embargos de Divergencia
- Acordao da Turma Recursal divergente de outra? → PEDILEF (TNU)
- Decisao do INSS administrativa? → Recurso a Junta de Recursos (CRPS)
- Decisao da Junta de Recursos? → Recurso as Camaras de Julgamento (CRPS)

Se ambiguo, perguntar ao operador.

### 3. Analise da decisao recorrida

Pedir ao operador (se nao anexada):
- Texto integral da decisao
- Numero do processo
- Tribunal/Vara/Turma
- Data de publicacao (para tempestividade)
- Argumentos da decisao a serem combatidos

### 4. Cadeia de skills

```
1. analise-carta-concessao-indeferimento (Tier 2 C)
   [se for recurso administrativo contra INSS]

2. triagem-dogmatica-previdenciario (Tier 1)

3. analise-trilateral-previdenciario (Tier 1)

4. jurisprudencia-estrategica-previdenciario (Tier 1)
   → especial atencao a Temas Repetitivos STJ + Repercussao Geral STF
   → se REsp: aplicar Filtro Anti-Sumula 7 (PA-16)
   → se PEDILEF: divergencia entre Turmas Recursais

5. skill recursal cabivel (Tier 2 A ou B):
   - recurso-jef-previdenciario
   - apelacao-previdenciaria-trf
   - recurso-especial-previdenciario
   - recurso-extraordinario-previdenciario
   - pedilef-tnu
   - embargos-declaracao-previdenciario
   - contrarrazoes-previdenciarias
   - recurso-junta-recursos-crps
   - recurso-camaras-julgamento-crps

6. Transversais (estilo + visual-law)

7. suprema-corte-previdenciario (R1-R4)
```

### 5. Atencao especial — REsp

Se for Recurso Especial:
- **PA-16 obrigatorio** — Filtro Anti-Sumula 7
- A controversia precisa ser de DIREITO, nao reexame fatico
- Demonstrar prequestionamento explicito do dispositivo
- Indicar Tema repetitivo aplicavel (se houver)

### 6. Atencao especial — REsp/RE em previdenciario

Temas relevantes (verificar Nivel 1 com dados completos):
- Tema 1102 STF (vida toda)
- Tema 350 STF (RE 631.240 — previo requerimento administrativo)
- Tema 416 STJ (necessidade de pericia oficial)
- Tema 503 STF (desaposentacao)
- Tema 692 STF (revisao da vida toda)
- Tema 999 STJ (decadencia art. 103)

Se nao confirmar Nivel 1, classificar Nivel 2 com `[VERIFICAR]`.

### 7. Tempestividade

Conferir prazo recursal aplicavel:
- JEF: 10 dias (art. 5o Lei 10.259/2001)
- Apelacao TRF: 15 dias (art. 1.003 §5o CPC)
- REsp/RE: 15 dias
- PEDILEF: 10 dias
- Recurso administrativo INSS: 30 dias (art. 305 IN 128/2022)

**Skill a acionar:** `previdenciario-master` + skill recursal cabivel.
