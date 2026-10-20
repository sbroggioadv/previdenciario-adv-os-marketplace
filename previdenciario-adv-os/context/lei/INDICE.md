# Índice da lei seca do previdenciário v2 — tema → diploma → artigos

> **Para que serve.** É o mapa que o agente revisor (`audit/agentes/revisor-previdenciario.md`) e as skills usam para achar o texto da lei sem lembrar de cabeça. Cada linha aponta o arquivo deste diretório e o dispositivo. O texto que vale é o do arquivo, não o desta tabela.
>
> **Regra de leitura.** Linha que começa com `(revogado) ~~…~~` é texto riscado na fonte: não é norma vigente. Num `grep` por "Art. N", ignore as linhas `(revogado)` e leia a outra. Homônimos: o mesmo número de artigo existe em vários diplomas (art. 27-A na Lei 8.213 e no Decreto 3.048; art. 3º na Lei 9.876 e na EC 113); confira sempre o arquivo.
>
> **Conferência.** As âncoras de artigo desta tabela são checadas por `audit/scripts/conferir_ancoras_indice.py` (existe linha vigente "Art. N" no arquivo citado). A amostragem do texto contra a fonte está em `docs/P2-relatorio.md`.
>
> Capturado em 2026-10-14; ampliado na correção P3 (mesmo dia: Manual CJF 2026, Res. CJF 983/2026, tabela do art. 188-P §5º em texto, Portaria do teto de 2026, CC e CPC art. 43, Decreto 10.695/2021, STF Tema 1.419). Selos: ✅ capturado e conferido; 🔴 não capturado ou capturado em parte (motivo dito).

## 1. Arquivos

