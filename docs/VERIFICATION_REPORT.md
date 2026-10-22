# Relatório de verificação

## Perfis de acesso locais (Claude Code) — 17/10/2026

| Comando / inspeção | Resultado |
| --- | --- |
| `test_access_roles.py` | 21 pass: toda rota autenticada declara um papel após `authorize` e antes da capacidade; política de escrita igual à matriz declarada; matriz papel × rota executada em todas as rotas (403 só abaixo do mínimo); 401 antes do papel; papel antes do perfil commercial-br; `/access/me`; token ausente do dump SQLite/listagem/governança e hash = HMAC com chave do servidor; revogação imediata e idempotente; `actor_id`/`subject_id` na auditoria; `role.denied` agregado; validação de rótulo/papel; limite de ativos; viewer assiste ao stream e revogação fecha 1008; token revogado recusado no WS; rotação do bootstrap invalida tokens derivados; chave explícita sobrevive |
| Testes web | 43 pass (4 novos em `access.test.ts`, 403 em `api.test.ts`) |
| `e2e/access-roles.spec.ts` | admin emite token viewer pela UI (axe sem violações); viewer vê selo de papel, stream ao vivo, nenhum botão de escrita nem seção admin, sem storage/URL com token, mobile sem overflow, axe sem violações; API 403; revogação → alerta 401 e stream "Acesso recusado" |
| Red no gate (1ª execução) | 8 E2E (4 × 2 navegadores): `[hidden]` inserido numa lista de seletores escondia `.network-controls` e selo alargava o mobile; corrigido |
| `check.ps1` final | exit 0: Ruff/format, mypy (59), contratos, 320 backend, 6 launchers, Prettier, 43 web, ESLint, tsc, build, 20 E2E Chromium+WebKit (1,6 min, 2 skip RuView), 1 E2E commercial-br |
| Não executado | Docker/demo e Docker E2E; `Dockerfile.verify` Linux; NVDA |

## Grupo A, F5 e F6 (Claude Code) — 17/10/2026

| Comando / inspeção | Resultado |
| --- | --- |
| `test_network_health.py` | 9 pass: base estável sem alerta; queda 15 vs 14 pontos; latência exige 2× e +20 ms; perda; desconexões; abstenção; buckets contínuos; rota autenticada e no perfil comercial; exclusão confirmada/escopada/auditada |
| `test_alert_webhook.py` | 17 pass: assinatura verificável por receptor HTTP real; redirect não seguido; 7 destinos públicos/DNS/metadados/credenciais recusados; só transições; troca de cômodo sem alerta; nova tentativa após falha; log limitado a 1.000; caminho do receptor mascarado |
| `test_csi_frame.py` | 16 pass: ida e volta; recusas estruturais e semânticas; replay/ordem/frescor/hardware; 20.000 mutações + 5.000 cabeçalhos reassinados sem exceção inesperada nem aceitação; transporte com falhas |
| Red no E2E de rede | seletor `getByRole("status")` ambíguo após nova região; corrigido com filtro por texto |
| `check.ps1` | exit 0: mypy (55), 299 backend, 6 launchers, 39 web, build, 18 E2E Chromium+WebKit (1,6 min, 2 skip RuView), 1 E2E commercial-br |

## Pendências finais do PR #6 (Claude Code) — 16/10/2026

| Comando / inspeção | Resultado |
| --- | --- |
| E2E CI do PR #6 (pausa) | Red: total 30→32 após pausar; corrigido (`queue.join()` antes de `paused`), CI 10/10 |
| Demo Docker (volume preservado, cópia prévia) | 0008 e depois 0009 aplicadas; 10.000 eventos mantidos; api/web healthy; imagens por digest |
| `test_rule_history.py` | 2 pass (ciclo com horários/auditoria; migração mantém NULL em regras antigas) |
| mypy baseline → final | 62 erros em 17 arquivos → 0 em 51 arquivos |
| Linux `Dockerfile.verify` 3.13 (digest) | Ruff, format, mypy, 256 backend, 6 launchers, pip-audit dos dois locks sem vulnerabilidades |
| WebKit no Windows | antes BLOCKED (DLL); agora executa. Red: `avatars` 401 com token digitado antes da hidratação; corrigido lendo o campo no submit |
| E2E Chromium + WebKit (lab) | 18 pass, 2 skip (RuView) |
| E2E `commercial-br` (Chromium) | 1 pass: 403 em eventos/sensores/replay/regras, nenhum WebSocket ou chamada espacial, axe sem violações |
| NVDA | BLOCKED: leitor de tela não instalado; exige validação manual assistiva |
| `check.ps1` final | exit 0: Ruff/format, mypy (51), 20 contratos, 256 backend, 6 launchers, Prettier, 35 web, ESLint, tsc, build, 18 E2E Chromium+WebKit (1,7 min, 2 skip RuView), 1 E2E commercial-br |

## Perfil aplicado e P3 (Claude Code) — 16/10/2026

