# Metodologia do plugin previdenciario-adv-os

> O primeiro arquivo que o orquestrador (`previdenciario-master`) lê, **sempre**. Diz como as 34 skills se articulam, qual anexo cada uma usa, qual é a pergunta que reordena a trilha e o que nunca se afirma sem fonte.
> Versão do plugin: **2.0.3**. Perspectiva: advogado do **segurado, dependente ou beneficiário** contra o INSS (polo ativo). O lado é preferência gravada no `previdenciario/perfil.md`, não trava.
> Este arquivo é distribuído com o plugin. A fonte de cada regra é um arquivo de `context/lei/` (mapa em `context/lei/INDICE.md`); o que não está lá não é citado.

---

## 1. ⛔ A REGRA DE LEITURA DOS ANEXOS (vale para TODAS as skills)

**Faça `grep` do dispositivo e leia a FAIXA. Nunca despeje um anexo inteiro no contexto.**

Formato do ponteiro dentro de cada skill:

```
`context/lei/<arquivo>.md` (arts. X e Y - grep o artigo e leia a faixa)
```

**Por quê:** os anexos são densos de propósito (a IN 128 tem cerca de 930 KB; o Decreto 3.048, 850 KB). Carregar o arquivo inteiro para citar um artigo desperdiça contexto, dilui a atenção e aumenta a chance de a skill puxar a redação revogada que está na linha ao lado da vigente.

Três disciplinas:

1. **Linha que começa com `(revogado) ~~…~~` é texto riscado na fonte: não é norma vigente.** Num `grep` por `Art. N`, descarte essas linhas e leia a outra. O art. 103 da Lei 8.213, por exemplo, aparece seis vezes no arquivo; só uma é a vigente.
2. **Toda skill referencia ao menos um anexo.** O anexo é a prova. Nunca cite "de cabeça".
3. **A citação nomeia o diploma.** Número de artigo sozinho não identifica a regra (ver §7.1).

**Como a skill acha o `context/`:** o Cowork entrega o caminho da pasta base da skill no carregamento; `context/` fica dois níveis acima (`<pasta-base>/../../context/`). Se o caminho relativo não abrir o arquivo, procurar pelo nome (`find "$HOME" -name '<arquivo>.md' -path '*/context/*'`). Se ainda falhar, seguir a seção "Se faltar anexo" da skill e avisar o advogado de que a citação ficou sem conferência.

---

## 2. OS PILARES

1. **Porta única.** Todo caso entra pelo `previdenciario-master`, que classifica pela `triagem-dogmatica-previdenciario` e roteia. Toda entrega fecha pelo `validador-previdenciario` e pela `suprema-corte-previdenciaria` (R1–R4, com o crivo anti-IA no R4).
2. **Standalone-first.** As contas rodam em scripts locais em Python, só biblioteca padrão, sem rede (§13). Os motores de atualização e de prazo são cópias conferidas por sha256, não dependência de outro plugin. Sem Python, a conta sai aberta pelo `context/calculo-<x>.md`.
3. **Anti-alucinação por design.** Nenhuma citação entra em peça sem âncora em `context/`. Número crítico (carência, tempo, RMI, valor da causa, atrasados) só por script ou por conta aberta. O que falta vira fórmula, nunca estimativa.
4. **Lei vigente em 2026.** A captura da fonte oficial supera o treino do modelo. Este domínio tem várias normas e decisões que mudam o resultado do caso e que um modelo treinado até o início de 2026 não conhece ou conhece pela metade: EC 136/2025 (requisitórios), Manual de Cálculos da Justiça Federal de julho/2026, Resolução CJF 983/2026, STF Tema 1.419 com os embargos de maio/2026, STF Tema 1.300 transitado em abril/2026, a tese nova do STF Tema 1.102 (embargos de novembro/2025), Decreto 12.797/2025 e Portaria Interministerial MPS/MF 13/2026 (piso e teto de 2026).
5. **Postura honesta.** Pendências e pontos que o texto não fecha são declarados, nunca escondidos. Tese inviável não se vende: a revisão da vida toda saiu do produto.
6. **Despersonalizado.** Autoria IA Combativa. A voz, o nome e as preferências do escritório vêm do `previdenciario/perfil.md`, criado pelo `/start-previdenciario`. Nenhum dado de cliente fica no plugin.

---

## 3. O MAPA DAS 6 CAMADAS (34 skills)

- **C0 — Orquestração e QA (6):** `previdenciario-master` (porta única), `previdenciario-onboarding` (wizard do `/start-previdenciario`, com migração do estado da 0.1.0), `triagem-dogmatica-previdenciario` (elicitação em camadas e pergunta crítica), `memoria-de-caso-previdenciario` (grava `previdenciario/casos/<slug>.md`), `estilo-juridico-previdenciario` (voz do escritório pelo `perfil.md`), `suprema-corte-previdenciaria` (gate final R1–R4).
- **C1 — Fundação (4):** `base-legal-previdenciaria` (acha o dispositivo pelo `INDICE.md`, avisa homônimo), `jurisprudencia-estrategica-previdenciario` (só o que está em `context/lei/temas-sumulas-prev.md`), `validador-previdenciario` (crivo item a item de toda citação antes da Corte), `anti-alucinacao-previdenciario` (guard permanente: §8 deste arquivo).
- **C2 — Transversal (7):** o "não esquecer nada". `estrategia-de-caso-previdenciario` (2–3 caminhos com trade-off), `analise-trilateral-previdenciario` (autor × INSS × juízo), `calculos-previdenciarios` ⭐ (hub de cálculo, roteia para os 7 scripts), `prazos-previdenciarios` (primeira parada quando a pergunta crítica dá "sim"), `parecer-previdenciario`, `documentos-extrajudiciais-previdenciarios`, `visual-law-previdenciario`.
- **C3 — Análise e prova (4):** `analise-cnis`, `analise-ppp-ltcat-aposentadoria-especial`, `analise-carta-concessao-indeferimento`, `pericia-medica-previdenciaria`.
- **C4 — Benefícios e vias (6):** `planejamento-previdenciario` ⭐, `acidentario-do-trabalho`, `bpc-loas-previdenciario`, `administrativo-inss-crps`, `rpps-servidor-publico` (triagem e encaminhamento, sem conta), `previdencia-complementar` (triagem e encaminhamento, sem conta).
- **C5 — Judicial e recursos (7):** `peticao-inicial-previdenciaria`, `replica-previdenciaria`, `mandado-seguranca-previdenciario`, `audiencia-previdenciaria`, `acao-revisional-rmi`, `cumprimento-sentenca-inss`, `recursos-previdenciarios` (standalone: JEF, TRF, PEDILEF, REsp, RE, CRPS).

