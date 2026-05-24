---
description: Diagnostica o estado do plugin Previdenciario no diretorio atual. Verifica configuracao, persona, skills ativas, Suprema Corte.
allowed-tools: Read, Bash, Glob, Grep
argument-hint: [--verbose]
---

Voce foi acionado pelo comando `/status-previdenciario` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** apresentar diagnostico do estado do plugin para o operador.

## PROTOCOLO DE EXECUCAO

### 1. Buscar pasta `previdenciario/`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/find-cowork.py
```

Se nao encontrar:

```
🔴 Plugin Previdenciario NAO esta configurado neste diretorio.

Diretorio atual: <cwd>
Procurei por `previdenciario/cowork-state.json` ate 6 niveis acima — nao achei.

Para configurar:
   /start-previdenciario

Ou se voce ja configurou em outro lugar, abra o Claude Code naquela pasta.
```

### 2. Se encontrar, ler estado e apresentar

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state.py show <cowork_path>
```

Apresentar:

```
════════════════════════════════════════════════════
✅ PLUGIN PREVIDENCIARIO — STATUS
════════════════════════════════════════════════════

📂 Diretorio: <cwd>
📁 COWORK: <cowork_path>
📋 State: <cowork_path>/previdenciario/cowork-state.json
🆔 Persona: <cowork_path>/previdenciario/persona.md
   ✓ existe / ✗ nao existe

────────────────────────────────────────────────────
👤 OPERADOR
────────────────────────────────────────────────────
   Nome: <advogado_nome>
   OAB: <oab_uf> <oab_numero>
   Escritorio: <firm_name>
   Cidade/UF: <cidade>/<uf>

────────────────────────────────────────────────────
⚙️  SUBAREAS ATIVAS
────────────────────────────────────────────────────
   <lista das subareas configuradas>

────────────────────────────────────────────────────
🛡️  GOVERNANCA
────────────────────────────────────────────────────
   Hierarquia das 4 Camadas: ATIVA
   22 Proibicoes Absolutas: VIGILANTES
   5 Protocolos Tecnicos: PRONTOS
   Suprema Corte (R1-R4): <ATIVA / DESATIVADA>

────────────────────────────────────────────────────
🎯 SKILLS
────────────────────────────────────────────────────
   Invariantes (sempre ativas): <N>
      - previdenciario-master
      - suprema-corte-r1-coleta
      - suprema-corte-r2-base-juridica
      - suprema-corte-r3-tese
      - suprema-corte-r4-completude
      - estilo-juridico-previdenciario
      - visual-law-previdenciario
      - memory-evolver
      - cowork-sync

   Opt-in ativas: <M>
      <lista>

────────────────────────────────────────────────────
🎙️  TOM DE VOZ
────────────────────────────────────────────────────
   Perfil: <perfil>
   Intensidade combativa: <X>/10

────────────────────────────────────────────────────
🔗 ENV VARS
────────────────────────────────────────────────────
   PREVIDENCIARIO_PERSONA: <set / unset>
   PREVIDENCIARIO_COWORK_PATH: <set / unset>
   .claude/settings.local.json: <existe / nao existe>

────────────────────────────────────────────────────
💾 MEMORIA
────────────────────────────────────────────────────
   MEMORY.md raiz: <existe e tem N linhas>
   Pendencias nao consolidadas: <K>
   Ultimo snapshot pre-compact: <YYYY-MM-DD>

════════════════════════════════════════════════════
```

### 3. Detectar problemas

Sinalizar se algum dos seguintes estiver inconsistente:
- 🔴 `previdenciario/cowork-state.json` existe mas `persona.md` nao
- 🔴 `settings.local.json` aponta para path inexistente
- 🟡 Skill invariante nao listada no state
- 🟡 Pendencias de memoria > 30 dias sem consolidacao

### 4. Modo --verbose

Se `--verbose`, adicionar:
- Schema version do state
- Plugin version no state
- Lista completa de skills opt_in_active
- Lista de skills opt_in_inactive
- Pasta de snapshots (count)
- Hash MD5 da persona.md atual

### 5. Sugestoes de proximos passos

Se status OK:
> "Tudo configurado. Use `/previdenciario-master` para ativar a cadeia ou faca uma pergunta com termos previdenciarios."

Se status com warnings:
> "Detectei N inconsistencia(s). Quer que eu execute `/start-previdenciario --update` para corrigir?"

**Sem skill especifica a acionar** — comando de diagnostico puro.
