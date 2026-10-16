# WiFi Spatial Intelligence Platform

## Evolução e demonstração

**Uso cotidiano com seu computador e roteador:** painel de diagnóstico real do
enlace Wi-Fi, com sinal, canal, taxas negociadas, sondas locais opcionais,
histórico, comparação de pontos e CSV. Coletor Windows separado da stack Docker.
Início/parada e interpretação: [Guia de diagnóstico Wi-Fi](docs/WIFI_DIAGNOSTICS.md).
Essa telemetria de host não transforma o observatório sintético em sensoriamento RF.

O observatório oferece **estruturas articuladas** em perspectiva isométrica:
pessoas, cães, gatos ou elenco misto, volume luminoso, articulação opcional,
tela cheia e retorno à planta 2D. Em **Avatares da cena**, a seleção muda apenas
a ilustração dos ocupantes sintéticos; não reconhece espécies nem poses por RF.
O modo também acompanha o replay, sem inventar posições ausentes.
Pesquisa de sensoriamento/modelos reais e avaliação dos links fornecidos:
[Pessoas, animais e RF](docs/PEOPLE_ANIMALS_RF_RESEARCH.md).

Diagnóstico, decisões e roteiro comercial de demonstração:
[MASTER_EVOLUTION_PLAN.md](MASTER_EVOLUTION_PLAN.md).
Fases, skills e opções gratuitas: [ROADMAP_AND_SKILLS.md](ROADMAP_AND_SKILLS.md).
Análise funcional da referência: [RUVIEW_FEATURES_ANALYSIS.md](RUVIEW_FEATURES_ANALYSIS.md).
Pendências operacionais: [TASKS.md](TASKS.md). O quadro `dashboard.html` na raiz é
um auxiliar local do plugin productivity, separado da aplicação Next.js;
não é necessário para executar o produto e não foi iniciado nesta entrega.

O gate também valida contratos publicados e os launchers de Uvicorn.
Resultados atuais e limitações: [VERIFICATION_REPORT](docs/VERIFICATION_REPORT.md).

## Estado atual — plano v3.0

O modo padrão é **synthetic-native**, implementado no domínio próprio, sem
instalar/rodar RuView. Os oito cenários, seis nós virtuais, controles, API/WS e
histórico são preservados. Contrato novo 2.0.0 aditivo; payloads anteriores 1.0/1.1
continuam legíveis. O laboratório legado externo está desligado por padrão.

No dashboard, conecte com o token local e use **Análises e replay**: escolha
período/fonte/cenário, consulte as janelas de 1 min/5 min/hora/dia, reproduza o
histórico, salve snapshots no SQLite e exporte JSON/CSV da página. Datas no fuso do
navegador são convertidas a UTC. Contagens são médias por amostra e variações
líquidas, não identificação de pessoas ou cruzamentos individuais confirmados.

Limites: 31 dias, 10.000 eventos/consulta, 200 itens/página pela API (100 na UI),
100 relatórios salvos. Sem dado não significa sala vazia. Sem posições inferidas
para registros que não as oferecem. Sensor individual não é filtro disponível
nos eventos agregados dos seis nós virtuais; usar a fonte de observação registrada.

```powershell
.\scripts\verify\check.ps1
.\scripts\verify\docker-e2e.ps1
# Compatibilidade legada opt-in, opcional para o produto:
.\scripts\verify\check.ps1 -RuView -RuViewHttpPort 4970 -RuViewWsPort 4971
```

Guia de [analytics](docs/ANALYTICS_API.md), [backup/retenção](docs/DATA_RETENTION_AND_BACKUP.md),
[decisões](docs/DECISIONS.md), [origem/limites clean-room](docs/ORIGINALITY_REGISTER.md),
[laboratório de modelos](docs/MODEL_LAB.md), [regras dry-run](docs/AUTOMATION_DRY_RUN.md),
[protótipo de pacotes](docs/ACQUISITION_PACKET_LAB.md) e
[protocolo de validação RF](docs/RF_VALIDATION_PROTOCOL.md) — todos L0/sem hardware.

Perfil de capacidades: `SPATIAL_CAPABILITY_PROFILE=lab` (padrão) libera tudo o que está
implementado; `commercial-br` mantém só o grupo A (rede) e recusa com 403 presença,
analytics espaciais, laboratório de modelos, automações e o stream ao vivo. O dashboard
esconde esses módulos e mostra o motivo. Catálogo em `GET /api/v1/capabilities`.

Stream ao vivo (`/api/v1/stream`, WebSocket): origem permitida obrigatória; o cliente
envia `{"token": "..."}` como primeiro frame em até 5 s; o servidor responde envelopes
`{"type": "status"|"event", "data": ...}` (status também a cada 2 s sem eventos). Até
8 conexões; fechamentos 1008 (origem, token ou perfil) e 1013 (limite ou taxa).
Os parágrafos de integração a seguir também documentam a compatibilidade histórica;
para habilitá-la explicitamente, definir SPATIAL_LEGACY_LAB_ENABLED=true somente
no laboratório local. Compose normal não exige o serviço externo.

