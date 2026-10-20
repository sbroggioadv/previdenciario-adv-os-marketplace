# Conta aberta — RMI de concessão e de revisão, decadência e prescrição

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_rmi.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_rmi.py` · **Tabelas:** `scripts/data/salario-minimo.json`, `scripts/data/teto-rgps.json`; feriados nacionais do motor de prazos (dias úteis da janela de pagamento do art. 41-A) · **Skills que leem:** `acao-revisional-rmi`, `analise-carta-concessao-indeferimento`, `calculos-previdenciarios`, `planejamento-previdenciario`. A regra vem de `context/calculo-transicao.md`.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 5).

---

## 1. Concessão — fórmulas, com a fonte de cada termo

```
media      = soma dos salários de contribuição desde 07/1994, já corrigidos ÷ divisor
divisor    = número de salários                                   (regra geral)
           = max(número de salários, 108)                         (art. 135-A, ver abaixo)
sb         = min(max(media, salário mínimo da DIB), teto da DIB)  (art. 29, §2º: piso e teto do SB, ANTES do coef)
coef       = 60% + 2% × (anos de contribuição − 20)  homem        (mínimo 60%)
           = 60% + 2% × (anos de contribuição − 15)  mulher e especial de 15
           = 100%  no pedágio de 100% (art. 20) e na incapacidade permanente acidentária
rmi        = sb × coef, depois piso da renda (1 salário mínimo) e teto
```

O piso do salário de benefício vem **antes** do coeficiente; o piso da renda, no fim, não o substitui. Exemplo (DIB em 01/01/2026, mínimo R$ 1.621,00): mulher com 41 anos de contribuição, média 108.000 ÷ 108 = 1.000,00; coef = 60% + 2% × (41 − 15) = 112%; SB = max(1.000,00; 1.621,00) = 1.621,00; RMI = 1.621,00 × 112% = **1.815,52**. Aplicar o coeficiente à média (1.000,00 × 112% = 1.120,00) e só depois o piso da renda dá 1.621,00: R$ 194,52 a menos por mês.

| Termo | Fonte |
|---|---|
| média de 100% desde 07/1994 | `context/lei/ec-103-2019.md`, art. 26, caput; PBC de 100% vem da EC, não da Lei 13.846 |
| limite da média ao teto | art. 26, §1º; teto de 2026 R$ 8.475,55 em `portaria-interministerial-mps-mf-13-2026.md`, art. 2º |
| **piso e teto do SB** (antes do coeficiente) | `lei-8213-1991.md`, art. 29, §2º ("não será inferior ao de um salário mínimo, nem superior ao do limite máximo do salário-de-contribuição na data de início do benefício"); valores de 2026 em `portaria-interministerial-mps-mf-13-2026.md`, art. 2º |
| **divisor mínimo de 108** | filiado **até 07/1994**, espécie **aposentadoria, exceto a por incapacidade permanente**, fato gerador **a partir de 05/05/2022**: `lei-8213-1991.md`, art. 135-A; `lei-14331-2022.md`; `in-128-2022-inss.md`, art. 228, §4º |
| coeficiente 60% + 2% | art. 26, §2º; acréscimo a partir de 15 anos para mulher e especial de 15, §5º |
| coeficiente 100% | art. 26, §3º (I: art. 20; II: incapacidade permanente acidentária) |
| art. 17 | média × fator previdenciário (art. 17, parágrafo único); sem tábua do IBGE → fórmula |
| direito adquirido até 13/11/2019 — tempo de contribuição | regra anterior: média dos 80% maiores × fator, ou opção do art. 29-C sem fator (pontos de 13/11/2019 **ou** os exigidos na data em que o segurado os completou antes, §4º: ver `context/calculo-transicao.md`): `lei-8213-1991.md`, arts. 29, I, e 29-C; `lei-9876-1999.md`, art. 3º (cogente); `in-128-2022-inss.md`, arts. 229 e 233, IV, "a" → fórmula sem a tábua |
| direito adquirido até 13/11/2019 — **idade, sem fator** | média dos 80% maiores; o segurado tem a **opção pela não aplicação do fator** (aplica-se o fator só se for mais vantajoso); coeficiente **70% + 1% por grupo de 12 contribuições, até 100%**. Fonte: `lei-9876-1999.md`, art. 7º; `in-128-2022-inss.md`, arts. 229, §2º, I, e 233, III, "a"; `lei-8213-1991.md`, art. 50 |
| direito adquirido até 13/11/2019 — **especial, sem fator** | média dos 80% maiores, **sem fator** (o art. 29, II, não o prevê para a especial); coeficiente **100%**. Fonte: `lei-8213-1991.md`, arts. 29, II, e 57, §1º; `in-128-2022-inss.md`, art. 233, V, "a" |
| direito adquirido — divisor mínimo da regra anterior | filiado até 28/11/1999: divisor não inferior a 60% do período decorrido de 07/1994 até a DIB. Fonte: `lei-9876-1999.md`, art. 3º, §2º; `in-128-2022-inss.md`, art. 230 |
| piso | `cf88-seguridade.md`, art. 201, §2º; valor do ano em `decreto-12797-2025-salario-minimo.md` (2026) e `decreto-12342-2024-salario-minimo.md` (2025) |

**Descarte** (`ec-103-2019.md`, art. 26, §6º; `in-128-2022-inss.md`, art. 228, §1º): podem sair da média as contribuições que a reduzam, desde que mantido o tempo mínimo da regra; o tempo descartado **não conta para nada**, nem para o acréscimo de 2%. Conta: para cada quantidade k de menores salários descartados (sem baixar do tempo mínimo), recalcular a média (com o divisor mínimo de 108 mantido, se aplicável) e o coeficiente com o tempo restante; descartar **só se a RMI aumentar**.

## 2. Revisão — diferenças, decadência e prescrição

```
diferenca_mensal   = rmi_devida − rmi_paga
decadência: início = dia 1º do mês seguinte ao do recebimento da primeira prestação
            termo nominal = início + 10 anos, no dia de igual número (CC, art. 132, §3º)
            fim    = termo nominal; se cair em dia sem expediente (fim de semana ou feriado — Lei 662/1949,
                     art. 1º), o seguinte dia útil                     (CC, art. 132, §1º)
            decadente = data_ajuizamento (ou do pedido de revisão) > fim
            dia útil pelo calendário do motor de prazos, em duas leituras: só feriados nacionais (estrita) e
            também carnaval, Paixão e Corpus Christi (ampla); se as duas divergem, ou sem calendário, `fim` = null
            e `decadente` = null ([VERIFICAR] o expediente) no marco entre o primeiro dia útil possível e o
            último — nunca true; feriado estadual ou municipal não está na tabela: [VERIFICAR] quando a
            decadência se consumou há poucos dias
