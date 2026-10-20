---
description: Mostra o estado do plugin previdenciario-adv-os no diretorio de trabalho - versao, perfil configurado ou nao, casos abertos com fase e proximo prazo e o resumo do caso ativo.
allowed-tools: Read, Bash, Glob, Grep, Skill
argument-hint: [slug do caso, opcional]
---

Voce foi acionado pelo comando `/status-previdenciario` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** responder em uma tela onde o escritorio esta: plugin, perfil e casos.

## PROTOCOLO
1. Acionar `memoria-de-caso-previdenciario` no modo resumo - ele le `previdenciario/perfil.md` e `previdenciario/casos/*.md` do diretorio de trabalho.
2. Mostrar: versao do plugin (2.0.1); perfil configurado ou nao; lista dos casos com fase e proximo prazo; e, do caso ativo (ou do slug recebido no argumento), 5 a 8 linhas com partes, beneficio, fase, situacao, proxima providencia e proximo prazo fatal.
3. Somente leitura: este comando nao grava nem altera caso.
4. Sem `perfil.md` e com `previdenciario/cowork-state.json` ou `persona.md` da 0.1.0: apontar `/start-previdenciario` para a migracao. Sem nada: apontar `/start-previdenciario`.
5. Prazo que nao estiver registrado no caso aparece como lacuna, nunca estimado.

**Skill a acionar:** `memoria-de-caso-previdenciario`.