| Arquivo | Diploma | Fonte | Situação |
|---|---|---|---|
| `cf88-seguridade.md` | CF/1988: arts. 40, 100, 194 a 204; ADCT arts. 97, 101 a 105 e 107-A | Planalto (compilada) | ✅ recorte |
| `ec-103-2019.md` | EC 103/2019 | Planalto | ✅ integral |
| `ec-113-2021.md` | EC 113/2021 | Planalto | ✅ integral; a redação original do art. 3º aparece riscada porque a EC 136 a substituiu (ver nota no cabeçalho do arquivo) |
| `ec-136-2025.md` | EC 136/2025 | Planalto | ✅ integral |
| `provimento-cnj-207-2025.md` | Provimento CNJ 207/2025 (requisitórios após a EC 136/2025) | CNJ (atos.cnj.jus.br; captura do plugin de cálculos, mesma URL, data e sha256) | ✅ integral |
| `lei-8213-1991.md` | Lei 8.213/1991 (Planos de Benefícios) | Planalto (compilada) | ✅ integral (a página termina no art. 156; o Anexo do fator previdenciário está na Lei 9.876) |
| `lei-8212-1991.md` | Lei 8.212/1991 (Custeio) | Planalto (compilada) | ✅ integral |
| `decreto-3048-1999.md` | Decreto 3.048/1999 (RPS) | Planalto (compilado) | ✅ integral, com os Anexos I a V em texto; a tabela do art. 188-P §5º é imagem no Planalto: o texto dela está em `decreto-3048-art188p-tabela.md` |
| `decreto-3048-art188p-tabela.md` | Decreto 3.048/1999, art. 188-P, §§5º e 6º (multiplicadores 15/20/25 × M/H) | Compilação oficial do Ministério da Previdência (PDF, p. 449) | ✅ recorte em texto |
| `lei-8742-1993-loas.md` | Lei 8.742/1993 (LOAS) | Planalto (compilada) | ✅ integral |
| `lei-10259-2001-jef.md` | Lei 10.259/2001 (JEF) | Planalto | ✅ integral |
| `lei-9876-1999.md` | Lei 9.876/1999 | Planalto | ✅ integral; no Anexo (fator previdenciário) as variáveis estão em texto, mas a **fórmula é imagem** na fonte (🔴) |
| `lei-11960-2009.md` | Lei 11.960/2009 | Planalto | ✅ integral (vigência na publicação, art. 9º; a página registra o DOU de 30/06/2009) |
| `lei-11430-2006.md` | Lei 11.430/2006 | Planalto | ✅ integral (vigência na publicação, art. 6º; a página registra o DOU de 27/12/2006) |
| `lei-13846-2019.md` | Lei 13.846/2019 | Planalto | ✅ integral |
| `lei-14331-2022.md` | Lei 14.331/2022 (inclui o art. 135-A da Lei 8.213) | Planalto | ✅ integral |
| `lei-9494-1997.md` | Lei 9.494/1997 (art. 1º-F) | Planalto | ✅ integral |
| `cpc-excertos-prev.md` | CPC: arts. 43, 292, 534 e 535 | Planalto | ✅ recorte |
| `cc-excertos-prev.md` | Código Civil: arts. 132, 389 e 406 (taxa legal, Lei 14.905/2024) | Planalto (compilada) | ✅ recorte |
| `lei-662-1949-feriados.md` | Lei 662/1949 (feriados nacionais), art. 1º na redação da Lei 10.607/2002 | Planalto | ✅ integral |
| `decreto-10695-2021-abono.md` | Decreto 10.695/2021 (abono anual de 2021 em maio e junho) | Planalto | ✅ integral |
| `decreto-10999-2022-abono.md` | Decreto 10.999/2022 (abono anual de 2022 em abril e maio) | Planalto | ✅ integral (captura de 2026-10-15, W3-integ) |
| `decreto-11517-2023-abono.md` | Decreto 11.517/2023 (abono anual de 2023 em maio e junho) | Planalto | ✅ integral (captura de 2026-10-15, W3-integ) |
| `decreto-11947-2024-abono.md` | Decreto 11.947/2024 (abono anual de 2024 em abril e maio) | Planalto | ✅ integral (captura de 2026-10-15, W3-integ) |
| `decreto-12425-2025-abono.md` | Decreto 12.425/2025 (abono anual de 2025 em abril e maio) | Planalto | ✅ integral (captura de 2026-10-15) |
| `decreto-12884-2026-abono.md` | Decreto 12.884/2026 (abono anual de 2026 em abril e maio) | Planalto | ✅ integral (captura de 2026-10-15) |
| `portaria-interministerial-mps-mf-13-2026.md` | Portaria Interministerial MPS/MF 13/2026: reajuste, piso R$ 1.621,00 e teto R$ 8.475,55 em 2026 | DOU (in.gov.br) | ✅ integral |
| `portaria-interministerial-mps-mf-6-2025.md` | Portaria Interministerial MPS/MF 6/2025: reajuste, piso R$ 1.518,00 e teto R$ 8.157,41 em 2025 (revogada pela Portaria 13/2026, art. 13; rege os fatos geradores de 2025) | DOU (in.gov.br); art. 2º conferido também no PDF do gov.br/previdencia | ✅ integral (capturada em 15/10/2026, lane W1-golden) |
| `decreto-12797-2025-salario-minimo.md` | Salário mínimo de 2026 (R$ 1.621,00) | Planalto | ✅ integral |
| `decreto-12342-2024-salario-minimo.md` | Salário mínimo de 2025 (R$ 1.518,00) | Planalto | ✅ integral |
| `serie-salario-minimo-1994-2026.md` | Série do salário mínimo, uma linha por vigência, 09/1994 a 2026 (36 vigências): valor, diário, horário, norma, URL, sha256 e trecho literal do artigo | Planalto (cada lei, MP ou decreto); conferência Ipeadata (mensal) e TRT-MG | ✅ 36 vigências, 0 divergência (W1-data, 2026-10-15); 🔴 07–08/1994 (R$ 64,79) sem texto primário: fica em lacuna |
| `serie-teto-rgps-1994-2026.md` | Série do teto e do piso do RGPS, uma linha por vigência, 07/1994 a 2026 (46 vigências): portarias anuais, EC 20/1998 art. 14 e EC 41/2003 art. 5º, com trecho literal | DOU (in.gov.br e fac-símile), Planalto, ANTTlegis; 1996 só LegisWeb (secundária); conferência AEPS 2017 (mensal até 2017) e INSS (2012–2021) | ✅; em 31/12/2003–31/01/2004 e 01–02/2011 ato × AEPS divergem: desde a 2.0.1 vale o ato (R$ 2.400,00 e R$ 3.691,74), com a divergência registrada |
| `serie-reajustes-rgps-1995-2026.md` | Série dos reajustes dos benefícios do RGPS, uma seção por vigência, 06/2002 a 01/2024 (23 vigências): integral, Anexo I pro rata pela DIB e incorporação do teto, com norma, URL, sha256 e trecho literal; 2025 e 2026 nas portarias próprias | DOU: fac-símile oficial (pesquisa.in.gov.br) de 2002 a 2018 e in.gov.br de 2019 a 2024 | ✅ 23 vigências, 8 anos conferidos na página oficial (W3-reajustes, 2026-10-19); 1997–2001 e 01/08/2006 fechados na 2.0.1 (arquivos `portaria-*-reajuste.md`); 🔴 05/1995 e 05/1996 ficam em lacuna (fac-símile só em imagem, sem texto) |
| `in-128-2022-inss.md` | IN PRES/INSS 128/2022, texto compilado (atualizada até a IN 212, de 06/08/2026, segundo a própria fonte) | Portal IN do INSS | ✅ integral, arts. 1 a 674 sem lacuna de numeração; 🔴 os **anexos** da IN não estão aqui (o portal os publica em páginas próprias) |
| `portaria-990-2022-anexo-v-indicadores-cnis.md` | Portaria DIRBEN/INSS 990/2022, Anexo V (indicadores do CNIS), alterado pela Portaria 1.316/2025 | Portal IN do INSS (PDF) | ✅ integral |
| `temas-sumulas-prev.md` | Teses literais de STF, STJ, TNU e SV 47 | portais oficiais | ✅ itens listados no arquivo |
| `manual-cjf-2026-calculos-prev.md` | Manual de Cálculos da Justiça Federal, **edição julho de 2026** (Res. CJF 990/2026): cap. 4.1 a 4.3 e cap. 5 | CJF (PDF) | ✅ recorte com página impressa; **vigente** |
| `manual-cjf-calculos-prev.md` | Manual de Cálculos da Justiça Federal, edição 2025 (15/08/2025): cap. 4.1 a 4.3 e cap. 5 | CJF (PDF) | ✅ recorte com página impressa; **edição superada em 07/2026, mantida para períodos históricos** |
| `res-cjf-983-2026.md` | Resolução CJF 983/2026 (requisições de pagamento; revoga a Res. 822/2023) | CJF (PDF) | ✅ integral |
| `mp-316-2006.md` | Medida Provisória 316/2006 (convertida na Lei 11.430/2006) | Planalto | ✅ integral (P5). A página inteira vem riscada porque a MP foi convertida: todas as linhas aparecem como `(revogado)`. O texto vivo é o da lei de conversão (`lei-11430-2006.md`) |
| `mp-404-2007.md` | Medida Provisória 404, de 11/12/2007 (convertida na Lei 11.665/2008): redação do art. 41-A, §§2º a 4º, da Lei 8.213 (antecipação do pagamento de quem recebe até um mínimo) | Planalto | ✅ integral (2.0.1). A página inteira vem riscada porque a MP foi convertida; o art. 2º (vigência na publicação) e o cabeçalho datam a MP: DOU de 12/12/2007. Âncora de artigo no texto vivo: `lei-11665-2008.md` |
| `lei-11665-2008.md` | Lei 11.665/2008 (conversão da MP 404/2007) | Planalto | ✅ integral (2.0.1) |
| `portaria-mpas-3971-1997-reajuste.md` | Portaria MPAS 3.971/1997 — reajuste de 01/06/1997 (7,76%) e Anexo pro rata | Datalegis da ANTT (base federal; a página avisa que não substitui o DOU) | ✅ integral (2.0.1) |
| `portaria-mpas-4478-1998-reajuste.md` | Portaria MPAS 4.478/1998 — reajuste de 01/06/1998 (4,81%) e Anexo pro rata | Datalegis da ANTT | ✅ integral (2.0.1) |
| `portaria-mpas-5188-1999-reajuste.md` | Portaria MPAS 5.188/1999 — mínimo de 05/1999 e reajuste de 01/06/1999 (4,61%, art. 5º) com Anexo III pro rata | Datalegis da ANTT | ✅ integral (2.0.1) |
| `portaria-mpas-6211-2000-reajuste.md` | Portaria MPAS 6.211/2000 — reajuste de 01/06/2000 (5,81%) e Anexo I pro rata | Datalegis da ANTT | ✅ integral (2.0.1) |
| `portaria-mpas-1987-2001-reajuste.md` | Portaria MPAS 1.987/2001 — reajuste de 01/06/2001 (7,66%) e Anexo I pro rata | Datalegis da ANTT | ✅ integral (2.0.1) |
| `portaria-mps-342-2006-reajuste.md` | Portaria MPS 342/2006 — reajuste de 01/08/2006 (5,01% sobre a renda de março/2006, substituindo os 5,00% de abril) e Anexo I pro rata | Datalegis da ANTT | ✅ integral (2.0.1) |
| `dl-2322-1987.md` | Decreto-Lei 2.322/1987 | Planalto | ✅ integral (P5) |
| `lei-9717-1998-rpps.md` | Lei 9.717/1998 (regras gerais dos RPPS) | Planalto (compilada) | ✅ integral (P5) |
| `lei-10887-2004.md` | Lei 10.887/2004 (cálculo dos proventos e contribuição do servidor) | Planalto (compilada) | ✅ integral (P5) |
| `lc-108-2001.md` | LC 108/2001 (complementar patrocinada por entes públicos) | Planalto | ✅ integral (P5); a página não tem versão "compilado" separada |
| `lc-109-2001.md` | LC 109/2001 (Regime de Previdência Complementar) | Planalto | ✅ integral (P5); a página não tem versão "compilado" separada |
| `lc-142-2013-pcd.md` | LC 142/2013 (aposentadoria da pessoa com deficiência no RGPS) | Planalto | ✅ integral (P5) |
| `ec-41-2003.md` | EC 41/2003 | Planalto | ✅ integral (P7); usado pelo art. 7º (paridade), ao qual remetem a EC 103, art. 4º, §7º, I, e art. 20, §3º, I |
| `ec-47-2005.md` | EC 47/2005 | Planalto | ✅ integral (P8, achado A05 da revisão r5); usado pelo art. 3º (transição do servidor com ingresso até 16/12/1998). A página não risca o art. 3º, mas a EC 103, art. 35, IV, o revoga (União na publicação; demais entes com lei que referende: art. 36, II e III) |
| `ldo-2025-lei-15080-2024.md` | Lei 15.080/2024 — LDO 2025 | Planalto | ✅ recorte do art. 37 (P7): atualização de precatórios e RPVs da União no exercício de 2025; §1º: IPCA-E no período do art. 100, §5º |
| `ldo-2026-lei-15321-2025.md` | Lei 15.321/2025 — LDO 2026 | Planalto | ✅ recorte do art. 41 (P7): mesma matéria no exercício de 2026; §1º: IPCA-E no período do art. 100, §5º. O caput (Selic no exercício) não foi conciliado com a EC 136 / Res. CJF 983, art. 7º, §3º, III: ver `docs/P7-relatorio.md` |
| `cf88-art109-competencia.md` | CF/1988: art. 109 (competência dos juízes federais) | Planalto (compilada) | ✅ recorte (P7, acréscimo do coordenador); arquivo próprio para não refazer `cf88-seguridade.md` |
| `regimento-crps-portaria-mps-125-2026.md` | Regimento Interno do CRPS — Portaria MPS 125/2026, compilada até 20/03/2026 | gov.br (Ministério da Previdência Social, página do CRPS; PDF) | ✅ integral (P7), 95 páginas; versão que a página oficial lista como vigente em 15/10/2026. 🔴 compilação posterior a 20/03/2026 não verificada; revogações vêm marcadas por escrito na fonte (o `pdftotext` não detecta tachado) |
| `cpc-recursos-prazos-prev.md` | CPC: arts. 183, 219 a 224, 1.003, 1.009 a 1.014, 1.022 a 1.026 e 1.029 a 1.041 | Planalto (compilada) | ✅ recorte (W1-ctx, 15/10/2026); amostragem 4/5 pelo `conferir_amostra.py` + 1/1 à mão (o art. 1.035-A falhou no sorteio só porque a normalização do conferidor não remove o "Vigência" que a fonte põe depois de "(Incluído pela Lei nº 15.484, de 2026)"; o caput está literal na fonte). Vigência e regime intertemporal do art. 1.035-A e das demais alterações da Lei 15.484/2026: ver a linha de `lei-15484-2026.md` e a nota "Lei 15.484/2026 — vigência e regime intertemporal" na seção 2 (processo judicial) |
| `lei-9099-1995.md` | Lei 9.099/1995 (Juizados Especiais Cíveis e Criminais), aplicada ao JEF no que não conflitar (Lei 10.259, art. 1º) | Planalto (compilada) | ✅ integral (W1-ctx); amostragem 5/5 |
| `lei-12016-2009-ms.md` | Lei 12.016/2009 (mandado de segurança) | Planalto (compilada) | ✅ integral (W1-ctx); amostragem 5/5 |
| `cf88-art5-102-105.md` | CF/1988: art. 5º (caput e LXIX); arts. 102 e 105 (competência do STF e do STJ) | Planalto (compilada) | ✅ recorte (W1-ctx); amostragem 2/2 (o sorteador só acha 2 linhas "Art. N" longas no recorte; LXIX conferido à mão). Os arts. 102 a 105 de `cf88-seguridade.md` são do ADCT: homônimos |
| `ec-20-1998.md` | EC 20/1998 | Planalto | ✅ integral (W1-ctx); amostragem 5/5. Usada pela redação que deu ao art. 40, §1º, III, "a", da CF (60/35 homem, 55/30 mulher), anterior à EC 103, base da idade da EC 47, art. 3º, III; `cf88-seguridade.md` só traz a redação atual do art. 40 |
| `lc-95-1998-art8.md` | LC 95/1998: art. 8º (vigência; §1º, contagem da vacância) | Planalto | ✅ recorte (W1-ctx r2, 15/10/2026); amostragem 1/1 pelo `conferir_amostra.py` (caput) + §§1º e 2º conferidos à mão contra o bruto. O recorte inclui, riscada, a redação revogada do art. 9º, como na fonte |
| `cpc-art14-intertemporal.md` | CPC: art. 14 (aplicação imediata da norma processual) | Planalto (compilada) | ✅ recorte (W1-ctx r2, 15/10/2026); amostragem 1/1 pelo `conferir_amostra.py` |
| `lei-15484-2026.md` | Lei 15.484/2026 (relevância da questão de direito federal no REsp; inclui o art. 1.035-A no CPC e altera os arts. 927, 932, 979, 988, 998, 1.030, 1.039 e 1.042) | Planalto (página da lei, DOU de 04/08/2026, edição extra) | ✅ integral (W1-ctx r1, 15/10/2026); amostragem 7/7 pelo `conferir_amostra.py` (todos os artigos da lei, inclusive os arts. 4º e 7º). Vigência e transição: nota "Lei 15.484/2026 — vigência e regime intertemporal" na seção 2 (processo judicial) |

