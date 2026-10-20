# Conta aberta — direito adquirido, transições da EC 103 e regra permanente

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_transicao.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_transicao.py` · **Tabela:** `scripts/data/transicoes-ec103.json` · **Skills que leem:** `estrategia-de-caso-previdenciario`, `calculos-previdenciarios`, `peticao-inicial-previdenciaria`, `planejamento-previdenciario`. O tempo vem de `context/calculo-tempo.md` (mesma convenção); o valor, de `context/calculo-rmi.md`.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 3).

---

## 1. Quem pode usar qual regra

| Situação | Regras possíveis | Fonte |
|---|---|---|
| Filiado ao RGPS **até 13/11/2019** | direito adquirido (se cumpriu tudo até 13/11/2019), arts. 15, 16, 17, 18, 20, 21 e a permanente (art. 19) | `context/lei/ec-103-2019.md`, arts. 3º e 15 a 21 |
| Filiado **depois** de 13/11/2019 | só a permanente (art. 19) | `ec-103-2019.md`, art. 19 |
| Art. 17 | só quem tinha **mais de** 28 anos (M) / 33 anos (H) de contribuição em 13/11/2019; exatamente 28 ou 33 não basta | `ec-103-2019.md`, art. 17, caput |

## 2. Requisitos e valor de cada regra

| Regra | Requisitos | Valor | Fonte |
|---|---|---|---|
| Art. 15 — pontos | 30 (M) / 35 (H) anos de contribuição **e** idade + tempo, "incluídas as frações", de 86 (M) / 96 (H) em 2019, +1 ponto por ano desde 01/01/2020, até 100 (M) / 105 (H); idade e tempo "apurados em dias" | 60% + 2% | `ec-103-2019.md`, art. 15 (II, §§1º e 2º); art. 26, §2º, I |
| Art. 16 — idade progressiva | 30 (M) / 35 (H) anos **e** idade de 56 (M) / 61 (H) em 2019, +6 meses por ano desde 01/01/2020, até 62 (M) / 65 (H) | 60% + 2% | art. 16; art. 26, §2º |
| Art. 17 — pedágio de 50% | 30/35 anos **+ 50% do tempo que faltava** em 13/11/2019; sem idade mínima | média × **fator previdenciário** | art. 17 (II e parágrafo único) |
| Art. 18 — idade | 60 (M, +6 meses por ano desde 2020, até 62) / 65 (H) anos de idade; 15 anos de contribuição | 60% + 2% | art. 18; art. 26, §2º |
| Art. 19 — permanente | 62 (M) / 65 (H) anos de idade; 15 (M) / 20 (H) anos de contribuição | 60% + 2% | art. 19; art. 26, §2º, IV |
| Art. 20 — pedágio de 100% | idade 57 (M) / 60 (H); 30/35 anos **+ período adicional igual ao tempo que faltava** em 13/11/2019 | **100% da média** | art. 20 (I, II e IV); art. 26, §3º, I |
| Art. 21 — especial por pontos | 66 pontos e 15 anos de efetiva exposição; 76 e 20; 86 e 25; idade e tempo apurados em dias; os pontos não sobem com o ano | 60% + 2% (na especial de 15, acréscimo a partir de 15 anos) | art. 21 (caput e §1º); art. 26, §§2º e 5º |
| Direito adquirido | cumpriu os requisitos da regra anterior até 13/11/2019 | regra anterior: 80% maiores salários e fator, ou opção do art. 29-C sem fator (ver abaixo) | `ec-103-2019.md`, art. 3º; `lei-8213-1991.md`, arts. 29 e 29-C; `lei-9876-1999.md`, art. 3º; `in-128-2022-inss.md`, art. 229, §3º |

**Opção do art. 29-C no direito adquirido** (`lei-8213-1991.md`, art. 29-C): soma de idade e tempo em 13/11/2019 de **96 pontos (H) / 86 (M)** (95/85 do caput, +1 em 31/12/2018 pelo §2º, I), com tempo mínimo de 35 (H) / 30 (M) anos; as frações somam **em meses completos** (§1º). **Professor e professora** com tempo exclusivamente de magistério na educação infantil e nos ensinos fundamental e médio: tempo mínimo de **30 (H) / 25 (M)** anos **e cinco pontos acrescidos** à soma de idade e tempo (§3º). Cumprida a opção, a RMI é a média dos 80% maiores **sem fator**; não cumprida, média × fator.

**Aquisição anterior da opção** (`lei-8213-1991.md`, art. 29-C, §4º: "Ao segurado que alcançar o requisito necessário ao exercício da opção de que trata o caput e deixar de requerer aposentadoria será assegurado o direito à opção com a aplicação da pontuação exigida na data do cumprimento do requisito"). A pontuação de 13/11/2019 não é o único teste: quem completou, em data anterior, a pontuação **exigida naquela data** (com o tempo mínimo já cumprido) conserva a opção, ainda que em 13/11/2019 não some 96/86. Como idade e tempo só crescem, a conta se resolve em dois testes, e basta um:

```
teste A (13/11/2019):  pontos em meses completos >= 96 (H) / 86 (M), tempo >= 35 / 30
teste B (30/12/2018):  pontos em meses completos >= 95 (H) / 85 (M), tempo >= 35 / 30
                       (último dia antes da majoração de 31/12/2018, §2º, I)
