# Progresso da plataforma

## Claude Code: F3B/F4 e manutenção — 21/10/2026

- PR #13 (perfis de acesso, sessão paralela) mesclado. Dependabot: #8 (Python 3.14) e
  #9 (Node 25) fechados por saírem das versões suportadas; #2, #3, #5, #10, #11 e #12
  reunidos e validados no PR #14. O CI do #14 achou um aviso novo do certifi
  (PYSEC-2026-4320, só no lock de desenvolvimento), corrigido para 2026.10.19.
- **Impressão RF do ambiente** (`spatial.rf_fingerprint`: PLANNED → IMPLEMENTED_SYNTHETIC):
  canal sintético com perfil multipercurso por ambiente; quadros SWF1 autenticados;
  fingerprint por subportadora, limiar calibrado, abstenção. Avaliação por semente:
  falso positivo 0/40, mudanças grandes 40/40, outro ambiente 10/10, mudanças sutis 0/40
  (ponto cego publicado), 10/10 abstenções.
- **Registro de modelos** (`lab.model_registry`): artefatos do projeto com integridade
  reverificada (VERIFIED/MISMATCH/UNREADABLE); fichas de terceiros só com metadados,
  licença SPDX e classificação de uso comercial; migração 0012; papéis admin/viewer.
- Painel "Impressão RF do ambiente e registro de modelos" (axe sem violações em
  Chromium e WebKit).

Pendente: demo Docker com migrações 0011/0012 (Docker Desktop parado e sem reinício
nesta sessão); ONNX (sem modelo treinável que justifique o formato); placa ESP32-S3
(decisão de compra/gravação do proprietário); NVDA; Firefox fora do gate.

## Claude Code: perfis de acesso locais (RBAC, F5) — 17/10/2026

Branch `feat/access-roles` (sobre `main` 4f0a091). ADR-015.

- **Papéis** `viewer`/`operator`/`admin`; `SPATIAL_TOKEN` segue como admin de bootstrap.
  `GatedRouter` exige `require_role` em toda rota (falha na importação se faltar) e
  aplica a capacidade por último: 401 → 403 de papel → 403 de perfil.
- **Migração 0011:** tabela `access_tokens` (id, rótulo, papel, HMAC-SHA256 do token,
  created_at, revoked_at, last_used_at) e `audit_events.actor_id`. Chave do HMAC em
  `SPATIAL_ACCESS_TOKEN_KEY` ou derivada do `SPATIAL_TOKEN`.
- **Endpoints:** `GET /api/v1/access/me` (viewer); `GET/POST /api/v1/access/tokens` e
  `POST /api/v1/access/tokens/{id}/revoke` (admin). Valor mostrado uma vez (`no-store`);
  revogação mantém o registro e vale na requisição seguinte; WS revalida a cada 2 s.
- **Dashboard:** selo de papel no cabeçalho, controles de escrita escondidos por papel
  (simulação, fonte, exclusões, ponto de medição, relatórios, experimentos, regras,
  teste do webhook) e seção admin **Perfis de acesso**. Token só em estado React.
- Agente Wi-Fi aceita `SPATIAL_AGENT_TOKEN` (operator). Mensagens 401/403 revisadas.
- Corrigido no caminho: regra CSS inserida numa lista de seletores escondia
  `.network-controls` (4 E2E vermelhos) e selo de papel alargava a página no mobile.

Comandos: `pytest`, `ruff`, `mypy`, `npm.cmd test`, `npm.cmd run build:e2e`,
`npx playwright test` (specs afetados) e `check.ps1` (resultados no VERIFICATION_REPORT).
Gate `check.ps1` exit 0: mypy (59), 320 backend (21 novos), 6 launchers, 43 web (4 novos),
20 E2E Chromium+WebKit (2 skip RuView), 1 E2E commercial-br.
Pendente: expiração/rotação automática de tokens, MFA/SSO, consentimento por pessoa (F5),
Docker E2E e demo não reexecutados nesta etapa; NVDA; Firefox fora do gate. Commit em `feat/access-roles`.

## Claude Code: grupo A, F5 e F6 — 17/10/2026

