# Conta aberta — benefícios por incapacidade e auxílio-acidente

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_incapacidade.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_incapacidade.py` · **Tabelas:** `scripts/data/salario-minimo.json`, `scripts/data/teto-rgps.json` · **Skills que leem:** `pericia-medica-previdenciaria`, `acidentario-do-trabalho`. Carência e qualidade de segurado vêm de `context/calculo-cnis.md`; este arquivo não decide se o segurado tem direito, só quanto e desde quando.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 4).

---

## 1. Fórmulas, com a fonte de cada termo

`SB` = salário de benefício. A base depende do **fato gerador, que é a DII** (não a DAT nem a DER):

- **DII a partir de 14/11/2019:** média de 100% dos salários de contribuição desde 07/1994, já corrigidos (`context/lei/ec-103-2019.md`, art. 26, caput), limitada ao teto (§1º). É o campo `media_100`.
- **Em qualquer espécie, inclusive no auxílio-acidente:** `SB = min(max(média, salário mínimo da DIB), teto da DIB)` (`lei-8213-1991.md`, art. 29, §2º; valores de 2026 em `portaria-interministerial-mps-mf-13-2026.md`, art. 2º). O piso do SB vem **antes** do percentual da espécie.
- **DII até 13/11/2019:** média aritmética simples dos **maiores salários de contribuição correspondentes a 80%** do período contributivo (`lei-8213-1991.md`, arts. 29, II, e 44; `in-128-2022-inss.md`, arts. 229 e 233, II, "a"). A `media_100` **não** é essa média: o script devolve exit 3 e pede a média dos 80% maiores, que se apura pela lista de salários (`calc_previdenciario_rmi.py`, campo `salarios_contribuicao`).
- **Sem DII:** o fato gerador não se presume (nem pela DAT): exit 3, com as duas contas abertas (DII depois de 14/11/2019 sobre a `media_100`; DII até 13/11/2019 sobre a média dos 80% maiores).

| Espécie | Conta | Limitadores | Fonte |
|---|---|---|---|
| **Auxílio por incapacidade temporária** (inclusive acidentário) | RMI = 91% × SB | fato gerador (DII) desde 01/03/2015: não pode passar da **média dos últimos 12 salários de contribuição** (ou dos existentes, se menos de 12; `in-128-2022-inss.md`, art. 233, I, "b"); piso de 1 salário mínimo | `lei-8213-1991.md`, arts. 61 e 29, §10; `cf88-seguridade.md`, art. 201, §2º |
| **Aposentadoria por incapacidade permanente previdenciária**, fato gerador desde 14/11/2019 | coeficiente = 60% + 2% × anos de contribuição acima de 20 (H) / 15 (M); RMI = coeficiente × SB | piso; teto | `ec-103-2019.md`, art. 26, §§2º, III, e 5º; `in-128-2022-inss.md`, art. 233, II, "b"; `temas-sumulas-prev.md`, STF Tema 1.300 |
| **Aposentadoria por incapacidade permanente acidentária** (acidente de trabalho, doença profissional ou do trabalho) | RMI = 100% × SB | piso; teto | `ec-103-2019.md`, art. 26, §3º, II; IN 128, art. 233, II, "c" |
| Incapacidade permanente com fato gerador **até 13/11/2019** | regra anterior: 100% × SB, com SB = média dos 80% maiores | piso; teto | IN 128, arts. 229 e 233, II, "a"; `lei-8213-1991.md`, arts. 29, II, e 44 |
| **Acréscimo de 25%** | + 25% da RMI, só na aposentadoria por incapacidade permanente do segurado que precisa de assistência permanente de outra pessoa; devido **mesmo acima do teto**; desde a DIB (se a necessidade foi constatada na perícia da concessão) ou desde o pedido | — | `lei-8213-1991.md`, art. 45; IN 128, art. 328 |
| **Auxílio-acidente** | RMI = 50% × SB, com o SB já no piso do art. 29, §2º | **sem piso da renda** (a RMI pode ficar abaixo do mínimo, mas o SB não); sem carência; vedada a acumulação com aposentadoria | `lei-8213-1991.md`, arts. 86, §§1º e 2º, e 26, I; `decreto-3048-1999.md`, art. 42, parágrafo único |

"Acidente sem nexo com o trabalho" não é acidentário: entra na regra de 60% + 2% (armadilha I-A).

**DIB do auxílio temporário** (`lei-8213-1991.md`, art. 60, caput e §1º; IN 128, art. 336, I):

```
empregado (exceto doméstico), IN 128, art. 336, I:
   requerido até o 30º dia da DAT -> DIB = 16º dia do afastamento (contado da DAT, inclusivo);
                                     se a DII é posterior ao 16º dia -> DIB = DII
   requerido depois do 30º dia    -> DIB = DER; se a DII é posterior à DER -> DIB = DII
