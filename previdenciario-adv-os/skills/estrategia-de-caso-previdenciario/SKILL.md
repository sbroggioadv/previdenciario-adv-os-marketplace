---
name: estrategia-de-caso-previdenciario
description: "Monta 2 a 3 caminhos para o caso previdenciario (via administrativa, JEF, vara federal, mandado de seguranca, novo requerimento), cada um com ganho, risco, prova que falta, prazo e numero conferido por script, e espera o advogado escolher. Compara as regras de aposentadoria pelo script de transicao. Use quando o operador disser qual a melhor estrategia, o que fazer neste caso, vale recorrer ou entrar com acao, administrativo ou judicial, JEF ou vara, plano do caso. Nao use para redigir a peca (a skill da trilha redige depois da escolha) nem para estimar percentual de exito."
---

# ESTRATEGIA-DE-CASO-PREVIDENCIARIO

> Camada C2. O plugin propoe caminhos; quem escolhe a tese e o advogado.

## Entradas
- Recebe: quadro do caso confirmado pela triagem (obrigatorio) · CNIS, carta do INSS, laudos, PPP · resultado de prazo e de calculo ja rodados (opcional)
- Chamada por: previdenciario-master · triagem-dogmatica-previdenciario | Chama: prazos-previdenciarios · calculos-previdenciarios · analise-trilateral-previdenciario · jurisprudencia-estrategica-previdenciario · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secoes 4 Triagem, 6 Distincao, 7 Armadilhas, 9 Relogio - grep a secao e leia a faixa)
- `context/calculo-transicao.md` (secoes 1, 2 e CAMPOS)
- `context/lei/ec-103-2019.md` (arts. 3, 15 a 21, 26 - grep o artigo e leia a faixa)
- `context/lei/lei-10259-2001-jef.md` (arts. 3 e 9) · `context/lei/cpc-excertos-prev.md` (art. 43)
- `context/lei/temas-sumulas-prev.md` (so o que estiver la)

## Objetivo
Entregar 2 a 3 caminhos comparaveis, com o trade-off de cada um, para o advogado decidir antes de qualquer redacao.

## Metodologia
1. [redacao] Devolver o quadro do caso em 3 a 6 linhas (segurado, beneficio, decisao do INSS, datas, documentos que existem) e esperar confirmacao. Lacuna fica escrita como lacuna.
2. Pergunta critica antes de tudo: ha prazo correndo ou beneficio cessado ou indeferido ha menos de 30 dias? Se sim, rodar `prazos-previdenciarios` e por o prazo no topo do plano.
3. Identificar o fato que decide (metodologia, secao 6): data de filiacao, data do trabalho especial, nexo com o trabalho, natureza do beneficio, valor da causa. Faltando o fato, perguntar; nao escolher a regra no escuro.
4. Aposentadoria: rodar o script de transicao (secao Calculo) e mostrar todas as regras aplicaveis, cumpre ou nao na DER, data em que cumpre, coeficiente. Com art. 17 sem a tabua do IBGE, a comparacao fica aberta e isso entra no plano. No direito adquirido, a opcao sem fator do art. 29-C (`context/lei/lei-8213-1991.md`, art. 29-C; `context/lei/in-128-2022-inss.md`, art. 229, par. 2) entra no plano como formula, com a limitacao declarada: o fluxo de calculo atual ainda nao a fecha em numero; se os pontos fecham, a comparacao com a alternativa com fator fica aberta. Outro numero (carencia, RMI, valor da causa) vem de `calculos-previdenciarios`.
5. Montar 2 a 3 caminhos. Cada um com: via e foro; o que pede; ganho; risco e o que o INSS vai alegar; prova que falta; prazo; custo e tempo provaveis em palavras, sem percentual. Vias usuais:
   - Administrativa: novo requerimento, recurso ao CRPS, pedido de revisao. Mais barata; o indeferimento repetido prepara a via judicial.
   - JEF: causa ate 60 salarios minimos (`lei-10259-2001-jef.md`, art. 3), alcada fixada na distribuicao (`cpc-excertos-prev.md`, art. 43); acima disso, vara federal ou renuncia expressa ao excedente, que alcanca as vincendas (`temas-sumulas-prev.md`, STJ Tema 1.030), decidida pelo cliente informado. Valor da causa so pelo script.
   - Mandado de seguranca: so com prova pre-constituida de ato ilegal; nao serve para provar incapacidade nem tempo controvertido.
   - Esperar e planejar: quando ainda nao cumpre regra nenhuma, a data em que cumpre e o caminho (via `planejamento-previdenciario`).