## 2. Tema → diploma → dispositivo, pelos 7 scripts do `03-inventario-calculos.md`

### Script 1 — `calc_cnis.py` (carência, qualidade de segurado, indicadores)

| Tema | Onde está |
|---|---|
| Períodos de carência (12 / 180 / 24) | `lei-8213-1991.md` · art. 25 ; `decreto-3048-1999.md` · art. 29 |
| Conceito e contagem da carência | `lei-8213-1991.md` · art. 24 ; `decreto-3048-1999.md` · art. 26 |
| Dispensa de carência (pensão, auxílio-acidente, acidente, doenças da lista) | `lei-8213-1991.md` · arts. 26 e 151 ; `decreto-3048-1999.md` · art. 30 |
| Contribuição em atraso do contribuinte individual para carência | `lei-8213-1991.md` · art. 27 ; `decreto-3048-1999.md` · art. 28 |
| Carência após perda da qualidade (metade reabre o cômputo das anteriores) | `lei-8213-1991.md` · art. 27-A ; `decreto-3048-1999.md` · art. 27-A ; `in-128-2022-inss.md` · arts. 189 a 205 (Título "Da carência") |
| Carência do salário-maternidade (inconstitucional) | `lei-8213-1991.md` · art. 25 (inciso III ainda no texto) ; `temas-sumulas-prev.md`, ADI 2.110 |
| Qualidade de segurado e período de graça (12/24/+12; 6 para facultativo) | `lei-8213-1991.md` · art. 15 ; `decreto-3048-1999.md` · art. 13 ; `in-128-2022-inss.md` · arts. 183 a 188 |
| Data da perda da qualidade | `decreto-3048-1999.md` · art. 14 ; `lei-8212-1991.md` · art. 30 (inciso II: vencimento no dia 15) |
| Valor probatório do CNIS e acerto | `lei-8213-1991.md` · art. 29-A ; `decreto-3048-1999.md` · art. 19 ; `in-128-2022-inss.md` · arts. 10 a 31 |
| Indicadores do CNIS (IEAN, pendências) | `portaria-990-2022-anexo-v-indicadores-cnis.md` (tabela; IEAN no grupo Vínculos e Remunerações) |
| IEAN não converte sozinho: exposição exige comprovação | `lei-8213-1991.md` · art. 57 (§§3º e 4º) ; `lei-8212-1991.md` · art. 22 (inciso II) |

