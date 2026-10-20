---
name: recursos-previdenciarios
description: "Redige recurso previdenciario standalone e as contrarrazoes: recurso ao CRPS (ordinario as Juntas, especial as Camaras), recurso inominado no JEF, pedido de uniformizacao (PEDILEF, regional ou TNU), apelacao ao TRF, embargos de declaracao, recurso especial e recurso extraordinario. Identifica a via pela decisao recorrida, conta o prazo pelo motor e so cita o que tem ancora em context/. Use quando o operador disser recurso, recorrer, Turma Recursal, PEDILEF, TNU, apelacao, TRF, REsp, RE, embargos, contrarrazoes, CRPS, Junta de Recursos, /recurso-previdenciario. Nao use para a inicial nem para o cumprimento."
---

# RECURSOS-PREVIDENCIARIOS

> Camada C5 (judicial e recursos). Toda a cadeia recursal do segurado, administrativa e judicial, sem depender de outra skill para a estrutura.

## Entradas
- Recebe: decisao recorrida e data da ciencia ou da intimacao (obrigatorio) · orgao que decidiu (INSS, Junta de Recursos, Vara do JEF, Vara Federal, Turma Recursal, TRF) (obrigatorio) · peca da parte contraria, se for contrarrazoes · `previdenciario/casos/<slug>.md` (se existir)
- Chamada por: previdenciario-master | Chama: prazos-previdenciarios · analise-trilateral-previdenciario · jurisprudencia-estrategica-previdenciario · base-legal-previdenciaria · calculos-previdenciarios · visual-law-previdenciario · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/decreto-3048-1999.md` (arts. 305, par. 1o, II e III, 307 e 308 - grep o artigo e leia a faixa)
- `context/lei/in-128-2022-inss.md` (arts. 578, 579 e 580)
- `context/lei/lei-10259-2001-jef.md` (arts. 1o, 4o, 5o, 9o, 13, 14 e 15)
- `context/lei/temas-sumulas-prev.md` (so o item pedido, com a Nota; STJ Sumula 111 para honorarios)
- `context/lei/cpc-excertos-prev.md` (arts. 43 e 292) · `context/lei/cpc-recursos-prazos-prev.md` (arts. 183, 1.003, 1.009, 1.010, 1.022, 1.023, 1.029, 1.035 e 1.035-A)
- `context/lei/lei-9099-1995.md` (arts. 12-A, 41, 42, 43 e 55) · `context/lei/cf88-art5-102-105.md` (arts. 102, III e par. 3o; 105, III e pars. 2o e 3o)
- `context/lei/lei-15484-2026.md` (arts. 4o e 7o) · `context/lei/lc-95-1998-art8.md` (art. 8o, par. 1o) · `context/lei/regimento-crps-portaria-mps-125-2026.md` (arts. 77, 78, 80 e 112)
- `context/metodologia-previdenciario.md` (secoes 4, 6, 7, 7.1, 9 e 10) · `context/escrita-humana.md` (secoes 5 a 8)

## Objetivo
Entregar a peca recursal certa para a decisao recorrida, tempestiva pela conta do motor, com cada erro da decisao atacado em bloco proprio e fundamento conferido.

## Metodologia
1. [redacao] Devolver o quadro em 3 a 6 linhas: decisao, orgao, data da ciencia, o que se perdeu e o que se quer reformar (ou manter, em contrarrazoes). Esperar a confirmacao.
2. Prazo primeiro: acionar `prazos-previdenciarios` com a data da ciencia e o rito. Prazo vencido (pelo marco que vale como prazo fatal, nunca so pela meta preventiva): avisar na primeira linha, antes de qualquer outra coisa (metodologia, secao 4) e nao prometer relevacao.
3. Identificar a via pela tabela abaixo. Duvida sobre cabimento: apresentar as duas vias ao advogado com o risco de cada uma.
4. Mapear o adversario e o julgador com `analise-trilateral-previdenciario`: o que a decisao disse, o que o INSS vai sustentar, o que o orgao julgador costuma exigir.
5. [redacao] Propor 2 a 3 linhas recursais (ex.: atacar so o erro de direito × atacar direito e valoracao da prova × recorrer so da DIB), com ganho e risco; esperar a escolha.
6. Fundamento: dispositivo por `base-legal-previdenciaria` (nomeando o diploma; homonimos na metodologia, secao 7.1); jurisprudencia so por `jurisprudencia-estrategica-previdenciario`. Numero (RMI, atrasados, DIB) so por `calculos-previdenciarios`; regime de atualizacao em fatias (metodologia, verdade 5).
7. Redigir pela estrutura comum, na voz do escritorio (`estilo-juridico-previdenciario`). Quadro comparativo, se ajudar, por `visual-law-previdenciario`, como anexo.
8. [redacao] Passada anti-IA com `context/escrita-humana.md` secao 7; depois `validador-previdenciario` e `suprema-corte-previdenciaria`. Gravar prazo e protocolo em `memoria-de-caso-previdenciario`.

### Qual via
| Decisao recorrida | Via | Ancora em context/ |
|---|---|---|
| INSS (indeferimento, cessacao, revisao) | recurso ordinario as Juntas de Recursos; 30 dias da ciencia | IN 128, art. 578; Decreto 3.048, art. 305, I e par. 1o, II |
| Junta de Recursos (fora da alcada) | recurso especial as Camaras de Julgamento; 30 dias | IN 128, arts. 579 e 580 |
| Recurso do INSS no CRPS | contrarrazoes em 30 dias; prazo fatal da intimacao da interposicao; a data contada da interposicao (Decreto) so como meta preventiva, ver `prazos-previdenciarios` | IN 128, art. 580; Regimento CRPS, arts. 77, 78 e 80; Decreto 3.048, art. 305, par. 1o, III |
| Sentenca de Vara do JEF | recurso inominado a Turma Recursal; so de sentenca definitiva, salvo medida cautelar; 10 dias da ciencia, uteis | Lei 10.259, arts. 1o, 4o e 5o; Lei 9.099, arts. 12-A, 41 e 42 |
| Acordao de Turma Recursal divergente de outra TR em direito material | PEDILEF: mesma regiao -> reuniao conjunta; regioes diferentes ou contra sumula/jurisprudencia dominante do STJ -> Turma de Uniformizacao | Lei 10.259, art. 14, pars. 1o e 2o |
| Orientacao da Turma de Uniformizacao contra sumula ou jurisprudencia dominante do STJ | provocacao do STJ | Lei 10.259, art. 14, par. 4o |
| Questao constitucional no JEF | recurso extraordinario | Lei 10.259, art. 15 |
| Sentenca de Vara Federal (ou estadual delegada) | apelacao ao TRF; 15 dias | CPC, arts. 1.003, par. 5o, 1.009 e 1.010; CF, art. 109, par. 4o |
| Acordao de TRF | recurso especial (lei federal) ou extraordinario (Constituicao); 15 dias | CF, arts. 105, III, e 102, III; CPC, arts. 1.003, par. 5o, e 1.029 |
| Decisao judicial com omissao, contradicao, obscuridade ou erro material | embargos de declaracao; 5 dias | CPC, arts. 1.022 e 1.023 |
| Acordao do CRPS com o mesmo vicio ou ambiguidade | embargos de declaracao; 30 dias da ciencia; erro material a qualquer tempo | Regimento CRPS, art. 92, IV e par. 2o |

Regras que mudam a estrategia: acao judicial com pedido identico importa renuncia ao recurso administrativo (Decreto 3.048, art. 307) - avisar antes de ajuizar com recurso pendente. Recurso tempestivo contra Junta ou Camara tem efeito suspensivo e devolutivo (art. 308). O INSS nao pode recusar o recebimento do recurso (IN 128, art. 578, par. 1o); a admissibilidade do intempestivo e do CRPS: intempestividade e causa de nao conhecimento (Regimento CRPS, art. 112, I), e a relevacao so cabe com liquidez e certeza inequivocas (pars. 1o e 2o), sem diligencia (par. 8o): examinar se o caso se encaixa, nunca prometer. Arquivamento sem merito por falta de documento nao tem recurso: novo requerimento (art. 578, pars. 2o e 3o). No JEF nao ha prazo diferenciado para o INSS, nem para recorrer (Lei 10.259, art. 9o), e nao ha reexame necessario (art. 13).

### Prazos judiciais
Apelacao, REsp, RE e suas contrarrazoes: 15 dias; embargos de declaracao: 5 dias (CPC, arts. 1.003, par. 5o, e 1.023); o INSS conta em dobro fora do JEF (art. 183). JEF: recurso inominado em 10 dias da ciencia da sentenca e contrarrazoes a ele em 10 dias da intimacao (nunca 15), em dias uteis (Lei 9.099, arts. 42, caput e par. 2o, e 12-A), sem prazo diferenciado para o INSS (Lei 10.259, art. 9o). Prazo do PEDILEF: nao capturado, `[VERIFICAR]`. A contagem dos dias e sempre do motor (`prazos-previdenciarios`).

### Estrutura comum
```
PETICAO DE INTERPOSICAO - orgao de origem; recorrente; via; pedido de remessa
RAZOES
I.   SINTESE DA DECISAO RECORRIDA - o que decidiu, em 1 paragrafo
II.  TEMPESTIVIDADE - data da ciencia e data-limite pela saida do motor
III. CABIMENTO - via e ancora da tabela; no PEDILEF, a tese do acordao e a do
     paradigma lado a lado, com a identidade de fato e de direito
     So no REsp: III-A. RELEVANCIA DA QUESTAO DE DIREITO FEDERAL - topico proprio
