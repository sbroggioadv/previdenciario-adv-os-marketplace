---
description: Aciona apenas a Suprema Corte (R1-R4) sobre documento ja produzido. Use quando quiser revisar uma peca/parecer/calculo que voce ou outra IA produziu.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
argument-hint: [path opcional do arquivo a revisar]
---

Voce foi acionado pelo comando `/revisao-previdenciaria-final` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** auditar documento ja produzido (peca, parecer, calculo, recurso) aplicando exclusivamente o sistema de revisao da Suprema Corte (R1-R4). Pula triagem dogmatica e estado-maior porque o documento ja existe.

## PROTOCOLO DE EXECUCAO

### 1. Identificar documento a revisar

Se argumento fornecido com path, ler o arquivo. Caso contrario:

```
Que documento voce quer revisar?

Opcoes:
1. Cole o texto integral aqui
2. Anexe o arquivo (.md, .docx, .pdf)
3. Indique o path do arquivo no diretorio atual
```

### 2. Identificar tipo de documento

```
Que tipo de documento e este?

a. Peticao inicial / contestacao / replica
b. Recurso (JEF, TRF, REsp, RE, PEDILEF, CRPS)
c. Parecer juridico
d. Calculo previdenciario
e. Notificacao extrajudicial
f. Comunicacao ao segurado
```

A escolha define qual checklist da Camada 3 aplicar (estilo do tipo).

### 3. Acionar Suprema Corte (skills do Tier 3)

```
suprema-corte-previdenciario (meta-skill orquestradora)
   │
   ├── R1 — suprema-corte-r1-coleta-dados
   ├── R2 — suprema-corte-r2-base-juridica
   ├── R3 — suprema-corte-r3-tese
   └── R4 — suprema-corte-r4-completude
```

### 4. Executar R1 — Coleta de Dados

Verificar:
- Todo dado factual extraido da fonte?
- Pontos de Omissao sinalizados? (PA-03)
- Faltam CNIS, PPP, LTCAT, laudo, carta de concessao?

Se houver lacuna critica → **PARALISA documento ate resolucao**.

### 5. Executar R2 — Base Juridica

Verificar:
- Toda lei citada existe e esta vigente? (PA-10)
- Toda jurisprudencia classificada Nivel 1/2/3? (PA-01)
- Toda norma infralegal no protocolo correto? (PA-02)
- Decadencia/prescricao analisada? (PA-09)
- Competencia correta? (PA-15)
- Regras de transicao EC 103/2019 verificadas? (PA-08)

Se violacao → bloquear ate corrigir.

### 6. Executar R3 — Tese Juridica

Verificar:
- Tese central sustentada?
- Escala de comprometimento (forte → fraco)?
- Teses adversarias antecipadas e neutralizadas?
- FIRAC integro por bloco tematico?
- AIDA na arquitetura macro?
- Baloney detection — falacias na tese adversa identificadas?
- Aventura juridica? Sinalizar.

### 7. Executar R4 — Completude

Verificar:
- Estilo conforme Camada 3 do tipo (peca / parecer / calculo)?
- Tom Nivel 4 (firmeza categorica)?
- Conformidade OAB-Provimento 205/2021 (se marketing)?
- Pedido determinado?
- Endereçamento correto?
- Rito processual apropriado?
- Output formato correto (Markdown vs plain text)?
- PA-05 — sem mistura de escopos?
- PA-17 — sem ataque pessoal?

### 8. Relatorio final

```
========================================
SUPREMA CORTE — RELATORIO DE AUDITORIA
========================================

Documento: <tipo>
Tamanho: <N paginas / palavras>

R1 — COLETA DE DADOS
   ✓ ou ✗ por item
   - Pontos de Omissao: <lista>
   - Bloqueios: <lista>

R2 — BASE JURIDICA
   ✓ ou ✗ por item
   - Lei: <validacoes>
   - Jurisprudencia: <classificacao>
   - Infralegal: <validacoes>

R3 — TESE
   ✓ ou ✗ por item
   - Pontos fortes: <lista>
   - Pontos fragilizados: <lista>

R4 — COMPLETUDE
   ✓ ou ✗ por item

VEREDICTO:
   [ ] APROVADO (sai como esta)
   [ ] APROVADO COM RECOMENDACOES (lista de melhorias opcionais)
   [ ] REPROVADO (lista de correcoes obrigatorias)

PROXIMO PASSO:
   <descricao>
```

**Skill a acionar:** `suprema-corte-previdenciario` (meta-skill).
