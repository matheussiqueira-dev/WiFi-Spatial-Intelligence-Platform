# Plano de Evolução — wifi-spatial-intelligence-platform

> Documento vivo, revisado semanalmente. Última revisão: 2026-11-05.
> Regra central: nenhuma mudança entra sem estar ligada a um objetivo desta página e sem manter ou melhorar as métricas da seção 2.

## 1. Identidade do projeto

- **Propósito:** laboratório local de eventos espaciais sintéticos (`L0_SYNTHETIC`, seis nós virtuais, sala de 8 × 6 m) com observatório 2D/isométrico, streaming persistido, analytics e replay, laboratório de modelos, regras dry-run e um painel real de diagnóstico do enlace Wi-Fi do host; demonstra engenharia de eventos, contratos versionados e operação reproduzível sem serviços pagos.
- **Tipo:** monorepo com API (FastAPI + SQLite) e web app (Next.js), contratos JSON Schema compartilhados e stack Docker Compose local.
- **Stack:** API Python `>=3.12,<3.14` (CI 3.12 e 3.13) com FastAPI, Uvicorn, websockets, SQLAlchemy, Alembic, pydantic-settings, lock em `apps/api/requirements.lock.txt` (dev com `pytest-cov`); web Next.js `16.4.5` (Turbopack), React `19.3.1`, TypeScript `7.0.2`, Zod `^4.6.7`, ESLint `^10.13.0` + `typescript-eslint`, Prettier, Playwright `1.64.1` com `@axe-core/playwright`; testes web com `tsx --test` e cobertura nativa do Node (`--experimental-test-coverage`, limiar de linhas).
- **Gerenciador de pacotes:** npm workspaces (`package-lock.json` na raiz, workspace `apps/web`); pip com lock pinado para a API.
- **Deploy:** local por Docker Compose (`compose.yaml`, variantes `*.verify.yaml`) e scripts PowerShell em `scripts/`; sem deploy público (o próprio plano mestre declara que não é produto multiusuário pronto para exposição pública).
- **Estrutura:** `apps/api/` (app hexagonal: adapters SQLite, API, domínio; `migrations/` Alembic; `tests/`); `apps/web/` (`src/` Next.js App Router com `proxy.ts`, `tests/` unitários, `e2e/` Playwright); `packages/contracts/` (20 schemas e exemplos exportados da API); `scripts/` (verify, setup, dev, backup, network); `docs/` (plano mestre, decisões, protocolos, relatórios de verificação).
- **Comandos:** install `npm ci` + `python -m venv apps/api/.venv && apps/api/.venv/bin/pip install -r apps/api/requirements.lock.txt` · dev `npm run dev` (web) e Uvicorn via `scripts/dev` · lint `npm run lint` + `ruff check apps/api scripts/verify scripts/network` · typecheck `npm run typecheck` + `mypy --config-file apps/api/pyproject.toml apps/api/app` · test `npm run test:web` + `pytest apps/api/tests` + `pytest scripts/verify/tests` · build `npm run build`

## 2. Estado atual (baseline)

