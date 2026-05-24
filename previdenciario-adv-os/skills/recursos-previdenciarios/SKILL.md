---
name: recursos-previdenciarios
description: >
  RECURSOS PREVIDENCIARIOS — Skill consolidada para producao de qualquer recurso previdenciario judicial. Identifica instancia automaticamente pelo contexto: Recurso Inominado JEF (10 dias), Apelacao TRF (15 dias), Recurso Especial STJ (15 dias com Filtro Anti-Sumula 7), Recurso Extraordinario STF (15 dias com Repercussao Geral), Pedido de Uniformizacao TNU (PEDILEF, 10 dias), Embargos de Declaracao (5 dias), Contrarrazoes (qualquer instancia). Aplica jurisprudencia especifica da instancia (Sumulas TNU, Temas STJ, Repercussao Geral STF). Use quando operador disser "recurso", "recorrer", "Turma Recursal", "TRF", "REsp", "RE", "PEDILEF", "embargos", "contrarrazoes", ou via /recurso-previdenciario.
---

# RECURSOS PREVIDENCIARIOS — Skill Tier 2 A (consolidada)

> Cobre TODA cadeia recursal: JEF -> TRF -> STJ -> STF + PEDILEF (TNU) + embargos + contrarrazoes.

---

## 1. TABELA DE PRAZOS POR INSTANCIA

| Recurso | Prazo | Base legal |
|---------|-------|------------|
| Recurso Inominado JEF | 10 dias | art. 5o Lei 10.259/2001 |
| Apelacao TRF | 15 dias | art. 1.003 §5o CPC |
| REsp (STJ) | 15 dias | art. 1.003 §5o CPC + art. 105 III CF |
| RE (STF) | 15 dias | art. 1.003 §5o CPC + art. 102 III CF |
| PEDILEF (TNU) | 10 dias | art. 14 Lei 10.259/2001 |
| Embargos de Declaracao | 5 dias | art. 1.023 CPC |
| Contrarrazoes | mesma do recurso | conforme cada instancia |
| Recurso administrativo INSS (Junta de Recursos) | 30 dias | art. 305 IN 128/2022 |

---

## 2. RECURSO INOMINADO JEF (Lei 10.259/2001)

**Cabivel:** sentenca do Juizado Especial Federal (causas ate 60 SM).

**Estrutura:**

```
EXCELENTISSIMO SENHOR DOUTOR JUIZ FEDERAL DA <vara JEF>

Processo n. <numero>
Recorrente: <nome>
Recorrido: INSS

<NOME>, ja qualificado, vem, com fulcro no art. 5o da Lei 10.259/2001,
no prazo legal de 10 dias, oferecer

RECURSO INOMINADO

para a Egregia Turma Recursal dos Juizados Especiais Federais da Secao
Judiciaria de <cidade>/<UF>, em face da r. sentenca de <data>, pelas
razoes em anexo.

Local, data.
<advogado> OAB/<UF> <numero>
```

**Razoes — estrutura FIRAC por erro da sentenca:**

```
RAZOES DE RECURSO INOMINADO

I. SINTESE
II. TEMPESTIVIDADE
III. RAZOES DA REFORMA
   III.1 — <erro 1>
     F: <fato consolidado>
     I: <questao>
     R: <fundamento>
     A: <subsuncao>
     C: <conclusao>
   III.2 — <erro 2>
   III.N — ...
IV. PEDIDO
   - Conhecimento e provimento
   - Reforma da sentenca
   - DIB + correcao + juros + Sumula 111 STJ
```

**Atencao:** buscar precedentes da PROPRIA Turma Recursal + Sumulas TNU + Temas STJ.

---

## 3. APELACAO TRF (CPC art. 1.009)

**Cabivel:** sentenca de Vara Federal Comum.

**Estrutura mais densa que recurso JEF:**

