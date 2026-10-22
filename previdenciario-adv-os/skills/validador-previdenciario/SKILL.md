---
name: validador-previdenciario
description: "Crivo anti-alucinacao do plugin previdenciario, antes da suprema-corte-previdenciaria. Lista cada item citavel da peca (dispositivo, tema, sumula, indice, percentual, prazo, valor, numero de calculo), cruza um a um com o context/ (grep do artigo na lei seca, redacao vigente, tese literal no arquivo de jurisprudencia, numero igual ao JSON do script) e da veredito OK ou BLOQUEAR por item; o item sem fonte so segue como [VERIFICAR] explicito, nunca como citacao. Na duvida, bloqueia. Use quando o operador disser validar, confere as citacoes, isso existe, isso esta vigente, checa a peca antes de protocolar, e sempre no passo 8 do previdenciario-master. Nao redige nem corrige merito: devolve a tabela e o que precisa de checagem ao vivo."
---

# VALIDADOR-PREVIDENCIARIO

> Camada 1 (fundacao; a skill mais importante dela). Nao redige: e o crivo. Nada entra na peca sem ter sido cruzado com o arquivo capturado. A fonte e o arquivo, nunca a memoria de treino nem busca de IA isolada.

## Entradas
- Recebe: a minuta, o parecer ou a resposta a validar (obrigatorio) · JSON dos scripts que rodaram no caso (opcional; obrigatorio se a peca traz numero calculado) · `previdenciario/casos/<slug>.md` (opcional)
- Chamada por: previdenciario-master · suprema-corte-previdenciaria | Chama: base-legal-previdenciaria · jurisprudencia-estrategica-previdenciario · anti-alucinacao-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/INDICE.md` (tema -> arquivo -> artigo; secao 3, o que nao foi capturado - grep o tema e leia a linha)
- `context/lei/<diploma>.md` (cada artigo citado - grep o artigo e leia a faixa)
- `context/lei/temas-sumulas-prev.md` (cada tema ou sumula citado - grep o numero e leia a faixa)
- `context/metodologia-previdenciario.md` (secao 7, armadilhas; 7.1, homonimos; 8, contrato M1-M9; 10, gate de vigencia; 13, exit dos scripts - grep a secao e leia a faixa)

## Objetivo
Impedir que dispositivo revogado ou de outro diploma, tema com conteudo trocado, indice da fatia errada ou numero sem script cheguem ao juizo ou ao INSS, cruzando cada item com o arquivo antes de liberar.

## Metodologia
1. **Listar todos os itens citaveis**, numerados: dispositivos (diploma + artigo + paragrafo + inciso), temas, sumulas e ADIs, indices e taxas por periodo, percentuais e coeficientes, marcos de prazo (DER, DIB, DII, decadencia, prescricao, recurso), valores (piso, teto, salario minimo do ano, alcada, RPV) e todo numero calculado. Item implicito conta ("conforme a legislacao" para sustentar um prazo = item sem fonte).
2. **Dispositivo:** pelo `base-legal-previdenciaria`. Grep do artigo no arquivo do diploma nomeado; conferir que a linha usada nao e `(revogado) ~~...~~` (salvo redacao que rege periodo passado, com a data dita); conferir que o conteudo atribuido esta na faixa; conferir o homonimo (art. 3, 15, 17, 20, 26, 27-A, 32, 42). Citacao sem diploma nomeado = BLOQUEAR.
3. **Jurisprudencia:** pelo `jurisprudencia-estrategica-previdenciario`. Item fora de `temas-sumulas-prev.md` = BLOQUEAR como citacao, com a correcao `[VERIFICAR]` (passo 9), nunca OK. Selo ✅ = OK se a tese diz o que a peca diz; 🔴 = OK so com as duas coisas juntas: o estado escrito na peca ("embargos pendentes", "sobrestado") **e** a reverificacao do passo 7 registrada (fonte oficial consultada e data); faltando a reverificacao, BLOQUEAR; ❌ = BLOQUEAR. Numero de tema sem tribunal = BLOQUEAR.
4. **Indice, juros e fatia:** conferir a fatia pela competencia e pela fase (metodologia, secao 5, verdade 5; contrato M5 e M8). Previdenciario de set./2006 a nov./2021 = INPC e juros do Manual (competencia anterior a set./2006 = a faixa da tabela do Manual CJF, ex. IGP-DI de maio/1996 a ago./2006 - `context/lei/manual-cjf-2026-calculos-prev.md`, grep `set./2006`); dez./2021 a ago./2025 = Selic unica (EC 113, art. 3, redacao original); desde set./2025, antes do requisitorio = INPC + taxa legal com deducao do INPC; no requisitorio = Res. CJF 983/2026, art. 7. BPC = regime das condenacoes em geral. "IPCA-E ate 2021 e Selic depois" = BLOQUEAR.
5. **Numero calculado:** o numero da peca tem de ser o mesmo do JSON do script com exit 0 (mesmo valor, mesma data-base, mesmos parametros em `parametros_usados`). Exit 3 = a peca traz a `formula_aberta` e `[VERIFICAR]`, nunca o numero. Sem JSON: o numero so passa se a peca disser que saiu da conta aberta de `context/calculo-<x>.md` e que nao foi conferido por script. Numero sem nenhuma das duas origens = BLOQUEAR. Refazer de cabeca nao e conferencia.
6. **Valor de tabela:** salario minimo, teto e taxa legal do mes so pelo arquivo com fonte (`decreto-12797-2025-salario-minimo.md`, `portaria-interministerial-mps-mf-13-2026.md`, `manual-cjf-2026-calculos-prev.md`). Mes sem fonte = BLOQUEAR o numero; a correcao e a formula com `[VERIFICAR]`.
7. **Gate de vigencia:** item da metodologia, secao 10 (ADI 7.873; Manual CJF e resolucoes; Tema 1.102; piso e teto do ano; lei do art. 26 da EC 103; Anexo V da Portaria 990; cache de indices; art. 103 da Lei 8.213 com a ADI 6.096) e BLOQUEAR enquanto nao for reverificado para esta peca (fonte oficial consultada e data registradas na tabela); a correcao e tirar a afirmacao firme e marcar `[VERIFICAR]` (a confirmar). Escrever o estado na peca nao substitui a reverificacao.
8. **Acionar** `anti-alucinacao-previdenciario` sobre a peca inteira: qualquer frase que case com uma proibicao do contrato e BLOQUEAR, com a correcao indicada.
9. **Veredito por item: OK ou BLOQUEAR.** `[VERIFICAR]` nao e veredito nem citacao validada: e a forma corrigida de um item bloqueado (a peca deixa de afirmar e marca a lacuna). Veredito geral, nesta precedencia: BLOQUEADA (algum item ainda afirmado sem fonte, divergente, item 🔴 sem estado **ou** sem reverificacao registrada, ou item do gate de vigencia sem reverificacao registrada - um basta) > MINUTA COM PENDENCIAS (todo item bloqueado ja convertido em `[VERIFICAR]` explicito na peca; nao segue para protocolo nem para a corte como pronta ate a checagem ao vivo) > LIBERADA (todos OK, nenhum `[VERIFICAR]`).

## Por que o arquivo vence
A 0.1.0 deste plugin citava o STJ Tema 1.041 para a conversao de tempo especial depois da EC 103 (o tema e de perdimento de veiculo e esta cancelado), o STF Tema 692 para a revisao da vida toda (o tema e a ART do CONFEA) e vendia a vida toda como tese depois que o STF a declarou inviavel. Tudo isso passaria numa leitura de memoria: o numero "parecia" certo. E a tese nova do STF Tema 1.102 (embargos de novembro/2025), o Tema 1.419 com os embargos de maio/2026 e a Res. CJF 983/2026 sao posteriores ao treino do modelo. Por isso a fonte de verdade e o arquivo capturado em `context/lei/`, nao a memoria nem uma busca de IA isolada. Na duvida, `[VERIFICAR]` e checagem ao vivo; nunca chutar.

## Armadilhas que o crivo procura pelo nome
- Dispositivo que parece certo: conferir justamente os artigos mais citados (EC 103, art. 26; Lei 8.213, arts. 15, 25, 27-A, 60, 103), porque e neles que o paragrafo ou o diploma vizinho escapa.
- Homonimo: Lei 8.213 x Decreto 3.048 no art. 27-A (redacoes diferentes); Lei 9.876 x EC 113 no art. 3; EC 103 x Lei 10.259 no art. 17; EC 103 x LOAS no art. 20.
- Atribuicao de autoria: PBC de 100% e da EC 103, art. 26, nao da Lei 13.846/2019; a Selic contra a Fazenda e da EC 113, art. 3.
- Numero fiel ao erro da prosa: numero da peca que bate com a skill mas nao com o script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha qual anexo faltou: todo item que dependia dele e BLOQUEAR, com a correcao `[VERIFICAR]`, nunca OK. Sem o arquivo de jurisprudencia, nenhum precedente e liberado.

## Entrega obrigatoria final
- Tabela: # · item como esta na peca · onde consta (`context/...`, linha) · veredito (OK · BLOQUEAR) · motivo e correcao (para item sem fonte: `[VERIFICAR]` + onde checar ao vivo).
- Veredito geral (BLOQUEADA · MINUTA COM PENDENCIAS · LIBERADA) e a lista do que precisa de checagem ao vivo antes de a peca seguir para a `suprema-corte-previdenciaria`.

## Guard
BLOQUEAR: item que nao consta no context/; redacao riscada usada como vigente; diploma nao nomeado; tema fora do arquivo como firme; item 🔴 sem o estado **ou** sem a reverificacao registrada; item do gate de vigencia sem a reverificacao registrada; numero sem JSON nem conta aberta declarada; fatia de juros errada; revisao da vida toda como pedido. `[VERIFICAR]` marca lacuna, nao libera citacao. O validador nao reescreve a peca: devolve a correcao para a skill que redigiu. Toda entrega fecha pela `suprema-corte-previdenciaria`.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill validador-previdenciario - plugin previdenciario-adv-os v2.0.3`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