⭐ **Núcleo comercial:** `calculos-previdenciarios` + `planejamento-previdenciario`, com os scripts por trás — qual regra vale mais, quando aposentar, quanto vai receber.

**Fluxo do master (9 passos):**

```
1 ler este arquivo → 2 triagem (fase + objetivo + skill alvo, pergunta critica primeiro)
→ 3 confirmar o quadro do caso em camadas (1 a 3 perguntas por turno; "nao sei" = lacuna)
→ 4 carregar memoria-de-caso-previdenciario
→ 5 transversal SEMPRE: prazos (se houver prazo), estrategia (2-3 caminhos), calculos (se houver numero)
→ 6 conduzir a trilha da camada (C3 → C4 → C5), propondo estrategias antes de redigir
→ 7 acionar o script ou a conta aberta (§13)
→ 8 validador-previdenciario + suprema-corte-previdenciaria (R1-R4, anti-IA no R4)
→ 9 atualizar memoria-de-caso-previdenciario (ato, proximo passo, prazo, skills que rodaram)
```

## 3.1 GRAFO DE ORQUESTRAÇÃO — quem chama quem

A tabela "quem chama quem" fica em **`context/grafo-orquestracao.md`**. Ela é **gerada** a partir da linha `Chamada por / Chama` de cada `SKILL.md`; não é mantida à mão neste arquivo, para não divergir das skills na primeira edição.

---

## 4. A ÁRVORE DE TRIAGEM — a pergunta crítica primeiro

> **1ª pergunta, sempre: há prazo correndo agora (recurso administrativo, resposta, recurso judicial) ou benefício cessado ou indeferido há menos de 30 dias?**
> Se sim → a trilha entra por **`prazos-previdenciarios`** antes de qualquer outra coisa. O prazo recursal não espera, e no auxílio por incapacidade temporária o requerimento feito depois de 30 dias de afastamento desloca o início do benefício para a data do requerimento, salvo DII posterior (`context/lei/lei-8213-1991.md`, art. 60, §1º; `context/lei/in-128-2022-inss.md`, art. 336).

**Prazo já vencido interrompe o fluxo na hora:** o master avisa antes de qualquer outra coisa. Recurso intempestivo não é automaticamente encerrado — o INSS não pode recusar o recebimento (`in-128-2022-inss.md`, art. 578, §1º) e a admissibilidade é do CRPS: a intempestividade é razão de não conhecimento (`context/lei/regimento-crps-portaria-mps-125-2026.md`, art. 112, I), e o conselheiro só propõe a relevação quando demonstradas de forma inequívoca a liquidez e a certeza do direito (art. 112, §1º) — inequívocas quando o INSS reconheceu o direito, no mesmo processo ou em outro, ou quando os dados para julgar estão nas bases governamentais a que o conselheiro tem acesso (§2º); a relevação vale só para decisão de conhecimento e provimento (§5º), não se aplica a incidentes, embargos de declaração e procedimentos do Conselho Pleno (§3º) e não admite diligência (§8º) —, mas a skill não promete relevação e apresenta também as outras vias (novo requerimento, ação judicial, revisão dentro da decadência).

```
Ha prazo correndo ou cessacao/indeferimento ha menos de 30 dias?
├── sim → prazos-previdenciarios → (depois) a trilha do caso
└── nao → O que o cliente quer?
          ├── saber se/quando aposenta, quanto recebe → planejamento-previdenciario
          │       (analise-cnis → tempo → transicao → RMI pelos scripts)
          ├── recebeu decisao do INSS → analise-carta-concessao-indeferimento
          │       ├── indeferido → administrativo-inss-crps (recurso CRPS) ou peticao-inicial
          │       └── concedido com valor errado → acao-revisional-rmi (checar decadencia)
          ├── incapacidade → pericia-medica-previdenciaria
          │       ├── nexo com o trabalho → acidentario-do-trabalho
          │       └── sem nexo → trilha previdenciaria comum
          ├── idoso ou pessoa com deficiencia sem renda → bpc-loas-previdenciario
          ├── tempo especial → analise-ppp-ltcat-aposentadoria-especial
          ├── processo em curso → replica / audiencia / recursos / cumprimento-sentenca-inss
          ├── ato ilegal com prova pre-constituida → mandado-seguranca-previdenciario
          └── servidor publico ou previdencia privada → rpps-servidor-publico / previdencia-complementar
                  (triagem e encaminhamento; sem conta na 2.0.3)
```

**Disciplinas da elicitação** (master e triagem): não perguntar o que dá para inferir do `perfil.md`, do `casos/<slug>.md` ou dos documentos enviados; no máximo 1 a 3 perguntas por turno; pergunta de risco só quando algo no caso aponta risco. O CNIS e o laudo médico são dado pessoal sensível: tratar só no computador do advogado e não colar em ferramenta externa.

---

## 5. AS VERDADES DURAS

Cada uma com a âncora e a consequência de errar. As mesmas estão no `CLAUDE.md` do plugin.

