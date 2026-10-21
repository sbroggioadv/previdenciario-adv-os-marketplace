---
name: previdenciario-onboarding
description: "Wizard de configuracao do plugin previdenciario ao perfil do escritorio. Cria previdenciario/perfil.md (identidade, lado, frentes, tom, modo de fluxo, Suprema Corte) e a pasta previdenciario/casos/ no diretorio de trabalho, com aviso LGPD. Migra a configuracao da 0.1.0 (cowork-state.json e persona.md) sem apagar os arquivos antigos. Roda de novo sem perder casos. Use quando o operador disser configurar previdenciario, instalar, primeira vez, atualizar configuracao, migrar da versao antiga, onboarding, /start-previdenciario. Nao use para abrir caso nem calcular: isso e do previdenciario-master."
---

> **🖱️ Escolhas = botoes:** em campos de **lista fechada** (comecar, diretorio local ou sincronizado, migrar ou comecar do zero, lado, frentes, tom, intensidade, modo de fluxo, Suprema Corte, confirmar gravacao, continuar/atualizar/recriar, sim/nao) use a ferramenta **AskUserQuestion** para mostrar **botoes clicaveis** (max. 4 por pergunta; se houver mais opcoes, divida em 2 perguntas). **Texto livre** (nome, OAB, cidade, escritorio, e-mail, telefone, ferramentas) segue como pergunta digitada normal.

# PREVIDENCIARIO ONBOARDING

> Camada 0. Wizard completo (padrao B+C): grava `previdenciario/perfil.md` + `previdenciario/casos/`. Linguagem acolhedora, sem jargao.

## Entradas
- Recebe: nada obrigatorio · estado da 0.1.0 no diretorio de trabalho (opcional, detectado sozinho)
- Chamada por: previdenciario-master (quando falta `previdenciario/perfil.md`) | Chama: nenhuma

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secoes 2 Pilares e 3 Mapa das 6 camadas - grep o titulo e leia a faixa), para explicar em 3 linhas o que o plugin cobre.
- `CLAUDE.md` do plugin (secao VERDADES DURAS, item 1), so para a nota de migracao.
- `templates/perfil.md.tpl` do plugin: modelo do perfil. Achar em `<pasta-base>/../../templates/perfil.md.tpl`; se nao existir, buscar pelo nome e usar o que cita `previdenciario-adv-os` na 1a linha.

## Objetivo
Configurar o plugin em ~5 minutos, migrar sem perda quem vem da 0.1.0 e devolver o advogado a porta unica sabendo o que esperar.

## Regras do wizard
1. Portugues do Brasil, tom acolhedor e direto. No maximo 3 perguntas por turno.
2. Lista fechada = AskUserQuestion. Texto livre = pergunta digitada.
3. Validar na hora: OAB so digitos (ponto opcional); UF com 2 letras maiusculas; e-mail com formato valido. Invalido: pedir de novo so aquele campo.
4. "Pular" e "nao sei" valem: o campo fica em branco, nunca inventado.
5. Nada e gravado antes do resumo confirmado (Bloco 8).
6. Nenhuma chamada a python, script ou hook. Ler com Read, gravar com Write; criar pasta com `mkdir -p`.

## Passo 0 — Leitura silenciosa (antes de perguntar)
`<raiz>` = diretorio de trabalho, ate o Bloco 1 confirmar outro. Toda leitura, copia e gravacao usa `<raiz>`. Verificar em `<raiz>`, nesta ordem:
1. `previdenciario/perfil.md` existe → **Fluxo de idempotencia**.
2. Senao, `previdenciario/cowork-state.json` ou `previdenciario/persona.md` existe → **Fluxo de migracao 0.1.0**.
3. Nada → wizard do Bloco 0 ao 9.

## Blocos de pergunta

### Bloco 0 — Abertura
Uma frase do que o plugin faz (Direito Previdenciario do segurado contra o INSS, do administrativo ao cumprimento, com calculo por script), tempo (~5 min) e botao [Comecar] [Agora nao].

### Bloco 1 — Diretorio + aviso LGPD
Mostrar `<raiz>/previdenciario/` como destino. Se o caminho contem `iCloud`, `Mobile Documents`, `CloudStorage`, `OneDrive`, `Dropbox` ou `Google Drive`, tratar como sincronizado.

> ⚠️ **Atencao: este plugin trata dado pessoal sensivel** (CNIS, PPP, laudo e pericia medica).
> Em pasta sincronizada, os casos podem subir para a nuvem. Recomendo um caminho **local**, fora de sync.