| Comando / inspeção | Resultado |
| --- | --- |
| Red `test_capability_enforcement.py` | 11 falhas antes do enforcement (endpoints 200 em commercial-br, stream aberto, capacidade não declarada) |
| `pytest apps/api/tests` | 253 pass |
| `check.ps1` | exit 0: Ruff/format, 20 contratos, 253 backend, 6 launchers, Prettier, 33 web, ESLint, tsc, build, 9 E2E (34,1 s), 1 skip |
| Docker Desktop | não iniciou (engine ausente); demo e Docker E2E não reexecutados |

## Auditoria P2/P3 e CI gratuito (Claude Code) — 15/10/2026, 22:15–22:58 Fortaleza

| Comando / inspeção | Resultado |
| --- | --- |
| Red antes das correções | plano `SCAN sensing_events`; OFFSET de retenção = retention; 61 validações para página de 10; JSON aninhado e erro do provedor matando a ingestão; L1 apagado pela retenção; relatório gravado com auditoria falha; payload inválido → 500; 4 helpers web ausentes |
| `Get-ProjectPython` PS 5.1 com stub em stderr | original: `RemoteException`; corrigido: encontra Python válido |
| Teste Alembic × ORM | vazio no head; detecta índice removido (prova negativa) |
| Benchmark 100 mil linhas | janela 1 min 256→1,2 ms; 2 h 440→144 ms; página replay 261→7 ms; fronteira de retenção 62→5 ms; write p50 1,5 ms |
| `check.ps1` (22:40) | exit 0: Ruff/format, contratos, 200 backend, 6 launchers, 30 web, Prettier, tsc, build, 9 E2E Chromium (42,0 s), 1 skip |
| CI backend em contêiner Linux (3.12 e 3.13) | exit 0: contratos sync (20), Ruff, 211 backend, 6 launchers, pip-audit dos dois locks sem vulnerabilidades conhecidas |
| CI web em contêiner Node 22 limpo (`npm ci`) | lint, tsc, 30 web e build aprovados; `format:check` acusou `src/lib/network.ts` enquanto outra sessão o editava (corrigido por ela no gate seguinte) |
| CI E2E em contêiner Linux (venv `.venv/bin`, Chromium com deps) | exit 0: 9 pass, 1 skip (RuView), 33,4 s |
| `npm audit --audit-level=moderate` | 0 vulnerabilidades |
| Gitleaks, pre-commit, Firefox/WebKit, NVDA | não executados nesta etapa |

## Continuidade Claude Code — 15/10/2026, 20:55–21:03 Fortaleza

| Comando / inspeção | Resultado |
| --- | --- |
| check.ps1 antes das mudanças (árvore Codex) | exit 0: 182 backend, 6 launchers, 26 web, contratos 16 sync, build, 9 E2E, 1 skipped |
| pytest tests/test_pipeline_sessions.py (Red) | 2 fail: backlog sob segmento novo; deque mutated during iteration |
| pytest tests/test_storage_hardening.py (Red) | 3 fail: coluna aplicada com versão 0001; snapshot órfão; FileNotFoundError no prune |
| pytest tests/test_runtime_hardening.py (Red) | 3 fail: WS 1013 após 30 reconexões; assinante antes da auth; 401 em vez de 413 |
| Mesmos testes após correções | 8 pass |
| check.ps1 final | exit 0: Ruff/format, 16 contratos sync, 190 backend, 6 launchers, 26 web, lint, tsc, build, 9 E2E Chromium (32,5 s), 1 skipped |

Python 3.13/Docker, Firefox, WebKit e NVDA não foram reexecutados nesta continuidade.

## Visualização articulada — 15/10/2026, a partir de 20:02 Fortaleza

Encerramento às 20:12 Fortaleza: lint, TypeScript e build finais exit 0.
Após correção da barra em fullscreen, caso avatars passou em Chromium (2,9 s) e
Firefox (5,0 s), total 13,9 s, incluindo entrar/sair e ausência de overflow na cena.
Frontend de uso reconstruído após esse ajuste, web/API healthy; API permanece
sem reinício desde a abertura da demo. Sem alteração posterior de código.

| Comando / inspeção | Resultado |
| --- | --- |
| npm.cmd run test:web Red | teste novo do Observatory falhou porque ainda havia pontos; teste de título identificou espaços React no SVG; ajustado título como string única |
| npm.cmd run test:web Green | 25 pass, zero fail; multielenco mantém evento imutável/contagem e nenhuma posição fabricada no legado |
| scripts/verify/check.ps1 | exit 0: 175 backend (34,33 s), 6 launchers (1,21 s), Ruff lint/format, 14 contratos sincronizados, ESLint, TypeScript, 25 web, build e 8 E2E Chromium (32,0 s); legado skipped |
| E2E_BROWSERS=firefox npm.cmd run test:e2e --workspace apps/web -- --grep avatars | exit 0: um caso passou (6,3 s; total 11,7 s) |
| scripts/verify/docker-e2e.ps1 | exit 0: stack isolada reconstruída/healthy; seis E2E (26,9 s), três skipped; 13 payloads idênticos após restart; relatório/replay/experimento preservados |
| cenário ampliado, E2E_BROWSERS=chromium,firefox com --grep avatars | exit 0 antes do ajuste de barra; entrar/sair de fullscreen passou nos dois browsers |
| capturas articulated-desktop/mobile/immersive.png | abertas e inspecionadas; corte de barra superior em fullscreen levou a ajuste grid e asserção de largura no E2E |