```
EXCELENTISSIMO SENHOR DOUTOR JUIZ FEDERAL DA <vara federal>

[interpor apelacao]

RAZOES DE APELACAO ao Egregio TRF da <X> Regiao:

I. SINTESE PROCESSUAL E DECISAO RECORRIDA
II. PRELIMINARES (se houver)
III. TEMPESTIVIDADE
IV. RAZOES DA REFORMA (FIRAC ampliado por erro)
V. ANTECIPACAO DE TESES DA PFE EM CONTRARRAZOES
VI. PEDIDO
```

**Atencao redobrada:** Acordaos da Turma Previdenciaria do TRF da regiao do operador (consistencia decisoria).

---

## 4. RECURSO ESPECIAL (STJ — art. 105 III CF)

**Cabivel:** acordao de TRF.

**Filtro Anti-Sumula 7 (PA-16) — OBRIGATORIO:**

```
Sumula 7 STJ:
  "A pretensao de simples reexame de prova nao enseja recurso especial."
```

Toda PFE em REsp tenta invocar Sumula 7. Antes de redigir, verificar:
- [ ] A controversia e SOBRE A LEI? (Sim -> REsp cabe)
- [ ] Demonstrar que NAO e reexame factico:

```
Esclareca-se, ab initio, que o presente recurso especial NAO pretende
reexame de prova. As questoes aqui controvertidas sao exclusivamente de
DIREITO, a saber: <listar questoes juridicas puras>. Os fatos foram
consolidados pelo acordao recorrido e sao TIDOS COMO INCONTROVERSOS
nesta sede recursal.
```

**Estrutura:**

```
RAZOES DE RECURSO ESPECIAL ao Colendo STJ:

I. SINTESE PROCESSUAL
II. TEMPESTIVIDADE
III. CABIMENTO
   III.1 — Hipotese (alinea a/c art. 105 III CF)
   III.2 — DEMONSTRACAO DE QUE NAO HA REEXAME (Filtro Anti-Sumula 7)
   III.3 — Prequestionamento
   III.4 — Tema Repetitivo STJ aplicavel (se houver)
IV. FUNDAMENTOS DA REFORMA
V. PEDIDO
```

**Temas STJ frequentes:**
- Tema 416 (pericia oficial)
- Tema 692 (aposentadoria por idade hibrida)
- Tema 999 (decadencia art. 103)
- Tema 1041 (conversao tempo especial pos-EC 103)
- Tema 1023 (BPC e renda per capita)

---

## 5. RECURSO EXTRAORDINARIO (STF — art. 102 III CF)

**Cabivel:** violacao DIRETA a CF (nao reflexa).

**Repercussao Geral OBRIGATORIA (CPC 1.035):**

Demonstrar 4 vetores:
- Relevancia economica
- Relevancia social
- Relevancia juridica
- Relevancia politica

**Estrutura:**

```
RAZOES DE RE ao Egregio STF:

I. SINTESE
II. TEMPESTIVIDADE
III. CABIMENTO
   III.1 — Dispositivo constitucional violado
   III.2 — Violacao DIRETA (nao reflexa)
   III.3 — Prequestionamento
IV. REPERCUSSAO GERAL (CPC 1.035) — 4 vetores
V. FUNDAMENTOS DA REFORMA
VI. PEDIDO
```

**Temas STF Repercussao Geral previdenciarios:**
- Tema 313 (acumulacao de aposentadorias)
- Tema 350 (RE 631.240 — previo requerimento)
- Tema 503 (desaposentacao)
- Tema 692 (RG da vida toda)
- Tema 942 (averbacao tempo)
- Tema 1102 (vida toda — merito)
- Tema 1124 (aposentadoria PCD pos-EC 103)

---

## 6. PEDILEF — TNU (Lei 10.259/2001 art. 14)

**Cabivel:**
- Acordao de Turma Recursal divergente de outra Turma Recursal
- Acordao contrario a sumula TNU
- Acordao contrario a jurisprudencia dominante STJ

**Estrutura:**

```
PEDIDO DE UNIFORMIZACAO DE INTERPRETACAO DE LEI FEDERAL a TNU:

I. SINTESE
II. TEMPESTIVIDADE
III. CABIMENTO E DEMONSTRACAO DA DIVERGENCIA
   III.1 — Tese fixada pelo acordao recorrido
   III.2 — Tese divergente do paradigma (Sumula TNU n. X / acordao)
   III.3 — Identidade factica e juridica
IV. RAZOES DA UNIFORMIZACAO
V. PEDIDO
```

