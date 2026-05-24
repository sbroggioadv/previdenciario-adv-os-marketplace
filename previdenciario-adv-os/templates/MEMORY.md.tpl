# MEMORY.md — {{SCOPE_NAME}}

> Memória externa deste workspace/pasta. Persistente entre sessões do Claude Code.

---

## Como Funciona

**Leitura automática:** O Claude lê este arquivo no início de cada sessão. Usa o que encontra para informar o trabalho.

**Escrita user-triggered:** O Claude **NUNCA** escreve aqui automaticamente. Só adiciona itens quando você pedir explicitamente:

- "lembre disso"
- "anote esta informação"
- "salve para próximas sessões"
- "registre na memória"
- "não esqueça"
- "memorize"

Quando triggered, o Claude escreve imediatamente e confirma.

**Persistência:** Itens permanecem aqui até você pedir para remover ou alterar.

**Conflitos:** Se você pedir para lembrar algo que conflita com item existente, o Claude flagga em vez de sobrescrever silenciosamente.

---

## Categorias Sugeridas

Você pode pedir para o Claude organizar itens em categorias. Sugestões iniciais:

- **Jurisprudência recorrente** que você costuma citar
- **Padrões internos** do escritório (ex: "sempre incluir cláusula X em contratos de tipo Y")
- **Decisões estratégicas** tomadas em casos importantes
- **Modelos preferidos** para tipos específicos de peça
- **Convenções de nomenclatura** de arquivos
- **Fluxos operacionais** específicos
- **Aprendizados** de erros passados

---

## Itens Memorizados

*(Vazio. Adicione itens pedindo "lembre disso" ao Claude durante uma sessão.)*

---

**Workspace:** `{{COWORK_PATH}}`
**Escopo:** {{SCOPE_NAME}}
**Plugin:** `previdenciario-adv-os` v{{PLUGIN_VERSION}}
**Inicializado em:** {{GENERATED_AT}}
