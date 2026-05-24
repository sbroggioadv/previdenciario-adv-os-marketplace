---
name: cumprimento-sentenca-inss
description: >
  CUMPRIMENTO DE SENTENCA INSS — Skill Tier 2 A. Produz peticao de cumprimento de sentenca em acao previdenciaria com transito em julgado. Estrutura: requerimento de execucao, calculo de liquidacao (Protocolo 2.4), expedicao de RPV (ate 60 SM por exequente) ou precatorio (acima de 60 SM), honorarios sucumbenciais (Sumula 111 STJ), juros e correcao. Acionada apos transito em julgado. Pipeline obrigatorio inclui calculo-rmi e liquidacao-sentenca-previdenciaria. Use quando operador disser "executar sentenca", "RPV", "precatorio", "cobrar atrasados".
---

# CUMPRIMENTO DE SENTENCA INSS — Skill Tier 2 A

> Executar a sentenca transitada em julgado. RPV ate 60 SM, precatorio acima.

---

## 1. PIPELINE OBRIGATORIO

```
operador pede cumprimento
       │
       ▼
1. Verificar transito em julgado
       │
       ▼
2. analise-cnis + carta-concessao (para validar dados)
       │
       ▼
3. liquidacao-sentenca-previdenciaria (Tier 2 D) — calculo
       │
       ▼
4. [[ cumprimento-sentenca-inss ]] (voce — peca)
       │
       ▼
5. Suprema Corte
```

---

## 2. PREMISSAS

- Sentenca **transitada em julgado**
- **Calculo de liquidacao** pronto (Protocolo 2.4 aplicado)
- Auto-ataque ja feito (Etapa 5 do Protocolo 2.4 — assumir papel da PFE)

---

## 3. DETERMINACAO RPV vs PRECATORIO

```
Lei 10.259/2001 art. 17:
  RPV = ate 60 salarios minimos
  Precatorio = acima de 60 SM
```

**Calculo rapido:**
- 60 × <SM atual> = limite RPV
- Se total devido <= limite: RPV (pagamento em ~60 dias)
- Se total devido > limite: precatorio (pagamento ate 31/12 do ano seguinte ao acrescentamento)

**Possibilidade de cisao** (renunciar ao excedente para RPV) — analisar com cliente.

---

## 4. ESTRUTURA OBRIGATORIA

```
EXCELENTISSIMO SENHOR DOUTOR JUIZ FEDERAL DA <vara/JEF>


Processo n. <numero>
Exequente: <nome>
Executado: INSS

<NOME>, ja qualificado, vem, por seu advogado, requerer

CUMPRIMENTO DE SENTENCA

com fulcro nos arts. 534 e 535 do CPC, pelos fatos e fundamentos a seguir:

I. DA SENTENCA E DO TRANSITO EM JULGADO

  - Sentenca de <data>, fls. <X>, julgou procedente
  - Transito em julgado em <data>, conforme certidao de fls. <Y>

II. DA LIQUIDACAO DO TITULO

  Apresenta-se o calculo de liquidacao em ANEXO, observados:

  - Periodo da execucao: <DIB> a <data atual>
  - Indice de correcao: IPCA-E ate 12/2021; SELIC apos (Lei 14.439/2022)
  - Juros: <conforme decisao — geralmente SELIC ja inclui juros>
  - Honorarios sucumbenciais: <%>, observada a Sumula 111 STJ (nao incidem
    sobre parcelas vincendas)
  - Custas processuais: <valor, se houver>

  TOTAL DEVIDO: R$ <valor>

  [Nota: se RPV, indicar "valor abaixo do limite de 60 SM = R$ <X>"]
  [se precatorio, indicar "valor acima do limite, expedicao via precatorio"]

III. DO REQUERIMENTO

  Requer-se:

  a) Intimacao do INSS para impugnar a execucao no prazo do art. 535 CPC
     (30 dias);

  b) Apos manifestacao do INSS (ou decurso do prazo):

     b.1) **Sendo RPV** (valor <= 60 SM): expedicao de Requisicao de
          Pequeno Valor (RPV) em favor do exequente, com pagamento em
          ate 60 dias;

     b.2) **Sendo precatorio** (valor > 60 SM): expedicao de OFICIO
          PRECATORIO (art. 100 CF) ao Tribunal competente, com pagamento
          conforme cronograma constitucional;

  c) Pagamento dos honorarios sucumbenciais separadamente do beneficio
     em favor da parte;

  d) Liberacao dos valores apos depositados.

Local, data.
<advogado> OAB/<UF> <numero>
```

---

## 5. ATENCAO — IMPUGNACAO DA EXECUCAO PELO INSS (art. 535 CPC)

PFE pode impugnar:
- Excesso de execucao (valores acima do titulo)
- Erro de calculo
- Compensacao com pagamentos administrativos
- Nao-incidencia de juros em determinado periodo
- Outros

Antecipar essas teses no calculo (Etapa 5 do Protocolo 2.4 — auto-ataque).

---

## 6. SUMULAS RELEVANTES

- **Sumula 111 STJ** — honorarios em previdenciario nao incidem sobre parcelas vincendas
- **Sumula 17 STJ** — incidencia de honorarios em fase de execucao
- **Sumula 105 STJ** — custas pelo INSS

---

## 7. PAS APLICAVEIS

- **PA-03** — sem invencao de valores
- **PA-20** — sem calculo estimativo silencioso
- **PA-22** — Suprema Corte

---

## 8. CHECKLIST DE SAIDA

- [ ] Transito em julgado certificado
- [ ] Calculo de liquidacao em anexo (Protocolo 2.4)
- [ ] Auto-ataque feito (Etapa 5)
- [ ] RPV ou precatorio decidido
- [ ] Sumula 111 aplicada nos honorarios
- [ ] Custas pelo INSS (Sumula 105)
- [ ] Pedido de liberacao
- [ ] Rodape OAB

---

*Pronto.*