6. Rodar `analise-trilateral-previdenciario` no caminho mais forte para expor a defesa do INSS e o olhar do juizo. Ajustar o risco de cada caminho.
7. Jurisprudencia so pela `jurisprudencia-estrategica-previdenciario`, do que estiver selado em `temas-sumulas-prev.md`. Item marcado como a confirmar entra assim.
8. Entregar os caminhos lado a lado e parar. Nao redigir nada antes da escolha.
9. [redacao] Passada anti-IA com `context/escrita-humana.md` no texto do plano antes de entregar.
10. Depois da escolha: registrar caminho, motivo e proximo passo na `memoria-de-caso-previdenciario` e devolver ao master a skill da trilha.

## Calculo
Script: `calc_previdenciario_transicao.py`
```flags
--entrada   arquivo   opcional   caminho do JSON; sem ele le a entrada padrao
--versao    flag      opcional   imprime a versao
```
```campos
nascimento   data   obrigatoria   AAAA-MM-DD
sexo   enum   obrigatoria   M|F
data_filiacao   data   obrigatoria   primeira filiacao ao RGPS
der   data   obrigatoria   data em que se verifica cada regra
periodos   lista   obrigatoria   sub-campos iguais aos do script de tempo
periodos[].inicio   data   obrigatoria   AAAA-MM-DD
periodos[].fim   data   obrigatoria   AAAA-MM-DD
periodos[].tipo   enum   obrigatoria   comum|especial-15|especial-20|especial-25
periodos[].fonte   enum   obrigatoria   CNIS|CTPS|sentenca|PPP
periodos[].competencias_abaixo_do_minimo   lista   opcional   AAAA-MM desde 11/2019
novembro_2019_integral   bool   condicional   se algum periodo cruza 13/11/2019; false da exit 3
professor   bool   opcional   padrao false; true com [VERIFICAR]
projecao_continua   bool   opcional   padrao false
projecao_ate   data   condicional   obrigatoria se projecao_continua = true
```
Rodar o script conforme `context/metodologia-previdenciario.md` (secao 13 Scripts), com o JSON em `previdenciario/casos/<slug>-calc-transicao.json`. Exit 0: usar e mostrar a memoria; duas datas com `[VERIFICAR]` aparecem as duas. Exit 2: perguntar de novo o campo recusado. Exit 3: comparacao aberta com a `formula_aberta`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-transicao.md`, mostrando cada passo, e avisar que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita no plano. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Quadro do caso confirmado, prazo no topo quando houver, e 2 a 3 caminhos lado a lado (via, pedido, ganho, risco, prova faltante, prazo, custo e tempo em palavras), com os numeros e suas fontes.
- Pergunta final ao advogado: qual caminho seguir.

## Guard
- Nunca percentual de exito nem promessa de resultado.
- Nunca escolher o caminho pelo advogado.
- Nunca oferecer a revisao do art. 29 contra o art. 3 da Lei 9.876 (STF Tema 1.102): tese inviavel. Cliente com cobranca do INSS por valores dessa revisao vai para a `analise-trilateral-previdenciario`, na defesa dentro da modulacao.
- Nunca converter especial trabalhado depois de 13/11/2019; nunca tema fora de `temas-sumulas-prev.md`.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill estrategia-de-caso-previdenciario - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
