# Grafo de orquestração — quem chama quem

> **Arquivo gerado** por `audit/scripts/gerar_grafo.py` a partir da linha `Chamada por / Chama` de cada `skills/<nome>/SKILL.md`. Não editar à mão: corrija a linha na skill e gere de novo (`python3 -I audit/scripts/gerar_grafo.py --write`).
>
> Porta única: `previdenciario-master`. Mapa das camadas e regra de leitura: `context/metodologia-previdenciario.md`.

Skills lidas: **34**.

| Skill | Chamada por | Chama |
|---|---|---|
| `acao-revisional-rmi` | `previdenciario-master` · `analise-carta-concessao-indeferimento` | `analise-cnis` · `calculos-previdenciarios` · `anti-alucinacao-previdenciario` · `estrategia-de-caso-previdenciario` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `acidentario-do-trabalho` | `previdenciario-master` · `pericia-medica-previdenciaria` | `analise-cnis` · `prazos-previdenciarios` · `peticao-inicial-previdenciaria` · `memoria-de-caso-previdenciario` |
| `administrativo-inss-crps` | `previdenciario-master` · `analise-carta-concessao-indeferimento` · `bpc-loas-previdenciario` | `prazos-previdenciarios` · `analise-cnis` · `bpc-loas-previdenciario` · `mandado-seguranca-previdenciario` · `memoria-de-caso-previdenciario` |
| `analise-carta-concessao-indeferimento` | `previdenciario-master` · `triagem-dogmatica-previdenciario` | `prazos-previdenciarios` · `analise-cnis` · `analise-ppp-ltcat-aposentadoria-especial` · `memoria-de-caso-previdenciario` |
| `analise-cnis` | `previdenciario-master` · `triagem-dogmatica-previdenciario` · `administrativo-inss-crps` · `planejamento-previdenciario` · `analise-carta-concessao-indeferimento` | `analise-ppp-ltcat-aposentadoria-especial` · `memoria-de-caso-previdenciario` |
| `analise-ppp-ltcat-aposentadoria-especial` | `previdenciario-master` · `analise-cnis` · `planejamento-previdenciario` · `calculos-previdenciarios` | `memoria-de-caso-previdenciario` |
| `analise-trilateral-previdenciario` | `previdenciario-master` · `estrategia-de-caso-previdenciario` | `jurisprudencia-estrategica-previdenciario` |
| `anti-alucinacao-previdenciario` | `previdenciario-master` · `validador-previdenciario` · `base-legal-previdenciaria` · `jurisprudencia-estrategica-previdenciario` | — |
| `audiencia-previdenciaria` | `previdenciario-master` | `prazos-previdenciarios` · `pericia-medica-previdenciaria` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `base-legal-previdenciaria` | `previdenciario-master` · `validador-previdenciario` | `anti-alucinacao-previdenciario` |
| `bpc-loas-previdenciario` | `previdenciario-master` | `pericia-medica-previdenciaria` · `administrativo-inss-crps` · `prazos-previdenciarios` · `peticao-inicial-previdenciaria` · `memoria-de-caso-previdenciario` |
| `calculos-previdenciarios` | `previdenciario-master` · `estrategia-de-caso-previdenciario` | — |
| `cumprimento-sentenca-inss` | `previdenciario-master` | `prazos-previdenciarios` · `calculos-previdenciarios` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `documentos-extrajudiciais-previdenciarios` | `previdenciario-master` | `base-legal-previdenciaria` · `prazos-previdenciarios` · `calculos-previdenciarios` · `recursos-previdenciarios` · `visual-law-previdenciario` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `estilo-juridico-previdenciario` | `previdenciario-master` · `peticao-inicial-previdenciaria` · `replica-previdenciaria` · `recursos-previdenciarios` · `parecer-previdenciario` · `documentos-extrajudiciais-previdenciarios` | — |
| `estrategia-de-caso-previdenciario` | `previdenciario-master` · `triagem-dogmatica-previdenciario` | `prazos-previdenciarios` · `calculos-previdenciarios` · `analise-trilateral-previdenciario` · `jurisprudencia-estrategica-previdenciario` · `memoria-de-caso-previdenciario` |
| `jurisprudencia-estrategica-previdenciario` | `previdenciario-master` · `estrategia-de-caso-previdenciario` · `analise-trilateral-previdenciario` · `validador-previdenciario` | `anti-alucinacao-previdenciario` |
| `mandado-seguranca-previdenciario` | `previdenciario-master` · `administrativo-inss-crps` | `prazos-previdenciarios` · `base-legal-previdenciaria` · `calculos-previdenciarios` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `memoria-de-caso-previdenciario` | `previdenciario-master` | — |
| `parecer-previdenciario` | `previdenciario-master` | `base-legal-previdenciaria` · `jurisprudencia-estrategica-previdenciario` · `calculos-previdenciarios` · `prazos-previdenciarios` · `estrategia-de-caso-previdenciario` · `visual-law-previdenciario` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `pericia-medica-previdenciaria` | `previdenciario-master` · `acidentario-do-trabalho` · `bpc-loas-previdenciario` · `audiencia-previdenciaria` | `estilo-juridico-previdenciario` · `memoria-de-caso-previdenciario` |
| `peticao-inicial-previdenciaria` | `previdenciario-master` · `analise-carta-concessao-indeferimento` | `estrategia-de-caso-previdenciario` · `calculos-previdenciarios` · `pericia-medica-previdenciaria` · `acidentario-do-trabalho` · `analise-trilateral-previdenciario` · `jurisprudencia-estrategica-previdenciario` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `planejamento-previdenciario` | `previdenciario-master` | `analise-cnis` · `analise-ppp-ltcat-aposentadoria-especial` · `visual-law-previdenciario` · `memoria-de-caso-previdenciario` · `validador-previdenciario` |
| `prazos-previdenciarios` | `previdenciario-master` · `triagem-dogmatica-previdenciario` · `estrategia-de-caso-previdenciario` | — |
| `previdencia-complementar` | `previdenciario-master` · `rpps-servidor-publico` | `memoria-de-caso-previdenciario` |
| `previdenciario-master` | — | `triagem-dogmatica-previdenciario` · `memoria-de-caso-previdenciario` · `previdenciario-onboarding` · `prazos-previdenciarios` · `estrategia-de-caso-previdenciario` · `analise-trilateral-previdenciario` · `calculos-previdenciarios` · `base-legal-previdenciaria` · `jurisprudencia-estrategica-previdenciario` · `analise-cnis` · `analise-ppp-ltcat-aposentadoria-especial` · `analise-carta-concessao-indeferimento` · `pericia-medica-previdenciaria` · `planejamento-previdenciario` · `acidentario-do-trabalho` · `bpc-loas-previdenciario` · `administrativo-inss-crps` · `rpps-servidor-publico` · `previdencia-complementar` · `peticao-inicial-previdenciaria` · `replica-previdenciaria` · `mandado-seguranca-previdenciario` · `audiencia-previdenciaria` · `acao-revisional-rmi` · `cumprimento-sentenca-inss` · `recursos-previdenciarios` · `parecer-previdenciario` · `documentos-extrajudiciais-previdenciarios` · `visual-law-previdenciario` · `estilo-juridico-previdenciario` · `anti-alucinacao-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` |
| `previdenciario-onboarding` | `previdenciario-master` | — |
| `recursos-previdenciarios` | `previdenciario-master` | `prazos-previdenciarios` · `analise-trilateral-previdenciario` · `jurisprudencia-estrategica-previdenciario` · `base-legal-previdenciaria` · `calculos-previdenciarios` · `visual-law-previdenciario` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `replica-previdenciaria` | `previdenciario-master` | `prazos-previdenciarios` · `analise-cnis` · `calculos-previdenciarios` · `analise-trilateral-previdenciario` · `jurisprudencia-estrategica-previdenciario` · `estilo-juridico-previdenciario` · `validador-previdenciario` · `suprema-corte-previdenciaria` · `memoria-de-caso-previdenciario` |
| `rpps-servidor-publico` | `previdenciario-master` | `previdencia-complementar` · `memoria-de-caso-previdenciario` |
| `suprema-corte-previdenciaria` | `previdenciario-master` | `validador-previdenciario` · `anti-alucinacao-previdenciario` |
| `triagem-dogmatica-previdenciario` | `previdenciario-master` | — |
| `validador-previdenciario` | `previdenciario-master` · `suprema-corte-previdenciaria` | `base-legal-previdenciaria` · `jurisprudencia-estrategica-previdenciario` · `anti-alucinacao-previdenciario` |
| `visual-law-previdenciario` | `previdenciario-master` · `parecer-previdenciario` · `documentos-extrajudiciais-previdenciarios` · `recursos-previdenciarios` | `calculos-previdenciarios` · `prazos-previdenciarios` · `recursos-previdenciarios` · `validador-previdenciario` · `suprema-corte-previdenciaria` |

