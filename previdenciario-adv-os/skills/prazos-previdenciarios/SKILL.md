---
name: prazos-previdenciarios
description: "Prazos do caso previdenciario, administrativos (recurso e contrarrazoes ao CRPS, exigencia do INSS) e judiciais (impugnacao, recurso, manifestacao), contados pelo motor de prazo local, com a data-limite, os dias contados e os alertas. Primeira parada quando ha prazo correndo ou beneficio cessado ou indeferido ha menos de 30 dias. Use quando o operador disser qual o prazo, ate quando posso recorrer, prazo do CRPS, prazo do recurso, perdi o prazo, contar prazo, ou quando a triagem responder sim a pergunta critica. Nao use para decadencia ou prescricao da revisao (calculos-previdenciarios, script de RMI) nem para prazo de outra area."
---

# PRAZOS-PREVIDENCIARIOS

> Camada C2. Responde a pergunta critica: o que vence, quando, e o que fazer se ja venceu.

## Entradas
- Recebe: o ato (decisao do INSS, intimacao, sentenca), a data e o meio da ciencia, a via (administrativa, JEF, vara federal) (obrigatorio) · feriados locais e suspensoes do tribunal (opcional)
- Chamada por: previdenciario-master · triagem-dogmatica-previdenciario · estrategia-de-caso-previdenciario | Chama: nenhuma (roda o motor de prazo)

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secao 9 Relogio, secao 4 Triagem, secao 13 Scripts - grep a secao e leia a faixa)
- `context/lei/in-128-2022-inss.md` (arts. 578, 580, 597, 599 - grep o artigo e leia a faixa)
- `context/lei/decreto-3048-1999.md` (art. 305 - grep o artigo e leia a faixa)
- `context/lei/lei-10259-2001-jef.md` (art. 9) · `context/lei/cpc-excertos-prev.md` (art. 535) · `context/lei/cpc-recursos-prazos-prev.md` (arts. 183, 224, 1.003 e 1.023)
- `context/lei/lei-9099-1995.md` (arts. 12-A e 42) · `context/lei/regimento-crps-portaria-mps-125-2026.md` (arts. 77, 78, 80 e 112)
- `context/lei/lei-8213-1991.md` (art. 60 - grep o artigo e leia a faixa)

## Objetivo
Dar a data-limite conferida pelo motor, com o fundamento do prazo e do modo de contar, antes de qualquer outra etapa do caso.

## Metodologia
1. Identificar o prazo e o seu fundamento no context/:
   - Recurso ao CRPS: 30 dias da ciencia da decisao (`decreto-3048-1999.md`, art. 305, par. 1, II; `in-128-2022-inss.md`, art. 580).
   - Contrarrazoes ao CRPS: 30 dias. Prazo fatal: da intimacao da interposicao (`in-128-2022-inss.md`, art. 580; regimento CRPS, art. 77, caput, contado pelo art. 78, com a intimacao do art. 80). O Decreto 3.048, art. 305, par. 1, III, diz "da interposicao": rodar o motor com os dois marcos e entregar as duas datas, a da interposicao como meta interna preventiva e a da intimacao como data-limite. Nunca declarar vencido, nem trocar de via, enquanto o prazo contado da intimacao estiver aberto. Sem a data da intimacao: tempestividade indeterminada, nunca vencida.
   - Impugnacao do INSS ao cumprimento: 30 dias, prazo proprio, sem dobro (`cpc-excertos-prev.md`, art. 535).
   - Prazo judicial na Vara Federal e no TRF: recursos e contrarrazoes em 15 dias, embargos de declaracao em 5 (`cpc-recursos-prazos-prev.md`, arts. 1.003, par. 5, e 1.023). No JEF: recurso inominado em 10 dias da ciencia da sentenca e contrarrazoes ao recurso inominado tambem em 10 dias, da intimacao para resposta (`lei-9099-1995.md`, art. 42, caput e par. 2); nunca 15. Duracao fora do context/ (PEDILEF, prazo fixado pelo juiz): vem da intimacao ou do advogado, marcada `[VERIFICAR]`; nunca de memoria.
2. Fixar o marco. Na via administrativa a intimacao eletronica se considera feita no acesso ao conteudo; sem acesso, presume-se valida passados 5 dias da disponibilizacao (`in-128-2022-inss.md`, art. 599, par. 1). Sem saber qual, contar dos dois e usar a data mais cedo.
3. Montar a entrada do motor pela via:
   - Administrativa (INSS, CRPS): dias corridos, excluido o dia do comeco, incluido o do vencimento, prorrogado ao primeiro dia util se o vencimento cair sem expediente (`in-128-2022-inss.md`, art. 597). No motor: `rito` cpc, `natureza` material, `unidade` corridos, `meio` ciencia-expressa, `incluir_pontos_forenses` false (Carnaval e outros pontos facultativos contam como uteis, para nao alongar o prazo em silencio). Aqui `material` e so o jeito de o motor contar como manda o art. 597 (corridos, sem recesso); o alerta `[VERIFICAR]` de prazo material que o motor emite fica respondido por esse artigo.
   - Vara federal e TRF: `rito` cpc, `natureza` processual, `unidade` uteis, `meio` conforme a intimacao (dje, sistema, ar, oficial, edital, ciencia-expressa).
   - JEF: o motor nao tem rito de JEF. Usar `rito` cpc com `unidade` uteis e avisar: no JEF nao ha prazo diferenciado para as pessoas juridicas de direito publico, o INSS inclusive (`lei-10259-2001-jef.md`, art. 9); nunca `dobro` fazenda no JEF. Os dias uteis no JEF vem da Lei 9.099, aplicada pelo art. 1 da Lei 10.259 (`lei-10259-2001-jef.md`, art. 1); a regra e o art. 12-A da Lei 9.099 (`lei-9099-1995.md`).
   - Dobro: antes de montar a entrada, perguntar quem representa o segurado. Advogado constituido: sem dobro. Defensoria Publica: `dobro` defensoria com `[VERIFICAR]` (o artigo do CPC nao esta no context/), inclusive no JEF, onde o art. 9 so alcanca a pessoa juridica de direito publico. Prazo do INSS fora do JEF: `dobro` fazenda (`cpc-recursos-prazos-prev.md`, art. 183), e nunca na impugnacao do art. 535, que ja e prazo proprio de 30 dias (`cpc-excertos-prev.md`, art. 535): ali `prazo` 30, sem `dobro`.
   - Feriado local, ponto facultativo do INSS, suspensao do tribunal ou indisponibilidade do sistema: entram em `feriados_locais` e `suspensoes`; o motor nao os conhece.