Após ajuste CSS final: lint, tipos, build e testes de avatar/fullscreen nos dois
browsers repetidos; resultado conclusivo no adendo de encerramento desta seção.
Não reexecutar backend integral por ajuste exclusivamente de layout.

Logs ignorados: artifacts/articulated-red.log, articulated-green.log,
articulated-check.log, articulated-firefox.log, articulated-fullscreen.log,
articulated-final-build.log, articulated-docker-e2e.log e articulated-demo-update.log.
Recibo Docker: native-compose-receipt.json, 2026-10-15T23:10:13.472367+00:00
(20:10:13 Fortaleza). Bases e portas isoladas. Stack de teste encerrada; volume
mantido. Stack de uso permanece ativa e saudável em 3000/8000.

Na demo somente web recriado com `docker compose up --build --detach --wait
--no-deps web`; API de uso não reiniciada e histórico não apagado. Navegador de
avaliação conectado, elenco misto com três posições virtuais; recibo sem segredos
artifacts/articulated-demo-ready.json. Nenhum token impresso ou gravado no script.

Avaliação externa limitada a páginas e metadados públicos HF: revisão encoder
98b29a35f962996d6e8207e4f46818dedb5764d5 (MIT), revisão pose MM-Fi
39f46e583081a577bddd72f239690281ec11644b (CC BY-NC 4.0). Não houve inferência,
download de pesos, execução de código remoto ou reprodução dos benchmarks citados.
Plano e fontes: PEOPLE_ANIMALS_RF_RESEARCH.md. Dados continuam L0_SYNTHETIC.
Python 3.13/auditorias não repetidos neste incremento sem mudança backend/locks;
resultados da continuação Docker abaixo permanecem anteriores ao renderer.

## Docker desbloqueado e revalidado — 15/10/2026, 19:43–19:45 Fortaleza

Na consulta inicial, Desktop estava `starting`, distribuição docker-desktop/WSL2
parada e serviços WslService/vmcompute ativos. Em seguida o engine respondeu
29.8.2 e Desktop passou a `running`, contexto desktop-linux, OS linux. Não houve
reinstalação, alteração de settings/serviços/WSL, reset, prune ou remoção de volume.
O estado anterior BLOCKED foi superado pela inicialização concluída.

| Comando / resultado | Evidência atual |
| --- | --- |
| docker version / docker desktop status | exit 0: client/server 29.8.2; Desktop running |
| scripts/verify/docker-e2e.ps1 | exit 0: imagens API/web reconstruídas, ambos healthy, 5 E2E Chromium (23,5 s), 3 skipped (2 injeções reservadas ao runner nativo e RuView opt-in) |
| smoke de reinício incluído no script | 12 payloads idênticos após reinício real; relatório, replay e experimento preservados; motor nativo padrão e legado false |
| docker build --build-arg PYTHON_VERSION=3.13 -f apps/api/Dockerfile.verify -t wifi-spatial-backend-verification-py313 . | exit 0: imagem atual reconstruída |
| docker run --rm wifi-spatial-backend-verification-py313 | exit 0: Ruff lint/format, 175 backend (33,23 s), 6 launchers (1,19 s), auditorias runtime/lock sem vulnerabilidades conhecidas |
| Ruff local após correção | check e format --check: exit 0; 59 arquivos |

Primeira execução Python 3.13 falhou EXE002: scripts/verify/tests/conftest.py e
test_launchers.py estavam executáveis no contexto Linux sem shebang. Adicionado
`#!/usr/bin/env python3` aos dois, imagem reconstruída e execução completa passou.
Não foi desabilitada regra de lint nem alterada política do SO.

Logs: artifacts/docker-recovery-e2e.log, docker-recovery-py313-build.log e
docker-recovery-py313-check.log. Recibo: artifacts/native-compose-receipt.json,
recorded_at 2026-10-15T22:44:21.081721+00:00 (19:44:21 Fortaleza).
Stack de verificação encerrada e container --rm removido; docker ps vazio ao
final. Volume preservado; nenhum banco de uso foi apagado. Desktop permanece
ativo. Staged IDE segue com 10 adições; nenhum commit/push.

Resultados anteriores BLOCKED abaixo são históricos. WebKit/NVDA e sensoriamento
real não foram validados nesta continuação; dados continuam L0_SYNTHETIC.

## Evolução corporativa — evidência desta entrega, 15/10/2026

**Encerramento às 18:49 Fortaleza:** após o último ajuste do callback de erro,
`npm.cmd run lint`, `npm.cmd run typecheck` e `npm.cmd run build:e2e` passaram
(exit 0). `E2E_BROWSERS=chromium,firefox npm.cmd run test:e2e` passou: **14 E2E,
51,4 s**, dois legados skipped. A variável de processo foi restaurada ao final.
Logs: artifacts/enterprise-final-web-build.log e enterprise-final-browsers.log.
Servidores próprios de teste encerrados pelo runner. Nenhuma falha residual de
teste conhecida nesta entrega; bloqueios de ambiente abaixo continuam explícitos.