IV.  RAZOES DE REFORMA - um bloco por erro: fato fixado -> questao -> norma ->
     aplicacao -> consequencia no resultado
V.   PEDIDOS - conhecimento e provimento; o que muda (DIB, RMI, beneficio);
     atualizacao em fatias; honorarios so na via judicial e so com ancora
     de cabimento naquele rito (sem ancora: [VERIFICAR]); no JEF, so o
     recorrente vencido paga (Lei 9.099, art. 55); a STJ Sumula 111
     so delimita a base nas acoes previdenciarias (vencidas ate a sentenca).
     No recurso ao CRPS, sem ancora em context/, nao pedir honorarios
```
Recurso especial: antes de redigir, pedir a data de publicacao do acordao recorrido. A Lei 15.484/2026 (DOU de 04/08/2026) vigora apos 30 dias (art. 7o), contados com a data da publicacao e o ultimo dia (LC 95, art. 8o, par. 1o): vigencia em 03/09/2026. Acordao publicado depois dela exige o topico especifico e fundamentado de relevancia (CPC, art. 1.035-A, par. 2o; Lei 15.484, art. 4o); sem ele, o recurso e inadmitido (par. 3o). Data desconhecida ou no proprio dia 03/09: incluir o topico. No topico, dizer se ha relevancia presumida (par. 4o; CF, art. 105, par. 3o, ex.: valor da causa acima de 500 salarios minimos, acordao contra jurisprudencia dominante do STJ) e, mesmo assim, fundamenta-la. Separar questao de direito de reexame de prova; os fatos sao os fixados no acordao. O enunciado do STJ sobre reexame de prova nao esta em context/: citar so depois de conferido (`[VERIFICAR]`). Recurso extraordinario: violacao direta da Constituicao, com a repercussao geral demonstrada (CF, art. 102, par. 3o; CPC, art. 1.035). Embargos: apontar o vicio, nao rediscutir o merito.

### Contrarrazoes
Mesma tabela de vias e o prazo correspondente. Estrutura: sintese do recurso do INSS · preliminares de nao conhecimento (intempestividade, inovacao, falta de cabimento) · resposta ponto a ponto, cada argumento do INSS com a norma e o fato que o afastam · pedido de nao provimento e de manutencao da decisao.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na peca. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Peticao de interposicao + razoes (ou contrarrazoes), prontas para o advogado revisar e protocolar.
- Fora da peca, ao advogado: data-limite com a saida do motor, lista de `[VERIFICAR]` e itens do gate de vigencia tocados.

## Guard
- Nunca dar numero de dias de prazo sem ancora nem contar dias de cabeca.
- Nunca citar tema ou sumula fora de `context/lei/temas-sumulas-prev.md`, nem com o conteudo que a 0.1.0 lhes dava (metodologia, secao 8; `anti-alucinacao-previdenciario`).
- Nunca recorrer com tese que o `CLAUDE.md` lista como inviavel; nunca pedir atualizacao em duas fases simplificadas no lugar do regime em fatias por competencia (verdade 5).
- Nunca omitir ao advogado o risco do art. 307 do Decreto 3.048 quando houver recurso administrativo pendente.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro da peca:
`Entregue pela skill recursos-previdenciarios - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