### Script 2 — `calc_tempo_contribuicao.py` (tempo comum, especial, concomitância)

| Tema | Onde está |
|---|---|
| Vedação da conversão de especial em comum para o trabalho após 13/11/2019 | `ec-103-2019.md` · art. 25 (§2º) ; `decreto-3048-1999.md` · art. 188-P (§5º) |
| Multiplicadores da conversão (2,00/2,33; 1,50/1,75; 1,20/1,40) | `decreto-3048-art188p-tabela.md` (texto do art. 188-P §5º, p. 449 da compilação oficial) |
| Conversão e caracterização pela lei da época | `lei-8213-1991.md` · art. 57 (§5º) ; `decreto-3048-1999.md` · art. 188-P (§6º) |
| Aposentadoria especial: exposição permanente, PPP e LTCAT | `lei-8213-1991.md` · arts. 57 e 58 ; `in-128-2022-inss.md` · arts. 260 a 302 |
| Ruído (limite vigente no Anexo IV, item 2.0.1) e faixa de 90 dB de 06/03/1997 a 18/11/2003 | `decreto-3048-1999.md` (Anexo IV, item 2.0.1) ; `temas-sumulas-prev.md`, STJ Tema 694 ; `in-128-2022-inss.md` · art. 292 |
| Tempo de contribuição: o que conta e o que não conta | `lei-8213-1991.md` · art. 55 ; `decreto-3048-1999.md` · arts. 59 e 60 ; `in-128-2022-inss.md` · arts. 206 a 218 |
| Contagem do tempo antes e depois de 13/11/2019 (dias × competências; ano de 365 e mês de 30) | `in-128-2022-inss.md` · arts. 206 e 207 |
| Concomitância de comum com especial comprovado: o especial não é prejudicado | `in-128-2022-inss.md` · art. 265 |
| Concomitância: soma dos salários no salário de benefício | `lei-8213-1991.md` · art. 32 |
| Vedação de contar em dobro e de somar tempo concomitante na contagem recíproca | `lei-8213-1991.md` · art. 96 |

### Script 3 — `calc_transicao.py` (direito adquirido, transições, permanente)

| Tema | Onde está |
|---|---|
| Direito adquirido até 13/11/2019 | `ec-103-2019.md` · art. 3 |
| Pontos (96/86 + 1 por ano) e professor | `ec-103-2019.md` · art. 15 |
| Idade progressiva | `ec-103-2019.md` · art. 16 |
| Pedágio de 50% (só RGPS; valor = média × fator) | `ec-103-2019.md` · art. 17 |
| Idade (transição) | `ec-103-2019.md` · art. 18 |
| Regra permanente e especial permanente | `ec-103-2019.md` · art. 19 |
| Pedágio de 100% | `ec-103-2019.md` · art. 20 |
| Especial por pontos | `ec-103-2019.md` · art. 21 ; `decreto-3048-1999.md` · art. 188-P (§1º: idade e tempo apurados em dias) |
| Cálculo: média de 100% desde 07/1994, 60% + 2%, 100% nos casos do §3º, descarte | `ec-103-2019.md` · art. 26 |
| Vigência da EC 103 | `ec-103-2019.md` · art. 36 |
| Regra anterior: 80% maiores, fator, opção 96/86 pontos | `lei-8213-1991.md` · arts. 29 e 29-C ; `lei-9876-1999.md` · art. 3 ; `temas-sumulas-prev.md`, ADIs 2.110/2.111 e Tema 1.102 |
| Fator previdenciário (expectativa de sobrevida, bônus de 5/10 anos) | `lei-8213-1991.md` · art. 29 (§§7º a 9º) ; `lei-9876-1999.md` (Anexo: variáveis em texto, fórmula em imagem 🔴) |
| Procedimento do INSS para as regras programáveis | `in-128-2022-inss.md` · arts. 244 a 324 |

