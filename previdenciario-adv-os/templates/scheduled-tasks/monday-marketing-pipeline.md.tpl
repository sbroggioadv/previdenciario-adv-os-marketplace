---
task_id: monday-marketing-pipeline
display_name: Pipeline de Marketing (Segunda-feira)
description: Gera propostas de conteudo da semana baseadas nas areas ativas do escritorio. Util apenas se a skill opt-in `marketing-juridico` estiver ativa.
cron_default: "0 14 * * 1"
cron_description: "Toda segunda-feira as 14:00 local"
opt_in: true
opt_in_reason: "Depende da skill opt-in `marketing-juridico` estar ativa. Escritorios sem producao de conteudo podem pular."
requires_skills:
  - marketing-juridico
requires_connectors: []
requires_tools: []
---

# Tarefa: Pipeline de Marketing Semanal

## Prompt que sera executado

Voce e o agente de producao de conteudo do escritorio **{{FIRM_NAME}}** — **apenas se** a skill `marketing-juridico` estiver ativa em `state.json`.

### Pre-check

1. Localizar COWORK.
2. Verificar se `skills.opt_in_active` inclui `marketing-juridico`.
3. Se NAO incluir, abortar:
   ```
   [monday-marketing] Abortado: skill `marketing-juridico` nao esta ativa.
   Para ativar: /cowork-add-skill marketing-juridico
   ```
4. Se incluir, prosseguir.

### Prompt principal (quando skill ativa)

Delegar para a skill `marketing-juridico` com a instrucao:

> "Gere o **pipeline de conteudo da semana** para {{FIRM_NAME}}, cobrindo as areas ativas configuradas ({{AREAS_PRINCIPAIS}}). Produza:
>
> 1. **3 ideias de carrossel Instagram** (gancho + 3 bullets cada, respeitando Prov. 205/2021).
> 2. **1 thread LinkedIn** (7 posts, tom consultivo-assertivo conforme `{{TOM_VOZ_PERFIL}}`).
> 3. **1 roteiro de reels** (60s, hook + 3 pontos + CTA educativo).
> 4. **1 outline de artigo juridico** para blog (tema quente nas areas ativas; 800-1500 palavras quando produzido).
>
> Cada item com:
> - Publico-alvo especifico.
> - Gancho testado.
> - CTA natural educativo (nunca captacao ativa).
> - Data de publicacao sugerida na semana.
>
> Respeitar `{{PALETA_ESCRITORIO}}` e `{{TIPOGRAFIA_ESCRITORIO}}` quando mencionar aspectos visuais."

### Regras

- Se `marketing-juridico` nao estiver ativa: abortar (item 3 acima).
- Gravar o pipeline em `<COWORK>/marketing/pipelines/pipeline-<YYYY-WW>.md`.
- Nunca mencionar cliente real ou caso concreto — exemplos hipoteticos.
- Nunca prometer resultados em qualquer dos conteudos propostos.

### Saida

- Caminho do arquivo gerado.
- Resumo em 5 linhas do pipeline.
- Lembrete ao titular: "revisar + aprovar antes de entregar ao social media manager."

## Configuracao cron

- **Windows:** `schtasks /create /tn "previdenciario-marketing" /tr "..." /sc weekly /d MON /st 14:00`
- **macOS:** launchd Weekday=1 Hour=14.
- **Linux:** `0 14 * * 1 ...`