prescrição: prescreve cada parcela cujo VENCIMENTO DEVIDO (a data em que deveria ter sido paga) é anterior a
            (data_ajuizamento − 5 anos); a data de um pagamento feito depois NÃO desloca o marco
            vencimento devido da competência = JANELA do art. 41-A, §§2º e 3º (a lei não fixa dia único):
                acima de 1 salário mínimo: do 1º ao 5º dia útil do mês seguinte (§2º)
                até 1 salário mínimo:      do 5º dia útil antes do fim do mês da competência
                                           ao 5º dia útil do mês seguinte (§3º)
                dia útil = expediente bancário normal (§4º)
            prescrita se ajuizamento > último dia da janela + 5 anos
            devida    se a janela inteira acaba antes do ajuizamento e o 1º dia + 5 anos o alcança
            janela que cruza o corte ou o ajuizamento: em aberto, salvo vencimento individual informado
                (campo datas_vencimento: o dia em que aquela competência DEVERIA ter sido paga)
parcelas_nao_prescritas = competências não prescritas cuja janela (ou vencimento informado) acabou antes do ajuizamento
diferenca_nominal  = Σ diferenca_mensal das não prescritas + diferenças do abono anual não prescritas
```

| Termo | Fonte |
|---|---|
| decadência de 10 anos, do dia 1º do mês seguinte ao primeiro recebimento | `lei-8213-1991.md`, art. 103, I |
| vence no dia de igual número | `cc-excertos-prev.md`, art. 132, §3º |
| termo em feriado prorroga-se ao seguinte dia útil | `cc-excertos-prev.md`, art. 132, §1º; feriados: `lei-662-1949-feriados.md`, art. 1º |
| prescrição quinquenal de cada prestação, contada "da data em que deveriam ter sido pagas" (vencimento devido, não pagamento realizado) | `lei-8213-1991.md`, art. 103, parágrafo único |
| vencimento devido (data em que a prestação deveria ser paga): acima de 1 salário mínimo, do 1º ao 5º dia útil do mês seguinte; até 1 salário mínimo, entre o 5º dia útil antes do fim do mês e o 5º dia útil do mês seguinte | `lei-8213-1991.md`, art. 41-A, §§2º e 3º (redação da Lei 11.665/2008; as redações anteriores aparecem riscadas no arquivo); `in-128-2022-inss.md`, art. 608 (mesma regra) |
| abono anual | `lei-8213-1991.md`, art. 40; data de pagamento pelo ato do ano, art. 1º, I e II: 2021, maio e junho (`decreto-10695-2021-abono.md`); 2022, abril e maio (`decreto-10999-2022-abono.md`); 2023, maio e junho (`decreto-11517-2023-abono.md`); 2024, abril e maio (`decreto-11947-2024-abono.md`); 2025, abril e maio (`decreto-12425-2025-abono.md`); 2026, abril e maio (`decreto-12884-2026-abono.md`); ano sem ato capturado → alerta, sem data presumida |
| correção das diferenças | regime de atualização em `context/calculo-rpv.md` (seção do regime); esta conta é nominal |

## 3. Passos para o advogado preencher

| # | Passo | Resultado |
|---|---|---|
| 1 | Modo: concessão ou revisão | ____ |
| 2 | Espécie (aposentadoria × incapacidade permanente × outra), regra e fato gerador (DER ou DII) | ____ |
| 3 | Filiação até 07/1994 e fato gerador desde 05/05/2022 em aposentadoria que não é por incapacidade permanente? → divisor mínimo 108 | sim / não |
| 4 | Soma e quantidade dos salários de contribuição desde 07/1994, corrigidos | ____ / ____ |
| 5 | Média, limite ao teto | ____ |
| 6 | Anos de contribuição e coeficiente (sem teto de 100% no percentual) | ____ |
| 7 | Descarte: testar e ficar só se a RMI subir | ____ |
| 8 | Piso e teto vigentes na DIB (Lei 8.213, art. 29, §2º), não no fato gerador; sem DIB e com limites diferentes na janela possível dela, conta aberta | ____ |
| 9 | Revisão: data do primeiro pagamento → fim da decadência | ____ |
| 10 | Revisão: corte prescricional (ajuizamento − 5 anos) e competências devidas, pela janela de pagamento de cada competência (ou pelo vencimento individual devido, se documentado; nunca pela data de um pagamento feito com atraso) | ____ |
| 11 | Marcar no texto "conta não conferida por script" | — |

## 4. Leituras e pontos que mudam o resultado

- **P4 (divisor × descarte):** o descarte não elimina o divisor mínimo; descartando, a média é soma restante ÷ max(salários restantes, 108). A entrada **tem de dizer a espécie**: sem excluir expressamente a incapacidade permanente, o divisor fica indeterminado (exit 2 por falta de `especie`).
- **Média informada sem soma e quantidade** num caso do art. 135-A: não dá para aplicar o divisor → exit 3 com a fórmula.
- **M3:** coeficiente acima de 100% é devido; o limite é monetário.
- **M7:** fator previdenciário sem a tábua do IBGE → fórmula e lista de dados faltantes (exit 3).
- **P5:** decadência vence no dia de igual número (§3º) e, caindo em dia sem expediente, no seguinte dia útil (§1º; QA final r6, C1: termo nominal 01/05/2026, feriado, vence em 04/05/2026). Sem calendário, ou com as leituras do dia útil divergentes, `decadente` = null: não é decadência consumada e não impede a revisão; o advogado confere o expediente do dia.
- **Janela do art. 41-A:** a faixa do benefício (acima ou até 1 salário mínimo) não chega pelos CAMPOS; o script usa a janela do §3º, que contém a do §2º, e lê o dia útil bancário com e sem carnaval, Sexta-feira da Paixão e Corpus Christi. Competência cuja janela cruza o corte ou o marco sai em `competencias_em_aberto` (exit 3), até o advogado informar o vencimento devido em `datas_vencimento` (nome antigo: `datas_pagamento`; ver a seção 6).
- **Direito adquirido:** o script não faz a conta da regra anterior (`regra = adquirido-anterior` → exit 3 com a fórmula); a conta aberta é a da tabela da seção 1, por espécie: tempo (fator ou art. 29-C), idade (sem fator por opção, 70% + 1%), especial (sem fator, 100%).
- **Sem média nem salários:** nunca RMI de cabeça; sai a fórmula (exit 3).
- **Reajuste da renda na revisão (W3-reajustes r2):** `scripts/data/reajustes-rgps.json` é a fonte única de **quando** o benefício acima do mínimo é reajustado. Data em que só o salário mínimo ou o teto mudam, num ano que tem a sua linha de reajuste (ex.: 01/02/2004, 01/03/2011, 01/02/2020, 01/05/2023), não pede fator: a renda se mantém, e o piso e o teto da competência valem (`lei-8213-1991.md`, art. 41-A, caput, e art. 33). Ano sem linha para a data (2027 em diante) continua abrindo a conta (exit 3). Desde a 2.0.1, 01/08/2006 fecha: 5,01% (ou o pro rata do Anexo I) sobre a **renda de março/2006**, em substituição aos 5,00% de abril, só para DIB até 31/03/2006 (`lei-11430-2006.md`, art. 3º; `portaria-mps-342-2006-reajuste.md`, art. 1º); e o teto de jan.–fev./2011 é o do ato (R$ 3.691,74, PI 407/2011), não o do AEPS (`serie-teto-rgps-1994-2026.md`). DIB até 2003 segue em aberto: as linhas de 1997 a 2001 estão na tabela, mas o aumento do mínimo de abril/maio era descontado no reajuste de junho (art. 3º das portarias), compensação não modelada, e faltam 1995 e 1996. **Arredondamento** da renda reajustada: ao centavo, meio para cima (ROUND_HALF_UP). A fonte não fixa a regra; é **interpretação operacional** (ex.: 500,00 × 1,04385 = 521,925 → 521,93).

## 5. Caso resolvido à mão — RMI-05 (dados inventados)

Caso de referência RMI-05, "confere" na re-revisão especialista de 14/10/2026; **pendente de conferência pelo advogado**.

**Entrada:** homem nascido em 01/01/1961; filiado em 01/1985; 114 meses de contribuição de 01/1985 a 06/1994 e **80 salários de contribuição** depois de 07/1994, cada um de R$ 5.000,00 (já corrigidos); soma desde 07/1994 = R$ 400.000,00. (a) aposentadoria por idade (art. 18), DER em 02/03/2026; (b) aposentadoria por incapacidade permanente previdenciária, mesmos salários, DII em 10/02/2026.

| Passo | (a) idade | (b) incapacidade permanente | Fonte |
|---|---|---|---|
| tempo | 114 + 80 = 194 meses = 16a 2m | idem | — |
| requisito | 65 anos em 01/01/2026 e 15 anos → cumpre o art. 18 | — | EC 103, art. 18 |
| divisor | filiado até 07/1994, aposentadoria comum, fato gerador depois de 05/05/2022 → max(80, 108) = **108** | exceção expressa → **80** | Lei 8.213, art. 135-A; IN 128, art. 228, §4º |
| média | 400.000,00 ÷ 108 = **3.703,70** | 400.000,00 ÷ 80 = **5.000,00** | EC 103, art. 26, caput |
| coeficiente | 16 anos, homem, nenhum acima de 20 → **60%** | fato gerador depois de 13/11/2019 → **60%** | art. 26, §2º |
| RMI | 3.703,70 × 0,60 = **R$ 2.222,22** | 5.000,00 × 0,60 = **R$ 3.000,00** | — |
| piso e teto | R$ 1.621,00 e R$ 8.475,55 não atuam | idem | — |

Sem o divisor mínimo, (a) daria R$ 3.000,00 e superestimaria a RMI em R$ 777,78 por mês. Saída esperada: (a) `divisor_aplicado = 108`, `media = 3703.70`, `coeficiente = 0.60`, `rmi = 2222.22`; (b) `divisor_aplicado = 80`, `media = 5000.00`, `coeficiente = 0.60`, `rmi = 3000.00`.

Armadilha da mesma conta ("confere"): **R-B** — mulher, 180 salários de R$ 3.000,00 e 60 de R$ 1.000,00: sem descarte, 600.000 ÷ 240 = 2.500,00 × 70% = R$ 1.750,00; descartando os 60 menores, 540.000 ÷ 180 = 3.000,00, tempo 15 anos, 60% → **R$ 1.800,00**; nunca R$ 2.100,00 (manter 70% com tempo descartado).

## 6. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags: `--entrada`, `--versao`. Convenções: `data` = `AAAA-MM-DD`; `decimal` = texto com ponto; campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → exit 2; chave iniciada por `_` é comentário.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `modo` | enum | sim | `concessao` · `revisao` |
| `especie` | enum | sim | `aposentadoria` · `incapacidade-permanente` · `outra` |
| `regra` | enum | sim no modo `concessao` | `art15` · `art16` · `art17` · `art18` · `art19` · `art19-especial` · `art20` · `art21` · `adquirido-anterior` · `incapacidade-permanente` · `incapacidade-permanente-acidentaria` |
| `sexo` | enum | sim | `M` · `F` |
| `data_filiacao` | data | sim | primeira filiação ao RGPS |
| `fato_gerador` | data | sim | DER (aposentadoria) ou DII (incapacidade) |
| `salarios_contribuicao` | lista de decimal | uma das três formas de média (1) | salários desde 07/1994, já corrigidos; obrigatória se `descartar = true` |
| `media` | decimal | uma das três formas de média (2) | média já calculada; recusada sozinha no caso do art. 135-A (exit 3) |
| `soma` | decimal | uma das três formas de média (3), com `quantidade` | soma dos salários desde 07/1994, corrigidos |
| `quantidade` | inteiro | com `soma` | número de salários somados |
| `tempo_contribuicao_anos` | inteiro | sim no modo `concessao` | anos completos |
| `tempo_contribuicao_meses` | inteiro | não; só no modo `concessao` | tempo de contribuição em meses, tirado do CNIS; compatível com `tempo_contribuicao_anos` (meses ÷ 12 arredondado para baixo), senão exit 2. Com ele o descarte usa o tempo exato (EC 103, art. 26, §6º); sem ele, se o melhor descarte depender dos meses além dos anos completos, exit 3 |
| `atividade_especial_anos` | enum | sim quando `regra` = `art19-especial` ou `art21` | `15` · `20` · `25` |
| `descartar` | bool | não | padrão `false` |
| `tempo_minimo_da_regra_anos` | inteiro | sim quando `descartar = true` | tempo mínimo que o descarte tem de preservar |
| `fator` | decimal | não | fator previdenciário já apurado; sem ele, `art17` e `adquirido-anterior` saem em exit 3 com a fórmula |
| `teto` | decimal | não | ausente = tabela pela data da DIB (Lei 8.213, art. 29, §2º), não a do fato gerador; sem `dib`: na aposentadoria, cada data da janela DER − 90 dias a DER (leituras divergentes → exit 3); na incapacidade permanente, exit 3 (a DIB é posterior à DII); ano fora da tabela → exit 3 |
| `salario_minimo` | decimal | não | ausente = tabela pela mesma data da DIB, com as mesmas regras do `teto`; ano fora da tabela → exit 3 |
| `rmi_paga` | decimal | sim no modo `revisao` | — |
| `rmi_devida` | decimal | sim no modo `revisao` | ou recalculada no modo `concessao` e informada aqui |
| `dib` | data | sim no modo `revisao`; em `concessao`, quando os limites do art. 29, §2º, mudam conforme a DIB | no modo `concessao`, sem ela a aposentadoria considera a DER e o desligamento até 90 dias antes (Lei 8.213, arts. 49, I, "a", e 54); se as leituras divergem, exit 3 |
| `media_acima_do_teto` | bool | sim quando `modo = revisao` com DIB no período de incorporação do teto de um reajuste capturado | `true` se a média ficou acima do teto na DIB: a diferença é incorporada no primeiro reajuste (Portaria 6/2025, art. 6º, DIB em 2024; Portaria 13/2026, art. 6º, DIB em 2025); ausente nesse período → exit 3 |
| `data_primeiro_pagamento` | data | sim no modo `revisao` | a DER não a substitui |
| `data_ajuizamento` | data | sim no modo `revisao`, salvo se houver `data_requerimento_revisao` | — |
| `data_requerimento_revisao` | data | alternativa a `data_ajuizamento` | pedido administrativo de revisão |
| `abono` | bool | sim no modo `revisao` | benefício com abono anual (Lei 8.213, art. 40) |
| `datas_vencimento` | objeto | não; só no modo `revisao` | `{"AAAA-MM": "AAAA-MM-DD"}`: **vencimento individual devido** de cada competência, isto é, o dia em que ela deveria ter sido paga (dentro da janela do art. 41-A), tirado de documento do INSS que o fixe; competência fora do período da DIB ao marco, ou data anterior ao próprio mês, → exit 2. Sem ele, vale a janela do art. 41-A. |

**Vencimento devido × pagamento realizado.** A prescrição corre "a contar da data em que deveriam ter sido pagas" (`lei-8213-1991.md`, art. 103, parágrafo único). Se a competência foi paga depois do vencimento (crédito atrasado, pagamento administrativo posterior), essa data **não** entra no campo e não desloca o marco: com vencimento devido em 05/10/2021, pagamento em 05/11/2021 e ajuizamento em 15/10/2026, a parcela está fora do quinquênio (05/10/2021 < 15/10/2021), embora o pagamento esteja dentro. O pagamento realizado não faz parte do contrato; o que ele afeta é o valor a abater (`rmi_paga`), não a data.

Usar exatamente uma das três formas de média; duas ao mesmo tempo → exit 2.

## 7. Saída e códigos

Concessão: `media`, `divisor_aplicado` (com o fundamento), `media_limitada_teto`, `coeficiente`, `rmi`, `descarte` (o que saiu, média nova, coeficiente novo, `compensou`). Revisão: `diferenca_mensal`, `parcelas_nao_prescritas` (quantidade, de, até, competências), `parcelas_prescritas`, `abonos_nao_prescritos`, `abonos_em_aberto`, `competencias_em_aberto`, `diferenca_nominal`, `prazo_decadencial_final`, `decadente`. Sempre: `alertas`, `parametros_usados`, `regra`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado |
| 2 | entrada inválida (inclusive sem `especie`, ou com duas formas de média) |
| 3 | sem média nem salários; média sem soma e quantidade no caso do art. 135-A; fator sem a tábua (art. 17); `regra = adquirido-anterior` (conta fora do script); piso ou teto do ano fora da tabela; revisão com competência ou abono cuja janela de pagamento cruza o corte da prescrição ou o marco (`competencias_em_aberto`); motor de prazos ausente no modo revisão |

---

---

## Cobertura temporal do script (COBERTURA)

Fonte: `scripts/calc/calc_previdenciario_rmi.py`, constante `COBERTURA`.

**Regra:** fato (data indicada na coluna *chave*) fora do intervalo em que a linha é a regra vigente → o script **não fecha veredito pela regra posterior**: sai em **exit 3** com `formula_aberta`, a regra histórica e a fonte de cada borda, para o advogado refazer a conta. Borda sem fonte capturada em `context/lei/` fica no lado conservador (o primeiro dia certo). A tabela abaixo é a constante `COBERTURA` do script, transcrita na W3-integ-2 (18/10/2026); mudou o script, muda esta tabela.

| Regra (chave) | De | Até | Coberto | Regra aplicada no intervalo | Fonte das bordas |
|---|---|---|---|---|---|
| `concessao/aposentadoria` | — | 28/11/1999 | **não** → exit 3 | requisitos até 28/11/1999: últimos 36 salários em até 48 meses (IN 128, art. 221, II, "b") | até: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221, II) |
| `concessao/aposentadoria` | 29/11/1999 | 13/11/2019 | **não** → exit 3 | direito adquirido até 13/11/2019 (EC 103, art. 3º): 80% maiores salários, coeficiente e fator da modalidade (FORMULA_ADQUIRIDO) | de: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221, II); até: EC 103/2019, publicada em 13/11/2019 (EC 103, arts. 3º e 36, III; IN 128, art. 233) |
| `concessao/aposentadoria` | 14/11/2019 | — | sim | EC 103, arts. 15 a 21 e 26 (média de 100% desde 07/1994; divisor mínimo do art. 135-A para fato gerador desde 05/05/2022 — Lei 14.331/2022, IN 128, art. 228, §4º — implementado dos dois lados) | de: EC 103/2019, publicada em 13/11/2019 (EC 103, arts. 3º e 36, III; IN 128, art. 233) |
| `concessao/incapacidade-permanente` | — | 28/11/1999 | **não** → exit 3 | últimos 36 salários em até 48 meses (IN 128, art. 221, II, "b"); até 28/04/1995, coeficiente de 80% + 1% por grupo de 12 contribuições, até 100% (Lei 8.213, art. 44, redação original — context/lei/lei-8213-1991.md:1199-1203); de 29/04/1995 (Lei 9.032 — IN 128, art. 352, §1º), 100% | até: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221, II) |
| `concessao/incapacidade-permanente` | 29/11/1999 | 13/11/2019 | sim | 100% da média dos 80% maiores (Lei 8.213, arts. 29, II, redação da Lei 9.876/1999, e 44, redação da Lei 9.032/1995; IN 128, arts. 229 e 233, II, "a") | de: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221, II); até: EC 103/2019, publicada em 13/11/2019 (EC 103, arts. 3º e 36, III; IN 128, art. 233) |
| `concessao/incapacidade-permanente` | 14/11/2019 | — | sim | EC 103, art. 26, §§2º, 3º, II, e 5º (média de 100%; sem o divisor mínimo do art. 135-A) | de: EC 103/2019, publicada em 13/11/2019 (EC 103, arts. 3º e 36, III; IN 128, art. 233) |
| `revisao/decadencia` | — | 27/06/1997 | sim | 10 anos contados de 01/08/1997 (STF Tema 313, tese II) | até: STF Tema 313, tese II (context/lei/temas-sumulas-prev.md:83-89): benefícios concedidos antes do advento da MP 1.523/1997 contam os 10 anos de 01/08/1997; o advento em 28/06/1997 (edição de 1997 da MP) vem do brief r13 e não está capturado em context/lei/ — a IN 128 só registra a MP 1.523 original, de 14/10/1996 (in-128-2022-inss.md:1305), que não trazia a decadência [VERIFICAR] |
| `revisao/decadencia` | 28/06/1997 | 31/12/2004 | **não** → exit 3 | três redações do art. 103 em sequência — 10 anos (Lei 9.528/1997), 5 anos (Lei 9.711, de 20/11/1998) e 10 anos (Lei 10.839/2004) | de: STF Tema 313, tese II (context/lei/temas-sumulas-prev.md:83-89): benefícios concedidos antes do advento da MP 1.523/1997 contam os 10 anos de 01/08/1997; o advento em 28/06/1997 (edição de 1997 da MP) vem do brief r13 e não está capturado em context/lei/ — a IN 128 só registra a MP 1.523 original, de 14/10/1996 (in-128-2022-inss.md:1305), que não trazia a decadência [VERIFICAR]; até: Lei 10.839, "de 2004" (redação do art. 103 em context/lei/lei-8213-1991.md:2192): o dia de início (MP 138/2003) não está capturado; a borda é 01/01/2005, primeiro dia certamente sob o texto dela |
| `revisao/decadencia` | 01/01/2005 | — | sim | 10 anos do dia 1º do mês seguinte ao do primeiro pagamento (Lei 8.213, art. 103, redação da Lei 10.839/2004, mantida no art. 103, I, pela Lei 13.846/2019 — lei-8213-1991.md:2192-2200) | de: Lei 10.839, "de 2004" (redação do art. 103 em context/lei/lei-8213-1991.md:2192): o dia de início (MP 138/2003) não está capturado; a borda é 01/01/2005, primeiro dia certamente sob o texto dela |
