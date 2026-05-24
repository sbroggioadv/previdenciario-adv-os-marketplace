---
name: visual-law-previdenciario
description: >
  VISUAL LAW PREVIDENCIARIO — Skill transversal sempre ativa. Cria recursos visuais que sintetizam casos previdenciarios complexos: timeline de vinculos previdenciarios (CNIS), matriz de provas, quadros comparativos das 5 regras de transicao da EC 103/2019, infograficos de calculo (RMI), tabelas de jurisprudencia classificada por niveis, fluxogramas de decisao (qual via processual). Acionada em qualquer producao documental que se beneficie de visual law (peticoes, pareceres, comunicacao ao segurado). Pecas usam visual law em ANEXOS (nao na narrativa principal); comunicacao ao segurado usa diretamente para acessibilidade.
---

# VISUAL LAW PREVIDENCIARIO — Skill Transversal

> Sempre ativa para producao documental que se beneficie de visualizacao. Em pecas, visual law vai em ANEXOS. Em comunicacao ao segurado, vai integrado.

---

## 1. PRODUTOS VISUAIS POR TIPO DE DEMANDA

### Aposentadorias

**Quadro comparativo das 5 regras de transicao EC 103/2019:**

| Regra | Tempo necessario | Idade minima | Pedagio | Calculo |
|-------|------------------|--------------|---------|---------|
| Pedagio 50% | ... | ... | 50% sobre tempo faltante | 60% + 2% por ano alem de 20 |
| Pedagio 100% | ... | ... | 100% sobre tempo faltante | media salarial integral |
| Pontos | ... | + idade = pontuacao | nao se aplica | media + redutor |
| Idade minima progressiva | ... | progressao anual | nao se aplica | 60% + 2% por ano |
| Professores | ... | reducao de 5 anos | conforme regra escolhida | conforme regra |

(Preencher dados especificos do caso na producao)

**Timeline de vinculos (CNIS):**

```
1990 ────────── 1995 ────────── 2000 ────────── 2005 ────────── 2010 ────────── HOJE
 │                │                │                │                │              │
 [Empresa A]   [Autonomo]      [Empresa B]    [Especial]      [Empresa C]
 12/1990     07/1996         01/2003         05/2008         01/2012
 a           a              a               a               a
 06/1996     12/2002         04/2008         12/2011         atual
```

### Beneficios por incapacidade

**Linha do tempo de incapacidade:**

```
DII (Data de Inicio da Incapacidade) ────────── DER ────────── DIB ────────── DCB
        │                                         │                │              │
        marcador medico                       requerimento    concessao     cessacao
        (laudo, prontuario)                   administrativo  (se houver)   (se houver)
```

**Matriz documentacao medica:**

| Documento | Data | Origem | Conteudo principal | Reforca tese? |
|-----------|------|--------|-------------------|---------------|
| Atestado | <data> | Dr X | CID + descricao + duracao | Sim/Parcial/Nao |
| Prontuario | <data> | Hospital Y | Internacao + tratamento | Sim |
| Exame | <data> | Lab Z | Resultado | Sim |
| Receituario | <data> | Especialista W | Medicacao continua | Parcial |

### Revisao de RMI

**Quadro comparativo de calculos:**

| Item | Calculo Original (DIB) | Calculo Revisado | Diferenca |
|------|----------------------|------------------|-----------|
| PBC (perido base de calculo) | <regra original> | <regra revisada> | ... |
| Salario-de-beneficio | R$ X | R$ Y | R$ Z |
| RMI | R$ A | R$ B | R$ C |
| Atrasados (5a) | — | R$ <calculo> | — |

### BPC/LOAS

**Quadro de hipossuficiencia:**

| Membro do grupo familiar | Idade | Renda | Observacao |
|--------------------------|-------|-------|------------|
| Requerente | ... | ... | ... |
| Conjuge | ... | ... | ... |
| Filho 1 | ... | ... | ... |
| ... | ... | ... | ... |
| **TOTAL** | — | R$ <total> | Per capita: R$ <total/N> |

Comparativo: 1/4 SM (criterio legal) vs realidade familiar.

### Recursos administrativos / processuais

**Fluxograma de decisao:**

