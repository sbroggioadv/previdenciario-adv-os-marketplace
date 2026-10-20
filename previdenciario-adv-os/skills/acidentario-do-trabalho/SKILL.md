---
name: acidentario-do-trabalho
description: "Trilha acidentaria contra o INSS: nexo do acidente ou da doenca com o trabalho (arts. 19 a 21-A da Lei 8.213), CAT, auxilio por incapacidade temporaria e aposentadoria por incapacidade permanente acidentarios, auxilio-acidente sem carencia e sem piso, competencia da Justica Estadual e prescricao do art. 104. Calcula o beneficio pelo script de incapacidade. Use quando o operador disser acidente de trabalho, doenca ocupacional, CAT, NTEP, B91, B92, B94, auxilio-acidente, sequela do acidente. Nao use para indenizacao contra o empregador nem para estabilidade no emprego (trabalhista-adv-os) nem para incapacidade sem nexo com o trabalho (pericia-medica-previdenciaria)."
---

# ACIDENTARIO DO TRABALHO

> Camada 4. Beneficios acidentarios e auxilio-acidente contra o INSS, do nexo a conta.

## Entradas
- Recebe: relato do acidente ou da doenca e a atividade (obrigatorio) · categoria do segurado (obrigatorio) · CAT, laudos, decisao do INSS, datas DAT, DII e DER (opcional, pedir se faltar)
- Chamada por: previdenciario-master · pericia-medica-previdenciaria | Chama: analise-cnis · prazos-previdenciarios · peticao-inicial-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/lei-8213-1991.md` (arts. 18, 19, 20, 21, 21-A, 22, 26, 60, 61, 86, 104, 129 e 129-A - grep o artigo e leia a faixa)
- `context/lei/decreto-3048-1999.md` (arts. 42, 104 e 337; Anexo II, Lista C - grep o artigo e leia a faixa)
- `context/lei/ec-103-2019.md` (art. 26, par. 2, III, e par. 3, II)
- `context/lei/temas-sumulas-prev.md` (STJ Tema 416, STF Tema 1.300, STJ Sumula 178)
- `context/calculo-incapacidade.md` (secao 5, CAMPOS)

## Objetivo
Dizer se o caso e acidentario, qual beneficio cabe, quanto vale pelo script e por qual via e foro seguir, antes de qualquer peca.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas (o que aconteceu, quando, atividade, categoria do segurado, afastamento, decisao do INSS) e esperar confirmacao.
2. Prazo primeiro: cessacao ou indeferimento ha menos de 30 dias, ou recurso correndo, vai para `prazos-previdenciarios` antes de tudo.
3. Nexo. Acidente tipico (art. 19), doenca profissional ou do trabalho (art. 20) e equiparados (art. 21). Nexo tecnico epidemiologico: a pericia do INSS considera caracterizada a natureza acidentaria quando constata o nexo (art. 21-A); o CID e a atividade se conferem juntos na Lista C do Anexo II do Decreto 3.048 (art. 337, par. 3): grep o CID e o CNAE e leia a faixa; o INSS deixa de aplicar o nexo quando demonstrada a sua inexistencia (art. 21-A, par. 1). Sem nexo laboral, o caso nao e acidentario: seguir pela `pericia-medica-previdenciaria`.
4. CAT (art. 22): a empresa ou o empregador domestico comunica ate o primeiro dia util seguinte ao da ocorrencia e, em caso de morte, de imediato; na falta, o acidentado, os dependentes, o sindicato, o medico ou autoridade publica podem emitir (par. 2), sem o prazo do caput. Sem CAT, pedir a prova do evento.
5. Beneficio cabivel (o numero sai do script):
   - temporario acidentario: 91% do salario de beneficio, limitado a media dos 12 ultimos salarios de contribuicao (art. 61; art. 29, par. 10); DIB pela regra do art. 60 com DAT, DII e DER separadas;
   - permanente acidentario: 100% da media (EC 103, art. 26, par. 3, II). Sem nexo laboral e incapacidade constatada depois da EC 103, 60% + 2 pontos (art. 26, par. 2, III; STF Tema 1.300, limitado a esse corte); incapacidade anterior segue a regra preservada pelo art. 3 da EC 103, conferida pela DII;
   - auxilio-acidente: 50% do salario de beneficio, ate a vespera de qualquer aposentadoria ou o obito (art. 86, par. 1), devido desde o dia seguinte a cessacao do auxilio por incapacidade temporaria (par. 2), basta reducao da capacidade para o trabalho habitual, ainda que minima (STJ Tema 416). Perda auditiva so com nexo e reducao comprovada (par. 4).
6. Carencia: dispensada no auxilio-acidente (art. 26, I) e na incapacidade decorrente de acidente de qualquer natureza ou de doenca profissional ou do trabalho (art. 26, II). Qualidade de segurado continua exigida: conferir pela `analise-cnis`.
7. Quem tem direito ao auxilio-acidente: so os segurados dos incisos I, II, VI e VII do art. 11 (art. 18, par. 1; Decreto 3.048, art. 104, caput: empregado, domestico, avulso e segurado especial). Contribuinte individual e facultativo ficam fora.
8. Acumulacao: auxilio-acidente e inacumulavel com aposentadoria (art. 86, par. 2); salario ou outro beneficio, exceto aposentadoria, nao o prejudica (par. 3); na reabertura do auxilio temporario pelo mesmo acidente ele fica suspenso e depois volta (Decreto 3.048, art. 104, par. 6). As demais combinacoes estao em aberto: dizer isso, nao inventar.
9. Via e foro. Litigio acidentario: na via judicial, Justica dos Estados, rito sumarissimo, com prova da notificacao do evento ao INSS (art. 129, II); o procedimento judicial e isento de custas e de verbas de sucumbencia (art. 129, par. unico); sobre custas do INSS na Justica Estadual ha a STJ Sumula 178. Ler as duas e dizer ao advogado o alcance de cada uma, sem afirmar isencao por conta propria. Inicial de incapacidade com os requisitos e documentos do art. 129-A (indeferimento, prova do acidente, documentacao medica).
10. Prescricao acidentaria: 5 anos, observado o art. 103, contados do acidente (morte ou incapacidade temporaria) ou do reconhecimento da incapacidade permanente ou do agravamento (Lei 8.213, art. 104). Homonimo: o art. 104 do Decreto 3.048 trata do auxilio-acidente, nao de prescricao.
11. [redacao] Propor 2-3 caminhos (recurso administrativo, novo requerimento com a CAT, acao acidentaria na Justica Estadual), cada um com ganho e risco; o advogado escolhe. Redacao da inicial vai para `peticao-inicial-previdenciaria`.
12. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7) antes de entregar texto livre.

## Calculo
Achar e rodar o script pela secao 13 de `context/metodologia-previdenciario.md`; o bloco campos e o contrato da entrada JSON.
```flags
# script: calc_previdenciario_incapacidade.py
--entrada  arquivo  opcional  JSON de entrada (sem ela, entrada padrao)
--versao  nenhum  opcional  imprime a versao
```
```campos
# script: calc_previdenciario_incapacidade.py
especie  enum  obrigatorio  temporaria | permanente | auxilio-acidente
acidentaria  bool  obrigatorio  true so com nexo laboral
sexo  enum  obrigatorio  M | F
media_100  decimal  obrigatorio  media de 100% desde 07/1994, corrigida
media_12_ultimos  decimal  condicional  obrigatorio quando especie = temporaria
tempo_contribuicao_anos  inteiro  condicional  obrigatorio quando especie = permanente e acidentaria = false
dii  data  condicional  obrigatorio quando especie = permanente, ou especie = temporaria e empregado = false
dib  data  condicional  permanente e auxilio-acidente, salvo teto e salario_minimo; limites da DIB
dat  data  condicional  obrigatorio quando especie = temporaria
der  data  condicional  obrigatorio quando especie = temporaria
empregado  bool  condicional  obrigatorio quando especie = temporaria; true exceto domestico
assistencia_permanente  bool  opcional  padrao false; so com especie = permanente
salario_minimo  decimal  opcional  ausente = tabela pela data da DIB ou DII
teto  decimal  opcional  ausente = tabela pela mesma data
carencia  enum  opcional  sim | nao | indeterminada | dispensada; so ecoada em alerta
qualidade_segurado  enum  opcional  mantida | perdida | indeterminada; so ecoada em alerta
```
Exit 0: usar e mostrar a memoria. Exit 2: perguntar de novo o dado recusado. Exit 3: `formula_aberta` com o termo faltante e `[VERIFICAR]`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-incapacidade.md`, passo a passo, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na entrega. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Parecer curto: nexo (sim, nao ou a provar), beneficio cabivel, valor pelo script com a memoria, carencia e qualidade, foro, prescricao, documentos que faltam.
- Os 2-3 caminhos com ganho e risco e o escolhido.

## Guard
Nunca piso de um salario minimo no auxilio-acidente (Decreto 3.048, art. 42, par. unico). Nunca pedir auxilio-acidente cumulado com aposentadoria. Nunca auxilio-acidente para contribuinte individual ou facultativo. Nunca tratar acidente sem nexo laboral como acidentario. Indenizacao contra o empregador e estabilidade do art. 118 sao trabalhistas: encaminhar a `trabalhista-adv-os`, sem redigir.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill acidentario-do-trabalho - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