## Quem chega a cada skill (inverso de "Chama")

| Skill | Chamada, segundo as outras skills, por |
|---|---|
| `acao-revisional-rmi` | `previdenciario-master` |
| `acidentario-do-trabalho` | `peticao-inicial-previdenciaria` · `previdenciario-master` |
| `administrativo-inss-crps` | `bpc-loas-previdenciario` · `previdenciario-master` |
| `analise-carta-concessao-indeferimento` | `previdenciario-master` |
| `analise-cnis` | `acao-revisional-rmi` · `acidentario-do-trabalho` · `administrativo-inss-crps` · `analise-carta-concessao-indeferimento` · `planejamento-previdenciario` · `previdenciario-master` · `replica-previdenciaria` |
| `analise-ppp-ltcat-aposentadoria-especial` | `analise-carta-concessao-indeferimento` · `analise-cnis` · `planejamento-previdenciario` · `previdenciario-master` |
| `analise-trilateral-previdenciario` | `estrategia-de-caso-previdenciario` · `peticao-inicial-previdenciaria` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` |
| `anti-alucinacao-previdenciario` | `acao-revisional-rmi` · `base-legal-previdenciaria` · `jurisprudencia-estrategica-previdenciario` · `previdenciario-master` · `suprema-corte-previdenciaria` · `validador-previdenciario` |
| `audiencia-previdenciaria` | `previdenciario-master` |
| `base-legal-previdenciaria` | `documentos-extrajudiciais-previdenciarios` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `previdenciario-master` · `recursos-previdenciarios` · `validador-previdenciario` |
| `bpc-loas-previdenciario` | `administrativo-inss-crps` · `previdenciario-master` |
| `calculos-previdenciarios` | `acao-revisional-rmi` · `cumprimento-sentenca-inss` · `documentos-extrajudiciais-previdenciarios` · `estrategia-de-caso-previdenciario` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `peticao-inicial-previdenciaria` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` · `visual-law-previdenciario` |
| `cumprimento-sentenca-inss` | `previdenciario-master` |
| `documentos-extrajudiciais-previdenciarios` | `previdenciario-master` |
| `estilo-juridico-previdenciario` | `acao-revisional-rmi` · `audiencia-previdenciaria` · `cumprimento-sentenca-inss` · `documentos-extrajudiciais-previdenciarios` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `pericia-medica-previdenciaria` · `peticao-inicial-previdenciaria` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` |
| `estrategia-de-caso-previdenciario` | `acao-revisional-rmi` · `parecer-previdenciario` · `peticao-inicial-previdenciaria` · `previdenciario-master` |
| `jurisprudencia-estrategica-previdenciario` | `analise-trilateral-previdenciario` · `estrategia-de-caso-previdenciario` · `parecer-previdenciario` · `peticao-inicial-previdenciaria` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` · `validador-previdenciario` |
| `mandado-seguranca-previdenciario` | `administrativo-inss-crps` · `previdenciario-master` |
| `memoria-de-caso-previdenciario` | `acao-revisional-rmi` · `acidentario-do-trabalho` · `administrativo-inss-crps` · `analise-carta-concessao-indeferimento` · `analise-cnis` · `analise-ppp-ltcat-aposentadoria-especial` · `audiencia-previdenciaria` · `bpc-loas-previdenciario` · `cumprimento-sentenca-inss` · `documentos-extrajudiciais-previdenciarios` · `estrategia-de-caso-previdenciario` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `pericia-medica-previdenciaria` · `peticao-inicial-previdenciaria` · `planejamento-previdenciario` · `previdencia-complementar` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` · `rpps-servidor-publico` |
| `parecer-previdenciario` | `previdenciario-master` |
| `pericia-medica-previdenciaria` | `audiencia-previdenciaria` · `bpc-loas-previdenciario` · `peticao-inicial-previdenciaria` · `previdenciario-master` |
| `peticao-inicial-previdenciaria` | `acidentario-do-trabalho` · `bpc-loas-previdenciario` · `previdenciario-master` |
| `planejamento-previdenciario` | `previdenciario-master` |
| `prazos-previdenciarios` | `acidentario-do-trabalho` · `administrativo-inss-crps` · `analise-carta-concessao-indeferimento` · `audiencia-previdenciaria` · `bpc-loas-previdenciario` · `cumprimento-sentenca-inss` · `documentos-extrajudiciais-previdenciarios` · `estrategia-de-caso-previdenciario` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` · `visual-law-previdenciario` |
| `previdencia-complementar` | `previdenciario-master` · `rpps-servidor-publico` |
| `previdenciario-master` | — |
| `previdenciario-onboarding` | `previdenciario-master` |
| `recursos-previdenciarios` | `documentos-extrajudiciais-previdenciarios` · `previdenciario-master` · `visual-law-previdenciario` |
| `replica-previdenciaria` | `previdenciario-master` |
| `rpps-servidor-publico` | `previdenciario-master` |
| `suprema-corte-previdenciaria` | `acao-revisional-rmi` · `audiencia-previdenciaria` · `cumprimento-sentenca-inss` · `documentos-extrajudiciais-previdenciarios` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `peticao-inicial-previdenciaria` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` · `visual-law-previdenciario` |
| `triagem-dogmatica-previdenciario` | `previdenciario-master` |
| `validador-previdenciario` | `acao-revisional-rmi` · `audiencia-previdenciaria` · `cumprimento-sentenca-inss` · `documentos-extrajudiciais-previdenciarios` · `mandado-seguranca-previdenciario` · `parecer-previdenciario` · `peticao-inicial-previdenciaria` · `planejamento-previdenciario` · `previdenciario-master` · `recursos-previdenciarios` · `replica-previdenciaria` · `suprema-corte-previdenciaria` · `visual-law-previdenciario` |
| `visual-law-previdenciario` | `documentos-extrajudiciais-previdenciarios` · `parecer-previdenciario` · `planejamento-previdenciario` · `previdenciario-master` · `recursos-previdenciarios` |

## Assimetrias

As duas pontas de uma chamada não se citam. Não bloqueia o build ("Chamada por" lista os chamadores principais); serve de leitura para o master e a Corte.

- `acao-revisional-rmi` chama `analise-cnis`, mas `analise-cnis` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `anti-alucinacao-previdenciario`, mas `anti-alucinacao-previdenciario` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `estrategia-de-caso-previdenciario`, mas `estrategia-de-caso-previdenciario` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `estilo-juridico-previdenciario`, mas `estilo-juridico-previdenciario` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `acao-revisional-rmi` em "Chamada por"
- `acao-revisional-rmi` lista `analise-carta-concessao-indeferimento` em "Chamada por", mas `analise-carta-concessao-indeferimento` não lista `acao-revisional-rmi` em "Chama"
- `acidentario-do-trabalho` chama `analise-cnis`, mas `analise-cnis` não lista `acidentario-do-trabalho` em "Chamada por"
- `acidentario-do-trabalho` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `acidentario-do-trabalho` em "Chamada por"
- `acidentario-do-trabalho` chama `peticao-inicial-previdenciaria`, mas `peticao-inicial-previdenciaria` não lista `acidentario-do-trabalho` em "Chamada por"
- `acidentario-do-trabalho` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `acidentario-do-trabalho` em "Chamada por"
- `acidentario-do-trabalho` lista `pericia-medica-previdenciaria` em "Chamada por", mas `pericia-medica-previdenciaria` não lista `acidentario-do-trabalho` em "Chama"
- `administrativo-inss-crps` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `administrativo-inss-crps` em "Chamada por"
- `administrativo-inss-crps` chama `bpc-loas-previdenciario`, mas `bpc-loas-previdenciario` não lista `administrativo-inss-crps` em "Chamada por"
- `administrativo-inss-crps` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `administrativo-inss-crps` em "Chamada por"
- `administrativo-inss-crps` lista `analise-carta-concessao-indeferimento` em "Chamada por", mas `analise-carta-concessao-indeferimento` não lista `administrativo-inss-crps` em "Chama"
- `analise-carta-concessao-indeferimento` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `analise-carta-concessao-indeferimento` em "Chamada por"
- `analise-carta-concessao-indeferimento` chama `analise-ppp-ltcat-aposentadoria-especial`, mas `analise-ppp-ltcat-aposentadoria-especial` não lista `analise-carta-concessao-indeferimento` em "Chamada por"
- `analise-carta-concessao-indeferimento` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `analise-carta-concessao-indeferimento` em "Chamada por"
- `analise-carta-concessao-indeferimento` lista `triagem-dogmatica-previdenciario` em "Chamada por", mas `triagem-dogmatica-previdenciario` não lista `analise-carta-concessao-indeferimento` em "Chama"
- `analise-cnis` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `analise-cnis` em "Chamada por"
- `analise-cnis` lista `triagem-dogmatica-previdenciario` em "Chamada por", mas `triagem-dogmatica-previdenciario` não lista `analise-cnis` em "Chama"
- `analise-ppp-ltcat-aposentadoria-especial` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `analise-ppp-ltcat-aposentadoria-especial` em "Chamada por"
- `analise-ppp-ltcat-aposentadoria-especial` lista `calculos-previdenciarios` em "Chamada por", mas `calculos-previdenciarios` não lista `analise-ppp-ltcat-aposentadoria-especial` em "Chama"
- `audiencia-previdenciaria` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `audiencia-previdenciaria` em "Chamada por"
- `audiencia-previdenciaria` chama `estilo-juridico-previdenciario`, mas `estilo-juridico-previdenciario` não lista `audiencia-previdenciaria` em "Chamada por"
- `audiencia-previdenciaria` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `audiencia-previdenciaria` em "Chamada por"
- `audiencia-previdenciaria` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `audiencia-previdenciaria` em "Chamada por"
- `audiencia-previdenciaria` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `audiencia-previdenciaria` em "Chamada por"
- `bpc-loas-previdenciario` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `bpc-loas-previdenciario` em "Chamada por"
- `bpc-loas-previdenciario` chama `peticao-inicial-previdenciaria`, mas `peticao-inicial-previdenciaria` não lista `bpc-loas-previdenciario` em "Chamada por"
- `bpc-loas-previdenciario` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `bpc-loas-previdenciario` em "Chamada por"
- `cumprimento-sentenca-inss` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `cumprimento-sentenca-inss` em "Chamada por"
- `cumprimento-sentenca-inss` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `cumprimento-sentenca-inss` em "Chamada por"
- `cumprimento-sentenca-inss` chama `estilo-juridico-previdenciario`, mas `estilo-juridico-previdenciario` não lista `cumprimento-sentenca-inss` em "Chamada por"
- `cumprimento-sentenca-inss` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `cumprimento-sentenca-inss` em "Chamada por"
- `cumprimento-sentenca-inss` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `cumprimento-sentenca-inss` em "Chamada por"
- `cumprimento-sentenca-inss` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `cumprimento-sentenca-inss` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `base-legal-previdenciaria`, mas `base-legal-previdenciaria` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `recursos-previdenciarios`, mas `recursos-previdenciarios` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `documentos-extrajudiciais-previdenciarios` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `documentos-extrajudiciais-previdenciarios` em "Chamada por"
- `estrategia-de-caso-previdenciario` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `estrategia-de-caso-previdenciario` em "Chamada por"
- `estrategia-de-caso-previdenciario` lista `triagem-dogmatica-previdenciario` em "Chamada por", mas `triagem-dogmatica-previdenciario` não lista `estrategia-de-caso-previdenciario` em "Chama"
- `mandado-seguranca-previdenciario` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `mandado-seguranca-previdenciario` chama `base-legal-previdenciaria`, mas `base-legal-previdenciaria` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `mandado-seguranca-previdenciario` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `mandado-seguranca-previdenciario` chama `estilo-juridico-previdenciario`, mas `estilo-juridico-previdenciario` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `mandado-seguranca-previdenciario` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `mandado-seguranca-previdenciario` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `mandado-seguranca-previdenciario` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `mandado-seguranca-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `base-legal-previdenciaria`, mas `base-legal-previdenciaria` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `jurisprudencia-estrategica-previdenciario`, mas `jurisprudencia-estrategica-previdenciario` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `estrategia-de-caso-previdenciario`, mas `estrategia-de-caso-previdenciario` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `parecer-previdenciario` em "Chamada por"
- `parecer-previdenciario` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `parecer-previdenciario` em "Chamada por"
- `pericia-medica-previdenciaria` chama `estilo-juridico-previdenciario`, mas `estilo-juridico-previdenciario` não lista `pericia-medica-previdenciaria` em "Chamada por"
- `pericia-medica-previdenciaria` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `pericia-medica-previdenciaria` em "Chamada por"
- `pericia-medica-previdenciaria` lista `acidentario-do-trabalho` em "Chamada por", mas `acidentario-do-trabalho` não lista `pericia-medica-previdenciaria` em "Chama"
- `peticao-inicial-previdenciaria` chama `estrategia-de-caso-previdenciario`, mas `estrategia-de-caso-previdenciario` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `pericia-medica-previdenciaria`, mas `pericia-medica-previdenciaria` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `acidentario-do-trabalho`, mas `acidentario-do-trabalho` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `analise-trilateral-previdenciario`, mas `analise-trilateral-previdenciario` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `jurisprudencia-estrategica-previdenciario`, mas `jurisprudencia-estrategica-previdenciario` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `peticao-inicial-previdenciaria` em "Chamada por"
- `peticao-inicial-previdenciaria` lista `analise-carta-concessao-indeferimento` em "Chamada por", mas `analise-carta-concessao-indeferimento` não lista `peticao-inicial-previdenciaria` em "Chama"
- `planejamento-previdenciario` chama `visual-law-previdenciario`, mas `visual-law-previdenciario` não lista `planejamento-previdenciario` em "Chamada por"
- `planejamento-previdenciario` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `planejamento-previdenciario` em "Chamada por"
- `planejamento-previdenciario` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `planejamento-previdenciario` em "Chamada por"
- `prazos-previdenciarios` lista `triagem-dogmatica-previdenciario` em "Chamada por", mas `triagem-dogmatica-previdenciario` não lista `prazos-previdenciarios` em "Chama"
- `previdencia-complementar` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `previdencia-complementar` em "Chamada por"
- `recursos-previdenciarios` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `analise-trilateral-previdenciario`, mas `analise-trilateral-previdenciario` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `jurisprudencia-estrategica-previdenciario`, mas `jurisprudencia-estrategica-previdenciario` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `base-legal-previdenciaria`, mas `base-legal-previdenciaria` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `recursos-previdenciarios` em "Chamada por"
- `recursos-previdenciarios` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `recursos-previdenciarios` em "Chamada por"
- `replica-previdenciaria` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `analise-cnis`, mas `analise-cnis` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `analise-trilateral-previdenciario`, mas `analise-trilateral-previdenciario` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `jurisprudencia-estrategica-previdenciario`, mas `jurisprudencia-estrategica-previdenciario` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `replica-previdenciaria` em "Chamada por"
- `replica-previdenciaria` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `replica-previdenciaria` em "Chamada por"
- `rpps-servidor-publico` chama `memoria-de-caso-previdenciario`, mas `memoria-de-caso-previdenciario` não lista `rpps-servidor-publico` em "Chamada por"
- `suprema-corte-previdenciaria` chama `anti-alucinacao-previdenciario`, mas `anti-alucinacao-previdenciario` não lista `suprema-corte-previdenciaria` em "Chamada por"
- `visual-law-previdenciario` chama `calculos-previdenciarios`, mas `calculos-previdenciarios` não lista `visual-law-previdenciario` em "Chamada por"
- `visual-law-previdenciario` chama `prazos-previdenciarios`, mas `prazos-previdenciarios` não lista `visual-law-previdenciario` em "Chamada por"
- `visual-law-previdenciario` chama `recursos-previdenciarios`, mas `recursos-previdenciarios` não lista `visual-law-previdenciario` em "Chamada por"
- `visual-law-previdenciario` chama `validador-previdenciario`, mas `validador-previdenciario` não lista `visual-law-previdenciario` em "Chamada por"
- `visual-law-previdenciario` chama `suprema-corte-previdenciaria`, mas `suprema-corte-previdenciaria` não lista `visual-law-previdenciario` em "Chamada por"