1. **A revisão da vida toda é inviável.** O art. 3º da Lei 9.876/1999 é cogente; o segurado que se enquadra nele não pode optar pela regra definitiva do art. 29, I e II, da Lei 8.213, "independentemente de lhe ser mais favorável" (`context/lei/temas-sumulas-prev.md`, ADIs 2.110/2.111 e STF Tema 1.102, tese nova). **Consequência:** ajuizar a tese hoje expõe o cliente a sucumbência, custas e perícia. A modulação tem dois critérios distintos: (a) são irrepetíveis os valores percebidos em virtude de decisões, definitivas ou provisórias, **prolatadas até 05/04/2024**; (b) nas ações da vida toda **pendentes de conclusão nessa data**, não se cobram honorários de sucumbência, custas e perícias contábeis. Ficam mantidas as repetições e os pagamentos já efetuados. O que o plugin faz é defender o segurado contra cobrança indevida dentro desses dois critérios.
2. **A conversão de tempo especial em comum vale só para o tempo trabalhado até 13/11/2019.** O critério é a data em que o trabalho foi prestado, não a data da filiação (`context/lei/ec-103-2019.md`, art. 25, §2º; `context/lei/decreto-3048-1999.md`, art. 188-P, §5º). Vínculo que cruza a data é fatiado. Multiplicadores: 15 anos → 2,00 (M) / 2,33 (H); 20 anos → 1,50 / 1,75; 25 anos → 1,20 / 1,40 (`context/lei/decreto-3048-art188p-tabela.md`). **Consequência:** converter um dia depois de 13/11/2019 infla o tempo e arrisca o requisito e a RMI pedidos, abrindo flanco na contestação e na perícia contábil.
3. **O PBC de 100% desde 07/1994 vem da EC 103, art. 26** — não da Lei 13.846/2019, que não mudou o art. 29 da Lei 8.213. Coeficiente: 60% + 2 pontos por ano acima de 20 anos (homem) ou 15 (mulher e especial de 15); 100% no pedágio de 100% e na incapacidade permanente acidentária; o pedágio de 50% é média × fator previdenciário (`context/lei/ec-103-2019.md`, arts. 17 e 26). **Consequência:** marco ou coeficiente errado muda a média e a RMI — para mais (risco de impugnação por excesso) ou para menos (diferença deixada para trás).
4. **Divisor mínimo de 108** para o filiado até 07/1994, nas aposentadorias com fato gerador a partir de 05/05/2022, exceto a por incapacidade permanente; o descarte não elimina o divisor (`context/lei/lei-8213-1991.md`, art. 135-A; `context/lei/in-128-2022-inss.md`, art. 228, §§1º e 4º). **Consequência:** dividir pelo número de salários de quem tem poucos recolhimentos superestima a média; a RMI só fica maior quando a média errada não cai no piso — a conta mostra as duas.
5. **Atualização e juros contra o INSS são em fatias por competência**, escolhidas pela data e pela fase (§9 e §13): até nov./2021, INPC (desde set./2006) e juros do Manual; de dez./2021 a ago./2025, Selic única (EC 113, redação original, restrita a esse período pelo STF Tema 1.419); desde set./2025, antes do requisitório, **INPC + taxa legal com dedução do INPC**; no requisitório, Res. CJF 983/2026, art. 7º (`context/lei/manual-cjf-2026-calculos-prev.md`, itens 4.3.1.1 e 4.3.2; `context/lei/res-cjf-983-2026.md`, art. 7º). O BPC segue o regime das condenações em geral, nunca o previdenciário. **Consequência:** "IPCA-E até 2021 e Selic depois" erra índice e juros em várias fatias e pode tanto expor a conta a impugnação por excesso quanto deixar diferença do cliente para trás.
6. **A Selic contra a Fazenda vem da EC 113/2021, art. 3º** — não de "Lei 14.439/2022". **Consequência:** fundamento atribuído à lei errada compromete a credibilidade da peça.
7. **Carência depois da perda da qualidade:** a metade da carência do benefício, contada desde a nova filiação (6 para os benefícios por incapacidade, cuja carência é 12; 12 para o auxílio-reclusão, cuja carência é 24), só reabre o cômputo das contribuições anteriores; a carência total continua a do art. 25. O salário-maternidade não entra nessa conta: a carência dele foi declarada inconstitucional (ADI 2.110) (`context/lei/lei-8213-1991.md`, art. 27-A; `context/lei/decreto-3048-1999.md`, art. 27-A). Sem o histórico anterior, a carência fica indeterminada. **Consequência:** tratar a metade como carência cumprida expõe o pedido a indeferimento com fundamento correto do INSS.
8. **Auxílio-acidente independe de carência e não tem piso de um salário mínimo** (`context/lei/lei-8213-1991.md`, arts. 26, I, e 86; `context/lei/decreto-3048-1999.md`, art. 42, parágrafo único); é inacumulável com aposentadoria (art. 86, §§1º e 2º). **Consequência:** pedir piso ou cumulação com aposentadoria é pedido contra a letra da lei e expõe esse ponto à improcedência.
9. **BPC: renda per capita "igual ou inferior a 1/4" do salário mínimo**, sem carência e **sem abono anual** (`context/lei/lei-8742-1993-loas.md`, art. 20, §3º; `context/lei/lei-8213-1991.md`, art. 40). O 1/4 não é o único meio de prova (`temas-sumulas-prev.md`, STF Tema 27 e STJ Tema 185). **Consequência:** somar abono no valor da causa do BPC infla a alçada; tratar 1/4 como teto absoluto deixa de produzir a prova de miserabilidade que a jurisprudência admite.
10. **RPV federal = 60 salários mínimos, verificado pelo valor atualizado até a transmissão ao tribunal**; acima disso, precatório, com faculdade de renunciar ao excedente; fracionar é vedado (`context/lei/lei-10259-2001-jef.md`, art. 17, §§1º, 3º e 4º; `context/lei/res-cjf-983-2026.md`, art. 3º, §4º; `context/lei/cf88-seguridade.md`, art. 100, §8º). O nome é "renúncia ao excedente", não "cisão". **Consequência:** via errada pode exigir renúncia, cancelamento e nova requisição (`res-cjf-983-2026.md`, art. 4º, §§2º e 3º), e o precatório pode cair no orçamento de um exercício posterior.
11. **IEAN é indicador de exposição a agente nocivo informada pelo empregador, passível de comprovação**; não converte tempo sozinho e não dispensa a prova técnica da exposição: PPP adequadamente preenchido e amparado em laudo técnico (o PPP assim preenchido dispensa a apresentação do LTCAT; pedir o laudo quando o PPP for incompleto ou precisar de esclarecimento) (`context/lei/portaria-990-2022-anexo-v-indicadores-cnis.md`; `context/lei/lei-8213-1991.md`, art. 57, §§3º e 4º; `context/lei/in-128-2022-inss.md`, art. 281, §4º). **Consequência:** pedir especial só pelo IEAN deixa o pedido sem a prova que a lei exige.

---

## 6. ⭐ REGRAS DE DISTINÇÃO (hipótese, não escolha)

Duas saídas que parecem alternativas, mas dependem de um fato. Identificar o fato **antes** de responder.

