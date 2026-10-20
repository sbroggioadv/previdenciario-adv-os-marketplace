# previdenciario-adv-os — regras internas do plugin

> Plugin de Direito Previdenciário brasileiro, versão **2.0.1**: 34 skills em 6 camadas, 9 comandos e 7 scripts de cálculo, sobre a EC 103/2019, as Leis 8.213/1991, 8.212/1991, 8.742/1993 e 10.259/2001, o Decreto 3.048/1999, a IN PRES/INSS 128/2022, a EC 113/2021, a EC 136/2025, o Manual de Cálculos da Justiça Federal de julho/2026 e a Resolução CJF 983/2026.
> **Advoga para o segurado, o dependente e o beneficiário contra o INSS** (polo ativo); o lado é preferência gravada no perfil do escritório, não trava.
> Despersonalizado (autoria IA Combativa; o escritório do cliente é configurado pelo `/start-previdenciario`, que grava `previdenciario/perfil.md`).
> **O núcleo comercial é a conta:** `calculos-previdenciarios` e `planejamento-previdenciario`, com os scripts por trás — qual regra vale mais, quando aposentar, quanto vai receber.
> Mapa completo, relógio e contrato de anti-alucinação: `context/metodologia-previdenciario.md` (lido primeiro, sempre).

## Invioláveis (anti-alucinação por design)

- **Nenhuma citação** de dispositivo, súmula, tema, resolução, índice ou prazo entra em peça sem âncora em `context/`. Guard permanente: `anti-alucinacao-previdenciario`; validação final: `validador-previdenciario` + `suprema-corte-previdenciaria` (R1–R4). Citação sem âncora sai como `[VERIFICAR]`, nunca como fato.
- **Grep o artigo e leia a faixa.** Nunca despejar o anexo inteiro, nunca citar de memória. Linha `(revogado) ~~…~~` é texto riscado na fonte: não é norma vigente. A citação **nomeia o diploma** — o mesmo número de artigo existe em vários (art. 3º, 17, 20, 26, 27-A, 42).
- **Lei vigente manda.** A captura em `context/lei/` supera o treino do modelo. Item marcado 🔴 no gate de vigência (`metodologia-previdenciario.md` §10) entra como "a confirmar" até ser reverificado.
- **Número crítico só por script ou conta aberta.** Carência, tempo, pontos, RMI, valor da causa, atrasados, RPV e prazo saem de `scripts/calc/` (exit 0) ou de `context/calculo-<x>.md`. Sem o dado, fórmula; nunca estimativa.
- **Hook é só aviso.** `hooks/hooks.json` tem um único `SessionStart` com um `echo` de uma linha. Nenhum hook chama Python, script ou arquivo; nenhum hook grava nada. Script de cálculo é chamado só pela skill, via Bash.
- **Dado de cliente fica no computador do advogado**, em `previdenciario/casos/<slug>.md`. CNIS e laudo médico são dado pessoal sensível: nunca vão para o plugin nem para ferramenta externa.

## VERDADES DURAS — nunca contrariar

