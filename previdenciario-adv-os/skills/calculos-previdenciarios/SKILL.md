---
name: calculos-previdenciarios
description: "Hub de calculo previdenciario: identifica a conta pedida, colhe os campos de entrada, roda o script local certo (cnis, tempo, transicao, incapacidade, rmi, valor-causa, rpv) e devolve o numero com memoria, regra e fonte, ou a conta aberta quando o script nao fecha. Nunca numero de cabeca. Use quando o operador disser calcular tempo de contribuicao, quanto falta para aposentar, qual regra de transicao, RMI, carencia, qualidade de segurado, valor da causa, atrasados, RPV ou precatorio, ou /calculo-previdenciario. Nao use para calculo judicial generico fora do previdenciario (calculosjudiciais-adv-os) nem para tese que o plugin declara inviavel (STF Tema 1.102)."
---

# CALCULOS-PREVIDENCIARIOS

> Camada C2. Porta do calculo avulso: escolhe o script, monta a entrada, interpreta o exit e entrega a memoria.

## Entradas
- Recebe: a conta pedida e os dados do caso (CNIS, CTPS, PPP, carta do INSS, datas, salarios) (obrigatorio) · `previdenciario/casos/<slug>.md` (opcional)
- Chamada por: previdenciario-master · estrategia-de-caso-previdenciario | Chama: nenhuma (roda os scripts de `scripts/calc/`)

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secao 13 Scripts, secao 9 Relogio - grep a secao e leia a faixa)
- `context/calculo-tempo.md`, `context/calculo-transicao.md`, `context/calculo-rmi.md` (secao CAMPOS e o caso resolvido)
- `context/calculo-cnis.md`, `context/calculo-incapacidade.md`, `context/calculo-valor-causa.md`, `context/calculo-rpv.md` (secao CAMPOS)
- `context/lei/ec-103-2019.md` (arts. 25, 26 - grep o artigo e leia a faixa)

## Objetivo
Entregar o numero conferido por script, ou a formula preenchida ate onde os dados permitem, sempre com a fonte de cada termo.

## Roteamento
| Pedido | Script | Conta aberta | Skill do dominio |
|---|---|---|---|
| carencia, qualidade de segurado, indicadores | `calc_previdenciario_cnis.py` | `calculo-cnis.md` | analise-cnis |
| tempo comum, especial convertido, concomitancia | `calc_previdenciario_tempo.py` | `calculo-tempo.md` | analise-ppp-ltcat-aposentadoria-especial |
| qual regra, quando cumpre, direito adquirido | `calc_previdenciario_transicao.py` | `calculo-transicao.md` | planejamento-previdenciario |
| incapacidade, auxilio-acidente, DIB | `calc_previdenciario_incapacidade.py` | `calculo-incapacidade.md` | pericia-medica-previdenciaria |
| RMI, revisao, decadencia, prescricao | `calc_previdenciario_rmi.py` | `calculo-rmi.md` | acao-revisional-rmi |
| valor da causa, alcada do JEF | `calc_previdenciario_valor_causa.py` | `calculo-valor-causa.md` | peticao-inicial-previdenciaria |
| atrasados, honorarios, RPV ou precatorio | `calc_previdenciario_rpv.py` | `calculo-rpv.md` | cumprimento-sentenca-inss |

Aposentadoria: ordem fixa cnis -> tempo -> transicao -> rmi; o resultado de um entra no seguinte.