professor e professora: tempo mínimo 30 / 25 e +5 pontos nos dois testes (§3º)
```

Exemplo (dados inventados): homem nascido em 30/12/1958, com 60 anos e exatamente 35 de contribuição em 30/12/2018, sem contribuição depois. Teste B: 60 + 35 = 95 → cumpre. Teste A: em 13/11/2019 tem 60 anos e 10 meses e 35 anos → 95 pontos e 10 meses, menos de 96 em meses completos → não cumpre. Resultado: **conserva a opção sem fator** pelo §4º. Exigir só os 96 pontos de 13/11/2019 eliminaria indevidamente a opção.

**Coeficiente** (`ec-103-2019.md`, art. 26): 60% + 2 pontos percentuais por ano de contribuição que passar de 20 (H) ou de 15 (M, §5º; e na especial de 15). **Sem teto de 100% no percentual** (M3): 102% é devido; o limite é monetário (teto do RGPS). Professor: arts. 15, §3º; 16, §2º; 19, §1º, II; 20, §1º (tempo exclusivamente em magistério na educação infantil e no ensino fundamental e médio).

**Tabela ano a ano** (aritmética direta dos §§ da EC 103; a mesma de `scripts/data/transicoes-ec103.json`):

| Ano | Art. 15 H | Art. 15 M | Art. 16 H | Art. 16 M | Art. 18 M |
|---|---|---|---|---|---|
| 2019 | 96 | 86 | 61 | 56 | 60 |
| 2020 | 97 | 87 | 61,5 | 56,5 | 60,5 |
| 2021 | 98 | 88 | 62 | 57 | 61 |
| 2022 | 99 | 89 | 62,5 | 57,5 | 61,5 |
| 2023 | 100 | 90 | 63 | 58 | 62 |
| 2024 | 101 | 91 | 63,5 | 58,5 | 62 |
| 2025 | 102 | 92 | 64 | 59 | 62 |
| 2026 | 103 | 93 | 64,5 | 59,5 | 62 |
| 2027 | 104 | 94 | 65 | 60 | 62 |
| 2028 | 105 | 95 | 65 | 60,5 | 62 |
| 2029 | 105 | 96 | 65 | 61 | 62 |
| 2030 | 105 | 97 | 65 | 61,5 | 62 |
| 2031 | 105 | 98 | 65 | 62 | 62 |
| 2032 | 105 | 99 | 65 | 62 | 62 |
| 2033 em diante | 105 | 100 | 65 | 62 | 62 |

Os arts. 17, 20 e 21 não têm acréscimo anual: os requisitos são os mesmos em qualquer ano.

## 3. Fórmulas dos pedágios e dos pontos

**Pedágio (arts. 17 e 20)** — a falta é medida em **uma só unidade**, dias pela regra de 365/30 (IN 128, art. 207, parágrafo único), antes de aplicar 50% ou 100%:

```
T13          = tempo em 13/11/2019, em dias, já convertido (fatia F1 de calculo-tempo)
T_exigido    = 30 × 365 = 10.950 dias (M)  |  35 × 365 = 12.775 dias (H)
falta        = T_exigido − T13                          (não trocar de unidade no meio da subtração)
art. 17:  exigido_depois = falta + 0,5 × falta           (fração preservada, M2)
art. 20:  exigido_depois = falta + falta = 2 × falta
acumulado    = 17 dias da competência 11/2019 (se trabalhada inteira) + competências desde 12/2019
cumpre na primeira competência em que acumulado ≥ exigido_depois, por inteiro (nunca arredondar para baixo)
```

Erro que esta conta evita: subtrair "30a − 29a 5m 8d" emprestando 360 dias de um ano. Com T13 = 10.743 dias, a falta é 10.950 − 10.743 = **207 dias**, não 202; o adicional de 50% é 103,5 dias; o exigido depois da EC no art. 20 é 414 dias. As competências desde 12/2019 entram no `acumulado` pelas duas normalizações de `context/calculo-tempo.md` (seção 3), e as duas saem na memória.

**Pontos (arts. 15 e 21)** — a EC manda apurar idade e tempo "em dias" e somar "incluídas as frações", mas não diz como a soma em dias vira pontos. Duas leituras:

```
Leitura B (regra do F1, M1; padrão do script): idade em dias corridos desde o nascimento (excluído o dia do
          nascimento) + tempo em dias (365/30) ≥ P × 365