1. **A revisão da vida toda é inviável.** O art. 3º da Lei 9.876/1999 é cogente e o segurado que se enquadra nele não pode optar pela regra definitiva do art. 29 da Lei 8.213, "independentemente de lhe ser mais favorável" (ADIs 2.110/2.111; STF Tema 1.102, tese nova de novembro/2025). O plugin antigo vendia a tese. **Ajuizar a tese hoje expõe o cliente a sucumbência, custas e perícia.** A modulação tem dois critérios, que não se confundem: são irrepetíveis os valores percebidos por decisões, definitivas ou provisórias, prolatadas até 05/04/2024; e, nas ações pendentes de conclusão nessa data, não se cobram sucumbência, custas e perícia; ficam mantidas as repetições e os pagamentos já feitos. O que se faz é defender o segurado contra cobrança indevida dentro desses critérios.
2. **Conversão de especial em comum só para o tempo trabalhado até 13/11/2019** (EC 103, art. 25, §2º; Decreto 3.048, art. 188-P, §5º), pela data do trabalho, não pela da filiação; vínculo que cruza a data é fatiado. Multiplicadores 2,00/2,33, 1,50/1,75 e 1,20/1,40 (mulher/homem; 15, 20 e 25 anos). **Converter um único dia posterior infla o tempo e arrisca o requisito e a RMI pedidos, abrindo flanco na contestação e na perícia contábil.**
3. **O PBC de 100% desde 07/1994 vem da EC 103, art. 26 — não da Lei 13.846/2019.** Coeficiente 60% + 2 pontos por ano acima de 20 (homem) ou 15 (mulher e especial de 15); 100% no pedágio de 100% e na incapacidade permanente acidentária; o pedágio de 50% é média × fator previdenciário (EC 103, arts. 17 e 26). **Marco ou coeficiente errado muda a RMI — para mais (risco de impugnação por excesso) ou para menos (diferença do cliente deixada para trás).**
4. **Divisor mínimo de 108** para o filiado até 07/1994, nas aposentadorias com fato gerador a partir de 05/05/2022, exceto a por incapacidade permanente, e o descarte não o elimina (Lei 8.213, art. 135-A; IN 128, art. 228). **Dividir pelo número real de salários superestima a média de quem tem poucos recolhimentos; a RMI só sobe quando essa média não cai no piso.**
5. **Atualização e juros contra o INSS são em fatias por competência:** até nov./2021, INPC (desde set./2006) e juros do Manual; de dez./2021 a ago./2025, Selic única (EC 113, art. 3º, redação original — STF Tema 1.419 restringe a esse período); desde set./2025, antes do requisitório, INPC + taxa legal com dedução do INPC (Manual CJF de julho/2026); no requisitório, Res. CJF 983/2026, art. 7º. O BPC segue o regime das condenações em geral. **"IPCA-E até 2021 e Selic depois" erra índice e juros em várias fatias e pode tanto expor a conta a impugnação por excesso quanto deixar diferença do cliente para trás.**
6. **A Selic contra a Fazenda vem da EC 113/2021 — "Lei 14.439/2022" não é a fonte.** **Fundamento atribuído à lei errada compromete a credibilidade da peça diante do juízo.**
7. **Carência depois da perda da qualidade:** a metade da carência do benefício, desde a nova filiação (6 nos benefícios por incapacidade; 12 no auxílio-reclusão), só reabre o cômputo das contribuições anteriores; a carência continua a integral do art. 25 (Lei 8.213 e Decreto 3.048, art. 27-A). Salário-maternidade fica fora: carência inconstitucional (ADI 2.110). Sem o histórico anterior, carência indeterminada. **Tratar a metade como carência cumprida expõe o pedido a indeferimento com fundamento correto do INSS.**
8. **Auxílio-acidente: sem carência, sem piso de um salário mínimo, inacumulável com aposentadoria** (Lei 8.213, arts. 26, I, e 86; Decreto 3.048, art. 42, parágrafo único). **Pedir piso ou cumulação com aposentadoria é pedido contra a letra da lei: expõe a peça à improcedência nesse ponto e tira credibilidade do restante.**
9. **BPC: renda per capita "igual ou inferior a 1/4" do salário mínimo, sem carência e sem abono anual** (LOAS, art. 20, §3º; Lei 8.213, art. 40); o 1/4 não é o único meio de prova (STF Tema 27; STJ Tema 185). **Somar abono infla o valor da causa e a alçada; tratar 1/4 como teto absoluto deixa de produzir a prova de miserabilidade que a jurisprudência admite.**
10. **RPV = 60 salários mínimos, conferido pelo valor atualizado até a transmissão ao tribunal**; acima, precatório, salvo renúncia expressa ao excedente para receber por RPV; fracionar é vedado (Lei 10.259, art. 17; Res. CJF 983/2026, arts. 3º, §4º, e 4º; CF, art. 100, §8º). Precatório apresentado até 1º de fevereiro é pago até o fim do exercício seguinte (CF, art. 100, §5º, EC 136). **Via errada pode exigir renúncia, cancelamento e nova requisição, e o precatório pode entrar no orçamento de um exercício posterior: o cliente espera mais.**
11. **Prazo recursal e o art. 60, §1º, não esperam.** Recurso ao CRPS em 30 dias da ciência (Decreto 3.048, art. 305, §1º, II); auxílio temporário requerido depois de 30 dias de afastamento começa na data do requerimento, salvo DII posterior (Lei 8.213, art. 60, §1º; IN 128, art. 336). **Por isso a primeira pergunta da triagem é sobre prazo: recurso fora do prazo depende de admissibilidade que não se pode prometer, e o requerimento tardio do auxílio temporário desloca a DIB para a DER, sem as parcelas anteriores a ela.**

## Divergências que o plugin DECLARA, não esconde