## Metodologia
1. Identificar a conta pela tabela acima. Pedido de mais de uma conta: rodar na ordem fixa.
2. Ler a secao CAMPOS do `context/calculo-<x>.md`. Perguntar so o campo obrigatorio que falta, 1 a 3 por turno. "Nao sei" e lacuna, nunca suposicao: campo obrigatorio sem valor nao vai ao script (seria exit 2, entrada invalida); a conta sai aberta pelo `calculo-<x>.md` ate onde da, com a lista do que falta. Exit 3 e outra coisa: o script recebeu entrada valida e a conta nao fecha (tabela, fator, duas leituras).
3. Montar o JSON so com os campos da lista (campo desconhecido o script recusa). Gravar em `previdenciario/casos/<slug>-calc-<x>.json`, no computador do advogado. CNIS e laudo sao dado sensivel: nunca colar em ferramenta externa.
4. Achar e rodar o script conforme a secao 13 da metodologia: `<pasta-base>/../../scripts/calc/calc_previdenciario_<x>.py --entrada <arquivo>`; sem o arquivo, busca pelo nome e `--versao` igual a 2.0.1.
5. Ler o exit:
   - 0: mostrar o resultado, a `memoria` passo a passo, a `regra` e a `fonte` de cada numero. Duas leituras com `[VERIFICAR]`: mostrar as duas, nunca escolher em silencio.
   - 2: dizer qual campo foi recusado e perguntar de novo so esse campo.
   - 3: entregar a `formula_aberta` preenchida ate onde da, com `[VERIFICAR]` e o dado que falta.
   - outro exit, sem Python ou sem script: conta aberta pelo `context/calculo-<x>.md`, passo a passo, com o aviso "conta nao conferida por script".
6. Conferir o resultado contra as verdades duras antes de entregar (abaixo). Divergencia: nao entregar o numero; mostrar a divergencia ao advogado.
7. Devolver ao chamador o resultado e o arquivo de entrada usado, para a `memoria-de-caso-previdenciario` registrar.

## Verdades que o resultado tem de respeitar
- Conversao de especial em comum so do tempo trabalhado ate 13/11/2019; vinculo que cruza a data e fatiado (`context/lei/ec-103-2019.md`, art. 25, par. 2).
- PBC de 100% desde 07/1994 vem da EC 103, art. 26, nao da Lei 13.846/2019. Coeficiente acima de 100% e devido; o limite e o teto em reais.
- Divisor minimo de 108 para o filiado ate 07/1994 nas aposentadorias com fato gerador desde 05/05/2022, exceto incapacidade permanente; o descarte nao o elimina.
- Fator previdenciario sem a tabua do IBGE: formula e lista de dados faltantes, nunca numero. No direito adquirido, a opcao sem fator (`context/lei/lei-8213-1991.md`, art. 29-C; `context/lei/in-128-2022-inss.md`, art. 229, par. 2) nao depende da tabua: o script nao faz a regra anterior (exit 3); conta aberta por modalidade pelo `context/calculo-rmi.md` (secoes 1 e 4; no art. 29-C, conferir se os pontos fecham), avisando "conta nao conferida por script".
- Atualizacao e juros contra o INSS em fatias por competencia, so pelos scripts de valor da causa e RPV; nunca "IPCA-E ate 2021 e Selic depois".
- Valor da causa: duas contas (com e sem abono nas 12 vincendas); nunca abono no BPC.

## Calculo
Os 7 scripts tem as mesmas flags. Abaixo os campos dos tres que este hub roda direto; para cnis, incapacidade, valor-causa e rpv, usar a lista CAMPOS do respectivo `context/calculo-<x>.md`.

Script: `calc_previdenciario_tempo.py`
```flags
--entrada   arquivo   opcional   JSON; sem ele, entrada padrao
--versao    flag      opcional   imprime a versao
```
```campos
sexo   enum   obrigatoria   M|F
periodos   lista   obrigatoria   ao menos 1 periodo
periodos[].inicio   data   obrigatoria   AAAA-MM-DD
periodos[].fim   data   obrigatoria   AAAA-MM-DD
periodos[].tipo   enum   obrigatoria   comum|especial-15|especial-20|especial-25
periodos[].fonte   enum   obrigatoria   CNIS|CTPS|sentenca|PPP
periodos[].competencias_abaixo_do_minimo   lista   opcional   AAAA-MM desde 11/2019; padrao []
novembro_2019_integral   bool   condicional   se algum periodo cruza 13/11/2019; false da exit 3
```

