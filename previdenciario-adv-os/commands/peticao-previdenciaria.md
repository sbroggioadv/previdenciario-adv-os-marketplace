---
description: Produz peca previdenciaria (inicial, replica, mandado de seguranca, revisional, cumprimento de sentenca, alegacoes finais) pela porta unica, com triagem, quadro confirmado, estrategia escolhida e Suprema Corte.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [inicial | replica | mandado-seguranca | revisional | cumprimento | audiencia]
---

Voce foi acionado pelo comando `/peticao-previdenciaria` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** entregar a peca cabivel ao caso, redigida so depois do quadro confirmado e da estrategia escolhida.

## PROTOCOLO
1. Acionar `previdenciario-master` - ele faz a triagem e roteia para a skill da peca: `peticao-inicial-previdenciaria`, `replica-previdenciaria`, `mandado-seguranca-previdenciario`, `acao-revisional-rmi`, `cumprimento-sentenca-inss` ou `audiencia-previdenciaria`. O argumento so adianta a classificacao; nao pula a triagem.
2. A pergunta critica do prazo vem primeiro, como em `/previdenciario-master`. Prazo correndo: `prazos-previdenciarios` antes da peca.
3. Valor da causa, alcada, RMI, regra de transicao e atrasados saem dos scripts pela `calculos-previdenciarios` ou como conta aberta, nunca estimados. Revisional abre pela decadencia e pela prescricao.
4. Recurso tem comando proprio: `/recurso-previdenciario`.
5. Fechar pelo `validador-previdenciario` e pela `suprema-corte-previdenciaria`.

**Skill a acionar:** `previdenciario-master`.
