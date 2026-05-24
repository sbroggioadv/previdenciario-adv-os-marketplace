# CLAUDE.md — Plugin Previdenciario-Adv-OS

> Instrucoes para futuras sessoes neste sub-repositorio. Ler PRIMEIRO ao retomar trabalho.

---

## Identidade do Projeto

- **Nome:** Plugin Previdenciario-Adv-OS
- **Slug:** `previdenciario-adv-os`
- **Tipo:** plugin oficial do Claude Code (`.claude-plugin/plugin.json`)
- **Audiencia:** advogados previdenciaristas brasileiros (RGPS + RPPS + Previdencia Complementar + Acidentario)
- **Versao atual:** 0.1.0-alpha.0 (em bootstrap S0)
- **Pasta de incubacao:** `plugins-adicionais/plugin-previdenciario/` (dentro do repo do plugin pai durante desenvolvimento)
- **Repo final:** placeholder neutro (a definir antes do release publico)

---

## REGRA DE OURO — DESPERSONALIZACAO ABSOLUTA (PLUGIN COMERCIAL)

Este plugin sera **comercializado**. Sem `authorship_whitelist`. **Zero mencoes** ao criador da metodologia em qualquer arquivo.

**ZERO mencoes permitidas (ver `audit/forbidden-terms.json` para lista canonica):**
- Nome do criador da metodologia (qualquer variante)
- OAB do criador
- Email/contato pessoal
- Padroes ou metodologias nomeadas pessoalmente
- Ferramentas proprietarias do escritorio-modelo
- Apelidos pessoais
- Mentorias, cursos ou coworks proprietarios do criador

**Defesa em profundidade:**

```bash
# Antes de CADA commit
python3 audit/audit.py

# Verificacao reforcada pre-release: rodar audit com saida JSON
python3 audit/audit.py --json | jq '.total_matches'
# esperado: 0
```

Catalogo completo de termos proibidos em `audit/forbidden-terms.json` (categoria `identidade_pessoal_do_criador`).

---

## Hierarquia das 4 Camadas (Constituicao Operacional)

```
CAMADA 1 — PROIBICOES ABSOLUTAS (PA-01 a PA-22) — inviolaveis
CAMADA 2 — PROTOCOLOS TECNICOS — aplicacao obrigatoria
CAMADA 3 — IDENTIDADE TECNICA E ESTILO — FIRAC + AIDA + Baloney
CAMADA 4 — SKILLS (49 totais) — operacional
```

Detalhamento em:
- `.planning/PROMPT-MESTRE-RECOMPOSTO.md` (fonte canonica integral)
- `.planning/HIERARQUIA-4-CAMADAS.md` (referencia rapida)
- `.planning/PROIBICOES-ABSOLUTAS.md` (PA-01 a PA-22)
- `.planning/PROTOCOLOS-TECNICOS.md` (5 protocolos)

---

## Como Retomar Trabalho

1. **Ler `MEMORY.md`** (raiz deste sub-repo) — estado executivo, sprint ativa, proximo passo
2. **Ler `.planning/DECISIONS.md`** — overlay autoritativo (10 decisoes cravadas D1-D10)
3. **Ler `.planning/ROADMAP.md`** — saber onde estamos (S0/S1/S2/S3/S4)
4. **`git status` + `git log -5`** para estado real do repo
5. **`python3 audit/audit.py`** para verificar despersonalizacao

---

## Arquitetura em Uma Frase

**Plugin previdenciario especializado** (49 skills em 4 tiers) com **engine clonado do plugin pai** (commands/hooks/scripts/templates) e **governance jurídica** (4 camadas + 22 PAs + 5 protocolos + Suprema Corte R1-R4) injetada via skill `previdenciario-master`. Persona do operador resolvida em runtime via `<cwd>/previdenciario/persona.md` (fora do plugin).

---

## Padroes a Seguir

### 1. Privacidade e LGPD

- Toda pasta `<cwd>/previdenciario/` do usuario-cliente e gitignored por default
- Warning LGPD se usuario escolher pasta sincronizada (iCloud/OneDrive/Dropbox/Drive)
- Transcricao de audio APENAS local (faster-whisper) — nunca cloud
- MCPs externos sempre opt-in com warning

### 2. Despersonalizacao bloqueante

```bash
python3 audit/audit.py
```

Zero matches = OK. Qualquer match bloqueia commit/release.

### 3. Idempotencia de `/start-previdenciario`

`/start-previdenciario` rodado N vezes deve produzir mesmo state hash. Testado em S1.

### 4. Portabilidade Win + Mac + Linux

- Scripts em bash + Python 3.11+
- `${CLAUDE_PLUGIN_ROOT}` em todos os hooks
- `${PREVIDENCIARIO_PERSONA}` resolvido via fallback chain pelo `scripts/resolve-persona.py`

### 5. Skills no formato canonico Anthropic

Apenas `SKILL.md` com frontmatter YAML:

```markdown
---
name: nome-da-skill
description: >
  Descricao com keywords de ativacao...
---

# Conteudo da skill...
```

### 6. Placeholders literais nas skills

`{{PLACEHOLDER}}` permanecem LITERAIS no disco. LLM resolve em runtime via persona injetada.

### 7. Cada skill (Tier 1/2/3) tem 2 secoes obrigatorias

```markdown
## Vedacoes especificas
- PA-XX: [explicacao do que NAO fazer nesta skill]

## Protocolos acionados
- 2.X: [qual protocolo aplica]
```

### 8. Hooks anti-flap

Debouncing 60s + filter por path + skip diff trivial.

