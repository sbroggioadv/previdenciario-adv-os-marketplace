---
name: suprema-corte-previdenciaria
description: "Gate de qualidade R1-R4 obrigatorio antes de QUALQUER entrega do plugin previdenciario (peca, recurso ao CRPS, parecer, calculo, requerimento): R1 fatos, via e competencia contra o quadro confirmado; R2 base legal com a redacao VIGENTE e o diploma nomeado; R3 tema ou sumula so com selo verde no anexo; R4 forma, prazo, calculo conferido com o JSON do script e checagem anti-IA objetiva (R4.AI, marcadores AI-01 a AI-16 com limiar). Use sempre como ultima etapa antes de entregar, ou quando o advogado disser revisao final, suprema corte, valida antes de protocolar, /revisao-previdenciaria-final."
---

# SUPREMA-CORTE-PREVIDENCIARIA - Gate R1-R4

> Camada 0. Revisao adversarial final. Nada sai do plugin sem passar por aqui. Foco: proteger o segurado e o advogado.

## Entradas
- Recebe: a entrega completa e o tipo (obrigatorio) · quadro confirmado e estrategia escolhida do `previdenciario/casos/<slug>.md` · saida JSON do script, quando houve calculo · tabela do `validador-previdenciario`, quando ja rodou.
- Chamada por: previdenciario-master | Chama: validador-previdenciario · anti-alucinacao-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/<diploma>.md` do dispositivo citado (grep o artigo e leia a faixa; conferir a redacao aplicavel ao periodo dos fatos; ler o cabecalho do anexo). Mapa: `context/lei/INDICE.md`.
- `context/lei/temas-sumulas-prev.md` (grep o numero; so item com ✅; ver a Nota).
- `context/metodologia-previdenciario.md` (secao 5 verdades duras; 7 e 7.1 armadilhas e homonimos; 8 contrato anti-alucinacao; 9 relogio; 10 gate de vigencia; 14 jargao).
- `context/escrita-humana.md` (secao 2 regra de contagem; 3 marcadores e limiares; 4 jargao legitimo; 8 pergunta-filtro).
- `context/calculo-<x>.md` da conta que a entrega usa (secao CAMPOS e a formula).

## Objetivo
Pegar o erro antes do INSS, do juizo ou da Junta: fato sem lastro, via ou competencia errada, norma riscada citada como vigente, homonimo, tema inexistente ou trocado, numero de cabeca, prazo errado, texto com cara de maquina.

## As 4 revisoes
1. **R1 - Fatos, via e competencia.**
   - Todo fato da entrega esta no quadro confirmado? Fato fora do quadro = achado. Lacuna declarada tratada como fato = REPROVA.
   - Datas coerentes entre si (filiacao, DER, DIB, DII, DCB, ciencia da decisao).
   - Via certa: administrativa (requerimento, Junta, CRPS) ou judicial; DER e decisao do INSS nos documentos quando a peca as pressupoe.
   - Competencia: JEF ate 60 salarios minimos, com 12 vincendas na soma (`context/lei/lei-10259-2001-jef.md`, art. 3 e par. 2). Acao acidentaria: excluida da Justica Federal (CF, art. 109, I, em `context/lei/cf88-art109-competencia.md`), vai a Justica Estadual; causa previdenciaria na Justica Estadual so por delegacao da lei (par. 3), com recurso ao TRF (par. 4). Enderecamento contra isso = achado.
2. **R2 - Base legal e lei VIGENTE.**
   - Cada dispositivo existe e a redacao citada e a aplicavel ao periodo dos fatos. Regra geral: a nao riscada; linha `(revogado)` apresentada como vigente hoje = REPROVA. Excecao intertemporal: redacao riscada que ainda rege fatos anteriores (ex.: EC 113, art. 3, redacao original, para a Selic de dez./2021 a ago./2025 - cabecalho de `context/lei/ec-113-2021.md` e STF Tema 1.419 em `temas-sumulas-prev.md`) e correta quando a peca diz o periodo; aplica-la fora dele = REPROVA.
   - A citacao nomeia o diploma; conferir os homonimos da metodologia secao 7.1 (art. 3, 17, 20, 26, 27-A, 42, 15, 32).
   - Nenhuma afirmacao proibida pela metodologia secao 8 (fonte errada da Selic, autoria errada do PBC de 100%, tema com conteudo trocado, tese inviavel oferecida); nenhuma verdade dura da secao 5 contrariada.
   - Item vermelho do gate de vigencia (metodologia secao 10) sem reverificacao entra como "a confirmar", nunca como fato.
   - Dispositivo sem ancora sem `[VERIFICAR]` = REPROVA. Com `[VERIFICAR]`, o marcador so identifica a pendencia: o R2 nao aprova e a entrega nao sai como validada enquanto ele existir.
3. **R3 - Jurisprudencia real.**
   - Todo tema, sumula ou ADI citado consta em `temas-sumulas-prev.md` com ✅ e com o mesmo conteudo da tese literal. 🔴 = "a confirmar" e conferencia ao vivo antes de protocolar. ❌ ou ausente = REPROVA.
   - Nenhum numero de processo, relator ou data que nao esteja no anexo. Atribuicao vaga ("jurisprudencia pacifica") = REPROVA (tambem AI-09).
4. **R4 - Forma, prazo, calculo e escrita.**
   - Prazo: tempestivo, contado pelo motor de prazo ou por `prazos-previdenciarios`, com termo inicial e rito declarados (no JEF, sem prazo diferenciado para a Fazenda).
   - Estrutura do tipo e pedidos coerentes com a causa de pedir e com a lei (ex.: auxilio-acidente sem piso de um salario minimo e sem cumulacao com aposentadoria; BPC sem abono anual).
   - Calculo: todo numero veio do script (exit 0) ou da conta aberta, e a Corte **refaz a conta**: confere parametros, regra, marcos e resultado contra a lei seca e a `context/calculo-<x>.md`, com a linha do tempo dos marcos (DER, DIB, 13/11/2019, fatias de juros). Com script: o numero da peca e igual ao do JSON (`parametros_usados`, `regra`, `fonte`, `memoria`) e os parametros sao os do caso. Com conta aberta: cada passo da tabela da `calculo-<x>.md` refeito, e o aviso "nao conferido por script" presente. Exit 3 aparece como formula com `[VERIFICAR]`. Juros e correcao em fatias por competencia (verdade 5). Divergencia, parametro errado ou passo que nao fecha = REPROVA.
   - **R4.AI** (abaixo).

## R4.AI - contagem objetiva
Contar so o corpo da peca pela regra de `escrita-humana.md` secao 2: fora da conta ficam enderecamento, qualificacao, assinatura do advogado, local e data, titulos numerados e toda citacao literal entre aspas ou em recuo; o rol de pedidos fica fora, exceto para AI-02, AI-06 e AI-16. Na duvida, o trecho nao conta e vira sugestao.

| ID | Marcador | Reprova com |
|---|---|---|
| AI-01 | travessao como pontuacao | 2+ no mesmo paragrafo, ou mais de 2 por 1.000 palavras (abaixo de 1.000, mais de 2 no total) |
| AI-02 | triade retorica abstrata | 2+ na peca |
| AI-03 | contraste fabricado ("nao e X, e Y") | 2+ na peca, ou 1 na abertura ou no fecho |
| AI-04 | abertura com elogio, eco ou anuncio | 1 |
| AI-05 | conectivo da lista A (secao 3.1) | mais de 1 |
| AI-06 | negrito fora de titulo, pedido e tese principal | mais de 3 trechos |
| AI-07 | lista onde cabe prosa na fundamentacao | 1 bloco |
| AI-08 | cadeia de 3+ gerundios na mesma frase | 2+ cadeias |
| AI-09 | atribuicao vaga a doutrina ou jurisprudencia | 1 |
| AI-10 | inflacao de importancia (lista C, secao 3.2) | 2+ |
| AI-11 | 2+ atenuadores na mesma oracao | 2+ ocorrencias |
| AI-12 | artefato de chatbot ou de modelo | 1 |
| AI-13 | 3+ designacoes da mesma parte em 2 paragrafos seguidos | 1 |
| AI-14 | fecho generico de esperanca ou de evidencia | 1 |
| AI-15 | emoji no corpo | 1 |
| AI-16 | rastro de ferramenta (skill, plugin, modelo, "gerado por") | 1 |

Tolerancia zero: AI-04, AI-07, AI-09, AI-12, AI-14, AI-15, AI-16. **Qualquer marcador no limiar ou acima = R4 REPROVA.** Sem soma de pontos. Depois da contagem, a pergunta-filtro ("o que ainda faz este texto soar gerado?") lista ate 3 sinais como sugestao, nunca como reprovacao.

**Jargao legitimo nunca reprova sozinho:** titulos numerados, data venia, in casu, restou demonstrado, destarte, negrito no pedido e o jargao do dominio (metodologia secao 14: DER, DIB, RMI, CNIS, PBC, periodo de graca, carencia, pedagio, reafirmacao da DER e os demais). Excesso da lista B vira sugestao. A voz do `perfil.md` nao relaxa os marcadores de tolerancia zero.

## Metodologia
1. Ler o quadro confirmado e a estrategia escolhida.
2. Acionar `validador-previdenciario` (tabela item a item) se ainda nao rodou; `anti-alucinacao-previdenciario` vale o tempo todo.
3. R1 -> R2 -> R3 -> R4, nessa ordem, com o anexo aberto em cada item.
4. Corrigir o que falhou e reexaminar so o R que reprovou e os seguintes. Tres reprovacoes seguidas no mesmo ponto: devolver ao master para rever a estrategia.

## Se faltar anexo
Anexo ausente = o item que dependia dele fica `[VERIFICAR]` e o R correspondente nao aprova; avisar em uma linha qual anexo faltou e pedir reinstalacao. Nunca conferir de memoria.

## Entrega obrigatoria final
- Veredito por R: OK / CORRIGIR (o que) / REPROVA (o que), com o trecho e o anexo.
- R4.AI: tabela id - contagem - limiar - trechos, e as ate 3 sugestoes da pergunta-filtro.
- A versao corrigida, pronta para o advogado revisar e assinar.
- Lista do que precisa de conferencia ao vivo antes de protocolar (itens 🔴 e `[VERIFICAR]`).

## Guard
Se qualquer R falhar, NAO liberar: corrigir e reexaminar. Item duvidoso: bloquear. Nenhuma linha de assinatura de skill ou plugin dentro da peca. A responsabilidade final e do advogado; este gate reduz o risco, nao o substitui.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill suprema-corte-previdenciaria - plugin previdenciario-adv-os v2.0.3`
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
