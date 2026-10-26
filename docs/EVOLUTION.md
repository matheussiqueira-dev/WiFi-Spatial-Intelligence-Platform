# Plano de Evolução — wifi-spatial-intelligence-platform

> Documento vivo, revisado semanalmente. Última revisão: 2026-10-23.
> Regra central: nenhuma mudança entra sem estar ligada a um objetivo desta página e sem manter ou melhorar as métricas da seção 2.

## 1. Identidade do projeto

- **Propósito:** laboratório local de eventos espaciais sintéticos (`L0_SYNTHETIC`, seis nós virtuais, sala de 8 × 6 m) com observatório 2D/isométrico, streaming persistido, analytics e replay, laboratório de modelos, regras dry-run e um painel real de diagnóstico do enlace Wi-Fi do host; demonstra engenharia de eventos, contratos versionados e operação reproduzível sem serviços pagos.
- **Tipo:** monorepo com API (FastAPI + SQLite) e web app (Next.js), contratos JSON Schema compartilhados e stack Docker Compose local.
- **Stack:** API Python `>=3.12,<3.14` (CI 3.12 e 3.13) com FastAPI, Uvicorn, websockets, SQLAlchemy, Alembic, pydantic-settings, lock em `apps/api/requirements.lock.txt`; web Next.js `16.4.0` (Turbopack), React `19.3.0`, TypeScript `7.0.2`, Zod `^4.6.7`, ESLint `^10.12.0` + `typescript-eslint`, Prettier, Playwright `1.64.1` com `@axe-core/playwright`; testes web com `tsx --test`.
- **Gerenciador de pacotes:** npm workspaces (`package-lock.json` na raiz, workspace `apps/web`); pip com lock pinado para a API.
- **Deploy:** local por Docker Compose (`compose.yaml`, variantes `*.verify.yaml`) e scripts PowerShell em `scripts/`; sem deploy público (o próprio plano mestre declara que não é produto multiusuário pronto para exposição pública).
- **Estrutura:** `apps/api/` (app hexagonal: adapters SQLite, API, domínio; `migrations/` Alembic; `tests/`); `apps/web/` (`src/` Next.js App Router com `proxy.ts`, `tests/` unitários, `e2e/` Playwright); `packages/contracts/` (20 schemas e exemplos exportados da API); `scripts/` (verify, setup, dev, backup, network); `docs/` (plano mestre, decisões, protocolos, relatórios de verificação).
- **Comandos:** install `npm ci` + `python -m venv apps/api/.venv && apps/api/.venv/bin/pip install -r apps/api/requirements.lock.txt` · dev `npm run dev` (web) e Uvicorn via `scripts/dev` · lint `npm run lint` + `ruff check apps/api scripts/verify scripts/network` · typecheck `npm run typecheck` + `mypy --config-file apps/api/pyproject.toml apps/api/app` · test `npm run test:web` + `pytest apps/api/tests` + `pytest scripts/verify/tests` · build `npm run build`

## 2. Estado atual (baseline)

