---
name: replica-previdenciaria
description: >
  REPLICA PREVIDENCIARIA — Skill Tier 2 A. Produz replica a contestacao do INSS em acao previdenciaria. Estrutura: identificacao do processo, refutacao ponto a ponto da contestacao (especialmente preliminares e arguicao de fatos incontroversos via art. 341 CPC), reforco da tese central, ataque a sumulas/jurisprudencia citadas pela PFE com distinguishing, conclusao com manutencao integral dos pedidos. Acionada apos contestacao do INSS ser apresentada nos autos. Tom adversarial mantido (PA-04). Use quando operador disser "replica", "responder contestacao do INSS", ou via comando.
---

# REPLICA PREVIDENCIARIA — Skill Tier 2 A

> Refuta a contestacao do INSS ponto a ponto, mantendo postura adversarial e neutralizando teses defensivas.

---

## 1. PIPELINE OBRIGATORIO

Mesmo do peticao-inicial: previdenciario-master → Estado-Maior (especial atencao ao analise-trilateral, agora com o conteudo CONCRETO da contestacao) → replica → transversais → Suprema Corte.

---

## 2. ESTRUTURA OBRIGATORIA

### 2.1 Cabecalho

```
EXCELENTISSIMO SENHOR DOUTOR JUIZ FEDERAL DA <vara>


Processo n. <numero>
Autor: <nome>
Reu: INSS

<NOME>, ja qualificado nos autos da acao em epigrafe, vem, por seu
advogado, no prazo legal (art. 350 CPC), oferecer

REPLICA

a contestacao apresentada pelo INSS, pelas razoes a seguir:
```

### 2.2 Fatos incontroversos (art. 341 CPC)

Listar fatos NAO impugnados especificamente pelo INSS — esses se tornam INCONTROVERSOS:

> Pela aplicacao do art. 341 do CPC, sao incontroversos os seguintes fatos
> nao impugnados especificamente na contestacao:
>
> a) <fato 1>
> b) <fato 2>
> c) <fato 3>

### 2.3 Refutacao das preliminares

**Preliminar de inadequacao da via:** desconstruir
**Preliminar de ausencia de previo requerimento:** apresentar comprovante
**Preliminar de decadencia:** demonstrar que prazo nao consumou
**Preliminar de coisa julgada:** distinguir do caso anterior
**Preliminar de litispendencia:** demonstrar inexistencia
**Preliminar de ilegitimidade:** desconstruir

Para cada preliminar levantada pelo INSS:
- Sintetizar o que a PFE alegou
- Refutar com fundamento legal + jurisprudencia
- Concluir pela rejeicao

### 2.4 Refutacao do merito

Para cada argumento de merito do INSS:

```
F: Alega o INSS que <tese da PFE>.
I: <questao>
R: <regra que refuta>
A: <subsuncao demonstrando improcedencia da tese da PFE>
C: <conclusao categorica>
```

**Atencao especial a sumulas/jurisprudencia da PFE:**

Aplicar **distinguishing**:

> Eventual citacao do <Tema/Sumula> nao se aplica ao caso porque <razoes
> tecnicas: distincao factica, modulacao temporal, contexto diverso>.

### 2.5 Reforco da tese central

Reafirmar a tese da inicial com vigor renovado, agora ja conhecendo a defesa:

> Demonstrado o equivoco das teses defensivas, resta inabalada a tese inaugural,
> que se sustenta em <fundamentos centrais reforcados>.

### 2.6 Conclusao

```
Diante do exposto, requer-se:

a) O acolhimento da presente replica;

b) A REJEICAO INTEGRAL das preliminares e do merito da contestacao;

c) A MANUTENCAO de todos os pedidos formulados na inicial;

d) O prosseguimento do feito com producao de provas <ja requeridas>.

Local, data.

<advogado>
OAB/<UF> <numero>
```

---

## 3. PAS APLICAVEIS

- **PA-04** — postura adversarial mantida
- **PA-11** — Nivel 4 nas refutacoes (sem "talvez")
- **PA-17** — combate a TESES, nao a PESSOAS (procurador federal eh oponente, nao alvo)
- **PA-18** — se contestacao tem ponto valido por surpresa, considerar ajuste estrategico (nao replicar erro proprio)
- **PA-22** — submeter a Suprema Corte

---

## 4. PROTOCOLOS ACIONADOS

- **2.1** (Jurisprudencial) — distinguishing das sumulas da PFE
- **2.5** (Compartimentacao) — escopo: replica processual

---

## 5. CHECKLIST DE SAIDA

- [ ] Cabecalho com numero do processo
- [ ] Fatos incontroversos (art. 341 CPC) listados
- [ ] Cada preliminar refutada
- [ ] Cada argumento de merito refutado
- [ ] Distinguishing aplicado a sumulas/jurisprudencia da PFE
- [ ] Tese central reforcada
- [ ] Pedidos mantidos integralmente
- [ ] Tom adversarial preservado
- [ ] Sem ataque pessoal
- [ ] Rodape com OAB

---

*Pronta para producao apos contestacao do INSS.*