Laboratório local para explorar eventos espaciais **sintéticos**. O MVP usa FastAPI,
SQLite e Next.js, com atualização por WebSocket e um Spatial Observatory 2D de 8 × 6 m.

Todas as observações são `L0_SYNTHETIC`. Os seis sensores são virtuais; o sistema não
captura sinais Wi-Fi/CSI, não executa modelos de IA e não realiza medições clínicas.
Posições são a verdade gerada pelo simulador, sem confiança de inferência fabricada.

F2 adiciona o **RuView oficial em modo simulado** como fonte opcional. Presença e
contagem sobre sinais sintéticos ficam em `L0_SYNTHETIC`, com origem explícita e
histórico SQLite. Posições upstream não são tratadas como verdade do laboratório.
O simulador interno e os oito cenários continuam disponíveis.

```powershell
# Após bootstrap, com Docker Desktop Linux ativo:
.\scripts\dev\start-ruview.ps1
.\scripts\dev\start.ps1
# Dashboard: conectar → selecionar RuView simulado → Iniciar simulação
# Verificação completa com o serviço oficial (portas livres):
.\scripts\verify\check.ps1 -RuView
```

Veja [integração, configuração, contratos e troubleshooting do RuView](docs/RUVIEW_INTEGRATION.md).
Serviço gratuito, independente de hardware e fixado por digest. O launcher preserva
`.env` e gera `.env.ruview` apenas se ausente; ambos ficam fora do Git.

## Execução no Windows

Requisitos: Python 3.12 ou 3.13, Node.js 22+ LTS e npm. Execute na raiz do projeto:

```powershell
.\scripts\setup\bootstrap.ps1
.\scripts\dev\start.ps1
```

O bootstrap preserva `.env` existente; na primeira execução gera um token aleatório
de 256 bits, cria o ambiente Python, instala os locks e exporta o contrato de eventos.
Abra `http://127.0.0.1:3000/dashboard`. Informe o valor de `SPATIAL_TOKEN` do arquivo
`.env` na tela de conexão. O token permanece apenas na memória da página: atualizar
a página exige entrar novamente. Nunca publique ou compartilhe esse arquivo.

API: health em `http://127.0.0.1:8000/api/v1/health`; esquema em `/openapi.json`. As páginas
`/docs` e `/redoc` carregam scripts de CDN e só existem com `SPATIAL_API_DOCS_ENABLED=true`. O script aguarda a API
ficar pronta e encerra somente o processo de backend que criou quando o frontend sai.
As portas devem estar livres. Para usar outras portas:

```powershell
.\scripts\dev\start.ps1 -ApiPort 8200 -WebPort 3200
```

Os logs de inicialização ficam em `artifacts/api.stdout.log` e `api.stderr.log`.
Um `.env` preexistente com token vazio ou com menos de 32 caracteres deve ser corrigido
pelo operador; o bootstrap não substitui segredos existentes.

## Docker Compose

Se o CLI informar que `dockerDesktopLinuxEngine` não existe, confira
`docker desktop status`. Aguarde a inicialização do Docker Desktop; se estiver
parado, use `docker desktop start --timeout 60`. Confirme com
`docker version` que há uma seção Server antes de rodar Compose. Neste ambiente,
o contexto é `desktop-linux`, com WSL 2. Não é necessário reinstalar o aplicativo,
recriar volumes ou redefinir o Docker para resolver uma inicialização pendente.

Requer Docker Desktop com containers Linux. Prepare `.env` com o bootstrap ou crie
um token aleatório de pelo menos 32 caracteres usando um gerenciador de segredos.

```powershell
docker compose config --quiet
docker compose up --build --detach --wait
docker compose ps
docker compose down
```

Dashboard e API usam as mesmas URLs acima. As portas publicadas ficam em `127.0.0.1`.
Ambos os containers executam com usuários sem privilégios. O volume `spatial-data`
preserva SQLite entre reinícios e `down`; evite `down --volumes` se precisar do histórico.
Não execute os servidores nativos e o Compose nas mesmas portas ao mesmo tempo.

`NEXT_PUBLIC_API_URL` é um **endereço público**, nunca um token. No build do frontend,
seu padrão é `http://127.0.0.1:8000`; mudar esse endereço exige reconstruir a aplicação.
Na execução nativa, o script configura automaticamente o endereço e as origens locais.
O Compose deste MVP foi configurado para uso local, sem exposição na rede.

## Simulação e histórico

- Cenários: sala vazia, presença estacionária, movimento, entrada, saída, perturbação
  sintética, perda de pacotes e desconexão virtual.
- Configure 0–20 ocupantes, semente de 0 a 4.294.967.295 e velocidade de 0,25× a 4×.
- Iniciar cria uma sessão; pausar drena a fila, continuar retoma, parar desconecta o
  provedor virtual. Não há novos eventos após uma pausa/parada concluída.
