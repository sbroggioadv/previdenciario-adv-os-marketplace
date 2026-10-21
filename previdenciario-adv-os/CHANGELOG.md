# Changelog

Todas as mudanças relevantes do plugin `previdenciario-adv-os`. Formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões pelo [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.0.2] - 2026-10-21

Correção sem mudança de uso: nada a refazer na configuração. Atualize pelo mesmo marketplace; não é preciso rodar `/start-previdenciario` de novo.

### Corrigido

- **Alerta do CNJ quando o teto global da Selic é aplicado.** No cálculo federal depois da EC 136, quando a Selic sobre o valor consolidado fica abaixo de IPCA + 2% a.a. e há juros anteriores (não Selic), a saída agora traz o alerta `[VERIFICAR]` com o texto literal do Provimento CNJ 207/2025 (art. 2º, III: a Selic "exclusivamente sobre o principal") ao lado da Res. CJF 983/2026 (art. 7º, §3º, III: a Selic sobre o valor consolidado), dizendo que as duas bases diferem e que o script segue a Res. CJF 983/2026. No RPV o alerta aparece na fase R2, com o prefixo `[motor de atualização, R2]`. O valor calculado não muda. Sem juros anteriores as duas bases coincidem e o alerta não sai. Fecha a ressalva registrada na 2.0.1.

### Dados

- Motor de atualização monetária igual ao do plugin de cálculos judiciais 0.1.3 (cópia conferida por sha256). Só o motor mudou, e só pelo alerta acima; nenhum índice e nenhum resultado mudou.

### Continua em aberto

- **Reajustes de 05/1995 e 05/1996:** sem texto capturado (o DOU só tem imagem).
- **Benefício com início anterior a 2004:** o valor da causa e a revisão da RMI abrem a conta (exit 3, fórmula com `[VERIFICAR]`), porque a compensação do aumento do mínimo no reajuste de junho não está modelada.
- **Portaria de reajuste de 2027:** ainda não publicada.

## [2.0.1] - 2026-10-20

Correção sem mudança de uso: nada a refazer na configuração. Atualize pelo mesmo marketplace; não é preciso rodar `/start-previdenciario` de novo.

### Corrigido

- **Valor da causa: o complemento até o salário mínimo não é reajustado.** Quando a renda do benefício ficava abaixo do mínimo e era elevada até ele, o script somava esse complemento à base e aplicava o reajuste anual sobre o total. A Lei 8.213, art. 41-A, §6º, manda compensar o aumento que veio da elevação ao mínimo no momento do reajuste: o índice incide sobre a renda própria do benefício, e o piso é conferido depois. Exemplo: DIB em 01/2020 e renda de R$ 1.039,00; em 01/2021 o script dava R$ 1.101,95, quando o certo é reajustar R$ 1.039,00 (R$ 1.095,63) e elevar ao mínimo (R$ 1.100,00). Valores da causa de benefícios no piso calculados com a 2.0.0 merecem nova conferência. A revisão da RMI já fazia a conta certa e ganhou teste para não regredir.
- **Valor da causa, RPV e revisão da RMI em 2007.** A data da MP 404/2007 foi capturada (11/12/2007, em vigor na publicação, DOU de 12/12/2007; `context/lei/mp-404-2007.md` e `lei-11665-2008.md`). Até a competência 11/2007 o pagamento é sempre no mês seguinte; desde a competência 12/2007 vale a antecipação do art. 41-A, §3º, para quem recebe até um mínimo. Antes, toda competência de 2007 com vencimento antecipado saía em aberto (exit 3); agora uma data no próprio mês até 11/2007 é recusada (exit 2) e, desde 12/2007, aceita dentro da janela.
- **Reajuste de 01/08/2006.** Fechado pela Lei 11.430/2006, art. 3º, e pela Portaria MPS 342/2006, art. 1º e Anexo I: 5,01% (ou o pro rata da DIB) sobre a renda de março/2006, substituindo os 5,00% de abril, só para benefício com início até 31/03/2006. Antes, a renda abria a partir dessa data.
- **Teto de jan/2004 e de jan–fev/2011.** Vale o ato normativo, não o AEPS: R$ 2.400,00 de 31/12/2003 a 31/01/2004 (EC 41/2003, art. 5º) e R$ 3.691,74 em jan–fev/2011 (PI MPS/MF 407/2011), com a divergência registrada nos dados. Antes, as duas janelas eram lacuna.

