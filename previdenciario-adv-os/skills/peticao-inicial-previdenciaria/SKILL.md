---
name: peticao-inicial-previdenciaria
description: >
  PETICAO INICIAL PREVIDENCIARIA — Skill Tier 2 A. Produz peticao inicial em acao previdenciaria contra INSS (JEF ou Vara Federal). Estrutura completa: enderecamento, qualificacao, fatos, direito (FIRAC por bloco), pedidos determinados, valor da causa, requerimentos finais. Aciona automaticamente o pipeline Tier 1 (triagem dogmatica + analise trilateral + jurisprudencia + estrategia de caso) antes de redigir. Cobre todos os beneficios previdenciarios: aposentadorias (idade, tempo, especial, PCD, professor), beneficios por incapacidade (BPI, aposentadoria por incapacidade permanente), pensao por morte, BPC/LOAS, auxilio-acidente, auxilio-reclusao, salario-maternidade, revisao da vida toda, restabelecimento de beneficio cessado. Use quando o operador pedir "peticao inicial", "acao previdenciaria", "ajuizar contra o INSS", ou via /peticao-previdenciaria.
---

# PETICAO INICIAL PREVIDENCIARIA — Skill Tier 2 A

> Produz peca processual completa para ajuizamento contra INSS. Pipeline obrigatorio: Tier 1 antes, Suprema Corte depois.

---

## 1. PIPELINE OBRIGATORIO

```
operador pede peticao inicial
       │
       ▼
1. previdenciario-master ativa governance (Camadas 1-3)
       │
       ▼
2. Estado-Maior (Tier 1) em sequencia:
   ├── triagem-dogmatica-previdenciario
   ├── analise-trilateral-previdenciario
   ├── jurisprudencia-estrategica-previdenciario
   └── estrategia-de-caso-previdenciario
       │
       ▼
3. analise-cnis (Tier 2 C) — se CNIS anexado
       │
       ▼
4. [[ peticao-inicial-previdenciaria ]] (voce — Tier 2 A) — produz
       │
       ▼
5. Transversais: estilo + visual-law
       │
       ▼
6. Suprema Corte R1->R2->R3->R4
```

---

## 2. ESTRUTURA OBRIGATORIA

### 2.1 Cabecalho

```
EXCELENTISSIMO SENHOR DOUTOR JUIZ FEDERAL DA <vara/JEF> DA SECAO JUDICIARIA DE <cidade> — <UF>


<NOME DO AUTOR>, ja qualificado, vem, respeitosamente, por seu advogado
infrafirmado (instrumento de mandato anexo), com fulcro nos arts. 319 e
seguintes do CPC c/c art. <especifico Lei 8.213/91>, propor

ACAO <TIPO> — <BENEFICIO PRETENDIDO>

em face de

INSTITUTO NACIONAL DO SEGURO SOCIAL — INSS, autarquia federal, CNPJ
29.979.036/0001-40, com sede em Brasilia/DF e procuradoria-geral em
<cidade>/<UF>,

pelos fatos e fundamentos a seguir:
```

### 2.2 Fatos (narrativa fluida)

- Identificar segurado: nome, NIT, profissao, idade
- Historico previdenciario (com base no CNIS — PA-13)
- Fato gerador do direito (incapacidade, idade, tempo, etc.)
- Requerimento administrativo (DER + indeferimento — PA-14)
- Documentos probatorios (lista descritiva, sem ataque ao adversario)

**ATENCAO:** narrativa CONTINUA e COESA. Sem listas no meio do texto. Conectivos sofisticados. Fatos pintados de forma a ja ECOAR o direito.

### 2.3 Direito (FIRAC por bloco)

**Bloco I — Cabimento da via processual e competencia**
- F: indeferimento administrativo confirmado em <data>
- I: cabe ajuizamento da acao? competencia?
- R: art. 109, I, CF + Tema 350 STF + art. 5o Lei 10.259/2001
- A: requisito atendido (DER + indeferimento), valor < 60 SM = JEF / > 60 SM = Vara Federal
- C: competencia firmada

**Bloco II — Tese central** (depende do beneficio)

Para **aposentadoria por idade**:
- F: 65 anos (homem) ou 62 (mulher) + 180 contribuicoes
- I: preenche os requisitos da Lei 8.213/91, art. 48?
- R: art. 48 + 49 Lei 8.213/91 + EC 103/19 art. 18 + Tema 692 STJ (idade hibrida)
- A: <subsuncao concreta>
- C: tem direito a aposentadoria por idade