| Verificação | Comando | Resultado | Data |
| --- | --- | --- | --- |
| Instalação | `npm ci` · `pip install -r apps/api/requirements.lock.txt` (Python 3.13.18, Node 22.23.4) | PASS · PASS (`pip check` sem conflitos) | 2026-11-05 |
| Lint | `npm run lint` · `npm run format:check` · `ruff check` · `ruff format --check` | PASS em todos | 2026-11-05 |
| Typecheck | `npm run typecheck` · `mypy --config-file apps/api/pyproject.toml apps/api/app` | PASS · PASS | 2026-11-05 |
| Testes | `npm run test:web` · `pytest apps/api/tests -q` · `pytest scripts/verify/tests -q` | 46/46 · 328/328 · 6/6; contratos em sincronia (`export_contract.py --check`) | 2026-11-05 |
| Cobertura | `pytest --cov=apps/api/app` (via `linux_checks.py`) · `npm run test:web` | API 94,73% linhas (gate 90%; uma execução antes das mudanças deu 94,70%, variação entre execuções sem mudança de código); web 89,75% (gate 85%; módulos carregados pelos testes) | 2026-11-05 |
| Build | `npm run build` | PASS (Next.js 16.4.5, 3 rotas) | 2026-11-05 |
| Vulnerabilidades (audit) | `npm audit` · `pip_audit -r requirements.runtime.txt` · `pip_audit -r requirements.lock.txt` | npm 0 critical / 0 high / 10 moderate (um advisory novo do `minimatch` em desenvolvimento, ver observações; antes 0); Python runtime 0; Python lock 0 | 2026-11-05 |
| CI no GitHub | `.github/workflows/ci.yml` | run em `d3d9684`: Backend 3.12/3.13, Web e E2E (Chromium + WebKit, dois perfis) verdes; job Security vermelho só em `npm audit --audit-level=moderate` (B14) | 2026-11-05 |

Observações (2026-11-05): os 10 moderate são um único advisory, GHSA-g3hv-75wg-m249 (`minimatch` < 11.0.1), pela cadeia de `eslint` e `typescript-eslint`, só em desenvolvimento; 10.2.6 é a última da linha 10 e a correção exige major. Uma tentativa local com `overrides` para minimatch 11 não resolveu a árvore (`typescript-eslint` 8.72.1 e TypeScript 7 entram em conflito ao recriar o lock) e foi descartada; nada disso foi commitado. E2E local e Docker Compose continuam não verificados aqui; o E2E verde vem do CI. Windows não verificado.

