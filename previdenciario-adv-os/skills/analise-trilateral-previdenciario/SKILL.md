---
name: analise-trilateral-previdenciario
description: "Testa o caminho escolhido pelos tres lados antes de redigir: o que sustenta o segurado, o que o INSS vai alegar (preliminares e merito) e como o caso chega ao juizo ou ao CRPS. Devolve uma matriz de forcas, fragilidades e respostas, e o ponto que decide o caso. Use quando o operador disser o que o INSS vai alegar, pontos fracos do caso, antecipar a defesa, como o juiz vai ver, teste de estresse da tese, ou quando a estrategia pedir. Nao use para escolher a via (estrategia-de-caso-previdenciario) nem para redigir a peca."
---

# ANALISE-TRILATERAL-PREVIDENCIARIO

> Camada C2. Antecipa a defesa do INSS e o olhar de quem decide, para a peca ja nascer respondendo.

## Entradas
- Recebe: quadro do caso confirmado e o caminho em analise (obrigatorio) · documentos, resultados de script, decisao do INSS (opcional)
- Chamada por: previdenciario-master · estrategia-de-caso-previdenciario | Chama: jurisprudencia-estrategica-previdenciario

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secoes 5 Verdades, 6 Distincao, 7 Armadilhas, 9 Relogio - grep a secao e leia a faixa)
- `context/lei/lei-8213-1991.md` (arts. 15, 25, 26, 27-A, 57, 86, 103 - grep o artigo e leia a faixa)
- `context/lei/lei-8742-1993-loas.md` (art. 20) · `context/lei/ec-103-2019.md` (arts. 25 e 26)
- `context/lei/temas-sumulas-prev.md` (so o que estiver la)

## Objetivo
Mostrar ao advogado, antes da redacao, onde o caso e forte, onde o INSS vai bater e qual fato decide.

## Metodologia
1. Partir do quadro confirmado. Se o quadro nao veio confirmado do master ou da estrategia, devolve-lo em 3 a 6 linhas e esperar.
2. Lado do segurado: fatos incontroversos, documentos que provam cada requisito, numero conferido por script, dispositivo com ancora no context/. Requisito sem prova vira fragilidade, nao forca.
3. Lado do INSS: listar o que um procurador alegaria neste caso, um item por linha, com a fonte. Checar sempre:
   - Preliminares: falta de requerimento administrativo previo do mesmo pedido; decadencia da revisao (`lei-8213-1991.md`, art. 103; STF Tema 313); prescricao das parcelas anteriores a 5 anos (art. 103, par. unico); coisa julgada; incompetencia pelo valor (alcada do JEF).
   - Merito: carencia ou qualidade de segurado (arts. 15, 25, 27-A; a metade do art. 27-A so reabre o computo, nao cumpre a carencia); tempo especial sem PPP amparado em laudo, ou conversao de tempo especial trabalhado depois de 13/11/2019 (`ec-103-2019.md`, art. 25, par. 2; o corte e a data do trabalho, nao a do pedido); capacidade residual na pericia; renda per capita acima de 1/4 no BPC (`lei-8742-1993-loas.md`, art. 20, par. 3); auxilio-acidente com aposentadoria (art. 86); coeficiente ou PBC errado (`ec-103-2019.md`, art. 26).
   - Para cada alegacao: a resposta do segurado e a prova que a sustenta, ou "sem resposta hoje".
4. Lado do juizo (ou do CRPS): o caso se explica em 30 segundos? Cada requisito tem documento indicado? O pedido e determinado e o valor saiu de script? Ha algo que gera desconfianca (tese ampla demais, numero sem memoria, jurisprudencia sem ancora)?
5. Jurisprudencia de qualquer dos lados so pela `jurisprudencia-estrategica-previdenciario`, do que esta em `temas-sumulas-prev.md`. O que nao esta la nao entra na matriz como fundamento.
6. Fechar com o ponto que decide o caso (o fato ou a prova de que tudo depende) e o que fazer antes de redigir para fortalece-lo.

## Caso modelo: cobranca depois da modulacao do STF Tema 1.102 (dados inventados)
Segurada recebeu diferencas por tutela concedida numa revisao do art. 29 contra o art. 3 da Lei 9.876; a tutela caiu e o INSS cobra a devolucao.
- Segurado: a modulacao (`temas-sumulas-prev.md`, STF Tema 1.102) torna irrepetiveis os valores percebidos por decisoes, definitivas ou provisorias, prolatadas ate 05/04/2024; e, nas acoes pendentes de conclusao nessa data, nao se cobram sucumbencia, custas e pericia. A data da decisao e a situacao da acao em 05/04/2024 decidem.
- INSS: decisao prolatada depois de 05/04/2024; ou repeticao e pagamento ja feitos, que ficam mantidos.
- Juizo: precisa ver a data da decisao que pagou e o andamento em 05/04/2024, com documento.
- Ponto que decide: data em que a decisao foi prolatada. Os embargos de 17/03/2026 seguiam pendentes na captura: `[VERIFICAR]` antes da peca.
- A tese de revisao em si nao se ajuiza: e inviavel (ADIs 2.110/2.111). A defesa e contra a cobranca.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na matriz. Alegacao sem fonte entra como `[VERIFICAR]`. Nunca preencher por suposicao.

## Entrega obrigatoria final
- Matriz em tres colunas (segurado, INSS, juizo) com forcas, fragilidades e resposta a cada alegacao do INSS, cada linha com a fonte.
- Ponto que decide o caso e a providencia antes da redacao.
- Lista do que ficou `[VERIFICAR]`.

## Guard
- Nunca esconder fragilidade do advogado; nunca estimar percentual de exito.
- Nunca usar tema ou sumula fora de `temas-sumulas-prev.md` nem com conteudo diferente do que esta la.
- Nunca montar argumento a favor da revisao do art. 29 contra o art. 3 da Lei 9.876.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill analise-trilateral-previdenciario - plugin previdenciario-adv-os v2.0.3`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