Ambiente confirmado: Windows/PowerShell, Python venv 3.12.10, Node 24.19.0.
Execução a partir de 18:32 America/Fortaleza. Branch feat/platform-foundation,
HEAD 2767417, staged somente .idea/.gitignore (10 adições), sem commit/push.

| Comando / amostra | Resultado desta execução |
| --- | --- |
| check.ps1 baseline | exit 1 Ruff: E501 em test_contract_invariants.py e test_job_supervision.py |
| venv python -m pytest apps/api/tests -q baseline | exit 1: 166 pass, 8 fail (34,64 s); schemas/fixtures defasados, captura stdout em vez de stderr, primeiro ponto geométrico inválido aceito |
| npm.cmd run test:web baseline | exit 1: 11 pass, 10 fail; funções ausentes, UUID/proveniência/união divergentes e golden fixtures ausentes |
| novo test_error_boundary.py Red | exit 1: resposta 500 era texto; Green no gate final após handler JSON sanitizado |
| export_contract.py / --check | exit 0: 14 artefatos exportados e sincronizados; modelos Python, JSON Schema e Zod exercitados |
| pytest scripts/verify/tests -q Red/Green | exit 1, seis falhas antes de --no-proxy-headers; exit 0, seis pass (1,06 s) depois |
| scripts/verify/check.ps1 final | exit 0: Ruff lint/format (59 arquivos), contratos, 175 backend, 6 launchers, ESLint, TypeScript, 21 web, build:e2e, 7 E2E Chromium (25,5 s), 1 legado skipped |
| npm.cmd exec -- prettier --check nos arquivos TS/TSX alterados | exit 0; recovery.spec.ts formatado após criação |
| npm.cmd audit --json | exit 0: vulnerabilities.total=0, 231 dependências reportadas |
| venv python -m pip_audit -r apps/api/requirements.runtime.txt | exit 0: No known vulnerabilities found |
| venv python -m pip_audit -r apps/api/requirements.lock.txt | exit 0: No known vulnerabilities found |
| docker version --format '{{.Server.Version}}' | exit 1: pipe dockerDesktopLinuxEngine ausente; daemon indisponível |
| git -C temp_ruview rev-parse HEAD / status / remote | a1ca023ee872683d160250d47ae3d4d228af55a0, clone limpo, fork solicitado |
| git ls-remote https://github.com/matheussiqueira-dev/RuView.git HEAD | exit 0: mesmo HEAD; fonte pública também consultada |

`venv python` usa apps/api/.venv/Scripts/python.exe. Logs em artifacts ignorado:
enterprise-baseline.log, enterprise-backend-baseline.log, enterprise-web-baseline.log,
enterprise-launchers-red.log, enterprise-final-check.log, enterprise-recovery-e2e.log,
enterprise-npm-audit.json, enterprise-pip-audit.log, enterprise-pip-lock-audit.log.

Falhas intermediárias: gate exigiu formatar export_contract.py/test_launchers.py.
Um runner adicional foi iniciado enquanto outro gate compilava; Assert-PortFree
recusou 4810 sem matar processo. Nova execução foi serializada. Primeiro E2E novo
tentou editar input legitimamente disabled; ajustado para draft inválido antes de
sessão iniciada por outro operador via API real. Ambos testes passaram no gate.
O bloqueio legítimo do formulário não foi removido.

Após o gate, captura da string do aviso antes de setError foi ajustada para evitar
callback ler variável limpa. Lint/tipos/build repetidos; browsers finais constam
no encerramento acima. Não atribuir esse último build ao gate anterior.

Capturas dashboard-desktop/mobile abertas e inspecionadas; tabela mobile tem
scroll próprio. Axe e overflow no E2E não substituem leitor de tela. WinError
10054 no fechamento forçado e NO_COLOR/FORCE_COLOR apareceram nesta etapa, sem
supressão. Containers/Compose/Python 3.13 atuais BLOCKED; imagem verify ajustada
mas não construída. RuView skipped, não PASS. WebKit/NVDA não reexecutados.
Sem checker Python integral, cobertura percentual, benchmark de carga/CWV,
certificação enterprise, clean-room estrita ou validação física/clínica. Tudo L0.

---

## Gate integrado F3B/F4/F5/F6 — 15/10/2026, 15:05–15:10 Fortaleza

Ambiente: Windows, Node 24.19.0, venv Python 3.12.10, Docker 29.8.2. Branch
feat/platform-foundation, HEAD 2767417; 155 untracked, .idea/.gitignore staged.
Nenhum arquivo de produto alterado nesta verificação.

