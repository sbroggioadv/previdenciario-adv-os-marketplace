# Série histórica dos reajustes dos benefícios do RGPS — 1995 a 2026 (fator integral, Anexo I pro rata e incorporação do teto)

Capturado em: 2026-10-19
Fonte primária: a portaria anual de reajuste de cada ano, no Diário Oficial da União — fac-símile oficial (`pesquisa.in.gov.br`, servlet INPDFViewer, Seção 1) até 2018 e página da matéria em `in.gov.br` de 2019 a 2024. 2025 e 2026 estão em `portaria-interministerial-mps-mf-6-2025.md` e `portaria-interministerial-mps-mf-13-2026.md`.
Dado de máquina: `scripts/data/reajustes-rgps.json` (uma linha por vigência; percentual em string decimal).

> **Como ler.** *Integral* = percentual do art. 1º, caput, para benefício com data de início (DIB) anterior ao período do Anexo I. *Anexo I* = percentual do primeiro reajuste pela DIB (art. 1º, §1º; em 2002 e 2003, art. 2º): a primeira linha ("até <mês>") é o mês do reajuste anterior e repete o integral. *Incorporação* = artigo que incorpora à renda, no primeiro reajuste, a diferença entre a média dos salários-de-contribuição e o teto (DIB no período indicado, até o limite). O **trecho** é cópia do texto extraído da fonte (`pdftotext`; o fac-símile de 2002–2018 tem camada de texto digital, não OCR). O sha256 é do arquivo baixado. Percentuais lidos da fonte; nenhum foi calculado, estimado ou tirado de fonte secundária.

> **Vigência sem linha.** Datas em que o salário mínimo ou o teto mudam em `scripts/data/` sem reajuste dos benefícios acima do mínimo (01/02/2004, 01/03/2011, 01/02/2020, 01/05/2023) não têm linha. Nos motores (`so_piso_e_teto` em `calc_previdenciario_valor_causa.py` e `calc_previdenciario_rmi.py`), data assim, num ano cujo reajuste anual está capturado em outra linha, não pede fator: a renda se mantém e valem o piso e o teto da competência; a conta só abre (exit 3) se faltar a linha do ano. 01/08/2006 é lacuna declarada e abre a conta — ver §3.

## 1. Linhas capturadas

### 2002 — vigência 2002-06-01

