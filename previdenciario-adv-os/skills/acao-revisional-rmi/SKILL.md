---
name: acao-revisional-rmi
description: "Redige a acao revisional da renda mensal inicial de beneficio ja concedido pelo INSS: confere primeiro a decadencia e a prescricao pelo script de RMI, recalcula a RMI (media desde 07/1994, divisor minimo de 108, coeficiente da EC 103, descarte, teto e piso), apura as diferencas nao prescritas e redige a peca com o pedido de correcao pelo regime em fatias. Use quando o operador disser revisao de beneficio, revisar a RMI, beneficio calculado errado, carta de concessao com valor errado, incluir tempo ou salarios no calculo. Nao use para concessao inicial (peticao-inicial-previdenciaria) nem para conferir a carta sem acao (analise-carta-concessao-indeferimento)."
---

# ACAO REVISIONAL DE RMI

> Camada 5. Nenhuma linha de peca antes de decadencia e prescricao conferidas pelo script ou, nas excecoes do passo 2 e sem script, por conta aberta conferida pelo advogado.

## Entradas
- Recebe: carta de concessao (NB, especie, DIB, RMI, data do primeiro pagamento) (obrigatorio) · CNIS e salarios de contribuicao (obrigatorio para recalcular) · erro apontado pelo cliente ou pela `analise-carta-concessao-indeferimento` (opcional)
- Chamada por: previdenciario-master · analise-carta-concessao-indeferimento | Chama: analise-cnis · calculos-previdenciarios · anti-alucinacao-previdenciario · estrategia-de-caso-previdenciario · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-rmi.md` (secoes 1, 2, 4 e 6) e `context/calculo-valor-causa.md` (secao 6)
- `context/lei/lei-8213-1991.md` (arts. 29-B, 41-A, 103, 129 e 135-A - grep o artigo e leia a faixa; descartar linhas `(revogado)`)
- `context/lei/ec-103-2019.md` (art. 26) · `context/lei/cc-excertos-prev.md` (art. 132, par. 3) · `context/lei/lei-9099-1995.md` (art. 55)
- `context/lei/temas-sumulas-prev.md` (STF Tema 313; ADIs 2.110/2.111; STF Tema 1.102; STJ Sumula 111) · `context/escrita-humana.md`

## Objetivo
Dizer ao advogado se a revisao ainda e possivel e quanto ela vale; sendo possivel e vantajosa, entregar a peca.

## Metodologia
1. Decadencia (bloqueante): script de RMI no modo `revisao`. Dez anos do dia 1 do mes seguinte ao primeiro recebimento (Lei 8.213, art. 103, I), vencendo no dia de igual numero ou, sem expediente, no util seguinte (CC, art. 132, par. 3 e 1). Concessao antes da MP 1.523/1997: de 01/08/1997 (STF Tema 313). Indeferimento, cancelamento ou cessacao (art. 103, II; ADI 6.096 nao capturada): `[VERIFICAR]` (gate de vigencia, item 7). `decadente` true: parar, avisar o advogado, nao redigir; null: nao parar; conferir o dia.
2. Prescricao: antes do corte, perguntar se o titular e menor, incapaz ou ausente; contra eles a prescricao e ressalvada (art. 103, par. unico, "na forma do Codigo Civil"; dispositivo do CC nao capturado: `[VERIFICAR]`). Havendo a hipotese, nao usar o corte do script: conta aberta parcela a parcela, conferida pelo advogado. Fora dela, prescrevem as parcelas cujo vencimento e anterior aos 5 anos do ajuizamento. O vencimento segue o art. 41-A: acima de 1 salario minimo, do 1o ao 5o dia util do mes seguinte (par. 2); ate 1 salario minimo, do 5o dia util antes do fim do mes ao 5o dia util do mes seguinte (par. 3). Sem o vencimento devido da competencia limitrofe (art. 103, par. unico), ela fica indeterminada e vai ao advogado; nunca presumir o 5o dia util.
3. Identificar a especie de revisao, sempre com ancora:
   - erro na media: salarios desde 07/1994 corrigidos pelo INPC (art. 29-B); salario omitido ou a menor (CNIS pela `analise-cnis`);
   - divisor minimo de 108 para filiado ate 07/1994, fato gerador desde 05/05/2022, exceto incapacidade permanente (art. 135-A); o descarte nao o elimina;
   - coeficiente da EC 103, art. 26 (60% + 2 pontos; 100% nos casos do par. 3; acima de 100% e devido, M3);
   - tempo nao computado (especial convertido so ate 13/11/2019; vinculo reconhecido): tempo pela `calculos-previdenciarios`, depois RMI;
   - fator previdenciario: sem a tabua do IBGE, so formula (M7).
4. Tese inviavel: pedido para afastar o art. 3 da Lei 9.876/1999 e aplicar a regra definitiva do art. 29, I e II, da Lei 8.213 nao se ajuiza (ADIs 2.110/2.111; STF Tema 1.102, tese nova, literal no anexo). Cliente que ja litigou nessa tese: defesa contra cobranca dentro da modulacao, pela `anti-alucinacao-previdenciario` (secao 8 da metodologia, M9).
5. [redacao] Devolver o quadro em 3-6 linhas (beneficio, DIB, primeiro pagamento, erro alegado, prazo decadencial final, RMI paga x devida) e esperar confirmacao.
6. [redacao] Propor 2-3 estrategias com ganho e risco (ex.: pedido administrativo de revisao, `in-128-2022-inss.md` arts. 583 a 589 - efeitos financeiros na DPR quando ha novo elemento, na DIP quando nao ha (art. 586), e o script aceita a `data_requerimento_revisao` como marco; acao direta; acao com pedido subsidiario de recalculo) e esperar a escolha.
7. Competencia material antes da alcada: revisao de beneficio acidentario vai a Justica Estadual (art. 129, II), sem alcada do JEF nem renuncia para ingressar nele; a classificacao federal do script nao se usa. Valor da causa (M6): diferencas nao prescritas (script de RMI) mais 12 diferencas vincendas (`cpc-excertos-prev.md`, art. 292, par. 1 e 2), em duas contas: com e sem a diferenca do abono anual vincendo (padrao: incluir, como interpretacao declarada, nunca pacifica). Somar a vista do advogado e rodar o script de valor da causa uma vez por conta, com `valor_da_causa_informado`. Se uma cabe no JEF e a outra nao, levar as duas ao advogado com a consequencia para alcada e renuncia.
8. [redacao] Redigir: enderecamento (pelo passo 7) · fatos (beneficio, carta, erro) · nao consumacao da decadencia, com as datas do script · fundamento da revisao, por bloco (fato, questao, regra ancorada, aplicacao, conclusao) · demonstrativo RMI paga x devida (memoria do script) · pedidos: revisar e implantar a nova RMI; diferencas nao prescritas corrigidas e com juros desde a citacao pelo texto-base, ressalvas M5/M8 e excecao acidentaria da `peticao-inicial-previdenciaria`, passo 8; honorarios pelo rito, como no passo 9 da mesma skill (JEF de primeiro grau: nao pedir, Lei 9.099, art. 55; demais: base da STJ Sumula 111).
9. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7), entregar ao `validador-previdenciario` e a `suprema-corte-previdenciaria`, gravar em `memoria-de-caso-previdenciario`.

## Calculo
Script `scripts/calc/calc_previdenciario_rmi.py` (lista de CAMPOS: `context/calculo-rmi.md`, secao 6):
```flags
--entrada   caminho   opcional   arquivo JSON da entrada; ausente = entrada padrao
--versao    -         opcional   imprime a versao e sai
```
```campos
modo  enum  sim  concessao · revisao
especie  enum  sim  aposentadoria · incapacidade-permanente · outra
regra  enum  sim no modo concessao  art15 · art16 · art17 · art18 · art19 · art19-especial · art20 · art21 · adquirido-anterior · incapacidade-permanente · incapacidade-permanente-acidentaria
sexo  enum  sim  M · F
data_filiacao  data  sim  primeira filiacao ao RGPS
fato_gerador  data  sim  DER (aposentadoria) ou DII (incapacidade)
salarios_contribuicao  lista de decimal  uma das tres formas de media (1)  desde 07/1994, corrigidos; obrigatoria se descartar
media  decimal  uma das tres formas de media (2)  sozinha no art. 135-A = exit 3
soma  decimal  uma das tres formas de media (3), com quantidade  desde 07/1994, corrigidos
quantidade  inteiro  com soma  numero de salarios somados
tempo_contribuicao_anos  inteiro  sim no modo concessao  anos completos
tempo_contribuicao_meses  inteiro  nao  meses do CNIS; descarte exato
atividade_especial_anos  enum  sim quando regra = art19-especial ou art21  15 · 20 · 25
descartar  bool  nao  padrao false
tempo_minimo_da_regra_anos  inteiro  sim quando descartar = true  minimo que o descarte preserva
fator  decimal  nao  sem ele, art17 e adquirido-anterior = exit 3
teto  decimal  nao  ausente = tabela; fora dela, exit 3
salario_minimo  decimal  nao  ausente = tabela; fora dela, exit 3
rmi_paga  decimal  sim no modo revisao  —
rmi_devida  decimal  sim no modo revisao  ou a recalculada em concessao
media_acima_do_teto  bool  condicional  revisao com DIB no periodo de incorporacao do teto
datas_vencimento  objeto  nao  so revisao; AAAA-MM: AAAA-MM-DD do vencimento devido
dib  data  sim no modo revisao; em concessao, quando a DIB muda os limites do art. 29, §2º  —
data_primeiro_pagamento  data  sim no modo revisao  a DER nao a substitui
data_ajuizamento  data  sim no modo revisao, salvo se houver data_requerimento_revisao  —
data_requerimento_revisao  data  alternativa a data_ajuizamento  pedido administrativo de revisao
abono  bool  sim no modo revisao  abono anual (art. 40)
```
Script `scripts/calc/calc_previdenciario_valor_causa.py` (lista de CAMPOS: `context/calculo-valor-causa.md`, secao 6):
```flags
--entrada   caminho   opcional   arquivo JSON da entrada; ausente = entrada padrao
--versao    -         opcional   imprime a versao e sai
```
```campos
data_ajuizamento  data  sim  distribuicao
valor_da_causa_informado  decimal  nao  total ja formado
rmi_pretendida  decimal  sim, salvo com valor_da_causa_informado  —
dib  data  sim, salvo com valor_da_causa_informado  DIB ou DER
natureza  enum  sim, salvo com valor_da_causa_informado  previdenciaria · assistencial
abono  bool  sim, salvo com valor_da_causa_informado  false no BPC
incluir_abono_nas_vincendas  bool  nao  padrao true (M6)
corrigir_vencidas  bool  nao  true = motor de atualizacao
renunciar_excedente  bool  nao  padrao false
salario_minimo  decimal  nao  ausente = tabela
datas_vencimento  objeto  nao  AAAA-MM: vencimento devido
prescricao  enum  nao  regular · nao_corre · interrompida
marco_prescricional  data  sim quando prescricao = interrompida  —
media_acima_do_teto  bool  condicional  DIB na incorporacao do teto
```
Rodar conforme `context/metodologia-previdenciario.md` (secao 13). Exit 0: mostrar a memoria. Exit 2: repetir a pergunta. Exit 3: `formula_aberta` com `[VERIFICAR]` e as leituras (prescricao, reajuste). Sem Python/script ou outro exit: conta aberta por `context/calculo-rmi.md`, numero nao conferido.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Sem carta de concessao ou sem a data do primeiro pagamento, a decadencia fica indeterminada e a peca nao e redigida.

## Entrega obrigatoria final
- Veredito de decadencia com as datas; demonstrativo RMI paga x devida e diferencas (memoria do script ou conta aberta); a peca, se cabivel; a lista de `[VERIFICAR]`.

## Guard
- Nunca redigir sem decadencia conferida; nunca RMI, diferenca ou prazo de cabeca.
- Nunca ajuizar a tese do art. 29 contra o art. 3 da Lei 9.876/1999; nunca atribuir o PBC de 100% a Lei 13.846/2019 (a fonte e a EC 103, art. 26).
- Nunca converter tempo especial trabalhado depois de 13/11/2019.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill acao-revisional-rmi - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
