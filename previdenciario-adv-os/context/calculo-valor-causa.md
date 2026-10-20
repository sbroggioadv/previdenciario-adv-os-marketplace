# Conta aberta — valor da causa e alçada do JEF

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_valor_causa.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_valor_causa.py` · **Tabela:** `scripts/data/salario-minimo.json`; motor de atualização (Engine A) quando corrige as vencidas; feriados nacionais do motor de prazos (dias úteis da janela de pagamento do art. 41-A) · **Skills que leem:** `peticao-inicial-previdenciaria`, `bpc-loas-previdenciario`.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 6).

---

## 1. Fórmulas, com a fonte de cada termo

```
vencidas        = Σ renda(c) de cada competência desde a DIB VENCIDA ANTES do ajuizamento (CPC, art. 292, §1º:
                  prestações vencidas, inclusive as não pagas); vencimento = data em que DEVERIA ter sido paga:
                  com vencimento individual informado (datas_vencimento): vencida se essa data < ajuizamento;
                    a data tem de cair dentro da janela legal da competência e em dia de expediente bancário
                    (fora da janela, sábado, domingo, feriado nacional ou data móvel sem expediente
                    bancário -- Carnaval, Paixão, Corpus Christi -> exit 2; calendário que não decide o
                    dia, sem o motor de prazos ou sem a tabela de feriados legível -> exit 3; art. 41-A, §4º)
                  sem ela, pela JANELA de pagamento (a lei distribui o pagamento; não há dia único):
                    competência desde 01/2008 (art. 41-A, MP 404/2007 e Lei 11.665/2008):
                      rmi acima de 1 mínimo: do 1º ao 5º dia útil do mês seguinte (§2º)
                      rmi até 1 mínimo: do 5º dia útil antes do fim do mês ao 5º do seguinte (§3º)
                      o parágrafo segue o valor DA PRÓPRIA COMPETÊNCIA; no BPC (um mínimo do mês), sempre o §3º
                    competência de 2007 (fronteira: a MP 404 só tem o ano capturado):
                      acima de 1 mínimo: §2º; até 1 mínimo, a janela vai do início do §3º ao fim do §2º, e
                      vencimento informado antes do mês seguinte -> em aberto (exit 3), nunca fechado pelo §3º
                    competência de 03/2004 a 12/2006, paga a partir de abril/2004: do 1º ao 5º dia útil do mês
                      seguinte para TODO benefício, sem antecipação (art. 41, §4º, redação da Lei 10.699/2003;
                      art. 41-A, §2º, redação da Lei 11.430/2006)
                    competência de 01/1993 a 02/2004: do 1º ao 10º dia útil do mês seguinte
                      (art. 41, §4º, redação da Lei 8.444/1992)
                    competência de 07/1991 a 12/1992: até o 10º dia útil do mês seguinte (redação original
                      ou da Lei 8.444/1992, sem o dia capturado: janela desde o 1º dia do mês seguinte)
                    antes de 2007, data no próprio mês da competência nunca é vencimento devido -> exit 2
                    competência anterior a 07/1991: sem regime capturado -> exit 3 até informar o vencimento
                    dia útil = expediente bancário normal (§4º)
                  janela inteira antes do ajuizamento -> vencida; começa no ajuizamento ou depois -> não;
                  janela que cruza o ajuizamento -> em aberto (exit 3, com as leituras com e sem a competência)
                  até informar o vencimento individual
                  PRESCRIÇÃO (Lei 8.213, art. 103, parágrafo único; campo prescricao): fora da soma a competência
                  cujo vencimento devido é anterior ao corte = marco − 5 anos (CC, art. 132, §3º: 29/02 → 01/03);
                    marco = ajuizamento (regular) ou marco_prescricional (interrompida); nao_corre = sem corte
                    (menor, incapaz ou ausente); vencimento ou janela que cruza o corte -> em aberto (exit 3,
                    leituras com e sem a competência), inclusive na faixa dos dias não úteis logo antes do
                    marco (CC, art. 132, §1º: o prazo que expira neles se prorroga até o marco)
                  prescricao ausente: se o corte regular não alcança nada, a conta segue; se alcança -> exit 3,
                    sem total, com as contas sem e com o corte em formula_aberta.leituras
