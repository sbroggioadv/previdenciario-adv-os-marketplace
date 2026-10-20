---
description: Porta unica do plugin previdenciario-adv-os. Recebe qualquer demanda previdenciaria, faz primeiro a pergunta critica do prazo e conduz todas as skills pertinentes ate a Suprema Corte.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [descricao do caso ou da demanda, opcional]
---

Voce foi acionado pelo comando `/previdenciario-master` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** receber a demanda previdenciaria em linguagem natural, classificar, confirmar o quadro do caso e conduzir a trilha completa ate a entrega revisada.

## PROTOCOLO
1. Acionar `previdenciario-master` - ele le `context/metodologia-previdenciario.md` e o `previdenciario/perfil.md` do diretorio de trabalho e conduz os 9 passos (triagem, quadro, memoria, transversais, trilha, script, gate, registro).
2. A pergunta critica vem antes de qualquer outra, sempre: **ha prazo correndo agora (recurso administrativo, resposta, recurso judicial) ou beneficio cessado ou indeferido ha menos de 30 dias?** Sim: a trilha entra por `prazos-previdenciarios`. Prazo ja vencido: avisar na primeira linha, sem prometer relevacao, e mostrar as outras vias. Nao sei: tratar como possivel prazo e pedir a data da ciencia.
3. Sem `previdenciario/perfil.md`: oferecer `/start-previdenciario` ou seguir com voz neutra, avisando em uma linha.
4. Nada e redigido antes do quadro do caso confirmado e da estrategia escolhida pelo advogado. Numero so por script ou conta aberta, nunca de cabeca.
5. Fechar pela `suprema-corte-previdenciaria`, depois do `validador-previdenciario`.

**Skill a acionar:** `previdenciario-master`.
