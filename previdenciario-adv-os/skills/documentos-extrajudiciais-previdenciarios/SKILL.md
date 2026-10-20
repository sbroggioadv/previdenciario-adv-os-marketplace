---
name: documentos-extrajudiciais-previdenciarios
description: "Redige documento previdenciario que nao e peca processual nem parecer: notificacao extrajudicial (ex-empregador para PPP e LTCAT, empresa sucessora, hospital para prontuario), requerimento ou oficio a orgao, e mensagem ao cliente em linguagem simples (concessao, indeferimento, pericia, pedido de documentos). Use quando o operador disser notificacao, notificar a empresa, pedir o PPP, oficio, requerimento, mensagem ao cliente, explicar ao segurado. Nao use para parecer (parecer-previdenciario) nem para peca judicial ou recurso."
---

# DOCUMENTOS-EXTRAJUDICIAIS-PREVIDENCIARIOS

> Camada C2 (transversal). Tres formatos, cada um com destinatario, tom e estrutura proprios: notificacao, requerimento/oficio e mensagem ao cliente.

## Entradas
- Recebe: formato pedido e destinatario (obrigatorio) · fato que motiva o documento e o que se quer obter (obrigatorio) · `previdenciario/casos/<slug>.md` e `previdenciario/perfil.md` (se existirem)
- Chamada por: previdenciario-master | Chama: base-legal-previdenciaria · prazos-previdenciarios · calculos-previdenciarios · recursos-previdenciarios · visual-law-previdenciario · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/lei-8213-1991.md` (art. 58, par. 4o - PPP na rescisao; grep o artigo e leia a faixa)
- `context/lei/in-128-2022-inss.md` (art. 284, pars. 5o e 6o - hipoteses de fornecimento do PPP e PPP digital; art. 283 - PPP e privativo do trabalhador)
- `context/lei/decreto-3048-1999.md` (art. 305, par. 1o, II - recurso ao CRPS em 30 dias da ciencia)
- `context/escrita-humana.md` (secoes 5, 6, 7 e 8 - registro por tipo de entrega e passada anti-IA)
- `context/metodologia-previdenciario.md` (secoes 4 e 9 - prazo critico e relogio)

## Objetivo
Entregar o documento pronto para envio, com um pedido claro, um prazo e o fundamento estritamente necessario, no registro certo para o destinatario.

## Metodologia
1. [redacao] Devolver em 3 a 5 linhas: formato, destinatario, o fato, o que se pede e o prazo que corre contra o cliente (se houver). Esperar a confirmacao.
2. Se o fato envolve decisao do INSS com ciencia ha menos de 30 dias ou beneficio cessado, avisar antes de redigir e acionar `prazos-previdenciarios`: notificacao nao suspende prazo recursal.
3. [redacao] Propor 2 a 3 caminhos quando houver escolha real (ex.: notificar o ex-empregador, a quem cabe fornecer o PPP ao trabalhador (IN 128, art. 284, par. 5o, I e II) × pedir no requerimento que o INSS solicite o PPP a empresa (par. 5o, III: o obrigado continua sendo a empresa) × consultar o PPP digital que o INSS disponibiliza a partir do eSocial, que nao cobre o periodo anterior a implantacao, de responsabilidade da empresa (par. 6o) × pedir producao da prova em juizo) e esperar a escolha.
4. Redigir pelo formato (abaixo), na voz do escritorio (`estilo-juridico-previdenciario`). Fundamento: so o dispositivo que obriga o destinatario, nomeando o diploma, achado por `base-legal-previdenciaria`.
5. [redacao] Passada anti-IA com `context/escrita-humana.md` secao 7. Na mensagem ao cliente, sem latim e sem numero de artigo.
6. Os tres formatos fecham por `validador-previdenciario` e `suprema-corte-previdenciaria` antes de ir ao advogado; na mensagem ao cliente, a conferencia inclui que nao promete resultado e nao expoe dado sensivel. Registrar envio e prazo em `memoria-de-caso-previdenciario`.

### Formato 1 - Notificacao extrajudicial
Registro: direto e firme; um pedido e um prazo; nenhuma ameaca vaga (escrita-humana, secao 6).
```
NOTIFICACAO EXTRAJUDICIAL
Notificante: <segurado>, por seu advogado (dados do perfil.md)
Notificado: <razao social, CNPJ, endereco>
1. Fato: vinculo de <data> a <data>, funcao <x>; documento ainda nao entregue.
2. Fundamento: dever de elaborar, manter e fornecer o PPP (Lei 8.213, art. 58,
   par. 4o; IN 128, art. 284, par. 5o, I e II).
3. Pedido: entregar <PPP do periodo X; LTCAT que o embasa> em <N> dias,
   por <meio>, ao endereco <x>.
4. Sem resposta no prazo: o segurado pedira a prova pela via cabivel
   (requerimento ao INSS ou producao em juizo), indicando qual.
Local, data. Assinatura do advogado.
```
Destinatarios usuais: ex-empregador (PPP, LTCAT); sucessora de empresa extinta; hospital ou clinica (prontuario, mediante autorizacao do paciente); sindicato. Prova do envio: AR, e-mail com confirmacao ou cartorio de titulos e documentos. O prazo dado ao notificado e escolha do advogado, nao prazo legal; nao inventar prazo de lei.

### Formato 2 - Requerimento ou oficio a orgao
Registro: protocolar e impessoal. Estrutura: destinatario e protocolo de referencia (NB, numero do processo administrativo) · identificacao do segurado · o que se requer, em itens · fundamento em uma linha · documentos anexos · fecho com local, data e assinatura. Recurso administrativo ao CRPS nao e oficio: vai por `recursos-previdenciarios` (prazo do Decreto 3.048, art. 305, par. 1o, II).

### Formato 3 - Mensagem ao cliente
Registro: simples; explica o que aconteceu, o que o escritorio fara e o que o cliente precisa fazer, com data (escrita-humana, secao 6).
- Concessao: valor e data do primeiro pagamento como constam na carta; se a RMI parecer errada, dizer que o escritorio vai conferir, sem afirmar erro antes da conta (`calculos-previdenciarios`).
- Indeferimento: motivo da carta em palavras simples; as vias e o prazo de cada uma, com data calculada por `prazos-previdenciarios`.
- Pericia: data, local, documentos a levar (laudos, receitas, exames), e que deve relatar as limitacoes do dia a dia sem exagero.
- Pedido de documentos: lista numerada, com onde obter cada um.
Troca de termo: "conforme dispoe o art. X" -> "a lei preve"; "tempus regit actum" -> "vale a lei da epoca"; "decisao do STF no Tema N" -> "o Supremo decidiu que", so se a decisao estiver em `context/lei/temas-sumulas-prev.md`.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita no documento. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- O documento no formato pedido, pronto para envio.
- Fora do documento, ao advogado: prazo dado ao destinatario, meio de prova do envio e `[VERIFICAR]` pendentes.

## Guard
- Nunca prometer resultado ao cliente nem dar data de pagamento que nao esteja na carta ou no ato.
- Nunca usar como exemplo ou argumento tese que o `CLAUDE.md` lista como inviavel (verdade dura 1).
- CNIS, laudo e prontuario sao dado pessoal sensivel: nao colar em mensagem de aplicativo nem em ferramenta externa; mandar pelo canal do escritorio. O PPP e privativo do trabalhador (IN 128, art. 283).
- Citacao so com ancora em `context/` (`anti-alucinacao-previdenciario`).

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill documentos-extrajudiciais-previdenciarios - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