| Parece escolha entre… | Na verdade depende de… | Âncora |
|---|---|---|
| regras de transição × regra permanente | data da filiação: até 13/11/2019 há transições; depois, só a permanente | `ec-103-2019.md`, arts. 15 a 21 (caput de cada um) e 19 |
| direito adquirido × transição | requisitos cumpridos até 13/11/2019; se cumpridos, aplica-se a lei da época, e as regras cumpridas são comparadas pelo script | `ec-103-2019.md`, art. 3º |
| regra definitiva do art. 29 × art. 3º da Lei 9.876 | não há opção: o art. 3º é cogente para quem se enquadra | `temas-sumulas-prev.md`, ADIs 2.110/2.111 |
| converter × não converter o especial | data em que cada dia foi trabalhado | `ec-103-2019.md`, art. 25, §2º |
| 60% + 2% × 100% na incapacidade permanente | nexo com o trabalho (acidente de trabalho, doença profissional ou do trabalho); acidente sem nexo laboral não é acidentário | `ec-103-2019.md`, art. 26, §§2º, III, e 3º, II; STF Tema 1.300 |
| pedágio de 50% × pedágio de 100% | tempo em 13/11/2019 (mais de 28 M / 33 H para o de 50%) e idade (57 M / 60 H para o de 100%); valores diferentes: no de 50%, média × fator previdenciário; no de 100%, 100% da média | `ec-103-2019.md`, arts. 17, 20 e 26, §3º, I |
| carência × tempo de contribuição | para carência do contribuinte individual, do especial e do facultativo, contam as contribuições a partir do primeiro pagamento sem atraso; as recolhidas com atraso referentes a competências **anteriores** a esse pagamento não contam (as posteriores seguem as demais condições). Para tempo, o recolhimento em atraso conta se feito antes do fato gerador, com as ressalvas do art. 208 da IN 128 | `lei-8213-1991.md`, art. 27, II; `in-128-2022-inss.md`, art. 208 |
| regime previdenciário × assistencial de atualização | natureza do benefício (o BPC é assistencial) | `manual-cjf-2026-calculos-prev.md`, item 4.3.1.1, Nota 3 |
| fase R1 × fase R2 dos juros | data-base da requisição: antes dela, Manual CJF; dela ao pagamento, Res. CJF 983/2026 | `res-cjf-983-2026.md`, art. 7º |
| RPV × precatório | valor atualizado até a transmissão; renunciar ao excedente é escolha do credor, fracionar não é | `lei-10259-2001-jef.md`, art. 17; `res-cjf-983-2026.md`, art. 3º, §4º |
| honorários sucumbenciais × contratuais na classificação | sucumbenciais em requisição própria; contratuais destacados integram o crédito da parte | `res-cjf-983-2026.md`, art. 16 |
| prazo de RPV de 60 dias × 2 meses | rito: JEF (Lei 10.259, art. 17) ou CPC (art. 535, §3º, II); um não se converte no outro | `lei-10259-2001-jef.md`; `cpc-excertos-prev.md` |

---

## 7. AS ARMADILHAS QUE DERRUBAM PEÇA

O que o modelo tende a afirmar e está errado (todas medidas na auditoria da 0.1.0).

| Afirmação errada | Correto |
|---|---|
| IEAN = "empresa de atividade não identificada" | exposição a agente nocivo informada pelo empregador (Portaria 990, Anexo V) |
| indicadores PE, PVI, IPESC, IGFIP | não constam do Anexo V; usar só as siglas da tabela oficial (ex.: PVIN, PREM-EXT, PEXT, IREC-INDPEND, IREM-ACD, IEAN) |
| conversão pós-EC 103 "para quem já era filiado" | critério é a data do trabalho, até 13/11/2019 |
| fatores só 1,4 (H) e 1,2 (M) | tabela completa de 15, 20 e 25 anos |
| ruído: "85 dB depois de 19/11/2003; antes 80" | há a faixa de 90 dB de 06/03/1997 a 18/11/2003, sem retroação do patamar posterior (STJ Tema 694); o limite vigente fica no Anexo IV do Decreto 3.048 |
| PBC de 100% pela Lei 13.846/2019 | EC 103, art. 26 |
| pedágio de 50% com "60% + 2%" e idade variável | média × fator; sem idade mínima; só para quem tinha mais de 33/28 anos em 13/11/2019 |
| pontos "105/100" desde o início | 96 (H) / 86 (M) em 2019, +1 por ano até 105/100; professor 91/81 até 100/92 |
| "as 5 regras de transição" | arts. 15, 16, 17, 18, 20 e 21, mais direito adquirido e permanente |
| pedágio de 50% para servidor público | o art. 17 é só do RGPS |
| pensão por morte com carência de 18 contribuições | pensão independe de carência; as 18 contribuições afetam a duração da cota do cônjuge |
| salário-maternidade com carência de 10 | carência declarada inconstitucional (ADI 2.110) |
| auxílio-acidente "não acumula com auxílio-doença" | a vedação expressa é com aposentadoria (art. 86, §§1º e 2º); outro benefício, exceto aposentadoria, não prejudica o auxílio-acidente (§3º, observado o §5º); na **reabertura** do auxílio por incapacidade temporária pelo mesmo acidente que gerou o auxílio-acidente, este fica suspenso até a cessação e depois é reativado (Decreto 3.048, art. 104, §6º) |
| "IPCA-E até 12/2021 e Selic depois (Lei 14.439/2022)" | regime em fatias (verdade 5); EC 113 é a fonte da Selic |
| "taxa legal não se aplica contra o INSS" | aplica-se desde set./2025, na fase anterior ao requisitório (Manual CJF 2026, item 4.3.2) |
| Súmula 105 do STJ para custas | a 105 é honorários em mandado de segurança; custas do INSS na Justiça Estadual: Súmula 178 |
| "cisão" do crédito na RPV | "renúncia ao excedente"; fracionar é vedado |
| juros do requisitório "IPCA + 2%" antes de set./2025 | antes de set./2025, Selic (Res. CJF 983/2026, art. 7º, §3º, I e II) |

## 7.1 🚨 HOMÔNIMO — a classe de erro que nenhum grep pega

O mesmo número de artigo existe em mais de um diploma deste domínio. Um `grep` cru devolve o errado primeiro. **A linha da citação nomeia o diploma, sempre.**

| Número | Diploma A | Diploma B (e C) |
|---|---|---|
| art. 3º | Lei 9.876/1999 (regra de transição do salário de benefício, cogente) | EC 113/2021 (atualização dos requisitórios) · EC 103/2019 (direito adquirido) · Lei 10.259/2001 (competência do JEF, 60 salários mínimos) |
| art. 17 | EC 103/2019 (pedágio de 50%) | Lei 10.259/2001 (pagamento da RPV em 60 dias) |
| art. 20 | EC 103/2019 (pedágio de 100%) | Lei 8.742/1993 (BPC) |
| art. 26 | EC 103/2019 (cálculo do benefício) | Lei 8.213/1991 (dispensa de carência) |
| art. 27-A | Lei 8.213/1991 | Decreto 3.048/1999 (mesma matéria, redações diferentes: "metade dos períodos" × "metade do número de contribuições") |
| art. 42 | Lei 8.213/1991 (aposentadoria por invalidez) | Decreto 3.048/1999 (limite no reajuste; o parágrafo único afasta o piso do auxílio-acidente) |
| art. 15 | Lei 8.213/1991 (qualidade de segurado e período de graça) | EC 103/2019 (transição por pontos) |
| art. 32 | Lei 8.213/1991 (atividades concomitantes: soma dos salários) | Decreto 3.048/1999 (salário de benefício em geral, no regulamento; não é a fonte da regra da soma) |
| Tema 692 | STF (ART do CONFEA, sem relação com previdência) | STJ (devolução de valores de tutela revogada) |
| Tema 1.041 | STJ (perdimento de veículo do transportador, cancelado) | — nunca usar para conversão; a regra é a EC 103, art. 25, §2º |

---

## 8. 🟡 CONTRATO DE ANTI-ALUCINAÇÃO — o que é PROIBIDO afirmar sem verificação

Guard permanente: `anti-alucinacao-previdenciario`. **Nunca preencher número por memória** — é onde o modelo alucina com mais confiança.

