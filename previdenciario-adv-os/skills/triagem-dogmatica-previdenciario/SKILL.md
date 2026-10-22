---
name: triagem-dogmatica-previdenciario
description: "Triagem do caso previdenciario: faz primeiro a pergunta critica do prazo, classifica fase, objetivo, beneficio e skill alvo, conduz a elicitacao em camadas (1 a 3 perguntas por turno, botoes nas listas fechadas), le o CNIS resumido e sinaliza os institutos que mudam o caso (prazo, DIB, decadencia, prescricao, carencia, qualidade de segurado, direito adquirido, conversao do especial, fatias de juros). Use quando o previdenciario-master classificar uma demanda, ou quando o advogado disser triagem, por onde comeco, qual skill uso, que caso e esse. Nao redige peca nem calcula RMI: devolve a classificacao e a trilha ao master."
---

# TRIAGEM-DOGMATICA-PREVIDENCIARIO

> Camada 0. Classifica o caso e monta o quadro antes de qualquer producao. A elicitacao completa mora aqui e no master; as demais skills so confirmam o quadro recebido.

## Entradas
- Recebe: a fala do advogado (obrigatorio) · documentos enviados, sobretudo o CNIS (opcional) · `previdenciario/perfil.md` e `previdenciario/casos/<slug>.md` (se existirem).
- Chamada por: previdenciario-master | Chama: nenhuma (devolve a skill alvo ao master)

## Anexos obrigatorios (context/)
- `context/metodologia-previdenciario.md` (secao 4 arvore de triagem; 6 regras de distincao; 9 relogio - grep a secao e leia a faixa).
- `context/calculo-cnis.md` (secoes 1 a 3 e 5 - carencia, qualidade, indicadores, CAMPOS).
- `context/lei/portaria-990-2022-anexo-v-indicadores-cnis.md` (grep pela sigla do indicador; nunca o arquivo inteiro).

## Objetivo
Devolver ao master, sem palpite: fase, objetivo, beneficio, skill alvo, prazo, institutos sinalizados, bloqueios e lacunas.

> **Escolhas = botoes:** nas listas fechadas (tipo de trabalho, prazo sim/nao/nao sei, beneficio, fase, via, confirmacao do quadro) use a ferramenta **AskUserQuestion** com botoes clicaveis (max. 4 opcoes por pergunta; mais que isso, divida em 2 perguntas). Datas, valores, relato e numeros seguem digitados.

## Metodologia
1. **Camada 0 - leitura silenciosa.** Ler `perfil.md`, `casos/<slug>.md`, os documentos e a fala inicial. Marcar o que ja esta respondido; nao perguntar de novo.
2. **Camada 1 - pergunta critica, sempre primeiro:** "Ha prazo correndo agora (recurso administrativo, resposta, recurso judicial) ou beneficio cessado ou indeferido ha menos de 30 dias?" Botoes: [Sim] [Nao] [Nao sei].
   - Sim -> skill alvo imediata `prazos-previdenciarios`; pedir a data da ciencia.
   - Prazo vencido -> avisar na hora, antes de qualquer outra pergunta, e seguir a metodologia secao 4 (sem prometer relevacao).
   - Nao sei -> tratar como prazo possivel ate ver a data.
3. **Camada 1 - tipo de trabalho:** requerimento, recurso administrativo, acao, processo em curso, parecer, calculo, planejamento (botoes em 2 rodadas se preciso).
4. **Camada 2 - estrategia:** objetivo do cliente, beneficio, restricao central. Ate 3 perguntas.
5. **Camada 3 - tatica (so o que a trilha exige),** em 2 ou 3 turnos: datas (filiacao, DER, DIB, DII, DCB, ciencia), vinculos e periodos, atividade especial, laudo, grupo familiar e renda (BPC), processo e fase. "Nao sei" vira lacuna declarada e a conversa segue.
6. **Camada 4 - risco, so com sinal:** decadencia perto, prova fraca, tese com selo 🔴 ou ❌ em `context/lei/temas-sumulas-prev.md`, dado sensivel pedido sem necessidade.
7. **CNIS resumido:** listar vinculos, origem, inicio e fim, ultima competencia, indicadores (sigla conferida no Anexo V; sigla que nao consta = "nao localizada", nunca traduzida de cabeca). Se carencia ou qualidade de segurado decidem o caso, rodar o script (secao Calculo) ou mandar para `analise-cnis` quando o CNIS for longo ou confuso.
8. **Sinalizar institutos** (so os pertinentes, com o anexo; sem lista de principios decorativa):
   - prazo do recurso ao CRPS e DIB do art. 60, par. 1 (`context/lei/lei-8213-1991.md`; `context/lei/decreto-3048-1999.md`, art. 305);
   - decadencia da revisao e prescricao das parcelas (`lei-8213-1991.md`, art. 103 e paragrafo unico; item 7 do gate de vigencia na metodologia secao 10);
   - direito adquirido ate 13/11/2019 e qual regra de transicao comparar (`context/lei/ec-103-2019.md`, art. 3 e arts. 15 a 21);
   - conversao de especial so do tempo trabalhado ate 13/11/2019 (`ec-103-2019.md`, art. 25, par. 2);
   - carencia apos a perda da qualidade (art. 27-A da Lei 8.213 e do Decreto 3.048: homonimos, nomear o diploma);
   - natureza do beneficio para atualizacao (previdenciario x assistencial) e fatias de juros (metodologia secoes 5 e 6);
   - nexo com o trabalho (acidentario) e competencia: JEF ate 60 salarios minimos (`context/lei/lei-10259-2001-jef.md`, art. 3); a acao acidentaria fica fora da Justica Federal e vai a Justica Estadual (CF, art. 109, I, em `context/lei/cf88-art109-competencia.md`).
