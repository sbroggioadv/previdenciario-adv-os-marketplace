# Perfil — previdenciario-adv-os

> Gravado pelo wizard `/start-previdenciario` (skill `previdenciario-onboarding`) em `<cwd>/previdenciario/perfil.md`.
> **Fica no diretório de trabalho do advogado, nunca dentro do plugin.** O plugin é somente leitura; escrever nele quebra na atualização.
> Lido pelo `previdenciario-master` (recorte e modo) e pelo `estilo-juridico-previdenciario` (voz). Nenhum hook lê este arquivo.

**Configurado em:** {{DATA}} · **Versão do plugin:** 2.0.0 · **Origem:** {{wizard 2.0.0 | migrado da 0.1.0 em DATA}}

---

## Identidade

| Campo | Valor |
|---|---|
| Nome | {{ADVOGADO_NOME}} |
| Registro profissional | OAB {{OAB_NUMERO}} / {{OAB_UF}} |
| Escritório | {{FIRM_NAME}} |
| Cidade / UF | {{CIDADE}} / {{UF}} |
| E-mail | {{EMAIL}} |
| Telefone | {{TELEFONE}} |

Campo não respondido fica em branco. Nada aqui é inventado.

## Recorte de atuação

| Campo | Valor |
|---|---|
| Lado | {{segurado, dependente e beneficiário (polo ativo) \| os dois lados, caso a caso}} |
| Frentes | {{RGPS — benefícios \| BPC/LOAS \| acidentário do trabalho \| planejamento previdenciário \| RPPS (lei seca, sem cálculo) \| previdência complementar (lei seca, sem cálculo)}} |

> **É preferência, não trava.** A `triagem-dogmatica-previdenciario` roteia qualquer caso que chegar, inclusive fora deste recorte e do lado oposto.

## Voz

| Campo | Valor |
|---|---|
| Tom | {{técnico-combativo \| técnico-cordial \| técnico-didático \| personalizado (migrado da 0.1.0): descrição}} |
| Intensidade | {{TOM_INTENSIDADE}}/10 |
| Postura | {{texto livre — migrado de `postura_default` da 0.1.0, ou em branco}} |
| Tom acolhedor automático | ativo — em caso com menor, pessoa com deficiência, doença grave ou idoso em situação de vulnerabilidade, o tom fica mais acolhedor e a proteção de dado sobe, sem o advogado pedir |
| Expressões preferidas | {{lista ou em branco}} |
| Termos a evitar | {{lista ou em branco}} |
| Formato de saída preferido | {{docx \| md \| pdf \| em branco}} |
| Modo de fluxo | {{checkpoint \| contínuo}} |

> Em modo contínuo, a confirmação do quadro do caso e a escolha entre 2 e 3 estratégias continuam obrigatórias antes de redigir.
> O tom do escritório vence as preferências de estilo da passada anti-IA; não vence os marcadores de tolerância zero do R4.AI nem as vedações éticas.

## Gates

| Gate | Estado |
|---|---|
| Suprema Corte (R1–R4) | {{ATIVA \| DESATIVADA}} |

> Com a Corte desativada, cada entrega diz no rodapé que a peça saiu **sem** a Corte.

## Ferramentas do escritório (opcional)

| Categoria | Ferramenta |
|---|---|
| Gestão processual | {{}} |
| Controle de prazo | {{}} |
| Cálculo | {{}} |
| CRM | {{}} |
| Outras | {{categoria: nome — uma por linha; inclui as categorias migradas da 0.1.0 sem equivalente acima}} |

> Disponibilidade de Python **não** é registrada aqui: muda entre sessões, e a skill de cálculo descobre na hora.

---

## LGPD

- Diretório escolhido: `{{CAMINHO}}`
- Pasta sincronizada (iCloud, OneDrive, Dropbox, Google Drive)? **{{sim \| não}}**
- {{SE SIM: confirmação expressa registrada em DATA — o advogado declarou, por escrito, ciência de que os casos podem subir para a nuvem.}}
- CNIS, PPP, LTCAT, laudo e perícia médica são dado pessoal sensível: ficam em `previdenciario/casos/`, nunca no plugin, nunca em ferramenta externa.

## Migração da 0.1.0 (só se houve)

- Arquivos antigos **preservados, não apagados:** {{lista — ex.: previdenciario/cowork-state.json, previdenciario/persona.md, previdenciario/CLAUDE.md, previdenciario/MEMORY.md, .claude/settings.local.json}}
- A 2.0.0 não lê mais esses arquivos nem injeta persona por hook. As variáveis `PREVIDENCIARIO_*` do `.claude/settings.local.json` ficaram sem uso; o advogado pode removê-las quando quiser.
- Itens não migrados: lista de skills ativas (na 2.0.0 todas ficam disponíveis), automações e tarefas agendadas, e a tese de revisão declarada inviável pelo STF (ver `CLAUDE.md` do plugin, verdade dura 1).

---

<!-- ══════════════════════════════════════════════════════════════════════
     ESTE ARQUIVO CONTÉM DADO DO ADVOGADO. Nunca sobe ao repositório público,
     nunca é gravado dentro do plugin, nunca sai da máquina dele.

     Os casos ficam em `previdenciario/casos/<slug>.md`, um arquivo por caso.
     Recriar o perfil NUNCA apaga `casos/`.

     Padrão canônico: PLAYBOOK-CLAUDE-v2/05-ONBOARDING-E-AMBIENTE.md §5.5
     ══════════════════════════════════════════════════════════════════════ -->