**Proibições:**

- ⛔ **Não citar "Lei 14.439/2022" para a Selic contra o INSS.** A fonte é a EC 113, art. 3º (redação original).
- ⛔ **Não citar "Tema 1.041 do STJ" para conversão de tempo especial.** É perdimento de veículo, cancelado. O tema da atividade de vigilante é o STJ Tema 1.031.
- ⛔ **Não citar "Tema 692 do STF" para a vida toda.** A vida toda é o STF Tema 1.102.
- ⛔ **Não oferecer a revisão da vida toda** como tese de concessão ou de revisão.
- ⛔ **Não atribuir à Lei 13.846/2019 o PBC de 100%.**
- ⛔ **Não tratar IEAN como "empresa não identificada"** nem como conversão automática. Os sufixos 15/20/25 que acompanham o IEAN em extratos não têm âncora no Anexo V: não automatizar; exigir prova técnica.
- ⛔ **Não citar a Súmula 105 do STJ para custas.**
- ⛔ **Não usar os números de tema com o conteúdo que a 0.1.0 lhes atribuía.** Objetos corretos em `context/lei/temas-sumulas-prev.md`: STJ Tema 416 = auxílio-acidente com lesão mínima; STJ Tema 692 = devolução de valores de tutela revogada; STJ Tema 999 = vida toda no STJ (superado); STJ Tema 1.007 = aposentadoria híbrida com rural remoto; STJ Tema 1.023 = prescrição de dano moral por DDT; STF Tema 313 = decadência; STF Tema 942 = conversão especial de **servidor** (RPPS); STF Tema 1.124 = ITBI. A Súmula 50 da TNU não autoriza converter trabalho posterior a 13/11/2019.
- ⛔ **Não dizer que a taxa legal "não se aplica contra o INSS".**
- 🚨 **Não inventar** salário mínimo, teto ou taxa legal de um mês: usar a tabela com fonte; mês sem fonte devolve fórmula.

**Regras adotadas nos pontos que o texto deixava abertos (M1–M9):**

| # | Regra | Fonte |
|---|---|---|
| M1 | **Unidade única: dias.** Tempo de contribuição data a data até 13/11/2019 e por competência integral desde 11/2019, **só a competência com salário de contribuição igual ou superior ao limite mínimo** (abaixo dele, só conta com complementação, agrupamento ou utilização de excedente — IN 128, art. 209, §1º; antes de 14/11/2019, a mesma exigência do mínimo vale para contribuinte individual, facultativo e segurado especial que contribui facultativamente — art. 210); ano de 365 dias e mês de 30. O bloco de competências posteriores a 11/2019 vira dias por `anos × 365 + meses restantes × 30` (12 competências = 1 ano de 365: interpretação operacional, padrão do script; alternativa exposta: 30 dias por competência, quando muda o resultado). **Pontos: idade e tempo apurados em dias** (idade = dias corridos desde o nascimento, excluído o dia do nascimento), comparados com pontos × 365 dias; a soma em anos, meses e dias não é a operação do texto, e a leitura civil pura sai só como sensibilidade. Não usar 365,25. Quando as normalizações mudam o veredito, as duas contas saem (exit 3). Competência 11/2019 trabalhada só em parte: exit 3, `[VERIFICAR]` | `in-128-2022-inss.md`, arts. 206, 207 (parágrafo único), 209 e 210; `ec-103-2019.md`, arts. 15, §2º, e 21, §1º; `decreto-3048-1999.md`, art. 188-P, §1º; `cc-excertos-prev.md`, art. 132; F1, `01-direito-vigente.md`, tabela dos pontos M |
| M2 | Pedágio: o adicional fracionário se cumpre só por inteiro; vale o primeiro dia que satisfaz o requisito; nunca arredondar para baixo | `ec-103-2019.md`, arts. 17 e 20 |
| M3 | Coeficiente acima de 100% é devido; o limite é o teto monetário, não o percentual | `ec-103-2019.md`, art. 26, §§2º e 5º; `in-128-2022-inss.md`, art. 233 |
| M4 | Limite da RPV verificado pelo valor atualizado até a transmissão; salário mínimo dessa data, como **interpretação operacional declarada** (a resolução não o diz literalmente) | `res-cjf-983-2026.md`, art. 3º, §4º |
| M5 | Fase anterior ao requisitório desde set./2025: INPC + taxa legal com dedução do INPC (previdenciário); IPCA-15 + taxa legal com dedução do IPCA-15 (assistencial) | `manual-cjf-2026-calculos-prev.md`, itens 4.2.1.1, 4.2.2, 4.3.1.1 e 4.3.2; `cc-excertos-prev.md`, art. 406 |
| M6 | Valor da causa: **duas contas**; padrão = incluir o abono anual nas 12 vincendas, declarado como interpretação; nunca no BPC | `cpc-excertos-prev.md`, art. 292, §2º; `lei-10259-2001-jef.md`, art. 3º, §2º |
| M7 | Fator previdenciário sem a tábua do IBGE capturada: fórmula e lista de dados faltantes | `lei-8213-1991.md`, art. 29, §§7º a 9º |
| M8 | Requisitório expedido antes da EC 136: Selic até ago./2025; desde set./2025, IPCA + 2% a.a. ou Selic, o menor, automaticamente (regra geral, §3º, II e III). Exceção: no período em que não há juros de mora corre só a correção — precatório pago no prazo constitucional (§2º) e RPV no prazo legal (`manual-cjf-2026-calculos-prev.md`, cap. 5, Nota 2). Precatório apresentado antes de set./2025 com trecho de 2025 dentro da graça: o texto não concilia o §3º, II, com o §2º → duas contas, `[VERIFICAR]` | `res-cjf-983-2026.md`, art. 7º, §§2º e 3º |
| M9 | Irrepetíveis os valores percebidos por decisões **prolatadas** até 05/04/2024; mantidas as repetições já feitas; novos embargos pendentes (17/03/2026) | `temas-sumulas-prev.md`, STF Tema 1.102 |

Marcos por competência, não por dia: a Selic de ago./2025 é aplicada em set./2025; a taxa legal de set./2025, em out./2025. Setembro de 2025 não se fraciona.

**Gaps intransponíveis (não preencher por invenção):**

