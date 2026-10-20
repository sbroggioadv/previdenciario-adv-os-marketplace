---
description: Calculo previdenciario pelos scripts locais do plugin (CNIS, tempo, transicao, incapacidade, RMI, valor da causa, RPV), com memoria, regra e fonte, ou a conta aberta quando o script nao fecha.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [cnis | tempo | transicao | incapacidade | rmi | valor-causa | rpv]
---

Voce foi acionado pelo comando `/calculo-previdenciario` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** entregar o numero conferido por script, ou a formula preenchida ate onde os dados permitem, sempre com a fonte de cada termo.

## PROTOCOLO
1. Acionar `calculos-previdenciarios` - o hub identifica a conta pelo argumento (ou pergunta, com botoes), le a secao CAMPOS do `context/calculo-<conta>.md`, colhe so os campos obrigatorios que faltam e roda `scripts/calc/calc_previdenciario_<conta>.py` localizado conforme a secao 13 da metodologia.
2. Nunca numero de cabeca. Exit 0: numero com memoria, regra e fonte. Exit 3: formula aberta com `[VERIFICAR]` e o dado que falta. Exit 2, sem Python ou sem script: conta aberta pelo `context/calculo-<conta>.md` com o aviso "conta nao conferida por script".
3. A entrada JSON e gravada em `previdenciario/casos/<slug>-calc-<conta>.json`, no computador do advogado. CNIS e laudo sao dado sensivel: nunca em ferramenta externa.
4. Nunca editar script nem tabela para a conta fechar.
5. Fechar pela `suprema-corte-previdenciaria` quando o calculo for entregue ao cliente ou entrar em peca.

**Skill a acionar:** `calculos-previdenciarios`.
