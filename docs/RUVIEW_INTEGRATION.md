# Integração RuView — F2 simulada

## Estado vigente v3.0 — laboratório legado opcional

O produto inicia com synthetic-native sem RuView. A integração histórica abaixo
é preservada para regressão, desabilitada por padrão. Requer
SPATIAL_LEGACY_LAB_ENABLED=true explicitamente; os runners isolados -RuView fazem
esse opt-in somente no ambiente de teste. Não atribuir o motor nativo ao upstream.
Evidências atuais e limitações de originalidade: VERIFICATION_REPORT.md e
ORIGINALITY_REGISTER.md. O restante deste guia registra a integração histórica.

Inspeção e execução em 14/10/2026, America/Fortaleza. Validação técnica de software;
não valida sensoriamento físico, contagem real, modelos ou medições clínicas.

## Referência upstream verificável

- Repositório oficial: [ruvnet/RuView](https://github.com/ruvnet/RuView).
- HEAD inspecionado: `a1ca023ee872683d160250d47ae3d4d228af55a0`.
- Imagem oficial executada: `ruvnet/wifi-densepose@sha256:bd2b2648a75ffb498a8e001b54c957c1f853d2ee709e16986d38f88676186d14`.
- Revisão declarada no label OCI da imagem: `0f95193190261a8966ad5f52e188aa6a480c2968`,
  também obtida e inspecionada; criada em `2026-10-12T16:56:30.937Z`, licença MIT.
- [Servidor da revisão da imagem](https://github.com/ruvnet/RuView/blob/0f95193190261a8966ad5f52e188aa6a480c2968/v2/crates/wifi-densepose-sensing-server/src/main.rs):
  `SensingUpdate`, `simulated_data_task`, `ws_sensing_handler`, `health_ready`, `latest`.
- [Entrypoint oficial](https://github.com/ruvnet/RuView/blob/0f95193190261a8966ad5f52e188aa6a480c2968/docker/docker-entrypoint.sh):
  `CSI_SOURCE=simulated` gera `--source simulated`. Não repetir essa flag em argumentos
  da imagem: o parser rejeita duplicatas. O binário direto aceita `--source simulated`.

O clone de inspeção fica em `artifacts/upstream/RuView`, ignorado. Não vendorizamos
o motor nem substituímos sua execução por um servidor próprio. Servidores pequenos
de testes injetam falhas, separados da validação com a imagem oficial.

## Superfícies identificadas

| Superfície | Comportamento observado / uso |
| --- | --- |
| REST HTTP, porta interna 3000 | `/health`, `/health/ready`; `/api/v1/status` retorna `status=ready`, `source=simulated`, `source_state=synthetic`; adaptador verifica os três campos em cada conexão |
| REST `/api/v1/sensing/latest` | Snapshot com `type=sensing_update`, timestamp Unix em segundos (float), source, tick, nodes, features, classification, signal_field, persons e estimated_persons opcionais; consultado, não usado como fallback |
| WebSocket `/ws/sensing`, porta interna 3001 | Frames JSON de sensing_update; a rota também existe no router HTTP. Usamos a porta WS dedicada; cliente websockets responde ping/pong |
| Autenticação upstream | Bearer no REST e no handshake WS do cliente servidor, nunca na URL. Nosso WebSocket continua autenticando no primeiro frame |

Outras APIs de pose, modelos, vitais e treinamento existem no upstream; não são
consumidas ou consideradas validadas nesta F2. Modo `auto` não comprova origem
sintética: exige-se `simulated` e `source_state=synthetic`. Nenhuma porta UDP,
MQTT ou de hardware é publicada.

`apps/api/tests/fixtures/ruview-sensing-update.json` contém os campos consumidos de
um frame recebido da imagem acima (tick 113). Sinais, keypoints, confianças e vitais
não são copiados para o evento normalizado.

## Contratos, persistência e controles

O evento interno `SensingEvent` **1.0.0** e seus oito cenários permanecem intactos.
`RuViewEvent` **1.1.0** é aditivo, com `source_id=ruview-01`,
`event_type=simulation.ruview.observation`, `generator=ruview-simulated`, tick
upstream, timestamp UTC e versão do adaptador. Ambos mantêm `SIMULATED`,
`L0_SYNTHETIC`, `IMPLEMENTED_SYNTHETIC` e privacidade `synthetic`.

Preservamos `classification.presence`. `estimated_persons` ausente com presença
vira **null**, nunca uma contagem inventada; ausência sem contagem vira zero.
Contagem fora de 0–20 ou incoerente com presença é rejeitada. Confiança/qualidade
medida e modelo ficam null. `ground_truth_positions=[]`: picos do campo/pose upstream
não são a verdade do laboratório 8 × 6 m. O mapa explica essa limitação sem desenhar
pessoas ou conectar os seis sensores internos durante uso do RuView.

Mesma tabela SQLite, retenção, paginação e pipeline de persistência antes de
publicação. Nenhuma migração destrutiva ou conversão de histórico. UUID derivado de
timestamp/tick e inserção idempotente deduplicam replay inclusive após reinício.
Dashboard valida ambas as versões com Zod. Schemas/exemplos em packages/contracts.

`POST /api/v1/sources/select` aceita `{ "source": "SIMULATED" }` ou
`{ "source": "RUVIEW_STREAM" }`, com Bearer e sessão parada. Seleção nunca apaga
histórico. Os controles `/simulation/start`, `/pause`, `/resume`, `/stop`, `/reset`
continuam disponíveis. No RuView, iniciar conecta o consumidor; parar não encerra
o container; pausar descarta frames mantendo a conexão, sem persistir/publicar.
Cenário, ocupantes, semente e velocidade internos não controlam o serviço externo
e ficam ocultos na interface. Status.config permanece por compatibilidade.

Ao reiniciar a API, a fonte padrão volta ao simulador interno **parado**. Histórico
de ambas as origens permanece. Seleção e controles são auditados.

## Conexão e qualidade dos dados

Adaptador separado em `app/ruview.py`, usando websockets já presente no lock e
urllib padrão; nenhuma nova dependência obrigatória. REST sem proxy de ambiente
nem redirects. URLs apenas no backend, em loopback ou hostname Docker `ruview`,
sem credenciais/query/fragment. Dashboard não recebe nem define URLs do serviço.

Timeout REST/conexão 2 s, leitura 0,5 s, fechamento 1 s; frame até 256 KiB e fila
WS de quatro mensagens. Filas do pipeline/dashboard continuam limitadas.
Reconexão progressiva 0,5–10 s sem fallback de fonte. Só aceitamos sensing_update
simulated com timestamp finito/recente, tolerando relógio futuro até 2 s.
Frames fora de ordem, inconsistentes, malformados e origem real são rejeitados;
outros tópicos são ignorados. Dados obsoletos não são publicados.

`/system/status.source_diagnostics`: serviço, conexão, idade/obsolescência, frames
aceitos/rejeitados/ignorados/duplicados, reconexões e erro sanitizado. Qualidade
significa integridade/frescor do fluxo, não RF ou confiança de inferência. Recebidos
incluem frames descartados durante pausa; contador de eventos persistidos é separado.
Não há replay de frames perdidos pelo serviço. Pausa/interrupções podem deixar lacunas.

## Inicialização e configuração

Depois de bootstrap, com Docker Desktop Linux ativo:

```powershell
.\scripts\dev\start-ruview.ps1
.\scripts\dev\start.ps1
```

O primeiro comando gera `.env.ruview` **somente se ausente**, com token aleatório.
A API lê `.env` e `.env.ruview` (segundo prevalece; variáveis de processo têm
precedência). Não modifica o token do dashboard. Cria apenas o projeto Compose
`wifi-spatial-ruview`, testa REST + WS e publica em loopback 4860/4861.
Dashboard: conectar com `SPATIAL_TOKEN`, parar sessão atual, selecionar
**RuView simulado**, clicar **Iniciar simulação**.

| Variável backend | Padrão / efeito |
| --- | --- |
| `SPATIAL_RUVIEW_HTTP_URL` | `http://127.0.0.1:4860`, REST autenticado |
| `SPATIAL_RUVIEW_WS_URL` | `ws://127.0.0.1:4861/ws/sensing`, streaming |
| `SPATIAL_RUVIEW_TOKEN` | Segredo separado do dashboard, nunca NEXT_PUBLIC |
| `SPATIAL_RUVIEW_STALE_SECONDS` | 5 s, permitido 1–60 s |

Portas alternativas: `start-ruview.ps1 -HttpPort 4960 -WsPort 4961`, então definir
as duas URLs correspondentes em `.env.ruview` antes de iniciar/reiniciar a API.
Não substituir tokens existentes. Para parar somente esse serviço:

```powershell
docker compose --env-file .env.ruview -f compose.ruview.yaml -p wifi-spatial-ruview down
```

Para toda a plataforma em Compose: gerar `.env.ruview`, parar o RuView separado
com o comando acima e os servidores nativos nas portas padrão, então:

```powershell
docker compose --env-file .env --env-file .env.ruview -f compose.yaml -f compose.ruview.yaml up --build --detach --wait
docker compose --env-file .env --env-file .env.ruview -f compose.yaml -f compose.ruview.yaml down
```

API em container usa `http://ruview:3000` e `ws://ruview:3001/ws/sensing`.
`SENSING_ALLOWED_HOSTS=ruview` autoriza esse hostname no controle Host do RuView,
mantendo a validação ativa. Sem essa entrada, o upstream responde HTTP 421.
O volume SQLite de uso é preservado. Não usar `down --volumes`.

## Verificação e troubleshooting

```powershell
.\scripts\verify\check.ps1 -RuView
# Stack inteira isolada + reinício real da API / SQLite:
.\scripts\verify\ruview-compose.ps1
```

Executa Ruff, pytest, ESLint, tipos, contratos, build de produção, E2E do MVP e E2E
da imagem oficial. Exige 4310/4810/4860/4861 livres; banco temporário e projeto
`wifi-spatial-f2-verification`. Pausa/despausa apenas o container cujo label
comprova esse projeto, testa recuperação e encerra serviços próprios ao terminar.
Credencial em `artifacts/ruview-verification.env`; nenhum histórico de uso excluído.
`check.ps1` sem `-RuView` marca o teste oficial skipped; não equivale à validação F2.

| Sintoma | Ação |
| --- | --- |
| Porta ocupada | Escolher outra ou encerrar manualmente sua própria instância; launcher preserva processos alheios |
| HTTP 401 / handshake recusado | Conferir mesmo SPATIAL_RUVIEW_TOKEN na API e container; recriar container/reiniciar API após alterar configuração |
| HTTP 421 | Conferir SENSING_ALLOWED_HOSTS=ruview no Compose; não desativar validação Host |
| Status/frame rejeitado | Conferir CSI_SOURCE=simulated, source_state=synthetic, digest, relógios e contrato; não contornar verificação de origem |
| Sem dados recentes / reconectando | Conferir Docker Desktop, container e portas; consumidor tenta até parar sessão |
| Sem pessoas no mapa | Esperado: não há posições de verdade compatíveis com o laboratório interno |
| Contagem indisponível | Presença sem estimated_persons; null não significa sala vazia |
| Source duplicado | Usar CSI_SOURCE=simulated com a imagem; não acrescentar --source |
| Histórico não cresce em pausa | Esperado; fluxo externo continua sem persistência/publicação |

Não usar latest para reprodução: o digest fixa o artefato testado. Atualização
exige reinspecionar contrato/proveniência e repetir o teste oficial.
