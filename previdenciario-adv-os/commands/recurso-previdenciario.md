---
description: Redige recurso previdenciario ou contrarrazoes na via correta (CRPS, recurso inominado no JEF, PEDILEF, apelacao ao TRF, embargos de declaracao, REsp, RE), com o prazo contado pelo motor local.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [crps | jef | pedilef | trf | embargos | resp | re | contrarrazoes]
---

Voce foi acionado pelo comando `/recurso-previdenciario` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** entregar o recurso cabivel contra a decisao recorrida, ou as contrarrazoes, dentro do prazo.

## PROTOCOLO
1. Acionar `recursos-previdenciarios` - ele identifica a via pela decisao recorrida (o argumento so adianta), pede o texto da decisao e a data da ciencia e so cita o que tem ancora em `context/`.
2. Prazo primeiro: `prazos-previdenciarios` conta os dias pelo motor local, com a data da ciencia e o rito. Prazo vencido: avisar na primeira linha, sem prometer relevacao, e mostrar as outras vias. Numero de dias que nao estiver em `context/lei/` entra como `[VERIFICAR]`, nunca de memoria. Contrarrazoes no CRPS: o prazo fatal conta da intimacao da interposicao (IN 128, art. 580; Regimento CRPS, art. 77); a data contada da interposicao (Decreto 3.048, art. 305, par. 1o, III) e so meta preventiva.
3. Recurso especial: pedir a data de publicacao do acordao recorrido. Publicado depois de 03/09/2026, vigencia da Lei 15.484/2026 (art. 7o; LC 95, art. 8o, par. 1o), o REsp exige topico especifico e fundamentado de relevancia, sob pena de inadmissao (CPC, art. 1.035-A, pars. 2o a 4o; Lei 15.484, art. 4o). Data desconhecida: incluir o topico.
4. Antes de ajuizar com recurso administrativo pendente, avisar que a acao judicial com pedido identico importa renuncia ao recurso administrativo.
5. Duvida sobre cabimento: apresentar as duas vias com o risco de cada uma e esperar a escolha do advogado.
6. Fechar pelo `validador-previdenciario` e pela `suprema-corte-previdenciaria`.

**Skill a acionar:** `recursos-previdenciarios`.
