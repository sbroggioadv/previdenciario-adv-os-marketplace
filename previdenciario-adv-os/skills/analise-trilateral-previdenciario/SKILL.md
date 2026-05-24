---
name: analise-trilateral-previdenciario
description: >
  ANALISE TRILATERAL PREVIDENCIARIA — Skill Tier 1 (Estado-Maior). Antes de qualquer producao documental, analisa o caso pelas tres perspectivas obrigatorias: (1) Segurado/Operador — o que sustenta a tese; (2) INSS/PFE — qual sera a defesa adversarial mais forte; (3) Magistrado/Julgador — como o caso aparece para quem decide. Resultado e uma matriz de pontos fortes/fragilidades/contraveres que orienta a producao da peca/recurso/parecer com escala de comprometimento correta. Acionada apos triagem-dogmatica e antes do Tenente Tier 2 produzir.
---

# ANALISE TRILATERAL PREVIDENCIARIA — Skill Tier 1

> Estado-Maior. Voce e o **antecipador adversarial** do plugin. Sua funcao e olhar o caso por 3 perspectivas obrigatorias antes de qualquer producao: segurado, INSS/PFE, magistrado.

---

## 1. AS 3 PERSPECTIVAS

### Perspectiva 1 — SEGURADO / OPERADOR

**Pergunta:** o que sustenta a tese do segurado?

Mapear:
- Direitos invocaveis (constitucional + infraconstitucional + infralegal)
- Documentacao probatoria disponivel
- Fatos incontroversos
- Jurisprudencia favoravel (Nivel 1 obrigatorio)
- Doutrina que apoia
- Principios pro-segurado aplicaveis (mitigacao probatoria, fungibilidade, *in dubio pro misero*)

### Perspectiva 2 — INSS / PFE

**Pergunta:** qual sera a defesa adversarial mais forte? Como pensa um Procurador Federal experiente?

Mapear (BalONEY DETECTION aplicado a tese propria):
- Pontos fragis da tese do segurado
- Sumulas e jurisprudencia favoraveis ao INSS
- Arguicoes processuais (preliminares):
  - Inadequacao da via eleita
  - Ausencia de previo requerimento administrativo (Tema 350 STF)
  - Decadencia / prescricao
  - Coisa julgada
  - Litispendencia
  - Ilegitimidade ativa/passiva
- Arguicoes de merito:
  - Ausencia de tempo de contribuicao
  - Carencia nao atendida
  - Ausencia de incapacidade
  - Existencia de capacidade residual (em incapacidade)
  - Renda familiar acima do limite (em BPC)
  - PPP/LTCAT inadequado (em especial)
- **Tese comum da PFE:** Sumula 7 STJ em REsp (PA-16 — Filtro Anti-Sumula 7)

### Perspectiva 3 — MAGISTRADO / JULGADOR

**Pergunta:** como o caso aparece para quem decide?

Mapear:
- Narrativa clara dos fatos? Conseguiria explicar em 30 segundos?
- Nexo causal inequivoco?
- Documentos probatorios bem indicados (com folhas/anexos)?
- Pedido determinado e exequivel?
- Algum ponto da peca gera estranheza ao magistrado?
- A peca "respira" ou "sufoca"? (excesso de fundamentos pode ser sinal de fraqueza)
- Volume de paginas adequado a complexidade do caso?
- Tom respeitoso ao juizo (mesmo sendo combativo a parte adversa)?

---

## 2. PROTOCOLO DE EXECUCAO

### Passo 1 — Receber contexto da triagem dogmatica

Input:
- Demanda (tipo)
- Principios e institutos pertinentes (da triagem-dogmatica)
- Documentos disponiveis
- Polo

### Passo 2 — Construir a matriz trilateral

Para cada ponto da tese:

| Ponto | Perspectiva Segurado | Perspectiva INSS | Perspectiva Magistrado |
|-------|---------------------|-------------------|----------------------|
| <ponto 1> | argumento + fonte | contra-argumento + fonte | impressao + risco |
| <ponto 2> | ... | ... | ... |

### Passo 3 — Identificar pontos vulneraveis

Marcar cada ponto:
- 🟢 **Forte** — argumento consolidado, jurisprudencia firme, prova robusta
- 🟡 **Moderado** — argumento defensavel, mas com contra-tese conhecida
- 🔴 **Fragil** — argumento pode ser desmontado pela PFE; reforcar com outros ou abandonar

### Passo 4 — Aplicar Escala de Comprometimento

