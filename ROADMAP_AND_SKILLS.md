# Roadmap e skills — evolução corporativa

Incremento posterior de 15/10: visual articulado humano/quadrúpede implementado;
plano de pesquisa de reconhecimento real, fontes e licenças de modelos em
[PEOPLE_ANIMALS_RF_RESEARCH](docs/PEOPLE_ANIMALS_RF_RESEARCH.md). R0/R1 pendentes,
sem captura/pesos/loader externos. Skills de design/revisão já selecionadas guiaram
UI, estados, testes e distinção de evidência neste incremento.

Data: 15/10/2026, America/Fortaleza. Subordinado a
[PROJECT_MASTER_PLAN v3.0](docs/PROJECT_MASTER_PLAN.md). Este roteiro organiza a
solicitação atual; não substitui o mestre nem promove pesquisa a produto validado.

**Atualização às 19:44 Fortaleza:** bloqueio Docker resolvido após o Desktop
concluir inicialização. Engine Linux 29.8.2 ativo, stack/restart verificados e
imagem Python 3.13 reconstruída. Linhas BLOCKED abaixo registram o diagnóstico
anterior; resultados atuais em docs/VERIFICATION_REPORT.md e TASKS.md.

## Diagnóstico de continuidade

Branch `feat/platform-foundation`, HEAD inicial `2767417`. Somente o commit inicial
existe no histórico local. Implementação extensa não rastreada; `.idea/.gitignore`
staged preservado. A documentação registra sessões anteriores de desenvolvimento,
mas não estabelece autoria por linha. Sem commit, push, publicação ou serviço pago.

O baseline desta execução divergiu do gate histórico de 135 testes: Ruff falhou
em duas linhas; execução direta encontrou 166 testes backend aprovados e 8 falhas,
e 11 web aprovados e 10 falhas. Os testes novos existentes foram preservados.
Detalhes e resultados finais: [VERIFICATION_REPORT](docs/VERIFICATION_REPORT.md).

## Skills aplicadas e ferramentas

| Fase solicitada | Skill / capacidade | Aplicação concreta | Evidência / saída |
| --- | --- | --- | --- |
| 1 — diagnóstico | engenharia: inspeção de código e histórico | Git, planos, contratos, testes, fontes locais e fonte pública do RuView | logs baseline em artifacts; análise existente preservada |
| 2 — orquestração | `engineering:architecture` | monólito modular, opções, riscos, ADR incremental | ADR-008 em docs/DECISIONS.md |
| 3 — refatoração | `engineering:code-review` | fronteiras HTTP/WS, contratos Python/TS, regressões de estado | api.ts, dashboard.tsx, contratos e testes |
| 3 — UX/performance | `design-skills:design-critique` | heurísticas H1/H3/H9: status confiável, parar sem validar formulário, erros acionáveis | estados de erro e carregamento; bundles separados |
| 4 — produto | análise de valor e desenho de sistemas | priorização por utilidade, risco e custo local | backlog abaixo, propostas distintas de implementação |
| 5 — acompanhamento | `productivity:task-management` | quadro local de tarefas, bloqueios explícitos | TASKS.md; dashboard.html auxiliar |
| 5 — documentação | documentação técnica e rastreabilidade | planos, fontes, comandos e limites de evidência | três artefatos da raiz e relatórios incrementais |

Skills são instruções de trabalho, não plugins necessários ao runtime. Nenhum
conector remoto ou plugin adicional foi instalado. O runtime permanece gratuito
e local. Não foram usados agentes paralelos nesta execução.

## Entrega atual por fase

1. **Diagnóstico executado:** continuidade e inventário; clone existente
   `temp_ruview` reaproveitado, revisão `a1ca023ee872683d160250d47ae3d4d228af55a0`.
   Análise estática; não compilamos nem executamos o código do clone.
2. **Skills selecionadas:** tabela acima; ferramentas disponíveis dispensam
   instalação adicional de plugins e dependências.
3. **Incremento implementado:** tratamento HTTP centralizado no cliente, JSON 500
   sanitizado no backend, compatibilidade de contratos, drift check, correção de
   janela geométrica e comportamento de controle/stream. Verificação final nos
   relatórios; não constitui refatoração total ou certificação enterprise.
4. **Features estruturadas:** backlog com critérios e dependências a seguir.
5. **Artefatos:** análise RuView ampliada sem descartar seu catálogo prévio;
   este roadmap e MASTER_EVOLUTION_PLAN; progresso e decisões atualizados.

## Backlog tático ordenado