| Comando exato | Exit / evidência |
| --- | --- |
| `scripts/verify/check.ps1` | 0 (67 s): Ruff check/format, 135 backend (31,07 s), ESLint, TypeScript, 11 web, build:e2e, 5 E2E Chromium (23,4 s), ruview.spec skipped |
| `E2E_BROWSERS=chromium,firefox E2E_RUVIEW=0 npm.cmd run test:e2e` | 0: 10 pass (48,8 s), 2 legados skipped; analytics, automation, dashboard, model-lab e CSP em ambos |
| `docker build --build-arg PYTHON_VERSION=3.13 -f apps/api/Dockerfile.verify -t wifi-spatial-backend-verification-py313 .` + `docker run --rm wifi-spatial-backend-verification-py313` | 0: 135 pass (29,11 s), Ruff 54 arquivos, pip-audit runtime/lock sem vulnerabilidades conhecidas |
| `scripts/verify/docker-e2e.ps1` | 0 (52 s): 5 E2E Chromium na stack nativa; smoke 12 eventos/payloads comparados, saved_report/replay/experiment preservados, native_default_after_restart=true, legacy_enabled=false; stack derrubada sem remover volume |
| `npm.cmd audit` | 0: found 0 vulnerabilities |

A falha integrada citada às 14:36 não foi reproduzida; não há registro do
diagnóstico original. WinError 10054 (proactor_events.py:165) apareceu no log do
servidor durante o fechamento forçado do E2E MVP, sem falha de teste. WebKit e
leitor de tela não executados (BLOCKED, como antes).

## Incremento C/D/G — 15/10/2026, 14:24–14:31 Fortaleza

- local_security.py: 8 pass (0,89 s). Timeout WS inicialmente pendurou teste:
  app retornava sem close explícito; corrigido e reexecutado, sem silenciar erro.
- check.ps1 -SkipE2E: 124 backend (28,61 s), 10 web, lint/tipos/build, exit 0.
  Tentativa anterior falhou I001 de imports, corrigido com Ruff; registrada como
  falha, não como gate aprovado. Ausência de pytest em teste novo também detectada
  no lint e corrigida antes do ciclo seguinte.
- CSP Red: nonce ausente no build anterior. Primeira verificação negativa via
  page.evaluate aguardou evento não recebido (timeout 45 s); teste passou a inserir
  script não autorizado no HTML da resposta e verificar securitypolicyviolation
  mais ausência do efeito. Firefox tinha mensagem console diferente; substituído
  diagnóstico dependente de idioma por evento padronizado, sem relaxar bloqueio.
- E2E Chromium/Firefox: 6 pass (36,7 s), 2 legados skipped. Scripts com nonce
  hidratam e funcionam; nonce muda por resposta; script sem nonce foi bloqueado.
- Playwright install firefox webkit: exit 0 no download, mas launch WebKit falha
  por ngtcp2_crypto_quictls.dll ausente. Resultado de execução WebKit BLOCKED;
  arquivo executável presente não equivale a compatibilidade comprovada.
- G Red: módulo app.domain.motion ausente; Green inicial 3 pass (0,17 s), antes
  dos testes extras de isolamento/denominadores. Artefatos/contratos exportados;
  TypeScript exit 0. Gate final do incremento ainda deve ser registrado.

## Execução EXECUTION_PLAN_V3 — 15/10/2026, a partir de 14:20 Fortaleza

Mestre relido integralmente: v3.0/hash inalterado. Git inicial 120 untracked,
staged .idea/.gitignore 10 adições, nenhum diff unstaged rastreado. Sem descarte.
check.ps1 baseline exit 0: 111 backend (27,33 s), 10 web, Ruff, ESLint, TypeScript,
build, 2 E2E (19,0 s), 1 legado skipped. Proactor WinError 10054 reproduzido na
pilha asyncio/proactor_events.py:165 shutdown(socket.SHUT_RDWR), durante cliente
forçadamente encerrado; recuperação observada, sem handler global de supressão.
Não foi observada a falha no encerramento normal desta amostra.

B Red: pytest test_recurring_backup.py exit 1 módulo ausente; Green exit 0:
5 pass (0,35 s). C Red: pytest test_local_security.py exit 1 módulo ausente;
primeiro Green detectou capacidade compartilhada entre classes bloqueando leitura;
corrigido para contadores por classe em cada peer limitado. Suíte local_security
e API: 18 pass (6,26 s), exit 0; Ruff exit 0. Nenhum serviço global instalado,
nenhum expurgo/prune de banco de uso, status não revela caminho/erro bruto.

## Entrega documental posterior — 15/10/2026

Criado docs/EXECUTION_PLAN_V3.md com comando único de início e roteiro detalhado.
Validada disponibilidade da sintaxe em codex --help/exec --help (exit 0);
comando inicial analisado pelo parser PowerShell sem iniciar sessão de execução.
Links locais e seções do roteiro conferidos. Nenhuma suíte do produto reexecutada
para esta mudança exclusivamente documental. Resultados funcionais abaixo são
da execução anterior, não evidências de que o backlog novo foi implementado.

## Continuação v3.0 — relatório vigente — 15/10/2026

Plano confirmado: cabeçalho v3.0; seção 3 autonomia, seção 4 separação clean-room,
F0R/F1R/F2R/F3A presentes e lidos integralmente. Arquivo único normativo:
docs/PROJECT_MASTER_PLAN.md; SHA-256
2dd0b492dd94bff52cb9eb2d22a9de5fa116c367405755a90493595c3ce36ad7.
Leitura inicial ainda encontrou v2; após atualização do proprietário, leitura
externa às 13:35 confirmou v3 (29.666 bytes). A cópia docs/docs é histórica.