Branch `feat/network-governance` (sobre `feat/capability-enforcement`, PR #6 aberto).

- **Grupo A — tendência e alertas** (`network.degradation_alerts`, IMPLEMENTED_LIVE):
  `GET /api/v1/network/health` com séries por hora e alertas consultivos (queda de sinal,
  latência, perda, desconexões, coletor parado) contra a linha de base do mesmo filtro;
  abstenção explícita sem dados suficientes. Painel com tendência horária e alertas.
- **Grupo A — avaliação de pontos:** coluna Bom/Regular/Fraco/Sem dados e ranking do
  melhor para o pior (heurística sinal × perda).
- **F5 — webhook local** (`network.alert_webhook`, IMPLEMENTED_LIVE): POST assinado
  (HMAC-SHA256 + timestamp) de `alert.raised`/`alert.cleared` por ponto, só para IP de
  loopback/rede privada, sem redirect/proxy; log limitado de entregas (migração 0010);
  status com destino mascarado e botão de teste no painel.
- **F5 — exclusão LGPD:** `DELETE /api/v1/network/history?confirm=ERASE[&location]` com
  auditoria do fato; botão no painel respeita o ponto filtrado e pede confirmação.
- **F6 — SWF1** (`hardware.csi_frame_protocol`, IMPLEMENTED_SYNTHETIC/L0): formato
  binário próprio para ESP32-S3 com HMAC por dispositivo, receptor com frescor/replay/
  ordem, recusa de placa não testada, simulador de transporte com falhas e fuzzing
  determinístico (25.000 casos). Especificação em `docs/CSI_FRAME_PROTOCOL.md`.
- Corrigido no caminho: seletor E2E ambíguo (`status`) após o painel ganhar duas regiões.

Gate `check.ps1` exit 0: Ruff/format, mypy (55), 20 contratos, 299 backend, 6 launchers,
Prettier, 39 web, ESLint, tsc, build, 18 E2E Chromium+WebKit, 1 E2E commercial-br.
Pendente: listener real de SWF1 e firmware (exigem placa e autorização); RBAC local e
consentimento por pessoa (F5); NVDA; Firefox fora do gate. Commit `feat/network-governance`.

## Claude Code: pendências do PR #6 concluídas — 16/10/2026

- **Imagens por digest:** `python:3.12-slim`, `node:22-slim` e o `Dockerfile.verify`
  (3.12 padrão, 3.13 por argumento) fixados pelo digest do índice multi-arquitetura;
  Dependabot ganha o ecossistema `docker`.
- **Histórico de regras (contracts-data-13):** migração 0009 com `created_at`/`revoked_at`
  e `audit_events.subject_id`; API e contrato Zod expõem os horários, o painel mostra
  "criada … · revogada …" ou "criação anterior ao histórico" (NULL não é inventado).
- **Tipagem:** mypy 2.4.0 (dev; lock regenerado só com adições) no `check.ps1`, no
  `linux_checks.py` e no CI; 62 erros corrigidos (anotações, `row_count`, estreitamento de
  `utcoffset`, porta `StreamingSource` no pipeline, tipo `Advice` compartilhado).
- **E2E:** WebKit voltou a executar no Windows e entrou no gate/CI; bug real corrigido
  (token digitado antes da hidratação não chegava ao estado React → 401). Novo spec do
  perfil `commercial-br` via `E2E_PROFILE`.
- Demo Docker reconstruída com imagens fixadas: Alembic 0009, 10.000 eventos preservados
  (cópia do volume antes da migração, fora do repositório).

Comandos: `pytest`, `mypy`, `ruff`, `npm.cmd run build:e2e`, `E2E_BROWSERS=chromium,webkit`
e `E2E_PROFILE=commercial-br npm.cmd run test:e2e`, `docker compose up --build --detach
--wait`, `Dockerfile.verify` 3.13 e `check.ps1` (resultados em VERIFICATION_REPORT).
Pendente: NVDA (leitor de tela não instalado, validação manual); Firefox fora do gate.

## Claude Code: perfil de capacidades aplicado e P3 da auditoria — 16/10/2026

PR #1 mesclado na `main` (`be66f40`). Trabalho em `feat/capability-enforcement`.

- **Perfil como bloqueio real:** `require_capability` (após a autenticação, 401 antes
  de 403) nos routers de presença/simulação/eventos/sensores/ocupação, analytics,
  laboratório de modelos, automação e rede (grupo A); stream fecha 1008 quando o perfil
  desliga presença. Nova capacidade declarada `automation.dry_run_rules`. `/system/status`,
  catálogo e governança seguem abertos. Dashboard carrega o catálogo no login, não abre
  WS nem sincroniza eventos fora do perfil e mostra aviso no lugar dos módulos grupo B.
- **P3:** `/docs`/`/redoc` (scripts de CDN) só com `SPATIAL_API_DOCS_ENABLED=true`;
  `SPATIAL_ALLOWED_HOSTS` substitui lista fixa com `testserver`; host `ruview` só com
  `SPATIAL_CONTAINER_NETWORK=true` (Compose); downgrades 0001/0002 recusam; fila de jobs
  recusa (409) com histórico de runs cheio; `operation.denied` só para recusas protetivas
  (`ProtectiveDenial`); portas `SampledSource`/`StreamingSource` com conformidade.
- **Docs:** `.env.example` completo, README (perfil, WS, `/docs` opcional, guias antes
  órfãos), roteiro RuView com opt-in, nota histórica no relatório v3, nome corrigido em
  README_IMPORTANTE. `.gitattributes` (`eol=lf`) evita CRLF em checkouts Windows, que
  quebravam o gate do Prettier.
- Testes novos: enforcement por perfil (27), config (4), políticas (4), conformidade (1),
  helper web (1).

Gate `check.ps1` exit 0: Ruff/format, 20 contratos, 253 backend, 6 launchers, Prettier,
33 web, ESLint, tsc, build e 9 E2E Chromium (34,1 s), 1 skipped. Perfil `commercial-br`
coberto por testes de API; não houve E2E de navegador nesse perfil.
Correção do E2E do PR #6 (`eb4e28a`): `pause` só reporta `paused` depois de
`queue.join()` (antes o estado mudava com eventos ainda na fila, total 30→32); specs E2E
aguardam o POST de pausa e o de recuperação para a sessão antes de começar. Teste de
regressão `test_paused_state_is_reported_only_after_the_queue_is_drained`. Gate exit 0
(254 backend, 9 E2E).

Demo Docker reconstruída (`docker compose up --build --detach --wait`, sem `down -v`):
volume `wifi-spatial_spatial-data` preservado (cópia prévia fora do repositório), Alembic
em `0008`, 10.000 eventos mantidos, api/web healthy; health, status, catálogo (perfil
`lab`, 7 capacidades ativas), eventos, sensores e rede 200 com token; `/docs` 404.
Pendente: fixar imagens por digest; histórico de regras (migração); tipagem Python;
NVDA/WebKit; E2E de navegador no perfil `commercial-br`.

## Claude Code: modularização do backend — 15/10/2026, 23:44–00:10

Feita após confirmação de que a sessão Codex estava parada (sem edições havia 10 min);
snapshot prévio no scratchpad da sessão. Detalhes em ADR-011.

- `main.py` de 530 para 115 linhas: composição apenas. Novo `bootstrap.py` (Container)
  e routers em `app/api/` (simulação, analytics, model lab, automação, catálogo/
  governança, stream). OpenAPI comparado antes/depois: 36 paths, operações e
  componentes idênticos; WebSocket coberto pelos testes existentes.
- `storage.py` de 452 linhas para fachada de 158 sobre `adapters/sqlite/` (database,
  models, events, rules, reports, lab, audit). Interface pública e transação evento +
  decisões preservadas.
- Também: `Pipeline.quiesced()`, constantes de cenário/sala/sensores e limites de regras
  no domínio, heartbeat WS sem descartar evento, `/system/status` no event loop,
  `/features` lista analytics/replay/model lab/automação como IMPLEMENTED_SYNTHETIC.
- Testes novos (`test_catalog_routes.py`, 6): providers com/sem legado, features, ciclo
  start→reset→start auditado, constantes × contrato × rotas e main sem rotas em closure.

Gate `check.ps1` exit 0: Ruff/format, 20 contratos sincronizados, 217 backend,
6 launchers, Prettier, 32 web, ESLint, TypeScript, build e 9 E2E Chromium (39,4 s),
1 skipped. Sem commit/push.

## Claude Code: pendências da auditoria e CI gratuito — 15/10/2026, 22:15–22:58

Executado em paralelo à sessão Codex abaixo (mesma árvore). Reverificação dos 70
achados abertos da auditoria por três agentes somente leitura; correções com Red→Green:

- **Storage/analytics (P2):** janela temporal usa o índice de timestamp (pré-filtro
  lexical ±1 s + UDF exata, ADR-003 preservado); retenção sem OFFSET, só sobre
  L0_SYNTHETIC; replay paginado no SQL (`count(*)` + página); run/relatório e
  auditoria na mesma transação; payload armazenado inválido é excluído e declarado
  em `limitations`, sem HTTP 500. Medido com 100 mil linhas: janela de 1 min 256→1,2 ms,
  página de replay 261→7 ms, fronteira de retenção 62→5 ms.
- **Runtime:** `RecursionError` de frame RuView rejeitado; falha inesperada do provedor
  para a sessão sem matar a tarefa de ingestão.
- **Frontend:** WS com deps `[token]` (paginar não reconecta); paginação de analytics
  usa a consulta aplicada (fim fixo) sem refazer replay; replay detecta mudança de
  total durante a carga; null nunca vira barra zero; borda de campos 3,34:1; `lang="en"`
  em textos da API; foco ao entrar/sair/fechar aviso; Sair zera a sessão; marca não
  recarrega a página; carga inicial e estados vazios no Model Lab/Automação; live
  regions sempre montadas; painéis memoizados; axe com `wcag22aa`.
- **Scripts/testes:** guarda E2E externa real (`e2e/target.ts`: projeto isolado, token e
  porta explícitos, porta conferida no Docker); `docker-e2e.ps1` com projeto e volume
  descartáveis por execução; conftest isola `SPATIAL_*`; `Get-ProjectPython` robusto no
  PS 5.1 (reproduzido e corrigido); `finally` restaura variáveis antes do shutdown;
  credenciais RuView sem `python -c`; smoke scripts sem proxy; Compose repassa backup e
  rate limit; `.dockerignore` com `**/runtime`; Playwright com diretório temporário por
  execução; gate de Prettier (`format:check`) e teste Alembic × ORM (`compare_metadata`).
- **CI gratuito:** `.github/workflows/ci.yml` (backend 3.12/3.13, web, E2E Chromium,
  Gitleaks pinado por checksum, npm audit), `.github/dependabot.yml` e
  `.pre-commit-config.yaml` opcional; actions pinadas por SHA de releases com ≥2 semanas.

Gate `check.ps1` (22:40) exit 0: 200 backend, 6 launchers, 30 web, Prettier, contratos,
build e 9 E2E. Jobs da CI reexecutados em contêineres Linux: backend 3.12 e 3.13 (211 +
6 testes, pip-audit sem vulnerabilidades), web (lint, tipos, 30 testes, build), E2E (9
pass, 1 skip). Gitleaks e pre-commit não executados localmente (exigiriam baixar
ferramentas); rodam no GitHub quando houver push. Nenhum commit/push nesta etapa.

Modularizar `main.py` em routers e `Store` em repositórios foi adiado nesta etapa para
não colidir com a sessão Codex; concluído depois (entrada acima, ADR-011).
Também pendentes P3 estruturais: hierarquia de exceções, `Pipeline.quiesced()`,
catálogo de constantes, porta `SourceProvider`, `/features` coerente, docs opt-in.

## Plano v4, catálogo de capacidades e análise de canais — 15/10/2026, ~22:20–23:10

Decisão do proprietário: construir todas as capacidades com funcionalidade e recortar
depois por mercado/regulação. Registrada como seção 0A do plano mestre (agora v4.0;
seções v3 seguem vigentes) e resumida em CLAUDE.md.

- **Catálogo** `apps/api/app/capabilities.py` + `GET /api/v1/capabilities`
  (autenticado): 12 capacidades em grupos A–D com status, evidência máxima, etiquetas
  `LGPD_PERSONAL/LGPD_SENSITIVE/ANATEL_RADIO/ANVISA_SAMD`, hardware/consentimento e
  perfis. `SPATIAL_CAPABILITY_PROFILE` (`lab` padrão, `commercial-br`). Perfil
  comercial nunca liga ANVISA, grupo D, PLANNED ou BLOCKED (teste). Hoje o catálogo
  é informativo: os endpoints existentes ainda **não** são bloqueados pelo perfil.
- **Grupo A — ocupação de canais**: parser `parse_networks` (pt/en) da lista passiva
  `netsh wlan show networks mode=bssid`, agregação por canal no host (SSID/BSSID
  descartados), contrato `ChannelSurvey`, tabela `channel_surveys` (migração 0008),
  `POST /api/v1/network/channel-surveys`, `GET /api/v1/network/channel-plan` com
  heurística de interferência (sobreposição 2,4 GHz, bloco 80 MHz em 5 GHz, desconto
  do próprio AP, margem 0,5, 6 GHz só listado). Coletor `--channel-survey`
  (`-ChannelSurvey` no script), a cada 60 s.
- **UI**: seção "Ocupação de canais" no painel Wi-Fi e painel "Capacidades e
  enquadramento" no dashboard. Contratos exportados (20 arquivos), Zod sincronizado.
- **Testes**: `test_channel_plan.py` (11 casos: parser sem vazamento de identificadores,
  agregação, contrato, recomendações, janela, API autenticada/idempotente, perfis),
  `tests/capabilities.test.ts` (2), `e2e/network.spec.ts` estendido (recomendação,
  catálogo, axe em `#capabilities`).
- **Teste real (L2)**: API isolada na porta 8765 com banco temporário; coletor
  `--once --channel-survey` neste host entregou amostra e varredura; plano: 5 GHz
  KEEP no canal 149; 2,4 GHz canal 1 mais ocupado (provavelmente o rádio 2,4 GHz do
  próprio roteador — limitação documentada). Stack Docker em 8000 não foi
  reconstruída; ela ainda roda o código anterior, sem a migração 0008.

Gate `check.ps1` exit 0: Ruff/format, contratos sincronizados (20), 211 backend, 6 launchers,
32 web, ESLint, TypeScript, Prettier, build e 9 E2E Chromium passaram, 1 skipped
(RuView), 43,4 s. WinError 10054 no fechamento forçado reapareceu, sem falha.

Pendências: aplicar o perfil como bloqueio real dos endpoints; reconstruir a stack
Docker para aplicar 0008; próximos itens do grupo A (mapa por ponto com planta,
alertas de degradação, inventário da própria rede); hardware CSI para grupos B/C.

## Continuidade Claude Code: revisão Codex e auditoria — 15/10/2026, 20:54–21:03 Fortaleza

Revisadas as entregas Codex de 18:32–20:46 (correções, avatares articulados,
ROADMAP_AND_SKILLS, MASTER_EVOLUTION_PLAN e o módulo `/api/v1/network`). O módulo de
rede ainda não tinha registro aqui: código, testes e WIFI_DIAGNOSTICS.md existem e
passaram no gate abaixo (test_network_diagnostics, network.spec), sem nova coleta
real nesta sessão. Telemetria segue L2_LIVE_UNVALIDATED, separada do domínio espacial.

Cruzados os 91 achados confirmados da auditoria adversarial de 15:20 (sem P0) com o
código atual. Codex já tinha resolvido worker de jobs, close WS 4002, proxy headers,
drift de contratos e validação de controles. Corrigidos agora com Red→Green:

- P1: backlog de sessão encerrada por falha de persistência era gravado sob o
  segment_id da sessão seguinte. O segmento passa a ser capturado no enfileiramento
  (Store.write aceita segment_id), itens da geração falhada são descartados e o
  start aguarda a fila. Teste: test_pipeline_sessions (2 casos).
- status() lia o deque de medições do threadpool: "deque mutated during iteration"
  reproduzido; agora usa cópia atômica e `latest` local.
- Migrações Alembic não atômicas no SQLite: falha entre passos deixava coluna
  aplicada e versão antiga. env.py usa BEGIN IMMEDIATE, DDL transacional por
  revisão, busy_timeout/UDF e dispose do engine. Teste com falha injetada e retry.
- Backup deixava snapshot órfão em falha e prune quebrava com FileNotFoundError:
  cópia em arquivo temporário verificada antes do rename; manifesto ausente gera
  recusa estável; conexão de retain() fechada explicitamente.
- Corpo HTTP lido/parseado antes da autenticação sem limite: middleware BodyLimit
  (64 KiB, 413), inclusive para corpo chunked.
- Reconexões WS legítimas consumiam o balde de falhas "auth" (31ª conexão negava
  token inválido com 429 e o stream com 1013). Novo balde `stream`
  (SPATIAL_RATE_STREAM=120/min); "auth" só conta falhas, incluindo timeout, JSON
  inválido e primeiro frame binário. Assinante só entra após autenticar; handshakes
  pendentes continuam ocupando vaga do limite de oito.

Gate check.ps1 exit 0: Ruff/format, contratos sincronizados (16), 190 backend,
6 launchers, 26 web, ESLint, TypeScript, build e 9 E2E Chromium (32,5 s), RuView
skipped. WinError 10054 no fechamento forçado reapareceu, sem falha de teste.
Snapshot pré-mudanças desta sessão: artifacts/pre-change-snapshot-2026-10-15.tar.gz.
Pendências da auditoria (P2/P3) seguem em ROADMAP_AND_SKILLS/TASKS: varredura de
analytics via UDF sem índice, paginação de analytics pelo formulário não submetido,
contraste de bordas, null desenhado como zero, decomposição de main.py/Store.
Sem commit/push, dado real, serviço pago ou dependência nova.
Às 21:10, por solicitação do proprietário, somente o serviço `api` da stack de uso
foi reconstruído (`docker compose up --build --detach --wait --no-deps api`); web
intocado, volume `wifi-spatial_spatial-data` preservado. API healthy, histórico
com 10.000 eventos antes e depois, e corpo de 70 KB recusado com 413 na imagem nova.

## Pessoas e animais articulados — 15/10/2026, 20:02–20:12 Fortaleza

Encerramento: ajuste final de fullscreen aprovado em Chromium/Firefox (dois casos,
13,9 s); lint/tipos/build exit 0; web de uso reconstruído e healthy, API preservada.

Escopo confirmado: visual agora e pesquisa RF depois; screenshot do proprietário
usado como direção visual. Adicionadas rigs procedurais próprias de pessoa (17
pontos), cão e gato, perspectiva isométrica SVG, corpos luminosos, articulação por
tick/cenário, elenco misto, volume opcional, tela cheia e retorno à planta 2D.
Preferência de movimento reduzido respeitada. IDs SVG únicos no live/replay.

Sem nova dependência, contrato ou migração; contagem/posições continuam da fonte
sintética. Avatar selecionado não é espécie reconhecida. Sem posições externas,
nenhum corpo é inventado. Vitais/RSSI/confiança não foram fabricados para imitar
a referência. Não há câmera orbitável, malha física ou inferência RF neste renderer.

Gate check.ps1 exit 0: 175 backend, 6 launchers, 25 web, lint/format, TypeScript,
14 contratos, build e 8 E2E Chromium (32,0 s), um legado skipped. E2E novo testa
humano/misto/contagem, volume, planta, pause, reduced-motion, 320 px sem overflow e
axe sem violações automatizadas. Caso passou também no Firefox (6,3 s).
Docker isolado: seis E2E (26,9 s), três skipped por escopo; 13 payloads idênticos
após restart e relatório/replay/experimento preservados. Volume mantido.

Teste adicional de entrar/sair da tela cheia passou nos dois browsers. Capturas
desktop/mobile/imersiva abertas e inspecionadas. Encontrado corte na barra superior
em tela cheia; corrigido grid e adicionado check explícito de largura. Build e
E2E direcionados finais no relatório, sem repetir backend inalterado.

Demo de uso em 3000/8000 atualizada somente pelo serviço web, API/histórico
preservados. Navegador conectado com três ocupantes sintéticos e elenco misto;
tokens somente em memória. Aplicação deixada ativa para avaliação.

Pesquisa criada em PEOPLE_ANIMALS_RF_RESEARCH.md, com revisões HF conferidas:
encoder pretrained MIT (8→128 features/embedding) candidato opcional; 82,3% é
triplet temporal, não pose. Pose MM-Fi é outro modelo, CC BY-NC 4.0; pesos não
incluídos no produto comercial. Nenhum peso/script remoto baixado/executado,
hardware capturado ou runtime externo obrigatório. Próximo R0/R1 no guia.
README, decisões ADR-009, especificação, originalidade, tarefas e matriz atualizados.
Sem commit/push, descarte de staged IDE, limpeza de uso ou gasto.

## Demonstração disponível para avaliação — 15/10/2026, 20:00 Fortaleza

Por solicitação do proprietário, stack normal iniciada por
`docker compose up --build --detach --wait`, sem usar runner de testes nem apagar
histórico. API 8000 e dashboard 3000 publicados somente em loopback, ambos healthy;
health retornou ok/simulation-only e dashboard HTTP 200. Navegador visível aberto,
conectado com token local somente em memória, cenário sintético iniciado e
ocupantes virtuais visíveis. Credencial não impressa nem incluída em URL/storage.
Recibo sem segredos: artifacts/demo-browser-ready.json. Containers e navegador
deixados ativos para avaliação. Para encerrar a stack: `docker compose down`,
preservando volume. Sem commit/push ou alteração da aplicação nesta inicialização.

## Docker operacional — 15/10/2026, 19:43–19:45 Fortaleza

Desktop estava inicializando e concluiu startup: engine Linux 29.8.2/contexto
desktop-linux/WSL2 ativos. Sem reinstalação, mudança global de configuração, reset
ou prune. README orienta verificar status e iniciar Desktop se estiver parado.

Executado docker-e2e.ps1: exit 0, builds atuais, API/web healthy, cinco E2E (23,5 s),
três skipped por escopo, 12 payloads idênticos após restart e relatório/replay/
experimento preservados. Stack própria encerrada sem excluir volume.
Python 3.13: imagem reconstruída, 175 backend e seis launchers passaram, Ruff e
ambas auditorias de locks aprovados sem vulnerabilidades conhecidas. Primeiro
run apontou EXE002 em dois testes; shebangs adicionados, rebuild/run aprovados.

Bloqueio Docker/Python 3.13 anterior resolvido, TASKS e planos atualizados.
Nenhum commit/push ou perda de histórico. Evidências em VERIFICATION_REPORT.md.

## Evolução corporativa incremental — 15/10/2026, a partir de 18:32 Fortaleza

Encerramento 18:49: frontend final com lint/tipos/build aprovados e 14 E2E
Chromium/Firefox (51,4 s), dois legados skipped. Gates e limites completos abaixo.

Diagnóstico, skills, correções, backlog de produto e artefatos executivos entregues
sequencialmente sobre o mestre v3. Branch feat/platform-foundation, HEAD 2767417;
staged `.idea/.gitignore` preservado. Sem commit/push, publicação ou serviço pago.

Baseline atual divergiu do histórico: Ruff bloqueou duas linhas de testes;
execução direta encontrou 166 backend pass/8 fail e 11 web pass/10 fail.
Contratos Python/export haviam evoluído localmente; fixtures e cliente divergiam.
Preservados os testes e intenção das alterações anteriores.

Implementado nesta etapa: cliente HTTP/CSV com ApiError e mensagens acionáveis;
JSON 500 sanitizado/no-store; contratos Zod discriminados por versão, UUID genérico
e tolerância histórica; schemas/fixtures regenerados e drift check no gate;
close WS privado 4002; merge temporal REST/WS; recuperação seletiva de aviso;
controles independentes da validação do formulário fora do start nativo;
painéis secundários com next/dynamic e loading acessível; janela geométrica rejeita
primeiro ponto fora da sala. Não há ganho percentual de performance medido.

Seis testes existentes de launchers reproduziram spoofing de peer por
X-Forwarded-For. Aplicado --no-proxy-headers em dev/E2E/Docker; testes incluídos
no gate. Dockerfile.verify inclui contratos e arquivos necessários aos testes.
Dois E2E novos verificam controle com draft inválido enquanto outro operador inicia
sessão via API real e fechamento de stream inválido sem exceção no browser.

Gate oficial: exit 0, 175 backend, 6 launchers, 21 web, lint/format, TypeScript,
14 contratos sincronizados, build e 7 E2E Chromium; RuView skipped. Último ajuste
de captura do aviso de sincronização recebeu lint/tipos/build e browsers separados,
conforme VERIFICATION_REPORT. Auditorias npm e ambos locks Python: zero
vulnerabilidades conhecidas. Desktop/mobile abertos e inspecionados, sem redesenho.

RUVIEW_FEATURES_ANALYSIS preservado com adendo; ROADMAP_AND_SKILLS e
MASTER_EVOLUTION_PLAN criados. README, ADR-008, originalidade, matriz e segurança
atualizados; TASKS.md e dashboard.html auxiliar do productivity, não executado.

Pendências: Docker daemon ausente, containers/Python 3.13 atuais BLOCKED;
WebKit/NVDA não reexecutados; RuView oficial sem nova integração. WinError 10054 e
NO_COLOR observados, sem supressão. Tipagem Python integral, benchmark, RBAC/TLS
público e hardware/validação científica permanecem fora da entrega comprovada.
Próximo: gates Docker quando disponível e tipagem Python gradual.

## Gate integrado fechado — 15/10/2026, 15:05–15:10 Fortaleza

Executado por Claude Code sobre a árvore atual, sem alteração de código. A falha
"a diagnosticar" registrada às 14:36 não se reproduz: as correções posteriores
(main.py, experiment_jobs.py, testes e E2E de 14:37–14:39) já estavam aplicadas.

- check.ps1 completo: exit 0. Ruff/format, 135 backend (31,07 s), ESLint,
  TypeScript, 11 web, build:e2e e 5 E2E Chromium (23,4 s); RuView skipped.
- E2E_BROWSERS=chromium,firefox: 10 pass (48,8 s), 2 legados skipped.
- Python 3.13 Docker (imagem reconstruída): 135 pass, Ruff e pip-audit dos dois
  locks sem vulnerabilidades conhecidas. npm audit: 0 vulnerabilidades.
- docker-e2e.ps1: stack nativa API/web, 5 E2E, reinício real com 12 payloads
  idênticos, relatório, replay e experimento preservados; legado off.

Residual: WinError 10054/Proactor reapareceu no fechamento forçado do E2E MVP,
sem falha de teste. WebKit e NVDA continuam BLOCKED. Nenhum commit/push; 155
arquivos untracked e .idea/.gitignore staged preservados. Detalhes no
VERIFICATION_REPORT.md. Próximo: commits por escopo mediante autorização.

## Avanço local F3B/F4/F5/F6 — 15/10/2026, 14:36 Fortaleza

G: 128 backend/11 web/lint/tipos/build passaram no gate; E2E novo falhou por
comparar innerText com textContent incluindo details oculto, sem divergência de
payload. Corrigido uso consistente de innerText: E2E G passou (3,5 s, total6,7 s).
Python 3.13 refeito nesse incremento: 128 pass (26,89 s), Ruff e auditorias dos
dois locks sem vulnerabilidades conhecidas. Modificações posteriores exigem novo gate.

F4: fila de uma CPU/duas esperas, estados persistidos, progresso por etapa,
cancelamento cooperativo e interrupted no restart implementados; 3 testes novos
passaram, incluindo capacidade/falha/cancelamento. UI integrada em validação.
F5: DSL restrita de presença/ocupação, API/SQLite/UI de regras e decisões dry-run,
revogação com drenagem e auditoria; Red ausente → 2 testes passaram. Nenhum despacho.
F6: protótipo de pacote próprio offline, autorização/allowlist virtual, checksum,
sequência/clock/limites; Red ausente → 2 testes passaram, incluindo 200 bytes fuzz.
F7: protocolo preparado; captura e desempenho físico continuam BLOCKED.
Gate integrado atual encontrou uma falha a diagnosticar; nenhuma conclusão integral.

## Marcos C/D/E/F e G integrado em validação — roteiro v3

C: limites locais e negativas auth/origem/WS/timeout/capacidade/operação
implementados; 8 testes específicos passaram. Timeout/malformed WS agora fecham
explicitamente o transporte: teste novo encontrou espera sem close e comprovou
a correção. Audit agregado tem tipos fixos, sem payload/segredo e sem crescimento
por identidade atacante. CSP usa nonce por resposta e scripts sem unsafe-inline;
estilos inline continuam exceção explícita. Next agora renderiza dinamicamente.

D: Firefox e WebKit baixados pelo Playwright. Chromium + Firefox: 6 E2E passaram
(36,7 s), dois legados skipped; inclui API real, analytics, mobile/axe e teste
negativo de script. WebKit BLOCKED por ngtcp2_crypto_quictls.dll ausente; NVDA
continua indisponível. Nenhuma dependência global do SO foi alterada.
Gate intermediário -SkipE2E: 124 backend, 10 web, lint/tipos/build aprovados.

E/F: fronteiras e testes nativos preservados, analytics revalidado nesses browsers.
G: domínio de janelamento/treino/avaliação geométrica sintética, separação por
sessão/configuração, hashes, artefatos JSON locais, migração 0004, API autenticada
e UI de matriz/predições/export/histórico implementados; testes de domínio/API
passaram. Gate integrado/E2E G em execução. RF/sitting/queda continuam sem suporte.

## Execução do roteiro v3 — marcos A/B/C em andamento — 15/10/2026

Mestre v3 relido, hash inalterado. Baseline check.ps1 exit 0: 111 backend
(27,33 s), 10 web, lint/tipos/build e 2 E2E (19,0 s); legado skipped.
WinError 10054 reproduzido no fechamento forçado do MVP; recuperação passou.
Git inicial: IDE staged preservado e 120 arquivos untracked, zero diff rastreado.

B: rotina recorrente opt-in no lifespan, desligada por padrão, destino limitado
ao workspace, lock exclusivo, status sem caminhos/segredos, encerramento com
espera da cópia; nenhum prune/expurgo automático. Red módulo ausente, Green:
5 testes incluindo escrita concorrente, restore, hold, exclusão e status real.
C: rate limiter em memória com relógio injetável, TTL/capacidade e classes
independentes; negativas agregadas em tabela aditiva limitada por tipos fixos,
sem tokens/IP/payload. Red módulo ausente; 18 testes segurança/API passaram.
Próximo: completar auditoria negativa, CSP e gates, depois compatibilidade e G.

## Roteiro de continuidade criado — 15/10/2026

Criado [EXECUTION_PLAN_V3.md](EXECUTION_PLAN_V3.md), subordinado ao mestre v3.0,
com comando único PowerShell para iniciar o Codex no checkout existente, backlog
detalhado, critérios de avanço, comandos de verificação, bloqueios e retomada.
Abrange estabilização F0R/F1R/F2R/F3A, baseline F3B e avanço condicionado F4–F7.
O indicador de 69 warnings informado pelo usuário permanece sem lista individual;
não foi convertido em diagnóstico. Esta entrega é documental: não executa o
backlog, não inicia serviços nem altera resultados de testes anteriores.
Sintaxe do CLI conferida localmente e comando analisado sem executá-lo.
Staged da IDE preservado; nenhum commit/push ou alteração de runtime.

## Marco funcional vigente — v3.0 — 15/10/2026, 14:08 Fortaleza

Plano oficial confirmado v3.0, incluindo Clean Room Design e F0R/F1R/F2R;
hash e leitura integral registrados em VERIFICATION_REPORT.md. Registros abaixo
são cronológicos: números menores e pendências já resolvidas são históricos.

Motor synthetic-native padrão e contrato 2.0.0 implementados, domínio puro com
portas/adaptadores, legado opt-in off, MVP preservado. F3A funcional: API/SQLite,
agregações 1/5 min/hora/dia, UTC, filtros/paginação, presença/ocupação, intervalos
desconhecidos, deltas líquidos, métricas de software, playback 2D, CSV/JSON e
relatórios persistidos. Dados exclusivamente L0_SYNTHETIC.

Último check.ps1: exit 0, 111 backend Windows, 10 web, Ruff/ESLint/TypeScript,
build e 2 E2E Chromium aprovados; legado skipped no modo padrão. Python 3.13:
111 testes e Ruff aprovados; auditorias detalhadas no relatório. Laboratório
legado foi revalidado separadamente com 3 E2E (antes da última correção temporal).
Docker atual confirmou 24 payloads, replay e relatório intactos após restart.
Backup/restore e retenção verificados em fixtures, sem expurgar histórico de uso.

Corrigidos lint E501, depreciação TestClient, contrato UTC, overflow 320px,
precisão submilissegundo SQLite e corrida de teardown WS reproduzida em 3.13.
F1R permanece parcial por browsers/leitor de tela ausentes e controles adicionais;
F2R tem independência operacional, sem certificação clean-room estrita devido à
exposição prévia. Pendências priorizadas e inventário: TECHNICAL_REPORT_V3.md.
Nenhum commit/push; staged IDE e todos os arquivos locais preservados.

## Continuação em execução — plano v3.0 — 15/10/2026

O mestre v2 foi inicialmente encontrado em docs/docs/ e copiado ao caminho
canônico com hash idêntico. Posteriormente o responsável disponibilizou v3.0
no caminho oficial `docs/PROJECT_MASTER_PLAN.md` (29.666 bytes, leitura confirmada
às 13:35 no Windows). A versão 3 foi lida integralmente e passa a orientar a
evolução; a duplicação antiga não é fonte de requisitos. Registros abaixo são
históricos e não significam indisponibilidade atual do documento.

Implementado nesta continuação, sem commit/push e preservando IDE staged:

- F3A: API de agregações UTC, filtros, replay, transições líquidas sem identidade,
  relatórios SQLite, migração aditiva 0002 e UI integrada com export CSV/JSON.
- Manutenção: backup SQLite consistente, checksum/integridade, restore exclusivo
  para destino novo, arquivo verificado antes de expurgo de auditoria, proteção
  de eventos security./audit. e hold; retenção de snapshots; logs rotativos.
- Depreciação resolvida com httpx2 2.13.1, conforme Starlette instalado e docs;
  dependência gratuita apenas de desenvolvimento e locks atualizados.
- Lint E501 reproduzido e corrigido em duas linhas SQL da fixture. Última execução
  Windows: Ruff, 100 testes backend, oito web, ESLint, tipos e build passaram.
- Python 3.13 Linux: imagem isolada construída com o lock; execução concluída
  com 98 testes e duas auditorias sem vulnerabilidades conhecidas. Essa imagem
  precede os dois testes adicionais de logs/retenção e migração; não declarar 100
  no Python 3.13 antes de reconstruir/reexecutar.
- E2E MVP e legado passaram; E2E F3A chegou a replay/export/snapshot SQLite e
  detectou overflow em 320 px. Correção de min-width/grid implementada, ainda
  aguardando nova execução. Falha anterior de seletor ambíguo de status corrigida.
- RuView ocupado em 4860 preservado; runner permite portas alternativas 4970/4971.
  Com v3, trabalho novo seguirá modo nativo e laboratório legado opcional/off.

Próximo: concluir regressão mobile/E2E e isolar domínio/portas/provedor nativo.
Firefox, WebKit e NVDA não instalados no Windows: BLOCKED para validação assistiva
e nesses motores. A lista original de 68 warnings não foi fornecida; não inventada.

## Encerramento da etapa técnica — 15/10/2026

O responsável confirmou que o PROJECT_MASTER_PLAN v2.0 não está disponível
localmente nem no GitHub e determinou concluir apenas as verificações existentes.
A pendência documental fica registrada: não reconstruir requisitos nem avançar
a F3A por suposição. Conformidade formal F0/F1/F2 permanece pendente do mestre.

As verificações técnicas executadas nesta etapa estão concluídas: a execução final
de `scripts/verify/check.ps1 -RuView` passou com 83 testes backend, sete testes web,
dois E2E, Ruff, ESLint, TypeScript e build. Compose isolado comprovou persistência
de oito eventos após reinício real da API; verificações Linux e auditorias de
dependências também passaram, com os limites temporais descritos no relatório.
Nesta confirmação de encerramento foram revisados os registros e o Git; não houve
nova execução das suítes, alteração funcional, commit ou push.

Evidências e limitações: [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md) e
[REQUIREMENTS_TRACEABILITY.md](REQUIREMENTS_TRACEABILITY.md). O aviso
TestClient/httpx e as validações adicionais já listadas continuam pendentes;
não impedem registrar a conclusão das verificações efetivamente executadas.
Dados mantidos em `L0_SYNTHETIC`; alterações locais e IDE staged preservados.

## Retomada de verificação — 15/10/2026

- Leitura integral de AGENTS.md, CLAUDE.md, PROGRESS.md, SECURITY_REVIEW.md e
  PHASE_RECONCILIATION.md. O plano mestre v2.0 continua ausente localmente.
- Consulta somente leitura ao GitHub via gh: repositório
  matheussiqueira-dev/WiFi-Spatial-Intelligence-Platform com apenas a branch main,
  árvore contendo somente LICENSE, nenhum PR e nenhum commit encontrado para
  docs/PROJECT_MASTER_PLAN.md. O link remoto não permite recuperar esse documento.
- A correção já presente em test_websocket_connection_limit fecha os transportes,
  aguarda até três segundos pela liberação dos assinantes e verifica um novo slot.
  Dez execuções independentes do teste passaram; isso não comprova ausência de
  toda intermitência possível.
- scripts/verify/check.ps1 passou: Ruff lint/formatação, 83 testes Python, ESLint,
  TypeScript, sete testes web, build de produção para E2E e um E2E Chromium com
  API real e banco temporário isolado. O E2E RuView foi ignorado pelo modo padrão;
  não houve revalidação do motor externo nem das auditorias Docker nesta retomada.
- Permanece o aviso de depreciação Starlette/TestClient/httpx. Nenhuma dependência
  foi alterada. Evidências anteriores de F2 continuam históricas.
- IDE staged e demais arquivos locais preservados; nenhum commit ou push.
  Conformidade com o mestre e trabalho dependente de F3A continuam pendentes de
  requisitos fornecidos, sem reconstrução do plano por hipótese. Todos os dados
  continuam L0_SYNTHETIC.

## Auditoria técnica F0/F1/F2 — 15/10/2026

Nova solicitação: auditar conformidade com PROJECT_MASTER_PLAN v2.0 e continuar
o backlog pela F3A. O arquivo mestre continua ausente no caminho informado e na
busca de nomes do workspace. Sua localização foi solicitada. Não foi inventado um
mestre nem um backlog de analytics; conformidade formal e F3A dependem dessa fonte.

- Criados [REQUIREMENTS_TRACEABILITY.md](REQUIREMENTS_TRACEABILITY.md), com 20
  itens técnicos locais, e [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md), com
  comandos, resultados, falhas, correções e limites. Não substituem o mestre.
- Primeira verificação completa `check.ps1 -RuView` passou: 83 testes backend,
  quatro contratos web, lint/tipos/build e dois E2E Chromium (41,8 s).
- Stack Compose isolada revalidada: API/web/RuView healthy; fluxo oficial simulado
  persistido e oito eventos com payloads idênticos após reinício real da API.
  Volume preservado; recibo em `artifacts/f2-compose-receipt.json`.
- Linux: Ruff e 83 testes passaram; npm audit e pip-audit dos dois locks sem
  vulnerabilidades conhecidas nas consultas desta execução.
- Corrigido nome acessível do mapa: null RuView não é zero; sem observação não é
  sala vazia; estimativas sintéticas e posições indisponíveis são explícitas.
  Três testes novos de renderização, sete testes web aprovados.
- Uma repetição encontrou CancelledError intermitente no teardown do teste do
  limite WebSocket. Corrigida sincronização por condição e adicionada prova de
  liberação/reutilização dos slots, sem suprimir erros. Teste direcionado passou.
- Verificação final integrada `check.ps1 -RuView` passou após as correções: Ruff,
  83 testes backend Windows (25,89 s), ESLint, TypeScript, sete testes web, build
  e dois E2E Chromium (31,1 s). Serviço de verificação encerrado.
- Arquivos de IDE staged e alterações locais preservados. Sem commit/push,
  exclusão de histórico, serviço pago ou alteração de política do SO. Sem nova
  dependência, mudança de contrato ou promoção de evidência além de L0_SYNTHETIC.

Pendências: fornecer mestre v2.0; executar F3A segundo seus requisitos; decidir
backup/expurgo conforme prioridades oficiais; depreciação TestClient/httpx;
Python 3.13, leitores de tela e outros navegadores ainda sem validação.

Atualização em 14/10/2026 (America/Fortaleza). Branch `feat/platform-foundation`.

## Continuação F2 — estado atual

**F2 implementada e validada tecnicamente no modo simulado**, conforme o critério
explícito da solicitação: imagem oficial RuView executada, fluxo WS consumido,
eventos normalizados apresentados no dashboard e persistidos em SQLite.
Todos continuam `L0_SYNTHETIC`. Não há validação científica/clínica ou hardware.

O documento mestre permanece ausente. [PHASE_RECONCILIATION.md](PHASE_RECONCILIATION.md)
registra a matriz verificável de F0/F1, decisões e a pendência formal. Nenhuma fase
foi declarada conforme a um documento inexistente. O registro do MVP abaixo é
histórico; os resultados atuais estão nesta seção.

### Implementação e preservação

- Inspecionado upstream oficial HEAD `a1ca023ee872683d160250d47ae3d4d228af55a0` e
  revisão OCI `0f95193190261a8966ad5f52e188aa6a480c2968`. Imagem fixada em
  `sha256:bd2b2648a75ffb498a8e001b54c957c1f853d2ee709e16986d38f88676186d14`.
  REST `/api/v1/status`, `/api/v1/sensing/latest` e WS `/ws/sensing` verificados.
- `app/ruview.py`: I/O e normalização desacoplados de FastAPI/SQLite; verificação
  de simulated/synthetic/ready, Bearer upstream por header, URLs locais, sem proxies
  nem redirects, limites de frames/filas/timeouts, timestamps recentes, contagem
  coerente, reconexão progressiva e erros sanitizados. Sem fallback silencioso.
- Novo `RuViewEvent` 1.1.0 separado do `SensingEvent` 1.0.0 preservado. Presença e
  contagem são estimativas sobre sinais sintéticos; seed desconhecido = null,
  contagem ausente com presença = null; sem posições de verdade/modelo/confiança.
  Schema/exemplo aditivos e Zod compatível com histórico misto.
- Seleção autenticada `/sources/select` apenas com sessão parada. Controles antigos
  preservados; geração de sessão evita publicar frame pendente após pausar/parar.
  Sem rede sob o lock de controle. Pausa mantém conexão e descarta dados externos.
- Pipeline mantém gravação antes de publicação, retenção e auditoria. SQLite usa a
  mesma migração/tabela, sem apagar dados. Inserção idempotente para replay de UUID.
- Dashboard oferece fontes, origem em cada linha, diagnósticos de serviço/frescor,
  rejeições/duplicatas/reconexões e avisos explícitos. Não desenha posições inventadas
  do RuView nem apresenta sensores internos como conectados à fonte externa.
- `compose.ruview.yaml`, `start-ruview.ps1`, `check.ps1 -RuView` e verificação isolada
  Compose permitem iniciar/testar o motor oficial sem hardware. Segredo do serviço
  separado em arquivo ignorado, sem sobrescrever `.env`.
- Os oito cenários, código de SimulationProvider, contrato interno, locks e arquivos
  de IDE staged foram preservados. Não houve commit/push, reset/clean, limpeza de
  histórico de uso, dependência nova ou alteração de controles do SO.

### Evidências executadas nesta continuação

| Verificação | Resultado |
| --- | --- |
| Baseline pytest antes das edições | **48 passaram**, confirmando o estado real do MVP |
| `scripts/verify/check.ps1 -RuView` | Passou: Ruff, pytest, ESLint, TypeScript, contratos, build de produção e ambos E2E |
| pytest final Windows | **83 passaram**, incluindo 35 casos novos RuView; aviso httpx/TestClient já existente |
| pytest Linux / Dockerfile.verify | **83 passaram**, mesmo aviso; Ruff também passou |
| Contratos web | **4 passaram**, incluindo novo evento RuView e rejeição de falsas evidências/posições |
| E2E Chromium nativo | **2 passaram**, 28,3 s no último ciclo: MVP original e RuView oficial |
| RuView E2E | Frames normalizados via WS, histórico SQLite, pause/resume/stop, pausa real do container, obsolescência, recuperação/reconexão e retorno ao simulador interno |
| UI desktop/mobile | Zero violações axe WCAG 2 A/AA e 2.1 AA; viewport 390 × 844 sem overflow; capturas inspecionadas |
| Build Docker API/web | Passou; stack isolada com API/web healthy e RuView em simulated |
| `scripts/verify/ruview-compose.ps1` | Stack independente, REST/WS oficiais, evento da API comprovadamente persistido e payloads idênticos após reinício real da API; volume preservado |
| `npm audit` | Zero vulnerabilidades conhecidas |
| pip-audit Linux runtime/lock completo | Zero vulnerabilidades conhecidas nos dois locks |
| Prettier dos arquivos TS alterados | Passou |

Capturas atuais: `artifacts/ruview-dashboard-desktop.png` e
`artifacts/ruview-dashboard-mobile.png`. Recibo do reinício real em
`artifacts/f2-compose-receipt.json`. Artefatos/credenciais/bancos continuam ignorados.
Scripts de teste encerram somente seus próprios serviços e preservam volumes.

### Falhas encontradas e corrigidas

1. Entrypoint oficial recusa token ausente com bind externo: configurado token
   separado e publicação somente loopback, mantendo os controles upstream.
2. `--source` duplicado com CSI_SOURCE: launcher usa apenas a variável suportada.
3. Snapshot intermediário durante fechamento e servidor de teste congelado:
   diagnóstico atribuído antes de fechar; teste encerra ao receber close.
4. Parada intencional do consumidor gerava aviso de indisponibilidade:
   corrigida a corrida entre disconnect e receive; E2E exige ausência de erro ao parar.
5. Host `ruview` entre containers retornava HTTP 421:
   adicionada entrada explícita `SENSING_ALLOWED_HOSTS=ruview`, sem desativar validação.

### Pendências e limites atuais

1. Receber PROJECT_MASTER_PLAN para reconciliar formalmente F0/F1/F2; escopo oficial
   desconhecido não é aprovação implícita.
2. Sem CSI real, hardware, modelos próprios, vitais, pose validada ou validação
   científica/clínica. O fluxo externo contém estimativas sintéticas, não verdade espacial.
3. RuView não oferece replay nessa integração; pausas/interrupções deixam lacunas.
   Compatibilidade verificada com o digest fixado; outras versões exigem nova execução.
4. Limites locais de um worker, Bearer compartilhado, offset e auditoria sem expurgo
   permanecem. Não há autorização de exposição pública ou suporte multiusuário.
5. TestClient/httpx mantém o aviso preexistente. Leitores de tela, outros navegadores
   e Python 3.13 continuam sem validação nesta continuação.
6. Alterações locais, sem commit/push. Guia operacional em
   [RUVIEW_INTEGRATION.md](RUVIEW_INTEGRATION.md).

## Referência e preservação

O documento mestre `docs/PROJECT_MASTER_PLAN.md` não estava disponível nas inspeções
desta sessão. O responsável confirmou que o fornecerá posteriormente e autorizou
continuar com os requisitos expressos. Este registro não substitui o documento mestre.

O estado inicial tinha somente o commit `2767417` (LICENSE), `.idea/.gitignore` staged
e backend/configurações/scripts não rastreados. Nenhum arquivo local foi descartado,
nenhum commit ou push foi feito. A alteração staged de IDE permanece preservada.

## Última etapa encontrada

Estrutura parcial do monorepo e backend sintético escrito, sem evidência de execução.
Não havia páginas web, testes, locks, Compose ou documentação. Bootstrap referenciava
um lock inexistente. Empacotamento Python tentava incluir `app` e `migrations` como
pacotes, impedindo a instalação editable. As etapas iniciais não foram tratadas como
concluídas apenas pela presença de arquivos.

## Implementação desta sessão

| Área | Arquivos principais | Resultado implementado |
| --- | --- | --- |
| Monorepo/dependências | package.json, package-lock.json, apps/api/pyproject.toml, requirements.* | Workspaces npm, dependências fixadas, empacotamento Python explícito |
| Backend | apps/api/app/main.py, pipeline.py, simulator.py, storage.py | API autenticada, migrações, controles serializados, drenagem, persistência antes de transmissão, WAL |
| Contrato | apps/api/app/contracts.py, packages/contracts/, apps/web/src/lib/ | Contrato Pydantic, JSON Schema, exemplo exportado e validação Zod |
| Frontend | apps/web/src/app/, components/dashboard.tsx, observatory.tsx | Dashboard responsivo, SVG 2D, sensores virtuais, presença/ocupação, controles, histórico |
| Tempo real | main.py, dashboard.tsx | WebSocket autenticado, limite de conexões e filas, heartbeat, reconexão progressiva, sincronização REST |
| Windows | scripts/common.ps1, setup/bootstrap.ps1, dev/start.ps1, verify/check.ps1 | Python compatível, token aleatório, portas livres, readiness, processos próprios e validações |
| Docker | compose.yaml, apps/*/Dockerfile, .dockerignore | Containers sem root, publicação loopback, healthchecks, volume SQLite |
| Testes | apps/api/tests/, apps/web/tests/, apps/web/e2e/ | Cenários, contratos, API, persistência, controles e navegador real |

## Decisões para reconciliar

1. Um laboratório de 8 × 6 m, seis sensores virtuais e até 20 ocupantes, preservando
   os contratos e o simulador já existentes.
2. Simulação nominal de 2 Hz, velocidade 0,25×–4×; seed reproduz medições, não UUID/tempo.
3. Backend local de um processo/worker. SQLite com WAL e timeout de escrita.
4. WebSocket envia dados após persistência, com filas limitadas; frontend valida os
   eventos e usa REST a cada 2 s para reconciliar o estado e o histórico.
5. Token compartilhado de desenvolvimento, gerado localmente e guardado em memória
   no navegador; sem login multiusuário, serviços externos ou exposição na rede.
6. SVG 2D sem biblioteca gráfica externa; paleta de laboratório azul/cinza e indicadores
   verdes de ocupação sintética; fontes locais, layout com observatório central.
7. Interferência é uma perturbação de posições sintéticas, sem modelo físico de CSI.
8. Auditoria preservada ao apagar eventos; sem expurgo automático da auditoria.
9. O escopo de Fases 0/1 é provisoriamente a infraestrutura e o MVP descritos pelo
   responsável. A conformidade com o documento mestre depende de sua disponibilização.

## Resultados finais verificáveis

| Verificação executada | Resultado |
| --- | --- |
| `scripts/setup/bootstrap.ps1` | Passou: venv, dependências, contrato, npm ci e preservação de `.env` existente |
| `scripts/dev/start.ps1 -ApiPort 8200 -WebPort 3200` | Passou: API pronta, dashboard HTTP 200, modo simulation-only e header nosniff; Ctrl+C seguido de confirmação do batch liberou ambas as portas |
| `scripts/verify/check.ps1` | Passou integralmente no Windows |
| pytest Windows | **48 testes passaram**, um aviso de depreciação de TestClient/httpx |
| pytest Linux (Dockerfile.verify) | **48 testes passaram**, mesmo aviso |
| Ruff lint e format | Passaram no Windows e no Linux |
| ESLint 10 e TypeScript | Passaram; configuração e testes TS também checados |
| Testes web do contrato | **3 testes passaram**, usando fixture exportada pelo Python |
| Build de produção Windows | Passou com Next.js 16.4.0; rotas `/`, `/dashboard` e not-found |
| Build Docker | Passou para API Python 3.12 e web Node 22/standalone |
| Compose healthchecks | Ambos os containers ficaram healthy; portas publicadas em loopback |
| E2E Chromium nativo | **1 teste integrado passou** em 4310/4810, 16,0 s de execução total |
| E2E Chromium Docker | **1 teste integrado passou** em 3000/8000, 12,6 s de execução total |
| axe WCAG 2 A/AA e 2.1 AA | Zero violações automatizadas nas telas desktop e mobile verificadas |
| Reinício real do container API | Passou: **4 eventos persistidos**, payloads idênticos antes/depois, simulação parada após reinício |
| `npm audit` (incluindo dev) | **Zero vulnerabilidades conhecidas** |
| pip-audit Linux (runtime e lock completo) | **Zero vulnerabilidades conhecidas** em ambos os locks |
| Git / exclusão de segredos | Branch e commit inicial preservados; `.env`, banco, venv e artefatos ignorados; nenhum commit/push |

O E2E verificou token incorreto/correto, seis sensores, frames WebSocket de eventos
efetivamente recebidos, três ocupantes sintéticos, indicação de presença, início,
pausa sem novos eventos, continuação, parada, paginação, histórico após recarga,
token ausente dos storages, reconexão após fechamento forçado do socket, viewport
390 × 844 sem overflow da página, headers e exclusão efetiva dos eventos.

Os testes backend cobrem os oito cenários com 0/2/20 ocupantes, limites e coerência,
determinismo, perda de pacotes sem encerrar o gerador, transições inválidas, autenticação,
origens, paginação, retenção, auditoria, reabertura SQLite, WebSocket autenticado,
oito conexões máximas, frames inválidos, desconexão virtual, falha de persistência
sem publicar sucesso falso e descarte de frames sem perda no banco.

Capturas desktop e mobile estão em `artifacts/dashboard-desktop.png` e
`artifacts/dashboard-mobile.png` (ignoradas pelo Git). Foram inspecionadas visualmente.
Os servidores nativos de teste e a stack `wifi-spatial-verification` foram encerrados.
O volume de verificação foi preservado; não foi usado `down --volumes`.

## Falhas encontradas e resolvidas

- Bootstrap sem locks e empacotamento com dois diretórios de topo: corrigidos.
- Concorrência nos controles/exclusão e leitura de pacotes perdidos: corrigidas.
- Comparação HMAC de token Unicode e limite de conexões durante handshake: corrigidos.
- Caminho Python com barras incompatíveis no runner Windows: corrigido com caminho
  absoluto entre aspas.
- Testes com seletores ambíguos de alert/conexão: corrigidos sem suprimir validações.
- `next start` com output standalone: standalone ficou específico do build Docker.
- Tabela mobile sem acesso ao scroll por teclado: adicionados foco, região e nome.
- Dependência transitiva `braces` vulnerável no preset de lint Next: removida a cadeia;
  lint usa ESLint 10, TypeScript ESLint e React Hooks compatíveis.
- Cache global npm inconsistente: instalação repetida com cache isolado em artifacts;
  cache global não foi apagado.
- Porta 3100 ocupada por servidor do portfolio: processo preservado; runner usa
  4310/4810, com startup explícito do CLI Next deste repositório.
- Arquivos Python transferidos com bit executável no contexto Docker: scripts passaram
  a ter shebangs, e Ruff passou também no Linux.
- pip-audit Windows bloqueado por DLL de tomli: executado em Linux sem modificar as
  políticas do Windows; os dois locks foram auditados com sucesso.

## Pendências e limites

1. Receber `docs/PROJECT_MASTER_PLAN.md` e reconciliar o escopo, decisões e critérios
   formais de Fases 0/1. Não existe aprovação implícita de fases ainda desconhecidas.
2. O TestClient atual avisa que httpx está depreciado em favor de httpx2. Os testes
   passam; migração da ferramenta de teste ficará para atualização específica.
3. Auditoria sem expurgo, histórico paginado por offset e sessão em memória são
   limites documentados do MVP local; não há autenticação multiusuário, TLS remoto,
   proteção de serviço público ou suporte a múltiplos workers.
4. Verificação de acessibilidade automatizada e visual foi feita em Chromium;
   validação manual com leitores de tela e outros navegadores permanece pendente.
5. Python 3.12, Node 24 no Windows e Node 22/Python 3.12 no Docker foram usados;
   Python 3.13 está permitido, mas não foi executado nesta sessão.
6. Sem sensoriamento físico, IA experimental, medições clínicas ou validação científica.
7. Alterações continuam locais e sem commits, conforme a orientação atual.

## Manutenção semanal: cobertura medida e gates — 29/10/2026

- Auditoria em Linux (Python 3.13.18, Node 22.23.4): lint, formatação, tipos, 46 testes
  web, 328 testes da API, 6 testes dos lançadores, contratos em sincronia, build e
  auditorias (`npm audit` 0; `pip-audit` runtime e lock 0) — tudo PASS. Os advisories do
  Next.js de 23/10 afetam `<=16.4.0`; `main` já está em 16.4.2 (PR #24).
- Cobertura da API: `pytest-cov` 7.1.0 e `coverage` 7.17.0 adicionados ao extra `dev` e
  ao lock de desenvolvimento (lock idêntico ao gerado por `lock_dependencies.py`; runtime
  inalterado). `linux_checks.py` e `check.ps1` exigem 90%; medido 94,73%.
- Cobertura web: `npm run test:web` usa a cobertura nativa do Node com limiar de 85% de
  linhas; medido 89,75% nos módulos carregados pelos testes unitários. Painéis React sem
  teste unitário não entram na medição (cobertos pelo E2E).
- Comandos: `npm ci`, `pip install -r apps/api/requirements.lock.txt`, `npm run lint`,
  `npm run format:check`, `npm run typecheck`, `npm run test:web`, `npm run build`,
  `npm audit`, `python scripts/verify/export_contract.py --check`,
  `python scripts/verify/linux_checks.py`.

Não verificado nesta sessão: E2E Playwright (navegadores não instalados no ambiente
Linux usado), Docker Compose (sem daemon) e `check.ps1` no Windows; o CI do GitHub é a
referência. Validar o gate de cobertura também no Windows no próximo uso local.
