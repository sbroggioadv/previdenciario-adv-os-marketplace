# Conta aberta — CNIS: carência, qualidade de segurado e indicadores

> **Aviso fixo: conta não conferida por script.** Este arquivo é a conta que o advogado faz à mão quando o script `scripts/calc/calc_previdenciario_cnis.py` não roda (sem Python), devolve exit 3 ou recebe dado fora das tabelas. Todo número tirado daqui sai na peça com a marca "conta não conferida por script" e passa pela conferência do advogado antes do protocolo.
>
> **Script:** `scripts/calc/calc_previdenciario_cnis.py` · **Tabelas:** `scripts/data/indicadores-cnis.json`; feriados nacionais do motor de prazos (só para o dia útil do vencimento) · **Skills que leem:** `analise-cnis`, `triagem-dogmatica-previdenciario`, `administrativo-inss-crps`.
> **Lei:** todo dispositivo citado abaixo está em `context/lei/` (mapa em `context/lei/INDICE.md`, script 1). O texto que vale é o do arquivo da lei, não o resumo daqui.

---

## 1. Fórmulas, com a fonte de cada termo

### 1.1 Carência

| Termo | Conta | Fonte |
|---|---|---|
| `exigidas` | 12 para auxílio por incapacidade temporária e aposentadoria por incapacidade permanente; 180 para aposentadoria por idade, por tempo e especial; 24 para auxílio-reclusão | `context/lei/lei-8213-1991.md`, art. 25, I, II e IV |
| dispensa | 0 para pensão, auxílio-acidente e salário-família; incapacidade por acidente de qualquer natureza ou por doença da lista **só quando o advogado marca** `acidente_ou_doenca_dispensa` (a lista vigente não está no corpus) | `lei-8213-1991.md`, art. 26 (I e II) e art. 151 |
| salário-maternidade | sem carência (o inciso III do art. 25 continua no texto, mas foi julgado inconstitucional) | `lei-8213-1991.md`, art. 25, III; `temas-sumulas-prev.md`, ADI 2.110 |
| BPC | assistencial: sem carência e **sem exigir vínculo nem qualidade de segurado** (a entrada do BPC pode vir sem nenhum vínculo) | `lei-8742-1993-loas.md`, art. 20 |
| `contadas` | número de competências válidas: dentro de um vínculo, com contribuição, apuradas pelas linhas abaixo | `lei-8213-1991.md`, art. 24 |
| indicador do CNIS | o efeito na carência é o que os **esclarecimentos da sigla** no Anexo V dizem, sigla por sigla; o tipo `CsPendencia` **sozinho não exclui** a competência (várias siglas desse tipo tratam de ajuste entre competências da EC 103, como `PDESFAZ-AJ-EC103` e `PMOV-INCONSIST`). Sigla cujo esclarecimento não fecha o efeito na carência: competência **incerta**, listada em `excluidas` com `[VERIFICAR]`; se ela decide o veredito, `indeterminada` (exit 3). A presunção de regularidade do recolhimento em atraso sem indicador (IN 128, art. 185, §3º) vale para a **qualidade** (seção 1.2), não para a carência: o atraso na carência segue as linhas "atraso (carência)" e "recolhimento depois do fato gerador" | `portaria-990-2022-anexo-v-indicadores-cnis.md` |
| recolhimento depois do fato gerador | não conta para a carência, ainda que de competência anterior; exceção: a competência do próprio fato gerador paga até o vencimento | `in-128-2022-inss.md`, art. 189, §§4º e 5º |
| contribuição mínima | desde 14/11/2019, a competência abaixo do salário mínimo só conta se complementada, agrupada ou com excedente utilizado (ajustes da EC 103, art. 29); empregado, doméstico e avulso com atividade iniciada antes de 14/11/2019 contam as competências até 11/2019 mesmo abaixo do mínimo; contribuinte individual, facultativo e especial que recolhe facultativamente, só com salário de contribuição de ao menos um mínimo, em qualquer época. Abaixo do mínimo sem ajuste informado: competência **incerta** com `[VERIFICAR]` (o ajuste ainda é possível); sem o mínimo da competência na tabela, idem | `in-128-2022-inss.md`, art. 189, caput e §§7º a 9º; `ec-103-2019.md`, art. 29 |
| atraso (carência) | contribuinte individual, especial e facultativo: só contam as competências a partir do **primeiro pagamento sem atraso**; as atrasadas de competências anteriores ficam fora | `lei-8213-1991.md`, art. 27, II |
| `cumprida` | `sim` se `contadas ≥ exigidas`; senão `nao` | `lei-8213-1991.md`, arts. 24 e 25 |

