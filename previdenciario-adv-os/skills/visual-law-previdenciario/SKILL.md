---
name: visual-law-previdenciario
description: "Monta o quadro visual do caso previdenciario: comparativo das regras de transicao da EC 103 (arts. 15 a 21, direito adquirido e permanente) gerado do texto da emenda, linha do tempo de vinculos do CNIS, linha DII-DER-DIB-DCB, quadro de renda per capita do BPC e quadro de calculo. Use quando o operador disser visual law, quadro comparativo, tabela das regras, linha do tempo, infografico, explicar com tabela. Nao use para calcular: o numero vem de calculos-previdenciarios."
---

# VISUAL-LAW-PREVIDENCIARIO

> Camada C2 (transversal). Transforma dado ja conferido em tabela, linha do tempo ou fluxo. Nao produz numero novo.

## Entradas
- Recebe: o tipo de quadro (obrigatorio) · os dados ja conferidos: saida de script, CNIS lido por `analise-cnis`, carta do INSS (obrigatorio) · destino: anexo de peca, parecer ou mensagem ao cliente (opcional)
- Chamada por: previdenciario-master · parecer-previdenciario · documentos-extrajudiciais-previdenciarios · recursos-previdenciarios | Chama: calculos-previdenciarios · prazos-previdenciarios · recursos-previdenciarios · validador-previdenciario · suprema-corte-previdenciaria

## Anexos obrigatorios (context/)
- `context/lei/ec-103-2019.md` (arts. 3o, 15 a 21 e 26 - grep o artigo e leia a faixa; descartar linhas `(revogado)`)
- `context/lei/lei-8742-1993-loas.md` (art. 20, caput e pars. 1o, 3o, 3o-A, 9o, 11, 11-A e 14)
- `context/lei/temas-sumulas-prev.md` (STF Tema 27, STJ Tema 185, TNU Sumula 79)
- `context/metodologia-previdenciario.md` (secoes 6 e 9 - distincoes e relogio)

## Objetivo
Entregar o quadro certo para o destino, com cada celula rastreavel ao dispositivo ou a saida do script.

## Metodologia
1. Escolher o quadro pelo pedido: aposentadoria -> regras de transicao + linha do CNIS; incapacidade -> linha DII-DER-DIB-DCB; BPC -> renda per capita; revisao -> quadro de calculo; recurso -> fluxo de vias.
2. Conferir que todo dado do caso ja veio conferido (script com exit 0, ou formula aberta marcada como tal). Faltou numero: pedir a `calculos-previdenciarios`; nunca preencher celula por estimativa.
3. Montar o quadro. Requisito do ano corrente (pontos, idade progressiva) e o resultado do caso saem do script de transicao, nao da conta de cabeca.
4. Decidir o lugar: em peca e parecer, como anexo ou quadro numerado fora da narrativa dos fatos; em mensagem ao cliente, integrado e sem numero de artigo.
5. Conferir celula a celula contra o dispositivo; sem ancora, a celula leva `[VERIFICAR]`.
6. Fechamento: chamada direto pelo master, o quadro passa por `validador-previdenciario` e `suprema-corte-previdenciaria` antes de ir ao advogado; chamada por outra skill, o quadro volta a ela, que fecha a entrega inteira pelos dois.

### Quadro 1 - Regras de aposentadoria do RGPS (EC 103; M = mulher, H = homem)
| Regra | Quem | Requisitos | Progressao | Valor |
|---|---|---|---|---|
| Direito adquirido (art. 3o) | requisitos cumpridos ate 13/11/2019 | os da lei da epoca | - | lei da epoca |
| Pontos (art. 15) | filiado ate 13/11/2019 | 30 M / 35 H de contribuicao + 86 M / 96 H pontos; idade e tempo em dias (par. 2o) | +1 ponto por ano desde 1o/01/2020, ate 100 M / 105 H (par. 1o) | 60% + 2 p.p. por ano acima de 15 M / 20 H (art. 26, pars. 2o, I, e 5o) |
| Pontos, professor (art. 15, par. 3o) | idem, so magisterio na educacao infantil, ensino fundamental e medio | 25 M / 30 H + 81 M / 91 H pontos | +1 por ano ate 92 M / 100 H | idem |
| Idade progressiva (art. 16) | filiado ate 13/11/2019 | 30 M / 35 H + idade 56 M / 61 H | +6 meses por ano desde 2020 ate 62 M / 65 H (par. 1o) | idem |
| Idade progressiva, professor (art. 16, par. 2o) | idem, so magisterio | tempo e idade reduzidos em 5 anos | +6 meses por ano ate 57 M / 60 H | idem |
| Pedagio de 50% (art. 17) | so quem tinha mais de 28 M / 33 H em 13/11/2019 | 30 M / 35 H + 50% do que faltava em 13/11/2019; sem idade minima | nao progride | media x fator previdenciario (par. unico) |
| Idade (art. 18) | filiado ate 13/11/2019 | 60 M / 65 H de idade + 15 anos | idade da mulher +6 meses por ano ate 62 (par. 1o) | 60% + 2 p.p. (art. 26, pars. 2o, I, e 5o) |
| Pedagio de 100% (art. 20) | filiado ate 13/11/2019 | 57 M / 60 H de idade + 30 M / 35 H + 100% do que faltava em 13/11/2019 | nao progride | 100% da media (art. 26, par. 3o, I) |
| Pedagio de 100%, professor (art. 20, par. 1o) | idem, so magisterio | idade e tempo reduzidos em 5 anos | nao progride | idem |
| Especial por pontos (art. 21) | filiado ate 13/11/2019, exposicao efetiva | 66 pontos + 15 anos; 76 + 20; 86 + 25 | nao progride | 60% + 2 p.p. acima de 20; acima de 15 no especial de 15 e para a mulher (art. 26, pars. 2o, IV, e 5o) |
| Permanente (art. 19) | filiado depois de 13/11/2019 | 62 M / 65 H de idade + 15 M / 20 H | - | 60% + 2 p.p. por ano acima de 15 M / 20 H (art. 26, pars. 2o, IV, e 5o) |
| Permanente especial (art. 19, par. 1o, I) | idem | idade 55 / 58 / 60 com 15 / 20 / 25 anos de exposicao | - | idem; acima de 15 no especial de 15 (art. 26, par. 5o) |
| Permanente professor (art. 19, par. 1o, II) | idem | 25 anos de magisterio + 57 M / 60 H | - | idem |
Notas fixas do quadro: o art. 17 e so do RGPS; a media e a da EC 103, art. 26, limitada ao teto (par. 1o); o fator previdenciario sai como formula enquanto a tabua do IBGE nao estiver capturada (metodologia, secao 8, M7). Quem filiou ate 13/11/2019 tem as transicoes comparadas pelo script; quem filiou depois, so a permanente (metodologia, secao 6).

