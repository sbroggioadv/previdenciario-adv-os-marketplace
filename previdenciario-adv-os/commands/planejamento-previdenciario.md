---
description: Planejamento de aposentadoria no RGPS - tempo pelo script, direito adquirido, transicoes da EC 103 e regra permanente, RMI de cada regra e comparacao de quando aposentar e quanto recebe.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [DER pretendida ou objetivo do cliente, opcional]
---

Voce foi acionado pelo comando `/planejamento-previdenciario` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** entregar a tabela regra a regra (cumpre ou nao, em que data, com que RMI) e 2 ou 3 rotas de aposentadoria com ganho e risco.

## PROTOCOLO
1. Acionar `planejamento-previdenciario` - ele confirma o quadro (idade, sexo, filiacao antes ou depois de 13/11/2019, tempo, especial, magisterio, objetivo) e roda, nesta ordem, os scripts de tempo, de transicao e de RMI.
2. Conversao de tempo especial so do trabalho prestado ate 13/11/2019; vinculo que cruza a data e fatiado pelo script. Filiado depois de 13/11/2019 so tem a regra permanente.
3. Regra com fator previdenciario sem o fator apurado sai com a formula e a lista do que falta, fica na tabela sem valor e nao entra no ranking. Nunca estimar o fator.
4. Servidor publico vai para `rpps-servidor-publico`; beneficio ja concedido, para `acao-revisional-rmi`; BPC, para `bpc-loas-previdenciario`.
5. Fechar pelo `validador-previdenciario` e pela `suprema-corte-previdenciaria`.

**Skill a acionar:** `planejamento-previdenciario`.
