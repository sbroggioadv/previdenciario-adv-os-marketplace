---
task_id: dashboard-data-refresh
display_name: Refresh de Dashboards do Escritorio
description: Atualiza dashboards locais com dados derivados de MEMORY.md, logs de skills e ferramentas declaradas. Roda manualmente ou agendada.
cron_default: "0 7 * * *"
cron_description: "Todos os dias as 07:00 local (ou manualmente via /cowork-run-task dashboard-data-refresh)"
opt_in: true
opt_in_reason: "Util para escritorios que mantem dashboard interno. Mentorados sem dashboard podem pular."
requires_connectors: []
requires_tools: []
integration_notes: "Se `tools.gestao_processual` ou `tools.crm_leads` estiverem declarados, a tarefa sugere como extrair dados via API/export manual — nao faz integracao automatica sem declaracao explicita."
---

# Tarefa: Refresh de Dashboards

## Prompt que sera executado

Voce e o agente de refresh dos dashboards do escritorio **{{FIRM_NAME}}**.

Sua tarefa:

1. Localizar COWORK.
2. Verificar se existe `<COWORK>/dashboards/` — se nao existir, criar + emitir aviso "dashboards/ inicializado. Adicione seus dashboards em .md ou .csv."
3. Consolidar dados das ultimas 24h em arquivos-fonte:
   - `<COWORK>/dashboards/_data/prazos.csv` — prazos extraidos dos MEMORY.md por area (formato: cliente, processo, data_fatal, status).
   - `<COWORK>/dashboards/_data/skills-usage.csv` — agregado do `.skills-log/`.
   - `<COWORK>/dashboards/_data/recebiveis.csv` — se existir pasta `<COWORK>/_financeiro/`, agregar.
4. Gerar/atualizar o dashboard principal em `<COWORK>/dashboards/dashboard-principal.md`:
   ```markdown
   # Dashboard — {{FIRM_NAME}}
   > Atualizado em: <timestamp>

   ## Prazos Criticos (proximos 7 dias)
   | Cliente | Processo | Prazo | Status |

   ## Leads em aberto
   <so se tools.crm_leads declarado>

   ## Uso de skills (24h)
   <top 5>

   ## Recebiveis (resumo)
   <so se financeiro_juridico ativo + dados locais>
   ```
5. Se `connectors.available` inclui `gsheets`, oferecer rascunho de sync para uma planilha Google (nunca fazer upload automatico).

### Regras

- Nao ler arquivo fora do COWORK.
- Nao vazar nome de cliente em arquivo agregado sem anonimizacao (usar "cliente X" em dashboards).
- Se o mentorado declarou ferramentas externas ([sistema de gestao processual] equivalente, CRM equivalente), orientar como **extrair manualmente** os dados — nunca pressumir API.

## Configuracao cron

- **Windows:** `schtasks /create /tn "previdenciario-dashboard" /tr "..." /sc daily /st 07:00`
- **macOS:** launchd Hour=7 diario.
- **Linux:** `0 7 * * * ...`