### Dados

- Reajustes anuais de 06/1997 a 06/2001 na tabela (`scripts/data/reajustes-rgps.json`), com o Anexo pro rata e a incorporação do teto de cada portaria, capturados da base Datalegis da ANTT (`context/lei/portaria-*-reajuste.md`). Os motores ainda abrem a conta para benefício com início até 2003 (veja "Limites" no README).
- Motor de atualização monetária igual ao do plugin de cálculos judiciais 0.1.2 (cópia conferida por sha256). Nenhum índice e nenhum resultado mudou; os alertas `[VERIFICAR]` do regime do requisitório da EC 136 agora citam o texto literal do Provimento CNJ 207/2025, capturado em `context/lei/provimento-cnj-207-2025.md` (exceto quando o teto global da Selic é aplicado; veja "Continua em aberto").

### Continua em aberto

- **Reajustes de 05/1995 e 05/1996:** sem texto capturado (o DOU só tem imagem).
- **Benefício com início anterior a 2004:** o valor da causa e a revisão da RMI abrem a conta (exit 3, fórmula com `[VERIFICAR]`), porque o aumento do mínimo de abril/maio era descontado no reajuste de junho e essa compensação não está modelada. A tabela de 1997 a 2001 já está carregada para quando estiver.
- **Portaria de reajuste de 2027:** ainda não publicada.
- **Alerta do CNJ quando o teto global da Selic é aplicado (ressalva conhecida):** no cálculo federal depois da EC 136, quando a Selic sobre o valor consolidado fica abaixo de IPCA + 2% a.a. e o teto é aplicado, o script mantém a fórmula da Res. CJF 983/2026 (art. 7º, §3º, III), que é a aceita, mas não repete o alerta com o texto literal do Provimento CNJ 207/2025 (art. 2º, III: Selic "exclusivamente sobre o principal"). O valor calculado não muda; nesse caso, confira você a divergência entre as duas normas antes de usar a conta. Correção prevista no plugin de cálculos 0.1.3 e no previdenciário 2.0.2.

### Documentação

- README ganhou a linha de instalação pelo marketplace.
- A tabela de saídas de `context/calculo-transicao.md` (§8) foi alinhada ao script: sai em aberto (exit 3) também quando só a data em que a regra se cumpre muda com a normalização das competências.

## [2.0.0] - 2026-10-15

Versão maior: muda a configuração gravada no seu computador, o aviso de início e os arquivos auxiliares do plugin. Os nomes das skills e dos comandos que você já usa continuam os mesmos.

### O que muda para quem já instalou

**Como atualizar.** Atualize o plugin pelo mesmo marketplace de onde você o instalou. Depois, rode `/start-previdenciario` uma vez.

**Configuração do escritório (migração).** A versão 0.1 guardava sua configuração em `previdenciario/cowork-state.json` e `previdenciario/persona.md`. A 2.0.0 usa um arquivo só, `previdenciario/perfil.md`. Ao rodar `/start-previdenciario`, o assistente encontra a configuração antiga e oferece:

- **converter para o perfil novo** (recomendado): nome, escritório, frentes de atuação, tom de voz e preferências são aproveitados. Mesmo assim, ele sempre reconfirma o aviso de LGPD (a pasta dos dados), o lado em que você atua e o modo de fluxo, e pergunta o que não deu para recuperar;
- **começar do zero.**

Nos dois casos, **nenhum arquivo antigo é apagado, movido ou editado**. Os arquivos `previdenciario/CLAUDE.md`, `previdenciario/MEMORY.md` e `.claude/settings.local.json` da versão 0.1 ficam intactos, e o plugin novo não os usa. Mas o Claude ainda pode carregá-los: o `CLAUDE.md` traz instruções da versão antiga, e o `settings.local.json` mantém as variáveis `PREVIDENCIARIO_PERSONA` e `PREVIDENCIARIO_COWORK_PATH`. Revise ou remova esses arquivos (ou só as variáveis) manualmente, quando quiser; o plugin não mexe neles. Não são migradas: a lista de skills ativas (na 2.0.0 todas ficam disponíveis), automações e tarefas agendadas (a 2.0.0 não agenda nada) e a tese da revisão da vida toda (veja abaixo). Anotações do `MEMORY.md` antigo não viram caso sozinhas.

