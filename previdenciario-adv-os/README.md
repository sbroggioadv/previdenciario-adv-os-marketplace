# Previdenciario Adv-OS

> Plugin Claude Code especializado em **Direito Previdenciario Brasileiro**: RGPS, RPPS (servidor publico), Previdencia Complementar (fechada e aberta) e Direito Acidentario do Trabalho.

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## O que e

Plugin que transforma o Claude Code em **escritorio de advocacia previdenciaria especializado**. Ao instalar e rodar `/start-previdenciario`, o operador configura sua identidade (nome, OAB, escritorio, tom de voz, ferramentas), e o plugin passa a operar 26 skills juridicas previdenciarias consolidadas com governance arquitetada em 4 camadas hierarquicas.

### Diferencial

- **Hierarquia das 4 Camadas (constitucional)** — 22 Proibicoes Absolutas inviolaveis (PA-01 a PA-22) blindam o plugin contra alucinacao, retroatividade indevida da EC 103/2019, omissao de decadencia, confusao de regimes.
- **5 Protocolos Tecnicos** — Jurisprudencial (3 niveis), Infralegal (3 niveis), Pericia Medica, Calculos, Compartimentacao de Escopos.
- **Suprema Corte R1-R4** — quatro auditorias obrigatorias antes de qualquer entrega de peca, parecer ou calculo.
- **26 skills modulares consolidadas** em 4 tiers (Tier 0/1/2/3) cobrindo contencioso judicial, administrativo INSS/CRPS, analise tecnica (CNIS/PPP/laudo), calculos previdenciarios, RPPS, Previdencia Complementar, Acidentario, audiencia.
- **Persona dinamica em runtime** — a identidade do advogado (nome, OAB, escritorio) vive no workspace local (`<cwd>/previdenciario/persona.md`), nunca dentro do plugin distribuido.

---

## Como funciona

```
Cliente instala o plugin
       |
       v
  /start-previdenciario (wizard ~5min)
       |
       v
Wizard pergunta: nome, OAB, cidade, escritorio, tom, ferramentas
       |
       v
scripts/render.py gera <cwd>/previdenciario/persona.md
       |
       v
Hook SessionStart injeta persona em toda nova sessao Claude
       |
       v
Skills com placeholders {{ADVOGADO_NOME}}, {{OAB}}, {{FIRM_NAME}}
sao resolvidos em runtime pelo LLM lendo a persona injetada
```

A casca tecnica do plugin e universal e comercial. O conteudo personalizado vive **fora** do plugin distribuido, no workspace local do cliente.

---

## Areas cobertas

### RGPS (Regime Geral de Previdencia Social)

- Aposentadorias (idade, tempo de contribuicao, especial, PCD, professor, EC 103/2019 + 5 regras de transicao)
- Beneficios por incapacidade (temporaria e permanente)
- Pensao por morte
- BPC/LOAS
- Auxilio-acidente, auxilio-reclusao
- Salario-maternidade
- Revisao de RMI (vida toda — Tema 1102 STF)
- Restabelecimento, cessacao administrativa
- Contagem de tempo de contribuicao, CNIS, vinculos

### RPPS (Servidor Publico)

- Uniao, Estados, Municipios
- LC 173/2020, abono permanencia, paridade
- CTC entre regimes

### Previdencia Complementar

- Fechada (LC 109/2001 + LC 108/2001 — fundos de pensao)
- Aberta (PGBL/VGBL — possivel relacao de consumo)

### Acidentario do Trabalho

- Justica Comum estadual (Sumula 235 STF)
- Nexo causal, NTEP

---

## Hierarquia das 4 Camadas

```
CAMADA 1 — PROIBICOES ABSOLUTAS (PA-01 a PA-22) — inviolaveis
CAMADA 2 — PROTOCOLOS TECNICOS — aplicacao obrigatoria
CAMADA 3 — IDENTIDADE TECNICA E ESTILO — FIRAC + AIDA + Baloney
CAMADA 4 — SKILLS — operacional
```

**A camada superior sempre prevalece.** Mesmo o operador nao pode sobrescrever a Camada 1.

---

## Suprema Corte (R1-R4)

Antes de qualquer documento sair do plugin, ele passa pelas quatro auditorias:

- **R1** — Coleta de Dados (CNIS, PPP, laudo, carta de concessao... lacuna pendente?)
- **R2** — Base Juridica (lei vigente? jurisprudencia classificada Nivel 1/2/3? infralegal validada?)
- **R3** — Tese (escala de comprometimento OK? FIRAC integro? teses adversarias antecipadas?)
- **R4** — Completude Estilistica e Operacional (estilo correto? pedido determinado? competencia certa? OAB?)

`/corte off` desativa a Suprema Corte na sessao atual (uso excepcional, sob risco do operador).

---

## Comandos (8 total — todos prefixados)

### Bootstrap
- **`/start-previdenciario`** — wizard de onboarding (~5 min). Cria pasta `previdenciario/` no diretorio atual com identidade, tom de voz e configuracao das skills.

### Coracao
- **`/previdenciario-master`** — ativa cadeia completa: persona + 4 camadas + 22 PAs + skills relevantes + Suprema Corte.

### Dominio
- **`/peticao-previdenciaria`** — orquestra peca processual completa (inicial, replica, contestacao, MS)
- **`/recurso-previdenciario`** — recurso (escolhe instancia automaticamente: JEF, TRF, REsp, RE, PEDILEF, CRPS)
- **`/parecer-previdenciario`** — parecer estrutura I-VI obrigatoria
- **`/calculo-previdenciario`** — calculo com auto-ataque (Protocolo 2.4)
- **`/revisao-previdenciaria-final`** — apenas Suprema Corte sobre documento ja produzido

### Gestao
- **`/status-previdenciario`** — diagnostico (pasta criada? persona OK? skills ativas?)

### Ativacao automatica

Nao precisa rodar comando se mencionar termos previdenciarios no prompt. O plugin desperta sozinho quando detecta:
- "previdenciario" / "previdencia"
- INSS, RGPS, RPPS, CRPS, BPC, LOAS
- aposentadoria, pensao, auxilio-doenca, auxilio-acidente
- CNIS, PPP, LTCAT, DER, DIB, RMI
- pericia medica, junta de recursos, requerimento administrativo
- EC 103, regra de transicao, vida toda

---

## Privacidade e LGPD

- Toda configuracao do escritorio do operador vive em **`<cwd>/previdenciario/`** (FORA do plugin distribuido)
- `<cwd>/previdenciario/` e gitignored por default
- Transcricao de audio APENAS local
- MCPs externos sempre opt-in com warning
- Plugin nao envia dados a servicos externos sem opt-in explicito

---

## Licenca

MIT — ver [`LICENSE`](LICENSE).