Ambiente observado: Windows/PowerShell 7.6.7, Git 2.55.0.windows.3, Node 24.19.0,
Python venv 3.12.10; Docker 29.8.2/Compose v5.5.1, Node 22 no build Docker,
Python 3.13.16 em imagem isolada. Next 16.4.0/React 19.3.0/TypeScript 5.9.3,
Playwright 1.64.0. Branch feat/platform-foundation; HEAD 2767417; árvore dirty.

### Comandos e resultados desta continuação

| Comando exato | Exit / evidência |
| --- | --- |
| `scripts/verify/check.ps1 -RuView` (baseline) | 1: 83 backend/7 web/lint/tipos/build passaram, porta 4860 ocupada impediu E2E; processo existente preservado |
| `python.exe -m pip install httpx2` no venv | 0: httpx2/httpcore2 2.13.1 e truststore 0.10.5; locks regenerados intencionalmente; sem alteração de versão das demais dependências |
| `python.exe -m pytest apps/api/tests/test_analytics.py -q` | primeira execução 14 pass/1 fail no teste de recusa de sobrescrita; corrigido fechamento e ordem das verificações; execução seguinte 15 pass |
| `python.exe -m pytest apps/api/tests/test_native_domain.py -q` (Red) | 1: quatro falhas esperadas antes da implementação: módulo ausente, fronteira ausente, legado ligado |
| `python.exe -m ruff format apps/api scripts/verify` + `python.exe -m ruff check apps/api scripts/verify` | 0 após correções E501; 35 arquivos formatados/verificados no último ciclo |
| `scripts/verify/check.ps1` após motor nativo/CSP | 0: 105 backend (27,53 s), 9 web, ESLint/TypeScript/build; dois E2E Chromium (18,9 s), um legado skipped por modo padrão |
| `scripts/verify/check.ps1 -RuView -RuViewHttpPort 4970 -RuViewWsPort 4971` após migração | 0: 105 backend (27,88 s), 9 web, lint/tipos/build; três E2E (31,7 s), incluindo imagem oficial no laboratório opt-in |
| `scripts/verify/docker-e2e.ps1` | 0: builds e stack somente API/web healthy; dois E2E (16,2 s), legado skipped; volume preservado |
| `scripts/verify/docker-e2e.ps1 -SkipBrowser` | 0: 12 eventos/payloads idênticos após reinício real da API; replay/snapshot iguais; padrão nativo e legacy_enabled=false; recibo artifacts/native-compose-receipt.json |
| `docker build --build-arg PYTHON_VERSION=3.13 -f apps/api/Dockerfile.verify -t wifi-spatial-backend-verification-py313 .` + `docker run --rm wifi-spatial-backend-verification-py313` | 0: imagem atualizada; 105 backend (25,22 s), Ruff e pip-audit dos locks runtime/completo sem vulnerabilidades conhecidas |
| `npm.cmd audit --json` | 0: zero vulnerabilidades conhecidas nas 231 dependências reportadas, inclusive desenvolvimento |
| `python.exe scripts/verify/maintenance_smoke.py` | 0: wrappers PowerShell backup/restore executados sobre fixture nova, payload exato e banco de uso intocado |
| `python.exe scripts/verify/license_inventory.py` e `node scripts/verify/inventory.mjs` | 0: versões/licenças e executáveis observados, sem segredos; Python 3.13.16 confirmado por docker run image python --version |
| `scripts/verify/check.ps1` final após precisão temporal e sincronização WS | 0: 111 backend Windows (27,13 s), 10 web, Ruff/ESLint/TypeScript/build, 2 E2E Chromium (21,1 s); legado skipped por padrão |
| Build/run Python 3.13 final após correção WS | 0: 111 pass (25,64 s), Ruff lint/format; pip-audit runtime e completo terminaram sem vulnerabilidades conhecidas |
| `scripts/verify/check.ps1 -RuView -RuViewHttpPort 4970 -RuViewWsPort 4971` última execução legada | 0: 110 backend, 10 web, lint/tipos/build e 3 E2E (34,0 s); precede teste/correção submilissegundo |
| `scripts/verify/docker-e2e.ps1` última execução com browser | 0: 2 E2E (16,9 s), legado skipped; precede correção submilissegundo |
| `scripts/verify/docker-e2e.ps1 -SkipBrowser` após precisão temporal | 0: 24 payloads idênticos após restart; replay/relatório preservados, legado off; recibo de 17:04:11 UTC |

Os comandos python.exe acima usam apps/api/.venv/Scripts/python.exe, não Python
global. Falhas do sandbox (Python inacessível/tsx ENOMEM/rede npm) foram repetidas
com autorização de host, sem alterar controles do SO. Logs de ferramentas nesta
sessão e artefatos locais suportam os resultados; não foi criado um transcript
integral retroativo. Não alegar cobertura percentual: mapeamento qualitativo dos
módulos críticos e testes específicos estão na matriz.

### Falhas e correções, sem reescrever falha como sucesso

