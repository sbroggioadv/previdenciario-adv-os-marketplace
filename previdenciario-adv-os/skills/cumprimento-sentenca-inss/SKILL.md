---
name: cumprimento-sentenca-inss
description: "Redige o cumprimento de sentenca contra o INSS depois do transito em julgado: implantacao do beneficio, demonstrativo do credito pelo script de atrasados (regime de atualizacao em fatias por competencia e da data-base ao pagamento), honorarios sobre as vencidas ate a sentenca, escolha entre RPV e precatorio pelo valor atualizado ate a transmissao, renuncia ao excedente quando o cliente decidir, e resposta a impugnacao do INSS. Use quando o operador disser cumprimento de sentenca, executar a sentenca, calcular atrasados, RPV, precatorio, requisitorio, impugnacao do INSS. Nao use para a fase de conhecimento (peticao-inicial-previdenciaria) nem para recurso (recursos-previdenciarios)."
---

# CUMPRIMENTO DE SENTENCA CONTRA O INSS

> Camada 5. Da sentenca transitada ao pagamento: o valor e a via saem do script, nunca de estimativa.

## Entradas
- Recebe: sentenca ou acordao e certidao de transito (obrigatorio) · competencias devidas e pagas, datas de citacao e sentenca, data-base da conta (obrigatorio para os atrasados) · datas de expedicao, apresentacao e transmissao da requisicao (quando ja houver) · contrato de honorarios (se houver destaque)
- Chamada por: previdenciario-master | Chama: prazos-previdenciarios · calculos-previdenciarios · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-rpv.md` (secoes 1 a 6 e 8)
- `context/lei/cpc-excertos-prev.md` (arts. 534 e 535 - grep o artigo e leia a faixa) · `context/lei/lei-10259-2001-jef.md` (arts. 9, 16 e 17)
- `context/lei/res-cjf-983-2026.md` (arts. 3, 4, 7 e 16) · `context/lei/manual-cjf-2026-calculos-prev.md` (itens 4.1, 4.3.1.1, 4.3.2 e cap. 5)
- `context/lei/cf88-seguridade.md` (art. 100, par. 5 e 8) · `context/lei/temas-sumulas-prev.md` (STJ Sumula 111; STJ Tema 905; STF Tema 1.419) · `context/escrita-humana.md`

## Objetivo
Entregar o requerimento de cumprimento com demonstrativo conferido, a via de pagamento correta e o prazo de pagamento esperado.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas: natureza (previdenciaria ou assistencial), rito (JEF ou comum), o que o titulo condenou, criterio de correcao proprio do titulo (se houver, prevalece sobre o Manual; item 4.1), datas de citacao, sentenca e transito, e a justica do titulo. Titulo acidentario da Justica Estadual (`context/lei/lei-8213-1991.md`, art. 129, II) nao e competencia federal nem delegada: a Res. CJF 983/2026 (art. 1) e o Manual CJF nao o regem; via, limite e regime do requisitorio estadual sem anexo em context/: `[VERIFICAR]`, sem script. Esperar confirmacao.
2. Obrigacao de fazer: implantacao do beneficio; no JEF, por oficio a autoridade (Lei 10.259, art. 16).
3. Rodar o script de atrasados (secao Calculo). Regime em fatias por competencia, nunca um indice unico: R1 ate a data-base (ate nov./2021 Manual e STJ Tema 905; dez./2021 a ago./2025 Selic unica, EC 113, art. 3, STF Tema 1.419; desde set./2025 INPC e taxa legal com deducao do INPC no previdenciario, IPCA-15 no BPC) e R2 da data-base ao pagamento (Res. CJF 983/2026, art. 7: desde set./2025 o menor entre IPCA + 2% a.a. e Selic). Exit 3: listar ao advogado todos os `dados_faltantes` e as `fatias_em_aberto` com as duas contas; nunca preencher.
4. Demonstrativo com os itens do CPC, art. 534 (indice, juros e taxas, termos inicial e final, descontos). Honorarios sucumbenciais em requisicao propria; na acao previdenciaria, so sobre as vencidas ate a sentenca (STJ Sumula 111, que se limita as acoes previdenciarias); no BPC, seguir a base fixada no titulo, sem reduzir pela Sumula 111, e marcar como fora do corpus `[VERIFICAR]` o fundamento adicional que se precise para a base; contratuais destacados integram o credito da parte na classificacao (Res. CJF 983/2026, art. 16).
5. Via de pagamento pelo valor atualizado ate a transmissao ao tribunal (Res. CJF 983/2026, art. 3, par. 4); limite de 60 salarios minimos por beneficiario (Lei 10.259, art. 17, par. 1, c/c art. 3). O salario minimo do limite e o vigente na transmissao, como interpretacao operacional declarada (M4). Acima do limite: precatorio, ou RPV com renuncia expressa ao excedente (art. 17, par. 4; Res. CJF 983/2026, art. 4). Fracionar e vedado (art. 17, par. 3; CF, art. 100, par. 8). O nome do instituto e "renuncia ao excedente".
6. [redacao] Propor 2-3 estrategias com ganho e risco e esperar a escolha (a renuncia e decisao do advogado com o cliente): ex.: RPV com renuncia ao excedente (recebe antes, abre mao da diferenca) x precatorio pelo valor integral (recebe tudo, espera o ciclo) x apresentar a conta propria x aguardar a do INSS.
7. Prazos de pagamento: RPV no JEF, 60 dias da entrega da requisicao (Lei 10.259, art. 17); no rito comum, 2 meses (CPC, art. 535, par. 3, II). Precatorio apresentado ate 1 de fevereiro, pago ate o fim do exercicio seguinte (CF, art. 100, par. 5). Sem juros de mora no prazo constitucional ou legal (Res. CJF 983/2026, art. 7, par. 2; Manual, cap. 5).
8. Impugnacao do INSS: 30 dias no rito do CPC (art. 535), com as materias do artigo; no JEF, sem prazo diferenciado para a Fazenda (Lei 10.259, art. 9). Datas pela `prazos-previdenciarios` (motor de prazo, rito `cpc`, com esse aviso). Alegacao de excesso exige que o INSS declare o valor que entende correto (art. 535, par. 2): apontar quando faltar. Resposta: confronto linha a linha com a memoria do script.
9. [redacao] Redigir: cabecalho com o numero do processo · titulo e transito · obrigacao de fazer · demonstrativo (anexo, memoria do script) · honorarios · via e, se houver, a renuncia expressa · pedidos (intimacao do INSS para impugnar; expedicao da RPV ou do precatorio; requisicao propria dos honorarios sucumbenciais).
10. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7), entregar ao `validador-previdenciario` e a `suprema-corte-previdenciaria`, gravar em `memoria-de-caso-previdenciario`.

## Calculo
Script `scripts/calc/calc_previdenciario_rpv.py` (lista de CAMPOS: `context/calculo-rpv.md`, secao 8):
```flags
--entrada   caminho   opcional   arquivo JSON da entrada; ausente = entrada padrao
--versao    -         opcional   imprime a versao e sai
```
```campos
natureza  enum  sim  previdenciaria · assistencial
rito  enum  sim  JEF · comum
parcelas  lista  uma das formas de atrasados (1)  uma entrada por competencia
parcelas[].competencia  competencia  sim  —
parcelas[].devido  decimal  sim  —
parcelas[].pago  decimal  nao  padrao "0.00"
diferenca_mensal  decimal  uma das formas de atrasados (2)  com competencia_inicial e competencia_final
competencia_inicial  competencia  com diferenca_mensal  —
competencia_final  competencia  com diferenca_mensal  —
data_citacao  data  sim quando ha atrasados  termo inicial dos juros
data_sentenca  data  sim quando ha honorarios sucumbenciais por percentual  corte da Sumula 111
data_base_conta  competencia  sim quando ha atrasados  data-base informada pelo juizo (fim de R1, inicio de R2)
valor_consolidado_12_2021  decimal  nao  principal consolidado em dez./2021, quando ja apurado (supre a falta da serie da poupanca)
juros_consolidados_12_2021  decimal  nao  "juros ate 12/2021", com valor_consolidado_12_2021
data_expedicao  data  nao  expedicao do requisitorio
data_apresentacao  data  nao  apresentacao/entrega ao tribunal; define o corte, o prazo e a graca
data_transmissao  data  sim quando ha valor_atualizado_ate_transmissao  marco do limite da RPV (M4)
data_pagamento  data  nao  sem ela, R2 sai em formula com a lista de faltantes
valor_atualizado_ate_transmissao  decimal  nao  valor do motor de atualizacao ate a transmissao; sem ele, a via nao fecha (exit 3)
honorarios_percentual  decimal  nao  percentual dos sucumbenciais sobre a base da Sumula 111
honorarios_sucumbenciais  decimal  nao  valor ja fixado (alternativa ao percentual; os dois juntos → exit 2)
honorarios_contratuais  decimal  nao  valor destacado; integra o credito na classificacao
renunciar_excedente  bool  nao  padrao false
titulo_com_criterio_proprio  texto  nao  se houver, o script alerta que o titulo prevalece sobre o Manual
salario_minimo  decimal  nao  ausente = tabela pela data da transmissao; ano fora da tabela → exit 3
datas_vencimento  objeto  nao  AAAA-MM: AAAA-MM-DD do vencimento devido (Lei 8.213, art. 103, par. unico)
honorarios_atualizados_ate_transmissao  decimal  sim para classificar os sucumbenciais  atualizados ate a transmissao (Res. CJF 983/2026, arts. 3, §4, e 16); sem ele, a via deles sai em formula
```
Rodar conforme `context/metodologia-previdenciario.md` (secao 13). Exit 0: usar e mostrar a memoria. Exit 2: perguntar de novo o dado errado. Exit 3: `formula_aberta`, `dados_faltantes` e `fatias_em_aberto` com `[VERIFICAR]`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-rpv.md`, dizendo que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Todo resultado com R2 leva `[VERIFICAR] ADI 7.873` (EC 136, andamento nao certificado). Custas do INSS na Justica Federal: indeterminado (Lei 9.289/1996 nao capturada).

## Entrega obrigatoria final
- O requerimento de cumprimento, o demonstrativo (memoria do script ou conta aberta), a via e o prazo de pagamento, a lista de dados faltantes e de `[VERIFICAR]`.

## Guard
- Nunca indice unico para todo o periodo; nunca IPCA + 2% antes de set./2025 no requisitorio; nunca taxa legal posterior a maio/2026 sem tabela do CJF.
- Nunca fracionar o credito; nunca decidir a renuncia pelo cliente; nunca classificar a via pelo valor da data da conta.
- Selic contra o INSS vem da EC 113/2021, art. 3; nenhuma lei ordinaria no lugar dela.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill cumprimento-sentenca-inss - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
