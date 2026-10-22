---
name: planejamento-previdenciario
description: "Planejamento de aposentadoria no RGPS: apura o tempo pelo script, testa direito adquirido, as transicoes da EC 103 (arts. 15 a 21) e a regra permanente, estima a RMI de cada regra cumprida e compara quando aposentar e quanto recebe, com a conta aberta quando falta dado. Use quando o operador disser planejamento previdenciario, quando posso me aposentar, qual regra e melhor, quanto vou receber, vale esperar mais um ano, /planejamento-previdenciario. Nao use para servidor publico (rpps-servidor-publico), para revisar beneficio ja concedido (acao-revisional-rmi) nem para BPC (bpc-loas-previdenciario)."
---

# PLANEJAMENTO PREVIDENCIARIO

> Camada 4. Nucleo comercial: qual regra vale mais, quando aposentar e quanto vai receber, com a conta por script e nunca de cabeca.

## Entradas
- Recebe: CNIS ou lista de periodos com datas (obrigatorio) · nascimento, sexo e primeira filiacao (obrigatorio) · data-alvo ou horizonte do pedido (obrigatorio) · PPP/LTCAT, salarios de contribuicao desde 07/1994, magisterio (opcional)
- Chamada por: previdenciario-master | Chama: analise-cnis · analise-ppp-ltcat-aposentadoria-especial · visual-law-previdenciario · memoria-de-caso-previdenciario · validador-previdenciario

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secoes 5, 6, 7, 8 e 13 - grep a secao e leia a faixa)
- `context/calculo-tempo.md` · `context/calculo-transicao.md` · `context/calculo-rmi.md` (secao CAMPOS e a conta aberta)
- `context/lei/ec-103-2019.md` (arts. 3, 15 a 21, 25 e 26 - grep o artigo e leia a faixa)
- `context/lei/in-128-2022-inss.md` (arts. 206, 207, 209, 228 e 577 - grep o artigo e leia a faixa)
- `context/lei/lc-142-2013-pcd.md` (arts. 3 e 8, so quando houver deficiencia)

## Objetivo
Entregar ao advogado a tabela regra a regra (cumpre ou nao, em que data, com que RMI) e as 2-3 rotas de aposentadoria com ganho e risco, cada numero vindo de script ou de conta aberta.

