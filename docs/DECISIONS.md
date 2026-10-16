# Decisões de arquitetura — v3.0

## ADR-013 — Histórico de regras, tipagem verificada e imagens fixadas

Status: Accepted. Data: 16/10/2026. Fecha contracts-data-13 e pendências do PR #6.

- Migração 0009 adiciona `local_rules.created_at/revoked_at` e `audit_events.subject_id`
  (anuláveis). Regras anteriores ficam com NULL: o horário real é desconhecido e não é
  inventado; a UI diz "criação anterior ao histórico". Revogar de novo mantém o primeiro
  horário e não duplica auditoria. `subject_id` guarda só o ID do registro afetado.
- mypy (MIT, plugin pydantic) roda no gate e no CI com `check_untyped_defs` sobre `app/`.
  Os `type: ignore[assignment]` em `contracts.py` são o estreitamento deliberado dos
  literais do contrato 2.0.0; `warn_unused_ignores` impede ignorar além disso.
- Imagens base fixadas pelo digest do índice multi-arquitetura; atualização só por PR
  revisado (Dependabot `docker`). O digest 3.13 do `Dockerfile.verify` é argumento.

## ADR-012 — Perfil de capacidades aplicado na borda HTTP/WS

Status: Accepted. Data: 16/10/2026. Complementa a seção 0A do plano v4.

- O catálogo deixa de ser só informativo: cada router declara a capacidade que expõe e
  `require_capability` recusa com 403 quando o perfil ativo a desliga. A verificação
  roda depois de `authorize`, para não revelar o perfil a clientes sem token.
- Superfícies operacionais (status, catálogo, governança, health) ficam abertas em todo
  perfil; o status contém apenas estado sintético e é necessário ao login do dashboard.
- O frontend lê o catálogo no login e omite módulos desligados, mas a fonte de verdade é
  o backend. Capacidade nova sem entrada no catálogo falha na importação do router.
- Etiquetas regulatórias continuam hipóteses de trabalho, não parecer jurídico.

## ADR-011 — Composition root, routers por contexto e repositórios SQLite

Status: Accepted. Data: 15/10/2026. Complementa ADR-001.

- `app/bootstrap.py` constrói um `Container` (store, pipeline, model lab, fila, limiter,
  backup, leitura de histórico, locks) por instância de aplicação; `create_app` só
  compõe lifespan, middlewares, handlers e routers. `logging.basicConfig` saiu do import.
- Rotas em `app/api/{simulation,analytics,model_lab,automation,catalog,stream}.py`,
  sem closures; dependências via `request.app.state.container`. Paths, parâmetros,
  `operationId` e componentes do OpenAPI comparados antes/depois: idênticos.
- `app/adapters/sqlite/` separa engine/UDF (`database.py`), ORM (`models.py`) e
  repositórios de eventos, regras, relatórios, laboratório e auditoria. Decisões de
  regras continuam na mesma transação do evento (ADR-007) via `record_decisions`.
  `app/storage.Store` permanece como fachada estável para pipeline, scripts e testes.
- Revogação usa `Pipeline.quiesced()` em vez de a rota tocar lock e fila internos.
  Cenários, geometria 8 × 6 e sensores virtuais vêm de `domain/acquisition.py`; limites
  20/1000 de `domain/rules.py`. O heartbeat do WS preserva o `get` pendente entre
  iterações, e `/system/status` roda no event loop.
- Não mudou: códigos HTTP, contratos exportados, migrações. Pendentes: hierarquia de
  exceções de domínio, auditar como `operation.denied` só recusas protetivas, porta
  explícita `SourceProvider`, `TrustedHost` configurável e docs `/docs` opt-in.

## ADR-010 — Integridade do histórico, verificação descartável e CI gratuito

Status: Accepted. Data: 15/10/2026.

- Payload armazenado que falha no contrato é **excluído e declarado** nas `limitations`
  do relatório (contagem, sem conteúdo no log), em vez de derrubar analytics com 500.
  Evidência forjada (ex.: L3 falso) continua nunca contada.
