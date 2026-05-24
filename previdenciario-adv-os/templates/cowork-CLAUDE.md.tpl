# CLAUDE.md — Workspace COWORK do {{FIRM_NAME}}

> Identidade e regras de trabalho deste workspace. Lido pelo Claude no início de cada sessão dentro desta pasta.

---

## Identidade do Workspace

- **Escritório:** {{FIRM_NAME}}
- **Titular:** {{ADVOGADO_NOME}}{{#OAB_NUMERO}} (OAB/{{OAB_UF}} {{OAB_NUMERO}}){{/OAB_NUMERO}}
- **Plugin operacional:** `previdenciario-adv-os` v{{PLUGIN_VERSION}}
- **Persona:** `<COWORK>/previdenciario/persona.md` (injetada por hook SessionStart)
- **State:** `<COWORK>/previdenciario/cowork-state.json`

---

## Áreas de Atuação Mapeadas

{{#AREAS_LIST}}
- **{{display_name}}** → pasta `{{slug}}/` (CLAUDE.md próprio)
{{/AREAS_LIST}}

Cada pasta de área tem `CLAUDE.md` próprio que contextualiza:
- Skills relevantes para a área
- Workflow específico
- Documentos e modelos de referência

---

## Como Trabalhar Aqui

### Ao iniciar uma demanda jurídica

O `firm-master` (orquestradora) é acionada automaticamente em **toda demanda jurídica**. Ela aplica o **protocolo de 6 etapas**:

1. **Identifica área** — direciona para o COMANDANTE certo (pasta de área)
2. **Aciona ESTADO-MAIOR** — `estrategia-de-caso`, `analise-trilateral`, `jurisprudencia-estrategica`
3. **Aciona TENENTES** — skills de execução específicas (peças, contratos, pareceres, etc.)
4. **Coleta documentos** — pede ao usuário o que falta antes de produzir
5. **Aplica SUPREMA CORTE** — R1→R2→R3→R4 antes de entregar (default-on, bypass disponível)
6. **Entrega** — output no formato preferido ({{OUTPUT_FORMAT_PREFERIDO}})

### Modo planejamento

Antes de executar tarefa não-trivial, o Claude apresenta:
- **Cadeia de raciocínio** — como vai resolver
- **Plano de ação** — etapas claras
- **Dúvidas** — o que falta para fazer com qualidade

Aguarda confirmação ou ajuste antes de começar.

### Comandos disponíveis

- `/start` — Re-rodar wizard completo (atualizar persona, áreas, skills)
- `/cowork-status` — Estado atual do workspace
- `/cowork-add-area <slug>` — Adicionar nova área de atuação
- `/cowork-add-skill <name>` — Ativar skill opt-in
- `/cowork-set <campo> <valor>` — Alterar campo específico do state
- `/corte off` / `/corte on` — Toggle Suprema Corte para esta sessão

---

## MEMORY SYSTEM

Esta pasta tem `MEMORY.md`. Funciona como memória externa do workspace.

**No início de cada sessão:** O Claude lê `MEMORY.md` antes de responder. Usa o que encontra para informar o trabalho — sem anunciar, apenas se basear.

**Memória é user-triggered.** Não escreve automaticamente. Só adiciona quando você pedir explicitamente: "lembre disso", "anote", "salve isso", "registre na memória".

**Conflitos:** Se você pedir para lembrar algo que conflita com memória existente, o Claude flagga em vez de sobrescrever silenciosamente.

---

## Privacidade & LGPD

- **Dados de cliente:** ficam APENAS nesta pasta `<COWORK>/`. Nunca saem da máquina, nunca vão para repositório, nunca para serviço cloud não-autorizado.
- **Áudios de reunião:** se transcrição for usada, **APENAS local** (faster-whisper). Nunca cloud.
- **MCPs externos** (Gmail, Calendar, etc.): só ativados via `/start` com warning explícito.
- **Auditoria:** sempre que ativar nova integração, o Claude avisa o impacto em LGPD.

---

## Atualização desta Configuração

Esta pasta é **gerada e mantida pelo plugin `previdenciario-adv-os`**. Para reconfigurar:

```
/start --update
```

Versão do schema deste workspace: {{SCHEMA_VERSION}}
Última atualização: {{GENERATED_AT}}