### Script 4 — `calc_incapacidade.py`

| Tema | Onde está |
|---|---|
| Auxílio por incapacidade temporária: 91% e teto da média dos 12 últimos | `lei-8213-1991.md` · arts. 61 e 29 (§10) |
| Início do benefício (16º dia; DER se requerido após 30 dias) | `lei-8213-1991.md` · art. 60 (caput e §1º) |
| Carência de 12 e dispensas | `lei-8213-1991.md` · arts. 25 e 26 |
| Aposentadoria por incapacidade permanente: 60% + 2%; 100% se acidentária | `ec-103-2019.md` · art. 26 (§2º, III; §3º, II; §5º) ; `temas-sumulas-prev.md`, STF Tema 1.300 |
| Regra anterior (100%) e acréscimo de 25% | `lei-8213-1991.md` · arts. 44 e 45 |
| Auxílio-acidente: 50%, sem carência, inacumulável com aposentadoria | `lei-8213-1991.md` · arts. 86 e 26 ; `temas-sumulas-prev.md`, STJ Tema 416 |
| Piso de um salário mínimo e exceção do auxílio-acidente | `cf88-seguridade.md` · art. 201 (§2º) ; `decreto-3048-1999.md` · arts. 35 e 42 (parágrafo único) |
| Procedimento do INSS | `in-128-2022-inss.md` · arts. 326 a 334 (permanente), 335 a 351 (temporária), 352 a 356 (auxílio-acidente) |

### Script 5 — `calc_rmi.py` (RMI, revisão, prescrição, decadência)

| Tema | Onde está |
|---|---|
| Média, teto e coeficiente pós-EC 103 | `ec-103-2019.md` · art. 26 |
| Divisor mínimo de 108 para filiado até 07/1994 (exceto incapacidade permanente) | `lei-8213-1991.md` · art. 135-A ; `lei-14331-2022.md` |
| Correção dos salários de contribuição pelo INPC | `lei-8213-1991.md` · art. 29-B |
| Valor mínimo e máximo do salário de benefício | `lei-8213-1991.md` · arts. 29 (§2º) e 33 |
| Reajuste e data de pagamento (janela do §2º: 1º ao 5º dia útil do mês seguinte, acima de 1 mínimo; do §3º: do 5º dia útil antes do fim do mês ao 5º do seguinte, até 1 mínimo; §4º: dia útil bancário) | `lei-8213-1991.md` · art. 41-A |
| Decadência de 10 anos e prescrição quinquenal | `lei-8213-1991.md` · art. 103 ; `temas-sumulas-prev.md`, STF Tema 313 ; `in-128-2022-inss.md` · arts. 591 a 596 |
| Revisão administrativa | `in-128-2022-inss.md` · arts. 583 e seguintes |
| Procedimento do INSS para cálculo | `in-128-2022-inss.md` · arts. 219 a 243 |
| Vida toda: inviável (art. 3º da Lei 9.876 é cogente) | `lei-9876-1999.md` · art. 3 ; `temas-sumulas-prev.md`, ADIs 2.110/2.111 e Tema 1.102 |
| Piso e teto do ano | `decreto-12797-2025-salario-minimo.md` · art. 1 ; `decreto-12342-2024-salario-minimo.md` · art. 1 ; `portaria-interministerial-mps-mf-13-2026.md` · art. 2 (teto de 2026: R$ 8.475,55) ; `portaria-interministerial-mps-mf-6-2025.md` · art. 2 (teto de 2025: R$ 8.157,41) ; anos anteriores: `serie-salario-minimo-1994-2026.md` e `serie-teto-rgps-1994-2026.md` (linha da vigência) |
| Reajuste anual da renda por ano (fator integral, Anexo I pro rata pela DIB, incorporação do teto), 2002 a 2026 | `serie-reajustes-rgps-1995-2026.md` (seção do ano) ; 1997 a 2001: `portaria-mpas-3971-1997-reajuste.md` · arts. 1 e 2 ; `portaria-mpas-4478-1998-reajuste.md` · arts. 1 e 2 ; `portaria-mpas-5188-1999-reajuste.md` · arts. 5 e 6 ; `portaria-mpas-6211-2000-reajuste.md` · arts. 1 e 2 ; `portaria-mpas-1987-2001-reajuste.md` · arts. 1 e 2 ; 01/08/2006 sobre a renda de março: `lei-11430-2006.md` · art. 3 ; `portaria-mps-342-2006-reajuste.md` · art. 1 ; `portaria-interministerial-mps-mf-6-2025.md` · art. 1 ; `portaria-interministerial-mps-mf-13-2026.md` · art. 1 ; dado de máquina: `scripts/data/reajustes-rgps.json` |
| Decadência: prazo em anos vence no dia de igual número; termo em feriado prorroga-se ao seguinte dia útil | `lei-8213-1991.md` · art. 103 ; `cc-excertos-prev.md` · art. 132 (§§1º e 3º) ; `lei-662-1949-feriados.md` · art. 1 (feriados nacionais) |
| Abono anual de 2021 pago em maio e junho (corte prescricional de RMI-04) | `decreto-10695-2021-abono.md` · art. 1 |
| Abono anual de 2022 pago em abril e maio (competências vencidas de 2022) | `decreto-10999-2022-abono.md` · art. 1 |
| Abono anual de 2023 pago em maio e junho (competências vencidas de 2023) | `decreto-11517-2023-abono.md` · art. 1 |
| Abono anual de 2024 pago em abril e maio (competências vencidas de 2024) | `decreto-11947-2024-abono.md` · art. 1 |
| Abono anual de 2025 pago em abril e maio (calendário do valor da causa) | `decreto-12425-2025-abono.md` · art. 1 |
| Abono anual de 2026 pago em abril e maio (calendário do valor da causa) | `decreto-12884-2026-abono.md` · art. 1 |

### Script 6 — `calc_valor_causa_prev.py` (valor da causa e alçada do JEF)