- Retenção por quantidade apaga somente `L0_SYNTHETIC`. Evidência L1/L2 futura exigirá
  política própria de retenção (Governance/RetentionPolicy), nunca efeito colateral.
- Replay pagina no SQL com ordem `spatial_epoch_us(timestamp), event_id`; offset continua
  (ADR-003). A UI recusa um replay cujo total muda durante a carga e pede nova consulta.
- `docker-e2e.ps1` cria um projeto Compose por execução e remove **apenas o volume
  descartável desse projeto** ao final; volumes de uso nunca são tocados. Specs externos
  exigem projeto `wifi-spatial-native-e2e*`, token e porta explícitos e conferem a porta
  no Docker antes de passos destrutivos.
- CI no GitHub Actions somente com runners Linux (cota gratuita), actions pinadas por
  SHA, sem segredos, permissões `contents: read`; Dependabot apenas propõe PRs. O gate
  local `check.ps1` continua normativo no Windows.

## ADR-009 — Avatares articulados como apresentação, pesquisa RF separada

Status: Accepted para apresentação; reconhecimento RF permanece pesquisa.
Data: 15/10/2026. Escopo confirmado pelo proprietário: visual agora, pesquisa depois.

Decisão: adicionar rigs e projeção isométrica próprios em SVG, sem Three.js/WebGL
ou assets externos. Mantém custo/dependências e permite contraste, SSR e testes
determinísticos. Corpos luminosos/articulações e animais atendem a referência visual
fornecida; tela cheia amplia a cena, sem prometer câmera orbitável ou malha física.
Planta 2D continua selecionável. IDs de gradiente/grade são únicos por instância,
evitando colisões entre cena ao vivo e replay.

Espécie é preferência visual local do operador, sem persistir/inventar classe nos
eventos. Contagem/posições e L0 continuam iguais; anatomia/gait são procedurais.
Rigs sem posições não são desenhados, inclusive no legado RuView. Não gerar
vitais/RSSI/confiança para imitar o screenshot. Movimento reduzido desativa a
articulação; pausa interrompe avanço por tick, controles de volume preservam dados.

Alternativas: motor 3D adiciona câmera/oclusão/assets, mas exige nova dependência,
budget GPU e validação; fica para necessidade explícita. Download automático de
modelos não resolve ausência de CSI/labels e mistura apresentação com inferência.
Não adotado. Loader/modelos RF continuam opcionais e separados do motor nativo.

Pesquisa: encoder HF MIT candidato, revisão fixada no guia; saída128D não é pose.
Modelo MM-Fi de pose declara CC BY-NC 4.0 e não entra no produto comercial.
Documentação/benchmark dos autores não foi reproduzida localmente. Próximo R0/R1
conforme PEOPLE_ANIMALS_RF_RESEARCH e RF_VALIDATION_PROTOCOL, sem captura agora.

## ADR-008 — Recuperação da demo e fronteiras corporativas incrementais

Status: Accepted para o incremento local; propostas de escala permanecem Proposed.
Data: 15/10/2026. Responsável pela decisão técnica: execução local autorizada.

Contexto: testes novos existentes divergiam de contratos exportados e do cliente.
REST podia substituir eventos recentes recebidos no WS; close 1008 iniciado pelo
browser era inválido; o formulário podia impedir pausa/parada. Launchers confiavam
em X-Forwarded-For, contrariando a identidade de peer definida em ADR-005.

Decisão: manter FastAPI/SQLite/Next e portas existentes. Centralizar erros HTTP e
CSV no cliente; fechar contrato inválido com 4002; preservar evento mais recente;
validar formulário somente no início nativo. Contratos TS discriminados por versão,
schemas/fixtures regenerados e drift check obrigatório. JSON 500 sanitizado no
backend. Lazy loading dos painéis secundários após conexão. Uvicorn com
--no-proxy-headers nos três launchers; seis regressões agora no gate oficial.

