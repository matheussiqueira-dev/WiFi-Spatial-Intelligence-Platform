# Reconciliação de F0/F1 — evidências e limite formal

Inspeção em 14/10/2026, America/Fortaleza, na branch `feat/platform-foundation`.
`docs/PROJECT_MASTER_PLAN.md` continua **ausente**. README, CLAUDE, AGENTS,
PROGRESS e SECURITY_REVIEW foram lidos integralmente; código e testes executados.

Não há documento para identificar números de requisitos, fronteiras oficiais ou
critérios de aprovação de F0/F1. Portanto, esta matriz registra o estado verificável
do escopo provisório descrito em PROGRESS, sem substituir o mestre, inventar suas
exigências ou conceder aprovação formal. Conformidade formal: **pendente do mestre**.

## Matriz de rastreabilidade técnica provisória

| Escopo provisório | Implementação existente preservada | Evidência executável nesta continuação | Situação |
| --- | --- | --- | --- |
| F0 — arquitetura e instalação | Workspaces npm, lockfile, venv Python, locks, FastAPI/SQLite/Next.js; scripts/setup, compose.yaml | Dependências existentes usadas sem alteração; builds Windows/Docker e verificações Ruff/ESLint/tipos passaram | Evidência técnica disponível; correspondência formal pendente |
| F0 — configuração e segurança local | Token em memória no frontend, Bearer REST, autenticação WS no primeiro frame, loopback, filas/limites, ignorados | Testes de auth/origin/limites e E2E de token inválido/válido e storage vazio; inspeção de configurações; auditorias sem alertas conhecidos | Evidência técnica disponível; sem autorização de exposição pública |
| F0 — armazenamento | Alembic 0001, SQLite WAL, retenção, auditoria | Testes de reabertura/retenção e reinício real da API em Compose com payloads idênticos | Evidência técnica disponível; migração inicial preservada |
| F1 — oito cenários | empty, stationary, walking, entering, leaving, interference, packet_loss, disconnect; SimulationProvider | Baseline antes da edição: 48 testes passaram; suíte final inclui os mesmos testes de 0/2/20 ocupantes, determinismo e desconexão | Preservado e retestado |
| F1 — contrato e proveniência | SensingEvent 1.0.0, JSON Schema, exemplo Python, Zod; SIMULATED/L0_SYNTHETIC | Testes Python/web e E2E; contrato interno preservado, evento RuView em versão separada 1.1.0 | Preservado; nenhuma simulação promovida a evidência real |
| F1 — controles e distribuição | Start/pause/resume/stop/reset, filas, gravação antes de transmissão | Testes de transições, parada/pausa sem novos registros, falha de armazenamento, descarte visual sem perda no banco, WebSocket real | Preservado e retestado |
| F1 — dashboard/histórico | Observatory SVG 8 × 6 m, seis sensores virtuais, métricas, paginação, exclusão com auditoria | E2E original passou; desktop/mobile sem overflow e zero violações axe verificadas | Preservado; leitores de tela/outros navegadores seguem pendentes |

## Decisões que ainda precisam ser confrontadas com o mestre

Laboratório único, limites de 20 ocupantes, seis sensores virtuais, seed/cadência,
SQLite com um worker, token de desenvolvimento compartilhado, SVG 2D, auditoria
sem expurgo, offset de paginação e ausência de sensoriamento real continuam decisões
documentadas do MVP. Sem o mestre, não é possível afirmar que satisfazem F0/F1 oficiais.

Quando o documento for fornecido: acrescentar seus identificadores e critérios à
matriz, classificar cada item como atendido/parcial/pendente com evidência, apontar
divergências e atualizar PROGRESS. Não criar retroativamente um mestre por inferência.

F2 foi implementada e validada pelo critério explícito da solicitação atual:
motor oficial simulado → streaming efetivo → normalização FastAPI → dashboard
→ histórico SQLite, origem sintética explícita e testes passando. A conformidade
da F2 com o mestre também só poderá ser reconciliada quando ele existir.
