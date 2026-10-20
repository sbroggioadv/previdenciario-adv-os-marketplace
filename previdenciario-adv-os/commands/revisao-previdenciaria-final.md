---
description: Roda so a Suprema Corte (R1 a R4, com a checagem anti-IA no R4) sobre peca, recurso, parecer, calculo ou requerimento previdenciario ja produzido.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, AskUserQuestion
argument-hint: [caminho do arquivo a revisar, opcional]
---

Voce foi acionado pelo comando `/revisao-previdenciaria-final` do plugin previdenciario-adv-os.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** auditar um documento que ja existe e devolver o veredito por revisora, com o trecho e o anexo de cada achado.

## PROTOCOLO
1. Acionar `suprema-corte-previdenciaria` - R1 fatos, via e competencia contra o quadro confirmado; R2 base legal na redacao vigente com o diploma nomeado; R3 tema ou sumula so com selo verde no anexo; R4 forma, prazo, calculo conferido com o JSON do script e checagem anti-IA objetiva.
2. Sem caminho no argumento: pedir o arquivo ou o texto colado. Documento ausente nao e revisado por suposicao.
3. Antes da Corte, rodar o `validador-previdenciario` sobre cada item citavel do documento.
4. Numero de calculo sem o JSON do script correspondente nao passa no R4: refazer a conta pela `calculos-previdenciarios` ou marcar "conta nao conferida por script".
5. Veredito por revisora: OK, CORRIGIR ou REPROVA. A Corte aponta, nao reescreve o documento sem pedido do advogado.

**Skill a acionar:** `suprema-corte-previdenciaria`.
