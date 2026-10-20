---
name: base-legal-previdenciaria
description: "Porta para a lei seca previdenciaria capturada em context/lei/. Acha o dispositivo pelo INDICE.md, faz grep do artigo no arquivo do diploma, descarta a redacao riscada, le a faixa vigente e devolve o texto com o diploma nomeado e o aviso de homonimo (art. 3, 17, 20, 26, 27-A, 42 existem em mais de um diploma). Use quando o operador disser qual artigo, onde esta na lei, me traz o texto do art., fundamento legal, base legal, cita a lei, e quando outra skill precisar do dispositivo antes de citar. Nao use para jurisprudencia (jurisprudencia-estrategica-previdenciario) nem para conferir uma peca inteira (validador-previdenciario)."
---

# BASE-LEGAL-PREVIDENCIARIA

> Camada 1 (fundacao). Nao redige peca: entrega o dispositivo vigente, lido no arquivo, com o diploma nomeado. Lei de memoria nao entra.

## Entradas
- Recebe: tema ou dispositivo procurado (obrigatorio) · data do fato, do periodo ou da competencia (opcional; decide qual redacao rege)
- Chamada por: previdenciario-master · validador-previdenciario | Chama: anti-alucinacao-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/INDICE.md` (secao 2, tema -> diploma -> artigo; secao 3, o que ficou de fora - ler a linha do tema)
- `context/lei/<arquivo-do-diploma>.md` (o artigo indicado no INDICE - grep o artigo e leia a faixa)
- `context/metodologia-previdenciario.md` (secao 1, regra de leitura; secao 7.1, homonimos; secao 10, gate de vigencia - grep a secao e leia a faixa)

## Objetivo
Devolver o texto vigente do dispositivo pedido, do diploma certo, com a faixa lida e a ressalva de vigencia, para que nenhuma peca cite artigo de cabeca.

## Metodologia
1. **Localizar no INDICE.** Grep do tema em `context/lei/INDICE.md`. A linha diz o arquivo e o artigo. Tema que aparece na secao 3 do INDICE (fora do corpus) -> parar e declarar o gap (passo 8).
2. **Grep do artigo, nunca do arquivo inteiro.** Padroes que funcionam no corpus:
   - `grep -n '^Art\. 27-A' context/lei/lei-8213-1991.md`
   - `grep -n '^Art\. 3[^0-9-]' context/lei/lei-9876-1999.md` (o corpus grafa `Art. 3o`, `Art. 3` com ordinal ou `Art. 3.`; o filtro evita casar o art. 30 ou o 3-A)
   - `grep -n '^(revogado) ~~Art\. 3' context/lei/ec-113-2021.md` (para achar a redacao riscada de proposito)
   Ler com `sed -n '<linha>,<linha+N>p'` a faixa do caput ate o ultimo paragrafo do artigo (para no proximo `^Art\.`).
3. **Descartar o riscado.** Linha que comeca com `(revogado) ~~...~~` nao e norma vigente hoje. O art. 103 da Lei 8.213 aparece varias vezes no arquivo; so uma e a vigente. O art. 27-A da Lei 8.213 tem tres redacoes riscadas antes da vigente (Lei 13.846/2019).
4. **Excecao: redacao riscada que rege periodo passado.** Quando a data do fato cai na vigencia da redacao antiga, a riscada e a que rege aquele periodo, e a citacao diz isso. Caso do corpus: a Selic unica do art. 3 da EC 113/2021 esta riscada (substituida pela EC 136/2025) e rege as competencias de dez./2021 a ago./2025 (`context/lei/temas-sumulas-prev.md`, STF Tema 1.419, embargos). Citar como "EC 113/2021, art. 3, redacao original".
5. **Nomear o diploma na linha da citacao, sempre.** Numero de artigo sozinho nao identifica a regra. Homonimos do dominio (lista completa na metodologia, secao 7.1):

| Numero | Nao confundir |
|---|---|
| art. 27-A | Lei 8.213 ("metade dos periodos" dos incisos do art. 25) x Decreto 3.048 ("metade do numero de contribuicoes"; as anteriores a perda so contam depois disso) - mesma materia, redacoes diferentes; citar a lei e, se usar o decreto, dizer que e o regulamento |
| art. 3 | Lei 9.876/1999 (regra de transicao do salario de beneficio, cogente) x EC 113/2021 (atualizacao dos requisitorios; a original riscada e a Selic) x EC 103/2019 (direito adquirido) x Lei 10.259/2001 (alcada do JEF) |
| art. 17 | EC 103 (pedagio de 50%) x Lei 10.259 (RPV em 60 dias) |
| art. 20 | EC 103 (pedagio de 100%) x Lei 8.742 (BPC) |
| art. 26 | EC 103 (calculo do beneficio) x Lei 8.213 (dispensa de carencia) |
| art. 42 | Lei 8.213 (aposentadoria por invalidez) x Decreto 3.048 (paragrafo unico afasta o piso do auxilio-acidente) |
| art. 15 | Lei 8.213 (qualidade de segurado) x EC 103 (transicao por pontos) |

6. **Conferir a marca de vigencia da fonte.** Remissao como "(Vide ADIN 6096)" no art. 103 da Lei 8.213 ou "(Vide ADI 2110)" no art. 3 da Lei 9.876 vai para a resposta. A ADI 6.096 nao esta capturada: decadencia sobre indeferimento, cancelamento ou cessacao sai "a confirmar" (metodologia, secao 10, item 7).
7. **Gate de vigencia.** Item da secao 10 da metodologia (salario minimo e teto do ano, lei que discipline o calculo do art. 26 da EC 103, Anexo V da Portaria 990, Manual CJF, Res. CJF 983/2026) entra como "a confirmar" se nao foi reverificado.
8. **Fora do corpus = gap declarado.** Sem arquivo em `context/lei/`, a skill nao cita o dispositivo: diz que nao esta capturado, o que isso limita e onde conferir ao vivo. Gaps conhecidos: anexos da IN 128/2022, Lei 9.289/1996 (custas na Justica Federal), ADI 6.096, tabua do IBGE, formula do fator previdenciario (imagem no Anexo da Lei 9.876), ato vigente da lista do art. 26, II, da Lei 8.213, regulamento do art. 20, par. 11-A, da LOAS. Ja capturados (nao sao mais gap): LC 108/2001, LC 109/2001, Lei 9.717/1998, Lei 10.887/2004, LC 142/2013, MP 316/2006, DL 2.322/1987 e o Regimento do CRPS (`regimento-crps-portaria-mps-125-2026.md`: prazos e contrarrazoes, arts. 77 e 78; intimacao, arts. 79 e 80; embargos de declaracao, art. 92; nao conhecimento e relevacao da intempestividade, art. 112).
9. **Acionar** `anti-alucinacao-previdenciario` antes de devolver: dispositivo citado com conteudo da lista de proibicoes (ex.: PBC de 100% atribuido a Lei 13.846/2019) e corrigido na hora.

## Atalhos que mais se pedem (sempre conferir no arquivo)
- Carencia: `lei-8213-1991.md` arts. 24, 25, 26, 27, 27-A · qualidade e graca: art. 15 · perda: `decreto-3048-1999.md` art. 14 e `lei-8212-1991.md` art. 30, II
- Transicoes e calculo: `ec-103-2019.md` arts. 3, 15 a 21, 25 (par. 2), 26 · multiplicadores: `decreto-3048-art188p-tabela.md`
- Divisor 108: `lei-8213-1991.md` art. 135-A · decadencia e prescricao: art. 103 · inicio do auxilio temporario: art. 60, par. 1
- BPC: `lei-8742-1993-loas.md` art. 20 · JEF: `lei-10259-2001-jef.md` arts. 3, 9, 17 · requisitorios: `res-cjf-983-2026.md` arts. 3, 7, 16

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha qual arquivo faltou e que o dispositivo ficou sem conferencia. Nunca preencher o texto do artigo de memoria: sem arquivo, a saida e `[VERIFICAR]` com o diploma e o numero, sem transcricao.

## Entrega obrigatoria final
- Para cada dispositivo: diploma + artigo/paragrafo/inciso · arquivo e linha onde foi lido · texto da faixa vigente (ou da redacao que rege o periodo, com a data) · aviso de homonimo quando houver · selo (✅ lido no arquivo · 🔴 a confirmar pelo gate · `[VERIFICAR]` fora do corpus).

## Guard
Bloqueia: artigo sem diploma nomeado; transcricao que nao saiu do arquivo; linha `(revogado)` apresentada como vigente sem a data do periodo que ela rege; dispositivo de diploma fora de `context/lei/` apresentado como conferido. Nao interpreta merito nem escolhe tese: isso e da trilha que chamou.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill base-legal-previdenciaria - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
