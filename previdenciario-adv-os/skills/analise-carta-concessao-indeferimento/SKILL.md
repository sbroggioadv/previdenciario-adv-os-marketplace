---
name: analise-carta-concessao-indeferimento
description: "Le a carta de concessao ou a comunicacao de indeferimento do INSS, extrai especie, DER, DIB, DIP, PBC, divisor, coeficiente, RMI e fundamentos da negativa, confere a RMI pelo script de RMI (divisor de 108, coeficiente, descarte, piso e teto), checa decadencia e prescricao e indica a via (recurso ao CRPS, revisao administrativa, acao judicial ou mandado de seguranca) com o prazo. Use quando o advogado anexar carta de concessao, decisao de indeferimento, memoria de calculo do INSS ou perguntar se o beneficio foi calculado certo. Nao use para redigir a peca (acao-revisional-rmi, peticao-inicial-previdenciaria, administrativo-inss-crps)."
---

# ANALISE DE CARTA DE CONCESSAO E DE INDEFERIMENTO

> Camada 3 (analise e prova). Le o ato do INSS, confere o numero e aponta a via, sem redigir a peca.

## Entradas
- Recebe: carta de concessao com memoria de calculo ou comunicacao de indeferimento (obrigatorio) · data da ciencia da decisao (obrigatorio, pelo prazo) · CNIS (via analise-cnis) · historico de creditos (revisao)
- Chamada por: previdenciario-master · triagem-dogmatica-previdenciario | Chama: prazos-previdenciarios (prazo correndo) · analise-cnis · analise-ppp-ltcat-aposentadoria-especial · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-rmi.md` (secoes 1 a 7 - formula, divisor, descarte, decadencia, prescricao, caso RMI-05, CAMPOS)
- `context/lei/ec-103-2019.md` (art. 26 - grep o artigo e leia a faixa)
- `context/lei/lei-8213-1991.md` (arts. 29, 41-A, 103 e 135-A - descarte linhas `(revogado)`)
- `context/lei/in-128-2022-inss.md` (arts. 228, 233, 574 a 577, 578, 580, 582 e 583 a 589)
- `context/lei/decreto-3048-1999.md` (art. 305, par. 1o - grep o artigo e leia a faixa)
- `context/metodologia-previdenciario.md` (secoes 5, 6, 9, 10 e 13)

## Objetivo
Diagnostico do ato do INSS: dados extraidos, erros com fundamento e efeito em reais, prazo e a via recomendada entre 2-3 caminhos.

## Metodologia
1. Pergunta critica antes de tudo: data da ciencia da decisao. Recurso ao CRPS em 30 dias da ciencia (Decreto 3.048, art. 305, par. 1o; IN 128, art. 580). Prazo correndo -> prazos-previdenciarios primeiro. Prazo vencido: avisar; o INSS nao pode recusar o recurso (IN 128, art. 578, par. 1o), mas a admissibilidade nao se promete.
2. Extrair sem interpretar: NB, especie, DER, DIB, DIP, DCB, regra aplicada, tempo e carencia computados, PBC, quantidade de salarios, divisor, media, coeficiente, fator (se houver), RMI. No indeferimento, copiar literalmente cada fundamento e o requisito apontado como nao atendido.
3. Devolver o quadro ao advogado em 3 a 6 linhas e esperar confirmacao.
4. Decisao formal: a decisao deve analisar as provas e cada requisito legal; justificativa so do sistema e insuficiente (IN 128, art. 574, pars. 1o e 2o). O INSS deve oferecer o beneficio mais vantajoso e verificar reafirmacao da DER (art. 577). Falha nesses pontos e materia de recurso ou de acao.
5. Arquivamento sem analise de merito por falta de documento: nao cabe recurso ao CRPS; cabe novo requerimento, com efeitos da nova data (IN 128, art. 578, pars. 2o e 3o).
6. Conferencia da concessao (rodar o script de RMI no modo `concessao`):
   - PBC: 100% desde 07/1994 (EC 103, art. 26), nunca pela Lei 13.846/2019; direito adquirido ate 13/11/2019 pela regra anterior (art. 29 e art. 3o da Lei 9.876, cogente).
   - Divisor minimo de 108: filiado ate 07/1994, aposentadoria que nao e por incapacidade permanente, fato gerador desde 05/05/2022 (Lei 8.213, art. 135-A; IN 128, art. 228).
   - Coeficiente: 60% + 2% por ano acima de 20 (H) / 15 (M e especial de 15); 100% no art. 20 e na incapacidade permanente acidentaria; acima de 100% e devido, limite e o teto (M3).
   - Descarte: so se a RMI subir; o tempo descartado nao conta para nada (art. 26, par. 6o).
   - Fator do art. 17 ou do direito adquirido: sem a tabua do IBGE sai formula (M7).
   - Piso (CF, art. 201, par. 2o) e teto do ano; periodos ou especial nao computados -> analise-cnis / analise-ppp-ltcat-aposentadoria-especial.
7. Revisao: rodar o script no modo `revisao` para decadencia (10 anos do dia 1o do mes seguinte ao primeiro recebimento; vence no dia de igual numero) e prescricao quinquenal. Decadencia sobre indeferimento, cancelamento ou cessacao: item 7 do gate de vigencia (ADI 6.096 nao capturada) -> "a confirmar".
8. Efeitos financeiros na via administrativa: recurso com novos elementos, no sentido do art. 587, produz efeitos da data de apresentacao (IN 128, art. 582); revisao a pedido produz efeitos da DPR, salvo sem novo elemento, na DIP com prescricao (arts. 585 e 586). Transformacao de aposentadoria apos o primeiro pagamento ou o saque do respectivo FGTS ou PIS e vedada, salvo as hipoteses dos pars. 1o a 3o do art. 589.
9. Diferencas sao nominais; correcao e juros pelo regime em fatias (verdade 5), conta de context/calculo-rpv.md, nunca "IPCA-E + Selic".
10. Propor 2-3 vias com ganho, risco e prazo (recurso ordinario as Juntas; revisao administrativa; acao judicial; mandado de seguranca: cabimento `[VERIFICAR]`, sem ancora no context/, decidido pela skill que redige) e esperar a escolha. A peca e de outra skill: administrativo-inss-crps, acao-revisional-rmi, peticao-inicial-previdenciaria ou mandado-seguranca-previdenciario, pelo master.
11. Texto ao cliente ou ao advogado: passada anti-IA com `context/escrita-humana.md`.

## Calculo
Script `calc_previdenciario_rmi.py`, localizado e rodado conforme `context/metodologia-previdenciario.md` (secao 13). Entrada em JSON.

```flags
--entrada   arquivo   opcional   caminho do JSON de entrada; ausente = stdin
--versao    flag      opcional   imprime a versao (2.0.1)
```

```campos
modo                         enum            sim                        concessao,revisao
especie                      enum            sim                        aposentadoria,incapacidade-permanente,outra
regra                        enum            se:modo=concessao          art15,art16,art17,art18,art19,art19-especial,art20,art21,adquirido-anterior,incapacidade-permanente,incapacidade-permanente-acidentaria
sexo                         enum            sim                        M,F
data_filiacao                data            sim                        primeira filiacao ao RGPS
fato_gerador                 data            sim                        DER ou DII
salarios_contribuicao        lista[decimal]  media:1de3                 desde 07/1994, corrigidos; obrigatoria se descartar=true
media                        decimal         media:1de3                 recusada sozinha no caso do art. 135-A (exit 3)
soma                         decimal         media:1de3                 com quantidade
quantidade                   inteiro         se:soma                    numero de salarios somados
tempo_contribuicao_anos      inteiro         se:modo=concessao          anos completos
tempo_contribuicao_meses  inteiro  nao  meses do CNIS; descarte exato
atividade_especial_anos      enum            se:regra=art19-especial|art21   15,20,25
descartar                    bool            nao                        padrao false
tempo_minimo_da_regra_anos   inteiro         se:descartar=true          tempo minimo a preservar
fator                        decimal         nao                        sem ele, art17 e adquirido-anterior saem em exit 3
teto                         decimal         nao                        ausente = tabela pela data do fato gerador
salario_minimo               decimal         nao                        ausente = tabela pela data do fato gerador
rmi_paga                     decimal         se:modo=revisao            -
rmi_devida                   decimal         se:modo=revisao            ou recalculada no modo concessao
media_acima_do_teto  bool  condicional  revisao com DIB no periodo de incorporacao do teto
datas_vencimento  objeto  nao  so revisao; AAAA-MM: AAAA-MM-DD do vencimento devido
dib                          data            se:modo=revisao            em concessao, se a DIB muda os limites do art. 29, §2º
data_primeiro_pagamento      data            se:modo=revisao            a DER nao a substitui
data_ajuizamento             data            se:modo=revisao            salvo data_requerimento_revisao
data_requerimento_revisao    data            alt:data_ajuizamento       pedido administrativo de revisao
abono                        bool            se:modo=revisao            beneficio com abono anual
```

Exatamente uma forma de media. Exit 0: usar o resultado e mostrar a memoria. Exit 2: perguntar de novo o dado errado. Exit 3: formula aberta com `[VERIFICAR]`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-rmi.md`, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Quadro extraido do ato; erros com fundamento e diferenca mensal; RMI conferida (ou formula aberta).
- Prazo (data limite) e decadencia; 2-3 vias com ganho, risco e prazo; skill que redige a escolhida.

## Guard
- Nunca "IPCA-E + Selic"; a Selic contra o INSS vem da EC 113, art. 3o (verdades 5 e 6). Nunca oferecer revisao que a verdade 1 declara inviavel.
- Nunca citar tema sem ancora em `temas-sumulas-prev.md`.
- Nunca RMI de cabeca: script ou conta aberta.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill analise-carta-concessao-indeferimento - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
