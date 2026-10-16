# Rastreabilidade de requisitos e evidências

## Apresentação de pessoas/animais e pesquisa posterior — 15/10/2026

| Requisito | Código / evidência | Limite |
| --- | --- | --- |
| Estruturas e volume visíveis | lib/scene-rig.ts, articulated-scene.tsx; scene-rig.test.ts | matemática procedural, não pose detectada |
| Elenco humano/cão/gato/misto | observatory.tsx, e2e/avatars.spec.ts | preferência local; não classificação de espécie ou mudança de contagem |
| Pausa, replay e posições compatíveis | evento/tick existente, testes Observatory e E2E | não inventar posições RuView nem criar tracking de identidade |
| Movimento reduzido e mobile | matchMedia, toggles rotulados, E2E 320 px/axe | leitor de tela manual não executado |
| Tela cheia e planta 2D | Fullscreen API e SVG original; teste de entrar/sair e largura | projeção isométrica; sem orbit/oclusão física |
| Reconhecimento RF futuro | PEOPLE_ANIMALS_RF_RESEARCH.md | R0/R1 pendentes; HF MIT encoder não é modelo de pose; MM-Fi NC fora do produto comercial |

Gate: 175 backend, seis launchers, 25 web, oito E2E Chromium; caso novo Firefox.
Docker: seis E2E e 13 payloads preservados no reinício. Resultados finais de layout
e falhas/limites detalhados em VERIFICATION_REPORT.md. Sem promoção para L3.

Atualização 15/10/2026, 19:45 Fortaleza: Docker deixou de estar BLOCKED. Stack
nativa reconstruída, cinco E2E e restart com 12 payloads preservados; Python 3.13
reconstruído com 175 backend/seis launchers, Ruff e auditorias aprovados. Três E2E
skipped na stack externa por escopo. Comandos e limitações no relatório vigente.

## Evolução corporativa — 15/10/2026

| Requisito / domínio | Implementação e teste | Evidência atual / limite |
| --- | --- | --- |
| Continuidade F0R | Git, mestre v3, progresso e baseline | sem descarte, staged IDE preservado; logs enterprise-* |
| Contratos / M15 | contracts.py, lib/contracts.ts, export_contract.py; test_contract_invariants.py e contracts.test.ts | fixtures multiversão e --check; 175 backend/21 web no gate |
| Recuperação da demo | lib/api.ts, dashboard.tsx, analytics-panel.tsx; api.test.ts e recovery.spec.ts | merge temporal, erros tipados, CSV comum, controles e close 4002; 7 E2E Chromium |
| Erro global HTTP | main.py; test_error_boundary.py | JSON 500/no-store sanitizado e health posterior |
| Identidade do peer / F1R | start.ps1, playwright.config.ts, Dockerfile; scripts/verify/tests/test_launchers.py | seis casos Red/Green; headers falsos não alteram peer |
| M06 baseline geométrico | domain/motion.py; test_motion_lab.py | primeiro ponto fora da sala causa abstenção; não valida RF |
| Fases 1–5 da solicitação atual | RUVIEW_FEATURES_ANALYSIS, ROADMAP_AND_SKILLS, MASTER_EVOLUTION_PLAN | análise preservada/ampliada, decisões e código próprio, backlog com aceite |
| Containers e Python 3.13 | Dockerfile.verify e linux_checks.py preparados | BLOCKED nesta execução: daemon Docker ausente |

Rastreabilidade qualitativa, sem percentual de cobertura. Resultados dos browsers
finais e falhas intermediárias estão em VERIFICATION_REPORT; M04/M05/M07/M09/M10/
M11/M14 continuam sem validação física/clínica. Nenhuma capacidade L3 fabricada.

## Gate integrado — 15/10/2026, 15:10