**Depois da perda da qualidade** (só para auxílio por incapacidade temporária, aposentadoria por incapacidade permanente, salário-maternidade e auxílio-reclusão, que são os benefícios que o art. 27-A nomeia):

```
metade_exigida = exigidas / 2                       (Lei 8.213, art. 27-A: metade dos incisos I, III e IV do art. 25)
novas          = competências válidas que começam a valer na nova filiação ou depois, pela DATA EFETIVA:
                 o dia do ingresso, se o vínculo começa no meio do mês (não o 1º dia da competência);
                 no atraso, a data do recolhimento
anteriores     = competências válidas antes da perda

novas <  metade_exigida                -> contadas = novas
novas >= metade_exigida                -> contadas = novas + anteriores
cumprida = "sim"  se novas >= metade_exigida  E  novas + anteriores >= exigidas
cumprida = "indeterminada" se o histórico anterior à perda não foi informado e novas < exigidas
```

A refiliação é a primeira contribuição posterior à perda, pela data efetiva: um vínculo iniciado no mês da perda, mas depois do dia dela, é refiliação; o que começa antes do dia da perda continua a cadeia anterior.

Fonte: `lei-8213-1991.md`, art. 27-A; `decreto-3048-1999.md`, art. 27-A ("as contribuições anteriores à perda somente serão computadas para fins de carência depois que o segurado contar [...] com metade"). A metade **não substitui** a carência: ela só reabre o cômputo das anteriores; a carência total continua a do art. 25.

### 1.2 Qualidade de segurado

**Carência e qualidade são apuradas em separado.** Nunca usar a lista filtrada da carência para medir a qualidade.

**Recolhimento em atraso e qualidade — a quem se aplica** (`in-128-2022-inss.md`, art. 185):

| Categoria | Atraso conta para a qualidade? | Marco | Fonte |
|---|---|---|---|
| contribuinte individual (inclusive MEI), facultativo e segurado especial que contribui facultativamente | sim, se pago **antes do fato gerador** | a **data do recolhimento**, não a competência | art. 185, caput, §§1º e 6º |
| os mesmos, com recolhimento feito **depois da perda** da qualidade | sim, **exceto o facultativo** | data do recolhimento | art. 185, §2º |
| **contribuinte individual prestador de serviço**, períodos de **atividade comprovada a partir da competência 04/2003** | **não se aplica a regra do caput** (§5º): o recolhimento tardio não cria novo evento na data do pagamento | a **competência** da atividade comprovada (a contribuição é a descontada pela empresa: MP 83/2002, Lei 10.666/2003, citadas no próprio §5º e no art. 189, §1º; a Lei 10.666 não está capturada) | art. 185, §5º |
| empregado, doméstico e avulso | fora do art. 185 (o §1º não os lista) | a competência do vínculo; recolhimento presumido (doméstico desde 06/2015) | art. 189, §§1º e 2º |
| competência do próprio fato gerador | conta se paga dentro do vencimento | a competência | art. 185, §7º |