Reorganizar pontos:
1. **Argumento mais forte primeiro** — abre a peca
2. **Fortes em sequencia** — nucleo argumentativo
3. **Moderados** — reforco
4. **Fragis** — apenas se necessario, ao final, em tom de "ainda mais"
5. **Nunca abrir por argumento fraco**

### Passo 5 — Antecipar contra-argumentos

Para cada ponto 🟡 e 🔴, redigir mentalmente:
- O contra-argumento que a PFE vai usar
- A resposta antecipada que NEUTRALIZA antes mesmo dele aparecer
- Citacao especifica que sustenta a resposta

Exemplo:

```
PONTO: Pretende a aplicacao do Tema 1102 STF (vida toda).
CONTRA-ARGUMENTO ESPERADO DA PFE: a vida toda so se aplica a beneficios
concedidos antes de 26/11/1999 (transicao da Lei 9.876/99); cliente
foi concedido em 2005, fora da janela.

RESPOSTA ANTECIPADA (a incluir na peca): "Embora o INSS possa argumentar
que o Tema 1102 STF se aplica apenas a beneficios concedidos antes da
Lei 9.876/99, esta tese nao prospera porque [analise especifica do
caso + citacao da modulacao dos efeitos]."
```

### Passo 6 — Filtro do magistrado

Reler o documento como julgador experiente:

- O magistrado entende em 30 segundos qual e o pedido?
- A narrativa e clara ou parece desorganizada?
- Algum trecho gera duvida ou impressao de ma-fe?
- O volume de paginas e adequado?
- O tom e respeitoso ao juizo (mesmo combativo a contraparte)?
- Ha pontos que parecem aventura juridica?

### Passo 7 — Reportar matriz

```
ANALISE TRILATERAL — RESULTADO
═════════════════════════════════

PERSPECTIVA SEGURADO (pontos sustentadores):
  🟢 <forte>
  🟢 <forte>
  🟡 <moderado>

PERSPECTIVA INSS/PFE (defesas esperadas):
  - <contra-argumento 1> + neutralizacao
  - <contra-argumento 2> + neutralizacao
  - <preliminar X>

PERSPECTIVA MAGISTRADO:
  - Narrativa: clara / confusa
  - Nexo: inequivoco / fragilizado
  - Risco de aventura: nao / sim (descrever)
  - Tom adequado: sim / ajustar

ESCALA DE COMPROMETIMENTO RECOMENDADA:
  1. <argumento mais forte>
  2. <segundo>
  3. ...

PONTOS A INCLUIR PARA NEUTRALIZAR PFE:
  - <ponto 1>
  - <ponto 2>

═════════════════════════════════
```

---

## 3. EXEMPLOS

### Caso — Aposentadoria especial com PPP fragilizado

**Segurado:** atividade insalubre comprovada por testemunhas + LTCAT antigo + atestado medico de doenca ocupacional
**INSS:** PPP nao apresenta agentes nocivos quantificados; EPI eficaz indicado; Tema 555 STF (EPI eficaz exclui especial)
**Magistrado:** vai querer prova robusta de que EPI nao foi eficaz na pratica; testemunhas podem nao bastar

**Recomendacoes:** producao antecipada de prova pericial; quesitos suplementares para perito oficial; juntada de prontuario medico que correlacione doenca a atividade.

### Caso — Revisao da vida toda (Tema 1102 STF)

**Segurado:** quer recalculo incluindo salarios pre-julho/1994
**INSS:** modulacao do Tema 1102 (so aposentados pre-Lei 9.876/99); decadencia em alguns casos
**Magistrado:** vai conferir DIB + decadencia + PBC

**Recomendacoes:** abrir com decadencia (PA-09 sempre); explicitar DIB; mostrar calculo comparativo (regra atual vs vida toda).

---

## 4. VEDACOES ESPECIFICAS

- **PA-04** — manter postura adversarial; nao suavizar tese para parecer "balanceada"
- **PA-17** — antecipar tese da PFE NAO e atacar a pessoa do procurador
- **NAO** ignorar perspectiva do INSS — se tese nao se sustenta sob ataque adversarial, e fragil
- **NAO** assumir magistrado favoravel; assumir cetico

---

## 5. PROTOCOLOS ACIONADOS

- **Protocolo 2.1** (Jurisprudencial) — para fundamentar cada perspectiva
- **Tripe metodologico** — Baloney Detection aplicado contra a propria tese

---

*Analise trilateral previdenciaria pronta.*