| Tema | Onde está |
|---|---|
| Vencidas + 12 vincendas | `cpc-excertos-prev.md` · art. 292 (§§1º e 2º) ; `lei-10259-2001-jef.md` · art. 3 (§2º) |
| Alçada de 60 salários mínimos | `lei-10259-2001-jef.md` · art. 3 ; `cpc-excertos-prev.md` · art. 43 (competência fixada na distribuição) |
| Renúncia ao excedente, inclusive vincendas | `temas-sumulas-prev.md`, STJ Tema 1.030 |
| Abono anual (não há no BPC) | `lei-8213-1991.md` · art. 40 ; `lei-8742-1993-loas.md` · art. 20 |
| Sem prazo diferenciado para o INSS no JEF | `lei-10259-2001-jef.md` · art. 9 |
| Competência da Justiça Federal para as causas do INSS (exceto acidente de trabalho); foro; delegação à Justiça Estadual por lei e recurso ao TRF | `cf88-art109-competencia.md` · art. 109 (I e §§2º a 4º) |

### Script 7 — `calc_rpv.py` (atrasados, honorários, RPV × precatório)

| Tema | Onde está |
|---|---|
| Correção e juros até 11/2021: Tema 905 e Tema 810 | `temas-sumulas-prev.md` (STJ Tema 905, STF Tema 810) ; `lei-9494-1997.md` (art. 1º-F) ; `manual-cjf-2026-calculos-prev.md` (itens 4.3.1.1 e 4.3.2, p. 55 a 60) |
| Marcos de vigência das Leis 11.430/2006 e 11.960/2009 | `lei-11430-2006.md` · art. 6 ; `lei-11960-2009.md` · art. 9 |
| INPC no previdenciário | `lei-8213-1991.md` · art. 41-A ; `lei-11430-2006.md` · art. 1 ; `mp-316-2006.md` (art. 2º, que incluía o art. 41-A; reajuste dos benefícios em manutenção, não correção de condenação: a aplicação à liquidação é do Manual, item 4.3.1.1) |
| Janela de pagamento: antecipação de quem recebe até um mínimo (art. 41-A, §3º) só desde a MP 404/2007, em vigor em 12/12/2007 (competência 12/2007 em diante) | `lei-11665-2008.md` · art. 1 ; `mp-404-2007.md` (página riscada: MP convertida; o art. 2º, vigência na publicação, e o cabeçalho "DE 11 DE DEZEMBRO DE 2007" datam a MP; publicação no DOU de 12/12/2007) ; `lei-8213-1991.md` · art. 41-A |
| Juros de 1% a.m. até jun./2009 na condenação previdenciária | `manual-cjf-2026-calculos-prev.md` (item 4.3.2, tabela) ; `dl-2322-1987.md` · art. 3 (o texto fala em créditos **trabalhistas** e juros **capitalizados mensalmente**; o "1% simples" previdenciário é regra do Manual, não da letra do DL) |
| BPC: correção e juros das condenações assistenciais (ações condenatórias em geral; desde set./2025, IPCA-15 + taxa legal com dedução do IPCA-15) | `manual-cjf-2026-calculos-prev.md` (item 4.3.1.1, Nota 3; itens 4.2.1.1 e 4.2.2) ; `temas-sumulas-prev.md` (Tema 810) |
| Selic única de dez./2021 a ago./2025 (redação original, riscada na fonte; Selic de ago./2025 computada em set./2025) | `ec-113-2021.md` · art. 3 (linha `(revogado)`) ; `manual-cjf-2026-calculos-prev.md` (itens 4.3.1.1, Notas 4 e 5, e 4.3.2) ; `temas-sumulas-prev.md` (STF Tema 1.419) |
| **Fase anterior à expedição, desde set./2025 (benefício previdenciário):** INPC + taxa legal (Selic com dedução do INPC), aplicada no mês seguinte ao da competência | `manual-cjf-2026-calculos-prev.md` (itens 4.3.1.1, 4.3.2 e Nota 3, com a tabela das competências set./2025 a maio/2026, aplicadas de out./2025 a jun./2026; item 4.2.2, Nota 7) ; `cc-excertos-prev.md` · art. 406 ; `temas-sumulas-prev.md` (STF Tema 1.419) |
| Requisitório federal da expedição ao pagamento: IPCA + 2% a.a., teto Selic, sem juros no período do §5º | `ec-113-2021.md` · art. 3 (redação da EC 136) ; `ec-136-2025.md` · arts. 3 e 9 ; `res-cjf-983-2026.md` · art. 7 (§3º, III: a partir de set./2025, IPCA + juros simples de 2% a.a. sobre o principal atualizado **ou** Selic sobre o consolidado, o que for menor; §4º: vedada a Selic composta; §§1º, 2º e 6º) |
| Requisitório após a EC 136: critérios do CNJ citados pelo motor travado — federal desde set./2025 e estadual, distrital e municipal desde ago./2025 (IPCA sobre principal e juros somados, juros de 2% a.a. só sobre o principal, teto Selic, sem juros no período do §5º do art. 100 da CF; data-base anterior pela Res. CNJ 303/2019) | `provimento-cnj-207-2025.md` · arts. 2, 3 e 4 (art. 2º: I, II, III, §§1º e 2º, federal; art. 3º: §1º, a, b e c, §§2º, 3º e 5º, estadual; art. 4º: precatório tributário só pela Selic) |
| Período de graça do precatório na redação original da EC 113: sem Selic, só correção monetária pelo IPCA-E (ADIs 4.357-QO e 4.425-QO; LDO 2025, art. 37, §1º; LDO 2026, art. 41, §1º) | `temas-sumulas-prev.md` (STF Tema 1.335; ADI 4.357-QO e 4.425-QO) ; `res-cjf-983-2026.md` · art. 7 (caput e §2º) ; `ldo-2025-lei-15080-2024.md` · art. 37 ; `ldo-2026-lei-15321-2025.md` · art. 41 ; `manual-cjf-2026-calculos-prev.md` (cap. 5, Notas 1, 2 e 4) |
| Limite da RPV verificado pela atualização até a transmissão ao tribunal | `res-cjf-983-2026.md` · art. 3 (§4º) |
| Honorários sucumbenciais em requisição própria; contratuais integram o crédito para classificar RPV × precatório | `res-cjf-983-2026.md` · art. 16 |
| Prazo do precatório (apresentado até 1º de fevereiro) e preferência alimentar | `cf88-seguridade.md` · art. 100 (§§1º e 5º) |
| Vedação de fracionar | `cf88-seguridade.md` · art. 100 (§8º) ; `lei-10259-2001-jef.md` · art. 17 (§3º) |
| RPV: 60 salários mínimos, 60 dias, renúncia | `lei-10259-2001-jef.md` · arts. 17 e 3 ; `cpc-excertos-prev.md` · art. 535 (§3º, II) |
| Impugnação do INSS no cumprimento | `cpc-excertos-prev.md` · arts. 534 e 535 |
| Honorários sobre as vencidas até a sentença; honorários como verba alimentar | `temas-sumulas-prev.md` (Súmula 111 do STJ; SV 47) |
| Base dos honorários: pagamento administrativo após a citação não reduz a base | `temas-sumulas-prev.md` (STJ Tema 1.050) |
| Requisições de pagamento (complementar, suplementar) | `manual-cjf-2026-calculos-prev.md` (cap. 5, p. 87 a 92) ; `res-cjf-983-2026.md` · art. 4 |