4. Gravar o JSON em `previdenciario/casos/<slug>-prazo.json` e rodar o motor (secao Calculo).
5. Entregar a data-limite, o dia da semana, o primeiro dia contado, os dias excluidos e todos os `alertas` do motor. Sinalizar se faltam 5 dias uteis ou menos.
6. Beneficio por incapacidade cessado ou indeferido: lembrar que o auxilio temporario requerido depois de 30 dias do afastamento comeca na DER, salvo DII posterior (`lei-8213-1991.md`, art. 60, par. 1). A DIB e conta do script de incapacidade, via `calculos-previdenciarios`.
7. Prazo ja vencido (pelo marco do prazo fatal, nunca so pela meta preventiva): avisar na primeira linha. O INSS nao pode recusar o recurso intempestivo (`in-128-2022-inss.md`, art. 578, par. 1), mas a admissibilidade e do CRPS: intempestividade leva ao nao conhecimento (regimento CRPS, art. 112, I), e a relevacao so cabe com liquidez e certeza inequivocas (pars. 1 e 2), sem diligencia (par. 8). Examinar se o caso se encaixa; nunca prometer relevacao. Apresentar as outras vias (novo requerimento, acao judicial, revisao dentro da decadencia) para a `estrategia-de-caso-previdenciario`.

## Calculo
Script: `calc_previdenciario_prazo.py` (motor de prazo, copia conferida por sha256; nao tem `--versao`).
```flags
--entrada    arquivo   opcional   caminho do JSON; sem ele le a entrada padrao
--feriados   arquivo   opcional   so para testes; no uso normal, nao passar
```
```campos
marco   data   obrigatoria   AAAA-MM-DD; significado depende do meio
meio   enum   obrigatoria   dje|sistema|ar|oficial|edital|ciencia-expressa
marco_portal   enum   condicional   consulta|envio; obrigatoria com meio sistema
prazo   inteiro   obrigatoria   1 a 3650
unidade   enum   obrigatoria   uteis|corridos|meses|anos
rito   enum   obrigatoria   cpc|clt|jec|penal; neste plugin so cpc
natureza   enum   opcional   processual|material; padrao processual
dobro   objeto   opcional   {"motivo": fazenda|mp|defensoria|litisconsortes-procuradores-distintos}
processo_eletronico   bool   condicional   com dobro de litisconsortes
feriados_locais   lista   opcional   AAAA-MM-DD ou {"data","motivo"}
suspensoes   lista   opcional   [inicio,fim] ou {"inicio","fim","motivo"}
incluir_pontos_forenses   bool   opcional   padrao true
uf   texto   opcional   so informativo
excecao_recesso_penal   enum   opcional   reu-preso|maria-da-penha|medida-urgente; nunca usar aqui
```
Achar o motor como na secao 13 da metodologia: `<pasta-base>/../../scripts/calc/calc_previdenciario_prazo.py --entrada <arquivo>`. Sem `--versao` no motor, havendo mais de uma copia, usar o motor de prazo que acompanha os scripts de calculo do plugin, versao 2.0.1 (a copia na pasta em que os demais scripts respondem 2.0.1 ao `--versao`).
Exit 0: usar o resultado. Exit 2: mostrar o `detalhe` e perguntar de novo o dado recusado. Sem Python, sem motor ou outro exit: contar a mao pela regra do passo 3, dia a dia, e avisar que a data nao foi conferida por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Sem a fonte da duracao do prazo, a data sai com `[VERIFICAR]`. Nunca preencher por suposicao.

## Entrega obrigatoria final
- Quadro: ato, fundamento do prazo, marco, modo de contagem, data-limite, dia da semana, dias excluidos, alertas do motor, e se ja venceu.
- Caminho do JSON de entrada usado.

## Guard
- Nunca data de cabeca; nunca omitir os alertas do motor.
- Nunca prometer conhecimento de recurso fora do prazo.
- Nunca aplicar dobro sem saber quem representa a parte; nunca dobro fazenda no JEF nem no art. 535.
- Feriado local e ato do tribunal ficam a cargo do advogado: dizer sempre que foram ou nao informados.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill prazos-previdenciarios - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
