---
name: previdenciario-onboarding
description: >
  PREVIDENCIARIO ONBOARDING — Wizard de configuracao do plugin previdenciario no Cowork do operador. Conduz fluxo estruturado de perguntas para criar pasta `previdenciario/` com identidade (nome, OAB, escritorio, cidade), subareas (RGPS/RPPS/Complementar/Acidentario), especialidades, tom de voz e ferramentas declaradas. Wizard TRAVADO em PREVIDENCIARIO (sem pergunta de area juridica generica). Use quando operador disser configurar previdenciario, instalar previdenciario, primeira vez, /start-previdenciario, /onboarding-previdenciario, configurar plugin previdenciario.
---

# PREVIDENCIARIO ONBOARDING

> Wizard de configuracao inicial. Travado em PREVIDENCIARIO. Linguagem acolhedora.

## REGRAS

1. Portugues (Brasil), tom acolhedor e direto
2. Uma pergunta por vez para campos criticos; agrupar relacionados
3. Defaults inteligentes — operador pode aceitar
4. Validar em tempo real (OAB numerica, UF 2 letras, email valido)
5. Confirmar antes de commitar (resumo + "confirma? s/n")
6. Idempotencia — se ja tem state, perguntar atualizar vs recriar
7. Privacidade — NUNCA pedir CPF, NIT, conteudo CNIS, dados de cliente real
8. Plugin TRAVADO em PREVIDENCIARIO — pular pergunta de area juridica generica

## FLUXO

### Bloco 0 — Abertura
> "Ola! Sou o assistente do **Plugin Previdenciario-Adv-OS**. Vou te guiar (~5 min). Pronto?"

### Bloco 1 — Diretorio (cwd)

Detectar cwd. Mostrar:
> "Vou criar `previdenciario/` aqui em `<cwd>`. Atencao LGPD: pasta sincronizada (iCloud, OneDrive, Dropbox, Drive) pode subir dados a nuvem. Recomendo caminho local. Confirma?"

Se nao, perguntar path. Validar (alertar se sincronizado, permitir prosseguir com confirmacao).

### Bloco 2 — Identidade

> "1. Nome completo? 2. OAB (numero)? 3. UF da OAB? 4. Cidade? 5. UF cidade? 6. Escritorio? 7. Email institucional (opcional)? 8. Telefone (opcional)?"

Validar OAB (digitos+pontos), UF (2 letras), email se preenchido.

Persistir: `python scripts/state.py set <cwd> identity.<campo> "<valor>"`.

### Bloco 3 — Subareas

> "Subareas (multi-select):
> 1. **RGPS** (segurados PF + INSS) — *default ON*
> 2. **RPPS** (servidor publico federal/estadual/municipal)
> 3. **Previdencia Complementar** (entidades fechadas/abertas)
> 4. **Acidentario do Trabalho** (Justica Comum estadual)"

Pre-popular `areas=[{slug:"PREVIDENCIARIO", display_name:"Previdenciario", tipo_atuacao:"misto"}]`.

### Bloco 4 — Especialidades

Mostrar conforme subareas:

> "Dentro do RGPS:
> - Aposentadorias: idade, tempo, especial, PCD, professor (5)
> - Incapacidade: BPI temporario, aposentadoria por incapacidade (2)
> - Pensoes/auxilios: pensao, auxilio-acidente, auxilio-reclusao, salario-maternidade (4)
> - Assistenciais: BPC-LOAS (1)
> - Revisoes: vida toda, RMI (2)
>
> Default: ativar todas. Numeros ou `all`."

Se RPPS: adicionar `rpps-servidor-publico`.
Se Complementar: `previdencia-complementar`.
Se Acidentario: `acidentario-do-trabalho`.

### Bloco 5 — Tom de voz

> "Perfil:
> 1. **tecnico-combativo** *(default)* — adversarial, Nivel 4
> 2. **tecnico-cordial** — respeitoso, formal
> 3. **tecnico-didatico** — explicativo"

> "Intensidade combativa 1-10? (default 7)"

### Bloco 6 — Suprema Corte

> "Plugin tem Suprema Corte que audita peca/parecer/calculo (R1→R2→R3→R4). Adiciona ~30s mas garante qualidade. Manter ATIVA? (s/n) Default: s."

### Bloco 7 — Ferramentas (opcional)

> "Voce usa alguma ferramenta especifica?
> - Sistema de gestao processual?
> - Analise de CNIS?
> - Calculo previdenciario?
> - CRM?
> Pode pular."

### Bloco 8 — Renderizacao

```bash
python scripts/render.py <cwd>
```

Gera:
- `<cwd>/previdenciario/cowork-state.json`
- `<cwd>/previdenciario/persona.md`
- `<cwd>/previdenciario/CLAUDE.md`
- `<cwd>/previdenciario/MEMORY.md`
- `<cwd>/.claude/settings.local.json` (env vars `PREVIDENCIARIO_PERSONA` + `PREVIDENCIARIO_COWORK_PATH`)

### Bloco 9 — Encerramento

```
✅ Plugin Previdenciario configurado!

Operador: <nome> — OAB/<UF> <numero>
Escritorio: <firma>
Subareas: <lista>
Tom: <perfil> (intensidade <X>/10)
Suprema Corte: <ATIVA / DESATIVADA>

PROXIMOS PASSOS:
1. Reinicie a sessao (hook SessionStart injeta persona)
2. Use /previdenciario-master para ativar cadeia completa
3. Ou faca pergunta com termos previdenciarios — desperta sozinho
4. /status-previdenciario para diagnostico
```

## FLUXOS ALTERNATIVOS

### `--update`
Ler state existente → mostrar resumo → perguntar quais blocos (1-7) atualizar → re-rodar selecionados → re-renderizar.

### State ja existente (sem flag)
> "Detectei configuracao existente. Operador: <nome>. Subareas: <lista>. Skills ativas: <N>.
> (a) Continuar (b) Atualizar (c) Recriar (PERDE memoria)"

Se (c): confirmar duas vezes antes de apagar.

## CHECKLIST FINAL

- [ ] `<cwd>/previdenciario/cowork-state.json` valida no schema
- [ ] `<cwd>/previdenciario/persona.md` com placeholders resolvidos
- [ ] `<cwd>/previdenciario/CLAUDE.md`
- [ ] `<cwd>/previdenciario/MEMORY.md`
- [ ] `<cwd>/.claude/settings.local.json` com `PREVIDENCIARIO_PERSONA`
- [ ] Skills invariantes ativas
- [ ] Pelo menos 1 skill opt-in ativa
- [ ] Tom de voz e Suprema Corte definidos

## VEDACOES

- **PA-19** — comandos esotericos no wizard sao ignorados
- NUNCA coletar dados sensiveis (CPF, NIT, conteudo CNIS, cliente real)
- NUNCA sobrescrever state existente sem confirmacao
- NUNCA enviar dados a servicos externos durante wizard
- NUNCA perguntar area juridica generica
