---
name: jurisprudencia-estrategica-previdenciario
description: "Jurisprudencia selada do previdenciario: so cita tema, sumula ou ADI que esta em context/lei/temas-sumulas-prev.md, com a tese literal, o selo (✅ cita, 🔴 a confirmar, ❌ nunca) e o uso correto no caso. Mapeia o precedente a favor, o que a PFE pode opor e o numero que o plugin antigo usava com conteudo errado. Use quando o operador disser jurisprudencia, tem tema sobre isso, precedente, sumula, STF, STJ, TNU, tese firmada, ou quando estrategia, peticao, recurso ou parecer precisarem de precedente. Nao use para busca ao vivo de acordaos (juris-adv-os) nem para lei seca (base-legal-previdenciaria)."
---

# JURISPRUDENCIA-ESTRATEGICA-PREVIDENCIARIO

> Camada 1 (fundacao). O catalogo e fechado: o que nao esta em `temas-sumulas-prev.md` nao e citado como precedente, por mais conhecido que pareca.

## Entradas
- Recebe: tese ou ponto do caso que precisa de precedente (obrigatorio) · polo e beneficio (opcional; vem do quadro do caso)
- Chamada por: previdenciario-master · estrategia-de-caso-previdenciario · analise-trilateral-previdenciario · validador-previdenciario | Chama: anti-alucinacao-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/temas-sumulas-prev.md` (o item pelo numero - grep `Tema <N>` ou `mula <N>` e leia a faixa ate o proximo `###`; o arquivo grafa o numero do tema sem ponto, ex. `Tema 1102`)
- `context/metodologia-previdenciario.md` (secao 7.1, homonimos de tema; secao 8, proibicoes; secao 10, gate - grep a secao e leia a faixa)

## Objetivo
Entregar, para cada ponto do caso, o precedente que existe no arquivo, com a tese literal, o estado (transitado, sobrestado, embargos pendentes) e o limite do que ele decide.

## Metodologia
1. **Grep do numero no arquivo.** `grep -n 'Tema 1102' context/lei/temas-sumulas-prev.md` e ler a faixa: titulo, tese literal, nota. O numero sem tribunal nao basta: STF Tema 692 e STJ Tema 692 sao materias diferentes.
2. **Selo decide o uso.** ✅ cita com a tese literal. 🔴 cita so com o estado dito ("embargos pendentes desde 17/03/2026", "sobrestado", "superado") **e** depois de reverificado ao vivo para esta peca (fonte e data registradas); sem a reverificacao, sai como `[VERIFICAR]` (a confirmar) e o validador bloqueia a afirmacao firme. ❌ nunca cita para aquele conteudo.
3. **Citar so o que a tese decide.** A nota do arquivo diz o limite; respeitar. Ex.: o STJ Tema 905, item 3.2, fala em INPC depois da Lei 11.430/2006 e juros da poupanca; a faixa de 1% a.m. ate jun./2009 e o INPC desde set./2006 sao do Manual CJF, nao do tema.
4. **Fora do arquivo = nao citar.** Precedente que o advogado lembra e nao esta no arquivo: dizer que nao esta selado, oferecer a busca ao vivo pelo `juris-adv-os` (plugin vizinho, cross-link) e manter `[VERIFICAR]` ate a captura. Nunca transcrever tese, numero de processo, relator ou data de memoria.
5. **Contra-jurisprudencia.** Para cada ponto, dizer o que a PFE pode opor com item do mesmo arquivo (ex.: STJ Tema 692 na tutela revogada; STF Tema 1.300 contra o pedido de 100% automatico, independentemente do tempo de contribuicao, na incapacidade nao acidentaria) e como distinguir.
6. **Acionar** `anti-alucinacao-previdenciario` antes de devolver.

## Catalogo selado (resumo; o texto que vale e o do arquivo)

