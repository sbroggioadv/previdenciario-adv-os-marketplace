---
description: Redige parecer juridico previdenciario (viabilidade, risco ou estrategia) na estrutura I a VI, com fatos confirmados, numeros por script e conclusao em cenarios, sem percentual de exito.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [tema ou pergunta da consulta, opcional]
---

Voce foi acionado pelo comando `/parecer-previdenciario` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** entregar o parecer pronto para o papel timbrado do escritorio, respondendo cada questao da consulta.

## PROTOCOLO
1. Acionar `parecer-previdenciario` - ele confirma o quadro de fatos com o advogado, monta as questoes e redige nas secoes I a VI.
2. Parecer nao e peca: sem enderecamento a juizo, sem pedidos. A conclusao vem em 2 ou 3 cenarios concretos com ganho, risco e prazo; nenhum percentual de exito.
3. Todo numero sai de script pela `calculos-previdenciarios` ou como conta aberta; toda citacao precisa de ancora em `context/`. Tese que o plugin declara inviavel nao entra como caminho.
4. Passada anti-IA com `context/escrita-humana.md` antes do gate.
5. Fechar pelo `validador-previdenciario` e pela `suprema-corte-previdenciaria`.

**Skill a acionar:** `parecer-previdenciario`.
