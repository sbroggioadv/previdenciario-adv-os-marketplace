---
name: analise-cnis
description: "Le o CNIS do segurado e devolve vinculos, competencias validas, carencia (com a regra da metade apos perda da qualidade), qualidade de segurado com data da perda, indicadores pelo Anexo V da Portaria DIRBEN/INSS 990/2022 e lacunas, rodando o script de CNIS. Use quando o advogado anexar o CNIS, perguntar se o cliente tem carencia ou qualidade de segurado, pedir leitura de indicador (IEAN, PREM-EXT, PEXT, familia PVIN-* e outros) ou antes de qualquer calculo de tempo, transicao ou RMI. Nao use para converter tempo especial (analise-ppp-ltcat-aposentadoria-especial) nem para calcular RMI (calculos-previdenciarios)."
---

# ANALISE DE CNIS

> Camada 3 (analise e prova). Primeira leitura de prova de quase todo caso: sem CNIS lido, nenhuma conta de tempo, carencia ou RMI sai.

## Entradas
- Recebe: CNIS completo do segurado (obrigatorio; PDF, imagem ou texto) · beneficio pretendido e data de referencia (DER, DII ou obito) (obrigatorio) · CTPS, guias, carnes (opcional)
- Chamada por: previdenciario-master · triagem-dogmatica-previdenciario · administrativo-inss-crps · planejamento-previdenciario · analise-carta-concessao-indeferimento | Chama: analise-ppp-ltcat-aposentadoria-especial (vinculo com IEAN ou atividade especial) · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/calculo-cnis.md` (secoes 1 a 7 - conta aberta, CAMPOS e caso CNIS-04)
- `context/lei/portaria-990-2022-anexo-v-indicadores-cnis.md` (grep pela SIGLA e leia a linha da tabela: tipo, grupo, descricao, esclarecimentos)
- `context/lei/lei-8213-1991.md` (arts. 15, 24, 25, 26, 27 e 27-A - grep o artigo e leia a faixa; descarte linhas `(revogado)`)
- `context/lei/decreto-3048-1999.md` (arts. 14 e 27-A - grep o artigo e leia a faixa)
- `context/lei/lei-8212-1991.md` (art. 30, II e par. 2o, I - vencimento)
- `context/lei/in-128-2022-inss.md` (arts. 208, 209 e 210 - atraso e competencia abaixo do minimo)
- `context/metodologia-previdenciario.md` (secoes 5, 7, 7.1, 8 e 13)

## Objetivo
Mapa do CNIS com carencia, qualidade de segurado e indicadores apurados pelo script (ou pela conta aberta, marcada como nao conferida), e a lista do que falta sanear antes de qualquer pedido.

## Metodologia
1. Dado sensivel: o CNIS fica no computador do advogado; nunca colar em ferramenta externa. Registrar no caso so o necessario.
2. Extrair identificacao minima (NIT, nascimento) e, por vinculo: origem (empregado, contribuinte individual, facultativo, especial, domestico, avulso), inicio, fim, competencias com salario de contribuicao, data de recolhimento (CI, especial e facultativo) e siglas de indicador do vinculo e da competencia. Nada inventado: campo ilegivel vira lacuna.
3. Confirmar com o advogado, em 3 a 6 linhas, o beneficio pretendido, a data de referencia e se o CNIS traz todo o historico anterior a eventual perda da qualidade. "Nao sei" = lacuna, nunca presuncao.
4. Indicadores: cada sigla e procurada no Anexo V e sai com descricao e tipo oficiais (`CsPendencia` = pendencia; `CsIndicador` = alerta; `CsAcerto` = acerto). Sigla nao localizada sai como "sigla nao localizada no Anexo V", nunca com descricao de memoria.
   - IEAN = exposicao a agente nocivo informada pelo empregador, passivel de comprovacao. Indica possivel enquadramento especial; nao converte tempo sozinho e nao dispensa PPP amparado em laudo (verdade 11). Sufixos 15/20/25 do IEAN nao tem ancora: nao automatizar. Vinculo com IEAN -> analise-ppp-ltcat-aposentadoria-especial.
   - Indicador de pendencia (`CsPendencia`): o efeito sobre a carencia sai dos esclarecimentos da propria sigla no Anexo V, nunca so do tipo. Efeito nao demonstrado: registrar a pendencia, listar o saneamento e marcar a carencia afetada como `indeterminada` com `[VERIFICAR]`. O script exclui por tipo (`context/calculo-cnis.md`, secao 1.1): havendo pendencia, conferir a saida dele contra o esclarecimento da sigla.
5. Carencia: exigida pelo art. 25 ou dispensa pelo art. 26 da Lei 8.213 (doenca da lista so quando o advogado marcar). Salario-maternidade sem carencia (ADI 2.110); BPC sem carencia. Atraso de CI, especial e facultativo: conta so a partir do primeiro pagamento sem atraso (art. 27, II). Nunca usar a regra do atraso para TEMPO (IN 128, art. 208) como se fosse de carencia.
6. Perda da qualidade antes da data de referencia: aplicar o art. 27-A (Lei 8.213 e Decreto 3.048, que tem redacao propria: citar o diploma). A metade so reabre o computo das anteriores; a carencia total continua a do art. 25. Sem historico anterior: `indeterminada`. Aposentadorias do art. 25, II: regra da perda nao esta no corpus -> `indeterminada` com `[VERIFICAR]`.
7. Qualidade de segurado. Antes da conta, perguntar se houve beneficio em manutencao (exceto auxilio-acidente), segregacao compulsoria, reclusao ou servico militar (Lei 8.213, art. 15, I, III, IV e V). Havendo qualquer um, a qualidade se mantem pela regra do inciso proprio e o script nao representa esses fatos: nao usar a `data_perda` dele; declarar a qualidade como `indeterminada` pela conta automatica e conferir a mao pelo inciso. Sem essas hipoteses: graca de 12 meses; +12 com MAIS de 120 contribuicoes sem perda na primeira aquisicao (ai exatamente 120 nao estende); se a prorrogacao ja foi adquirida em bloco anterior e a qualidade se perdeu, bastam 120 NOVAS (IN 128, art. 184, par. 4o, segunda parte; campo `prorrogacao_reaquisicao`); +12 com desemprego registrado; 6 para o facultativo; vencimento no dia 15 do mes seguinte a competencia posterior ao fim da graca (dia util seguinte se nao houver expediente bancario); perda no dia seguinte. Feriado local nao e considerado sem calendario do caso.
8. Concomitancia: dia sobreposto conta uma vez para tempo; soma de salarios e assunto do salario de beneficio (Lei 8.213, art. 32), nao desta skill.
9. Rodar o script (secao Calculo) e mostrar a memoria. Exit 3: entregar a formula aberta com `[VERIFICAR]`.
10. Omissoes a sinalizar: CNIS desatualizado; vinculo conhecido pelo cliente e ausente (reconhecimento de vinculo -> fronteira `trabalhista-adv-os`); periodo rural nao registrado; competencia sem salario; competencia abaixo do minimo (listada em `excluidas`, nunca presumida). Tempo rural: so com dispositivo conferido no anexo; sem ele, lacuna.
11. Gravar o resultado pela memoria-de-caso-previdenciario.

## Calculo
Script `calc_previdenciario_cnis.py`, localizado e rodado conforme `context/metodologia-previdenciario.md` (secao 13). Entrada em JSON.

```flags
--entrada   arquivo   opcional   caminho do JSON de entrada; ausente = stdin
--versao    flag      opcional   imprime a versao (2.0.2)
```

```campos
beneficio                                   enum           sim   idade,tempo,especial,incapacidade,salario-maternidade,auxilio-reclusao,pensao,auxilio-acidente,bpc
data_referencia                             data           sim   DER, DII ou data do obito
vinculos                                    lista          condicional   ao menos 1 vinculo, salvo beneficio = bpc (LOAS, art. 20)
vinculos[].origem                           enum           sim   empregado,contribuinte-individual,facultativo,especial,domestico,avulso
vinculos[].inicio                           data           sim   -
vinculos[].fim                              data           nao   ausente = vinculo sem fim (vai para lacunas)
vinculos[].filiacao_domestica_comprovada  bool  nao  so origem domestico; true = filiacao comprovada
vinculos[].indicadores                      lista[texto]   nao   siglas do Anexo V; padrao []
vinculos[].competencias                     lista          sim   uma entrada por competencia
vinculos[].competencias[].mes               competencia    sim   -
vinculos[].competencias[].valor             decimal        nao   salario de contribuicao
vinculos[].competencias[].recolhido_em      data           nao   data do pagamento (atraso de CI, especial, facultativo)
vinculos[].competencias[].indicadores       lista[texto]   nao   siglas do Anexo V; padrao []
historico_anterior_informado                bool           sim   false leva a carencia apos a perda a indeterminada
desemprego_registrado                       bool           nao   padrao false
acidente_ou_doenca_dispensa                 bool           nao   padrao false; decisao do advogado
dias_sem_expediente_bancario                lista[data]    nao   ausente = feriados nacionais do motor de prazos, com alerta
ano_implementacao_requisitos  inteiro  nao  ano das condicoes da tabela do art. 142
inscrito_ate_24_07_1991  bool  nao  art. 142; ausente = inferido dos vinculos
```

Exit 0: usar o resultado e mostrar a memoria. Exit 2: perguntar de novo o dado errado. Exit 3: formula aberta com `[VERIFICAR]`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-cnis.md`, passo a passo, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita (ex.: sem o Anexo V, indicadores saem sem descricao). Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Tabela de vinculos (origem, inicio, fim, competencias validas, indicadores, pendencias).
- Carencia: exigidas, contadas, cumprida (sim / nao / indeterminada), excluidas com motivo; apos perda, novas, metade e anteriores reaproveitadas.
- Qualidade de segurado: ultima competencia, graca, vencimento, data da perda.
- Indicadores com descricao oficial e acao de saneamento; lacunas; proximo passo (ppp, calculos-previdenciarios ou planejamento-previdenciario).
- Memoria do script ou a marca "conta nao conferida por script".

## Guard
- Nunca IEAN como "empresa nao identificada"; nunca sigla que nao conste do Anexo V (as erradas da 0.1.0 estao na secao 7 da metodologia).
- Nunca tratar a metade do art. 27-A como carencia cumprida; nunca presumir historico anterior.
- Nunca carencia de pensao (independe) nem de salario-maternidade.
- Nunca numero de carencia, graca ou data de perda de cabeca: script ou conta aberta.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill analise-cnis - plugin previdenciario-adv-os v2.0.2`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