| Verificação | Comando | Resultado | Data |
| --- | --- | --- | --- |
| Instalação | `npm ci` · `pip install -r apps/api/requirements.lock.txt` (Python 3.13.16) | PASS · PASS | 2026-10-23 |
| Lint | `npm run lint` · `npm run format:check` · `ruff check` · `ruff format --check` | PASS em todos (118 arquivos Python formatados) | 2026-10-23 |
| Typecheck | `npm run typecheck` · `mypy --config-file apps/api/pyproject.toml apps/api/app` | PASS · PASS (0 issues em 63 arquivos) | 2026-10-23 |
| Testes | `npm run test:web` · `pytest apps/api/tests -q` · `pytest scripts/verify/tests -q` | 46/46 · 328/328 · 6/6; contratos em sincronia (`export_contract.py --check`, 20 arquivos) | 2026-10-23 |
| Cobertura | — | não verificado (sem `coverage`/`pytest-cov` no lock nem cobertura configurada no `tsx --test`) | 2026-10-23 |
| Build | `npm run build` | PASS na segunda execução; a primeira foi interrompida pelo próprio `next build` por versão do Next.js com vulnerabilidade conhecida | 2026-10-23 |
| Vulnerabilidades (audit) | `npm audit --json` · `pip_audit -r requirements.runtime.txt` · `pip_audit -r requirements.lock.txt` | npm: 1 critical (`next` 16.0.0–16.4.0: GHSA-2464-fhr4-w9xw, GHSA-p3m5-59mp-jv5r, GHSA-673q-mjm6-r5xr; correção em 16.4.3, sem major); Python runtime: 0; Python lock: 6 CVEs em `filelock` 4.1.1 (correção 4.2.1) | 2026-10-23 |
| CI no GitHub | `.github/workflows/ci.yml` | jobs `backend` (3.12/3.13), `web`, `e2e` (Chromium + WebKit, perfis `lab` e `commercial-br`), `security` (varredura de segredos no histórico e `npm audit --audit-level=moderate`); actions fixadas por SHA; último CI em `main` (`e9bdc2a`, 2026-10-22) com sucesso | 2026-10-23 |