Recolhimento em atraso que está no CNIS **sem** indicador de pendência presume-se regular **para esta finalidade** (qualidade), "na forma do art. 19 do RPS" (art. 185, §3º, que se refere ao caput). Não é fundamento para a carência: lá valem a Lei 8.213, art. 27, II, e a IN 128, art. 189 (tabela 1.1). Recolhimentos a título de complementação não caracterizam atraso (art. 185, §4º).

Exemplo (dados inventados): prestador de serviço a empresa com atividade comprovada em 01/2020 e recolhimento tardio dessa competência em 01/2026. Pelo §5º, o evento da qualidade é 01/2020, não 01/2026; usar a data do pagamento deslocaria a graça em seis anos. Os CAMPOS do script não distinguem o CI prestador de serviço (`origem = contribuinte-individual` cobre os dois): nesse caso, a qualidade é conta do advogado (seção 7).

**Hipóteses do art. 15 além da graça por cessação de contribuições** (`lei-8213-1991.md`, art. 15):

| Hipótese | Mantém a qualidade | Inciso |
|---|---|---|
| em gozo de benefício, **exceto auxílio-acidente** | sem limite de prazo, enquanto durar o benefício; a graça do inciso II começa depois da cessação | I |
| depois de cessar contribuições (regra geral) | 12 meses (+12, +12: §§1º e 2º) | II |
| doença de segregação compulsória | até 12 meses após cessar a segregação | III |
| retido ou recluso | até 12 meses após o livramento | IV |
| incorporado às Forças Armadas | até 3 meses após o licenciamento | V |
| facultativo | 6 meses após a cessação das contribuições | VI |

A conta abaixo é a do inciso II (e VI). Se o caso tem benefício em manutenção (inciso I) ou uma das hipóteses III a V, o marco inicial é outro e entra na conta do advogado; os CAMPOS do script não têm campo para elas (ver seção 7).

```
C  = último evento da QUALIDADE (não da lista da carência): a última competência com contribuição
     (ou a de cessação do vínculo) ou, no atraso pago antes do fato gerador, o mês do recolhimento,
     SÓ para CI, facultativo e especial que contribui facultativamente (art. 185, §1º; facultativo
     não depois da perda, §2º); NUNCA para o CI prestador de serviço em atividade comprovada
     desde 04/2003 (art. 185, §5º: vale a competência) nem para empregado, doméstico e avulso
G  = 12 meses                                  (art. 15, II)
   + 12 se houver MAIS DE 120 contribuições sem perda da qualidade   (art. 15, §1º; na primeira aquisição,
        exatamente 120 não estende)
        reaquisição: se a prorrogação já foi adquirida em bloco anterior e a qualidade se perdeu, ela volta
        com 120 NOVAS contribuições sem perda (IN 128, art. 184, §4º, segunda parte: "somente será devida
        em outra oportunidade quando o segurado completar 120 (cento e vinte) novas contribuições mensais
        sem perda da qualidade de segurado"); adquirida uma vez, toda oportunidade seguinte pede 120 novas.
        O bloco que adquiriu é o que somou as contribuições exigidas na sua própria oportunidade (mais de 120
        na primeira; 120 novas depois). A graça maior também decide se o ingresso seguinte ainda está dentro
        do mesmo bloco sem perda.
   + 12 se houver desemprego registrado        (art. 15, §2º)
   facultativo: G = 6                          (art. 15, VI)
fim_da_graca      = último dia da competência C + G
competencia_seg   = competência seguinte a fim_da_graca
vencimento        = dia 15 do mês seguinte a competencia_seg          (Lei 8.212, art. 30, II)
                    sem expediente bancário no dia 15 -> dia útil imediatamente posterior (Lei 8.212, art. 30, §2º, I)
data_perda        = vencimento + 1 dia                                (Decreto 3.048, art. 14; Lei 8.213, art. 15, §4º)
```