Observações (2026-10-29): os advisories do Next.js listados em 2026-10-23 afetam `>=16.0.0 <=16.4.0` segundo a base de advisories do npm; a versão 16.4.2 em `main` (PR #24) já está fora da faixa e `npm audit` retorna 0. `filelock` 4.2.1 entrou pelo PR #25. Os PRs de dependência #16–#26 foram mesclados pelo dono em 2026-10-26; não há PR aberto. E2E Playwright e Docker Compose não verificados localmente (navegadores do Playwright e daemon Docker indisponíveis neste ambiente; cobertos pelo job `e2e` do CI). Histórico: em 2026-10-23 o gate `linux_checks.py` falhava no `pip_audit` do lock e o job `security` falharia no `npm audit`.

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
| O1 | Funcionamento | Gates locais e de CI verdes em `main` | passos falhando em `linux_checks.py` e no job `security` | 1 e 1 (2026-11-05: 0 e 1) | 0 e 0 | P0 | ativo (regrediu por advisory novo; B14 depende do dono) |
| O2 | Cobertura de testes | Medir e fixar gate de cobertura | % linhas `apps/api/app`; % linhas `apps/web/src` | não medida; não medida | API ≥ 85%; web ≥ 70% com gate no CI | P2 | monitorado (2026-10-29: API 94,73% com gate 90%; web 89,75% com gate 85%) |
| O3 | Segurança | Zero vulnerabilidades conhecidas | critical/high npm; CVEs Python (runtime + lock) | 1 critical; 0 + 6 (2026-11-05: 0; 0 + 0) | 0; 0 + 0 | P0 | monitorado (0 critical/high; moderate de desenvolvimento em B14) |
| O4 | Performance | Medir latência do stream e FPS do observatório | p95 evento→render; FPS em cenário de 6 nós | não medido | linha de base registrada em `docs/VERIFICATION_REPORT.md`; p95 ≤ 250 ms | P3 | ativo |
| O5 | Qualidade/Manutenibilidade | Fila de atualizações de dependência sob controle | PRs de dependência abertos; PRs com CI vermelho | 9; 3 (2026-11-05: 4 abertos; 1 vermelho) | ≤ 3; 0 | P1 | ativo (regrediu em 2026-11-05: 8 PRs abertos; reduzidos para 4 nesta revisão) |
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

- [x] **B1 (P0, O3)** _(2026-10-26, PR #24 do dono: `next` 16.4.2 já fora da faixa afetada `<=16.4.0`; `npm audit` 0 em 2026-10-29)_ Atualizar `next` de `16.4.0` para `16.4.3` (patch, fecha GHSA-2464-fhr4-w9xw, GHSA-p3m5-59mp-jv5r e GHSA-673q-mjm6-r5xr) e fechar o PR #24, que para em 16.4.2 — `npm audit --audit-level=moderate` com exit 0; `npm run build` sem interrupção; E2E do CI verde.
- [x] **B2 (P0, O1)** _(2026-10-26, `f30cc10`, PR #25 do dono)_ Atualizar `filelock` para `4.2.1` em `apps/api/requirements.lock.txt` — `python scripts/verify/linux_checks.py` com exit 0.
- [x] **B3 (P1, O5)** _(2026-10-26, PRs #16–#26 mesclados pelo dono; nenhum PR aberto)_ Triar os PRs de dependência #16–#23: corrigir a causa das falhas de CI em `react`/`react-dom` 19.3.1 e no grupo de tooling web, ou fechá-los com motivo — no máximo 3 PRs de dependência abertos e nenhum com CI vermelho.
- [ ] **B4 (P1, O1; objetivo monitorado — depende de decisão do dono)** Agendar execução semanal do CI em `main` (`schedule`) para que advisories novos quebrem o gate sem depender de push — workflow com gatilho `schedule` presente e executado.
- [ ] **B5 (P1, O3; objetivo monitorado — com 16.4.2 a versão afetada saiu de `main`; resta só o registro histórico)** Avaliar a exposição real do advisory de Image Optimization: confirmar que `next.config.ts` não habilita SVG remoto e registrar a decisão em `docs/SECURITY_REVIEW.md` — seção com data, versão e conclusão.
- [x] **B6 (P2, O2)** _(2026-10-29, `5e39f4f`: `pytest-cov` 7.1.0 + `coverage` 7.17.0 no lock de dev; `--cov-fail-under=90` em `linux_checks.py` e `check.ps1`; 94,73%)_ Cobertura da API com `pytest-cov` (lock de dev) e `--cov-fail-under` no `linux_checks.py` — relatório por módulo; meta de O2.
- [x] **B7 (P2, O2)** _(2026-10-29, `1138741`: `npm run test:web` mede cobertura nativa do Node com `--test-coverage-lines=85`, inclusive no job `web` do CI; 89,75%)_ Cobertura dos testes web (`--experimental-test-coverage` do runner do Node via `tsx`, ou `c8`) com limiar no job `web` — relatório gerado no CI; meta de O2.
- [ ] **B8 (P2, O5)** Planejar suporte a Python 3.14 (hoje `requires-python = ">=3.12,<3.14"`) com job experimental no CI — matriz 3.14 verde ou incompatibilidades listadas por dependência.
- [ ] **B9 (P2, O5)** Retirar do índice os arquivos de ambiente local versionados na raiz (configuração de IDE em `.idea/`, `dashboard.html` auxiliar local e os prompts de início de sessão duplicados em raiz e `docs/`) após decisão do dono — `git ls-files` sem esses arquivos; `.gitignore` atualizado.
- [ ] **B10 (P2, O6)** Consolidar a documentação da raiz (plano mestre, roadmap, análise de referência, tarefas) com índice único em `docs/` — README aponta para um único índice; nenhum link quebrado (verificação de links no CI).
- [ ] **B11 (P3, O4)** Benchmark de latência evento→render e FPS do observatório com o gerador virtual, registrado em `docs/VERIFICATION_REPORT.md` — comando reprodutível e números com ambiente anotado.
- [ ] **B13 (P2, O2)** Levar os painéis React hoje fora da medição (`network-panel`, `analytics-panel` e demais) para a cobertura unitária, ou medir todos os arquivos de `src/` quando o runner do Node incluir arquivos não carregados — relatório lista todos os arquivos de `src/` e o gate de 85% se mantém.
- [ ] **B14 (P1, O1)** Job `security` falha em `npm audit --audit-level=moderate` por GHSA-g3hv-75wg-m249 (`minimatch` em desenvolvimento), sem correção sem major — job verde sem afrouxar o critério, por versão do ESLint/`typescript-eslint` com `minimatch` ≥ 11.0.1 ou por decisão do dono (seção 9).
- [ ] **B15 (P2, O5)** Tratar os PRs restantes: #33 `sqlalchemy` (E2E WebKit vermelho, investigar se é instável), #30 `fastapi` 0.162 (várias versões com "Breaking Changes"), #28 `typescript-eslint` 8.72.1 (peer de TypeScript exclui 7.0.2) e #34 `filelock` — no máximo 3 abertos e nenhum vermelho.
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
| 2026-10-29 | Faixa dos advisories Next.js GHSA-2464-fhr4-w9xw, GHSA-p3m5-59mp-jv5r e GHSA-673q-mjm6-r5xr: `>=16.0.0 <=16.4.0` | https://github.com/advisories/GHSA-2464-fhr4-w9xw | monitorar | `main` em 16.4.2 já corrigido; 16.4.3 é a `latest` (patch sem advisory novo associado); seguir pelo fluxo do Dependabot |
| 2026-10-29 | Release de segurança do Next.js de outubro (16.4.1 como versão corrigida) | https://docs.pantheon.io/release-notes/2026/10/nextjs-security-release | adotar | Confirma que a linha 16.4.x após 16.4.0 contém as correções (O3) |
| 2026-10-29 | Node.js October 2026 security releases (22.x, 24.x, 26.x) | https://nodejs.org/en/blog/vulnerability/october-2026-security-releases?assessment=20261021 | adotar | Local em 22.23.4; o CI usa `node-version: 22`, que resolve a última patch |
| 2026-10-29 | Cobertura nativa do test runner do Node (`--experimental-test-coverage`, `--test-coverage-lines`, desde 22.8) | https://nodejs.org/api/test.html | adotar | Cumpre B7 sem dependência nova; mede só módulos carregados (B13) |
| 2026-10-29 | `pytest-cov` 7.1.0 / `coverage` 7.17.0 | https://pytest-cov.readthedocs.io/en/latest/changelog.html | adotar | Cumpre B6; dependência só de desenvolvimento, `pip-audit` limpo |
| 2026-11-05 | Next.js 16.4.5, release de segurança de 03/11: 7 advisories moderate (GHSA-vc7v-qv4w-wrv8, GHSA-7qx7-33qx-rqx2, GHSA-vvgp-ww4w-46vf, GHSA-mfr8-8qww-v76h, GHSA-f3mh-rxg3-f5g2, GHSA-rhh4-g77r-r9qj, GHSA-pc58-hwjq-p385) | https://nextjs.org/blog/upcoming-nextjs-security-release-november-2026 · https://www.netlify.com/changelog/2026-11-03-nextjs-security-vulnerabilities/ | adotado | Patch na mesma major; `npm audit` ainda não os listava (`07515c6`) |
| 2026-11-05 | GHSA-g3hv-75wg-m249, `minimatch` >=7 <11.0.1 | `npm audit` · https://github.com/advisories/GHSA-g3hv-75wg-m249 | monitorar | Quebra o job `security`; só em desenvolvimento (B14) |
| 2026-11-05 | `typescript-eslint` 8.72.1 com peer `typescript <6.1.0` | `npm install` local · PR #28 | avaliar | Projeto está em TypeScript 7.0.2; não sobe sem resolver o peer (B15) |
| 2026-11-05 | FastAPI 0.162.0 / Starlette 1.10.0, SQLAlchemy 2.1.8, filelock 4.2.9 | https://fastapi.tiangolo.com/release-notes/ · https://pypi.org/project/sqlalchemy/ | avaliar | Sem advisory em `pip_audit`; seguem pelo fluxo dos PRs (B15) |

## 8. Ideias de features

| # | Feature | Valor para o usuário/portfólio | Risco | Status (proposta / aprovada / implementada / descartada) |
| --- | --- | --- | --- | --- |
| F1 | Tour guiado da demo com pacote de evidência exportável | Recrutador ou CTO executa um fluxo verificável em minutos | baixo | proposta |
| F2 | Comparação lado a lado de dois cenários no replay | Mostra analytics e contratos com dado sintético rotulado | médio (limites de histórico) | proposta |
| F3 | Painel de saúde do pipeline (fila, eventos descartados, conexões WS) | Observabilidade operacional demonstrável | baixo | implementada (preexistente: fila, descartes, espera e reconexões já aparecem no painel principal; registrado em 2026-10-29) |
| F4 | Exportação de relatório de diagnóstico Wi-Fi em PDF/CSV com metodologia | Uso cotidiano real do diagnóstico do enlace | baixo | implementada em CSV (preexistente: "Exportar medições CSV"); PDF segue proposta |

## 9. Decisões pendentes do dono

- ~~Aprovar o patch do Next.js para 16.4.3 e fechar o PR #24?~~ Resolvido: PR #24 (16.4.2) mesclado e fora da faixa afetada.
- Política para a fila de PRs de dependência (agrupamento, limite, cadência de merge).
- Remover do Git os arquivos de ambiente local da raiz (configuração de IDE, quadro auxiliar e prompts de início de sessão)?
- Abrir suporte a Python 3.14 nesta janela ou aguardar compatibilidade das dependências?
- Metas de cobertura (API 85%, web 70%) aceitas como gate? Em 2026-10-29 os gates entraram em 90% (API) e 85% (web, módulos carregados); confirmar ou ajustar.
- Agendar CI semanal em `main` (B4)? O advisory de 05/11 só apareceu no push; com agendamento teria quebrado o job `security` antes.
- B14: o job `security` está vermelho por `minimatch` em desenvolvimento. Opções: (a) aceitar o vermelho até `eslint` e `typescript-eslint` subirem a dependência; (b) separar produção (`npm audit --omit=dev --audit-level=moderate`, bloqueante) de desenvolvimento (só relatório); (c) lista de exceção revisada por semana. Nenhuma foi aplicada porque afrouxa o gate. Recomendação: (b).
- Merge de PRs de dependência verdes fica com o dono; nesta revisão as mudanças equivalentes de #27, #29, #31, #32 entraram direto na `main`.
- Aprovar uma feature para o próximo ciclo (F1 tour guiado ou F2 comparação no replay); F3 e F4 (CSV) já existiam.

## 10. Registro semanal

| Data | Auditoria | Mudanças (commits) | Métricas | Próximo foco |
| --- | --- | --- | --- | --- |
| 2026-10-23 | Documento inicial e baseline | — | ver seção 2 | B1, B2, B3 |
| 2026-10-29 | Auditoria completa (install, lint, format, typecheck, testes, contratos, build, `npm audit`, `pip-audit` dos dois locks); B1–B3 já resolvidos pelo dono; O1, O3 e O5 monitorados; CI de `main` verde | `5e39f4f` B6, `1138741` B7; nenhuma feature nova (nenhuma aprovada; F3 e F4 já existiam) | npm 1 critical → 0; lock Python 6 → 0; cobertura API não medida → 94,73%; web não medida → 89,75%; testes 46/328/6 → 46/328/6 | B13, B4 (com aprovação), B11 |
| 2026-11-05 | Auditoria completa; Next.js com 7 advisories moderate; 8 PRs de dependência abertos; advisory novo do `minimatch` quebra o job `security` | `07515c6` Next 16.4.5, `6a78254` filelock/ast-serialize/ruff, `d3d9684` setup-python 7.1.0; nenhuma feature (nenhuma aprovada) | testes 46/328/6 → 46/328/6; cobertura API 94,73%, web 89,75%; npm 0 → 10 moderate (dev); Python 0; PRs abertos 8 → 4 | B14 (decisão do dono), B15, B11 |