- **Abono anual nas 12 vincendas do valor da causa:** o plugin calcula as duas contas e usa como padrão incluir o abono (CPC, art. 292, §2º), declarado como interpretação, sem fingir pacificação. Nunca no BPC.
- **Salário mínimo de qual data na verificação da RPV:** a Res. CJF 983/2026 manda verificar pelo valor atualizado até a transmissão, mas não diz literalmente qual mínimo; o plugin usa o da data de transmissão como interpretação operacional declarada e exige as datas de conta, expedição e transmissão.
- **STF Tema 27 e a redação atual da LOAS:** a tese foi fixada sobre "inferior a 1/4"; a lei hoje diz "igual ou inferior". Aplicar a tese à redação nova é leitura, dita como tal.
- **INPC de set. a dez./2006:** o Manual CJF começa o INPC em set./2006; o STJ Tema 905 fala em "período posterior à vigência da Lei 11.430/2006" (publicada em 27/12/2006). O plugin segue o Manual e expõe a diferença.
- **Andamento não certificado:** os novos embargos no STF Tema 1.102 (opostos em 17/03/2026) estavam pendentes na captura; o andamento da ADI 7.873 (EC 136) não foi consultado. Nenhum dos dois é afirmado como julgado ou não julgado: reverificar antes de cada peça que dependa deles. Notícia não é decisão.
- **Precatório apresentado antes de set./2025 dentro do período de graça:** o texto da Res. CJF 983/2026 não concilia a Selic do art. 7º, §3º, II, com o §2º; o script devolve as duas contas.

## Gaps intransponíveis (não preencher por invenção)

- **Tábua de mortalidade do IBGE** não capturada e **fórmula do fator previdenciário** só em imagem na fonte: o fator sai como fórmula, com a lista de dados que faltam.
- **Anexo IV do Decreto 3.048 (ruído) em número:** não automatizar o limite; exigir a prova técnica (PPP amparado em laudo; LTCAT quando o PPP for insuficiente — IN 128, art. 281, §4º).
- **Lista vigente de doenças que dispensam carência** (Lei 8.213, art. 26, II): não conferida; a dispensa entra só quando o advogado marca.
- **Regulamento da ampliação do BPC até 1/2 salário mínimo** (LOAS, art. 20, §11-A): não conferido; nenhuma ampliação automática.
- **Lei 9.289/1996 (custas na Justiça Federal):** não capturada; não afirmar isenção nem cobrança do INSS na Justiça Federal.
- **Acumulação do auxílio-acidente com o auxílio temporário:** fechadas só a vedação com aposentadoria (Lei 8.213, art. 86) e a suspensão na reabertura pelo mesmo acidente (Decreto 3.048, art. 104, §6º); as demais combinações seguem indeterminadas.
- **Juros da poupança (maio/2012 a nov./2021)** e **taxa legal depois de maio/2026** sem tabela do CJF: fórmula.
- **RPPS e previdência complementar:** a LC 108/2001, a LC 109/2001 e a lei do RPPS só são citáveis se o texto estiver em `context/lei/` (conferir no `INDICE.md`). Sem o arquivo, **não citar artigo delas**: a skill faz checklist de documentos e de questões e declara o gap. Ancorados: CF, arts. 40 e 202; EC 103, arts. 4º, 10 e 20 para o servidor federal. Nenhum cálculo do servidor na 2.0.1.
- **Aposentadoria da pessoa com deficiência (LC 142/2013) e pensão por morte:** sem script; o dispositivo da duração da cota da pensão é conferido no anexo antes de citar.

## Porta única

`previdenciario-master` é o orquestrador. Lê `context/metodologia-previdenciario.md`, classifica pela `triagem-dogmatica-previdenciario` — **1ª pergunta sempre: há prazo correndo agora (recurso administrativo, resposta, recurso judicial) ou benefício cessado ou indeferido há menos de 30 dias? Se sim, entra por `prazos-previdenciarios` antes de tudo** —, confirma o quadro do caso em camadas, carrega `memoria-de-caso-previdenciario`, aplica a transversal (prazos, estratégia com 2–3 caminhos, cálculo pelos scripts), conduz a trilha das camadas C3 a C5, fecha pelo `validador-previdenciario` e pela `suprema-corte-previdenciaria` e grava o caso em `previdenciario/casos/<slug>.md`. Voz e forma do escritório por `estilo-juridico-previdenciario`, lendo o `perfil.md`; texto sem marca de IA por `context/escrita-humana.md`.

## Fronteiras (cross-link soft, NÃO duplicar)

Cálculo judicial genérico e auditoria de laudo → `calculosjudiciais-adv-os` · busca de jurisprudência ao vivo → `juris-adv-os` · reconhecimento de vínculo trabalhista para o CNIS → `trabalhista-adv-os`.

**OUT — gap declarado:** cálculo do RPPS; previdência complementar além do que estiver capturado em `context/lei/`; aposentadoria da pessoa com deficiência e pensão por morte sem script; ruído e fator previdenciário em número.
