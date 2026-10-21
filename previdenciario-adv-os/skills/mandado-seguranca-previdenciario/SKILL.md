---
name: mandado-seguranca-previdenciario
description: "Redige mandado de seguranca contra ato de autoridade do INSS ou do CRPS (cessacao sem processo regular, recusa de protocolo ou de analise, demora no requerimento ou no recurso, recusa de cumprir decisao administrativa), so quando o direito se prova por documento ja existente. Faz o teste de cabimento antes de redigir e desvia para a acao comum quando o caso depende de pericia ou testemunha. Use quando o operador disser mandado de seguranca, MS contra o INSS, ato ilegal do INSS, demora do INSS, liminar contra a agencia. Nao use quando houver necessidade de prova a produzir (peticao-inicial-previdenciaria) nem para recurso administrativo (administrativo-inss-crps)."
---

# MANDADO DE SEGURANCA PREVIDENCIARIO

> Camada 5. Testa o cabimento e redige a impetracao contra ato do INSS, sem afirmar prazo ou rito que nao esteja ancorado.

## Entradas
- Recebe: o ato impugnado, com data e autoridade que o praticou (obrigatorio) · prova documental do direito (CNIS, carta de concessao, decisao do CRPS, protocolo) (obrigatorio) · `previdenciario/casos/<slug>.md` (se houver)
- Chamada por: previdenciario-master · administrativo-inss-crps | Chama: prazos-previdenciarios · base-legal-previdenciaria · calculos-previdenciarios · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/lei-12016-2009-ms.md` (arts. 1, 7, 12, 14, 23 e 25 - grep o artigo e leia a faixa)
- `context/lei/lei-10259-2001-jef.md` (art. 3, par. 1, I) · `context/lei/cf88-art109-competencia.md` (art. 109, I e VIII)
- `context/lei/in-128-2022-inss.md` (artigo do procedimento que o ato violou - grep pelo tema)
- `context/lei/lei-8213-1991.md` e `context/lei/decreto-3048-1999.md` (o direito material do caso; cuidado com homonimo, `context/metodologia-previdenciario.md` secao 7.1)
- `context/lei/temas-sumulas-prev.md` (STJ Sumula 105) · `context/escrita-humana.md`

## Objetivo
Entregar a impetracao com liminar quando o direito e liquido e certo, ou dizer ao advogado, com o motivo, que a via e outra.

## Metodologia
1. Teste de cabimento, antes de qualquer redacao (todos sim, ou o MS nao serve):
   - ha ato (ou omissao) identificavel de autoridade do INSS ou do CRPS, com data?
   - o direito se prova so com documento que o advogado ja tem?
   - o caso dispensa pericia medica, prova testemunhal e calculo controvertido?
   Algum "nao": recomendar `peticao-inicial-previdenciaria` (ou o recurso ao CRPS pela `administrativo-inss-crps`) e explicar por que.
2. Prazo da impetracao: 120 dias da ciencia do ato pelo interessado (Lei 12.016/2009, art. 23). Contagem pelo `prazos-previdenciarios` (dias corridos, sem recesso, como prazo material), com a data da ciencia; sem ela, prazo indeterminado. Omissao continuada do INSS: dizer ao advogado qual e o ato impugnado e de quando e a ciencia; sem isso, nao afirmar que o prazo corre nem que esgotou.
3. Competencia: o MS esta excluido do JEF (`context/lei/lei-10259-2001-jef.md`, art. 3, par. 1, I); contra ato de autoridade federal, vai a vara federal (CF, art. 109, VIII).
4. [redacao] Devolver o quadro em 3-6 linhas (impetrante, autoridade coatora e cargo, ato e data, direito, prova documental, urgencia) e esperar confirmacao.
5. [redacao] Propor 2-3 estrategias com ganho e risco (ex.: MS com liminar; MS so contra a demora, para ordenar a analise; acao comum com tutela de urgencia quando ha risco de precisar de prova) e esperar a escolha.
6. Direito liquido e certo: localizar o dispositivo material pela `base-legal-previdenciaria` (Lei 8.213, Decreto 3.048, IN 128) e citar o diploma por extenso. Demora administrativa: citar o prazo da IN 128 so se o grep achar o artigo vigente; sem achar, `[VERIFICAR]`.
7. [redacao] Redigir: enderecamento a vara federal · impetrante e autoridade coatora (cargo e endereco funcional) · ciencia ao INSS por seu orgao de representacao · fatos com a data do ato e da ciencia · direito liquido e certo, por bloco (fato, questao, regra ancorada, aplicacao, conclusao) · lista da prova pre-constituida · liminar (fundamento relevante e risco de ineficacia da medida, Lei 12.016, art. 7, III; carater alimentar do beneficio; conferir as vedacoes do par. 2 e a ADI 4.296 citada na fonte, que nao esta no anexo de temas: `[VERIFICAR]`) · pedidos (notificacao da autoridade, art. 7, I; ciencia ao orgao de representacao do INSS, art. 7, II; oitiva do Ministerio Publico Federal, art. 12; concessao da seguranca) · valor da causa.
8. Honorarios: nao ha condenacao em honorarios em MS (Lei 12.016, art. 25; STJ Sumula 105, literal no anexo). Custas do INSS na Justica Federal: indeterminado (Lei 9.289/1996 nao capturada); nao afirmar isencao nem cobranca.
9. Valor da causa: o MS nao tem formula ancorada em context/; quando houver beneficio em discussao, o advogado indica a base e o numero sai pela `calculos-previdenciarios`, nunca de cabeca.
10. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7), entregar ao `validador-previdenciario` e a `suprema-corte-previdenciaria`, gravar em `memoria-de-caso-previdenciario`.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. A Lei 12.016/2009 esta integral em `context/lei/lei-12016-2009-ms.md`: citar pela faixa lida. CF fora do recorte capturado e a ADI 4.296 sao gap: citacao delas sai como `[VERIFICAR]`.

## Entrega obrigatoria final
- O resultado do teste de cabimento; se cabivel, a peticao do MS com o pedido de liminar, a lista da prova pre-constituida e o prazo decadencial com a data-limite do motor no topo e a lista de `[VERIFICAR]`.

## Guard
- Nunca impetrar quando o direito depende de prova a produzir; o MS denegado por falta de prova pre-constituida custa tempo ao cliente.
- Nunca citar sumula para custas do INSS: a STJ Sumula 105 trata de honorarios em MS.
- Nunca dar a data-limite dos 120 dias sem a data da ciencia nem contar de cabeca; nunca citar artigo da Lei 12.016/2009 sem ler a faixa.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill mandado-seguranca-previdenciario - plugin previdenciario-adv-os v2.0.2`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