```
Decisao
   │
   ├── Suficiente? ──── SIM ──→ Aceitar
   │                              │
   │                              v
   │                          Comunicar
   │                          segurado
   │
   └── Recorrer? ──── SIM ──→ Identificar instancia
                                  │
                                  ├── INSS administrativo
                                  │     └── Junta de Recursos (30d)
                                  │           └── Camaras de Julgamento
                                  │
                                  └── Judicial
                                        ├── JEF (10d)
                                        ├── Apelacao TRF (15d)
                                        ├── REsp/RE (15d)
                                        └── PEDILEF TNU (10d)
```

### Jurisprudencia classificada

**Quadro de fundamentos jurisprudenciais:**

| Tema | Tribunal | Status | Aplicacao ao caso |
|------|----------|--------|-------------------|
| Tema 1102 | STF (RG) | Nivel 1 [se confirmado] | Sustenta tese central |
| Tema 999 | STJ | Nivel 1 | Verificar decadencia |
| Tema 416 | STJ | Nivel 1 | Pericia oficial |
| ... | ... | ... | ... |

---

## 2. PROTOCOLO DE EXECUCAO

### Passo 1 — Identificar produto visual cabivel

Pelo tipo de demanda + tipo de documento sendo produzido:

| Demanda | Visual law cabivel |
|---------|-------------------|
| Aposentadoria por tempo | Quadro comparativo regras + timeline CNIS |
| Aposentadoria por idade | Timeline CNIS + tabela carencia |
| Aposentadoria especial | Timeline CNIS + matriz PPP/LTCAT + agentes nocivos |
| Beneficio incapacidade | Timeline DII-DER-DIB + matriz documentacao medica |
| BPC | Quadro hipossuficiencia familiar |
| Revisao RMI | Quadro comparativo calculos |
| Recurso | Fluxograma instancia + quadro jurisprudencial |
| Comunicacao ao segurado | Visual simplificado com proximos passos |

### Passo 2 — Decidir onde colocar

- **Peca processual:** visual law em **ANEXO** (nao na narrativa principal — Camada 3)
- **Parecer:** pode ir na secao IV (Fundamentacao) ou em ANEXO
- **Comunicacao ao segurado:** vai INTEGRADO ao texto (acessibilidade)
- **Calculo:** vai INTEGRADO (nucleo do documento)
- **Recurso administrativo:** geralmente integrado, formato simples

### Passo 3 — Construir o visual

Use markdown para tabelas/listas. Para fluxogramas e timelines, ASCII art ou descricao textual estruturada.

### Passo 4 — Validar conteudo

- Dados extraidos de fonte (PA-03 — sem invencao)
- Pontos de Omissao sinalizados
- Jurisprudencia classificada por nivel (PA-01)

### Passo 5 — Reportar produto visual

Entregar o visual + indicacao de onde inserir (anexo/integrado).

---

## 3. PRINCIPIOS DE DESIGN

- **Simplicidade** — visual deve facilitar leitura, nao complicar
- **Hierarquia visual** — informacao mais importante em destaque
- **Consistencia** — mesma simbologia ao longo do documento
- **Verdade** — nao ocultar dados desfavoraveis ao segurado
- **Acessibilidade** — em comunicacao ao segurado, sem jargao tecnico

---

## 4. SIMBOLOGIA PADRAO

- 🟢 — Forte / favoravel / aprovado
- 🟡 — Moderado / atencao / com ressalvas
- 🔴 — Fragil / desfavoravel / reprovado
- ✓ — Item OK
- ✗ — Item ausente / problema
- → — Fluxo / progressao
- ↓ — Sequencia / etapa seguinte

---

## 5. VEDACOES ESPECIFICAS

- **PA-03** — visual law nao pode conter dados inventados
- **PA-10** — visual law nao pode atribuir conteudo a precedente sem confirmar
- **NAO** colocar tabelas no meio de narrativa fatica de peca processual (Camada 3)
- **NAO** sobrecarregar comunicacao ao segurado com tabelas tecnicas
- **NAO** usar simbologia inconsistente (escolha um padrao e mantenha)

---

## 6. PROTOCOLOS ACIONADOS

- **Protocolo 2.5** (Compartimentacao) — onde inserir varia conforme tipo de documento

---

*Visual law previdenciario sempre ativo.*
