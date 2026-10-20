# Escrita humana no texto jurídico — anexo padrão

> Anexo de `context/` copiado byte a byte para todo plugin da família e conferido por sha256 no build. **Não edite a cópia dentro do plugin.** Ajuste do domínio vai em `context/escrita-humana-<dom>.md`.
>
> **Lista de marcadores:** v1 · 07/10/2026 · limiares iniciais, ainda **não calibrados** contra corpus de peças reais (ver §9).
>
> **Como as skills usam este arquivo:** por grep e faixa, pela seção. A skill de redação lê §5 a §8 na passada anti-IA; a `suprema-corte-<dom>` lê §2 a §4 no R4.AI. Os números de seção são estáveis: mudar a numeração quebra o grep das skills.

---

## §1 Para que serve

Juiz, assessor, desembargador e advogado da parte contrária já leem peças procurando texto de máquina. Texto com cara de IA perde credibilidade antes de ser lido no mérito. Este anexo diz como escrever para que a peça soe como o que ela é: trabalho de um advogado que conhece o caso.

A régua tem duas partes:

- **Marcadores contáveis (§3):** decidem se o R4 reprova. Dois revisores que contam igual chegam ao mesmo veredito.
- **Orientação de escrita (§5 a §8):** como escrever bem desde o primeiro rascunho, para que a contagem não precise reprovar nada.

Este anexo não substitui a voz do escritório gravada em `perfil.md`. A voz do escritório vence as preferências de estilo. Ela não vence os marcadores de tolerância zero nem as vedações éticas da OAB.

---

## §2 Regra de contagem

Conta-se só o **corpo da peça**. Ficam fora da contagem:

- endereçamento e qualificação das partes;
- assinatura do advogado, local e data;
- toda **citação literal** de lei, súmula, acórdão ou doutrina, entre aspas ou em recuo (o texto citado não é nosso);
- títulos numerados de seção ("I — Dos Fatos", "II — Do Direito");
- o rol de pedidos, exceto para AI-02, AI-06 e AI-16, que contam também ali.

Palavras: contam-se as sequências separadas por espaço no corpo. Parágrafo: bloco separado por linha em branco.

Na dúvida se um trecho é marcador, ele **não conta** para reprovação e vai para a camada de julgamento (§8) como sugestão. Essa regra protege o veredito de impressão pessoal.

---

## §3 Marcadores (lista v1) — o que reprova no R4.AI

Qualquer marcador acima do limiar reprova o R4. Não há soma de pontos.

| ID | Marcador | Limiar de reprovação |
|---|---|---|
| AI-01 | travessão (— ou –) usado como pontuação | 2 ou mais no mesmo parágrafo; **ou** mais de 2 por 1.000 palavras (peça com menos de 1.000 palavras: mais de 2 no total) |
| AI-02 | tríade retórica: três termos abstratos coordenados sem função enumerativa | 2 ou mais na peça |
| AI-03 | contraste fabricado: "não é X, é Y", "não se trata de X, mas de Y", "mais do que X, Y" | 2 ou mais na peça; **ou** 1 na abertura ou no fecho |
| AI-04 | abertura com elogio, eco do pedido ou anúncio do texto | 1 (tolerância zero) |
| AI-05 | conectivo da lista A (§3.1) | mais de 1 na peça |
| AI-06 | negrito fora de título, pedido e tese principal | mais de 3 trechos na peça |
| AI-07 | lista onde cabe prosa: rótulo em negrito + dois-pontos dentro da fundamentação, ou marcadores cujos itens são frases argumentativas completas | 1 bloco (tolerância zero) |
| AI-08 | cadeia de gerúndios: 3 ou mais orações de gerúndio seguidas na mesma frase | 2 ou mais cadeias na peça |
| AI-09 | atribuição vaga a doutrina ou jurisprudência, sem nome e fonte | 1 (tolerância zero) |
| AI-10 | inflação de importância (lista C, §3.2) | 2 ou mais na peça |
| AI-11 | hedge encadeado: 2 ou mais atenuadores na mesma oração | 2 ou mais ocorrências na peça |
| AI-12 | artefato de chatbot ou de modelo | 1 (tolerância zero) |
| AI-13 | variação sinonímica da mesma parte: 3 ou mais designações diferentes em 2 parágrafos seguidos | 1 ocorrência |
| AI-14 | fecho genérico de esperança ou de evidência | 1 (tolerância zero) |
| AI-15 | emoji no corpo | 1 (tolerância zero) |
| AI-16 | rastro de ferramenta: assinatura de skill ou plugin, nome de modelo, "gerado por" | 1 (tolerância zero) |