| ID | Código | Teste/comando observado | Estado / lacuna |
| --- | --- | --- | --- |
| G (F3B) | domain/motion.py, application/model_lab.py, 0004, model-lab-panel.tsx | test_motion_lab.py; model-lab.spec Chromium/Firefox/Docker | IMPLEMENTED_SYNTHETIC; sitting/queda/RF BLOCKED |
| F4 jobs | application/experiment_jobs.py, 0006 | test_experiment_jobs.py (fila, falha, cancelamento, interrupted) | PARTIAL; vitais/pose/sono BLOCKED |
| F5 regras | domain/rules.py, rule_contracts.py, 0005, automation-panel.tsx | test_rules.py; automation.spec Chromium/Firefox/Docker | PARTIAL dry-run; RBAC/consentimento/webhook pendentes |
| F6 pacotes | domain/packet_lab.py | test_packet_lab.py (fuzz 200 bytes) | PARTIAL offline, sem API/UI; hardware NOT_TESTED |
| Gate | check.ps1, docker-e2e.ps1, Dockerfile.verify 3.13 | 135 backend (3.12 e 3.13), 11 web, 10 E2E Chromium+Firefox, smoke Docker | Exit 0 em todos; WebKit/NVDA BLOCKED |

## Roteiro EXECUTION_PLAN_V3 — execução de 15/10/2026

C1/C2: 8 testes específicos aprovados; negativos incluem timeout, malformado,
origem, capacidade WS e sentinelas. C3: proxy.ts/force-dynamic, teste security.spec
negativo aprovado Chromium/Firefox, nonce diferente por resposta. D: 6 E2E
Chromium/Firefox (2 skips legado); WebKit BLOCKED DLL e NVDA ausente. G: motion.py,
application/model_lab.py, migration 0004, lab_contracts.py, model-lab-panel.tsx;
test_motion_lab.py e contratos/E2E específicos em validação integrada.

| ID | Código | Teste/comando observado | Estado / lacuna |
| --- | --- | --- | --- |
| A | check.ps1, inventário Git | check.ps1 exit 0: 111 backend/10 web/2 E2E | IMPLEMENTED_SYNTHETIC; warnings IDE sem lista |
| B1/B2 | recurring_backup.py, config/main, .env.example | test_recurring_backup.py: 5 pass; fixture sob escrita restaurada | IMPLEMENTED_SYNTHETIC opt-in observado em fixtures; inativo no uso padrão |
| C1/C2 | security.py, storage.py, migration 0003, main.py | test_local_security.py + test_api.py: 18 pass | PARTIAL, completar negativas/CSP e gates |

Registros anteriores abaixo preservam evidências históricas; não substituem os
resultados de cada novo marco.

## Matriz vigente — mestre v3.0 — 15/10/2026

Fonte única: docs/PROJECT_MASTER_PLAN.md, cabeçalho v3.0, seções 3/4 e
F0R/F1R/F2R/F3A lidas integralmente. SHA-256
2dd0b492dd94bff52cb9eb2d22a9de5fa116c367405755a90493595c3ce36ad7.
Branch feat/platform-foundation, HEAD 2767417, dirty; IDE staged preservado.
Fechamento do marco que originou esta matriz (registro): 111 testes backend Windows
e 111 Python 3.13, 10 web; lint/tipos/build aprovados. Dois E2E nativos no check
final; laboratório legado separado teve três. Docker: 24 payloads/replay/relatório
preservados após reinício. Auditorias npm e ambos os locks Python sem
vulnerabilidades conhecidas. Contagens atuais: gate integrado no topo deste arquivo
e VERIFICATION_REPORT.md; TECHNICAL_REPORT_V3.md é síntese do marco anterior.
Linhas F1R-02/03/04, M06, M12 e M13 atualizadas ao gate integrado de 15:10.
Tabelas AUD-* abaixo são **registro histórico anterior**, não a matriz normativa
atual. A numeração M01–M16 v3 difere da v2; usar somente a tabela vigente.