Botoes: [Usar este diretorio] [Indicar outro caminho]. Se sincronizado: exigir confirmacao **escrita** ("estou ciente do risco") e registrar a data no perfil. Outro caminho: ele vira `<raiz>`; refazer a checagem de sync e o Passo 0 nele.

### Bloco 2 — Identidade (texto livre)
Nome completo · OAB (numero) e UF · cidade e UF · escritorio · e-mail (opcional) · telefone (opcional). Dois turnos de no maximo 3 perguntas.

### Bloco 3 — Recorte (botoes)
- **Lado:** [Segurado, dependente e beneficiario - polo ativo (Recomendado)] [Os dois lados, caso a caso]. Explicar em 1 linha: define a perspectiva em que as pecas nascem. E preferencia, nao trava: a triagem roteia qualquer caso, inclusive do lado oposto.
- **Frentes** (multiSelect, 2 perguntas): (1) [RGPS - beneficios] [BPC/LOAS] [Acidentario do trabalho] [Planejamento previdenciario]; (2) [RPPS - lei seca, sem calculo] [Previdencia complementar - lei seca, sem calculo] [Nenhuma destas].

### Bloco 4 — Tom das pecas (botoes)
[Tecnico-combativo (Recomendado)] [Tecnico-cordial] [Tecnico-didatico]. Intensidade: [5] [7 (Recomendado)] [9] (outro valor de 0 a 10 vem digitado).
Avisar: em caso com menor, pessoa com deficiencia, doenca grave ou idoso vulneravel, o tom fica mais acolhedor e a protecao de dado sobe sozinho.

### Bloco 5 — Modo de fluxo (botoes)
[Checkpoint - confirma a cada etapa (Recomendado)] [Continuo]. Dizer que, mesmo no continuo, o quadro do caso e a escolha entre 2 e 3 estrategias sao confirmados antes de redigir.

### Bloco 6 — Suprema Corte (botoes)
[Manter ativa (Recomendado)] [Desativar]. A Corte audita toda entrega em R1-R4; da para pular caso a caso. Desativada, o rodape de cada entrega avisa que saiu sem ela.

### Bloco 7 — Ferramentas (opcional, texto livre)
Gestao processual, controle de prazo, calculo, CRM. Botao [Pular]. Nunca registrar se ha Python na maquina.

### Bloco 8 — Resumo e gravacao
Mostrar o resumo em tabela e perguntar [Gravar] [Corrigir um campo] [Cancelar]. Corrigir volta so ao campo apontado. Confirmado:
1. `mkdir -p <raiz>/previdenciario/casos` (sem Bash, e so se `casos/` nao existir: gravar `casos/LEIA-ME.md` com uma linha; arquivo existente nunca e regravado).
2. Se ja ha `perfil.md`: copia para `perfil.anterior-<AAAA-MM-DD-HHMM>.md` (nome ocupado: sufixo `-2`, `-3`; copia anterior nunca e regravada) e segunda confirmacao [Substituir o perfil atual] [Voltar].
3. Gravar `<raiz>/previdenciario/perfil.md` preenchendo `templates/perfil.md.tpl`; secao nao usada sai; campo sem resposta fica em branco.
4. Nao criar `.claude/settings.local.json` nem nada fora de `previdenciario/`.

### Bloco 9 — Encerramento
```
Plugin previdenciario-adv-os v2.0.2 configurado.
Advogado: <nome> - OAB <numero>/<UF> · Escritorio: <firma> (<cidade>/<UF>)
Lado: <lado> · Frentes: <lista> · Tom: <perfil> (<X>/10) · Modo: <modo>
Suprema Corte: <ATIVA | DESATIVADA> · Perfil em: <raiz>/previdenciario/perfil.md

PROXIMOS PASSOS (nao precisa reiniciar a sessao):
1. /previdenciario-master - descreva o caso; a porta unica roteia
2. /planejamento-previdenciario - qual regra vale mais e quando aposentar
3. /calculo-previdenciario - conta avulsa por script
4. /status-previdenciario - perfil, casos e versao
```

## Fluxo de idempotencia (perfil.md ja existe)
Ler o perfil e mostrar: advogado, lado, frentes, data. Botoes: [Continuar usando - nada muda] [Atualizar blocos] [Recriar do zero].
- Atualizar: perguntar quais blocos (2 a 7), refazer so esses, Bloco 8 (copia + dupla confirmacao).
- Recriar: confirmar antes de comecar; no Bloco 8, copia + segunda confirmacao. **`casos/` nunca e apagado nem tocado.**