### Quadro 2 - Linha do tempo do CNIS
Uma linha por vinculo ou periodo: empregador ou categoria, inicio, fim, indicador do Anexo V (sigla como no extrato) e marca do que conta para carencia e para tempo, conforme a saida de `analise-cnis`. Periodo especial fatiado em 13/11/2019 aparece em duas linhas.

### Quadro 3 - Incapacidade
`DII -> DAT -> DER -> DIB -> DCB`, cada marco com data e documento de origem. DAT, DII e DER nunca se confundem (metodologia, secao 9, linha do inicio do auxilio).

### Quadro 4 - BPC, renda per capita
| Membro do grupo (mesmo teto) | Renda mensal | Entra no calculo? |
|---|---|---|
Regras do quadro: criterio "igual ou inferior a 1/4" do salario minimo (LOAS, art. 20, par. 3o). Entra no quadro so quem compoe a familia do par. 1o e vive sob o mesmo teto: requerente, conjuge ou companheiro, pais (na falta de um, madrasta ou padrasto), irmaos solteiros, filhos e enteados solteiros, menores tutelados; quem mora junto sem estar nesse rol fica fora da conta, com a razao na coluna. Soma dos rendimentos mensais desses membros (par. 3o-A). Fora da conta os valores do par. 9o e o BPC ou beneficio previdenciario de ate 1 salario minimo concedido a idoso acima de 65 anos ou a pessoa com deficiencia da mesma familia, quando o pedido e de BPC para outro idoso ou pessoa com deficiencia (par. 14); idoso a partir de 65 anos (caput). O 1/4 nao e o unico meio de prova (STF Tema 27; STJ Tema 185; TNU Sumula 79, laudo social). O Tema 27 foi fixado sobre a redacao "inferior a 1/4"; a lei hoje diz "igual ou inferior": aplicar a tese a redacao nova e leitura, dita como tal no quadro. Ampliacao ate 1/2 (par. 11-A) depende de regulamento nao conferido: nunca aplicar sozinha. BPC nao tem abono anual (metodologia, secao 5, verdade 9).

### Quadro 5 - Calculo (revisao ou concessao)
| Item | Carta do INSS | Conta conferida | Diferenca |
|---|---|---|---|
Linhas: PBC, divisor, media, coeficiente, RMI, DIB. Cada valor da coluna "conta conferida" cita a saida do script (ou "formula aberta, nao conferida por script").

### Quadro 6 - Vias contra decisao
Decisao do INSS -> recurso ordinario as Juntas de Recursos do CRPS (IN 128, art. 578) em 30 dias da ciencia (Decreto 3.048, art. 305, par. 1o, II) ou acao judicial (Decreto 3.048, art. 307: acao com pedido identico importa renuncia ao recurso administrativo). Decisao judicial -> via e prazo por `recursos-previdenciarios` e `prazos-previdenciarios`; o quadro nao traz dias de cabeca.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita no quadro. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- O quadro em markdown, com titulo, fonte de cada coluna e a indicacao de onde inserir (anexo ou integrado).

## Guard
- Nenhum numero do caso sem script ou formula aberta marcada; nenhum dispositivo sem ancora.
- Simbolos fixos no documento inteiro: ✅ conferido, 🟡 a confirmar, 🔴 contra o pedido. Dado desfavoravel ao segurado aparece; nao se oculta.
- Em mensagem ao cliente: sem artigo, sem sigla sem explicacao, sem dado sensivel alem do necessario.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do quadro:
`Entregue pela skill visual-law-previdenciario - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