- A desconexão simulada produz cinco observações e encerra a sessão com aviso explícito.
- A perturbação modifica posições sintéticas; não simula fisicamente interferência CSI.
- Uma mesma semente e cenário reproduzem as medições e os ticks. UUID e horário de
  execução variam entre sessões; o stream produz nominalmente 2 eventos/s em 1×.
- WebSocket transmite eventos **depois** de persistidos. O frontend reconecta com espera
  progressiva e sincroniza estado e histórico via REST a cada dois segundos.
- A latência exibida mede a espera na fila antes da gravação; não é latência de sensor.
- Histórico ordenado do mais novo para o mais antigo, 20 itens por página na interface;
  prefira pausar/parar ao navegar para manter as páginas estáveis.
- Retenção: últimos 10.000 eventos por padrão, configurável em
  `SPATIAL_RETENTION_EVENTS` (100–100.000). A exclusão exige simulação parada e conserva
  a auditoria dos controles. A auditoria não tem expurgo automático neste MVP.
- Após reiniciar o backend, a simulação fica parada e o histórico continua disponível;
  a última observação da sessão não é restaurada como uma medição ao vivo.

## Verificação

```powershell
npm.cmd exec --workspace apps/web -- playwright install chromium
.\scripts\verify\check.ps1
```

O runner usa uma API nova em 4810, build de produção em 4310 e um SQLite temporário
exclusivo. Ele recusa reutilizar servidores existentes. Não toca no histórico de uso.
O build para E2E aponta para 4810; para execução de produção manual, reconstrua com
`npm.cmd run build` para restaurar o endereço padrão ou defina `NEXT_PUBLIC_API_URL`.

Comandos individuais:

```powershell
.\apps\api\.venv\Scripts\python.exe -m pytest apps/api/tests -q
.\apps\api\.venv\Scripts\python.exe -m ruff check apps/api scripts/verify
.\apps\api\.venv\Scripts\python.exe -m ruff format --check apps/api scripts/verify
npm.cmd run lint
npm.cmd run format:check
npm.cmd run typecheck
npm.cmd run test:web
npm.cmd run build:e2e
npm.cmd run test:e2e
npm.cmd audit
.\apps\api\.venv\Scripts\python.exe -m pip_audit -r apps/api/requirements.runtime.txt
```

O teste E2E apaga eventos **apenas na sua base temporária**. Para rodar os mesmos
specs contra containers, use somente `.\scripts\verify\docker-e2e.ps1`: ele cria um
projeto Compose descartável `wifi-spatial-native-e2e-<data>` (API 4900, web 4400),
define `E2E_EXTERNAL`, `E2E_COMPOSE_PROJECT`, `E2E_TOKEN`, `E2E_API_PORT` e
`E2E_WEB_PORT` e remove ao final apenas o volume desse projeto. Os specs recusam o
modo externo sem essas variáveis explícitas, recusam a porta 8000 e conferem no Docker
que a porta pertence ao projeto isolado antes de apagar qualquer dado.

CI gratuito em `.github/workflows/ci.yml` (runners Linux): backend 3.12/3.13 com
`linux_checks.py`, web, E2E Chromium, Gitleaks e npm audit. `.pre-commit-config.yaml`
é opcional (`pip install pre-commit`) e não substitui `check.ps1`.

## Organização

```text
apps/api/app/          contratos Pydantic, pipeline, analytics e serviços
apps/api/app/main.py  composição: lifespan, middlewares e inclusão dos routers
apps/api/app/bootstrap.py       Container com adaptadores e serviços por instância
apps/api/app/api/              routers por contexto (simulação, analytics, model lab,
                               automação, catálogo/governança, stream WebSocket)
apps/api/app/domain/           domínio puro (cena sintética, janelas, regras, pacotes)
apps/api/app/adapters/sqlite/  repositórios por contexto; app/storage.py é a fachada
apps/api/migrations/  migrações Alembic
apps/api/tests/       contratos, cenários, API, WebSocket e banco
apps/web/src/         App Router, dashboard, observatório, validação dos dados
apps/web/tests/       testes do contrato exportado pelo Python
apps/web/e2e/         integração em navegador real
packages/contracts/  JSON Schema e exemplo sintético gerados
scripts/setup/       preparação Windows
scripts/dev/         execução Windows
scripts/verify/      locks, contrato e verificações
docs/                 progresso, decisões e revisão
```

Zod valida as respostas REST e WebSocket no navegador. Os contratos Python geram o
JSON Schema e um exemplo usado nos testes de compatibilidade. Não há serviços pagos,
mapas remotos, fontes remotas ou dependências de sensores físicos neste MVP.

O [registro de progresso](docs/PROGRESS.md) separa implementações e validações.
Veja também a [revisão de segurança e privacidade](docs/SECURITY_REVIEW.md).
O documento mestre oficial é `docs/PROJECT_MASTER_PLAN.md`, versão 3.0.
A duplicação antiga em docs/docs não é referência normativa.
