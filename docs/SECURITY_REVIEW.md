# Revisão de segurança, privacidade e qualidade

## Adendo — 17/10/2026 (webhook, exclusão, SWF1)

- Webhook de alertas é a primeira saída HTTP iniciada pela API. Mitigações de SSRF:
  destino fixo em configuração do servidor (nunca pelo dashboard), apenas IP literal de
  loopback/rede privada (DNS recusado contra rebinding; link-local/metadados e 0.0.0.0
  recusados), sem credenciais na URL, sem redirect, sem proxy, timeout de 3 s. O status
  expõe só esquema/host/porta, pois o caminho pode conter o segredo do receptor.
  Assinatura HMAC-SHA256 com timestamp; segredo ≥ 32 caracteres, fora de logs.
- Exclusão do histórico de rede exige `confirm=ERASE`, autenticação e capacidade de
  rede; audita só a ação. Não há desfazer: orientar exportação prévia.
- SWF1 autentica cada quadro antes de interpretar campos, recusa replay/ordem e
  hardware não testado; fuzzing determinístico no CI. Não há listener exposto.

## Adendo — 16/10/2026

Perfil de capacidades aplicado no backend (403 após autenticação; WS 1008). Páginas
`/docs`/`/redoc`, que carregam scripts de CDN sem SRI, desligadas por padrão. Allowlist
de Host configurável sem `testserver` em produção. Host `ruview` aceito só com
`SPATIAL_CONTAINER_NETWORK=true`. Negativas `operation.denied` restritas a recusas
protetivas, reduzindo ruído na auditoria. Continua sem aprovação para exposição fora de
loopback.

## Adendo — 15/10/2026, 21:03 Fortaleza

Corrigidos: corpo HTTP parseado antes da autenticação sem limite (BodyLimit 64 KiB,
413, inclusive chunked); reconexões WS válidas esgotando o balde de falhas "auth"
(novo balde `stream`, falhas de token/timeout/frame binário continuam auditadas e
limitadas); assinante WS registrado antes da autenticação. Evidência em
tests/test_runtime_hardening.py e gate de 21:03 no VERIFICATION_REPORT. Continua
sem aprovação para exposição fora de loopback.

## Adendo incremental — 15/10/2026, evolução corporativa

Revisadas as alterações de transporte/contratos e launchers desta etapa. Não é
auditoria exaustiva do repositório ou upstream. Seis testes existentes confirmaram
que os launchers confiavam em X-Forwarded-For; o peer usado por LocalLimiter podia
ser trocado por header. Aplicado --no-proxy-headers em dev, Playwright e Docker;
os seis casos passaram e agora integram check.ps1/linux_checks. Mantém operação
loopback; trust em proxy futuro requer decisão específica, não flag silenciosa.

Handler 500 devolve JSON sanitizado/no-store e registra somente tipo de exceção,
sem URL/body/token/texto bruto. Teste injeta conteúdo privado e verifica resposta
e health posterior. Cliente centraliza HTTP/CSV e não mostra corpo de erro bruto.
WS continua autenticando no primeiro frame; 4002 substitui close 1008 iniciado
ilegalmente pelo browser. Sem credencial persistida ou dependência nova.

Auditorias npm e locks Python runtime/completo executadas: zero vulnerabilidades
conhecidas nesta consulta; não é prova de ausência de vulnerabilidades no produto.
Docker atual indisponível; configuração preparada/testada via Uvicorn Config local,
mas imagem atual não executada. Sem aprovação de exposição pública, RBAC ou TLS
remoto. Verificação completa e falhas: VERIFICATION_REPORT.md.

Pendências antigas sobre nonce/rate/negativas nas seções históricas abaixo foram
superadas pelos incrementos já descritos em ADR-005/006 e testes atuais; RBAC,
consentimento multiusuário e revisão para rede pública permanecem pendentes.

## Estado vigente v3.0 — 15/10/2026

