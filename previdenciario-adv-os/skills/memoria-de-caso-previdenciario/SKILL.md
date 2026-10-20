---
name: memoria-de-caso-previdenciario
description: "Mantem o estado do caso previdenciario no diretorio de trabalho do advogado, um arquivo por caso em previdenciario/casos/<slug>.md: partes, beneficio e NB, fase administrativa ou judicial, datas DER/DIB/DII/DCB, situacao, prazos, quadro confirmado, estrategia escolhida, atos praticados e proxima providencia. Use para abrir, atualizar ou retomar um caso, ou quando o advogado disser memoria do caso, onde paramos, retomar caso, status, /status-previdenciario. Nunca grava dentro do plugin."
---

# MEMORIA-DE-CASO-PREVIDENCIARIO

> Camada 0. Estado vivo do caso. Lido no inicio e atualizado no fim de cada tarefa pelo `previdenciario-master`.

## Entradas
- Recebe: o caso ativo (slug ou descricao) e o resultado do ato que acabou de rodar (obrigatorio) · quadro confirmado, estrategia escolhida, prazo conferido (quando houver).
- Chamada por: previdenciario-master | Chama: nenhuma

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secao 9 relogio do dominio e secao 3 fluxo do master - grep a secao e leia a faixa).
- Modelo do arquivo: `templates/caso.md.tpl` na raiz do plugin (`<pasta-base>/../../templates/caso.md.tpl`), se existir; sem ele, usar a estrutura abaixo.

## Objetivo
Nunca perder o fio: quem e quem, qual beneficio, em que fase, que prazo corre, o que ja foi feito e o que vem.

## Onde grava (caminho explicito)
- Caso: `<diretorio de trabalho>/previdenciario/casos/<slug>.md`. Um caso por arquivo.
- Perfil do escritorio (so leitura aqui): `<diretorio de trabalho>/previdenciario/perfil.md`.
- **Nunca** na pasta do plugin: o plugin e read-only e escrever nele quebra na atualizacao.
- Slug: `<apelido-do-caso>-<beneficio>-<aaaa>` em kebab-case (ex.: `caso-a-auxilio-temporario-2026`). Sem CPF, NIT, NB, numero de processo ou nome completo no slug.

## Estrutura do caso
1. **Partes:** segurado, dependente ou beneficiario (cliente) · INSS · outros (empregador, ente do RPPS, entidade de previdencia) · advogado (do `perfil.md`).
2. **Objeto:** beneficio ou revisao pedida, especie, NB quando houver, e o dispositivo aplicavel com o diploma nomeado e o anexo de onde saiu.
3. **Fase:** consultiva -> requerimento (DER) -> recurso a Junta e ao CRPS -> acao (JEF ou Vara) -> recurso (TRF, turmas, superiores) -> cumprimento (RPV ou precatorio).
4. **Processo ou protocolo:** numero, orgao (APS, JR, CRPS, juizo), secao ou subsecao.
5. **Situacao atual, com data:** beneficio ativo, cessado, indeferido, concedido com valor discutido; tutela deferida; datas DER, DIB, DII, DCB, data da ciencia da decisao.
6. **Prazos:** prazo, termo inicial, vencimento e a skill que conferiu (`prazos-previdenciarios` ou o script de prazo). Nunca de cabeca. Decadencia da revisao e prescricao das parcelas, quando pertinentes.
7. **Quadro confirmado** (data da confirmacao) + **lacunas declaradas**.
8. **Estrategia escolhida** + alternativas descartadas e o motivo.
9. **Calculos:** script e versao, exit, numero e data, ou "conta aberta, nao conferida por script".
10. **Atos praticados** (append-only: data, ato, skill, linha de assinatura) + **proxima providencia** + **proximo prazo fatal**.

## Metodologia
1. **Localizar:** listar `previdenciario/casos/`. Mais de um caso possivel: perguntar qual, com botoes (ferramenta AskUserQuestion, max. 4 opcoes). Nenhum: abrir novo.
2. **Ao abrir:** criar o arquivo com os 10 blocos; preencher so o que veio do quadro confirmado; o resto fica como lacuna.
3. **Ao atualizar:** acrescentar o ato no fim (nunca reescrever atos anteriores), atualizar situacao e fase, gravar o prazo que a skill de prazo devolveu e a proxima providencia.
4. **Fato novo relevante** (documento novo, decisao nova, prazo novo): registrar e avisar o master de que o quadro precisa ser reconfirmado.
5. **Estado da 0.1.0:** se existir `previdenciario/cowork-state.json` ou `persona.md` sem `perfil.md`, nao converter aqui; apontar `/start-previdenciario` (migracao). Nunca apagar arquivo antigo.
6. **Resumo (/status-previdenciario):** versao do plugin (2.0.0), perfil configurado ou nao, lista dos casos com fase e proximo prazo, e, do caso ativo, 5 a 8 linhas: partes, beneficio, fase, situacao, proxima providencia, proximo prazo fatal.

## Se faltar anexo
Seguir com a estrutura desta skill e avisar em uma linha que o modelo `templates/caso.md.tpl` nao foi encontrado. Sem `perfil.md`: registrar "perfil nao configurado" e seguir.

## Entrega obrigatoria final
- Arquivo `previdenciario/casos/<slug>.md` criado ou atualizado (dizer o caminho) + resumo executivo do caso.

## Guard
Dados do caso sao sensiveis (CNIS, laudo, dados de saude e de renda). Gravar so no diretorio de trabalho, nunca no plugin, nunca em ferramenta externa. Se a pasta for sincronizada (iCloud, OneDrive, Dropbox, Drive) e o perfil nao registrar a ciencia do advogado, avisar em uma linha. Nao inventar prazo, data, NB nem situacao: o que nao souber, perguntar ou marcar como lacuna. Um caso nunca le nem grava no arquivo de outro.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill memoria-de-caso-previdenciario - plugin previdenciario-adv-os v2.0.0`
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
