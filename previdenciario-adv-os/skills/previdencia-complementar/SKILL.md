---
name: previdencia-complementar
description: "Triagem e encaminhamento em previdencia complementar (fundo de pensao e plano aberto), sobre a lei seca: CF art. 202 e art. 40, par. 14 a 16, LC 109/2001 e LC 108/2001. Separa entidade fechada e aberta, patrocinio publico e privado, e mapeia os institutos (beneficio proporcional diferido, portabilidade, resgate, autopatrocinio), direito acumulado, regulamento aplicavel, deficit, custeio e prescricao, com checklist de documentos. Sem conta de reserva, resgate ou beneficio na 2.0.0. Use quando o operador disser previdencia privada, previdencia complementar, fundo de pensao, entidade fechada, plano aberto, portabilidade, resgate, deficit do plano, Funpresp. Nao use para o RPPS do servidor (rpps-servidor-publico) nem para o beneficio do INSS."
---

# PREVIDENCIA COMPLEMENTAR

> Camada 4. Fundo de pensao e plano aberto: qual regra da lei seca vale e o que pedir, sem conta.

## Entradas
- Recebe: entidade e plano, fechada ou aberta (obrigatorio) · o que o cliente quer (beneficio, resgate, portabilidade, contestar deficit ou reajuste) (obrigatorio) · regulamento do plano, certificado, extratos, vinculo com o patrocinador (opcional, pedir se faltar)
- Chamada por: previdenciario-master · rpps-servidor-publico | Chama: memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/lc-109-2001.md` (arts. 1, 4, 8, 14, 15, 17, 21, 26, 27, 31, 36, 68 e 75 - grep o artigo e leia a faixa)
- `context/lei/lc-108-2001.md` (arts. 1, 3, 5 e 6 - grep o artigo e leia a faixa)
- `context/lei/cf88-seguridade.md` (art. 202, caput e par. 1 a 6; art. 40, par. 14 a 16) · `context/lei/ec-103-2019.md` (art. 33)

## Objetivo
Classificar a relacao (entidade, patrocinio, plano), apontar o dispositivo da lei seca que decide o pedido e a lista do que o advogado precisa obter, declarando o que depende de regulamento ou de norma nao capturada.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas (entidade, plano, patrocinador, situacao do vinculo, pedido) e esperar confirmacao.
2. Natureza: regime privado, complementar, autonomo em relacao ao RGPS, facultativo e baseado em reservas (CF, art. 202, caput; LC 109, art. 1). A concessao pela complementar nao depende da concessao pelo RGPS (LC 109, art. 68, par. 2), salvo o plano de beneficio definido patrocinado por ente publico instituido depois da LC 108, que exige o beneficio do regime a que o participante se filia pelo patrocinador (LC 108, art. 3, II).
3. Entidade:
   - fechada: acessivel so aos empregados ou servidores do patrocinador ou aos associados do instituidor (LC 109, art. 31); a do instituidor oferece so contribuicao definida (par. 2, II);
   - aberta: sociedade anonima, planos acessiveis a qualquer pessoa fisica (art. 36), individuais ou coletivos (art. 26).
4. Patrocinio publico (LC 108, art. 1; CF, art. 202, par. 3 a 6): carencia minima de 60 contribuicoes e cessacao do vinculo para o beneficio programado e continuado (art. 3, I); reajuste pelos regulamentos, vedado repasse de ganho de produtividade, abono e vantagens (par. unico); custeio pelo patrocinador e pelos participantes, com a contribuicao normal do patrocinador nunca acima da do participante (art. 6, par. 1); vedado aporte publico fora da condicao de patrocinador (art. 5).
5. Separar a trilha pela entidade antes dos passos 5 a 7: os arts. 14 a 17 e 21 da LC 109 estao na secao dos planos de entidades fechadas e nao se aplicam ao plano aberto.
   - fechada: institutos obrigatorios (art. 14) - beneficio proporcional diferido, portabilidade, resgate e autopatrocinio; portabilidade so com cessacao do vinculo com o patrocinador (par. 1), nao e resgate e os recursos nao passam pelo participante (art. 15, I e II); direito acumulado = reservas do participante ou reserva matematica, o que for mais favoravel (art. 15, par. unico);
   - aberta: planos individuais ou coletivos (art. 26) e direito a portabilidade e resgate total ou parcial nas condicoes do orgao regulador (art. 27); essas condicoes nao estao em context/: `[VERIFICAR]`.
6. Regulamento aplicavel: na fechada, alteracao vale para todos os participantes a partir da aprovacao pelo orgao regulador, respeitado o direito acumulado (art. 17); quem ja cumpriu os requisitos tem o regulamento da data em que ficou elegivel (par. unico); beneficio e direito adquirido quando implementadas todas as condicoes do regulamento (art. 68, par. 1). Na aberta, a regra de alteracao depende de norma do regulador nao capturada. Pedir sempre o regulamento vigente na adesao e o vigente na elegibilidade.
7. Deficit (so fechada): equacionado por patrocinadores, participantes e assistidos na proporcao das contribuicoes, sem prejuizo de acao regressiva contra quem deu causa (art. 21). Conferir a proporcao no plano de custeio; o calculo atuarial nao e feito aqui.
8. Fronteira trabalhista: contribuicoes do empregador, beneficios e condicoes do plano nao integram o contrato de trabalho (LC 109, art. 68; CF, art. 202, par. 2). Pedido contra o empregador vai para `trabalhista-adv-os`.
9. Servidor publico: complementar instituida por lei do ente, so contribuicao definida, com o teto do RGPS no RPPS (CF, art. 40, par. 15); ate a disciplina da relacao do ente com entidades abertas, so entidade fechada administra plano patrocinado pelo ente (EC 103, art. 33), e essa disciplina nao esta em context/: nao afirmar plano aberto para o servidor; quem ingressou antes do ato de instituicao so entra por opcao previa e expressa (CF, art. 40, par. 14 a 16). Efeito no RPPS vai para `rpps-servidor-publico`.
10. Prescricao: 5 anos para as prestacoes nao pagas nem reclamadas, sem prejuizo do beneficio, resguardados menores dependentes, incapazes e ausentes (LC 109, art. 75).
11. Fora de context/ (declarar, nao citar): regulamento do plano, normas do orgao regulador, tributacao de contribuicao e resgate (LC 109, art. 69 remete a lei nao capturada), jurisprudencia sobre consumidor, sucessao e competencia. Para jurisprudencia ao vivo, `juris-adv-os`; aqui sai `[VERIFICAR]`.
12. [redacao] Propor 2-3 caminhos (pedido administrativo a entidade com o regulamento na mao, portabilidade ou resgate, acao judicial), cada um com ganho e risco; o advogado escolhe.
13. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7) antes de entregar texto livre.

## Checklist de documentos
Regulamento do plano na adesao e na elegibilidade · estatuto da entidade · certificado de participante e proposta de inscricao · extratos de contribuicao e de saldo · plano de custeio e demonstracoes do deficit, se houver · prova da cessacao do vinculo com o patrocinador · resposta da entidade ao pedido administrativo · termo de opcao (servidor).

## Calculo
Sem script na 2.0.0. Reserva, resgate, beneficio, deficit e portabilidade nao sao apurados pelo plugin: valor informado pela entidade ou pelo advogado sai marcado "conta nao conferida por script".

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na entrega. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Classificacao (entidade, patrocinio, modalidade quando o regulamento disser) e os dispositivos da lei seca que decidem o pedido.
- Checklist de documentos marcado (tem ou falta), gaps declarados e os 2-3 caminhos com o escolhido.

## Guard
Nunca citar sumula, tema ou norma do orgao regulador que nao esteja em context/. Nunca afirmar regra que dependa do regulamento sem le-lo. Nunca calcular reserva, resgate ou beneficio. Nunca afirmar tributacao do resgate. Nunca tratar o plano como parte do contrato de trabalho.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill previdencia-complementar - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
