---
name: analise-ppp-ltcat-aposentadoria-especial
description: "Analisa PPP e LTCAT para reconhecer tempo especial: agente nocivo, habitualidade e permanencia, EPI (IN 128, art. 291), ruido pela faixa da data do periodo, e converte em comum so o tempo trabalhado ate 13/11/2019, fatiando o vinculo que cruza a data, pelo script de tempo. Use quando o advogado anexar PPP, LTCAT ou laudo ambiental, perguntar por aposentadoria especial, conversao de tempo especial, vinculo com IEAN no CNIS ou quesitos de pericia tecnica. Nao use para pericia medica de incapacidade (pericia-medica-previdenciaria) nem para conversao de servidor publico (rpps-servidor-publico)."
---

# ANALISE DE PPP, LTCAT E APOSENTADORIA ESPECIAL

> Camada 3 (analise e prova). Decide o que e tempo especial provado e quanto ele vale convertido, sempre pela data em que cada dia foi trabalhado.

## Entradas
- Recebe: prova da epoca de cada periodo (obrigatorio; IN 128, arts. 272 e 274): PPP emitido a partir de 18/07/2002 ou antigo formulario emitido ate 31/12/2003, com o laudo no ruido e, para periodos de 14/10/1996 a 31/12/2003, com LTCAT ou demonstracao do art. 277, V, para qualquer agente (art. 274, III, a); ate 28/04/1995 por categoria profissional, a CTPS basta quando ela tem a informacao do enquadramento (art. 274, par. 1o) · LTCAT ou demonstracao ambiental (quando o PPP for incompleto) · CNIS com os vinculos e indicadores (obrigatorio; via analise-cnis) · sexo do segurado (obrigatorio)
- Chamada por: previdenciario-master · analise-cnis · planejamento-previdenciario · calculos-previdenciarios | Chama: memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-tempo.md` (secoes 1 a 6 - fatias F1/F2/F3, multiplicadores, caso TEMPO-04, CAMPOS)
- `context/lei/ec-103-2019.md` (art. 25, par. 2o - grep o artigo e leia a faixa)
- `context/lei/decreto-3048-art188p-tabela.md` (multiplicadores do art. 188-P, par. 5o)
- `context/lei/lei-8213-1991.md` (arts. 57, pars. 3o a 5o, e 58, pars. 1o a 4o - descarte linhas `(revogado)`)
- `context/lei/in-128-2022-inss.md` (arts. 265, 268, 272, 274, 276, 277, 281, 291 e 292 - grep o artigo e leia a faixa)
- `context/lei/portaria-990-2022-anexo-v-indicadores-cnis.md` (grep `IEAN`)
- `context/lei/temas-sumulas-prev.md` (STJ Tema 694; STJ Tema 1031; TNU Sumula 50; STF Tema 942)
- `context/metodologia-previdenciario.md` (secoes 5, 6, 7, 8 e 13)

## Objetivo
Quadro por periodo (agente, prova, EPI, habitualidade, enquadravel ou nao) e o tempo especial bruto e convertido saido do script, com o que falta provar.

## Metodologia
1. Prova da exposicao: PPP emitido pela empresa com base em LTCAT (Lei 8.213, art. 58, par. 1o); o PPP adequadamente preenchido e amparado em laudo dispensa o LTCAT (IN 128, art. 281, par. 4o). PPP incompleto, sem responsavel pelos registros ambientais ou contraditorio: pedir o LTCAT ou demonstracao do art. 277 e conferir os elementos do art. 276.
2. Por periodo, extrair: funcao e setor, agente (quimico, fisico, biologico ou associacao), intensidade ou concentracao medida, tecnica de medicao, EPC e EPI, responsavel tecnico e assinatura (art. 281, pars. 1o e 2o). Antes de apontar campo vazio como falha, aplicar as dispensas por data do art. 281, par. 4o-A (responsavel pelos registros ambientais fora do ruido e EPC ate 13/10/1996; EPI ate 03/12/1998; codigo GFIP ate 31/12/1998). Fora delas, campo vazio vira lacuna; nada se completa por presuncao.
3. Habitualidade e permanencia: trabalho nao ocasional nem intermitente (Lei 8.213, art. 57, par. 3o; IN 128, art. 268). Para periodos ate 28/04/1995 a permanencia nao e exigida, inclusive no enquadramento por categoria profissional (art. 268, par. 2o).
4. Agente nocivo: a relacao e do Anexo IV do Decreto 3.048 (Lei 8.213, art. 58; IN 128, art. 268, par. 1o). Ler a linha do agente no anexo; o Anexo XVI da IN 128 nao esta capturado (gap).
5. Ruido: ler em IN 128, art. 292, a faixa vigente na DATA do periodo e a tese do STJ Tema 694 (sem retroacao do patamar posterior). Nunca escrever o limite de memoria; o limite do Anexo IV nao e automatizado. Valores multiplos para um unico periodo laborado ate 02/12/1998: art. 292, par. 2o (com valores acima e abaixo, exige histograma ou memoria de calculo).
6. EPI: so considerado em demonstracoes emitidas a partir de 03/12/1998 e se comprovadamente eliminar ou neutralizar a nocividade, com os registros dos incisos I a V do art. 291 da IN 128 (hierarquia EPC antes de EPI, uso ininterrupto, CA valido, troca comprovada, higienizacao). Falta de registro = ponto de defesa. Ruido acima do limite: a declaracao de EPI eficaz no PPP nao descaracteriza o especial (art. 291, par. 2o).
7. Vigilante: STJ Tema 1031 esta sobrestado na fonte -> citar como "a confirmar". STF Tema 942 e de servidor (RPPS): nunca regra do RGPS.
8. Conversao em comum: so do tempo trabalhado ate 13/11/2019, pela data do trabalho e nao pela da filiacao (EC 103, art. 25, par. 2o; Decreto 3.048, art. 188-P, par. 5o). Vinculo que cruza a data e fatiado. Multiplicadores so da tabela (15, 20 e 25 anos; mulher e homem). TNU Sumula 50 nao alcanca trabalho posterior a 13/11/2019. Comum concomitante com especial comprovado: o dia conta como especial (IN 128, art. 265).
9. Confirmar com o advogado o quadro por periodo (3 a 6 linhas) antes de rodar o script.
10. Rodar o script de tempo (secao Calculo) e mostrar a memoria; as duas normalizacoes de F1+F2 com F3 saem com `[VERIFICAR]`. Requisito da aposentadoria especial ou de transicao: devolver o tempo a calculos-previdenciarios (script de transicao), nao decidir aqui.
11. Havendo prova a produzir, propor 2-3 estrategias com ganho e risco (ex.: pedir LTCAT ou demonstracao do art. 277 a empresa; pedir retificacao do PPP; pericia tecnica judicial) e esperar a escolha. Quesitos de pericia tecnica (judicial): presenca do agente no ambiente; intensidade por metodologia; habitualidade e permanencia; EPI e os itens do art. 291; ruido pela faixa da data. Redigir na voz do escritorio (estilo-juridico-previdenciario) e passar `context/escrita-humana.md` antes de entregar.
12. Pendencias praticas: empresa extinta -> pedir pela sucessora. Na via administrativa nao se aceita laudo de atividade diversa (salvo mesmo setor), de equipamento ou setor similar, de localidade diversa ou de empresa diversa (IN 128, art. 277, par. unico); laudo similar na via judicial so com fonte propria verificada, nunca por presuncao. O trabalhador pode solicitar a retificacao do PPP a empresa (art. 281, par. 6o); nao a faz sozinho.

## Calculo
Script `calc_previdenciario_tempo.py`, localizado e rodado conforme `context/metodologia-previdenciario.md` (secao 13). Entrada em JSON.

```flags
--entrada   arquivo   opcional   caminho do JSON de entrada; ausente = stdin
--versao    flag      opcional   imprime a versao (2.0.0)
```

```campos
sexo                                        enum                sim                          M,F
periodos                                    lista               sim                          ao menos 1 periodo
periodos[].inicio                           data                sim                          -
periodos[].fim                              data                sim                          -
periodos[].tipo                             enum                sim                          comum,especial-15,especial-20,especial-25
periodos[].fonte                            enum                sim                          CNIS,CTPS,sentenca,PPP
periodos[].competencias_abaixo_do_minimo    lista[competencia]  nao                          so de 11/2019 em diante; padrao []
novembro_2019_integral                      bool                se:periodo-cruza-13/11/2019   false leva a exit 3
```

Exit 0: usar o resultado e mostrar a memoria. Exit 2: perguntar de novo o dado errado. Exit 3 (competencia 11/2019 so em parte): as duas contas com `[VERIFICAR]`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-tempo.md`, passo a passo, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita (ex.: sem a tabela do art. 188-P, sem conversao). Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Quadro por periodo: agente, medicao, prova (PPP/LTCAT), EPI, habitualidade, enquadravel (sim / nao / depende de prova), fundamento.
- Tempo especial bruto, convertido (so ate 13/11/2019) e total, com a memoria do script ou a marca "conta nao conferida por script".
- Lista do que falta provar e de quem pedir; quesitos tecnicos, quando houver pericia.

## Guard
- Nunca converter um dia posterior a 13/11/2019; nunca decidir pela data da filiacao.
- Nunca so fatores 1,4/1,2: a tabela tem 15, 20 e 25 anos.
- Nunca tema de tribunal como fonte da regra de conversao: a regra e a EC 103, art. 25, par. 2o (metodologia, secao 8).
- Nunca pedir especial so pelo IEAN, sem PPP ou laudo.
- Nunca limite de ruido de memoria.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill analise-ppp-ltcat-aposentadoria-especial - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