Fontes: `lei-8213-1991.md`, art. 15 (II, VI, §§1º, 2º e 4º); `decreto-3048-1999.md`, art. 14; `lei-8212-1991.md`, art. 30 (II e §2º, I). Sem o calendário bancário do caso, o script usa os feriados nacionais do motor de prazos e avisa que feriado local não foi considerado.

### 1.3 Indicadores

Cada sigla é procurada no Anexo V (`context/lei/portaria-990-2022-anexo-v-indicadores-cnis.md`) e sai com a descrição oficial e o tipo. **IEAN** = "Exposição a agente nocivo informada pelo empregador, passível de comprovação": efeito "possível enquadramento especial; exige PPP/LTCAT; sem conversão automática" (`lei-8213-1991.md`, art. 57, §§3º e 4º). Sigla que não está no Anexo V sai como "sigla não localizada no Anexo V", nunca com descrição de memória. Os sufixos 15/20/25 do IEAN não têm âncora no Anexo V: não automatizar.

---

## 2. Passos para o advogado preencher

| # | Passo | Onde achar o dado | Resultado |
|---|---|---|---|
| 1 | Benefício pretendido e data de referência (DER, DII ou óbito) | requerimento, laudo, certidão | ____ / ____ |
| 2 | Carência exigida (art. 25) ou dispensa (art. 26) | tabela 1.1 | ____ |
| 3 | Listar os vínculos do CNIS com início, fim e categoria | CNIS | ____ |
| 4 | Contar as competências válidas: efeito de cada indicador pelos esclarecimentos da sigla no Anexo V; tirar as recolhidas depois do fato gerador (salvo a do mês do fato gerador em dia); conferir a contribuição mínima; para CI/especial/facultativo, tirar as pagas em atraso antes do primeiro pagamento em dia (que seguem contando para a qualidade pela data do pagamento, salvo o CI prestador de serviço desde 04/2003: seção 1.2) | CNIS, guias | ____ |
| 5 | Houve perda da qualidade antes da data de referência? Se sim, separar `anteriores` e `novas` | passo 8 aplicado à época | ____ / ____ |
| 6 | Benefício do art. 27-A? Aplicar a regra da metade (seção 1.1) | — | ____ |
| 7 | Carência cumprida? | — | sim / não / indeterminada |
| 8 | Qualidade: benefício em manutenção ou hipótese do art. 15, III a V? Senão, último evento (competência ou data do recolhimento em atraso), graça (12/24/+12; 6 facultativo), vencimento, data da perda | seção 1.2 | ____ |
| 9 | Indicadores: conferir cada sigla no Anexo V | Anexo V | ____ |
| 10 | Marcar no texto "conta não conferida por script" | — | — |

---

## 3. Leituras e pontos que mudam o resultado

- **P2 (vencimento sem expediente bancário):** dia útil seguinte; a perda é no dia seguinte a esse vencimento. Sem calendário confiável, a data sai com alerta.
- **Atraso: carência × tempo.** Para carência vale o art. 27, II, da Lei 8.213; para **tempo** vale a IN 128, art. 208 (atraso conta se pago antes do fato gerador, salvo o facultativo depois da perda e o CI prestador a pessoa jurídica desde 04/2003). Nunca usar a contagem do tempo para a carência. Para a **qualidade** vale o art. 185 da IN 128, com a mesma exceção do CI prestador de serviço desde 04/2003 (§5º; seção 1.2).
- **Perda da qualidade nas aposentadorias (art. 25, II).** O art. 27-A não alcança aposentadoria por idade, por tempo nem especial. A regra da perda nessas espécies não está em `context/lei/`: o script devolve as competências válidas, mas `cumprida` sai `indeterminada` (exit 3) com `[VERIFICAR]`, e o advogado decide.
- **Competência abaixo do salário mínimo:** regra na tabela 1.1 (IN 128, art. 189, §§7º a 9º). Como o ajuste da EC 103, art. 29, ainda pode ser feito, a competência abaixo do mínimo sem ajuste informado sai em `excluidas` como incerta, com `[VERIFICAR]`; não entra por presunção e, se decide o veredito, a carência fica `indeterminada` (exit 3).
- **Indicador de pendência:** o efeito vem dos esclarecimentos da sigla (tabela 1.1), não do tipo `CsPendencia`.