Observações: o gate `scripts/verify/linux_checks.py` falha hoje no passo `pip_audit -r apps/api/requirements.lock.txt` (`filelock`), e o job `security` falharia no `npm audit --audit-level=moderate` com o advisory crítico do Next.js publicado depois do último CI verde. E2E Playwright não verificado localmente (exige download dos navegadores Chromium e WebKit e a API em execução; coberto pelo job `e2e` do CI). Docker Compose não verificado (sem daemon nesta revisão). Há 9 PRs de atualização de dependências abertos (#16–#24); os de `react`/`react-dom` 19.3.1 e do grupo de tooling web estão com CI vermelho, e o de `next` 16.4.2 está verde mas não alcança a versão corrigida 16.4.3.

## 3. Histórico e trajetória

30 commits entre 2026-10-14 e 2026-10-21, em ciclos curtos por PR.

- **2026-10-14 a 2026-10-15 — fundação:** plataforma synthetic-native com analytics, model lab, regras e diagnóstico Wi-Fi.
- **2026-10-16 — modularização e gates:** backend modularizado, CI gratuito, perfil de capacidades (`lab`/`commercial-br`), histórico de regras, mypy no gate, imagens por digest e E2E WebKit; correção de E2E com fila drenada antes de reportar pausa.
- **2026-10-17 — governança de rede:** alertas de rede, webhook local assinado, exclusão LGPD, protocolo SWF1, perfis de acesso locais com tokens por pessoa.
- **2026-10-21 — dependências e modelos:** lote de atualizações integrado em `chore/dependency-updates` (certifi para PYSEC-2026-4320, FastAPI, pydantic-settings, setuptools, actions), impressão RF sintética sobre SWF1 e registro de modelos com checksum.

Áreas de maior churn nos últimos 30 commits: `docs` (59 alterações de arquivo), `apps/api/app` (55), `apps/api/tests` (45), `scripts/verify` (33), `apps/web/src/components` (30). Padrão: features acompanhadas de testes e contratos; débito recorrente é o volume de documentação na raiz (plano mestre, roadmap, análise de referência, tarefas, prompts de sessão) e a fila de atualizações de dependência que se acumula entre ciclos.

## 4. Objetivos definidos (critério de parada)

| # | Eixo | Objetivo | Métrica | Baseline | Meta | Prioridade | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | Funcionamento | Gates locais e de CI verdes em `main` | passos falhando em `linux_checks.py` e no job `security` | 1 e 1 | 0 e 0 | P0 | ativo |
| O2 | Cobertura de testes | Medir e fixar gate de cobertura | % linhas `apps/api/app`; % linhas `apps/web/src` | não medida; não medida | API ≥ 85%; web ≥ 70% com gate no CI | P2 | ativo |
| O3 | Segurança | Zero vulnerabilidades conhecidas | critical/high npm; CVEs Python (runtime + lock) | 1 critical; 0 + 6 | 0; 0 + 0 | P0 | ativo |
| O4 | Performance | Medir latência do stream e FPS do observatório | p95 evento→render; FPS em cenário de 6 nós | não medido | linha de base registrada em `docs/VERIFICATION_REPORT.md`; p95 ≤ 250 ms | P3 | ativo |
| O5 | Qualidade/Manutenibilidade | Fila de atualizações de dependência sob controle | PRs de dependência abertos; PRs com CI vermelho | 9; 3 | ≤ 3; 0 | P1 | ativo |
| O6 | Dados/Observabilidade | Honestidade dos dados e rastreabilidade | eventos não `L0_SYNTHETIC` exibidos sem rótulo; contratos fora de sincronia | 0; 0 | manter 0; 0 | P1 | monitorado |

## 5. Guardrails

- Mudança só com objetivo associado (O#) ou item de backlog (B#); refatoração sem ganho mensurável é proibida.
- Nenhuma métrica da seção 2 pode piorar; se piorar, a mudança é revertida.
- Upgrade de versão major, mudança de arquitetura, remoção de funcionalidade e alteração de deploy exigem aprovação do dono (entram em "Decisões pendentes").
- No máximo uma feature nova por semana, de risco baixo, atrás de testes.
- Monólito modular hexagonal é decisão vigente: sem novos serviços, filas ou banco sem benchmark que justifique.
- Nenhuma afirmação de sensoriamento RF, pose, espécie, sinais vitais ou identificação: dados continuam `L0_SYNTHETIC` até haver hardware autorizado e protocolo de validação executado.
- Contratos em `packages/contracts/` só mudam por exportação da API (`export_contract.py`), de forma aditiva.
- Locks Python revalidados em Linux e no container antes do merge; actions do CI permanecem fixadas por SHA.
- O laboratório legado externo continua desligado por padrão.

## 6. Backlog priorizado

- P0 = quebra funcionamento/segurança · P1 = risco alto · P2 = qualidade · P3 = melhoria

- [ ] **B1 (P0, O3)** Atualizar `next` de `16.4.0` para `16.4.3` (patch, fecha GHSA-2464-fhr4-w9xw, GHSA-p3m5-59mp-jv5r e GHSA-673q-mjm6-r5xr) e fechar o PR #24, que para em 16.4.2 — `npm audit --audit-level=moderate` com exit 0; `npm run build` sem interrupção; E2E do CI verde.
- [ ] **B2 (P0, O1)** Atualizar `filelock` para `4.2.1` em `apps/api/requirements.lock.txt` — `python scripts/verify/linux_checks.py` com exit 0.
- [ ] **B3 (P1, O5)** Triar os PRs de dependência #16–#23: corrigir a causa das falhas de CI em `react`/`react-dom` 19.3.1 e no grupo de tooling web, ou fechá-los com motivo — no máximo 3 PRs de dependência abertos e nenhum com CI vermelho.
- [ ] **B4 (P1, O1)** Agendar execução semanal do CI em `main` (`schedule`) para que advisories novos quebrem o gate sem depender de push — workflow com gatilho `schedule` presente e executado.
- [ ] **B5 (P1, O3)** Avaliar a exposição real do advisory de Image Optimization: confirmar que `next.config.ts` não habilita SVG remoto e registrar a decisão em `docs/SECURITY_REVIEW.md` — seção com data, versão e conclusão.
- [ ] **B6 (P2, O2)** Cobertura da API com `pytest-cov` (lock de dev) e `--cov-fail-under` no `linux_checks.py` — relatório por módulo; meta de O2.
- [ ] **B7 (P2, O2)** Cobertura dos testes web (`--experimental-test-coverage` do runner do Node via `tsx`, ou `c8`) com limiar no job `web` — relatório gerado no CI; meta de O2.
- [ ] **B8 (P2, O5)** Planejar suporte a Python 3.14 (hoje `requires-python = ">=3.12,<3.14"`) com job experimental no CI — matriz 3.14 verde ou incompatibilidades listadas por dependência.
- [ ] **B9 (P2, O5)** Retirar do índice os arquivos de ambiente local versionados na raiz (configuração de IDE em `.idea/`, `dashboard.html` auxiliar local e os prompts de início de sessão duplicados em raiz e `docs/`) após decisão do dono — `git ls-files` sem esses arquivos; `.gitignore` atualizado.
- [ ] **B10 (P2, O6)** Consolidar a documentação da raiz (plano mestre, roadmap, análise de referência, tarefas) com índice único em `docs/` — README aponta para um único índice; nenhum link quebrado (verificação de links no CI).
- [ ] **B11 (P3, O4)** Benchmark de latência evento→render e FPS do observatório com o gerador virtual, registrado em `docs/VERIFICATION_REPORT.md` — comando reprodutível e números com ambiente anotado.
- [ ] **B12 (P3, O6)** Tour de onboarding e pacote de evidência da demo sem apagar histórico (item ativo em `TASKS.md`) — E2E cobre o tour do início ao fim.

## 7. Radar técnico

| Data | Item | Fonte | Veredito (adotar / avaliar / descartar) | Motivo |
| --- | --- | --- | --- | --- |
| 2026-10-23 | Advisory crítico Next.js 16.0.0–16.4.0 (Image Optimization com SVG) | https://github.com/advisories/GHSA-2464-fhr4-w9xw | adotar | Correção em 16.4.3 sem major (B1) |
| 2026-10-23 | Advisories Next.js Server Actions e `use cache` | https://github.com/advisories/GHSA-673q-mjm6-r5xr | adotar | Mesmo patch 16.4.3 (B1) |
| 2026-10-23 | Python 3.15 lançado; 3.14 bugfix; 3.12–3.13 só segurança | https://devguide.python.org/versions/ | avaliar | `requires-python` exclui 3.14 (B8) |
| 2026-10-23 | Playwright 1.64 (projeto `default`, `--shuffle`, `Locator.within()`) | https://playwright.dev/docs/release-notes | avaliar | Já em 1.64.1; `--shuffle` pode revelar dependência entre specs E2E |
| 2026-10-23 | Node.js 24 em LTS; 22 em LTS; 20 em EOL | https://nodejs.org/en/about/previous-releases | avaliar | CI usa Node 22; adicionar 24 antes da próxima atualização de Next |
| 2026-10-23 | Starlette com suporte a `httpx2` no test client | https://starlette.dev/release-notes/ | adotar | Já adotado no extra `dev` da API; manter alinhado nas atualizações |

## 8. Ideias de features

| # | Feature | Valor para o usuário/portfólio | Risco | Status (proposta / aprovada / implementada / descartada) |
| --- | --- | --- | --- | --- |
| F1 | Tour guiado da demo com pacote de evidência exportável | Recrutador ou CTO executa um fluxo verificável em minutos | baixo | proposta |
| F2 | Comparação lado a lado de dois cenários no replay | Mostra analytics e contratos com dado sintético rotulado | médio (limites de histórico) | proposta |
| F3 | Painel de saúde do pipeline (fila, eventos descartados, conexões WS) | Observabilidade operacional demonstrável | baixo | proposta |
| F4 | Exportação de relatório de diagnóstico Wi-Fi em PDF/CSV com metodologia | Uso cotidiano real do diagnóstico do enlace | baixo | proposta |

## 9. Decisões pendentes do dono

- Aprovar o patch do Next.js para 16.4.3 e fechar o PR #24?
- Política para a fila de PRs de dependência (agrupamento, limite, cadência de merge).
- Remover do Git os arquivos de ambiente local da raiz (configuração de IDE, quadro auxiliar e prompts de início de sessão)?
- Abrir suporte a Python 3.14 nesta janela ou aguardar compatibilidade das dependências?
- Metas de cobertura (API 85%, web 70%) aceitas como gate?

## 10. Registro semanal

| Data | Auditoria | Mudanças (commits) | Métricas | Próximo foco |
| --- | --- | --- | --- | --- |
| 2026-10-23 | Documento inicial e baseline | — | ver seção 2 | B1, B2, B3 |