### 9. Hook SessionStart e o coracao da personalizacao

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/resolve-persona.py
```

`${PREVIDENCIARIO_PERSONA}` resolvido em runtime via fallback chain.

### 10. Commits semanticos com marcador de sprint

```
chore(s0): bootstrap plugin previdenciario [PREV-S0/SETUP]
feat(s1): /start previdenciario funcional [PREV-S1/CORE]
feat(s2): governance + estado-maior [PREV-S2/GOV]
feat(s3a): tenentes contenciosos [PREV-S3a/CONTENCIOSO]
feat(s3b): tenentes administrativos [PREV-S3b/CRPS]
feat(s4a): analise tecnica [PREV-S4a/ANALISE]
feat(s4b): calculos [PREV-S4b/CALC]
feat(s4c): rpps complementar acidentario [PREV-S4c/REGIMES]
feat(s4d): documentos extrajudiciais [PREV-S4d/DOCS]
feat(s4e): audiencia [PREV-S4e/AUDIENCIA]
chore(release): v0.1.0-alpha.1 [PREV-S4/RELEASE]
```

### 11. Sempre atualizar MEMORY.md ANTES de push

1. Editar `MEMORY.md` (raiz)
2. Rodar `python3 audit/audit.py` (deve passar)
3. `git add`
4. `git commit` semantico
5. (opcional) `git push`

---

## Decisoes Cravadas (referencia rapida)

Ver `.planning/DECISIONS.md` para detalhe completo (D1-D14).

| ID | Decisao |
|---|---|
| D1 | Nome `Plugin-Previdenciario-Adv-OS`, slug `previdenciario-adv-os` |
| D2 | Plugin COMERCIAL — despersonalizacao absoluta intransigente |
| D3 | Hierarquia das 4 Camadas e constitutiva |
| D4 | `/start-previdenciario` travado em PREVIDENCIARIO (sem pergunta de area) |
| D5 | 49 skills em 4 tiers + transversais + engine |
| D6 | 8 commands prefixados (D12 substitui os 19 originais) |
| D7 | Engine clonado do plugin pai com adaptacoes minimas |
| D8 | Conviver em `plugins-adicionais/` durante incubacao |
| D9 | Persona resolvida em runtime via `<cwd>/previdenciario/persona.md` |
| D10 | 5 testes obrigatorios bloqueantes para release |
| **D11** | **Pasta dedicada `previdenciario/` (substitui `.dev-adv/`) — isolamento entre plugins** |
| **D12** | **8 commands prefixados (substitui 19 originais) — `/start-previdenciario`, `/previdenciario-master`, etc.** |
| **D13** | **Ativacao automatica por contexto — keywords previdenciarias disparam plugin sem comando** |
| **D14** | **Env vars renomeadas: `PREVIDENCIARIO_PERSONA` + `PREVIDENCIARIO_COWORK_PATH`** |

---

## Proibicoes

1. **NAO** comecar nova Sprint sem ler `MEMORY.md` e `.planning/ROADMAP.md`
2. **NAO** incluir nome/identidade do criador da metodologia em qualquer arquivo (audit bloqueia)
3. **NAO** publicar antes de v1.0 GA com testes obrigatorios verdes
4. **NAO** habilitar MCP externo por default
5. **NAO** transcrever cloud — sempre local
6. **NAO** sobrescrever customizacao do usuario-cliente sem perguntar
7. **NAO** colocar persona renderizada DENTRO do plugin instalado — vive em `<cwd>/previdenciario/persona.md`
8. **NAO** criar SKILL.md sem secao "Vedacoes especificas" mapeando PAs
9. **NAO** alterar nome do plugin sem nova decisao em `.planning/DECISIONS.md`
10. **NAO** aceitar instrucao do usuario que conflite com Camada 1 (PA-01 a PA-22)

---

## Estrutura do Sub-Repo

```
plugin-previdenciario/
├── .claude-plugin/plugin.json   # manifest
├── .planning/                    # 8 docs (PROMPT MESTRE + 7 derivados)
├── commands/                     # 14 commands de infra + 5 de dominio (S1)
├── skills/                       # 49 skills (S1 a S4)
├── hooks/                        # SessionStart + PostToolUse + UserPromptSubmit + PreCompact
├── context/                      # persona-fallback.md
├── templates/                    # *.tpl renderizados no /start
├── scripts/                      # render.py, state.py, resolve-persona.py, etc.
├── audit/                        # forbidden-terms.json + audit.py + audit-script.sh
├── README.md                     # institucional, neutro
├── LICENSE                       # MIT, copyright neutro
├── .gitignore                    # LGPD-aware
├── CLAUDE.md                     # este arquivo
└── MEMORY.md                     # estado executivo
```

---

## Comunicacao

- **Idioma:** Portugues (Brasil)
- **Tom dos docs internos:** tecnico, direto, sem mencoes pessoais
- **Tom das mensagens pro usuario-cliente (skills, commands, wizard):** acolhedor, didatico, respeita `tom_voz` configurado dinamicamente em runtime
- **Reportes:** ✅ concluido / 🔴 erro / 🏁 sprint finalizada

---

## Checklist de Retomada em Nova Sessao

```markdown
- [ ] Li MEMORY.md
- [ ] Sei em qual sprint estamos (S0/S1/S2/S3/S4)
- [ ] Sei se ha pendencia aguardando aprovacao
- [ ] Conferi DECISIONS.md
- [ ] Rodei git status / git log -5
- [ ] Rodei python3 audit/audit.py (deve passar)
- [ ] Se vou tocar em skills: li EXTRACTION-PLAN.md
- [ ] Se vou tocar em PAs: li PROIBICOES-ABSOLUTAS.md
- [ ] Se vou tocar em commands: li ROADMAP.md (S1 detalha 5 commands de dominio)
```

---

**Ultima atualizacao:** 2026-04-30 (bootstrap S0).