| Ordem | Entrega / valor | Implementação proposta | Aceite mensurável | Dependência / estado |
| --- | --- | --- | --- | --- |
| P0 | fechar gate local e contratos | check.ps1, export_contract.py --check; fixtures multiversão | lint, tipos, testes, build, API real/E2E aprovados | incremento atual; resultados no relatório |
| P1 | repetir Docker e Python 3.13 | scripts existentes, portas/bases isoladas | build atual; testes e restart com payloads idênticos | BLOCKED: daemon Docker ausente nesta execução |
| P1 | tour comercial de 3 minutos | roteiro guiado: cenário → pausa → replay → export → experimento → regra dry-run | operador conclui sem limpar dados existentes; evidência L0 em todas as telas | roteiro no MASTER; onboarding em código PLANNED |
| P1 | tipagem Python estática gradual | portas History, Clock e jobs antes de main/storage; adotar checker por módulo | checker sem erros nos módulos incluídos; ampliar sem ignorar tudo | PLANNED; lint não equivale a typecheck Python |
| P2 | separar composition root e rotas | extrair routers por domínio, injetar serviços via Depends | mesmos schemas/status/auth e testes de regressão; nenhum banco novo | PLANNED, pequenos incrementos |
| P2 | comparar sessões e cenários | reutilizar snapshot/end fixo; duas consultas limitadas | mesmas janelas/unidades; delta sintético reproduzível | analytics já existe; comparação PLANNED |
| P2 | pacote de evidência para recrutador/CTO | manifesto com versões, checksum, seed, limites, teste e export | reproduzir resultado sem token, dumps de uso ou dados pessoais | PLANNED |
| P2 | desempenho observado | medir tempo até conexão, p95 de fila, memória, drops e consulta no limite de 10k | baseline repetível e orçamento definido pelos resultados | benchmark PLANNED; nenhuma meta inventada |
| P2 | acessibilidade complementar | fluxo completo teclado, zoom, NVDA e WebKit quando disponíveis | relatório por tecnologia assistiva; axe é parcial | leitor de tela e WebKit pendentes |
| P3 | cursor e índices para histórico | medir EXPLAIN/latência; cursor timestamp+UUID; migração aditiva | ausência de duplicação/perda com timestamp igual e ingestão concorrente | PLANNED; manter offset compatível |
| P3 | observabilidade local | métricas de software e traces sem tokens/payloads | interrupção e backpressure diagnosticáveis; sem export remoto | PLANNED |
| P3 | conectores locais governados | dispatcher separado, allowlist, dry-run, timeout e revogação | nenhuma saída antes de opt-in; testes SSRF/limites/idempotência | regras atuais somente DRY_RUN |
| Pesquisa | hardware e modelos RF | contrato independente, consentimento, parser, ground truth externo | protocolo F6/F7 com evidência observada | hardware NOT_TESTED; vitais/pose/queda BLOCKED |

## Bibliotecas e conectores gratuitos

Sem nova dependência instalada nesta etapa. Prefira a stack existente até haver
necessidade demonstrada. Licença do pacote não inclui automaticamente modelos,
datasets, hardware, hospedagem ou serviços comerciais relacionados.

| Opção | Licença / fonte primária | Utilidade | Condição de adoção |
| --- | --- | --- | --- |
| FastAPI, SQLAlchemy, Alembic, Pydantic; Next/React/Zod | inventário local em docs/THIRD_PARTY_NOTICES.md | contratos, persistência e UI já instalados | manter locks e validar atualizações deliberadas |
| OpenTelemetry Python | [Apache-2.0](https://github.com/open-telemetry/opentelemetry-python/blob/main/LICENSE) | traces locais de consulta/ingestão | collector local opcional; cardinalidade limitada; sem PII |
| prometheus_client | [Apache-2.0](https://github.com/prometheus/client_python/blob/master/LICENSE) | fila, falhas e latência de software | endpoint local protegido; sem rótulos UUID/token |
| Ajv | [MIT](https://github.com/ajv-validator/ajv/blob/master/LICENSE) | executar JSON Schema 2020-12 completo | substituir avaliador subset dos testes quando novo vocabulário exigir |
| MQTT.js | [MIT](https://github.com/mqttjs/MQTT.js/blob/main/LICENSE.md) | cliente de conector MQTT em serviço Node opcional | broker local próprio; não colocar senha no navegador |
| Home Assistant | [documentação MQTT oficial](https://www.home-assistant.io/integrations/mqtt/) | integração opcional de regras de presença | execução local; dry-run anterior ao dispatcher; nenhum cloud obrigatório |

As fontes de licença foram consultadas nesta execução. Versões candidatas,
vulnerabilidades e licenças transitivas exigem nova avaliação antes da instalação.
Não habilitar cloud, contas, billing, Codex/LLM ou runtimes upstream no produto.

## Operação e encerramento

Os comandos oficiais continuam no README. `scripts/verify/check.ps1` agora também
recusa schemas/fixtures desatualizados sem sobrescrevê-los. Docker, Python 3.13 e
laboratório RuView devem ser verificados separadamente quando disponíveis.
Trabalho futuro tem prioridade explícita no quadro local; entregas desta etapa
estão registradas com suas evidências, sem confundir backlog com implementação.
