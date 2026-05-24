---
task_id: meeting-triage
display_name: Triagem de Reunioes (Transcricao LOCAL)
description: Monitora pasta de transcricoes e produz resumo + tarefas derivadas para cada reuniao nova. EXIGE transcricao local (nunca cloud) para respeitar sigilo profissional.
cron_default: "*/30 * * * *"
cron_description: "A cada 30 minutos (ou manualmente)"
opt_in: true
opt_in_reason: "Toca dados de reunioes com clientes. Exige transcritor LOCAL declarado em tools.transcricao_reunioes. Proibe explicitamente transcricao cloud."
requires_tools:
  - transcricao_reunioes      # obrigatorio — deve ser solucao local (whisper local, etc)
warning_lgpd: "SIGILO PROFISSIONAL. Reunioes com clientes contem dados sob segredo profissional (CPC art. 388 + Codigo de Etica da OAB). Esta tarefa EXIGE transcricao local — nunca aceitar solucao cloud mesmo se declarada."
---

# Tarefa: Triagem de Reunioes (Transcricao Local)

## Prompt que sera executado

**⚠️ Pre-check obrigatorio:**

1. Ler `tools.transcricao_reunioes` da persona. Se nao declarado:
   ```
   [meeting-triage] Abortado: nenhum transcritor declarado.
   Para habilitar: declare em tools.transcricao_reunioes uma solucao LOCAL (ex: whisper-local, Apple Voice Memos + whisper). Nunca use solucao cloud.
   ```
2. Avaliar se a solucao declarada e cloud (heuristica por nome do produto comum). Se parecer cloud, emitir aviso e aguardar confirmacao explicita do usuario via `/cowork-set preferences.transcricao_e_local true`. Se usuario confirmou `false` ou nao confirmou, abortar.

### Prompt principal

Voce e o agente de triagem pos-reuniao do escritorio **{{FIRM_NAME}}**.

Sua tarefa:

1. Monitorar a pasta de transcricoes declarada em persona (campo livre — por convencao, `<COWORK>/_transcricoes/` se nao especificado).
2. Listar arquivos `.txt` / `.md` novos nas ultimas N execucoes (manter log em `<COWORK>/previdenciario/.hook-state.json` campo `meeting-triage.processed_files`).
3. Para cada transcricao nova, acionar a skill `resumo-audiencia` (ja existente — e generalista para reunioes tambem) com a instrucao:
   > "Produzir ata estruturada da reuniao: cabecalho, cronologia, pontos controversos, decisoes, proximos passos, responsaveis, prazos. Tom profissional."
4. Salvar a ata em `<COWORK>/<area>/Reunioes/ata-<YYYY-MM-DD>-<participantes-resumo>.md`.
5. Extrair tarefas derivadas e:
   - Adicionar como entrada em MEMORY.md da area.
   - Se `tools.tarefas_projetos` declarado, preparar rascunho de criacao (nunca criar automaticamente sem confirmacao manual do titular).

### Regras LGPD e sigilo profissional

- **Transcricao cloud proibida.** Se detectar que a solucao e cloud, abortar sempre.
- Nunca copiar transcricao para fora do COWORK.
- `<COWORK>/_transcricoes/` DEVE estar em `.gitignore` (conferir).
- A ata gerada respeita o perfil `{{TOM_VOZ_PERFIL}}` mas sempre em tom profissional-objetivo.
- Se a reuniao contem dados sensiveis (saude, orientacao sexual, etc — art. 5 II LGPD), marcar ata com nota de confidencialidade reforcada.

## Configuracao cron

- **Windows (a cada 30min):** `schtasks /create /tn "previdenciario-meeting" /tr "..." /sc minute /mo 30`
- **macOS:** launchd StartInterval=1800.
- **Linux:** `*/30 * * * * ...`

### Alternativa: watch manual

Se preferir, pode-se executar manualmente apos cada reuniao via `/cowork-run-task meeting-triage`.