**Seus casos.** Cada caso passa a ter um arquivo próprio em `previdenciario/casos/<caso>.md`, com o quadro confirmado, a estratégia escolhida e o que foi entregue. A pasta `casos/` nunca é apagada pelo plugin, nem quando você refaz a configuração.

**Aviso de início de sessão.** Continua sendo uma linha de texto, impressa por um `echo`, agora com a versão e o caminho para começar. Nenhum script do plugin roda e nada é gravado ao abrir a sessão; o plugin só grava em `previdenciario/` quando você usa um comando ou uma skill.

**Arquivos auxiliares que saem.** A configuração deixou de depender de Python, e saem do plugin `scripts/state.py`, `scripts/render.py`, `scripts/hook-utils.py`, `scripts/resolve-persona.py`, `scripts/fingerprint.py`, `scripts/state-schema.json` e a pasta `hooks/scripts/`. A sua identidade não é mais injetada em toda sessão: o plugin lê o `perfil.md` quando precisa.

**Skills.** Nenhuma skill foi removida nem mudou de nome; todas foram reescritas sobre a lei seca anexada. Chegam skills novas:

- `memoria-de-caso-previdenciario`: guarda o quadro confirmado, a estratégia escolhida e o que foi entregue em `previdenciario/casos/<caso>.md`;
- `base-legal-previdenciaria`: acha o dispositivo na lei anexada e avisa quando o mesmo número de artigo existe em mais de um diploma;
- `validador-previdenciario`: confere cada citação contra os anexos antes da revisão final;
- `anti-alucinacao-previdenciario`: guarda permanente contra citação sem âncora;
- `prazos-previdenciarios`: prazos administrativos e processuais; é a primeira parada quando há prazo correndo;
- `parecer-previdenciario`: o `/parecer-previdenciario` agora tem skill própria;
- `planejamento-previdenciario`: qual regra vale mais, quando aposentar, quanto vai receber;
- `bpc-loas-previdenciario`: trilha própria do BPC.

**Comandos.** Os 8 comandos continuam com o mesmo nome. Cinco que apontavam para skill inexistente ou com nome errado foram corrigidos: `/start-previdenciario`, `/status-previdenciario`, `/calculo-previdenciario`, `/parecer-previdenciario` e `/revisao-previdenciaria-final`. Chega um comando novo, `/planejamento-previdenciario`.

**Revisão da vida toda.** Saiu do plugin como tese: do cardápio da configuração, da petição inicial e da ação revisional. O STF fixou que a regra do art. 3º da Lei 9.876/1999 é obrigatória para quem se enquadra nela, ainda que a regra definitiva fosse mais favorável (ADIs 2.110 e 2.111; Tema 1.102). Ajuizar a tese hoje expõe o cliente a sucumbência, custas e perícia. O plugin passa a orientar a defesa do segurado contra cobrança indevida, dentro dos critérios de modulação fixados pelo STF.

**Contas que saem abertas.** Entrada inválida, como a falta da espécie do benefício, faz o script parar e dizer o que falta (código de saída 2). O código de saída 3 marca a conta que depende de dado ou de decisão do advogado e tem duas formas: (a) a conta não fecha (falta uma tabela oficial ou um valor que só o advogado tem) e sai a fórmula aberta, preenchida até onde dá, com a marca `[VERIFICAR]`; (b) o texto legal admite duas leituras e saem as duas contas completas, com número, para o advogado escolher e declarar na peça. É uma decisão de produto: o que não fecha vira fórmula, não estimativa. Exemplos de (a): fator previdenciário (sem a tábua do IBGE), série dos juros da poupança de maio/2012 a nov./2021 sem o valor consolidado de dez./2021, taxa legal de competências posteriores a maio/2026. Exemplo de (b): valor da causa com abono anual, em que a inclusão do abono nas vincendas não é pacífica. A competência 11/2019 trabalhada só em parte sai marcada `[VERIFICAR]`. Os casos de referência que conferem os scripts rodam como teste de regressão e aguardam conferência de advogado revisor.

### Adicionado

