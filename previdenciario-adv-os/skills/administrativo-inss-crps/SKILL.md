---
name: administrativo-inss-crps
description: "Via administrativa contra o INSS: requerimento de beneficio com carencia e qualidade de segurado conferidas pelo script antes do protocolo (no BPC nao se aplicam), reafirmacao da DER, beneficio mais vantajoso, novo requerimento, recurso ordinario as Juntas e recurso especial as Camaras do CRPS em 30 dias, contrarrazoes, novos elementos no recurso, defesa contra revisao de oficio e anulacao. Use quando o operador disser requerimento no INSS, Meu INSS, recurso ao CRPS, Junta de Recursos, Camara de Julgamento, indeferimento administrativo, revisao de oficio, defesa administrativa. Nao use para mandado de seguranca (mandado-seguranca-previdenciario) nem para acao judicial (peticao-inicial-previdenciaria)."
---

# ADMINISTRATIVO INSS CRPS

> Camada 4. Do requerimento ao recurso no CRPS, com a carencia conferida antes do protocolo nos beneficios previdenciarios (no BPC nao se aplica).

## Entradas
- Recebe: o que se pede ao INSS ou a decisao recebida, com a data da ciencia (obrigatorio) · CNIS e documentos do segurado (obrigatorio no beneficio previdenciario; no BPC, documentos da renda e do grupo familiar e, se for o caso, da deficiencia) · processo administrativo completo (opcional, pedir no recurso)
- Chamada por: previdenciario-master · analise-carta-concessao-indeferimento · bpc-loas-previdenciario | Chama: prazos-previdenciarios · analise-cnis · bpc-loas-previdenciario · mandado-seguranca-previdenciario · memoria-de-caso-previdenciario

## Anexos obrigatorios (context/)
- `context/lei/in-128-2022-inss.md` (arts. 576, 576-A, 577, 578, 579, 580, 582 e 583 - grep o artigo e leia a faixa)
- `context/lei/decreto-3048-1999.md` (art. 305 - grep o artigo e leia a faixa)
- `context/lei/regimento-crps-portaria-mps-125-2026.md` (arts. 77, 78, 80, 89 e 112)
- `context/lei/lei-8213-1991.md` (arts. 103, 103-A, 105 e 129-A - grep o artigo e leia a faixa)
- `context/calculo-cnis.md` (secao 5, CAMPOS)
- `context/metodologia-previdenciario.md` (secoes 4 e 9: prazo vencido e relogio)

## Objetivo
Levar o pedido ao INSS ou ao CRPS do jeito que mais preserva o direito e a data de inicio do cliente, sem prometer o que a via administrativa nao garante.

## Metodologia
1. [redacao] Devolver o quadro em 3-6 linhas (o que se pede ou o que foi decidido, especie, data da ciencia, documentos) e esperar confirmacao.
2. Prazo primeiro: recurso correndo ou decisao ha menos de 30 dias vai para `prazos-previdenciarios`. Prazo vencido: avisar antes de tudo. O INSS nao pode recusar o recebimento do recurso (IN 128, art. 578, par. 1), mas a admissibilidade e do CRPS: intempestividade leva ao nao conhecimento (Regimento CRPS, art. 112, I), e a relevacao so cabe com liquidez e certeza inequivocas (pars. 1o e 2o), sem diligencia (par. 8o). Examinar se o caso se encaixa, nunca prometer relevacao, e mostrar as outras vias.
3. Antes de requerer: no BPC, carencia e qualidade de segurado nao se aplicam (CF, art. 203, caput; LOAS, art. 20): nao rodar o script do CNIS nem barrar o pedido por falta de vinculo; conferir os requisitos assistenciais pela `bpc-loas-previdenciario`. Nos beneficios previdenciarios, rodar `calc_previdenciario_cnis.py` para carencia e qualidade de segurado. Exit 3 (carencia indeterminada) nao autoriza afirmar que o requisito esta cumprido; dizer o que falta provar. Lacunas do CNIS vao para `analise-cnis`.
4. Requerimento: documentacao incompleta nao e motivo para recusa (Lei 8.213, art. 105); juntar desde ja toda a prova, porque elemento novo apresentado so no recurso fixa os efeitos financeiros na data da apresentacao (IN 128, art. 582). Pedir que o INSS ofereca o beneficio mais vantajoso e reafirme a DER, com concordancia, se o requisito se completar antes da decisao (art. 577, I e II).
5. Arquivamento por falta de documento indispensavel: nao cabe recurso ao CRPS; novo requerimento produz efeitos da nova data (art. 578, par. 2 e 3). Por isso o requerimento completo vale mais que o recurso.
6. Novo requerimento da mesma especie: so depois da decisao do anterior e do decurso dos 30 dias do recurso ordinario (art. 576-A, redacao da IN 208/2026), salvo pedido de revisao e beneficio por incapacidade (paragrafo unico). Ler a faixa antes de orientar: redacao mudou duas vezes em 2026.
7. Recurso ordinario: das decisoes do INSS, as Juntas de Recursos do CRPS (art. 578). Recurso especial: das decisoes da Junta, as Camaras de Julgamento, ressalvadas as materias de alcada exclusiva das Juntas (art. 579; Regimento CRPS, art. 89, pars. 2o e 3o - ler a faixa). Prazo de 30 dias da ciencia da decisao (Decreto 3.048, art. 305, par. 1, II; IN 128, art. 580).
8. Contrarrazoes: 30 dias. Prazo fatal da intimacao da interposicao (IN 128, art. 580; Regimento CRPS, arts. 77, 78 e 80). O Decreto diz "da interposicao" (art. 305, par. 1, III): essa data vale so como meta interna preventiva, pela `prazos-previdenciarios`. Nunca tratar como vencida defesa ainda no prazo da intimacao; sem a data da intimacao, tempestividade indeterminada. No recurso ordinario, as razoes do indeferimento substituem as contrarrazoes do INSS (art. 580, par. 2); o INSS pode reformar a propria decisao (Decreto, art. 305, par. 3).
9. Revisao de oficio e anulacao: o direito do INSS de anular ato favoravel ao beneficiario decai em 10 anos da pratica, salvo ma-fe comprovada (Lei 8.213, art. 103-A); com efeitos patrimoniais continuos, conta da percepcao do primeiro pagamento (par. 1), e qualquer medida da autoridade que impugne a validade do ato ja e exercicio do direito de anular (par. 2). Na defesa, pedir a data do ato, a do primeiro pagamento e a da primeira medida de impugnacao, e conferir se ha acusacao de ma-fe. Revisao a pedido do segurado segue o art. 583 da IN e a decadencia do art. 103 da Lei 8.213, com o item 7 do gate de vigencia (ADI 6.096 nao capturada).
10. Demora do INSS sem decisao: avaliar `mandado-seguranca-previdenciario`; nao afirmar prazo legal de analise que nao esteja em context/.
11. Via judicial: a inicial de beneficio por incapacidade exige comprovante do indeferimento ou da nao prorrogacao (Lei 8.213, art. 129-A, II, a); guardar a decisao e o processo administrativo.
12. [redacao] Propor 2-3 caminhos (requerimento completo, recurso ao CRPS, novo requerimento, acao judicial), cada um com ganho e risco para a DIB do cliente; o advogado escolhe.
13. [redacao] Redigir a peca (requerimento, recurso ordinario, recurso especial, contrarrazoes ou defesa) em I. fatos, II. fundamentos com o diploma nomeado, III. pedido e documentos; voz do escritorio pelo `estilo-juridico-previdenciario`; passada anti-IA com `context/escrita-humana.md` (secao 7).

