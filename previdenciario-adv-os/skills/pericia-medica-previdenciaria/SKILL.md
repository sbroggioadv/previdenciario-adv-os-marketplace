---
name: pericia-medica-previdenciaria
description: "Analisa laudo pericial (INSS, judicial ou de assistente tecnico) em beneficio por incapacidade, auxilio-acidente e BPC da pessoa com deficiencia: CID, DII, DAT, nexo com o trabalho, coerencia interna, quesitos nao respondidos e condicoes pessoais; formula quesitos e quesitos suplementares e calcula a RMI e a DIB pelo script de incapacidade. Use quando o advogado anexar laudo, pedir quesitos, impugnacao de laudo, analise de pericia, DII ou valor do auxilio. Nao use para PPP, LTCAT ou tempo especial (analise-ppp-ltcat-aposentadoria-especial) nem para avaliacao social do BPC (bpc-loas-previdenciario)."
---

# PERICIA MEDICA PREVIDENCIARIA

> Camada 3 (analise e prova). Le o laudo como prova tecnica, ataca o laudo e nao o perito, e fecha o numero do beneficio pelo script.

## Entradas
- Recebe: laudo pericial (obrigatorio para analise) · beneficio pretendido e fase (administrativa ou judicial) (obrigatorio) · atestados, exames, prontuarios, receitas, CAT (opcional) · DAT, DII, DER e SB (para o calculo)
- Chamada por: previdenciario-master · acidentario-do-trabalho · bpc-loas-previdenciario · audiencia-previdenciaria | Chama: estilo-juridico-previdenciario · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-incapacidade.md` (secoes 1 a 6 - percentuais, limitadores, DIB, caso INCAP-03, CAMPOS)
- `context/lei/lei-8213-1991.md` (arts. 21-A, 26, 42, 59, 60, 61, 62, 86 e 101 - grep o artigo e leia a faixa; descarte linhas `(revogado)`)
- `context/lei/ec-103-2019.md` (art. 26, pars. 2o, III, e 3o, II)
- `context/lei/lei-8742-1993-loas.md` (art. 20, pars. 2o, 2o-A e 10)
- `context/lei/in-128-2022-inss.md` (arts. 233 e 336)
- `context/lei/temas-sumulas-prev.md` (STF Tema 1300; STJ Tema 416; TNU Sumula 47)
- `context/calculo-cnis.md` (carencia e qualidade de segurado)
- `context/escrita-humana.md` (passada anti-IA)

## Objetivo
Parecer tecnico sobre o laudo (fragilidades, confronto documental, quesitos) e, quando houver dado, RMI e DIB do beneficio pelo script.

## Metodologia
1. Dado sensivel: laudo, CID e prontuario ficam no computador do advogado; nunca em ferramenta externa.
2. Devolver o quadro do caso em 3 a 6 linhas (beneficio, fase, CID alegado, DAT, DII, DER, nexo com o trabalho, carencia e qualidade conferidas pela analise-cnis) e esperar confirmacao. "Nao sei" = lacuna.
3. Leitura do laudo, item a item: tipo e data; especialidade do perito frente a doenca; anamnese; exame fisico ou analise documental (a lei admite telemedicina e analise documental na forma do regulamento: Lei 8.213, art. 42, par. 1o-A; nao e nulidade automatica, e ponto a examinar); CID e compatibilidade com a queixa; DII fixada e com que base; capacidade examinada para a atividade habitual (art. 59); temporaria ou permanente e insusceptibilidade de reabilitacao (art. 42); nexo com o trabalho; quesitos de cada parte respondidos.
4. Coerencia interna: anamnese x exame x conclusao; CID grave com conclusao de capacidade sem fundamento; progressao documentada ignorada. Cada contradicao com o trecho do laudo e o documento que a contraria.
5. Confronto documental: atestados, exames, internacoes, receituario continuo e relatorios de especialista, com datas, para sustentar a DII e a duracao.
6. Pontos de direito que mudam o resultado:
   - Incapacidade parcial: analisar condicoes pessoais e sociais (TNU Sumula 47, literal no anexo).
   - Auxilio-acidente: devido ainda que minima a lesao (STJ Tema 416, literal no anexo); sem carencia; sem piso; inacumulavel com aposentadoria (art. 86).
   - Permanente: a DII decide a regra; DII depois de 13/11/2019 e sem nexo laboral = 60% + 2% (STF Tema 1300); com nexo laboral = 100% (EC 103, art. 26, par. 3o, II). Acidente sem nexo com o trabalho nao e acidentario.
   - Nexo tecnico epidemiologico: a caracterizacao acidentaria pela pericia segue o art. 21-A da Lei 8.213 (ler a faixa); com nexo, devolver ao master a trilha acidentario-do-trabalho.
   - BPC da pessoa com deficiencia: impedimento de longo prazo (minimo de 2 anos) em interacao com barreiras (LOAS, art. 20, pars. 2o e 10); avaliacao na forma do regulamento (par. 2o-A).
   - DIB do auxilio temporario: DAT, DII e DER separadas (art. 60, par. 1o; IN 128, art. 336, I e II); requerimento depois de 30 dias desloca a DIB. A DII decide a DIB tambem na temporaria (DII posterior ao 16o dia ou a DER prevalece): pedir sempre a DII; sem ela, DIB `indeterminada`, nunca DAT ou DER no lugar.
7. Propor 2-3 estrategias com ganho e risco (ex.: quesitos complementares; impugnacao com pedido de nova pericia por especialista; assistente tecnico; manter o laudo e discutir so a DII) e esperar a escolha.
8. Quesitos por beneficio (redigir na hora, objetivos, um fato por quesito):
   - Temporaria ou permanente: existencia, grau e duracao da incapacidade; DII e base documental; incapacidade para a atividade habitual descrita; possibilidade de reabilitacao considerando idade, escolaridade e historico; tratamento e prazo de recuperacao; nexo com o trabalho.
   - Auxilio-acidente: consolidacao das lesoes; sequela; reducao da capacidade para o trabalho habitual, qualquer que seja o grau.
   - BPC deficiencia: natureza do impedimento; duracao igual ou superior a 2 anos; barreiras e participacao; autonomia nas atividades diarias.
   - Suplementares: quesito nao respondido, reformulado para resposta direta; ponto omitido; pedido de esclarecimento da contradicao apontada.
9. Peticao de quesitos ou de impugnacao: voz e cabecalho pelo estilo-juridico-previdenciario (perfil.md). Nao citar dispositivo de rito processual que nao esteja no context/; sem ele, pedir pelo nome do ato ("complementacao do laudo", "nova pericia") sem numero de artigo.
10. Calculo, quando houver dado: rodar o script (secao Calculo) para RMI, limitador e DIB; carencia e qualidade ecoam a saida da analise-cnis.
11. Passada anti-IA com `context/escrita-humana.md` antes de entregar.

## Calculo
Script `calc_previdenciario_incapacidade.py`, localizado e rodado conforme `context/metodologia-previdenciario.md` (secao 13). Entrada em JSON.

```flags
--entrada   arquivo   opcional   caminho do JSON de entrada; ausente = stdin
--versao    flag      opcional   imprime a versao (2.0.0)
```

```campos
especie                  enum      sim                                          temporaria,permanente,auxilio-acidente
acidentaria              bool      sim                                          true so com nexo laboral
sexo                     enum      sim                                          M,F
media_100                decimal   sim                                          SB, media de 100% desde 07/1994, corrigida
media_12_ultimos         decimal   se:especie=temporaria                        media dos ultimos 12 salarios de contribuicao
tempo_contribuicao_anos  inteiro   se:especie=permanente+acidentaria=false      anos completos
dii                      data      condicional                                  permanente; ou temporaria com empregado = false; data do inicio da incapacidade
dib  data  condicional  permanente e auxilio-acidente, salvo teto e salario_minimo; limites da DIB
dat                      data      se:especie=temporaria                        data do afastamento da atividade
der                      data      se:especie=temporaria                        data de entrada do requerimento
empregado                bool      se:especie=temporaria                        true para empregado, exceto domestico
assistencia_permanente   bool      nao                                          padrao false; so com especie=permanente
salario_minimo           decimal   nao                                          ausente = tabela pela data da DIB ou DII
teto                     decimal   nao                                          ausente = tabela pela mesma data
carencia                 enum      nao                                          sim,nao,indeterminada,dispensada
qualidade_segurado       enum      nao                                          mantida,perdida,indeterminada
```

Na temporaria a DIB sai do script pela DAT, DER e DII (IN 128, art. 336): para quem nao e empregado (inclusive o domestico), `dii` e obrigatoria e a DIB e a DII ou a DER (inciso II); para o empregado, exceto o domestico, sem `dii` a DIB fica em conta aberta, 16o dia ou DER, ou a DII se posterior, com `[VERIFICAR]`, porque a DII nao se presume (inciso I). Pedir a DII sempre que houver. Exit 0: usar o resultado e mostrar a memoria. Exit 2: perguntar de novo o dado errado (inclusive DAT ou DER na temporaria). Exit 3: formula com o termo faltante. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-incapacidade.md`, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Parecer sobre o laudo: conclusao do perito, fragilidades (graves e moderadas) com o trecho, confronto documental.
- Quesitos ou quesitos suplementares, ou a peticao na estrategia escolhida.
- RMI, limitador e DIB pelo script (ou a marca "conta nao conferida por script").

## Guard
- Nunca STJ Tema 416 como "necessidade de pericia oficial": e auxilio-acidente com lesao minima.
- Nunca piso no auxilio-acidente nem acumulacao com aposentadoria; nunca "nao acumula com auxilio-doenca" como regra fechada.
- Nunca atacar a pessoa do perito; o alvo e o laudo.
- Nunca inventar CID, DII ou data de exame.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill pericia-medica-previdenciaria - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
