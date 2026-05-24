---
name: administrativo-inss-crps
description: >
  ADMINISTRATIVO INSS / CRPS — Skill consolidada para todos os procedimentos administrativos previdenciarios. Cobre requerimento administrativo (DER + Tema 350 STF), recurso a Junta de Recursos do CRPS (1a instancia administrativa, 30 dias), recurso as Camaras de Julgamento do CRPS (2a instancia, 30 dias), e defesa administrativa em revisao de oficio (art. 103-A Lei 8.213/91, decadencia decenal do INSS). Linguagem formal-administrativa, foco em Lei 8.213/91 + Decreto 3.048/99 + IN 128/2022 + sumulas AGU/CRPS. Use para qualquer interacao administrativa com INSS.
---

# ADMINISTRATIVO INSS / CRPS — Skill Tier 2 B (consolidada)

> Procedimentos administrativos previdenciarios. Linguagem direta, fundamentacao em Lei + Decreto + IN.

---

## 1. SITUACOES E FLUXOS

| Situacao | Documento | Prazo |
|----------|-----------|-------|
| Pleito inicial | Requerimento Administrativo | n/a (cria DER) |
| Indeferimento -> recurso | Recurso a Junta de Recursos do CRPS | 30 dias do conhecimento |
| Decisao da Junta -> recurso | Recurso as Camaras de Julgamento do CRPS | 30 dias |
| Revisao de oficio do INSS | Defesa Administrativa | conforme notificacao |
| Mora administrativa (>45 dias) | Mandado de Seguranca por mora | 120 dias do ato |

---

## 2. REQUERIMENTO ADMINISTRATIVO

**Por que protocolar:**
- Tema 350 STF (RE 631.240) — exige previo requerimento para acao judicial
- Cria DER (Data de Entrada do Requerimento) — marco para DIB
- Carta de indeferimento e prova essencial para acao judicial

**Canais:**
- Meu INSS (web/app) — preferencial
- Telefone 135
- Agencia (com agendamento)

**Estrutura:**

```
AO INSTITUTO NACIONAL DO SEGURO SOCIAL — INSS
GERENCIA EXECUTIVA DE <cidade> / AGENCIA <X>

REQUERENTE: <nome completo>
CPF: <numero>
NIT: <numero>
Endereco: <completo>

REQUERIMENTO DE <BENEFICIO>

ESPECIE SAB:
  41 - aposentadoria por idade
  42 - aposentadoria por tempo de contribuicao
  91 - incapacidade temporaria (BPI)
  32 - incapacidade permanente
  21 - pensao por morte
  87 - BPC idoso
  88 - BPC pessoa com deficiencia
  ...

I. FUNDAMENTACAO
   Documentos anexos:
   - <CNIS>
   - <RG, CPF>
   - <comprovante de residencia>
   - <documentos especificos do beneficio>:
     * Aposentadoria idade: idade comprovada + 180 contribuicoes
     * Aposentadoria tempo: CNIS + PPP/LTCAT (se especial)
     * BPI: laudo + atestados + receituario
     * Pensao: certidao de obito + dependencia
     * BPC: hipossuficiencia + idade ou laudo de deficiencia

II. PEDIDO
   a) Processamento do requerimento
   b) Pericia / analise / o que cabivel
   c) CONCESSAO do beneficio com:
      - DIB: <DER ou anterior>
      - DIP: logo apos concessao
   d) Subsidiariamente: CARTA DE INDEFERIMENTO MOTIVADA com fundamentos
      expressos (para fins de eventual recurso)

Pede deferimento.

Local, data.
<assinatura segurado>
[via procurador, se houver — OAB]
```

**Atencao prazos:** 45 dias para decisao (art. 41-A IN 128/2022 — verificar redacao atual). Se INSS demorar, MS por mora.

---

## 3. RECURSO A JUNTA DE RECURSOS DO CRPS (1a instancia administrativa)

**Cabivel:** decisao do INSS (indeferimento, cessacao, revisao indeferida).

**Prazo:** 30 dias do conhecimento da decisao (art. 305 IN 128/2022).

**Estrutura:**

```
A ILUSTRISSIMA JUNTA DE RECURSOS DO CONSELHO DE RECURSOS DA
PREVIDENCIA SOCIAL (CRPS)

PROCESSO ADMINISTRATIVO N. <numero>
RECORRENTE: <nome>, CPF, NIT

<NOME>, qualificado, inconformado com decisao da APS de <cidade> que
<indeferiu/cessou/negou revisao> o beneficio NB <numero>, vem, no
prazo de 30 dias previsto no art. 305 da IN 128/2022, apresentar

RECURSO

a esta Egregia Junta de Recursos:

I. SINTESE DOS FATOS
   - Beneficio: <tipo> NB <numero>
   - DER: <data>
   - Decisao recorrida: <indeferimento>
   - Motivo (carta): <reproduzir>

II. TEMPESTIVIDADE

III. FUNDAMENTOS DA REFORMA
   III.1 — <fundamento 1>
     A decisao se equivocou ao <ponto>.
     Conforme dispoe o art. <X> da Lei 8.213/91 [c/c art. <Y> Dec
     3.048/99] [c/c art. <Z> IN 128/2022]:
       "<reproduzir dispositivo>"
     No caso, <subsuncao>.
     Sumula AGU n. <X> ainda dispoe:
       "<reproduzir>"
   III.2 — <fundamento 2>

IV. DOCUMENTOS NOVOS (se houver)
   Em sede de recurso, junta-se:
   - <documento 1>
   - <documento 2>

V. PEDIDO
   a) Conhecimento e provimento
   b) REFORMA para conceder/restabelecer beneficio com DIB e efeitos
   c) Subsidiariamente: nova pericia / instrucao complementar
   d) Cumprimento da decisao apos transito

Local, data.
<recorrente ou advogado OAB>
```

