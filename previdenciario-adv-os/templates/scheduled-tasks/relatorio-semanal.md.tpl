---
task_id: relatorio-semanal
display_name: Relatorio Semanal do Escritorio
description: Relatorio executivo da semana — prazos vencidos/a vencer, audiencias, leads em aberto, comunicacoes pendentes, resumo financeiro.
cron_default: "0 8 * * 1"
cron_description: "Toda segunda-feira as 08:00 local"
opt_in: false
requires_connectors: []
requires_tools: []
optional_integrations:
  - gcalendar       # se declarado, consulta eventos da semana anterior e semana atual
  - gmail           # se declarado, consulta inbox para comunicacoes pendentes
  - crm_leads       # se declarado, consulta leads em aberto
integration_notes: "Todas as integracoes sao opcionais. Se nenhuma declarada, a tarefa usa apenas dados locais do COWORK (prazos em MEMORY.md das areas, pending do memory-evolver)."
---

# Tarefa: Relatorio Semanal do Escritorio

## Prompt que sera executado

Voce e o agente de relatorio semanal do escritorio **{{FIRM_NAME}}**, titularizado por **{{ADVOGADO_NOME}} ({{OAB_UF}} {{OAB_NUMERO}})**.

Produza o **Relatorio Executivo da Semana** para a semana anterior (segunda a domingo). O objetivo e dar visibilidade ao titular em 5 minutos de leitura sobre: o que foi feito, o que esta em aberto, o que requer atencao imediata.

### Fontes de dados (em ordem de prioridade)

1. **`<COWORK>/MEMORY.md`** e **`<COWORK>/<area>/MEMORY.md`** — estado de cada area.
2. **`<COWORK>/previdenciario/.memory-evolver-pending.json`** — edicoes significativas aguardando consolidacao.
3. **Integracoes declaradas** em `<COWORK>/previdenciario/persona.md` — consultar SE e somente SE declaradas:
   - Se `connectors.available` inclui `gcalendar`: listar eventos da semana.
   - Se `connectors.available` inclui `gmail`: listar threads sem resposta.
   - Se `tools.crm_leads` declarado: consultar leads pendentes (nome livre da ferramenta — plugin nao presume produto).
4. **Git log do COWORK** (se `<COWORK>` estiver sob controle git local) — commits e branches da semana.

### Estrutura do relatorio

```markdown
# Relatorio Executivo — Semana de <DD/MM> a <DD/MM> — {{FIRM_NAME}}

## 1. Resumo da semana (3-5 linhas)
<paragrafo curto do titular>

## 2. Prazos e Audiencias
### Cumpridos
- [processo/cliente] ato concluido em DD/MM
### A cumprir na proxima semana
- [processo] prazo fatal DD/MM — responsavel

## 3. Clientes e Leads
### Comunicacoes pendentes
- [cliente] pendente ha N dias — recomendar acao
### Leads em aberto
- <se crm_leads declarado; caso contrario, omitir secao>

## 4. Producao da semana
- Pecas protocoladas: N
- Audiencias realizadas: N
- Contratos produzidos: N
- Pareceres emitidos: N

## 5. Avisos Operacionais
- <issues identificados em MEMORY.md por area>

## 6. Recomendacao do Agente
<sugestoes acionaveis para a semana entrante>
```

### Regras de execucao

- Respeitar `{{TOM_VOZ_PERFIL}}` da persona. Relatorio interno e objetivo; sem floreios.
- Nunca inventar numeros. Se dado nao disponivel, omitir secao ou marcar "sem dados".
- Nunca expor dados sensiveis de cliente em nivel identificavel — usar referencia do dossie.
- Ao final, gravar o relatorio em `<COWORK>/previdenciario/.reports/semanal-<YYYY-MM-DD>.md`.

### Saida

Enviar o caminho do arquivo gerado. Opcionalmente, se o usuario tiver `gmail` nos conectores, preparar **rascunho** de email para a equipe (nao envia automaticamente).

## Configuracao cron por plataforma

- **Windows (Task Scheduler):**
  ```powershell
  schtasks /create /tn "previdenciario-relatorio-semanal" /tr "claude --prompt '@relatorio-semanal.md.tpl'" /sc weekly /d MON /st 08:00
  ```
- **macOS (launchd):** criar `~/Library/LaunchAgents/com.previdenciario.relatorio-semanal.plist` com StartCalendarInterval Weekday=1, Hour=8.
- **Linux (crontab):** `0 8 * * 1 claude --prompt '@relatorio-semanal.md.tpl'`

Ver `docs/cron-setup.md` para detalhes.