Alternativas: reescrita/microsserviços (custo operacional e risco altos, sem dados
de carga); biblioteca global de estado/HTTP (dependência desnecessária para os
defeitos observados); incremento sobre stack atual (baixo custo e regressão
observável, escolhido). Nenhuma biblioteca nova nesta entrega.

Consequências: compatibilidade histórica preservada; nenhuma migração de banco
necessária. Mais verificações no gate e pacotes de contrato incluídos na imagem
de verificação. Um worker/SQLite e tipagem Python parcial continuam limites.
Trust de proxy futuro exigirá decisão explícita com TLS/proxy autenticado; não
reativar headers somente para alterar o endereço mostrado. Ganho de carregamento
não foi quantificado; bundles separados não constituem benchmark.

Seguimento: Docker atual indisponível; reconstruir/verificar quando daemon voltar.
Routers por domínio, checker Python e benchmark são próximos incrementos, não
conclusões desta ADR. Planos e critérios em ROADMAP_AND_SKILLS.md.

## ADR-007 — Fila, previews e preparação de hardware

Fila F4 é aditiva ao endpoint síncrono G, usa o mesmo ModelLab e lock CPU. Duas
vagas de espera/um worker e máximo 100 jobs, sem exclusão automática. Cancelamento
cooperativo respeita a fronteira de commit; progresso mede fases, não tempo previsto.
Restart não retoma jobs silenciosamente. Erros sanitizados mantêm diagnóstico
por estado e resultados, sem payload de exceção em HTTP. Modelos JSON internos
não são código executável carregado de usuário. Licença própria/stdlib, sem nova
dependência RF/ML ou código upstream.

Regras F5 apenas dry-run: predicados tipados, 20 regras e 1.000 decisões, sem
eval/exec, URLs ou dispatcher. Banco e decisão na mesma transação; revogação
sincronizada com ingestão. Capacidade explícita impede crescimento ilimitado;
histórico não é apagado. RBAC/consentimento e ações externas não são entregues.

F6 prepara parser offline com envelope próprio e sinal de teste, sem chamá-lo
CSI. Hash sem chave não autentica hardware. F7 documenta protocolo sem executar
captura: autorização e referência física continuam pré-condições humanas.

## ADR-006 — CSP com nonce e baseline de geometria virtual

CSP: hashes estáticos exigiriam extrair e atualizar scripts de hidratação a cada
build/rota; SRI experimental não resolve sozinho inline dinâmico. Adotado nonce
criptográfico por resposta em proxy.ts, propagado ao request para Next e ao header
response. force-dynamic/no-store desabilitam cache HTML estático, mantêm assets
cacheáveis e suportam standalone. Scripts sem unsafe-inline em produção, eval
somente dev; style-src mantém unsafe-inline para atributos React do gráfico.
Não chamar a política inteira de CSP estrita. Fonte consultada:
https://nextjs.org/docs/app/guides/content-security-policy.

Baseline G usa somente geometria de um ponto virtual. Classes walking/stationary
descrevem trajetória gerada, não atividade humana observada. Sitting é indistinguível
e permanece unsupported, junto a queda/RF/vitais/pose. Rótulos de referência ficam
separados das features: preditor recebe apenas velocidade média e parâmetros
treinados. Treino escolhe limiar em dados train; validation/test não o alteram.
Sessões e espaçamentos de amostra disjuntos por split, sem quadros compartilhados.
Janelas com lacuna/menos de três pontos ou próximas do limiar retornam unknown.
Métricas sintéticas incluem rejeição, matriz e denominadores null quando vazios.
Até 96 janelas/dataset, 100 runs persistidos, uma execução por vez, sem upload de
modelo/pickle/path. Operação CPU curta síncrona limitada; sem job em background
que continue após uma resposta de sucesso. Fila/cancelamento de treino longo F4
exige incremento próprio, não é alegado a partir deste baseline.