### Recurso administrativo ao CRPS (consumido por `prazos-previdenciarios`)

| Tema | Onde está |
|---|---|
| Prazo de 30 dias para recurso e contrarrazões, da ciência da decisão (exceto FAP); prazo do INSS a partir do recebimento do processo | `regimento-crps-portaria-mps-125-2026.md` · art. 77 ; `decreto-3048-1999.md` · art. 305 |
| Natureza, estrutura e competência do CRPS (Juntas, Câmaras, Conselho Pleno) | `regimento-crps-portaria-mps-125-2026.md` · art. 1 (no Anexo; o art. 1º da Portaria é o de aprovação — homônimo) |

### BPC/LOAS (consumido pelos scripts 1, 6 e 7)

| Tema | Onde está |
|---|---|
| Benefício, renda per capita, deficiência, acumulação | `lei-8742-1993-loas.md` · arts. 20 e 20-B |
| Critério de 1/4 não é o único | `temas-sumulas-prev.md` (STF Tema 27; STJ Tema 185; TNU Súmula 79) |
| Previsão constitucional | `cf88-seguridade.md` · art. 203 |

### RPPS federal e previdência complementar (P5: lei seca, sem script nesta leva)

| Tema | Onde está |
|---|---|
| Regime próprio do servidor (base constitucional) | `cf88-seguridade.md` · art. 40 |
| Regras gerais de organização dos RPPS; vedação de benefício distinto do RGPS | `lei-9717-1998-rpps.md` · arts. 1 e 5 |
| Contribuição do ente e dos servidores dos RPPS | `lei-9717-1998-rpps.md` · arts. 2 e 3 ; `lei-10887-2004.md` · arts. 4, 5, 6 e 8 |
| Média de 80% das maiores remunerações (regra anterior à EC 103) | `lei-10887-2004.md` · art. 1 |
| Média de 100% desde 07/1994 (RPPS da União e RGPS, até lei própria) | `ec-103-2019.md` · art. 26 |
| Aposentadoria do servidor federal: regra até lei federal | `ec-103-2019.md` · art. 10 |
| Transição do servidor federal: pontos e pedágio de 100% | `ec-103-2019.md` · arts. 4 e 20 |
| Pessoa com deficiência (RGPS e servidor federal) | `ec-103-2019.md` · art. 22 ; `lc-142-2013-pcd.md` · arts. 3 e 8 |
| Pensão por morte e acumulação (RGPS e servidor federal) | `ec-103-2019.md` · arts. 23 e 24 |
| Reajuste de proventos e pensões pela data e índice do RGPS | `lei-10887-2004.md` · art. 15 |
| Paridade (reajuste com a remuneração da ativa) para quem se aposenta com integralidade pela EC 103, art. 4º, §6º, I, ou art. 20, §2º, I | `ec-41-2003.md` · art. 7 ; `ec-103-2019.md` · arts. 4 (§7º, I) e 20 (§3º, I) |
| Transição da EC 47 (ingresso até 16/12/1998: proventos integrais, redução de idade, paridade) e sua revogação pela EC 103 | `ec-47-2005.md` · art. 3 ; `ec-41-2003.md` · arts. 6 e 7 ; `ec-103-2019.md` · arts. 3, 35 e 36 |
| Previdência complementar: base constitucional | `cf88-seguridade.md` · art. 202 ; `cf88-seguridade.md` · art. 40 (§§14 a 16) |
| Regime complementar: natureza, entidades abertas e fechadas, institutos (BPD, portabilidade, resgate, autopatrocínio) | `lc-109-2001.md` · arts. 1, 4, 14, 31 e 36 |
| Benefícios e contribuições do plano não integram o contrato de trabalho | `lc-109-2001.md` · art. 68 |
| Prescrição quinquenal das prestações | `lc-109-2001.md` · art. 75 |
| Patrocínio por entes públicos: carência de 60 contribuições, paridade de custeio, vedação de aporte | `lc-108-2001.md` · arts. 1, 3, 5 e 6 |


### Processo judicial: prazos, recursos, Juizados e mandado de segurança (W1-ctx; consumido por `prazos-previdenciarios` e pelas skills de peças)

> As âncoras de artigo com ponto de milhar (1.003, 1.009…) não são checadas pelo `conferir_ancoras_indice.py` (o regex lê só "1"); foram conferidas por `grep "^Art\. 1\.0NN\."` no arquivo em 15/10/2026.

