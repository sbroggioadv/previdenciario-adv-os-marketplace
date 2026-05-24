---
description: Orquestra producao de peticao previdenciaria completa (inicial, replica, contestacao). Aciona triagem dogmatica + estado-maior + skill da peca + Suprema Corte.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
argument-hint: [tipo opcional: inicial | replica | contestacao | mandado-seguranca]
---

Voce foi acionado pelo comando `/peticao-previdenciaria` do plugin Previdenciario-Adv-OS.

Argumento recebido: `$ARGUMENTS`

**Objetivo:** produzir peca processual previdenciaria com governance completa das 4 Camadas e auditoria R1-R4.

## PROTOCOLO DE EXECUCAO

### 1. Verificar plugin ativo

Garanta que `previdenciario/cowork-state.json` existe. Se nao, sugerir `/start-previdenciario`.

### 2. Identificar tipo de peca

Pelo argumento OU perguntar ao operador:

```
Que tipo de peca voce quer produzir?

JUDICIAL:
1. Peticao inicial previdenciaria (JEF / Vara Federal)
2. Replica
3. Recurso JEF (Turma Recursal)
4. Apelacao TRF
5. REsp / RE / PEDILEF
6. Embargos de declaracao
7. Contrarrazoes
8. Mandado de Seguranca contra ato do INSS
9. Cumprimento de sentenca

ADMINISTRATIVA:
10. Recurso a Junta de Recursos (CRPS)
11. Recurso as Camaras de Julgamento (CRPS)
12. Defesa administrativa
13. Requerimento administrativo (DER)

Selecione (1-13) ou descreva.
```

### 3. Coleta de dados (PROTOCOLO PA-13 e PA-14)

Antes de produzir, verificar (e pedir se faltar):
- **CNIS** do segurado (PA-13 — sem CNIS, paralisa)
- **Carta de concessao OU oficio de indeferimento** (PA-14 — Tema 350 STF)
- **DER** (data de entrada do requerimento)
- **DIB** (data de inicio do beneficio, se concedido)
- **PPP/LTCAT** (se aposentadoria especial)
- **Laudo pericial** (se incapacidade)
- **Documentacao medica** (prontuarios, atestados)

Se algo faltar, sinalizar como "Ponto de Omissao" e perguntar ao operador.

### 4. Acionar cadeia de skills

```
1. triagem-dogmatica-previdenciario (Tier 1)
   → identifica principios + institutos transversais aplicaveis

2. analise-trilateral-previdenciario (Tier 1)
   → segurado + INSS/PFE + magistrado

3. jurisprudencia-estrategica-previdenciario (Tier 1)
   → STF/STJ/TNU/TRFs com classificacao 3 niveis (PA-01)

4. analise-cnis (Tier 2 C) [se CNIS anexado]
   → mapear vinculos, lacunas, pendencias

5. skill-da-peca-cabivel (Tier 2 A ou B):
   - peticao-inicial-previdenciaria
   - replica-previdenciaria
   - recurso-jef-previdenciario
   - apelacao-previdenciaria-trf
   - recurso-especial-previdenciario (com Filtro Anti-Sumula 7 — PA-16)
   - mandado-seguranca-previdenciario
   - recurso-junta-recursos-crps
   - etc.

6. Aplicar transversais:
   - estilo-juridico-previdenciario (FIRAC + AIDA + Baloney + tom Nivel 4)
   - visual-law-previdenciario (matriz de provas, timeline, quadros)

7. suprema-corte-previdenciario (Tier 3) — obrigatorio
   → R1 (coleta) → R2 (base) → R3 (tese) → R4 (completude)
```

### 5. Verificacoes especificas

- **PA-04:** zero narrativa conciliatoria automatica com INSS
- **PA-05:** linguagem de peca, nao parecer
- **PA-09:** se for revisao de RMI, abrir com decadencia (art. 103 Lei 8.213/91)
- **PA-15:** competencia correta:
  - RGPS contra INSS → JEF (ate 60 SM) ou Vara Federal
  - RPPS estadual/municipal → Justica Comum estadual
  - Acidentario → Justica Comum estadual (Sumula 235 STF)
- **PA-21:** zero CDC contra INSS

### 6. Entrega

Peca finalizada com:
- Endereco completo do juizo
- Qualificacao das partes
- Fatos com narrativa fluida (sem listas no meio do texto)
- Direito com FIRAC por bloco
- Pedidos determinados
- Rodape com OAB do operador
- Anexos sugeridos

**Skill a acionar:** `previdenciario-master` (master orquestrador) + skill da peca cabivel.