9. **Bloqueios automaticos:** prazo vencido; decadencia aparentemente consumada (avisar e sugerir alternativa, sem decidir pelo advogado); pedido que contraria verdade dura (metodologia secao 5); tema ou sumula fora do anexo.
10. **Devolver o resultado** (formato abaixo) e o quadro do caso para o master confirmar com o advogado.

## Calculo
So quando carencia ou qualidade de segurado decidem a triagem. Rodar `calc_previdenciario_cnis.py` conforme `context/metodologia-previdenciario.md` secao 13 (pasta base -> `scripts/calc/` -> busca pelo nome -> `--versao` 2.0.3). Entrada em JSON por `--entrada <arquivo>` ou pela entrada padrao. Bloco `campos`: uma linha por campo, colunas separadas por 2+ espacos: nome · tipo (`lista<sub>` quando a lista tem tipo) · obrigatorio|opcional · valores do enum separados por `|`, ou `min=N`, ou `padrao=<valor>`.
```flags
--entrada  path  opcional
--versao   bool  opcional
```
```campos
beneficio  enum  obrigatorio  idade|tempo|especial|incapacidade|salario-maternidade|auxilio-reclusao|pensao|auxilio-acidente|bpc
data_referencia  data  obrigatorio
vinculos  lista  condicional  min=1, salvo beneficio=bpc
vinculos[].origem  enum  obrigatorio  empregado|contribuinte-individual|facultativo|especial|domestico|avulso
vinculos[].inicio  data  obrigatorio
vinculos[].fim  data  opcional
vinculos[].filiacao_domestica_comprovada  bool  nao  so origem domestico; true = filiacao comprovada
vinculos[].indicadores  lista<texto>  opcional  padrao=[]
vinculos[].competencias  lista  obrigatorio
vinculos[].competencias[].mes  competencia  obrigatorio
vinculos[].competencias[].valor  decimal  opcional
vinculos[].competencias[].recolhido_em  data  opcional
vinculos[].competencias[].indicadores  lista<texto>  opcional  padrao=[]
historico_anterior_informado  bool  obrigatorio
desemprego_registrado  bool  opcional  padrao=false
acidente_ou_doenca_dispensa  bool  opcional  padrao=false
dias_sem_expediente_bancario  lista<data>  opcional  padrao=feriados-nacionais-com-alerta
ano_implementacao_requisitos  inteiro  nao  ano das condicoes da tabela do art. 142
inscrito_ate_24_07_1991  bool  nao  art. 142; ausente = inferido dos vinculos
```
Exit 0: usar `carencia`, `qualidade_segurado` e `lacunas`, mostrando a memoria. Exit 2: perguntar de novo o dado errado. Exit 3 (carencia indeterminada), sem Python ou script ausente: conta aberta por `context/calculo-cnis.md`, avisando que o numero nao foi conferido por script. `acidente_ou_doenca_dispensa` e decisao do advogado, nunca da triagem. Dados de exemplo sao sempre inventados.

## Resultado da triagem (formato)
| Campo | Valor |
|---|---|
| Prazo | sim (data) / nao / nao sei / vencido |
| Fase | administrativa (requerimento, JR, CRPS) / judicial (JEF, Vara, TRF, superiores, cumprimento) / consultiva |
| Objetivo e beneficio | ... |
| Skill alvo e ordem | ex.: prazos-previdenciarios -> analise-carta-concessao-indeferimento -> administrativo-inss-crps |
| Institutos sinalizados | so os pertinentes, cada um com o anexo |
| Bloqueios | ... |
| Lacunas declaradas | ... |
| Dado sensivel | CNIS e laudo ficam so no computador do advogado |

## Se faltar anexo
Seguir com o que ha em `context/` e avisar em uma linha o que faltou e o que isso limita. Sigla, artigo ou tema que dependeria do anexo ausente sai como `[VERIFICAR]`, nunca de memoria.

## Entrega obrigatoria final
- Tabela "Resultado da triagem" + quadro do caso preenchido para o master confirmar + perguntas pendentes (no maximo 3).

## Guard
Nunca classificar sem a pergunta critica. Nunca preencher data, vinculo ou valor por suposicao. Nunca citar tema, sumula ou principio sem ancora em `context/`. Nao despejar lista de principios que nao mudam o caso.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill triagem-dogmatica-previdenciario - plugin previdenciario-adv-os v2.0.3`
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