abono_vencidas  = Σ por ano: (meses do ano com benefício ÷ 12) × renda do ano (a de dezembro, art. 40,
                  parágrafo único; 1ª parcela = 50% da renda da competência dela), só de abono já vencido;
                  cada parcela prescreve com a competência que a carrega (sem calendário do ano, só quando todas
                  as competências possíveis prescreveram; no meio, em aberto)
vincendas_12    = 12 × renda(propositura)       (a vigente no ajuizamento; nunca antecipa o reajuste seguinte)
renda(c)        = rmi na DIB, reajustada em cada data de reajuste (Lei 8.213, art. 41-A, caput: a do salário
                  mínimo) pelo fator da Portaria do ano (Anexo I, pro rata pelo mês da DIB no primeiro reajuste),
                  arredondada ao centavo, meio para cima (ROUND_HALF_UP: interpretação operacional, a fonte não fixa
                  a regra); piso de um salário mínimo (CF, art. 201, §2º; não se aplica se a rmi já está abaixo do
                  mínimo da DIB, como no auxílio-acidente) e teto vigentes na data; competência anterior ao
                  primeiro reajuste vale a rmi
                  data em que só o mínimo ou o teto mudam, num ano com linha de reajuste (ex.: 01/02/2004,
                  01/03/2011, 01/02/2020, 01/05/2023): renda mantida, só o piso passa ao mínimo novo (Lei 8.213,
                  art. 41-A e art. 33); reajustes-rgps.json é a fonte única de QUANDO o benefício acima do mínimo
                  é reajustado (série 2002–2026)
                  ano sem linha de reajuste (1995–2001; 2027 em diante), a lacuna declarada de 01/08/2006
                  (Portaria MPS 342/2006, não é fator sobre a renda vigente), teto ausente (jan.–fev./2011), DIB até 2003,
                  pro rata ausente, DIB no período de incorporação do teto sem media_acima_do_teto (ou com true),
                  rmi acima do teto da DIB -> exit 3 na evolução da renda, sem total, com as contas sem reajuste
                  (renda congelada, só referência) e com reajuste em formula_aberta.leituras
BPC             = cada vencida vale o salário mínimo DA PRÓPRIA COMPETÊNCIA e as 12 vincendas o da propositura
                  (LOAS, art. 20; CPC, art. 292, §§1º e 2º); se o mínimo muda entre elas ou difere da rmi_pretendida,
                  o script não congela um valor: exit 3 com conta_bpc_por_competencia
abono_vincendo  = 1 × renda(propositura)          (padrão M6; nunca no BPC)
valor_da_causa  = vencidas + abono_vencidas + vincendas_12 [+ abono_vincendo]
alcada_jef      = 60 × salário mínimo vigente na data da distribuição (congelada)
competencia     = "JEF" se valor_da_causa ≤ alcada_jef
                  "vara-federal" se maior
                  "JEF-com-renuncia" se maior e houver renúncia expressa: valor_renunciado = valor_da_causa − alcada_jef
