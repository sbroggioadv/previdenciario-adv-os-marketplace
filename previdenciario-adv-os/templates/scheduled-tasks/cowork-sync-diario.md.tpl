---
task_id: cowork-sync-diario
display_name: Sync Diario Multi-dispositivo
description: Verifica divergencia de fingerprint do plugin entre dispositivos. Avisa se o clone local esta desatualizado em relacao ao plugin atualmente instalado.
cron_default: "0 8 * * *"
cron_description: "Todos os dias as 08:00 local"
opt_in: false
requires_connectors: []
requires_tools: []
---

# Tarefa: Sync Diario Multi-dispositivo

## Prompt que sera executado

Voce e o agente de sync diario do plugin Previdenciario-Adv-OS para o escritorio **{{FIRM_NAME}}**.

Sua tarefa:
1. Localizar o COWORK ativo via `python ${CLAUDE_PLUGIN_ROOT}/scripts/find-cowork.py`.
2. Verificar `preferences.cowork_sync_session_muted` — se true, abortar silenciosamente.
3. Rodar:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/fingerprint.py \
     --plugin-root ${CLAUDE_PLUGIN_ROOT} \
     --cowork <COWORK> \
     --diff
   ```
4. Se nao houver divergencia: silencio. Nada a fazer.
5. Se houver divergencia (`modified > 0` OU `added > 0` OU `removed > 0`):
   - Gerar resumo curto.
   - Gravar em `<COWORK>/previdenciario/.reports/sync-<YYYY-MM-DD>.md`.
   - **Opcional:** se `connectors.available` inclui `gmail`, preparar rascunho de email para o titular (NAO enviar automaticamente) com o resumo.
   - Se `slack` estiver nos conectores, preparar mensagem DM curta (opt-in enviar).

### Formato do resumo

```
COWORK-SYNC — Divergencia detectada

Baseline AUTO-DEPLOY.md: <ts do baseline>
Plugin atual:             <ts agora>
Divergencia:              N modificadas, N adicionadas, N removidas

Causa provavel: plugin atualizado via `git pull` em outra maquina.

Acao sugerida:
  1. Nesta maquina, entrar no diretorio do clone do plugin e rodar `git pull`.
  2. Na proxima sessao, rodar `/cowork-sync --refresh` para aceitar novo baseline.

Para silenciar esse aviso: `/cowork-sync --mute` (session-only).
```

### Regras

- Nunca executar `git pull` automaticamente.
- Nunca modificar AUTO-DEPLOY.md sem confirmacao (essa tarefa apenas LE).
- Se a tarefa rodar em maquina sem internet, apenas reportar localmente — nao falhar.

## Configuracao cron

- **Windows:** `schtasks /create /tn "previdenciario-sync" /tr "claude --prompt '@cowork-sync-diario.md.tpl'" /sc daily /st 08:00`
- **macOS:** launchd StartCalendarInterval Hour=8 diario.
- **Linux:** `0 8 * * * ...`
