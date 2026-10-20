---
description: Configura o plugin previdenciario-adv-os no diretorio de trabalho (perfil do escritorio e pasta de casos) e migra a configuracao da versao 0.1.0 sem apagar os arquivos antigos.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [vazio para configurar | atualizar]
---

Voce foi acionado pelo comando `/start-previdenciario` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** deixar `previdenciario/perfil.md` e `previdenciario/casos/` prontos no diretorio de trabalho do advogado, em cerca de 5 minutos.

## PROTOCOLO
1. Acionar `previdenciario-onboarding` - ele detecta o estado e escolhe o fluxo: `perfil.md` ja existe (idempotencia: continuar, atualizar ou recriar o perfil), configuracao da 0.1.0 (`previdenciario/cowork-state.json` ou `persona.md`, migracao) ou nada (wizard dos blocos 0 a 9).
2. Nunca apagar `previdenciario/casos/` nem os arquivos da 0.1.0; a migracao le os antigos e grava o `perfil.md` ao lado deles.
3. Escolhas de lista fechada viram botoes (AskUserQuestion); nome, OAB, cidade e demais textos livres seguem digitados. O aviso LGPD e obrigatorio.
4. Nenhum script e executado: o wizard so le e grava arquivos de texto.
5. Ao final, devolver o advogado ao `/previdenciario-master`. Este comando nao abre caso nem calcula, entao nao passa pela `suprema-corte-previdenciaria`.

**Skill a acionar:** `previdenciario-onboarding`.
