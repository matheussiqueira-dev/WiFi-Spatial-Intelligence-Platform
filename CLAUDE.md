# Guia do projeto

## Atualização normativa v3.0

Leia docs/PROJECT_MASTER_PLAN.md v3 integralmente. Não usar docs/docs/ como fonte.
Padrão: synthetic-native, domínio puro Acquisition, adaptadores/portas e leitura
de histórico por caso de uso; contrato 2.0.0 aditivo, 1.0/1.1 legados preservados.
RuView somente laboratório legado opcional (SPATIAL_LEGACY_LAB_ENABLED=false por
padrão), importado sob demanda. Não é dependência obrigatória do produto novo.
Os detalhes antigos abaixo são históricos quando divergirem desta atualização.
Origem e limite de exposição prévia: docs/ORIGINALITY_REGISTER.md. Não alegar
clean-room estrita ou originalidade jurídica absoluta. Analytics/backup/retention
e evidências atuais estão nos relatórios e guias correspondentes.

Leia `AGENTS.md`, `docs/PROGRESS.md`, `docs/SECURITY_REVIEW.md` e, se existir,
`docs/PROJECT_MASTER_PLAN.md` integralmente antes de continuar. O documento mestre
consolidado será a referência principal quando fornecido. Não recrie esse documento
a partir de hipóteses sobre o histórico de conversas.

## Estado e limites

Diagnóstico de host autorizado em 15/10/2026: módulo separado `/api/v1/network`,
contratos em `network_contracts.py`, tabelas próprias e agente Windows opt-in.
Telemetria operacional `HOST_NETWORK_TELEMETRY / L2_LIVE_UNVALIDATED`; não conectar
às observações espaciais, não inferir CSI/pessoas/animais. Guia WIFI_DIAGNOSTICS.md.

Monorepo com backend FastAPI, banco SQLite/Alembic e frontend Next.js App Router.
O provedor padrão é `NativeProvider` (`synthetic-native`); `RuViewProvider` exige
opt-in de laboratório (configuração em `docs/RUVIEW_INTEGRATION.md`). Toda observação tem
`source_type=SIMULATED`, `evidence_level=L0_SYNTHETIC` e
`validation_status=IMPLEMENTED_SYNTHETIC`. Não há CSI, hardware, inferência de IA,
biometria ou validação clínica. Capacidades futuras devem permanecer PLANNED/BLOCKED.

Preserve a arquitetura e alterações locais. Não substitua arquivos funcionais para
reiniciar o projeto. Não faça commits, push, uso de serviços pagos ou expansão de IA
sem autorização. Não inclua segredos em código, logs ou relatórios.

## Comandos reais

Execute a partir da raiz no Windows com Python 3.12/3.13 e Node.js 22+ LTS:

```powershell
.\scripts\setup\bootstrap.ps1
.\scripts\dev\start.ps1
# Depois de parar os servidores, em outro momento:
npm.cmd exec --workspace apps/web -- playwright install chromium
.\scripts\verify\check.ps1
docker compose up --build --detach --wait
docker compose down
```

O bootstrap cria `.env` somente se ausente. Nunca imprima SPATIAL_TOKEN em saídas
compartilhadas. O usuário informa esse token no dashboard. Não use `NEXT_PUBLIC_`
para segredos nem salve o token em localStorage, sessionStorage ou URL.

Use `npm.cmd` em PowerShell. O runner E2E exige 4310/4810 livres e uma compilação feita
por `npm.cmd run build:e2e`; não confunda o endpoint embutido nesse build com o padrão
8000 do uso normal. `check.ps1` prepara o build apropriado automaticamente.
`check.ps1 -SkipE2E` executa as verificações sem iniciar o navegador.

## Contratos e qualidade

`apps/api/app/contracts.py` define o evento. Após alterá-lo, execute:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts/verify/export_contract.py
```

Atualize também o validador Zod em `apps/web/src/lib/contracts.ts` e os testes.
Mudanças de dependências são explícitas: preserve package-lock.json e locks Python.
`scripts/verify/lock_dependencies.py` gera locks da instalação existente; rode-o
somente após uma atualização intencional e valide novamente no Windows e no Docker.

Registre em `docs/PROGRESS.md` o que mudou, resultados, comandos executados, falhas,
limitações e pendências. Uma funcionalidade só está validada quando executada.