Leitura A (exposta pelo script): idade civil em anos, meses e dias + tempo em anos, meses e dias (365/30),
          somados com 30 dias = 1 mês e 12 meses = 1 ano; cumpre quando a soma ≥ P anos
```

A re-revisão especialista de 14/10/2026 deixou indeterminada a **primeira data** dos pontos (as leituras podem dar dias diferentes). O script devolve as duas datas com `[VERIFICAR]`.

**Quando sai exit 3.** A conta inteira é refeita com a outra normalização das competências desde 12/2019 (`_sensibilidade_normalizacao` do script) e comparada à padrão em todos os valores: vereditos, datas em que cumpre, coeficientes, tempos, requisitos e contas abertas. **Qualquer diferença na projeção**, inclusive só na data em que cumpre, sai em exit 3 com as duas leituras em `formula_aberta.saida_depende_da_normalizacao` e `[VERIFICAR]`. Com menos de 12 competências até o horizonte as duas normalizações coincidem e nada muda. As convenções dos arts. 206 e 207 da IN 128 seguem declaradas como acima.

## 4. Passos para o advogado preencher

| # | Passo | Resultado |
|---|---|---|
| 1 | Data de filiação: até 13/11/2019? Se não, só o art. 19 | ____ |
| 2 | Tempo em 13/11/2019 (T13, em dias) e na DER, por `context/calculo-tempo.md` | ____ / ____ |
| 3 | Idade na DER (civil) e, para pontos, também em dias corridos | ____ |
| 4 | Direito adquirido em 13/11/2019? Opção do art. 29-C: teste A (96/86 pontos em 13/11/2019) **ou** teste B (95/85 pontos em 30/12/2018, §4º), em meses completos; professor: 30/25 anos e +5 pontos. Sem nenhum dos dois, valor por fórmula com fator | ____ |
| 5 | Para cada regra da seção 2: requisito exigido × valor do segurado; cumpre na DER? em que data/competência cumpre? | tabela por regra |
| 6 | Pedágios: falta em dias, adicional com a fração, acumulado depois da EC | ____ |
| 7 | Coeficiente de cada regra (sem teto de 100%); art. 17 e direito adquirido = fórmula com fator | ____ |
| 8 | Mais vantajosa: por coeficiente quando todas têm coeficiente; com art. 17 ou direito adquirido sem art. 29-C cumpridos, comparação aberta (sem a tábua do IBGE não há fator) | ____ |
| 9 | Marcar no texto "conta não conferida por script" | — |

## 5. Leituras e pontos que mudam o resultado

- **M1:** unidade única, dias. Tempo pela IN 128 (data a data até 13/11/2019; competências integrais desde 11/2019; 365/30); pontos com idade e tempo apurados em dias contra pontos × 365 (leitura B); leitura civil pura só como sensibilidade. O F1 diz que a soma em anos, meses e dias (leitura A) "não é a operação do texto"; o script a expõe só como sensibilidade (`leituras.datas` e `sensibilidade_leitura_A`, com `[VERIFICAR]`) e ela fica **fora do veredito**: a leitura A sozinha não muda `cumprida_na_der` nem leva a exit 3. O exit 3 por leitura vem só da divergência entre as normalizações da leitura B (padrão × 30 dias por competência) ou de requisito indeterminado.
- **M2:** adicional do pedágio com a fração, cumprido só por inteiro.
- **M3:** coeficiente acima de 100% é devido; o teto é monetário.
- **M7:** sem a tábua do IBGE não há fator previdenciário numérico: art. 17 e direito adquirido sem a opção do art. 29-C saem como fórmula e lista de dados faltantes. **Se uma regra que depende do fator está cumprida na DER, o script devolve exit 3** (`formula_aberta.fator_previdenciario`, com as regras e o que falta), porque a comparação entre as regras fica aberta; o direito adquirido que cumpre o art. 29-C não depende do fator e não leva a exit 3; no direito adquirido, idade, expectativa e tempo na data da publicação da EC 103 (`in-128-2022-inss.md`, art. 229, §3º). A fórmula do fator é imagem na fonte (`lei-9876-1999.md`, Anexo) e não é reproduzida aqui.

## 6. Caso resolvido à mão — TRANS-03 (dados inventados)

Caso de referência TRANS-03, "confere" na re-revisão especialista de 14/10/2026, **na projeção das premissas e das regras atuais**; **pendente de conferência pelo advogado**.

**Entrada:** homem nascido em 01/03/1961; empregado; primeira contribuição em 01/03/2020; vínculo contínuo com salário de contribuição igual ou superior ao mínimo em todas as competências (premissa expressa).

| Passo | Conta | Fonte |
|---|---|---|
| filiação | 01/03/2020, depois de 13/11/2019 → arts. 15 a 18, 20 e 21 inaplicáveis | EC 103, arts. 15 a 21 |
| idade | 65 anos em **01/03/2026** | art. 19 |
| tempo | 20 anos = 240 competências: 03/2020 a 02/2040 → 20 anos **na competência 02/2040** | IN 128, art. 206, caput e §2º |
| primeira DER | o tempo conta "até a competência do requerimento" e cada competência vale inteira; a contribuição do empregado é presumida → requerimento a partir de **01/02/2040** | IN 128, art. 206, caput, §§2º e 6º |
| coeficiente | 20 anos, nenhum acima de 20 → **60%** | EC 103, art. 26, §2º, IV |
| sensibilidade civil | data a data, os 20 anos fechariam em 29/02/2040 (não é saída) | — |

Saída esperada: todas as transições `aplicavel = false`; `art19.competencia_em_que_cumpre = 2040-02`; `art19.primeira_der = 2040-02-01`; `coeficiente = 0.60`. Não garante legislação futura nem presume remuneração mínima não comprovada.

Armadilhas da mesma conta ("confere"): **TR-A** — mulher com exatamente 28 anos em 13/11/2019: 28 > 28 é falso → art. 17 inaplicável. **TR-B** — mulher, art. 15 cumprido, 36 anos completos, média R$ 4.000,00: 60% + 2% × 21 = 102% → **R$ 4.080,00**, não R$ 4.000,00.

## 7. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags: `--entrada`, `--versao`. Convenções: `data` = `AAAA-MM-DD`; `competencia` = `AAAA-MM`; `decimal` = texto com ponto; campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → exit 2; chave iniciada por `_` é comentário.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `nascimento` | data | sim | — |
| `sexo` | enum | sim | `M` · `F` |
| `data_filiacao` | data | sim | primeira filiação ao RGPS |
| `der` | data | sim | data em que se verifica cada regra |
| `periodos` | lista | sim | mesmo formato e mesmos sub-campos de `context/calculo-tempo.md` (`inicio`, `fim`, `tipo`, `fonte`, `competencias_abaixo_do_minimo`) |
| `novembro_2019_integral` | bool | sim quando algum período abrange 13/11/2019 e continua depois | `false` leva a exit 3 |
| `professor` | bool | não | padrão `false`; `true` declara que todo o tempo informado é de magistério exclusivo (arts. 15, §3º; 16, §2º; 19, §1º, II; 20, §1º), com `[VERIFICAR]` |
| `projecao_continua` | bool | não | padrão `false`; `true` projeta competências mensais válidas depois do último período para achar `data_em_que_cumpre` (premissa expressa na saída) |
| `projecao_ate` | data | sim quando `projecao_continua = true` | limite da projeção |

## 8. Saída e códigos

Uma linha por regra: `regra` (`adquirido-tc`, `adquirido-idade`, `art15` … `art21`), `aplicavel`, `cumprida_na_der`, `data_em_que_cumpre` ou `competencia_em_que_cumpre`, `requisitos` (exigido × segurado), `coeficiente` ou `"media x fator"`, `fundamento`; mais `leituras` (A e B dos pontos; normalizações do pedágio), `sensibilidade_civil`, `mais_vantajosa` (ou comparação aberta), `alertas`, `parametros_usados`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado; com menos de 12 competências desde 12/2019 até o horizonte as duas normalizações coincidem |
| 2 | entrada inválida |
| 3 | veredito na DER muda conforme a leitura ou a normalização, ou qualquer valor da projeção, inclusive só a data em que cumpre, muda com a normalização das competências desde 12/2019 (seção 3); competência 11/2019 trabalhada em parte; **regra cumprida na DER que depende do fator previdenciário** (art. 17; direito adquirido sem art. 29-C), porque sem a tábua do IBGE não há número |

---

---

## Cobertura temporal do script (COBERTURA)

Fonte: `scripts/calc/calc_previdenciario_transicao.py`, constante `COBERTURA`.

**Regra:** fato (data indicada na coluna *chave*) fora do intervalo em que a linha é a regra vigente → o script **não fecha veredito pela regra posterior**: sai em **exit 3** com `formula_aberta`, a regra histórica e a fonte de cada borda, para o advogado refazer a conta. Borda sem fonte capturada em `context/lei/` fica no lado conservador (o primeiro dia certo). A tabela abaixo é a constante `COBERTURA` do script, transcrita na W3-integ-2 (18/10/2026); mudou o script, muda esta tabela.

Coluna *fora*: `aberta` = fora do intervalo, exit 3 com a regra histórica; `inexistente` = antes do intervalo a regra não existia e não se aplica (sem exit 3 por ela).

| Linha | Chave | Alcance | Desde | Até | Fora | Regra | Fonte das bordas | Antes do intervalo |
|---|---|---|---|---|---|---|---|---|
| `ec103` | `der` | `art15` · `art16` · `art17` · `art18` · `art19` · `art19-professor` · `art19-especial` · `art20` · `art21` | 13/11/2019 | — | inexistente | — | desde: EC 103, art. 36, III (vigência na publicação; ec-103-2019.md:705); publicada em 13/11/2019 (IN 128, art. 249, §1º, in-128-2022-inss.md:2307); até: sem nota de alteração ou revogação dos arts. 15 a 21 em ec-103-2019.md | antes de 13/11/2019 a regra não existia: vale o direito adquirido (linhas adquirido-*) |
| `adquirido-tempo` | `data_da_apuracao` | `adquirido-tc` · `adquirido-proporcional-ec20` | 16/12/1998 | 13/11/2019 | aberta | — | desde: EC 20/1998, de 15/12/1998 (ec-20-1998.md:18): 35/30 anos (CF, art. 201, §7º, I) e proporcional do art. 9º; publicada e vigente em 16/12/1998 (IN 128, art. 5º, IV: "16 de dezembro de 1998, data da publicação e vigência da Emenda Constitucional nº 20"; in-128-2022-inss.md:53); até: EC 103, art. 3º (direito adquirido até a entrada em vigor) | aposentadoria por tempo de serviço da Lei 8.213, arts. 52 e 53 (25 anos M / 30 H, 70% + 6% por ano até 100% aos 30/35; lei-8213-1991.md:1279-1285), com o salário de benefício do art. 29 na redação original (média dos últimos 36 salários em até 48 meses; lei-8213-1991.md:801) |
| `adquirido-rmi-lei-9876` | `data_da_apuracao` | `adquirido-tc` · `adquirido-proporcional-ec20` | 29/11/1999 | 13/11/2019 | aberta | — | desde: Lei 9.876/1999: art. 29 da Lei 8.213 na redação dela (média e fator; lei-8213-1991.md:803), DOU de 29.11.1999 (lei-9876-1999.md:337); até: EC 103, art. 3º | de 16/12/1998 a 28/11/1999: salário de benefício do art. 29 da Lei 8.213 na redação original (média dos últimos 36 salários em até 48 meses, sem fator previdenciário; lei-8213-1991.md:801) |
| `adquirido-carencia-142` | `data_da_apuracao` | `adquirido-tc` · `adquirido-idade` · `adquirido-proporcional-ec20` · `adquirido-especial` | 29/04/1995 | 13/11/2019 | aberta | — | desde: Lei 8.213, art. 142, redação da Lei 9.032/1995 ("ano em que o segurado implementou todas as condições"; lei-8213-1991.md:2843), publicada em 29/04/1995 (IN 128, art. 261, I, in-128-2022-inss.md:2411); até: EC 103, art. 3º | de 25/07/1991 a 28/04/1995: art. 142 na redação original, tabela pelo ano da entrada do requerimento (lei-8213-1991.md:2786-2841); antes, regime anterior à Lei 8.213 (CLPS, não capturada) |
| `conversao-188P` | `der` | `adquirido-tc` · `adquirido-proporcional-ec20` · `art15` · `art16` · `art17` · `art18` · `art19` · `art19-professor` · `art20` | 30/06/2020 | — | aberta | — | desde: art. 188-P, §5º, incluído pelo Decreto 10.410, de 30/06/2020 (decreto-3048-art188p-tabela.md:74-78); até: art. 188-P, §5º, em vigor (sem nota de alteração) | requerimento anterior a 30/06/2020: multiplicadores do art. 70 do Decreto 3.048, revogado pelo Decreto 10.410/2020 (decreto-3048-1999.md:1677), texto não capturado em context/lei/ |
| `art29C` | `data_da_apuracao` | `adquirido-tc` | 01/01/2016 | 13/11/2019 | aberta | — | desde: art. 29-C incluído pela MP 676/2015 e pela Lei 13.183/2015 (lei-8213-1991.md:869-889); dia de vigência não datado em context/lei/: o primeiro dia certo é 01/01/2016; até: EC 103, art. 3º | sem a opção do art. 29-C: média × fator previdenciário (Lei 8.213, art. 29, I) |