- Tábua de mortalidade do IBGE: não capturada → fator previdenciário sai como fórmula.
- Fórmula do fator previdenciário (Anexo da Lei 9.876/1999): imagem na fonte; só as variáveis estão em texto.
- Anexo IV do Decreto 3.048 com o limite de ruído vigente em número: não automatizar; ler o anexo e exigir a prova técnica (PPP amparado em laudo; LTCAT quando o PPP for insuficiente — IN 128, art. 281, §4º).
- Anexos da IN 128/2022: não capturados.
- Ato ministerial vigente da lista de doenças que dispensam carência (Lei 8.213, art. 26, II): não conferido; a dispensa entra só quando o advogado marca.
- Regulamento do art. 20, §11-A, da LOAS (ampliação até 1/2 salário mínimo): não conferido; sem ampliação automática.
- Lei 9.289/1996 (custas na Justiça Federal): não capturada; isenção do INSS na Justiça Federal indeterminada.
- Acumulação do auxílio-acidente com auxílio temporário: fechadas só a vedação com aposentadoria (Lei 8.213, art. 86, §§1º e 2º) e a suspensão na reabertura pelo mesmo acidente (Decreto 3.048, art. 104, §6º); as demais combinações seguem indeterminadas.
- Série de juros da poupança (maio/2012 a nov./2021) e taxa legal depois de maio/2026 sem tabela do CJF: fórmula.
- MP 316/2006 e DL 2.322/1987: **capturados** (`context/lei/mp-316-2006.md` e `context/lei/dl-2322-1987.md`). A MP vem toda riscada na fonte porque foi convertida na Lei 11.430/2006, cujo texto é o vivo. O DL, art. 3º, fala em créditos **trabalhistas** e juros **capitalizados mensalmente**: o "1% ao mês simples" previdenciário até jun./2009 é regra do Manual (item 4.3.2), não da letra do DL.
- Dispositivo exato da duração da cota de pensão por morte (Lei 8.213, art. 77): conferir no anexo antes de citar.
- **RPPS e previdência complementar:** capturados a LC 108/2001 (`lc-108-2001.md`), a LC 109/2001 (`lc-109-2001.md`) e a Lei 9.717/1998, regras gerais dos RPPS (`lei-9717-1998-rpps.md`), além de CF, arts. 40 e 202 (`cf88-seguridade.md`), e EC 103, arts. 4º, 10 e 20, para o servidor federal; cita-se só o dispositivo achado no arquivo (mapa no `INDICE.md`). Lei própria de RPPS de estado ou município não está em `context/lei/`: sem ela, a skill não cita dispositivo dela, faz checklist de documentos e de questões e declara o gap. A LC 142/2013 (pessoa com deficiência) também está capturada (`lc-142-2013-pcd.md`); o que falta ali é script, não texto.
- **Fora do escopo dos scripts na 2.0.3:** cálculo do RPPS, aposentadoria da pessoa com deficiência (LC 142/2013) e pensão por morte.

---

## 9. ⏰ O RELÓGIO DO DOMÍNIO

| Prazo ou marco | Como conta | Fonte |
|---|---|---|
| **Recurso ao CRPS** | 30 dias, da ciência (intimação) da decisão. Contrarrazões: 30 dias, com prazo fatal contado da ciência (intimação) da interposição do recurso pela parte contrária; o Decreto conta "da interposição do recurso", tensão textual registrada: a data contada da interposição serve só como **meta preventiva**, nunca para declarar o prazo vencido enquanto o da intimação está aberto; sem a data da intimação, tempestividade indeterminada | `in-128-2022-inss.md`, art. 580; `regimento-crps-portaria-mps-125-2026.md`, arts. 77 e 78; `decreto-3048-1999.md`, art. 305, §1º, II e III |
| **Início do auxílio por incapacidade temporária (DIB)** | empregado, **exceto o doméstico**: 16º dia do afastamento se requerido até o 30º dia da DAT, senão DER. Demais segurados, **inclusive o doméstico**: DII se requerido até 30 dias da DAT ou da cessação das contribuições, senão DER. Em todos, DII posterior prevalece. DAT, DII e DER nunca se confundem | `lei-8213-1991.md`, art. 60, caput e §1º; `in-128-2022-inss.md`, art. 336, I e II |
| **Período de graça** | em gozo de benefício (exceto auxílio-acidente), sem limite; 12 meses após cessar as contribuições; 24 com mais de 120 contribuições sem perda; +12 para o desempregado com registro; 6 para o facultativo; segregação, reclusão e serviço militar nos incisos III a V | `lei-8213-1991.md`, art. 15 |
| **Perda da qualidade** | dia seguinte ao vencimento da contribuição relativa ao mês posterior ao fim da graça; vencimento no dia 15 do mês seguinte; sem expediente bancário, dia útil seguinte | `decreto-3048-1999.md`, art. 14; `lei-8212-1991.md`, art. 30, II e §2º, I |
| **Decadência da revisão** | 10 anos, do dia 1º do mês seguinte ao do primeiro recebimento; vence no dia de igual número. Não há decadência para a concessão inicial | `lei-8213-1991.md`, art. 103, I; `cc-excertos-prev.md`, art. 132, §3º; `temas-sumulas-prev.md`, STF Tema 313 |
| **Prescrição das parcelas** | 5 anos, de quando cada parcela deveria ter sido paga; ressalvados menores, incapazes e ausentes | `lei-8213-1991.md`, art. 103, parágrafo único |
| **Conversão do especial** | só tempo trabalhado até 13/11/2019, inclusive | `ec-103-2019.md`, art. 25, §2º |
| **Vigência da EC 103** | 13/11/2019 (marco do direito adquirido e das transições) | `ec-103-2019.md`, arts. 3º e 36 |
| **Progressão anual das transições** | +1 ponto (art. 15) e +6 meses de idade (art. 16; idade da mulher no art. 18) a cada 1º de janeiro, desde 2020, **até os limites**: pontos 105 (H) / 100 (M); idade do art. 16, 65 (H) / 62 (M); idade da mulher do art. 18, 62. Professor: pontos até 100 (H) / 92 (M); idade do art. 16, §2º, até 60 (H) / 57 (M). Arts. 17, 20 e 21 não progridem | `ec-103-2019.md`, arts. 15, 16 e 18 |
| **Divisor mínimo de 108** | aposentadorias com fato gerador a partir de 05/05/2022 | `in-128-2022-inss.md`, art. 228, §4º |
| **Vida toda — modulação** | irrepetibilidade: valores percebidos por decisões prolatadas até 05/04/2024; isenção de sucumbência, custas e perícia: ações pendentes de conclusão nessa data | `temas-sumulas-prev.md`, STF Tema 1.102 |
| **Fatias de atualização** | competências: até nov./2021 · dez./2021 a ago./2025 · desde set./2025 | `manual-cjf-2026-calculos-prev.md`, itens 4.3.1.1 e 4.3.2 |
| **Alçada do JEF** | fixada na distribuição | `cpc-excertos-prev.md`, art. 43; `lei-10259-2001-jef.md`, art. 3º |
| **Recursos no rito comum** | dias úteis; 15 dias para apelação, REsp e RE; 5 para embargos de declaração, que interrompem o prazo dos demais; a Fazenda (o INSS) tem prazo em dobro | `cpc-recursos-prazos-prev.md`, arts. 183, 219, 1.003 (§5º), 1.023 e 1.026 |
| **Recursos no JEF** | dias úteis; recurso inominado em 10 dias da ciência da sentença; embargos de declaração em 5 dias, com interrupção; **sem prazo diferenciado para o INSS** | `lei-9099-1995.md`, arts. 12-A, 42, 49 e 50; `lei-10259-2001-jef.md`, arts. 1º e 9º |
| **Mandado de segurança** | decadência de 120 dias da ciência do ato impugnado | `lei-12016-2009-ms.md`, art. 23 |
| **Impugnação do INSS ao cumprimento** | 30 dias no CPC; no JEF, sem prazo diferenciado para a Fazenda | `cpc-excertos-prev.md`, art. 535; `lei-10259-2001-jef.md`, art. 9º |
| **RPV** | JEF: 60 dias da entrega da requisição; CPC: 2 meses da entrega; sem juros de mora nesse prazo | `lei-10259-2001-jef.md`, art. 17; `cpc-excertos-prev.md`, art. 535, §3º, II; `manual-cjf-2026-calculos-prev.md`, cap. 5, Nota 2 |
| **Precatório** | apresentado até 1º de fevereiro → pago até o fim do exercício seguinte; sem juros de mora se pago em dia | `cf88-seguridade.md`, art. 100, §5º; `res-cjf-983-2026.md`, art. 7º, §2º |
| **Piso e teto** | mudam todo ano em janeiro; 2026: piso R$ 1.621,00 e teto R$ 8.475,55 | `decreto-12797-2025-salario-minimo.md`; `portaria-interministerial-mps-mf-13-2026.md`, art. 2º |