## Metodologia
1. [redacao] Devolver o quadro do caso em 3-6 linhas (idade, sexo, filiacao antes ou depois de 13/11/2019, tempo informado, especial, magisterio, objetivo) e esperar confirmacao. "Nao sei" vira lacuna, nunca suposicao.
2. Lacunas do CNIS (vinculo sem fim, indicador pendente, competencia abaixo do minimo) vao antes para `analise-cnis`; especial alegado vai para `analise-ppp-ltcat-aposentadoria-especial` e so entra com prova tecnica.
3. Tempo: rodar `calc_previdenciario_tempo.py`. Conversao so do trabalho prestado ate 13/11/2019 (EC 103, art. 25, par. 2); vinculo que cruza a data e fatiado pelo script.
4. Regras: rodar `calc_previdenciario_transicao.py` com a DER pretendida. Filiado depois de 13/11/2019 so tem a regra permanente (art. 19). Requisitos cumpridos ate 13/11/2019 = direito adquirido (art. 3). Para achar a data futura, `projecao_continua = true` com `projecao_ate`, e a premissa (contribuir todo mes no minimo) vai escrita na entrega.
5. Valor: para cada regra cumprida ou com data provavel, rodar `calc_previdenciario_rmi.py` no modo `concessao` com a `regra` daquela linha e conferir a memoria contra a tabela. Media de 100% desde 07/1994 (EC 103, art. 26, caput) e coeficiente da regra: 60% + 2 pontos por ano acima de 20 (art. 26, par. 2), acima de 15 para a mulher e o especial de 15 (par. 5); 100% no pedagio de 100% (par. 3, I, caso do art. 20, par. 2, II); media x fator no pedagio de 50% (art. 17). Direito adquirido ate 13/11/2019 segue a legislacao da data dos requisitos (art. 3, par. 2), nunca o coeficiente do art. 26. Divisor minimo de 108 para quem ja era filiado em 07/1994, com fato gerador desde 05/05/2022 (IN 128, art. 228).
6. Comparacao aberta quando ha fator: o pedagio de 50% (art. 17) sempre usa o fator; o direito adquirido segue a modalidade adquirida (EC 103, art. 3, par. 2): por tempo de contribuicao, media dos 80% maiores x fator (Lei 8.213, art. 29, I) ou, cumpridos os pontos do art. 29-C, sem fator; por idade, com fator ou pela opcao sem fator do art. 7 da Lei 9.876, sem exigencia de pontos; especial, media dos 80% maiores sem fator (Lei 8.213, art. 29, II). A tabua do IBGE nao esta capturada: regra com fator e sem o fator apurado sai em exit 3 com a formula, fica na tabela sem valor, com a lista dos dados que faltam, e nao entra no ranking. As modalidades sem fator (art. 29-C, art. 7 da Lei 9.876 e especial) nao dependem dele, mas `adquirido-anterior` fica fora do calculo automatico com ou sem `fator` (IN 128, art. 229): limite do script; ficam na comparacao com a conta aberta do `context/calculo-rmi.md` e o aviso "conta nao conferida por script". Nunca estimar o fator.
7. Melhor data: comparar aposentar ja com esperar ate a proxima mudanca (ponto e idade progressivos em 1o de janeiro, +2 pontos de coeficiente por ano extra, descarte de salarios). Quando as duas normalizacoes de M1 mudam o veredito, mostrar as duas datas.
8. [redacao] Propor 2-3 rotas, cada uma com ganho e risco. Exemplos: aposentar ja na regra X; esperar ate a data Y por coeficiente maior; complementar competencias abaixo do minimo antes de pedir (IN 128, art. 209, par. 1). O advogado escolhe.
9. Requerimento: lembrar que o INSS deve oferecer o beneficio mais vantajoso e pode reafirmar a DER com concordancia (IN 128, art. 577, I e II).
10. Pessoa com deficiencia: requisitos da LC 142 (art. 3) e percentuais (art. 8) entram como regra citada, sem conta por script na 2.0.3; dizer isso.
11. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7) antes de entregar o texto ao cliente; a tabela pode ir pelo `visual-law-previdenciario`.

## Calculo
Achar e rodar cada script pela secao 13 da metodologia; o bloco campos e o contrato da entrada JSON.

Script `calc_previdenciario_tempo.py` (`context/calculo-tempo.md`, secao 5):
```flags
# script: calc_previdenciario_tempo.py
--entrada  arquivo  opcional  JSON de entrada; sem ela, stdin
--versao  nenhum  opcional  imprime a versao
```
```campos
# script: calc_previdenciario_tempo.py
sexo  enum  obrigatorio  M | F
periodos  lista  obrigatorio  ao menos 1 periodo
periodos[].inicio  data  obrigatorio  AAAA-MM-DD
periodos[].fim  data  obrigatorio  AAAA-MM-DD
periodos[].tipo  enum  obrigatorio  comum | especial-15 | especial-20 | especial-25
periodos[].fonte  enum  obrigatorio  CNIS | CTPS | sentenca | PPP
periodos[].competencias_abaixo_do_minimo  lista de competencia  opcional  de 11/2019 em diante
novembro_2019_integral  bool  condicional  se abrange 13/11/2019 e continua; false = exit 3
```

Script `calc_previdenciario_transicao.py` (`context/calculo-transicao.md`, secao 7):
```flags
# script: calc_previdenciario_transicao.py
--entrada  arquivo  opcional  JSON de entrada; sem ela, stdin
--versao  nenhum  opcional  imprime a versao
```
```campos
# script: calc_previdenciario_transicao.py
nascimento  data  obrigatorio  AAAA-MM-DD
sexo  enum  obrigatorio  M | F
data_filiacao  data  obrigatorio  primeira filiacao ao RGPS
der  data  obrigatorio  data em que se verifica cada regra
periodos  lista  obrigatorio  ao menos 1 periodo
periodos[].inicio  data  sim  AAAA-MM-DD
periodos[].fim  data  sim  AAAA-MM-DD
periodos[].tipo  enum  sim  comum | especial-15 | especial-20 | especial-25
periodos[].fonte  enum  sim  CNIS | CTPS | sentenca | PPP
periodos[].competencias_abaixo_do_minimo  lista  nao  de 11/2019 em diante
novembro_2019_integral  bool  condicional  se abrange 13/11/2019 e continua; false = exit 3
professor  bool  opcional  padrao false; todo o tempo de magisterio exclusivo
projecao_continua  bool  opcional  padrao false; projeta competencias apos o ultimo periodo
projecao_ate  data  condicional  obrigatorio quando projecao_continua = true
```

