---
name: rpps-servidor-publico
description: "Triagem e encaminhamento do servidor titular de cargo efetivo no regime proprio (RPPS), sobre a lei seca: CF art. 40, EC 103 (arts. 4, 9, 10, 20, 22, 24 e 26) para o servidor federal, Lei 9.717/1998 e Lei 10.887/2004. Aponta a regra permanente ou de transicao, integralidade e paridade, abono de permanencia, acumulacao, contagem reciproca e a lei do ente que falta, com checklist de documentos. Sem conta de proventos na 2.0.3. Use quando o operador disser servidor publico, RPPS, regime proprio, aposentadoria do servidor, abono de permanencia, integralidade, paridade, CTC. Nao use para quem ocupa exclusivamente emprego publico, cargo em comissao, cargo temporario ou mandato, sem cargo efetivo (RGPS, planejamento-previdenciario) nem para a previdencia complementar do servidor (previdencia-complementar)."
---

# RPPS SERVIDOR PUBLICO

> Camada 4. Servidor de cargo efetivo: regra aplicavel e documentos, com a lei seca e sem conta.

## Entradas
- Recebe: ente (Uniao, Estado, DF ou Municipio) e cargo (obrigatorio) · datas de ingresso no servico publico e no cargo atual (obrigatorio) · nascimento, sexo, tempo de contribuicao com certidoes, opcao pela complementar, magisterio, deficiencia ou atividade nociva (opcional, pedir se faltar)
- Chamada por: previdenciario-master | Chama: previdencia-complementar · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/cf88-seguridade.md` (art. 40, par. 1 a 22; art. 201, par. 9 - grep o artigo e leia a faixa)
- `context/lei/ec-103-2019.md` (arts. 4, 8, 9, 10, 20, 22, 23, 24 e 26 - grep o artigo e leia a faixa)
- `context/lei/lei-9717-1998-rpps.md` (arts. 1 e 5) · `context/lei/lei-10887-2004.md` (arts. 1, 4 a 6 e 15)
- `context/lei/lc-142-2013-pcd.md` (arts. 3 e 8, so com deficiencia) · `context/lei/temas-sumulas-prev.md` (STF Tema 942)
- `context/lei/ec-41-2003.md` (arts. 2, 6 e 7) · `context/lei/ec-47-2005.md` (art. 3) · `context/lei/ec-103-2019.md` (arts. 3, 35 e 36, para a vigencia delas) · `context/lei/cf88-art109-competencia.md` (art. 109, I)

## Objetivo
Dizer ao advogado qual regra do RPPS se aplica ao servidor, o que a lei seca exige em cada uma, o que falta para conferir e quais documentos pedir, sem apurar tempo nem provento.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas (ente, cargo, ingresso no servico publico e no cargo, idade, objetivo) e esperar confirmacao.
2. Filtro de regime: RPPS e do titular de cargo efetivo (CF, art. 40, caput). Vai para o RGPS quem ocupa exclusivamente cargo em comissao, outro cargo temporario, mandato eletivo ou emprego publico (par. 13): conferir primeiro se ha cargo efetivo e se a ocupacao e exclusiva; so entao sair desta skill para `planejamento-previdenciario`. Vinculos simultaneos (efetivo e outro cargo ou mandato) nao se decidem aqui sem fonte: `[VERIFICAR]`.
3. Ente: servidor federal segue a EC 103 ate a lei federal (art. 10). Estados, DF e Municipios seguem as normas anteriores a EC 103 enquanto a lei local nao mudar (EC 103, arts. 4, par. 9; 10, par. 7; 20, par. 4; 22, par. unico). A lei do ente nao esta em context/: pedir ao advogado e nao citar artigo dela.
4. Regra permanente do servidor federal (EC 103, art. 10, par. 1, I): 62 anos (mulher) ou 65 (homem), 25 de contribuicao, 10 de servico publico e 5 no cargo. Tambem incapacidade permanente insuscetivel de readaptacao (II) e compulsoria (III, na forma do CF, art. 40, par. 1, II). Especiais do art. 10, par. 2: policial e agentes, atividade com exposicao efetiva a agente nocivo, professor; com exposicao nociva, conversao de tempo especial em comum vedada (par. 3).
5. Transicoes de quem ingressou ate 13/11/2019:
   - pontos (EC 103, art. 4): idade minima, 30 (mulher) ou 35 (homem) de contribuicao, 20 de servico publico, 5 no cargo e pontos progressivos, idade e tempo apurados em dias (par. 3); professor nos par. 4 e 5;
   - pedagio de 100% (art. 20): 57 ou 60 anos, 30 ou 35 de contribuicao, 20 de servico publico, 5 no cargo e o periodo adicional;
   - o pedagio de 50% (art. 17) e so do RGPS: nunca aplicar ao servidor.
6. Valor, so a regra (sem numero):
   - integralidade: totalidade da remuneracao do cargo para quem ingressou ate 31/12/2003 sem a opcao do CF, art. 40, par. 16 (art. 4, par. 6, I, com a idade minima ali exigida; art. 20, par. 2, I), com o reajuste do art. 7 da EC 41 (paridade, `ec-41-2003.md`) que a propria EC 103 indica (art. 4, par. 7, I);
   - demais: media de 100% desde 07/1994 (EC 103, art. 26), limitada ao teto do RGPS para quem entrou depois da complementar ou optou (par. 1); 60% + 2 pontos por ano acima de 20 (par. 2, I e II); 100% no pedagio de 100% (par. 3, I) e na incapacidade permanente decorrente de acidente do trabalho, doenca profissional ou do trabalho (par. 3, II, ressalvado no par. 2, II), conforme a causa provada; compulsoria pela formula do par. 4. O acrescimo acima de 15 anos do par. 5 e da mulher filiada ao RGPS, nao da servidora;
   - regra anterior a EC 103: o direito adquirido e calculado pela legislacao da data dos requisitos (EC 103, art. 3, par. 1); a media das maiores remuneracoes de 80% do periodo desde 07/1994 vale so para as aposentadorias que a Lei 10.887, art. 1, alcanca (o proprio art. 1 remete ao CF, art. 40, par. 3, e ao art. 2 da EC 41); transicoes da EC 41 (arts. 2 e 6) e da EC 47 (art. 3): revogadas pela EC 103, art. 35, III e IV; para o servidor federal, na publicacao (art. 36, III), ressalvado quem cumpriu os requisitos antes (art. 3); nos Estados, DF e Municipios, so quando lei do ente referendar a revogacao (art. 36, II). Ler a faixa da regra, conferir a data dos requisitos e, fora da Uniao, a existencia da lei local; sem ela, dizer que a regra depende da lei do ente, sem escolher a formula;
   - reajuste dos proventos sem paridade na data e indice do RGPS (Lei 10.887, art. 15; a fonte remete a ADI 4.582, nao capturada).
7. Pontos que mudam o caso: abono de permanencia igual a contribuicao para quem cumpre a voluntaria e fica (EC 103, arts. 8 e 10, par. 5); rol do RPPS limitado a aposentadorias e pensao, com incapacidade temporaria e salario-maternidade pagos pelo ente (art. 9, par. 2 e 3); vedada mais de uma aposentadoria pelo RPPS, salvo cargos acumulaveis (CF, art. 40, par. 6); acumulacao de pensao e aposentadoria pelo art. 24 da EC 103; contagem reciproca com compensacao financeira (CF, art. 201, par. 9) e vedacao de tempo ficticio (art. 40, par. 10); RPPS nao concede beneficio distinto do RGPS salvo a Constituicao (Lei 9.717, art. 5).
8. Especial do servidor: conversao ate a EC 103 pelas regras do RGPS; depois, pela lei complementar do ente (STF Tema 942; CF, art. 40, par. 4-C). Servidor federal com deficiencia: LC 142 com 10 anos de servico publico e 5 no cargo (EC 103, art. 22).
9. Pensao por morte do servidor (EC 103, art. 23): sem conta nesta versao; dizer isso.
10. [redacao] Propor 2-3 caminhos (pedir a aposentadoria na regra X, esperar a regra Y, pedir abono de permanencia, requerer averbacao ou CTC antes), cada um com ganho e risco; o advogado escolhe.
11. [redacao] Passada anti-IA com `context/escrita-humana.md` (secao 7) antes de entregar texto livre.

## Checklist de documentos
Certidao de tempo de contribuicao de cada regime anterior · ficha funcional com ingresso no servico publico e em cada cargo · historico de cargos e de magisterio · termo de opcao pela complementar, se houver · fichas financeiras desde 07/1994 · lei do RPPS do ente e lei da complementar do ente · laudos de atividade nociva ou avaliacao da deficiencia · ato de aposentadoria ou indeferimento, se ja houver.

## Calculo
Sem script na 2.0.3. Tempo, pontos, media e provento do servidor nao sao apurados pelo plugin: a tabela mostra exigido x informado pelo advogado, com o aviso "conta do advogado, nao conferida por script". Nunca usar os scripts do RGPS para o servidor.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na entrega. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Regime e ente, regras aplicaveis com os requisitos citados da lei seca, e o que falta conferir.
- Checklist de documentos marcado (tem ou falta) e os 2-3 caminhos com o escolhido.
- Gaps declarados: lei do ente, ADI 4.582, competencia do servidor estadual ou municipal (fora do recorte do CF, art. 109, `[VERIFICAR]`); servidor federal: Justica Federal (CF, art. 109, I).

## Guard
Nunca transportar regra do RGPS para o servidor sem ancora. Nunca pedagio de 50% para servidor. Nunca citar artigo de lei estadual ou municipal que nao esteja em context/. Nunca calcular provento. Nunca afirmar integralidade ou paridade sem conferir data de ingresso e opcao.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill rpps-servidor-publico - plugin previdenciario-adv-os v2.0.3`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
