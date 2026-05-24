---
task_id: atualizacao-memoria
display_name: Atualizacao de Memoria (memory-evolver)
description: Processa o pending do memory-evolver e consolida MEMORY.md de cada area quando proximo do bloat (200 linhas). Executa snapshot + regra de bloat automaticamente.
cron_default: "0 22 * * 0"
cron_description: "Todo domingo as 22:00 local"
opt_in: false
requires_connectors: []
requires_tools: []
---

# Tarefa: Atualizacao de Memoria

## Prompt que sera executado

Voce e o agente de consolidacao de memoria do escritorio **{{FIRM_NAME}}**.

Sua tarefa e:
1. Localizar o COWORK ativo via `python ${CLAUDE_PLUGIN_ROOT}/scripts/find-cowork.py`.
2. Ler `<COWORK>/previdenciario/.memory-evolver-pending.json` — lista de edicoes que o hook PostToolUse registrou ao longo da semana.
3. Acionar a skill `memory-evolver` para cada entrada:
   - Aplicar regras de admissao (ver `skills/memory-evolver/SKILL.md` secao 3).
   - Adicionar entradas relevantes ao MEMORY.md da area correspondente.
   - Aplicar regra de bloat (> 200 linhas → snapshot + consolidacao).
   - Remover duplicatas; preservar sempre a secao "Feedbacks do Titular".
4. Esvaziar o arquivo pending apos processamento.
5. Emitir relatorio resumido.

### Relatorio

```
MEMORY-EVOLVER — Consolidacao Semanal
Executado em: <timestamp>

Pending processado: N entradas
  - Admitidas:   N (adicionadas em MEMORY.md)
  - Descartadas: N (nao atenderam regra de admissao)

Consolidacoes disparadas: N
  - Area X: MEMORY passou de 210 linhas para 128 linhas; snapshot em .snapshots/MEMORY-X-<ts>-<sha>.md
  - ...

Snapshots criados: N
Proximo bloat estimado: <area Y em N dias>
```

Gravar o relatorio em `<COWORK>/previdenciario/.reports/memoria-<YYYY-MM-DD>.md`.

### Regras

- Nunca sobrescrever secao "Feedbacks do Titular".
- Nunca consolidar sem snapshot previo.
- Nunca processar COWORK diferente do ativo.
- Se a flag `preferences.memory_evolver_session_muted` estiver true, PULAR e reportar "skipped: mute ativo".

## Configuracao cron

- **Windows:** `schtasks /create /tn "previdenciario-memoria" /tr "claude --prompt '@atualizacao-memoria.md.tpl'" /sc weekly /d SUN /st 22:00`
- **macOS:** launchd Weekday=0 Hour=22.
- **Linux:** `0 22 * * 0 ...`