Script `calc_previdenciario_rmi.py` (`context/calculo-rmi.md`, secao 6):
```flags
# script: calc_previdenciario_rmi.py
--entrada  arquivo  opcional  JSON de entrada; sem ela, stdin
--versao  nenhum  opcional  imprime a versao
```
```campos
# script: calc_previdenciario_rmi.py
modo  enum  obrigatorio  concessao | revisao
especie  enum  obrigatorio  aposentadoria | incapacidade-permanente | outra
regra  enum  condicional  obrigatorio em concessao: art15 | art16 | art17 | art18 | art19 | art19-especial | art20 | art21 | adquirido-anterior | incapacidade-permanente | incapacidade-permanente-acidentaria
sexo  enum  obrigatorio  M | F
data_filiacao  data  obrigatorio  primeira filiacao ao RGPS
fato_gerador  data  obrigatorio  DER (aposentadoria) ou DII (incapacidade)
salarios_contribuicao  lista  condicional  media 1; obrigatoria se descartar
media  decimal  condicional  forma de media 2; sozinha no art. 135-A = exit 3
soma  decimal  condicional  forma de media 3, com quantidade
quantidade  inteiro  condicional  com soma
tempo_contribuicao_anos  inteiro  condicional  em concessao; anos completos
tempo_contribuicao_meses  inteiro  nao  meses do CNIS; descarte exato
atividade_especial_anos  enum  condicional  15 | 20 | 25; em art19-especial e art21
descartar  bool  opcional  padrao false
tempo_minimo_da_regra_anos  inteiro  condicional  se descartar = true
fator  decimal  opcional  sem ele, art17 = exit 3; adquirido-anterior sempre exit 3
teto  decimal  opcional  ausente = tabela
salario_minimo  decimal  opcional  ausente = tabela
rmi_paga  decimal  condicional  obrigatorio em revisao
rmi_devida  decimal  condicional  obrigatorio em revisao
media_acima_do_teto  bool  condicional  revisao com DIB na incorporacao do teto
datas_vencimento  objeto  nao  so revisao; AAAA-MM: AAAA-MM-DD do vencimento devido
dib  data  condicional  revisao; concessao se a DIB muda os limites do art. 29, §2º
data_primeiro_pagamento  data  condicional  obrigatorio em revisao
data_ajuizamento  data  condicional  em revisao, salvo data_requerimento_revisao
data_requerimento_revisao  data  condicional  alternativa a data_ajuizamento
abono  bool  condicional  obrigatorio em revisao
```
Exit 0: usar e mostrar a memoria. Exit 2: perguntar de novo o dado recusado. Exit 3: `formula_aberta` com `[VERIFICAR]` e as duas leituras. Sem Python, script ausente ou outro exit: conta aberta pelo `context/calculo-<x>.md`, passo a passo, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na entrega. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Tabela por regra: aplicavel, cumpre na DER, data em que cumpre, coeficiente ou "media x fator", RMI ou formula, fundamento.
- As 2-3 rotas com ganho e risco, a rota escolhida pelo advogado e as premissas da projecao.
- Lista de lacunas e de `[VERIFICAR]` que o advogado precisa fechar antes do requerimento.

## Guard
Nunca numero de cabeca: tempo, pontos, data e RMI so por script ou conta aberta. Nunca converter dia trabalhado depois de 13/11/2019. Nunca ranquear regra que depende do fator sem a tabua. Pedagio de 50% e so do RGPS. Servidor publico vai para `rpps-servidor-publico`. Projecao e cenario, nunca promessa de beneficio.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill planejamento-previdenciario - plugin previdenciario-adv-os v2.0.3`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
