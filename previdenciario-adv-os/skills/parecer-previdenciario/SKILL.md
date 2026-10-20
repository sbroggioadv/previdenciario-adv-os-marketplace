---
name: parecer-previdenciario
description: "Redige parecer juridico previdenciario (consulta de viabilidade, risco ou estrategia) na estrutura I a VI, com fatos confirmados pelo advogado, numeros so por script ou conta aberta, citacao so com ancora em context/ e conclusao em cenarios concretos, sem percentual de exito. Use quando o operador disser parecer, consulta, opiniao legal, viabilidade do caso, vale a pena entrar com a acao, /parecer-previdenciario. Nao use para peca processual (peticao-inicial-previdenciaria, recursos-previdenciarios) nem para notificacao ou mensagem ao cliente (documentos-extrajudiciais-previdenciarios)."
---

# PARECER-PREVIDENCIARIO

> Camada C2 (transversal). Parecer consultivo do escritorio sobre um caso previdenciario: responde as perguntas do consulente com fundamento ancorado e cenarios de decisao.

## Entradas
- Recebe: pergunta(s) do consulente (obrigatorio) · documentos do caso: CNIS, carta do INSS, PPP, laudo, sentenca (opcional) · `previdenciario/casos/<slug>.md` (se existir)
- Chamada por: previdenciario-master | Chama: base-legal-previdenciaria · jurisprudencia-estrategica-previdenciario · calculos-previdenciarios · prazos-previdenciarios · estrategia-de-caso-previdenciario · visual-law-previdenciario · estilo-juridico-previdenciario · validador-previdenciario · suprema-corte-previdenciaria · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secoes 5, 6, 7.1, 8, 9 e 10 - grep a secao e leia a faixa)
- `context/lei/INDICE.md` (tema -> diploma -> artigo; ponto de partida de toda citacao)
- `context/lei/temas-sumulas-prev.md` (so o item pedido - grep o numero do tema e leia a entrada inteira, com a Nota)
- `context/escrita-humana.md` (secoes 5, 6, 7 e 8 - passada anti-IA)
- `context/calculo-<x>.md` (so quando a resposta depender de numero e o script nao rodar)

## Objetivo
Entregar ao advogado um parecer que responde cada questao com fundamento conferido em `context/`, diz o que nao fecha e termina em cenarios de decisao com ganho, risco e proximo passo.

## Metodologia
1. [redacao] Devolver o quadro do caso em 3 a 6 linhas (segurado, beneficio ou ato do INSS, datas que importam: DER, DIB, DCB, ciencia da decisao; o que se quer saber) e esperar a confirmacao. "Nao sei" vira lacuna declarada, nunca suposicao.
2. Prazo antes de tudo: se houver recurso, resposta ou cessacao/indeferimento ha menos de 30 dias, avisar na primeira linha e acionar `prazos-previdenciarios` (metodologia, secao 4).
3. Formular as questoes: uma principal, no maximo duas subsidiarias, cada uma respondivel por sim, nao ou depende de fato X.
4. Para cada questao, achar o dispositivo pelo `INDICE.md` via `base-legal-previdenciaria` e a jurisprudencia via `jurisprudencia-estrategica-previdenciario`. Citacao nomeia o diploma (homonimos: metodologia 7.1). Item sem ancora sai como `[VERIFICAR]`.
5. Numero (carencia, tempo, regra de transicao, RMI, valor da causa, atrasados, decadencia, prescricao): pedir a `calculos-previdenciarios`. Script com exit 0: usar e anexar a memoria. Exit 3 ou sem script: formula aberta do `context/calculo-<x>.md`, com o aviso de que o numero nao foi conferido por script.
6. [redacao] Propor 2 a 3 caminhos (via `estrategia-de-caso-previdenciario`), cada um com ganho, risco e custo de tempo; esperar a escolha do advogado ou apresenta-los como cenarios na secao V.
7. Redigir na estrutura abaixo, na voz do escritorio (`estilo-juridico-previdenciario`, lendo `previdenciario/perfil.md`). Tabela comparativa, se ajudar, por `visual-law-previdenciario`, como anexo.
8. [redacao] Passada anti-IA com `context/escrita-humana.md` secao 7 (contar marcadores da secao 3, reescrever o que estoura, pergunta-filtro da secao 8). Nao anunciar a passada no texto.
9. Entregar a `validador-previdenciario` e a `suprema-corte-previdenciaria` (R1 a R4) antes de devolver ao advogado; gravar o ato em `memoria-de-caso-previdenciario`.

### Estrutura I a VI
```
I. INTRODUCAO - consulente (como no perfil/caso), objeto, questoes, documentos examinados
II. FATOS - so o quadro confirmado; lacunas listadas ao final da secao
III. QUESTOES - numeradas
IV. FUNDAMENTACAO - uma subsecao por questao:
    IV.n.1 norma (dispositivo nomeado, com o diploma)
    IV.n.2 jurisprudencia (so item de temas-sumulas-prev.md; Nota respeitada)
    IV.n.3 conta (resultado do script ou formula aberta, com a memoria em anexo)
    IV.n.4 aplicacao ao caso e conclusao parcial
V. ANALISE CRITICA - o que nao fecha (divergencia declarada, gap, item a confirmar
   do gate de vigencia); 2-3 cenarios com ganho, risco e prazo; nenhum percentual
VI. CONCLUSAO - resposta a cada questao em uma ou duas frases, em primeira pessoa
    ("entendo que"); caminho recomendado; documentos a obter; prazos com data
```

### Regras de conteudo
- Percentual de exito nao entra: nao ha base para medi-lo. O risco e descrito pelo fato que o gera (prova fraca, tese com divergencia declarada, item pendente no STF).
- Doutrina so com autor, obra, edicao e pagina fornecidos pelo advogado; sem isso, nao atribuir (escrita-humana, AI-09).
- Divergencia que o plugin declara (abono nas vincendas, salario minimo da RPV, Tema 27 e a redacao atual da LOAS, INPC de 2006): expor as duas leituras e qual o plugin usa, como interpretacao.
- Consulta sobre revisao pela regra definitiva do art. 29 da Lei 8.213 em vez do art. 3o da Lei 9.876: o parecer conclui pela inviabilidade (STF Tema 1.102, tese nova; ADIs 2.110 e 2.111) e trata so a modulacao, nos dois criterios da entrada do tema. Embargos pendentes: reverificar (metodologia, secao 10, item 2).
- Prazos com data so por `prazos-previdenciarios` ou pelo script de RMI (decadencia, prescricao); nunca contados de cabeca.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita no parecer. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Parecer em markdown, secoes I a VI, pronto para o papel timbrado do escritorio.
- Anexos: memoria de cada conta (ou formula aberta) e, se houver, quadro do `visual-law-previdenciario`.
- Fora do parecer, ao advogado: lista de `[VERIFICAR]`, lacunas e itens do gate de vigencia tocados.

## Guard
- Nunca citar dispositivo, tema, sumula ou indice sem ancora em `context/`; nunca de memoria (`anti-alucinacao-previdenciario`).
- Nunca oferecer como tese o que o `CLAUDE.md` lista como verdade dura contraria.
- Nunca prometer resultado nem estimar chance em numero.
- CNIS e laudo sao dado pessoal sensivel: ficam no computador do advogado; nada vai para ferramenta externa.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do parecer:
`Entregue pela skill parecer-previdenciario - plugin previdenciario-adv-os v2.0.1`.
Registrar a mesma linha em `previdenciario/casos/<slug>.md`.
