# CLAUDE.md — {{AREA_DISPLAY_NAME}}

> Pasta de **{{AREA_DISPLAY_NAME}}** do {{FIRM_NAME}}. Esta pasta contextualiza o Claude para tudo que produzir relacionado a esta área.

---

## Propósito da Pasta

Gestão e produção de material para **{{AREA_DISPLAY_NAME}}** do escritório. Centraliza:

{{#TIPO_ATUACAO_CONTENCIOSO}}
- Processos em andamento
- Petições, contestações, recursos, agravos, embargos, tutelas
- Estratégia processual
- Memórias de cálculo
- Comunicação com clientes sobre processos
{{/TIPO_ATUACAO_CONTENCIOSO}}
{{#TIPO_ATUACAO_CONSULTIVO}}
- Pareceres jurídicos
- Análises de risco
- Consultas formais
- Adequação regulatória
{{/TIPO_ATUACAO_CONSULTIVO}}
{{#TIPO_ATUACAO_MISTO}}
- Operações contenciosas e consultivas
- Toda produção jurídica relacionada à área
{{/TIPO_ATUACAO_MISTO}}

---

## Skills Sugeridas para Esta Área

> A skill `firm-master` é acionada SEMPRE em qualquer demanda. As listadas abaixo são complementares.

{{#SKILLS_SUGERIDAS_LIST}}
- `{{.}}`
{{/SKILLS_SUGERIDAS_LIST}}

{{^SKILLS_SUGERIDAS_LIST}}
*(Nenhuma skill sugerida específica para esta área — `firm-master` orquestra automaticamente conforme a demanda.)*
{{/SKILLS_SUGERIDAS_LIST}}

---

## Polo Predominante

{{#POLO_PREDOMINANTE_AUTOR}}
O escritório atua predominantemente como **autor/requerente/recorrente** nesta área. Estratégia padrão é **propositiva e ofensiva**.
{{/POLO_PREDOMINANTE_AUTOR}}
{{#POLO_PREDOMINANTE_REU}}
O escritório atua predominantemente como **réu/requerido/recorrido** nesta área. Estratégia padrão é **defensiva e impugnativa**, sem suavizar contraposições.
{{/POLO_PREDOMINANTE_REU}}
{{#POLO_PREDOMINANTE_AMBOS}}
O escritório atua em **ambos os polos** nesta área. Sempre identificar polo no início da demanda antes de definir estratégia.
{{/POLO_PREDOMINANTE_AMBOS}}

---

## Subpastas

{{#SUBFOLDERS_LIST}}
- `{{.}}/`
{{/SUBFOLDERS_LIST}}

---

## Instruções Específicas

- Toda produção segue o tom configurado em `<COWORK>/previdenciario/persona.md` (perfil `{{TOM_VOZ_PERFIL}}`, intensidade {{TOM_VOZ_INTENSIDADE}}/10)
- Output preferido: `{{OUTPUT_FORMAT_PREFERIDO}}` (peças prontas para protocolo/assinatura)
- **Suprema Corte aplicada automaticamente** (R1→R2→R3→R4) antes de entregar peças/contratos/pareceres
- Sempre **mostrar cadeia de raciocínio** e **plano de ação** antes de executar
- **Nunca inventar** fundamentos, jurisprudência ou doutrina — pesquisar e citar
- **Sempre informar o cliente** dos riscos da situação

---

## O Que Lembrar

- Esta área tem **prazos processuais fatais** (se contenciosa) — sempre identificar e confirmar prazo antes de qualquer ação
- Cada cliente tem canal próprio de comunicação (configurado individualmente)
- Estratégias contextualizadas ao cenário jurídico **vigente em {{ANO_VIGENTE}}**
- Esta pasta tem `MEMORY.md` próprio para casos, decisões e padrões aprendidos nesta área

---

## MEMORY SYSTEM

Esta pasta tem `MEMORY.md`. Memória externa específica desta área de atuação.

**No início de cada sessão:** O Claude lê o `MEMORY.md` desta pasta antes de trabalhar em demandas desta área.

**Memória é user-triggered.** Só escreve quando você pedir explicitamente. Itens podem incluir: jurisprudência recorrente que você cita, padrões internos do escritório para esta área, decisões estratégicas tomadas, modelos preferidos.

---

**Pasta gerada por:** Plugin `previdenciario-adv-os` v{{PLUGIN_VERSION}}
**Configurável em:** `/start --update` ou `/cowork-set`
**Última atualização:** {{GENERATED_AT}}