O plano oficial agora é v3.0; seções antigas abaixo são históricas. Superfícies
adicionais revisadas: consultas analytics autenticadas/limitadas, CSV/JSON,
snapshots SQLite, migração aditiva, provedor nativo, flag de legado, CSP,
backup/restore e expurgo offline com arquivo verificado. Casos negativos de
auth/origem, contratos, retenção e restauração estão na suíte executada.
Token permanece em memória; laboratório legado off; nenhum sensoriamento real.
Não se declara auditoria exaustiva ou aprovação para exposição pública.
Pendências: rate limit HTTP geral, CSP com nonce em vez de inline, auditoria
completa de negativas auth, RBAC/consentimento para uso futuro multiusuário.
Resultados vigentes: VERIFICATION_REPORT.md e TECHNICAL_REPORT_V3.md.

## Revalidação local — 15/10/2026

Reexecutadas verificações Windows/Linux, integração com a imagem oficial simulada,
Docker Compose isolado e persistência após reinício real da API. A execução final
`check.ps1 -RuView` passou com 83 testes backend, sete testes web e dois E2E,
além de lint/tipos/build. npm audit e pip-audit dos dois locks sem vulnerabilidades
conhecidas nas consultas desta execução. Escopo e falhas intermediárias em
[VERIFICATION_REPORT.md](VERIFICATION_REPORT.md); fronteiras mapeadas em
[REQUIREMENTS_TRACEABILITY.md](REQUIREMENTS_TRACEABILITY.md).

Corrigida interpretação acessível de contagem RuView desconhecida e sincronização
do teardown no teste de limite de WebSockets, que agora também exige liberação e
reutilização dos slots. Não houve alteração dos controles de autenticação,
dependências ou locks. Limites do MVP local abaixo continuam aplicáveis.
O documento mestre v2.0 permanece ausente, impedindo auditoria formal dos seus
requisitos. Não se declara conformidade com a v2.0 ou conclusão da F3A.

## Adendo F2 — integração simulada, 14/10/2026

Escopo adicional inspecionado: app/ruview.py, configuração, novo contrato, pipeline,
inserção idempotente, seleção autenticada, validação Zod, dashboard, Compose e
launchers/testes. O relatório do MVP abaixo continua como registro histórico.
Não foi realizada auditoria integral dos milhares de arquivos do motor upstream.
Imagem oficial fixada por digest; apenas a fronteira efetivamente consumida foi
inspecionada/validada. Isso não constitui aprovação de exposição pública.

| Fronteira adicional | Controle / evidência |
| --- | --- |
| Destino e credenciais | URLs backend restritas a loopback/ruview, sem query/userinfo; nenhum URL arbitrário enviado pelo dashboard; proxy de ambiente e redirects REST/WS bloqueados; testes de URL/redirect/token incorreto |
| Serviço oficial | Bearer separado, token aleatório em arquivo ignorado; handshake upstream usa header, WS da plataforma mantém primeiro frame; ports loopback, non-root, read-only, cap-drop/no-new-privileges; apenas REST/WS publicados |
| Host upstream | Entrada explícita ruview no allowlist, mantendo validação; conexão entre containers executada, erro 421 corrigido |
| Proveniência e qualidade | Status ready/simulated/synthetic e source por frame; timestamps finitos/recentes, presença/contagem coerentes, origem real rejeitada; sem confiança, modelo ou posições de verdade fabricados |
| Recursos e falhas | 256 KiB/frame, fila WS quatro, timeouts, backoff até 10 s; rede fora do lock; testes de JSON inválido/oversize/origem/freeze/serviço ausente e recuperação; E2E pausa/despausa container oficial |
| Banco e streaming | Mesma tabela/migração, insert idempotente, persistência antes de WS; testes de replay/reabertura e payloads idênticos após reinício real da API com dados oficiais simulados |
| Frontend | Contratos 1.0/1.1, token só em memória, origem por linha, null para contagem desconhecida, sem pessoas fictícias no mapa RuView; axe desktop/mobile sem violações verificadas |