Os prazos processuais em dias são contados pelo motor de prazo (§13), nunca de cabeça. O motor não tem rito JEF: usa o rito do CPC e o aviso de que no JEF não há prazo diferenciado para a Fazenda.

---

## 10. 🔴 GATE DE REVERIFICAÇÃO DE VIGÊNCIA — antes de cada publicação e de cada peça que dependa do item

| # | Item | O que checar |
|---|---|---|
| 1 | ADI 7.873 (EC 136/2025) | mérito julgado? liminar? muda a fase do requisitório |
| 1-A | Manual de Cálculos da Justiça Federal e resoluções do CJF | nova edição? nova tabela da taxa legal com dedução do INPC depois de maio/2026? alteração da Res. CJF 983/2026? |
| 2 | STF Tema 1.102 | os embargos de 17/03/2026 foram julgados? a modulação mudou? |
| 3 | Salário mínimo e teto do RGPS | ano novo publicado? recapturar o decreto do salário mínimo e a portaria interministerial de janeiro |
| 4 | Lei que "discipline o cálculo" (EC 103, art. 26, caput) | lei nova substitui a regra transitória do art. 26 |
| 5 | Portaria DIRBEN/INSS 990/2022, Anexo V | nova alteração da tabela de indicadores do CNIS |
| 6 | Cache de índices do motor de atualização | `data_captura` e intervalo dentro da validade |
| 7 | Lei 8.213, art. 103 | a fonte remete à ADI 6.096 ("Vide ADIN 6096"), não capturada: conferir antes de afirmar decadência sobre indeferimento, cancelamento ou cessação |

Acionado pela `suprema-corte-previdenciaria` (R2). Item 🔴 sem reverificação entra na peça como "a confirmar", nunca como fato.

---

## 11. FRONTEIRAS — cross-link soft, NÃO duplicar

Cálculo judicial genérico e auditoria de laudo → `calculosjudiciais-adv-os` · busca de jurisprudência ao vivo → `juris-adv-os` · reconhecimento de vínculo para o CNIS → `trabalhista-adv-os`.

**OUT — gap declarado na 2.0.3:** cálculo do RPPS; previdência complementar além do que estiver capturado em `context/lei/`; aposentadoria da pessoa com deficiência (LC 142/2013) e pensão por morte sem script; limite de ruído do Anexo IV em número; fator previdenciário em número (sem a tábua do IBGE).

---

## 12. MAPA DOS ANEXOS `context/`

**Lei seca e jurisprudência (`context/lei/`)** — sempre **grep o artigo e leia a faixa**:

| Anexo | Conteúdo | Como usar |
|---|---|---|
| `lei/INDICE.md` | mapa tema → diploma → artigo, pelos 7 scripts | primeiro passo para achar o dispositivo |
| `lei/ec-103-2019.md` | EC 103/2019 integral (~84 KB) | arts. 3º, 15–21, 25, 26 |
| `lei/lei-8213-1991.md` | Lei 8.213/1991 compilada (~336 KB) | descartar linhas `(revogado)` |
| `lei/lei-8212-1991.md` | Lei 8.212/1991 compilada (~322 KB) | art. 30 (vencimento) |
| `lei/decreto-3048-1999.md` | Decreto 3.048/1999 com Anexos I a V (~851 KB) | homônimos (§7.1) |
| `lei/decreto-3048-art188p-tabela.md` | multiplicadores do art. 188-P, §5º, em texto | tabela de conversão |
| `lei/in-128-2022-inss.md` | IN PRES/INSS 128/2022 compilada (~930 KB) | arts. 206–208, 228, 233, 265, 336 |
| `lei/portaria-990-2022-anexo-v-indicadores-cnis.md` | indicadores do CNIS (~604 KB) | grep pela sigla |
| `lei/lei-8742-1993-loas.md` | LOAS | arts. 20 e 20-B |
| `lei/lei-10259-2001-jef.md` | Lei dos JEFs | arts. 3º, 9º, 17 |
| `lei/cf88-seguridade.md` | CF: arts. 40, 100, 194–204; ADCT | arts. 100 e 201 |
| `lei/ec-113-2021.md`, `lei/ec-136-2025.md` | requisitórios e Selic | redação original riscada = período até ago./2025 |
| `lei/lei-9876-1999.md`, `lei/lei-13846-2019.md`, `lei/lei-14331-2022.md`, `lei/lei-9494-1997.md`, `lei/lei-11430-2006.md`, `lei/lei-11960-2009.md` | leis de cálculo e de atualização | marcos de vigência |
| `lei/cpc-excertos-prev.md`, `lei/cc-excertos-prev.md` | CPC arts. 43, 292, 534, 535; CC arts. 132, 389, 406 | valor da causa, prazos, taxa legal |
| `lei/manual-cjf-2026-calculos-prev.md` | Manual CJF, julho/2026 (vigente) | itens 4.1–4.3 e cap. 5 |
| `lei/manual-cjf-calculos-prev.md` | Manual CJF, edição 2025 | só períodos históricos |
| `lei/res-cjf-983-2026.md` | requisições de pagamento | arts. 3º, 7º, 16 |
| `lei/decreto-12797-2025-salario-minimo.md`, `lei/decreto-12342-2024-salario-minimo.md`, `lei/portaria-interministerial-mps-mf-13-2026.md`, `lei/decreto-10695-2021-abono.md` | piso, teto e abono | valores com data |
| `lei/temas-sumulas-prev.md` | teses literais de STF, STJ, TNU e SV 47 | só citar o que está lá; ✅ cita, 🔴 "a confirmar", ❌ nunca |