---

## 4. Caso resolvido à mão — CNIS-04 (dados inventados)

Caso de referência CNIS-04, conferido aritmeticamente ("confere") na re-revisão especialista de 14/10/2026; **pendente de conferência pelo advogado**.

**Entrada:** segurado perdeu a qualidade em 2022; nova filiação em 01/2025; 7 contribuições de 01/2025 a 07/2025; benefício incapacidade, sem dispensa de carência. Histórico anterior à perda: (a) 4 contribuições; (b) 6; (c) não informado.

| Passo | Conta | Fonte |
|---|---|---|
| carência integral | 12 | Lei 8.213, art. 25, I |
| metade | 12 ÷ 2 = 6 | art. 27-A |
| novas | 7 ≥ 6 → as anteriores voltam a contar | art. 27-A; Decreto 3.048, art. 27-A |
| (a) | 4 + 7 = **11** < 12 → `cumprida = "nao"`, falta 1 | art. 25, I |
| (b) | 6 + 7 = **13** ≥ 12 → `cumprida = "sim"` | art. 25, I |
| (c) | só as 7 novas são certas; 7 < 12 → `cumprida = "indeterminada"`, exit 3, alerta "informe o CNIS anterior à perda da qualidade" | não presumir histórico |

Segundo caso, para a qualidade de segurado — armadilha C-A (também "confere"): empregado, última competência 05/2024, **exatamente 120** contribuições, sem desemprego registrado. Sem prorrogação adquirida em bloco anterior (primeira aquisição), 120 não é "mais de 120" → G = 12; fim da graça 05/2025; competência seguinte 06/2025; vencimento 15/07/2025 (terça-feira, dia útil); **perda em 16/07/2025**, sem a extensão para 24 meses (`lei-8213-1991.md`, art. 15, II, §§1º e 4º; `decreto-3048-1999.md`, art. 14).

---

## 5. CAMPOS da entrada (contrato do script e das skills)

Entrada em JSON (`--entrada <arquivo>` ou stdin). Flags do script: `--entrada`, `--versao`. Convenções comuns aos 7 scripts:

- `data` = texto `AAAA-MM-DD`; `competencia` = texto `AAAA-MM`; `decimal` = texto com ponto (`"1621.00"`); `inteiro`; `bool`; `texto`; `enum` = um dos valores listados; `lista` = lista JSON.
- Sub-campo de lista escrito como `campo[].sub`.
- Campo obrigatório ausente ou `null`, campo desconhecido ou valor fora do `enum` → **exit 2**. Chave que começa com `_` é comentário e é ignorada.
- Opcional ausente assume o padrão indicado.

