---
name: acao-revisional-rmi
description: >
  ACAO REVISIONAL DE RMI — Skill Tier 2 A. Produz acao para revisar a Renda Mensal Inicial (RMI) de beneficio previdenciario ja concedido. Cobre revisao da vida toda (Tema 1102 STF), revisao do buraco negro (Lei 9.876/99), revisao por erro de calculo, revisao por inclusao de tempo nao computado, revisao de fator previdenciario, e outras. ATENCAO PA-09: SEMPRE abrir com verificacao de decadencia (art. 103 caput Lei 8.213/91 — 10 anos da DIB). Pipeline obrigatorio inclui Tema 999 STJ e analise comparativa de calculos. Use para qualquer revisao de RMI.
---

# ACAO REVISIONAL DE RMI — Skill Tier 2 A

> Revisar RMI de beneficio ja concedido. **PA-09 abre TODA analise: decadencia decenial.**

---

## 1. PA-09 — VERIFICACAO BLOQUEANTE

```
Lei 8.213/91, art. 103 caput:
  Decadencia DECENAL — 10 anos contados do primeiro dia do mes seguinte
  ao do recebimento da primeira prestacao do beneficio.

Tema 999 STJ:
  Confirma a decadencia decenal e estabelece marcos.
```

**Antes de qualquer producao:** calcular se prazo decadencial NAO foi consumado.

```
DIB: <data>
Inicio do prazo: <DIB + 1 dia do mes seguinte>
Termo final: <inicio + 10 anos>
Hoje: <data>

[ ] Dentro do prazo — pode revisar
[ ] Fora do prazo — investigar Tema 975 STJ (fato novo) ou recusar causa
```

Se fora do prazo, NAO redigir. Sinalizar ao operador.

---

## 2. ESPECIES DE REVISAO

### 2.1 Revisao da vida toda (Tema 1102 STF)

- **Cabivel para:** beneficios concedidos antes de 26/11/1999 (Lei 9.876/99) E em data dentro do prazo decadencial
- **Tese:** incluir salarios-de-contribuicao anteriores a julho/1994 no PBC
- **Atencao:** modulacao do Tema 1102 (verificar acórdão atualizado)

### 2.2 Revisao do buraco negro

- **Cabivel:** beneficios concedidos entre 1988 e 1991
- **Tese:** correcao monetaria das parcelas no periodo

### 2.3 Revisao por erro de calculo

- **Cabivel:** sempre dentro do prazo
- **Tese:** corrigir erro especifico (ex: PBC incorreto, fator previdenciario aplicado errado, periodos nao computados)

### 2.4 Revisao por inclusao de tempo

- **Cabivel:** quando ha tempo de contribuicao reconhecido judicialmente APOS a concessao
- **Tese:** recalcular RMI com tempo total

---

## 3. ESTRUTURA OBRIGATORIA

```
EXCELENTISSIMO SENHOR DOUTOR JUIZ FEDERAL DA <vara/JEF>


<NOME>, ja qualificado, vem, por seu advogado (procuracao anexa), com
fulcro nos arts. 319 e ss. do CPC c/c art. <X> da Lei 8.213/91, propor

ACAO REVISIONAL DE RENDA MENSAL INICIAL

em face do INSS, pelos fatos e fundamentos a seguir:

I. DOS FATOS

  - Beneficio: <tipo> NB <numero>
  - DIB: <data>
  - DIP (data de inicio dos pagamentos): <data>
  - RMI atual: R$ <valor>
  - Documentos: carta de concessao + CNIS

II. DA NAO CONSUMACAO DA DECADENCIA (PA-09)

  Nos termos do art. 103 caput da Lei 8.213/91 e do Tema 999 STJ,
  o prazo decadencial e DECENAL, contado do primeiro dia do mes
  seguinte ao recebimento da primeira prestacao.

  No caso, primeira prestacao em <data>; inicio do prazo em <data>;
  termo final em <data>. Acao proposta em <data> — DENTRO DO PRAZO.

III. DOS FUNDAMENTOS DA REVISAO

  III.1 — <especie de revisao>
    F: <fatos>
    I: <questao>
    R: <fundamento — Lei 8.213/91 + Tema 1102 STF (se vida toda) + ...>
    A: <subsuncao>
    C: <conclusao>

IV. DO CALCULO COMPARATIVO

  RMI ATUAL (regra de concessao): R$ <valor>
  RMI RECALCULADO (regra revisada): R$ <valor>
  DIFERENCA MENSAL: R$ <valor>

  [calculo detalhado em anexo — Protocolo 2.4]

V. DO PEDIDO

  Requer-se:

  a) A citacao do INSS;

  b) A producao de prova documental (calculos juntados) e pericial
     contabil (se necessaria);

  c) A PROCEDENCIA do pedido para CONDENAR o INSS a:
     - revisar a RMI do beneficio NB <numero>, fixando-a em R$ <novo>;
     - pagar as diferencas vencidas desde <data — observada a prescricao
       quinquenal art. 103 paragrafo unico>;
     - corrigir e atualizar (IPCA-E + SELIC);
     - pagar honorarios sucumbenciais (Sumula 111 STJ);
     - implantar a RMI revisada em folha.

Local, data.
<advogado> OAB/<UF> <numero>
```

---

## 4. PRESCRICAO QUINQUENAL DAS PARCELAS (art. 103 paragrafo unico)

Mesmo dentro do prazo decadencial, parcelas vencidas anteriores a 5 anos do ajuizamento estao prescritas:

```
Acao proposta em <data>
Parcelas vencidas desde <data - 5 anos>
Anteriores a essa data: PRESCRITAS (art. 103 paragrafo unico Lei 8.213/91)
```

---

## 5. PAS APLICAVEIS

- **PA-09** — verificacao de decadencia BLOQUEANTE (PRIMEIRA acao)
- **PA-13** — sem CNIS + carta concessao, paralisar
- **PA-20** — sem dados, calculo nao se faz
- **PA-22** — Suprema Corte

---

## 6. CHECKLIST DE SAIDA

- [ ] **Decadencia verificada e demonstrada como NAO consumada**
- [ ] CNIS + carta de concessao analisados
- [ ] Especie de revisao identificada
- [ ] Tema 1102 STF ou outro fundamento Nivel 1 citado
- [ ] Calculo comparativo (atual x revisado)
- [ ] Prescricao quinquenal observada
- [ ] Pedido especifico de revisao de RMI
- [ ] Honorarios + Sumula 111
- [ ] Rodape OAB

---

*Pronto. PA-09 e o primeiro filtro.*
