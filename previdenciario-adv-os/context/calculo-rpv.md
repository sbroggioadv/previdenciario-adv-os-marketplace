# Conta aberta — atrasados, honorários, RPV × precatório e regime de atualização

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_rpv.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_rpv.py` · **Tabelas:** `scripts/data/salario-minimo.json`, `scripts/data/vigencias-tema905.json`; motor de atualização (Engine A, regimes `fazenda-ec113` e `fazenda-requisitorio-ec136`, cache de índices em `scripts/data/indices/`); motor de prazos (Engine B, rito `cpc`) · **Skill que lê:** `cumprimento-sentenca-inss`.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 7). O Manual de Cálculos da Justiça Federal usado é a **edição de julho/2026**, vigente (`context/lei/manual-cjf-2026-calculos-prev.md`); a requisição segue a **Res. CJF 983/2026** (`context/lei/res-cjf-983-2026.md`). Título judicial com critério próprio prevalece sobre o Manual (Manual 2026, item 4.1): o script só alerta.

---

## 1. Duas fases, escolhidas pela competência e pela data-base da requisição

| Fase | Período | Regra |
|---|---|---|
| **R1 — condenação** | das parcelas até a **data-base da conta** informada pelo juízo | Manual 2026, itens 4.3.1.1 e 4.3.2 (previdenciário) ou 4.2.1.1 e 4.2.2 (assistencial) |
| **R2 — requisição** | da data-base ao **pagamento** | Res. CJF 983/2026, art. 7º |

Os marcos são **competências**, não dias: a Selic de ago./2025 é computada em set./2025; a taxa legal de set./2025, em out./2025 (Manual 2026, item 4.3.1.1, Nota 4; item 4.2.2, Nota 7). Setembro/2025 não é fracionado por dias.

## 2. Conta aberta do regime de atualização — R1 (condenação)

### 2.1 Benefício previdenciário

| Competências | Correção | Juros de mora (desde a citação, salvo decisão em contrário) | Fonte |
|---|---|---|---|
| até ago./2006 | indexadores históricos do Manual (IGP-DI de maio/1996 a ago./2006) | até jun./2009: **1% a.m. simples** | Manual 2026, itens 4.3.1.1 e 4.3.2 |
| set./2006 a nov./2021 | **INPC** | jul./2009 a abr./2012: **0,5% a.m. simples**; maio/2012 a nov./2021: **juros da poupança** (0,5% a.m. se a Selic anual passar de 8,5%; senão, 70% da Selic mensalizada) | Manual 2026, itens 4.3.1.1 e 4.3.2; `lei-9494-1997.md`, art. 1º-F; `lei-8213-1991.md`, art. 41-A; `lei-11430-2006.md`; `temas-sumulas-prev.md`, STJ Tema 905 e STF Tema 810 |
| **consolidação em dez./2021** | INPC de nov./2021 (0,84%) e juros de dez./2021 (0,4412%); o resultado separa "principal" e "juros até 12/2021" | — | Manual 2026, item 4.3.1.1, Nota 5 |
| dez./2021 a ago./2025 | **Selic simples** sobre o consolidado (principal + juros), cada taxa aplicada no mês seguinte ao da competência; o resultado é a parcela "juros Selic", somada aos "juros até 12/2021"; vedada a cumulação com juros e correção | (na Selic) | `ec-113-2021.md`, art. 3º (redação original); Manual 2026, item 4.3.1.1, Notas 4 e 5, e item 4.2.2, Nota 1; STF Tema 1.419 |
| a partir de set./2025 | **INPC** | **taxa legal com dedução do INPC**, aplicada no mês seguinte ao da competência, sobre o principal corrigido; em set./2025, o principal e os juros acumulados recebem a correção | Manual 2026, item 4.3.1.1; item 4.3.2 e Nota 3 (tabela); item 4.2.1, Nota 6; `cc-excertos-prev.md`, art. 406; STF Tema 1.419 |

**Taxa legal com dedução do INPC.** Não é subtração improvisada de percentuais: usar a tabela do Manual (item 4.3.2, Nota 3), que vai da competência set./2025 (1,377047%) à competência **maio/2026** (aplicada em jun./2026). **Competências posteriores a maio/2026 (aplicações posteriores a jun./2026): fórmula**, até nova tabela do CJF.

**Juros:** excluído o mês de início e incluído o mês da conta; incidem sobre o valor atualizado (Manual 2026, item 4.1.3, Nota 5). O 1% até jun./2009 vem do Manual (DL 2.322/1987), não da literalidade do Tema 905; o produto segue o Manual e expõe a diferença em set. a dez./2006.

### 2.2 Benefício assistencial (BPC)

Segue as ações condenatórias em geral, **nunca** o 1% previdenciário (Manual 2026, item 4.3.1.1, Nota 3; itens 4.2.1.1 e 4.2.2): correção pelo **IPCA-E** (= IPCA-15 desde jan./2001) até nov./2021; juros de 0,5% a.m. até dez./2002, Selic de jan./2003 a jun./2009, 0,5% a.m. de jul./2009 a abr./2012, poupança de maio/2012 a nov./2021; Selic de dez./2021 a ago./2025; **a partir de set./2025, IPCA-15 + taxa legal com dedução do IPCA-15**.

## 3. Conta aberta do regime de atualização — R2 (da data-base ao pagamento)

| Data-base da requisição | Regra | Fonte |
|---|---|---|
| até dez./2021 | Selic sobre o valor consolidado (principal e juros) em dez./2021 | `res-cjf-983-2026.md`, art. 7º, §3º, I |
| de dez./2021 a ago./2025 | Selic só sobre o principal e os juros consolidados em dez./2021, somada aos juros Selic indicados na requisição — **até ago./2025** | art. 7º, §3º, II |
| **a partir de set./2025, para qualquer data-base** | o **menor** entre: (a) IPCA + juros simples de 2% a.a. sobre o principal atualizado; (b) Selic sobre o consolidado (principal e juros) | art. 7º, §3º, III |
| sempre | vedada a capitalização composta da Selic sobre os juros Selic | art. 7º, §4º |
| pagamento depois do prazo constitucional | até ago./2025, Selic sobre o consolidado posicionado na inscrição; desde set./2025, a comparação do §3º, III, posicionada na inscrição | art. 7º, §6º |

```
V_ipca  = (principal + juros) × fator_IPCA  +  principal × fator_IPCA × 2% a.a. (simples, fora do período de graça)
V_selic = (principal + juros não Selic) × (1 + Σ Selic)  +  juros Selic
valor   = min(V_ipca, V_selic)        (art. 7º, §3º, III; a Selic nunca incide sobre os juros Selic, §4º)
```

**Período sem juros de mora (graça).**
- Precatório pago até o fim do exercício seguinte: sem juros de mora nesse prazo (`res-cjf-983-2026.md`, art. 7º, §2º; `ec-113-2021.md`, art. 3º, §3º, redação da EC 136). A suspensão começa no **corte constitucional de apresentação**, não na origem do crédito: 1º de fevereiro na redação da EC 136 (`cf88-seguridade.md`, art. 100, §5º); 2 de abril para as apresentações de 2022 até a EC 136 (Manual 2026, cap. 5, Nota 1).
- RPV: sem juros de mora no prazo legal de pagamento, 60 dias a partir da apresentação (Manual 2026, cap. 5, Nota 2).
- A correção continua no período de graça; fora dele, os juros voltam (requisição complementar: Manual 2026, cap. 5, item 5.2).

## 4. Honorários, limite da RPV, via e prazos

| Termo | Conta | Fonte |
|---|---|---|
| base dos honorários sucumbenciais | só as prestações vencidas **até a sentença** | `temas-sumulas-prev.md`, STJ Súmula 111 |
| pagamento administrativo depois da citação | **não** reduz a base dos honorários: ela é a totalidade dos valores devidos na ação de conhecimento | `temas-sumulas-prev.md`, STJ Tema 1.050; `manual-cjf-2026-calculos-prev.md`, item 4.3.3, Nota 4 |
| sucumbenciais na requisição | requisição própria; **não** entram no valor do credor para classificar RPV × precatório | `res-cjf-983-2026.md`, art. 16, §1º |
| contratuais destacados | **integram** o crédito da parte na classificação; com renúncia, crédito + contratuais não passam do limite. Contratuais **iguais** ao limite cabem (soma = limite, crédito líquido da parte zero, com alerta `[VERIFICAR]`); só os **maiores** que o limite deixam a composição incompatível (exit 3) | art. 16, §§2º e 3º |
| limite da RPV federal | 60 salários mínimos (2026: 60 × 1.621,00 = R$ 97.260,00), por beneficiário | `res-cjf-983-2026.md`, art. 3º, I; `lei-10259-2001-jef.md`, art. 17, §1º, c/c art. 3º |
| valor comparado com o limite | o valor **atualizado até a transmissão ao tribunal**; o da data da conta não basta | `res-cjf-983-2026.md`, art. 3º, §4º |
| via | ≤ limite → RPV; > limite → precatório, ou RPV com **renúncia expressa ao excedente** | `res-cjf-983-2026.md`, art. 4º; `lei-10259-2001-jef.md`, art. 17, §4º |
| fracionar | **vedado** (parte RPV, parte precatório) | `cf88-seguridade.md`, art. 100, §8º; `lei-10259-2001-jef.md`, art. 17, §3º |
| prazo da RPV no JEF | **60 dias** da entrega da requisição | `lei-10259-2001-jef.md`, art. 17, caput |
| prazo da RPV no rito comum | **2 meses** da entrega da requisição | `cpc-excertos-prev.md`, art. 535, §3º, II |
| prazo do precatório | apresentado até **1º de fevereiro** → pago até 31/12 do **exercício seguinte**; depois do corte, no ciclo seguinte | `cf88-seguridade.md`, art. 100, §5º (redação da EC 136) |
| impugnação do INSS | 30 dias no rito do CPC; no JEF, sem prazo diferenciado para a Fazenda (o motor de prazos não tem rito JEF: usa `cpc` e avisa) | `cpc-excertos-prev.md`, arts. 534 e 535; `lei-10259-2001-jef.md`, art. 9º |

"Renúncia ao excedente" é o nome certo; "cisão" não é.

## 5. Passos para o advogado preencher

| # | Passo | Resultado |
|---|---|---|
| 1 | Natureza (previdenciária × assistencial), rito (JEF × comum), título com critério próprio? | ____ |
| 2 | Parcelas devidas e pagas por competência; citação; sentença; data-base da conta | ____ |
| 3 | R1 por fatia (seção 2), com os marcos 12/2021, 08/2025, 09/2025 e a data-base | ____ |
| 4 | Honorários: base até a sentença × percentual; sucumbenciais à parte, contratuais dentro do crédito | ____ |
| 5 | Valor atualizado até a transmissão; limite de 60 salários mínimos; via; renúncia | ____ |
| 6 | Apresentação: corte de 1º de fevereiro (ou 2 de abril, antes da EC 136) → prazo de pagamento e período de graça | ____ |
| 7 | R2 (seção 3) até o pagamento, com o menor entre IPCA + 2% e Selic | ____ |
| 8 | Listar **todo** dado que falta para fechar até o pagamento (seção 6) | ____ |
| 9 | Marcar no texto "conta não conferida por script" | — |

## 6. Leituras e pontos que mudam o resultado

- **M4 — salário mínimo do limite:** a Res. 983 fixa a atualização até a transmissão, mas não diz de que data é o mínimo; o produto usa o **vigente na transmissão**, como interpretação operacional declarada, e exige as datas de conta, expedição e transmissão. Testar a virada de ano.
- **M5 — R1 desde set./2025:** INPC + taxa legal com dedução do INPC (previdenciário); IPCA-15 + taxa legal com dedução do IPCA-15 (assistencial). Cálculo judicial (R1) e atualização da requisição (R2) não se sobrepõem no mesmo mês.
- **M8 — requisição com data-base anterior a set./2025:** Selic até ago./2025; **desde set./2025, art. 7º, §3º, III, automaticamente**; nunca IPCA + 2% antes de set./2025; não há opção livre entre regime antigo e novo.
- **Ponto aberto (precatório apresentado antes de set./2025):** no trecho de 2025 entre o início da graça e ago./2025, a Selic do art. 7º, §3º, II (que engloba juros) convive com a ausência de juros do §2º, e o texto não concilia. O script devolve esse trecho em `fatias_em_aberto`, com as duas contas (Selic do inciso II × atualização sem juros), exit 3.
- **Dados que faltam para fechar até o pagamento** — o exit 3 lista **todos**, não só um: série de juros da poupança (maio/2012 a nov./2021; ausente do cache, salvo se o consolidado de dez./2021 for informado); data do pagamento; espécie da requisição (RPV × precatório, que sai da via); data de apresentação (início da graça); taxa legal de competências posteriores a maio/2026. Uma regra pode estar fechada e o valor continuar incalculável por falta de dado.
- **ADI 7.873 (EC 136):** andamento não certificado; todo resultado com R2 traz `[VERIFICAR] ADI 7.873: andamento não certificado; reverificar` (o aviso antigo do motor de atualização é filtrado e não se repete).
- **Custas do INSS na Justiça Federal:** indeterminado (Lei 9.289/1996 não capturada); não afirmar isenção nem cobrança.

## 7. Caso resolvido à mão — RPV-01 (dados inventados)

Caso de referência RPV-01, "confere" na re-revisão especialista de 14/10/2026, no cenário de 2026; **pendente de conferência pelo advogado**.

**Entrada:** execução no **JEF**; conta da parte R$ 90.000,00 com data-base 02/2026; requisição transmitida ao tribunal em 03/2026; valor atualizado até a transmissão (calculado pelo motor de atualização e informado) = R$ 90.650,00.

| Passo | Conta | Fonte |
|---|---|---|
| limite | 60 × 1.621,00 (mínimo vigente na transmissão, M4) = **R$ 97.260,00** | Res. CJF 983/2026, art. 3º, I e §4º; `decreto-12797-2025-salario-minimo.md`, art. 1º |
| comparação | 90.650,00 ≤ 97.260,00 → **RPV**; margem **R$ 6.610,00** | — |
| prazo | rito JEF: **60 dias** da entrega da requisição (não os 2 meses do CPC) | Lei 10.259, art. 17 |
| juros no prazo | sem juros de mora nesses 60 dias | Manual 2026, cap. 5, Nota 2 |

Saída esperada: `via = "RPV"`, `valor_verificado = 90650.00`, `marco_verificacao = "transmissão ao tribunal (Res. CJF 983/2026, art. 3º §4º)"`, `limite_rpv = 97260.00`, `salario_minimo_do_limite = "vigente na transmissão (interpretação declarada, M4)"`, `prazo_pagamento = "60 dias da entrega da requisição (Lei 10.259, art. 17)"`. Sem o valor atualizado até a transmissão, exit 3: o valor da data da conta não basta.

Casos da mesma conta ("confere"): **RPV-04** — precatório apresentado em 01/02/2027 → pago até **31/12/2028**; em 02/02/2027 → até **31/12/2029**. **P-A** — (i) crédito de R$ 102.000,00 com R$ 5.000,00 de contratuais destacados: classifica-se R$ 102.000,00 > R$ 97.260,00 → precatório ou renúncia; (ii) crédito de R$ 97.000,00 e R$ 5.000,00 de sucumbenciais autônomos: classificam-se em separado → duas RPVs (cenário federal de 2026). **P-B** — unidade sintética com índices **fictícios**: principal R$ 10.000,00, fora da graça, IPCA 1,01 e Selic simples 2,5%: V_ipca = 10.100,00 + 202,00 = 10.302,00; V_selic = 10.250,00 → adota **R$ 10.250,00**.

## 8. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags: `--entrada`, `--versao`. Convenções: `data` = `AAAA-MM-DD`; `competencia` = `AAAA-MM`; `decimal` = texto com ponto; campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → exit 2; chave iniciada por `_` é comentário. A entrada traz **atrasados** (parcelas ou diferença mensal), **via** (`valor_atualizado_ate_transmissao`) ou os dois; sem nenhum dos dois → exit 2.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `natureza` | enum | sim | `previdenciaria` · `assistencial` |
| `rito` | enum | sim | `JEF` · `comum` |
| `parcelas` | lista | uma das formas de atrasados (1) | uma entrada por competência |
| `parcelas[].competencia` | competencia | sim | — |
| `parcelas[].devido` | decimal | sim | — |
| `parcelas[].pago` | decimal | não | padrão `"0.00"` |
| `diferenca_mensal` | decimal | uma das formas de atrasados (2) | com `competencia_inicial` e `competencia_final` |
| `competencia_inicial` | competencia | com `diferenca_mensal` | — |
| `competencia_final` | competencia | com `diferenca_mensal` | — |
| `data_citacao` | data | sim quando há atrasados | termo inicial dos juros |
| `data_sentenca` | data | sim quando há honorários sucumbenciais por percentual | corte da Súmula 111 |
| `data_base_conta` | competencia | sim quando há atrasados | data-base informada pelo juízo (fim de R1, início de R2) |
| `valor_consolidado_12_2021` | decimal | não | principal consolidado em dez./2021, quando já apurado (supre a falta da série da poupança) |
| `juros_consolidados_12_2021` | decimal | não | "juros até 12/2021", com `valor_consolidado_12_2021` |
| `data_expedicao` | data | não | expedição do requisitório |
| `data_apresentacao` | data | não | apresentação/entrega ao tribunal; define o corte, o prazo e a graça |
| `data_transmissao` | data | sim quando há `valor_atualizado_ate_transmissao` | marco do limite da RPV (M4) |
| `data_pagamento` | data | não | sem ela, R2 sai em fórmula com a lista de faltantes |
| `valor_atualizado_ate_transmissao` | decimal | não | valor do motor de atualização até a transmissão; sem ele, a via não fecha (exit 3) |
| `honorarios_percentual` | decimal | não | percentual dos sucumbenciais sobre a base da Súmula 111 |
| `honorarios_sucumbenciais` | decimal | não | valor já fixado (alternativa ao percentual; os dois juntos → exit 2) |
| `honorarios_contratuais` | decimal | não | valor destacado; integra o crédito na classificação |
| `renunciar_excedente` | bool | não | padrão `false` |
| `titulo_com_criterio_proprio` | texto | não | se houver, o script alerta que o título prevalece sobre o Manual |
| `salario_minimo` | decimal | não | ausente = tabela pela data da transmissão; ano fora da tabela → exit 3 |
| `datas_vencimento` | objeto | não | `{"AAAA-MM": "AAAA-MM-DD"}`: **vencimento individual devido** da competência, isto é, o dia em que ela deveria ter sido paga (Lei 8.213, art. 103, parágrafo único; CPC, art. 292, §1º), não o do pagamento realizado; fecha a base dos honorários (Súmula 111) quando a janela de pagamento do art. 41-A cruza a sentença. A data tem de cair na janela legal da competência (art. 41, §4º, nas redações históricas, e art. 41-A, §§2º a 4º, mesma tabela de regimes do valor da causa; renda em manutenção não informada, então vale a janela do §3º, que contém a do §2º, e antes da MP 404/2007 só o mês seguinte) e em dia de expediente bancário normal (§4º), conferido no calendário bancário, separado do forense: fora dela ou em sábado, domingo, feriado nacional ou data móvel da tabela do motor (segunda e terça de Carnaval, Sexta-feira da Paixão, Corpus Christi) → exit 2; dia de semana sem o motor de prazos ou com a tabela de feriados ausente, ilegível ou sem o ano (o calendário não decide o dia) → vencimento em aberto (exit 3), nunca fechado. Em 2007, data só possível com a antecipação do §3º (MP 404 sem data de vigência capturada) não vale nem é recusada: o vencimento fica em aberto (exit 3) |
| `honorarios_atualizados_ate_transmissao` | decimal | sim para classificar os sucumbenciais | honorários sucumbenciais atualizados até a transmissão (Res. CJF 983/2026, arts. 3º, §4º, e 16): é o valor que se confere contra o limite da RPV; sem ele, a via dos sucumbenciais sai em fórmula. Exige honorários sucumbenciais (percentual ou valor) e `valor_atualizado_ate_transmissao`; sem eles → exit 2 |

## 9. Saída e códigos

JSON com `principal_corrigido` e `juros` por fatia (marcos 12/2021, 08/2025, 09/2025 e `data_base_conta`), `fatias_em_aberto`, `total_parte`, `base_honorarios`, `honorarios`, `classificacao_honorarios`, `limite_rpv`, `valor_verificado`, `via` (`RPV` · `precatorio` · `RPV-com-renuncia`), `valor_renunciado`, `prazo_pagamento`, `pagamento_no_prazo_constitucional`, `dados_faltantes` (lista completa), `alertas` (ADI 7.873; vedação de fracionar; taxa legal sem tabela depois de maio/2026; JEF sem prazo diferenciado), `parametros_usados`, `regra`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado |
| 2 | entrada inválida (inclusive sem atrasados nem via; duas formas de atrasados; percentual e valor de sucumbenciais juntos; `datas_vencimento` fora da janela legal da competência ou em dia sem expediente bancário) |
| 3 | qualquer item de `dados_faltantes` impede o valor (série da poupança, pagamento, apresentação, taxa legal sem tabela, valor atualizado até a transmissão) ou há trecho em `fatias_em_aberto` |
