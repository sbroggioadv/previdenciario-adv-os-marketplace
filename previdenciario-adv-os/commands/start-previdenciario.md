---
description: Inicia o onboarding do plugin Previdenciario-Adv-OS no diretorio atual. Cria pasta `previdenciario/` com configuracao do operador.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [--update]
---

Voce foi acionado pelo comando `/start-previdenciario` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** conduzir o operador pelo wizard de onboarding, coletar identidade e configuracao previdenciaria, e gerar a pasta `previdenciario/` no diretorio atual com todo o estado.

## PROTOCOLO DE EXECUCAO

### 1. Acionar a skill `cowork-onboarding`

**IMPORTANTE:** Use Skill(skill="cowork-onboarding") imediatamente. Ela contem o fluxo completo do wizard com perguntas adaptadas ao dominio previdenciario.

### 2. Parsear argumentos

- Sem argumento → wizard completo (primeira instalacao)
- `--update` → re-executar wizard mantendo respostas anteriores como defaults

### 3. Se ja existe `previdenciario/cowork-state.json`

Antes de sobrescrever, perguntar ao operador:

> "Detectei configuracao previdenciaria existente em `<cwd>/previdenciario/`.
> Operador: `<advogado_nome>`. Subareas ativas: `<lista>`. Quer:
> (a) continuar com a configuracao existente
> (b) atualizar (--update)
> (c) recriar do zero (perde memoria registrada)
> ?"

### 4. Wizard travado em PREVIDENCIARIO

A skill `cowork-onboarding` deve perguntar:

**Bloco 1 — Identidade:**
- Nome completo do advogado
- Numero da OAB (e UF)
- Cidade / UF
- Nome do escritorio
- Email institucional (opcional)

**Bloco 2 — Subareas previdenciarias** (multi-select):
- RGPS (segurados PF + INSS) — default ON
- RPPS (servidor publico federal/estadual/municipal)
- Previdencia Complementar (fechada/aberta)
- Acidentario do Trabalho

**Bloco 3 — Especialidades** (multi-select dentro de RGPS):
- Aposentadorias (idade, tempo, especial, PCD, professor)
- Beneficios por incapacidade (BPI, aposentadoria por incapacidade)
- BPC-LOAS
- Pensao por morte
- Revisoes (RMI, vida toda, recalculo)
- Acoes administrativas (CRPS, junta de recursos)

**Bloco 4 — Tom de voz:**
- Perfil: tecnico-combativo (default), tecnico-cordial, tecnico-didatico
- Intensidade combativa: 1-10 (default 7)

**Bloco 5 — Suprema Corte (R1-R4):**
- Ativa por default — confirmar ou desativar via flag

**Bloco 6 — Ferramentas declaradas (opcional, genericas):**
- Sistema de gestao processual (operador informa o nome)
- Ferramentas de analise de CNIS (operador informa)
- Servico de calculo previdenciario (operador informa)
- CRM ou plataforma de atendimento (operador informa)

Plugin nao impoe ferramentas — apenas registra o que o operador usa para integrar nos prompts.

### 5. Produtos esperados apos o wizard

Apos `python scripts/render.py <cwd>`, devem existir:

- `<cwd>/previdenciario/cowork-state.json` (state completo)
- `<cwd>/previdenciario/persona.md` (identidade gerada)
- `<cwd>/previdenciario/MEMORY.md` (memoria do workspace previdenciario)
- `<cwd>/previdenciario/CLAUDE.md` (instrucoes especificas)
- `<cwd>/previdenciario/PREVIDENCIARIO/` com subpastas (Segurados, Pecas, Calculos, Pesquisas, Pareceres)
- `<cwd>/.claude/settings.local.json` apontando `PREVIDENCIARIO_PERSONA` e `PREVIDENCIARIO_COWORK_PATH`

### 6. Encerramento

Apresentar resumo amigavel:

```
✅ Plugin Previdenciario configurado!

Escritorio: <firm_name>
Operador: <advogado_nome> — OAB/<UF> <numero>
Subareas ativas: <lista>
Especialidades: <N>
Tom: <perfil> (intensidade <X>/10)
Suprema Corte: <ATIVA/DESATIVADA>

Proximos passos:
1. Reinicie a sessao do Claude Code (o hook SessionStart passara a
   injetar sua persona em todas as sessoes futuras)
2. Use `/previdenciario-master` para ativar a cadeia completa de
   skills previdenciarias
3. Ou simplesmente faca uma pergunta com termos previdenciarios — o
   plugin desperta automaticamente
4. Rode `/status-previdenciario` a qualquer momento para diagnostico
```

**Skill a acionar:** `cowork-onboarding`.