Verificação atual: **83 testes backend** passaram no Windows/Linux, **4 contratos
web**, **2 E2E** (MVP + motor oficial), lint/tipos/build passaram. npm audit e ambos
locks Python auditados sem vulnerabilidades conhecidas. Sem dependências novas.

Limites: dados upstream sintéticos não viram evidência real; não há replay de frames
perdidos, sensores físicos ou validação de modelos. Integridade/frescor do transporte
não mede qualidade científica/RF. A auditoria do motor completo e outras versões
não foi feita. Os riscos residuais do MVP local abaixo permanecem aplicáveis.
Operação/evidências: [RUVIEW_INTEGRATION.md](RUVIEW_INTEGRATION.md) e
[PROGRESS.md](PROGRESS.md).

Escopo: código próprio da API, contratos, simulador, pipeline, persistência, migrações,
frontend, controles, acesso REST/WebSocket, scripts, configuração e dependências do
MVP local. Revisão de 14/10/2026, com testes executados no Windows e Linux/Docker.

Não foi realizada avaliação de um serviço público ou validação de hardware. O código
atual não implementa coleta CSI, biometria, modelos ou sensoriamento real. A revisão
combina inspeção dos arquivos/caminhos de dados com testes, sem enviar código privado
ou credenciais a serviços de terceiros. As auditorias consultam nomes/versões de
dependências em bases públicas de vulnerabilidades.

## Controles inspecionados e verificados

| Fronteira | Controle e evidência |
| --- | --- |
| Segredos | Token aleatório de 256 bits no bootstrap; `.env` preservado e ignorado; sem token em variável NEXT_PUBLIC, URL, logs de aplicação ou arquivos de código |
| REST | Bearer obrigatório nos endpoints de dados e controles; comparação constante em bytes; testes de acesso sem token e origem não permitida |
| WebSocket | Origem local obrigatória, autenticação no primeiro frame em até 5 s, slots reservados antes do handshake, até 8 conexões; testes de token inválido/Unicode e frames malformados |
| Recursos | Ingestão com fila de 64, fila de 16 por assinante, envio com timeout; launchers limitam frames a 4096 bytes e a fila de entrada a 16 |
| Controle | Lock para transições e exclusão; pausa/parada drenam a fila; exclusão durante execução retorna 409; teste verifica que eventos deixam de crescer |
| Persistência | SQLite com SQLAlchemy parametrizado, migração Alembic, WAL e busy timeout; retenção dos eventos; testes de reabertura e reinício real do container |
| Falhas | Erro de gravação interrompe o provedor sem transmitir uma observação como persistida; teste de falha injetada |
| Proveniência | Campos SIMULATED/L0_SYNTHETIC fixos; coerência de posição/presença/ocupação; rejeita modelo/confiança/sinal fabricados; testes Python e Zod |
| Frontend | Token apenas em memória; React renderiza texto sem HTML bruto; respostas validadas com Zod; reconexão com espera progressiva e aviso de dados desatualizados |
| Dados | Nenhuma câmera, microfone, geolocalização, cadastro pessoal ou coleta de rede; simulação local explícita em interface e histórico |
| Containers | Usuários não root, no-new-privileges, portas loopback, healthchecks; `.env`, bancos, caches e artefatos excluídos do contexto |
| Scripts | Verificação de portas, prontidão e ownership dos processos; nenhuma limpeza de arquivos existentes ou encerramento de servidores de outros projetos |
| Headers | nosniff, DENY, no-referrer, Permissions-Policy para câmera/microfone/geolocalização; headers verificados no E2E |
| Qualidade | Ruff, ESLint, TypeScript, 48 testes backend, 3 testes web, build e E2E com API real; inspeção visual e axe em desktop/mobile |