- Norma: Portaria MPAS 525, de 29/05/2002, arts. 1º e 2º e Anexo I (DOU 31/05/2002, Seção 1, p. 40)
- Integral: 9.20% · Anexo I a partir da DIB em junho/2001 (pro_rata_desde 2001-06-01)
- Incorporação do teto: DIB de 2001-06-01 a 2002-05-31, limite R$ 1561.56 (Portaria MPAS 525, art. 5º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=40&data=31/05/2002&captchafield=firstAccess · sha256 `84b23ac3e9b5f78c79ae1aaddeb5363bbfe0a22a851cba44f91d4bc8cae2f065`

Trecho do art. do reajuste:

```text
Art. 1o Os benefícios mantidos pela Previdência Social serão reajustados, em 1º de junho de 2002, em nove vírgula vinte por cento. Art. 2º Para os benefícios concedidos pela Previdência Social em data posterior a 30 de junho de 2001, o reajuste, nos termos do art. 1º, dar-se-á de acordo com os percentuais indicados no Anexo I desta Portaria. Art. 3º Para os benefícios majorados na competência abril de 2002, devido à elevação do salário mínimo par
```

Trecho da incorporação:

```text
A partir de 1º de junho de 2002, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1º junho de 2001 a 31 de maio de 2002, a diferença percentual entre a média dos salários-de-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no art. 2º e o limite de R$ 1.561,56 (um mil quinhentos e sessenta e um reais e cinqüenta e seis centavos). Art. 6º O valor
```

| DIB | Reajuste (%) |
|---|---|
| até junho/2001 | 9.20 |
| em julho/2001 | 8.55 |
| em agosto/2001 | 7.36 |
| em setembro/2001 | 6.52 |
| em outubro/2001 | 6.05 |
| em novembro/2001 | 5.06 |
| em dezembro/2001 | 3.72 |
| em janeiro/2002 | 2.96 |
| em fevereiro/2002 | 1.87 |
| em março/2002 | 1.56 |
| em abril/2002 | 0.93 |
| em maio/2002 | 0.25 |

### 2003 — vigência 2003-06-01

- Norma: Portaria MPS 727, de 30/05/2003, arts. 1º e 2º e Anexo I (DOU 02/06/2003, Seção 1, p. 20)
- Integral: 19.71% · Anexo I a partir da DIB em junho/2002 (pro_rata_desde 2002-06-01)
- Incorporação do teto: DIB de 2002-06-01 a 2003-05-31, limite R$ 1869.34 (Portaria MPS 727, art. 5º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=20&data=02/06/2003&captchafield=firstAccess · sha256 `d001602310f86fbcf810f5a2f22610191109bf6a54ea64484c05cdff1ead2d8a`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios mantidos pela Previdência Social serão reajustados, em 1º de junho de 2003, em dezenove vírgula setenta e um por cento. Art. 2º Para os benefícios concedidos pela Previdência Social em data posterior a 30 de junho de 2002, o reajuste, nos termos do art. 1º, dar-se-á de acordo com os percentuais indicados no Anexo I desta Portaria. Art. 3º Para os benefícios majorados na competência abril de 2003, devido à elevação do salário
```

Trecho da incorporação:

```text
A partir de 1º de junho de 2003, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1º junho de 2002 a 31 de maio de 2003, a diferença percentual entre a média dos salários-de-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no art. 2º e o limite de R$ 1.869,34 (um mil oitocentos e sessenta e nove reais e trinta e quatro centavos). Art. 6º O valor
```

| DIB | Reajuste (%) |
|---|---|
| até junho/2002 | 19.71 |
| em julho/2002 | 18.98 |
| em agosto/2002 | 17.63 |
| em setembro/2002 | 16.63 |
| em outubro/2002 | 15.67 |
| em novembro/2002 | 13.88 |
| em dezembro/2002 | 10.15 |
| em janeiro/2003 | 7.25 |
| em fevereiro/2003 | 4.67 |
| em março/2003 | 3.16 |
| em abril/2003 | 1.77 |
| em maio/2003 | 0.38 |

### 2004 — vigência 2004-05-01

- Norma: Portaria MPS 479, de 07/05/2004, art. 1º, caput e §1º, e Anexo I (DOU 10/05/2004, Seção 1, pp. 35–36)
- Integral: 4.53% · Anexo I a partir da DIB em junho/2003 (pro_rata_desde 2003-06-01)
- Incorporação do teto: DIB de 2003-06-01 a 2004-04-30, limite R$ 2508.72 (Portaria MPS 479, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=35&data=10/05/2004&captchafield=firstAccess · sha256 `1c747086ad079f7c9bd5cdd57de091db42192352c4d91e95d8b7f218e0962e01`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=36&data=10/05/2004&captchafield=firstAccess · sha256 `bcb524b3111e7069f9263cb17162022ebb4ae5bdc80af6a863893cdc13c866af`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios mantidos pela Previdência Social serão reajustados, a partir de 1º de maio de 2004, em quatro vírgula cinqüenta e três por cento. § 1º Os benefícios concedidos pela Previdência Social em data posterior a 30 de junho de 2003 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados devido à elevação do salário mínimo para R$ 260,00 (duzentos e sessenta reais), o refe
```

Trecho da incorporação:

```text
A partir de 1º de maio de 2004, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1º junho de 2003 a 30 de abril de 2004, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 2.508,72 (dois mil quinhentos e oito reais e setenta e dois centavos). Art. 7º A contrib
```

| DIB | Reajuste (%) |
|---|---|
| até junho/2003 | 4.53 |
| em julho/2003 | 4.59 |
| em agosto/2003 | 4.55 |
| em setembro/2003 | 4.36 |
| em outubro/2003 | 3.51 |
| em novembro/2003 | 3.11 |
| em dezembro/2003 | 2.73 |
| em janeiro/2004 | 2.18 |
| em fevereiro/2004 | 1.34 |
| em março/2004 | 0.94 |
| em abril/2004 | 0.37 |

### 2005 — vigência 2005-05-01

- Norma: Portaria MPS 822, de 11/05/2005, art. 1º, caput e §1º, e Anexo I (DOU 12/05/2005, Seção 1, p. 36)
- Integral: 6.355% · Anexo I a partir da DIB em maio/2004 (pro_rata_desde 2004-05-01)
- Incorporação do teto: DIB de 2004-05-01 a 2005-04-30, limite R$ 2668.15 (Portaria MPS 822, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=36&data=12/05/2005&captchafield=firstAccess · sha256 `f1e70ee8b636a1d7f00462cfe1ec25e22bf94e720b216f8e55e7d3064194d2de`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios mantidos pela Previdência Social serão reajustados, a partir de 1º de maio de 2005, em seis inteiros e trezentos e cinqüenta e cinco milésimos por cento. § 1º Os benefícios concedidos pela Previdência Social em data posterior a 1º de junho de 2004 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados devido à elevação do salário mínimo para R$ 300,00 (trezentos
```

Trecho da incorporação:

```text
A partir de 1º de maio de 2005, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1º maio de 2004 a 30 de abril de 2005, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 2.668,15 (dois mil seiscentos e sessenta e oito reais e quinze centavos). Art. 7º A contr
```

| DIB | Reajuste (%) |
|---|---|
| até maio/2004 | 6.355 |
| em junho/2004 | 5.932 |
| em julho/2004 | 5.405 |
| em agosto/2004 | 4.641 |
| em setembro/2004 | 4.120 |
| em outubro/2004 | 3.944 |
| em novembro/2004 | 3.767 |
| em dezembro/2004 | 3.313 |
| em janeiro/2005 | 2.432 |
| em fevereiro/2005 | 1.851 |
| em março/2005 | 1.405 |
| em abril/2005 | 0.670 |

### 2006 — vigência 2006-04-01

- Norma: Portaria MPS 119, de 18/04/2006, art. 1º, caput e §1º, e Anexo I (DOU 19/04/2006, Seção 1, pp. 42–43)
- Integral: 5.00% · Anexo I a partir da DIB em maio/2005 (pro_rata_desde 2005-05-01)
- Incorporação do teto: DIB de 2005-05-01 a 2006-03-31, limite R$ 2801.56 (Portaria MPS 119, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=42&data=19/04/2006&captchafield=firstAccess · sha256 `bc9556dae01ec1d5b39789670d9a8e0f9321176612e6d84ed124f798a0629bad`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=43&data=19/04/2006&captchafield=firstAccess · sha256 `80e8eb9999ca993ed26355f622c53f4edb965385fefc9026ecef18841b3da317`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios mantidos pela Previdência Social serão reajustados, a partir de 1º de abril de 2006, em cinco inteiros por cento. § 1º Os benefícios concedidos pela Previdência Social em data posterior a 1º de maio de 2005 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados devido à elevação do salário mínimo para R$ 350,00 (trezentos e cinqüenta reais), o referido aumento de
```

Trecho da incorporação:

```text
A partir de 1º de abril de 2006, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1º maio de 2005 a 31 de março de 2006, a diferença percentual entre a média dos salários-de-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 2.801,56 (dois mil oitocentos e um reais e cinqüenta e seis centavos). Art. 7º Excepcion
```

| DIB | Reajuste (%) |
|---|---|
| até maio/2005 | 5.00 |
| em junho/2005 | 4.270 |
| em julho/2005 | 4.385 |
| em agosto/2005 | 4.354 |
| em setembro/2005 | 4.354 |
| em outubro/2005 | 4.198 |
| em novembro/2005 | 3.597 |
| em dezembro/2005 | 3.040 |
| em janeiro/2006 | 2.630 |
| em fevereiro/2006 | 2.241 |
| em março/2006 | 2.007 |

### 2007 — vigência 2007-04-01

- Norma: Portaria MPS 142, de 11/04/2007, art. 1º, caput e §1º, e Anexo I (DOU 12/04/2007, Seção 1, p. 45)
- Integral: 3.30% · Anexo I a partir da DIB em abril/2006 (pro_rata_desde 2006-04-01)
- Incorporação do teto: DIB de 2006-04-01 a 2007-03-31, limite R$ 2894.28 (Portaria MPS 142, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=45&data=12/04/2007&captchafield=firstAccess · sha256 `b87b288f9da64f8a859bfdb3ce8c5694f91c4ddd8a552c9d16bbcae5cc724664`

Trecho do art. do reajuste:

```text
Art. 1 o- Os benefícios mantidos pela Previdência Social serão reajustados, a partir de 1 o- de abril de 2007, em três inteiros e trinta centésimos por cento. § 1 o- Os benefícios concedidos pela Previdência Social em data posterior ao mês de abril de 2006 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2 o- Para os benefícios majorados devido à elevação do salário mínimo para R$ 380,00 (trezentos e oitenta rea
```

Trecho da incorporação:

```text
A partir de 1 o- de abril de 2007, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1 o- abril de 2006 a 31 de março de 2007, a diferença percentual entre a média dos salários-de-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1 o- do art. 1 o- e o limite de R$ 2.894,28 (dois mil oitocentos e noventa e quatro reais e vinte e oito centavos).
```

| DIB | Reajuste (%) |
|---|---|
| até abril/2006 | 3.30 |
| em maio/2006 | 3.17 |
| em junho/2006 | 3.04 |
| em julho/2006 | 3.11 |
| em agosto/2006 | 3.00 |
| em setembro/2006 | 3.02 |
| em outubro/2006 | 2.85 |
| em novembro/2006 | 2.41 |
| em dezembro/2006 | 1.98 |
| em janeiro/2007 | 1.36 |
| em fevereiro/2007 | 0.86 |
| em março/2007 | 0.44 |

### 2008 — vigência 2008-03-01

- Norma: Portaria Interministerial MPS/MF 77, de 11/03/2008, art. 1º, caput e §1º, e Anexo I (DOU 12/03/2008, Seção 1, pp. 42–43)
- Integral: 5.00% · Anexo I a partir da DIB em abril/2007 (pro_rata_desde 2007-04-01)
- Incorporação do teto: DIB de 2007-04-01 a 2008-02-29, limite R$ 3038.99 (Portaria Interministerial MPS/MF 77, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=42&data=12/03/2008&captchafield=firstAccess · sha256 `2106a57e7201cf8c0f01b3113564a3b3106f82d1dfd0008bbfdba73f9512dfc4`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=43&data=12/03/2008&captchafield=firstAccess · sha256 `10b8adc4951841a4d26b48f9b49240b2ed8bfebeb10c7004fc07ab6b23819e98`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios mantidos pela Previdência Social serão reajustados, a partir de 1º de março de 2008, em cinco inteiros por cento. § 1º Os benefícios concedidos pela Previdência Social em data posterior ao mês de abril de 2007 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados devido à elevação do salário mínimo para R$ 415,00 (quatrocentos e quinze reais), o referido aumento
```

Trecho da incorporação:

```text
A partir de 1º de março de 2008, será incorporada à renda mensal dos benefícios de prestação continuada pagos pela Previdência Social, com data de início no período de 1º abril de 2007 a 29 de fevereiro de 2008, a diferença percentual entre a média dos salários-de-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 3.038,99 (três mil e trinta e oito reais e noventa e nove centavos). Art. 7º A cont
```

| DIB | Reajuste (%) |
|---|---|
| até abril/2007 | 5.00 |
| em maio/2007 | 4.73 |
| em junho/2007 | 4.45 |
| em julho/2007 | 4.13 |
| em agosto/2007 | 3.80 |
| em setembro/2007 | 3.19 |
| em outubro/2007 | 2.93 |
| em novembro/2007 | 2.62 |
| em dezembro/2007 | 2.19 |
| em janeiro/2008 | 1.20 |
| em fevereiro/2008 | 0.51 |

### 2009 — vigência 2009-02-01

- Norma: Portaria Interministerial MPS/MF 48, de 12/02/2009, art. 1º, caput e §1º, e Anexo I (DOU 13/02/2009, Seção 1, pp. 52–53)
- Integral: 5.92% · Anexo I a partir da DIB em março/2008 (pro_rata_desde 2008-03-01)
- Incorporação do teto: DIB de 2008-03-01 a 2009-01-31, limite R$ 3218.90 (Portaria Interministerial MPS/MF 48, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=52&data=13/02/2009&captchafield=firstAccess · sha256 `dfaa7ef55d650952472b5138218863aa0c4eb7d7e43ffdd109e5ef9d48c63a8e`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=53&data=13/02/2009&captchafield=firstAccess · sha256 `702e2c1eda22b6f781cb19335815ccdd4160760a23acf314115d649cc6f879a8`

Trecho do art. do reajuste:

```text
Art. 1 o- Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1 o- de fevereiro de 2009, em cinco inteiros e noventa e dois centésimos por cento. § 1 o- Os benefícios pagos pelo INSS em data posterior ao mês de março de 2008 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2 o- Para os benefícios majorados por força da elevação do salário-mínimo para R$ 465,00 (q
```

Trecho da incorporação:

```text
A partir de 1 o- de fevereiro de 2009, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1 o- março de 2008 a 31 de janeiro de 2009, a diferença percentual entre a média dos salários-decontribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1 o- do art. 1 o- e o limite de R$ 3.218,90 (três mil duzentos e dezoito reais e noventa centavos). Art. 7 o- A contribuição dos
```

| DIB | Reajuste (%) |
|---|---|
| até março/2008 | 5.92 |
| em abril/2008 | 5.38 |
| em maio/2008 | 4.71 |
| em junho/2008 | 3.72 |
| em julho/2008 | 2.78 |
| em agosto/2008 | 2.19 |
| em setembro/2008 | 1.97 |
| em outubro/2008 | 1.82 |
| em novembro/2008 | 1.32 |
| em dezembro/2008 | 0.93 |
| em janeiro/2009 | 0.64 |

### 2010 — vigência 2010-01-01

- Norma: Portaria Interministerial MPS/MF 333, de 29/06/2010, art. 1º, caput e §1º, e Anexo I (DOU 30/06/2010, Seção 1, p. 95; retroativa a 01/01/2010, revogou a PI 350/2009)
- Integral: 7.72% · Anexo I a partir da DIB em fevereiro/2009 (pro_rata_desde 2009-02-01)
- Incorporação do teto: DIB de 2009-02-01 a 2009-12-31, limite R$ 3467.40 (Portaria Interministerial MPS/MF 333, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=95&data=30/06/2010&captchafield=firstAccess · sha256 `a1c198df546ff1aee200d4e147522a43e1385164318ba5cdae41bc415fb19106`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2010, em 7,72% (sete inteiros e setenta e dois centésimos por cento). § 1º Os benefícios pagos pelo INSS em data posterior ao mês de fevereiro de 2009 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário-mínimo para R$ 510,00
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2010, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º fevereiro de 2009 a 31 de dezembro de 2009, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 3.467,40 (três mil quatrocentos e sessenta e sete reais e quarenta centavos). Art. 7º A contrib
```

| DIB | Reajuste (%) |
|---|---|
| até fevereiro/2009 | 7.72 |
| em março/2009 | 7.39 |
| em abril/2009 | 7.17 |
| em maio/2009 | 6.58 |
| em junho/2009 | 5.95 |
| em julho/2009 | 5.51 |
| em agosto/2009 | 5.26 |
| em setembro/2009 | 5.18 |
| em outubro/2009 | 5.01 |
| em novembro/2009 | 4.77 |
| em dezembro/2009 | 4.38 |

### 2011 — vigência 2011-01-01

- Norma: Portaria Interministerial MPS/MF 407, de 14/07/2011, art. 1º, caput e §1º, e Anexo I (DOU 15/07/2011, Seção 1, p. 54; a partir de 01/01/2011, revogou a PI 568/2010)
- Integral: 6.47% · Anexo I a partir da DIB em janeiro/2010 (pro_rata_desde 2010-01-01)
- Incorporação do teto: DIB de 2010-02-01 a 2010-12-31, limite R$ 3691.74 (Portaria Interministerial MPS/MF 407, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=54&data=15/07/2011&captchafield=firstAccess · sha256 `74ab72d55821d478399998e1e12ee00ebc6e80df65425bc96268697eb848fa5f`

Trecho do art. do reajuste:

```text
Art. 1o Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1o de janeiro de 2011, em 6,47% (seis inteiros e quarenta e sete centésimos por cento), com efeitos financeiros a partir de 1º de janeiro de 2011. § 1o Os benefícios pagos pelo INSS com data de início a partir de fevereiro de 2010, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2011, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º fevereiro de 2010 a 31 de dezembro de 2010, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 3.691,74 (três mil seiscentos e noventa e um reais e setenta e quatro centavos). Art. 7º A cont
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2010 | 6.47 |
| em fevereiro/2010 | 5.54 |
| em março/2010 | 4.80 |
| em abril/2010 | 4.06 |
| em maio/2010 | 3.31 |
| em junho/2010 | 2.87 |
| em julho/2010 | 2.98 |
| em agosto/2010 | 3.05 |
| em setembro/2010 | 3.13 |
| em outubro/2010 | 2.57 |
| em novembro/2010 | 1.64 |
| em dezembro/2010 | 0.60 |

### 2012 — vigência 2012-01-01

- Norma: Portaria Interministerial MPS/MF 2, de 06/01/2012, art. 1º, caput e §1º, e Anexo I (DOU 09/01/2012, Seção 1, p. 59)
- Integral: 6.08% · Anexo I a partir da DIB em janeiro/2011 (pro_rata_desde 2011-01-01)
- Incorporação do teto: DIB de 2011-01-01 a 2011-12-31, limite R$ 3916.20 (Portaria Interministerial MPS/MF 2, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=59&data=09/01/2012&captchafield=firstAccess · sha256 `71325edd1ce9dc34f702eddf2b472cfa6716c8950d3551504dd4acbe911e42c7`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social (INSS) serão reajustados, a partir de 1º de janeiro de 2012, em 6,08% (seis inteiros e oito décimos por cento). § 1º Os benefícios a que se refere o caput com data de início a partir de fevereiro de 2011 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário-mínimo para R$ 622,00 (
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2012, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2011 a 31 de dezembro de 2011, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 3.916,20 (três mil novecentos e dezesseis reais e vinte centavos). Art. 7º A contribuição dos seg
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2011 | 6.08 |
| em fevereiro/2011 | 5.09 |
| em março/2011 | 4.53 |
| em abril/2011 | 3.84 |
| em maio/2011 | 3.10 |
| em junho/2011 | 2.52 |
| em julho/2011 | 2.29 |
| em agosto/2011 | 2.29 |
| em setembro/2011 | 1.86 |
| em outubro/2011 | 1.41 |
| em novembro/2011 | 1.08 |
| em dezembro/2011 | 0.51 |

### 2013 — vigência 2013-01-01

- Norma: Portaria Interministerial MPS/MF 15, de 10/01/2013, art. 1º, caput e §1º, e Anexo I (DOU 11/01/2013, Seção 1, pp. 46–47)
- Integral: 6.20% · Anexo I a partir da DIB em janeiro/2012 (pro_rata_desde 2012-01-01)
- Incorporação do teto: DIB de 2012-01-01 a 2012-12-31, limite R$ 4159.00 (Portaria Interministerial MPS/MF 15, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=46&data=11/01/2013&captchafield=firstAccess · sha256 `2e6a0ca06ec1f2f3403f0fe1c542b750717e0e5c3039df43f7d3ce55365b9615`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=47&data=11/01/2013&captchafield=firstAccess · sha256 `2ee0a6176610be6b5edf2a91b1dd219565067f9764f17d68acb2a7f0d05298b8`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social (INSS) serão reajustados, a partir de 1º de janeiro de 2013, em 6, 20% (seis inteiros e vinte décimos por cento). § 1º Os benefícios a que se refere o caput com data de início a partir de 1o de fevereiro de 2012 serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário-mínimo para R$
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2013, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2012 a 31 de dezembro de 2012, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 4.159,00 (quatro mil cento e cinquenta e nove reais). Art. 7º A contribuição dos segurados empreg
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2012 | 6.20 |
| em fevereiro/2012 | 5.66 |
| em março/2012 | 5.25 |
| em abril/2012 | 5.06 |
| em maio/2012 | 4.39 |
| em junho/2012 | 3.82 |
| em julho/2012 | 3.55 |
| em agosto/2012 | 3.11 |
| em setembro/2012 | 2.65 |
| em outubro/2012 | 2.00 |
| em novembro/2012 | 1.28 |
| em dezembro/2012 | 0.74 |

### 2014 — vigência 2014-01-01

- Norma: Portaria Interministerial MPS/MF 19, de 10/01/2014, art. 1º, caput e §1º, e Anexo I (DOU 13/01/2014, Seção 1, pp. 21–22)
- Integral: 5.56% · Anexo I a partir da DIB em janeiro/2013 (pro_rata_desde 2013-01-01)
- Incorporação do teto: DIB de 2013-01-01 a 2013-12-31, limite R$ 4390.24 (Portaria Interministerial MPS/MF 19, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=21&data=13/01/2014&captchafield=firstAccess · sha256 `a3d22747f85cff998c4c012b8c1cadaacde4816ad626a857bd93f9db053fd99d`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=22&data=13/01/2014&captchafield=firstAccess · sha256 `bf90f35694cd4d5714236bbf550ccf245036fadb91408e9453271fd316ace417`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2014, em 5,56% (cinco inteiros e cinquenta e seis décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1o de fevereiro de 2013, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário-mí
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2014, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2013 a 31 de dezembro de 2013, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 4.390,24 (quatro mil, trezentos e noventa reais e vinte e quatro centavos). Art. 7º A contribuiçã
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2013 | 5.56 |
| em fevereiro/2013 | 4.60 |
| em março/2013 | 4.06 |
| em abril/2013 | 3.44 |
| em maio/2013 | 2.83 |
| em junho/2013 | 2.47 |
| em julho/2013 | 2.19 |
| em agosto/2013 | 2.32 |
| em setembro/2013 | 2.16 |
| em outubro/2013 | 1.88 |
| em novembro/2013 | 1.26 |
| em dezembro/2013 | 0.72 |

### 2015 — vigência 2015-01-01

- Norma: Portaria Interministerial MPS/MF 13, de 09/01/2015, art. 1º, caput e §1º, e Anexo I (DOU 12/01/2015, Seção 1, pp. 15–16)
- Integral: 6.23% · Anexo I a partir da DIB em janeiro/2014 (pro_rata_desde 2014-01-01)
- Incorporação do teto: DIB de 2014-01-01 a 2014-12-31, limite R$ 4663.75 (Portaria Interministerial MPS/MF 13, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=15&data=12/01/2015&captchafield=firstAccess · sha256 `14d5bb226f294bf6a67ff3176522932f5c27243861852e4b4fae3e9d6524adcb`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=16&data=12/01/2015&captchafield=firstAccess · sha256 `68d5b885c6bfcbee3746ac183b22edbe831cc04e3f2993a498faab2e2796972d`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2015, em 6,23% (seis inteiros e vinte e três décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de fevereiro de 2014, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário mínimo
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2015, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2014 a 31 de dezembro de 2014, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 4.663,75 (quatro mil seiscentos e sessenta e três reais e setenta e cinco centavos). Art. 7º A co
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2014 | 6.23 |
| em fevereiro/2014 | 5.56 |
| em março/2014 | 4.89 |
| em abril/2014 | 4.04 |
| em maio/2014 | 3.23 |
| em junho/2014 | 2.62 |
| em julho/2014 | 2.35 |
| em agosto/2014 | 2.22 |
| em setembro/2014 | 2.04 |
| em outubro/2014 | 1.54 |
| em novembro/2014 | 1.15 |
| em dezembro/2014 | 0.62 |

### 2016 — vigência 2016-01-01

- Norma: Portaria Interministerial MTPS/MF 1, de 08/01/2016, art. 1º, caput e §1º, e Anexo I (DOU 11/01/2016, Seção 1, pp. 67–68)
- Integral: 11.28% · Anexo I a partir da DIB em janeiro/2015 (pro_rata_desde 2015-01-01)
- Incorporação do teto: DIB de 2015-01-01 a 2015-12-31, limite R$ 5189.82 (Portaria Interministerial MTPS/MF 1, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=67&data=11/01/2016&captchafield=firstAccess · sha256 `c0763c4f0614e20760808923ce97798c227dd9b46a53950e8ceb9a1a5cf2cad3`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=68&data=11/01/2016&captchafield=firstAccess · sha256 `e8b46d06069bf92b6f1ba34008006f64cd846268bf220b45546961760bda7cb3`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2016, em 11,28% (onze inteiros e vinte e oito décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de fevereiro de 2015, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário mínimo
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2016, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2015 a 31 de dezembro de 2015, a diferença percentual entre a média dos saláriosde-contribuição considerados no cálculo do salário-de-benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 5.189,82 (cinco mil cento e oitenta e nove reais e oitenta e dois centavos). Art. 7º A contribuiç
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2015 | 11.28 |
| em fevereiro/2015 | 9.65 |
| em março/2015 | 8.40 |
| em abril/2015 | 6.78 |
| em maio/2015 | 6.03 |
| em junho/2015 | 4.99 |
| em julho/2015 | 4.19 |
| em agosto/2015 | 3.59 |
| em setembro/2015 | 3.33 |
| em outubro/2015 | 2.81 |
| em novembro/2015 | 2.02 |
| em dezembro/2015 | 0.90 |

### 2017 — vigência 2017-01-01

- Norma: Portaria MF 8, de 13/01/2017, art. 1º, caput e §1º, e Anexo I (DOU 16/01/2017, Seção 1, pp. 12–13)
- Integral: 6.58% · Anexo I a partir da DIB em janeiro/2016 (pro_rata_desde 2016-01-01)
- Incorporação do teto: DIB de 2016-01-01 a 2016-12-31, limite R$ 5531.31 (Portaria MF 8, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=12&data=16/01/2017&captchafield=firstAccess · sha256 `91e9dae8449b53957a22d2a320bf563543561df12fc3eaa97949c59dfea74437`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=1&pagina=13&data=16/01/2017&captchafield=firstAccess · sha256 `b2ea3beec9e7166521f120fe7bc6fc6d3c5d42bee255ece89d524a2178edd3c6`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2017, em 6,58% (seis inteiros e cinquenta e oito décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de fevereiro de 2016, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário mín
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2017, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2016 a 31 de dezembro de 2016, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 5.531,31 (cinco mil quinhentos e trinta e um reais e trinta e um centavos). Art. 7º A contribuiç
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2016 | 6.58 |
| em fevereiro/2016 | 4.99 |
| em março/2016 | 4.01 |
| em abril/2016 | 3.55 |
| em maio/2016 | 2.89 |
| em junho/2016 | 1.89 |
| em julho/2016 | 1.42 |
| em agosto/2016 | 0.77 |
| em setembro/2016 | 0.46 |
| em outubro/2016 | 0.38 |
| em novembro/2016 | 0.21 |
| em dezembro/2016 | 0.14 |

### 2018 — vigência 2018-01-01

- Norma: Portaria MF 15, de 16/01/2018, art. 1º, caput e §1º, e Anexo I (DOU 17/01/2018, Seção 1, pp. 28–29)
- Integral: 2.07% · Anexo I a partir da DIB em janeiro/2017 (pro_rata_desde 2017-01-01)
- Incorporação do teto: DIB de 2017-01-01 a 2017-12-31, limite R$ 5645.80 (Portaria MF 15, art. 6º)
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=515&pagina=28&data=17/01/2018&captchafield=firstAccess · sha256 `3e96cf3b1604a953b8a4c9f91b522071d8a3794cadd5f69ff2e763bd3ac3cd90`
- Fonte: https://pesquisa.in.gov.br/imprensa/servlet/INPDFViewer?jornal=515&pagina=29&data=17/01/2018&captchafield=firstAccess · sha256 `ae1ff091efcbfb2fbaffb9db872e57cf68a210fbc372757767922b2864d6f463`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2018, em 2,07% (dois inteiros e sete décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2018, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário mínimo para R$ 95
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2018, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2017 a 31 de dezembro de 2017, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 5.645,80 (cinco mil seiscentos e quarenta e cinco reais e oitenta centavos). Art. 7º A contribui
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2017 | 2.07 |
| em fevereiro/2017 | 1.64 |
| em março/2017 | 1.40 |
| em abril/2017 | 1.07 |
| em maio/2017 | 0.99 |
| em junho/2017 | 0.63 |
| em julho/2017 | 0.93 |
| em agosto/2017 | 0.76 |
| em setembro/2017 | 0.79 |
| em outubro/2017 | 0.81 |
| em novembro/2017 | 0.44 |
| em dezembro/2017 | 0.26 |

### 2019 — vigência 2019-01-01

- Norma: Portaria ME 9, de 15/01/2019, art. 1º, caput e §1º, e Anexo I (DOU 16/01/2019, Seção 1)
- Integral: 3.43% · Anexo I a partir da DIB em janeiro/2018 (pro_rata_desde 2018-01-01)
- Incorporação do teto: DIB de 2018-01-01 a 2018-12-31, limite R$ 5839.45 (Portaria ME 9, art. 6º)
- Fonte: https://www.in.gov.br/web/dou/-/portaria-n-9-de-15-de-janeiro-de-2019-59253472 · sha256 `831970756614553545402ca9435587dce0d6207cde4e951654256774520eeb8a`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2019, em 3,43% (três inteiros e quarenta e três décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2018, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário mínimo
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2019, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2018 a 31 de dezembro de 2018, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 5.839,45 (cinco mil oitocentos e trinta e nove reais e quarenta e cinco centavos). Art. 7º A con
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2018 | 3.43 |
| em fevereiro/2018 | 3.20 |
| em março/2018 | 3.01 |
| em abril/2018 | 2.94 |
| em maio/2018 | 2.72 |
| em junho/2018 | 2.28 |
| em julho/2018 | 0.84 |
| em agosto/2018 | 0.59 |
| em setembro/2018 | 0.59 |
| em outubro/2018 | 0.29 |
| em novembro/2018 | 0.00 |
| em dezembro/2018 | 0.14 |

### 2020 — vigência 2020-01-01

- Norma: Portaria SEPRT/ME 914, de 13/01/2020, art. 1º, caput e §1º, e Anexo I (DOU 14/01/2020, Seção 1)
- Integral: 4.48% · Anexo I a partir da DIB em janeiro/2019 (pro_rata_desde 2019-01-01)
- Incorporação do teto: DIB de 2019-01-01 a 2019-12-31, limite R$ 6101.06 (Portaria SEPRT/ME 914, art. 6º)
- Fonte: https://www.in.gov.br/web/dou/-/portaria-n-914-de-13-de-janeiro-de-2020-237937443 · sha256 `cb209478593633c42cde91ccd799b29911b6d454e2a497758108443b835e0d2b`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2020, em 4,48% (quatro inteiros e quarenta e oito décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2019, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Para os benefícios majorados por força da elevação do salário míni
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2020, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2019 a 31 de dezembro de 2019, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 6.101,06 (seis mil, cento e um reais e seis centavos). Art. 7º A contribuição dos segurados empr
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2019 | 4.48 |
| em fevereiro/2019 | 4.11 |
| em março/2019 | 3.55 |
| em abril/2019 | 2.76 |
| em maio/2019 | 2.14 |
| em junho/2019 | 1.99 |
| em julho/2019 | 1.98 |
| em agosto/2019 | 1.88 |
| em setembro/2019 | 1.76 |
| em outubro/2019 | 1.81 |
| em novembro/2019 | 1.77 |
| em dezembro/2019 | 1.22 |

### 2021 — vigência 2021-01-01

- Norma: Portaria SEPRT/ME 477, de 12/01/2021, art. 1º, caput e §1º, e Anexo I (DOU 13/01/2021, Seção 1)
- Integral: 5.45% · Anexo I a partir da DIB em janeiro/2020 (pro_rata_desde 2020-01-01)
- Incorporação do teto: DIB de 2020-01-01 a 2020-12-31, limite R$ 6433.57 (Portaria SEPRT/ME 477, art. 6º)
- Fonte: https://www.in.gov.br/web/dou/-/portaria-seprt/me-n-477-de-12-de-janeiro-de-2021-298858991 · sha256 `1c17f48429e24c3af48f0300e5b4381c1eea6731ecc355757be3b5311e1aceea`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2021, em 5,45% (cinco inteiros e quarenta e cinco décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2020, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Aplica-se o disposto neste artigo às pensões especiais pagas às ví
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2021, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2020 a 31 de dezembro de 2020, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 6.433,57 (seis mil quatrocentos e trinta e três reais e cinquenta e sete centavos). Art. 7º A co
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2020 | 5.45 |
| em fevereiro/2020 | 5.25 |
| em março/2020 | 5.07 |
| em abril/2020 | 4.88 |
| em maio/2020 | 5.12 |
| em junho/2020 | 5.39 |
| em julho/2020 | 5.07 |
| em agosto/2020 | 4.61 |
| em setembro/2020 | 4.23 |
| em outubro/2020 | 3.34 |
| em novembro/2020 | 2.42 |
| em dezembro/2020 | 1.46 |

### 2022 — vigência 2022-01-01

- Norma: Portaria Interministerial MTP/ME 12, de 17/01/2022, art. 1º, caput e §1º, e Anexo I (DOU 20/01/2022, Seção 1)
- Integral: 10.16% · Anexo I a partir da DIB em janeiro/2021 (pro_rata_desde 2021-01-01)
- Incorporação do teto: DIB de 2021-01-01 a 2021-12-31, limite R$ 7087.22 (Portaria Interministerial MTP/ME 12, art. 6º)
- Fonte: https://www.in.gov.br/web/dou/-/portaria-interministerial-mtp/me-n-12-de-17-de-janeiro-de-2022-375006998 · sha256 `7601d74d182ce1e156ff340dc69f54b85fbcfa505b8687b48fb4f4c89af790a9`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2022, em 10,16% (dez inteiros e dezesseis décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2021, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Aplica-se o disposto neste artigo às pensões especiais pagas às vítimas da
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2022, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2021 a 31 de dezembro de 2021, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 7.087,22 (sete mil e oitenta e sete reais e vinte e dois centavos). Art. 7º A contribuição dos s
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2021 | 10.16 |
| em fevereiro/2021 | 9.86 |
| em março/2021 | 8.97 |
| em abril/2021 | 8.04 |
| em maio/2021 | 7.63 |
| em junho/2021 | 6.61 |
| em julho/2021 | 5.97 |
| em agosto/2021 | 4.90 |
| em setembro/2021 | 3.99 |
| em outubro/2021 | 2.75 |
| em novembro/2021 | 1.58 |
| em dezembro/2021 | 0.73 |

### 2023 — vigência 2023-01-01

- Norma: Portaria Interministerial MPS/MF 26, de 10/01/2023, art. 1º, caput e §1º, e Anexo I (DOU 11/01/2023, Seção 1)
- Integral: 5.93% · Anexo I a partir da DIB em janeiro/2022 (pro_rata_desde 2022-01-01)
- Incorporação do teto: DIB de 2022-01-01 a 2022-12-31, limite R$ 7507.49 (Portaria Interministerial MPS/MF 26, art. 6º)
- Fonte: https://www.in.gov.br/web/dou/-/portaria-interministerial-mps/mf-n-26-de-10-de-janeiro-de-2023-457160869 · sha256 `d159bf2aec12af45806a541ae34893ac20c02d18e232c67dc49d1800a03605a2`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2023, em 5,93% (cinco inteiros e noventa e três décimos por cento). § 1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2022, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. § 2º Aplica-se o disposto neste artigo às pensões especiais pagas às víti
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2023, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2022 a 31 de dezembro de 2022, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 7.507,49 (sete mil quinhentos e sete reais e quarenta e nove centavos). Art. 7º A contribuição d
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2022 | 5.93 |
| em fevereiro/2022 | 5.23 |
| em março/2022 | 4.19 |
| em abril/2022 | 2.43 |
| em maio/2022 | 1.38 |
| em junho/2022 | 0.93 |
| em julho/2022 | 0.30 |
| em agosto/2022 | 0.91 |
| em setembro/2022 | 1.22 |
| em outubro/2022 | 1.55 |
| em novembro/2022 | 1.07 |
| em dezembro/2022 | 0.69 |

### 2024 — vigência 2024-01-01

- Norma: Portaria Interministerial MPS/MF 2, de 11/01/2024, art. 1º, caput e §1º, e Anexo I (DOU 12/01/2024, Seção 1)
- Integral: 3.71% · Anexo I a partir da DIB em janeiro/2023 (pro_rata_desde 2023-01-01)
- Incorporação do teto: DIB de 2023-01-01 a 2023-12-31, limite R$ 7786.02 (Portaria Interministerial MPS/MF 2, art. 6º)
- Fonte: https://www.in.gov.br/web/dou/-/portaria-interministerial-mps/mf-n-2-de-11-de-janeiro-de-2024-537035232 · sha256 `d0a9d69dac3b4aa2e95a4ad39efe210445d93b7a4aa09b3382e8ffda5761e1df`

Trecho do art. do reajuste:

```text
Art. 1º Os benefícios pagos pelo Instituto Nacional do Seguro Social - INSS serão reajustados, a partir de 1º de janeiro de 2024, em 3,71% (três inteiros e setenta e um décimos por cento). §1º Os benefícios a que se refere o caput, com data de início a partir de 1º de janeiro de 2023, serão reajustados de acordo com os percentuais indicados no Anexo I desta Portaria. §2º Aplica-se o disposto neste artigo às pensões especiais pagas às vítimas d
```

Trecho da incorporação:

```text
A partir de 1º de janeiro de 2024, será incorporada à renda mensal dos benefícios de prestação continuada pagos pelo INSS, com data de início no período de 1º janeiro de 2023 a 31 de dezembro de 2023, a diferença percentual entre a média dos salários de contribuição considerados no cálculo do salário de benefício e o limite máximo em vigor no período, exclusivamente nos casos em que a referida diferença resultar positiva, observado o disposto no § 1º do art. 1º e o limite de R$ 7.786,02 (sete mil setecentos e oitenta e seis reais e dois centavos). Art. 7º A contribuição do
```

| DIB | Reajuste (%) |
|---|---|
| até janeiro/2023 | 3.71 |
| em fevereiro/2023 | 3.23 |
| em março/2023 | 2.44 |
| em abril/2023 | 1.79 |
| em maio/2023 | 1.26 |
| em junho/2023 | 0.89 |
| em julho/2023 | 0.99 |
| em agosto/2023 | 1.08 |
| em setembro/2023 | 0.88 |
| em outubro/2023 | 0.77 |
| em novembro/2023 | 0.65 |
| em dezembro/2023 | 0.55 |

## 2. Linhas de 2025 e 2026

Ver `portaria-interministerial-mps-mf-6-2025.md` (arts. 1º e 6º e Anexo I) e `portaria-interministerial-mps-mf-13-2026.md` (idem).

## 3. Lacunas (sem linha no JSON; o motor abre a conta)

> **2.0.1 (20/10/2026).** Fechados com texto capturado na base Datalegis da ANTT, um arquivo por portaria em `context/lei/`: 06/1997 (`portaria-mpas-3971-1997-reajuste.md`), 06/1998 (`portaria-mpas-4478-1998-reajuste.md`), 06/1999 (`portaria-mpas-5188-1999-reajuste.md`, arts. 5º, 6º e 9º e Anexo III), 06/2000 (`portaria-mpas-6211-2000-reajuste.md`), 06/2001 (`portaria-mpas-1987-2001-reajuste.md`) e 01/08/2006 (`portaria-mps-342-2006-reajuste.md`, com a Lei 11.430/2006, art. 3º): URL e sha256 do bruto em cada arquivo e em cada linha do JSON, percentuais conferidos contra o texto por `tests/test_dados_reajustes.py` (com isca). 01/08/2006 entrou como linha com `sobre_renda_de` (renda de março/2006), `substitui` (01/04/2006) e `dib_ate` (31/03/2006), aplicada pelos dois motores. Restam: 05/1995 e 05/1996 (sem texto) e a trava dos motores para DIB anterior a 2004 (compensação do mínimo não modelada). O histórico abaixo fica como registro da 2.0.0.

- **reajustes de 1995 a 2001 (05/1995, 05/1996 e 06/1997 a 06/2001)** — páginas das portarias localizadas no fac-símile do DOU (09/05/1995 p. 18; 15/05/1996 p. 57; 06/06/1997 p. 53; 05/06/1998 pp. 61-62; 10/05/1999 p. 44; 26/05/2000 pp. 27-28; 05/06/2001 pp. 51-52), mas são imagens digitalizadas: o OCR perde linhas do Anexo e nenhum fator foi transcrito sem conferência; 1995 e 1996 somam duas parcelas (IPC-r/IGP-DI pro rata + aumento real) sem um percentual único por DIB. Os motores abrem a conta para DIB anterior a 2004 antes de consultar esta tabela
- **2006-08-01** — Portaria MPS 342/2006 (DOU 17/08/2006, p. 38), art. 1º, e MP 316/2006, art. 4º: 5,01% sobre a renda de março/2006, substituindo o 5,00% de 01/04/2006 — não é um fator sobre a renda vigente em julho/2006; a linha (renda × fator) não o representa sem derivar um percentual que a norma não traz. Renda aberta a partir dessa data
- **2004-02-01, 2011-03-01, 2020-02-01 e 2023-05-01** — mudança do teto (EC 41/2003) ou do salário mínimo sem reajuste dos benefícios acima do mínimo; nenhuma norma fixa fator para essas datas e a tabela não traz linha para elas. Nos motores (so_piso_e_teto em calc_previdenciario_rmi.py e calc_previdenciario_valor_causa.py), data assim, num ano cujo reajuste anual está capturado em outra linha, não pede fator: a renda se mantém e valem o piso e o teto da competência (Lei 8.213, art. 41-A e art. 33). As quatro datas caem em anos com linha (2004-05-01, 2011-01-01, 2020-01-01 e 2023-01-01); a conta só abre se faltar a linha do ano (decisão do motor, fora desta tabela)
- **reajuste de 2027 em diante** — portaria de 2027 não capturada

