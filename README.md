# Previdenciario Adv-OS — Marketplace

Marketplace oficial do plugin **Previdenciario Adv-OS** para Claude Code / Cowork.

Sistema operacional do advogado previdenciarista — 26 skills consolidadas (RGPS + RPPS + Previdencia Complementar + Acidentario), 4 camadas hierarquicas com 22 Proibicoes Absolutas, 5 protocolos tecnicos e Suprema Corte R1-R4.

---

## Instalacao

### Via Claude Cowork (UI)

1. Abra o Claude Cowork (aba lateral)
2. Settings → Plugins → aba **Pessoal** → botao **+** → **Uploads locais**
3. Adicione o marketplace colando esta URL:

   ```
   https://github.com/sbroggioadv/previdenciario-adv-os-marketplace
   ```

4. Clique em **Sincronizar**
5. Instale o plugin **`previdenciario-adv-os`** que aparecer no marketplace
6. Rode `/start-previdenciario` em qualquer pasta de trabalho para o wizard de onboarding (~5 min)

---

## Plugin disponivel

### `previdenciario-adv-os` (v0.1.0)

Plugin Claude Code especializado em Direito Previdenciario Brasileiro.

**Cobertura:**
- RGPS (aposentadorias, beneficios por incapacidade, pensao, BPC/LOAS, salario-maternidade, revisao RMI)
- RPPS (Uniao/Estados/Municipios, LC 173/2020, abono permanencia, CTC)
- Previdencia Complementar (fechada LC 109 + aberta PGBL/VGBL)
- Acidentario do Trabalho (Justica Comum estadual, NTEP, nexo)

**Skills (26 consolidadas em 4 tiers):**
- Tier 0 — orquestrador (`previdenciario-master`)
- Tier 1 (Estado-Maior) — triagem-dogmatica, analise-trilateral, jurisprudencia-estrategica, estrategia-de-caso
- Tier 2 (Tenentes) — peticao-inicial, replica, recursos, MS, cumprimento, revisional, administrativo INSS/CRPS, analise-cnis, ppp-ltcat, pericia-medica, calculos, RPPS, complementar, acidentario, documentos extrajudiciais, audiencia
- Tier 3 — Suprema Corte Previdenciaria R1-R4
- Transversais — estilo-juridico, visual-law
- Engine — onboarding (`/start-previdenciario`)

**Comandos (8):** `/start-previdenciario`, `/previdenciario-master`, `/peticao-previdenciaria`, `/recurso-previdenciario`, `/parecer-previdenciario`, `/calculo-previdenciario`, `/revisao-previdenciaria-final`, `/status-previdenciario`.

Detalhes completos em [`previdenciario-adv-os/README.md`](./previdenciario-adv-os/README.md).

---

## Licenca

MIT — ver [LICENSE](./LICENSE).
