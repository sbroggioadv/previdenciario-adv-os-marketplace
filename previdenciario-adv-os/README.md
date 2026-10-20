# Previdenciário Adv OS — v2.0.0

Plugin de Direito Previdenciário brasileiro para o advogado do **segurado, do dependente e do beneficiário contra o INSS**: do requerimento administrativo ao cumprimento de sentença, com as contas feitas por script e cada número acompanhado da fonte.

Autoria: IA Combativa. O plugin não traz identidade de escritório: o seu é configurado por `/start-previdenciario` e fica na pasta que você escolher.

## O que cobre

- **RGPS:** aposentadorias (regra permanente, direito adquirido e as transições da EC 103/2019), aposentadoria especial e conversão de tempo, benefícios por incapacidade, auxílio-acidente, revisão de RMI.
- **BPC/LOAS**, com a renda per capita "igual ou inferior a 1/4" e sem abono anual.
- **Acidentário do trabalho.**
- **Via administrativa:** INSS e recurso ao CRPS.
- **Via judicial:** petição inicial, réplica, mandado de segurança, audiência, recursos (JEF, TRF, PEDILEF, REsp, RE) e cumprimento de sentença com RPV ou precatório.
- **RPPS e previdência complementar:** triagem e encaminhamento, sem conta (veja "Limites").

## Como funciona

34 skills em 6 camadas:

| Camada | Papel |
|---|---|
| C0 Orquestração e QA | porta única, configuração, triagem, memória do caso, voz do escritório, revisão final |
| C1 Fundação | lei seca, jurisprudência selada, validador de citações, guarda anti-alucinação |
| C2 Transversal | estratégia com 2 a 3 caminhos, cálculo, prazos, parecer, documentos e visual law |
| C3 Análise e prova | CNIS, PPP e LTCAT, carta de concessão ou indeferimento, perícia médica |
| C4 Benefícios e vias | planejamento previdenciário, acidentário, BPC, RPPS, complementar, administrativo |
| C5 Judicial e recursos | da inicial ao cumprimento de sentença |

A primeira pergunta da triagem é sempre sobre prazo: se há recurso ou resposta correndo, ou benefício cessado ou indeferido há menos de 30 dias, o caso entra por `prazos-previdenciarios` antes de qualquer outra coisa.

### Cálculo

Sete scripts locais fazem as contas: CNIS e carência, tempo de contribuição, regras de transição, incapacidade, RMI, valor da causa e RPV. Rodam no seu computador, com Python 3, sem internet. Cada resultado vem com a regra e a fonte de cada número e a memória passo a passo.

Se falta um dado obrigatório da entrada, como a espécie do benefício, o script para sem fazer conta e diz o que falta (código de saída 2). Se a entrada está completa, mas a conta não fecha (falta uma tabela oficial ou um valor que só você tem), o script **não estima**: devolve a fórmula aberta, preenchida até onde dá, com a marca `[VERIFICAR]` (código de saída 3). Quando o texto legal admite duas leituras, saem as duas contas, completas e com número, para você escolher (também código de saída 3). Sem Python no computador, a skill entrega a mesma conta aberta, avisando que o número não foi conferido por script.

### Citações

A lei seca usada pelo plugin está anexada (EC 103/2019, Leis 8.213/1991, 8.212/1991, 8.742/1993 e 10.259/2001, Decreto 3.048/1999, IN PRES/INSS 128/2022, Manual de Cálculos da Justiça Federal de 2026, entre outras). Toda citação de dispositivo, súmula ou tema é conferida contra esses anexos. O que não tem âncora sai marcado `[VERIFICAR]`, nunca como fato. A revisão final R1–R4 (Suprema Corte) vem ligada e audita cada entrega. Você pode desligá-la em `/start-previdenciario` ou pular caso a caso; nesse caso a entrega sai com o aviso "Suprema Corte: não executada" no rodapé.

## Comandos

| Comando | Para quê |
|---|---|
| `/start-previdenciario` | configura o escritório (e migra a configuração da versão 0.1) |
| `/previdenciario-master` | porta única: descreva o caso e o plugin conduz |
| `/status-previdenciario` | mostra o perfil, os casos e a versão |
| `/calculo-previdenciario` | cálculo avulso: cnis, tempo, transicao, incapacidade, rmi, valor-causa ou rpv |
| `/planejamento-previdenciario` | qual regra vale mais, quando aposentar, quanto vai receber |
| `/peticao-previdenciaria` | peça processual |
| `/recurso-previdenciario` | recurso administrativo ou judicial |
| `/parecer-previdenciario` | parecer |
| `/revisao-previdenciaria-final` | só a revisão final sobre um texto já pronto |

## Onde ficam os seus dados

Tudo o que o plugin grava fica na pasta que você escolher em `/start-previdenciario` (por padrão, a pasta em que você trabalha), dentro de `previdenciario/`:

- `previdenciario/perfil.md`: identidade e preferências do escritório;
- `previdenciario/casos/<caso>.md`: o quadro confirmado, a estratégia escolhida e o que foi entregue em cada caso.

CNIS, laudo médico e documentos do cliente são dado pessoal sensível (LGPD), e o plugin não os envia a nenhum serviço externo. Mas, se a pasta escolhida for sincronizada (Dropbox, iCloud, OneDrive, Google Drive), os casos sobem para a nuvem junto com ela. Por isso a configuração recomenda uma pasta local e pede confirmação escrita para usar uma pasta sincronizada. O aviso que aparece ao abrir a sessão é uma linha de texto impressa por um `echo`: nenhum script do plugin roda e nada é gravado nesse momento.

## Limites desta versão

- **RPPS:** triagem e checklist; nenhum cálculo do servidor.
- **Previdência complementar:** triagem e checklist; cita só o que estiver anexado.
- **Fator previdenciário:** sai como fórmula, porque a tábua de mortalidade do IBGE não está anexada.
- **Limite de ruído da aposentadoria especial:** não é automatizado; exige a prova técnica (PPP amparado em laudo).
- **Aposentadoria da pessoa com deficiência e pensão por morte:** sem script.
- **Revisão da vida toda:** não é oferecida como tese. O STF fixou que a regra do art. 3º da Lei 9.876/1999 é obrigatória para quem se enquadra nela (ADIs 2.110 e 2.111; Tema 1.102); o plugin explica o que ainda se pode fazer pelo segurado.

## Atualizando da versão 0.1

Veja a seção "O que muda para quem já instalou" no [`CHANGELOG.md`](CHANGELOG.md). Em resumo: depois de atualizar, rode `/start-previdenciario` uma vez para converter a configuração antiga; nada do que você já tinha é apagado. O plugin novo não usa o `CLAUDE.md` e o `.claude/settings.local.json` da versão 0.1, mas o Claude ainda pode carregá-los: revise ou remova esses arquivos quando quiser.

## Fronteiras

Cálculo judicial genérico e auditoria de laudo contábil ficam no plugin de cálculos judiciais; busca de jurisprudência ao vivo, no plugin de jurisprudência; reconhecimento de vínculo trabalhista para o CNIS, no plugin trabalhista.