**Sumulas TNU:**
- Sumula 41 — beneficio assistencial
- Sumula 47 — fungibilidade auxilio-doenca/aposentadoria por incapacidade
- Sumula 50 — averbacao tempo
- Sumula 79 — pericia medica e quesitos do segurado

---

## 7. EMBARGOS DE DECLARACAO (CPC 1.022, prazo 5 dias)

**Hipoteses:**
- I — Omissao
- II — Contradicao
- III — Obscuridade
- IV — Erro material

**Atencao:** embargos NAO servem para rediscutir merito. Efeitos infringentes apenas em casos excepcionais.

**CPC 1.026 §2o:** embargos protelatorios = multa de 2% sobre valor da causa.

**Estrutura:**

```
EMBARGOS DE DECLARACAO:

I. SINTESE
II. DO VICIO A SANAR
   II.1 — Omissao / Contradicao / Obscuridade / Erro material
III. PEDIDO
   - Sanamento + (se cabivel) efeitos infringentes
IV. PREQUESTIONAMENTO (se fase recursal)
```

---

## 8. CONTRARRAZOES (qualquer instancia)

**Quando:** INSS interpoe recurso contra decisao favoravel ao segurado.

**Tom:** defensivo + adversarial — manter o que foi conquistado.

**Estrutura:**

```
CONTRARRAZOES:

I. SINTESE
II. REFUTACAO PONTO A PONTO DO RECURSO DA PFE
   - Cada argumento da PFE -> FIRAC inverso
   - Distinguishing das sumulas citadas
III. REFORCO DA DECISAO RECORRIDA
IV. PEDIDO DE IMPROVIMENTO
```

**Em STJ:** atacar Sumula 7 do PROPRIO STJ contra a PFE quando ela pede reexame factico (PA-16 inverso).

---

## 9. ESCOLHA AUTOMATICA DE INSTANCIA (decision tree)

```
Decisao recorrida e de:
├── JEF (Vara) -> Recurso Inominado a Turma Recursal (10 dias)
├── Vara Federal Comum -> Apelacao TRF (15 dias)
├── Turma Recursal -> ?
│   ├── Materia de DIREITO -> REsp (15 dias)
│   ├── Materia constitucional -> RE (15 dias)
│   └── Divergencia entre TRs ou contra Sumula TNU -> PEDILEF (10 dias)
├── TRF -> ?
│   ├── Materia de lei federal -> REsp (15 dias)
│   └── Materia constitucional -> RE (15 dias)
└── Decisao com vicio (omissao/contradicao/etc.) -> Embargos de Declaracao (5 dias)
```

---

## 10. PAS APLICAVEIS

- **PA-01** — jurisprudencia classificada Nivel 1/2/3
- **PA-04** — adversarial
- **PA-11** — Nivel 4
- **PA-15** — competencia
- **PA-16** — Filtro Anti-Sumula 7 em REsp
- **PA-22** — Suprema Corte antes de entregar

---

## 11. PROTOCOLOS ACIONADOS

- **2.1** Jurisprudencial (Temas, Sumulas, classificacao 3 niveis)
- **2.5** Compartimentacao (escopo: recurso processual)

---

## 12. CHECKLIST DE SAIDA

- [ ] Tempestividade verificada conforme instancia
- [ ] Estrutura adequada a instancia (sintese, fundamentos, pedido)
- [ ] FIRAC por erro da decisao recorrida
- [ ] Jurisprudencia Nivel 1 obrigatoria (Temas/Sumulas)
- [ ] Filtro Anti-Sumula 7 (REsp) ou Repercussao Geral (RE)
- [ ] Distinguishing das sumulas adversas (contrarrazoes)
- [ ] Pedido especifico de provimento/improvimento
- [ ] Honorarios + Sumula 111 STJ
- [ ] Rodape OAB

---

*Skill recursal universal. Acionar conforme contexto.*