- E501 reproduzido em código novo e nas duas linhas SQL da fixture analytics;
  formatter não quebra strings SQL automaticamente; linhas corrigidas manualmente.
- Contrato TS inicialmente recusava timestamp +00:00; agora aceita apenas UTC
  Z/+00:00, sem permitir offset não UTC. safeExtend de literais incompatíveis foi
  substituído por composição de schema e refinamento próprio, sem cast/any.
- E2E: seletor status ambíguo corrigido por nome acessível. Overflow 320 px
  reproduzido (grid min-content dos controles); minmax(0,1fr)/duas colunas corrigiram.
  Testes seguintes passaram também com relatório/replay carregados e axe.
- Uma tentativa npm --grep perdeu argumento no workspace e não encontrou testes;
  comando correto é npm.cmd run test:e2e --workspace apps/web -- --grep analytics:.
- WinError 10054/Proactor reapareceu ao interromper stream, inclusive no MVP nativo;
  recuperação e E2E passaram. É erro residual do transporte Windows em teste de
  falha, não uma ausência de warning. Não foi ocultado globalmente.
- Python 3.13 teve execução intermediária exit 1: 110 pass/1 fail, CancelledError
  no teardown de test_real_transport_persistence_controls_and_source_switch.
  Fechamento explícito e espera limitada pela liberação real dos assinantes
  corrigiram a corrida; última suíte 111 pass. Não foi suprimida exceção.
- Limite submilissegundo: teste Red retornou 0 em vez de 1 por arredondamento de
  julianday. UDF spatial_epoch_us compara microssegundos UTC inteiros. Teste
  isolado e suítes Windows/Linux passaram, sem regravar dados históricos.

### Independência e fronteira de validação

Domínio Acquisition é stdlib; teste AST impede imports de HTTP/ORM/legado.
Teste em processo novo comprova que create_app default não importa app.ruview.
Flag legada false e seleção recusada foram testadas. Stack nativa executou somente
API/web, com autenticação/stream/analytics reais. Contratos 1.0/1.1/2.0 coexistem;
migração aditiva preserva payloads antigos sem atribuir sessões inventadas.
Isso comprova independência operacional observada, **não clean-room estrita**:
há exposição prévia do implementador ao legado, registrada no ORIGINALITY_REGISTER.

Backups e retenção foram testados em fixtures. Nenhuma remoção de banco de uso,
volume persistente, token, staged ou alteração local. Screenshots analytics
desktop/mobile foram abertos e inspecionados: sem corte indevido no painel;
tabela mobile mantém região de scroll acessível. Não houve leitor de tela manual.

### Limitações atuais

Fechamento Git: branch feat/platform-foundation; HEAD
27674175866b0d0e20b10ddee30ab33268134d84. Um arquivo staged .idea/.gitignore
(10 adições), zero modificações unstaged em arquivos rastreados e 119 arquivos
untracked (git ls-files --others --exclude-standard). .env, runtime, artifacts e
venv ignorados. Nenhum commit/push ou stage adicional. Relatório consolidado:
TECHNICAL_REPORT_V3.md.

Firefox/WebKit/NVDA ausentes: BLOCKED, não PASS. Lista original de 68 warnings não
fornecida: UNVERIFIED; avisos observados em WARNINGS_TRIAGE. Não há percentual de
cobertura, benchmark de carga/RAM/CPU, perfis multiusuário/TLS público, validação
física/clínica ou garantia de originalidade jurídica. HTTP rate limit geral e
trilha completa de negativas auth permanecem pendentes no escopo local. Exports
são por página; não há cursores/rollups incrementais. Todos os dados são L0.

---

## Registro histórico anterior à v3.0

Data: 15/10/2026, America/Fortaleza. Branch: `feat/platform-foundation`.
Escopo: regressão técnica do MVP F0/F1 e RuView F2 existentes, segurança local,
infraestrutura e persistência. Sem commit, push ou uso de serviços pagos.

## Encerramento do escopo autorizado

O responsável confirmou a indisponibilidade do plano v2.0 localmente e no GitHub
e instruiu encerrar as verificações existentes sem inferir requisitos ou iniciar
F3A. As execuções técnicas abaixo estão concluídas; não há suíte em andamento.
A confirmação de encerramento revisou registros/Git e atualizou documentação,
sem repetir testes já aprovados ou alterar código. Permanecem os limites de
validação descritos neste relatório e a pendência de conformidade formal.

## Limite da auditoria de conformidade

O arquivo `docs/PROJECT_MASTER_PLAN.md` v2.0 não está disponível. Não foi possível
avaliar sua atualização operacional, requisitos técnicos, backlog ou critérios
oficiais. A [matriz](REQUIREMENTS_TRACEABILITY.md) usa identificadores locais e
separa evidência técnica de conformidade formal. F3A não implementada nesta etapa
por falta do conteúdo que define seu escopo.

## Execuções e resultados

