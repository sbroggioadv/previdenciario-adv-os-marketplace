# Previdenciario Adv-OS — Marketplace

> ## ⚖️ Este repositório NÃO é software livre
>
> O código fica visível para viabilizar a instalação no Claude/Cowork — não porque seja gratuito.
>
> **PREVIDENCIARIO ADV-OS — R$ 398,00, pagamento único** (sem assinatura, sem recorrência)
> 👉 **[Adquirir a licença](https://pay.kirvano.com/f682ea43-0f51-4b77-93c7-021c863e85b2)**
>
> **Ao forkar ou clonar este repositório você adere à [licença de uso](LICENSE)**, devendo efetuar o
> pagamento no link acima e enviar o comprovante para **luis@sbroggio.io**.
>
> Os forks são públicos no GitHub e são registrados pelo titular (data, conta e repositório).
>
> **Já comprou?** Nada a fazer — sua licença cobre o uso e o fork para instalação. Este aviso vale de
> 11/08/2026 em diante, para quem chega ao repositório sem ter adquirido.


Marketplace oficial do plugin **Previdenciario Adv-OS** para Claude Code / Cowork.

Sistema operacional do advogado previdenciarista que atua para o segurado, o dependente e o beneficiário contra o INSS — 34 skills em 6 camadas, 9 comandos, 7 scripts de cálculo previdenciário + 2 motores auxiliares (atualização monetária e prazos), com fonte de cada número, lei seca anexada e revisão final R1–R4 (Suprema Corte).

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

### `previdenciario-adv-os` (v2.0.2)

Plugin de Direito Previdenciário brasileiro para o advogado do segurado, do dependente e do beneficiário contra o INSS, do requerimento administrativo ao cumprimento de sentença.

**Cobertura:**
- RGPS: aposentadorias (regra permanente, direito adquirido e transições da EC 103/2019), aposentadoria especial e conversão de tempo, benefícios por incapacidade, auxílio-acidente, revisão de RMI
- BPC/LOAS
- Acidentário do trabalho
- Via administrativa (INSS e recurso ao CRPS) e judicial: inicial, réplica, mandado de segurança, audiência, recursos (JEF, TRF, PEDILEF, REsp, RE) e cumprimento de sentença com RPV ou precatório
- RPPS e previdência complementar: triagem e encaminhamento, sem cálculo

**Skills (34 em 6 camadas):**
- C0 Orquestração e QA — porta única (`previdenciario-master`), configuração, triagem, memória do caso, voz do escritório, revisão final R1–R4
- C1 Fundação — lei seca, jurisprudência selada, validador de citações, guarda anti-alucinação
- C2 Transversal — estratégia com 2 a 3 caminhos, cálculo, prazos, parecer, documentos e visual law
- C3 Análise e prova — CNIS, PPP e LTCAT, carta de concessão ou indeferimento, perícia médica
- C4 Benefícios e vias — planejamento previdenciário, acidentário, BPC, RPPS, complementar, administrativo
- C5 Judicial e recursos — da inicial ao cumprimento de sentença

**Cálculo (7 scripts de cálculo previdenciário + 2 motores auxiliares, todos locais, sem internet):** CNIS e carência, tempo de contribuição, regras de transição da EC 103, incapacidade, RMI, valor da causa e RPV; os motores auxiliares cuidam da atualização monetária e dos prazos. Cada número sai com a regra e a fonte; o que não fecha sai como fórmula aberta marcada `[VERIFICAR]`, nunca como estimativa.

**Citações:** a lei seca está anexada (EC 103/2019, Leis 8.213, 8.212, 8.742 e 10.259, Decreto 3.048, IN 128, Manual de Cálculos da Justiça Federal 2026) e toda citação é conferida contra os anexos.

**Comandos (9):** `/start-previdenciario`, `/previdenciario-master`, `/status-previdenciario`, `/calculo-previdenciario`, `/planejamento-previdenciario`, `/peticao-previdenciaria`, `/recurso-previdenciario`, `/parecer-previdenciario`, `/revisao-previdenciaria-final`.

**Para quem já instalou a versão 0.1:**
- Atualize o plugin pelo mesmo marketplace e rode `/start-previdenciario` uma vez: ele encontra a configuração antiga e oferece converter para o novo `previdenciario/perfil.md` ou começar do zero.
- Nenhum arquivo antigo é apagado, movido ou editado. O `CLAUDE.md` e o `.claude/settings.local.json` da 0.1 deixam de ser usados, mas o Claude ainda pode carregá-los; revise ou remova quando quiser.
- Cada caso passa a ter arquivo próprio em `previdenciario/casos/<caso>.md`.
- Nenhuma skill ou comando mudou de nome. Chegam 8 skills novas e o comando `/planejamento-previdenciario`; cinco comandos que apontavam para skill errada foram corrigidos.
- A revisão da vida toda saiu como tese (ADIs 2.110 e 2.111; Tema 1.102).
- A configuração do escritório não depende mais de Python, e os scripts auxiliares de estado saíram do plugin (os scripts de cálculo seguem rodando com Python 3).

Tudo o que muda, com as correções de regra de cálculo, está em [`previdenciario-adv-os/CHANGELOG.md`](./previdenciario-adv-os/CHANGELOG.md). Detalhes completos em [`previdenciario-adv-os/README.md`](./previdenciario-adv-os/README.md).

---

## Licenca

Uso licenciado mediante aquisição — ver [`LICENSE`](./LICENSE). As cópias obtidas até 11/08/2026 permanecem sob MIT; a partir dessa data o código é proprietário.