| Campo | Tipo | Obrigatório | Valores / padrão |
|---|---|---|---|
| `beneficio` | enum | sim | `idade` · `tempo` · `especial` · `incapacidade` · `salario-maternidade` · `auxilio-reclusao` · `pensao` · `auxilio-acidente` · `bpc` |
| `data_referencia` | data | sim | DER, DII ou data do óbito |
| `vinculos` | lista | sim, exceto `beneficio = bpc` | ao menos 1 vínculo; no BPC a lei não exige vínculo (LOAS, art. 20) |
| `vinculos[].origem` | enum | sim | `empregado` · `contribuinte-individual` · `facultativo` · `especial` · `domestico` · `avulso` |
| `vinculos[].inicio` | data | sim | — |
| `vinculos[].fim` | data | não | ausente = vínculo sem data de fim (vai para `lacunas`) |
| `vinculos[].filiacao_domestica_comprovada` | bool | não | só `origem = domestico`; `true` = filiação como empregado doméstico comprovada (IN 128, art. 190, §1º, e art. 223, §5º); ausente = não informado (conta aberta se decidir o veredito) |
| `vinculos[].indicadores` | lista de texto | não | siglas do Anexo V; padrão `[]` |
| `vinculos[].competencias` | lista | sim | uma entrada por competência do vínculo |
| `vinculos[].competencias[].mes` | competencia | sim | — |
| `vinculos[].competencias[].valor` | decimal | não | salário de contribuição da competência |
| `vinculos[].competencias[].recolhido_em` | data | não | data do pagamento (necessária para o atraso de CI, especial e facultativo) |
| `vinculos[].competencias[].indicadores` | lista de texto | não | siglas do Anexo V da competência; padrão `[]` |
| `historico_anterior_informado` | bool | sim | `true` se os vínculos anteriores à perda da qualidade estão todos na entrada; `false` leva a carência após a perda a `indeterminada` |
| `desemprego_registrado` | bool | não | padrão `false` |
| `acidente_ou_doenca_dispensa` | bool | não | padrão `false`; decisão do advogado, nunca do script |
| `dias_sem_expediente_bancario` | lista de data | não | ausente = feriados nacionais do motor de prazos, com alerta |
| `ano_implementacao_requisitos` | inteiro | não | aposentadorias com a tabela do art. 142 da Lei 8.213: ano em que o segurado implementou todas as condições; ausente = conta aberta se a tabela decidir |
| `inscrito_ate_24_07_1991` | bool | não | aposentadorias: inscrição na Previdência Social Urbana até 24/07/1991 ou trabalhador/empregador rural coberto pela Previdência Social Rural (Lei 8.213, art. 142); ausente = inferido dos vínculos |

---

## 6. Saída e códigos

JSON com `carencia` (`exigidas`, `fundamento_exigidas`, `contadas`, `cumprida` = `sim` · `nao` · `indeterminada`, `faltam`, `excluidas` com motivo; depois da perda, `novas_desde_refiliacao`, `metade_exigida`, `anteriores`, `anteriores_reaproveitadas`), `qualidade_segurado` (`ultima_competencia`, `contribuicoes_sem_perda`, `graca_meses`, `fim_da_graca`, `competencia_seguinte`, `vencimento_nominal`, `vencimento`, `data_perda`, `mantem_qualidade_na_data_referencia`, `recolhimentos_em_atraso_pela_data`), `indicadores` (sigla, tipo, descrição, efeito, esclarecimentos), `tempo_do_vinculo`, `lacunas`, `alertas`, `parametros_usados`, `regra`, `fonte`, `memoria`, `formula_aberta`, `versao`.

| Exit | Quando |
|---|---|
| 0 | calculado |
| 2 | entrada inválida |
| 3 | carência `indeterminada` (histórico anterior ausente; perda da qualidade em aposentadoria; competências incertas — indicador sem efeito fechado, valor abaixo do mínimo sem ajuste, mínimo fora da tabela — que mudariam o veredito); devolve a conta aberta desta seção em `formula_aberta` |

## 7. O que fica aberto (não preencher por invenção)

Lista de doenças que dispensam carência (ato vigente do art. 26, II, não capturado); sufixos 15/20/25 do IEAN; regra da perda da qualidade nas aposentadorias do art. 25, II; efeito, na carência, das siglas cujo esclarecimento no Anexo V não o fecha; ajuste da EC 103, art. 29, que o segurado ainda pode requerer; hipóteses do art. 15, I e III a V (benefício em manutenção, segregação, reclusão, serviço militar), que entram na conta do advogado porque os CAMPOS não as recebem; qualidade do CI **prestador de serviço** com atividade comprovada desde 04/2003 (IN 128, art. 185, §5º), porque `origem` não distingue o prestador de serviço do CI que recolhe por conta própria.

---

---

## Cobertura temporal do script (COBERTURA)

