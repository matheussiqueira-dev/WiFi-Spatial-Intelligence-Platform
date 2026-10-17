# Relatório técnico do marco v3.0

> **Snapshot histórico (15/10/2026, tarde).** Fases e contagens abaixo refletem aquele
> marco; F3B/F4/F5/F6 avançaram depois. Estado vigente: docs/PROGRESS.md,
> docs/VERIFICATION_REPORT.md e docs/DECISIONS.md (ADR-010/011). docs/docs/ é cópia
> idêntica do plano, não normativa.

15/10/2026, America/Fortaleza. Fonte normativa única: PROJECT_MASTER_PLAN.md,
29.666 bytes, cabeçalho v3.0, seção 4 Clean Room Design e fases F0R/F1R/F2R
confirmadas por leitura integral. SHA-256:
2dd0b492dd94bff52cb9eb2d22a9de5fa116c367405755a90493595c3ce36ad7.
docs/docs/ contém duplicação histórica v2 e não foi usada como requisito vigente.

## 1. Arquivos e funcionalidades

Os arquivos do produto já eram majoritariamente não rastreados. Git não permite
reconstruir retrospectivamente um diff por sessão; este inventário identifica os
arquivos trabalhados e deve ser lido junto à matriz e aos testes.

| Arquivos/grupo | Entrega |
| --- | --- |
| apps/api/app/domain/acquisition.py, ports/clock.py, adapters/native.py, adapters/providers.py | Gerador próprio determinístico, oito cenários virtuais, relógio por porta, composição nativa; legado lazy/off |
| apps/api/app/ports/history.py, application/read_history.py, adapters/history.py | Leitura de histórico por caso de uso e adaptador SQLite |
| apps/api/app/config.py, contracts.py, pipeline.py, main.py, ruview.py | Contrato nativo 2.0.0 aditivo, seleção protegida, API autenticada, métricas reais de software, compatibilidade legada opt-in |
| apps/api/app/analytics.py, storage.py, migrations/versions/0002_analytics.py | Agregações temporais, filtros, paginação, intervalos/transições, replay, CSV, relatórios SQLite e migração sem sobrescrever payload |
| apps/web/src/lib/analytics.ts, contracts.ts, components/analytics-panel.tsx, dashboard.tsx, observatory.tsx, app/globals.css | Dashboard com API real, filtros UTC/local, gráficos/tabelas, playback 2D, relatórios, export JSON/CSV, acessibilidade e correção mobile |
| packages/contracts/*analytics*, *native*, streaming-event.schema.json | Schemas e fixtures versionados Python/TypeScript |
| apps/api/app/maintenance.py, scripts/backup/*, compose*.yaml, apps/web/next.config.ts | Backup/restore separado, checksum/integridade, retenção protegida, logs rotativos, stack nativa isolada e CSP |
| apps/api/tests/test_analytics.py, test_native_domain.py, test_api.py, test_ruview.py; apps/web/tests/*; apps/web/e2e/* | Testes novos de contratos/analytics/domínio/backup/migração/UTC-DST/limites, regressões MVP/legado e UI real |
| apps/api/pyproject.toml, requirements.*; scripts/verify/*; package*.json, apps/web/package.json | Compatibilidade TestClient/httpx2, locks, verificação 3.13, inventário, Docker E2E e smoke de persistência/manutenção |
| README.md, CLAUDE.md, .env.example, docs/* | Instruções de operação nativa, rastreabilidade, evidências, procedência, decisões, segurança e backup |

Não há novas medições RF ou inferência clínica. Todos os eventos gerados mantêm
L0_SYNTHETIC. Entradas/saídas são deltas líquidos quando distinguíveis entre
amostras contínuas; lacunas viram unknown, sem identificação de indivíduos.

## 2. Estado das fases

| Fase | Estado observado | Limites |
| --- | --- | --- |
| F0R | Auditoria técnica executada | Fonte original dos 68 warnings não disponível: UNVERIFIED |
| F1R | PARTIAL: estabilização, auth, backup/restore, retenção e gates executados | Firefox/WebKit/NVDA BLOCKED; rate limit HTTP geral e auditoria completa de negativas auth pendentes |
| F2R | IMPLEMENTED_SYNTHETIC operacional; procedência PARTIAL | Motor nativo independente em execução; separação clean-room estrita não certificada; legado preservado/off |
| F3A | IMPLEMENTED_SYNTHETIC no escopo de uma sala/fonte agregada | Analytics históricos/API/SQLite/playback/export funcionais; sem cruzamentos individuais, cursores ou rollups incrementais |
| F3B | Não iniciada como classificador | Cenários gerados não são reconhecimento de atividade nem RF fingerprint |
| F4 | BLOCKED para inferência validada | Nenhum modelo/dataset/referência clínica; laboratório de treino não implementado |
| F5 | PARTIAL somente na governança existente | Automações, RBAC e consentimento expandido pendentes |
| F6 | Hardware NOT_TESTED | Nenhum dispositivo ativado, firmware carregado ou compra |
| F7 | BLOCKED | Requer autorização específica, dispositivos e referências experimentais |

M01–M16 e vínculos a testes: REQUIREMENTS_TRACEABILITY.md. Não se declara
conformidade integral com toda a v3.0 nem validação científica.

## 3. Independência em relação ao RuView

Domínio Acquisition usa apenas stdlib; teste AST verifica a fronteira. Processo
novo testa startup sem importar app.ruview. NativeProvider produz contrato próprio
2.0.0. Flag SPATIAL_LEGACY_LAB_ENABLED=false bloqueia seleção legada por padrão.
Compose normal contém API/web sem serviço RuView obrigatório. Stack nativa foi
executada com API, WS, dashboard, SQLite e reinício real: 24 payloads, replay e
relatório preservados; native_default_after_restart=true e legacy_enabled=false.

Isso demonstra independência operacional. ORIGINALITY_REGISTER.md registra a
exposição anterior ao código legado; não há evidência para prometer clean-room
estrita ou originalidade jurídica absoluta. FUNCTIONAL_SPEC.md, DECISIONS.md e
THIRD_PARTY_NOTICES.md registram especificação, decisões e dependências.

## 4. Verificações executadas

| Verificação | Resultado e limite temporal |
| --- | --- |
| check.ps1 final Windows Python 3.12.10 | exit 0: 111 backend, 10 web, Ruff, ESLint, TypeScript strict, build Next e 2 E2E Chromium; 1 legado skipped |
| Docker Python 3.13.16 atualizado | exit 0: 111 backend, Ruff e pip-audit dos dois locks sem vulnerabilidades conhecidas |
| check.ps1 -RuView em 4970/4971 | exit 0: 110 backend, 10 web e 3 E2E; anterior à última correção temporal/teste adicional |
| Docker E2E nativo | exit 0: 2 E2E; última execução com navegador anterior à correção temporal |
| Docker smoke após correção temporal | exit 0: builds e reinício, 24 payloads idênticos, snapshot/replay preservados |
| Backup/restore | Wrappers PowerShell e testes sobre fixtures: integridade/payload e recusa de sobrescrita comprovados |
| npm audit | exit 0: sem vulnerabilidades conhecidas nas 231 dependências reportadas |
| Acessibilidade | axe, teclado, foco e largura 320 px aprovados no Chromium; Firefox/WebKit/NVDA não executados |

Comandos, durações, versões e falhas intermediárias: VERIFICATION_REPORT.md.
Nenhuma execução parcial é contada como suíte aprovada.

## 5. Falhas, warnings e regressões

Corrigidos: Ruff E501; depreciação TestClient/httpx; UTC +00:00 recusado pelo
schema; composição TS de literais; seletor E2E ambíguo; overflow mobile; precisão
SQLite submilissegundo; corrida de teardown WebSocket em Python 3.13 (execução
intermediária 110 pass/1 fail, seguida de 111 pass após sincronização).

Residual observado: WinError 10054/Proactor ao forçar interrupções de stream no
Windows; recuperação e gates passaram, erro não foi ocultado. NO_COLOR/FORCE_COLOR
e pip root em build descartável são informativos. Não foi demonstrada regressão
funcional nos cenários exercitados; isso não prova ausência de defeitos fora deles.
Não existe fonte para classificar individualmente os 68 warnings da IDE.

## 6. Pendências priorizadas

1. P1 operacional: definir frequência/responsável e executar backup recorrente no
   ambiente de uso; scripts estão prontos, nenhum scheduler global foi instalado.
2. P2: investigar Proactor 10054 se reproduzido fora de interrupções forçadas;
   concluir Firefox/WebKit e leitor de tela quando disponíveis.
3. P2 segurança: rate limit HTTP geral, trilha de negativas auth e CSP com nonce;
   RBAC/TLS/consentimento antes de qualquer expansão além do uso local autorizado.
4. P2: obter logs dos 68 warnings; revisão independente de origem/licenças caso
   seja exigida separação clean-room estrita. Não remover legado sem migração segura.
5. Escala: filtros por sensores reais quando existirem, cursores/rollups e
   benchmarks de carga/RAM/CPU; export atual é paginado e consulta limitada a 10k.
6. Próxima fase funcional F3B: especificação/testes de baseline experimental,
   datasets separados e incerteza; captura real continua condicionada à autorização.

## 7. Git e preservação

Branch feat/platform-foundation, HEAD 27674175866b0d0e20b10ddee30ab33268134d84.
Único staged: .idea/.gitignore, 10 adições, preservado. Nenhuma alteração unstaged
em arquivo já rastreado. Implementação e documentação são arquivos untracked;
119 arquivos no fechamento (git ls-files --others --exclude-standard).
Portanto a árvore não está limpa.
Nenhum stage adicional, commit, push, reset, clean, descarte ou exclusão de volume.
Segredos, SQLite, runtime, logs, venv e artifacts permanecem ignorados.
