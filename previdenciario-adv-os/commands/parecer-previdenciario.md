---
description: Produz parecer juridico previdenciario formal com estrutura I-VI obrigatoria + Suprema Corte.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
argument-hint: [tema opcional]
---

Voce foi acionado pelo comando `/parecer-previdenciario` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** produzir parecer juridico previdenciario com estrutura formal I-VI e auditoria R1-R4.

## PROTOCOLO DE EXECUCAO

### 1. Verificar plugin ativo

`previdenciario/cowork-state.json` existe? Se nao, sugerir `/start-previdenciario`.

### 2. Levantar tema e contexto

Se argumento fornecido, usar como tema. Caso contrario:

```
Sobre o que e o parecer?

Exemplos comuns:
- Viabilidade de aposentadoria por tempo de contribuicao apos EC 103/2019
- Cabimento de revisao da vida toda (Tema 1102 STF)
- Conversao de tempo especial em comum
- Reconhecimento de tempo rural
- Acumulacao de beneficios
- Migracao entre regimes (RGPS ↔ RPPS)
- Calculo de salario-de-beneficio
- Outro: descrever
```

Coletar tambem:
- Cliente (nome, qualificacao, CNIS, vinculos)
- Pergunta especifica a ser respondida
- Contexto factual relevante
- Documentos disponiveis

### 3. Compartimentacao de escopo (PA-05)

**ATENCAO:** parecer NAO e peca processual. Linguagem de parecer:
- Estrutura formal obrigatoria (I a VI)
- Tom tecnico-elegante
- Doutrina autorizada com autoria identificada
- Conclusao categorica indicando o caminho seguro

NAO usar:
- Endereco a juizo
- Pedidos determinados
- Cabecalho de peticao
- Linguagem demolidora estilo combate

### 4. Estrutura I-VI obrigatoria

```
I. INTRODUCAO
   - Identificacao do consulente
   - Tema e pergunta
   - Metodologia adotada
   - Estrutura do parecer

II. FATOS
   - Narrativa factual fluida
   - Dados objetivos do CNIS, contratos, periodos
   - Pontos de Omissao sinalizados (PA-03)

III. QUESTOES
   - Lista das perguntas a responder
   - Hierarquia entre elas (principal vs subsidiarias)

IV. FUNDAMENTACAO
   - Por bloco tematico, aplicar FIRAC
   - Cada Questao tem sua secao
   - Legislacao classificada (Lei + Decreto + IN)
   - Jurisprudencia classificada Nivel 1/2/3 (PA-01)
   - Doutrina autorizada com autoria

V. ANALISE CRITICA
   - Pontos de risco identificados
   - Teses adversarias antecipadas (PFE/INSS)
   - Cenarios alternativos
   - Probabilidade de exito (sem chute — fundamentar)

VI. CONCLUSAO
   - Resposta direta a cada Questao do bloco III
   - Caminho recomendado (estrategico)
   - Documentos a providenciar
   - Prazos relevantes (decadencia, prescricao)
```

### 5. Cadeia de skills

```
1. triagem-dogmatica-previdenciario (Tier 1)
2. jurisprudencia-estrategica-previdenciario (Tier 1)
3. parecer-juridico-previdenciario (Tier 2 F) — skill principal
4. analise-cnis (Tier 2 C) — se cliente anexou CNIS
5. estilo-juridico-previdenciario (transversal)
6. suprema-corte-previdenciario (R1-R4)
```

### 6. Verificacoes obrigatorias

- **PA-05:** linguagem de parecer, nao peca
- **PA-09:** se discutir revisao, abrir com decadencia
- **PA-10:** zero invencao de dispositivo
- **PA-11:** firmeza Nivel 4 nas conclusoes (sem "talvez")
- **PA-21:** zero CDC em RGPS

### 7. Entrega

Parecer pronto com:
- Estrutura I-VI integral
- Citacoes de doutrina com autoria
- Jurisprudencia classificada
- Conclusao categorica

**Skill a acionar:** `previdenciario-master` + `parecer-juridico-previdenciario`.
