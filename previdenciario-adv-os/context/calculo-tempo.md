# Conta aberta — tempo de contribuição: comum, especial convertido e concomitância

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_tempo.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_tempo.py` · **Tabela:** `scripts/data/conversao-especial.json` · **Skills que leem:** `analise-ppp-ltcat-aposentadoria-especial`, `calculos-previdenciarios`, `planejamento-previdenciario`; a saída alimenta `context/calculo-transicao.md`.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 2).

---

## 1. Fórmulas, com a fonte de cada termo

O tempo é contado em **três fatias**, porque a regra muda em 13/11/2019:

| Fatia | Conta | Conversão de especial | Fonte |
|---|---|---|---|
| **F1** — até 13/11/2019 | dias de data a data, **inclusivos** (o dia de início e o de fim contam) | sim: dias × multiplicador | `context/lei/in-128-2022-inss.md`, art. 206, §§1º e 3º; `ec-103-2019.md`, art. 25, §2º |
| **F2** — competência 11/2019 | integral: 30 dias; os dias 01 a 13/11 já estão em F1, então **acrescem 17 dias** se o mês foi trabalhado inteiro | não | IN 128, art. 206, §§2º e 4º; art. 207, parágrafo único |
| **F3** — de 12/2019 em diante | cada competência com salário de contribuição **igual ou superior ao mínimo** vale 1 mês, qualquer que seja o número de dias trabalhados; abaixo do mínimo, fora | não | IN 128, art. 206, caput e §2º |

```
F1_bruto      = soma dos dias da UNIÃO dos períodos até 13/11/2019 (dia sobreposto conta uma vez)
F1_convertido = Σ dias_comuns × 1  +  Σ dias_especiais × multiplicador(atividade, sexo)
F2            = 17 dias, sem conversão (só com a competência 11/2019 trabalhada inteira)
F3            = N competências válidas desde 12/2019 (12 competências = 1 ano)
```

**Multiplicadores** (conversão de especial em comum; `context/lei/decreto-3048-art188p-tabela.md`, Decreto 3.048, art. 188-P, §5º; só para trabalho até 13/11/2019):

| Atividade especial de | Mulher | Homem |
|---|---|---|
| 15 anos | 2,00 | 2,33 |
| 20 anos | 1,50 | 1,75 |
| 25 anos | 1,20 | 1,40 |

**Concomitância.** Dois vínculos no mesmo dia: o dia conta **uma vez** (o tempo é período, IN 128, art. 206). Comum concomitante com especial comprovado: o dia conta **como especial** (IN 128, art. 265). A soma dos salários das atividades concomitantes é assunto do salário de benefício (Lei 8.213, art. 32), não do tempo.

**Representação em anos, meses e dias** (IN 128, art. 207, parágrafo único: mês de 30 dias, ano de 365 dias, composto pelos 12 meses):

```
anos  = parte inteira de (dias ÷ 365)
resto = dias − anos × 365
meses = parte inteira de (resto ÷ 30)
dias  = resto − meses × 30          (fração de dia mantida até o fim, sem arredondar)
```

O ano de 365,25 dias não tem fonte e não é usado.

---

## 2. Passos para o advogado preencher

| # | Passo | Onde achar o dado | Resultado |
|---|---|---|---|
| 1 | Listar os períodos com início, fim, tipo (comum ou especial de 15/20/25) e fonte (CNIS, CTPS, sentença, PPP) | CNIS, CTPS, PPP/LTCAT | ____ |
| 2 | Fazer a união dos períodos; nos dias sobrepostos de comum com especial, contar como especial | linha do tempo | ____ |
| 3 | F1: dias até 13/11/2019 por tipo | contagem inclusiva | comum ____ / especial ____ |
| 4 | Converter os dias especiais de F1 pelo multiplicador da tabela | seção 1 | ____ |
| 5 | F2: a competência 11/2019 foi trabalhada inteira? Se sim, +17 dias; se só em parte, parar (seção 3) | CNIS | ____ |
| 6 | F3: contar as competências desde 12/2019 com salário de contribuição ≥ mínimo | CNIS | ____ |
| 7 | Representar em anos, meses e dias (365/30) e registrar qual normalização foi usada na soma de F1 + F2 com F3 | seção 3 | ____ |
| 8 | Marcar no texto "conta não conferida por script" | — | — |

---

## 3. Leituras que mudam o resultado (M1 e o ponto aberto da normalização)

- **M1 — convenção do produto.** Data a data até 13/11/2019; competência 11/2019 integral; competências integrais desde 12/2019; representação em 365/30. A leitura civil pura (data a data também depois da EC) sai **só como sensibilidade**, quando muda o resultado, e nunca como saída.
- **Normalização da soma de F1 + F2 (dias) com F3 (competências) — ponto aberto.** A re-revisão especialista de 14/10/2026 deixou indeterminado como juntar as duas unidades. Há duas operações:
  1. **somar em anos, meses e dias**: F3 vira anos e meses (12 competências = 1 ano = 365 dias; o resto, meses de 30) e é somado com carga de 30 dias = 1 mês e 12 meses = 1 ano;
  2. **converter F3 direto em dias**: N × 30.
  Exemplo: 13 competências valem 395 dias na operação 1 e 390 na operação 2. O script devolve **as duas**, com `[VERIFICAR]`, e guarda dias de F1/F2 e competências de F3 separados na memória; quando os totais diferem, sai em **exit 3** com as duas contas em `formula_aberta`, sem escolher (a IN 128, art. 207, parágrafo único, fixa o mês de 30 e o ano de 365 dias, mas não a operação); quando coincidem (ex.: 11 competências, 330 dias nas duas), exit 0. Este script não julga requisito: se a diferença muda o cumprimento de uma regra, quem decide é o de transições (`context/calculo-transicao.md`). Quando todo o tempo é anterior a 13/11/2019 (só F1), o ponto não existe.
- **Competência 11/2019 trabalhada só em parte.** A IN 128 não diz como juntar a contagem data a data até 13/11 com a competência integral nesse caso: exit 3 com as duas contas (dias trabalhados de 14 a 30/11 × competência inteira).
- **Frações (M2).** Fração de dia fica na memória até o fim; "10 anos × 1,4 = 14 anos" não é saída.

---

## 4. Caso resolvido à mão — TEMPO-04 (dados inventados)

Caso de referência TEMPO-04, "confere" na re-revisão especialista de 14/10/2026; **pendente de conferência pelo advogado**. Todo o tempo é anterior a 13/11/2019 (só F1), então o ponto aberto da normalização não atua.

**Entrada:** homem; comum de 01/01/2010 a 31/12/2012; especial-25 reconhecido de 01/07/2012 a 30/06/2014.

| Passo | Conta | Fonte |
|---|---|---|
| sobreposição | 01/07/2012 a 31/12/2012 = **184 dias**, contados uma vez, como especial | IN 128, art. 265 |
| comum efetivo | 01/01/2010 a 30/06/2012 = 365 + 365 + 182 = **912 dias** | IN 128, art. 206, §1º |
| especial bruto | 01/07/2012 a 30/06/2014 = 365 + 365 = **730 dias** | IN 128, art. 206, §1º |
| conversão | 730 × 1,40 = **1.022 dias** | Decreto 3.048, art. 188-P, §5º; EC 103, art. 25, §2º |
| total | 912 + 1.022 = **1.934 dias** | — |
| representação | 1.934 − 5 × 365 = 109; 109 = 3 × 30 + 19 → **5a 3m 19d** | IN 128, art. 207, parágrafo único |

Saída esperada: `concomitancia = {dias: 184, contado_como: "especial-25", fundamento: "IN 128, art. 265"}`, `dias = 1934`, `tempo_total = 5a 3m 19d`. Errado seria somar os 184 dias duas vezes (comum + especial).

---

## 5. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags: `--entrada`, `--versao`. Convenções: `data` = `AAAA-MM-DD`; `competencia` = `AAAA-MM`; `decimal` = texto com ponto; campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → exit 2; chave iniciada por `_` é comentário.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `sexo` | enum | sim | `M` · `F` |
| `periodos` | lista | sim | ao menos 1 período |
| `periodos[].inicio` | data | sim | — |
| `periodos[].fim` | data | sim | — |
| `periodos[].tipo` | enum | sim | `comum` · `especial-15` · `especial-20` · `especial-25` |
| `periodos[].fonte` | enum | sim | `CNIS` · `CTPS` · `sentenca` · `PPP` |
| `periodos[].competencias_abaixo_do_minimo` | lista de competencia | não | só competências de 11/2019 em diante; padrão `[]` |
| `novembro_2019_integral` | bool | sim quando algum período abrange 13/11/2019 e continua depois; senão, ignorado | `false` leva a exit 3 (ponto aberto da seção 3) |

---

## 6. Saída e códigos

JSON com `fatias` (F1 com `dias`, `multiplicador` e `convertido_dias` por tipo; F2 com `dias_acrescidos`; F3 com `competencias`), `tempo_comum`, `tempo_especial_bruto`, `tempo_especial_convertido`, `tempo_total` (anos, meses, dias, e os dias de F1/F2 e as competências de F3 separados), `normalizacoes` (as duas operações da seção 3, quando há F3), `concomitancia`, `sensibilidade_civil` (só quando muda o resultado), `alertas`, `parametros_usados`, `regra`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado |
| 2 | entrada inválida |
| 3 | competência 11/2019 trabalhada só em parte (as duas contas); ou as duas normalizações da soma de F1 + F2 com F3 (seção 3) dão totais diferentes: a IN 128, art. 207, parágrafo único, fixa mês de 30 e ano de 365 dias, mas não decide a operação, e o script devolve as duas contas com `[VERIFICAR]` e `formula_aberta`, sem escolher; com totais iguais, exit 0 |

---

---

## Cobertura temporal do script (COBERTURA)

Fonte: `scripts/calc/calc_previdenciario_tempo.py`, constante `COBERTURA`.

**Regra:** fato (data indicada na coluna *chave*) fora do intervalo em que a linha é a regra vigente → o script **não fecha veredito pela regra posterior**: sai em **exit 3** com `formula_aberta`, a regra histórica e a fonte de cada borda, para o advogado refazer a conta. Borda sem fonte capturada em `context/lei/` fica no lado conservador (o primeiro dia certo). A tabela abaixo é a constante `COBERTURA` do script, transcrita na W3-integ-2 (18/10/2026); mudou o script, muda esta tabela.

Coluna *fora*: `aberta` = fora do intervalo, exit 3 com a regra histórica; `inexistente` = antes do intervalo a regra não existia e não se aplica (sem exit 3 por ela).

| Linha | Chave | Alcance | Desde | Até | Fora | Regra | Fonte das bordas | Antes do intervalo |
|---|---|---|---|---|---|---|---|---|
| `conversao-188P` | `der` | — | 30/06/2020 | — | aberta | multiplicadores do Decreto 3.048, art. 188-P, §5º (2,00/2,33; 1,50/1,75; 1,20/1,40), ao trabalho prestado até 13/11/2019 | desde: art. 188-P, §5º, incluído pelo Decreto 10.410, de 30/06/2020 (decreto-3048-art188p-tabela.md:74-78); até: art. 188-P, §5º, em vigor (sem nota de alteração) | requerimento anterior a 30/06/2020: multiplicadores do art. 70 do Decreto 3.048, revogado pelo Decreto 10.410/2020 (decreto-3048-1999.md:1677), texto não capturado em context/lei/ |