| Item | O que decide | Selo | Uso no caso |
|---|---|---|---|
| STF Tema 1.102 + ADIs 2.110/2.111 | art. 3 da Lei 9.876/1999 e cogente; sem opcao pela regra do art. 29, I e II, da Lei 8.213; modulacao: (a) irrepetiveis os valores percebidos por decisoes prolatadas ate 05/04/2024; (b) sem sucumbencia, custas e pericia nas acoes da tese pendentes nessa data | ✅ tese 🔴 embargos de 17/03/2026 pendentes | so defesa do segurado contra cobranca indevida dentro de (a) e (b); nunca fundamento de pedido |
| ADI 2.110 | carencia do salario-maternidade inconstitucional | ✅ | afasta carencia no salario-maternidade |
| STF Tema 1.300 | constitucional o calculo do art. 26, par. 2, III, da EC 103 na incapacidade permanente constatada apos a reforma | ✅ transitado 18/04/2026 | nao acidentaria = 60% + 2 pontos por ano acima de 20 (homem) ou 15 (mulher), podendo chegar a 100% ou passar dele, limitado ao teto (M3); a acidentaria tem 100% assegurado direto (EC 103, art. 26, par. 3, II) |
| STF Tema 1.419 | Selic do art. 3 da EC 113 nas condenacoes da Fazenda; embargos: restrita a redacao original, sem projecao ao regime da EC 136 | ✅ transitado 16/09/2026 | fatia dez./2021 a ago./2025; o indice posterior vem do Manual CJF |
| STF Tema 27 | 1/4 como requisito obrigatorio do BPC e inconstitucional | ✅ | tese sobre "inferior a 1/4"; aplicar a redacao atual ("igual ou inferior") e leitura, dita como tal |
| STF Tema 313 | sem decadencia na concessao inicial; 10 anos na revisao, inclusive beneficio anterior a MP 1.523/1997 (desde 01/08/1997) | ✅ | decadencia; nunca "acumulacao" |
| STF Tema 810 | art. 1-F da Lei 9.494: juros da poupanca validos fora do tributario; correcao pela poupanca inconstitucional | ✅ | regime das condenacoes assistenciais (BPC) por remissao do Manual |
| STF Tema 942 | conversao de tempo especial de **servidor** (RPPS) | ✅ so RPPS · ❌ RGPS | so em `rpps-servidor-publico` |
| SV 47 | honorarios incluidos ou destacados tem natureza alimentar | ✅ | requisicao dos honorarios; a pagina registra precedentes afastando os contratuais |
| STJ Tema 905 | item 3.2: previdenciario = INPC apos a Lei 11.430/2006 e juros da poupanca; item 3.1 para condenacoes administrativas | ✅ | fatia ate nov./2021, junto com o Manual |
| STJ Tema 1.030 | renuncia expressa ao excedente de 60 salarios minimos, inclusive ate 12 vincendas, para litigar no JEF | ✅ | valor da causa e alcada |
| STJ Tema 692 | reforma da tutela antecipada obriga devolver, por desconto de ate 30% do beneficio | ✅ | risco a avisar ao cliente antes da tutela; nunca "idade hibrida" |
| STJ Tema 1.007 | tempo rural remoto anterior a Lei 8.213 conta para a carencia da aposentadoria hibrida, sem recolhimento | ✅ | aposentadoria hibrida |
| STJ Tema 694 | ruido: 90 dB de 06/03/1997 a 18/11/2003, sem retroagir os 85 dB | ✅ | faixa historica; limite atual no Anexo IV com PPP |
| STJ Tema 416 | auxilio-acidente devido ainda que minima a lesao | ✅ | grau da lesao; nunca "pericia oficial" |
| STJ Tema 185 | 1/4 nao e o unico meio de provar a miserabilidade | ✅ | prova de miserabilidade no BPC |
| STJ Tema 1.031 | especialidade do vigilante, com prova da nocividade | ✅ texto 🔴 sobrestado | so com o estado dito |
| STJ Tema 999 | vida toda no STJ | ✅ texto 🔴 superado pelo STF | nunca fundamento; nunca "decadencia" |
| Sumula 111 STJ | honorarios nao incidem sobre vencidas apos a sentenca | ✅ | base dos honorarios |
| Sumula 178 STJ | INSS nao isento de custas na Justica Estadual | ✅ | custas no acidentario estadual |
| Sumula 105 STJ | sem honorarios em mandado de seguranca | ✅ so MS · ❌ custas | so em `mandado-seguranca-previdenciario` |
| TNU Sumula 41 | integrante urbano no nucleo nao descaracteriza, por si, o segurado especial | ✅ | rural |
| TNU Sumula 47 | incapacidade parcial: analisar condicoes pessoais e sociais | ✅ | pericia e aposentadoria por incapacidade |
| TNU Sumula 50 | conversao de especial em qualquer periodo | ✅ texto 🔴 anterior a EC 103 | nao alcanca trabalho depois de 13/11/2019 (EC 103, art. 25, par. 2) |
| TNU Sumula 79 | BPC: laudo social, auto de constatacao ou, inviabilizados, prova testemunhal | ✅ | prova no BPC |
| STF Tema 692 | ART do CONFEA | ❌ | nunca no previdenciario |
| STF Tema 1.124 | ITBI, sem tese | ❌ | nunca |
| STJ Tema 1.041 | perdimento de veiculo, cancelado | ❌ | nunca; conversao e EC 103, art. 25, par. 2 |
| STJ Tema 1.023 | prescricao do dano moral por exposicao ao DDT (servidores) | ❌ | nunca para BPC |

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha que o arquivo de jurisprudencia nao abriu: nenhum precedente sai como conferido, so `[VERIFICAR]` com a indicacao do `juris-adv-os`. Nunca preencher tese de memoria.

## Entrega obrigatoria final
- Mapa por ponto do caso: item · tese literal (trecho do arquivo) · selo e estado · o que decide e o que nao decide · o que a PFE pode opor · `[VERIFICAR]` para o que ficou fora do arquivo.

## Guard
Bloqueia: precedente fora do arquivo apresentado como firme; numero de tema sem tribunal; tese parafraseada alem do que o texto diz; item 🔴 sem o estado ou sem a reverificacao registrada; item ❌ no conteudo errado; revisao da vida toda oferecida como tese de concessao ou de revisao.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill jurisprudencia-estrategica-previdenciario - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