**Linguagem:** formal-administrativa. Foco em DISPOSITIVOS (lei + decreto + IN). Sumulas AGU vinculantes ao INSS sao obrigatorias quando aplicaveis. Sem latim extensivo.

---

## 4. RECURSO AS CAMARAS DE JULGAMENTO DO CRPS (2a instancia)

**Cabivel (limitado):**
- Divergencia entre Juntas de Recursos
- Violacao a sumula CRPS / AGU vinculante
- Materia constitucional

**Prazo:** 30 dias da decisao da Junta de Recursos.

**Estrutura:**

```
ILUSTRISSIMOS SRS. MEMBROS DA <X> CAMARA DE JULGAMENTO DO CRPS

PROCESSO ADMINISTRATIVO N. <numero>

RECURSO ESPECIAL

I. SINTESE
II. TEMPESTIVIDADE
III. CABIMENTO
   III.1 — Hipotese de cabimento
   III.2 — Demonstracao da divergencia / violacao a sumula

       A decisao recorrida diverge do entendimento da <outra Junta>
       no processo <numero>:
         "<reproduzir tese paradigma>"
       OU
       Violou a Sumula AGU/CRPS n. <X>:
         "<reproduzir>"

IV. FUNDAMENTOS DA REFORMA
V. PEDIDO
```

---

## 5. DEFESA ADMINISTRATIVA (revisao de oficio do INSS)

**Quando:** INSS notifica segurado para revisar beneficio de oficio (suspeita de irregularidade) ou pede devolucao por suposto erro.

**Verificacao bloqueante PA-09 (decadencia do INSS):**

```
Lei 8.213/91 art. 103-A:
  Decadencia DECENAL para INSS rever atos de oficio (apos 10 anos da
  concessao, INSS nao pode rever — exceto FRAUDE comprovada).
```

Beneficio com mais de 10 anos -> DEFENDER COM DECADENCIA.

**Estrutura:**

```
AO INSS — APS DE <cidade>

PROCESSO ADMINISTRATIVO N. <numero>

DEFESA ADMINISTRATIVA

I. SINTESE DO PROCEDIMENTO
   Em <data>, fui notificado para <descrever pedido administracao>.

II. PRELIMINARMENTE — DECADENCIA DO INSS PARA REVER (art. 103-A)
   [se aplicavel — beneficio com >10 anos]

   O beneficio NB <numero> foi concedido em <data>. Decorrido lapso
   superior a 10 anos, opera-se a DECADENCIA do direito do INSS de
   rever-lo de oficio (art. 103-A da Lei 8.213/91), salvo comprovada
   fraude — o que nao se verifica no caso.

   Requer-se RECONHECIMENTO DA DECADENCIA e ARQUIVAMENTO.

III. NO MERITO (subsidiariamente)

   III.1 — Refutacao da pretensao do INSS
     [FIRAC]

   III.2 — Boa-fe objetiva e tutela da confianca
     Se INSS pretende cobrar devolucao:
     - Sumula 34 AGU — recebimento de boa-fe afasta repeticao
     - Tema 979 STJ — boa-fe nos beneficios

   III.3 — Documentacao probatoria

IV. PEDIDO
   a) Acolhimento da preliminar de decadencia + ARQUIVAMENTO
   b) No merito: REJEICAO INTEGRAL
   c) MANUTENCAO do beneficio nos termos atuais
   d) Subsidiariamente: pericia / instrucao
```

**Sumulas relevantes:**
- Sumula 34 AGU — recebimento de boa-fe
- Tema 979 STJ — boa-fe nos beneficios

---

## 6. PAS APLICAVEIS

- **PA-02** — vedacao a alucinacao IN/Portaria/Sumula AGU
- **PA-04** — adversarial (INSS e contraparte)
- **PA-09** — decadencia do INSS em revisao de oficio (art. 103-A)
- **PA-13** — CNIS para refutar divergencias
- **PA-14** — requerimento administrativo cria DER (Tema 350 STF)
- **PA-22** — Suprema Corte antes de entregar

---

## 7. PROTOCOLOS ACIONADOS

- **2.1** Jurisprudencial (Sumulas AGU + CRPS classificadas)
- **2.2** Infralegal (IN 128/2022 vigente)
- **2.5** Compartimentacao (escopo: documento administrativo)

---

## 8. CHECKLIST DE SAIDA

- [ ] Tipo de procedimento identificado (requerimento / Junta / Camaras / defesa)
- [ ] Tempestividade verificada
- [ ] Lei + Decreto + IN citados com vigencia
- [ ] Sumulas AGU/CRPS Nivel 1
- [ ] Linguagem administrativa adequada (sem latim excessivo)
- [ ] Pedido especifico (concessao / reforma / arquivamento)
- [ ] Documentos anexos listados
- [ ] Rodape OAB (se via advogado)

---

*Skill administrativa universal. Acionar conforme procedimento.*