| ID | Requisito | Código | Testes | Evidência | Status | Lacunas | Responsável |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F0R-01 | Inventário e recuperação baseline | manifests, check.ps1, docs | suítes existentes e novas | lint E501 reproduzido/corrigido; Git/versões inspecionados | IMPLEMENTED_SYNTHETIC | 68 warnings originais sem fonte verificável | Agente / proprietário para logs |
| F1R-01 | Backup consistente/restore separado | maintenance.py, scripts/backup | test_sqlite_backup_restore_integrity_and_guarded_retention; maintenance_smoke.py | checksum, integrity_check, payload exato e recusa de sobrescrita | IMPLEMENTED_SYNTHETIC | Sem scheduler global; operador executa rotina | Proprietário |
| F1R-02 | Retenção controlada | storage.py (security_denial), migração 0003, maintenance.py, logging/Compose | test_snapshot_retention_and_rotating_logs; test_local_security.py; retenção existente | sete snapshots/30 dias; auditoria 90 dias, arquivo+backup/hold; negativas agregadas; logs limitados | IMPLEMENTED_SYNTHETIC | Sem WORM/RBAC; negativas só como contadores agregados de nove tipos (sem token/IP/payload), sem histórico individual; `retain` não verifica se a API está parada | Agente |
| F1R-03 | Autorização, WS/CORS, CSP | main.py, security.py (LocalLimiter), apps/web/src/proxy.ts (CSP com nonce), next.config.ts (demais headers) | testes auth/origin/limites; test_local_security.py; E2E dashboard e security.spec.ts | Bearer em memória, origem negada, limite auth/write/read por peer, nonce por resposta e script sem nonce bloqueado | IMPLEMENTED_SYNTHETIC | style-src 'unsafe-inline' mantido (ADR-006); limiter local por processo, zerado no reinício, não é controle de serviço público; sem TLS/RBAC | Agente |
| F1R-04 | Compatibilidade e acessibilidade | Dockerfile.verify, e2e, CSS/ARIA | Python 3.12/3.13, teclado/axe/320 px; E2E Chromium/Firefox | comandos/resultados no relatório | PARTIAL | WebKit (DLL ausente) e NVDA BLOCKED; validação manual assistiva BLOCKED | Proprietário / ambiente |
| F2R-01 | Domínio próprio e portas | domain/acquisition.py, ports, adapters/native.py, application/read_history.py | test_native_domain.py | Red observado (4 falhas), Green; AST sem framework/ORM/legado | IMPLEMENTED_SYNTHETIC | Extração de outros contextos é incremental | Agente |
| F2R-02 | Contrato próprio compatível | NativeEvent 2.0.0, Zod, packages/contracts | native.test.ts, contracts.test.ts, migração legada | 1.0/1.1/2.0 legíveis, L0 preservado | IMPLEMENTED_SYNTHETIC | Não há observação real | Agente |
| F2R-03 | Produto sem motor externo obrigatório | adapters/providers.py, pipeline.py, config.py, Compose | test_default_startup_does_not_import_legacy_engine; test_legacy_is_off_by_default; Docker E2E | default synthetic-native; legado off; somente API/web na stack normal | IMPLEMENTED_SYNTHETIC | Arquivos legados preservados, não removidos | Agente |
| F2R-04 | Procedência e separação clean-room | ORIGINALITY_REGISTER, FUNCTIONAL_SPEC, THIRD_PARTY_NOTICES, DECISIONS | inventário de imports/licenças | origem declarada e exposição anterior documentadas | PARTIAL | Sem implementador isolado/revisão jurídica; não certificar independência absoluta | Proprietário / revisão independente |
| F3A-01 | Janelas, UTC, filtros e paginação | analytics.py, storage.py, main.py, migration 0002 | test_analytics.py, analytics.test.ts | fixtures determinísticas, reorder/duplicação, limites, UTC/DST | IMPLEMENTED_SYNTHETIC | Filtro por fonte agregada; sem streams por nó virtual | Agente |
| F3A-02 | Intervalos, ocupação e deltas | aggregate, UI analytics | fixtures de unknown/gap/segment/tick | contagem null preservada, deltas líquidos, sem identidade | IMPLEMENTED_SYNTHETIC | Entradas/saídas individuais não distinguíveis; não alegadas | Agente |
| F3A-03 | Replay, export e relatórios duráveis | replay API, analytics_reports, analytics-panel | E2E analytics, reabertura SQLite, native_compose_smoke | seek/play/pause, JSON/CSV, snapshot/replay após restart | IMPLEMENTED_SYNTHETIC | Export por página; sem rollup incremental/cursor | Agente |
| F3A-04 | Métricas observadas de software | pipeline.status metrics, latência persistida | testes de backpressure/falha; UI/E2E | taxa, fila, espera p50/p95, descartes visuais, last-seen/reconexões | IMPLEMENTED_SYNTHETIC | Perda/qualidade RF null; sem CPU/RAM fabricados | Agente |
| LEGACY-F2 | Compatibilidade histórica opt-in | ruview.py e scripts legados | test_ruview.py e E2E oficial -RuView | execução real da imagem fixa em portas alternativas; retorno ao nativo | INTEGRATED_LEGACY | Não é motor próprio nem dependência obrigatória | Agente |