Fonte: `scripts/calc/calc_previdenciario_cnis.py`, constante `COBERTURA`.

**Regra:** fato (data indicada na coluna *chave*) fora do intervalo em que a linha é a regra vigente → o script **não fecha veredito pela regra posterior**: sai em **exit 3** com `formula_aberta`, a regra histórica e a fonte de cada borda, para o advogado refazer a conta. Borda sem fonte capturada em `context/lei/` fica no lado conservador (o primeiro dia certo). A tabela abaixo é a constante `COBERTURA` do script, transcrita na W3-integ-2 (18/10/2026); mudou o script, muda esta tabela.

| Linha | Chave | Alcance | Desde | Até | Fora | Regra | Fonte das bordas | Antes do intervalo |
|---|---|---|---|---|---|---|---|---|
| `carencia-incapacidade` | `data_referencia` | `incapacidade` | 25/07/1991 | — | aberta | 12 contribuições (Lei 8.213, art. 25, I) ou dispensa (art. 26, II) | desde: IN 128, art. 199, II ("25 de julho de 1991, data de vigência da Lei nº 8.213"; in-128-2022-inss.md:1754); art. 25, I, na redação original (lei-8213-1991.md:715); até: art. 25, I, sem nota de alteração em lei-8213-1991.md | antes da Lei 8.213: regime anterior (CLPS), não capturado em context/lei/ |
| `carencia-aposentadorias` | `data_referencia` | `idade` · `tempo` · `especial` | 29/04/1995 | — | aberta | 180 contribuições (art. 25, II) ou a tabela do art. 142 pelo ano em que o segurado implementou todas as condições | desde: Lei 8.213, art. 142, redação da Lei 9.032/1995 ("ano em que o segurado implementou todas as condições"; lei-8213-1991.md:2843), publicada em 29/04/1995 (IN 128, art. 261, I: "até 28 de abril de 1995, véspera da publicação da Lei nº 9.032"; in-128-2022-inss.md:2411); até: arts. 25, II (redação da Lei 8.870/1994), e 142 sem alteração posterior em lei-8213-1991.md | de 25/07/1991 a 28/04/1995: art. 142 na redação original, tabela pelo ano da entrada do requerimento, com outros números de 1996 em diante (lei-8213-1991.md:2786-2841, redação revogada); antes da Lei 8.213: regime anterior (CLPS), não capturado em context/lei/ |
| `carencia-auxilio-reclusao` | `data_referencia` | `auxilio-reclusao` | 18/01/2019 | — | aberta | 24 contribuições (Lei 8.213, art. 25, IV) | desde: art. 25, IV, incluído pela MP 871/2019 (lei-8213-1991.md:727-729), publicada em 18/01/2019 (lei-13846-2019.md:968); IN 128, art. 198, II (in-128-2022-inss.md:1750); até: art. 25, IV, na redação da Lei 13.846/2019, sem alteração posterior | fato gerador até 17/01/2019: auxílio-reclusão isento de carência (IN 128, art. 198, I, in-128-2022-inss.md:1749; Lei 8.213, art. 26, I, redação da Lei 9.876/1999, lei-8213-1991.md:737) |
| `carencia-salario-maternidade` | `data_referencia` | `salario-maternidade` | 05/04/2024 | — | aberta | sem carência: art. 25, III, julgado inconstitucional (ADI 2.110) | desde: ADI 2.110, ata do julgamento publicada em 5/4/24 (temas-sumulas-prev.md:22); IN 128, art. 200, tabela, linha "05/04/2024 em diante ... ADI nº 2.110" (in-128-2022-inss.md:1795-1800); até: linha final da tabela da IN 128, art. 200 | antes de 05/04/2024: isentas a empregada, a avulsa e a doméstica (Lei 8.213, art. 26, VI, Lei 9.876/1999); 10 contribuições da contribuinte individual, da facultativa e da segurada especial (art. 25, III), como a IN 128, art. 200, aplica até 04/04/2024; o efeito da ADI 2.110 sobre fato anterior não está fechado em context/ |
| `carencia-pensao-auxilio-acidente` | `data_referencia` | `pensao` · `auxilio-acidente` | 25/07/1991 | — | aberta | sem carência (Lei 8.213, art. 26, I) | desde: IN 128, art. 199, II ("25 de julho de 1991, data de vigência da Lei nº 8.213"; in-128-2022-inss.md:1754); art. 26, I, já na redação original dispensa pensão e auxílio-acidente (lei-8213-1991.md:735); até: art. 26, I, redação da Lei 13.846/2019, mantém os dois | antes da Lei 8.213: regime anterior (CLPS), não capturado em context/lei/ |
| `carencia-bpc` | `data_referencia` | `bpc` | 07/12/1993 | — | aberta | benefício assistencial sem carência (LOAS, art. 20) | desde: Lei 8.742, de 7 de dezembro de 1993 (lei-8742-1993-loas.md:16); dia da publicação não capturado; até: LOAS, art. 20, em vigor | antes da LOAS não havia o BPC |
| `perda-27A` | `data_referencia` | `incapacidade` · `salario-maternidade` · `auxilio-reclusao` | 25/07/1991 | — | aberta | após a perda, as contribuições anteriores voltam quando as novas alcançam a fração da carência do regime do fato gerador (REGIMES_27A) | desde: IN 128, art. 200, caput ("benefícios requeridos a partir de 25 de julho de 1991"; in-128-2022-inss.md:1758); até: IN 128, art. 200, tabela, linha "05/04/2024 em diante" | antes da Lei 8.213: regime anterior (CLPS), não capturado em context/lei/ |
| `qualidade-art15-ate-2018` | `perda` | — | 25/07/1991 | 31/12/2018 | aberta | graça do art. 15, II e VI, §§1º, 2º e 4º, da Lei 8.213, na redação original | desde: IN 128, art. 199, II ("25 de julho de 1991, data de vigência da Lei nº 8.213"; in-128-2022-inss.md:1754); até: MP 905/2019 deu ao art. 15, II, redação que conta a graça também do fim do seguro-desemprego, e o fez salário de contribuição (Lei 8.212, art. 28, §12); revogada pela MP 955/2020 (lei-8213-1991.md:447-449; lei-8212-1991.md:1015). Dias não capturados: a borda é o fim de 2018 | art. 15, II, redação da MP 905/2019: graça também a contar de quando o segurado deixar de receber o seguro-desemprego, cuja parcela era salário de contribuição; só prorroga a qualidade, por isso só a perda apurada fica aberta |
| `qualidade-art15-desde-2021` | `perda` | — | 01/01/2021 | — | aberta | graça do art. 15, II e VI, §§1º, 2º e 4º, da Lei 8.213, na redação original | desde: revogação da MP 905/2019 pela MP 955/2020 (lei-8213-1991.md:447-449); dia não capturado: a borda é o início de 2021; até: art. 15, II, na redação original, em vigor | ver qualidade-art15-ate-2018 |
| `vencimento-dia-15` | `competencia` | — | competência 01/1993 | — | aberta | vencimento do CI, do facultativo e do doméstico no dia 15 do mês seguinte (Lei 8.212, art. 30, II e V); sem expediente bancário, dia útil anterior até 28/11/1999 (§2º, Lei 8.620/1993) e posterior desde 29/11/1999 (§2º, Lei 9.876/1999) | desde: art. 30, II, redação da Lei 8.620, de 5.1.1993, e §2º incluído por ela (lei-8212-1991.md:1232); até: art. 30, §2º, I, redação da Lei 13.202/2015 (lei-8212-1991.md:1246) | competências anteriores a 01/1993: prazo da alínea b do inciso I do art. 30 da Lei 8.212 em redações sucessivas (dia 8, depois dia 2) cujas datas não estão capturadas |