Health e documentação OpenAPI são públicos neste ambiente local; não incluem tokens
ou dados persistidos. Os endpoints de governança mantêm capacidades reais como false
e registram provedores futuros como PLANNED/BLOCKED.

## Correções aplicadas

- A comparação HMAC deixou de falhar com tokens Unicode, usando bytes UTF-8.
- O teto de sockets passou a considerar conexões aguardando autenticação, evitando
  ultrapassar oito slots por handshakes concorrentes.
- Encerramento WebSocket acompanha imediatamente a desconexão do cliente e cancela
  leituras pendentes, liberando o slot e evitando tarefas órfãs.
- Exclusão, pausa e parada foram serializadas com a produção; eventos recebidos pelo
  frontend já passaram pela persistência.
- Falha no banco desconecta o simulador e não apresenta um evento como gravado.
- Configuração oculta valores de entrada em erros de validação e o token em repr.
- Retirada a cadeia de lint Next/fast-glob/micromatch/braces que apresentava alerta alto
  de esgotamento de pilha em padrões profundamente aninhados. Ferramentas de lint
  foram substituídas por ESLint 10/TypeScript ESLint/React Hooks e a auditoria ficou limpa.
- Corrigida a área de tabela mobile para foco e rolagem acessíveis pelo teclado.

## Auditorias de dependências

- `npm audit`: zero vulnerabilidades conhecidas, incluindo ferramentas de desenvolvimento.
- `pip-audit -r apps/api/requirements.runtime.txt`: zero vulnerabilidades conhecidas.
- `pip-audit -r apps/api/requirements.lock.txt`: zero vulnerabilidades conhecidas.

As auditorias Python foram executadas em um container Linux isolado criado por
`apps/api/Dockerfile.verify`. O launcher local pip-audit foi bloqueado pela política
do Windows ao carregar tomli; nenhum controle do SO foi desligado ou alterado.
Uma auditoria sem alertas não comprova ausência de vulnerabilidades desconhecidas.

## Itens residuais classificados

| Severidade | Classe | Limite ou recomendação |
| --- | --- | --- |
| MÉDIA se exposto remotamente | Configuração | Bearer compartilhado e HTTP são adequados ao escopo loopback; não há TLS, rate limit público, identidade multiusuário ou autorização por papel. Não publicar esta configuração como serviço remoto |
| BAIXA | Configuração | Eventos têm retenção por quantidade, mas a tabela de auditoria cresce com controles. Definir expurgo/backup antes de uso prolongado |
| BAIXA | Recomendação de atualização | TestClient/Starlette avisa depreciação de httpx; avaliar httpx2 numa atualização específica, preservando cobertura e locks |
| BAIXA | Qualidade | Sessão de simulação é local ao processo. Executar um worker; escalar exige separar estado e distribuição de eventos |
| BAIXA | Operação de testes | Traces de falha podem conter dados de autenticação da sessão de teste; são ignorados pelo Git e devem permanecer locais. E2E externo só pode apontar para stack de verificação isolada |

Não foram identificadas vulnerabilidades críticas ou altas exploráveis no escopo
local revisado após as correções. Os itens acima limitam a conclusão: este relatório
não autoriza exposição pública, não substitui pentest e não valida sensoriamento real.

## Reprodução Linux

```powershell
docker build -f apps/api/Dockerfile.verify -t wifi-spatial-backend-verification .
docker run --rm wifi-spatial-backend-verification
```

O container instala o lock completo e executa lint, formatação, pytest e as duas
auditorias. Para repetir a verificação do reinício, primeiro suba somente uma stack
isolada chamada `wifi-spatial-verification` com o Compose do repositório, então rode:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts/verify/compose_smoke.py
```

O script confirma o label do projeto Docker antes de reiniciar sua API. Ele adiciona
eventos sintéticos e verifica payloads idênticos no banco após o reinício; não apaga
o volume. Veja os limites completos e resultados em [PROGRESS.md](PROGRESS.md).