- Sete scripts de cálculo locais, sem rede: CNIS, carência e qualidade de segurado; tempo de contribuição (comum, especial convertido e concomitância); regras de transição da EC 103/2019; incapacidade e auxílio-acidente; RMI, com divisor mínimo, descarte, decadência e prescrição; valor da causa e alçada do JEF; atrasados por fatia de regime e RPV ou precatório. Saída com regra e fonte de cada número, memória passo a passo e fórmula aberta.
- Motores de atualização monetária e de prazo em dias, copiados do plugin de cálculos judiciais e conferidos por sha256.
- Lei seca em `context/lei/`, metodologia do domínio, conta aberta de cada script em `context/calculo-*.md` e guia de escrita sem marca de IA.
- Revisão final R1–R4 com verificação de marcas de texto gerado por IA. Vem ligada; pode ser desligada na configuração ou pulada caso a caso, e então a entrega sai com o aviso "Suprema Corte: não executada".
- Aviso de LGPD na configuração: CNIS e laudo são dado pessoal sensível e ficam na pasta que o advogado escolher. Se ela for sincronizada (Dropbox, iCloud, OneDrive, Google Drive), os casos sobem para a nuvem; a configuração recomenda pasta local e pede confirmação escrita para usar uma sincronizada.

### Mudou

- Configuração em `previdenciario/perfil.md`, com botões nas escolhas de lista fechada, e casos em `previdenciario/casos/`.
- Triagem começa pela pergunta de prazo: recurso ou resposta correndo, ou benefício cessado ou indeferido há menos de 30 dias.
- Recursos tratados como peças independentes: JEF, TRF, PEDILEF, REsp, RE e CRPS.
- `plugin.json` reduzido a nome, versão, descrição e autor.

### Corrigido

- Conversão de tempo especial em comum só até 13/11/2019, pela data do trabalho, com o vínculo fatiado nessa data (EC 103, art. 25, §2º; Decreto 3.048, art. 188-P, §5º).
- Período básico de cálculo de 100% desde 07/1994 atribuído à EC 103, art. 26, e coeficiente de 60% mais 2 pontos por ano de contribuição acima de 20 (homem) ou de 15 (mulher e especial de 15); a incapacidade permanente acidentária fica em 100%.
- Divisor mínimo de 108 para o filiado até 07/1994, nas aposentadorias com fato gerador desde 05/05/2022, exceto a por incapacidade permanente (Lei 8.213, art. 135-A).
- Atualização e juros contra o INSS em fatias por competência, pelo Manual de Cálculos da Justiça Federal (ed. jul./2026) e pela Res. CJF 983/2026, conforme o período e a natureza do benefício: indexadores históricos do Manual até ago./2006; de set./2006 a nov./2021, INPC no previdenciário e IPCA-E no BPC; Selic de dez./2021 a ago./2025 (EC 113/2021); desde set./2025, INPC no previdenciário e IPCA-15 no BPC, mais taxa legal; Res. CJF 983/2026 no requisitório. Antes era "IPCA-E até 2021 e Selic depois".
- Carência depois da perda da qualidade de segurado: a metade só reabre o cômputo das contribuições anteriores; a carência exigida continua a integral (Lei 8.213, art. 27-A).
- Auxílio-acidente sem carência, sem piso de um salário mínimo e sem acumulação com aposentadoria (Lei 8.213, arts. 26, I, e 86).
- BPC com renda per capita "igual ou inferior a 1/4" do salário mínimo, sem carência e sem abono anual (LOAS, art. 20, §3º; Lei 8.213, art. 40).
- RPV de 60 salários mínimos conferida pelo valor atualizado até a transmissão, com "renúncia ao excedente" e vedação de fracionar (Lei 10.259, art. 17; Res. CJF 983/2026).
- Temas e súmulas citados só a partir da lista selada em `context/lei/temas-sumulas-prev.md`; os que não tinham âncora saíram.

### Removido

- Revisão da vida toda como tese.
- `scripts/state.py`, `scripts/render.py`, `scripts/hook-utils.py`, `scripts/resolve-persona.py`, `scripts/fingerprint.py`, `scripts/state-schema.json` e `hooks/scripts/`.
- Injeção da persona em toda sessão e gravação em `.claude/settings.local.json`.

## [0.1.1] - 2026-10-13

### Corrigido

- `hooks.json` no formato aceito pelo Claude Code (eventos dentro da chave `hooks`). Sem o envelope, o aviso de início não aparecia.

## [0.1.0] - 2026-05-24

### Adicionado

- Primeira versão pública: 26 skills, 8 comandos e configuração do escritório por `/start-previdenciario`.