Para **aposentadoria por incapacidade permanente**:
- F: incapacidade comprovada por laudo/prontuarios
- I: direito a aposentadoria ou auxilio-doenca?
- R: art. 42 Lei 8.213/91 + Tema 416 STJ + Sumula 47 TNU (fungibilidade)
- A: incapacidade total e permanente comprovada
- C: tem direito a aposentadoria por incapacidade permanente (subsidiariamente, BPI)

Para **revisao da vida toda**:
- F: aposentadoria concedida em <data> com PBC limitado
- I: cabe inclusao de salarios pre-julho/1994?
- R: Tema 1102 STF + Tema 999 STJ (decadencia — PA-09)
- A: dentro do prazo decadencial; calculo comparativo demonstra vantagem
- C: tem direito a revisao

(Adaptar para outros beneficios: pensao, BPC, auxilio-acidente, salario-maternidade, etc.)

**Bloco III — Antecipacao de teses adversariais (PFE)**

> Eventual alegacao da PFE de <tese adversa> nao prospera porque <neutralizacao>.

(Ver outputs de analise-trilateral-previdenciario)

**Bloco IV — Tutela antecipada (se aplicavel)**

- Probabilidade do direito + perigo de dano (art. 300 CPC)
- Caso de cessacao indevida ou urgencia medica

### 2.4 Pedidos (determinados, exequiveis)

```
Diante do exposto, requer:

a) A concessao de TUTELA ANTECIPADA para <X> (se aplicavel);

b) A citacao do INSS para, querendo, contestar a presente acao;

c) A producao de todas as provas em direito admitidas, especialmente:
   - documental (CNIS, PPP, LTCAT, prontuarios medicos, atestados —
     todos juntados);
   - pericial medica (Tema 416 STJ);
   - depoimento pessoal das partes;
   - oitiva de testemunhas;

d) A PROCEDENCIA do pedido para CONDENAR o INSS a:
   - <conceder/restabelecer/revisar> o beneficio de <tipo>, NB <numero>,
     com DIB em <data>;
   - pagar as prestacoes vencidas desde <data>, devidamente corrigidas
     pelo IPCA-E ate 12/2021 e SELIC apos (Lei 14.439/2022), com juros
     legais;
   - pagar honorarios advocaticios de sucumbencia, observada a Sumula
     111 STJ (nao incidem sobre parcelas vincendas).

Da-se a causa o valor de R$ <valor>.

Local, data.

<advogado>
OAB/<UF> <numero>
```

### 2.5 Documentos a juntar (lista de anexos)

- Procuracao
- Documentos pessoais do segurado
- CNIS atualizado
- PPP/LTCAT (se especial)
- Carta de concessao / oficio de indeferimento (PA-14)
- Documentacao medica (se incapacidade/BPC)
- Comprovantes de tempo rural (se rural)
- Outros pertinentes ao caso

---

## 3. PAS APLICAVEIS

- **PA-01** — jurisprudencia citada classificada Nivel 1/2/3
- **PA-03** — sem invencao de fatos
- **PA-04** — postura adversarial contra INSS (sem suavizar)
- **PA-05** — linguagem de peca, nao parecer
- **PA-09** — se for revisao, abrir com decadencia (art. 103)
- **PA-13** — sem CNIS, paralisar
- **PA-14** — sem DER + indeferimento, PARALISAR (excecoes do Tema 350)
- **PA-15** — competencia correta (JEF/Vara Federal)
- **PA-17** — sem ataque pessoal
- **PA-21** — zero CDC contra INSS
- **PA-22** — submeter a Suprema Corte antes de entregar

---

## 4. PROTOCOLOS ACIONADOS

- **2.1** (Jurisprudencial) — toda jurisprudencia classificada
- **2.2** (Infralegal) — toda IN/Portaria classificada
- **2.5** (Compartimentacao) — escopo: peca judicial

---

## 5. CHECKLIST DE SAIDA

- [ ] Cabecalho com enderecamento correto
- [ ] Qualificacao do autor completa
- [ ] Fatos com narrativa fluida (sem listas)
- [ ] Pelo menos 1 bloco FIRAC
- [ ] Fundamentacao legal especifica (Lei 8.213/91 + art. correto)
- [ ] Jurisprudencia Nivel 1 ou Nivel 2 com [VERIFICAR]
- [ ] Antecipacao de tese adversaria
- [ ] Pedidos determinados com DIB + correcao + juros
- [ ] Sumula 111 STJ na sucumbencia
- [ ] Lista de documentos anexos
- [ ] Valor da causa
- [ ] Rodape com OAB

---

*Pronta para producao. Acionar pipeline.*
