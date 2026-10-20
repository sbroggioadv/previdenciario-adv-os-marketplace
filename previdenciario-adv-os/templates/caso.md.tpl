# Caso — {{slug}}

> Gravado em `<cwd>/previdenciario/casos/{{slug}}.md` pela skill `memoria-de-caso-previdenciario`.
> **Um arquivo por caso.** Um caso não vaza para o outro, e o advogado arquiva ou apaga um sem tocar nos demais.
> O `slug` não leva nome civil, CPF nem NIT do cliente: use um código do escritório (ex.: `2026-031-aposentadoria-especial`).

**Aberto em:** {{DATA}} · **Última atualização:** {{DATA}} · **Plugin:** previdenciario-adv-os v2.0.0

---

## 1. Partes

| Papel | Quem |
|---|---|
| Segurado / dependente / beneficiário | {{código interno do escritório}} |
| Réu / órgão | {{INSS \| ente do RPPS \| entidade de previdência complementar}} |
| Advogado | {{do perfil.md}} |

## 2. Objeto

| Campo | Valor |
|---|---|
| Benefício ou pedido | {{espécie — ex.: aposentadoria especial, auxílio por incapacidade temporária, BPC}} |
| NB | {{}} |
| DER | {{}} |
| DIB | {{}} |
| DII (incapacidade) | {{}} |
| DCB / data do indeferimento | {{}} |
| Fundamento | {{dispositivo, com o diploma nomeado e ancorado em `context/lei/`}} |

## 3. Fase

**{{fase atual}}** *(fases: requerimento administrativo → recurso ao CRPS → ação judicial → recursos → cumprimento de sentença)*

## 4. Processo / protocolo

| Campo | Valor |
|---|---|
| Número | {{}} |
| Órgão | {{APS / CRPS / JEF / Vara Federal / Justiça Estadual (acidentário) / Tribunal}} |
| Seção / subseção / comarca | {{}} |

## 5. Situação atual

**{{o estado que muda a urgência}}** desde {{DATA}}.

{{Ex.: benefício cessado, indeferimento recebido, prazo de recurso correndo, perícia marcada, sentença publicada.}}

## 6. Prazos

| Prazo | Termo inicial | Vence em | Conferido por |
|---|---|---|---|
| {{}} | {{DATA}} | {{DATA}} | `prazos-previdenciarios` |

> **Nunca de cabeça.** Todo prazo aqui foi conferido pela skill de prazos, contra o anexo ou pelo script.

## 7. Quadro confirmado

**Confirmado em:** {{DATA}}

| Campo | Valor |
|---|---|
| Tipo de trabalho | {{petição inicial / recurso / parecer / cálculo / requerimento / planejamento}} |
| Polo | {{ativo / passivo}} |
| Objetivo | {{}} |
| Fatos-chave | {{3 a 5 linhas}} |
| Documentos recebidos | {{CNIS, PPP, LTCAT, carta de concessão, laudo — só a lista, sem o conteúdo}} |
| Prazo | {{data-limite ou "sem prazo correndo"}} |
| Restrição central | {{}} |
| Lacunas declaradas | {{o que ficou como "não sei"}} |

> Fato novo relevante reabre o quadro: nova confirmação antes de redigir de novo.

## 8. Estratégia escolhida

| | Caminho | Motivo |
|---|---|---|
| **Escolhido** | {{}} | {{}} |
| Descartado | {{}} | {{}} |
| Descartado | {{}} | {{}} |

## 9. Atos praticados *(append-only — nunca reescrever, só acrescentar)*

| Data | Ato | Script / conta | Assinatura |
|---|---|---|---|
| {{DATA}} | {{o que foi feito}} | {{calc_previdenciario_x v2.0.0 \| conta aberta}} | Entregue pela skill {{skill}} - plugin previdenciario-adv-os v2.0.0 |

## Próxima providência

**{{o que vem}}** — prazo fatal: **{{DATA}}**

---

<!-- ══════════════════════════════════════════════════════════════════════
     DADO PESSOAL SENSÍVEL (CNIS, laudo, perícia). Fica no diretório de
     trabalho do advogado. NUNCA dentro do plugin, NUNCA em repositório
     público, NUNCA em ferramenta externa.

     Se o diretório estiver em pasta sincronizada, o advogado foi avisado no
     onboarding e a confirmação está registrada no perfil.md.

     A linha de assinatura vive aqui e no rodapé da resposta — nunca dentro
     da peça que vai a protocolo.
     ══════════════════════════════════════════════════════════════════════ -->