**Anexos do plugin:**

| Anexo | Conteúdo | Quem lê |
|---|---|---|
| `metodologia-previdenciario.md` | este arquivo | o master primeiro; todas |
| `grafo-orquestracao.md` | quem chama quem, gerado das skills | master, Corte |
| `calculo-cnis.md`, `calculo-tempo.md`, `calculo-transicao.md`, `calculo-incapacidade.md`, `calculo-rmi.md`, `calculo-valor-causa.md`, `calculo-rpv.md` | conta aberta de cada script: fórmula com fonte de cada termo, tabela de passos, caso resolvido à mão, lista de `CAMPOS` da entrada, aviso "conta não conferida por script" | skills que calculam |
| `escrita-humana.md` | regras de escrita sem marca de IA | skills que redigem; Corte (R4) |

---

## 13. 🧮 SCRIPTS — o que existe, onde fica, como achar

**Todos em `scripts/calc/`** na raiz do plugin. Nunca chamados por hook; só pela skill, via Bash.

| Script | Conta | Skills consumidoras |
|---|---|---|
| `calc_previdenciario_cnis.py` | carência, qualidade de segurado, indicadores | `analise-cnis`, `triagem-dogmatica-previdenciario`, `administrativo-inss-crps` |
| `calc_previdenciario_tempo.py` | tempo comum, especial convertido até 13/11/2019, concomitância | `analise-ppp-ltcat-aposentadoria-especial`, `calculos-previdenciarios`, `planejamento-previdenciario` |
| `calc_previdenciario_transicao.py` | direito adquirido, arts. 15–21, regra permanente | `estrategia-de-caso-previdenciario`, `calculos-previdenciarios`, `peticao-inicial-previdenciaria`, `planejamento-previdenciario` |
| `calc_previdenciario_incapacidade.py` | temporária, permanente, auxílio-acidente, DIB | `pericia-medica-previdenciaria`, `acidentario-do-trabalho` |
| `calc_previdenciario_rmi.py` | RMI de concessão e revisão, divisor 108, descarte, decadência, prescrição | `acao-revisional-rmi`, `analise-carta-concessao-indeferimento`, `calculos-previdenciarios`, `planejamento-previdenciario` |
| `calc_previdenciario_valor_causa.py` | vencidas + 12 vincendas, alçada do JEF | `peticao-inicial-previdenciaria`, `bpc-loas-previdenciario` |
| `calc_previdenciario_rpv.py` | atrasados por fatia de regime, honorários, RPV × precatório | `cumprimento-sentenca-inss` |
| `calc_previdenciario_atualizacao.py` | motor de atualização (cópia conferida por sha256) | chamado pelos scripts de valor da causa e RPV |
| `calc_previdenciario_prazo.py` | motor de prazo em dias (cópia conferida por sha256) | `prazos-previdenciarios`; scripts de RMI e RPV |

Tabelas próprias em `scripts/data/` (com `fonte`, `data_captura`, `intervalo` e `validade`; valor sem fonte = `null`); índices do motor de atualização em `scripts/data/indices/`; feriados do motor de prazo em `scripts/calc/data/`. O hub `calculos-previdenciarios` atende o pedido avulso de qualquer conta.

**Contrato de chamada.** Entrada em JSON, por `--entrada <arquivo>` ou pela entrada padrão; `--versao` imprime a versão. Campo desconhecido é recusado. Cada skill que calcula declara os blocos `flags` e `campos`, iguais à lista de `CAMPOS` do `context/calculo-<x>.md`. A saída é JSON com `parametros_usados`, `regra` e `fonte` de cada número, `versao`, `memoria` passo a passo e `formula_aberta`.

**Códigos de saída:**

| Código | Significa | A skill faz |
|---|---|---|
| 0 | calculado | usa o resultado e mostra a memória |
| 2 | entrada inválida | pergunta de novo ao advogado o dado errado |
| 3 | falta dado ou tabela, ou o texto legal não fecha | entrega a `formula_aberta` preenchida até onde dá, com `[VERIFICAR]` e as duas leituras quando houver |

Qualquer outro código, ou script ausente, ou Python ausente: conta aberta pelo `context/calculo-<x>.md`, dizendo que o número **não foi conferido por script**.

**Como a skill acha o script** (o `CLAUDE_PLUGIN_ROOT` chega vazio no Bash do Cowork; nenhum passo depende dele):

1. **Pasta base da skill → `scripts/calc/`:** `<pasta-base>/../../scripts/calc/calc_previdenciario_<x>.py`.
2. **Se não existir, busca pelo nome único**, primeiro na pasta do usuário e depois na raiz.
3. **Se a busca devolver mais de um arquivo** (versões antigas em cache depois de atualizar), rodar `--versao` em cada um e usar o que bate com **2.0.3**. Nenhum bate: conta aberta e aviso.
4. **Nada funcionou:** conta aberta.

```bash
N='calc_previdenciario_<x>.py'
achar() { find "$1" -name "$N" -path '*/scripts/calc/*' -print0 2>/dev/null; }
{ achar "$HOME"; } | while IFS= read -r -d '' f; do printf '%s\t' "$f"; python3 "$f" --versao; done
# nada achado em $HOME: repetir com achar /
# caminhos com espaco (ex.: Application Support) passam inteiros: -print0 + read -d ''
```

---

## 14. ✍️ JARGÃO LEGÍTIMO DO DOMÍNIO — o que o anti-IA não reprova

Termos técnicos do previdenciário que o crivo anti-IA (R4) não conta como marca de texto gerado:

DER, DIB, DIP, DII, DCB, RMI, RMA, SB, SC, PBC, NB, CNIS, CTPS, PPP, LTCAT, EPI, NTEP, CAT, B31, B32, B91, B92, B94, B87/B88, B41, B42, B46, B21, JEF, PFE, CRPS, JR, TNU, PEDILEF, RPV, período de graça, qualidade de segurado, carência, período básico de cálculo, fator previdenciário, pedágio, regra de transição, direito adquirido, reafirmação da DER, tempo especial, conversão, enquadramento por categoria, habitualidade e permanência, auxílio por incapacidade temporária, aposentadoria por incapacidade permanente, auxílio-acidente, abono anual, miserabilidade, grupo familiar, impedimento de longo prazo.
