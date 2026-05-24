---
name: analise-cnis
description: >
  ANALISE DE CNIS — Skill Tier 2 C. Le e analisa Cadastro Nacional de Informacoes Sociais (CNIS) do segurado, mapeando vinculos empregaticios, contribuicoes, periodos concomitantes, lacunas, pendencias administrativas (PE, PVI, IREC), e integridade do registro. Output: mapa de tempo de contribuicao bruto + carencia + sinalizacao de problemas. ALICERCE de qualquer demanda previdenciaria — PA-13 obriga analise antes de qualquer peca/calculo. Use quando operador anexar CNIS ou pedir analise de tempo, vinculos, ou conferencia de dados previdenciarios.
---

# ANALISE DE CNIS — Skill Tier 2 C

> Le o CNIS, mapeia vinculos e tempo, sinaliza pendencias. **PA-13 obriga esta analise antes de qualquer producao.**

---

## 1. O QUE EXTRAIR DO CNIS

### 1.1 Identificacao
- NIT (Numero de Inscricao do Trabalhador)
- Nome completo
- Data de nascimento
- Filiacao

### 1.2 Vinculos
Para cada vinculo (empregaticio, contribuinte individual, facultativo, etc.):
- Empregador (nome + CNPJ)
- Categoria (empregado, contribuinte individual, facultativo, etc.)
- Data de admissao
- Data de saida (se ja encerrado)
- Salario-de-contribuicao (mes a mes ou faixas)
- Indicadores administrativos (PE, PVI, IREC, IPESC, etc.)

### 1.3 Indicadores administrativos comuns

| Indicador | Significado | Acao |
|-----------|-------------|------|
| **PE** | Pendencia | INSS suspendeu computacao por divergencia |
| **PVI** | Pendencia de vinculo | Vinculo nao confirmado pelo empregador |
| **IREC** | Indicador de recolhimento extemporaneo | Recolhimento fora do prazo |
| **IEAN** | Indicador de Empresa de Atividade Nao Identificada | Empresa nao localizada |
| **IPESC** | Indicador de Pendencia de Salario de Contribuicao | Salario sem comprovacao |
| **IGFIP** | Indicador de divergencia GFIP | Recolhimento divergente |

**Tarefa:** identificar todos os indicadores e propor estrategia para sanea-los.

---

## 2. MAPA DE TEMPO

Gerar tabela:

| Vinculo | Inicio | Fim | Tempo bruto | Especial? | Concomitante? | Pendencias |
|---------|--------|-----|-------------|-----------|---------------|------------|
| Empresa A | 01/1990 | 06/1996 | 6a 6m | Nao | Nao | Nenhuma |
| Empresa B | 03/1996 | 12/2002 | 6a 10m | Nao | **Sim** (sobreposicao 03-06/1996) | PVI |
| Especial C | 01/2003 | 04/2008 | 5a 4m | **Sim** (LTCAT) | Nao | PE |
| ... | ... | ... | ... | ... | ... | ... |

**Tempo bruto total:** <somar>
**Tempo apos resolver concomitancia:** <descontar sobreposicao>
**Tempo especial convertido (1.4x homem / 1.2x mulher):** <calcular>
**Carencia (meses com contribuicao valida):** <contar separadamente>

---

## 3. CARENCIA — CALCULAR SEPARADAMENTE

```
Lei 8.213/91 art. 24 — carencia:
  Numero MINIMO de contribuicoes para concessao do beneficio,
  CONTADO MES A MES (nao se confunde com tempo).

  Aposentadoria por idade: 180 meses (15 anos)
  BPI temporario: 12 meses (com excecoes — Lei 8.213/91 art. 26)
  Aposentadoria por incapacidade permanente: 12 meses (com excecoes)
  Pensao por morte: pelo menos 18 contribuicoes para regra Lei 13.135/15
  Salario-maternidade: 10 contribuicoes (segurada especial e contribuinte
    individual)
```

Verificar:
- Total de contribuicoes mes a mes (apenas competencias com indicadores OK)
- Nao incluir pendencias nao saneadas

---

## 4. CONCOMITANCIA

Quando dois vinculos se sobrepoem temporalmente:
- O tempo NAO se duplica
- Mas as contribuicoes podem aumentar o salario-de-beneficio (PBC)
- Aplicar regras do art. 32 do Decreto 3.048/99

---

## 5. RECONHECIMENTO DE TEMPO RURAL

Se houver vinculo rural:
- Anterior a 11/1991: pode ser comprovado por inicio de prova material (ITR, escola, sindicato, certidao escolar) + testemunhas
- Apos 11/1991: precisa de contribuicao ou comprovacao especifica (Lei 8.213/91 art. 26 + 39)

---

## 6. PROTOCOLO DE EXECUCAO

### Passo 1 — Extrair dados
Ler CNIS anexado (PDF / imagem / texto). Estruturar conforme Secao 1.

### Passo 2 — Detectar pendencias
Listar todos os indicadores administrativos e propor saneamento.

### Passo 3 — Mapear vinculos
Tabela conforme Secao 2.

### Passo 4 — Resolver concomitancia
Aplicar Secao 4. Identificar sobreposicoes.

### Passo 5 — Apurar tempo bruto
Somar tempo de cada vinculo, descontando concomitancia.

### Passo 6 — Apurar carencia
Contar meses com contribuicao OK (Secao 3).

### Passo 7 — Sinalizar pontos de Omissao (PA-03)
- CNIS desatualizado? sinalizar
- Vinculo nao informado mas conhecido pelo segurado? sinalizar
- Periodos rurais nao registrados? sinalizar
- Salarios-de-contribuicao ausentes em alguma competencia? sinalizar

### Passo 8 — Reportar

```
ANALISE DE CNIS — RELATORIO
═══════════════════════════════════════

SEGURADO: <nome> (NIT <numero>)

VINCULOS MAPEADOS: <N>
TEMPO BRUTO TOTAL: <X> anos, <Y> meses
TEMPO APOS CONCOMITANCIA: <X> anos, <Y> meses
TEMPO ESPECIAL CONVERTIDO: <X> anos, <Y> meses (se aplicavel)
TEMPO TOTAL (bruto + especial convertido): <X> anos, <Y> meses

CARENCIA (meses): <N>

PENDENCIAS DETECTADAS:
  - <indicador 1> em <vinculo X> — saneamento: <acao>
  - <indicador 2> em <vinculo Y> — saneamento: <acao>

PONTOS DE OMISSAO (PA-03):
  - <ponto 1>
  - <ponto 2>

VINCULOS COM POTENCIAL DE TEMPO ESPECIAL:
  - <vinculo X — solicitar PPP/LTCAT>

RECOMENDACAO:
  - Antes de propor <beneficio>, sanear pendencias e completar dados.

═══════════════════════════════════════
```

---

## 7. PAS APLICAVEIS

- **PA-03** — sem invencao de vinculos / datas / valores
- **PA-13** — analise de CNIS e PRE-REQUISITO
- **PA-20** — sem calculo de tempo silencioso

---

## 8. PROTOCOLOS ACIONADOS

- **2.4** Etapa 2 (apurar tempo + carencia separadamente)

---

*Analise de CNIS pronta.*
