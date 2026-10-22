---
name: peticao-inicial-previdenciaria
description: "Redige a peticao inicial previdenciaria contra o INSS (JEF, vara federal ou, na acidentaria, Justica Estadual): concessao, restabelecimento ou conversao de beneficio do RGPS, com regra de aposentadoria escolhida pelo script de transicoes, valor da causa e alcada pelo script de valor da causa, pedido de juros e correcao pelo regime em fatias do Manual CJF e da Res. CJF 983/2026, e fundamentacao so com dispositivo ancorado em context/. Use quando o operador disser peticao inicial, ajuizar contra o INSS, acao previdenciaria, entrar com processo, /peticao-previdenciaria. Nao use para revisao de beneficio ja concedido (acao-revisional-rmi), mandado de seguranca (mandado-seguranca-previdenciario) ou execucao (cumprimento-sentenca-inss)."
---

# PETICAO INICIAL PREVIDENCIARIA

> Camada 5. Do quadro confirmado a peca de ingresso contra o INSS, cada numero vindo de script ou de conta aberta.

## Entradas
- Recebe: quadro do caso (segurado, beneficio, DER, decisao do INSS, documentos) (obrigatorio) · CNIS, PPP, laudos, carta de indeferimento (opcional) · `previdenciario/casos/<slug>.md` (se houver)
- Chamada por: previdenciario-master · analise-carta-concessao-indeferimento | Chama: estrategia-de-caso-previdenciario · calculos-previdenciarios · pericia-medica-previdenciaria · acidentario-do-trabalho · analise-trilateral-previdenciario · jurisprudencia-estrategica-previdenciario · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-transicao.md` (secoes 1, 2 e 7) e `context/calculo-valor-causa.md` (secoes 1, 3, 4 e 6)
- `context/lei/ec-103-2019.md` (arts. 3, 15 a 21, 25 e 26 - grep o artigo e leia a faixa)
- `context/lei/lei-8213-1991.md` (art. 129, competencia acidentaria) · `context/lei/lei-10259-2001-jef.md` (arts. 1, 3, 4, 9 e 12) · `context/lei/lei-9099-1995.md` (art. 55) · `context/lei/cpc-excertos-prev.md` (arts. 43 e 292)
- `context/lei/manual-cjf-2026-calculos-prev.md` (itens 4.3.1.1 e 4.3.2) · `context/lei/res-cjf-983-2026.md` (art. 7)
- `context/lei/temas-sumulas-prev.md` (STJ Tema 905, STF Tema 1.419, STJ Tema 1.030, STJ Sumula 111) · `context/escrita-humana.md`

## Objetivo
Entregar a peticao inicial pronta para revisao do advogado, com competencia, pedidos e valor da causa demonstrados.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas (segurado, beneficio, DER, decisao do INSS e data, documentos, rito provavel) e esperar confirmacao. Fato que o advogado nao confirmou nao entra na peca.
2. Pre-requisitos: DER e decisao de indeferimento (ou a demora documentada) juntados. Sem eles, avisar antes de redigir; a tese do interesse de agir sem requerimento so entra com `[VERIFICAR]` (precedente nao capturado).
3. Prazo: se a pergunta critica da triagem deu "sim", confirmar que `prazos-previdenciarios` ja rodou. Auxilio por incapacidade temporaria requerido depois de 30 dias do afastamento: DIB na DER, salvo DII posterior (`context/lei/lei-8213-1991.md`, art. 60, par. 1).
4. [redacao] Propor 2-3 estrategias com ganho e risco (ex.: regra A x regra B; JEF com renuncia x vara federal; principal com subsidiario de outro beneficio) e esperar a escolha do advogado.
5. Calculo por especie (secao Calculo), RMI pretendida sempre de memoria de calculo, nunca de cabeca:
   - aposentadoria: script de transicoes (regra e data em que cumpre); RMI pela `calculos-previdenciarios`;
   - incapacidade temporaria, permanente ou auxilio-acidente: sem transicoes; DIB e RMI pela memoria de `pericia-medica-previdenciaria` (ou `acidentario-do-trabalho`, se acidentaria), com os limitadores de `context/calculo-incapacidade.md`;
   - BPC: sem transicoes; um salario minimo (LOAS, art. 20), natureza assistencial, sem abono.
   Competencia material antes da alcada: acao acidentaria (acidente do trabalho, doenca profissional ou do trabalho) vai a Justica Estadual, com a prova da notificacao do evento ao INSS pela CAT (`context/lei/lei-8213-1991.md`, art. 129, II); o script nao a enderece. Demais: Justica Federal.
   Depois, o script de valor da causa com essa RMI: valor e, na Justica Federal, alcada e JEF ou vara.
6. [redacao] Redigir na ordem: enderecamento (competencia do passo 5) · qualificacao (do caso, nunca do plugin) · fatos em narrativa continua · direito por bloco (fato, questao, regra ancorada, aplicacao, conclusao) · tutela de urgencia, se pedida (no JEF, Lei 10.259, art. 4; dispositivo do CPC sobre tutela nao esta em context/: `[VERIFICAR]`) · provas (pericia: Lei 10.259, art. 12 no JEF) · pedidos · valor da causa · documentos.
7. Fundamentacao por beneficio, sempre pelo anexo:
   - aposentadoria: EC 103, art. 3 (adquirido), arts. 15 a 21 (a regra que o script apontou) e art. 26 (media de 100% desde 07/1994; nunca a Lei 13.846/2019);
   - especial: conversao so do tempo trabalhado ate 13/11/2019 (EC 103, art. 25, par. 2); prova por PPP e laudo (`context/lei/lei-8213-1991.md`, arts. 57 e 58); IEAN nao basta;
   - incapacidade temporaria: Lei 8.213, arts. 59 a 62; renda de 91% do salario de beneficio, inclusive na acidentaria (art. 61), limitada a media dos ultimos 12 salarios de contribuicao (IN 128, art. 233, I, "b"); o coeficiente da EC 103 nao se aplica;
   - incapacidade permanente: Lei 8.213, art. 42; coeficiente pela EC 103, art. 26, par. 2, III (60% + 2 pontos, incapacidade constatada depois da reforma, STF Tema 1.300); 100%, independentemente do acrescimo do par. 2, III, e do par. 5, quando acidentaria (par. 3, II);
   - auxilio-acidente: Lei 8.213, art. 86, sem carencia (art. 26, I), sem piso (Decreto 3.048, art. 42, par. unico), inacumulavel com aposentadoria;
   - BPC: LOAS, art. 20, par. 3 ("igual ou inferior a 1/4"), sem abono; prova de miserabilidade alem do 1/4 (STF Tema 27; STJ Tema 185); laudo social (TNU Sumula 79).
8. Pedido de correcao e juros, texto-base (Justica Federal ou delegada): "parcelas vencidas corrigidas e acrescidas de juros de mora desde a citacao, na forma do Manual de Calculos da Justica Federal vigente (STJ Tema 905 ate nov./2021; Selic unica de dez./2021 a ago./2025, EC 113/2021, art. 3, nos termos do STF Tema 1.419; a partir de set./2025, INPC e taxa legal com deducao do INPC) e, na fase do requisitorio, da Resolucao CJF 983/2026, art. 7". BPC: regime das condenacoes em geral (IPCA-E ate nov./2021; IPCA-15 e taxa legal com deducao do IPCA-15 desde set./2025). M5 e M8 ficam em aberto: nao fixar taxa da fase desde set./2025 nem regime do requisitorio na peca; taxa legal posterior a maio/2026 sem tabela do CJF e `[VERIFICAR] ADI 7.873` (EC 136). Acao acidentaria estadual: Manual e Res. CJF 983/2026 nao a regem (art. 1); regime sem anexo, `[VERIFICAR]`.
9. Honorarios pelo rito: JEF, sem honorarios em primeiro grau, salvo ma-fe (Lei 9.099, art. 55, via Lei 10.259, art. 1): nao pedir; vara federal ou estadual: pedir (CPC, art. 85, `[VERIFICAR]`), base nas vencidas ate a sentenca (STJ Sumula 111 so delimita a base). Custas do INSS na Justica Federal: indeterminado (Lei 9.289/1996 nao capturada); na Justica Estadual, STJ Sumula 178.
10. Valor da causa com a `prescricao` do caso e as duas contas do abono (M6), padrao incluir, nunca no BPC; acima da alcada, renuncia expressa ao excedente so por decisao do advogado com o cliente (STJ Tema 1.030); competencia fixada na distribuicao (CPC, art. 43).
11. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7), entregar ao `validador-previdenciario` e a `suprema-corte-previdenciaria`, gravar em `memoria-de-caso-previdenciario`.

## Calculo
Script `scripts/calc/calc_previdenciario_transicao.py` (CAMPOS: `context/calculo-transicao.md`, secao 7):
```flags
--entrada   caminho   opcional   arquivo JSON da entrada; ausente = entrada padrao
--versao    -         opcional   imprime a versao e sai
```
```campos
nascimento  data  sim  —
sexo  enum  sim  M · F
data_filiacao  data  sim  primeira filiacao ao RGPS
der  data  sim  data em que se verifica cada regra
periodos  lista  sim  ao menos 1 periodo
periodos[].inicio  data  sim  AAAA-MM-DD
periodos[].fim  data  sim  AAAA-MM-DD
periodos[].tipo  enum  sim  comum | especial-15 | especial-20 | especial-25
periodos[].fonte  enum  sim  CNIS | CTPS | sentenca | PPP
periodos[].competencias_abaixo_do_minimo  lista  nao  de 11/2019 em diante
novembro_2019_integral  bool  sim se periodo abrange 13/11/2019 e continua  false = exit 3
professor  bool  nao  padrao false; todo o tempo de magisterio exclusivo, com [VERIFICAR]
projecao_continua  bool  nao  padrao false; projeta competencias apos o ultimo periodo
projecao_ate  data  sim quando projecao_continua = true  limite da projecao
```
Script `scripts/calc/calc_previdenciario_valor_causa.py` (CAMPOS: `context/calculo-valor-causa.md`, secao 6):
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
Rodar conforme `context/metodologia-previdenciario.md` (secao 13). Exit 0: mostrar a memoria. Exit 2: repetir a pergunta. Exit 3: `formula_aberta` com `[VERIFICAR]` e as leituras. Sem Python/script ou outro exit: conta aberta pelos `context/calculo-<x>.md`, avisando: numero nao conferido.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na peca. Dispositivo, tema ou sumula sem ancora sai como `[VERIFICAR]`, nunca como fato.

## Entrega obrigatoria final
- A peticao inicial em texto, as memorias dos calculos do passo 5 (ou a conta aberta), a lista de documentos a juntar e a lista de `[VERIFICAR]` pendentes.

## Guard
- Nunca pedir a regra definitiva do art. 29, I e II, da Lei 8.213 contra o art. 3 da Lei 9.876/1999: e cogente (ADIs 2.110/2.111; STF Tema 1.102).
- Nunca converter tempo especial trabalhado depois de 13/11/2019; nunca piso nem cumulacao com aposentadoria no auxilio-acidente; nunca abono no BPC.
- Selic contra o INSS vem da EC 113/2021, art. 3; nenhuma lei ordinaria e citada no lugar dela.
- Nenhum numero (tempo, RMI, valor da causa, alcada) de cabeca.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill peticao-inicial-previdenciaria - plugin previdenciario-adv-os v2.0.3`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