## ADR-005 — Backup recorrente e limites locais

Rotina opt-in por processo da API, snapshot imediato e intervalo padrão diário;
destino explícito dentro do workspace, lock exclusivo compartilhado por destino,
sem roubar lock após crash, sem scheduler global nem prune automático. Operador
deve confirmar recuperação e remover lock obsoleto apenas após verificar ownership.
Cópia no mesmo disco não cobre perda do dispositivo. Status oferece somente
contadores, UTC e códigos de erro estáveis. Encerramento aguarda cópia em curso.

Limiter de janela fixa 60 s: 30 tentativas auth, 60 escritas e 600 leituras por
peer; limite de 1024 peers, TTL e rejeição conservadora na capacidade, sem evict
de chave abusiva. Usa endereço da conexão, ignora X-Forwarded-For. Um worker;
reinício zera os contadores, não é controle de serviço público. Auditoria de
negativas agregada em até nove tipos fixos, contador/primeiro e último UTC/UUID
do último incidente. Não armazena token, IP, headers ou payload. Retenção é
agregada, não histórico individual ilimitado; auditoria antiga preservada.

15/10/2026. Registro incremental; não certifica conclusão de fases futuras.

## ADR-001 — Monólito modular, migração por fronteiras

Preservar FastAPI/SQLite/Next.js. Domínio Acquisition puro em app/domain;
portas explícitas de relógio e histórico; adaptadores nativo/SQLite; caso de uso
de leitura em application. Contratos HTTP/Pydantic ficam na borda existente.
Pipeline legado não foi reorganizado por estética. Outros bounded contexts serão
extraídos quando houver comportamento implementado; arquivos vazios não são entrega.

## ADR-002 — Provedor padrão e compatibilidade

synthetic-native é o padrão; contrato novo 2.0.0, source native-01. SIMULATED
continua aceito como alias de seleção, mas produz a nova versão explicitamente.
Eventos antigos continuam legíveis. Laboratório de integração externo exige flag
explícita, fica fora do startup normal e mantém atribuição. Não apagar legado
antes da comprovação da migração e autorização para remoção de arquivos.

## ADR-003 — Histórico, continuidade e métricas

Coluna segment_id e tabela analytics_reports via migração 0002. Novo trecho em
start/resume; registros antigos ficam sem sessão atribuída, sem inventar vínculo.
Agregações recalculadas deterministicamente e snapshots salvos com retenção de
100 relatórios. Paginação offset limitada a 10.000 eventos por consulta; manter
fim UTC fixo no replay. Cursores e rollups incrementais ficam para volume maior.

Filtros temporais usam microssegundos UTC inteiros (UDF spatial_epoch_us) em vez
de julianday, que arredondava fronteiras submilissegundo. Início inclusivo/fim
exclusivo preservados, sem regravar payloads históricos nem alterar schema.

Médias por amostra, não ponderadas por tempo. Intervalos somente entre observações
do mesmo trecho/fonte; lacunas > gap_seconds viram unknown. Deltas líquidos não
provam entradas/saídas individuais. Não extrapolar além dos extremos observados.
Quantis empíricos inferiores: índice floor((n−1)×p); latência é espera antes da
gravação, não latência de sensor nem de processamento completo. Drop é de entrega
visual; perda RF indisponível. Taxa histórica n/amplitude temporal, null se sem
amplitude; taxa runtime por janela de até 60 s e buffer de 2.000 amostras.

## ADR-004 — Recuperação e retenção

Backup via SQLite backup API com checksum/integridade, restore para arquivo novo,
sem substituir banco ativo. Expurgo de auditoria somente offline, após backup e
arquivo verificado, mínimo 90 dias; security./audit. e legal hold são preservados.
Hashes locais detectam alteração quando comparados ao recibo confiável; não são
WORM, assinatura independente ou proteção contra administrador local malicioso.
