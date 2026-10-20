---
name: replica-previdenciaria
description: "Redige a replica a contestacao do INSS em acao previdenciaria: fatos nao impugnados, refutacao de cada preliminar e de cada ponto de merito, confronto de todo tema ou sumula citado pela procuradoria com o texto selado em context/, e reforco da tese da inicial. Use quando o operador disser replica, responder a contestacao do INSS, impugnar a contestacao, manifestacao sobre a contestacao. Nao use para recurso (recursos-previdenciarios), alegacoes finais (audiencia-previdenciaria) ou impugnacao ao cumprimento (cumprimento-sentenca-inss)."
---

# REPLICA PREVIDENCIARIA

> Camada 5. Responde a contestacao do INSS ponto a ponto, so com fundamento ancorado, e decide com o advogado o que manter e o que ajustar.

## Entradas
- Recebe: a contestacao do INSS (obrigatorio) · a peticao inicial e os documentos ja juntados (obrigatorio) · `previdenciario/casos/<slug>.md` (se houver)
- Chamada por: previdenciario-master | Chama: prazos-previdenciarios · analise-cnis · calculos-previdenciarios · analise-trilateral-previdenciario · jurisprudencia-estrategica-previdenciario · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/temas-sumulas-prev.md` (grep pelo numero que o INSS citou e leia a tese literal)
- `context/lei/lei-8213-1991.md` (arts. 15, 25, 27-A, 57, 103 - grep o artigo e leia a faixa)
- `context/lei/ec-103-2019.md` (arts. 25 e 26) · `context/lei/lei-10259-2001-jef.md` (arts. 9 e 11)
- `context/metodologia-previdenciario.md` (secoes 7, 7.1 e 8) · `context/escrita-humana.md`

## Objetivo
Entregar a replica que rejeita cada defesa do INSS com fundamento conferido, sem deixar ponto valido da contestacao sem resposta estrategica.

## Metodologia
1. Prazo pela `prazos-previdenciarios` (motor de prazo, rito `cpc`); nunca de cabeca. No JEF, nao ha prazo diferenciado para o INSS (Lei 10.259, art. 9).
2. [redacao] Devolver o quadro em 3-6 linhas: pedido da inicial, cada preliminar e cada tese de merito da contestacao, documentos novos juntados pelo INSS. Esperar confirmacao.
3. Classificar cada argumento do INSS:
   - correto e relevante (ex.: tempo especial depois de 13/11/2019 pedido como convertido; piso no auxilio-acidente; abono no BPC): nao replicar o erro da inicial; levar ao advogado a proposta de ajuste;
   - correto e irrelevante para o resultado: reconhecer e mostrar por que nao muda o pedido;
   - errado: refutar com o dispositivo ou a tese literal do anexo.
4. [redacao] Propor 2-3 estrategias (ex.: refutacao integral; refutacao com ajuste ou desistencia parcial de um pedido; refutacao com pedido de prova pericial ou testemunhal) com ganho e risco, e esperar a escolha.
5. Confronto de precedentes: todo tema ou sumula citado pelo INSS e buscado em `temas-sumulas-prev.md`. Achou: comparar a tese literal com o caso (distincao factica, recorte temporal, modulacao). Nao achou: nao refutar pelo conteudo que o modelo lembra; marcar `[VERIFICAR]` e sugerir a busca ao vivo (`juris-adv-os`, cross-link).
6. Defesas tipicas e onde esta a resposta:
   - decadencia: nao ha decadencia para a concessao inicial (STF Tema 313); na revisao, 10 anos (Lei 8.213, art. 103, I); sobre indeferimento ou cessacao, o artigo remete a ADI 6.096 nao capturada: `[VERIFICAR]` (gate de vigencia, item 7);
   - prescricao: so as parcelas vencidas antes dos 5 anos do ajuizamento (art. 103, par. unico), ressalvados menores, incapazes e ausentes ("na forma do Codigo Civil"; dispositivo do CC nao capturado: `[VERIFICAR]`); perguntar ao advogado antes de aceitar o corte do INSS;
   - perda da qualidade e carencia: periodo de graca (art. 15) e a regra do art. 27-A (a metade so reabre o computo das anteriores); conta pela `analise-cnis`;
   - especial: conversao so ate 13/11/2019 (EC 103, art. 25, par. 2); ruido de 90 dB de 06/03/1997 a 18/11/2003 (STJ Tema 694); limite vigente no Anexo IV nao automatizado: exigir a prova tecnica;
   - falta de requerimento administrativo: provar com a DER; precedente sobre interesse de agir nao capturado: `[VERIFICAR]`;
   - renuncia e alcada do JEF: STJ Tema 1.030; competencia fixada na distribuicao (CPC, art. 43).
7. Fatos nao impugnados especificamente: apontar cada um. O dispositivo do CPC sobre o onus da impugnacao especificada nao esta em `cpc-excertos-prev.md`: citar so com `[VERIFICAR]`. Documento que so o INSS detinha e nao trouxe: lembrar o dever de fornecer a documentacao no JEF (Lei 10.259, art. 11).
8. [redacao] Redigir: cabecalho com o numero do processo · sintese da contestacao · fatos nao impugnados · preliminares, uma a uma · merito, um bloco por tese (fato, questao, regra ancorada, aplicacao, conclusao) · reforco da tese da inicial · pedidos (rejeicao das preliminares, procedencia, provas). Combater a tese, nunca a pessoa do procurador.
9. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7), entregar ao `validador-previdenciario` e a `suprema-corte-previdenciaria`, gravar em `memoria-de-caso-previdenciario`.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Precedente citado pelo INSS e ausente de `temas-sumulas-prev.md` sai como `[VERIFICAR]`, nunca com conteudo de memoria.

## Entrega obrigatoria final
- A replica em texto, a tabela "argumento do INSS -> classificacao -> resposta e ancora", a proposta de ajuste (se houver ponto valido) e a lista de `[VERIFICAR]`.

## Guard
- Nunca atribuir a tema ou sumula um conteudo que nao esteja literal no anexo; numeros com conteudo trocado estao em `context/metodologia-previdenciario.md`, secao 8.
- Nunca sustentar na replica pedido que a lei veda (conversao depois de 13/11/2019, regra definitiva do art. 29 contra o art. 3 da Lei 9.876/1999, piso no auxilio-acidente); levar o ajuste ao advogado.
- Nenhum numero novo (tempo, RMI, valor) de cabeca: script pela `calculos-previdenciarios` ou conta aberta.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill replica-previdenciaria - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
