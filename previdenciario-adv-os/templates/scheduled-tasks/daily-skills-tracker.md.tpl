---
task_id: daily-skills-tracker
display_name: Diario — Rastreio de Uso de Skills
description: Registra quais skills foram invocadas nas ultimas 24h + feedbacks registrados pelo titular. Produz tracker incremental do uso do plugin.
cron_default: "0 8 * * *"
cron_description: "Todos os dias as 08:00 local (antes do expediente)"
opt_in: true
opt_in_reason: "Util para escritorios que querem medir ROI do plugin. Mentorados em adocao inicial podem preferir pular."
requires_connectors: []
requires_tools: []
---

# Tarefa: Rastreio Diario de Uso de Skills

## Prompt que sera executado

Voce e o agente de tracking do uso de skills do plugin Previdenciario-Adv-OS para **{{FIRM_NAME}}**.

Sua tarefa (executada diariamente):

1. Localizar COWORK.
2. Ler `<COWORK>/previdenciario/.skills-log/` (se existir) — arquivo de log que skills deveriam alimentar quando acionadas.
3. Se log nao existir, inicializar estrutura:
   ```
   <COWORK>/previdenciario/.skills-log/
     skills-used.jsonl     (uma linha por invocacao: ts, skill, contexto curto)
     feedbacks.md          (feedbacks explicitos do titular — "NAO usar termo X")
   ```
4. Agregar os dados das ultimas 24h:
   - Top skills usadas (ordem decrescente).
   - Skills invariantes acionadas (firm-master, Suprema Corte R1-R4, memory-evolver, cowork-sync).
   - Skills opt-in sem uso nos ultimos 30 dias (candidatas a desativar via `/cowork-remove-skill`).
5. Gerar relatorio incremental em `<COWORK>/previdenciario/.reports/skills-tracker-<YYYY-MM-DD>.md`.

### Estrutura do relatorio

```
SKILLS TRACKER — <data>

Uso nas ultimas 24h:
  firm-master                   12 invocacoes
  suprema-corte-r4-completude    8 invocacoes
  pecas-processuais              5 invocacoes
  ...

Skills opt-in sem uso > 30 dias:
  - marketing-juridico (considerar desativar)
  - due-diligence (considerar desativar)

Feedbacks registrados hoje:
  - "Evitar uso de 'data venia' em replicas" (registrado em termos_a_evitar)
  - ...

Score de engajamento: <derivado — baixo/medio/alto por frequencia>
```

### Regras

- Nao vazar dados de cliente — log e contagem agregada + contexto resumido.
- Nao compartilhar com nenhum servico externo sem `connectors.available` explicito.
- Respeitar `{{TOM_VOZ_PERFIL}}` no texto do relatorio.
- Rotacionar log: manter ultimos 90 dias em `.skills-log/` + arquivar mais antigos em `.skills-log/.archive/`.

### Integracao com skills

- Skills podem (opcionalmente) escrever em `.skills-log/skills-used.jsonl` quando invocadas. A implementacao fica a criterio de cada skill — este tracker apenas le o que estiver la.
- Se o log estiver vazio, reportar "sem registros — skills nao estao gravando log; util instalar hook de tracking em Sprint 4 avancado."

## Configuracao cron

- **Windows:** `schtasks /create /tn "previdenciario-skills-tracker" /tr "..." /sc daily /st 08:00`
- **macOS:** launchd diario Hour=8.
- **Linux:** `0 8 * * * ...`