| Comando / inspeção | Resultado |
| --- | --- |
| Primeira execução `scripts/verify/check.ps1 -RuView` fora do sandbox | Passou: Ruff lint/formatação, 83 testes Python, ESLint, TypeScript, quatro contratos web, build de produção e dois E2E Chromium (41,8 s) |
| `scripts/verify/ruview-compose.ps1` | Passou: builds API/web, stack isolada healthy, REST/WS oficiais e reinício real da API |
| Recibo `artifacts/f2-compose-receipt.json` | Oito eventos; official_stream_persisted=true, payloads_identical_after_restart=true, api_stopped_after_restart=true |
| `docker build -f apps/api/Dockerfile.verify -t wifi-spatial-backend-verification .` e `docker run --rm wifi-spatial-backend-verification` | Passaram: Ruff, 83 testes Linux e pip-audit dos dois locks sem vulnerabilidades conhecidas; antes do ajuste posterior no teste de teardown |
| `npm.cmd audit --json` fora do sandbox | Zero vulnerabilidades conhecidas, inclusive desenvolvimento |
| `npm.cmd run test:web` após correção do mapa | Sete testes passaram: quatro contratos e três regressões de apresentação acessível |
| Repetição intermediária de `check.ps1 -RuView` | Falhou em test_websocket_connection_limit no teardown: 82 passaram e um falhou com concurrent.futures.CancelledError; não ocultado nem tratado como aprovação |
| Teste direcionado após sincronizar fechamento/liberação/reutilização | Um teste passou; aviso TestClient/httpx permanece |
| Verificação final integrada após correções: `scripts/verify/check.ps1 -RuView` | Passou integralmente: Ruff, 83 testes backend Windows (25,89 s), ESLint, TypeScript, sete testes web, build de produção e dois E2E Chromium (31,1 s); serviço de verificação encerrado |
| Git e exclusão de runtime | Apenas LICENSE e .idea/.gitignore constam em git ls-files; .env, .env.ruview, runtime, artifacts e venv continuam ignorados; staged de IDE preservado |

## Correções executadas

1. `apps/web/src/components/observatory.tsx`: o nome acessível do SVG convertia
   contagem RuView desconhecida em zero e descrevia estimativas como ocupantes do
   laboratório interno. Agora distingue contagem indisponível, estimativa sobre
   sinais sintéticos, ausência de posições e ausência de observação. Não desenha
   pessoas RuView nem inventa dados. Três regressões em `tests/observatory.test.ts`.
2. `apps/api/tests/test_api.py`: o teste de limite de conexões deixava o TestClient
   cancelar as tarefas imediatamente após enviar disconnect. A repetição revelou
   uma corrida durante limpeza assíncrona. O teste agora fecha explicitamente as
   conexões, aguarda por condição com prazo de três segundos e exige zero
   assinantes antes do teardown. Também comprova a reutilização de um slot. Não
   suprime exceções nem relaxa o teto de oito conexões; backend inalterado.

## Fronteiras de segurança inspecionadas

Leitura do backend próprio (configuração, contratos, simulador, adaptador RuView,
pipeline, armazenamento e rotas), frontend (requisições, validação Zod, conexões,
controles, mapa e histórico), migrações, testes, launchers e configuração Docker.

- Auth REST por Bearer e comparação constante; origem validada; WS autentica no
  primeiro frame, com timeout e limite de conexões. Testes de acessos inválidos,
  limites, formatos e origem foram executados.
- Token do frontend em memória; inspeção de chamadas e E2E confirmam storages
  vazios. Sem token NEXT_PUBLIC ou URL de autenticação.
- Adaptador aceita apenas destinos locais configurados no backend, sem proxies
  ou redirects; rejeita dados reais/incompatíveis. Testes reais HTTP/WS locais e
  integração com imagem oficial simulada.
- SQLAlchemy usa expressões parametrizadas; PRAGMAs são constantes. Retenção e
  exclusão preservam auditoria; falha de banco não publica sucesso.
- React renderiza dados como texto; nenhuma inserção de HTML bruto encontrada no
  frontend próprio. Headers, responsividade e axe verificados no E2E.
- Containers sem root e portas em loopback; scripts não encerraram processos
  alheios nem removeram volumes. Upstream inteiro não foi auditado; compatibilidade
  continua restrita ao digest fixado.

Não foi confirmada vulnerabilidade crítica/alta explorável no escopo local
inspecionado. Isso não aprova exposição pública, não equivale a pentest nem valida
sensoriamento ou inferência científica. Todos os eventos seguem `L0_SYNTHETIC`.

## Falhas de ambiente e limites

A primeira tentativa restrita não acessava o Python referenciado pelo venv;
tsx também falhou em uv_os_get_passwd/ENOMEM e npm audit não alcançou o registro.
As verificações foram repetidas com aprovação fora do sandbox e sem alterar
controles do Windows. Esses erros não foram atribuídos ao código do produto.

O aviso de depreciação TestClient/httpx continua. Nenhuma dependência ou lock foi
alterado. Auditoria sem expurgo, ausência de política automatizada de backup,
paginação por offset, Bearer compartilhado e sessão de um worker permanecem limites.
Não houve nova instalação limpa, teste Python 3.13, leitor de tela manual, outros
navegadores ou hardware. Capturas E2E desta execução foram produzidas; não se
declara nova inspeção visual manual a partir apenas dos resultados automatizados.