## Fluxo de migracao 0.1.0
1. Avisar: "Encontrei a configuracao da versao 0.1.0. Desde a 2.0.0 o plugin grava tudo em `previdenciario/perfil.md` e nao injeta mais persona por hook."
2. Botoes: [Converter para o perfil novo (Recomendado)] [Comecar do zero] [Cancelar]. Nas duas primeiras, **nenhum arquivo antigo e apagado, movido ou editado**.
3. Converter: ler com Read `previdenciario/cowork-state.json`; sem ele, `persona.md` pelos titulos (Identidade Profissional, Areas de Atuacao Ativas, Tom de Voz e Postura, Suas Ferramentas, Diretrizes Permanentes: formato e status da Corte). Do JSON, mapear:
   - `identity.advogado_nome`, `oab_numero`, `oab_uf`, `firm_name`, `cidade`, `uf`, `email`, `telefone` → Identidade
   - `tom_voz.perfil` (inclusive `personalizado`) e `intensidade_combativa` → Tom e Intensidade; `postura_default` (na persona, "Postura default") → Postura, sempre preservada; `expressoes_assinatura` e `termos_a_evitar` → Voz
   - Frentes: RGPS sempre; `skills.opt_in_active` com `rpps-servidor-publico` → RPPS, `previdencia-complementar` → Complementar, `acidentario-do-trabalho` → Acidentario. Sem sinal: perguntar o Bloco 3 · `suprema_corte.enabled` → Gates · `preferences.sync_folder_warning_acknowledged` → so indica que ja houve aviso; o Bloco 1 roda de novo
   - `tools.*` → Ferramentas (fora das 4 categorias, em Outras como `categoria: nome`); `preferences.output_format_preferido` (docx, md ou pdf) → Formato
   Valor nulo, vazio ou com `{{` nao resolvido = campo em branco.
4. Nao migrar: listas de skills ativas (desde a 2.0.0 todas ficam disponiveis), `automations` e tarefas agendadas (o plugin nao agenda nada desde a 2.0.0) e a tese de revisao que o `CLAUDE.md` declara inviavel (verdade dura 1). Dizer isso ao advogado em 1 linha.
5. Perguntar sempre Bloco 1 (LGPD), lado e modo, e todo campo de Recorte, Voz ou Gates que nao se recuperou (frentes vindas so da persona: perguntar o Bloco 3). Depois Bloco 8, com "Origem: migrado da 0.1.0" e a lista de arquivos antigos preservados.
6. No encerramento, informar: `previdenciario/CLAUDE.md`, `previdenciario/MEMORY.md` e `.claude/settings.local.json` antigos ficaram intactos e o plugin novo nao os usa, mas o Claude ainda pode carregar o `CLAUDE.md` e o `settings.local.json` (variaveis `PREVIDENCIARIO_*`). O advogado pode revisa-los ou remove-los manualmente quando quiser; o plugin nao mexe neles. Anotacoes do `MEMORY.md` antigo nao viram caso sozinhas.

## Se faltar anexo
Sem `templates/perfil.md.tpl`: gravar o perfil com as mesmas secoes (Identidade, Recorte, Voz, Gates, Ferramentas, LGPD, Migracao) e avisar em uma linha que o modelo nao foi achado e convem reinstalar o plugin. Sem a metodologia: seguir o wizard e dizer que a explicacao das camadas fica para o master.

## Entrega obrigatoria final
- `previdenciario/perfil.md` gravado + `previdenciario/casos/` existente + resumo do Bloco 9.

## Vedacoes
- NUNCA coletar no wizard: CPF, NIT, documento de identificacao, conteudo de CNIS, laudo ou pericia, nome de cliente, nome de menor.
- NUNCA apagar, mover ou editar `casos/` nem arquivo da 0.1.0.
- NUNCA sobrescrever perfil existente sem dupla confirmacao e copia anterior.
- NUNCA gravar dentro da pasta do plugin nem enviar dado a servico externo.
- NUNCA antecipar tese nem prometer resultado: a postura honesta vale ja no onboarding.

## Guard
Nao inventar dado do advogado: o que nao foi respondido fica em branco. Pasta sincronizada so segue com confirmacao escrita registrada. Configuracao e descartavel; o trabalho em `casos/` nao.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do perfil.md:
`Entregue pela skill previdenciario-onboarding - plugin previdenciario-adv-os v2.0.2`.