**Tolerância zero:** AI-04, AI-07, AI-09, AI-12, AI-14, AI-15, AI-16.

**Fora da lista, de propósito:** aspas curvas. O editor de texto converte aspas retas em curvas sozinho; como marcador, daria falso-positivo em peça escrita inteira por humano.

### §3.1 Lista A — conectivos de IA (AI-05)

`vale ressaltar` · `vale destacar` · `cumpre destacar` · `cabe salientar` · `é importante notar` · `é importante ressaltar` · `nesse sentido,` (em abertura de parágrafo) · `em suma` · `em última análise` · `no cerne da questão` · `não se pode olvidar` · `insta salientar`

### §3.2 Lista C — inflação de importância (AI-10)

`pilar fundamental` · `pedra angular` · `marco` (fora de "marco temporal", "marco interruptivo" e afins técnicos) · `crucial` · `essencial` (ornamental) · `verdadeiro` / `verdadeira` antes de substantivo ("verdadeira afronta") · `inegável` · `indubitavelmente` · `de suma importância` · `paradigmático`

### §3.3 Exemplos de cada marcador (autorais, para calibrar o olho)

| ID | Com o vício | Sem o vício |
|---|---|---|
| AI-01 | "A ré cobrou duas vezes — sem aviso — e negou o estorno — mesmo com o comprovante." | "A ré cobrou duas vezes, sem aviso, e negou o estorno mesmo diante do comprovante." |
| AI-02 | "A medida assegura transparência, previsibilidade e confiança." | "A medida obriga a ré a informar o valor antes da cobrança." |
| AI-03 | "Não se trata de mero aborrecimento, mas de violação de direito." | "A cobrança em duplicidade viola o art. 42, parágrafo único, do CDC." |
| AI-04 | "Excelente pedido. Segue abaixo a contestação solicitada." | (a peça começa no endereçamento) |
| AI-07 | "**Da legitimidade:** a autora é titular..." / "**Do interesse:** a ré resiste..." | "A autora é titular do crédito e a ré resiste ao pagamento, o que basta para a legitimidade e o interesse." |
| AI-08 | "...consolidando o débito, impedindo a quitação, gerando juros e agravando o dano." | "A ré consolidou o débito e impediu a quitação. Vieram os juros, e o dano cresceu." |
| AI-09 | "A jurisprudência pacífica reconhece o dever de indenizar." | "O STJ reconheceu o dever de indenizar no julgado X (citar número, órgão e data do anexo)." |
| AI-11 | "Em tese, eventualmente, poder-se-ia cogitar de abuso." | "Há abuso: a cláusula X transfere ao consumidor um risco do fornecedor." |
| AI-13 | "a autora... a requerente... a demandante... a postulante" em dois parágrafos | "a autora" do começo ao fim |
| AI-14 | "Diante do exposto, resta cristalino que o direito assiste à autora." | "Pelo exposto, a autora pede: ..." |
| AI-16 | "Peça elaborada com o plugin X, skill Y." | (nada; a rastreabilidade fica no rodapé da resposta ao advogado) |

---

## §4 Jargão legítimo (lista B) — nunca reprova sozinho

Estas expressões fazem parte do código profissional do advogado brasileiro. O problema é o **acúmulo** ou o uso como enfeite. Excesso vira **sugestão de correção** no R4, sem reprovar, a menos que também caia num marcador do §3.

| Expressão | Uso legítimo | Limite de acúmulo |
|---|---|---|
| `data venia` / `concessa venia` | discordar da fundamentação contrária | 2 por peça |
| `in casu`, `pacta sunt servanda`, `iura novit curia` e latim técnico | quando o termo é mais preciso que a tradução | 3 por peça |
| `destarte`, `outrossim`, `não obstante` | conectivo com função real | 1 por seção |
| `egrégio`, `colendo` | tribunal de segunda instância ou superior | só para o órgão certo |
| `douto`, `douta` | fundamentação da parte contrária ou do juízo | 2 por peça |
| `restou demonstrado`, `verifica-se` | voz passiva tradicional, sobretudo em recurso | 3 por peça |
| `mister`, `imperioso` | necessidade jurídica real | 1 por peça |
| negrito em pedido e em tese principal | ajuda a leitura em diagonal | conta no AI-06 só fora desses lugares |
| títulos numerados ("I — Dos Fatos") | estrutura tradicional | sem limite |

---