Script: `calc_previdenciario_transicao.py`
```flags
--entrada   arquivo   opcional   JSON; sem ele, entrada padrao
--versao    flag      opcional   imprime a versao
```
```campos
nascimento   data   obrigatoria   AAAA-MM-DD
sexo   enum   obrigatoria   M|F
data_filiacao   data   obrigatoria   primeira filiacao ao RGPS
der   data   obrigatoria   data em que se verifica cada regra
periodos   lista   obrigatoria   sub-campos iguais aos do script de tempo
periodos[].inicio   data   obrigatoria   AAAA-MM-DD
periodos[].fim   data   obrigatoria   AAAA-MM-DD
periodos[].tipo   enum   obrigatoria   comum|especial-15|especial-20|especial-25
periodos[].fonte   enum   obrigatoria   CNIS|CTPS|sentenca|PPP
periodos[].competencias_abaixo_do_minimo   lista   opcional   AAAA-MM desde 11/2019
novembro_2019_integral   bool   condicional   se algum periodo cruza 13/11/2019; false da exit 3
professor   bool   opcional   padrao false; true com [VERIFICAR]
projecao_continua   bool   opcional   padrao false
projecao_ate   data   condicional   obrigatoria se projecao_continua = true
```

Script: `calc_previdenciario_rmi.py`
```flags
--entrada  arquivo  opcional  JSON; sem ele, entrada padrao
--versao   flag    opcional  imprime a versao
```
```campos
modo  enum  obrigatoria  concessao|revisao
especie  enum  obrigatoria  aposentadoria|incapacidade-permanente|outra
regra  enum  condicional  no modo concessao: art15|art16|art17|art18|art19|art19-especial|art20|art21|adquirido-anterior|incapacidade-permanente|incapacidade-permanente-acidentaria
sexo  enum  obrigatoria  M|F
data_filiacao  data  obrigatoria  AAAA-MM-DD
fato_gerador  data  obrigatoria  DER ou DII
salarios_contribuicao  lista  condicional  forma de media 1; obrigatoria se descartar = true
media  decimal  condicional  forma de media 2
soma  decimal  condicional  forma de media 3, com quantidade
quantidade  inteiro  condicional  com soma
tempo_contribuicao_anos  inteiro  condicional  obrigatoria no modo concessao
tempo_contribuicao_meses  inteiro  nao  meses do CNIS; descarte exato
atividade_especial_anos  enum  condicional  15|20|25 quando regra = art19-especial ou art21
descartar  bool  opcional  padrao false
tempo_minimo_da_regra_anos  inteiro  condicional  obrigatoria se descartar = true
fator  decimal  opcional  sem ele art17 e adquirido-anterior saem em exit 3
teto  decimal  opcional  ausente = tabela pela DIB, nunca a DII
salario_minimo  decimal  opcional  idem; sem DIB e com efeito, exit 3
rmi_paga  decimal  condicional  obrigatoria no modo revisao
rmi_devida  decimal  condicional  obrigatoria no modo revisao
media_acima_do_teto  bool  condicional  revisao com DIB no periodo de incorporacao do teto
datas_vencimento  objeto  nao  so revisao; AAAA-MM: AAAA-MM-DD do vencimento devido
dib  data  condicional  revisao; em concessao, se a DIB muda os limites do art. 29, §2º
data_primeiro_pagamento  data  condicional  obrigatoria no modo revisao
data_ajuizamento  data  condicional  no modo revisao, salvo data_requerimento_revisao
data_requerimento_revisao  data  condicional  alternativa a data_ajuizamento
abono  bool  condicional  obrigatoria no modo revisao
```
Uma so forma de media por entrada; duas ao mesmo tempo da exit 2.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Sem o `calculo-<x>.md`, nao ha conta aberta: entregar so a lista de dados e dizer que o numero ficou sem conferencia. Nunca preencher por suposicao.

## Entrega obrigatoria final
- Numero com memoria, regra e fonte (exit 0), ou formula aberta com `[VERIFICAR]` e o dado que falta (exit 3), ou conta aberta marcada "conta nao conferida por script".
- Caminho do JSON de entrada usado.

## Guard
- Nunca numero de cabeca, nunca arredondar, nunca estimar o fator, o salario minimo ou o teto de um mes sem fonte.
- Nunca calcular a revisao do art. 29 contra o art. 3 da Lei 9.876: a tese e inviavel (ADIs 2.110/2.111; STF Tema 1.102 em `context/lei/temas-sumulas-prev.md`). Se pedida, explicar e oferecer a analise da cobranca indevida pela `analise-trilateral-previdenciario`.
- Selic contra a Fazenda: a fonte e a EC 113, art. 3 (`context/lei/ec-113-2021.md`), e nenhuma lei ordinaria.
- Nunca editar o script nem a tabela para fazer a conta fechar.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill calculos-previdenciarios - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
