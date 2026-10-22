---
name: bpc-loas-previdenciario
description: "Trilha do beneficio de prestacao continuada (BPC/LOAS) do idoso de 65 anos ou mais e da pessoa com deficiencia: grupo familiar, renda per capita igual ou inferior a 1/4 do salario minimo, exclusoes da renda, outros meios de prova da miserabilidade, impedimento de longo prazo, CadUnico, acumulacao vedada, sem carencia e sem abono, valor da causa pelo script com natureza assistencial. Use quando o operador disser BPC, LOAS, beneficio assistencial, idoso sem renda, deficiente sem renda, miserabilidade, renda per capita, B87, B88. Nao use para aposentadoria da pessoa com deficiencia (LC 142, planejamento-previdenciario) nem para beneficio previdenciario por incapacidade (pericia-medica-previdenciaria)."
---

# BPC LOAS

> Camada 4. Beneficio assistencial de um salario minimo, do grupo familiar ao valor da causa.

## Entradas
- Recebe: idade ou documentos da deficiencia (obrigatorio) · quem mora na casa e quanto cada um recebe (obrigatorio) · decisao do INSS, CadUnico, laudos, gastos com saude (opcional, pedir se faltar)
- Chamada por: previdenciario-master | Chama: pericia-medica-previdenciaria · administrativo-inss-crps · prazos-previdenciarios · peticao-inicial-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/lei-8742-1993-loas.md` (arts. 20 e 20-B - grep o artigo e leia a faixa)
- `context/lei/temas-sumulas-prev.md` (STF Tema 27, STJ Tema 185, TNU Sumula 79)
- `context/lei/lei-8213-1991.md` (art. 40, abono so no previdenciario)
- `context/lei/manual-cjf-2026-calculos-prev.md` (item 4.3.1.1, Nota 3: regime assistencial)
- `context/calculo-valor-causa.md` (secao 6, CAMPOS)

## Objetivo
Dizer se o caso preenche o BPC pela letra da LOAS ou pela prova alternativa da miserabilidade, montar a prova e o valor da causa pelo script.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas (requerente idoso ou com deficiencia, quem mora junto, rendas, decisao do INSS) e esperar confirmacao.
2. Prazo primeiro: indeferimento ou cessacao ha menos de 30 dias vai para `prazos-previdenciarios`.
3. Requisito subjetivo (LOAS, art. 20, caput): idoso com 65 anos ou mais, ou pessoa com deficiencia. Deficiencia = impedimento de longo prazo, de no minimo 2 anos, em interacao com barreiras (par. 2 e 10), com avaliacao medica e social (par. 6) e nos termos do regulamento (par. 2-A). Quesitos e laudo vao para `pericia-medica-previdenciaria`.
4. Grupo familiar (par. 1): requerente, conjuge ou companheiro, pais (na falta de um, madrasta ou padrasto), irmaos solteiros, filhos e enteados solteiros e menores tutelados, desde que sob o mesmo teto. Quem esta fora do rol nao entra na conta.
5. Renda per capita: soma dos rendimentos mensais do grupo sob o mesmo teto, vedadas deducoes nao previstas em lei (par. 3-A), dividida pelo numero de membros. Criterio legal: igual ou inferior a 1/4 do salario minimo (par. 3). Fora da soma: BPC ou beneficio previdenciario de ate um salario minimo de outro idoso acima de 65 anos ou pessoa com deficiencia da mesma familia (par. 14); auxilio financeiro temporario e indenizacao por danos decorrentes de rompimento e colapso de barragens, e rendimentos de estagio supervisionado e de aprendizagem (par. 9), conferida a natureza de cada recebimento. Mostrar a conta linha a linha; o salario minimo do mes vem da tabela com fonte.
6. Acima de 1/4: outros elementos de prova da miserabilidade e da vulnerabilidade (par. 11); o 1/4 nao e o unico meio de prova (STJ Tema 185; STF Tema 27, fixado sobre a redacao antiga "inferior a 1/4" - aplicar a tese a redacao atual e leitura, dizer isso). Prova socioeconomica por laudo social, auto de constatacao ou, inviabilizados, testemunhas (TNU Sumula 79). Os aspectos do art. 20-B (grau da deficiencia, dependencia de terceiros, gastos com saude nao fornecidos pelo SUS) servem como elementos de prova.
7. Ampliacao ate 1/2 salario minimo (par. 11-A e art. 20-B, par. 1): depende de regulamento por escalas, nao conferido em context/. Nunca conceder nem prometer automaticamente.
8. Requisitos formais: inscricao no CPF e no CadUnico (par. 12); registro biometrico do requerente ou do responsavel (par. 12-A e 12-B). Acolhimento em instituicao de longa permanencia nao impede (par. 5); mais de um membro da familia pode receber (par. 15).
9. Acumulacao (par. 4): vedada com qualquer outro beneficio da seguridade ou de outro regime, salvo assistencia medica, pensao especial indenizatoria e as transferencias de renda indicadas. Se ha beneficio em curso, escolher antes de pedir.
10. Valor: um salario minimo, sem carencia (a assistencia independe de contribuicao, CF, art. 203, caput, em `context/lei/cf88-seguridade.md`) e sem abono anual (Lei 8.213, art. 40 preve abono so para beneficio previdenciario). Atrasados no regime das condenacoes em geral, nunca no previdenciario (Manual CJF 2026, item 4.3.1.1, Nota 3).
11. Valor da causa e alcada pelo script, com `natureza = assistencial` e `abono = false`.
12. Homonimo: o art. 20 da LOAS (BPC) nao e o art. 20 da EC 103 (pedagio de 100%). Citar sempre o diploma.
13. [redacao] Propor 2-3 caminhos (novo requerimento com prova social completa, recurso ao CRPS pela `administrativo-inss-crps`, acao judicial com prova alternativa da miserabilidade), cada um com ganho e risco; o advogado escolhe.
14. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7) antes de entregar texto livre.

## Calculo
Achar e rodar o script pela secao 13 de `context/metodologia-previdenciario.md`; o bloco campos e o contrato da entrada JSON.
```flags
# script: calc_previdenciario_valor_causa.py
--entrada  arquivo  opcional  JSON de entrada (sem ela, entrada padrao)
--versao  nenhum  opcional  imprime a versao
```
```campos
# script: calc_previdenciario_valor_causa.py
data_ajuizamento  data  obrigatorio  data da distribuicao
valor_da_causa_informado  decimal  opcional  total ja formado; dispensa os campos de RMI
rmi_pretendida  decimal  condicional  obrigatorio salvo com valor_da_causa_informado
dib  data  condicional  obrigatorio salvo com valor_da_causa_informado; DIB pretendida ou DER
natureza  enum  condicional  previdenciaria | assistencial; obrigatorio salvo com valor_da_causa_informado
abono  bool  condicional  obrigatorio salvo com valor_da_causa_informado; false quando natureza = assistencial
incluir_abono_nas_vincendas  bool  opcional  padrao true; ignorado quando abono = false
corrigir_vencidas  bool  opcional  padrao false; true chama o motor de atualizacao
renunciar_excedente  bool  opcional  padrao false
salario_minimo  decimal  opcional  ausente = tabela pela data do ajuizamento
datas_vencimento  objeto  opcional  AAAA-MM: AAAA-MM-DD do vencimento devido (Lei 8.213, art. 103, par. unico)
prescricao  enum  opcional  regular | nao_corre | interrompida
marco_prescricional  data  condicional  sim quando prescricao = interrompida
media_acima_do_teto  bool  condicional  so no ramo previdenciario (nunca no BPC): DIB na incorporacao do teto
```
No BPC: `natureza = assistencial`, `abono = false` (`true` com BPC = exit 2) e `rmi_pretendida` = salario minimo da DIB. O BPC e um salario minimo mensal (LOAS, art. 20): cada vencida vale o minimo da propria competencia e as 12 vincendas o da propositura (CPC, art. 292, par. 1 e 2). Se o minimo muda entre as competencias (ex.: DIB 12/2025, ajuizamento 02/2026: 1.518 + 1.621 + 12 x 1.621 = 22.591), o script sai em exit 3 com `conta_bpc_por_competencia`: conferir essa conta e rodar de novo com `valor_da_causa_informado` para a alcada, so quando `total_unico = true` (qualquer outra pendencia que mude o valor, como a competencia da DIB no meio do mes, bloqueia a reentrada); com `competencias_pendentes`, pedir antes o vencimento delas (`datas_vencimento`), sem total unico. Nunca aceitar exit 0 com o minimo congelado nem trocar todas as competencias pelo minimo novo. Exit 0: usar e mostrar a memoria. Exit 2: perguntar de novo o dado recusado (vencimento informado fora da janela de pagamento ou em dia sem expediente bancario tambem e exit 2). Exit 3: `formula_aberta` com `[VERIFICAR]`; sem `prescricao` e com competencia de mais de cinco anos, as contas sem e com o corte quinquenal (Lei 8.213, art. 103, par. unico): perguntar o regime ao advogado. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-valor-causa.md`, passo a passo, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na entrega. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Quadro do grupo familiar com a conta da renda per capita e as exclusoes aplicadas.
- Requisito subjetivo e prova que falta; plano de prova da miserabilidade quando a renda passa de 1/4.
- Valor da causa e alcada pelo script, com a memoria; os 2-3 caminhos e o escolhido.

## Guard
Nunca "inferior a 1/4" para a lei atual: e "igual ou inferior". Nunca abono no BPC. Nunca carencia no BPC. Nunca ampliacao automatica ate 1/2 salario minimo. Nunca tratar 1/4 como teto absoluto. Nunca atualizar atrasados do BPC pelo regime previdenciario.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill bpc-loas-previdenciario - plugin previdenciario-adv-os v2.0.3`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