demais segurados, IN 128, art. 336, II:
   requerido até 30 dias da DAT (ou da cessação das contribuições) -> DIB = DII
   requerido depois               -> DIB = DER; se a DII é posterior à DER -> DIB = DII
```

DAT, DII e DER entram separadas; uma nunca substitui a outra. **A DIB depende da DII também no empregado** (IN 128, art. 336, I, "a" e "b": DII posterior ao 16º dia ou à DER desloca a DIB). Por isso, sem a DII, o script não fecha a DIB nem a RMI do empregado: devolve exit 3 com a DIB mínima (16º dia ou DER) "ou a DII, se posterior" e as contas abertas. Para quem não é empregado a DIB **é** a DII (IN 128, art. 336, II, "a"): sem ela, exit 2.

**Ordem dos limitadores:** (1) SB = min(max(média, salário mínimo da DIB), teto da DIB), em toda espécie, inclusive no auxílio-acidente (art. 29, §2º); (2) percentual da espécie; (3) na temporária, limite da média dos 12 últimos; (4) piso da renda de 1 salário mínimo (exceto auxílio-acidente); (5) acréscimo de 25%, quando devido, por último e sem teto.

Exemplos (DIB em 01/01/2026, mínimo R$ 1.621,00): auxílio-acidente com média 1.000,00 → SB 1.621,00 → RMI = 50% × 1.621,00 = **810,50** (não 500,00: o auxílio-acidente não tem piso da renda, mas tem o do SB; `lei-8213-1991.md`, arts. 29, §2º, e 86, §1º; `decreto-3048-1999.md`, art. 42, parágrafo único). Aposentadoria por incapacidade permanente acidentária com a mesma média → 100% × 1.621,00 = 1.621,00.

---

## 2. Passos para o advogado preencher

| # | Passo | Onde achar o dado | Resultado |
|---|---|---|---|
| 1 | Espécie: temporária, permanente ou auxílio-acidente | laudo, decisão | ____ |
| 2 | Acidentária (nexo com o trabalho)? | CAT, laudo | sim / não |
| 3 | SB (média de 100% desde 07/1994, corrigida, ou, com DII até 13/11/2019, média dos 80% maiores) e, na temporária, média dos 12 últimos | CNIS, carta de concessão | ____ / ____ |
| 4 | DII (fato gerador) em qualquer espécie: antes ou depois de 13/11/2019? Antes: SB = média dos 80% maiores. Permanente: sexo e anos de contribuição | laudo, CNIS | ____ |
| 5 | Percentual da espécie e RMI antes dos limitadores | seção 1 | ____ |
| 6 | Limitadores na ordem da seção 1 | tabelas de piso e teto do ano | ____ |
| 7 | Acréscimo de 25%? (só permanente com assistência permanente) | laudo | ____ |
| 8 | Temporária: DAT, DII, DER → DIB | requerimento, atestado | ____ |
| 9 | Carência e qualidade de segurado conferidas em `context/calculo-cnis.md` | — | ____ |
| 10 | Marcar no texto "conta não conferida por script" | — | — |

---

## 3. Leituras e pontos que mudam o resultado

- **P3 (DIB):** os 30 dias contam da DAT; DII posterior prevalece. Sem a DAT, o script não troca pela DII: exit 2. Sem a DII, o script não a presume: exit 2 para quem não é empregado; exit 3 para o empregado (DIB mínima + "ou a DII, se posterior").
- **STF Tema 1.300:** constitucional o cálculo do art. 26, §2º, III, para incapacidade constatada depois da reforma (trânsito em 18/04/2026). A data que decide é a do **fato gerador (DII)**, não a da DER.
- **Acumulação do auxílio-acidente com auxílio temporário** — ponto aberto: a lei só fecha a vedação com aposentadoria (art. 86, §§1º a 3º); origem da incapacidade e reabertura não foram fechadas. O script aceita a acumulação fora da aposentadoria e alerta com `[VERIFICAR]`.
- **Dispensa de carência por doença da lista:** só quando o advogado marca (`context/calculo-cnis.md`).

---

## 4. Caso resolvido à mão — INCAP-03 (dados inventados)

Caso de referência INCAP-03, "confere" na re-revisão especialista de 14/10/2026 (inclusive contra um oráculo aritmético independente); **pendente de conferência pelo advogado**.

**Entrada:** mulher, 16 anos de contribuição, SB R$ 1.900,00, previdenciária (sem nexo com o trabalho), DII e DIB em 2026. (a) aposentadoria por incapacidade permanente; (b) controle: auxílio por incapacidade temporária, com média dos 12 últimos de R$ 1.850,00. Salário mínimo de 2026: R$ 1.621,00 (`decreto-12797-2025-salario-minimo.md`, art. 1º).

| Passo | (a) permanente | (b) temporária | Fonte |
|---|---|---|---|
| percentual | fato gerador depois de 13/11/2019; mulher: 60% + 2% × (16 − 15) = **62%** | **91%** | EC 103, art. 26, §§2º, III, e 5º; Lei 8.213, art. 61 |
| RMI bruta | 1.900,00 × 0,62 = 1.178,00 | 1.900,00 × 0,91 = 1.729,00 | — |
| média dos 12 últimos | não se aplica | 1.729,00 ≤ 1.850,00 → não limita | Lei 8.213, art. 29, §10 |
| piso | 1.178,00 < 1.621,00 → **R$ 1.621,00** | 1.729,00 > 1.621,00 → não atua | CF, art. 201, §2º |
| saída | `rmi = 1621.00`, `limitador_aplicado = "piso, CF art. 201 §2º"` | `rmi = 1729.00`, `limitador_aplicado = "nenhum"` | — |

Armadilha da mesma conta ("confere"): **I-B** — auxílio-acidente, SB R$ 2.400,00: 50% = **R$ 1.200,00**, abaixo do mínimo, e **não** sobe ao piso (Decreto 3.048, art. 42, parágrafo único).

---

## 5. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags: `--entrada`, `--versao`. Convenções: `data` = `AAAA-MM-DD`; `decimal` = texto com ponto; campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → exit 2; chave iniciada por `_` é comentário.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `especie` | enum | sim | `temporaria` · `permanente` · `auxilio-acidente` |
| `acidentaria` | bool | sim | `true` só com nexo laboral (acidente de trabalho, doença profissional ou do trabalho) |
| `sexo` | enum | sim | `M` · `F` |
| `media_100` | decimal | sim | SB: média de 100% desde 07/1994, já corrigida |
| `media_12_ultimos` | decimal | sim quando `especie = temporaria` | média dos últimos 12 salários de contribuição (ou dos existentes) |
| `tempo_contribuicao_anos` | inteiro | sim quando `especie = permanente` e `acidentaria = false` | anos completos de contribuição |
| `dii` | data | sim quando `especie = permanente`, ou `especie = temporaria` e `empregado = false`; ausente → exit 2; na temporária do empregado e no auxílio-acidente o campo é aceito e, sem ele, a saída é exit 3 (fato gerador e DIB em aberto) | data do início da incapacidade (fato gerador) |
| `dib` | data | sim quando `especie = permanente` ou `auxilio-acidente`, salvo `teto` e `salario_minimo` informados; ausente → exit 3 (os limites do salário de benefício são os da DIB, Lei 8.213, art. 29, §2º, e a DII não a substitui) | data de início do benefício; na permanente e no auxílio-acidente é posterior à DII (arts. 43 e 86, §2º) |
| `dat` | data | sim quando `especie = temporaria` | data do afastamento da atividade (para quem não é empregado, a da cessação das contribuições, se for o marco) |
| `der` | data | sim quando `especie = temporaria` | data de entrada do requerimento |
| `empregado` | bool | sim quando `especie = temporaria` | `true` para o segurado empregado, exceto o doméstico (IN 128, art. 336, I) |
| `assistencia_permanente` | bool | não | padrão `false`; só vale com `especie = permanente` |
| `salario_minimo` | decimal | não | ausente = tabela pela data da DIB (Lei 8.213, art. 29, §2º; na temporária, a DIB calculada); a DII decide o regime, mas não substitui a DIB: na permanente e no auxílio-acidente sem `dib`, exit 3; ano fora da tabela → exit 3 |
| `teto` | decimal | não | ausente = tabela pela mesma data da DIB, com as mesmas regras do `salario_minimo`; ano fora da tabela → exit 3 |
| `carencia` | enum | não | `sim` · `nao` · `indeterminada` · `dispensada` (saída de `calc_previdenciario_cnis.py`); só ecoada em alerta |
| `qualidade_segurado` | enum | não | `mantida` · `perdida` · `indeterminada`; só ecoada em alerta |

---

## 6. Saída e códigos

JSON com `rmi`, `percentual`, `limitador_aplicado` (`"art. 29 §10"`, `"piso, CF art. 201 §2º"` — piso da renda —, `"piso do SB, Lei 8.213 art. 29 §2º"` — o salário de benefício subiu ao salário mínimo e nenhum limitador posterior atuou (ex.: auxílio-acidente, sem piso da renda; percentual de 100%) —, `"teto"` ou `"nenhum"`), `acrescimo_25` (quando devido), `dib` (temporária), `carencia_exigida`, `fundamento`, `alertas` (Tema 1.300; regra anterior para DII até 13/11/2019; acumulação do auxílio-acidente), `parametros_usados`, `regra`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado |
| 2 | entrada inválida (inclusive falta de `especie`; de DAT, DER, `empregado` ou `media_12_ultimos` na temporária; de DII na permanente ou na temporária de quem não é empregado) |
| 3 | salário mínimo ou teto do ano fora da tabela; DII ausente na temporária do empregado ou no auxílio-acidente; DII até 13/11/2019 (falta a média dos 80% maiores): devolve `dados_faltantes` e a fórmula desta seção com o termo faltante |

---

---

## Cobertura temporal do script (COBERTURA)

Fonte: `scripts/calc/calc_previdenciario_incapacidade.py`, constante `COBERTURA`.

**Regra:** fato (data indicada na coluna *chave*) fora do intervalo em que a linha é a regra vigente → o script **não fecha veredito pela regra posterior**: sai em **exit 3** com `formula_aberta`, a regra histórica e a fonte de cada borda, para o advogado refazer a conta. Borda sem fonte capturada em `context/lei/` fica no lado conservador (o primeiro dia certo). A tabela abaixo é a constante `COBERTURA` do script, transcrita na W3-integ-2 (18/10/2026); mudou o script, muda esta tabela.

| Regra (chave) | De | Até | Coberto | Regra aplicada no intervalo | Fonte das bordas |
|---|---|---|---|---|---|
| `temporaria` | — | 28/04/1995 | **não** → exit 3 | art. 61, redação original: 80% do SB + 1% por grupo de 12 contribuições, até 92% (92% no acidente do trabalho); SB pelos últimos 36 salários em até 48 meses | até: Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171) |
| `temporaria` | 29/04/1995 | 28/11/1999 | **não** → exit 3 | 91% (art. 61, Lei 9.032/1995); SB pelos últimos 36 salários em até 48 meses (IN 128, art. 221, II, "b") | de: Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171); até: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md) |
| `temporaria` | 29/11/1999 | 28/02/2015 | **não** → exit 3 | 91% da média dos 80% maiores (art. 29, II), sem o limite do art. 29, §10 | de: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md); até: MP 664/2014, vigente desde 01/03/2015 (IN 128, art. 233, I, "b") |
| `temporaria` | 01/03/2015 | 13/11/2019 | **não** → exit 3 | 91% da média dos 80% maiores, limitado pelo art. 29, §10 (redações da MP 664/2014 e da Lei 13.135/2015, de mesmo teor — lei-8213-1991.md:841-843) | de: IN 128, art. 233, I, "b"; até: EC 103/2019, publicada em 13/11/2019 (IN 128, art. 233, II, "a" e "b") |
| `temporaria` | 14/11/2019 | — | sim | 91% (art. 61) da média de 100% desde 07/1994 (EC 103, art. 26; Decreto 3.048, art. 32, redação do Decreto 10.410/2020), limitado pelo art. 29, §10 | de: EC 103/2019, publicada em 13/11/2019 (IN 128, art. 233, II, "a" e "b") |
| `temporaria-dib` | — | 28/11/1999 | **não** → exit 3 | art. 60, redação original: empregado e empresário do 16º dia, demais da DII | até: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md) |
| `temporaria-dib` | 29/11/1999 | 28/02/2015 | sim | art. 60, redação da Lei 9.876/1999 (lei-8213-1991.md:1411-1413) | de: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md); até: MP 664/2014, vigente desde 01/03/2015 (IN 128, art. 375 — in-128-2022-inss.md:3383) |
| `temporaria-dib` | 01/03/2015 | 18/06/2015 | **não** → exit 3 | art. 60 na redação da MP 664/2014 | de: MP 664/2014, vigente desde 01/03/2015 (IN 128, art. 375 — in-128-2022-inss.md:3383); até: Lei 13.135, de 18/06/2015 (IN 128, art. 375): o dia 18 entra na janela, as duas leituras valem |
| `temporaria-dib` | 19/06/2015 | — | sim | art. 60, caput e §1º, redação da Lei 9.876/1999; IN 128, art. 336 | de: Lei 13.135/2015 (IN 128, art. 375): volta a redação da Lei 9.876/1999 |
| `permanente` | — | 28/04/1995 | **não** → exit 3 | art. 44, redação original: 80% do SB + 1% por grupo de 12 contribuições, até 100% | até: Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171) |
| `permanente` | 29/04/1995 | 28/11/1999 | **não** → exit 3 | 100% (art. 44, Lei 9.032/1995) dos últimos 36 salários em até 48 meses | de: Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171); até: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md) |
| `permanente` | 29/11/1999 | 13/11/2019 | **não** → exit 3 | 100% da média dos 80% maiores (arts. 29, II, e 44) | de: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md); até: EC 103/2019, publicada em 13/11/2019 (IN 128, art. 233, II, "a" e "b") |
| `permanente` | 14/11/2019 | — | sim | EC 103, art. 26, §§2º, III, 3º, II, e 5º, sobre a média de 100% desde 07/1994 | de: EC 103/2019, publicada em 13/11/2019 (IN 128, art. 233, II, "a" e "b") |
| `auxilio-acidente` | — | 28/04/1995 | **não** → exit 3 | art. 86, §1º, redação original: 30%, 40% ou 60% do salário de contribuição do dia do acidente | até: Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171) |
| `auxilio-acidente` | 29/04/1995 | 28/11/1999 | **não** → exit 3 | 50% do SB (art. 86, §1º, Leis 9.032/1995 e 9.528/1997) dos últimos 36 salários | de: Lei 9.032/1995, publicada em 29/04/1995 (IN 128, art. 352, §1º — context/lei/in-128-2022-inss.md:3171); até: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md) |
| `auxilio-acidente` | 29/11/1999 | 10/11/2019 | **não** → exit 3 | 50% do SB pela média dos 80% maiores (art. 86, §1º, Lei 9.528/1997) | de: Lei 9.876/1999, publicada em 29/11/1999 (IN 128, art. 221 — context/lei/in-128-2022-inss.md); até: MP 905/2019, de 11/11/2019, revogada pela MP 955/2020, de 20/04/2020 (redação riscada com "Vigência encerrada" em context/lei/lei-8213-1991.md:1942; as datas de publicação não estão capturadas em context/lei/ — [VERIFICAR]: a janela vai do dia da MP 905 ao da MP 955, inclusive, a maior possível) |
| `auxilio-acidente` | 11/11/2019 | 20/04/2020 | **não** → exit 3 | art. 86, §1º, redação da MP 905/2019: 50% da aposentadoria por invalidez a que o segurado teria direito | de: MP 905/2019, de 11/11/2019, revogada pela MP 955/2020, de 20/04/2020 (redação riscada com "Vigência encerrada" em context/lei/lei-8213-1991.md:1942; as datas de publicação não estão capturadas em context/lei/ — [VERIFICAR]: a janela vai do dia da MP 905 ao da MP 955, inclusive, a maior possível); até: MP 905/2019, de 11/11/2019, revogada pela MP 955/2020, de 20/04/2020 (redação riscada com "Vigência encerrada" em context/lei/lei-8213-1991.md:1942; as datas de publicação não estão capturadas em context/lei/ — [VERIFICAR]: a janela vai do dia da MP 905 ao da MP 955, inclusive, a maior possível) |
| `auxilio-acidente` | 21/04/2020 | — | sim | 50% do SB (art. 86, §1º, redação da Lei 9.528/1997, restabelecida pela MP 955/2020; IN 128, art. 233, X), SB pela média de 100% desde 07/1994 | de: MP 905/2019, de 11/11/2019, revogada pela MP 955/2020, de 20/04/2020 (redação riscada com "Vigência encerrada" em context/lei/lei-8213-1991.md:1942; as datas de publicação não estão capturadas em context/lei/ — [VERIFICAR]: a janela vai do dia da MP 905 ao da MP 955, inclusive, a maior possível) |
