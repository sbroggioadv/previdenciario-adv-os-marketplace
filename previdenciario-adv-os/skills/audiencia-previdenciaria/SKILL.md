---
name: audiencia-previdenciaria
description: "Prepara a audiencia em acao previdenciaria e redige as alegacoes finais: roteiro de perguntas ao perito, roteiro de testemunhas (tempo rural, incapacidade, nexo com o trabalho), orientacao ao segurado para o depoimento e memoriais que ligam cada prova produzida ao pedido. Use quando o operador disser audiencia, instrucao, testemunhas, perito em audiencia, depoimento pessoal, alegacoes finais, memoriais. Nao use para quesitos e critica do laudo antes da audiencia (pericia-medica-previdenciaria) nem para recurso (recursos-previdenciarios)."
---

# AUDIENCIA PREVIDENCIARIA

> Camada 5. Antes da audiencia, roteiros; depois dela, alegacoes finais que so falam da prova que de fato foi produzida.

## Entradas
- Recebe: fase (preparacao ou alegacoes finais) e o tipo de acao (obrigatorio) · peticao inicial, contestacao, laudo e documentos (obrigatorio) · ata e anotacoes da audiencia (obrigatorio para alegacoes finais) · `previdenciario/casos/<slug>.md` (se houver)
- Chamada por: previdenciario-master | Chama: prazos-previdenciarios · pericia-medica-previdenciaria · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/lei-10259-2001-jef.md` (arts. 1, 9, 11 e 12 - grep o artigo e leia a faixa) · `context/lei/lei-9099-1995.md` (art. 55)
- `context/lei/temas-sumulas-prev.md` (TNU Sumulas 41, 47 e 79; STJ Tema 694; STJ Sumula 111 - leia a tese literal)
- `context/lei/lei-8213-1991.md` (arts. 42, 59, 86 e 55) · `context/lei/ec-103-2019.md` (art. 25)
- `context/escrita-humana.md`

## Objetivo
Levar o advogado preparado para a audiencia e, encerrada a instrucao, entregar memoriais que conectam prova a pedido.

## Metodologia
**Preparacao**
1. [redacao] Devolver o quadro em 3-6 linhas: o que ainda precisa ser provado oralmente, o que o laudo disse, quem sao as testemunhas, a data da audiencia. Esperar confirmacao.
2. [redacao] Propor 2-3 estrategias para a audiencia (ex.: priorizar a prova oral do periodo controvertido; pedir esclarecimentos do perito em ata; propor ou recusar acordo com os limites que o advogado fixar) e esperar a escolha antes de montar roteiros e orientacao.
3. Prazos de JEF (Lei 10.259): citacao para audiencia de conciliacao com antecedencia minima de 30 dias (art. 9); o INSS deve fornecer a documentacao de que disponha ate a instalacao da audiencia (art. 11); laudo ate cinco dias antes da audiencia (art. 12). Datas concretas pela `prazos-previdenciarios`.
4. Roteiro do perito, em escala: formacao e especialidade; o que examinou e por quanto tempo; quais documentos medicos leu (citar cada um pela data); omissoes (achado documentado que o laudo nao enfrenta); contradicoes (exame fisico x conclusao); prognostico diante da idade, da escolaridade e da atividade habitual. Respeito a pessoa, firmeza no ponto tecnico. Critica do laudo e quesitos complementares: `pericia-medica-previdenciaria`.
5. Roteiro de testemunhas por tipo de prova:
   - tempo rural: desde quando conhece a parte, onde e como trabalhava, com quem, cultura ou criacao, frequencia, forma de sustento; integrante da familia com renda urbana nao descaracteriza por si so (TNU Sumula 41, literal no anexo);
   - incapacidade: atividade habitual, quando notou a mudanca, exemplo concreto, tentativa de retorno;
   - nexo com o trabalho: como ocorreu o acidente ou o adoecimento, ambiente, uso de protecao, registro do evento.
6. Orientacao ao segurado (texto simples, sem latim): responder so o perguntado; "nao me recordo" em vez de chutar data ou valor; descrever sintomas e rotina sem exagero nem minimizacao; nao esconder trabalho concomitante. O modelo redige a orientacao na hora, no tom do `perfil.md`.

**Alegacoes finais**
7. [redacao] Devolver o quadro depois da instrucao em 3-6 linhas (o que foi provado e por qual prova, o que ficou sem prova, o que o laudo e a ata registram) e esperar confirmacao. Vale tambem quando a skill entra direto nesta fase.
8. [redacao] Propor 2-3 estrategias para os memoriais (ex.: insistir no pedido principal; priorizar a tese subsidiaria que a prova sustenta; pedir conversao em diligencia ou esclarecimento do perito) e esperar a escolha.
9. Usar so a prova produzida e registrada (ata, laudo, documentos com folha ou evento). Nada que nao conste dos autos.
10. [redacao] Redigir: sintese do processo · prova documental · prova pericial (pontos favoraveis e falhas tecnicas ja apontadas) · prova oral (trecho e referencia da ata) · conexao prova -> direito por bloco (fato provado, questao, regra ancorada, aplicacao, conclusao) · tese subsidiaria · pedidos.
11. Ancoras uteis, sempre pelo anexo: incapacidade parcial com analise das condicoes pessoais e sociais (TNU Sumula 47); BPC com laudo social, auto de constatacao ou, inviabilizados, testemunhas (TNU Sumula 79); ruido de 90 dB de 06/03/1997 a 18/11/2003 (STJ Tema 694); conversao de especial so ate 13/11/2019 (EC 103, art. 25, par. 2). Regra de distribuicao do onus da prova do CPC nao esta em `cpc-excertos-prev.md`: citar so com `[VERIFICAR]`; o dever do INSS de trazer a documentacao no JEF esta no art. 11 da Lei 10.259.
12. Pedidos: os da inicial; correcao e juros pelo regime em fatias, com o texto-base da `peticao-inicial-previdenciaria`, passo 8 (Manual CJF vigente e Res. CJF 983/2026 so na Justica Federal ou delegada; acao acidentaria estadual: `[VERIFICAR]`), sem fixar indice; honorarios pelo rito: no JEF, sem condenacao em primeiro grau, salvo litigancia de ma-fe (Lei 9.099, art. 55, aplicada pela Lei 10.259, art. 1); na vara federal ou estadual, cabimento pelo CPC, art. 85 (nao capturado: `[VERIFICAR]`), com a base nas vencidas ate a sentenca (STJ Sumula 111, que so delimita a base).

**Fechamento (os dois modos)**
13. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7), entregar ao `validador-previdenciario` e a `suprema-corte-previdenciaria`, gravar em `memoria-de-caso-previdenciario`.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Precedente ou dispositivo processual sem ancora sai como `[VERIFICAR]`.

## Entrega obrigatoria final
- Preparacao: roteiro do perito, roteiro de testemunhas, orientacao ao segurado e mapa "ponto a provar -> prova -> quem fala".
- Alegacoes finais: o texto dos memoriais e a lista de `[VERIFICAR]`.

## Guard
- Nunca referir prova que nao foi produzida nem trecho que nao esta na ata.
- Nunca usar sumula da TNU com conteudo diferente do literal do anexo; nunca um indexador unico para todo o periodo: o regime e em fatias por competencia (`context/calculo-rpv.md`, secao 2).
- Nunca instruir o segurado a dizer o que nao viveu.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill audiencia-previdenciaria - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