## Calculo
Achar e rodar o script pela secao 13 de `context/metodologia-previdenciario.md`; o bloco campos e o contrato da entrada JSON.
```flags
# script: calc_previdenciario_cnis.py
--entrada  arquivo  opcional  JSON de entrada (sem ela, entrada padrao)
--versao  nenhum  opcional  imprime a versao
```
```campos
# script: calc_previdenciario_cnis.py
beneficio  enum  obrigatorio  idade | tempo | especial | incapacidade | salario-maternidade | auxilio-reclusao | pensao | auxilio-acidente | bpc
data_referencia  data  obrigatorio  DER, DII ou data do obito
vinculos  lista  condicional  ao menos 1 vinculo, salvo beneficio = bpc (LOAS, art. 20)
vinculos[].origem  enum  obrigatorio  empregado | contribuinte-individual | facultativo | especial | domestico | avulso
vinculos[].inicio  data  obrigatorio  AAAA-MM-DD
vinculos[].fim  data  opcional  ausente = vinculo sem fim (vai para lacunas)
vinculos[].filiacao_domestica_comprovada  bool  nao  so origem domestico; true = filiacao comprovada
vinculos[].indicadores  lista de texto  opcional  siglas do Anexo V; padrao []
vinculos[].competencias  lista  obrigatorio  uma entrada por competencia
vinculos[].competencias[].mes  competencia  obrigatorio  AAAA-MM
vinculos[].competencias[].valor  decimal  opcional  salario de contribuicao
vinculos[].competencias[].recolhido_em  data  opcional  data do pagamento
vinculos[].competencias[].indicadores  lista de texto  opcional  siglas do Anexo V; padrao []
historico_anterior_informado  bool  obrigatorio  false leva a carencia apos a perda a indeterminada
desemprego_registrado  bool  opcional  padrao false
acidente_ou_doenca_dispensa  bool  opcional  padrao false; decisao do advogado
dias_sem_expediente_bancario  lista de data  opcional  ausente = feriados nacionais do motor de prazos
ano_implementacao_requisitos  inteiro  nao  ano das condicoes da tabela do art. 142
inscrito_ate_24_07_1991  bool  nao  art. 142; ausente = inferido dos vinculos
```
Exit 0: usar e mostrar a memoria. Exit 2: perguntar de novo o dado recusado. Exit 3: carencia indeterminada, `formula_aberta` com `[VERIFICAR]`. Sem Python, script ausente ou outro exit: conta aberta por `context/calculo-cnis.md`, passo a passo, avisando que o numero nao foi conferido por script.

## Se faltar anexo
Seguir com o que ha no context/ e avisar em uma linha o que faltou e o que isso limita na entrega. Nunca preencher o que faltou por suposicao.

## Entrega obrigatoria final
- Beneficio previdenciario: carencia e qualidade de segurado pelo script, com a memoria. BPC: registro de que carencia e qualidade nao se aplicam e quadro dos requisitos assistenciais da `bpc-loas-previdenciario`.
- A peca pedida (requerimento, recurso, contrarrazoes ou defesa) com a lista de documentos e o prazo contado.
- Os 2-3 caminhos e o escolhido.

## Guard
Nunca protocolar beneficio previdenciario sem conferir carencia e qualidade; nunca exigi-las no BPC. Nunca contar prazo de cabeca: vai para `prazos-previdenciarios`. Nunca prometer admissao de recurso fora do prazo. Nunca citar regimento do CRPS, enunciado do CRPS ou sumula administrativa que nao esteja em context/. Nunca deixar prova para o recurso quando ela ja existe no requerimento.

## Assinatura (fora da peca)
No rodape da resposta ao advogado, nunca dentro do documento:
`Entregue pela skill administrativo-inss-crps - plugin previdenciario-adv-os v2.0.0`.
Registrar a mesma linha no `previdenciario/casos/<slug>.md`.