```

| Termo | Fonte |
|---|---|
| vencidas + 12 vincendas | `context/lei/cpc-excertos-prev.md`, art. 292, §§1º e 2º; `lei-10259-2001-jef.md`, art. 3º, §2º |
| parcela vencida = competência cujo vencimento devido (data em que deveria ser paga) é anterior ao ajuizamento, paga ou não; vencimento na janela do §2º (acima de 1 mínimo) ou do §3º (até 1 mínimo), dia útil bancário pelo §4º | `lei-8213-1991.md`, art. 41-A, §§2º a 4º (redação da Lei 11.665/2008) |
| janela das competências até 02/2004 (a de 03/2004 é paga em abril, já com 5 dias úteis) | `lei-8213-1991.md`, art. 41, §4º, redação original ("até o 10º dia útil"), da Lei 8.444/1992 ("do primeiro ao décimo dia útil") e da Lei 10.699/2003 ("A partir de abril de 2004 ... do primeiro ao quinto dia útil"): redações riscadas, lidas só para o período delas |
| sem antecipação até a MP 404/2007: de 03/2004 a 12/2006 o pagamento é sempre no mês seguinte; 2007 é a fronteira (a MP só tem o ano capturado) | `lei-8213-1991.md`, art. 41, §4º, redação da Lei 10.699/2003, e art. 41-A, §2º, redação da Lei 11.430/2006 ("do 1o (primeiro) ao 5o (quinto) dia útil do mês seguinte"); art. 41-A, §3º, redação da "MPv nº 404, de 2007", mantida pela Lei 11.665/2008 |
| BPC: mínimo de cada competência nas vencidas, mínimo da propositura nas vincendas | `lei-8742-1993-loas.md`, art. 20, caput; `cpc-excertos-prev.md`, art. 292, §§1º e 2º; mínimos de 2025 e 2026 nos decretos abaixo |
| abono anual proporcional (1/12 por mês) | `lei-8213-1991.md`, art. 40; abono de ano corrente ainda não vencido não entra nas vencidas |
| reajuste anual da renda (vencidas pela renda de cada competência, vincendas pela da propositura) | `lei-8213-1991.md`, art. 41-A, caput; `portaria-interministerial-mps-mf-6-2025.md` e `portaria-interministerial-mps-mf-13-2026.md`, art. 1º, §1º, art. 6º e Anexo I; `cpc-excertos-prev.md`, art. 292, §§1º e 2º |
| BPC sem abono | `lei-8742-1993-loas.md`, art. 20; o art. 40 da Lei 8.213 não abrange o BPC. Só na natureza assistencial: `abono = false` em benefício previdenciário é parâmetro da entrada, cita o art. 40 da Lei 8.213 (conferir a espécie) e sai com alerta `[VERIFICAR]`, nunca a LOAS |
| prescrição quinquenal: prescreve a prestação vencida há mais de cinco anos, contados da data em que deveria ter sido paga, salvo menores, incapazes e ausentes; o valor da causa segue o conteúdo patrimonial | `lei-8213-1991.md`, art. 103, parágrafo único; `cpc-excertos-prev.md`, art. 292, §§1º a 3º |
| contagem do prazo em anos (dia de igual número, ou o imediato; prorrogação do vencimento em feriado) | `cc-excertos-prev.md`, art. 132, caput e §§1º e 3º |
| alçada de 60 salários mínimos | `lei-10259-2001-jef.md`, art. 3º, caput |
| competência fixada na distribuição (o reajuste anual do mínimo não desloca processo já distribuído) | `cpc-excertos-prev.md`, art. 43 |
| salário mínimo | 2025: R$ 1.518,00 (`decreto-12342-2024-salario-minimo.md`, art. 1º); 2026: R$ 1.621,00 (`decreto-12797-2025-salario-minimo.md`, art. 1º) |
| renúncia ao excedente, expressa, inclusive das vincendas | `temas-sumulas-prev.md`, STJ Tema 1.030 |

**Valor nominal × corrigido.** Sem `corrigir_vencidas`, o valor é nominal e sai com o alerta "falta a correção das vencidas". Com ela, cada vencida é corrigida até o ajuizamento pelo regime da seção 3.

---

## 2. Passos para o advogado preencher

| # | Passo | Resultado |
|---|---|---|
| 1 | RMI pretendida, DIB (ou DER), data do ajuizamento | ____ |
| 2 | Natureza: previdenciária (tem abono) ou assistencial/BPC (sem abono) | ____ |
| 3 | Listar as competências desde a DIB e marcar as que venceram antes do ajuizamento: pelo vencimento individual devido, se documentado, ou pela janela do art. 41-A (a de fronteira fica em aberto); nunca pela data de um pagamento feito com atraso | ____ |
| 3a | Regime prescricional: regular (corte = ajuizamento − 5 anos), interrompida (corte = marco − 5 anos) ou não corre (menor, incapaz, ausente); riscar as competências com vencimento devido antes do corte | ____ |
| 4 | Somar as vencidas não prescritas (nominais ou corrigidas pela seção 3) | ____ |
| 5 | Abonos vencidos, proporcionais | ____ |
| 6 | 12 vincendas; abono vincendo pelo padrão M6 (e a conta alternativa sem ele) | ____ / ____ |
| 7 | Alçada pelo salário mínimo da distribuição; competência | ____ |
| 8 | Acima da alçada: vara federal ou renúncia expressa (quanto se renuncia) | ____ |
| 9 | Marcar no texto "conta não conferida por script" | — |

---

## 3. Conta aberta do regime de atualização das vencidas (correção até o ajuizamento)

Antes da citação não há juros de mora ("desde a citação, salvo decisão em contrário": `context/lei/manual-cjf-2026-calculos-prev.md`, item 4.3.2). No valor da causa entra só a **correção monetária** de cada vencida, da competência até o ajuizamento, pelo Manual de Cálculos da Justiça Federal (edição julho/2026, vigente). Os marcos são **competências**, não dias.

| Competências | Previdenciário | Assistencial (BPC) | Fonte |
|---|---|---|---|
| até ago./2006 | indexadores históricos do Manual (IGP-DI de maio/1996 a ago./2006) | indexadores históricos do item 4.2.1.1; IPCA-E (= IPCA-15) desde jan./2001 | Manual 2026, itens 4.3.1.1 e 4.2.1.1 |
| set./2006 a nov./2021 | **INPC** | **IPCA-E** (= IPCA-15 desde jan./2001) | Manual 2026, item 4.3.1.1 (com Nota 3 para o assistencial); `lei-8213-1991.md`, art. 41-A; `lei-11430-2006.md`; `temas-sumulas-prev.md`, STJ Tema 905 e STF Tema 810 |
| dez./2021 a ago./2025 | **Selic** simples (engloba correção e juros; a de ago./2025 é computada em set./2025) | idem | `ec-113-2021.md`, art. 3º (redação original); Manual 2026, item 4.3.1.1, Notas 4 e 5; `temas-sumulas-prev.md`, STF Tema 1.419 |
| a partir de set./2025 | **INPC** | **IPCA-15** | Manual 2026, itens 4.3.1.1 e 4.2.1.1; STF Tema 1.419 |

**Ponto aberto — a faixa dez./2021 a ago./2025 antes da citação.** A Selic dessa faixa "engloba" correção e juros, e o Manual capturado não diz se, no período anterior à citação (que é todo o período do valor da causa), ela entra inteira ou se só a parte de correção. O script usa o resultado do motor de atualização e marca a fatia com `[VERIFICAR]`; à mão, faça as duas contas (Selic inteira × fatia sem juros) e leve as duas ao advogado se a diferença mudar a competência.

Índice de correção: produto dos índices mensais do mês da competência ao mês anterior ao do marco final. Mês fora do cache de índices → a fatia sai em fórmula (exit 3), nunca com índice de memória. O detalhe dos juros (que só correm depois da citação) está em `context/calculo-rpv.md`, seção 3.

No script, a correção é pedida ao motor de atualização com o regime `fazenda-ec113` e a `natureza` (`previdenciaria` ou `assistencial`), parcela a parcela, de `data_inicial` = dia 1º do mês da competência (a correção começa na competência: `manual-cjf-2026-calculos-prev.md`, item 4.3.1.1, Nota 2) até `data_final` = ajuizamento, com `data_citacao` = ajuizamento: os juros só correm desde a citação (item 4.3.2), e a citação fictícia no próprio ajuizamento zera os juros do valor da causa (`scripts/calc/calc_previdenciario_valor_causa.py`, função `corrigir`).

---

## 4. Leituras e pontos que mudam o resultado

- **M6 — abono nas vincendas.** Duas contas sempre; **padrão: incluir** o abono anual nas 12 vincendas, como interpretação declarada do CPC, art. 292, §2º ("prestação anual"), **sem afirmar que é pacífico**; nunca no BPC. Como a leitura não é pacífica, **todo caso com abono sai em exit 3**, com as duas contas completas: `valor_da_causa` traz o critério padrão (ou o escolhido em `incluir_abono_nas_vincendas`), `alternativa_m6` traz a outra (com `competencia`, `valor_da_causa` e `valor_renunciado` próprios) e `formula_aberta.leituras` repete as duas. A escolha é do advogado, declarada na petição. Se a escolha muda a competência (uma conta cabe no JEF e a outra não), sai também o alerta `[VERIFICAR] M6 muda a competência`. Sem abono (BPC, ou `abono = false`) não há alternativa e o caso fecha em exit 0.
- **Janela de fronteira (art. 41-A, ou art. 41, §4º, até a competência 02/2004):** a competência cuja janela de pagamento cruza o ajuizamento não é contada nem descartada: fica em aberto, e o valor da causa sai sem número (exit 3), com `formula_aberta.leituras` trazendo a conta sem e com a competência, até o advogado informar o vencimento devido em `datas_vencimento` (ver a seção 6). Exemplo: DIB 01/01/2003, ajuizamento 10/02/2003, RMI 500,00: a janela de 01/2003 vai de 03 a 14/02/2003 (dez dias úteis), e as leituras são 6.000,00 e 6.500,00. Já a competência 03/2004, paga em abril, tem a janela de 01 a 07/04/2004: com ajuizamento em 12/04/2004, vencida (6.500,00).
- **Sem antecipação antes da MP 404/2007:** a janela do §3º (até um mínimo, a partir do fim do próprio mês) não vale para trás. Exemplo: DIB 01/03/2004, ajuizamento 29/03/2004, RMI 240,00 (o mínimo): a janela de 03/2004 é de 01 a 07/04/2004; março não venceu e o valor é 12 × 240,00 = **2.880,00**; vencimento informado em 25/03/2004 é incompatível com a lei do período (exit 2). Aplicar o §3º retroativamente dava 3.120,00 (R$ 240,00 a mais). Nas competências de 2007, sem a data da MP capturada, o vencimento antecipado informado deixa a competência em aberto (exit 3, leituras com e sem ela).
- **BPC com o mínimo mudando:** o BPC é um salário mínimo mensal (LOAS, art. 20). As vencidas se somam competência a competência, cada uma com o mínimo do seu mês, e as 12 vincendas pelo mínimo da propositura (CPC, art. 292, §§1º e 2º). Exemplo: DIB 01/12/2025, ajuizamento 15/02/2026, dezembro e janeiro vencidos: 1.518,00 + 1.621,00 + 12 × 1.621,00 = **22.591,00**. Congelar o mínimo da DIB dá 21.252,00 (R$ 1.339,00 a menos); trocar tudo pelo mínimo novo erra dezembro. O script devolve exit 3 com `conta_bpc_por_competencia`; com a conta conferida e `total_unico = true`, rode de novo com `valor_da_causa_informado` para a alçada. **A reentrada só vale sem nenhuma outra pendência que mude o valor** (competência da DIB no meio do mês, abono, correção, mínimo): o total informado apagaria a pendência (exemplo: DIB 15/12/2025, ajuizamento 15/02/2026: dezembro integral 1.518,00 ou proporcional 832,45, exit 3 sem total único). **Com competência de fronteira em aberto não há total único**: `valor_da_causa_nominal` sai nulo, a conta sem a competência vai em `valor_sem_competencias_pendentes`, e o total só se fecha depois de informar `datas_vencimento` (exemplo: DIB 01/12/2025, ajuizamento 05/01/2026: leituras 19.452,00 e 20.970,00; com o vencimento de dezembro em 02/01/2026, 20.970,00).
- **Honorários (para quem usa esta conta adiante):** o pagamento administrativo, total ou parcial, feito depois da citação válida **não reduz** a base dos honorários da ação de conhecimento, que é a totalidade dos valores devidos (`temas-sumulas-prev.md`, STJ Tema 1.050; `manual-cjf-2026-calculos-prev.md`, item 4.3.3, Nota 4). Abater o que o INSS pagou no curso da ação vale para o crédito da parte, não para a base dos honorários; a conta é de `context/calculo-rpv.md`.
- **Prescrição quinquenal (QA final r5 A01; exemplo refeito no QA final r9 A01).** Só entram as competências com vencimento devido a partir do corte (Lei 8.213, art. 103, parágrafo único). Exemplo VC-PRESC-SEM-ABONO: DIB 01/01/2020, ajuizamento 10/03/2026, RMI 2.000,00, sem abono, média **não** acima do teto. Entrada: `{"data_ajuizamento": "2026-03-10", "rmi_pretendida": "2000.00", "dib": "2020-01-01", "natureza": "previdenciaria", "abono": false, "prescricao": "regular", "media_acima_do_teto": false}` (exit 0). Corte 10/03/2021: as 14 competências de 01/2020 a 02/2021 (a janela de 02/2021 vai de 01 a 05/03/2021) prescreveram (12 × 2.000,00 + 2 × 2.109,00 = 28.218,00). A renda das vencidas é a de cada competência, reajustada em cada janeiro (Lei 8.213, art. 41-A; Portarias anuais, art. 1º e Anexo I: 2021 pro rata 1,0545; 2022 1,1016; 2023 1,0593; 2024 1,0371; 2025 1,0477; 2026 1,0390): 2.109,00 · 2.323,27 · 2.461,04 · 2.552,34 · 2.674,09 · 2.778,38. Vencidas 03/2021 a 02/2026 = 10 × 2.109,00 + 12 × 2.323,27 + 12 × 2.461,04 + 12 × 2.552,34 + 12 × 2.674,09 + 2 × 2.778,38 = 146.775,64; vincendas pela renda da propositura (CPC, art. 292, §§1º e 2º) = 12 × 2.778,38 = 33.340,56; total **180.116,20**, vara federal. Somar desde a DIB dá 208.334,20 (R$ 28.218,00 a mais). Com abono, o corte vale nas duas contas M6: abonos de 2021 a 2025 = 12.119,74 (o de 2020, 2.000,00, prescreveu); **195.014,32** com o abono vincendo de 2.778,38 e 192.235,94 sem ele (exit 3, M6). Congelar a renda da DIB dava 144.000,00 (R$ 36.116,20 a menos): o script só mostra essa conta como referência, em `formula_aberta.leituras.sem_reajuste_renda_congelada`, quando falta `media_acima_do_teto` (exit 3, nunca o total). Sem `prescricao`, o script devolve exit 3 com as contas sem corte (208.334,20) e com o corte regular (180.116,20), nunca o total fechado; `nao_corre` (menor, incapaz, ausente) e `interrompida` com `marco_prescricional` são decisão do advogado, que o script não presume. A causa e o efeito da interrupção não são apurados: o script só recebe o marco.
- **Reajuste anual da renda (QA final r7 C1).** A renda não fica congelada na RMI: em cada data de reajuste (1º de janeiro em 2025 e 2026) recebe o reajuste da Portaria do ano (Lei 8.213, art. 41-A), distinto da correção monetária das vencidas. Exemplo VC-3: DIB 01/01/2025, RMI 3.600,00, ajuizamento 10/02/2026, abono, `prescricao = regular`, `media_acima_do_teto = false`. Renda 3.600,00 em 2025 e 3.600,00 × 1,039 = 3.740,40 desde 01/2026 (Portaria 13/2026, Anexo I, DIB em janeiro de 2025: 3,90%). Vencidas 12 × 3.600,00 + 3.740,40 = 46.940,40; abono de 2025 3.600,00; 12 vincendas × 3.740,40 = 44.884,80 (sem antecipar 2027); abono vincendo 3.740,40; total **99.165,60**, acima da alçada de 97.260,00: vara federal. Sem abono vincendo (M6), 95.425,20, JEF. A renda congelada dava 97.200,00 (R$ 1.965,60 a menos) e JEF. Ano sem linha de reajuste (1995–2001, 2027 em diante), a lacuna declarada de 01/08/2006, o teto ausente de jan.–fev./2011, pro rata ausente ou incorporação do teto sem a média: exit 3 na evolução da renda, nunca o total com a renda congelada. Os exemplos de janela histórica acima mostram só a regra de cada um, com renda constante: com essas DIBs o script abre também a evolução da renda.
- **P9 — alçada congelada na distribuição** (CPC, art. 43).
- **Renúncia:** só expressa, e alcança as vincendas (STJ Tema 1.030). O script calcula quanto se renuncia; quem decide renunciar é o advogado com o cliente.
- **No JEF não há prazo diferenciado para o INSS** (`lei-10259-2001-jef.md`, art. 9º).

---

## 5. Caso resolvido à mão — VC-03 (dados inventados)

Caso de referência VC-03, "confere" na re-revisão especialista de 14/10/2026; **pendente de conferência pelo advogado**. É o caso em que a data da distribuição muda a competência.

**Entrada:** valor da causa já formado de R$ 95.000,00. (a) ajuizamento em 15/12/2025; (b) ajuizamento em 05/01/2026.

| Passo | (a) 15/12/2025 | (b) 05/01/2026 | Fonte |
|---|---|---|---|
| salário mínimo da distribuição | R$ 1.518,00 | R$ 1.621,00 | decretos de 2025 e 2026, art. 1º |
| alçada | 60 × 1.518,00 = **91.080,00** | 60 × 1.621,00 = **97.260,00** | Lei 10.259, art. 3º |
| comparação | 95.000,00 > 91.080,00 | 95.000,00 ≤ 97.260,00 | — |
| competência | **vara federal** (ou JEF com renúncia de 3.920,00) | **JEF** | CPC, art. 43 |

Saída esperada: (a) `competencia = "vara-federal"`; (b) `competencia = "JEF"`. Em (b), o reajuste do mínimo em anos seguintes não tira o processo do JEF.

Armadilhas da mesma conta ("confere"): **V-A** — BPC de R$ 1.621,00, 2 vencidas e 12 vincendas: 14 × 1.621,00 = **R$ 22.694,00**, abono zero. **V-B** — total já formado de R$ 97.260,01 em 2026: alçada 97.260,00; excede em **R$ 0,01**; com renúncia expressa, renuncia-se R$ 0,01.

---

## 6. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags: `--entrada`, `--versao`. Convenções: `data` = `AAAA-MM-DD`; `decimal` = texto com ponto; campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → exit 2; chave iniciada por `_` é comentário.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `data_ajuizamento` | data | sim | data da distribuição |
| `valor_da_causa_informado` | decimal | não | total já formado; quando presente, o script só faz a alçada e a renúncia, e os campos de RMI são dispensados |
| `rmi_pretendida` | decimal | sim, salvo com `valor_da_causa_informado` | — |
| `dib` | data | sim, salvo com `valor_da_causa_informado` | DIB pretendida (ou a DER) |
| `natureza` | enum | sim, salvo com `valor_da_causa_informado` | `previdenciaria` · `assistencial` |
| `abono` | bool | sim, salvo com `valor_da_causa_informado` | `false` obrigatório quando `natureza = assistencial` (`true` com BPC → exit 2) |
| `incluir_abono_nas_vincendas` | bool | não | padrão `true` (M6); ignorado quando `abono = false` |
| `corrigir_vencidas` | bool | não | padrão `false`; `true` chama o motor de atualização (seção 3) |
| `renunciar_excedente` | bool | não | padrão `false` |
| `salario_minimo` | decimal | não | ausente = tabela pela data do ajuizamento; ano fora da tabela → exit 3 |
| `datas_vencimento` | objeto | não | `{"AAAA-MM": "AAAA-MM-DD"}`: **vencimento individual devido** da competência, isto é, o dia em que ela deveria ter sido paga (dentro da janela do art. 41-A, ou do art. 41, §4º, até a competência 02/2004), tirado de documento do INSS que o fixe; fecha a competência cuja janela cruza o ajuizamento. Competência fora do período da DIB ao ajuizamento, data anterior ao próprio mês, **data fora da janela legal da competência** (antes da MP 404/2007, sempre no mês seguinte) ou **dia sem expediente bancário normal** no calendário bancário, separado do forense (sábado, domingo, feriado nacional ou data móvel da tabela do motor: segunda e terça de Carnaval, Sexta-feira da Paixão, Corpus Christi; art. 41-A, §4º) → exit 2; dia de semana sem o motor de prazos ou com a tabela de feriados ausente, ilegível ou sem o ano (o calendário não decide o dia) → exit 3, nunca fechado; data antecipada (antes do mês seguinte) em competência de 2007, sem a data da MP 404 capturada → exit 3. O nome antigo, `datas_pagamento`, não é mais lido: o script 2.0.0 o recusa como campo desconhecido (exit 2) |
| `prescricao` | enum | não | `regular` · `nao_corre` · `interrompida`: regime prescricional do caso (seção 4). Ausente e capaz de mudar o total → exit 3 com as contas sem e com o corte regular; ausente e sem alcance → conta normal |
| `marco_prescricional` | data | sim quando `prescricao = interrompida` | data em que a prescrição deixou de correr (ato interruptivo ou suspensivo informado pelo advogado); o corte conta 5 anos para trás dela. Sem `interrompida`, ou depois do ajuizamento → exit 2 |
| `media_acima_do_teto` | bool | condicional: DIB no período de incorporação do teto de um reajuste da conta | a média dos salários de contribuição superou o teto da DIB? No reajuste seguinte à DIB incorpora-se à renda a diferença percentual entre a média e o teto (Portarias 6/2025 e 13/2026, art. 6º). Ausente nesse caso, ou `true` (o percentual depende da média, que o script não recebe) → exit 3 na evolução da renda (seção 4) |

**Vencimento devido × pagamento realizado.** O CPC, art. 292, §1º, manda considerar as prestações **vencidas**, pagas ou não; o marco é a data em que a prestação deveria ter sido paga, como no art. 103, parágrafo único, da Lei 8.213. Um pagamento feito depois (crédito atrasado) não entra no campo nem muda a classificação da competência; na concessão, em regra, nem existe pagamento.

---

## 7. Saída e códigos

JSON com `vencidas` (competências, janela ou data informada de cada uma, valor), `abono_vencidas`, `vincendas_12`, `abono_vincendo`, `valor_da_causa_apurado`, `valor_da_causa`, `criterio_abono_vincendas`, `alternativa_m6` (e `alternativa_com_abono_vincendas` ou `alternativa_sem_abono_vincendas`), `alcada_jef`, `competencia` (`JEF` · `vara-federal` · `JEF-com-renuncia`), `valor_renunciado`, `conta_bpc_por_competencia` (só no BPC com o mínimo mudando), `evolucao_renda` (segmentos de renda, passos de cada reajuste, renda na propositura; nulo no BPC), `prescricao` (regime, corte, competências e abonos prescritos ou em aberto), `fundamento`, `alertas` (valor nominal sem correção; STJ Tema 1.030), `parametros_usados`, `regra`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado, sem abono (BPC ou `abono = false`) e sem competência em aberto; ou só alçada e renúncia sobre `valor_da_causa_informado` |
| 2 | entrada inválida |
| 3 | renda reajustada desconhecida em competência da conta ou na propositura (ano sem linha de reajuste, lacuna declarada de 01/08/2006 ou teto ausente de jan.–fev./2011, DIB até 2003, pro rata ausente, `media_acima_do_teto` ausente ou `true` no período de incorporação do teto, rmi acima do teto da DIB; contas sem e com reajuste em `formula_aberta.leituras`); regime prescricional não informado e capaz de mudar o total (contas sem e com o corte em `formula_aberta.leituras`); competência cujo vencimento cruza o corte quinquenal; **leitura M6 em aberto: todo caso com abono** (as duas contas saem completas; a escolha é do advogado); competência cuja janela de pagamento cruza o ajuizamento sem `datas_vencimento` (valor sem número; leituras com e sem ela); competência de 2007 com vencimento antecipado informado (MP 404/2007 sem data capturada); `datas_vencimento` em dia de semana sem o motor de prazos ou sem a tabela de feriados legível (calendário bancário não decide o dia); BPC com o salário mínimo mudando entre as competências ou diferente da `rmi_pretendida` (conta por competência em `conta_bpc_por_competencia`); salário mínimo do ano fora da tabela; correção pedida com mês fora do cache de índices (a parte corrigível sai calculada e o resto em fórmula) |