## §5 Como escrever como advogado

1. **Sujeito, verbo, dispositivo.** "A ré descumpriu o art. 42 do CDC" diz mais que três linhas sobre a importância da boa-fé.
2. **Fato antes de adjetivo.** Em vez de "conduta gravíssima", diga o que aconteceu, quando e com que prova.
3. **Uma ideia por frase, frases de tamanhos diferentes.** Frase curta para o ponto principal. Frase longa só quando a relação entre os elementos precisa ser dita de uma vez.
4. **Chame cada parte sempre do mesmo jeito.** Escolha "autora" ou "consumidora" e mantenha. Trocar de nome a cada parágrafo confunde o leitor e é sinal de máquina (AI-13).
5. **Cite com nome e lugar.** Doutrina: autor, obra, edição, página. Julgado: tribunal, número, órgão, data, e só se estiver no anexo de jurisprudência com ✅. Sem isso, não atribua (AI-09).
6. **Prosa na fundamentação, lista no pedido.** Argumento se encadeia em parágrafo; pedidos se enumeram.
7. **Voz ativa quando o sujeito importa.** "O INSS indeferiu" é melhor que "foi indeferido" quando quem indeferiu é parte da tese.
8. **Corte a abertura e o fecho de cerimônia.** A peça começa no endereçamento e termina nos pedidos, no valor da causa e na assinatura.
9. **Vírgula, dois-pontos e parênteses resolvem quase tudo.** O travessão fica para quando nenhum deles serve.
10. **Diga a dúvida uma vez, com a fonte.** "Há julgado em sentido contrário no tribunal X" vale mais que três atenuadores na mesma frase.

---

## §6 Por tipo de entrega

| Entrega | Registro | Cuidado principal |
|---|---|---|
| Petição, contestação, recurso | institucional, técnico | síntese do pedido logo no início; negrito só em pedido e tese; trigrama no máximo 1 na peça |
| Parecer | analítico, em primeira pessoa quando concluir ("entendo") | conclusão com cenários concretos, nunca fecho genérico positivo |
| Contrato | operacional, neutro | nada de adjetivo avaliativo em cláusula; negrito só em título de cláusula e penalidade |
| Notificação extrajudicial | direto, firme | um pedido claro e um prazo; nada de ameaça vaga |
| E-mail ou mensagem ao cliente | simples, sem latim | explicar o próximo passo e o que o cliente precisa fazer; nunca prometer resultado |
| Material de divulgação do escritório | institucional | vedações do Provimento 205/2021 da OAB valem acima de qualquer estilo: sem promessa de resultado, sem autopromoção, sem expor cliente |

---

## §7 Passada anti-IA na skill de redação

A skill que redige texto livre faz esta passada **antes** de entregar à `suprema-corte-<dom>`. É a primeira camada; o R4.AI é a segunda.

1. Contar no rascunho os marcadores do §3 pela regra do §2.
2. Reescrever todo trecho que estoura limiar. Marcador de tolerância zero sai sempre.
3. Conferir a lista B (§4) e reduzir o acúmulo.
4. Fazer a pergunta-filtro do §8 e reescrever os sinais encontrados.
5. Entregar à Corte o texto revisado, sem anunciar a passada dentro da peça.

Skill que só devolve tabela, cálculo, veredito ou configuração não faz a passada.

---

## §8 Pergunta-filtro

Depois da contagem:

> **"O que ainda faz este texto soar gerado por máquina?"**

Listar até 3 sinais, com o trecho, e reescrever. Na Suprema Corte, esses sinais entram como **sugestão de correção**, não como reprovação. A reprovação vem só da contagem do §3.

---

## §9 Versão e calibragem

| Versão | Data | Mudança |
|---|---|---|
| lista v1 | 07/10/2026 | limiares iniciais, fixados pela redação do manual de construção dos plugins |

**Calibragem pendente** antes de congelar o manual de construção dos plugins: rodar o R4.AI sobre `templates/texto-isca-anti-ia.md` (isca e versão limpa) e sobre ao menos 3 peças reais já protocoladas pelo escritório, anonimizadas e mantidas fora do repositório. Limiar que reprova peça humana boa sobe; limiar que deixa passar vício plantado desce. Cada ajuste vira nova linha nesta tabela, com nova versão da lista.

Fonte do método: o capítulo 04 do manual de construção dos plugins (§4.3 e §4.4). Ideia de origem: laudo comparativo de 07/10/2026 sobre um repositório externo de plugins jurídicos; nenhum texto foi copiado de lá.