## Catálogo M01–M16 v3.0

| ID | Requisito | Código | Testes | Evidência | Status | Lacunas / prioridade | Responsável |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | Presence | domain, aggregate, dashboard | native/analytics/E2E | presença e intervalos históricos L0 | IMPLEMENTED_SYNTHETIC | Sem referência real; F3A | Agente |
| M02 | Occupancy | NativeEvent, analytics | contratos/fixtures/E2E | contagens/agregações L0 | IMPLEMENTED_SYNTHETIC | Sem MAE real; F3A | Agente |
| M03 | Entries/exits | aggregate.transitions | unknown/gap/deltas | estimativas líquidas exibidas | PARTIAL | Não comprova cruzamentos individuais; F3A | Agente |
| M04 | Respiratory rate | nenhum estimador | models/validation negativos existentes | sem modelo/medida disponível | BLOCKED | Referência/dados/estimador; F4 | Proprietário / pesquisa |
| M05 | Heart rate | nenhum estimador | models/validation negativos | sem medida disponível | BLOCKED | Dados/referência; F4 | Proprietário / pesquisa |
| M06 | Activity recognition | domain/motion.py (baseline geométrico walking/stationary sobre trajetória sintética), cenários de movimento | test_motion_lab.py; model-lab.spec | baseline G mede tarefa artificial L0, não atividade humana | PARTIAL | Atividade humana real, sitting e queda BLOCKED; labels/dados reais/avaliação; F3B/F7 | Agente / pesquisa |
| M07 | Fall detection | não implementado | nenhum teste de detector | nenhuma alegação de detecção | BLOCKED | Dados e protocolo de falso alarme; F3B/F4 | Pesquisa |
| M08 | RF fingerprints | não implementado | nenhum teste de RF | sem CSI capturado | BLOCKED | Dataset/calibração; F3B | Pesquisa |
| M09 | Sleep quality | não implementado | nenhum teste de sono | sem inferência | BLOCKED | Dataset/referência; F4 | Pesquisa |
| M10 | Apnea screening | não implementado | nenhum teste clínico | sem diagnóstico | BLOCKED | Estudos/referência; F4 | Pesquisa |
| M11 | 17-keypoint pose | não implementado | nenhum teste de pose | sem pose alegada | BLOCKED | Modelo/dados/avaliação; F4 | Pesquisa |
| M12 | Model lab/CSI/LoRA/RVF | application/model_lab.py, application/experiment_jobs.py, migrações 0004/0006, /api/v1/model-lab/*; /api/v1/models segue sem modelo de inferência | test_motion_lab.py; test_experiment_jobs.py; test_auth_origin_and_validation; model-lab.spec | registro de runs e fila CPU local com modelos JSON internos sintéticos | PARTIAL | CSI/ONNX/LoRA/RVF e upload de modelo BLOCKED; sem dados reais; F4 | Agente / pesquisa |
| M13 | Home automation/hooks | domain/rules.py, rule_contracts.py, migração 0005, /api/v1/automation/*, automation-panel.tsx | test_rules.py; automation.spec | decisões DRY_RUN com dispatched=false; sem ações externas | PARTIAL | Somente dry-run; webhooks/Home Assistant/plugins, RBAC e consentimento não implementados; F5 | Agente |
| M14 | Multimodal world model | laboratório 2D sintético, sem fusão | observatory/E2E | representação virtual | PARTIAL | Sensores/calibração/fusão; F7 | Pesquisa |
| M15 | Governed evidence/privacy | contratos, auth, auditoria/backup | segurança/retenção/restore | L0, token em memória, backup verificado | PARTIAL | Consentimento/RBAC real e witness não implementados; F5 | Proprietário / agente |
| M16 | Operator onboarding/calibration | bootstrap e guias locais | instalação histórica / smoke atual | operação virtual documentada | PARTIAL | Calibração física/onboarding dispositivos; F5/F6 | Proprietário |

VALIDATED_REAL_DATA não foi atribuído a nenhum item. F3B/F4/F5/F6/F7 não foram
declaradas concluídas. Relatório técnico e comandos: VERIFICATION_REPORT.md.

---

## Registro histórico anterior à disponibilização do plano

Auditoria de 15/10/2026 (America/Fortaleza), branch `feat/platform-foundation`.

## Referência e classificação

`docs/PROJECT_MASTER_PLAN.md` v2.0 não existe no workspace inspecionado. Sua
localização foi solicitada ao responsável. Não foi possível ler a atualização
operacional, o backlog ou os critérios oficiais dessa versão. Os identificadores
`AUD-*` abaixo são locais desta auditoria: **não são requisitos do mestre**.
F0/F1/F2 correspondem ao escopo provisório já registrado em PROGRESS e
PHASE_RECONCILIATION. Conformidade formal com a v2.0: **pendente**.

No encerramento, o responsável confirmou que a v2.0 também não está disponível
no GitHub e determinou concluir somente as verificações técnicas existentes.
Essas verificações foram concluídas conforme o relatório. A F3A permanece sem
implementação nesta etapa; nenhum requisito ou critério foi presumido.

"Verificado" significa execução técnica do escopo descrito, sempre com dados
`L0_SYNTHETIC`. Não significa validação científica, clínica ou de hardware.
Detalhes de execução e falhas estão em [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md).

## Matriz técnica F0/F1/F2

| ID local | Fase provisória / critério observado | Implementação | Evidência executada em 15/10 | Resultado / limite |
| --- | --- | --- | --- | --- |
| AUD-01 | F0: arquitetura existente | apps/api/app, apps/web/src, package-lock.json, requirements.* | Ruff, pytest Windows/Linux, lint/tipos web, build Windows/Docker | Verificado; instalação limpa do bootstrap não repetida |
| AUD-02 | F0: segredos locais | config.py, .gitignore, .dockerignore, dashboard.tsx | git ls-files e git check-ignore; E2E token incorreto/correto e storages vazios | Verificado no uso local; sem login multiusuário |
| AUD-03 | F0: autenticação e origens | main.py authorize/stream | test_auth_origin_and_validation, test_websocket_rejects_untrusted_access, test_websocket_rejects_malformed_auth | Verificado; WS autentica no primeiro frame |
| AUD-04 | F0: limite/liberação de sockets | main.py stream | test_websocket_connection_limit: oito aceitos, nono recusado, liberação e reutilização | Corrida do teardown do TestClient encontrada e sincronização corrigida; ver relatório |
| AUD-05 | F0: isolamento de infraestrutura | compose*.yaml, Dockerfiles, scripts/common.ps1 | check.ps1 -RuView; ruview-compose.ps1; inspeção de portas, usuários e volumes | Stack isolada healthy; volume preservado; uso público fora do escopo |
| AUD-06 | F0: persistência/migrações | storage.py, migrations/0001_events.py | testes de retenção/reabertura; reinício real Compose | Oito eventos no recibo, payloads idênticos após reinício |
| AUD-07 | F0: dependências | package-lock.json, requirements.runtime.txt, requirements.lock.txt | npm audit --json; pip-audit nos dois locks em Linux | Zero vulnerabilidades conhecidas nas consultas desta execução |
| AUD-08 | F1: oito cenários sintéticos | simulator.py, SimulationConfig | test_scenarios_are_bounded_synthetic_and_reproducible, oito cenários × 0/2/20 ocupantes | Verificado; nenhuma modelagem física de CSI |
| AUD-09 | F1: contrato/proveniência | contracts.py, packages/contracts, lib/contracts.ts | testes Pydantic/Zod e fixtures Python; rejeição de falsa inferência/evidência | SIMULATED/L0_SYNTHETIC preservados |
| AUD-10 | F1: controles e concorrência | pipeline.py control/control_lock | test_control_pause_stop_history_and_audit, E2E MVP | Pausa/parada sem crescimento; exclusão bloqueada durante execução |
| AUD-11 | F1: gravação antes de transmissão | pipeline.py consume, storage.py write | test_websocket_stream_auth_and_persistence; falha injetada; assinante lento | Persistência comprovada; sem publicar sucesso quando o banco falha |
| AUD-12 | F1: dashboard/histórico | dashboard.tsx, observatory.tsx | E2E autenticação, WS, presença, sensores, paginação, recarga e exclusão | Verificado com API real e banco temporário |
| AUD-13 | F1/F2: acessibilidade e mobile | dashboard.tsx, observatory.tsx | axe desktop/mobile e viewport 390 × 844 no E2E; três regressões de renderização | Correção de contagem desconhecida no nome acessível; leitores de tela manuais pendentes |
| AUD-14 | F2: execução do motor oficial | compose.ruview.yaml, start-ruview.ps1 | REST/WS reais da imagem fixada; E2E oficial | Verificado em simulated/synthetic, sem hardware |
| AUD-15 | F2: normalização e rejeições | ruview.py, RuViewEvent 1.1.0 | test_captured_official_contract, test_rejects_untrusted_contract, test_no_fabricated_count_or_ground_truth | null preservado; posições, confiança e modelo não fabricados |
| AUD-16 | F2: fronteira de rede | config.py, NoRedirect, LocalConnect | testes de URL, redirects, origem do frame e token upstream incorreto | Destinos locais, sem proxies/redirects; token separado |
| AUD-17 | F2: falhas e recuperação | ruview.py next_event/diagnostics | injeções de freeze, oversize, JSON inválido, indisponibilidade; pausa/despausa do container oficial no E2E | Reconexão comprovada, sem fallback silencioso |
| AUD-18 | F2: seleção/controles/histórico misto | sources/select, pipeline.py, Zod | teste integrado de transporte e troca; E2E oficial | Troca somente parada; ambos os contratos preservados |
| AUD-19 | F2: deduplicação e reinício | storage.py write, UUID RuView | test_duplicate_frames_are_not_persisted; test_replay_is_idempotent_after_database_reopen; Compose | Deduplicação e reinício real verificados |
| AUD-20 | Governança/evidências | contracts.py, validation/governance/features/providers | inspeção de endpoints e testes de proveniência | Capacidades reais indisponíveis; sem promoção de simulação a evidência real |

## Requisitos ainda não reconciliáveis

| Item | Estado | Próxima ação necessária |
| --- | --- | --- |
| Identificadores e critérios oficiais F0/F1/F2 da v2.0 | Pendente de fonte | Disponibilizar o mestre; mapear cada requisito à implementação e ao teste, registrando atendido/parcial/pendente |
| Atualização operacional v2.0 | Pendente de fonte | Comparar instruções oficiais com scripts e limites atuais |
| F3A — Advanced Spatial Analytics | Bloqueada por especificação ausente | Ler escopo, métricas, contratos, persistência e critérios da v2.0 antes de implementar |
| Backlog posterior à F3A | Desconhecido | Extrair prioridades do mestre, sem inferir módulos a partir do título da fase |
| Backup/expurgo, multiusuário e múltiplos workers | Limites existentes, sem alteração de política | Reconciliar prioridades com o mestre; nenhum histórico de uso foi apagado |
| Python 3.13, outros navegadores e leitores de tela | Validação pendente | Executar nos ambientes correspondentes conforme critérios oficiais |

Nenhuma aprovação formal de fase ou conclusão do backlog é concedida por esta matriz.