| Tema | Onde está |
|---|---|
| Prazo em dobro da Fazenda (autarquia inclusive) e intimação pessoal | `cpc-recursos-prazos-prev.md` · art. 183 |
| Contagem em dias úteis; suspensão de 20/12 a 20/01; exclusão do dia do começo | `cpc-recursos-prazos-prev.md` · arts. 219, 220 e 224 |
| Prazo recursal de 15 dias (exceto embargos de declaração) e sua contagem | `cpc-recursos-prazos-prev.md` · art. 1.003 (§5º) |
| Apelação: cabimento, forma, efeitos, devolução | `cpc-recursos-prazos-prev.md` · arts. 1.009 a 1.014 |
| Embargos de declaração: cabimento, 5 dias, interrupção, prequestionamento ficto | `cpc-recursos-prazos-prev.md` · arts. 1.022 a 1.026 |
| REsp e RE: interposição, admissibilidade, repercussão geral, repetitivos | `cpc-recursos-prazos-prev.md` · arts. 1.029 a 1.041 (1.035: repercussão geral; 1.036 a 1.041: repetitivos) |
| Competência do STF (recurso extraordinário; repercussão geral) | `cf88-art5-102-105.md` · art. 102 (III e §3º) |
| Competência do STJ (recurso especial; relevância, EC 125/2022) | `cf88-art5-102-105.md` · art. 105 (III e §§2º e 3º) |
| JEF: sem prazo diferenciado para o INSS, inclusive para recorrer | `lei-10259-2001-jef.md` · art. 9 |
| JEF: só sentença definitiva é recorrível (salvo cautelar do art. 4º); sem reexame necessário | `lei-10259-2001-jef.md` · arts. 5 e 13 |
| JEF: pedido de uniformização e recurso extraordinário | `lei-10259-2001-jef.md` · arts. 14 e 15 |
| Aplicação subsidiária da Lei 9.099 ao JEF | `lei-10259-2001-jef.md` · art. 1 |
| Juizados: dias úteis na contagem de prazos | `lei-9099-1995.md` · art. 12-A |
| Juizados: recurso inominado em 10 dias, efeito devolutivo | `lei-9099-1995.md` · arts. 41, 42 e 43 |
| Juizados: embargos de declaração em 5 dias, interrupção do prazo | `lei-9099-1995.md` · arts. 48, 49 e 50 |
| Mandado de segurança: base constitucional | `cf88-art5-102-105.md` · art. 5 (inciso LXIX) |
| Mandado de segurança: cabimento, vedações, liminar, apelação, decadência de 120 dias, sem honorários | `lei-12016-2009-ms.md` · arts. 1, 5, 7, 14, 23 e 25 |
| REsp: relevância da questão de direito federal (tópico específico, presunção do art. 105, §3º, da CF, quórum de 2/3, suspensão nacional) | `cpc-recursos-prazos-prev.md` · art. 1.035-A ; `cf88-art5-102-105.md` · art. 105 (§§2º e 3º) |
| REsp: relevância — exigência do tópico só para recurso contra acórdão publicado depois da vigência; efeitos do julgamento nos processos em andamento; vigência 30 dias após a publicação | `lei-15484-2026.md` · arts. 4, 5 e 7 |
| Vigência da lei com vacância: contagem com a data da publicação e o último dia; vigência no dia seguinte | `lc-95-1998-art8.md` · art. 8 (§1º) |
| Lei processual nova: aplicação imediata aos processos em curso, sem retroagir | `cpc-art14-intertemporal.md` · art. 14 |

**Lei 15.484/2026 — vigência e regime intertemporal** (texto em `lei-15484-2026.md`, conferido 7/7 contra a página do Planalto em 15/10/2026):

- **Publicação:** DOU de 04/08/2026, edição extra (rodapé da página do Planalto).
- **Vigência (art. 7º):** "após decorridos 30 (trinta) dias de sua publicação oficial". Contagem pela LC 95/1998, art. 8º, §1º (`lc-95-1998-art8.md`): inclui a data da publicação e o último dia do prazo, com vigência "no dia subseqüente à sua consumação integral". Dia 1 = 04/08/2026; dia 30 = 02/09/2026; **vigência em 03/09/2026**.
- **Exigência do tópico de relevância (art. 4º):** só nos recursos especiais "interpostos contra acórdãos publicados após a data de entrada em vigor desta Lei". O marco é a **publicação do acórdão recorrido**, não a data da interposição: REsp interposto depois da vigência contra acórdão publicado antes dela não precisa do tópico do art. 1.035-A, §2º.
- **Efeitos do julgamento da relevância (art. 5º):** reconhecida ou recusada pelo STJ, os efeitos processuais e materiais incidem nos processos em andamento no STJ e nas instâncias de origem.
- **Alterações correlatas do CPC (art. 3º: arts. 927, III-A; 932, IV, "b", e V, "b"; 979, §3º; 988, V e §§4º e 5º, II; 998, parágrafo único; 1.030, I, "c", II e V, "a"; 1.039, parágrafo único; 1.042, caput e §2º):** a lei não lhes dá regra de transição própria; entram em vigor na mesma data do art. 7º. Fora dos arts. 4º e 5º, a aplicação a processos pendentes segue o CPC, art. 14 (`cpc-art14-intertemporal.md`): a norma processual "não retroagirá e será aplicável imediatamente aos processos em curso, respeitados os atos processuais praticados e as situações jurídicas consolidadas sob a vigência da norma revogada". No recorte `cpc-recursos-prazos-prev.md` estão, já com a nova redação, os arts. 1.030, 1.035-A e 1.039; os demais aparecem só como texto de alteração em `lei-15484-2026.md`.

### Servidor: redação anterior à EC 103 (W1-ctx)

| Tema | Onde está |
|---|---|
| Art. 40, §1º, III, "a", da CF na redação da EC 20/1998 (60 anos e 35 de contribuição, homem; 55 e 30, mulher): idade-base da redução da EC 47, art. 3º, III | `ec-20-1998.md` · art. 1 (é o artigo da emenda que reescreve o artigo 40 da CF) ; `ec-47-2005.md` · art. 3 |

## 3. O que ficou de fora (🔴)

| Item | Motivo | Consequência |
|---|---|---|
| Fórmula do fator previdenciário (Anexo da Lei 9.876/1999) | imagem na página do Planalto; só as definições das variáveis estão em texto | fórmula sem texto conferível neste diretório |
| Anexos da IN 128/2022 | o Portal IN publica cada anexo em página própria; não capturados nesta entrega | consultar ao vivo no portal |
| Tábua de mortalidade do IBGE | fora da lista desta entrega | fator previdenciário sai como fórmula |
| Lei 9.289/1996 (custas na Justiça Federal) | fora da lista | isenção do INSS na Justiça Federal segue indeterminada |
| Lista de doenças que dispensam carência (ato atual do art. 151 da Lei 8.213) | fora da lista | dispensa de carência por doença não é automatizada |
| Regulamento do art. 20 §11-A da LOAS (ampliação até 1/2 salário mínimo) | fora da lista | BPC sem ampliação automática acima de 1/4 |
| Andamento atual da ADI 7.873 (EC 136) | não consultado | pendência de atualização |
| Série mensal da taxa legal (competências posteriores a maio/2026; aplicações posteriores a junho/2026) | o Manual traz a tabela só até a competência maio/2026, aplicada em junho/2026 | meses posteriores: fórmula, até nova tabela do CJF/BCB |
| Inteiro teor dos acórdãos (Tema 1.102 nos embargos; Tema 905) | só teses e andamentos | leitura do dispositivo integral pendente |
