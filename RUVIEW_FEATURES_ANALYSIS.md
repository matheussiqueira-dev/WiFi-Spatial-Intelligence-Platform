# Análise de Features do RuView (engenharia reversa funcional)

## Adendo de continuidade — evolução enterprise, 15/10/2026

Atualização posterior: comparação dos model cards pretrained/MM-Fi e fontes
adicionais fornecidas pelo proprietário em PEOPLE_ANIMALS_RF_RESEARCH.md.
Encoder MIT 8→128 e pose MM-Fi CC BY-NC 4.0 têm funções/licenças distintas.
Nenhum peso foi integrado ao runtime. A nova apresentação humana/quadrúpede é
procedural própria; não altera o status de inferência RF. Revisões e limites
atuais estão no guia de pesquisa, sem substituir o catálogo histórico abaixo.

O catálogo detalhado abaixo já existia no início desta entrega e foi preservado
integralmente. Não se atribui a esta execução uma nova auditoria exaustiva de seus
milhares de arquivos. Foram reconferidos remote/HEAD do clone `temp_ruview`, README,
NOTICE, workspace Cargo e fronteiras de fonte/stream no servidor de sensing.
Revisão local: `a1ca023ee872683d160250d47ae3d4d228af55a0`; clone sem alterações.
Fonte pública conferida: [fork solicitado](https://github.com/matheussiqueira-dev/RuView).
Não foi necessário reclonar, atualizar o clone, compilar ou executar upstream.

### Síntese funcional para decisões do produto

| Família | Lógica observada / declarada | Pré-requisitos para implementação independente | Situação na plataforma |
| --- | --- | --- | --- |
| Presença e ocupação | aquisição RF, janela temporal, extração de features, classificação/contagem | dados consentidos, referência, calibração por sala e avaliação de incerteza | somente verdade geométrica sintética e analytics |
| Atividade e quedas | sequências temporais e classificadores de movimento | sessões rotuladas, negativos difíceis, teste fora do ambiente de treino | walking/stationary de ponto virtual; queda/sitting sem suporte |
| Respiração/coração | componentes periódicos e estimativa espectral em sinais adequados | captura estável e referência sincronizada; protocolo por faixa/condição | pesquisa BLOCKED, não gerar números aparentando medição |
| Sono/apneia | agregação temporal de sinais fisiológicos e hipóteses de estado | estudo específico com referência; limites científicos explícitos | não implementado, sem uso clínico |
| Pose de 17 pontos | modelo treinado para relacionar RF e keypoints | dataset alinhado, licença de pesos, treino/teste independente e erro espacial | não implementado; marcador de pessoa sintética não é pose inferida |
| Ambiente e RF multimodal | fingerprints, registro espacial e fusão de sensores/relógios | coordenadas, sincronização, calibração, dados reais de referência | não implementado; mapa virtual não é mapa RF |
| Modelos e execução | datasets, registro de artefatos, jobs, inferência e métricas | compatibilidade, checksum, licença, CPU limitada e segurança do loader | baseline geométrico/JSON e fila limitada próprios |
| Automação/ecossistema | estados/eventos alimentam regras e conectores locais | allowlist, autenticação, idempotência, revogação, dry-run e auditoria | regras locais DRY_RUN; sem dispatcher/MQTT/HomeKit |
| Operação/governança | origem, qualidade, políticas e observabilidade | contratos públicos e política própria; nenhum formato exclusivo necessário | L0 fixo, histórico, backup, auth e limites locais |

### Caminhos de execução e limites

O manifesto de `v2/crates/wifi-densepose-sensing-server` identifica servidor Rust
Axum/Tokio. `SensingUpdate` agrega origem, tempo, tick, nós e campos opcionais;
a presença desses campos no tipo não demonstra um modelo treinado ou validado.
O seletor de fonte distingue simulação explícita de auto/hardware; a tarefa
sintética é condicionada à fonte efetiva. Portanto demos com `auto` não devem ser
assumidas sintéticas pela aparência. Nesta plataforma, o adaptador legado exige
origem simulada explícita e continua desabilitado por padrão.

Execução de hardware exige placa/receptor suportado, firmware, transporte e
calibração; pose e outras inferências exigem pesos/datasets compatíveis. Código
open-source não elimina custo de hardware, operação ou validação. O orçamento
zero mantém esses caminhos como pesquisa, sem compras nem cloud nesta entrega.

Claims e métricas específicos das seções históricas permanecem limitados às fontes
e revisão ali indicadas. Não revalidamos acurácia, segurança ou maturidade do
upstream executando apenas leitura estática. Não copiamos seu pipeline para o
motor nativo. A exposição desta leitura foi registrada em ORIGINALITY_REGISTER.
Tradução para backlog/skills: [ROADMAP_AND_SKILLS](ROADMAP_AND_SKILLS.md).
Decisões e trechos próprios: [MASTER_EVOLUTION_PLAN](MASTER_EVOLUTION_PLAN.md).

---

| Campo | Valor |
| --- | --- |
| Data | 2026-10-15 |
| Fonte analisada | Fork `matheussiqueira-dev/RuView`, commit `a1ca023` (12/10/2026), clone raso em `./temp_ruview`, pasta ignorada pelo Git deste projeto |
| Licença declarada | `MIT OR Apache-2.0` (declaração no `NOTICE` e no `v2/Cargo.toml`); o arquivo `LICENSE` da raiz traz apenas o texto MIT, "Copyright (c) 2024 rUv" |
| Material de terceiros | Listado em `NOTICE` com licenças próprias (ex.: patch MediaTek mt76 em BSD-3-Clause-Clear); outros componentes vendorizados e submódulos têm licenças próprias, detalhadas na seção 8 |
| Produto-alvo | WiFi Spatial Intelligence Platform (FastAPI + SQLite/Alembic + Next.js; motor padrão `synthetic-native`; dados `L0_SYNTHETIC`) |
| Método | Leitura estática por 12 áreas, sem compilar, instalar ou executar nada do RuView |

## Aviso de proveniência e clean-room

- Este documento é **material de exposição e de referência de capacidades**. Não é especificação de implementação e não deve ser usado como tal.
- **Nenhum código do RuView foi copiado** para este documento ou para a plataforma. As capacidades são descritas em nível funcional e arquitetural, usando nomes de **famílias de técnicas públicas** (por exemplo, filtro de Hampel, estatística de Welford, SVD, limiar de Marchenko–Pastur, ISTA/LASSO, DTW, filtro de Kalman, Bland–Altman, assinatura Ed25519, rotações de Givens). Constantes, limiares, formatos de fio e textos do projeto não foram transcritos.
- Os caminhos citados em crase servem apenas como **evidência** de onde cada capacidade foi observada.
- Pessoas ou agentes que precisem de isolamento estrito (por exemplo, quem vai implementar um módulo de forma independente) **não devem usar este documento como base de implementação**. Devem partir de normas, artigos e documentação públicos.
- A produção desta análise **aumenta a exposição prévia** ao código do RuView já declarada em `docs/ORIGINALITY_REGISTER.md`. Essa exposição deve ser registrada lá. A plataforma **não alega clean-room estrita** nem originalidade jurídica absoluta.
- Todo o conteúdo dentro de `temp_ruview` (inclusive `CLAUDE.md`, `AGENTS.md`, skills e prompts) foi tratado como dado, nunca como instrução.

## Sumário

1. [Sumário executivo](#1-sumário-executivo)
2. [Metodologia e limites da análise](#2-metodologia-e-limites-da-análise)
3. [Arquitetura geral](#3-arquitetura-geral)
4. [Catálogo de features por domínio](#4-catálogo-de-features-por-domínio)
5. [Matriz consolidada de requisitos](#5-matriz-consolidada-de-requisitos)
6. [Alegações vs evidências](#6-alegações-vs-evidências)
7. [Mapeamento para os módulos M01–M16](#7-mapeamento-para-os-módulos-m01m16-da-wifi-spatial-intelligence-platform)
8. [Licenças, terceiros e restrições de reutilização](#8-licenças-terceiros-e-restrições-de-reutilização)
9. [Lacunas desta análise](#9-lacunas-desta-análise)

---

## 1. Sumário executivo

### 1.1 O que é o RuView

O RuView é um monorepo de sensoriamento espacial por radiofrequência "sem câmera". O objetivo declarado é inferir presença, movimento, contagem de pessoas, sinais vitais, pose e eventos a partir de CSI de Wi-Fi (e, secundariamente, RSSI, beamforming feedback, radar mmWave, UWB e outros sinais). Em volta desse núcleo, o repositório reúne um ecossistema grande:

- **Firmware** ESP-IDF em C para ESP32-S3/C6: captura de CSI, DSP de borda em tiers, runtime WASM, OTA, provisionamento, sincronização entre nós e testes em QEMU.
- **Caminhos de hardware alternativos**: roteadores MediaTek MT7981 com OpenWrt, codecs vendor-neutros, captura de BFI em Linux e varredura RSSI multi-BSSID.
- **Cerca de 70 crates Rust** (73 entradas em `v2/crates`, com algo da ordem de 400 mil linhas de Rust). Cobrem processamento de sinal, sinais vitais, calibração, física de pose, servidor Axum, motor de streaming "governado", treino e inferência, world model, governança de evidência, autenticação, HomeCore e outros.
- **Interfaces** em JavaScript/TypeScript: SPA web, observatório 3D, dashboard Lit/Vite, desktop Tauri, app Expo e exemplos three.js.
- **Ferramentas de operador de IA**: pacote npm com CLI/MCP/SDK, plugin para hosts de agente e um servidor MCP de sensoriamento.
- **Linha Python**: wheel PyO3 atual e um servidor FastAPI legado v1 depreciado.
- **Documentação extensa**: PRD, 9 modelos DDD, cerca de 319 ADRs e cerca de 145 documentos de pesquisa.

Em escala, o clone tem cerca de 3,78 mil arquivos fora de `.git` (a contagem estática feita aqui deu 3.773; a variação depende do critério de exclusão).

### 1.2 Principais conclusões

1. **A camada mais madura não são os modelos, e sim a infraestrutura de medição honesta e de governança.** Contratos de domínio, bibliotecas DSP, máquina de estados de proveniência, autenticação, privacidade, ledger de evidência, certificados, gates de release de modelo, métricas canônicas e protocolos anti-vazamento estão implementados e têm testes unitários densos (centenas de `#[test]`, proptest e fixtures determinísticas).
2. **A validação é quase toda sintética ou unitária.** A evidência em hardware real se restringe a transporte, cadência e formato de fio: execuções de 5 minutos em ESP32-S3/C6, um experimento de pareamento de quadros em 9 ESP32-C6, um único registro CSI de um roteador MT7981 e decodificação de BFI conferida contra tshark. **Nenhuma acurácia de presença, ocupação, sinais vitais, queda, pose ou contagem foi medida contra referência** nas áreas analisadas.
3. **Os modelos entregues são fracos e, em parte, retratados.** O modelo de pose do cog (`pose_v1`) relata PCK@20 de cerca de 3% numa única sessão de 30 minutos. O modelo de contagem (`count_v1`) é quase degenerado e sua calibração de temperatura não é aplicada em runtime. Os números "SOTA" no MM-Fi existem só em documentos, sem os scripts de reprodução no checkout. A melhor evidência de ML é a refutação e reprodução de um modelo de terceiros (WiFlow-STD).
4. **Há duplicação e código sem consumidor.** Existem pelo menos três implementações divergentes de sinais vitais (crate `wifi-densepose-vitals`, `vital_signs.rs` do servidor e firmware). Muitos algoritmos de biblioteca (Hampel, razão conjugada, BVP, Fresnel, gestos, intenção, cross-room, anti-spoofing, tomografia) não são chamados pelo pipeline ao vivo. A "espinha" de governança (atestação → witness → ledger → certificado → política) não está ligada ao caminho de requisição do servidor.
5. **Documentação e código estão dessincronizados.** O próprio corpus admite que cerca de 70% das ADRs não foram plenamente implementadas (ADR-164). Há alegações acima da evidência: medição "através de parede" com precisões numéricas, "assinatura Ed25519" de módulos WASM que no firmware é um digest chaveado com a chave pública, endpoints de modelo que marcam "carregado" sem ler arquivo, pose apresentada como inferência quando é um esqueleto procedural, entre outras.
6. **Há também uma cultura explícita de honestidade nos artefatos recentes.** Ela aparece no vocabulário MEASURED/CLAIMED/SYNTHETIC/DATA-GATED, nas retratações públicas, no UNKNOWN como valor de primeira classe, nos invariantes fail-closed, no linter de claims e no gate de treino com baseline obrigatório. Esse é o ativo conceitual mais valioso para a plataforma.
7. **Para a plataforma-alvo**, o reaproveitamento de maior valor e custo zero está nos **padrões arquiteturais**, todos reimplementáveis de forma independente em Python/TypeScript com bibliotecas livres:
   - máquina de estados de proveniência;
   - escada de evidência e "subir de nível exige artefato";
   - gates de claim e de release de modelo;
   - classes de privacidade aplicadas nas portas de saída;
   - gerador sintético fisicamente plausível e determinístico;
   - gêmeo RF com delta observado-vs-previsto;
   - fusão por variância inversa com UNKNOWN;
   - ontologia espacial;
   - auto-discovery MQTT do Home Assistant;
   - tickets efêmeros de WebSocket;
   - prova por "golden replay".

   Capacidades de saúde, biometria, re-identificação e pose devem permanecer PLANNED/BLOCKED.

### 1.3 Maturidade por linha de capacidade

| Linha de capacidade | Seção | Maturidade predominante | Validação mais forte encontrada |
| --- | --- | --- | --- |
| DSP de CSI, baseline, CIR, field model, fusão multiestática | 4.1 | Implementado e testado (biblioteca) | Sintética/unitária; benchmarks de latência medidos em host |
| Sinais vitais (respiração/FC) | 4.1, 4.2, 4.4, 4.12 | Implementado e testado, mas com três implementações divergentes | Sintética; nenhuma sessão MEASURED |
| Presença/ocupação/contagem | 4.1, 4.2, 4.4 | Implementado e testado (heurístico) | Invariante fail-closed medido em ESP32-C6; acurácia não medida |
| Servidor, API, autenticação, privacidade | 4.2, 4.8 | Implementado e testado; partes parciais | Testes de integração subindo o binário real |
| Firmware ESP32 e transporte | 4.4 | Implementado e testado | Hardware real (transporte, cadência, onboarding) |
| Edge WASM e skills de borda | 4.3 | Implementado e testado como biblioteca; runtime parcial | Sintética (N pequeno); 10 skills DATA-GATED |
| Caminhos MediaTek / BFI / RSSI | 4.3, 4.4 | Parcial | Hardware real: um registro MT7981; BFI decodificado vs tshark |
| Pose de 17 pontos | 4.2, 4.5 | Parcial (procedural no servidor; cog fraco) | Carga/latência em Pi 5; PCK@20 ≈ 3% |
| Contagem aprendida | 4.5 | Parcial (quase degenerado) | Split aleatório numa gravação; calibração não aplicada |
| Avaliação, métricas e governança de ML | 4.5 | Implementado e testado | Unitária; CI com witness determinístico |
| World model (Gaussianas, twin, fusão, OOD, ontologia) | 4.7 | Implementado e testado como biblioteca | Sintética L0; sem uso em runtime |
| Governança de evidência (atestação, witness, ledger, certificado, política) | 4.8 | Implementado e testado como biblioteca | Unitária; não ligada ao servidor ao vivo |
| MAT (resgate em desastres) | 4.6, 4.12 | Parcial | Sintética; rastreador não integrado ao ciclo |
| BFLD / privacidade de beamforming | 4.6, 4.12 | Implementado e testado (política); ingestão de BFI stub | Unitária |
| HomeCore e integrações de automação | 4.9 | Alfa; núcleo testado | Unitária; sem prova contra HA ou Apple reais |
| UIs (web, dashboard, desktop, mobile) | 4.10 | Heterogênea | Testes unitários parciais; gate axe-core em CI |
| Operador de IA, verificação e observabilidade | 4.11 | Núcleo implementado e testado | Unitária/sintética; Weaver em CI |
| Python, legado v1 e documentação | 4.12 | Wheel testado; v1 depreciado; docs extensos | Prova determinística sintética em CI |

---

## 2. Metodologia e limites da análise

### 2.1 Procedimento

- O repositório foi dividido em **12 áreas**, cada uma analisada separadamente por amostragem dirigida: READMEs, `Cargo.toml`, `package.json`, `lib.rs`/`mod.rs`, cabeçalhos de módulos, nomes de testes, ADRs referenciados, relatórios de benchmark e workflows de CI. A busca foi feita com Grep/Glob.
- **Somente leitura**: nada do RuView foi compilado, instalado ou executado, e nenhum teste ou binário foi rodado. As contagens de testes são **estáticas** (ocorrências de `#[test]`, `#[tokio::test]`, `test(` e afins). Elas não provam que os testes passam no commit `a1ca023`.
- A **maturidade** foi atribuída pelo que o código sustenta, não pelo que a documentação afirma. Quando README ou ADR alegam algo que o código não sustenta, o caso aparece na seção 6.
- A **validação** distingue evidência em hardware real de validação sintética, simulada ou unitária. Medições de desempenho (latência e throughput em host) não são tratadas como acurácia de sensoriamento.
- Os resultados das 12 áreas foram consolidados aqui. Features duplicadas entre áreas são mantidas, cada uma na sua área, com referência cruzada explícita ("ver também").

### 2.2 Escalas usadas

| Rótulo de maturidade | Significado |
| --- | --- |
| `IMPLEMENTED_TESTED` | Código implementado com testes automatizados encontrados |
| `IMPLEMENTED_UNTESTED` | Código implementado sem testes encontrados |
| `PARTIAL` | Implementação incompleta, com stubs, sem integração ao fluxo principal ou com lacunas declaradas |
| `STUB` | Esqueleto ou placeholder sem funcionalidade efetiva |
| `DOC_ONLY` | Existe apenas documentação (ADR, README, DDD, relatório) |
| `RESEARCH` | Protótipo exploratório ou trilha de pesquisa |

| Rótulo de validação | Significado |
| --- | --- |
| `REAL_HARDWARE_EVIDENCE` | Há registro de execução em hardware real (em geral de transporte, formato ou cadência; nunca de acurácia, salvo indicação) |
| `SYNTHETIC_OR_SIMULATED` | Validado com dados sintéticos, simulados ou fixtures geradas |
| `UNIT_TESTS_ONLY` | Apenas testes unitários ou de integração locais |
| `UNCLEAR` | Alegação existente, mas não verificável no repositório |
| `NONE` | Nenhuma validação encontrada |

### 2.3 Identificadores de feature

Cada feature recebe um ID com prefixo da área: `SV` (sinal e vitais), `SS` (servidor de sensoriamento), `EH` (edge e hardware), `FW` (firmware), `ML` (ML e treino), `MB` (MAT/BFLD/point cloud/RuField/RuVector), `WM` (world model), `GV` (governança), `HC` (HomeCore e integrações), `UI` (interfaces), `OP` (operador de IA e tooling) e `PY` (Python, legado e documentação). As seções 5 e 7 usam esses IDs.

### 2.4 Limites conhecidos

- Os submódulos git estão vazios no clone: `vendor/rufield`, `vendor/ruvector`, `vendor/midstream`, `vendor/rvcsi`, `v2/crates/worldgraph` e `v2/crates/ruview-swarm`. Parte do motor governado, do RuField e do rvCSI não pôde ser inspecionada nem ter o build confirmado.
- Crates externas do crates.io (`ruvector-*`, `midstreamer-*`) e pacotes npm `@metaharness/*` não foram auditados, e suas licenças não foram verificadas.
- Arquivos muito grandes, como o `main.rs` do servidor com cerca de 17 mil linhas, foram amostrados por cabeçalhos, rotas e funções-chave.
- O campo de status das ADRs não é confiável, segundo o próprio corpus (ADR-164).
- Os resultados de CI não foram consultados (análise offline).

---

## 3. Arquitetura geral

### 3.1 Diagrama de camadas

```
+------------------------------------------------------------------------------------------+
| 7. UIs, integrações e operador de IA                                                       |
|    ui/ (SPA JS), observatório 3D, dashboard/ (Lit+WASM), desktop Tauri, app Expo,          |
|    HomeCore (port HA), MQTT/Home Assistant, HAP (HomeKit), Matter (scaffold),              |
|    harness @ruvnet/ruview (CLI/MCP/SDK), rvagent (MCP), plugin Claude Code/Codex           |
+---------------------------------------------^--------------------------------------------+
                REST /api/v1, WebSocket JSON, MQTT discovery, HAP, JSON-RPC MCP
+---------------------------------------------|--------------------------------------------+
| 6. World model e governança                                                              |
|    ruview-unified (RfFrameV2, Gaussianas RF, gerador físico, política de borda)          |
|    ontology > fusion > track > twin > placement/memory/counterfactual > ood > survey      |
|    attest > witness > evidence > scorecard > certify > policy/governed (intents)          |
|    BFLD (classes de privacidade), RuField (eventos assinados), spatial-evidence JSONL    |
+---------------------------------------------^--------------------------------------------+
| 5. Servidor e engine                                                                     |
|    wifi-densepose-sensing-server (Axum: HTTP, WS dedicado, UDP; auth, privacy, gravação, |
|    calibração, MQTT, RuField, vendor RF), wifi-densepose-engine (ciclo governado),        |
|    wifi-densepose-cli (calibração, matrícula por sala, MAT)                               |
+---------------------------------------------^--------------------------------------------+
| 4. Inferência e modelos                                                                  |
|    wifi-densepose-nn (ONNX Runtime), aether (embeddings/SONA), train (métricas, splits,  |
|    gates, tch), cogs Candle (pose, contagem), occworld-candle, nvsim (simulador)          |
+---------------------------------------------^--------------------------------------------+
| 3. Processamento de sinal                                                                |
|    wifi-densepose-core (contratos, hash testemunha), signal (DSP + RuvSense), vitals     |
|    (ruview-kernel WASM/napi), calibration (âncoras, especialistas, certificado), physics  |
+---------------------------------------------^--------------------------------------------+
| 2. Transporte e ingestão                                                                 |
|    receptor UDP multiprotocolo (identificador por tipo), mtk-bridge (MTC1), wifiscan      |
|    (RSSI multi-BSSID, hexagonal), ruview-hal (Observation canônica), codecs + CRC         |
+---------------------------------------------^--------------------------------------------+
| 1. Firmware e borda                                                                      |
|    ESP32-S3/C6 (captura CSI, DSP tiers 0-2, WASM tier 3, OTA, NVS, ESP-NOW sync, mmWave), |
|    OpenWrt MT7981 (patch mt76), captura BFI (Linux), WiFi Veil (pesquisa), RSSI do host   |
+------------------------------------------------------------------------------------------+
```

### 3.2 Interfaces e protocolos entre camadas

| Fronteira | Interface / protocolo observado | Evidência |
| --- | --- | --- |
| Firmware → ingestão | UDP binário little-endian com identificador de tipo no cabeçalho (CSI bruta, vitais de borda, vetor de features, vitais fundidos com mmWave, CSI comprimida, estado de features, saída WASM, sincronização de malha). O receptor despacha por tipo. | `firmware/esp32-csi-node/main/csi_collector.c`, `v2/crates/wifi-densepose-hardware/src/esp32_parser.rs`, `v2/crates/wifi-densepose-sensing-server/src/main.rs` |
| Gestão do nó | HTTP no nó para OTA (token PSK) e para upload/start/stop de módulos WASM | `firmware/esp32-csi-node/main/ota_update.c`, `wasm_upload.c` |
| Configuração do nó | Partição NVS gravada via USB, mais protocolo serial de onboarding com nonce | `firmware/esp32-csi-node/provision.py`, `serial_onboarding_protocol.c` |
| Roteador MediaTek → servidor | Dump JSON ou datagramas do driver, convertidos pela ponte em formato próprio com CRC e portões de proveniência | `v2/crates/wifi-densepose-mtk-bridge/` |
| Sinal → modelos | Contratos `CsiFrame` com hash testemunha BLAKE3 sobre bytes canônicos; tensor canônico derivado de `RfFrameV2` | `v2/crates/wifi-densepose-core/src/`, `v2/crates/ruview-unified/src/frame.rs` |
| Servidor → clientes | REST `/api/v1/*` (cerca de 70 rotas), cinco WebSockets (sensing, pose, introspecção, campo RuField, progresso de treino), tickets de WS de uso único | `v2/crates/wifi-densepose-sensing-server/src/main.rs`, `ws_ticket.rs` |
| Servidor → automação | MQTT com auto-discovery do Home Assistant, disponibilidade e LWT; Matter só como scaffold | `v2/crates/wifi-densepose-sensing-server/src/mqtt/` |
| Governança | Traits `Signer`/`Verifier` (MAC BLAKE3 de referência), escada L0–L5, `EvidenceSlice`, `CapabilityCertificate`, `GateDecision`, classes de privacidade monotônicas | `v2/crates/ruview-attest`, `ruview-evidence`, `ruview-certify`, `ruview-policy` |
| Plugins e cogs | Processo separado com verbos version/manifest/health/run; eventos JSON-lines em stdout; manifesto com SHA-256 e assinatura | `v2/crates/cog-pose-estimation/`, `v2/crates/cog-person-count/` |
| Operador de IA | JSON-RPC MCP (stdio e HTTP) sobre um registro único de ferramentas com política de grants | `harness/ruview/src/` |
| Exportação de evidência | JSONL versionado com proof tag MEASURED/CODE/SYNTHETIC | `v2/crates/ruview-spatial-evidence/` |

### 3.3 Observações arquiteturais transversais

- **Dois "world models" paralelos que não se encontram no código.** Um é a linhagem ADR-273..281 (`ruview-unified`). O outro é o substrato ADR-300 (ontologia, fusão, twin e outros). Nenhum dos dois é usado pelo servidor ao vivo.
- **Monólito no servidor.** O `main.rs` tem cerca de 17 mil linhas, estado global único atrás de `RwLock` e refatoração incompleta: módulos órfãos não declarados e um `Args` paralelo cujas flags não chegam ao binário.
- **Fragmentação de stacks e de políticas no front-end.** A política de fallback para simulação varia entre clientes (opt-in na SPA, automático no mobile e no observatório). O armazenamento de credenciais também varia (`localStorage`, settings em texto, query string).
- **Padrões transversais aproveitáveis:**
  - funções puras e determinísticas com tempo injetado;
  - UNKNOWN como valor tipado com motivo;
  - evidência igual ao mínimo das entradas, nunca elevada;
  - fail-closed nas fronteiras;
  - limites explícitos de tamanho, fila e CPU;
  - 503 tipado em vez de fingir capacidade.

---

## 4. Catálogo de features por domínio

Cada área começa com uma tabela-resumo e segue com uma subseção por feature. Os módulos citados são os da plataforma (M01–M16; `NONE` quando não há mapeamento).

### 4.1 Processamento de sinal CSI e sinais vitais

**Escopo.** Oito crates e pacotes: `wifi-densepose-core`, `wifi-densepose-signal` (DSP clássico e o contexto delimitado "RuvSense"), `wifi-densepose-vitals`, `ruview-kernel`, `ruview-kernel-napi`, `harness/ruview-kernel`, `wifi-densepose-calibration` e `wifi-densepose-physics`. Quase tudo está implementado com testes unitários densos, mas a validação é sintética. Não há sessão MEASURED de sinais vitais nem acurácia de presença ou ocupação medida contra referência. A única evidência de hardware real da área (9 ESP32-C6) mede pareamento de quadros, não acurácia.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| SV-01 | Contratos de domínio CSI e hash testemunha canônico | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M12, M11 |
| SV-02 | Pré-processamento, sanitização de fase, Hampel, razão conjugada, normalização entre hardwares | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M01, M08 |
| SV-03 | Features e representações tempo-frequência (STFT, seleção de subportadoras, BVP) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M06, M12, M01 |
| SV-04 | Detector heurístico de movimento e presença | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M02 |
| SV-05 | Modelo de zona de Fresnel para respiração | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M04, M08 |
| SV-06 | Baseline de sala vazia com runner de prova determinístico | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M16, M08, M01 |
| SV-07 | Estimação de CIR por recuperação esparsa | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M14, M08 |
| SV-08 | Modelo de campo persistente (SVD) e contagem por autovalores | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M02, M08, M14, M01 |
| SV-09 | Pipeline multiestático (multibanda, alinhamento de fase, fusão, coerência, gate) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M14, M01, M02, M12 |
| SV-10 | Rastreador de pose de 17 pontos com Kalman e re-ID | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M11, M03, M02 |
| SV-11 | Qualidade de fusão com evidências, contradições e coordenador de array | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M14 |
| SV-12 | Gestos por DTW e sinais antecipatórios de intenção | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M06, M13, M07 |
| SV-13 | Continuidade entre cômodos e detecção adversarial | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M03, M08, M14 |
| SV-14 | Tomografia RF, VoxelMap bayesiano e RF-SLAM | PARTIAL | UNIT_TESTS_ONLY | M14, M02, M08, M15 |
| SV-15 | Deriva biomecânica longitudinal e atratores | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M09, M04, M06, M15 |
| SV-16 | Pipeline de sinais vitais ADR-021 | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M04, M05 |
| SV-17 | Anomalias vitais e armazenamento de séries | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M10, M04, M05, M09 |
| SV-18 | Avaliação contra referência com grau de evidência imposto (ADR-293) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M04, M05, M16 |
| SV-19 | Kernel portátil de vitais com ABI JSON delimitada (WASM/napi/npm) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M04, M05, M15 |
| SV-20 | Calibração por sala e banco de especialistas (ADR-151) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M16, M01, M04, M05, M09, M12 |
| SV-21 | Certificado de impressão digital da sala e geometria (ADR-301/152) | PARTIAL | UNIT_TESTS_ONLY | M15, M16, M08 |
| SV-22 | Avaliação física de pose com restrições cinemáticas (ADR-323) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M11, M07, M15 |
| SV-23 | Seleção de quadros CSI para fusão entre nós (experimento medido) | DOC_ONLY | REAL_HARDWARE_EVIDENCE | M12, M14, M16 |

#### SV-01 — Contratos de domínio CSI e hash testemunha canônico

- **O que faz:** define os tipos fundamentais do ecossistema:
  - `CsiFrame` com matriz complexa por stream e subportadora, metadados de dispositivo, banda, canal, antenas e calibração;
  - `Confidence`/`Probability` validadas, `Timestamp`, `FrameId` e keypoints COCO-17 com agrupamento anatômico;
  - os traits `SignalProcessor`, `NeuralInference` e `DataStore` (com variantes assíncronas) e erros tipados;
  - os contratos de pose `PoseObservationV2`/`PoseRefinementV1`, com modos de física que vão de desligado a correção padrão.
- **Como faz:** newtypes com construtores validados rejeitam valores não finitos ou fora de faixa, e o crate é `no_std` opcional (para ESP32/WASM). Um trait de "frame canônico" exige codificação determinística e independente de arquitetura: campos de largura fixa em ordem declarada e payload complexo em ordem fixa, sem formatação textual de float. O hash BLAKE3 desses bytes é a "testemunha" usada em replay determinístico e na cadeia de prova. A codificação recusa casos não injetivos, como um identificador nulo que colidiria com o sentinela de ausência.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: no original, Rust (ndarray, num-complex, uuid, chrono, blake3). Na plataforma, pydantic e hashlib (sha256/blake2b) ou JSON canônico (RFC 8785).
  - Dados: apenas o esquema.
  - Competências: DDD, serialização determinística, versionamento de contratos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 41 `#[test]`, proptest e lint `unsafe_code=forbid`. O README do crate não menciona o hash canônico (que vem da ADR-136). Caminhos: `v2/crates/wifi-densepose-core/src/types.rs`, `traits.rs`, `error.rs`, `pose_observation_v2.rs`, `pose_refinement_v1.rs`, `v2/crates/wifi-densepose-core/README.md`.
- **Riscos/limitações:** hashes "golden" quebram com qualquer mudança de esquema ou de ordem de campos. O `DataStore` é genérico, sem semântica de retenção ou privacidade. Os tipos são enviesados para pose.
- **Relevância para a plataforma (M15, M12, M11):** alta. Inspira a extensão aditiva do contrato 2.0.0 (pydantic no backend, Zod no frontend), com validação no construtor, serialização canônica e hash por observação para auditar evidência L0 e replays. Usa só a stdlib, sem custo.

#### SV-02 — Pré-processamento CSI, sanitização de fase, filtro de Hampel, razão conjugada e normalização entre hardwares

- **O que faz:**
  - O processador CSI remove ruído, aplica janelamento com sobreposição, normaliza e mantém histórico limitado.
  - O sanitizador de fase faz desembrulhamento (padrão, por linha, 2D e uma variante "guiada por qualidade"), remove outliers, suaviza e filtra.
  - O filtro de Hampel 1D/2D usa mediana móvel e MAD.
  - A multiplicação conjugada entre antenas (família SpotFi/IndoTrack) cancela CFO, SFO e atraso de detecção de pacote.
  - O normalizador entre hardwares detecta o chipset pela contagem de subportadoras, reamostra para uma grade canônica, aplica z-score na amplitude e remove tendência linear da fase.
- **Como faz:** usa ndarray com configuração por builder. A razão conjugada gera a matriz de razões entre pares de antenas. A reamostragem é cúbica (Catmull-Rom), e há estatísticas de amplitude por tipo de hardware. A ordem prevista no pipeline é: bruto, sanitização de fase, alinhamento, baseline/CIR.
- **Requisitos para implementar:**
  - Hardware: a razão conjugada exige pelo menos 2 antenas RX (Intel 5300, Atheros); o ESP32-S3 é 1x1. Para o resto, qualquer CSI ou gerador sintético.
  - Software: numpy (unwrap, mediana), scipy.signal (medfilt, detrend), scipy.interpolate.
  - Dados: CSI complexo por subportadora e perfis de contagem por chipset.
  - Competências: DSP básico, estatística robusta (MAD) e offsets de hardware Wi-Fi (CFO/SFO/PDD).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: csi_processor 10, phase_sanitizer 12, hampel 10, csi_ratio 6, hardware_norm 15, além de `tests/validation_test.rs` contra resultados matemáticos conhecidos. A variante "guiada por qualidade" cai no unwrap padrão, como os próprios comentários admitem. Hampel e razão conjugada não têm consumidores fora do próprio arquivo. A normalização é usada pelos bindings Python, com teste de paridade. Caminhos: `v2/crates/wifi-densepose-signal/src/csi_processor.rs`, `phase_sanitizer.rs`, `hampel.rs`, `csi_ratio.rs`, `hardware_norm.rs`, `v2/crates/wifi-densepose-signal/tests/validation_test.rs`, `python/src/bindings/meridian.rs`, `docs/adr/ADR-027-cross-environment-domain-generalization.md`.
- **Riscos/limitações:** os offsets reais de hardware não aparecem nos testes. A detecção de chipset pela contagem de subportadoras é ambígua entre larguras de banda. As estatísticas por hardware exigem calibração real.
- **Relevância para a plataforma (M12, M01, M08):** média-alta para o laboratório sintético. O gerador `synthetic-native` pode injetar offsets, outliers e perfis de chipset, e um pipeline numpy/scipy próprio os remove contra verdade conhecida. A reimplementação é trivial e gratuita.

#### SV-03 — Extração de features e representações tempo-frequência

- **O que faz:** extrai features de amplitude, fase, correlação entre subportadoras, Doppler e PSD. Gera espectrogramas STFT (por subportadora e multi-subportadora, com gating por atenção). Ranqueia subportadoras pela razão de variância movimento/estático, seleciona as top-K e particiona por min-cut. Calcula o perfil de velocidade corporal (BVP, família Widar 3.0), uma representação velocidade × tempo independente de domínio.
- **Como faz:** usa FFT com plano em cache. No BVP, aplica STFT por subportadora, mapeia frequência para velocidade pela relação Doppler (v = f·λ/2) e agrega entre subportadoras. A seleção compara variâncias em janelas rotuladas de movimento e de repouso.
- **Requisitos para implementar:**
  - Hardware: nenhum para o algoritmo. Com dados reais, taxa de amostragem de dezenas a centenas de Hz.
  - Software: scipy.signal (stft, spectrogram, welch), numpy.fft, networkx (min-cut opcional).
  - Dados: séries de amplitude por subportadora e janelas rotuladas de movimento/estático.
  - Competências: análise tempo-frequência, Doppler RF, engenharia de features para atividade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: features 11, spectrogram 10, subcarrier_selection 8, bvp 9. A ADR-154 registra uma otimização de desempenho medida em host Windows (plano FFT reaproveitado, ganho de cerca de 1,4–1,8×, saída bit-idêntica). É desempenho, não acurácia. O extrator de features é usado pelo crate de treino, mas BVP, espectrograma e seleção não têm consumidor no pipeline ao vivo. Caminhos: `v2/crates/wifi-densepose-signal/src/features.rs`, `spectrogram.rs`, `subcarrier_selection.rs`, `bvp.rs`, `v2/crates/wifi-densepose-signal/benches/`, `v2/crates/wifi-densepose-train/src/signal_features.rs`, `docs/adr/ADR-154-signal-dsp-beyond-sota.md`.
- **Riscos/limitações:** o ganho de SNR atribuído à seleção vem da literatura e não foi medido no repositório. O BVP pressupõe geometria e portadora conhecidas. Sem uso ao vivo, a utilidade real não foi demonstrada.
- **Relevância para a plataforma (M06, M12, M01):** alta para M06 e M12. Espectrogramas e BVP sintéticos podem alimentar visualizações no dashboard e classificadores simples (scikit-learn), sem IA paga.

#### SV-04 — Detector heurístico de movimento e presença

- **O que faz:** calcula um escore de movimento composto (variância, correlação, fase e Doppler opcional) e decide presença com confiança suavizada. Suporta limiar adaptativo e calibração com sala vazia.
- **Como faz:** combina escores normalizados com pesos configuráveis, suaviza a confiança por EMA e compara com limiar fixo ou adaptado pela variância de baseline. Calcula variância temporal (histórico) e espacial (entre subportadoras).
- **Requisitos para implementar:**
  - Hardware: nenhum (sintético) ou qualquer fonte CSI.
  - Software: numpy; scikit-learn opcional para calibrar pesos.
  - Dados: features CSI e uma janela de sala vazia.
  - Competências: detecção por limiar, histerese/EMA, controle de falso positivo.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 18 testes, sem consumidor evidente no servidor ao vivo e sem acurácia medida. Caminhos: `v2/crates/wifi-densepose-signal/src/motion.rs`, `docs/ddd/signal-processing-domain-model.md`.
- **Riscos/limitações:** pesos heurísticos. Não distingue pessoa de animal ou de objeto em movimento. É sensível a deriva ambiental.
- **Relevância para a plataforma (M01, M02):** muito alta como base conceitual de M01 no modo `synthetic-native`: escore composto, EMA, histerese e calibração de sala vazia como serviço de domínio puro, testado contra a verdade do gerador.

#### SV-05 — Modelo de zona de Fresnel para respiração

- **O que faz:** modela a variação do sinal quando o deslocamento torácico cruza fronteiras de zonas de Fresnel entre TX e RX. Calcula comprimento de onda, raio da n-ésima zona e variações esperadas de fase e amplitude. Estima a confiança de respiração e a taxa por autocorrelação, e resolve inversamente a geometria TX–corpo–RX.
- **Como faz:** usa geometria elipsoidal clássica de Fresnel (família FarSense/Wi-Sleep). A taxa vem da autocorrelação da série de amplitude, e a geometria inversa é ajustada por solver.
- **Requisitos para implementar:**
  - Hardware: em dados reais, posições conhecidas de TX/RX e da portadora.
  - Software: numpy.
  - Dados: distâncias, frequência e série de amplitude.
  - Competências: propagação RF e fisiologia respiratória.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 10 testes, sem consumidores fora do arquivo. Caminhos: `v2/crates/wifi-densepose-signal/src/fresnel.rs`, `docs/ddd/signal-processing-domain-model.md`.
- **Riscos/limitações:** assume geometria estática e aproximadamente em linha de visada. Na prática, a posição do tórax é desconhecida e o multipercurso domina.
- **Relevância para a plataforma (M04, M08):** média-alta para o gerador sintético produzir respiração fisicamente plausível e para explicar ao operador por que a confiança cai conforme a posição.

#### SV-06 — Calibração de baseline de sala vazia (ADR-135) com runner de prova determinístico

- **O que faz:** captura estatísticas por subportadora de uma sala vazia (média e variância de amplitude, média circular e dispersão de fase), por tier PHY e com mínimo de quadros. Em runtime, gera uma pontuação de desvio, subtrai a baseline e a serializa em formato binário versionado. Um binário de prova regenera ou verifica o hash da saída sobre um canal sintético estacionário.
- **Como faz:** usa Welford online para amplitude e estatística circular para fase. O formato binário tem cabeçalho fixo e corpo sem ramificação de float, estável para SHA-256. O runner arredonda a saída de forma portátil, para lidar com a divergência de bibliotecas matemáticas entre plataformas. Ruído estacionário presente na captura passa a fazer parte do "vazio".
- **Requisitos para implementar:**
  - Hardware: em uso real, nó com tier PHY conhecido e sala vazia; nenhum no sintético.
  - Software: numpy, scipy.stats (circmean/circvar), SQLite (blob versionado) ou JSON canônico com hash.
  - Dados: centenas de quadros de sala vazia.
  - Competências: estatística online e circular, reprodutibilidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 10 testes no módulo e mais 32 de integração (sintético com semente fixa, round-trip, deriva), com hash esperado preenchido. A ADR-135 continua "Proposed". A detecção automática de deriva descrita na ADR (escore de deriva, evento e flag de obsolescência) não existe no código, como a guia de calibração admite. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/calibration.rs`, `v2/crates/wifi-densepose-signal/tests/calibration_synthetic.rs`, `calibration_roundtrip.rs`, `calibration_drift.rs`, `v2/crates/wifi-densepose-signal/src/bin/calibration_proof_runner.rs`, `archive/v1/data/proof/expected_calibration_features.sha256`, `docs/calibration-guide.md`, `docs/adr/ADR-135-empty-room-baseline-calibration.md`.
- **Riscos/limitações:** fundo que muda durante a captura enviesa a baseline. A obsolescência é tudo-ou-nada. Só foi provado com dados sintéticos.
- **Relevância para a plataforma (M16, M08, M01):** muito alta para M16. O fluxo "capturar sala vazia → baseline versionada com hash → desvio → recalibrar" cabe como caso de uso FastAPI persistido em SQLite/Alembic e rotulado L0, e ainda permite acrescentar o escore de deriva que o RuView não implementou. Ver também SS-06 e SV-20.

#### SV-07 — Estimação da CIR (resposta ao impulso do canal) por recuperação esparsa (ADR-134)

- **O que faz:** converte CSI de frequência em CIR no domínio do atraso, isolando taps de multipercurso. Rejeita fase não sanitizada (guarda contra "taps fantasmas" por variância circular), contagem de subportadoras inconsistente e quadros só de amplitude. Pode servir de gate opcional na fusão multiestática.
- **Como faz:** resolve LASSO com matriz de sensoriamento sub-DFT. O warm-start é por mínimos quadrados regularizados (Tikhonov) via série de Neumann, com refinamento por ISTA (limiarização suave). A guarda de fase usa a variância circular de Mardia, corrigida na ADR-154 (antes usava variância linear).
- **Requisitos para implementar:**
  - Hardware: CSI com fase coerente e sanitizada; com 20 MHz a resolução de atraso fica na ordem de dezenas de ns.
  - Software: numpy (ISTA) ou scikit-learn (Lasso, OMP).
  - Dados: CSI complexo e índices das subportadoras ativas.
  - Competências: sensoriamento compressivo, otimização convexa, canal OFDM.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 16 testes no módulo e 16 de integração com fixtures sintéticas por tier, hash esperado preenchido. O comentário do runner de prova ainda diz que a CIR não está implementada, o que está desatualizado. O limiar da guarda é declarado dependente de dados. A ADR-134 está "Proposed". Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/cir.rs`, `v2/crates/wifi-densepose-signal/tests/cir_synthetic.rs`, `cir_pipeline.rs`, `cir_ghost_taps.rs`, `v2/crates/wifi-densepose-signal/src/bin/cir_proof_runner.rs`, `archive/v1/data/proof/expected_cir_features.sha256`, `docs/adr/ADR-134-csi-to-cir-time-domain-multipath.md`.
- **Riscos/limitações:** resolução de atraso grosseira em ambientes internos. Limiar não calibrado. Sensibilidade a fase residual.
- **Relevância para a plataforma (M12, M14, M08):** média. O gerador pode sintetizar um canal multi-tap conhecido para o laboratório recuperar, medindo o erro contra verdade conhecida. A variante treinável (LISTA) seria expansão de IA e deve ficar PLANNED.

#### SV-08 — Modelo de campo persistente (modos via SVD) e contagem de ocupação por autovalores (ADR-030)

- **O que faz:** aprende a baseline eletromagnética da sala vazia (duração mínima e janelas completas) e a decompõe em modos ambientais. Em runtime, separa deriva ambiental (projeção nos modos) de perturbação corporal (resíduo), verifica correspondência com a sala vazia, estima ocupação contando autovalores significativos, exporta snapshots e verifica o frescor da calibração.
- **Como faz:** média por enlace com acumulador de Welford combinável e SVD da covariância. A contagem compara autovalores com o limiar de Marchenko–Pastur (teoria de matrizes aleatórias), ancorado na energia residual de sala vazia. Sem a feature de álgebra linear (BLAS), a estimativa devolve "não calibrado".
- **Requisitos para implementar:**
  - Hardware: vários enlaces/subportadoras e minutos de sala vazia para dados reais.
  - Software: numpy.linalg (svd, eigh); OpenBLAS é livre.
  - Dados: minutos de CSI vazio e janelas recentes.
  - Competências: álgebra linear, PCA/SVD, matrizes aleatórias.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 34 testes, incluindo "só ruído conta zero" e "vazio deslocado conta ≥ 1". Integrado ao servidor como complemento da heurística de contagem. A ADR-030 está "Proposed", e o benchmark com autovalores não compila no host Windows (BLAS). Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/field_model.rs`, `v2/crates/wifi-densepose-sensing-server/src/field_bridge.rs`, `docs/adr/ADR-030-ruvsense-persistent-field-model.md`.
- **Riscos/limitações:** sensível a correlações não corporais e ao número de enlaces. Baseline obsoleta gera falso positivo. O build com BLAS no Windows é frágil.
- **Relevância para a plataforma (M02, M08, M14, M01):** alta. O gerador pode criar K perturbações sobre modos ambientais e numpy estima K pelo limiar de Marchenko–Pastur, avaliado contra a verdade, em Python puro e sem problemas de build. Ver também SS-04.

#### SV-09 — Pipeline multiestático RuvSense: multibanda, alinhamento de fase, fusão, coerência e gate (ADR-029)

- **O que faz:**
  - Funde quadros de salto de canal num snapshot wideband virtual e remove o offset de fase do oscilador por canal.
  - Funde N nós ponderando por atenção: amplifica energia correlacionada entre nós, típica de corpo, e suprime energia de nó único, típica de multipercurso.
  - Separa pessoas por min-cut.
  - Calcula coerência por enlace contra um template e aplica um gate de quatro decisões (aceitar, só predizer, rejeitar, recalibrar) que controla a atualização do Kalman a jusante.
- **Como faz:** o alinhamento usa componentes estáticos e solver iterativo. A fusão usa atenção cruzada com softmax, consenso entre nós e partição de grafo de correlação. A coerência é uma média de verossimilhanças gaussianas por subportadora ponderada pela variância inversa. O gate combina o escore com um contador de obsolescência, e o gate de CIR é opcional (para testes A/B).
- **Requisitos para implementar:**
  - Hardware: vários nós com salto de canal e sincronização aproximada; nenhum no sintético.
  - Software: numpy (softmax), networkx/scipy.
  - Dados: quadros sincronizados de vários nós e canais e um template por enlace.
  - Competências: fusão de sensores, sistemas multiestáticos, grafos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: multistatic 47, coherence 23, coherence_gate 18, multiband 16, phase_align 15, mod 14. O fusor é usado pelo servidor e pelo motor governado; o alinhamento de fase não tem consumidor externo. O benchmark de desempenho da atenção (sub-microssegundo) foi medido. A ADR-029 está "Proposed". Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/mod.rs`, `multiband.rs`, `phase_align.rs`, `multistatic.rs`, `coherence.rs`, `coherence_gate.rs`, `v2/crates/wifi-densepose-sensing-server/src/multistatic_bridge.rs`, `v2/crates/wifi-densepose-engine/src/lib.rs`, `docs/adr/ADR-029-ruvsense-multistatic-sensing-mode.md`.
- **Riscos/limitações:** depende de pareamento de quadros, que se degrada em malhas fragmentadas (ver SV-23). Limiares não calibrados. Acoplamento a crates externas da mesma autoria.
- **Relevância para a plataforma (M14, M01, M02, M12):** média-alta. O gate de quatro decisões é um padrão excelente para M15/M14, porque explica por que uma medição foi rejeitada. A fusão multi-nó pode ser simulada com N nós virtuais.

#### SV-10 — Rastreador de pose de 17 keypoints com filtro de Kalman e re-identificação

- **O que faz:** rastreia várias pessoas como esqueletos COCO-17 persistentes (posição e velocidade por keypoint), com ciclo de vida da trilha (tentativa, ativa, perdida, encerrada). Associa detecções às trilhas por custo combinado (Mahalanobis mais similaridade cosseno de embedding), aplica restrições de esqueleto e atenção temporal.
- **Como faz:** predict/update de Kalman por keypoint com matrizes fixas na pilha. O nascimento da trilha exige acertos consecutivos. A atribuição usa matcher baseado em min-cut, e uma janela de re-ID recupera cruzamentos.
- **Requisitos para implementar:**
  - Hardware: nenhum (sintético); com dados reais, depende de um estimador de pose upstream.
  - Software: filterpy (MIT) ou numpy, scipy.optimize.linear_sum_assignment.
  - Dados: detecções de 17 pontos e embeddings opcionais.
  - Competências: rastreamento multi-alvo, Kalman, associação de dados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 38 testes, integrado ao servidor via ponte. O benchmark mede latência (centenas de ns), não precisão; as metas de erro citadas no cabeçalho não são medidas. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/pose_tracker.rs`, `v2/crates/wifi-densepose-sensing-server/src/tracker_bridge.rs`, `v2/crates/wifi-densepose-signal/benches/dsp_perf_bench.rs`.
- **Riscos/limitações:** a qualidade depende da pose upstream, que não é comprovada. Embeddings de re-ID são biometria. O modelo de velocidade constante falha em quedas.
- **Relevância para a plataforma (M11, M03, M02):** alta para M03, já que o ciclo de vida da trilha gera eventos de entrada e saída. A re-ID deve ficar BLOCKED, usando IDs anônimos de trilha.

#### SV-11 — Qualidade de fusão com referências de evidência, contradições e coordenador de array (ADR-137/138)

- **O que faz:** cada estágio de fusão emite um escore de qualidade junto com o payload, listando a evidência que justificou a fusão e as discordâncias toleradas (flags de contradição). Essas contradições **rebaixam obrigatoriamente** a classe de privacidade a jusante. O coordenador de array barra nós com geometria insuficiente ou relógio de baixa qualidade e projeta "evidência direcional", em vez de decisões de pose.
- **Como faz:** tipos fortes (referência de evidência, contradição, ID de calibração, família) e um trait comum de "pontuável por qualidade" permitem roteamento, gate e log uniformes no motor de streaming.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: pydantic, enum, SQLite para trilha de auditoria.
  - Dados: metadados de proveniência e qualidade de relógio/geometria.
  - Competências: governança de dados, privacy by design.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 5 testes por módulo, consumidos pelo motor governado e pelo servidor. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/fusion_quality.rs`, `array_coordinator.rs`, `v2/crates/wifi-densepose-engine/src/lib.rs`, `docs/adr/ADR-137-fusion-engine-quality-scoring-evidence.md`, `docs/adr/ADR-138-linkgroup-array-coordinator-clock-quality.md`.
- **Riscos/limitações:** regras de rebaixamento dependem de ADRs externas; escores não calibrados contra resultados reais.
- **Relevância para a plataforma (M15, M14):** muito alta. A regra "todo resultado carrega escore, evidências e contradições, e uma contradição rebaixa a autoridade" cabe no contrato 2.0.0 como campos opcionais aditivos.

#### SV-12 — Gestos por DTW e sinais antecipatórios de intenção

- **O que faz:** classifica gestos (acenar, apontar, chamar, empurrar, círculo e personalizados) comparando séries de perturbação por pessoa com uma biblioteca de templates. Há variantes com DTW em cache, LCS e distância de edição. O detector de intenção identifica ajustes posturais antecipatórios pela velocidade e aceleração na trajetória de embeddings.
- **Como faz:** normalização, projeção em componentes principais e DTW com banda Sakoe–Chiba, classificando pelo template mais próximo abaixo de um limiar. A intenção dispara quando a aceleração é alta com velocidade ainda baixa.
- **Requisitos para implementar:**
  - Hardware: CSI multi-enlace com resolução por pessoa (real); nenhum no sintético.
  - Software: dtaidistance (Apache-2.0) ou tslearn (BSD), scikit-learn (PCA).
  - Dados: templates de gestos rotulados.
  - Competências: séries temporais, reconhecimento de padrões, biomecânica.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: gesture 18, temporal_gesture 16, intention 14. É biblioteca sem consumidor. A intenção é hipótese de pesquisa sem dados. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/gesture.rs`, `temporal_gesture.rs`, `intention.rs`.
- **Riscos/limitações:** gestos "através de parede" não demonstrados. A intenção gera inferência comportamental sensível e falsos alarmes.
- **Relevância para a plataforma (M06, M13, M07):** média. DTW sobre gestos sintéticos é um bom demonstrador de "gesto → hook local" (M13). A intenção deve ficar PLANNED/BLOCKED. Ver também EH-03.

#### SV-13 — Continuidade de identidade entre cômodos e detecção adversarial (anti-spoofing)

- **O que faz:**
  - **Cross-room:** cada cômodo tem uma impressão eletromagnética. Trilhas perdidas perto de uma fronteira são comparadas por cosseno com novas trilhas no cômodo adjacente dentro de uma janela temporal, e as transições vão para um grafo append-only, sem imagem.
  - **Adversarial:** identifica sinais fisicamente impossíveis, como injeção que afeta um único enlace (um corpo real perturba todos os enlaces que atravessa), violação dos modos do campo, descontinuidade temporal e energia incompatível com o número de corpos.
- **Como faz:** limiar de similaridade com janela de tempo, combinado com verificações de consistência multi-enlace, projeção nos modos, continuidade temporal e conservação de energia. A ADR-154 corrige um desvio por NaN.
- **Requisitos para implementar:**
  - Hardware: malha multi-enlace e multi-cômodo (real).
  - Software: numpy, pydantic.
  - Dados: embeddings por cômodo e cenários de injeção.
  - Competências: segurança de sensores, detecção de anomalias, privacidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: cross_room 15, adversarial 20. Nenhum consumidor externo e nenhuma avaliação adversarial real. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/cross_room.rs`, `adversarial.rs`, `docs/adr/ADR-154-signal-dsp-beyond-sota.md`.
- **Riscos/limitações:** continuidade de identidade equivale a re-identificação, com risco de vigilância. Limiares heurísticos.
- **Relevância para a plataforma (M15, M03, M08, M14):** a detecção adversarial é muito relevante para M15: verificação de plausibilidade física de entradas, testada com injeção de falhas no gerador. O cross-room deve ficar BLOCKED; no máximo, contagens agregadas anônimas de transição entre cômodos.

#### SV-14 — Tomografia RF grosseira, VoxelMap temporal bayesiano e RF-SLAM

- **O que faz:** a tomografia gera um volume 3D de baixa resolução invertendo atenuações por enlace (Radio Tomographic Imaging). Um rastreador de evolução mantém baselines por enlace e detecta change-points cruzados. O VoxelMap acumula evidência por voxel com log-odds, protegido por um gate de privacidade (completo, anônimo, restrito). O RF-SLAM v1 trabalha com mapa fixo; a v2 (descoberta de refletores) está desligada até haver dataset multi-dia.
- **Como faz:** grade de voxels com pesos de caminho e inversão esparsa por ISTA com L1. Welford e log-odds por voxel. Associação por raio e classificação de refletores.
- **Requisitos para implementar:**
  - Hardware: muitos enlaces com geometria conhecida (real); nenhum no sintético.
  - Software: numpy, scipy.sparse; three.js para visualização.
  - Dados: atenuação por enlace, posições de nós e dataset multi-dia para descoberta.
  - Competências: problemas inversos, grids de ocupação bayesianos, SLAM.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: tomography 12, evolution 7, rf_slam 8. Evolução e SLAM são usados no motor; a tomografia só em benchmark; a descoberta está bloqueada por falta de dados. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/tomography.rs`, `evolution.rs`, `rf_slam.rs`, `docs/adr/ADR-142-evolution-tracker-temporal-voxel-aggregation.md`, `docs/adr/ADR-143-rf-slam-reflector-discovery-anchor-learning.md`.
- **Riscos/limitações:** resolução espacial muito baixa com poucos enlaces. O mapa de ocupação é dado sensível.
- **Relevância para a plataforma (M14, M02, M08, M15):** alta para M14 sintético (grid log-odds e ISTA em numpy, visualizados no Next.js). O gate de privacidade por voxel (completo, anônimo, só histograma) é diretamente adotável em M15.

#### SV-15 — Deriva biomecânica longitudinal e análise de atratores

- **O que faz:** mantém baselines biofísicas por pessoa ao longo de dias (simetria de marcha, estabilidade, regularidade respiratória, microtremor, atividade). Detecta deriva sustentada só depois de um mínimo de dias e com desvio persistente, e produz relatórios com métricas e desvios, **nunca linguagem diagnóstica**. Também faz embedding de espaço de fase (Takens), estima o expoente de Lyapunov e classifica o atrator.
- **Como faz:** Welford com histórico completo e regras de persistência temporal. Os atratores dependem de uma crate externa.
- **Requisitos para implementar:**
  - Hardware: monitoramento contínuo por semanas (real).
  - Software: numpy, nolds (MIT), SQLite.
  - Dados: métricas diárias por pessoa.
  - Competências: estatística longitudinal, dinâmica não linear, ética em saúde.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: longitudinal 23, attractor_drift 17. O servidor só usa o histórico de embeddings, e não há dado longitudinal real. Caminhos: `v2/crates/wifi-densepose-signal/src/ruvsense/longitudinal.rs`, `attractor_drift.rs`, `v2/crates/wifi-densepose-sensing-server/src/main.rs`.
- **Riscos/limitações:** depende de pose e vitais não validados. Perfis por pessoa implicam identificação. Lyapunov é instável com séries curtas.
- **Relevância para a plataforma (M09, M04, M06, M15):** média. As regras "só métricas e desvios, nunca diagnóstico" e "mínimo de dias antes de alertar" são diretamente adotáveis como política de produto.

#### SV-16 — Pipeline de sinais vitais ADR-021 (pré-processador EMA, respiração e frequência cardíaca)

- **O que faz:** extrai taxa respiratória e frequência cardíaca de CSI multi-subportadora com status Valid, Degraded, Unreliable ou Unavailable. A respiração se reinicia quando a estimativa sai da banda, para evitar travar num valor antigo depois que a pessoa sai. A FC rejeita valores fora da banda fisiológica e tem a confiança limitada pela evidência do primeiro estágio, para que filtragem extra não promova ruído a "válido".
- **Como faz:**
  - EMA por subportadora remove a componente estática.
  - Ressonador IIR de 2ª ordem na banda pública de 0,1–0,5 Hz, com contagem de cruzamentos por zero, para respiração.
  - Ressonadores em cascata na banda de 0,8–2,0 Hz para atenuar vazamento respiratório, com pico de autocorrelação e ponderação por coerência de fase, para FC.
  - Robustez a NaN/Inf.
- **Requisitos para implementar:**
  - Hardware: CSI multi-subportadora estável com sujeito parado e próximo (real); nenhum no sintético.
  - Software: scipy.signal (butter, sosfilt, welch, find_peaks), numpy.correlate.
  - Dados: resíduos por subportadora e janelas de 15–30 s.
  - Competências: filtragem digital, estimação espectral, fisiologia cardiorrespiratória.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Contagem de testes: heartrate 20, breathing 18, preprocessor 7, types 6, incluindo regressões nomeadas por issue. O README admite que não há validação em CSI real nem clínica, e a ADR-021 está "Partially Implemented". O crate só é consumido pelo kernel e pelos bindings Python. **O servidor ao vivo usa outra implementação (SS-05) e o firmware, uma terceira (FW-02).** Caminhos: `v2/crates/wifi-densepose-vitals/src/preprocessor.rs`, `breathing.rs`, `heartrate.rs`, `types.rs`, `v2/crates/wifi-densepose-vitals/README.md`, `docs/adr/ADR-021-vital-sign-detection-rvdna-pipeline.md`.
- **Riscos/limitações:** FC por CSI comercial é experimental, porque o sinal cardíaco é muito mais fraco que o respiratório. O comentário que chama "Valid" de grau clínico contradiz os avisos não clínicos.
- **Relevância para a plataforma (M04, M05):** muito alta para o modo `synthetic-native`. O gerador injeta tons respiratório e cardíaco conhecidos com ruído e harmônicos, e um pipeline scipy próprio os recupera com métrica de erro. A saída deve permanecer L0/IMPLEMENTED_SYNTHETIC. Ver também SS-05, FW-02 e PY-02.

#### SV-17 — Detecção de anomalias vitais e armazenamento de séries

- **O que faz:** gera alertas de apneia, taquipneia, bradipneia, taquicardia, bradicardia e mudança súbita, com severidade de 0 a 1 e descrição. Armazena leituras em ring buffer com estatísticas (médias, extremos, fração válida).
- **Como faz:** z-score sobre Welford e janela recente, com remoção O(1) do mais antigo.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, SQLite/Alembic; ruptures (BSD-2) para change-point/CUSUM, se desejado.
  - Dados: série de leituras com status.
  - Competências: detecção estatística de anomalias, comunicação de risco não clínica.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: anomaly 11, store 9. A ADR-021 promete CUSUM e armazenamento em camadas com TTL, mas o código tem só z-score e ring buffer. Caminhos: `v2/crates/wifi-densepose-vitals/src/anomaly.rs`, `store.rs`.
- **Riscos/limitações:** z-score adaptativo pode normalizar uma condição persistente. Rótulos clínicos sugerem diagnóstico.
- **Relevância para a plataforma (M10, M04, M05, M09):** alta para M10 como demonstrador sintético de "evento sinalizado" (pausas injetadas), nunca como diagnóstico, com retenção governada.

#### SV-18 — Avaliação contra referência (ground truth) com graduação de evidência imposta (ADR-293)

- **O que faz:** ingere uma série de referência (cinta torácica, oxímetro, ECG) a partir de CSV não confiável, com erros por linha e limites. Alinha estimativa e referência e devolve os parâmetros de alinhamento sem aplicá-los silenciosamente. Calcula concordância: pares, cobertura com lacunas, MAE, RMSE, viés, limites de Bland–Altman e porcentagem dentro de tolerância. Exige escopo de sessão (sujeitos, movimento, LOS/NLOS, distância). O grau "Measured" só é construível com pares, cobertura mínima e comando reprodutor.
- **Como faz:** o offset sai do máximo da correlação cruzada normalizada numa janela de lag limitada, com ajuste linear opcional de deriva de relógio. A regra de evidência está no construtor do tipo.
- **Requisitos para implementar:**
  - Hardware: para medição real, um dispositivo de referência de consumo e um nó CSI; no sintético, a própria verdade do gerador.
  - Software: numpy, scipy.stats, pydantic, pandas opcional.
  - Dados: CSV de referência e metadados de escopo.
  - Competências: concordância de métodos (Bland–Altman), metrologia.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 38 testes (parsing hostil, offsets conhecidos, fixture calculada à mão). Nenhuma sessão MEASURED publicada. Caminhos: `v2/crates/wifi-densepose-vitals/src/groundtruth.rs`, `docs/adr/ADR-293-vitals-ground-truth-rig.md`.
- **Riscos/limitações:** concordância com dispositivo de consumo é evidência de engenharia, não validação médica.
- **Relevância para a plataforma (M15, M04, M05, M16):** muito alta. "Grau imposto no construtor" corresponde ao `evidence_level` do produto: o L0 só é promovível com reprodutor e cobertura. O mesmo motor avalia o gerador contra a própria verdade. Ver também GV-09.

#### SV-19 — Kernel portátil de vitais com ABI JSON delimitada (ruview-kernel)

- **O que faz:** expõe o pipeline de vitais por uma única função texto→texto (operação mais JSON → envelope de sucesso/erro). As operações cobrem build info, validação, análise em lote, síntese, sessões de streaming e caminho binário. Todas as entradas são tratadas como não confiáveis, com limites. Inclui gerador sintético determinístico com tons conhecidos. O transporte WASM não importa nada do host, e há um backend napi opcional. O loader JS recusa módulos com imports e verifica `SHA256SUMS` com falha fechada.
- **Como faz:** um núcleo seguro compartilhado pelos dois transportes, de modo que a paridade é propriedade do transporte. Alocação explícita, PRNG bit-idêntico entre alvos e caminho binário bit-exato.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Python puro no FastAPI; Pyodide/WebAssembly opcional.
  - Dados: quadros CSI ou parâmetros de síntese.
  - Competências: design de ABI, cadeia de suprimentos, determinismo numérico.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 7 testes Rust de ABI e cerca de 17 `node:test`. Os artefatos wasm/nativos não estão commitados. O ganho do caminho binário foi medido num único host Linux (desempenho). A ADR-368 está "proposed". Caminhos: `v2/crates/ruview-kernel/src/lib.rs`, `wasm_abi.rs`, `v2/crates/ruview-kernel/tests/abi.rs`, `v2/crates/ruview-kernel-napi/src/lib.rs`, `harness/ruview-kernel/README.md`, `harness/ruview-kernel/test/security.test.mjs`, `docs/adr/ADR-368-ruview-kernel-wasm-napi-npm.md`.
- **Riscos/limitações:** herda as limitações dos vitais. Checksums só protegem com fonte confiável. O napi tem autoridade total do processo.
- **Relevância para a plataforma (M12, M04, M05, M15):** alta como padrão. Um núcleo de cálculo puro, determinístico e limitado, com envelope de erro estruturado, combina com o domínio puro de Acquisition. Reimplementar em Python, sem depender do pacote npm.

#### SV-20 — Calibração por sala e banco de especialistas estatísticos (ADR-151)

- **O que faz:** implementa o fluxo "ensine a sala antes do modelo": baseline, âncoras, extração, treino, inferência.
  - Matrícula guiada com oito âncoras curtas (vazio, em pé, sentado, deitado, respiração lenta e normal, movimento pequeno, postura de sono), gate de qualidade e repetição de âncoras reprovadas, em sessão event-sourced.
  - Especialistas pequenos por sinal (respiração, batimento experimental, inquietação, postura, presença, anomalia).
  - Banco versionado por sala ligado à baseline, marcado STALE quando a baseline muda.
  - Runtime com regras de honestidade: a anomalia veta positivos, ausência de presença anula sinais e banco STALE sinaliza tudo. Na fusão multiestática, presença é OR e o veto de qualquer nó prevalece.
- **Como faz:** gate de presença por z-score contra a baseline e de movimento pela variação quadro a quadro do desvio. Especialistas por limiar, protótipo ou periodicidade (não são redes). Uma CLI encadeia as etapas.
- **Requisitos para implementar:**
  - Hardware: nó CSI e sala controlável (real); nenhum no sintético.
  - Software: FastAPI, Next.js (assistente), numpy/scipy, SQLite/Alembic.
  - Dados: baseline e capturas curtas por âncora.
  - Competências: desenho de onboarding, controle de qualidade de dados, modelos leves.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Contagem de testes: specialist 10, extract 9, anchor 8, bank 7, enrollment 7, multistatic 7, runtime 4, além de `tests/full_loop.rs` em CSI sintético. A guia admite que o ciclo nunca rodou ponta a ponta em hardware, que não distingue pet de pessoa e que a obsolescência é tudo-ou-nada. Caminhos: `v2/crates/wifi-densepose-calibration/src/anchor.rs`, `enrollment.rs`, `extract.rs`, `specialist.rs`, `bank.rs`, `runtime.rs`, `multistatic.rs`, `v2/crates/wifi-densepose-calibration/tests/full_loop.rs`, `docs/calibration-guide.md`, `docs/adr/ADR-151-room-calibration-specialist-training.md`.
- **Riscos/limitações:** risco de sobreajuste com poucos minutos de captura. Âncoras parciais removem especialistas silenciosamente.
- **Relevância para a plataforma (M16, M01, M04, M05, M09, M12):** muito alta para M16: assistente de âncoras com gate e repetição, eventos auditáveis, banco versionado com STALE e regras de veto, tudo com âncoras sintéticas L0.

#### SV-21 — Certificado de impressão digital da sala e geometria de transceptores (ADR-301 / ADR-152)

- **O que faz:** emite um certificado portátil, assinado, versionado e com validade, que afirma qual é a sala, quando foi medida e qual evidência mostra que ela continua a mesma. O certificado vincula uma impressão estatística de tamanho fixo a espaço, sensor assinante, versão, expiração, nível de evidência (L0 sintético a L5) e hash. O mint recusa rotular caracterização sintética como medida e limita a autocalibração a um nível baixo. O status é tipado (válido, expirado, adulterado, deriva além do envelope). A renovação é append-only. Há um embedding de geometria determinístico, invariante à ordem dos nós e total (entradas absurdas viram "não medido").
- **Como faz:** traits de assinador/verificador substituíveis. A implementação atual é um MAC com segredo compartilhado, declarado como placeholder. A deriva pequena é absorvida e a grande invalida.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: PyNaCl ou cryptography (Ed25519), pydantic, SQLite.
  - Dados: impressão estatística e geometria opcional.
  - Competências: criptografia aplicada, versionamento imutável.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: certificate 15, geometry_embedding 8, geometry 3. É consumido por `ruview-certify` e `ruview-ood`. A assinatura de produção não existe, e o MAC placeholder usa comparação não constante no tempo (admitido no código). Caminhos: `v2/crates/wifi-densepose-calibration/src/certificate.rs`, `geometry.rs`, `geometry_embedding.rs`, `docs/adr/ADR-301-automatic-domain-calibration.md`, `docs/adr/ADR-152-wifi-pose-sota-2026-intake.md`.
- **Riscos/limitações:** o MAC simétrico não dá proveniência real. Envelope não calibrado. Gestão de chaves fora de escopo.
- **Relevância para a plataforma (M15, M16, M08):** muito alta. Certificados de sala com nível de evidência, expiração, status tipado e renovação append-only, assinados com Ed25519 de verdade, com a regra "sintético nunca vira medido" imposta em código. Ver também GV-05 e WM-20.

#### SV-22 — Avaliação física de pose com restrições cinemáticas e correção autorizada (ADR-323)

- **O que faz:** recebe uma observação de pose métrica e sempre devolve uma avaliação tipada (disposição ou abstenção), com resíduos por restrição, resumo de intervenção, hipóteses de contato do pé e proveniência.
  - Restrições: comprimento ósseo por trilha anônima, limites articulares amplos, plano do chão, contato do pé e coerência temporal.
  - Modos: de desligado/auditoria até correção. A correção só é aplicada com recibo de autorização vinculado ao hash exato da configuração.
  - Há auditoria opcional de dinâmica articulada (só pontua) e um resíduo aprendido opcional com teto de correção.
- **Como faz:** projetor do tipo position-based dynamics ponderado por covariância e determinístico, com replay verificado contra hashes golden e um alvo de fuzzing.
- **Requisitos para implementar:**
  - Hardware: nenhum (GPU só para o backend aprendido).
  - Software: numpy; PyBullet opcional.
  - Dados: poses 3D métricas com covariância e chão calibrado.
  - Competências: cinemática humana, otimização com restrições, segurança por autorização.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 36 testes em 9 arquivos, incluindo propriedades (confiança nunca aumenta; invariância a translação e espelhamento; pose prona não é forçada a ficar em pé). É consumido pelo servidor. A ADR-323 está "Proposed" e o runtime fica em auditoria. Caminhos: `v2/crates/wifi-densepose-physics/src/engine.rs`, `constraints/mod.rs`, `projector/pbd.rs`, `learned/mod.rs`, `dynamics/mod.rs`, `v2/crates/wifi-densepose-physics/tests/properties.rs`, `floor_and_fall.rs`, `v2/crates/wifi-densepose-physics/fuzz/fuzz_targets/pose_frame.rs`, `v2/crates/wifi-densepose-sensing-server/src/pose_physics.rs`, `docs/adr/ADR-323-native-rust-physics-constrained-pose-refinement.md`.
- **Riscos/limitações:** corrige uma pose sem acurácia comprovada. Correção agressiva pode mascarar quedas. O resíduo aprendido é expansão de IA.
- **Relevância para a plataforma (M11, M07, M15):** média-alta como princípio de governança ("auditar por padrão e corrigir só com autorização") e para auditar poses sintéticas. O backend aprendido fica PLANNED.

#### SV-23 — Seleção de quadros CSI para fusão entre nós: experimento medido em frota real

- **O que faz:** compara três gates de limitação de taxa de quadros (intervalo por nó, janela de relógio de malha e módulo do número de sequência 802.11) e suas combinações. A métrica é a fração de transmissões capturadas por dois ou mais nós, pré-condição para fusão entre receptores.
- **Como faz:** experimento fatorial com a frota inteira por braço, blocos em quadrado latino contra deriva lenta, leitura de volta para verificar que o gate está ativo, razões sobre contadores diferenciados e piso de ruído por rodada nula de várias horas. Resultado relatado: o gate por sequência dobrou aproximadamente o pareamento (com menor taxa bruta); o alinhamento por relógio ficou no ruído, em parte porque nós sem sincronização caíram silenciosamente no gate por tempo. Uma previsão errada está documentada.
- **Requisitos para implementar:**
  - Hardware: frota de nós CSI e transmissores (real).
  - Software: orquestração em Python e contadores no firmware.
  - Dados: contadores por nó e identificadores de transmissão.
  - Competências: desenho experimental (fatorial, quadrado latino, piso de ruído), Wi-Fi.
- **Evidência e maturidade:** `DOC_ONLY` / `REAL_HARDWARE_EVIDENCE`. 9 ESP32-C6 numa única casa, 3 blocos e 12 braços. Mede só pareamento e declara explicitamente que não é afirmação de acurácia. Caminhos: `docs/csi-frame-selection-measured.md`, `firmware/esp32-csi-node/run_arms.py`, `firmware/esp32-csi-node/main/c6_sync_espnow.c`.
- **Riscos/limitações:** um único ambiente e um único período caracterizado. Malhas fragmentadas degradam silenciosamente.
- **Relevância para a plataforma (M12, M14, M16):** alta como metodologia: piso de ruído antes de comparar, verificação de que a configuração foi aplicada, contadores diferenciados e blocos balanceados. Isso vale para qualquer A/B do gerador e para o simulador de frota. Ver também FW-09.

### 4.2 Servidor de sensoriamento, engine, CLI e APIs

**Escopo.** A área tem três crates. `wifi-densepose-sensing-server` soma cerca de 60 mil linhas, das quais cerca de 17 mil estão em `src/main.rs`; é um binário Axum com três listeners (HTTP, WebSocket dedicado e UDP). `wifi-densepose-engine` é a raiz de composição do "caminho governado". `wifi-densepose-cli` reúne login, calibração, matrícula por sala e MAT. A contagem estática deu cerca de 989 funções de teste no `src` do servidor (208 em `main.rs`), 59 testes de integração, 36 no engine e 38 na CLI, todos sintéticos. Nenhuma inferência de modelo roda no loop ao vivo.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| SS-01 | Ingestão UDP multiprotocolo e endurecimento do plano de dados | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M12, M15, M16 |
| SS-02 | Resolução de fonte, simulador e máquina de estados de proveniência | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16 |
| SS-03 | Extração de features, presença/movimento e fusão determinística de sala | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M06, M08 |
| SS-04 | Contagem de pessoas (heurística, min-cut, eigenmodos) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M02, M03, M08 |
| SS-05 | Vitais por FFT com gate de publicação e abstenção | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M04, M05, M15 |
| SS-06 | Calibração de sala vazia e baseline de bootstrap | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15, M08 |
| SS-07 | Motor de streaming governado e ponte ao vivo | PARTIAL | UNIT_TESTS_ONLY | M14, M15, M08 |
| SS-08 | Pose COCO-17 derivada do sinal, rastreamento, pico de campo e física | PARTIAL | SYNTHETIC_OR_SIMULATED | M11, M14, M15 |
| SS-09 | Contêiner de modelos RVF e gestão de modelos | PARTIAL | UNIT_TESTS_ONLY | M12 |
| SS-10 | Treinamento in-server, offline, contrastivo e índice de fingerprints | PARTIAL | SYNTHETIC_OR_SIMULATED | M12, M06, M08, M11 |
| SS-11 | Classificador adaptativo de atividade por ambiente | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M06, M08, M16 |
| SS-12 | Gravação JSONL com marca d'água sintética e redação | PARTIAL | UNIT_TESTS_ONLY | M12, M15 |
| SS-13 | Streaming WebSocket e tap de introspecção | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M06, M15 |
| SS-14 | Autenticação/autorização da API e endurecimento HTTP | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16 |
| SS-15 | Modo de privacidade fail-closed | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M04, M05, M09, M11 |
| SS-16 | Home Assistant via MQTT com auto-discovery | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13 |
| SS-17 | Primitivas semânticas de automação | PARTIAL | UNIT_TESTS_ONLY | M09, M07, M10, M13, M06 |
| SS-18 | Ponte Matter (scaffolding sem SDK) | STUB | UNIT_TESTS_ONLY | M13 |
| SS-19 | Superfície RuField (eventos Ed25519 com gate de egress) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M15 |
| SS-20 | Fontes alternativas: telemetria de fornecedores RF e RSSI do host | PARTIAL | UNIT_TESTS_ONLY | M08, M14, M01 |
| SS-21 | Malha multi-nó: estado, sincronização, posições, mDNS | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M02, M16, M14 |
| SS-22 | Observabilidade, endpoints operacionais e registro de borda | PARTIAL | UNIT_TESTS_ONLY | M15, M16 |
| SS-23 | CLI `wifi-densepose` (login, Spaces, calibração, matrícula, MAT) | PARTIAL | UNIT_TESTS_ONLY | M16, M12, M02, M08 |
| SS-24 | Empacotamento Docker com postura fail-closed | IMPLEMENTED_UNTESTED | UNCLEAR | M16, M15 |

#### SS-01 — Ingestão UDP multiprotocolo de CSI/rádio e endurecimento do plano de dados

- **O que faz:** recebe datagramas de nós sensores e identifica o tipo pelo identificador do cabeçalho. Os tipos aceitos são: CSI ESP32 (I/Q por antena/subportadora, RSSI, ruído, tipo de PPDU, flags), vitais de borda, vitais fundidos, eventos de módulos WASM, sincronização de malha, CSI MIMO MediaTek, CSI Qualcomm, CSI Realtek 1x1 e radar Realtek. Mantém estado por nó, restringe quem injeta quadros e permite duplicar datagramas para consumidores locais (tee).
- **Como faz:** uma tarefa assíncrona dona do socket aplica allowlist de IP/CIDR (loopback sempre admitido) e conta descartes, com log em backoff. O tee é não bloqueante e só para loopback. Parsers ordenados por tipo tratam colisões históricas de identificadores. Um gate por nó rejeita mudança de grade de subportadoras. Para MediaTek, há ring buffer limitado por dispositivo, classificador heurístico rotulado como não validado e índice de atividade por EMA rápida/lenta. O bind padrão é loopback, e bind roteável sem allowlist é recusado na partida (salvo override explícito).
- **Requisitos para implementar:**
  - Hardware: nós ESP32-S3/C6 ou roteadores MediaTek para dados reais; nenhum em desenvolvimento.
  - Software: socket UDP assíncrono, parsers binários e ring buffers.
  - Dados: quadros reais ou fixtures binárias sintéticas.
  - Competências: formatos CSI 802.11 (HT/HE), redes assíncronas, modelagem de ameaças.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Há testes dos parsers em `main.rs` (colisão de identificadores, subportadoras de 16 bits, integridade de vitais de borda). Outros arquivos: udp_bind 13, udp_tee 6, mediatek_csi_ring 13, mediatek_heuristic 10, mediatek_activity 12. `tests/multi_node_test.rs` envia quadros sintéticos. A heurística MediaTek se declara CLAIMED. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (receptor UDP e parsers ESP32), `csi.rs`, `udp_bind.rs`, `udp_tee.rs`, `mediatek_csi.rs`, `mediatek_csi_ring.rs`, `qualcomm_csi.rs`, `realtek_csi.rs`, `realtek_radar.rs`, `SECURITY.md`, `tests/multi_node_test.rs`.
- **Riscos/limitações:** o plano de dados não é autenticado (sem MAC/AEAD por quadro nem anti-replay), como o `SECURITY.md` admite. A allowlist por IP é contornável por spoofing. O probe de boot em modo auto abre em 0.0.0.0 por alguns segundos. Em Docker Desktop, a reescrita do IP de origem anula a allowlist por sub-rede. Há lógica duplicada entre `main.rs` e `csi.rs`.
- **Relevância para a plataforma (M01, M02, M12, M15, M16):** alta como padrão e baixa como código. A ingestão deve ficar atrás de uma porta, com o `NativeProvider` como padrão. Vale reimplementar: contrato versionado de quadro bruto com despacho por tipo, bind seguro com allowlist e tee só em loopback (asyncio `DatagramProtocol`) e ring buffer limitado (`collections.deque`). Ingestão de hardware real fica PLANNED/BLOCKED.

#### SS-02 — Resolução de fonte, simulador e máquina de estados de proveniência

- **O que faz:** decide quais tarefas iniciar a partir da fonte pedida (auto, esp32, wifi, simulada, mediatek, qualcomm, realtek). No modo auto, serve dados sintéticos rotulados até chegar o primeiro quadro real e então promove a fonte. Mantém um estado canônico de proveniência que impede o sintético de aparecer como "ao vivo" e aplica marca d'água em exportações sintéticas.
- **Como faz:** uma função pura de planejamento recebe a fonte pedida e os resultados das sondagens e devolve o plano. Valores desconhecidos são rejeitados. A máquina de estados é pura: em função da idade do último quadro, do status de autenticação e do tipo de fonte, resolve para Sintético, Ao vivo verificado, Ao vivo não verificado, Obsoleto ou Desconectado. Não existe estado "desconhecido", e ambiguidade nunca vira "verificado". O status expõe estado, espera por quadros e idade do último quadro.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: lógica pura testável com relógio injetado.
  - Dados: cenários de transição.
  - Competências: modelagem de estados, rastreabilidade, fail-closed.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 13 testes em `provenance.rs`, mais módulos de teste de plano de fonte e de status em `main.rs`. A documentação do Docker diverge: diz que o modo auto falha sem hardware, mas o código serve dados simulados. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/provenance.rs`, `main.rs` (plano de fonte, simulador, readiness), `docs/adr/ADR-295-source-provenance-state-machine.md`.
- **Riscos/limitações:** um operador desatento pode ver dados simulados antes de existir fonte real. A mitigação depende de a UI respeitar o rótulo.
- **Relevância para a plataforma (M15, M16):** muito alta e diretamente alinhada a `source_type=SIMULATED`/`L0_SYNTHETIC`: enum de proveniência com transição pura (Pydantic, pytest e hypothesis), exposto de forma aditiva no contrato 2.0.0, com regra explícita "sintético nunca vira ao vivo" e marca d'água em todo export. Ver também UI-02 e PY-15.

#### SS-03 — Extração de features, classificação de presença/movimento e fusão determinística de sala

- **O que faz:** de cada quadro extrai amplitude ponderada, variância por subportadora, potência nas bandas de movimento e de respiração, frequência dominante e RSSI. Classifica cada nó em ausente, presente parado ou presente em movimento, com suavização e histerese, e funde os nós numa inferência de sala que ignora nós obsoletos.
- **Como faz:** pesos de subportadora por sensibilidade e variância em janela deslizante. A constante de tempo da EMA vem do fps **medido** (não de contagem de quadros). Há baseline lenta subtraída depois do aquecimento e debounce temporal antes de aceitar uma transição. A fusão de sala é função pura sobre as inferências por nó, ponderada por frescor e independente da ordem. Nó silencioso vira indisponível, em vez de congelar o último valor. Inferência por nó e agregado de sala são tipos separados. Um classificador adaptativo pode sobrepor a decisão (SS-11).
- **Requisitos para implementar:**
  - Hardware: nenhum em desenvolvimento.
  - Software: estatística de janela, EMA, FSM com histerese.
  - Dados: séries sintéticas ou gravadas com rótulos de ocupação.
  - Competências: DSP e máquinas de estado robustas a jitter.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 13 testes em `inference.rs` e vários módulos em `main.rs` (presença suavizada, debounce, classificação de sala, EMA de fps). O README declara "regras de consistência de estado, sem alegação de acurácia". Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (extração, classificação, debounce, fusão multi-nó), `inference.rs`, `csi.rs`.
- **Riscos/limitações:** limiares heurísticos. Não há avaliação contra referência. Há dois caminhos de suavização a manter (por tick e por nó).
- **Relevância para a plataforma (M01, M02, M06, M08):** alta. Separar "inferência por nó" de "agregado de sala", com fusão pura e determinística, janela de frescor e debounce baseado em tempo, cabe no domínio de Acquisition sobre dados sintéticos, com testes de determinismo property-based.

#### SS-04 — Estimativa de contagem de pessoas (heurística, min-cut e eigenmodos)

- **O que faz:** estima quantas pessoas há na sala por três caminhos: escore heurístico com histerese assimétrica, particionamento do grafo de correlação entre subportadoras e, com calibração, a energia de perturbação do modelo de campo. Agrega entre nós frescos, condicionado à presença de sala.
- **Como faz:** (a) limiares de subida mais altos que os de descida; (b) grafo de subportadoras com arestas de correlação, fonte e sumidouro virtuais e min-cut exato (max-flow) para estimar clusters de movimento; (c) SVD do modelo de campo, separando deriva e perturbação. Um pacote ausente de um nó não zera a sala, e uma leitura positiva isolada não força contagem.
- **Requisitos para implementar:**
  - Hardware: um ou mais nós; os eigenmodos exigem calibração de sala vazia.
  - Software: álgebra linear e min-cut/max-flow.
  - Dados: gravações com contagem anotada.
  - Competências: grafos, álgebra linear, avaliação de contagem.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 27 testes em `field_bridge.rs` e módulos de agregação em `main.rs`. Comentários citam issues de usuários sobre falsos positivos, sem métrica publicada (MAE). Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (escore, correlação, agregação), `field_bridge.rs`, `README.md`.
- **Riscos/limitações:** sensível a multipercurso (o próprio código relata falsos "duas pessoas" com uma pessoa se movendo). Janela curta. Não implementa entradas e saídas.
- **Relevância para a plataforma (M02, M03, M08):** média-alta. Min-cut via networkx e eigenmodos via `numpy.linalg.svd`, testados contra geradores com contagem conhecida. A regra de agregação multi-nó por frescor é valiosa para M02. Ver também SV-08.

#### SS-05 — Detecção de sinais vitais por FFT com gate de publicação e abstenção explícita

- **O que faz:** estima respiração e FC a partir de amplitude e fase. **Só publica números** quando há calibração explícita e fresca, exatamente um ocupante e qualidade suficiente. Caso contrário, publica um motivo de abstenção (calibração exigida, exatamente um ocupante exigido ou gate de qualidade).
- **Como faz:** buffers por nó na taxa medida, reconfigurados quando o relógio estabiliza. Passa-banda FIR (sinc janelado) nas bandas fisiológicas públicas, FFT própria com zero-padding e detecção de pico em banda, confiança pela razão pico/ruído, variância circular de fase, média aparada e suavização. Um prior de bootstrap nunca autoriza taxas.
- **Requisitos para implementar:**
  - Hardware: CSI estável e ocupante quase imóvel (real).
  - Software: FFT, FIR, estatística robusta.
  - Dados: séries com referência (cinta, oxímetro), hoje inexistentes.
  - Competências: sinais biomédicos e regulação de saúde.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 16 testes em `vital_signs.rs` e 18 em `tests/vital_signs_test.rs`, todos com senoides sintéticas. A documentação traz bandas cardíacas inconsistentes entre si. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/vital_signs.rs`, `main.rs` (gates de publicação), `tests/vital_signs_test.rs`.
- **Riscos/limitações:** FC por amplitude CSI é muito frágil. Exibir números sem validação pode ser lido como dado de saúde.
- **Relevância para a plataforma (M04, M05, M15):** M04 e M05 devem continuar PLANNED/BLOCKED. O padrão de **abstenção** deve ser importado já: o contrato carrega "vitais numéricos autorizados" e "motivo de abstenção" e nunca publica número sem autorização de evidência. Ver também SV-16.

#### SS-06 — Calibração de sala vazia e baseline de bootstrap com autoridade reduzida

- **O que faz:** fluxo REST de calibração do modelo de campo (start, stop, cancel, status, reset, promote e refine de bootstrap). A calibração fica ligada a nó-fonte e grade CSI explícitos. Permite persistir um prior agregado de sala vazia, vinculado à instalação e com expiração, que reduz falsos positivos no boot, mas **nunca autoriza evidência calibrada nem vitais**.
- **Como faz:** o nó-fonte é escolhido explicitamente depois de evidência de grade ao vivo, e calibração no boot é recusada. Os ids são opacos e o binding é um digest da grade. Para promover, o servidor mede um holdout separado de amostras espaçadas, exige maioria classificada como vazia e nenhuma estimativa vital, e devolve diagnósticos estruturados (observado, exigido, comparação). A persistência guarda só agregados (sem CSI bruto), com schema versionado, binding por hash de instalação, digest verificado e expiração; ao restaurar, a autoridade é só de bootstrap. O reset exige admin.
- **Requisitos para implementar:**
  - Hardware: nó real e sala comprovadamente vazia.
  - Software: persistência com hash, relógio de parede, diagnósticos estruturados.
  - Dados: holdout de sala vazia.
  - Competências: procedimentos de calibração, níveis de autoridade, segurança de arquivos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 12 testes em `bootstrap_baseline.rs` e módulos de expiração/grade em `main.rs`. Não há relato de execução em campo. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/bootstrap_baseline.rs`, `main.rs` (rotas de calibração), `README.md`.
- **Riscos/limitações:** "sala vazia" depende da honestidade do operador. O prior pode ficar obsoleto antes de expirar. O hash detecta corrupção, não adulteração.
- **Relevância para a plataforma (M16, M15, M08):** muito alta para M16. Níveis de autoridade (bootstrap < calibrado < verificado), holdout com diagnósticos por verificação e persistência com digest e expiração em SQLite/Alembic, tudo com dados L0. O formato de diagnóstico (verificação, observado, exigido, comparação) é um bom contrato aditivo.

#### SS-07 — Motor de streaming governado e ponte para o caminho ao vivo

- **O que faz:** compõe num ciclo auditável:
  - a fusão multi-nó e o escore de qualidade com contradições;
  - o carimbo da calibração aplicada;
  - o rebaixamento de classe de privacidade;
  - o registro de uma crença num grafo de mundo com proveniência obrigatória;
  - um witness criptográfico determinístico;
  - recomendação de recalibração e monitoramento do risco de partição da malha (MeshGuard).
  No servidor, roda ao lado da fusão "nua" e expõe o estado de confiança no status.
- **Como faz:** a fusão pondera por atenção e devolve evidência e contradições. Contradição, divergência de calibração ou risco de malha rebaixam a privacidade um degrau, de forma monotônica. Um nó de estado semântico é anexado ao grafo. O witness é BLAKE3 sobre proveniência, classe e calibração. A recalibração dispara por coerência baixa sustentada ou change-point. O MeshGuard mantém min-cut dinâmico com pesos quantizados e atualização só quando o peso muda. Na ponte ao vivo, a classe mais restrita suprime as amplitudes brutas; os demais derivados continuam publicados sem governança.
- **Requisitos para implementar:**
  - Hardware: nenhum para o motor; nós com posições conhecidas para a parte direcional.
  - Software: BLAKE3, grafo com proveniência, min-cut incremental.
  - Dados: quadros multi-nó com timestamps e ids de calibração.
  - Competências: arquitetura de confiança, privacy by design, grafos.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 26 testes em `lib.rs` e 10 em `mesh_guard.rs` (determinismo, rebaixamento, witness, ciclo vazio fail-closed), mais um benchmark contra orçamento e 18 testes na ponte multiestática. O grafo de mundo vem de um submódulo vazio no clone. `engine_bridge.rs` admite a governança parcial. Caminhos: `v2/crates/wifi-densepose-engine/src/lib.rs`, `mesh_guard.rs`, `benches/engine_cycle.rs`, `v2/crates/wifi-densepose-sensing-server/src/engine_bridge.rs`, `multistatic_bridge.rs`.
- **Riscos/limitações:** a governança de saída é parcial. Os submódulos externos ampliam a superfície. O witness é hash, não assinatura.
- **Relevância para a plataforma (M14, M15, M08):** muito alta como inspiração. Registro de saída com evidência, versão de modelo e calibração e decisão de privacidade; rebaixamento monotônico; witness determinístico (hashlib/blake3) sobre serialização canônica gravado no histórico SQLite; risco de partição com networkx. Ver também SV-11 e GV-02.

#### SS-08 — Pose COCO-17 derivada do sinal, rastreamento, localização por pico de campo e física fail-closed

- **O que faz:** publica, por pessoa, 17 keypoints, bounding box, zona, posição e movimento. Aplica suavização, restrição de comprimento ósseo e Kalman. A posição é o pico mais forte do campo de sinal. Há visões bruta, ambas e refinada da camada física, com schemas JSON publicados.
- **Como faz:** **o esqueleto é procedural**: um template COCO-17 em pixels é modulado por escalares do sinal (potência de movimento, potência respiratória, frequência dominante, fase respiratória), com deslocamento por pessoa. Não há rede neural no loop ao vivo, e o campo de keypoints de modelo é sempre nulo. A localização lê o pico de uma grade 2D de variâncias e o próprio código diz que não é triangulação. A camada física só refina com contexto verificado; senão devolve 409 tipado. O modo de privacidade proíbe as visões bruta e física.
- **Requisitos para implementar:**
  - Hardware: para pose real, vários nós e modelo treinado com verdade pareada.
  - Software: Kalman, JSON Schema, física de pose.
  - Dados: datasets pareados CSI–pose.
  - Competências: estimação de pose, metrologia (PCK, OKS).
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. `pose.rs` não tem testes. Há testes em tracker_bridge 4, field_localize 6, pose_physics 3 e testes HTTP da física. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (derivação, suavização, rotas e WS de pose), `pose.rs`, `tracker_bridge.rs`, `field_localize.rs`, `pose_physics.rs`, `docs/schemas/pose-observation-v2.schema.json`, `docs/schemas/pose-refinement-v1.schema.json`.
- **Riscos/limitações:** risco alto de um boneco animado por heurística ser tomado por pose real. O rótulo de "inferência de modelo" pode ser ativado sem inferência. Coordenadas em pixels não são métricas.
- **Relevância para a plataforma (M11, M14, M15):** M11 continua PLANNED/BLOCKED. Vale importar os contratos fail-closed (schema canônico com dimensionalidade, frame, calibração e hash; 409 tipado sem evidência). O antipadrão a evitar é esqueleto procedural apresentado como pose. Qualquer visualização deve ser rotulada como ilustração sintética.

#### SS-09 — Contêiner de modelos RVF, carregamento progressivo e gestão de modelos

- **O que faz:** contêiner binário próprio com manifesto, pesos, metadados, configuração de vitais, quantização, witness, índice vetorial, overlay e perfis de adaptação. Faz carregamento progressivo em camadas, detecta e converte formatos publicados (safetensors, manifesto JSONL) e expõe endpoints para listar, carregar, descarregar e apagar modelos e perfis de adaptação.
- **Como faz:** segmentos com cabeçalho fixo, alinhamento e checksum (rejeita corrupção). Um pipeline estendido adiciona índice HNSW e perfis. A detecção usa identificador e extensão, com erro acionável. As flags de CLI cobrem carga, conversão e exportação.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: serialização binária, hashing.
  - Dados: pesos treinados (inexistentes de forma validada).
  - Competências: formatos de arquivo, MLOps.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: rvf_container 24, rvf_pipeline 16, model_format 9, mais 16 de integração. Porém: o endpoint de carga só grava o id e marca "carregado" sem ler arquivo; a ativação de perfil LoRA só registra log; o salvamento grava pesos recém-inicializados; `model_manager.rs` é órfão. As rotas DELETE usam sintaxe de parâmetro que provavelmente não casa na versão do roteador (inferido, não executado). Caminhos: `v2/crates/wifi-densepose-sensing-server/src/rvf_container.rs`, `rvf_pipeline.rs`, `model_format.rs`, `main.rs` (rotas de modelos), `model_manager.rs`, `tests/rvf_container_test.rs`.
- **Riscos/limitações:** formato proprietário sem especificação independente. Falsa sensação de "modelo ativo". Sem assinatura.
- **Relevância para a plataforma (M12):** média. Preferir formatos abertos (safetensors, ONNX, manifesto JSON com SHA-256 e Ed25519 opcional). Lição de qualidade: um endpoint "load" deve carregar de verdade ou responder 501/409 tipado, nunca sucesso sem efeito. Ver também EH-02.

#### SS-10 — Treinamento (API in-server, treino offline, pré-treino contrastivo, embeddings e índice de fingerprints)

- **O que faz:** dentro do servidor, treina um modelo linear a partir de gravações e exporta o contêiner, com progresso por WebSocket. Offline (CLI do binário), carrega datasets públicos, treina um transformer de grafo com perda composta, faz pré-treino contrastivo, extrai embeddings e constrói índices de fingerprints.
- **Como faz:** o job in-server tem slot único. Se nenhuma gravação carrega, cai para o buffer ao vivo e marca "degradado". As features são variância, gradientes e potência por Goertzel. A regressão linear usa descida de gradiente com PCK. **Os alvos são pseudo-rótulos** calculados pela mesma heurística do esqueleto procedural. Os endpoints de pré-treino e LoRA reutilizam o mesmo job linear. Offline há parsers próprios de `.npy` e `.mat`, perda de 6 termos, SGD com momentum, cosine annealing e pré-treino estilo SimCLR (InfoNCE).
- **Requisitos para implementar:**
  - Hardware: CPU para o linear; GPU para pose séria.
  - Software: álgebra linear e loop de treino (no alvo: scikit-learn, PyTorch CPU, MLflow).
  - Dados: MM-Fi/Wi-Pose (licenças próprias) ou gravações rotuladas.
  - Competências: ML, contrastivo, splits sem vazamento.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. Contagem de testes: training_api 33, trainer 28, dataset 17, mais testes HTTP. O treino offline usa amostras sintéticas quando o dataset falta, avisando só por log. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/training_api.rs`, `trainer.rs`, `dataset.rs`, `main.rs`, `v2/crates/wifi-densepose-aether/src/`.
- **Riscos/limitações:** treinar contra pseudo-rótulos gera métricas circulares. Os rótulos "pretrain" e "LoRA" são enganosos. O fallback sintético é silencioso.
- **Relevância para a plataforma (M12, M06, M08, M11):** média, como laboratório opcional PLANNED. Regras: nunca usar a saída da heurística como rótulo; rodadas com dados sintéticos são L0 e marcadas como degradadas; reportar baseline trivial ao lado do PCK. Ver também ML-01 e OP-05.

#### SS-11 — Classificador adaptativo de atividade por ambiente

- **O que faz:** aprende limiares específicos da sala a partir de gravações rotuladas pelo nome do arquivo. Pode ser carregado a quente para sobrepor a heurística.
- **Como faz:** estatísticas por classe, distância tipo Mahalanobis ponderada aos centróides e refinamento por regressão logística. As classes são descobertas pelos nomes. O modelo é salvo em JSON versionado; a versão mais nova usa a frequência temporal medida.
- **Requisitos para implementar:**
  - Hardware: nenhum para treino.
  - Software: estatística descritiva e regressão logística (scikit-learn LDA/QDA/LogisticRegression).
  - Dados: gravações rotuladas.
  - Competências: aprendizado supervisionado leve.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 7 testes, sem acurácia real. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/adaptive_classifier.rs`, `main.rs` (rotas adaptativas).
- **Riscos/limitações:** rótulos por nome de arquivo são frágeis. Overfitting ao ambiente. Sem validação cruzada.
- **Relevância para a plataforma (M06, M08, M16):** média-alta como padrão de "personalização por ambiente" com modelo pequeno e explicável. O evento deve registrar qual classificador produziu a decisão.

#### SS-12 — Gravação de sessões CSI em JSONL com marca d'água sintética e redação de privacidade

- **O que faz:** inicia e para gravações dos updates em JSONL, lista e apaga sessões. Marca gravações feitas sob fonte sintética e, no modo de privacidade, remove biometria antes de gravar.
- **Como faz:** uma tarefa assina o broadcast e grava uma linha por mensagem, com flush periódico. No modo de privacidade, linhas não parseáveis são descartadas (fail-closed). A marca d'água vai no registro de metadados da sessão. Erros de sistema de arquivos voltam genéricos, com correlation id.
- **Requisitos para implementar:**
  - Hardware: disco.
  - Software: escrita assíncrona, sanitização de ids, redação JSON.
  - Dados: stream de updates.
  - Competências: segurança de sistema de arquivos e governança de dados.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Há testes de formato. Por leitura: o início de gravação usa o id do cliente no caminho sem a sanitização aplicada na exclusão (provável traversal com truncamento de arquivo), e a rota exige só escopo de leitura. `path_safety.rs` existe, mas não é usado ali. `recording.rs` é órfão. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (rotas de gravação), `recording.rs`, `path_safety.rs`, `bearer_auth.rs`.
- **Riscos/limitações:** gravações contêm dados pessoais. Não há retenção nem rotação visíveis. Há os defeitos de caminho e de rota descritos acima.
- **Relevância para a plataforma (M12, M15):** alta como lição. Ids gerados pelo servidor (uuid4) ou validados por regex, verificação de contenção de caminho e marca L0 por registro, além de testes de rota para cada verbo HTTP.

#### SS-13 — Streaming em tempo real (WebSocket) e tap de introspecção de baixa latência

- **O que faz:** transmite updates de sensoriamento, pose, introspecção por quadro, eventos de campo e progresso de treino. Mede a taxa real do stream e a contagem de clientes.
- **Como faz:** um canal broadcast de JSON alimenta, em fan-out, os clientes WS, o gravador, a ponte MQTT e o RuField. Clientes lentos perdem mensagens em vez de travar o loop. A introspecção calcula o expoente de Lyapunov e o regime de atrator e faz casamento DTW contra uma biblioteca de assinaturas, que na prática é criada vazia.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: WebSocket e pub/sub; tslearn/dtaidistance para DTW.
  - Dados: assinaturas rotuladas.
  - Competências: tempo real, contrapressão, séries temporais.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Contagem de testes: introspection 8, stream_stats 7, mais 5 de latência arquitetural. O DTW só funciona em testes com biblioteca injetada. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (handlers WS, tick de broadcast), `introspection.rs`, `stream_stats.rs`, `tests/introspection_latency.rs`.
- **Riscos/limitações:** JSON reparseado por cliente. Biblioteca de assinaturas vazia. Lyapunov instável em janelas curtas.
- **Relevância para a plataforma (M01, M06, M15):** alta. WebSocket do Starlette com fan-out por `asyncio.Queue` limitada (descartar em vez de bloquear), métricas medidas de taxa e clientes e o padrão "snapshot REST + stream WS com o mesmo contrato".

#### SS-14 — Autenticação e autorização da API e endurecimento HTTP

- **O que faz:** protege a API e os WebSockets com token estático opcional, OAuth (JWKS) e escopos por método. Inclui tickets de WebSocket de uso único, login de navegador com PKCE no servidor e cookie de sessão assinado, allowlist de Host contra DNS rebinding, recusa de bind roteável sem autenticação, erros genéricos com correlation id e sanitização de identificadores.
- **Como faz:** comparação de token em tempo constante e JWT verificado offline, com fail-closed se o OAuth pedido não inicializa. Leitura exige escopo de leitura; mutação exige admin, salvo uma allowlist explícita. Rotas novas caem em admin por padrão. O ticket é opaco, curto e de uso único. No login de navegador, o token OAuth nunca chega ao JavaScript. A ordem das camadas (Host → bearer → privacidade, aplicadas depois dos merges) é verificada por um teste que sobe o binário real.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: verificação JWT/JWKS, HMAC, CSPRNG, middleware.
  - Dados: nenhum.
  - Competências: OAuth 2.0/PKCE, DNS rebinding, CWE-209, path traversal.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: bearer_auth 62, browser_session 32, ws_ticket 13, host_validation 14, http_bind 5, error_response 5, path_safety 9. `tests/auth_wiring.rs` (7) sobe o binário e documenta dois bypasses históricos. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/bearer_auth.rs`, `ws_ticket.rs`, `browser_session.rs`, `host_validation.rs`, `http_bind.rs`, `error_response.rs`, `path_safety.rs`, `tests/auth_wiring.rs`, `SECURITY.md`.
- **Riscos/limitações:** autenticação desligada por padrão em loopback. O OAuth depende de um provedor externo específico. Não há rate limiting visível. A allowlist de "mutações seguras" inclui a gravação (ver SS-12).
- **Relevância para a plataforma (M15, M16):** muito alta. Escopos por método com allowlist fail-closed (dependências FastAPI), ticket WS de uso único em vez de token na URL, `TrustedHostMiddleware`, recusa de bind público sem token, handler genérico com correlation id e teste E2E que sobe o servidor real. Para OAuth opcional, Authlib com Keycloak/Authentik (gratuitos). Ver também GV-11 a GV-14 e UI-03.

#### SS-15 — Modo de privacidade em todo o servidor (redação de biometria fail-closed)

- **O que faz:** com o modo de privacidade ativo, remove FC, FR e keypoints de pose de REST, WS, gravações, MQTT e Matter. Mantém presença, movimento, contagem, zona e postura grosseira. As entidades biométricas nem são anunciadas no Home Assistant.
- **Como faz:** um middleware reescreve corpos JSON **removendo chaves** (não anulando), para que o cliente não distinga "suprimido" de "ausente". Frames e linhas passam por um redator. Conteúdo não parseável é descartado (WS, gravação) ou vira 500 (REST). As visões de pose bruta e física retornam 403 tipado. Estados inferidos (primitivas) continuam habilitados.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: middleware de resposta e parser JSON.
  - Dados: nenhum.
  - Competências: privacy by design, classificação de dados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: privacy_filter 6, mqtt/privacy 4, mais testes de superfície em `main.rs`. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/privacy_filter.rs`, `src/mqtt/privacy.rs`, `main.rs`.
- **Riscos/limitações:** redação por nome de chave é frágil, porque novos campos escapam. Estados inferidos de saúde (sono, angústia) continuam passando. Não há classificação formal por campo.
- **Relevância para a plataforma (M15, M04, M05, M09, M11):** alta. Implementar como política declarativa no contrato: cada campo do evento 2.0.0 recebe uma classe de sensibilidade e um serializador central aplica a política com allowlist, fail-closed e remoção de chaves (Pydantic e middleware FastAPI).

#### SS-16 — Integração Home Assistant via MQTT com auto-discovery

- **O que faz:** publica cada nó como dispositivo do HA e cada capacidade como entidade (presença, contagem, FC, FR, movimento, queda, RSSI, ocupação por zona, pose opcional, primitivas), com discovery retido, disponibilidade e LWT, limitação de taxa e TLS/mTLS.
- **Como faz:** uma ponte converte o broadcast em snapshots tipados por nó e transforma a borda de subida da flag de queda em evento único. Um **planejador puro** (sem broker nem relógio) decide as mensagens: disponibilidade offline quando não há fonte real, estados com change-gate e sensores com limite de taxa. Invariantes de segurança em funções puras (rejeitar curingas e nulos em ids de tópico, limitar payload, senha por variável de ambiente).
- **Requisitos para implementar:**
  - Hardware: host do broker.
  - Software: Mosquitto, cliente MQTT com TLS, Home Assistant (todos gratuitos).
  - Dados: stream de estados.
  - Competências: MQTT e schema de discovery do HA.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: bridge 10, config 16, discovery 12, publisher 3, security 22 (com proptest), state 21, planner 13. A integração com broker real é opcional, por variável de ambiente. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/mqtt/mod.rs`, `bridge.rs`, `config.rs`, `discovery.rs`, `planner/mod.rs`, `publisher.rs`, `security.rs`, `state.rs`, `tests/mqtt_integration.rs`.
- **Riscos/limitações:** publicar biometria no HA amplia a exposição. O schema do HA muda entre versões.
- **Relevância para a plataforma (M13):** alta. aiomqtt/paho-mqtt com Mosquitto e o schema público de discovery do HA, com planejador puro separado do transporte, disponibilidade offline para fonte não real e atributo de proveniência L0 em cada entidade. Ver também HC-14 e PY-04.

#### SS-17 — Primitivas semânticas de automação

- **O que faz:** converte o stream em estados de alto nível publicados como entidades: dormindo, angústia, sala ativa, anomalia de inatividade, reunião, banheiro, risco de queda, saída da cama, sem movimento e transição entre cômodos. Inclui um barramento de eventos, um registro auditável de estado semântico (versão de modelo, calibração, ação de privacidade, expiração, evidências) e uma regra de roteamento por concordância de vários sinais.
- **Como faz:** cada primitiva é uma FSM com tempo de permanência, condição de saída e período refratário sobre presença, movimento, FR, FC, contagem e zonas. O risco de queda é um escore 0–100 por quedas confirmadas e variância de movimento. As primitivas são registradas como objetos de trait no barramento.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: FSMs temporizadas (biblioteca `transitions`) e relógio injetado (freezegun).
  - Dados: longitudinais reais para calibrar.
  - Competências: automação residencial, gerontecnologia, fadiga de alerta.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. De 4 a 14 testes por primitiva. As flags de zonas e limiares existem só na estrutura de argumentos da biblioteca; o binário usa sempre a configuração padrão, então "banheiro" e "cama" não são configuráveis. O registro semântico e o roteamento não são usados fora do módulo. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/semantic/mod.rs`, `bus.rs`, `sleeping.rs`, `distress.rs`, `fall_risk.rs`, `elderly_anomaly.rs`, `record.rs`, `src/cli.rs`.
- **Riscos/limitações:** termos como "angústia", "risco de queda" e "anomalia em idoso" sugerem uso em saúde sem validação. As baselines não persistem.
- **Relevância para a plataforma (M09, M07, M10, M13, M06):** média-alta como arquitetura (barramento de primitivas plugáveis com FSM pura e registro com proveniência e expiração). Primitivas de saúde ficam PLANNED/BLOCKED. Sala ativa, reunião, transição e ausência de movimento podem ser implementadas com dados L0.

#### SS-18 — Ponte Matter (scaffolding sem SDK)

- **O que faz:** define como as entidades virariam dispositivos Matter: mapeamento para IDs de cluster e tipo de dispositivo, árvore de endpoints de um bridge e geração de códigos de comissionamento (manual e QR).
- **Como faz:** tipos puros e tabelas, independentes de SDK. Os códigos seguem formatos públicos da especificação Matter (empacotamento de bits, dígito verificador Verhoeff, base-38).
- **Requisitos para implementar:**
  - Hardware: um controlador Matter.
  - Software: SDK Matter (rs-matter, connectedhomeip, python-matter-server), todos open-source.
  - Dados: nenhum.
  - Competências: especificação Matter.
- **Evidência e maturidade:** `STUB` / `UNIT_TESTS_ONLY`. Contagem de testes: bridge 10, clusters 16, commissioning 21. A feature `matter` está vazia e não é usada pelo binário. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/matter/mod.rs`, `bridge.rs`, `clusters.rs`, `commissioning.rs`, `Cargo.toml`.
- **Riscos/limitações:** sem interoperabilidade real. A certificação comercial é paga.
- **Relevância para a plataforma (M13):** baixa no curto prazo (MQTT e HA cobrem o valor). Manter como PLANNED.

#### SS-19 — Superfície RuField: eventos de campo assinados (Ed25519) com gate de egress por privacidade

- **O que faz:** converte cada ciclo governado num evento de campo assinado e o expõe de forma aditiva em endpoints próprios (anel de eventos recentes e stream). Classes acima da política de rede nunca saem do host.
- **Como faz:** monta um snapshot a partir dos dados do ciclo e do estado de confiança. A conversão e a assinatura ficam num crate anticorrupção. Ciclos vazios não geram evento fantasma. Sem a variável de seed, o assinador usa uma **seed de desenvolvimento fixa no código**, marcada nos metadados com aviso.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Ed25519 e serialização canônica.
  - Dados: ciclos.
  - Competências: assinatura e gestão de chaves.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 4 testes no módulo e 4 de integração (verificação de assinatura, ausência de evento fantasma). O vendor está vazio no clone. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/rufield_surface.rs`, `tests/rufield_surface_test.rs`, `v2/crates/wifi-densepose-rufield/Cargo.toml`.
- **Riscos/limitações:** com a seed padrão, qualquer pessoa com o código-fonte forja assinaturas. Não há gestão nem rotação de chaves.
- **Relevância para a plataforma (M14, M15):** média-alta. Assinar exportações de evidência com Ed25519 (PyNaCl/cryptography), com chave gerada na instalação e nunca embutida. Sem chave, o boot deve falhar ou publicar explicitamente "unsigned". Ver também MB-18.

#### SS-20 — Fontes alternativas: telemetria de fornecedores RF (ADR-270) e RSSI do Wi-Fi do host

- **O que faz:** (a) mantém um registro de 10 provedores de telemetria RF (Mist/Juniper, NETGEAR, Origin AI, Plume/OpenSync, Google Nest, Linksys, Luma/OpenWrt, Electric Imp, RF Solutions, Wifigarden), com descritores de capacidade, decodificadores e ingestão por POST; (b) captura RSSI multi-BSSID do próprio host (netsh no Windows, CoreWLAN no macOS).
- **Como faz:** (a) eventos validados contra o descritor e etiquetados como vivos ou simulados. Por tipo, nenhum adaptador consegue construir CSI complexa a partir de dados escalares, e provedores sem contrato falham fechado. (b) Uma tarefa periódica com registro de BSSIDs limitado e com expiração, caindo para o RSSI único da interface quando a varredura falha.
- **Requisitos para implementar:**
  - Hardware: Wi-Fi gerenciado de fornecedor ou um PC com Wi-Fi.
  - Software: clientes HTTP/webhook e utilitários do SO.
  - Dados: credenciais e contratos (em geral pagos).
  - Competências: APIs de gestão Wi-Fi.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: vendor_mist_netgear 10, vendor_origin_plume 10, vendor_remaining 6, vendor_rf 2, todos com fixtures. O próprio código avisa que o JSON é contrato para sidecars, não o formato real do fornecedor. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/vendor_rf.rs`, `vendor_mist_netgear.rs`, `vendor_origin_plume.rs`, `vendor_remaining.rs`, `main.rs` (tarefa Wi-Fi do host).
- **Riscos/limitações:** APIs pagas conflitam com custo zero. RSSI do host tem resolução muito baixa. O sidecar aceita eventos "vivos" fabricáveis.
- **Relevância para a plataforma (M08, M14, M01):** média. O padrão de adaptador seguro por capacidade (o tipo impede promover escalar a CSI) e o rótulo de proveniência por evento são excelentes para portas e adaptadores. Fontes gratuitas viáveis: OpenWrt/OpenSync local e RSSI do host. Ver também EH-19 e EH-20.

#### SS-21 — Malha multi-nó: estado por nó, sincronização de relógio, posições e descoberta local (mDNS)

- **O que faz:** expõe saúde e features por nó, estado de sincronização, visão e métricas da malha em formato texto Prometheus, e posições configuradas. Remove nós obsoletos e anuncia a instalação por DNS-SD.
- **Como faz:** cada nó tem histórico, EMA de fps, classificação, contagem, novidade e últimas vitais com rótulo de frescor. Pacotes de sincronização atualizam líder, seguidor e offset. Nós sem posição usam um padrão, e o status informa quais. O TXT do mDNS não leva SSID nem dados pessoais e é pulado em loopback.
- **Requisitos para implementar:**
  - Hardware: vários nós.
  - Software: mDNS/DNS-SD (zeroconf) e prometheus-client.
  - Dados: posições medidas.
  - Competências: sincronização de relógio e observabilidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Testes de expulsão de nós, sincronização e posições em `main.rs`, 9 em `multi_node_test.rs` e 2 em `discovery.rs`. Os offsets de bancada citados não têm log anexo. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/main.rs` (estado de nó, endpoints de malha), `discovery.rs`, `tests/multi_node_test.rs`.
- **Riscos/limitações:** posições padrão silenciosas distorcem a fusão. mDNS não funciona bem em containers.
- **Relevância para a plataforma (M02, M16, M14):** alta para M16. Nós sintéticos com posição, frescor e sincronização simulada, `/metrics` e um onboarding que mostra quais nós estão na posição padrão.

#### SS-22 — Observabilidade, endpoints operacionais e registro de módulos de borda

- **O que faz:** exporta logs OpenTelemetry via OTLP (feature opcional) com eventos curados e convenções semânticas geradas de um registro validado. Oferece endpoints de saúde (live, ready, version, metrics) e status, uma stack Docker de coletor e um proxy com cache para um catálogo remoto de módulos de borda.
- **Como faz:** ponte tracing→OTLP. Nomes e atributos vêm de um registro verificado em CI (ferramenta Weaver). O readiness reporta proveniência e confiança. O catálogo é buscado com timeout e cache TTL, e informa o SHA-256 do conteúdo.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: SDK OpenTelemetry, Collector, backend de logs (Loki, OpenSearch), psutil.
  - Dados: nenhum.
  - Competências: observabilidade e operações.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: telemetry 1, semconv 1, edge_registry 7. **Dois endpoints de saúde devolvem percentuais fixos** de CPU, memória e disco e marcam "pose" sempre saudável. O catálogo não compara o SHA-256 com um valor fixado. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/telemetry.rs`, `semconv.rs`, `edge_registry.rs`, `main.rs` (handlers de saúde), `docs/observability.md`, `docker/otel-compose.yml`.
- **Riscos/limitações:** métricas fixas enganam orquestradores. Catálogo de nuvem sem assinatura.
- **Relevância para a plataforma (M15, M16):** alta. opentelemetry-python com OTLP desligado por padrão, registro próprio de nomes verificado em CI e health/readiness que reporte o estado real (fonte, frescor, migrações, banco), nunca constantes. Ver também OP-17.

#### SS-23 — CLI `wifi-densepose` (login, Spaces, calibração, calibrate-serve, matrícula e treino por sala, MAT)

- **O que faz:** binário com os subcomandos login/logout/whoami (provedor externo), leitura de recursos espaciais de uma API de nuvem, captura de baseline via UDP, servidor HTTP de calibração com UI, matrícula guiada por âncoras, treino de especialistas por sala, leitura ao vivo por mistura de especialistas e triagem para desastres (MAT).
- **Como faz:** PKCE com servidor em loopback ou colagem de código, com armazenamento local e refresh. A calibração usa parser local e o gravador do crate de sinal. O servidor de calibração tem uma tarefa dona do socket, canal mpsc, CORS permissivo, token opcional e sanitização do id da sala. **O MAT só gera dados de demonstração com a flag de simulação**; sem ela, informa que não há hardware.
- **Requisitos para implementar:**
  - Hardware: ESP32 com CSI bruto.
  - Software: CLI com subcomandos (Typer/Click no alvo), cliente OAuth, mini servidor HTTP.
  - Dados: sessões rotuladas por âncora.
  - Competências: UX de linha de comando, calibração.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: auth 4, calibrate 14, calibrate_api 11, mat 5, room 4; Spaces sem testes. Um comentário cita validação ao vivo sem log. Caminhos: `v2/crates/wifi-densepose-cli/src/main.rs`, `auth.rs`, `spaces.rs`, `calibrate.rs`, `calibrate_api.rs`, `room.rs`, `mat.rs`, `v2/crates/wifi-densepose-cli/README.md`.
- **Riscos/limitações:** o servidor de calibração abre UDP em 0.0.0.0 e usa CORS permissivo, abaixo do endurecimento do servidor principal. O MAT com dados fixos pode ser confundido com triagem real.
- **Relevância para a plataforma (M16, M12, M02, M08):** média-alta para M16: um assistente de onboarding em etapas no Next.js e comandos Typer no backend, sobre dados sintéticos. Funcionalidades de triagem médica ou de desastre com dados demonstrativos devem ser evitadas.

#### SS-24 — Empacotamento e implantação em Docker com postura fail-closed

- **O que faz:** build multi-estágio do servidor (MQTT e, opcionalmente, OTel) e de binários correlatos. A imagem slim verifica a presença dos assets da UI. O entrypoint recusa iniciar sem token em bind roteável. O compose usa `cap_drop ALL`, `no-new-privileges`, limites de recursos e portas TCP só em 127.0.0.1. Há também uma imagem Python legada.
- **Como faz:** o entrypoint encerra se o bind não for loopback sem token e sem opt-in. Ele só faz bind UDP em todas as interfaces se houver allowlist ou override, e explica quando nenhum nó vai aparecer. O healthcheck só verifica o PID 1.
- **Requisitos para implementar:**
  - Hardware: host Docker.
  - Software: Docker/Compose, Debian slim.
  - Dados: nenhum.
  - Competências: endurecimento de containers e redes Docker.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNCLEAR`. Não há testes da área. Os comentários afirmam que o modo auto falha sem hardware, mas o código hoje serve dados simulados. O build depende de submódulos vazios no clone. Caminhos: `docker/Dockerfile.rust`, `docker/docker-entrypoint.sh`, `docker/docker-compose.yml`, `docker/otel-compose.yml`, `docker/Dockerfile.python`.
- **Riscos/limitações:** deriva documental. Healthcheck trivial. UDP publicado em todas as interfaces.
- **Relevância para a plataforma (M16, M15):** alta como checklist: entrypoint fail-closed sem `SPATIAL_TOKEN` em bind público, `cap_drop`, `no-new-privileges`, portas em 127.0.0.1, imagens fixadas por digest e healthcheck que consulte o readiness real.

### 4.3 Edge/WASM, HAL, bridges de hardware e Wi-Fi scan

**Escopo.** A área tem cinco blocos:

1. **Tier 3 programável no ESP32**: runtime WASM3 no firmware mais o crate `wifi-densepose-wasm-edge`, com cerca de 65 módulos em 12 categorias.
2. **Harness de rotulagem honesta** (ADR-160/163).
3. **Bridges e codecs** (`wifi-densepose-hardware`, `wifi-densepose-mtk-bridge`).
4. **Varredura RSSI multi-BSSID** (`wifi-densepose-wifiscan`).
5. **HAL multimodal** (`ruview-hal`).

Os relatórios do repositório (não reexecutados) declaram 631 testes no wasm-edge, cerca de 208 no hardware, cerca de 169 no wifiscan e cerca de 90 no mtk-bridge. A evidência em hardware real é estreita: fixtures ESP32-C6, uma tabela autodeclarada de runtime no ESP32-S3 e um registro MT7981 fora do repositório. Nenhuma skill tem acurácia de campo.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| EH-01 | Runtime WASM no ESP32 (Tier 3) com host API, capabilities e orçamento | IMPLEMENTED_UNTESTED | REAL_HARDWARE_EVIDENCE | M12, M13 |
| EH-02 | Contêiner RVF e distribuição de módulos (manifesto, hash, "assinatura", OTA) | PARTIAL | UNIT_TESTS_ONLY | M12, M15 |
| EH-03 | Skills núcleo: gesto DTW, coerência, anomalia física, zonas, tendência vital, intrusão | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01–M06, M08, M15 |
| EH-04 | Pacote vertical de segurança e industrial | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01–M04, M06, M08, M13 |
| EH-05 | Pacote vertical de edifícios e varejo/hospitalidade | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M02, M03, M13 |
| EH-06 | Skills médicas experimentais (feature-gated) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M04, M05, M07, M09, M10 |
| EH-07 | Módulos exóticos e de pesquisa | RESEARCH | SYNTHETIC_OR_SIMULATED | M04, M06, M08, M09 |
| EH-08 | Inteligência de sinal (gate, atenção, compressão, recuperação esparsa, matching, transporte ótimo) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M02, M08, M14, M15, M16 |
| EH-09 | Aprendizado adaptativo no dispositivo | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M06, M08, M12, M16 |
| EH-10 | Raciocínio espacial, temporal e autônomo (incluindo "quantum-inspired") | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M08, M13, M14 |
| EH-11 | Integridade do fluxo CSI, perfil comportamental e endurecimento de fronteira | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| EH-12 | Pipeline unificado de skills e harness de validação honesta | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M15, M16 |
| EH-13 | Bindings WASM para navegador (painel WiFi-Mat) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M04 |
| EH-14 | Ingestão ESP32 (ADR-018), agregador UDP, ponte e sincronização | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M12, M16 |
| EH-15 | Malha multiestática: TDM, beacons autenticados, QUIC modelado, RAL | PARTIAL | UNIT_TESTS_ONLY | M14, M15, M16 |
| EH-16 | Codecs vendor-neutros e simuladores determinísticos | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M16 |
| EH-17 | Ponte MediaTek mt76 com portões de proveniência | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M12, M15, M16 |
| EH-18 | Modelo de protocolo IEEE 802.11bf (WLAN Sensing) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M15, M16 |
| EH-19 | Contrato de provedores RF de fornecedores e simulador | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M13, M15 |
| EH-20 | Varredura Wi-Fi multi-BSSID por RSSI e pipeline RSSI | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M02, M04, M08 |
| EH-21 | HAL de sensores multimodal com evidência e proveniência | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M15 |

#### EH-01 — Runtime WASM programável no nó ESP32 (Tier 3) com host API, capabilities e orçamento por frame

- **O que faz:** carrega a quente algoritmos compilados para WebAssembly que rodam no microcontrolador depois do DSP nativo (tiers 0–2) e emitem eventos tipados localmente. São até 4 slots com ciclo de vida init/frame/timer.
- **Como faz:**
  - O firmware embute o interpretador WASM3 com arena pré-alocada por slot.
  - O módulo importa funções de um namespace de host: fase, amplitude, variância, BPM do Tier 2, presença, energia, histórico, emissão de evento e log.
  - Cada função do host é liberada por bits de capability vindos do manifesto. **Um `.wasm` cru sem manifesto recebe todas.**
  - Cada chamada por quadro é cronometrada contra um orçamento; falhas consecutivas põem o slot em erro e o sistema degrada para o Tier 2.
  - No lado Rust, o crate é `no_std`, sem heap e com sanitização única de não finitos na fronteira.
- **Requisitos para implementar:**
  - Hardware: ESP32-S3 (de preferência com PSRAM) ou C6, AP 2,4 GHz e USB.
  - Software: ESP-IDF 5.x, wasm3, Rust `wasm32-unknown-unknown`.
  - Dados: quadros do Tier 2 ou sintéticos.
  - Competências: C embarcado/FreeRTOS, ABI WASM MVP, Rust `no_std`, perfilamento.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `REAL_HARDWARE_EVIDENCE`. A ADR-040 relata medições autodeclaradas num ESP32-S3 (init de runtime, binário combinado pequeno, taxa de CSI), sem log bruto. O boot log documentado mostra a verificação desligada. Não há testes C do runtime. O script de teste gera módulos mínimos à mão: testa o runtime, não os algoritmos. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/lib.rs`, `.cargo/config.toml`, `firmware/esp32-csi-node/main/wasm_runtime.c`, `wasm_runtime.h`, `docs/edge-modules/README.md`, `docs/adr/ADR-040-wasm-programmable-sensing.md`, `scripts/esp32_wasm_test.py`, `docs/edge-modules/esp32_boot_log.txt`.
- **Riscos/limitações:** o interpretador é muito mais lento que nativo, e os orçamentos nunca foram medidos no dispositivo. Módulo cru recebe todas as capabilities. O upload não tem autenticação HTTP. Limiares fixos de compilação.
- **Relevância para a plataforma (M12, M13):** o valor está no padrão de sandbox de plugins: host API mínima, capabilities declaradas, orçamento por chamada e quarentena após falhas. Reimplementável no backend com wasmtime-py (Apache-2.0) ou Extism (BSD-3), usando fuel/epoch como orçamento, sobre quadros L0. Execução em ESP32 fica PLANNED/BLOCKED. Ver também FW-04.

#### EH-02 — Contêiner RVF e cadeia de distribuição de módulos (manifesto, hash, assinatura, upload OTA)

- **O que faz:** empacota o WASM com cabeçalho, manifesto (nome, versão de host API, capabilities, orçamento, limites de eventos e memória, faixa de subportadoras, hash, autor), assinatura e vetores de teste. O firmware valida e carrega o pacote por endpoints REST (upload, listar, iniciar, parar, remover).
- **Como faz:** o builder calcula o SHA-256 e serializa estruturas compactas espelhadas no C, deixando a assinatura zerada para "assinar externamente". O firmware confere tamanhos e hash via PSA Crypto. **Com verificação ativa, a "assinatura" é um digest SHA-256 sobre (chave pública ‖ região assinada)**, não Ed25519. Sem verificação, aceita `.wasm` cru.
- **Requisitos para implementar:**
  - Hardware: ESP32 com memória suficiente.
  - Software: sha2, mbedTLS/PSA e, para assinatura real, Ed25519 nos dois lados.
  - Dados: binários e chaves.
  - Competências: formatos binários, criptografia, gestão de chaves, supply chain.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 2 testes Rust (round-trip e hash) e nenhum teste C. Um achado da auditoria (injeção de assinatura sem checagem de limites) continua no código. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/rvf.rs`, `firmware/esp32-csi-node/main/rvf_parser.c`, `wasm_upload.c`, `v2/crates/wifi-densepose-desktop/src/commands/wasm.rs`, `docs/security-audit-wasm-edge-vendor.md`.
- **Riscos/limitações:** quem conhece a chave pública forja a "assinatura". Upload sem autenticação de transporte. O cliente desktop e o firmware usam porta e formato de upload diferentes (provável incompatibilidade).
- **Relevância para a plataforma (M12, M15):** alta como inspiração para empacotar artefatos de modelo/plugin com manifesto declarativo (Pydantic/JSON Schema) e **assinatura Ed25519 real** (cryptography/PyNaCl), verificada antes de ativar. O digest chaveado não deve ser copiado. Ver também SS-09.

#### EH-03 — Skills de borda núcleo: gesto DTW, coerência de fase, anomalia física, ocupação por zonas, tendência vital e intrusão

- **O que faz:** sete módulos "flagship":
  - reconhecimento de gestos por templates;
  - monitor de coerência de fase;
  - detecção de sinais fisicamente inconsistentes (interferência, antena solta, adulteração);
  - ocupação por zonas;
  - tendências de respiração e FC com eventos de bradi/taqui e apneia;
  - intrusão em zonas antes quietas.
- **Como faz:** DTW com banda Sakoe-Chiba; média de fasores unitários das diferenças de fase com EMA; checagens de consistência fase/amplitude; zonas por agrupamento heurístico de subportadoras com baseline vazia e limiar de variância; janelas móveis com eventos após N chamadas consecutivas fora de faixa; FSM calibrar → armar → alertar. Todos com buffers fixos, cooldowns e IDs de evento por faixa de categoria.
- **Requisitos para implementar:**
  - Hardware: nó CSI ou nenhum (sintético).
  - Software: numpy/scipy, dtaidistance/tslearn.
  - Dados: CSI rotulado por zona, gesto e intrusão.
  - Competências: séries temporais, DTW, EMA/Welford, FSMs.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Segundo os resultados do repositório, tendência vital, ocupação e intrusão acertam 100% em sinais plantados, com amostras mínimas (um positivo e um negativo). Gesto, coerência e anomalia não têm número. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/gesture.rs`, `coherence.rs`, `adversarial.rs`, `occupancy.rs`, `vital_trend.rs`, `intrusion.rs`, `docs/edge-modules/core.md`, `benchmarks/edge-skills/RESULTS.md`, `v2/crates/wifi-densepose-wasm-edge/tests/synthetic_validation.rs`.
- **Riscos/limitações:** limiares constantes. O mapeamento de subportadoras para zonas é heurístico. N muito pequeno.
- **Relevância para a plataforma (M01–M06, M08, M15):** alta. Detectores em Python sobre a cena sintética, com eventos tipados no contrato 2.0.0 e qualidade alimentada pelo índice de coerência. Ver também SV-12 e SV-13.

#### EH-04 — Pacote vertical de segurança e industrial

- **O que faz:**
  - **Segurança:** violação de perímetro com direção, "alta refletividade metálica" (renomeada a partir de "detecção de arma"), tailgating em portas, loitering e movimento de pânico.
  - **Indústria:** proximidade empilhadeira/pedestre, espaço confinado com prova de vida, sala limpa (lotação e movimento), pecuária e vibração estrutural.
- **Como faz:** gradiente de fase entre grupos de subportadoras para direção; razão de variâncias com Welford para refletividade; envelope de energia com múltiplos picos para tailgating; FSMs com histerese; derivada da energia e entropia de direção para pânico; assinatura de baixa frequência para veículos; confirmação periódica de respiração; análise espectral de vibração.
- **Requisitos para implementar:**
  - Hardware: nós nos acessos ou zonas, ou simulação.
  - Software: numpy/scipy.
  - Dados: capturas rotuladas por cenário com referência em vídeo ou sensor.
  - Competências: DSP, FSMs, segurança do trabalho.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes por módulo e uma execução de todos os módulos sem pânico sobre 300 quadros sintéticos. Nenhum número de acurácia. A refletividade metálica é DATA-GATED. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/sec_perimeter_breach.rs`, `sec_weapon_detect.rs`, `sec_tailgating.rs`, `sec_loitering.rs`, `sec_panic_motion.rs`, `ind_forklift_proximity.rs`, `ind_confined_space.rs`, `ind_clean_room.rs`, `ind_livestock_monitor.rs`, `ind_structural_vibration.rs`, `docs/edge-modules/security.md`, `docs/edge-modules/industrial.md`.
- **Riscos/limitações:** menções a normas são de domínio, sem certificação. Alto risco de falso positivo. "Arma" por refletividade não discrimina objeto. Implicações de vigilância (LGPD).
- **Relevância para a plataforma (M01–M04, M06, M08, M13):** média-alta. FSMs de loitering, tailgating, lotação e prova de vida podem virar regras compostas no motor de regras (`domain/rules.py`) sobre eventos sintéticos, com hooks M13 em dry-run. Detecção de metal ou arma fica BLOCKED.

#### EH-05 — Pacote vertical de edifícios inteligentes e varejo/hospitalidade

- **O que faz:**
  - **Edifícios:** presença para HVAC (chegada rápida, saída tolerante), iluminação por zonas, contagem em elevador, ciclo de vida de sala de reunião e auditoria energética com histogramas semanais.
  - **Varejo:** fila com espera estimada, heatmap de permanência 3x3, fluxo direcional (entradas, saídas, líquido), giro de mesas e engajamento em gôndola.
- **Como faz:** debounce e timeouts assimétricos; FSMs de reunião e de mesa; histogramas 24x7; Lei de Little (λ, μ) para fila; acumuladores de permanência; gradiente de fase assimétrico para fluxo.
- **Requisitos para implementar:**
  - Hardware: um nó por zona, mesa ou porta, ou simulação.
  - Software: Python/pandas.
  - Dados: contagens de referência (catraca, vídeo anonimizado), logs de HVAC.
  - Competências: analytics de ocupação, teoria de filas, automação predial.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Nenhuma acurácia medida. Contagem em elevador e fluxo direcional são alegações sem dados. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/bld_hvac_presence.rs`, `bld_lighting_zones.rs`, `bld_elevator_count.rs`, `bld_meeting_room.rs`, `bld_energy_audit.rs`, `ret_queue_length.rs`, `ret_dwell_heatmap.rs`, `ret_customer_flow.rs`, `ret_table_turnover.rs`, `ret_shelf_engagement.rs`, `docs/edge-modules/building.md`, `docs/edge-modules/retail.md`.
- **Riscos/limitações:** contagem por variância é frágil. Direção por gradiente não demonstrada. Analytics de varejo esbarram na LGPD.
- **Relevância para a plataforma (M01, M02, M03, M13):** alta para insights de negócio. KPIs de ocupação, fila, permanência, giro e economia de energia sobre eventos sintéticos (pandas/polars sobre SQLite), com dashboards em Recharts/ECharts.

#### EH-06 — Skills médicas experimentais (feature-gated, não clínicas)

- **O que faz:** sinaliza candidatos a pausas tipo apneia, anomalias de ritmo cardíaco, desconforto respiratório, proxies de marcha/risco de queda e movimento rítmico tipo convulsão.
- **Como faz:** regras sobre BPM e energia (durações sustentadas, janelas de variabilidade, análise espectral, autocorrelação). Só compilam com uma feature não padrão. Cada cabeçalho traz aviso obrigatório (experimental, não validado clinicamente, não é dispositivo médico), conferido por **teste de texto do código-fonte**.
- **Requisitos para implementar:**
  - Hardware: nó CSI e equipamentos clínicos de referência.
  - Software: Rust/Python.
  - Dados: datasets clínicos com aprovação ética.
  - Competências: engenharia biomédica, regulação (ANVISA/FDA/CE).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Todas são DATA-GATED. Os testes de rotulagem garantem a presença dos avisos. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/med_sleep_apnea.rs`, `med_cardiac_arrhythmia.rs`, `med_respiratory_distress.rs`, `med_gait_analysis.rs`, `med_seizure_detect.rs`, `tests/honest_labeling.rs`, `docs/edge-modules/medical.md`, `docs/adr/ADR-160-edge-skill-library-honest-labeling.md`.
- **Riscos/limitações:** risco regulatório e de falsa segurança. "Convulsão" é só movimento rítmico. Dependem de BPM não validados.
- **Relevância para a plataforma (M04, M05, M07, M09, M10):** o valor é a governança: feature flag desligada por padrão, avisos verificados automaticamente (pytest varrendo docstrings e strings de UI) e lista DATA-GATED explícita. Os módulos continuam PLANNED/BLOCKED.

#### EH-07 — Módulos exóticos e de pesquisa

- **O que faz:** estágio de sono do tipo PSG (heurístico), proxies de afeto, clusters de gesto tipo língua de sinais, extração de tempo e batida de regência, crescimento de plantas, "ghost hunter" (perturbações e respiração oculta em sala sem presença), detecção de chuva por vibração, sincronização respiratória entre pessoas, "cristal temporal" (coordenação periódica) e embedding hiperbólico para localização hierárquica.
- **Como faz:** autocorrelação, correlação cruzada entre grupos de subportadoras, deriva lenta com oscilação diurna, contagem de grupos com variância elevada, DTW/clusters, geometria hiperbólica e limiares para afeto.
- **Requisitos para implementar:**
  - Hardware: nó CSI ou nenhum.
  - Software: numpy.
  - Dados: rótulos específicos (PSG, afeto autorrelatado, pluviômetro).
  - Competências: pesquisa em sensoriamento RF.
- **Evidência e maturidade:** `RESEARCH` / `SYNTHETIC_OR_SIMULATED`. Ghost hunter, chuva e cristal temporal acertam em sinais plantados com N pequeno; o cristal temporal tem ressalva documentada (não separa duplicação de período). Afeto, sono e sinais são DATA-GATED. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/exo_dream_stage.rs`, `exo_emotion_detect.rs`, `exo_gesture_language.rs`, `exo_music_conductor.rs`, `exo_plant_growth.rs`, `exo_ghost_hunter.rs`, `exo_rain_detect.rs`, `exo_breathing_sync.rs`, `exo_time_crystal.rs`, `exo_hyperbolic_space.rs`, `exo_happiness_score.rs`, `docs/edge-modules/exotic.md`.
- **Riscos/limitações:** afeto e sono são eticamente sensíveis. Os nomes chamativos induzem a erro.
- **Relevância para a plataforma (M04, M06, M08, M09):** baixa a média. A detecção de perturbação em ambiente supostamente vazio e a de vibração ajudam o diagnóstico de interferência no onboarding e no M08. Afeto e sono ficam BLOCKED.

#### EH-08 — Inteligência de sinal: gate de coerência, atenção por subportadora, compressão temporal, recuperação esparsa, matching de pessoas e transporte ótimo

- **O que faz:** classifica cada quadro (aceitar, só prever, rejeitar, recalibrar), estima o foco espacial da atividade, mantém histórico longo comprimido, recupera subportadoras nulas, mantém IDs estáveis de até 4 pessoas e detecta "movimento sutil" por mudança de distribuição.
- **Como faz:** z-score do índice de coerência com histerese; softmax por tiles de subportadoras com entropia suavizada; quantização em três camadas (quente/morna/fria); ISTA para nulos; atribuição gulosa por distância L2; distância de Wasserstein fatiada com projeções fixas.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy/scipy, POT (MIT), `scipy.optimize.linear_sum_assignment`.
  - Dados: cenários com pessoas rotuladas e dropouts.
  - Competências: estatística robusta, otimização esparsa, transporte ótimo.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. A atenção localizou o pico em 8 de 8 casos; o transporte ótimo acertou 1+1; o matching teve zero trocas em 40 quadros. **A recuperação esparsa reconstrói pior do que deixar os nulos** (evidência negativa declarada). Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/sig_coherence_gate.rs`, `sig_flash_attention.rs`, `sig_temporal_compress.rs`, `sig_sparse_recovery.rs`, `sig_mincut_person_match.rs`, `sig_optimal_transport.rs`, `docs/edge-modules/signal-intelligence.md`.
- **Riscos/limitações:** a "flash attention" é só softmax por tiles. "Min-cut" e "Hungarian" são aproximações gulosas. A compressão com perda pode distorcer análises.
- **Relevância para a plataforma (M02, M08, M14, M15, M16):** alta. O gate com histerese alimenta o campo de qualidade do contrato. A compressão em camadas inspira a política de retenção e downsampling. A recuperação esparsa não deve ser reimplementada.

#### EH-09 — Aprendizado adaptativo no dispositivo

- **O que faz:** gestos ensináveis (três repetições depois de quietude), anomalia por atratores dinâmicos, auto-otimização de limiares com restrições de segurança e classificador linear de zonas com aprendizado contínuo.
- **Como faz:** protocolo de matrícula por DTW; estado da sala como sistema dinâmico com expoente de Lyapunov; hill-climbing com limites e rollback; Elastic Weight Consolidation (Kirkpatrick et al.) com Fisher aproximada.
- **Requisitos para implementar:**
  - Hardware: nenhum para simulação.
  - Software: river (BSD), scikit-learn.
  - Dados: feedback do operador e sequências rotuladas.
  - Competências: aprendizado online, sistemas dinâmicos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. A matrícula foi medida, mas **o replay idêntico não disparou o match**, e isso foi reportado. A auditoria aponta estouro de ID de gesto aprendido. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/lrn_dtw_gesture_learn.rs`, `lrn_anomaly_attractor.rs`, `lrn_meta_adapt.rs`, `lrn_ewc_lifelong.rs`, `docs/edge-modules/adaptive-learning.md`.
- **Riscos/limitações:** o auto-ajuste pode derivar. Lyapunov é instável. O ganho do EWC é incerto.
- **Relevância para a plataforma (M06, M08, M12, M16):** média. Vale aproveitar o ajuste de limiares com feedback explícito do operador, limites e rollback auditável, além de river para drift. EWC é expansão de IA e fica PLANNED.

#### EH-10 — Raciocínio espacial, temporal e autônomo no dispositivo (incluindo módulos "quantum-inspired")

- **O que faz:**
  - busca aproximada de fingerprints;
  - pessoa dominante numa cena;
  - rastreamento por zona com rede de spikes;
  - rotinas diárias e desvios;
  - invariantes de segurança em lógica temporal;
  - planejamento de quais módulos ativar;
  - inferência simbólica de contexto;
  - resiliência de topologia da malha;
  - métricas "inspiradas em quântica".
- **Como faz:** HNSW de camada única; PageRank sobre correlação entre grupos de fase; neurônios leaky integrate-and-fire com STDP; LCS sobre símbolos por minuto em 24 h; monitor LTL com regras globais/eventuais e contraexemplos; GOAP com A*; forward-chaining com detecção de contradição; Stoer-Wagner simplificado; esfera de Bloch e iteração tipo Grover sobre hipóteses.
- **Requisitos para implementar:**
  - Hardware: nenhum (malha para self-healing).
  - Software: networkx, hnswlib.
  - Dados: semanas de eventos e fingerprints rotulados.
  - Competências: grafos, lógica temporal, planejamento, sistemas de regras.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. O rastreador de spikes acertou 4 de 4 só com estímulo esparso e colapsa com estímulo denso (ressalva documentada). Os demais só têm testes unitários. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/spt_micro_hnsw.rs`, `spt_pagerank_influence.rs`, `spt_spiking_tracker.rs`, `tmp_pattern_sequence.rs`, `tmp_temporal_logic_guard.rs`, `tmp_goap_autonomy.rs`, `aut_psycho_symbolic.rs`, `aut_self_healing_mesh.rs`, `qnt_quantum_coherence.rs`, `qnt_interference_search.rs`, `docs/edge-modules/spatial-temporal.md`, `docs/edge-modules/autonomous.md`.
- **Riscos/limitações:** rótulos de marketing para técnicas clássicas. GOAP sem supervisão humana. Rotina diária é dado comportamental sensível.
- **Relevância para a plataforma (M08, M13, M14):** média-alta. Monitor de invariantes estilo LTL e regras forward-chaining como camada de "guardas" sobre eventos em Python puro; networkx (BSD) e hnswlib (Apache-2.0) para fingerprints. Evitar rótulos "quânticos".

#### EH-11 — Integridade do fluxo CSI, perfil comportamental e endurecimento de fronteira

- **O que faz:** detecta replay, injeção e jamming. Mantém um perfil comportamental de 6 dimensões do ambiente. Impede que valores não finitos corrompam o estado e aplica as correções de uma auditoria de segurança.
- **Como faz:** replay por hash FNV-1a de features quantizadas contra um anel; injeção pela fração de subportadoras com saltos grandes; jamming por proxy de SNR; perfil com Welford e z-scores combinados com indicador de maturidade; sanitização de NaN/Inf; buffers por instância em vez de estáticos.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Python, river.
  - Dados: capturas com ataques conhecidos.
  - Competências: segurança de sensores, auditoria de código embarcado.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Os testes de fronteira mostram que um NaN cru trava a coerência e que a versão sanitizada se recupera. A auditoria lista 15 achados e as correções. O falso replay por quantização continua como limitação. Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/ais_prompt_shield.rs`, `ais_behavioral_profiler.rs`, `lib.rs`, `docs/security-audit-wasm-edge-vendor.md`, `docs/edge-modules/ai-security.md`.
- **Riscos/limitações:** o nome "prompt shield" é enganoso. Falso replay em ambiente estático. Sem autenticação criptográfica do fluxo.
- **Relevância para a plataforma (M15):** alta. Rejeição de não finitos (validadores Pydantic), detecção de replay por sequência e hash, drift de perfil (river) e a auditoria como checklist (divisão por zero, overflow, limites de buffer).

#### EH-12 — Pipeline unificado de skills no host e harness de validação honesta (ADR-160/163)

- **O que faz:** registra todas as skills (59 no padrão, 64 com o tier médico) atrás de uma interface uniforme e roda todas por quadro. Mede a detecção em sinais com verdade plantada, mede latência no host e garante, por teste, que avisos e renomeações honestas permaneçam no código.
- **Como faz:** uma visão emprestada do quadro com todos os insumos; adaptadores gerados por macro; matriz de confusão sobre sinais determinísticos (LCG semeado); benches criterion; testes textuais de presença de avisos; conformidade de orçamento medida no host. O vocabulário é: MEASURED-on-synthetic, MEASURED-on-host, CLAIMED (ESP32) e DATA-GATED.
- **Requisitos para implementar:**
  - Hardware: máquina comum.
  - Software: pytest, hypothesis, pytest-benchmark.
  - Dados: geradores determinísticos.
  - Competências: testes, metrologia de desempenho, cultura de evidência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. São declarados 631/669 testes (não reexecutados). As latências de host são explicitamente "não equivalentes ao ESP32". Caminhos: `v2/crates/wifi-densepose-wasm-edge/src/pipeline_all.rs`, `skill_registry.rs`, `tests/pipeline_all.rs`, `tests/synthetic_validation.rs`, `tests/honest_labeling.rs`, `tests/budget_compliance.rs`, `benchmarks/edge-skills/RESULTS.md`, `benchmarks/edge-latency/RESULTS.md`, `docs/adr/ADR-163-edge-latency-measurement.md`.
- **Riscos/limitações:** validação sintética prova a matemática, não o campo. N pequeno. Testes de texto garantem rótulos, não comportamento.
- **Relevância para a plataforma (M12, M15, M16):** muito alta. O vocabulário de evidência e os testes que impedem remover avisos casam com L0/IMPLEMENTED_SYNTHETIC e com o ORIGINALITY_REGISTER. Um "registro de detectores" com interface uniforme em Python segue o mesmo padrão.

#### EH-13 — Bindings WASM para navegador: painel WiFi-Mat de resposta a desastres

- **O que faz:** biblioteca para JavaScript com eventos de desastre, zonas (retângulo, círculo, polígono), sobreviventes com triagem e cor, alertas, estatísticas, renderização em canvas, ingestão de CSI com respiração leve e WebSocket.
- **Como faz:** estado em Rust compilado para wasm32 com API exposta ao JS. A respiração usa cruzamentos por zero, e há uma função de simulação para demonstração.
- **Requisitos para implementar:**
  - Hardware: navegador.
  - Software: wasm-pack, wasm-bindgen.
  - Dados: cenários de resgate.
  - Competências: WASM no browser, triagem.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 4 testes no navegador; detecções simuladas. Caminhos: `v2/crates/wifi-densepose-wasm/src/lib.rs`, `mat.rs`, `README.md`.
- **Riscos/limitações:** domínio de vida humana sem validação. Cruzamentos por zero são frágeis.
- **Relevância para a plataforma (M01, M04):** baixa. Zonas e triagem podem ser TypeScript nativo no Next.js. O caso de resgate deve ser, no máximo, demonstração rotulada. Ver também MB-01 a MB-07.

#### EH-14 — Ingestão de frames ESP32 (ADR-018), agregador UDP multi-nó, ponte para o pipeline e pacotes de sincronização

- **O que faz:** analisa de forma determinística o quadro binário de CSI e reconhece os pacotes "irmãos" do mesmo socket para roteá-los. Agrega vários nós com contagem de perdas, converte I/Q em amplitude e fase e recupera timestamps alinhados à malha.
- **Como faz:** cabeçalho fixo mais I/Q de 8 bits com contagem de subportadoras variável (HT 64, HE-SU 256). **Nunca gera dado**: retorna erro tipado. O agregador mantém estado por nó (lacunas de sequência) e entrega por canal. O pacote de sincronização pareia (nó, sequência) com o fluxo e informa a época alinhada com offset suavizado.
- **Requisitos para implementar:**
  - Hardware: ESP32-S3/C6 e rede local.
  - Software: Python (struct, asyncio).
  - Dados: capturas reais para regressão.
  - Competências: protocolos binários, OFDM HT/HE, UDP.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. Dois payloads reais de um ESP32-C6 (HE-SU 256 e HT 64) servem como fixtures de regressão. Contagem de testes: parser 18, sync 15, agregador 5, ponte 4. É evidência de formato de fio, não de qualidade. Caminhos: `v2/crates/wifi-densepose-hardware/src/esp32_parser.rs`, `csi_frame.rs`, `bridge.rs`, `aggregator/mod.rs`, `sync_packet.rs`, `tests/adr110_live_frames.rs`, `firmware/esp32-csi-node/main/rv_feature_state.h`.
- **Riscos/limitações:** UDP sem autenticação no crate. Há um identificador de pacote com rótulos diferentes entre firmware e parser. O suporte declarado a Intel 5300 não tem código.
- **Relevância para a plataforma (M12, M16):** alta como referência para o `packet_lab` da plataforma: parser que nunca fabrica dados, reconhecimento de pacotes irmãos, contagem de lacunas por nó como métrica de qualidade. A ingestão real fica PLANNED atrás de flag. O `esp-csi` da Espressif (Apache-2.0) é a referência pública. Ver também FW-01.

#### EH-15 — Malha multiestática: agendamento TDM, beacons autenticados, transporte QUIC (modelado) e camada de abstração de rádio

- **O que faz:** coordena a captura multiestática (cada nó transmite no seu slot, gerando N·(N−1) enlaces). Autentica beacons, modela transporte seguro e espelha a camada de abstração de rádio e o plano de malha do firmware.
- **Como faz:** slots TDMA com guarda e estimativa de deriva de cristal; HMAC-SHA256 truncado com nonce, janela anti-replay e níveis permissivo/transicional/estrito; QUIC só como transições de estado; trait de rádio com modos e perfis e um rádio mock; CRC32.
- **Requisitos para implementar:**
  - Hardware: 3–4 ESP32-S3 ou simulação.
  - Software: cryptography (HMAC/Ed25519), aioquic (BSD) se necessário.
  - Dados: logs de sincronização.
  - Competências: TDMA, sincronização de relógios, criptografia.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: tdm 18, secure_tdm 36, quic 34, radio 8. O connect do QUIC só altera estado. **A configuração padrão usa chave de teste embutida e nível transicional, que aceita não autenticados.** Caminhos: `v2/crates/wifi-densepose-hardware/src/esp32/tdm.rs`, `secure_tdm.rs`, `quic_transport.rs`, `v2/crates/wifi-densepose-hardware/src/radio_ops.rs`, `docs/adr/ADR-081-adaptive-csi-mesh-firmware-kernel.md`.
- **Riscos/limitações:** chave padrão embutida. QUIC não implementado. Deriva real não demonstrada.
- **Relevância para a plataforma (M14, M15, M16):** média. Modelar agenda de captura, perfis e saúde de nós no simulador multi-sensor. Nunca usar chaves padrão. Multiestático real fica BLOCKED.

#### EH-16 — Codecs vendor-neutros e simuladores determinísticos de CSI/radar (MediaTek, Qualcomm Atheros, Realtek)

- **O que faz:** formatos de fio próprios (não a ABI do fabricante) para CSI MIMO e relatórios de radar, com simuladores de linha de comando que geram quadros determinísticos para arquivo ou UDP, sempre marcados como sintéticos.
- **Como faz:** cabeçalho versionado com perfil de chipset, tipo de PPDU e contagens; flags CALIBRATED, SYNTHETIC, SATURATED, sincronizado e "perda anterior"; CRC32; PRNG semeado com fasores mais ruído.
- **Requisitos para implementar:**
  - Hardware: nenhum para simulação.
  - Software: struct, zlib.crc32, `numpy.random.Generator`.
  - Dados: sementes e parâmetros.
  - Competências: formatos de fio versionados, MIMO-OFDM.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. De 8 a 11 testes por codec. Os cabeçalhos dizem explicitamente que não são a ABI do fabricante. Caminhos: `v2/crates/wifi-densepose-hardware/src/mediatek_csi.rs`, `qualcomm_csi.rs`, `realtek_csi.rs`, `rtl8720f.rs`, `src/bin/mediatek-csi-sim.rs`, `src/bin/qualcomm-csi-sim.rs`, `src/bin/realtek-csi-sim.rs`, `v2/crates/wifi-densepose-hardware/README.md`.
- **Riscos/limitações:** fasores simples não reproduzem multipercurso. Hardware real depende de SDKs fechados. Formatos proliferam.
- **Relevância para a plataforma (M12, M16):** alta como padrão: codec próprio versionado com CRC, flag SYNTHETIC obrigatória e simulador semeado, alinhados ao modo `synthetic-native` e ao contrato aditivo.

#### EH-17 — Ponte MediaTek mt76 (MT7981) com portões de proveniência

- **O que faz:** processo que consome CSI do driver mt76 e o converte no formato próprio para a ingestão do servidor, com gravação e replay. Separa rigorosamente dado físico de dado sintético.
- **Como faz:**
  - Agrupa cadeias em quadros pelo marcador de "última cadeia" por transmissor. Grupos incompletos são descartados e contados, **nunca preenchidos com zero**.
  - Datagramas sem identidade viram 1x1 por honestidade. Campos ausentes recebem sentinela e PPDU desconhecido.
  - **Sintético é "pegajoso"**: sidecar de proveniência, infixo no nome ou cabeçalho. O replay exige escolha explícita (sintético ou "capturado em" modelo/firmware).
  - A escuta exige allowlist CIDR. CALIBRATED nunca é definido; dado físico recebe "physical-unvalidated".
- **Requisitos para implementar:**
  - Hardware: roteador MT7981/MT7976 com OpenWrt e patch CSI.
  - Software: OpenWrt 24.10, mt76 com patch, ferramentas de dump.
  - Dados: dumps com atestação.
  - Competências: OpenWrt/drivers, MIMO-OFDM, governança de proveniência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. Um único registro real (WL-WN586X3) percorreu o caminho, como verificação de caminho, não de qualidade, e fica fora do repositório. Cerca de 90 testes. Fixtures fabricadas com sidecar. Caminhos: `v2/crates/wifi-densepose-mtk-bridge/README.md`, `src/assemble.rs`, `src/provenance.rs`, `src/listen_allow.rs`, `src/udp_in.rs`, `tests/provenance_gate.rs`, `tests/hardware_capture.rs`, `docs/adr/ADR-267-mediatek-mimo-csi-wire-protocol.md`.
- **Riscos/limitações:** um único registro. O UDP perde a estrutura MIMO. Exige patch de terceiros. O registro real contém MAC de cliente.
- **Relevância para a plataforma (M12, M15, M16):** muito alta como padrão de governança: sintético pegajoso, atestação explícita do operador, allowlist obrigatória, rótulo "physical-unvalidated" diferente de "calibrated" e descarte contado em vez de zero-fill. Tudo em Python (ipaddress, sidecar JSON, Pydantic). Hardware fica PLANNED. Ver também FW-15.

#### EH-18 — Modelo de protocolo IEEE 802.11bf (WLAN Sensing) para compatibilidade futura

- **O que faz:** superfície tipada dos procedimentos padronizados (setup de medição, instâncias, relatórios, sensing-by-proxy e término), com negociação de capacidades e **ConsentMode obrigatório em todo setup** (somente laboratório, consentimento explícito, política gerenciada ou desabilitado). Uma ponte mapeia o CSI oportunista atual no caminho de relatório.
- **Como faz:** FSM de sessão determinística (ocioso, negociando, ativo, terminando), registro de setups com rejeição por colisão e capacidade, transporte simulado e acumulação circular de fase.
- **Requisitos para implementar:**
  - Hardware: nenhum hoje.
  - Software: enum/dataclasses ou `transitions` (MIT).
  - Dados: nenhum.
  - Competências: IEEE 802.11, FSMs, privacy by design.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 26 testes. Declara-se não certificado e sem silício compatível. Caminhos: `v2/crates/wifi-densepose-hardware/src/ieee80211bf/mod.rs`, `types.rs`, `session.rs`, `transport.rs`, `tests_fsm.rs`, `tests_sbp.rs`, `docs/adr/ADR-153-ieee-802-11bf-sensing-protocol-layer.md`.
- **Riscos/limitações:** é uma interpretação própria de um padrão de acesso pago.
- **Relevância para a plataforma (M14, M15, M16):** alta em governança. Um ConsentMode obrigatório pode entrar de forma aditiva no contrato 2.0.0 (bloco de privacidade), e a FSM serve de modelo para o onboarding. Suporte real fica PLANNED.

#### EH-19 — Contrato de provedores RF de fornecedores (ADR-270), decodificadores estritos e simulador

- **O que faz:** camada segura por capacidade para telemetria de fornecedores Wi-Fi/IoT. Impede que RSSI, ocupação de nuvem ou inventário de rede sejam tratados como CSI complexo.
- **Como faz:** o descritor declara ID, capacidades (CSI complexo, sensoriamento derivado, telemetria, somente rede, não suportado) e disponibilidade (disponível, credenciais, contrato, experimental). Os decodificadores rejeitam campos desconhecidos e usam allowlists de métricas. O simulador gera JSONL/UDP com flag sintética, e o UDP canônico só aceita sintético.
- **Requisitos para implementar:**
  - Hardware: equipamentos e contas reais.
  - Software: FastAPI e Pydantic (`extra='forbid'`).
  - Dados: payloads documentados.
  - Competências: integração de APIs, capability security.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 2 testes no contrato e 28 nos decodificadores. Todos os descritores têm "hardware não validado". Caminhos: `v2/crates/wifi-densepose-hardware/src/vendor_rf.rs`, `src/bin/vendor-rf-sim.rs`, `v2/crates/wifi-densepose-sensing-server/src/vendor_*.rs`, `docs/vendor-rf-providers.md`, `docs/adr/ADR-270-vendor-rf-sensing-integration-program.md`.
- **Riscos/limitações:** integrações reais exigem contratos comerciais. Esquemas presumidos.
- **Relevância para a plataforma (M01, M02, M13, M15):** alta como padrão: enum de capacidade com validação estrita para qualquer conector futuro. Integrações comerciais violam o custo zero. Alternativas livres: Home Assistant, MQTT, OpenWrt/ubus. Ver também SS-20.

#### EH-20 — Varredura Wi-Fi multi-BSSID por RSSI e pipeline de sensoriamento por RSSI

- **O que faz:** descobre e acompanha os APs visíveis (Windows, Linux, macOS), monta quadros multi-AP e estima presença, movimento, respiração grosseira, qualidade e postura por fingerprint, apenas com RSSI de equipamentos comuns.
- **Como faz:**
  - Arquitetura hexagonal: tipos de valor, registro com Welford por AP e expiração, mapeamento estável de BSSID para índice, e porta de varredura com adaptadores (netsh, wlanapi nativo com fallback, `iw`, CoreWLAN via helper).
  - Pipeline de 8 estágios: gate preditivo por resíduo EMA, pesos softmax por BSSID, correlação de Pearson com clusterização BFS, movimento ponderado, respiração por passa-banda IIR e cruzamentos por zero, gate de qualidade de três fatores, fingerprint por cosseno e orquestrador.
- **Requisitos para implementar:**
  - Hardware: qualquer notebook com Wi-Fi (custo zero).
  - Software: subprocess/pywifi (MIT)/nmcli.
  - Dados: séries de RSSI com referência e templates por ambiente.
  - Competências: arquitetura hexagonal, RSSI, privacidade de dados de rede.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 169 testes, 56 deles só no parser do netsh. O throughput declarado é de computação, não de aquisição. Não há dataset validado. Caminhos: `v2/crates/wifi-densepose-wifiscan/src/lib.rs`, `domain/registry.rs`, `port/scan_port.rs`, `adapter/netsh_scanner.rs`, `adapter/wlanapi_native.rs`, `adapter/linux_scanner.rs`, `adapter/macos_scanner.rs`, `pipeline/orchestrator.rs`, `docs/adr/ADR-022-windows-wifi-enhanced-fidelity-ruvector.md`, `docs/adr/ADR-025-macos-corewlan-wifi-sensing.md`.
- **Riscos/limitações:** a taxa de varredura (cache do driver de vários segundos) fica abaixo de Nyquist para respiração, o que torna **respiração por RSSI fisicamente implausível** nesse caminho. A saída do netsh varia com o idioma. BSSIDs de terceiros podem ser dado pessoal.
- **Relevância para a plataforma (M01, M02, M04, M08):** muito alta, porque é o único "hardware" de custo zero. Reimplementável com portas e adaptadores (netsh, nmcli/iw, pywifi) para presença grossa, ocupação relativa e fingerprint do ambiente, com nível de evidência próprio (separado de L0), atrás de flag e com hash de BSSID. Não prometer respiração por RSSI. Ver também PY-09.

#### EH-21 — HAL de sensores multimodal (ruview-hal) com evidência e proveniência

- **O que faz:** leva qualquer modalidade (CSI, 802.11bf, BLE, UWB, mmWave, acústica, câmera, lidar, IMU ou rótulo customizado validado) a uma observação canônica da ontologia, com descritor de sensor, incerteza, nível de evidência e proveniência.
- **Como faz:** interface com "descrever" e "normalizar". A normalização é **infalível**: entrada malformada vira observação UNKNOWN ou degradada, nunca erro nem pânico. Rótulos são validados. Os adaptadores de referência (CSI e IMU) são sempre sintéticos e no nível mais baixo, sem poder subir. Não há I/O.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Pydantic e `typing.Protocol`.
  - Dados: fixtures.
  - Competências: modelagem de domínio, ontologias, proveniência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 8 testes. Consumido por fusão, sensoriamento ativo e ganho de informação. Caminhos: `v2/crates/ruview-hal/src/lib.rs`, `adapter.rs`, `descriptor.rs`, `label.rs`, `modality.rs`, `observation.rs`, `v2/crates/ruview-ontology/src/provenance.rs`, `docs/adr/ADR-320-sensor-hal.md`.
- **Riscos/limitações:** só CSI e IMU sintéticos têm adaptador. A escala de evidência difere da escala da plataforma.
- **Relevância para a plataforma (M14, M15):** muito alta. Uma porta de domínio "adaptador de sensor" com descrição e normalização infalível, UNKNOWN de primeira classe, modalidade enumerada e proveniência obrigatória. Ver também WM-11.

### 4.4 Firmware ESP32/OpenWrt, WiFi Veil e BFI

**Escopo.** A área tem quatro blocos:

1. Firmware ESP-IDF em C para ESP32-S3 (produção) e ESP32-C6 (pesquisa Wi-Fi 6) em `firmware/esp32-csi-node`.
2. Caminho experimental de CSI em roteadores MediaTek MT7981 via OpenWrt.
3. Ferramentas Python de captura e decodificação de beamforming feedback (BFI), mais um pipeline offline de aprendizado.
4. WiFi Veil/privshield, uma contramedida de privacidade modelada sinteticamente.

O transporte e a cadência do ESP32 têm evidência em hardware real, assim como o invariante de ocupação. Nenhuma acurácia de sensoriamento foi validada.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| FW-01 | Captura de CSI no ESP32 e streaming binário por UDP | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M01, M02, M12, M16 |
| FW-02 | DSP de borda (tiers 0–2): presença, respiração, FC, queda, compressão | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M04, M05, M07 |
| FW-03 | Invariantes de evidência na borda: ocupação fail-closed e relógio DSP | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M02, M15, M16 |
| FW-04 | Runtime WASM (tier 3) com contêiner "assinado" e API HTTP | PARTIAL | UNCLEAR | M12, M13 |
| FW-05 | OTA com rollback e verificação de saúde no primeiro boot | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15 |
| FW-06 | Provisionamento NVS e configuração em runtime | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15 |
| FW-07 | Onboarding USB por desafio com nonce e identidade | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M16, M15 |
| FW-08 | Kernel adaptativo e plano de malha (ADR-081) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M14, M16 |
| FW-09 | Sincronização temporal entre nós e gating alinhado | PARTIAL | REAL_HARDWARE_EVIDENCE | M02, M03, M14, M16 |
| FW-10 | Extensões ESP32-C6 Wi-Fi 6 (HE-LTF, TWT, soft-AP HE, LP-core, antena) | PARTIAL | REAL_HARDWARE_EVIDENCE | M12, M16 |
| FW-11 | Fusão com radar mmWave via UART | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M04, M05, M14 |
| FW-12 | Operação de frota: térmico, watchdog, log de saúde, energia, coordenação | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15 |
| FW-13 | Interface local: display AMOLED e LED | IMPLEMENTED_UNTESTED | NONE | NONE |
| FW-14 | Testes sem hardware (QEMU, fuzzing), CI e releases | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M16 |
| FW-15 | CSI em roteadores MT7981 via OpenWrt com portão de proveniência | PARTIAL | REAL_HARDWARE_EVIDENCE | M08, M12, M15 |
| FW-16 | Captura e decodificação de BFI VHT/HE com oráculo independente | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M08, M12, M15 |
| FW-17 | Pipeline offline CSI/BFI com controles experimentais e holdout selado | RESEARCH | SYNTHETIC_OR_SIMULATED | M06, M12, M15 |
| FW-18 | WiFi Veil / privshield: contramedida de privacidade contra BFI | PARTIAL | SYNTHETIC_OR_SIMULATED | M15, M08 |
| FW-19 | Modelo de domínio de hardware (DDD) e guia de build/BOM | DOC_ONLY | NONE | M12, M14, M16 |

#### FW-01 — Captura de CSI no ESP32 e streaming binário por UDP

- **O que faz:** registra o callback de CSI do driver, serializa cada quadro (I/Q por subportadora e antena, RSSI, ruído, canal, PPDU, flags) num formato binário versionado e envia por UDP a um agregador. Também oferece: filtro por MAC de origem, sobreposição de canal, salto de canais por timer, auto-ping ao gateway para gerar tráfego OFDM quando o ambiente está ocioso, saneamento do primeiro word inválido e limitação de taxa do callback.
- **Como faz:** produtor/consumidor dual-core. No núcleo de rádio, o callback aplica um gate de taxa (por tempo, ou por "bucket" de época sincronizada quando há sincronia válida), filtra MAC, sanitiza e empurra para um ring buffer SPSC lock-free. O envio usa um socket único com backoff exponencial em falta de buffers. Um modo diagnóstico registra (MAC, sequência) para medir quadros comuns entre nós.
- **Requisitos para implementar:**
  - Hardware: ESP32-S3 (PSRAM, 4–8 MB) ou C6; AP com tráfego; host na mesma LAN.
  - Software: ESP-IDF 5.4/5.5, esptool, Docker opcional.
  - Dados: tráfego ambiente ou auto-ping.
  - Competências: C/FreeRTOS, API CSI da Espressif, lwIP, OFDM.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. Testes host de saneamento e fuzzing libFuzzer+ASan do serializador no CI. Relatórios físicos de 5 minutos em S3 e em dois C6 mostram zero falhas de envio, parser ou reboot. **Os próprios relatórios dizem que isso prova transporte, não acurácia.** A injeção de NDP é um placeholder sem chamadores. Caminhos: `firmware/esp32-csi-node/main/csi_collector.c`, `stream_sender.c`, `main.c`, `test/test_csi_sanitize.c`, `test/fuzz_csi_serialize.c`, `docs/validation/2026-08-31-esp32-s3-rate-aware-transport.md`, `docs/validation/2026-08-31-esp32-c6-rate-aware-sensing.md`.
- **Riscos/limitações:** a cadência depende do tráfego recebido. Quadros contêm MACs de terceiros. Sem autenticação nem cifragem. A variante com display tinha falso positivo de painel que zerava a CSI.
- **Relevância para a plataforma (M01, M02, M12, M16):** alta como referência para a fase de prontidão de hardware. A plataforma pode especificar seu próprio contrato de pacote (versão, sequência, CRC, timestamp, proveniência) com ingestão UDP em loopback ou allowlist. Um firmware próprio pode ser escrito sobre o exemplo público `esp-csi` (Apache-2.0). Nenhum hardware deve ser comprado sem decisão do usuário. Ver também EH-14.

#### FW-02 — Pipeline DSP de borda (tiers 0–2): presença, respiração, frequência cardíaca, queda e compressão

- **O que faz:** o tier 0 repassa o bruto. O tier 1 extrai fase com unwrap, estatísticas incrementais, seleção top-K por variância e compressão delta. O tier 2 estima respiração e FC, presença, queda e um "slot count" multi-pessoa, e emite pacotes de vitais e vetor de features a 1 Hz.
- **Como faz:** fase por atan2 e unwrap; Welford por subportadora; biquads IIR passa-banda nas bandas respiratória e cardíaca públicas; BPM por cruzamento de zero com alternativa por autocorrelação; presença por energia contra limiar média + k·desvio aprendido no boot, com histerese e debounce; queda por "aceleração" de fase; XOR + RLE contra o quadro anterior. O "número de pessoas" é uma heurística de capacidade de slots, como o README admite.
- **Requisitos para implementar:**
  - Hardware: ESP32-S3 dual-core (C6 em taxa reduzida), ou QEMU.
  - Software: ESP-IDF, libm, QEMU da Espressif.
  - Dados: gravações com referência (cinta, oxímetro, anotação de presença e queda).
  - Competências: DSP clássico, estatística online, avaliação com baseline.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Teste host de vitais, contagem e presença, fuzz do enfileiramento e execução em QEMU com gerador mock de 10 cenários. Nenhum relatório compara com referência rotulada. Caminhos: `firmware/esp32-csi-node/main/edge_processing.c`, `edge_processing.h`, `test/test_vitals_count_presence.c`, `test/fuzz_edge_enqueue.c`, `main/mock_csi.c`, `firmware/esp32-csi-node/README.md`.
- **Riscos/limitações:** o limiar depende de sala vazia no boot. Ventiladores, micro-ondas e variações do AP geram fantasmas. "Contagem" não mede ocupação. Risco de alegação clínica.
- **Relevância para a plataforma (M01, M02, M04, M05, M07):** alta como inspiração algorítmica para o motor sintético. As técnicas são públicas (Welford, biquad, autocorrelação, histerese, média + kσ) e reimplementáveis em numpy/scipy, com M04/M05/M07 como PLANNED/BLOCKED. Ver também SV-16 e SS-05.

#### FW-03 — Invariantes de evidência na borda: ocupação fail-closed e relógio DSP governado por taxa

- **O que faz:** garante que um pacote de "sala vazia" nunca carregue contagem não nula. Desacopla a taxa dos filtros (relógio DSP fixo por alvo) da taxa bruta de CSI e reporta as duas no diagnóstico de 1 s.
- **Como faz:** uma função pura de "evidência de contagem" força zero quando a presença é falsa. O pipeline decima a CSI bruta para o relógio DSP configurado, para que filtros calibrados para uma taxa não sejam aplicados silenciosamente a outra.
- **Requisitos para implementar:**
  - Hardware: um C6/S3 e um nó-controle.
  - Software: firmware com diagnósticos, servidor que registre e script de captura.
  - Dados: janelas de sala vazia suficientes.
  - Competências: critérios de aceitação e invariantes.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. Relatório de 2026-08-31: em 300 s, o nó atualizado teve zero pacotes "ausente com contagem", enquanto os nós-controle exibiram a contradição em todos os pacotes ausentes. O relatório de taxa mostra o relógio DSP estável. **Os relatórios declaram que não é acurácia de contagem.** Caminhos: `firmware/esp32-csi-node/main/edge_processing.c`, `docs/validation/2026-08-31-esp32-c6-occupancy-integrity.md`, `docs/validation/2026-08-31-esp32-c6-rate-aware-sensing.md`, `docs/adr/ADR-346-fail-closed-edge-occupancy-evidence.md`, `docs/adr/ADR-347-rate-aware-esp32-temporal-sensing.md`.
- **Riscos/limitações:** o invariante evita contradição lógica, não melhora acurácia. As execuções são curtas, e um nó não atingiu o mínimo de pacotes ausentes.
- **Relevância para a plataforma (M02, M15, M16):** muito alta e de baixo custo. "Invariante fail-closed + relatório de aceite reprodutível" cabe nos validadores Pydantic/Zod do contrato 2.0.0 (presença falsa implica ocupação zero; taxa de amostragem declarada e verificada), com testes Hypothesis.

#### FW-04 — Runtime WASM programável (tier 3) com contêiner assinado e API de gestão HTTP

- **O que faz:** carrega, inicia, para e descarrega módulos WASM em tempo de execução, com host API (fase, amplitude, variância, vitais, presença, eventos) executada por quadro depois do DSP.
- **Como faz:** WASM3 embarcado, slots com arenas em PSRAM, ciclo de vida, guarda de tempo por quadro com auto-parada e telemetria. O upload aceita o contêiner próprio (cabeçalho, manifesto, hash e campo de assinatura) ou `.wasm` cru em modo de laboratório. A "verificação de assinatura" é um digest SHA-256 sobre chave pública e região assinada.
- **Requisitos para implementar:**
  - Hardware: ESP32-S3 com PSRAM.
  - Software: WASM3 (MIT), Rust wasm32, assinatura real (Ed25519 via mbedTLS/libsodium/Monocypher).
  - Dados: nenhum.
  - Competências: sandboxing, criptografia, supply chain.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. **O fonte do WASM3 não está no repositório**: o CMake baixa de um fork de terceiros sem hash fixado e, se falhar, compila sem tier 3 (o relatório físico do S3 confirma build sem WASM). O README promete fuzz do parser e do upload que não existe. Caminhos: `firmware/esp32-csi-node/main/wasm_runtime.c`, `wasm_upload.c`, `rvf_parser.c`, `firmware/esp32-csi-node/components/wasm3/CMakeLists.txt`, `docs/adr/ADR-040-wasm-programmable-sensing.md`.
- **Riscos/limitações:** o upload WASM é execução remota de código, e a verificação atual é forjável por quem conhece a chave pública. HTTP sem TLS. Download de build não reprodutível.
- **Relevância para a plataforma (M12, M13):** média, como lição. "Plugins de análise" locais no host com wasmtime-py/Extism e manifestos com Ed25519 real e hashes fixados. No firmware, adiar e nunca habilitar upload sem assinatura assimétrica. Ver também EH-01 e EH-02.

#### FW-05 — Atualização OTA com rollback e verificação de saúde no primeiro boot

- **O que faz:** recebe imagem por HTTP autenticado, grava no slot alternativo, reporta estado e só confirma a imagem depois de o nó comprovar conectividade e envio de CSI. Caso contrário, reverte.
- **Como faz:** token Bearer comparado em tempo constante com uma PSK em NVS (fail-closed sem chave). Uma máquina de estados pura de "saúde do primeiro boot" observa IP e primeiro quadro aceito, respeita uptime mínimo e timeout e decide entre aprovar e reverter. Bootloader e partições não são alcançáveis por OTA.
- **Requisitos para implementar:**
  - Hardware: ESP32 com duas partições OTA e rollback habilitado.
  - Software: ESP-IDF OTA, gestão de segredos.
  - Dados: nenhum.
  - Competências: ciclo de vida de firmware.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Decisão de saúde coberta por teste host no CI. O runbook descreve verificações físicas sem resultado registrado. Caminhos: `firmware/esp32-csi-node/main/ota_update.c`, `ota_health.c`, `test/test_ota_health.c`, `firmware/esp32-csi-node/RUNBOOK.md`, `docs/adr/ADR-379-ota-first-boot-health-check.md`.
- **Riscos/limitações:** PSK em HTTP sem TLS. Sem Secure Boot V2 nem assinatura de imagem. Um AP fora do ar no boot causa rollback de imagem boa.
- **Relevância para a plataforma (M16, M15):** média para a fase de hardware. Inspira o "fleet management" no backend (versão por dispositivo, estado pendente/válido). Secure Boot e Flash Encryption são gratuitos no ESP-IDF.

#### FW-06 — Provisionamento NVS e configuração em tempo de execução

- **O que faz:** grava credenciais Wi-Fi, agregador, ID do nó, canal, filtro MAC, plano de salto, tier, limiares, chave OTA e parâmetros WASM na partição NVS via USB, sem recompilar. Cai para os padrões se a NVS estiver corrompida.
- **Como faz:** um script gera CSV → binário NVS (gerador oficial) e grava via esptool. Mantém estado por porta/MAC em diretório privado, redige segredos, lê senha e PSK de arquivos owner-only (rejeita symlinks) e **recusa omitir a PSK depois de configurada** (porque a reescrita é da partição inteira). Tem dry-run. O carregador no firmware valida faixas.
- **Requisitos para implementar:**
  - Hardware: USB.
  - Software: Python 3.10+, esptool (GPL-2.0, ferramenta externa), gerador NVS.
  - Dados: credenciais e topologia.
  - Competências: gestão de segredos, formato NVS.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Seis arquivos de teste de provisionamento no CI, fuzz do carregador NVS e matriz de configurações em QEMU (subconjunto no CI). Caminhos: `firmware/esp32-csi-node/provision.py`, `main/nvs_config.c`, `tests/test_provision_secrets.py`, `tests/test_provision_ota_psk.py`, `test/fuzz_nvs_config.c`, `scripts/generate_nvs_matrix.py`.
- **Riscos/limitações:** a reescrita total apaga chaves não reenviadas. Binários de dry-run contêm credenciais. Checagens POSIX não se aplicam no Windows.
- **Relevância para a plataforma (M16, M15):** alta. Segredos em arquivo owner-only, redação em logs, estado por dispositivo e recusa explícita de operações destrutivas, alinhados à regra de nunca imprimir `SPATIAL_TOKEN`.

#### FW-07 — Onboarding USB por desafio com nonce e identidade do dispositivo

- **O que faz:** permite que um app host descubra uma placa por USB, obtenha um recibo vinculado a nonce (chip, versão, identidade), atribua um ID de nó livre e o endereço do servidor em LAN privada (opcionalmente credenciais Wi-Fi), reinicie e **só declare sucesso quando o servidor vê o nó "fresco"**.
- **Como faz:** protocolo de linhas em serial com mensagens de saudação e configuração. O parser puro valida nonce, faixa de ID, IP privado (rejeita público), porta, SSID e senha. A identidade é um digest SHA-256 com separação de domínio sobre o MAC base (com correção no C6). As credenciais nunca aparecem no recibo.
- **Requisitos para implementar:**
  - Hardware: placa via USB.
  - Software: firmware com o protocolo, app ou CLI (pyserial ou Web Serial).
  - Dados: registro de IDs usados.
  - Competências: protocolos seriais robustos, identidade e privacidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. Testes host no CI. Testemunho físico com um ESP32-S3 (troca de ID colidido, monitor de 5 minutos) e seguimento em C6. Entrada de novas credenciais e distribuição assinada não foram medidas. Caminhos: `firmware/esp32-csi-node/main/serial_onboarding.c`, `serial_onboarding_protocol.c`, `onboarding_identity.h`, `test/test_serial_onboarding_protocol.c`, `docs/validation/2026-08-31-macos-usb-node-onboarding.md`, `docs/adr/ADR-363-native-macos-usb-node-onboarding.md`.
- **Riscos/limitações:** o digest de MAC é um pseudônimo estável. Depende de console serial livre. O app de referência é só para macOS.
- **Relevância para a plataforma (M16, M15):** alta. O fluxo "descobrir → desafiar → configurar → verificar evidência fresca antes de declarar sucesso" é um ótimo padrão de UX para o dashboard e pode ser simulado com um dispositivo virtual até haver hardware.

#### FW-08 — Kernel adaptativo e plano de malha de sensoriamento (ADR-081)

- **O que faz:** organiza o firmware em quatro camadas:
  - abstração de rádio por vtable (real e mock);
  - controlador adaptativo com máquina de estados;
  - plano de malha com papéis e mensagens tipadas;
  - pacote compacto de "estado de features" com flags de qualidade (válido, calibrando, deriva, degradado, recomenda recalibração).
- **Como faz:** três laços (rápido, médio, lento) agregam rendimento, falhas, RSSI, ruído, movimento, presença, anomalia e coerência. Uma função de decisão pura propõe perfil, canal, estado (boot, autoteste, calibração, idle, ativo, alerta, degradado) e recalibração, de forma conservadora por padrão. Há quatro papéis, sete tipos de mensagem e envelope com CRC32 (a autenticação HMAC fica no lado Rust).
- **Requisitos para implementar:**
  - Hardware: vários nós.
  - Software: FreeRTOS e agregador.
  - Dados: telemetria contínua.
  - Competências: sistemas distribuídos embarcados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Há testes host do controlador, da malha e do pacote de features, **mas nenhum workflow de CI os executa**. Não há evidência física de troca adaptativa. Caminhos: `firmware/esp32-csi-node/main/adaptive_controller.c`, `adaptive_controller_decide.c`, `rv_radio_ops.h`, `rv_radio_ops_mock.c`, `rv_mesh.c`, `rv_feature_state.h`, `tests/host/test_adaptive_controller.c`, `docs/adr/ADR-081-adaptive-csi-mesh-firmware-kernel.md`.
- **Riscos/limitações:** CRC não autentica. Políticas podem oscilar. Complexidade alta para ganho não medido.
- **Relevância para a plataforma (M12, M14, M16):** alta como modelo conceitual: porta de rádio com adaptador real e mock (espelha `NativeProvider` versus adaptadores futuros), flags de qualidade e confiança por métrica no contrato 2.0.0 e uma máquina de estados de saúde do nó para M16.

#### FW-09 — Sincronização temporal entre nós e gating de quadros alinhado à malha

- **O que faz:** faz os nós compartilharem uma época comum (líder e seguidores) para aceitarem os mesmos quadros na mesma janela. Inclui um experimento fatorial numa frota de nove nós.
- **Como faz:** beacons periódicos com flag de líder e época, eleição e rastreamento de offset, implementados via ESP-NOW (o caminho 802.15.4 do C6 se mostrou quebrado). O gate usa um "bucket" da época sincronizada, com fallback por tempo. O script de experimento aplica quatro braços em quadrado latino e verifica o modo ativo antes de amostrar.
- **Requisitos para implementar:**
  - Hardware: três ou mais ESP32 e, idealmente, referência de tempo.
  - Software: ESP-NOW e API de malha.
  - Dados: logs de (MAC, sequência).
  - Competências: relógios distribuídos, desenho experimental.
- **Evidência e maturidade:** `PARTIAL` / `REAL_HARDWARE_EVIDENCE`. O log de testemunho registra o 802.15.4 bloqueado e um soak ESP-NOW de 300 s sem falhas numa placa, com a medição cruzada interrompida. O runbook relata a frota de nove C6: o alinhamento por janela rendeu ganho marginal e a seleção por sequência, ganho muito maior (dados brutos fora do git). O script contém IPs de LAN fixos. Caminhos: `firmware/esp32-csi-node/main/c6_sync_espnow.c`, `c6_timesync.c`, `run_arms.py`, `RUNBOOK.md`, `docs/WITNESS-LOG-110.md`.
- **Riscos/limitações:** ESP-NOW consome airtime. Deriva de cristal. Resultados dependentes da casa. Sem coerência de fase entre nós.
- **Relevância para a plataforma (M02, M03, M14, M16):** média-alta. O desenho experimental é reutilizável, e o motor sintético pode simular nós com relógios desviados para testar alinhamento e fusão tolerante a ausências. Ver também SV-23.

#### FW-10 — Extensões ESP32-C6 Wi-Fi 6: HE-LTF, TWT, soft-AP HE, hibernação LP-core e seleção de antena

- **O que faz:** marca o tipo de PPDU (HT ou HE-SU), negocia Target Wake Time, oferece um modo soft-AP HE para bancada, hibernação com núcleo de baixo consumo acordando por GPIO e seleção de antena interna ou externa.
- **Como faz:** opções Kconfig por recurso. TWT com fallback gracioso. Programa RISC-V no LP-core com debounce. Chave RF por GPIO com log de boot obrigatório.
- **Requisitos para implementar:**
  - Hardware: ESP32-C6, AP 802.11ax com TWT, medidor de corrente.
  - Software: ESP-IDF 5.5.x.
  - Dados: capturas HT versus HE.
  - Competências: Wi-Fi 6, gestão de energia.
- **Evidência e maturidade:** `PARTIAL` / `REAL_HARDWARE_EVIDENCE`. Boot em 3 placas e correção de MAC verificada. **HE-LTF só com IDF 5.5.2** (o 5.4 documentado rebaixa para HT). TWT nunca aceito. Hibernação não medida. O veredito do log é "não pronto para release". Caminhos: `firmware/esp32-csi-node/main/c6_twt.c`, `c6_softap_he.c`, `c6_lp_core.c`, `c6_antenna_select.c`, `test/test_adr110_encoding.c`, `docs/WITNESS-LOG-110.md`, `docs/adr/ADR-110-esp32-c6-firmware-extension.md`.
- **Riscos/limitações:** forte dependência da versão do blob do driver. Recursos não medidos podem ser vendidos como capacidades.
- **Relevância para a plataforma (M12, M16):** baixa-média. Serve para documentar requisitos de hardware e para o simulador declarar tipo de PPDU e número de tons como metadados.

#### FW-11 — Fusão com radar mmWave (24/60 GHz) via UART

- **O que faz:** detecta automaticamente sensores mmWave comerciais por UART, lê presença, distância, alvos e vitais e funde tudo com as estimativas de CSI num pacote estendido.
- **Como faz:** a sondagem só confia num sensor depois de validar um quadro completo (cabeçalho, comprimento, checksum), com predicados puros. A fusão é uma combinação ponderada fixa que preserva os valores individuais. Há mock em QEMU.
- **Requisitos para implementar:**
  - Hardware: módulo mmWave com UART.
  - Software: driver UART e protocolo público do fabricante.
  - Dados: referência de vitais.
  - Competências: fusão de sensores (variância inversa, Kalman).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Teste de detecção no CI e mock. Não há validação com sensor físico. Caminhos: `firmware/esp32-csi-node/main/mmwave_sensor.c`, `mmwave_detect.h`, `test/test_mmwave_detect.c`, `docs/adr/ADR-063-mmwave-sensor-fusion.md`.
- **Riscos/limitações:** pesos fixos sem calibração. Conflitos de pinos.
- **Relevância para a plataforma (M01, M04, M05, M14):** média. Cada sensor como adaptador separado com evidência própria e fusão explícita, modelável no sintético com um segundo sensor de ruído distinto.

#### FW-12 — Operação de frota: térmico, watchdog de uplink, log de saúde em flash, energia e ponte de coordenação

- **O que faz:** reduz a potência de TX por temperatura com histerese, reinicia o nó se o uplink parar, grava registros de saúde num anel em FAT, faz duty-cycle com light sleep e, opcionalmente, envia heartbeat a um coordenador externo.
- **Como faz:** monitor térmico que expõe estado e potência, para que quedas de RSSI por throttling não sejam confundidas com obstrução. Watchdog pelo último envio aceito. Logger em anel. Power management do ESP-IDF. Tarefa HTTP periódica para o coordenador.
- **Requisitos para implementar:**
  - Hardware: ESP32 com sensor de temperatura e flash de 8–16 MB.
  - Software: ESP-IDF.
  - Dados: telemetria contínua.
  - Competências: confiabilidade embarcada.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. A histerese térmica tem teste no CI; o restante não tem testes. O README alerta para superaquecimento de placas compactas. Caminhos: `firmware/esp32-csi-node/main/thermal.c`, `test/test_thermal_hysteresis.c`, `main/node_log.c`, `main/power_mgmt.c`, `main/swarm_bridge.c`, `firmware/esp32-csi-node/RUNBOOK.md`.
- **Riscos/limitações:** limiares por instalação. Watchdog curto pode entrar em loop de reboot. A ponte depende de um serviço do ecossistema do autor.
- **Relevância para a plataforma (M16, M15):** média. "Saúde de dispositivo" (temperatura, throttling, idade do último pacote, reboots) como telemetria separada das observações, com retenção própria. MQTT local em vez da ponte proprietária.

#### FW-13 — Interface local no nó: display AMOLED (LVGL) e LED de visualização

- **O que faz:** quatro telas (painel, vitais, presença, sistema) em placas com AMOLED e um LED endereçável piscando a 40 Hz, com cor mapeada pela energia de movimento.
- **Como faz:** HAL QSPI, tarefa LVGL de baixa prioridade e detecção do painel em runtime. LED via RMT.
- **Requisitos para implementar:**
  - Hardware: placa específica com AMOLED ou WS2812.
  - Software: LVGL 8.3 (MIT).
  - Dados: nenhum.
  - Competências: UI embarcada.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `NONE`. Sem testes. O README documenta o falso positivo de painel que zerava a CSI. O LED de 40 Hz é apresentado como estímulo "gamma", com aviso de fotossensibilidade. Caminhos: `firmware/esp32-csi-node/main/display_hal.c`, `display_task.c`, `display_ui.c`, `docs/adr/ADR-045-amoled-display-support.md`, `docs/adr/ADR-183-onboard-led-gamma-stimulus-csi-colormap.md`.
- **Riscos/limitações:** acoplamento perigoso com a captura. O flicker sugere uma alegação terapêutica.
- **Relevância para a plataforma (NONE):** baixa. Lição: nunca acoplar periféricos opcionais ao caminho de captura e evitar estímulos com conotação terapêutica.

#### FW-14 — Teste sem hardware, CI e empacotamento de releases do firmware

- **O que faz:** exercita o firmware sem placas:
  - gerador CSI sintético em QEMU com cenários (vazio, parado, andando, queda, multi-pessoa, varredura de canal, filtro MAC, overflow, RSSI limite, quadro vazio);
  - matriz NVS e validação automática do log UART com severidades;
  - fuzzing libFuzzer+ASan, testes host com stubs, GDB e gcov.
  O CI compila S3 8 MB, S3 4 MB e C6 com gates de tamanho e checa integridade, versão e contrato de entrega. Os releases têm `SHA256SUMS`.
- **Como faz:** modelo de sinal sintético por subportadora injetado por timer. Scripts geram NVS, iniciam QEMU, coletam UART e aplicam as checagens.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: ESP-IDF, QEMU Espressif (GPL-2.0), clang/libFuzzer, lcov.
  - Dados: corpus semente.
  - Competências: emulação, fuzzing, CI.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Workflows presentes e citados como verdes. O README promete 14 configurações e fuzz de parsers inexistentes; há só três alvos de fuzz e o CI roda um subconjunto. Há binários históricos e um arquivo de estado de agente versionados. Caminhos: `firmware/esp32-csi-node/main/mock_csi.c`, `sdkconfig.qemu`, `test/Makefile`, `test/test_delivery_contract.py`, `scripts/validate_qemu_output.py`, `scripts/generate_nvs_matrix.py`, `.github/workflows/firmware-ci.yml`, `.github/workflows/firmware-qemu.yml`.
- **Riscos/limitações:** o QEMU não emula rádio nem cadência real. A documentação promete mais cobertura do que existe.
- **Relevância para a plataforma (M12, M16):** muito alta e alinhada ao modo `synthetic-native`: cenários nomeados com expectativas verificáveis, validador automático com severidades e fuzz de parsers (Hypothesis, Atheris). Ver também OP-15.

#### FW-15 — CSI em roteadores MediaTek MT7981 via OpenWrt com ponte e portão de proveniência

- **O que faz:** extrai CSI por cadeia de recepção de roteadores Filogic (WN586X3 Rev A) com OpenWrt e o patch de CSI do fabricante, converte para o formato próprio e envia ao servidor, rotulando toda origem como "física não validada" ou "simulada".
- **Como faz:** patches de CSI do mt76, suporte de placa, correções de limites na ferramenta de dump e de atributo netlink. A CSI é lida por dump JSON (rico) ou streaming UDP (uma antena por datagrama). A ponte exige atestação de hardware ou declaração sintética pegajosa. Uma análise offline mostrou que **a fase por cadeia é praticamente aleatória (CFO por pacote), mas a fase cruzada entre duas cadeias do mesmo rádio é estável** (técnica pública de cancelamento de CFO).
- **Requisitos para implementar:**
  - Hardware: roteador MT7981B + MT7976C e um cliente transmitindo.
  - Software: OpenWrt 24.10.8, mt76 com patch, ferramentas corrigidas.
  - Dados: capturas privadas (contêm MACs).
  - Competências: build OpenWrt, netlink, fase MIMO.
- **Evidência e maturidade:** `PARTIAL` / `REAL_HARDWARE_EVIDENCE`. MEASURED: primeiro quadro real entregue e estabilidade de fase cruzada em seis capturas de duas unidades (fora do repositório). CLAIMED: entrega contínua, outras placas e heurísticas de presença. Caminhos: `firmware/openwrt-wn586x3/README.md`, `firmware/openwrt-wn586x3/patches/`, `docs/mediatek-router-csi.md`, `scripts/mediatek-csi-phase-stability.py`, `docs/adr/ADR-266-mediatek-filogic-csi-platform.md`.
- **Riscos/limitações:** a taxa segue o tráfego do cliente. Sem calibração. Patches com licenças GPL-2.0/BSD-3-Clause-Clear/Apache-2.0. Risco de inutilizar o roteador.
- **Relevância para a plataforma (M08, M12, M15):** média-alta conceitualmente. O portão de proveniência mapeia diretamente para L0_SYNTHETIC → L1_RECORDED_UNVALIDATED → L2_LIVE_UNVALIDATED, e a fase cruzada entre cadeias é uma feature pública útil para M08. O hardware exige autorização. Ver também EH-17.

#### FW-16 — Captura e decodificação de Beamforming Feedback (BFI) VHT/HE em Linux com oráculo independente

- **O que faz:** captura passivamente, em modo monitor, os relatórios de beamforming comprimido enviados em claro do cliente ao AP. Decodifica os ângulos, reconstrói a matriz de steering, mede taxa, lacunas e duplicatas e valida a decodificação contra o dissector do tshark, sempre restaurando a conexão Wi-Fi original.
- **Como faz:** o helper exige interface gerenciada e rota Ethernet de gestão independente. Troca temporariamente para monitor, roda tcpdump limitado e grava PCAP com manifesto (comando, filtros, hash, contadores, restauração verificada). Um wrapper gera tráfego descendente só para o cliente verificado. O decodificador em Python puro lê radiotap e aceita apenas formatos suportados. A matriz é reconstruída por produto de rotações de Givens (decomposição padronizada no IEEE 802.11). Um comparador confere todos os ângulos e campos contra uma versão fixada do tshark.
- **Requisitos para implementar:**
  - Hardware: AP próprio Wi-Fi 6, cliente associado, PC Linux com adaptador capaz de monitor e Ethernet separada.
  - Software: Python 3.11+, iw, ip, nmcli, tcpdump, tshark.
  - Dados: capturas privadas da própria rede.
  - Competências: 802.11ac/ax, radiotap, administração Linux.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. 64 testes sintéticos no CI. MEASURED: 21 relatórios HE 2×2/80 MHz conferidos 21/21 com tshark, e depois 66 e 96 relatórios. **Repetições nas mesmas condições deram 0 e 1 relatórios**, então a amostragem sustentada não foi estabelecida. Não está ligado à produção e não infere movimento. Caminhos: `tools/bfi/README.md`, `tools/bfi/bfi_decode.py`, `capture_linux.py`, `run_trial_linux.py`, `compare_tshark.py`, `quality_report.py`, `tools/bfi/VALIDATION.md`, `.github/workflows/bfi-research.yml`.
- **Riscos/limitações:** relatórios esparsos e irregulares. Depende de o AP fazer sounding. **Captura passiva de terceiros é questão legal e ética** (BFI pode identificar pessoas segundo a literatura).
- **Relevância para a plataforma (M08, M12, M15):** média. O método de aceitação (oráculo independente, manifesto com hash, gates e resultado "inconclusivo" explícito para zero relatórios) é um modelo de governança de evidência. Uso só na própria rede, com consentimento, e M08 como pesquisa.

#### FW-17 — Pipeline offline de aprendizado CSI/BFI com controles experimentais e holdout selado

- **O que faz:** prepara datasets numéricos (CSI pública NTU-Fi, capturas privadas, BFI real decodificado), treina baselines LSTM/GRU, aplica controles temporais e estáticos pré-registrados, baixa um dataset público de BFI por manifesto fixado e mantém um teste selado até a avaliação final.
- **Como faz:** importadores leem só matrizes numéricas (sem executar MATLAB/pickle), verificam hashes e rejeitam duplicatas entre partições. O BFI é codificado de forma circular (cos/sin). O treino normaliza só com o treino, usa partições cronológicas com "purge", seleciona por validação e emite recibos com hash, e a avaliação final é de uso único. Controles: embaralhar a ordem temporal, remover a média por gravação e baselines estáticos (centróide, ridge).
- **Requisitos para implementar:**
  - Hardware: CPU (GPU opcional).
  - Software: NumPy, SciPy, PyTorch.
  - Dados: NTU-Fi (CC BY 4.0), CSI-BFI-HAR (GPL-3.0), capturas próprias.
  - Competências: ML de séries temporais, avaliação sem vazamento, ética biométrica.
- **Evidência e maturidade:** `RESEARCH` / `SYNTHETIC_OR_SIMULATED`. Cerca de 141 testes sintéticos no CI. Resultados documentados: **um ridge estático empatou com LSTM/GRU e embaralhar a ordem temporal não reduziu a acurácia**, ou seja, não há evidência de aprendizado de movimento. O piloto de previsão com BFI real não superou a persistência. Holdout não pontuado. Caminhos: `tools/bfi_learning/README.md`, `prepare.py`, `prepare_bfi.py`, `train.py`, `static_baseline.py`, `download_public_bfi.py`, `tools/bfi_learning/RESULTS.md`, `tools/bfi_learning/CONTROLS.md`.
- **Riscos/limitações:** foco em identificação de pessoas, fora do escopo da plataforma. Confusão dia/sala. Licenças GPL-3.0.
- **Relevância para a plataforma (M06, M12, M15):** alta como metodologia para o Model Lab: recibos com hash, normalização só no treino, partições cronológicas com purge, holdout selado, baselines triviais e controles de embaralhamento antes de qualquer alegação. Excluir identificação individual.

#### FW-18 — WiFi Veil / privshield: contramedida de privacidade contra sensoriamento por BFI

- **O que faz:** modela uma "firewall de privacidade" que altera a realimentação de beamforming do próprio nó com uma rotação secreta por sessão. Um farejador passivo não reidentifica pessoas, e o AP legítimo (que compartilha a chave) desfaz a rotação. Inclui auditoria de conformidade "não é jamming", otimizador, prova determinística, TUI, console HTML, núcleo C portátil e adaptadores.
- **Como faz:** modelo sintético de dois subespaços (um "comm" dominante e um "fino" com a assinatura de identidade). O protetor aplica rotações de Givens chaveadas só no subespaço fino, uma transformação ortogonal que preserva energia. Há atacantes de reidentificação, modelo de throughput, auditoria de energia, testemunha FNV-1a e PRNG não criptográfico. O núcleo C99 sem malloc é testado em host. Adaptadores para openwifi, OpenWrt, Nexmon e ESP32 (só como detector ou controlador de superfície).
- **Requisitos para implementar:**
  - Hardware: PHY aberto (openwifi em Zynq + AD9361) para medição real.
  - Software: Rust, C99, libnl, Vivado.
  - Dados: BFI real com identidades consentidas.
  - Competências: álgebra linear, MIMO, segurança, regulação de RF.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. 43 testes Rust e teste host do C. Todos os números (reidentificação no nível de acaso, ~98% de throughput) são SYNTHETIC/L0. Os adaptadores são esqueletos com marcadores TODO(hw). Há cópias quase idênticas em duas pastas. Caminhos: `wifi-veil/README.md`, `wifi-veil/src/protector.rs`, `attacker.rs`, `optimize.rs`, `compliance.rs`, `proof.rs`, `wifi-veil/firmware/core/veil_shield.c`, `firmware/privshield/README.md`, `wifi-veil/docs/adr/ADR-288-veil-privacy-shield-compliant-waveform.md`.
- **Riscos/limitações:** o modelo de dois subespaços pode não refletir canais reais. A troca de chaves não está especificada. Os ângulos ficam bloqueados nos blobs comerciais.
- **Relevância para a plataforma (M15, M08):** média como insight de negócio: modelo de ameaça de sensoriamento passivo, painel de risco de privacidade e testemunha determinística (hashlib) para relatórios. A contramedida fica PLANNED/BLOCKED. Ver também GV-16 e GV-17.

#### FW-19 — Modelo de domínio de hardware (DDD) e guia de build/BOM

- **O que faz:** documenta a camada de hardware como cinco contextos delimitados (nó sensor, borda, WASM, agregação, provisionamento), com agregados, eventos, invariantes, mapa de contextos, camadas anticorrupção e uma BOM de kit de três nós.
- **Como faz:** especificação textual. O agregador alinha timestamps por relógio monotônico de cada nó, sem NTP, e faz fusão **em nível de features** (porque a deriva de cristal impede coerência de fase entre nós), tolerando nós ausentes.
- **Requisitos para implementar:**
  - Hardware: kit de três ESP32-S3.
  - Software: nenhuma execução.
  - Dados: nenhum.
  - Competências: DDD, arquitetura embarcado + servidor.
- **Evidência e maturidade:** `DOC_ONLY` / `NONE`. Parcialmente desatualizado: tamanhos de partição antigos, identificadores de pacote inconsistentes, métricas sem reprodutor. Caminhos: `docs/ddd/hardware-platform-domain-model.md`, `docs/build-guide.md`.
- **Riscos/limitações:** documentação divergente induz integradores a erro.
- **Relevância para a plataforma (M12, M14, M16):** alta como inspiração de arquitetura: fusão em nível de features, tolerância a ausências e anticorrupção entre formato de fio e domínio. A documentação de protocolo deve ser gerada a partir do contrato (como a plataforma já faz com `export_contract.py`).

### 4.5 ML, treino, modelos pré-treinados, pose e contagem

**Escopo.** Cerca de 40 mil linhas de Rust em 9 crates, mais documentos de benchmark, model card e modelo DDD. O que está mais maduro e testado **não são os modelos**: é a infraestrutura de medição honesta, que roda sem GPU e entra no CI com `--no-default-features` (métricas canônicas, protocolos anti-vazamento, claim gate de presença, gates de release e score runner com witness). O treino supervisionado em LibTorch fica atrás de uma feature e fora do CI.

Os modelos entregues saíram de uma única gravação de 30 minutos:

- `pose_v1`: PCK@20 de cerca de 3%;
- `count_v1`: quase degenerado.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| ML-01 | Pipeline de treino supervisionado WiFi→pose/DensePose (tch/LibTorch) | PARTIAL | UNIT_TESTS_ONLY | M11, M12 |
| ML-02 | Ingestão e pré-processamento de datasets CSI | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M08 |
| ML-03 | Métricas canônicas de pose com normalização explícita | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M11, M15 |
| ML-04 | Protocolos de split anti-vazamento, baseline mean-pose e grau de evidência | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M12, M16 |
| ML-05 | Benchmark falsificável de presença/ocupação e harness de ablação | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M02, M15 |
| ML-06 | Gates de liberação de modelo (ADR-298) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M12 |
| ML-07 | Aceitação tri-métrica e score runner AetherArena com witness/ledger | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15, M11, M04, M05, M03 |
| ML-08 | Prova determinística de treino | PARTIAL | SYNTHETIC_OR_SIMULATED | M15, M12 |
| ML-09 | MERIDIAN: generalização entre ambientes e adaptação rápida | PARTIAL | UNIT_TESTS_ONLY | M12, M16, M08 |
| ML-10 | Receita de pré-treino MAE (patchificação e mascaramento) | PARTIAL | UNIT_TESTS_ONLY | M12 |
| ML-11 | Port do WiFlow-STD e quantização int8 medida | IMPLEMENTED_TESTED | UNCLEAR | M11, M12 |
| ML-12 | Motor de inferência `wifi-densepose-nn` | PARTIAL | UNIT_TESTS_ONLY | M11, M12, M01, M02, M06 |
| ML-13 | AETHER: embedding contrastivo, graph-transformer e índice de fingerprints | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M08, M12, M11, M15 |
| ML-14 | SONA: adaptação online (LoRA + EWC + drift) e inferência esparsa/quantizada | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M16, M08 |
| ML-15 | Cog de estimativa de pose 17 keypoints | IMPLEMENTED_TESTED | REAL_HARDWARE_EVIDENCE | M11, M16, M13 |
| ML-16 | Cog de contagem de pessoas | PARTIAL | REAL_HARDWARE_EVIDENCE | M02, M03, M01 |
| ML-17 | Estudo MM-Fi: SOTA, fronteira de eficiência e calibração few-shot | RESEARCH | UNCLEAR | M11, M06, M16, M12 |
| ML-18 | Modelos no Hugging Face e model card com retratações | DOC_ONLY | UNCLEAR | M01, M04, M05, M07, M09, M12, M15 |
| ML-19 | OccWorld em Candle (world model de ocupação 3D) | PARTIAL | UNIT_TESTS_ONLY | M14 |
| ML-20 | nvsim e nvsim-server: simulador de magnetômetro NV-diamante | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M15 |
| ML-21 | Governança de evidência de benchmarks (ledgers, protocolo, template de card) | DOC_ONLY | UNCLEAR | M15, M12 |
| ML-22 | Benchmark HOMECORE vs Home Assistant (documento) | DOC_ONLY | UNCLEAR | M13 |

#### ML-01 — Pipeline de treino supervisionado WiFi→pose/DensePose (tch-rs/LibTorch)

- **O que faz:** treina de ponta a ponta um modelo que leva amplitude e fase CSI a heatmaps de 17 keypoints e a segmentação DensePose (partes + UV), com configuração serializável, laço de treino e CLI com dry-run sintético.
- **Como faz:** configuração única com presets por contagem nativa de subportadoras. A arquitetura segue a família "DensePose from WiFi" (CMU): um tradutor de modalidade (MLPs sobre amplitude e fase com atenção entre pares de antena) gera uma pseudo-imagem para um backbone tipo ResNet, com cabeças de keypoints e DensePose. A perda é composta (MSE de heatmap mascarado, entropia cruzada + Smooth-L1, destilação opcional). AdamW, decaimento em marcos, clipping, early stopping, log CSV e checkpoint pelo melhor PCK. Pesos do zero, sem ImageNet.
- **Requisitos para implementar:**
  - Hardware: GPU CUDA recomendada.
  - Software: PyTorch (BSD-3), safetensors, export ONNX.
  - Dados: CSI pareado com keypoints (MM-Fi ou câmera professora); pseudo-rótulos UV para DensePose.
  - Competências: DL de pose, treino reprodutível.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Modelo, perdas, trainer e prova só compilam com a feature tch e não rodam no CI; só os 24 testes de config rodam sem ela. **Nenhum artefato entregue foi produzido por este trainer.** O DDD cita um dataset e um adaptador de professor ausentes. Caminhos: `v2/crates/wifi-densepose-train/src/config.rs`, `model.rs`, `losses.rs`, `trainer.rs`, `src/bin/train.rs`, `v2/crates/wifi-densepose-train/tests/test_losses.rs`.
- **Riscos/limitações:** FFI pesada. Fora do CI. Sem resultados. O README superestima a completude.
- **Relevância para a plataforma (M11, M12):** inspira um Model Lab com config versionada e checkpoints, mas amplia a IA (exige autorização) e depende de dados reais. Fica PLANNED/BLOCKED.

#### ML-02 — Ingestão e pré-processamento de datasets CSI (MM-Fi, Widar3.0, sintético determinístico)

- **O que faz:** abstração única de dataset com três fontes (MM-Fi em disco, logs "bfee" do Widar3.0/Intel 5300 e gerador sintético determinístico), batching semeado, reamostragem de subportadoras, buffer comprimido e features de sinal.
- **Como faz:** loader MM-Fi com memory-map e split disjunto por sujeito, com asserção de não vazamento. O parser Widar valida cada registro na fronteira e pula os inválidos sem pânico, e as fixtures são geradas em código. Reamostragem linear ou esparsa (base gaussiana + Tikhonov), quantização em camadas.
- **Requisitos para implementar:**
  - Hardware: CPU e disco.
  - Software: `np.load(mmap_mode)`, `np.interp`, scipy.sparse, pytest/hypothesis.
  - Dados: MM-Fi (CC BY-NC), Widar3.0 (licença não verificada) ou sintético.
  - Competências: formatos CSI, validação de entrada não confiável.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: test_dataset 27, test_subcarrier 18, loader real 3, inline 23, Widar 20, mais um bench do parser. Nenhum teste usa os datasets reais. Caminhos: `v2/crates/wifi-densepose-train/src/dataset.rs`, `src/dataset/widar.rs`, `subcarrier.rs`, `signal_features.rs`, `tests/test_dataset.rs`, `tests/test_real_loader.rs`.
- **Riscos/limitações:** MM-Fi impede uso comercial. Reamostragem não resolve deslocamento de domínio. O parser é superfície de ataque.
- **Relevância para a plataforma (M12, M08):** muito relevante para uma porta de dataset com fonte sintética determinística por padrão e adaptadores opcionais de formatos públicos (opt-in, verificando licença).

#### ML-03 — Métricas canônicas de pose e harness de acurácia com normalização explícita

- **O que faz:** uma única implementação de PCK@k e OKS. Todo número de PCK carrega a normalização usada (torso, diagonal da bbox ou absoluta). Inclui MPJPE, PCK por articulação e associação predição↔GT entre várias pessoas.
- **Como faz:** acerto se o erro for menor que k × tamanho do torso (distância entre quadris). Sem quadris, usa a diagonal da bbox; sem articulações visíveis, resultado 0 (nunca 1). OKS segue o padrão COCO, com escala pela área. Um enum autodescritivo impede PCK sem definição. Associação por algoritmo húngaro (custo OKS), fluxo de custo mínimo ou min-cut incremental.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy, `scipy.optimize.linear_sum_assignment`.
  - Dados: pares predição/GT.
  - Competências: avaliação de pose (COCO, MM-Fi).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: test_metrics 21, accuracy 15, eval 11, com fixtures calculadas à mão. Os documentos registram duas métricas retratadas por ambiguidade, motivo da centralização. Caminhos: `v2/crates/wifi-densepose-train/src/metrics_core.rs`, `accuracy.rs`, `metrics.rs`, `eval.rs`, `tests/test_metrics.rs`.
- **Riscos/limitações:** números com normalizações diferentes não são comparáveis (o repositório documenta três PCK@20 incompatíveis).
- **Relevância para a plataforma (M11, M15):** alta e imediata. Um módulo Python de métricas com a normalização como parâmetro obrigatório e incluída no resultado serializado.

#### ML-04 — Protocolos de split anti-vazamento, baseline mean-pose e relatórios com grau de evidência

- **O que faz:** protocolos padrão (cross-subject, cross-environment, cross-orientation e split aleatório só para comparação) como funções puras de metadados + semente. Audita cada split, ajusta um baseline de pose média só no treino e só aceita relatório com baseline e grau de evidência.
- **Como faz:** a atribuição é determinística por hash dos metadados, sem estado de RNG. A auditoria **falha com erro** se sujeitos ou ambientes se cruzarem quando o protocolo alega disjunção e, sempre, se janelas da mesma gravação ficarem dos dois lados. O grau "MEASURED" não pode ser construído sem o comando reprodutor.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: hashlib, dataclasses, pytest.
  - Dados: metadados por amostra (sujeito, ambiente, orientação, gravação, janela).
  - Competências: metodologia experimental, vazamento temporal e de sujeito.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: protocols 9, leakage 14. O estudo MM-Fi mostra a motivação: a acurácia de ação cai de 88% (aleatório) para cerca de 10% (cross-subject). O próprio RuView viola o protocolo no `count_v1`. Caminhos: `v2/crates/wifi-densepose-train/src/protocols.rs`, `src/protocols/leakage.rs`.
- **Riscos/limitações:** depende de metadados corretos.
- **Relevância para a plataforma (M15, M12, M16):** altíssima e implementável já sobre dados sintéticos. Um serviço de domínio puro que se recusa a registrar métricas com split vazado ou sem baseline, encaixado nos níveis de evidência.

#### ML-05 — Benchmark falsificável de presença/ocupação e harness de ablação (privacidade + latência)

- **O que faz:** pontua predições de presença e contagem contra a verdade e **só libera alegação** se os dados forem medidos (não sintéticos nem mock), o split não vazar, o teste tiver as duas classes e o **limite inferior do IC** passar o limiar pré-registrado. A ablação compara combinações de features e mede FP/FN, latência p50/p95, vazamento por membership inference e degradação entre salas.
- **Como faz:** procedência por dataset (Measured, Synthetic, Mock), validação de split, F1 vazio = 0, IC bootstrap de 95% determinístico, separabilidade de escores membro/não membro e relatório em Markdown.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy (Generator semeado), scipy.stats.
  - Dados: sequências rotuladas com procedência.
  - Competências: bootstrap, IC, privacidade em ML.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: occupancy_bench 12, ablation 6. O próprio módulo recusa alegações sobre dados sintéticos. Caminhos: `v2/crates/wifi-densepose-train/src/occupancy_bench.rs`, `ablation.rs`.
- **Riscos/limitações:** séries temporais pedem bootstrap por blocos (variante não verificada). Limiares exigem governança.
- **Relevância para a plataforma (M01, M02, M15):** altíssima. O "claim gate" por procedência é o `source_type`/`evidence_level` da plataforma.

#### ML-06 — Gates de liberação de modelo (sanidade de classificadores, ADR-298)

- **O que faz:** bloqueia a publicação de cabeças degeneradas ou mal rotuladas: fronteira de decisão inalcançável, saída quase constante, taxa de positivos degenerada, ausência de baseline e métrica exibida sob nome de tarefa diferente da calculada.
- **Como faz:** verificação analítica se o viés domina a norma dos pesos de uma cabeça linear sobre embeddings normalizados, variância e taxa de positivos sobre sondas diversas e relatório pareado com baseline. Cada métrica carrega seu tipo calculado, e o rótulo de exibição deriva dele (impede mostrar acurácia de triplet como "acurácia de presença"). Os diagnósticos são estruturados.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: álgebra linear básica.
  - Dados: pesos e sondas.
  - Competências: diagnóstico de modelos, MLOps.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 13 testes, incluindo regressão da cabeça de presença publicada que era degenerada. O workflow só protege o próprio checker; **os uploads ao Hugging Face são manuais e não passam pelo gate**. Caminhos: `v2/crates/wifi-densepose-train/src/model_gates.rs`, `.github/workflows/model-release-gate.yml`.
- **Riscos/limitações:** cobre só cabeças lineares. Sem CLI.
- **Relevância para a plataforma (M15, M12):** muito relevante: um "release gate" Python antes de promover qualquer modelo no M12, mais a regra de proveniência da métrica no contrato.

#### ML-07 — Teste de aceitação tri-métrico (Bronze/Silver/Gold) e score runner AetherArena com witness e ledger

- **O que faz:** classifica um sistema em níveis por erro articular (PCK/OKS), separação de pessoas (MOTA) e precisão de vitais. Um binário de CI pontua predições contra um split e emite um witness reprodutível, encadeável num ledger append-only que alimenta um leaderboard público.
- **Como faz:** três avaliadores com limiares configuráveis, MOTA na definição do MOT Challenge. O witness traz hash das entradas, versão do harness, métricas, nível e hash estável do score quantizado. Há modos de autoteste e de repetibilidade (K execuções idênticas). O ledger em Python é encadeado por hash.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: JSON, SHA-256, SQLite, py-motmetrics (MIT), Gradio opcional.
  - Dados: split privado de verdade.
  - Competências: métricas de rastreamento, benchmarks reprodutíveis.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 20 testes. O CI compila, roda o autoteste e repete 16 vezes. O Space está no ar com leaderboard vazio e split privado pendente (há divergência com o ledger, ver WM-24). Caminhos: `v2/crates/wifi-densepose-train/src/ruview_metrics.rs`, `src/bin/aa_score_runner.rs`, `aether-arena/fixtures/expected_score.sha256`, `aether-arena/ledger/ledger_tools.py`, `aether-arena/STATUS.md`, `.github/workflows/aether-arena-harness.yml`.
- **Riscos/limitações:** limiares arbitrários. Ledger sem âncora externa. MM-Fi não comercial.
- **Relevância para a plataforma (M15, M11, M04, M05, M03):** muito relevante. "Witness = hash(entradas) + hash(score quantizado) + versão do harness" num ledger SQLite append-only com hash chain e Ed25519 opcional.

#### ML-08 — Prova determinística de treino (trust kill switch)

- **O que faz:** executa um mini-treino semeado sobre o dataset sintético e certifica que a perda caiu acima de uma margem e que o SHA-256 dos pesos finais bate com um valor commitado. Prova reprodutibilidade, **explicitamente não acurácia**.
- **Como faz:** sementes fixas, N passos, serialização ordenada e hash. Códigos de saída PASS, FAIL e SKIP; queda de perda insuficiente é FAIL, nunca SKIP.
- **Requisitos para implementar:**
  - Hardware: CPU/GPU com LibTorch.
  - Software: SHA-256.
  - Dados: dataset sintético.
  - Competências: reprodutibilidade numérica.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. **Não há hash esperado commitado**, então a verificação termina em SKIP. Depende de tch, fora do CI. Caminhos: `v2/crates/wifi-densepose-train/src/proof.rs`, `src/bin/verify_training.rs`, `tests/test_proof.rs`.
- **Riscos/limitações:** o hash quebra entre versões e hardware.
- **Relevância para a plataforma (M15, M12):** útil como teste de fumaça do Model Lab, preferencialmente com tolerância por plataforma em vez de hash bit a bit.

#### ML-09 — MERIDIAN: generalização entre ambientes e adaptação rápida

- **O que faz:** fatoração pose/ambiente com treino adversarial, codificação da geometria dos APs que condiciona as features (FiLM), "domínios virtuais", avaliação cross-domain e adaptação em tempo de teste que gera deltas LoRA a partir de frames não rotulados.
- **Como faz:** reversão de gradiente com lambda crescente; codificação de Fourier das posições e agregação invariante à ordem (estilo DeepSets) modulando o backbone; transformações físicas plausíveis por domínio com PRNG semeado; objetivo autossupervisionado (contrastivo temporal + entropia) minimizado por diferenças finitas.
- **Requisitos para implementar:**
  - Hardware: CPU (GPU para o adversarial real).
  - Software: PyTorch, PEFT (Apache-2.0).
  - Dados: vários ambientes e sujeitos com geometria.
  - Competências: adaptação de domínio (DANN, FiLM, TTA).
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: domain 18, geometry 14, virtual_aug 12, rapid_adapt 12, eval 11. A TTA registra que um "gradiente falso" anterior foi removido e que **não há ganho de PCK medido**. O estudo MM-Fi relata que DANN e CORAL não fecharam o gap, mas a calibração few-shot fechou. Caminhos: `v2/crates/wifi-densepose-train/src/domain.rs`, `geometry.rs`, `virtual_aug.rs`, `rapid_adapt.rs`, `eval.rs`.
- **Riscos/limitações:** evidência interna negativa para a abordagem adversarial. Diferenças finitas escalam mal.
- **Relevância para a plataforma (M12, M16, M08):** moderada. A lição prática é priorizar calibração few-shot por sala (M16) em vez de invariância zero-shot.

#### ML-10 — Receita de pré-treino MAE para encoder RF (patchificação e mascaramento)

- **O que faz:** implementa a metade sem GPU de um pré-treino por autoencoder mascarado sobre janelas tempo × subportadora: recorte, patches, mascaramento determinístico com razão alta e reconstrução da grade.
- **Como faz:** recorte para número inteiro de patches, permutação semeada e funções inversas. O encoder é declarado futuro.
- **Requisitos para implementar:**
  - Hardware: GPU para o pré-treino efetivo.
  - Software: PyTorch/ViT.
  - Dados: corpora CSI heterogêneos grandes.
  - Competências: self-supervised, ViT.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 19 testes com proptest. Nenhum encoder treinado. O estudo MM-Fi conclui que encoders pré-treinados quase não transferem. Caminhos: `v2/crates/wifi-densepose-train/src/mae.rs`, `tests/test_mae.rs`.
- **Riscos/limitações:** custo de dados e computação alto e retorno baixo.
- **Relevância para a plataforma (M12):** baixa; apenas referência de pesquisa.

#### ML-11 — Port nativo do WiFlow-STD e quantização int8 medida

- **O que faz:** reimplementa em Rust/tch uma arquitetura externa de pose por CSI (WiFlow-STD, Apache-2.0), com invariantes de forma e contagem de parâmetros testáveis sem GPU, carga de checkpoints retreinados e um script de quantização int8 medida sob métrica travada.
- **Como faz:** TCN causal agrupada no tempo, blocos residuais assimétricos e atenção axial dupla no espaço. Paridade contra PyTorch. Quantização FX comparando fp32 e int8 em CPU com PCK normalizado pelo torso.
- **Requisitos para implementar:**
  - Hardware: GPU para retreino.
  - Software: PyTorch, safetensors.
  - Dados: dataset WiFlow público (15 keypoints).
  - Competências: portabilidade numérica, quantização.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNCLEAR`. 27 testes de config e 8 de modelo; a paridade está marcada como ignorada (fixtures fora do git). Os resultados relatam o checkpoint upstream **refutado como publicado** (cerca de 0,08% PCK@20) e a reprodução em cerca de 96% depois de reparos, em dataset de terceiros. Caminhos: `v2/crates/wifi-densepose-train/src/wiflow_std/`, `tests/test_wiflow_std_parity.rs`, `scripts/quantize_half_int8.py`, `benchmarks/wiflow-std/RESULTS.md`.
- **Riscos/limitações:** código derivado de terceiros com obrigação de atribuição Apache-2.0, ausente do `NOTICE`. Esqueleto e hardware diferentes.
- **Relevância para a plataforma (M11, M12):** vale como estudo de caso de governança ("reprodução de alegação de terceiros" como tipo de evidência), não como arquitetura.

#### ML-12 — Motor de inferência `wifi-densepose-nn` (ONNX Runtime, tradutor, DensePose, cabeças multitarefa com incerteza)

- **O que faz:** abstração de backend com ONNX Runtime funcional e mock, pipeline tradutor + cabeça DensePose e sete cabeças lineares sobre um embedding RF comum (pose, presença, contagem, atividade, vitais, marcha, identidade), cada uma com incerteza escalar.
- **Como faz:** trait de backend separando motor e execução. Tradutor e DensePose retornam erro explícito sem pesos. As cabeças produzem saída mais variância (incerteza heteroscedástica). Há perda triplet, perda de robustez a calibração e amostrador contrastivo.
- **Requisitos para implementar:**
  - Hardware: CPU, GPU opcional.
  - Software: onnxruntime (MIT).
  - Dados: modelos ONNX.
  - Competências: serving, multi-head com incerteza.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 40 testes, com uma fixture ONNX mínima. **Só existem os backends ONNX e mock**; as features tch e Candle só puxam dependências. O decode do tradutor devolve zeros. Não há pesos treinados. Caminhos: `v2/crates/wifi-densepose-nn/src/inference.rs`, `onnx.rs`, `translator.rs`, `densepose.rs`, `rf_encoder.rs`, `Cargo.toml`.
- **Riscos/limitações:** o README promete backends inexistentes. Há placeholders.
- **Relevância para a plataforma (M11, M12, M01, M02, M06):** bom padrão: porta de inferência com adaptador ONNX e um adaptador sintético padrão, com incerteza explícita no contrato aditivo. Fica PLANNED/BLOCKED até haver modelo validado.

#### ML-13 — AETHER: embedding contrastivo de CSI, graph-transformer CSI→pose e índice de fingerprints

- **O que faz:** embeddings autossupervisionados (estilo SimCLR/InfoNCE), mineração de negativos difíceis, alinhamento cross-modal com pose, transformer com GCN sobre o grafo COCO e índice de fingerprints com kNN e anomalia. Gera os pesos usados pelo servidor e por um wheel Python.
- **Como faz:** duas visões aumentadas (jitter, ruído, máscara, escala, rotação de fase), cabeça de projeção com LoRA opcional e InfoNCE com temperatura; atenção cruzada antena↔corpo com GCN; busca de força bruta com interface compatível com HNSW; pesos em vetor plano.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy/PyTorch, FAISS (MIT), hnswlib (Apache-2.0).
  - Dados: gravações longas não rotuladas.
  - Competências: contrastivo, GNN, busca vetorial.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: embedding 29, graph_transformer 28, mais paridade golden com pytest. É consumido pelo servidor. O model card relata acurácia de triplet temporal de 82,3% numa captura de 2 ESP32-S3 (externo ao repositório). Caminhos: `v2/crates/wifi-densepose-aether/src/embedding.rs`, `graph_transformer.rs`, `tests/golden_parity.rs`, `python/tests/golden/aether_embedding.json`.
- **Riscos/limitações:** triplet mede representação, não tarefa. Não transfere entre salas. Embeddings de identidade são biometria.
- **Relevância para a plataforma (M08, M12, M11, M15):** relevante para M08 (embeddings + kNN + anomalia em sintético, com sqlite-vec ou hnswlib). Embeddings de identidade e marcha ficam excluídos.

#### ML-14 — SONA: adaptação online (LoRA + EWC++ + detecção de drift) e inferência esparsa/quantizada

- **O que faz:** adapta modelos a mudanças do ambiente com poucos parâmetros, detecta drift estatístico, salva perfis por ambiente e reduz o custo de inferência por esparsidade e quantização INT8/FP16.
- **Como faz:** deltas LoRA mescláveis com regularização EWC (Fisher), perda de consistência temporal, detector de drift por média e variância contra baseline, perfilamento de neurônios quentes e frios e quantizador com medição de erro.
- **Requisitos para implementar:**
  - Hardware: CPU/edge.
  - Software: river (BSD-3), PEFT, `onnxruntime.quantization`.
  - Dados: amostras por ambiente.
  - Competências: aprendizado contínuo, quantização.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: sona 20, sparse_inference 21. O card relata esquecimento de cerca de 33% (não resolvido). Caminhos: `v2/crates/wifi-densepose-aether/src/sona.rs`, `sparse_inference.rs`.
- **Riscos/limitações:** EWC não impede esquecimento. O drift só por média e variância é grosseiro.
- **Relevância para a plataforma (M12, M16, M08):** a detecção de drift tem aplicação imediata (alerta de recalibração no M16, com river). LoRA e quantização ficam PLANNED.

#### ML-15 — Cog de estimativa de pose 17 keypoints (runtime out-of-process, Candle, LoRA por sala)

- **O que faz:** binário plug-in que consome janelas CSI do servidor por HTTP, infere 17 keypoints 2D e emite eventos JSON em stdout. Implementa o contrato version/manifest/health/run e aceita um adaptador LoRA por sala.
- **Como faz:** polling, janela deslizante, encoder de convoluções 1D dilatadas mais MLP com sigmoide e pesos safetensors via Candle. Sem pesos, cai num esqueleto centrado com confiança 0 (modo explícito no health). O hash combinado do artefato acompanha cada observação. **A "confiança" por quadro é uma constante igual ao PCK@50 de validação.** O manifesto traz SHA-256 e Ed25519, verificados por um gateway externo.
- **Requisitos para implementar:**
  - Hardware: ESP32, câmera para rótulos, host de inferência.
  - Software: onnxruntime, FastAPI.
  - Dados: dezenas de milhares de pares CSI–keypoints multi-sala.
  - Competências: pose, coleta pareada.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `REAL_HARDWARE_EVIDENCE`. 10 testes de fumaça, artefatos commitados, treino com 1.077 amostras de **uma sessão de 30 minutos** e validação com **PCK@20 de 3,0%** e PCK@50 de 18,5% (meta: 35%). Cold start medido num Pi 5 real. O README do cog está desatualizado. Caminhos: `v2/crates/cog-pose-estimation/src/inference.rs`, `runtime.rs`, `manifest.rs`, `cog/artifacts/train_results.json`, `tests/smoke.rs`, `docs/benchmarks/pose-estimation-cog.md`.
- **Riscos/limitações:** acurácia inútil para produção. Confiança constante engana. Pose por RF é sensível em privacidade.
- **Relevância para a plataforma (M11, M16, M13):** o valor está no contrato de plugin (processo isolado, verbos, JSON-lines, modo degradado explícito, manifesto com hash/assinatura). A pose em si fica BLOCKED, e a confiança deve ser real ou ausente.

#### ML-16 — Cog de contagem de pessoas (distribuição + confiança + fusão multi-nó)

- **O que faz:** estima uma distribuição de probabilidade sobre 0–7 pessoas, a contagem mais provável, uma faixa aproximada de 95% e uma confiança. Pode fundir vários nós.
- **Como faz:** encoder compartilhado com cabeça de contagem (softmax) e de confiança (sigmoide). A faixa sai da massa acumulada. A fusão é um produto de especialistas ponderado por confiança, com pisos numéricos. O "clip" trunca e renormaliza. É fail-closed para saídas não finitas.
- **Requisitos para implementar:**
  - Hardware: vários nós e verdade de contagem.
  - Software: numpy, scipy/torch (temperature scaling).
  - Dados: gravações multi-sala com contagens variadas e splits por sessão.
  - Competências: contagem ordinal, calibração probabilística, fusão bayesiana.
- **Evidência e maturidade:** `PARTIAL` / `REAL_HARDWARE_EVIDENCE`. 9 testes de fumaça, 7 de fusão e 3 de manifesto. Treino numa gravação com rótulos só 0/1. A v0.0.1 era degenerada. A v0.0.2 relata 62,3% global e 34,3% na classe 1, com confiança sem correlação. **A temperatura aparece no manifesto, mas nenhum código a aplica.** O "min-cut" é só um clip. Cold start medido num Pi 5. Caminhos: `v2/crates/cog-person-count/src/inference.rs`, `fusion.rs`, `runtime.rs`, `cog/artifacts/count_train_results.json`, `docs/benchmarks/person-count-cog.md`.
- **Riscos/limitações:** split aleatório numa gravação contínua, sujeito a vazamento pelo próprio protocolo do repositório (ML-04).
- **Relevância para a plataforma (M02, M03, M01):** o formato de saída (distribuição + faixa + confiança + número de nós) e a fusão por produto de especialistas são ótimos para o contrato de ocupação, inclusive no gerador sintético. O modelo aprendido fica PLANNED. Calibração por temperature scaling medida por ECE.

#### ML-17 — Estudo MM-Fi: pose e ação SOTA, fronteira de eficiência e calibração few-shot por sala (documentação)

- **O que faz:** documenta resultados reportados de pose 2D e 27 ações no MM-Fi: modelos pequenos que superariam o SOTA publicado, quantização até int4 com QAT, colapso cross-subject/cross-environment e recuperação por calibração few-shot com adaptador LoRA.
- **Como faz:** projeção linear temporal, encoder Transformer, pooling por atenção temporal (descrito como a maior alavanca), cabeça MLP e refinamento por grafo do esqueleto, com mixup, TTA, EMA e ensemble. Conclusão forte: um encoder aleatório congelado com readout treinado fica perto de um encoder treinado.
- **Requisitos para implementar:**
  - Hardware: GPU.
  - Software: PyTorch, QAT.
  - Dados: MM-Fi (CC BY-NC) e amostras rotuladas da sala.
  - Competências: pesquisa em sensing CSI.
- **Evidência e maturidade:** `RESEARCH` / `UNCLEAR`. Os números (PCK@20 em random split de cerca de 83%, micro int4 em cerca de 74%, calibração de cerca de 3% para cerca de 74%) estão só em documentos. **Os scripts de reprodução citados não existem neste checkout.** Os próprios documentos ressalvam que o random split é in-domain e parcialmente vazado (cross-environment de cerca de 10–17%). Caminhos: `docs/benchmarks/mmfi-wifi-sensing-study.md`, `docs/benchmarks/wifi-pose-efficiency-frontier.md`, `aether-arena/calibration/calibrate.py`.
- **Riscos/limitações:** não verificável. Licença não comercial. Formato de entrada incompatível com o ESP32.
- **Relevância para a plataforma (M11, M06, M16, M12):** insights estratégicos: investir em calibração por sala no onboarding, readout pequeno bem treinado e sempre reportar cross-subject/cross-environment. Hipótese de pesquisa PLANNED.

#### ML-18 — Modelos pré-treinados publicados no Hugging Face e model card (com retratações)

- **O que faz:** espelha o README de um repositório de modelos: encoder contrastivo de features ESP32, versões quantizadas, cabeça de presença, adaptadores LoRA por nó, métricas e conversão para o contêiner do servidor. Inclui correções públicas.
- **Como faz:** cerca de 8 features agregadas a cerca de 1 Hz, encoder MLP com triplet/InfoNCE, quantização, LoRA e EWC. A v2 retrata o "100% presença" (gravação de uma só classe) e uma curva de perda errada.
- **Requisitos para implementar:**
  - Hardware: 2+ ESP32-S3.
  - Software: Hugging Face Hub, safetensors.
  - Dados: gravações longas.
  - Competências: model cards honestos.
- **Evidência e maturidade:** `DOC_ONLY` / `UNCLEAR`. Pesos e métricas externos. O card lista capacidades (FC "através de roupas", estágios de sono, alerta de queda, 1–4 pessoas) sem evidência quantitativa e admite PCK@20 de 2,5% sem câmera, arquivos quantizados sem leitor e "uma sala, uma captura, dois nós". Caminhos: `docs/huggingface/MODEL_CARD.md`, `scripts/train-ruvllm.js`.
- **Riscos/limitações:** alegações de saúde e segurança sem validação. Métricas de representação confundidas com métricas de tarefa no passado.
- **Relevância para a plataforma (M01, M04, M05, M07, M09, M12, M15):** exemplo de "como corrigir publicamente" e de antipadrões. Model cards com rótulo de evidência por número e proibição de alegações clínicas.

#### ML-19 — OccWorld em Candle: world model de ocupação 3D (VQ-VAE + transformer autoregressivo)

- **O que faz:** tokeniza grades de ocupação semântica 3D e prevê autoregressivamente os próximos quadros, extraindo priors de trajetória com confiança.
- **Como faz:** embedding de classe, encoder convolucional, quantização por codebook VQ, transformer com atenção temporal e espacial e decoder. Os pesos vêm de safetensors com remapeamento. O construtor "dummy" informa explicitamente que os pesos não são treinados. As formas são validadas.
- **Requisitos para implementar:**
  - Hardware: GPU.
  - Software: PyTorch/Candle.
  - Dados: sequências de ocupação 3D (inexistentes no contexto RF).
  - Competências: world models, VQ-VAE.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 30 testes, incluindo testes de "honestidade" (flag de pesos não treinados) e checkpoint malicioso. Não há checkpoint treinado, bench nem consumidores. Caminhos: `v2/crates/wifi-densepose-occworld-candle/src/lib.rs`, `vqvae.rs`, `transformer.rs`, `inference.rs`, `tests/predict_honesty.rs`.
- **Riscos/limitações:** sem valor sem checkpoint. Fonte de ocupação 3D por RF incerta.
- **Relevância para a plataforma (M14):** visão de longo prazo. O padrão "flag de pesos treinados + testes de honestidade" é aproveitável agora.

#### ML-20 — nvsim e nvsim-server: simulador determinístico de magnetômetro NV-diamante com witness

- **O que faz:** simula o traço de um magnetômetro NV-diamante: cena com fontes magnéticas, propagação com atenuação, física do sensor, digitalização (ADC, anti-aliasing, lock-in) e quadros binários. Gera witness SHA-256 reprodutível e expõe tudo via WASM e servidor REST/WebSocket.
- **Como faz:** dipolos analíticos, laços por Biot–Savart, objetos ferrosos; tabela de materiais com flags de valores conjecturais; ODMR lorentziano, ruído de disparo, T2*, projeção em 4 eixos; quantização, passa-baixa IIR e lock-in; quadro com identificador e versão; prova sobre cena de referência; ChaCha20 semeado.
- **Requisitos para implementar:**
  - Hardware: CPU/navegador.
  - Software: numpy, magpylib (BSD-2).
  - Dados: sintéticos.
  - Competências: magnetometria NV, eletromagnetismo, DSP.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 53 testes (o README diz 34 e afirma que módulos existentes "ainda não foram entregues"). O servidor não tem testes nem autenticação, usa **CORS curinga com fallback permissivo** e o Docker faz bind em 0.0.0.0. Caminhos: `v2/crates/nvsim/src/scene.rs`, `sensor.rs`, `digitiser.rs`, `pipeline.rs`, `proof.rs`, `frame.rs`, `v2/crates/nvsim/README.md`, `v2/crates/nvsim-server/src/main.rs`.
- **Riscos/limitações:** outro domínio. Modelo de primeira ordem. Servidor inseguro fora de localhost.
- **Relevância para a plataforma (M14, M15):** muito inspirador como arquitetura `synthetic-native`: gerador físico semeado, quadros versionados, prova por hash de cena de referência e paridade entre transportes. Nunca expor endpoints sem token e com CORS aberto. Ver também UI-10.

#### ML-21 — Governança de evidência de benchmarks: ledgers append-only, protocolo RuForecast, template de model card e bridge Autogenous

- **O que faz:** padroniza o registro de desempenho: logs só com acréscimo e campos obrigatórios de procedência (commit, hash do lockfile, toolchain, host, config, hash do corpus, comando, rótulo). Inclui um template de card com rótulo por número e um utilitário local que assina e verifica a promoção de hiperparâmetros com "juízes" de replay.
- **Como faz:** separa medições de runtime de acurácia. O protocolo proíbe download implícito de modelo, dataset ou CUDA e rotula rodadas com worktree sujo como só diagnóstico. O card exige rótulos MEASURED/SYNTHETIC/CLAIMED/UNMEASURED e licenças separadas para código, pesos e dados.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Git, pytest-benchmark, Ed25519.
  - Dados: corpora com digest.
  - Competências: MLOps, supply chain.
- **Evidência e maturidade:** `DOC_ONLY` / `UNCLEAR`. O ledger de física registra latência MEASURED sem acurácia. O protocolo não tem resultados. **A bridge depende de um caminho absoluto local do autor e não compila em outro lugar.** Caminhos: `docs/benchmarks/physics-pose-refinement.md`, `docs/benchmarks/ruforecast.md`, `docs/huggingface/RUVIEW_FORECAST_MODEL_CARD_TEMPLATE.md`, `v2/crates/ruforecast-autogenous-bridge/src/main.rs`.
- **Riscos/limitações:** processo pesado sem automação.
- **Relevância para a plataforma (M15, M12):** altíssima. Ledger append-only com os campos de procedência, mapeamento de rótulos para os níveis L0… e template próprio de model card. Gratuito.

#### ML-22 — Benchmark HOMECORE vs Home Assistant (documento)

- **O que faz:** compara um núcleo de automação em Rust compatível no fio com o HA contra o próprio HA (startup, memória, tamanho, latência, throughput REST).
- **Como faz:** medição num host Windows/Docker. O próprio documento ressalva que latência e throughput comparam endpoints diferentes.
- **Requisitos para implementar:**
  - Hardware: host único.
  - Software: Home Assistant.
  - Dados: nenhum.
  - Competências: benchmarking.
- **Evidência e maturidade:** `DOC_ONLY` / `UNCLEAR`. Os scripts citados não existem no checkout. Caminhos: `docs/benchmarks/homecore-vs-home-assistant.md`.
- **Riscos/limitações:** comparação confundida e não reproduzível.
- **Relevância para a plataforma (M13):** indireta. Para M13, integrar com o HA existente em vez de reimplementar o núcleo. Ver também §4.9.

### 4.6 MAT (desastres/resgate), SAR, BFLD, point cloud, RuField e RuVector

**Escopo.** Seis crates Rust e um harness TypeScript:

1. `wifi-densepose-mat`: cerca de 21 mil linhas e cerca de 200 testes, para avaliação de vítimas em massa.
2. `wifi-densepose-sar`: tomografia RF coerente, L0 declarado.
3. `wifi-densepose-bfld`: camada de privacidade sobre beamforming feedback, com 392 anotações de teste (cerca de 40 meta-testes).
4. `wifi-densepose-pointcloud`: protótipo de nuvem de pontos.
5. `wifi-densepose-rufield`: ponte para eventos assinados.
6. `wifi-densepose-ruvector`: integrações de sinal, ANN e fusão multivista.

Mais um scaffold de agentes de desenvolvimento. A validação é toda sintética, e o RuField depende de um submódulo vazio no clone.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| MB-01 | Modelo de domínio MAT (evento, zonas, sobreviventes, eventos, deduplicação) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M15 |
| MB-02 | Detecção de sinais vitais MAT (respiração, batimento, movimento, ensemble) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M04, M05, M06, M01 |
| MB-03 | Triagem START adaptada e avaliação de vítimas em massa | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M04, M05, M15 |
| MB-04 | Localização MAT (RSSI, GDOP, profundidade, fusão, TDoA, UWB) | PARTIAL | SYNTHETIC_OR_SIMULATED | M02, M08, M14, M16 |
| MB-05 | Rastreamento de sobreviventes (Kalman 3D, húngaro, re-ID, ciclo de vida) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M02, M03 |
| MB-06 | Geração, despacho e escalonamento de alertas | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15 |
| MB-07 | API REST/WS MAT e superfícies (CLI, WASM, Python) | IMPLEMENTED_UNTESTED | UNIT_TESTS_ONLY | M13, M16 |
| MB-08 | Adaptadores de ingestão de CSI (ESP32, UDP, PCAP, Intel/Atheros, FeitCSI, simulado) | PARTIAL | SYNTHETIC_OR_SIMULATED | M12, M16 |
| MB-09 | ML de escombros e classificador de vitais com incerteza | PARTIAL | UNIT_TESTS_ONLY | M12, M04, M05 |
| MB-10 | Tomografia RF coerente de banda larga (SAR/backprojection) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M08 |
| MB-11 | BFLD: formato de frame, seções e sinks com classe de privacidade | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M12 |
| MB-12 | BFLD: risco de identidade, gate de coerência, embedding efêmero, hash por site | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| MB-13 | BFLD: plano de controle de privacidade e avaliação WiFi Veil | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16 |
| MB-14 | BFLD: matcher "Soul Signature" (biometria por RF) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15 |
| MB-15 | BFLD: integração MQTT/Home Assistant | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M01, M02 |
| MB-16 | Point cloud: profundidade por câmera, fusão voxel, PLY/splats e visualizador | PARTIAL | UNIT_TESTS_ONLY | M14, M11 |
| MB-17 | Point cloud: pipeline CSI (movimento, vitais ingênuos, pose stub, "tomografia" RSSI) | PARTIAL | UNIT_TESTS_ONLY | M08, M01, M02, M11, M12 |
| MB-18 | RuField: ponte para eventos Ed25519, P0–P5 e modalidade ultrassônica | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15, M14 |
| MB-19 | RuVector: integrações de sinal (min-cut, espectrograma, BVP, Fresnel, TDoA, compressão) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M06, M08, M04, M05, M12 |
| MB-20 | RuVector: recuperação aproximada (RaBitQ, Hadamard, HNSW) e log de privacidade | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M08, M12, M15 |
| MB-21 | RuVector: fusão multivista (atenção geométrica, GDI, Cramér-Rao, coerência) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M14, M16, M08 |
| MB-22 | RuVector: pipeline experimental "CRV" | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | NONE |
| MB-23 | Harness de agentes de desenvolvimento para o crate SAR | PARTIAL | UNIT_TESTS_ONLY | NONE |

#### MB-01 — Modelo de domínio MAT (evento de desastre, zonas, sobreviventes, event sourcing e deduplicação)

- **O que faz:** modela um incidente como raiz de agregado, com zonas de varredura (retângulo, círculo, polígono, sensores posicionados) e sobreviventes. Registra eventos de domínio num store plugável e evita contar a mesma pessoa várias vezes.
- **Como faz:** DDD com os contextos Detecção, Localização e Alertas e uma camada anticorrupção. O coordenador roda ciclos periódicos que, por zona, detectam, aplicam ensemble e limiar, localizam, registram, emitem eventos e despacham alertas. A deduplicação é em dois níveis: por proximidade espacial quando há posição real; senão, pela mesma zona com assinatura vital compatível.
- **Requisitos para implementar:**
  - Hardware: nenhum (domínio puro); três ou mais nós por zona em operação real.
  - Software: FastAPI, SQLite/Alembic, tabela de eventos append-only.
  - Dados: cenários sintéticos.
  - Competências: DDD e event sourcing.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Cerca de 37 testes de domínio e 6 de integração com senoides. **Os repositórios descritos no DDD não existem** (só há um store em memória). **O pipeline compartilha um único buffer de CSI entre todas as zonas** (o parâmetro de zona não é usado), o que gera leituras idênticas por zona. O exemplo do README falha por não inicializar o evento. Caminhos: `v2/crates/wifi-densepose-mat/src/lib.rs`, `src/domain/disaster_event.rs`, `scan_zone.rs`, `survivor.rs`, `events.rs`, `docs/ddd/wifi-mat-domain-model.md`, `docs/adr/ADR-001-wifi-mat-disaster-detection.md`.
- **Riscos/limitações:** domínio crítico para a vida (falso negativo e superconta). Sem persistência nem auditoria.
- **Relevância para a plataforma (M01, M02, M15):** útil como padrão (agregado com invariantes, eventos append-only, deduplicação em dois níveis) para ocupação e presença sintéticas. O caso de uso de resgate fica PLANNED/BLOCKED.

#### MB-02 — Detecção de sinais vitais MAT (respiração, batimento, movimento e ensemble)

- **O que faz:** estima presença e taxas de respiração e batimento, classifica o movimento (amplo, fino, tremor, periódico) e funde tudo numa confiança com triagem recomendada.
- **Como faz:** FFT com pico na banda respiratória refinado por interpolação parabólica e regularidade espectral para classificar o padrão. Para o batimento, remove o componente respiratório (notch e passa-alta) e procura pico na banda cardíaca, habilitado só em sensibilidade alta. O movimento usa variância e autocorrelação. O ensemble é uma votação ponderada que delega a triagem ao calculador canônico. Buffers comprimidos opcionais.
- **Requisitos para implementar:**
  - Hardware: CSI com taxa estável (real); nenhum no sintético.
  - Software: scipy.signal (iirnotch, butter, find_peaks).
  - Dados: séries com respiração e batimento injetados.
  - Competências: estimação espectral, fisiologia.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Cerca de 25 testes, com regressões de segurança (pulso sem respiração nunca vira "falecido"). Não há CSI real. **A taxa de amostragem padrão da configuração é alta e diverge de nós ESP32 típicos**; sem ajuste, as frequências estimadas saem erradas. Caminhos: `v2/crates/wifi-densepose-mat/src/detection/breathing.rs`, `heartbeat.rs`, `movement.rs`, `ensemble.rs`, `pipeline.rs`, `tests/integration_adr001.rs`.
- **Riscos/limitações:** batimento por CSI é muito frágil. Confiança não calibrada.
- **Relevância para a plataforma (M04, M05, M06, M01):** alta como referência algorítmica (refinamento parabólico, remoção do harmônico respiratório, regularidade espectral), sempre L0 e não clínica.

#### MB-03 — Triagem START adaptada e avaliação de vítimas em massa

- **O que faz:** converte leituras remotas em categorias (imediato, tardio, menor, falecido, desconhecido), prioriza alertas e gera uma avaliação agregada do incidente.
- **Como faz:** regra determinística adaptando o protocolo START (respiração; movimento como substituto de perfusão e estado mental). Uma sobreposição conservadora escala para "imediato" quem tem pulso sem respiração.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: funções puras e tabelas de decisão testáveis (pytest/hypothesis).
  - Dados: casos sintéticos.
  - Competências: protocolos de emergência e segurança de sistemas críticos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Contagem de testes: triage 8, serviço 4, ensemble 8. O escalonamento por deterioração prometido no guia não existe (só por tempo). Caminhos: `v2/crates/wifi-densepose-mat/src/domain/triage.rs`, `src/alerting/triage_service.rs`.
- **Riscos/limitações:** classificar alguém como "falecido" por RF é ética e legalmente sensível.
- **Relevância para a plataforma (M04, M05, M15):** baixa como funcionalidade (BLOCKED) e alta como padrão de segurança: tabela determinística com sobreposições conservadoras e regressão por caso crítico, aplicável a alertas sintéticos de queda (M07).

#### MB-04 — Localização MAT (trilateração RSSI, GDOP, profundidade sob escombros, fusão, TDoA e restrição UWB)

- **O que faz:** estima a posição 2D pelo RSSI real de cada sensor e a profundidade por atenuação, funde estimativas no tempo e oferece um solver TDoA e um refinador por alcances UWB com gating.
- **Como faz:** modelo log-distance para distância; mínimos quadrados ponderados linearizados; **GDOP real, que retorna nada em geometria colinear**. **Sensores sem RSSI real são omitidos sem fabricar medida**; com menos de três, a posição é nula. A profundidade vem da atenuação excedente sobre o espaço livre. TDoA por série de Neumann; UWB por descida de gradiente com gate de Mahalanobis.
- **Requisitos para implementar:**
  - Hardware: três ou mais transceptores posicionados; UWB opcional.
  - Software: `scipy.optimize.least_squares`, shapely.
  - Dados: layouts sintéticos com verdade.
  - Competências: geometria de localização, estimação estatística.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. 22 testes. **O perfil de escombros é stub**, que ignora a zona. TDoA e UWB não são usados pelo serviço. A ADR-144 está parcial. As precisões do guia não têm evidência. Caminhos: `v2/crates/wifi-densepose-mat/src/localization/triangulation.rs`, `depth.rs`, `fusion.rs`, `range_constraint.rs`, `docs/adr/ADR-144-uwb-range-constraint-fusion.md`.
- **Riscos/limitações:** distância por RSSI erra metros. Risco de falsa precisão.
- **Relevância para a plataforma (M02, M08, M14, M16):** alta para M16 (assistente de posicionamento com GDOP e omissão honesta de medidas ausentes) e para M14 (incerteza por posição).

#### MB-05 — Rastreamento de sobreviventes (Kalman 3D, associação húngara, re-identificação por fingerprint e ciclo de vida)

- **O que faz:** mantém trilhas entre ciclos, associa observações, recupera trilhas perdidas e gerencia estados (tentativa, ativa, perdida, encerrada, resgatada).
- **Como faz:** Kalman de velocidade constante 3D, custo de Mahalanobis com gate e algoritmo húngaro (guloso acima de certo tamanho). Re-ID por distância euclidiana ponderada sobre features normalizadas. Máquina de estados com contadores.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: filterpy (MIT), `linear_sum_assignment`.
  - Dados: trajetórias sintéticas com oclusões.
  - Competências: MOT.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 18 testes. **O ciclo de varredura nunca chama o rastreador**, e a API também não o usa (biblioteca não integrada). Caminhos: `v2/crates/wifi-densepose-mat/src/tracking/tracker.rs`, `kalman.rs`, `fingerprint.rs`, `lifecycle.rs`, `docs/adr/ADR-026-survivor-track-lifecycle.md`.
- **Riscos/limitações:** re-ID por vitais é biometria fraca.
- **Relevância para a plataforma (M02, M03):** muito alta para contagens estáveis e eventos de entrada/saída auditáveis. Re-ID fica BLOCKED. Ver também SV-10 e WM-12.

#### MB-06 — Geração, despacho e escalonamento de alertas MAT

- **O que faz:** gera alertas priorizados, envia para handlers plugáveis, escala os não reconhecidos por tempo ou capacidade e permite reconhecê-los.
- **Como faz:** gerador a partir do agregado e dispatcher com pendentes, handlers assíncronos (só console e áudio implementados), escalonamento por timeout e forçado por capacidade, e um evento por alerta.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: APScheduler, Apprise/ntfy/Gotify (self-hosted), MQTT.
  - Dados: eventos sintéticos.
  - Competências: desenho de alertas.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 10 testes mais 4. Os canais "push" e "rádio" do guia não existem. Caminhos: `v2/crates/wifi-densepose-mat/src/alerting/generator.rs`, `dispatcher.rs`, `src/domain/alert.rs`.
- **Riscos/limitações:** sem persistência. Fadiga de alerta.
- **Relevância para a plataforma (M13, M15):** média-alta. Pipeline de alerta com handlers plugáveis, timeout e reconhecimento auditável, em dry-run.

#### MB-07 — API REST/WebSocket MAT e superfícies de consumo (CLI, WASM e Python)

- **O que faz:** expõe eventos, zonas, sobreviventes, alertas, ingestão de CSI, controle de varredura e status via HTTP e WebSocket. A mesma lógica é reaproveitada por CLI, WASM e wheel Python.
- **Como faz:** roteador com estado em memória e broadcast para WS, DTOs e erros mapeados.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: já coberto pela stack da plataforma.
  - Dados: eventos sintéticos.
  - Competências: APIs seguras.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNIT_TESTS_ONLY`. Os handlers (cerca de 1,1 mil linhas) não têm testes. **O teste de integração diz cobrir a API, mas não a toca.** **A API não tem autenticação.** Caminhos: `v2/crates/wifi-densepose-mat/src/api/mod.rs`, `handlers.rs`, `websocket.rs`, `state.rs`, `v2/crates/wifi-densepose-cli/src/mat.rs`, `python/src/bindings/mat.rs`.
- **Riscos/limitações:** permite injetar vítimas fabricadas e negação de serviço.
- **Relevância para a plataforma (M13, M16):** baixa; é contraexemplo. Toda ingestão deve exigir autenticação, limites e marcação de origem e evidência.

#### MB-08 — Adaptadores de ingestão de CSI (ESP32 serial, UDP, PCAP, Intel 5300/Atheros, FeitCSI 802.11ax e simulado)

- **O que faz:** abstrai fontes heterogêneas atrás de um adaptador único com descoberta, stream assíncrono e leituras normalizadas.
- **Como faz:** camada anticorrupção com despacho por tipo. Parser CSV do ESP-CSI com serial atrás de feature opcional (sem ela, erro tipado). Parsers de formatos conhecidos, mas **leitura ao vivo de Intel/Atheros retorna "hardware indisponível"**. UDP e replay PCAP. O parser FeitCSI (AX200/AX210, até 160 MHz, 6 GHz) valida cabeçalho, versão e teto de alocação e faz reamostragem explícita registrada. PicoScenes é recusado. Simulador com vitais sintéticos.
- **Requisitos para implementar:**
  - Hardware: ESP32-S3, Intel AX210; nenhum na plataforma.
  - Software: pyserial, asyncio, scapy/dpkt; FeitCSI (GPL) só como processo externo.
  - Dados: capturas gravadas com proveniência.
  - Competências: formatos CSI, parsing defensivo.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. Cerca de 49 testes. As fixtures FeitCSI são geradas em código, e a ADR-292 declara a validação em silício pendente. O layout FeitCSI foi derivado da leitura de código GPL (ver §8). Caminhos: `v2/crates/wifi-densepose-mat/src/integration/hardware_adapter.rs`, `csi_receiver.rs`, `feitcsi.rs`, `signal_adapter.rs`, `docs/adr/ADR-292-wideband-80211ax-csi-ingest.md`.
- **Riscos/limitações:** formatos de terceiros mudam. Ecossistema GPL. Superfície de ataque.
- **Relevância para a plataforma (M12, M16):** média. Erro tipado em vez de dado fabricado, teto de alocação, replay determinístico e reamostragem registrada, para a futura porta Acquisition.

#### MB-09 — ML de escombros e classificador de vitais com incerteza (fallback por regras)

- **O que faz:** pretende classificar o material dos escombros, prever atenuação e profundidade com incerteza e classificar padrões vitais com incerteza aleatória e epistêmica.
- **Como faz:** a arquitetura declarada é multi-cabeça com MC Dropout. **Na prática, a inferência ONNX está atrás de uma feature que não existe no `Cargo.toml`** (avisos suprimidos), então sempre roda o fallback por regras.
- **Requisitos para implementar:**
  - Hardware: GPU para treino.
  - Software: onnxruntime, scikit-learn/PyTorch.
  - Dados: dados rotulados de atenuação e vitais sob escombros, praticamente inexistentes.
  - Competências: quantificação de incerteza.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 20 testes. Não existe nenhum modelo `.onnx` de escombros ou vitais no repositório. Caminhos: `v2/crates/wifi-densepose-mat/src/ml/mod.rs`, `debris_model.rs`, `vital_signs_classifier.rs`, `v2/crates/wifi-densepose-mat/Cargo.toml`.
- **Riscos/limitações:** a documentação sugere ML real que não roda.
- **Relevância para a plataforma (M12, M04, M05):** baixa como modelo. Lição para M12: todo modelo declara se está ativo, qual fallback está em uso e com qual evidência, e um flag morto deve falhar o build ou o teste.

#### MB-10 — Tomografia RF coerente de banda larga (SAR/backprojection), crate de pesquisa

- **O que faz:** simula medições complexas de frequência escalonada coletadas por abertura sintética sobre alvos pontuais, reconstrói a refletividade 3D por backprojection delay-and-sum, extrai nuvem de pontos e confere a resolução contra fórmulas fechadas.
- **Como faz:** simulador direto determinístico (ChaCha20) com atraso de ida e volta e ruído. A reconstrução corrige a fase e soma de forma coerente, em paralelo, avançando o fasor por multiplicação incremental (provado equivalente à forma direta). A extração usa limiar relativo e máximos locais. Fórmulas clássicas de radar (resolução em alcance e transversal, tolerância de erro de pose) são verificadas.
- **Requisitos para implementar:**
  - Hardware: VNA/SDR de banda larga com antena precisa (real); CPU.
  - Software: numpy, numba/jax opcional, Open3D.
  - Dados: cenas sintéticas.
  - Competências: radar/SAR, processamento coerente.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 25 testes, 3 deles de validação física. Declara-se L0/SYNTHETIC e é crate folha. O desempenho foi medido por criterion (software). Caminhos: `v2/crates/wifi-densepose-sar/src/lib.rs`, `measurement.rs`, `reconstruct.rs`, `resolution.rs`, `pointcloud.rs`, `tests/physics_validation.rs`, `docs/adr/ADR-287-coherent-wideband-rf-tomography-crate.md`.
- **Riscos/limitações:** não se transfere para Wi-Fi comum (CSI de ESP32 não é coerente nem tem banda suficiente). Pode alimentar alegações de "ver através da parede".
- **Relevância para a plataforma (M14, M08):** média-baixa. É exemplo de disciplina "provado, não afirmado" (testes contra fórmulas físicas). Um módulo de pesquisa em numpy marcado RESEARCH/L0, se desejado.

#### MB-11 — BFLD: formato de frame, payload em seções e sinks com classe de privacidade

- **O que faz:** define o transporte de dados derivados de beamforming feedback (802.11ac/ax): cabeçalho fixo, seções tipadas e CRC. Garante pelo sistema de tipos que dados brutos nunca saiam do nó.
- **Como faz:** cabeçalho little-endian sem unsafe. Seções com prefixo de comprimento (ângulos comprimidos opacos, proxies de amplitude e fase, SNR, delta opcional, extensão). CRC-32. Quatro classes de privacidade (bruto local, derivado, anônimo, restrito) e traits de sink (local, rede, Matter) que declaram a classe mínima aceita. Uma checagem bloqueia frame bruto em sink de rede. **O rebaixamento é monotônico** e zera seções proibidas com proteção contra otimização.
- **Requisitos para implementar:**
  - Hardware: AP 802.11ac/ax e monitor mode (real); nenhum na plataforma.
  - Software: struct/construct, zlib.crc32, dataclasses imutáveis.
  - Dados: frames sintéticos.
  - Competências: protocolos binários, privacy by design.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 60 testes, com proptest. **Não decodifica BFI real** (a matriz é opaca). As ADRs de captura estão "Proposed". Caminhos: `v2/crates/wifi-densepose-bfld/src/lib.rs`, `frame.rs`, `payload.rs`, `sink.rs`, `privacy_gate.rs`, `docs/adr/ADR-118-bfld-beamforming-feedback-layer-for-detection.md`, `docs/adr/ADR-119-bfld-frame-format-and-wire-protocol.md`.
- **Riscos/limitações:** as garantias de tipo valem só dentro do processo; em Python exigem testes de propriedade equivalentes. Captura em monitor mode tem implicações legais.
- **Relevância para a plataforma (M15, M12):** alta. Classe de privacidade em todo evento, sinks que declaram a classe mínima e rebaixamento irreversível com erro tipado, como campo aditivo no contrato 2.0.0.

#### MB-12 — BFLD: score de risco de identidade, gate de coerência, embedding efêmero e hash por site com rotação

- **O que faz:** mede quão identificável é o fluxo e decide publicar, rebaixar, descartar ou recalibrar. Mantém embeddings de identidade só em RAM e gera pseudônimos não correlacionáveis entre sites e trocados diariamente.
- **Como faz:** o escore é o produto limitado de quatro fatores (separabilidade, estabilidade, consistência, confiança), conservador sob incerteza, com quatro ações. O gate aplica histerese e debounce temporal, inclusive com relógio fora de ordem. O embedding é um tipo sem serialização nem clonagem, com Debug redigido e zerado no descarte, guardado num anel drenado na recalibração. O pseudônimo é BLAKE3 com chave secreta por site sobre a época do dia e as features canônicas.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: `hashlib.blake2b` com chave ou blake3, `secrets`.
  - Dados: features sintéticas.
  - Competências: pseudonimização, linkability, criptografia.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: risco 12, gate 13, desvio de relógio 7, anel 9, hasher 8, mais isolamento e determinismo. As entradas de risco vêm do chamador. **O pipeline não é usado pelo engine nem pelo servidor**, que só consomem as classes e os modos. Caminhos: `v2/crates/wifi-densepose-bfld/src/identity_risk.rs`, `coherence_gate.rs`, `embedding.rs`, `embedding_ring.rs`, `signature_hasher.rs`, `pipeline.rs`, `docs/adr/ADR-120-bfld-privacy-class-and-hash-rotation.md`, `docs/adr/ADR-121-bfld-identity-risk-scoring.md`.
- **Riscos/limitações:** "zerar no descarte" não garante ausência de cópias, e em Python é ainda mais fraco. A rotação de sal exige gestão de segredos.
- **Relevância para a plataforma (M15):** muito alta. Pseudônimos com chave por instalação e rotação diária, gate com histerese e ação "recalibrar" que invalida o estado identificável. Embeddings de identidade ficam BLOCKED.

#### MB-13 — BFLD: plano de controle de privacidade (modos, ações e atestação encadeada) e avaliação WiFi Veil

- **O que faz:** expõe ao operador modos de privacidade nomeados (pesquisa bruta, casa privada, empresa anônima, cuidado com consentimento, sem identidade estrita), cada um com uma classe-alvo e ações obrigatórias. **Toda mudança de modo gera uma prova de atestação encadeada por hash.** Opcionalmente avalia o risco de reidentificação via WiFi Veil.
- **Como faz:** as ações são um conjunto de bits (permitir, suprimir identidade, reduzir resolução, descartar bruto, só agregados). Um registro é a fonte única do modo ativo, e cada prova BLAKE3 é encadeada à anterior. O Veil é feature opcional (repositório git externo), sintético e consultivo.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Enum/IntFlag, hashlib, SQLite.
  - Dados: nenhum.
  - Competências: governança de privacidade (LGPD/GDPR), trilhas imutáveis.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 6 testes mais 6. **É a parte do BFLD efetivamente consumida em produção** ("casa privada" como padrão). Caminhos: `v2/crates/wifi-densepose-bfld/src/privacy_mode.rs`, `veil.rs`, `v2/crates/wifi-densepose-engine/src/lib.rs`, `docs/adr/ADR-294-wifi-veil-integration.md`.
- **Riscos/limitações:** cadeia de hash sem assinatura ou âncora só detecta adulteração parcial. O modo "com consentimento" exige fluxo real.
- **Relevância para a plataforma (M15, M16):** muito alta. Modo de privacidade visível ao operador, mapeado para classe e ações, com atestação encadeada e assinatura Ed25519 opcional por elo.

#### MB-14 — BFLD: matcher "Soul Signature" (identificação biométrica por canais RF)

- **O que faz:** compara assinaturas multicanal (embedding contrastivo, reflexão por subportadora, perfis cardíaco e respiratório) para reconhecer pessoas inscritas e alimentar o oráculo do gate.
- **Como faz:** cosseno por canal, ponderado e normalizado pelos canais disponíveis nos dois lados (degradação graciosa). Retorna escore, número de canais e contribuição por canal.
- **Requisitos para implementar:**
  - Hardware: arranjo multicanal (real).
  - Software: numpy.
  - Dados: biometria real com consentimento (é o bloqueio ético e legal).
  - Competências: biometria (FAR/FRR, EER), ética.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Os testes declaram dados sintéticos e nunca pessoas reais, e incluem um resultado negativo (canais cardíaco e respiratório sozinhos não separam identidades). O código afirma que a identificação nominal não foi demonstrada. Caminhos: `v2/crates/wifi-densepose-bfld/src/soul_match.rs`, `soul_channels.rs`, `tests/soul_match.rs`.
- **Riscos/limitações:** biometria sem consentimento é vigilância. Dado sensível (LGPD).
- **Relevância para a plataforma (M15):** deve permanecer **BLOCKED** (a plataforma proíbe biometria). Vale apenas como padrão de documentação honesta de resultado negativo.

#### MB-15 — BFLD: integração MQTT/Home Assistant (tópicos, discovery, disponibilidade/LWT e worker)

- **O que faz:** publica presença, movimento, contagem, atividade por zona, confiança e risco de identidade como entidades do HA, com discovery, LWT e worker dedicado. Inclui blueprints (iluminação por presença, HVAC por movimento, anomalia de risco).
- **Como faz:** roteador puro de tópico e payload condicionado à classe de privacidade (o risco de identidade só sai numa classe específica). Discovery retido e estado não retido. Trait de publicação com implementação de captura para testes e cliente MQTT com TLS.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Mosquitto, aiomqtt/paho-mqtt, Home Assistant.
  - Dados: eventos sintéticos.
  - Competências: discovery MQTT do HA, QoS, retain, LWT.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: roteamento 11, discovery 10+6, disponibilidade 10, LWT 8, smoke 7, blueprints. O teste com Mosquitto ao vivo é opcional. Há discrepância de versão de cliente entre README e Cargo. Caminhos: `v2/crates/wifi-densepose-bfld/src/mqtt_topics.rs`, `ha_discovery.rs`, `availability.rs`, `rumqttc_publisher.rs`, `pipeline_handle.rs`, `tests/mosquitto_integration.rs`, `docs/adr/ADR-122-bfld-ruview-ha-matter-exposure.md`.
- **Riscos/limitações:** expõe ocupação residencial na LAN.
- **Relevância para a plataforma (M13, M01, M02):** muito alta. Discovery do HA com filtragem por classe de privacidade antes do egresso, LWT e separação de tópicos retidos e não retidos, em dry-run. Ver também SS-16.

#### MB-16 — Point cloud: profundidade por câmera, retroprojeção, fusão voxel, PLY/Gaussian splats e visualizador 3D

- **O que faz:** gera nuvem de pontos a partir de câmera, funde com ocupação derivada de Wi-Fi, exporta em PLY, converte para splats e serve um visualizador 3D.
- **Como faz:** captura via ferramentas externas. A profundidade vem de um servidor MiDaS local ou, na falta dele, de pseudo-profundidade por luminância e bordas. Retroprojeção pinhole, deduplicação por voxel, splats por voxel. Servidor com loopback por padrão. O visualizador usa three.js e **MediaPipe FaceMesh via CDN**.
- **Requisitos para implementar:**
  - Hardware: webcam; GPU opcional.
  - Software: Open3D (MIT), three.js/react-three-fiber; MiDaS/Depth-Anything se câmera for permitida.
  - Dados: quadros de câmera (dado pessoal).
  - Competências: visão 3D, gráficos web.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Poucos testes (fusion 5, pointcloud 3, depth 2) e sem README. O servidor MiDaS não faz parte do repositório. Sem autenticação. Caminhos: `v2/crates/wifi-densepose-pointcloud/src/main.rs`, `camera.rs`, `depth.rs`, `fusion.rs`, `pointcloud.rs`, `stream.rs`, `viewer.html`.
- **Riscos/limitações:** landmarks faciais por câmera contradizem a proposta "sem câmera". Dependências por CDN.
- **Relevância para a plataforma (M14, M11):** baixa a média. Aproveitar só o visualizador de voxels sintéticos (empacotado localmente) e o export PLY. Câmera e FaceMesh ficam fora ou BLOCKED.

#### MB-17 — Point cloud: pipeline CSI (parser ADR-018, movimento/vitais heurísticos, pose stub, "tomografia" RSSI, fingerprint de sala e treino)

- **O que faz:** recebe CSI por UDP, detecta movimento, estima respiração, produz uma "pose" e uma grade 3D, registra fingerprints de sala, alterna modo noturno, calibra profundidade e exporta pares para um "cérebro" externo.
- **Como faz:** usa o parser de referência. O movimento vem da variação de amplitude. A respiração vem de contagem de picos com taxa assumida, e **o batimento é fixado em zero**. **A pose é um stub declarado.** **A "tomografia" coloca blobs gaussianos em posições fixas por ID de nó**, escalados por RSSI e suavizados por EMA (com proteção contra NaN). Fingerprint por média e cosseno, treino por varredura de limiar e saneamento de caminhos.
- **Requisitos para implementar:**
  - Hardware: dois ou mais ESP32-S3.
  - Software: asyncio, numpy/scipy.
  - Dados: frames rotulados.
  - Competências: CSI e tomografia real (Radio Tomographic Imaging com regularização).
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Contagem de testes: parser 10, csi_pipeline 3, training 4. O listener UDP fica em 0.0.0.0 no modo serve. Caminhos: `v2/crates/wifi-densepose-pointcloud/src/csi_pipeline.rs`, `parser.rs`, `training.rs`, `brain_bridge.rs`.
- **Riscos/limitações:** visualizações plausíveis de dados não físicos induzem confiança indevida.
- **Relevância para a plataforma (M08, M01, M02, M11, M12):** média como contraexemplo. Fingerprint de sala por estatística e cosseno e grade com EMA protegida contra NaN são reaproveitáveis. Tomografia real deve usar RTI com Tikhonov. A pose nunca deve ser exibida como pose.

#### MB-18 — RuField: ponte anticorrupção para FieldEvents assinados (Ed25519), mapeamento P0–P5 e modalidade ultrassônica

- **O que faz:** converte cada ciclo num evento de campo assinado, com mapeamento de privacidade **pelo conteúdo de informação** e egresso fail-closed. Expõe o resultado ao vivo e acrescenta perfis ultrassônicos como segunda modalidade.
- **Como faz:** snapshot de primitivas próprias convertido em evento com modalidade, eixos, posição (só se houver pico real, nunca fabricada) e assinatura. A classe "derivada", com poucos bytes mas portadora de identidade, é mapeada para níveis biométricos altos, nunca para o mais baixo. O rebaixamento só aumenta a privacidade. O egresso só permite os níveis baixos sem cerimônia de consentimento. Há checagem de "fusabilidade" (assinatura verificada). A modalidade ultrassônica é simulada e não pode alegar pessoa.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: PyNaCl/cryptography, Pydantic, JSON canônico (RFC 8785).
  - Dados: snapshots sintéticos.
  - Competências: proveniência criptográfica, taxonomias de privacidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 26 testes. **As cinco dependências rufield-* ficam num submódulo vazio no clone** (build não confirmado). A documentação diz que não está ligado ao servidor, mas o servidor já o liga (SS-19). Chave de desenvolvimento. Caminhos: `v2/crates/wifi-densepose-rufield/src/lib.rs`, `privacy.rs`, `bridge.rs`, `ultrasonic.rs`, `tests/p1_gates.rs`, `docs/adr/ADR-262-rufield-ruview-integration.md`.
- **Riscos/limitações:** gestão de chaves indefinida. A assinatura prova origem, não veracidade.
- **Relevância para a plataforma (M15, M14):** muito alta. Assinatura Ed25519 por evento, mapeamento de privacidade pelo conteúdo, posição nunca fabricada e egresso fail-closed. Os níveis de privacidade podem coexistir com os níveis de evidência.

#### MB-19 — RuVector: integrações de sinal ADR-017 (min-cut de subportadoras, espectrograma com atenção, BVP, Fresnel, TDoA, buffers comprimidos)

- **O que faz:** seleciona subportadoras sensíveis a movimento, limpa espectrogramas Doppler, agrega BVP, estima distâncias TX–corpo–RX e comprime buffers de respiração e batimento.
- **Como faz:** corte mínimo num grafo de similaridade de sensibilidade, gate por atenção, atenção produto-escalar ponderando STFT, mínimos quadrados regularizados por Neumann (Fresnel e TDoA) e compressão temporal em camadas com potência extraível sem descompressão total.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: networkx/igraph, scipy.signal, scipy.sparse.linalg, zarr/numcodecs.
  - Dados: CSI sintético.
  - Competências: grafos, álgebra esparsa, Fresnel.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 23 testes. A alegação de acurácia TDoA abaixo de alguns metros só tem layouts sintéticos. Licenças das crates externas não verificadas. Caminhos: `v2/crates/wifi-densepose-ruvector/src/signal/subcarrier.rs`, `spectrogram.rs`, `bvp.rs`, `fresnel.rs`, `src/mat/triangulation.rs`, `v2/crates/wifi-densepose-ruvector/README.md`, `docs/adr/ADR-017-ruvector-signal-mat-integration.md`.
- **Riscos/limitações:** dependência de um ecossistema de um único mantenedor. Quantização pode apagar vitais fracos.
- **Relevância para a plataforma (M06, M08, M04, M05, M12):** média. Seleção de subportadoras por grafo e Fresnel no pipeline sintético; retenção em camadas de precisão inspira a política de retenção.

#### MB-20 — RuVector: recuperação aproximada (sketch RaBitQ, rotação Hadamard, estimador não-viesado, HNSW float e quantizado) e log de eventos de privacidade

- **O que faz:** responde a "já vi algo parecido?" para embeddings (re-ID, fingerprint de sala, novidade), com sketches de 1 bit, índice HNSW e medição honesta de recall e QPS. Mantém um log de novidade sem embeddings brutos.
- **Como faz:** quantização por sinal com Hamming por popcount, rotação ortogonal estruturada antes de quantizar, estimador de produto interno para re-ranqueamento, cobertura top-K contra a verdade em float, HNSW com gate de recall e variante quantizada, formato de sketch versionado e log em anel com hash SHA-256 de conteúdo.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: hnswlib, FAISS, sqlite-vec, numpy.
  - Dados: embeddings sintéticos com verdade exata.
  - Competências: ANN, quantização vetorial, metodologia de benchmark.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Cerca de 84 testes. A ADR-261 relata números em fixture sintético e **um resultado negativo honesto**: a variante quantizada não superou o HNSW float com recall igual. O gate de recall pegou um bug real. Caminhos: `v2/crates/wifi-densepose-ruvector/src/sketch.rs`, `rotation.rs`, `estimator.rs`, `coverage.rs`, `hnsw.rs`, `hnsw_quantized.rs`, `event_log.rs`, `docs/adr/ADR-084-rabitq-similarity-sensor.md`, `docs/adr/ADR-261-ruvector-graph-ann-index.md`.
- **Riscos/limitações:** a "não invertibilidade" do sketch é argumento informal. Re-ID é sensível. Implementação própria de HNSW tem custo de manutenção.
- **Relevância para a plataforma (M08, M12, M15):** alta para M08 (busca por similaridade com sqlite-vec/hnswlib e gate de recall versus força bruta no CI). Metodologia com resultado negativo é exemplar.

#### MB-21 — RuVector: fusão multivista (atenção com viés geométrico, GDI, cota de Cramér-Rao e gate de coerência de fase)

- **O que faz:** combina embeddings de vários pontos de vista, avalia a qualidade geométrica do arranjo (diversidade e limite teórico de precisão) e bloqueia atualizações quando o ambiente está instável.
- **Como faz:** atenção entre pontos de vista com termo de separação angular e base (projeções identidade, sem treino); índice de diversidade geométrica; cota de Cramér-Rao pela inversa da informação de Fisher; coerência como magnitude da média de fasores unitários. Um agregado orquestra tudo.
- **Requisitos para implementar:**
  - Hardware: nenhum (real: 3+ nós posicionados).
  - Software: numpy.
  - Dados: layouts e fases sintéticas.
  - Competências: teoria de estimação, geometria de arranjos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 50 testes. A documentação fala em atenção "aprendida", mas não há treino. Caminhos: `v2/crates/wifi-densepose-ruvector/src/viewpoint/mod.rs`, `attention.rs`, `geometry.rs`, `coherence.rs`, `fusion.rs`, `docs/adr/ADR-031-ruview-sensing-first-rf-mode.md`.
- **Riscos/limitações:** a CRB é limite inferior. Coerência ruidosa em CSI comum.
- **Relevância para a plataforma (M14, M16, M08):** muito alta para M16: GDI e CRB como "escore de qualidade do posicionamento" antes de coletar dados, e coerência como pré-condição de calibração, em numpy puro.

#### MB-22 — RuVector: pipeline experimental "CRV" de sessões multiestágio

- **O que faz:** organiza CSI em sessões de seis estágios inspirados num protocolo de "Coordinate Remote Viewing": padrão gestáltico, features "sensoriais", topologia da malha, coerência, busca e partição de pessoas por min-cut, e convergência entre salas.
- **Como faz:** limiares, encoder espectral, grafo de APs, busca diferenciável e min-cut.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: networkx, scikit-learn.
  - Dados: sintéticos.
  - Competências: grafos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 43 testes, atrás de feature desligada. Sem consumidores identificados. Caminhos: `v2/crates/wifi-densepose-ruvector/src/crv/mod.rs`, `benches/crv_bench.rs`.
- **Riscos/limitações:** a nomenclatura parapsicológica traz risco de credibilidade.
- **Relevância para a plataforma (NONE):** muito baixa e não recomendada. A partição de pessoas pode vir de clustering ou rastreamento direto.

#### MB-23 — Harness de agentes de desenvolvimento para o crate SAR (Claude Code, router k-NN e flywheel)

- **O que faz:** scaffold para contribuidores com IA: papéis de agentes, roteamento de consultas para o modelo mais barato previsto, laço de auto-melhoria com gate e permissões de host de agente.
- **Como faz:** k-NN sobre embedding manual de 4 eixos com exemplos ilustrativos, flywheel com proponente e avaliador sintéticos, permissões que negam push e leitura de `.env`, e servidores MCP via npx com versão "latest".
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Node 20+, vitest.
  - Dados: logs de avaliação.
  - Competências: engenharia de agentes.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Os agentes são arquivos de 7 linhas, o manifesto está defasado e há 3 arquivos de teste. Caminhos: `harness/wifi-densepose-sar/README.md`, `src/router.ts`, `src/flywheel.ts`, `.claude/settings.json`.
- **Riscos/limitações:** MCP com versão não fixada é risco de supply chain.
- **Relevância para a plataforma (NONE):** só para o processo de desenvolvimento (permissões mínimas e versões fixadas). Ver também OP-11 e OP-12.

### 4.7 World model unificado, fusão multimodal e memória espacial

**Escopo.** São cerca de 20 crates Rust (quase todos biblioteca pura, determinística e sem I/O) e a pasta Python `aether-arena`. Há duas linhagens de "world model" que não se unem no código:

- **ADR-273..281**: `ruview-unified`, com contrato RF nativo, adaptadores, encoder, memória de Gaussianas, gerador físico e política.
- **ADR-300 ("perception substrate")**: ontologia, fusão, rastreamento, gêmeo RF, posicionamento, memória/anomalia, contrafactual, sensoriamento ativo, OOD, auto-levantamento, memória criptografada, evidência JSONL e cliente de nuvem.

Quase todo crate tem testes unitários, mas todos usam fixtures sintéticas (L0/L1). **Nenhum está ligado ao servidor ao vivo**; só o cliente Cognitum é consumido pela CLI. `ruview-swarm` e `worldgraph` são submódulos vazios.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| WM-01 | Contrato de quadro RF nativo (RfFrameV2) com tensor canônico derivado | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M15 |
| WM-02 | Registro de adaptadores multimodais, ranging BLE CS e mapa delay-Doppler | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M14, M08 |
| WM-03 | Encoder RF "fundacional" com reconstrução mascarada e adaptadores menores que 1% | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M06, M11, M12 |
| WM-04 | Protocolo de avaliação anti-vazamento e aceitação ponta a ponta | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M12, M15, M16 |
| WM-05 | Memória de Gaussianas RF com consultas de ganho e atualização inversa | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M08 |
| WM-06 | Grafo de cena com ativação limitada por tarefa | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M14, M15 |
| WM-07 | Gerador de mundos RF sintéticos guiado por física | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M03, M12, M14 |
| WM-08 | Plano de controle de privacidade de borda e trust boundary | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M13 |
| WM-09 | Percepção programável (contrato de tarefa, AoI, fusão coerente, atuadores) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M15, M13 |
| WM-10 | Ontologia espacial canônica (Site▸Building▸Floor▸Space▸Zone) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M14, M15, M16, M02, M03 |
| WM-11 | Fusão de presença por variância inversa com UNKNOWN | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M14 |
| WM-12 | Rastreamento persistente pseudônimo | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M02, M03, M15 |
| WM-13 | Gêmeo digital RF com delta observado-vs-previsto | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M08, M14, M16 |
| WM-14 | Otimizador de posicionamento de sensores | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M16, M08, M14 |
| WM-15 | Auto-levantamento de nós em modo verificação (FTM/UWB) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M16 |
| WM-16 | Memória espacial de longo prazo e anomalia por desvio da normalidade | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M08, M02, M09, M14, M15 |
| WM-17 | Memória vetorial criptografada por tenant (ADR-326) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M14 |
| WM-18 | Inferência contrafactual de cena | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M14 |
| WM-19 | Sensoriamento ativo (ganho de informação e controle em malha fechada) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M14, M16 |
| WM-20 | Detecção OOD e gating de domínio (KNOWN/DEGRADED/UNKNOWN) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15, M16, M08 |
| WM-21 | Exportação de evidência espacial em JSONL versionado | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M14 |
| WM-22 | Cliente de leitura Cognitum Spaces com fronteira de dados limitada | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M13 |
| WM-23 | Projeção off-axis, filtro One Euro e paralaxe RF grosseira | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | NONE |
| WM-24 | AetherArena: benchmark com ledger encadeado e Space de leaderboard | PARTIAL | UNCLEAR | M12, M15, M11 |
| WM-25 | Calibração por sala via adaptador LoRA (AetherArena) | IMPLEMENTED_TESTED | UNCLEAR | M12, M11, M16 |

#### WM-01 — Contrato de quadro RF nativo (RfFrameV2) com tensor canônico como visão derivada

- **O que faz:** registro autoritativo de uma captura RF. Preserva o tensor complexo nativo de rank arbitrário, com:
  - máscara de validade e eixos declarados (tempo, frequência, atraso, Doppler, alcance, azimute, antena);
  - estado de fase declarado (bruta, sanitizada, calibrada, indisponível);
  - poses TX/RX num referencial único, geometria de antenas, idade da amostra, qualidade e proveniência.
  O tensor canônico de tamanho fixo é **só uma visão calculada** e nunca sobrescreve o nativo.
- **Como faz:** construtor validado impõe aridade de shape e máscara e coerência de eixos, e impede misturar proveniência sintética com medida (quadro sintético não declara evidência acima de L0). A conversão reamostra por referência imutável. Erros tipados.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, pydantic.
  - Dados: capturas multi-dispositivo para validar eixos.
  - Competências: modelagem de dados RF (CSI/CIR, CFO/STO), versionamento de schema.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 5 testes de invariantes e proptest garantindo que o construtor nunca entra em pânico. Sem captura real. Caminhos: `v2/crates/ruview-unified/src/frame.rs`, `tensor.rs`, `docs/adr/ADR-279-native-rf-frame-contract.md`, `docs/adr/ADR-274-universal-rf-encoder-adapter-registry.md`.
- **Riscos/limitações:** complexidade excessiva para CSI simples. O tensor canônico perde informação.
- **Relevância para a plataforma (M12, M15):** alta como padrão de contrato. Campos aditivos de estado de fase, máscara, idade da amostra e classe de proveniência no 2.0.0, travando SIMULATED em L0.

#### WM-02 — Registro de adaptadores multimodais (WiFi CSI, FMCW, UWB CIR, SRS celular, BLE Channel Sounding), ranging BLE CS e mapa delay-Doppler

- **O que faz:** converte capturas de fornecedores diferentes num tensor canônico. Estima distância por BLE Channel Sounding com validação cruzada entre fase e RTT e calcula a transformada atraso-Doppler.
- **Como faz:** três estágios por adaptador: layout (inclui DFT de tempo rápido no FMCW e de-combing de SRS), normalização de amplitude pela mediana com offset registrado e sanitização de fase por remoção de offset e rampa (mínimos quadrados), salvo captura calibrada. O registro é fail-closed. No BLE CS, divergência entre fase e RTT gera anomalia (indício de relay ou multipercurso), em vez de média. O mapa atraso-Doppler é separável (IDFT/DFT).
- **Requisitos para implementar:**
  - Hardware: opcional (ESP32, FMCW, UWB, BLE 6.0).
  - Software: numpy/scipy.
  - Dados: capturas por modalidade.
  - Competências: OFDM, FMCW, ranging, sanitização de fase.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 7 testes (incluindo distância BLE exata e sinalização tipo relay) e benches. Um exemplo HIL com ESP32 existe sem saída capturada (capacidade alegada). Caminhos: `v2/crates/ruview-unified/src/adapters.rs`, `tensor.rs`, `math.rs`, `examples/esp32_live_hardware_test.rs`, `docs/adr/ADR-281-ble-cs-delay-doppler-pose-factorization.md`.
- **Riscos/limitações:** adaptadores não WiFi só com sinais ideais. Ranging por fase é vulnerável a multipercurso.
- **Relevância para a plataforma (M12, M14, M08):** média. Registro de adaptadores como porta (hexagonal) para fontes simuladas de várias modalidades. A sanitização de fase e o mapa atraso-Doppler são técnicas públicas úteis no gerador. Hardware fica PLANNED/BLOCKED.

#### WM-03 — Encoder RF "fundacional" com pré-treino por reconstrução mascarada e adaptadores de tarefa menores que 1% do backbone

- **O que faz:** tokeniza a janela RF canônica, codifica num latente modulado por idade e geometria, pré-treina por reconstrução mascarada e treina cabeças pequenas sobre o encoder congelado: presença, atividade (low-rank), localização 3D, pose fatorada conteúdo-versus-sala e anomalia por z-score do erro de reconstrução.
- **Como faz:** tokens por (enlace × grupo de subportadoras) com features e codificação posicional; rede pequena com pooling médio e porta multiplicativa pela idade; backward derivado à mão e verificado por diferenças finitas; SGD com máscara semeada; verificação de orçamento de parâmetros das cabeças.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy ou PyTorch, peft.
  - Dados: corpus do gerador e dados reais para qualquer alegação.
  - Competências: masked autoencoding, LoRA, ML reprodutível.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Testes de gradiente, queda de perda abaixo do baseline, determinismo, orçamento e resistência a vazamento por sala. A ADR-273 relata cerca de 40 mil parâmetros e F1 = 1,0 em presença, **só em mundos sintéticos separáveis por construção**. Caminhos: `v2/crates/ruview-unified/src/tokenizer.rs`, `encoder.rs`, `pretrain.rs`, `heads.rs`, `docs/adr/ADR-150-rf-foundation-encoder.md`.
- **Riscos/limitações:** "fundacional/universal" é exagerado para um MLP desse tamanho. Sem dados medidos.
- **Relevância para a plataforma (M01, M06, M11, M12):** média, restrita ao Model Lab. O padrão backbone congelado + adaptadores com orçamento + gate de vazamento é bom, mas inferência de IA exige autorização: fica PLANNED com resultados L0.

#### WM-04 — Protocolo de avaliação anti-vazamento (strict split, ECE, abstenção, degradação) e teste de aceitação ponta a ponta

- **O que faz:** garante que métricas reflitam generalização, não reconhecimento de sala, sessão, pessoa ou chipset. Faz holdout por valores inteiros de uma dimensão e prova a disjunção. Mede ECE, risco seletivo com abstenção e degradação entre condições conhecidas e desconhecidas.
- **Como faz:** chave de proveniência multidimensional (sala, dia, pessoa, chipset, firmware, layout), manifesto de disjunção e métricas F1, MPJPE, ECE e seletivas. O teste ponta a ponta encadeia CSI simulado → pré-treino sem rótulos → adaptador → avaliação em salas e chipsets novos → latência p95 → exportação pelo trust boundary.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: scikit-learn (GroupKFold, LeaveOneGroupOut), numpy, pytest.
  - Dados: metadados de partição.
  - Competências: desenho experimental, calibração.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 7 testes mais 3 de aceitação. A ADR admite que F1 = 1,0 só valida a maquinaria. Caminhos: `v2/crates/ruview-unified/src/eval.rs`, `tests/e2e_acceptance.rs`, `docs/adr/ADR-273-unified-rf-spatial-world-model.md`.
- **Riscos/limitações:** em mundos simples todos os gates passam trivialmente.
- **Relevância para a plataforma (M12, M15, M16):** muito alta e barata: splits por grupo, ECE e abstenção, e a regra "acurácia agregada nunca basta" como governança. Ver também ML-04.

#### WM-05 — Memória espacial de Gaussianas RF-aware com consultas de ganho de canal e atualização inversa

- **O que faz:** representa a cena como Gaussianas 3D anisotrópicas que carregam estado geométrico e semântico, estado RF (refletividade por banda e ângulo, extinção, Doppler), confiança, proveniência, decaimento e vínculos. Prevê o ganho complexo entre dois pontos e aprende obstáculos pelos resíduos de enlaces.
- **Como faz:** fusão por gate de Mahalanobis com média ponderada e confiança noisy-OR; decaimento exponencial idempotente com persistência estática; poda e merge com compatibilidade semântica; hash espacial com consultas por raio, corredor, kNN e semântica. O ganho é Friis × transmitância de Beer-Lambert, com profundidade óptica como integral de linha em forma fechada (erf) de cada Gaussiana no segmento TX→RX. **Mapa vazio equivale exatamente a Friis.** A atualização inversa dá um passo de gradiente projetado e cria uma Gaussiana se nada intersecta.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy/scipy (erf), `scipy.spatial.cKDTree`, three.js.
  - Dados: enlaces TX/RX com amplitude.
  - Competências: geometria 3D, propagação (Friis, extinção), estruturas espaciais.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Testes de Friis exato, monotonicidade, integral contra quadratura, aprendizado de parede, fusão, decaimento e hash contra varredura linear, mais benches. A ligação ao servidor (P3) está pendente. Caminhos: `v2/crates/ruview-unified/src/gaussian/primitive.rs`, `map.rs`, `gain.rs`, `docs/adr/ADR-275-rf-aware-gaussian-spatial-memory.md`.
- **Riscos/limitações:** propagação só na linha de visada (sem multipercurso nem difração). Inversão mal-posta. Noisy-OR assume independência.
- **Relevância para a plataforma (M14, M08):** alta no modo sintético: "blobs" gaussianos com decaimento e proveniência consultáveis por zona, persistidos em SQLite, sempre como modelo L0.

#### WM-06 — Grafo de cena com ativação limitada por tarefa

- **O que faz:** relações simbólicas esparsas (contém, adjacente, observa) entre objetos, salas, classes de pessoa (nunca identidade), dispositivos e eventos. O raciocínio só acessa um subgrafo ativado e limitado.
- **Como faz:** a única leitura sancionada é uma BFS a partir de sementes, filtrada por tipos relevantes à tarefa e parada por orçamento. Não há varredura completa.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: networkx ou CTEs recursivas em SQLite.
  - Dados: planta e dispositivos.
  - Competências: grafos, minimização de dados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 3 testes, sem consumidores. Caminhos: `v2/crates/ruview-unified/src/gaussian/graph.rs`.
- **Riscos/limitações:** estrutura simples. Duplica parcialmente a ontologia.
- **Relevância para a plataforma (M14, M15):** média. "Acesso por subgrafo limitado" é um bom princípio de minimização de dados para M15 e para agentes.

#### WM-07 — Gerador de mundos RF sintéticos guiado por física

- **O que faz:** gera janelas CSI rotuladas a partir de multipercurso: salas paralelepipédicas, paredes com permitividade complexa e pessoas como espalhadores móveis (o Doppler **emerge** da variação de caminho, não é injetado). Aplica randomização de domínio sobre parâmetros físicos (materiais, geometria, ganho, fase, ruído, CFO, perda de pacotes, interferência) e gera chaves de partição.
- **Como faz:** método das imagens (Allen–Berkley) até reflexão de 2ª ordem, coeficiente de Fresnel em incidência normal a partir da permitividade e soma coerente por subportadora. ChaCha20 semeado: corpus idêntico byte a byte por semente, e todo tensor é carimbado como sintético.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy; pyroomacoustics (MIT, adaptável); Sionna RT (Apache-2.0, pesado).
  - Dados: parâmetros de materiais (ITU-R P.2040, público).
  - Competências: propagação eletromagnética, OFDM, randomização de domínio.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Âncoras físicas testadas: caminho direto igual a Friis, reciprocidade, atraso de 1ª ordem pela geometria espelhada, taxa Doppler analítica e sanidade de Fresnel para concreto; determinismo e completude de rótulos. Caminhos: `v2/crates/ruview-unified/src/synth/room.rs`, `raytrace.rs`, `generator.rs`, `docs/adr/ADR-276-physics-guided-synthetic-rf-worlds.md`.
- **Riscos/limitações:** só salas paralelepipédicas, um material por parede, 2ª ordem e pessoas pontuais. O gap sim-to-real não foi medido.
- **Relevância para a plataforma (M01, M02, M03, M12, M14):** **muito alta**. É exatamente o que um produto `synthetic-native` precisa para ir além de dados aleatórios: um gerador CSI fisicamente plausível e determinístico alimentando presença, ocupação e entradas/saídas com L0. Deve ser reimplementado de forma independente a partir da literatura pública.

#### WM-08 — Plano de controle de privacidade de borda e trust boundary de exportação

- **O que faz:** autoriza o sensoriamento por propósito (presença, atividade, vitais, localização, pose, reconhecimento de identidade, diagnóstico de canal) e por zona, e impõe retenção máxima no egresso. **RF bruto nunca sai**: o único tipo exportável é um evento limitado que exige incerteza, proveniência, versão de modelo e propósito.
- **Como faz:** motor de políticas com zonas, propósitos concedidos, idade máxima e **segundo fator explícito para identidade**. É fail-closed (zona desconhecida, propósito não concedido ou identidade sem habilitação dupla resultam em negação). O tipo de evento não comporta tensores. Vocabulário alinhado a IEEE 802.11bf e ETSI ISAC.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: pydantic (tipos discriminados), dependências FastAPI, SQLite; OPA opcional.
  - Dados: zonas, propósitos e consentimentos.
  - Competências: privacy by design, LGPD/GDPR.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 5 testes e proptests (fail-closed sob concessões arbitrárias; exportação bruta inalcançável). Caminhos: `v2/crates/ruview-unified/src/policy.rs`, `tests/security_boundaries.rs`, `docs/adr/ADR-277-edge-sensing-control-plane.md`.
- **Riscos/limitações:** políticas em memória, sem persistência nem auditoria.
- **Relevância para a plataforma (M15, M13):** muito alta. "Propósito × zona × retenção" como entidades de domínio e um único DTO exportável com incerteza, proveniência, versão de modelo e propósito. Identidade BLOCKED por padrão.

#### WM-09 — Percepção programável: contrato de tarefa, planejador por idade-da-informação, fusão coerente fail-closed, atuadores governados e representação suficiente por tarefa

- **O que faz:** define o contrato de tarefa (propósito, área, resolução, latência, confiança, retenção, consumidores, consentimento) e ações ativas com teto de privacidade. Agenda o refresh das regiões mais desatualizadas e críticas, só permite fusão coerente com sincronia comprovada, exige recibo para atuadores de rádio e valida que representações compactas não vazem campos proibidos.
- **Como faz:** a admissão passa pela política. A prioridade por região é incerteza × taxa de mudança × criticidade ÷ custo. O grupo coerente verifica sincronia e rejeita valores não finitos. Cada propósito tem campos proibidos (por exemplo, identidade em ocupação).
- **Requisitos para implementar:**
  - Hardware: nenhum (atuadores RIS são pesquisa).
  - Software: Python e heapq.
  - Dados: metadados de regiões.
  - Competências: Age of Information, escalonamento.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 7 suítes. A "redução de tráfego ≥ 70%" vem de uma simulação favorável por construção. Caminhos: `v2/crates/ruview-unified/src/control.rs`, `docs/adr/ADR-280-active-sensing-programmable-perception.md`.
- **Riscos/limitações:** economia sintética. Sem drivers.
- **Relevância para a plataforma (M14, M15, M13):** média. O contrato de tarefa com consentimento e a "representação mínima por propósito" cabem no M15, e o AoI pode guiar a cadência do simulador. Atuadores ficam BLOCKED.

#### WM-10 — Ontologia espacial canônica (Site▸Building▸Floor▸Space▸Zone + entidades folha)

- **O que faz:** modelo único de contenção espacial e de entidades (Sensor, Pessoa pseudônima, Objeto, Observação, Trilha, Evento), lido e escrito por todas as superfícies. Cada fato tem exatamente um nível de evidência e um registro de proveniência semântica.
- **Como faz:** registro de grafo com pai único na espinha. Rejeita filhos sem pai. As folhas resolvem zona, espaço e andar para cima. IDs validados e nunca aleatórios. A proveniência inclui versão de modelo, de calibração e decisão de privacidade. Há uma tabela de mapeamento das formas legadas por superfície.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: SQLAlchemy/Alembic + SQLite, pydantic.
  - Dados: plantas e cadastro.
  - Competências: DDD; ontologias abertas de referência (Brick Schema, RealEstateCore).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 8 testes mais doctest. É a dependência mais usada da área. As superfícies ainda não foram migradas. Caminhos: `v2/crates/ruview-ontology/src/lib.rs`, `entity.rs`, `graph.rs`, `id.rs`, `provenance.rs`, `docs/adr/ADR-306-canonical-spatial-ontology.md`.
- **Riscos/limitações:** sem geometria nem versionamento temporal. A escada de evidência está duplicada em vários crates.
- **Relevância para a plataforma (M14, M15, M16, M02, M03):** muito alta. Tabelas site/building/floor/space/zone com FK de pai único e folhas com `evidence_level` e proveniência obrigatórios, numa migração aditiva.

#### WM-11 — Fusão de presença multimodal sensível à incerteza com UNKNOWN de primeira classe

- **O que faz:** reduz várias observações de presença (possivelmente conflitantes e de modalidades diferentes) a um estado por contêiner: probabilidade, variância fundida, observações contribuintes e nível de evidência agregado. Quando não dá para responder, devolve **UNKNOWN com motivo**.
- **Como faz:** ponderação pela variância inversa (concordância "afia" a estimativa e fontes incertas pesam pouco). O conflito é medido por qui-quadrado reduzido: acima do limiar dá UNKNOWN, em vez de uma média enganosa. Cobertura insuficiente também dá UNKNOWN. **A evidência fundida é o mínimo das entradas.** É determinística e independente da ordem.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, scipy.stats.chi2.
  - Dados: observações com variância calibrada.
  - Competências: fusão bayesiana, calibração.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 12 testes. Não há consumidor em runtime. Caminhos: `v2/crates/ruview-fusion/src/lib.rs`, `engine.rs`, `estimate.rs`, `observation.rs`, `world.rs`, `docs/adr/ADR-311-real-sensor-fusion.md`.
- **Riscos/limitações:** só presença escalar. Assume independência entre fontes. Sem dinâmica temporal.
- **Relevância para a plataforma (M01, M02, M14):** muito alta e imediata. Várias fontes simuladas por zona fundidas por variância inversa num caso de uso, com UNKNOWN em conflito ou falta de cobertura e evidência mínima. Cerca de 100 linhas de Python testáveis com Hypothesis.

#### WM-12 — Rastreamento persistente pseudônimo e privacy-preserving

- **O que faz:** mantém continuidade de trilhas sem identidade civil, associando detecções (contêiner, posição 2D, feature grosseira não reversível, timestamp) a pseudônimos rotacionáveis. Responde a trajetórias do tipo "pessoa_7: cozinha → corredor → quarto".
- **Como faz:** expira trilhas antigas. Considera só trilhas no mesmo contêiner ou em adjacentes pela topologia (portas), com gates de posição e de feature quantizada. **Se as duas melhores candidatas estão próximas demais, recusa atribuir** e cria uma trilha tentativa (sub-associar é a falha segura). Atribuição gulosa 1:1, ciclo de vida, UNKNOWN com motivos tipados, features sem de-quantizador e rotação de pseudônimo.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: `scipy.optimize.linear_sum_assignment`, filterpy, numpy.
  - Dados: detecções simuladas e grafo de adjacência.
  - Competências: MOT, privacy engineering.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 17 testes (continuidade, bloqueio não adjacente, não-troca, ambiguidade, pseudônimos opacos, determinismo). Nenhuma métrica MOTA alegada. Caminhos: `v2/crates/ruview-track/src/manager.rs`, `feature.rs`, `topology.rs`, `config.rs`, `tests/tracking.rs`, `docs/adr/ADR-307-persistent-identity-tracking.md`.
- **Riscos/limitações:** sem modelo de movimento. Atribuição gulosa. Pseudônimos persistentes continuam sendo dado pessoal.
- **Relevância para a plataforma (M02, M03, M15):** alta para M03 (entradas/saídas por transição entre zonas adjacentes) e M02, com rotação de pseudônimo para M15, tudo L0.

#### WM-13 — Gêmeo digital RF por implantação (twin) com delta observado-vs-previsto

- **O que faz:** mantém um modelo versionado do ambiente RF de uma instalação (nós, paredes, parâmetros, multipercurso, calibração). Prevê média e variância por enlace e compara com observações, destacando quais enlaces desviam e quanto.
- **Como faz:** modelo log-distance mais atenuação por paredes atravessadas e variância extra por enlace. A previsão é UNKNOWN quando faltam dados. O delta dá desvio assinado e significância em desvios-padrão, enlace a enlace. O versionamento avança por eventos (calibração, edição de geometria, mudança aceita). Cenas sintéticas semeadas.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, shapely.
  - Dados: planta com paredes e nós.
  - Competências: modelos empíricos de propagação (log-distance, multi-wall/COST-231, públicos).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 8 testes (delta zero quando observado é igual a previsto, delta localizado em nó movido e em refletor novo). Consumido por posicionamento, memória e contrafactual. Rotulado SYNTHETIC/L0. Caminhos: `v2/crates/ruview-twin/src/twin.rs`, `predict.rs`, `delta.rs`, `docs/adr/ADR-315-digital-rf-twin.md`.
- **Riscos/limitações:** propagação grosseira e variâncias assumidas.
- **Relevância para a plataforma (M08, M14, M16):** muito alta. Transforma o simulador num gêmeo por instalação, com previsão e delta por enlace (alertas de mudança de ambiente, M08), versionado por calibração (M16), em Python e SQLite.

#### WM-14 — Otimizador de posicionamento de sensores com laço pós-instalação

- **O que faz:** recomenda posições de nós para uma planta e um inventário, pontua a observabilidade das zonas-alvo pelo gêmeo, reporta pontos cegos e incerteza e compara o previsto com o medido para sugerir ajustes.
- **Como faz:** pontos em grade nas regiões-alvo. Um ponto é "observável" se está no primeiro elipsoide de Fresnel de um enlace bem previsto. Busca gulosa progressiva com traço monotônico, ranking de placements, comparador pós-instalação com veredito por alvo (UNKNOWN sem medida) e resíduo de atenuação para o gêmeo. Entradas limitadas.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, shapely; OR-Tools opcional.
  - Dados: planta, zonas e inventário.
  - Competências: Fresnel, cobertura submodular.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 14 testes. Sem métrica real. Caminhos: `v2/crates/ruview-placement/src/lib.rs`, `coverage.rs`, `fresnel.rs`, `plan.rs`, `compare.rs`, `docs/adr/ADR-308-sensor-placement-optimizer.md`.
- **Riscos/limitações:** proxy grosseira. Busca sub-ótima.
- **Relevância para a plataforma (M16, M08, M14):** alta para M16: assistente de posicionamento sintético que sugere onde colocar nós e explica pontos cegos, rotulado L0, exibido em SVG/canvas.

#### WM-15 — Auto-levantamento de nós em modo verificação (FTM/UWB), para detectar erros de configuração

- **O que faz:** compara distâncias medidas entre pares de nós (Wi-Fi FTM; UWB no futuro) com as posições digitadas pelo operador. Detecta unidade errada (pés, polegadas, centímetros), IDs trocados, nó movido e outliers, **sem nunca escrever posições**.
- **Como faz:** resíduo por enlace com tolerância. Ajusta uma escala global por mínimos quadrados e acusa unidade quando a escala fica perto de fatores de conversão conhecidos. Busca permutações (algoritmo de Heap, poucos nós) que expliquem melhor as distâncias, ou declara ambiguidade quando o layout é simétrico (distâncias não distinguem rotação nem reflexão). Detecta nó cujos enlaces discordam em grupo e usa calibração por boot. **Um gate bloqueia escrita de posições até a fonte ter erro p90 medido abaixo de um limite.**
- **Requisitos para implementar:**
  - Hardware: ESP32 com FTM ou UWB (real); simulável.
  - Software: numpy/scipy (lstsq), `itertools.permutations`.
  - Dados: pares de distâncias com sigma.
  - Competências: geometria de distâncias, metrologia de ranging.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 29 testes com cenários sintéticos. As tolerâncias padrão vêm de uma bancada MEASURED com duas placas ESP32-S3 descrita na ADR-381 (dados brutos não verificados). A ADR está "Proposed". Caminhos: `v2/crates/ruview-survey/src/lib.rs`, `check.rs`, `report.rs`, `calibration.rs`, `fill.rs`, `tests/check_synthetic.rs`, `docs/adr/ADR-381-node-self-survey.md`.
- **Riscos/limitações:** o FTM tem viés de metros entre reinícios e só pega erros grosseiros. Busca exponencial. Simetrias escondem erros.
- **Relevância para a plataforma (M16):** alta. Um checador "warn-only" que valida a configuração de nós contra distâncias simuladas e acusa unidades erradas ou IDs trocados é um diferencial de UX barato.

#### WM-16 — Memória espacial de longo prazo e anomalia como desvio da normalidade aprendida

- **O que faz:** aprende o "normal" por zona: ocupação por hora (UTC), assinatura de propagação por enlace (semeada pelo gêmeo) e assinaturas por canal de modalidade. Sinaliza anomalias sem treinar um detector por classe e as grava num ledger append-only.
- **Como faz:** média e variância com fator de esquecimento (absorve deriva lenta; mudanças abruptas desviam), desvio padronizado com piso e **UNKNOWN abaixo do histórico mínimo** (sem falso positivo antes de haver baseline). A baseline herda o piso de evidência e nunca o eleva. Os registros de anomalia são sintéticos, com L0 forçado.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, SQLite; river (BSD).
  - Dados: séries por zona com timestamps.
  - Competências: estatística online (EWMA/Welford), sazonalidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 11 testes. Não alega taxas de detecção. Caminhos: `v2/crates/ruview-memory/src/baseline.rs`, `stat.rs`, `anomaly.rs`, `v2/crates/ruview-evidence/src/lib.rs`, `docs/adr/ADR-312-long-term-spatial-memory.md`.
- **Riscos/limitações:** só hora do dia (sem dia da semana). Assume distribuição gaussiana.
- **Relevância para a plataforma (M08, M02, M09, M14, M15):** muito alta. Baselines EWMA por zona, canal e hora no SQLite já existente, com UNKNOWN antes do histórico mínimo e eventos de anomalia L0 rastreáveis.

#### WM-17 — Memória espacial vetorial criptografada e particionada por tenant (ADR-326)

- **O que faz:** guarda histórico espacial semântico (só registros agregados; **o tipo não tem campo** para CSI, tensores, gravações, biometria ou identidade) em índices vetoriais fisicamente separados por tenant e workspace. Responde buscas com explicações limitadas ("similaridade não é causalidade") e persiste em snapshot criptografado com rotação de chave.
- **Como faz:** a partição seleciona o índice HNSW **antes** da busca (sem filtragem pós-busca). Deduplicação por (fonte, id), rejeição de reuso conflitante e sequência monotônica por fonte (anti-replay). Grafo de derivação acíclico com poda em cascata e apagamento exato. Snapshot AEAD XChaCha20-Poly1305 com key id, sem sobrescrever destino e rejeitando adulteração. Chaves zeradas da memória.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: hnswlib, sqlite-vec, FAISS; PyNaCl/cryptography.
  - Dados: embeddings agregados.
  - Competências: AEAD, multitenancy, LGPD (retenção e apagamento).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 7 testes. Gates de implantação pendentes e sem consumidores. Caminhos: `v2/crates/ruview-spatial-memory/src/lib.rs`, `v2/crates/wifi-densepose-ruvector/src/hnsw.rs`, `docs/adr/ADR-326-tenant-scoped-ruvector-spatial-memory.md`.
- **Riscos/limitações:** tudo em memória. Gestão de chaves fica com o chamador.
- **Relevância para a plataforma (M15, M14):** alta como padrão: exclusão estrutural de dados brutos no tipo, anti-replay, apagamento em cascata, retenção obrigatória e backup criptografado com rotação, alinhados ao backup/retention existente.

#### WM-18 — Inferência contrafactual de cena (hipóteses incluindo a nula)

- **O que faz:** pontua hipóteses de cena (ninguém, um ocupante em tal posição, dois ocupantes) usando o gêmeo como modelo gerador. Devolve a explicação de máxima verossimilhança com margem, ou UNKNOWN.
- **Como faz:** distribuição base por enlace mais modelo sintético de atenuação por ocupante e log-verossimilhança gaussiana somada. UNKNOWN quando a margem é baixa, a verossimilhança média fica abaixo de um piso (fora do modelo), não há hipóteses ou não há enlaces. Limites de ocupantes e hipóteses.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy/scipy.stats.
  - Dados: gêmeo e medições.
  - Competências: teste de hipóteses, modelos generativos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 9 testes, **com validação circular** (observações geradas pelo mesmo modelo). As hipóteses "vindas da fusão" não estão implementadas. Caminhos: `v2/crates/ruview-counterfactual/src/infer.rs`, `hypothesis.rs`, `docs/adr/ADR-313-counterfactual-inference.md`.
- **Riscos/limitações:** modelo de corpo grosseiro e hipóteses enumeradas manualmente.
- **Relevância para a plataforma (M01, M02, M14):** média-alta como explicabilidade: "a observação é melhor explicada por 1 pessoa do que por 0 ou 2, com margem X", sobre o gêmeo e L0.

#### WM-19 — Sensoriamento ativo: agendador por ganho de informação e controlador em malha fechada

- **O que faz:** decide onde gastar o próximo orçamento de amostragem (compute, energia, banda) e qual configuração propor (canal, largura, cadência, antenas) para reduzir mais a incerteza por zona. **Só emite planos**, nunca RF.
- **Como faz:** valor = redução esperada ÷ custo ponderado, com seleção gulosa respeitando orçamento multidimensional. Redução desconhecida segue política explícita (sondar ou adiar), **nunca zero**. Piso de amostragem e registro dos pulados. O controle é explore/exploit, e UNKNOWN alarga a exploração.
- **Requisitos para implementar:**
  - Hardware: nenhum (rádios controláveis são pesquisa).
  - Software: Python; OR-Tools opcional.
  - Dados: incerteza e custos por sensor.
  - Competências: design experimental, bandits.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 15 mais 13 testes. Scaffolds de pesquisa L0/L1 sem consumidores. Caminhos: `v2/crates/ruview-infogain/src/scheduler.rs`, `cost.rs`, `v2/crates/ruview-active/src/policy.rs`, `control.rs`, `docs/adr/ADR-314-information-gain-scheduler.md`, `docs/adr/ADR-309-active-sensing.md`.
- **Riscos/limitações:** ganhos e custos vêm do chamador. Guloso não ótimo.
- **Relevância para a plataforma (M14, M16):** média-baixa. Pode orientar a cadência do simulador. Controle de rádio fica BLOCKED.

#### WM-20 — Detecção de fora-de-distribuição e gating de domínio (KNOWN/DEGRADED/UNKNOWN)

- **O que faz:** anexa um estado de domínio a toda inferência, para que o sistema diga "não reconheço esta situação" em vez de dar um rótulo confiante e errado. Suprime a classe em UNKNOWN e emite um pedido de recalibração (sinal, não ação).
- **Como faz:** distância entre a impressão ao vivo e a certificada, com envelope interno (DEGRADED) e externo (UNKNOWN) e histerese. Certificado ausente, vencido ou divergente dá UNKNOWN, com precedência sobre a deriva. Contradição ou qualidade baixa dá DEGRADED, e sinal inutilizável dá UNKNOWN. **A incerteza do modelo só pode piorar o estado.** O assinador de referência é um MAC rotulado como placeholder.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: hmac ou PyNaCl.
  - Dados: impressões por calibração.
  - Competências: OOD, máquinas de estado de confiança.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 25 testes, incluindo entrada hostil virando UNKNOWN. Consumido por certificação e política. Caminhos: `v2/crates/ruview-ood/src/domain.rs`, `gate.rs`, `certificate.rs`, `v2/crates/wifi-densepose-calibration/src/certificate.rs`, `docs/adr/ADR-302-out-of-distribution-detection.md`.
- **Riscos/limitações:** impressão escalar simples. MAC simétrico. Envelope não validado.
- **Relevância para a plataforma (M15, M16, M08):** muito alta. A máquina VALID→DEGRADED→UNKNOWN ligada a um certificado de calibração com validade casa com M16 e M15, e o modo sintético pode simular deriva para demonstrar a degradação.

#### WM-21 — Exportação de evidência espacial em JSONL versionado (spatial.evidence.v1)

- **O que faz:** serializa Gaussianas RF e observações de enlace (com perda excedente sobre o espaço livre) como registros JSONL versionados, cada um com proof tag MEASURED, CODE ou SYNTHETIC.
- **Como faz:** structs locais espelhando o contrato. Cada registro é validado antes de serializar (schema exato, finitude, faixas, IDs, tamanho de linha). **Proveniência sintética sai sempre como SYNTHETIC** (o tag só pode baixar). MEASURED exige ID de reprodutor. O parser rejeita tipos desconhecidos. Golden fixtures de contrato externo.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: pydantic, jsonschema (MIT).
  - Dados: registros do world model.
  - Competências: contratos versionados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 15 testes. A ADR está "proposed". O caminho de enlace aceita o tag do chamador sem checagem (lacuna documentada). Caminhos: `v2/crates/ruview-spatial-evidence/src/wire.rs`, `gaussian.rs`, `link.rs`, `tests/evidence.rs`, `docs/adr/ADR-382-spatial-evidence-rf-export.md`.
- **Riscos/limitações:** depende de contrato externo sem especificação no repositório.
- **Relevância para a plataforma (M15, M14):** alta. Exportação JSONL versionada com proof tag que só pode baixar e reprodutor obrigatório para MEASURED, compatível com o contrato aditivo.

#### WM-22 — Cliente de leitura Cognitum Spaces com fronteira de dados limitada

- **O que faz:** lê estado espacial semântico agregado de um serviço de nuvem externo multi-tenant, via OAuth ou API key, sem enviar dados brutos e sem nenhum método de ação.
- **Como faz:** HTTPS obrigatório (HTTP só em loopback), sem redirecionamentos, credenciais redigidas, resposta limitada em bytes, profundidade e nós, e **rejeição de qualquer campo proibido em qualquer nível** (CSI, CIR, tensores, gravações, pose, ondas vitais, identidade) ou de declaração de privacidade incompleta.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: httpx, pydantic.
  - Dados: conta no serviço externo.
  - Competências: OAuth, validação defensiva.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 10 testes. A ADR alega evidência de produção não verificável. Consumido pela CLI. Caminhos: `v2/crates/ruview-cognitum-spaces/src/lib.rs`, `v2/crates/wifi-densepose-cli/src/spaces.rs`, `docs/adr/ADR-325-cognitum-spaces-activation-and-governed-spatial-exchange.md`.
- **Riscos/limitações:** SaaS externo com termos e custo desconhecidos, incompatível com custo zero.
- **Relevância para a plataforma (M15, M13):** baixa como integração e alta como padrão de validação defensiva de payloads externos para conectores e webhooks do M13. Ver também OP-21.

#### WM-23 — Projeção de perspectiva off-axis (head-coupled) com filtro One Euro e paralaxe RF grosseira

- **O que faz:** transforma a tela numa "janela" (frustum assimétrico) para demos three.js, com suavização de rastreamento e um estágio que converte o pico do campo RF numa paralaxe grosseira e deliberadamente limitada.
- **Como faz:** formulação de perspectiva generalizada de Kooima (2008), filtro One Euro de Casiez et al. (CHI 2012) e deadband, ganho e clamp. Rotulado como paralaxe grosseira, nunca como rastreamento de cabeça.
- **Requisitos para implementar:**
  - Hardware: webcam opcional.
  - Software: three.js, TypeScript.
  - Dados: dimensões da tela.
  - Competências: computação gráfica.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 23 testes. Declara-se clean-room a partir de artigos. Caminhos: `v2/crates/ruview-offaxis/src/projection.rs`, `filter.rs`, `rf.rs`, `examples/three.js/demos/07-off-axis-window.html`, `docs/adr/ADR-324-off-axis-head-coupled-perspective-demo.md`.
- **Riscos/limitações:** é demo de UX; o caminho RF não é localização.
- **Relevância para a plataforma (NONE):** baixa. Só o filtro One Euro para suavizar séries no front-end.

#### WM-24 — AetherArena: benchmark público com ledger encadeado por hash e Space de leaderboard

- **O que faz:** benchmark para inteligência espacial sem câmera (pose, presença, latência de borda, determinismo), com scorer aberto e versionado, split privado, ledger append-only com hash de prova e leaderboard num Space Gradio.
- **Como faz:** manifesto TOML da submissão e ciclo de vida planejado com sandbox sem rede. O scorer determinístico vive em outro crate (ML-07). Ledger JSONL encadeado pelo SHA-256 canônico da linha anterior. O app Gradio verifica a cadeia; as abas de submissão e verificação são só texto.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: Python, Gradio (Apache-2.0), hashlib, PyNaCl.
  - Dados: dataset com licença compatível.
  - Competências: benchmarks, reprodutibilidade.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. A cadeia é verificável. O ledger tem 1 linha gênese e 4 resultados MM-Fi sem hash de prova por linha. **O STATUS diz "board vazio", em contradição com o ledger.** Não há fluxo de submissão nem sandbox. Caminhos: `aether-arena/README.md`, `STATUS.md`, `VERIFY.md`, `schema/aa-submission.toml`, `ledger/ledger_tools.py`, `ledger/ledger.jsonl`, `space/app.py`, `docs/adr/ADR-149-public-community-leaderboard-huggingface.md`.
- **Riscos/limitações:** "resultados assinados" é só cadeia de hash. MM-Fi é não comercial.
- **Relevância para a plataforma (M12, M15, M11):** média-alta como padrão: ledger JSONL encadeado com Ed25519 para resultados de verificação e calibração.

#### WM-25 — Calibração por sala via adaptador LoRA (serviço de referência AetherArena)

- **O que faz:** ajusta um adaptador LoRA minúsculo por sala, a partir de captura rotulada curta (CSI + keypoints COCO-17), sobre uma base de pose congelada. Há dois produtores de formato não intercambiáveis.
- **Como faz:** a base fica congelada e o adaptador de baixo posto é treinado com poucas centenas de amostras da sala. Os testes rodam a CLI ponta a ponta com dados aleatórios em CPU.
- **Requisitos para implementar:**
  - Hardware: CPU; câmera de referência e nós CSI para captura.
  - Software: PyTorch, peft, safetensors.
  - Dados: pares por sala (exigem câmera); checkpoint base com licença a verificar.
  - Competências: fine-tuning eficiente, pose.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNCLEAR`. Os testes validam só o encanamento. O README relata ganho numa sala MM-Fi não vista e diz que não é prova de adaptação plug-and-play a partir de ESP32. Caminhos: `aether-arena/calibration/README.md`, `model.py`, `calibrate.py`, `cog_calibrate.py`, `infer.py`, `test_calibration.py`.
- **Riscos/limitações:** exige verdade por câmera. Com poucas amostras pode piorar. Dados CC BY-NC.
- **Relevância para a plataforma (M12, M11, M16):** baixa no produto atual (M11 BLOCKED). Referência conceitual de "base congelada + adaptador por ambiente com versionamento e certificado".

### 4.8 Governança: evidência, atestação, autenticação, políticas, privacidade e ground truth

**Escopo.** A área reúne quatro blocos:

1. **"Perception certificate spine" (ADR-300).** Atestação de sensor → cadeia de testemunho → ledger de evidências → scorecard → certificado de capacidade → gate de autorização → intents governadas.
2. **Plano de ground truth.**
3. **Autenticação OAuth/JWT e camadas web** integradas ao servidor.
4. **Pesquisa de contramedida RF (WiFi Veil) e governança documental de claims.**

As bibliotecas de governança estão implementadas e têm testes unitários, mas a validação é toda sintética/L0. Com exceção de `ruview-auth` e de um consumidor de `ruview-evidence` (`ruview-memory`), **nada desta espinha está ligado ao caminho de requisição do servidor ao vivo**, como o próprio user-guide admite.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| GV-01 | Identidade autenticada de sensor e cadeia de custódia | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16, M12 |
| GV-02 | Cadeia de testemunho em estágios com hashes encadeados | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M14, M13 |
| GV-03 | Ledger append-only de evidências de acurácia por contexto | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16, M12 |
| GV-04 | Escada de evidência L0–L5, piso mínimo e UNKNOWN como valor | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16 |
| GV-05 | Certificados de capacidade assinados, expiráveis e condicionados ao domínio | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16, M01, M11 |
| GV-06 | Gate de autorização de ações por classe de risco | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15, M07 |
| GV-07 | Intents governadas, aprovações assinadas, idempotência e recibos encadeados | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15 |
| GV-08 | Scorecard multidomínio com intervalo de Wilson e gate pelo pior domínio | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M15, M16 |
| GV-09 | Plano de validação ground truth (séries, alinhamento, concordância, escopo) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M04, M05, M01, M02, M15, M16 |
| GV-10 | Rótulos de radar mmWave, autolabel, split por sessão e baseline majoritário | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M03, M12, M16 |
| GV-11 | Verificação offline de OAuth/JWT com escopos por raio de impacto | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| GV-12 | Login PKCE (CLI), armazenamento de credenciais e refresh single-flight | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16 |
| GV-13 | Autenticação web em camadas, sessão server-side e tickets de WS | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| GV-14 | Endurecimento de superfície (Host allowlist, caminhos, bind restrito) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| GV-15 | Privacidade em runtime (privacy mode, rebaixamento, proveniência) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M04, M05, M11, M09 |
| GV-16 | WiFi VEIL: modelo de referência sintético | RESEARCH | SYNTHETIC_OR_SIMULATED | M15, M08 |
| GV-17 | WiFi VEIL em firmware/hardware (núcleo C e adaptadores) | PARTIAL | UNIT_TESTS_ONLY | M15, M08 |
| GV-18 | Governança de claims (PROOF.md, prove.sh, retratações, witness bundle, redação) | IMPLEMENTED_UNTESTED | UNCLEAR | M15 |
| GV-19 | Guarda de repositório para dados pessoais de CSI | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M12 |
| GV-20 | Protocolo clean-room, classificação de dados, threat model e auditoria | DOC_ONLY | NONE | M15, M12 |

#### GV-01 — Identidade autenticada de sensor e cadeia de custódia (atestação de medições)

- **O que faz:** cada medição carrega identidade cadastrada, sequência, timestamp, hash do payload e referência de calibração. Na ingestão, são **rejeitados como erro** (nunca como aviso): dispositivo desconhecido, assinatura inválida, adulteração, replay, timestamp velho e timestamp no futuro.
- **Como faz:** envelope com conteúdo canônico (prefixo de comprimento, separação de domínio). O verificador mantém um mapa de dispositivos com seus verificadores e a última sequência aceita. A ordem de verificação é: cadastro → tag → hash → sequência estritamente crescente → frescor com orçamento de desvio de relógio. O estado só avança se tudo passar. A assinatura de referência é um MAC simétrico (BLAKE3 keyed, comparação em tempo constante); Ed25519 é apenas citado como substituto futuro. Tempo injetado.
- **Requisitos para implementar:**
  - Hardware: nenhum; em produção, armazenamento seguro de chave nos nós.
  - Software: hmac/hashlib ou blake3; PyNaCl/cryptography para Ed25519.
  - Dados: registro de dispositivos e chaves.
  - Competências: MAC versus assinatura, canonicalização, replay e frescor.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 15 testes (replay, timestamps, adulteração de payload e de campo, chave errada, determinismo, canonicalização não ambígua). Declara-se SYNTHETIC-grade. A ADR ainda diz "planned". **Não está integrado ao receptor UDP**, que só tem allowlist de IP. Caminhos: `v2/crates/ruview-attest/src/lib.rs`, `docs/adr/ADR-305-authenticated-sensor-identity.md`, `v2/crates/wifi-densepose-sensing-server/src/udp_bind.rs`.
- **Riscos/limitações:** MAC não dá não-repúdio. A sequência fica em memória (janela de replay após reinício). Sem rotação nem revogação.
- **Relevância para a plataforma (M15, M16, M12):** alta. Assinar o pacote de aquisição sintético (HMAC-SHA256 ou Ed25519), com sequência e frescor persistidos no SQLite, como campo aditivo no 2.0.0.

#### GV-02 — Cadeia de testemunho em estágios com hashes encadeados (witness chain)

- **O que faz:** em vez de um booleano solto, registra o raciocínio em estágios ordenados: observação RF → evidência DSP → inferência → corroboração independente → estado espacial → decisão de política. Cada estágio tem confiança e nível de evidência.
- **Como faz:** o hash de cada estágio (BLAKE3 canônico com separação de domínio) inclui o do anterior. A verificação recomputa tudo e confere a raiz (observação RF), os elos, a ordem estritamente crescente de tipos e o head. O nível efetivo é o mínimo dos estágios. **Uma correção gera uma nova cadeia que referencia a anterior** (append-only). "Confiança desconhecida" e "corroboração ausente" são valores de primeira classe.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: hashlib/blake3, SQLite.
  - Dados: saídas intermediárias.
  - Competências: estruturas hash-linked, proveniência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 17 testes (adulteração no meio e no fim, reordenação, elo ausente). Os hashes **não são chaveados nem assinados**, então quem reescreve a cadeia recomputa tudo. **A regra "raiz sintética limita a L0" não é imposta estruturalmente** (o nível vem do chamador). Não está ligado ao servidor. Caminhos: `v2/crates/ruview-witness/src/lib.rs`, `docs/adr/ADR-319-witness-chain.md`, `docs/adr/ADR-010-witness-chains-audit-trail-integrity.md`.
- **Riscos/limitações:** tamper-evident só contra mutação ingênua.
- **Relevância para a plataforma (M15, M14, M13):** alta. Tabela SQLite de estágios encadeados, endpoint de verificação e visualização no dashboard. Recomendado assinar o head com Ed25519 e impor no domínio que SIMULATED implica L0. Ver também HC-17.

#### GV-03 — Ledger append-only de evidências de acurácia por contexto

- **O que faz:** histórico imutável de desempenho indexado por contexto (sala, dispositivo, classe de sujeito, versão de modelo), com recall em movimento e parado, FPR, drift, incerteza, idade de calibração e amostras.
- **Como faz:** registros só por três construtores que fixam a proveniência: sintético (sempre L0), alegado (sem referência, nunca L0) e medido (exige reprodutor). Não há setter. O append consome o registro e atribui sequência. Consultas devolvem um slice de **um único contexto**, e não há API que combine contextos. O resumo usa média ponderada, piso de evidência e classe rebaixada pelo mais fraco. **Contexto vazio dá "sem evidência", que é diferente de acurácia zero.**
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: SQLite com triggers que bloqueiam UPDATE/DELETE, SQLAlchemy/Alembic.
  - Dados: avaliações por contexto (L0).
  - Competências: modelagem de avaliação.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 9 testes. Único consumidor externo: `ruview-memory`. **Os registros derivam desserialização com campos privados**, então um JSON forjado pode criar um "sintético" com nível alto (a invariante vale para a API, não para dados desserializados). Caminhos: `v2/crates/ruview-evidence/src/lib.rs`, `docs/adr/ADR-304-evidence-engine.md`.
- **Riscos/limitações:** só em memória, sem assinatura.
- **Relevância para a plataforma (M15, M16, M12):** alta. Tabela append-only com triggers de imutabilidade e "sem evidência" explícito, também como registro honesto de experimentos do Model Lab. Ver também ML-21.

#### GV-04 — Disciplina de honestidade: escada de evidência L0–L5, piso mínimo e UNKNOWN como valor

- **O que faz:** padroniza quatro regras:
  - a evidência é uma escada de L0 (simulação) a L5 (produção certificada);
  - agregados nunca reportam acima do elo mais fraco;
  - sintético nasce L0 e não pode ser promovido;
  - UNKNOWN, "sem evidência" e "confiança desconhecida" são valores, não erros nem zeros.
- **Como faz:** enums ordenados usados como piso, construtores restritos e tipos-soma que separam ausente de zero. A escada é **espelhada em vários crates** (ledger, witness, ontologia, frame) com adaptadores.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Enum Pydantic e Zod.
  - Dados: metadados de proveniência.
  - Competências: política de evidência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Coberta pelos testes de piso, de "sintético L0" e de "sem evidência" em vários crates. Caminhos: `v2/crates/ruview-evidence/src/lib.rs`, `v2/crates/ruview-witness/src/lib.rs`, `v2/crates/ruview-groundtruth/src/lib.rs`, `docs/adr/ADR-282-ruview-ecosystem-positioning.md`, `docs/adr/ADR-300-perception-substrate-program.md`.
- **Riscos/limitações:** várias cópias da escada geram risco de divergência. Em alguns pontos a garantia depende do chamador.
- **Relevância para a plataforma (M15, M16):** muito alta e imediata. Um enum único no contrato 2.0.0, com níveis acima de L0 marcados PLANNED/BLOCKED, regras puras (SIMULATED implica L0, agregado usa piso, contagem desconhecida é null) e **uma única definição compartilhada** entre Pydantic e Zod. Ver também PY-15.

#### GV-05 — Certificados de capacidade assinados, expiráveis e condicionados ao domínio

- **O que faz:** substitui "suporta presença" por um certificado assinado válido para uma capacidade, uma sala, um dispositivo, uma versão de modelo e uma calibração, com métricas congeladas do ledger para aquele contexto e validade limitada.
- **Como faz:** o mint é função pura sobre o slice do ledger e se recusa a emitir quando não há evidência, o contexto diverge, a calibração é de outra sala, o nível excede o piso ou a validade passa a da calibração. Conteúdo canônico assinado. O consumo exige verificação criptográfica separada mais um gate (assinado, não expirado, domínio "Known").
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: JSON canônico (RFC 8785/JCS), PyNaCl.
  - Dados: ledger, calibração e estado OOD.
  - Competências: PKI leve, claims condicionados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 13 testes com ledger sintético. **O gate "is_valid" só checa a presença da assinatura, não a validade** (risco de uso incorreto). Um campo "por 24 h" carrega a FPR do ledger (rótulo enganoso admitido). Só existem as capacidades presença e pose. Caminhos: `v2/crates/ruview-certify/src/lib.rs`, `src/tests.rs`, `docs/adr/ADR-318-capability-certificates.md`.
- **Riscos/limitações:** assinatura de referência simétrica.
- **Relevância para a plataforma (M15, M16, M01, M11):** alta. Um "certificado de capacidade" L0 por ambiente sintético torna explícito que nenhuma capacidade foi validada em RF real. Numa reimplementação, a validação sempre inclui verificar a assinatura. Ver também SV-21 e WM-20.

#### GV-06 — Gate de autorização de ações por classe de risco (fail-closed)

- **O que faz:** decide se uma ação de atuador pode ocorrer comparando a garantia exigida pela classe (conveniência, segurança, segurança crítica) com a garantia disponível. **Toda negação nomeia exatamente uma condição.**
- **Como faz:** função pura sem relógio, com ordem fixa: política presente → certificado válido → classe mínima → frescor → domínio Known → teto de incerteza (NaN nega) → piso de evidência. Sem política, nega. A conveniência pode prosseguir com domínio desconhecido, mas registra isso.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: função pura em Python.
  - Dados: certificados e estado OOD.
  - Competências: segurança funcional.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 17 testes unitários e 3 de integração. Limiares ilustrativos. A documentação do crate está desatualizada quanto às dependências. Caminhos: `v2/crates/ruview-policy/src/lib.rs`, `docs/adr/ADR-321-decision-policy-action-authorization.md`, `docs/user-guide.md`.
- **Riscos/limitações:** sem integração com atuadores reais.
- **Relevância para a plataforma (M13, M15, M07):** alta. Complementa o `AUTOMATION_DRY_RUN`: com tudo em L0, qualquer ação além de conveniência é sempre negada ("evidência abaixo do piso"), o que explica por que a automação continua em dry-run.

#### GV-07 — Intents governadas, aprovações assinadas, idempotência e recibos encadeados

- **O que faz:** camada que **nunca toca atuadores** e transforma pedidos tipados (observar, recomendar, executar) em recibos testemunhados. O padrão é "recomendar". "Executar" só gera recibo "Autorizado" com política versionada, concessão, alvo em allowlist, aprovações distintas e assinadas e garantia viva suficiente.
- **Como faz:** a intent carrega tenant, workspace, ação, versão de política, alvo, classe, solicitante, janela, nonce e digests. As aprovações assinam o digest da intent. O motor mantém idempotência (repetição idêntica devolve o mesmo recibo e reuso alterado é conflito), detecção de reuso de nonce e recibos encadeados por hash.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: FastAPI e SQLite (intents, aprovações, recibos), Ed25519.
  - Dados: políticas e aprovadores.
  - Competências: aprovação "four-eyes", idempotência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 6 testes. Sem consumidor. Gates de implantação pendentes. Caminhos: `v2/crates/ruview-policy/src/governed.rs`, `docs/adr/ADR-327-governed-action-intents-and-witness-receipts.md`.
- **Riscos/limitações:** estado em memória. Sem RBAC real. "Autorizado" não prova atuação.
- **Relevância para a plataforma (M13, M15):** muito alta e alinhada às regras da plataforma: modos Observe e Recommend como padrão, Execute BLOCKED, recibos encadeados no SQLite e idempotency-key mais nonce nos POSTs de automação.

#### GV-08 — Scorecard multidomínio com intervalo de Wilson e gate de promoção pelo pior domínio

- **O que faz:** impede promover modelos por acurácia agregada. Mantém uma célula por domínio operacional (sala conhecida ou inédita, dispositivo inédito, sujeito parado a distância, pose em sujeito ou sala inédita, rejeição OOD, drift). **O gate falha se qualquer domínio piorar além da tolerância, mesmo que a média melhore.**
- **Como faz:** estimativa e IC por score de Wilson (determinístico). Domínio vazio é "sem evidência" e nunca passa. Pior domínio por tarefa, comparação anterior/atual com tolerância e detecção de perda de cobertura e de aumento de drift.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: statsmodels (proportion_confint "wilson"), pytest.
  - Dados: avaliação particionada por domínio.
  - Competências: estatística de proporções.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 17 testes (Wilson conferido à mão, regressão escondida, perda de cobertura). Sem uso em CI de modelos reais. Caminhos: `v2/crates/ruview-scorecard/src/lib.rs`, `docs/adr/ADR-317-benchmark-multi-domain-scorecard.md`.
- **Riscos/limitações:** domínios fixos no código. Só métricas binomiais.
- **Relevância para a plataforma (M12, M15, M16):** alta. Cenários do gerador particionados por "domínio" e gate de pior domínio no `check.ps1`.

#### GV-09 — Plano de validação ground truth: séries, alinhamento temporal, concordância e escopo obrigatório

- **O que faz:** compara estimativas RF com referências independentes (câmera, mmWave, tapete de pressão, wearable, oxímetro, microfone, rótulo manual) para presença, contagem, distância, postura, atividade, FC e FR. **As referências nunca viram entrada de inferência.** Gera um registro graduado para o ledger.
- **Como faz:** séries validadas e alinhamento por deslocamento constante (correlação cruzada normalizada para contínuos, concordância de rótulos para categóricos), **reportado e nunca aplicado em silêncio**. Pares, cobertura, MAE, RMSE, viés e concordância, com escopo obrigatório. Measured exige referência independente e reprodutor. Sobreposição insuficiente gera relatório inconclusivo, não erro.
- **Requisitos para implementar:**
  - Hardware: sensores de referência reais para sair de L0.
  - Software: numpy, `scipy.signal.correlate`, pandas.
  - Dados: sessões sincronizáveis com consentimento.
  - Competências: sincronização, Bland–Altman, ética.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 15 testes com séries sintéticas. Nenhum log real (coerente com a política de dados). Caminhos: `v2/crates/ruview-groundtruth/src/lib.rs`, `align.rs`, `agreement.rs`, `scope.rs`, `series.rs`, `source.rs`, `docs/adr/ADR-303-ground-truth-synchronization.md`.
- **Riscos/limitações:** só deslocamento constante (sem drift de relógio). Vitais exigem cuidado regulatório.
- **Relevância para a plataforma (M04, M05, M01, M02, M15, M16):** média-alta como arquitetura. Implementar já o "plano de validação" com referências sintéticas (o gerador fornece a verdade), preparando o `RF_VALIDATION_PROTOCOL`. Medição real fica PLANNED/BLOCKED. Ver também SV-18.

#### GV-10 — Rótulos de radar mmWave, autolabel de ocupação, split disjunto por sessão e baseline majoritário

- **O que faz:** converte logs de radar mmWave em rótulos de presença, contagem e distância com incerteza e motivo de "desconhecido". Corta gravações CSI nas janelas do radar, oferece split por sessão sem vazamento e um baseline trivial para comparar qualquer acurácia.
- **Como faz:** JSONL tolerante com limites. O deslocamento de relógio é um parâmetro declarado. Janelas são descartadas com motivo contabilizado, incluindo uma **guarda de retenção** que descarta "vazio" logo após "ocupado", porque rastreadores perdem pessoas paradas. Split por sessão e baseline ajustado no treino.
- **Requisitos para implementar:**
  - Hardware: radar mmWave (custo baixo, não zero) e nó CSI.
  - Software: pandas, scikit-learn (GroupShuffleSplit, DummyClassifier).
  - Dados: gravações sincronizadas.
  - Competências: rotulagem fraca e limitações de radar.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Contagem de testes: radar 14, autolabel 7, baseline 5, mais um pipeline sintético. O código reconhece que radar não é verdade humana. Caminhos: `v2/crates/ruview-groundtruth/src/radar.rs`, `autolabel.rs`, `baseline.rs`, `examples/radar_autolabel.rs`, `tests/radar_autolabel_pipeline.rs`.
- **Riscos/limitações:** viés do radar com pessoa parada. Deslocamento global.
- **Relevância para a plataforma (M01, M02, M03, M12, M16):** média. Split por grupo, baseline obrigatório e "Unknown com motivo" já no Model Lab sintético. Radar fica PLANNED.

#### GV-11 — Verificação offline de tokens OAuth/JWT com escopos por raio de impacto

- **O que faz:** o servidor atua como resource server e verifica offline os tokens de um provedor de identidade via JWKS, exigindo o escopo da rota (leitura para streams e inferência; admin para treino e exclusões).
- **Como faz:** algoritmo fixado no código (o cabeçalho só é comparado, o que neutraliza "alg none" e a troca de algoritmo). Cache de JWKS com TTL, intervalo mínimo, timeout e refetch limitado, **lock nunca mantido durante I/O** e fail-closed só se nunca houve JWKS válido. Claims: allowlist de client_id, escopo, recusa de credenciais de longa duração e leeway. Transporte injetável.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: PyJWT ou joserfc/Authlib, httpx; IdP open-source (Keycloak, Authentik, Zitadel).
  - Dados: JWKS.
  - Competências: OAuth/OIDC.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Matriz negativa com 25 testes (chaves geradas em teste), além de jwks 10, verify 6 e principal 6. É o único crate da área integrado ao servidor e à CLI. **O Cargo.toml não declara licença.** Caminhos: `v2/crates/ruview-auth/src/lib.rs`, `verify.rs`, `jwks.rs`, `principal.rs`, `tests/verifier_matrix.rs`, `docs/adr/ADR-271-cognitum-oauth-resource-server.md`.
- **Riscos/limitações:** acoplado a um IdP específico com claims não padronizadas. Sem revogação.
- **Relevância para a plataforma (M15):** média. Quando houver multiusuário: algoritmo fixo, cache de JWKS com rate limit e escopos por raio de impacto, com IdP self-hosted gratuito.

#### GV-12 — Login interativo PKCE (CLI) com armazenamento de credenciais e refresh single-flight

- **O que faz:** obtém tokens via navegador (PKCE com callback em loopback) ou colagem de código (SSH ou containers), persiste credenciais e renova com segurança refresh tokens rotativos.
- **Como faz:** PKCE (RFC 7636). Mutex assíncrono mantido durante o await, rechecagem depois do lock e persistência antes de retornar. **Nunca reenvia o mesmo refresh token.** Lock advisory de arquivo entre processos. Atrás de features opcionais.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Authlib/oauthlib, filelock.
  - Dados: registro de cliente.
  - Competências: OAuth nativo (RFC 8252), concorrência.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 37 testes de login mais 4 de PKCE. Sem teste ponta a ponta contra IdP. Caminhos: `v2/crates/ruview-auth/src/login/mod.rs`, `flow.rs`, `callback.rs`, `store.rs`, `src/pkce.rs`, `v2/crates/wifi-densepose-cli/src/auth.rs`.
- **Riscos/limitações:** lock só Unix. Credenciais em arquivo.
- **Relevância para a plataforma (M15, M16):** baixa no curto prazo. O padrão de refresh single-flight vale para qualquer cliente futuro.

#### GV-13 — Autenticação da superfície web: bearer em camadas, sessão de navegador server-side e tickets de WebSocket

- **O que faz:** protege a API com token estático opcional ou OAuth aditivo. Permite login no navegador **sem que o JavaScript veja o access token**. Fecha os WebSockets com tickets de uso único.
- **Como faz:** comparação em tempo constante, JWT com escopo por rota e 401. Sem configuração, o servidor fica aberto (postura LAN histórica). Na sessão de navegador, PKCE e state ficam em cookie assinado e o servidor emite seu próprio cookie HttpOnly e SameSite=Lax (Secure só sob TLS). O ticket é obtido por POST autenticado, é curto, de uso único, limitado por principal e não serve para REST.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Starlette, itsdangerous, Authlib.
  - Dados: nenhum.
  - Competências: segurança web.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: bearer_auth 19, browser_session 32, ws_ticket 13. Postura "aberto por padrão" declarada. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/bearer_auth.rs`, `browser_session.rs`, `ws_ticket.rs`, `docs/adr/ADR-272-websocket-authentication-tickets.md`.
- **Riscos/limitações:** API sem autenticação por padrão fora de loopback. Ticket na URL vai para logs. Cookie sem prefixo `__Host-`.
- **Relevância para a plataforma (M15):** média-alta. A plataforma já autentica o WS pelo primeiro frame (preferível ao ticket em query). "O navegador nunca segura o token", com sessão server-side e cookie HttpOnly, é a evolução natural para multiusuário. Ver também SS-14 e UI-03.

#### GV-14 — Endurecimento de superfície: allowlist de Host contra DNS rebinding, saneamento de caminhos e bind restrito do plano de dados

- **O que faz:** impede leitura do servidor local via DNS rebinding, bloqueia path traversal em identificadores e restringe o receptor UDP a loopback por padrão, com allowlist e contador de descartes.
- **Como faz:** middleware de Host, identificador seguro por subconjunto de caracteres e decisão de bind como função pura (bind roteável sem proteção é recusado).
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: `TrustedHostMiddleware` (Starlette), pathlib.
  - Dados: nenhum.
  - Competências: segurança de aplicações locais.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Contagem de testes: host_validation 5, path_safety 9, udp_bind 13. A ADR-296 declara que a allowlist de IP não autentica o remetente. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/host_validation.rs`, `path_safety.rs`, `udp_bind.rs`, `http_bind.rs`, `docs/adr/ADR-296-sensor-data-plane-bind-hardening.md`.
- **Riscos/limitações:** spoofing na LAN.
- **Relevância para a plataforma (M15):** alta e de custo baixo: `TrustedHostMiddleware`, revisão de identificadores em rotas de arquivo e bind em loopback documentado no `SECURITY_REVIEW`.

#### GV-15 — Privacidade em tempo de execução: filtro privacy-mode, rebaixamento de classe e máquina de estados de proveniência

- **O que faz:** combina o modo de privacidade (SS-15), o rebaixamento de classe por contradições ou risco de malha (SS-07) e a máquina de estados de fonte (SS-02).
- **Como faz:** remoção de chaves, e não anulação. O rebaixamento é recalculado a cada ciclo, nunca pula mais de um nível nem relaxa no mesmo ciclo. A proveniência é função pura em que ambiguidade nunca resolve para "verificado".
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: middleware FastAPI, Pydantic com exclusão por política.
  - Dados: classificação de campos.
  - Competências: privacy by design.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 3 testes mais 13. O documento de confiança é ancorado em arquivos e linhas do motor. Caminhos: `v2/crates/wifi-densepose-sensing-server/src/privacy_filter.rs`, `provenance.rs`, `docs/trust-and-engine-errors.md`, `docs/adr/ADR-295-source-provenance-state-machine.md`.
- **Riscos/limitações:** pelo menos duas escadas de privacidade diferentes (quatro níveis no BFLD, P0–P5 no unified). O filtro por nome deixa vazar campos novos.
- **Relevância para a plataforma (M15, M04, M05, M11, M09):** alta. Privacy mode com **allowlist** (não denylist), classe única de privacidade no contrato e proveniência em que SIMULATED nunca vira LIVE.

#### GV-16 — WiFi VEIL: contramedida de privacidade por formato de onda compatível (modelo de referência sintético)

- **O que faz:** pesquisa uma defesa contra reidentificação passiva via beamforming feedback em claro. O nó aplica ao próprio relatório uma rotação ortogonal chaveada por sessão, que o receptor legítimo desfaz. Não emite RF.
- **Como faz:** modelo de dois subespaços com rotações de Givens chaveadas no subespaço fino, além de modos de unitária por pacote e de dither com privacidade diferencial. Inclui atacantes, throughput, compliance (razão de energia próxima de 1, "não é jamming"), otimizador, prova determinística, TUI, console e um harness npm.
- **Requisitos para implementar:**
  - Hardware: nenhum para o modelo.
  - Software: numpy, scikit-learn (NearestCentroid).
  - Dados: BFI real para ir além de L0.
  - Competências: 802.11, privacidade diferencial.
- **Evidência e maturidade:** `RESEARCH` / `SYNTHETIC_OR_SIMULATED`. Cerca de 43 testes. Os números descrevem o modelo L0, como o README declara. A numeração de ADR é inconsistente. Caminhos: `v2/crates/wifi-densepose-privshield/README.md`, `src/protector.rs`, `attacker.rs`, `compliance.rs`, `optimize.rs`, `proof.rs`, `harness/wifi-densepose-privshield/README.md`, `docs/adr/ADR-288-veil-privacy-shield-compliant-waveform.md`.
- **Riscos/limitações:** transferência para hardware não provada. Questões regulatórias.
- **Relevância para a plataforma (M15, M08):** baixa como funcionalidade. Útil a ideia de um teste pytest de "vazamento de privacidade" que tenta reidentificar entidades sintéticas a partir de saídas agregadas e exige desempenho próximo ao acaso. Ver também FW-18.

#### GV-17 — WiFi VEIL em firmware e hardware: núcleo C portável e adaptadores por fornecedor

- **O que faz:** leva o VEIL ao silício: núcleo C99 consistente byte a byte com o PRNG Rust e adaptadores (PHY aberto em FPGA, OpenWrt, firmware Broadcom e ESP32 em papéis de apoio).
- **Como faz:** núcleo sem malloc nem I/O, testado em host. Adaptadores scaffold com TODO(hw), matriz de viabilidade e protocolo de medição.
- **Requisitos para implementar:**
  - Hardware: Zynq com AD9361, APs, Raspberry Pi, ESP32, RIS (nada a custo zero).
  - Software: toolchains C, Vivado.
  - Dados: capturas de bancada.
  - Competências: firmware sem fio, FPGA.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Só o núcleo tem teste. Há 63 marcadores TODO(hw). Caminhos: `firmware/privshield/README.md`, `firmware/privshield/core/veil_shield.c`, `core/test/test_veil_shield.c`, `firmware/privshield/openwifi/MEASUREMENT.md`, `docs/adr/ADR-290-veil-e2e-hardware-implementation-program.md`.
- **Riscos/limitações:** viabilidade baixa fora do PHY aberto.
- **Relevância para a plataforma (M15, M08):** muito baixa (BLOCKED). Exemplo de "banner de honestidade" em artefatos não validados.

#### GV-18 — Governança de claims e reprodutibilidade: PROOF.md, prove.sh, retratações e witness bundle com redação

- **O que faz:** gradua alegações como MEASURED (reproduzida, com teste que falha no código anterior à correção), CLAIMED ou DATA/HARDWARE-GATED. Oferece um script de prova única, testes "anti-slop", retratações públicas e um pacote de testemunho com segredos redigidos.
- **Como faz:** o gate de testes do workspace mais uma prova determinística (hash do pipeline de referência). Itens dependentes de GPU, dataset ou hardware só imprimem o pré-requisito. Códigos de saída distintos. O bundle passa os logs por um filtro de redação heurístico.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: PowerShell/pytest com markers; detect-secrets ou gitleaks em vez de regex própria.
  - Dados: fixtures de prova.
  - Competências: engenharia de release.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNCLEAR`. Os scripts não foram executados. A alegação de "milhares de testes, 0 falhas" não foi verificada. A redação não tem testes. Caminhos: `PROOF.md`, `docs/proof-of-capabilities.md`, `scripts/prove.sh`, `scripts/generate-witness-bundle.sh`, `scripts/redact-secrets.py`, `archive/v1/data/proof/verify.py`.
- **Riscos/limitações:** a redação heurística pode falhar. A prova atesta determinismo, não acurácia.
- **Relevância para a plataforma (M15):** alta e gratuita. Registro de claims graduadas com ID de teste, uma seção "o que não alegamos" e redação de segredos por ferramenta madura. Ver também OP-14.

#### GV-19 — Guarda de repositório para dados pessoais de CSI (política de dados)

- **O que faz:** impede versionar capturas brutas de CSI (dados pessoais: respiração, movimento, presença). Falha com arquivos de formato de captura, metadados ou JSONL grandes rastreados ou em stage, com allowlist para fixtures sintéticas.
- **Como faz:** script determinístico sobre a lista de arquivos do git, com padrões de extensão, limite de tamanho, allowlist, códigos de saída distintos e autoteste. Nasceu de um incidente real (ADR-299).
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: pre-commit, check-added-large-files, gitleaks.
  - Dados: definição de formatos sensíveis.
  - Competências: higiene de repositório, LGPD.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. O threat model registra o autoteste aprovado e uma varredura limpa. A coordenação do histórico git segue pendente. Caminhos: `scripts/csi-data-policy-check.sh`, `scripts/csi-data-policy.allow`, `docs/adr/ADR-299-csi-data-incident-repo-controls.md`.
- **Riscos/limitações:** baseado em extensão e tamanho.
- **Relevância para a plataforma (M15, M12):** alta e preventiva. Hook pre-commit com padrões de futuras capturas e allowlist de fixtures sintéticas, antes de qualquer opt-in de laboratório.

#### GV-20 — Protocolo clean-room, classificação de dados P0–P5, threat model STRIDE e auditoria de segurança

- **O que faz:** documenta controles de originalidade e segurança:
  - clean-room com caminhos mutuamente exclusivos (independente ou derivado com atribuição), intake de exposição, atestação por PR, controles de ferramentas de IA, gate de licença de datasets e manifesto de proveniência com SBOM;
  - threat model com classificação P0–P5 por destino, fail-closed, quarentena de resultados externos, assinatura de release e STRIDE;
  - auditoria de um subsistema de automação com achados críticos.
- **Como faz:** documentos normativos com tabelas de decisão. Na auditoria, o achado crítico de autenticação foi remediado com um token store, **mantendo um modo de migração que reproduz o comportamento inseguro**.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: cyclonedx-py, pip-audit, npm audit, gitleaks, osv-scanner.
  - Dados: inventário de datasets.
  - Competências: licenciamento, STRIDE, LGPD, governança de IA.
- **Evidência e maturidade:** `DOC_ONLY` / `NONE`. O clean-room se declara "Proposed" e diz não comprovar que os controles passaram. O threat model registra que ferramentas de auditoria de dependências não estavam instaladas. Caminhos: `docs/security/ruview-forecast-clean-room.md`, `docs/security/ruview-forecast-threat-model.md`, `docs/security/HOMECORE-security-audit-iter10.md`, `v2/crates/homecore-api/src/auth.rs`.
- **Riscos/limitações:** é só processo, sem automação.
- **Relevância para a plataforma (M15, M12):** alta como processo: classificação de dados por destino, registro de sessões de IA (ferramenta, versão, sem colar código de referência), SBOM e checklist STRIDE no `SECURITY_REVIEW`. A plataforma **não deve alegar clean-room estrita**.

### 4.9 HomeCore, automação local, HAP/Matter/Home Assistant e integrações

**Escopo.** A área tem dois blocos com maturidade bem diferente.

1. **HOMECORE**, um port alfa em Rust do núcleo do Home Assistant: nove crates de biblioteca e um binário integrador, com cerca de 400 marcadores de teste. Toda a validação é local e sintética, sem prova contra o Home Assistant real, controladores Apple ou hardware. Parte dos testes depende de features que o CI principal desliga.
2. **Integrações RuView → ecossistema**: publicação MQTT para o HA, blueprints, cog, protótipo HomeKit em Python, ponte de LiDAR do iPhone, adaptador de pesquisa e metaharness. O Matter não está implementado em lugar nenhum. Os READMEs das crates estão defasados, enquanto os documentos mais recentes (`v2/docs/homecore-capabilities.md`, `docs/integrations/home-assistant.md`) rotulam com honestidade o que é CLAIMED e o que é MEASURED.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| HC-01 | Núcleo HOMECORE (estados, barramento, serviços, registros) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15 |
| HC-02 | API REST compatível com HA, token longo e CORS por allowlist | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15 |
| HC-03 | API WebSocket compatível com HA | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13 |
| HC-04 | Motor de automação gatilho→condição→ação com modos limitados | PARTIAL | UNIT_TESTS_ONLY | M13, M01, M02, M03, M07 |
| HC-05 | Templates Jinja em sandbox com orçamento de CPU | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15 |
| HC-06 | Recorder SQLite (histórico, logbook, deduplicação, purge, restauração, busca) | PARTIAL | UNIT_TESTS_ONLY | M13, M15, M02 |
| HC-07 | Migração do Home Assistant (`.storage` → HOMECORE) | PARTIAL | UNIT_TESTS_ONLY | M13, M16 |
| HC-08 | Plugins WASM em sandbox com Ed25519, SHA-256 e capabilities | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15 |
| HC-09 | Assist: reconhecimento de intenções (regex + feature hashing) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13 |
| HC-10 | Pipeline de voz STT→intenção→TTS e protocolo de satélite (contratos) | STUB | UNIT_TESTS_ONLY | M13 |
| HC-11 | Ponte HomeKit (HAP) nativa em Rust | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M13, M01, M07, M15 |
| HC-12 | Protótipo HomeKit em Python (HAP-python), HomePod, Atalhos, MCP | IMPLEMENTED_UNTESTED | UNCLEAR | M13, M01, M07, M15 |
| HC-13 | homecore-server: binário integrador, gateway BFF e dashboard | PARTIAL | UNIT_TESTS_ONLY | M13, M15, M16 |
| HC-14 | Publicação MQTT para HA com primitivas e modo de privacidade | PARTIAL | UNCLEAR | M13, M01, M02, M04, M05, M07, M09, M15 |
| HC-15 | Blueprints de automação do HA e dashboards Lovelace | IMPLEMENTED_UNTESTED | UNIT_TESTS_ONLY | M13, M01, M02, M07, M09 |
| HC-16 | cog-ha-matter: pacote instalável (mDNS, manifest, publisher; Matter adiado) | PARTIAL | UNIT_TESTS_ONLY | M13, M15 |
| HC-17 | Cadeia de testemunhas append-only com hash + Ed25519 | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| HC-18 | Ponte de LiDAR do iPhone (profundidade → relay WS → nuvem de pontos) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M14, M16 |
| HC-19 | Adaptador "virtual-view" (pesquisa, desabilitado, sem atuação) | RESEARCH | UNIT_TESTS_ONLY | M14 |
| HC-20 | Metaharness "homecore" para desenvolvedores (CLI + MCP somente leitura) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | NONE |

#### HC-01 — Núcleo HOMECORE: máquina de estados, barramento de eventos, registro de serviços e registros de entidades/dispositivos

- **O que faz:** mapa concorrente entity_id → snapshot de estado (valor, atributos, last_changed e last_updated); eventos tipados de sistema e eventos de domínio livres; despacho de chamadas de serviço com isolamento de pânico; registros de entidades e dispositivos no formato do HA.
- **Como faz:** padrão "hub" do HA reimplementado em Rust assíncrono. Um mapa concorrente fragmentado guarda os estados, e cada escrita gera evento num canal broadcast de capacidade fixa. **Assinantes lentos recebem sinal de atraso e devem se ressincronizar.** Um Context (id, user_id, parent_id) forma a cadeia de causalidade, que atribui mudanças a usuários e evita loops de automação. O handler é clonado fora do lock. O EntityId é validado estritamente.
- **Requisitos para implementar:**
  - Hardware: qualquer CPU.
  - Software: no alvo, asyncio e Pydantic.
  - Dados: nenhum externo.
  - Competências: programação assíncrona, semântica de estado do HA.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 26 testes e um benchmark. O README ainda diz "P1 scaffold" e mostra contagem de testes antiga. Persistência e validação de schema estão pendentes. Caminhos: `v2/crates/homecore/src/state.rs`, `bus.rs`, `event.rs`, `service.rs`, `registry.rs`, `entity.rs`, `docs/adr/ADR-127-homecore-state-machine-rust.md`.
- **Riscos/limitações:** mutações de registro não persistem. Broadcast fixo perde eventos.
- **Relevância para a plataforma (M13, M15):** alta como padrão. Barramento in-process com eventos Pydantic e **Context causal** (id, parent, ator), que ajuda a auditoria (M15) e a prevenção de loops (M13).

#### HC-02 — API REST compatível com Home Assistant + autenticação por token longo + CORS por allowlist

- **O que faz:** rotas no formato do HA para estados, serviços, eventos, template, verificação de configuração, log de erro, histórico, logbook, calendários e câmera, mais **uma matriz de compatibilidade legível por máquina**.
- **Como faz:** Bearer validado contra um armazenamento de tokens vindo de variável de ambiente. Sem tokens, o binário falha fechado; há um modo de desenvolvimento explícito que aceita qualquer token. CORS por allowlist sem credenciais e erros como envelope tipado. Calendário vazio e câmera "indisponível" são tipados. A rota de compatibilidade declara o que está implementado, o que depende de integração e o que fica vazio.
- **Requisitos para implementar:**
  - Hardware: servidor local.
  - Software: no alvo, FastAPI.
  - Dados: tokens.
  - Competências: compatibilidade de protocolo.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 39 testes, incluindo HTTP in-process e autenticação do binário. A ADR-161 registra correções (rota pública e WS que aceitava qualquer token). Algumas rotas são cascas honestas. Caminhos: `v2/crates/homecore-api/src/app.rs`, `rest.rs`, `auth.rs`, `tokens.rs`, `tests/compatibility_surface.rs`, `v2/docs/homecore-capabilities.md`, `docs/adr/ADR-161-homecore-server-layer-security.md`.
- **Riscos/limitações:** tokens sem expiração nem rotação. Lookup não constante no tempo. O servidor integrador escuta em 0.0.0.0 por padrão.
- **Relevância para a plataforma (M13, M15):** média. Vale aproveitar a **rota de matriz de capacidades legível por máquina** (alinhada a PLANNED/BLOCKED), a falha fechada sem token e o CORS sem credenciais. Expor uma API "estilo HA" não é necessário.

#### HC-03 — API WebSocket compatível com HA (handshake de auth, comandos, assinatura de eventos com fila limitada)

- **O que faz:** protocolo WS do HA (exigência de auth, autenticação, resultado) e comandos de ping, estados, configuração, serviços, registros, chamada de serviço, disparo de evento, template e assinatura.
- **Como faz:** autenticação obrigatória antes de qualquer comando. Uma **tarefa escritora por conexão drena uma fila de saída limitada**, para que um cliente que não lê não esgote a memória. Em caso de lag, ressincroniza em vez de encerrar.
- **Requisitos para implementar:**
  - Hardware: servidor.
  - Software: WebSocket (Starlette).
  - Dados: nenhum.
  - Competências: streaming e backpressure.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Teste ponta a ponta de handshake. A ADR-161 registra três correções (autenticação contornável, respostas logadas e descartadas, stream encerrado por lag). Caminhos: `v2/crates/homecore-api/src/ws.rs`, `tests/ws_handshake.rs`.
- **Riscos/limitações:** subconjunto de comandos.
- **Relevância para a plataforma (M13):** média. Fila de saída limitada por conexão com ressincronização é diretamente aplicável ao stream sintético da plataforma.

#### HC-04 — Motor de automação gatilho→condição→ação com modos de execução limitados

- **O que faz:** automações declarativas em YAML no estilo HA.
  - Gatilhos: mudança de estado, cruzamento numérico, horário e evento.
  - Condições: estado, numérica, template e combinações lógicas.
  - Ações: serviço, atraso, cena, `choose` e espera por gatilho.
  - Modos: single, restart, queued e parallel, com teto de concorrência.
- **Como faz:** casamento síncrono a cada evento e temporizador de 1 Hz para horário. Cada automação tem estado de execução: guarda de reentrância (single), aborto (restart), mutex FIFO (queued) e semáforo (teto). Atrasos com conversão segura de duração (rejeita negativos, NaN e infinitos, com teto).
- **Requisitos para implementar:**
  - Hardware: servidor.
  - Software: Pydantic/JSON Schema e asyncio (Task.cancel, Lock, Semaphore).
  - Dados: automações do operador.
  - Competências: semântica de regras e concorrência.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 54 testes, cobrindo timer, single, parallel, template, restart, queued e teto. **A espera por gatilho é stub** (só dorme). Faltam vários gatilhos e ações. O README descreve gatilhos, ações e um formato YAML diferentes dos aceitos. Caminhos: `v2/crates/homecore-automation/src/engine.rs`, `trigger.rs`, `condition.rs`, `action.rs`, `runmode.rs`, `tests/engine_behaviors.rs`, `docs/adr/ADR-129-homecore-automation-engine.md`, `docs/adr/ADR-162-plugin-security-and-bounded-runmodes.md`.
- **Riscos/limitações:** sem persistência do estado de execução nem trace. Condição malformada desliga um ramo em silêncio.
- **Relevância para a plataforma (M13, M01, M02, M03, M07):** alta. É o núcleo das regras da fase de automação. Regras validadas por Pydantic sobre observações sintéticas, com modos via asyncio, sem copiar nada.

#### HC-05 — Templates Jinja em sandbox com orçamento de CPU e limite de tamanho

- **O que faz:** renderiza templates no estilo HA em condições, na rota REST e no WS.
- **Como faz:** funções globais sobre o estado vivo. **Orçamento de instruções da VM** contra expansão ilimitada e rejeição de fontes acima de um tamanho antes de compilar. Erros tipados.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Jinja2 SandboxedEnvironment ou DSL fechada (simpleeval com whitelist).
  - Dados: templates.
  - Competências: segurança de linguagens embutidas.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 12 testes, incluindo o caso de DoS. Só quatro funções globais. Caminhos: `v2/crates/homecore-automation/src/template.rs`.
- **Riscos/limitações:** o orçamento não limita memória diretamente.
- **Relevância para a plataforma (M13, M15):** média-alta como lição. A plataforma exige "sem execução arbitrária de código", então o preferível é uma DSL fechada; se houver templates, usar sandbox com limites e timeout.

#### HC-06 — Recorder SQLite: histórico, logbook, deduplicação de atributos, purge, restauração e busca

- **O que faz:** persiste mudanças e eventos em SQLite, atende histórico e logbook, purga, restaura o último estado no boot e oferece busca textual e um índice "semântico" opcional.
- **Como faz:** o listener **assina o broadcast no construtor**, para não perder eventos. São quatro tabelas inspiradas no recorder do HA, com blobs de atributos deduplicados por hash FNV-1a do JSON canônico. Restauração determinística, limitada e com isolamento de linhas malformadas. A busca usa LIKE com escape. O "semântico" é **hash SHA-256 reduzido a vetor** num HNSW, e o próprio código admite que não captura semântica.
- **Requisitos para implementar:**
  - Hardware: disco.
  - Software: SQLite, SQLite FTS5 (embutido).
  - Dados: fluxo de estados.
  - Competências: séries temporais em SQLite.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 34 testes. O índice semântico é opcional e fica fora do CI. O README alega schema idêntico ao do HA, mas o código implementa um subconjunto. Sem retenção agendada. Caminhos: `v2/crates/homecore-recorder/src/db.rs`, `schema.rs`, `dedup.rs`, `listener.rs`, `semantic.rs`, `v2/crates/homecore-server/src/restore.rs`, `docs/adr/ADR-132-homecore-recorder-history-semantic-search.md`.
- **Riscos/limitações:** LIKE não escala. Nome "semântico" enganoso.
- **Relevância para a plataforma (M13, M15, M02):** alta como confirmação de design (a plataforma já usa SQLite e retenção): deduplicação de blobs por hash, restauração limitada e listener que assina antes de iniciar. Para busca, FTS5.

#### HC-07 — Migração do Home Assistant (`.storage` → HOMECORE)

- **O que faz:** uma CLI importa registros de entidades e dispositivos e config entries do HA e inspeciona `secrets.yaml` e automações em modo de leitura.
- **Como faz:** lê o envelope versionado e **rejeita versão desconhecida**. Gera avisos tipados. A escrita é atômica (temporário sincronizado mais link sem sobrescrita). **Erros de segredos não ecoam o valor.**
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: serde/YAML (no alvo, Python).
  - Dados: `.storage` do HA.
  - Competências: formatos internos do HA.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 25 testes. Limitações honestas listadas (não converte automações nem resolve segredos). Caminhos: `v2/crates/homecore-migrate/src/storage.rs`, `storage_format/v13.rs`, `entity_registry.rs`, `secrets.rs`, `cli.rs`, `docs/adr/ADR-165-homecore-migrate-from-home-assistant.md`.
- **Riscos/limitações:** acoplado a formatos internos instáveis.
- **Relevância para a plataforma (M13, M16):** baixa como funcionalidade. Média como padrão para import/export e backup: envelope versionado, escrita atômica sem sobrescrita e erros sem segredos.

#### HC-08 — Plugins WASM em sandbox com assinatura Ed25519, integridade SHA-256 e permissões por capacidade

- **O que faz:** carrega integrações como módulos WebAssembly isolados com uma ABI estreita (ler e escrever estado, assinar mudanças, log). **Bibliotecas dinâmicas arbitrárias nunca são carregadas.**
- **Como faz:** descoberta restrita a filhos imediatos, rejeição de symlinks e traversal, e limites. A verificação tem três passos: SHA-256 do módulo contra o manifest, Ed25519 do publicador e chave na allowlist. Sem assinatura, só com flag de desenvolvimento. Um Store por plugin, **sem WASI** (sem rede nem sistema de arquivos), com limites de memória e combustível por chamada. As escritas passam por um conjunto de permissões derivado das globs do manifest, **negando tudo por padrão**. Fan-out por fila limitada.
- **Requisitos para implementar:**
  - Hardware: servidor.
  - Software: wasmtime-py (Apache-2.0), PyNaCl/cryptography, hashlib.
  - Dados: pacotes assinados e chaves de publicadores.
  - Competências: sandboxing, ABI, capabilities.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 35 testes mais integração Wasmtime, **atrás de uma feature ausente do CI padrão**. O README está defasado. A ADR-162 registra que as permissões antes eram parseadas mas nunca consultadas. Caminhos: `v2/crates/homecore-plugins/src/wasmtime_runtime.rs`, `verify.rs`, `permissions.rs`, `discovery.rs`, `host_abi.rs`, `manifest.rs`, `tests/integration.rs`, `docs/adr/ADR-128-homecore-integration-plugin-system.md`.
- **Riscos/limitações:** ABI não congelada. Combustível não limita tempo de chamadas do host. Sem revogação de chaves.
- **Relevância para a plataforma (M13, M15):** alta para "plugins WASM assinados opcionais com capabilities". Manifest Pydantic, negação por padrão e nascimento desabilitado (PLANNED) até revisão de segurança. Ver também EH-01.

#### HC-09 — Assist: reconhecimento de intenções (regex + embedding por feature hashing) e handlers estilo HA

- **O que faz:** converte frases em intenções (ligar, desligar, brilho, cancelar) com slots e executa o serviço correspondente, com resposta estruturada.
- **Como faz:** pipeline reconhecedor → handler → resposta. Regex com grupos nomeados e limite de bytes. O reconhecedor "semântico" usa feature hashing (unigramas e trigramas de caracteres, L2) com k-NN exato por cosseno e limiar, recorrendo à regex abaixo do limiar. Há runner local e um runner nulo que declara que o LLM externo não existe.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: scikit-learn (HashingVectorizer) ou rapidfuzz.
  - Dados: exemplares por intenção.
  - Competências: NLU clássica.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 53 testes. O "semântico" fica fora do CI. Os comentários falam em HNSW, mas a implementação é varredura exata. O servidor usa só regex. Caminhos: `v2/crates/homecore-assist/src/pipeline.rs`, `recognizer.rs`, `semantic_recognizer.rs`, `embedding.rs`, `handler.rs`, `runner.rs`, `docs/adr/ADR-133-homecore-assist-ruflo.md`.
- **Riscos/limitações:** similaridade só lexical, só inglês. Os handlers atuam sem confirmação.
- **Relevância para a plataforma (M13):** baixa a média. Consultas em linguagem natural **somente leitura** sobre dados sintéticos, sem LLM.

#### HC-10 — Pipeline de voz STT→intenção→TTS e protocolo de satélite (contratos)

- **O que faz:** tipos de áudio limitados, contratos assíncronos de STT e TTS, pipeline voz→intenção→voz com timeout e protocolo de sessão de "satélite" independente de transporte.
- **Como faz:** validação de formato antes de aceitar dados e máquina de estados da sessão com autenticação no hello. **Os provedores padrão são "desabilitados" e retornam erro tipado em vez de transcrições inventadas.**
- **Requisitos para implementar:**
  - Hardware: microfone ou satélite.
  - Software: Vosk, whisper.cpp, Piper (gratuitos e locais).
  - Dados: áudio (sensível).
  - Competências: áudio e streaming.
- **Evidência e maturidade:** `STUB` / `UNIT_TESTS_ONLY`. Contratos testados, sem provedores e sem transporte exposto. Caminhos: `v2/crates/homecore-assist/src/audio.rs`, `speech.rs`, `voice.rs`, `satellite.rs`, `v2/docs/homecore-capabilities.md`.
- **Riscos/limitações:** sem provedor não há funcionalidade. Protocolo próprio.
- **Relevância para a plataforma (M13):** baixa e fora do escopo (BLOCKED/PLANNED). O padrão útil é "provedor desabilitado retorna erro tipado, nunca dado fabricado".

#### HC-11 — Ponte HomeKit (HAP) nativa em Rust: Pair-Setup SRP, Pair-Verify, transporte cifrado, mDNS e mapeamento entidade→acessório

- **O que faz:** faz o HOMECORE aparecer como bridge HomeKit para o app Casa, HomePod e Siri (leitura de ocupação, movimento, contato, temperatura, umidade, luz, interruptor, fechadura). Mapeia sinais RuView (presença, movimento, queda, respiração presente) **sem expor identidade**.
- **Como faz:**
  - Pair-Setup com SRP-6a (3072 bits, SHA-512), HKDF, ChaCha20-Poly1305 e Ed25519; Pair-Verify com X25519 e verificação estrita.
  - Registros cifrados com nonces monotônicos. Falhas fecham a conexão sem oráculo.
  - Rotas bloqueadas até a verificação. Gestão de pareamentos restrita a administrador; remover o último administrador apaga tudo e revoga sessões.
  - Arquivo de identidade versionado com substituição atômica e permissões restritas (fail-closed). O código de setup aparece só no primeiro provisionamento e é zerado.
  - mDNS `_hap._tcp`. O mapeador RuView **não carrega escore de risco de identidade nem hash de assinatura RF**.
- **Requisitos para implementar:**
  - Hardware: host na LAN com hub Apple e multicast.
  - Software: no alvo, HAP-python (Apache-2.0) com zeroconf.
  - Dados: arquivo de pareamento.
  - Competências: criptografia aplicada, protocolos binários.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 48 testes (vetor SRP, adulteração, replay, reinício atômico, ciclo TCP em loopback). **Sem teste contra controlador Apple real nem MFi.** Escrita de característica não existe. Os testes de servidor ficam fora do CI. O mapeador não está ligado. A dependência SRP é release candidate. Caminhos: `v2/crates/homecore-hap/src/pair_setup.rs`, `pair_verify.rs`, `crypto.rs`, `server.rs`, `pairing.rs`, `mdns.rs`, `mapping.rs`, `ruview.rs`, `docs/adr/ADR-125-ruview-apple-home-native-hap-bridge.md`.
- **Riscos/limitações:** a especificação não comercial não autoriza produto sem MFi. Mapear queda para sensor de vazamento é ambíguo.
- **Relevância para a plataforma (M13, M01, M07, M15):** média, como integração opcional futura via HAP-python. O mais valioso é o padrão de privacidade: só estados limiarizados e anônimos saem, como regra de M15, e acessórios com dados L0 se rotulam como simulados. Fica PLANNED.

#### HC-12 — Protótipo HomeKit em Python (HAP-python) + guia HomePod + Atalhos/launchd + consumo via MCP

- **O que faz:** um watcher lê UDP de um ESP32-C6, aplica um gate de classe de privacidade e grava estados por cômodo. Um servidor HTTP simples expõe vitais, BFLD e eventos. Uma bridge HAP-python cria acessórios por cômodo. Um job launchd com Atalhos anuncia eventos no HomePod.
- **Como faz:** três daemons encadeados por arquivos JSON em `/tmp` e polling HTTP. Os eventos semânticos limiarizados ("presença desconhecida", "ocupação inesperada") viram características booleanas, nunca probabilidades.
- **Requisitos para implementar:**
  - Hardware: Mac, iPhone, HomePod/Apple TV, ESP32-C6.
  - Software: HAP-python, Atalhos, Node.
  - Dados: fluxo UDP.
  - Competências: ecossistema Apple.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNCLEAR`. O guia alega validação em C6 real sem artefatos reproduzíveis. As ferramentas MCP vêm de pacote externo. **O exemplo usa um PIN de setup fixo.** Caminhos: `docs/user-guide-apple-homepod.md`, `scripts/ruview-hap-bridge.py`, `scripts/c6-presence-watcher.py`, `scripts/ruview-sensing-server.py`, `scripts/macos-shortcuts/`.
- **Riscos/limitações:** acoplamento por `/tmp` sem integridade. PIN fixo.
- **Relevância para a plataforma (M13, M01, M07, M15):** média como referência: HAP-python basta para um MVP HomeKit opcional que leia a API local autenticada (não arquivos). O vocabulário de eventos limiarizados é útil. Não copiar os scripts.

#### HC-13 — homecore-server: binário integrador, gateway BFF e dashboard operacional estático

- **O que faz:** um processo único com núcleo, recorder, restauração, serviços embutidos, automação, plugins, HAP opcional, API, intenções e gateway BFF (cômodos, cogs, métricas, proxy de calibração). Serve um dashboard em JS puro com painéis, incluindo um assistente de calibração.
- **Como faz:** boot em ordem de dependência e desligamento gracioso. **O BFF é a única origem que o navegador conhece, e os segredos de upstream ficam no servidor.** Rotas sem upstream retornam 503 tipado, e a UI mostra estado de erro sem cair em mock. Os mocks só carregam em modo demo explícito, com selo visível.
- **Requisitos para implementar:**
  - Hardware: appliance local.
  - Software: no alvo, route handlers do Next.js.
  - Dados: configurações.
  - Competências: integração, padrão BFF.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 22 testes Rust. Os testes Node da UI não estão no CI. Muitas rotas BFF são 503. Há inconsistência entre um cabeçalho ("não compilado") e a ADR ("compilado e testado"). **A UI guarda o token em `localStorage`**, e as entidades demo trazem um atributo de fonte que cita hardware real. Caminhos: `v2/crates/homecore-server/src/main.rs`, `gateway.rs`, `restore.rs`, `plugins.rs`, `hap.rs`, `ui/js/api.js`, `ui/js/mock.js`, `ui/js/panels/calibration.js`, `docs/adr/ADR-131-homecore-ui-operational-dashboard.md`.
- **Riscos/limitações:** bind 0.0.0.0. Token persistente no navegador. Demo com biometria simulada rotulada como fonte real.
- **Relevância para a plataforma (M13, M15, M16):** alta como referência e como lista de antipadrões. Aproveitar: BFF com segredos só no servidor, 503 tipado para upstream ausente e mocks só em demo com selo. Evitar: token em `localStorage`, bind público por padrão e rótulo de hardware em dado simulado.

#### HC-14 — Publicação MQTT para Home Assistant (auto-discovery) com primitivas semânticas e modo de privacidade

- **O que faz:** o servidor de sensoriamento cria no HA um dispositivo por nó com entidades de sinais e seis primitivas semânticas. O modo de privacidade remove biometria do fio. (O código está no servidor, ver SS-16 e SS-17; aqui ficam o guia, os benchmarks e as métricas.)
- **Como faz:** configs retidas, disponibilidade por entidade com heartbeat e **entidades sem fonte real ficam offline**. O client-id é persistido. As primitivas são FSMs com aquecimento e histerese.
- **Requisitos para implementar:**
  - Hardware: broker na LAN.
  - Software: Mosquitto/EMQX, HA, aiomqtt/paho.
  - Dados: snapshots.
  - Competências: discovery MQTT.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. **Há CI com Mosquitto real** e micro-benchmarks. O guia reconhece o que falta: sem last-will nem "offline" ao encerrar, primitivas por zona não anunciadas, flags de limiares e Matter não aceitas, pose não anunciada. **A tabela de precisão/recall das primitivas é CLAIMED**, porque a ferramenta de replay não está no repositório. Caminhos: `docs/integrations/home-assistant.md`, `docs/integrations/semantic-primitives-metrics.md`, `docs/integrations/benchmarks.md`, `.github/workflows/mqtt-integration.yml`, `docs/adr/ADR-115-home-assistant-integration.md`.
- **Riscos/limitações:** MQTT em texto claro fora de localhost. Estados derivados de biometria saem mesmo no modo de privacidade.
- **Relevância para a plataforma (M13, M01, M02, M04, M05, M07, M09, M15):** muito alta. É o caminho mais barato para "integração com HA apenas via protocolos públicos", com entidades sintéticas que carregam source_type, evidence_level e validation_status e disponibilidade honesta. Vitais e queda ficam desabilitados ou rotulados como não diagnósticos.

#### HC-15 — Blueprints de automação do HA e dashboards Lovelace de exemplo

- **O que faz:** oito blueprints (sofrimento, dormindo, saída da cama, inatividade, reunião, banheiro, risco de queda, armar segurança), três dashboards Lovelace (cômodo, grade multi-nó, visão AAL) e três blueprints BFLD.
- **Como faz:** YAML declarativo com entradas selecionáveis e validação estrutural no CI (construtores inertes para tags especiais).
- **Requisitos para implementar:**
  - Hardware: instância HA.
  - Software: Home Assistant, PyYAML.
  - Dados: entidades MQTT.
  - Competências: automações no HA.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNIT_TESTS_ONLY`. A validação é só sintática. **Três blueprints dependem de primitivas não anunciadas**, vários leem um atributo não publicado e o README do Lovelace diverge na contagem de entidades. Caminhos: `examples/ha-blueprints/README.md`, `examples/ha-blueprints/01-notify-on-possible-distress.yaml`, `examples/lovelace/03-healthcare-aal-view.yaml`, `v2/crates/cog-ha-matter/blueprints/bfld/`, `scripts/validate-ha-blueprints.py`.
- **Riscos/limitações:** automações mortas. Casos clínicos.
- **Relevância para a plataforma (M13, M01, M02, M07, M09):** média. Blueprints próprios ligados só às entidades que a plataforma publica, com validação no CI e, se possível, num container HA. Rotular como demonstração sintética. Ver também UI-15.

#### HC-16 — cog-ha-matter: pacote "cog" instalável no appliance Seed (mDNS, manifest, publisher MQTT; Matter adiado)

- **O que faz:** empacota o publisher MQTT como artefato instalável, com anúncio mDNS para o HA descobrir o broker, manifest com URL, SHA-256 e assinatura, CLI com privacidade e pipeline de build, assinatura e upload.
- **Como faz:** builders puros, client-id único por processo, registro mDNS com chaves travadas por teste e "goodbye" ao encerrar.
- **Requisitos para implementar:**
  - Hardware: appliance ou Linux.
  - Software: mdns-sd (no alvo: zeroconf), gcloud para publicação.
  - Dados: snapshots (não conectados).
  - Competências: distribuição de binários.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 25 testes de cog (mais 43 de witness, ver HC-17). **O publisher sobe sem fonte: o canal nunca recebe dados.** A documentação promete broker embutido, limiares aprendidos, federação e OTA, nada implementado. Matter adiado. A etapa de assinatura no Makefile é no-op. Caminhos: `v2/crates/cog-ha-matter/src/main.rs`, `runtime.rs`, `mdns.rs`, `manifest.rs`, `cog/Makefile`, `docs/adr/ADR-116-cog-ha-matter-seed.md`.
- **Riscos/limitações:** não entrega estado ao HA. Nuvem paga para distribuição.
- **Relevância para a plataforma (M13, M15):** baixa como produto. Média como padrão (mDNS via zeroconf, manifest com hash e assinatura, distribuição por GitHub Releases). Matter fica BLOCKED.

#### HC-17 — Cadeia de testemunhas (witness chain): log append-only por hash encadeado + assinatura Ed25519

- **O que faz:** registra cada transição num log que evidencia adulteração (sequência, timestamp, tipo, payload, hash do anterior).
- **Como faz:** SHA-256 sobre bytes canônicos a partir de uma gênese fixa, com append como único mutador e JSONL validado. **A assinatura Ed25519 cobre os mesmos bytes canônicos**, o que impede "transplantar" um evento para outra posição. Cadeia e assinatura ficam separadas, para que a rotação de chave invalide assinaturas, não a cadeia.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: hashlib, PyNaCl/cryptography.
  - Dados: eventos de auditoria.
  - Competências: logs de auditoria.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 43 testes (32 da cadeia e 11 da assinatura). **Não é usada pelo binário nem pelo HOMECORE.** Gestão de chaves fora de escopo. Caminhos: `v2/crates/cog-ha-matter/src/witness.rs`, `witness_signing.rs`.
- **Riscos/limitações:** sem âncora externa (quem tem a chave reescreve tudo).
- **Relevância para a plataforma (M15):** alta. Tabela SQLite append-only com hash encadeado e Ed25519 opcional, mais endpoint de verificação de integridade. Ver também GV-02.

#### HC-18 — Ponte de LiDAR do iPhone (ARKit sceneDepth → quadro compacto → relay WebSocket → nuvem de pontos no navegador)

- **O que faz:** usa um iPhone ou iPad com LiDAR como sensor de geometria (profundidade, confiança, intrínsecos, pose; **sem RGB**), com relay Node e visualizador web.
- **Como faz:** o app SwiftUI reduz a resolução e codifica a profundidade em inteiro de 16 bits mais confiança, com limite de FPS. O relay exige um token efêmero comparado em tempo constante, serve uma lista fixa de arquivos e limita mensagens. O codec do navegador valida tudo antes de projetar. A proveniência é rotulada "só geometria".
- **Requisitos para implementar:**
  - Hardware: iPhone/iPad Pro com LiDAR, Mac com Xcode.
  - Software: iOS 17+, Node 20+.
  - Dados: profundidade do ambiente.
  - Competências: ARKit, geometria de câmera.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes Node marcados MEASURED e type-check Swift no CI. **Captura física, latência e banda não foram medidas** (estimativas SYNTHETIC). Caminhos: `integrations/iphone-lidar/README.md`, `native/RuViewLiDAR/LiDARCaptureManager.swift`, `web/codec.mjs`, `web/relay.mjs`, `web/codec.test.mjs`, `.github/workflows/iphone-lidar.yml`.
- **Riscos/limitações:** **token na query string e `ws://` sem TLS** (aceitável só em dev, e proibido pelas regras da plataforma).
- **Relevância para a plataforma (M14, M16):** média e futura (mapeamento de cômodos e posicionamento), PLANNED/NOT_TESTED. O codec validado com proveniência "sem RGB" é reaproveitável; corrigir o antipadrão do token.

#### HC-19 — Adaptador "virtual-view" (protótipo de pesquisa, desabilitado por padrão, sem atuação)

- **O que faz:** ponte opcional com um "broker" de outro repositório que renderiza vistas virtuais de cenas métricas e devolve uma decisão (renderizar, pular, bloquear), sempre sem autoridade.
- **Como faz:** valida a estrutura do snapshot como JSON simples por descritores, rejeitando proxies, getters, protótipos, não finitos, arrays esparsos e ciclos, com limites de profundidade, nós e tamanho e **sem executar código da entrada**. Exige schema de cena e referencial. Vem desabilitado e o objeto retornado é congelado.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Node 20+, repositório companheiro.
  - Dados: snapshots.
  - Competências: validação defensiva em JS.
- **Evidência e maturidade:** `RESEARCH` / `UNIT_TESTS_ONLY`. 11 testes no CI. O README proíbe uso em controle real. Caminhos: `integrations/virtual-view/README.md`, `adapter.mjs`, `adapter.test.mjs`.
- **Riscos/limitações:** depende de outro repositório.
- **Relevância para a plataforma (M14):** baixa. A validação estrutural defensiva serve de referência para os validadores Zod e Pydantic.

#### HC-20 — Metaharness "homecore" para desenvolvedores (CLI npm + servidor MCP somente leitura + adaptadores de agentes)

- **O que faz:** pacote npm que mapeia capacidades a fontes e comandos de validação, diagnostica o ambiente, roda perfis de teste numa cópia confiável e expõe um servidor MCP stdio somente leitura com um "brain" revisado.
- **Como faz:** política MCP que nega por padrão (só leitura) e limita bytes, fila, duração e chamadas. Confiança ancorada no checkout encontrado na partida. Redação de segredos. Execuções que escrevem exigem duas confirmações. Manifest SHA-256.
- **Requisitos para implementar:**
  - Hardware: estação de desenvolvimento.
  - Software: Node 20+.
  - Dados: corpus revisado.
  - Competências: segurança de ferramentas para agentes.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. 7 arquivos de teste mais smoke no CI. Depende de um kernel WASM externo não auditado. Caminhos: `harness/homecore/README.md`, `src/mcp-server.js`, `src/policy.js`, `src/redact.js`, `src/repo-trust.js`, `.harness/mcp-policy.json`, `docs/adr/ADR-285-homecore-wasm-first-metaharness.md`.
- **Riscos/limitações:** superfície de injeção via conteúdo do repositório.
- **Relevância para a plataforma (NONE):** baixa para o produto e média para o processo (MCP local somente leitura com nega-por-padrão). Ver também OP-01 a OP-03.

### 4.10 Interfaces: UI web, dashboard, observatório, desktop, mobile e exemplos

**Escopo.** São pelo menos sete superfícies com stacks diferentes:

- SPA em JavaScript puro (`ui/`);
- páginas 3D experimentais (observatório, pose-fusion, `viz.html`);
- dashboard Vite + Lit + Signals para o simulador nvsim;
- desktop Tauri v2 + React;
- app Expo/React Native;
- exemplos: HOMECORE em Lit, blueprints, dashboards Python, treinador WiFlow, three.js e pesquisa;
- ativos de design.

As partes mais maduras são a máquina de proveniência com banner, os tickets de WebSocket e o service worker com allowlist, todos testados em CI. **Não há pacote de contrato compartilhado**: cada stack redefine os tipos do stream.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| UI-01 | SPA web de operação (`ui/`) com abas | PARTIAL | UNIT_TESTS_ONLY | M01, M02, M11, M16 |
| UI-02 | Máquina de estados de proveniência do stream e banner global | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16, M01 |
| UI-03 | Tickets de WebSocket de uso único e service worker com allowlist | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15 |
| UI-04 | Visualização 3D de campo de sinal e cena de sala (Three.js) | IMPLEMENTED_UNTESTED | NONE | M01, M08, M11 |
| UI-05 | Renderização de pose 2D e console Live Demo | IMPLEMENTED_UNTESTED | NONE | M11, M02, M16 |
| UI-06 | Painéis de laboratório de modelos (gravação, treino, LoRA, modelos) | IMPLEMENTED_UNTESTED | NONE | M12, M15 |
| UI-07 | Kit de UX operacional (paleta, atalhos, onboarding, i18n, export) | IMPLEMENTED_UNTESTED | NONE | M16, M15 |
| UI-08 | Observatório: cena 3D cinematográfica de cenários sintéticos | PARTIAL | SYNTHETIC_OR_SIMULATED | M01, M02, M04, M05, M06, M07, M09 |
| UI-09 | Pose-fusion: demo dual-modal câmera + CSI | RESEARCH | SYNTHETIC_OR_SIMULATED | M11, M14 |
| UI-10 | Dashboard nvsim (Lit + Signals, WASM em Worker, witness) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15, M12 |
| UI-11 | Edge App Store: catálogo com rótulos honestos de runtime | PARTIAL | SYNTHETIC_OR_SIMULATED | M13, M12, M15 |
| UI-12 | RuView Desktop (Tauri v2 + React) para frota ESP32 | PARTIAL | UNIT_TESTS_ONLY | M16, M13 |
| UI-13 | App móvel Expo/React Native | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M02, M04, M05, M16 |
| UI-14 | Frontend HOMECORE (Lit) e recon de design system | PARTIAL | UNIT_TESTS_ONLY | M13 |
| UI-15 | Integração HA: blueprints e dashboards Lovelace | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15, M07, M09, M03 |
| UI-16 | Dashboards de terminal e exemplos de sinais vitais (Python via serial) | IMPLEMENTED_UNTESTED | UNCLEAR | M04, M05, M09, M10, M08, M02 |
| UI-17 | WiFlow: treinador CSI→pose supervisionado por câmera no navegador | RESEARCH | UNCLEAR | M11, M12, M15, M16 |
| UI-18 | Demos three.js e ponte serial→WebSocket | RESEARCH | NONE | M11, M14 |
| UI-19 | Exemplos de pesquisa: física sintética SOTA e "happiness vector" | RESEARCH | SYNTHETIC_OR_SIMULATED | M08, M02, M16, M15, M14 |
| UI-20 | Design systems e ativos visuais de documentação | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | NONE |

#### UI-01 — SPA web de operação (`ui/`) com navegação por abas

- **O que faz:** painel servido pelo servidor com as abas Dashboard (saúde, recursos, estatísticas de pose, ocupação por zona), Hardware, Live Demo, Sensing, Training e abas estáticas (Architecture, Performance, Applications).
- **Como faz:** ES modules sem bundler, orquestrador com gerenciador de abas, serviços finos de REST e WS com interceptors, detecção de backend (servidor, legado Python ou mock desativado), import dinâmico isolando falhas de painéis e polling de saúde.
- **Requisitos para implementar:**
  - Hardware: nenhum para a UI.
  - Software: navegador, servidor estático.
  - Dados: stream no formato de update do servidor.
  - Competências: front-end JS, WebSocket, Canvas.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Só 4 testes de reidratação de saúde rodam no CI. O relatório de testes é autodeclarado. **A aba Hardware gera CSI aleatório.** **As abas de desempenho exibem métricas de literatura fixas no HTML.** Caminhos: `ui/index.html`, `ui/app.js`, `ui/components/TabManager.js`, `ui/components/DashboardTab.js`, `ui/components/DashboardTab.test.mjs`, `ui/components/HardwareTab.js`, `ui/services/api.service.js`, `ui/utils/backend-detector.js`, `ui/TEST_REPORT.md`.
- **Riscos/limitações:** sem validação de contrato no cliente. Métricas fixas passam por resultados. Imagem de CDN de terceiros.
- **Relevância para a plataforma (M01, M02, M11, M16):** alta como arquitetura de informação (abas por domínio, carga preguiçosa isolando falhas). Reimplementar em rotas do Next.js com Zod e sem métricas fixas.

#### UI-02 — Máquina de estados de proveniência do stream e banner global de fonte de dados

- **O que faz:** classifica a origem do que está na tela: ao vivo (hardware), simulado pelo servidor, reconectando (congelado), inalcançável, simulado pelo navegador ou autenticação exigida. **Uma barra fixa aparece em todas as abas só quando o dado não é confiável.** A simulação no cliente fica **desligada por padrão**.
- **Como faz:** backoff exponencial com teto, separação entre estado de conexão e estado de fonte de dados, leitura do campo de origem do servidor e descarte de tentativas superadas. Uma sonda HTTP descobre se o fechamento foi por falta de token e, nesse caso, para de tentar. Frames sintéticos levam marcador.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: navegador; servidor que declare a origem por frame.
  - Dados: campo de proveniência.
  - Competências: máquinas de estado, UX de confiabilidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes de token ausente e rejeitado, queda com reconexão e saída do estado de autenticação, rodando no CI. O comentário do serviço registra que a simulação no cliente já causou um diagnóstico errado. Caminhos: `ui/services/sensing.service.js`, `ui/services/sensing.service.test.mjs`, `ui/utils/data-source-banner.js`, `ui/utils/connection-status.js`.
- **Riscos/limitações:** **a política diverge entre frontends** (mobile e observatório caem para demo automaticamente).
- **Relevância para a plataforma (M15, M16, M01):** muito alta. Um componente global de proveniência no layout Next.js alimentado por source_type, evidence_level e validation_status, com proibição explícita de geração sintética no navegador. Ver também SS-02.

#### UI-03 — Fronteira de segurança do cliente web: tickets de WebSocket de uso único e service worker com allowlist

- **O que faz:** antes de abrir o WS, troca o token por um ticket curto de uso único (o construtor de WebSocket não aceita cabeçalho Authorization). Remove tokens acidentais da query e mantém compatibilidade com servidores antigos. O service worker faz cache-first só de assets numa allowlist, manda a API para a rede sem gravar resposta, devolve 503 offline em vez de dado velho, nunca intercepta rotas de credencial, purga o cache de API no logout e versiona o cache.
- **Como faz:** um ticket por tentativa, nunca reutilizado. 401/403 rejeitam o token; 5xx não quebram a conexão. Estratégias por classe de requisição, ignorando não-GET, upgrades e cross-origin.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: endpoint de ticket com TTL; Serwist (MIT) se houver PWA.
  - Dados: nenhum.
  - Competências: segurança web (auth de WS, Cache API, XSS).
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 17 testes de ticket, 4 do serviço WS e cerca de 13 do service worker, no CI. ADRs aceitas. **O token de longa duração fica em `localStorage`** (painel de configurações), o que contraria a regra da plataforma. Caminhos: `ui/services/ws-ticket.js`, `ui/services/ws-ticket.test.mjs`, `ui/services/websocket.service.js`, `ui/sw.js`, `ui/sw.test.mjs`, `ui/utils/quick-settings.js`, `docs/adr/ADR-272-websocket-authentication-tickets.md`.
- **Riscos/limitações:** exposição a XSS. Ticket na URL vai para logs de proxy (mitigado por TTL curto e uso único).
- **Relevância para a plataforma (M15):** alta. Ticket efêmero no FastAPI, mantendo o `SPATIAL_TOKEN` só em memória ou em cookie HttpOnly, nunca em storage ou URL. Ver também GV-13.

#### UI-04 — Visualização 3D de campo de sinal e cena de sala (Three.js)

- **O que faz:** "Gaussian splats" de campo (tamanho = variância, cor = quieto/presença/movimento, opacidade = confiança) e uma cena com corpo de 24 partes, sala, zonas, heatmap e visualizações de amplitude, fase, Doppler e energia, com HUD.
- **Como faz:** Three.js de CDN, shader customizado e OrbitControls. Nenhum DSP no cliente.
- **Requisitos para implementar:**
  - Hardware: GPU com WebGL.
  - Software: react-three-fiber/drei, deck.gl (MIT).
  - Dados: features e grade 3D.
  - Competências: WebGL.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `NONE`. Sem testes. Caminhos: `ui/components/gaussian-splats.js`, `ui/viz.html`, `ui/components/scene.js`, `body-model.js`, `environment.js`, `signal-viz.js`.
- **Riscos/limitações:** pode sugerir precisão espacial inexistente. Depende de CDN.
- **Relevância para a plataforma (M01, M08, M11):** média. Planta baixa e heatmap sintéticos com selo L0, evitando avatares de corpo enquanto M11 estiver BLOCKED.

#### UI-05 — Renderização de pose 2D e console Live Demo

- **O que faz:** canvas com modos esqueleto, keypoints, "heatmap" e "dense" (aproximações por regiões, não DensePose UV), overlay de zonas, start/stop, badge do modo de estimativa, **guia de capacidades esperadas por quantidade de nós** e configurações exportáveis.
- **Como faz:** renderer 2D com limiar de confiança e medição de FPS.
- **Requisitos para implementar:**
  - Hardware: vários nós e modelo treinado para pose real.
  - Software: navegador.
  - Dados: keypoints COCO-17.
  - Competências: Canvas e UX de tempo real.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `NONE`. Sem testes. Caminhos: `ui/components/PoseDetectionCanvas.js`, `ui/utils/pose-renderer.js`, `ui/components/LiveDemoTab.js`, `ui/services/pose.service.js`, `ui/components/SettingsPanel.js`.
- **Riscos/limitações:** os modos "dense" e "heatmap" podem ser confundidos com DensePose.
- **Relevância para a plataforma (M11, M02, M16):** baixa a média. O "guia de capacidades por número de nós" é uma boa prática de expectativa honesta para M16.

#### UI-06 — Painéis de laboratório de modelos (gravação, treino, pré-treino, LoRA e gestão de modelos)

- **O que faz:** UI para gravações, treino, pré-treino e adaptação, progresso em gráficos e gestão de modelos e perfis.
- **Como faz:** serviços REST finos sobre endpoints que exigem escopos, com carga dinâmica.
- **Requisitos para implementar:**
  - Hardware: captura real e CPU/GPU.
  - Software: no alvo, MLflow (Apache-2.0) local.
  - Dados: gravações rotuladas.
  - Competências: MLOps.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `NONE`. Sem testes de frontend. Caminhos: `ui/components/TrainingPanel.js`, `ui/components/ModelPanel.js`, `ui/services/training.service.js`, `ui/services/model.service.js`.
- **Riscos/limitações:** permite ativar modelos sem gate de evidência visível. Operações destrutivas acessíveis.
- **Relevância para a plataforma (M12, M15):** baixa no curto prazo. Inspira um Model Lab governado com gates obrigatórios antes de ativar. Ver também SS-09 e SS-10.

#### UI-07 — Kit de UX operacional (utilitários transversais da UI)

- **O que faz:** paleta de comandos com busca fuzzy, atalhos, tour de onboarding, central de notificações, toasts, i18n EN/PL, tema, gerenciador de inatividade (pausa animações e polling), monitor de desempenho, captura de tela, exportação JSON/CSV, configurações rápidas, navegação mobile, roteador por hash e log de atividade.
- **Como faz:** módulos independentes comunicando-se por eventos DOM e persistência leve no navegador.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: cmdk (MIT), next-intl (MIT), driver.js (MIT).
  - Dados: nenhum.
  - Competências: UX e acessibilidade.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `NONE`. Sem testes. **A exportação não carrega metadados de proveniência.** Caminhos: `ui/utils/command-palette.js`, `keyboard-shortcuts.js`, `onboarding.js`, `i18n.js`, `idle-manager.js`, `data-export.js`, `quick-settings.js`.
- **Riscos/limitações:** token em `localStorage`. i18n limitada.
- **Relevância para a plataforma (M16, M15):** alta e barata. Paleta, i18n pt-BR/EN, tour e exportação CSV/JSON **com cabeçalho de proveniência e hash**. Pausar polling na inatividade reduz a carga.

#### UI-08 — Observatório: cena 3D cinematográfica de cenários sintéticos

- **O que faz:** cena imersiva com até 4 figuras wireframe e vários tipos de pose, props, partículas, ondas, pós-processamento, HUD e 12 cenários (vazio, respiração, dois andando, queda, sono, intrusão, gesto, multidão, resgate, idosos, fitness, patrulha) com crossfade. Tenta detectar servidor ao vivo e cai para demo.
- **Como faz:** gerador sintético compatível com o contrato, com **PRNG semeado por cenário**, ruído temporalmente correlacionado (branco filtrado por IIR), campos espacialmente coerentes e padrões comportamentais por cenário.
- **Requisitos para implementar:**
  - Hardware: GPU.
  - Software: Three.js r160.
  - Dados: gerador ou stream.
  - Competências: modelagem de sinais sintéticos, design de movimento.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. **Seis módulos de painel são órfãos** (não importados). Sem testes. O gerador chama de "fisiologicamente acurados" vitais que são sintéticos. Caminhos: `ui/observatory.html`, `ui/observatory/js/main.js`, `demo-data.js`, `figure-pool.js`, `pose-system.js`, `hud-controller.js`.
- **Riscos/limitações:** estética confundível com medição. Fallback automático para demo.
- **Relevância para a plataforma (M01, M02, M04, M05, M06, M07, M09):** alta como inspiração para o motor sintético: catálogo de cenários determinísticos com semente, ruído correlacionado e transições suaves, implementados no backend (numpy) e só visualizados no Next.js, sempre L0.

#### UI-09 — Pose-fusion: demo dual-modal câmera + CSI no navegador

- **O que faz:** modos dual, só vídeo e só CSI. Detecta movimento na webcam, gera CSI simulado correlacionado ao vídeo (ou recebe via WS), extrai embeddings com CNN e atenção, funde com gating de confiança e decodifica 17 keypoints com extensões.
- **Como faz:** diferença entre quadros vira grade de movimento, com heurística de partes. **A CNN tem pesos aleatórios semeados, sem treino.** A atenção vem de um pacote WASM vendorizado. Confiança de vídeo por brilho e movimento.
- **Requisitos para implementar:**
  - Hardware: webcam.
  - Software: WASM, wasm-pack.
  - Dados: vídeo e CSI.
  - Competências: visão, fusão multimodal.
- **Evidência e maturidade:** `RESEARCH` / `SYNTHETIC_OR_SIMULATED`. Sem testes. **No modo demo, o CSI é sintetizado a partir do próprio vídeo**, então não demonstra contribuição do WiFi. Binários WASM commitados. Caminhos: `ui/pose-fusion.html`, `ui/pose-fusion/js/fusion-engine.js`, `cnn-embedder.js`, `pose-decoder.js`, `csi-simulator.js`, `ui/pose-fusion/pkg/`.
- **Riscos/limitações:** a câmera captura biometria. Pode induzir a crer em pose por WiFi.
- **Relevância para a plataforma (M11, M14):** baixa. O gating de confiança por modalidade fica só como referência conceitual para M14.

#### UI-10 — Dashboard nvsim (Vite + Lit + Signals) com WASM em Web Worker e witness de determinismo

- **O que faz:** painel do simulador de magnetometria com cena SVG arrastável, inspector, console com REPL, paleta, onboarding, ajuda, configurações (transporte WASM ou WS), HUD, PWA e uma view de pesquisa especulativa.
- **Como faz:** web components Lit com store reativa. **Uma interface de cliente comum (WASM local ou WS) desacopla o dashboard do transporte.** Worker com RPC e ArrayBuffers transferíveis. **Witness SHA-256 sobre N quadros contra um hash esperado como gate de determinismo.** IndexedDB, precache workbox, COOP/COEP e GitHub Pages.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Lit (BSD-3), signals-core (MIT), workbox (MIT), Playwright, axe-core.
  - Dados: cena e semente.
  - Competências: web components, Workers/WASM, acessibilidade.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. **Gate Playwright + axe-core (WCAG 2 A/AA) em 6 views no CI**, com zero violações críticas ou sérias. Não foram encontrados testes unitários. A ADR declara 8 de 12 gates OK. Caminhos: `dashboard/src/main.ts`, `dashboard/src/transport/NvsimClient.ts`, `WasmClient.ts`, `WsClient.ts`, `worker.ts`, `dashboard/src/store/appStore.ts`, `dashboard/tests/a11y.spec.ts`, `.github/workflows/dashboard-a11y.yml`, `docs/adr/ADR-092-nvsim-dashboard-implementation.md`.
- **Riscos/limitações:** domínio sem relação com WiFi. View especulativa sobre vigilância. Fontes por CDN.
- **Relevância para a plataforma (M15, M12):** alta pelos padrões: transporte abstrato no frontend e witness SHA-256 de lotes do gerador semeado guardado como evidência. Ver também ML-20.

#### UI-11 — Edge App Store: catálogo de módulos com rótulos honestos de runtime

- **O que faz:** catálogo de 66 entradas por categoria (faixas de IDs de evento), com maturidade (disponível, beta, pesquisa), orçamento S/M/L, tags, ADR e toggle. **O runtime é explícito**: executando no navegador, simulado (proxy reduzido) ou só em malha.
- **Como faz:** registro estático tipado. Runtimes simulados recebem o último quadro e decidem eventos ilustrativos.
- **Requisitos para implementar:**
  - Hardware: malha ESP32 para execução real.
  - Software: Lit.
  - Dados: CSI.
  - Competências: governança de catálogo.
- **Evidência e maturidade:** `PARTIAL` / `SYNTHETIC_OR_SIMULATED`. **1 entrada roda de fato, 6 rodam simuladas, 1 é só em malha**; as demais não têm runtime. Ainda assim, 35 aparecem como "disponível". O código admite que o proxy é outra modalidade física. Caminhos: `dashboard/src/store/apps.ts`, `dashboard/src/store/appRuntimes.ts`, `dashboard/src/components/nv-app-store.ts`.
- **Riscos/limitações:** "disponível" convive com execução inexistente. Categorias especulativas.
- **Relevância para a plataforma (M13, M12, M15):** média-alta como governança: catálogo de capacidades versionado com estado explícito (IMPLEMENTED_SYNTHETIC, PLANNED, BLOCKED), exibido no Next.js.

#### UI-12 — RuView Desktop (Tauri v2 + React) para gestão de frota ESP32

- **O que faz:** Dashboard, Nós, Flash (assistente em 3 passos), OTA (unitária e em lote), Edge Modules (upload, estatísticas, biblioteca), Sensing (servidor, log, feed), Mesh View (grafo force-directed), Descoberta de rede e Configurações.
- **Como faz:** comandos IPC em Rust. Descoberta por mDNS e beacon UDP, heurística de VID/PID para portas, flash via espflash, OTA multipart com HMAC-SHA256 do hash por PSK com semáforo, checagem de identificador WASM, servidor como processo filho e provisionamento NVS por serial.
- **Requisitos para implementar:**
  - Hardware: ESP32 via USB.
  - Software: Tauri v2 (MIT/Apache), Node 20+, WebView2, espflash.
  - Dados: firmwares, módulos, PSK.
  - Competências: Rust, Tauri, OTA.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 45 testes Rust, **vários reimplementando a lógica no próprio teste ou só checando o tamanho de hash**. O README diz "Work in Progress", e o release Windows é debug build dependente do Vite. A verificação de firmware não faz readback. O provisionamento não é chamado pela UI. **A biblioteca de módulos tem avaliações e downloads fictícios.** Caminhos: `v2/crates/wifi-densepose-desktop/README.md`, `src/commands/discovery.rs`, `flash.rs`, `ota.rs`, `wasm.rs`, `provision.rs`, `tests/api_integration.rs`, `ui/src/pages/EdgeModules.tsx`, `.github/workflows/desktop-release.yml`.
- **Riscos/limitações:** PSK e credenciais em texto. Métricas falsas de marketplace. Artefatos de build commitados.
- **Relevância para a plataforma (M16, M13):** média-baixa agora (sem hardware). O fluxo descobrir → provisionar → verificar → monitorar como assistente web com nós sintéticos. Desktop fica para depois, com segredos no keychain do SO.

#### UI-13 — App móvel Expo/React Native (iOS, Android, Web)

- **O que faz:** telas Live (splats em WebView), Vitals (gauges e sparklines), Zones (planta SVG com ocupação), MAT (triagem START) e Settings (URL validada, tema, modo RSSI). **Cai para simulação automaticamente.** RSSI nativo no Android; stub no iOS e na Web.
- **Como faz:** Expo SDK 55, React Navigation, zustand persistido, axios, WS com backoff, ponte WebView por postMessage, ring buffer e validador de URL por protocolos permitidos.
- **Requisitos para implementar:**
  - Hardware: smartphone.
  - Software: Expo e React Native (MIT).
  - Dados: stream.
  - Competências: React Native.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 211 casos Jest **fora de qualquer workflow de CI**. **Os 6 fluxos Maestro têm 0 bytes.** Screenshot placeholder. Caminhos: `ui/mobile/package.json`, `ui/mobile/README.md`, `src/services/ws.service.ts`, `src/services/simulation.service.ts`, `src/services/rssi.service.android.ts`, `src/services/rssi.service.ios.ts`, `src/screens/MATScreen/index.tsx`, `src/utils/urlValidator.ts`, `ui/mobile/e2e/`.
- **Riscos/limitações:** contradiz a política opt-in de simulação. Marketing "através de paredes pelo celular" sem sustentação. A tela MAT é de alto risco.
- **Relevância para a plataforma (M01, M02, M04, M05, M16):** baixa a média. Uma PWA responsiva no Next.js é mais barata que app nativo.

#### UI-14 — Frontend HOMECORE (exemplo Lit) e recon de design system

- **O que faz:** UI no estilo HA para estados, serviços e configurações, com cliente REST + WS que espelha o handshake do HA, tokens de design (só escuro) e ícones Lucide.
- **Como faz:** custom elements Lit e proxy do Vite. **Os tokens vieram de um recon de navegador sobre um dashboard de appliance de terceiros.**
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Lit, Vite, Lucide (ISC).
  - Dados: entidades.
  - Competências: protocolo WS do HA.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 11 casos Vitest fora do CI. **O token é lido de `localStorage`, da query `?token=` ou de meta tag, com um token literal de desenvolvimento como fallback.** Caminhos: `examples/frontend/README.md`, `src/api/client.ts`, `src/components/StateCard.ts`, `src/styles/tokens.css`, `docs/design/HOMECORE-FRONTEND-design-recon.md`.
- **Riscos/limitações:** risco de trade dress ao copiar a identidade visual de terceiros.
- **Relevância para a plataforma (M13):** média. O modelo entidade/estado/serviço serve ao M13. Nunca token em URL e nunca copiar tokens visuais de terceiros.

#### UI-15 — Integração com Home Assistant: blueprints de automação e dashboards Lovelace

- **O que faz:** os mesmos 8 blueprints e 3 dashboards de HC-15, vistos do lado das interfaces, com uma tabela de compatibilidade com o modo de privacidade (estados inferidos continuam sendo publicados; biometria bruta é suprimida).
- **Como faz:** YAML com selectors e um validador Python seguro no CI.
- **Requisitos para implementar:**
  - Hardware: servidor HA.
  - Software: HA, Mosquitto, cliente MQTT.
  - Dados: entidades de primitivas.
  - Competências: automação residencial.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. O validador roda no CI (sintático). Caminhos: `examples/ha-blueprints/`, `examples/lovelace/`, `scripts/validate-ha-blueprints.py`, `.github/workflows/mqtt-integration.yml`.
- **Riscos/limitações:** primitivas de saúde não validadas dão falsa segurança. Armar segurança por inatividade pode falhar.
- **Relevância para a plataforma (M13, M15, M07, M09, M03):** alta. Discovery MQTT de estados sintéticos rotulados, com o princípio "privacidade publica só estados inferidos, nunca biometria". Ver HC-14 e HC-15.

#### UI-16 — Dashboards de terminal e exemplos de sinais vitais (Python via serial)

- **O que faz:** painéis de terminal: unificado CSI + radar + luz (FC, FR, "pressão estimada", estresse, presença); monitor de sala com fingerprint e drift (portas e janelas); estimador de tendência de pressão; suíte de 10 capacidades (incluindo sono, apneia, tosse, ronco, meditação); triagem de apneia com índice tipo AHI; e estresse por HRV.
- **Como faz:** regex sobre logs seriais, Welford, z-score, passa-banda e cruzamentos por zero, com aviso de "não é dispositivo médico".
- **Requisitos para implementar:**
  - Hardware: ESP32-S3 e ESP32-C6 com radar 60 GHz.
  - Software: pyserial, numpy.
  - Dados: logs; referência para calibrar pressão.
  - Competências: sinais fisiológicos e metrologia clínica.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNCLEAR`. O README mostra "saída de exemplo de hardware real" sem log. Sem testes. **O próprio repositório conclui, em resultados negativos, que pressão arterial sem contato via CSI é fisicamente inviável.** A "HRV" é calculada sobre a série de FC reportada, não sobre intervalos batimento a batimento. Caminhos: `examples/ruview_live.py`, `examples/environment/room_monitor.py`, `examples/medical/bp_estimator.py`, `examples/medical/vitals_suite.py`, `examples/sleep/apnea_screener.py`, `examples/stress/hrv_stress_monitor.py`.
- **Riscos/limitações:** risco regulatório e de dano. Parsing frágil.
- **Relevância para a plataforma (M04, M05, M09, M10, M08, M02):** baixa para implementar (M04/M05/M09/M10 BLOCKED). Serve como lista do que não prometer e como exemplo de painel TUI (Rich/Textual) sobre dados sintéticos.

#### UI-17 — WiFlow: treinador CSI→pose supervisionado por câmera no navegador (com pipeline Python e A/B de vazamento)

- **O que faz:** página com quatro estágios bloqueados em sequência: calibrar (baseline de sala vazia), capturar (pares keypoints de câmera + CSI normalizado, com rotina guiada e cobertura por pose), treinar (MLP no navegador com PCK, MPJPE e **baseline de pose média obrigatório**, com veredito) e inferir (só CSI). O status é estrito (ao vivo, simulado, sem servidor CSI). Há versões Python e um script A/B que compara splits cronológico, aleatório e bloco com gap.
- **Como faz:** rótulos por MediaPipe Pose. TensorFlow.js seleciona o backend (WebGPU, depois WASM-SIMD, depois WebGL) e mostra um badge. IndexedDB, Welford e validação cronológica.
- **Requisitos para implementar:**
  - Hardware: webcam e 2+ ESP32-S3.
  - Software: TensorFlow.js (Apache-2.0), MediaPipe, PyTorch.
  - Dados: milhares de pares de uma pessoa e uma sala.
  - Competências: avaliação sem vazamento.
- **Evidência e maturidade:** `RESEARCH` / `UNCLEAR`. O README alega um ganho de cerca de 9 p.p. de PCK sobre o baseline, sem dataset nem log. **O script A/B reconhece que o split cronológico vaza por autocorrelação e que o ganho pode ser vazamento temporal.** Não há validação entre dias, salas ou através de parede, apesar do nome da pasta. Caminhos: `examples/through-wall/README.md`, `wiflow_browser.html`, `wiflow_capture.py`, `wiflow_train.py`, `wiflow_ab.py`, `docs/adr/ADR-079-camera-ground-truth-training.md`.
- **Riscos/limitações:** ganho pequeno e possivelmente vazado. Biometria por câmera. Nome enganoso.
- **Relevância para a plataforma (M11, M12, M15, M16):** média como metodologia: baseline obrigatório, split com gap, gates entre etapas e badge honesto de backend. A captura fica BLOCKED.

#### UI-18 — Demos three.js e ponte serial→WebSocket

- **O que faz:** seis demos progressivas (nuvem de pontos, câmera cinematográfica com pseudo-CSI, malha skinned, avatar FBX, webcam → MediaPipe → retarget IK com overlay ESP32, janela off-axis via WASM), além de um servidor estático e de uma ponte que lê logs do firmware e publica métricas por WS.
- **Como faz:** HTML autocontido com three.js e MediaPipe de CDN. A ponte asyncio normaliza métricas e **sintetiza a amplitude exibida**.
- **Requisitos para implementar:**
  - Hardware: webcam, GPU, ESP32 opcional.
  - Software: three.js, MediaPipe, websockets (BSD).
  - Dados: avatar obtido pelo usuário.
  - Competências: animação 3D, IK.
- **Evidência e maturidade:** `RESEARCH` / `NONE`. Só screenshots. **O esqueleto vem da câmera, não do WiFi.** Uma referência de ADR não confere com o conteúdo. Caminhos: `examples/three.js/README.md`, `demos/05-skinned-realtime.html`, `demos/07-off-axis-window.html`, `server/ruvultra-csi-bridge.py`.
- **Riscos/limitações:** o asset de avatar tem termos da Adobe. Dependência de CDN.
- **Relevância para a plataforma (M11, M14):** baixa. A ponte serial → WS é padrão útil para um futuro adaptador de hardware.

#### UI-19 — Exemplos de pesquisa: física sintética SOTA e "happiness vector"

- **O que faz:** scripts numpy com resultados JSON:
  - piso físico (Cramér-Rao de ToA, zona de Fresnel, multi-espalhador);
  - busca de posicionamento de antenas;
  - saliência de subportadoras e consistência multi-enlace contra spoofing;
  - contagem e fingerprint só por RSSI (kNN);
  - re-ID entre salas e deslocamento de autovalores;
  - resultados negativos (pressão arterial sem contato);
  - verticais e fusão "quântico-clássica".

  O "happiness vector" calcula um escore de sentimento de hóspedes de hotel em 8 dimensões a partir de marcha, respiração, postura e permanência.
- **Como faz:** simulação numérica com modelos simplificados, otimização de cobertura e classificadores simples.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, scikit-learn.
  - Dados: parâmetros sintéticos.
  - Competências: propagação RF, estatística.
- **Evidência e maturidade:** `RESEARCH` / `SYNTHETIC_OR_SIMULATED`. O README admite física sintética com divergência possível de 5 a 30% no mundo real. Há JSONs de resultado e nenhum teste. Caminhos: `examples/research-sota/README.md`, `01-physics-floor/`, `02-placement/`, `04-rssi/r9_rssi_fingerprint_knn.py`, `07-negative-results/README.md`, `examples/happiness-vector/README.md`.
- **Riscos/limitações:** **o happiness vector é inferência de emoção em ambiente comercial, sem consentimento**: dado sensível pela LGPD e prática restrita por regulações de IA.
- **Relevância para a plataforma (M08, M02, M16, M15, M14):** média. Posicionamento por Fresnel e fingerprint RSSI com kNN para o planejador sintético (M16) e M08, e registro de resultados negativos (M15). **O happiness vector não deve ser adotado.**

#### UI-20 — Design systems e ativos visuais de documentação

- **O que faz:** tokens de design do desktop (tema escuro, glassmorphism, animações), tokens HOMECORE e sistema visual do README (SVGs animados só com CSS, respeito a `prefers-reduced-motion`, geração e verificação automatizadas e a regra de que **ilustração conceitual não é medição**), além de diagramas PNG sem fonte editável.
- **Como faz:** variáveis CSS, gerador e verificador Python com parser XML endurecido (rejeita DTD e entidades, limita tamanho, sem rede) e unittest em CI.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: defusedxml.
  - Dados: nenhum.
  - Competências: design tokens, parsing seguro.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. O verificador tem CI. Os PNGs são só documentação, e o diagrama de frontend mostra login e calibração inexistentes. Caminhos: `v2/crates/wifi-densepose-desktop/ui/src/design-system.css`, `docs/adr/ADR-053-ui-design-system.md`, `docs/readme-visual-system.md`, `scripts/render-readme-visuals.py`, `scripts/verify-readme-visuals.py`, `docs/archtocode-visual-overview/`.
- **Riscos/limitações:** PNGs sem fonte divergem do código. Identidades visuais concorrentes.
- **Relevância para a plataforma (NONE):** média. Diagramas como código (Mermaid, D2), tokens claro e escuro, regra "ilustração não é evidência" e verificação de assets em CI.

### 4.11 Operador de IA, MCP, CLI, plugins, verificação, benchmarks e observabilidade

**Escopo.** O núcleo da área é o pacote npm `@ruvnet/ruview` (`harness/ruview`, v0.9.2, sem dependências de runtime). Ele expõe cerca de 22 ferramentas por CLI, servidor MCP (stdio e HTTP) e SDK, todas sobre o mesmo registro com política de autoridade mínima. Em volta dele há:

- o pacote guarda-chuva `ruview`;
- o plugin para hosts de agente;
- o servidor MCP SENSE-BRIDGE (`@ruvnet/rvagent`);
- um CLI TypeScript;
- a camada de verificação (script `verify` na raiz, `prove.sh`, provas por hash, witness bundles, guardas);
- simulação QEMU/swarm, benchmarks, semconv OpenTelemetry e um stack de monitoramento legado;
- instalação e deploy, scripts de aplicações e relatórios de QE.

A harness tem cerca de 279 casos `node:test` e o rvagent cerca de 116 casos Jest. A validação é unitária ou sintética.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| OP-01 | Núcleo do operador de IA (`@ruvnet/ruview`) e pacote guarda-chuva | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15 |
| OP-02 | Política de autoridade mínima, grants e validação de argumentos | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M13, M16 |
| OP-03 | Subprocessos seguros, redação de segredos e confiança no repositório | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16 |
| OP-04 | Guardrail de honestidade de claims (claim-check) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M16, M11, M12 |
| OP-05 | Gate de avaliação de modelos (train-gate) e treino com proteção | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M12, M11, M02, M15 |
| OP-06 | Transporte MCP HTTP, console MCP Apps e UI de terminal | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15, M13 |
| OP-07 | Doctor estruturado com remediação | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16 |
| OP-08 | Acesso a dispositivos do host e a hosts remotos (somente leitura) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M02, M04, M05, M14, M16 |
| OP-09 | Flash de firmware verificado com evidência de boot | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M16 |
| OP-10 | Guidance com citação de fonte e "contributor brain" revisado | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M16, M15 |
| OP-11 | Flywheel/Darwin de políticas do agente e agente noturno de pesquisa | PARTIAL | UNIT_TESTS_ONLY | M16, M15, M12 |
| OP-12 | Integração com hosts de agente (plugin, skills, manifesto, painel) | PARTIAL | UNIT_TESTS_ONLY | M16, M15 |
| OP-13 | SENSE-BRIDGE (`@ruvnet/rvagent`) e CLI `ruview-cli` | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M02, M04, M05, M11, M12, M13, M15 |
| OP-14 | Prova determinística, witness bundles e guardas de regressão | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15, M16, M12 |
| OP-15 | Simulação de firmware em QEMU, swarm multi-nó e injeção de falhas | IMPLEMENTED_UNTESTED | SYNTHETIC_OR_SIMULATED | M16, M14 |
| OP-16 | Benchmarks e reprodução independente de claims | IMPLEMENTED_UNTESTED | UNCLEAR | M11, M12, M02, M04, M05, M15 |
| OP-17 | Observabilidade: semconv OpenTelemetry e stack de monitoramento legado | PARTIAL | UNIT_TESTS_ONLY | M15, M16, M01, M07, M04 |
| OP-18 | Instalação, build e deploy | PARTIAL | NONE | M16 |
| OP-19 | Aplicações de sensoriamento em scripts (ao vivo ou replay) | IMPLEMENTED_UNTESTED | NONE | M01, M02, M04, M05, M06, M08, M09, M10, M14 |
| OP-20 | Pontes, gateways e pipeline de dados de treino | PARTIAL | UNCLEAR | M13, M12, M11, M04, M05, M02, M16 |
| OP-21 | Adaptador de hierarquia espacial externa com projeção semântica | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M15, M02, M03, M14 |
| OP-22 | Relatórios de QE gerados por agentes e tutoriais | DOC_ONLY | NONE | M15, M16, M08, M14 |

#### OP-01 — Núcleo do operador de IA (MetaHarness `@ruvnet/ruview`) e pacote guarda-chuva `ruview`

- **O que faz:** cerca de 22 ferramentas (onboarding, verify, doctor, devices, firmware, treino, guidance, memória, spaces, kernel) expostas por CLI (verbos, saída JSON ou formatada), servidor MCP JSON-RPC 2.0 e SDK tipado. O guarda-chuva junta a harness, o metaharness Homecore e o kernel de vitais num único CLI e servidor MCP.
- **Como faz:** arquitetura registry-first. Cada ferramenta declara schema e classe de política, e CLI, MCP e SDK chamam o mesmo despachante passando a origem (CLI e SDK são confiáveis; MCP depende de grants). Todo resultado é JSON estruturado com negativa honesta (fail-closed). O guarda-chuva carrega componentes sob demanda.
- **Requisitos para implementar:**
  - Hardware: nenhum para o núcleo.
  - Software: no alvo, Typer, SDK MCP Python (MIT) e FastAPI.
  - Dados: nenhum.
  - Competências: JSON-RPC/MCP, API orientada a casos de uso.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 279 casos de teste. O CI roda test, test:security e verificação do brain. A ADR-182 ainda descreve o estado antigo. Caminhos: `harness/ruview/src/tools.js`, `cli.js`, `sdk.js`, `mcp-server.js`, `harness/ruview/package.json`, `harness/ruview-umbrella/src/index.js`, `docs/adr/ADR-182-npx-ruview-harness-via-metaharness.md`, `docs/adr/ADR-376-ruview-umbrella-npm-package.md`.
- **Riscos/limitações:** superfície grande e acoplada ao monorepo. Deriva de versões entre configurações e pacotes. Dependências de desenvolvimento com licença não verificada.
- **Relevância para a plataforma (M16, M15):** alta como padrão: um "operator harness" Python com um único registro dos casos de uso exposto como CLI, MCP e REST, com toda resposta mantendo source_type, evidence_level e validation_status.

#### OP-02 — Política de autoridade mínima, grants e validação de argumentos

- **O que faz:** classe de autoridade por ferramenta (leitura, execução, leitura de hardware, rede, externa, remota, escrita no workspace, escrita em hardware). Via MCP, exige grants concedidos pelo operador e **confirmação explícita em ações mutantes**, gera anotações MCP (readOnly, destructive, idempotent, openWorld) e valida argumentos por um subconjunto fechado de JSON Schema.
- **Como faz:** ferramenta sem política é negada. Chamada não MCP é confiável. MCP verifica, nesta ordem, grant, leitura, confirmação e classe. **Ferramentas de "plano" não aceitam confirmação**, para que um cliente somente leitura possa revisar o comando exato sem executá-lo. Hosts de agente rodam em leitura por padrão, e flags de bypass são proibidas.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Pydantic/FastAPI.
  - Dados: nenhum.
  - Competências: capabilities, least privilege.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes de política, MCP e kernel. **A política está declarada em três lugares sem verificação cruzada evidente.** Caminhos: `harness/ruview/src/policy.js`, `harness/ruview/.harness/claims.json`, `harness/ruview/.harness/mcp-policy.json`, `harness/ruview/test/policy.test.mjs`.
- **Riscos/limitações:** validador parcial. A auditoria é uma linha em stderr.
- **Relevância para a plataforma (M15, M13, M16):** muito alta. Leitura sintética livre; hooks de automação com grant e confirmação; backup e retenção como escrita confirmada; Pydantic com `extra='forbid'`.

#### OP-03 — Execução segura de subprocessos, redação de segredos e confiança no repositório

- **O que faz:** executa ferramentas externas **sem shell**, com allowlist de variáveis de ambiente, timeout, limite de saída e cancelamento. Redige segredos e confirma que o checkout é confiável antes de executar código dele.
- **Como faz:** ambiente filho limpo, argv e buffers limitados. A redação cobre variáveis sensíveis, cabeçalhos de autorização, pares chave=valor e formatos de tokens/JWT. A confiança compara o caminho real com a raiz e marcadores. A captura serial usa hex para não colidir com os padrões.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: subprocess, `logging.Filter`, re.
  - Dados: nenhum.
  - Competências: segurança de processos.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes em hosts e spaces. Caminhos: `harness/ruview/src/process-runner.js`, `redact.js`, `repo-trust.js`, `exec.js`, `scripts/redact-secrets.py`.
- **Riscos/limitações:** a redação é heurística. A confiança por marcadores é fraca.
- **Relevância para a plataforma (M15, M16):** alta. Filtro de redação no logging (a plataforma proíbe imprimir `SPATIAL_TOKEN`) e wrapper de subprocess com env allowlist para `check.ps1`.

#### OP-04 — Guardrail de honestidade de claims (claim-check)

- **O que faz:** lint de texto para relatórios, PRs, model cards e README. Sinaliza números de acurácia sem rótulo MEASURED/CLAIMED/SYNTHETIC, MEASURED sem reprodutor e a retórica de 100% ou "perfeito" que o projeto retratou. Disponível como ferramenta MCP, verbo CLI com código de saída e SDK.
- **Como faz:** análise linha a linha. Termos de métrica longos por substring e curtos só com fronteira e número na linha. Remove spans de código, exige número, procura tags e dicas de reprodutor. Findings com severidade e sugestão.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Python, pre-commit.
  - Dados: nenhum.
  - Competências: governança de evidências.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testado. **O "hook" citado nos comentários não existe nas configurações**, e o guardrail não é aplicado ao plugin no CI (que cita um número sem rótulo). Caminhos: `harness/ruview/src/guardrails.js`, `harness/ruview/test/tools.test.mjs`, `harness/ruview/skills/verify.md`.
- **Riscos/limitações:** heurística lexical em inglês. Não verifica se o reprodutor existe.
- **Relevância para a plataforma (M15, M16, M11, M12):** **muito alta e barata**. Um `claim_check.py` (termos pt-BR e en; tags L0_SYNTHETIC, PLANNED, BLOCKED, MEASURED) no `check.ps1`, no CI e no pre-commit, varrendo `docs/*.md`, `PROGRESS.md` e textos do dashboard, para impedir alegações de acurácia ou de clean-room estrita sem rótulo.

#### OP-05 — Gate de avaliação de modelos (train-gate) e treino com proteção

- **O que faz:** só torna publicável uma métrica de pose com baseline de pose média no mesmo split, split sem vazamento (cronológico com intervalo ou agrupado; **aleatório por quadro é recusado**), sem sujeito compartilhado, limites temporais coerentes e delta positivo. Devolve a única frase de claim permitida. Inclui um plano de treino (que não executa) e um treino com confirmação, checkpoints restritos e smoke rotulado como sintético.
- **Como faz:** validação declarativa de um relatório JSON, com falhas bloqueantes e avisos (score quase perfeito como indício de vazamento) e delta em pontos percentuais. O treino monta argv para o trainer com scrubbing de ambiente.
- **Requisitos para implementar:**
  - Hardware: nenhum para o gate.
  - Software: Pydantic, scikit-learn (GroupKFold/TimeSeriesSplit).
  - Dados: relatório com metadados.
  - Competências: avaliação de ML, vazamento.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes de gate e de tempo. O gate confia nos metadados e não recalcula métricas. Caminhos: `harness/ruview/src/training.js`, `test/training.test.mjs`, `test/training-time.test.mjs`, `harness/ruview/skills/train-pose.md`.
- **Riscos/limitações:** relatório fabricado passaria.
- **Relevância para a plataforma (M12, M11, M02, M15):** alta para M12. Schema Pydantic de relatório de avaliação e gate com baseline trivial, split agrupado e rótulo L0. Ver também ML-04 e ML-06.

#### OP-06 — Transporte MCP HTTP, console MCP Apps e UI de terminal

- **O que faz:** servidor MCP Streamable HTTP com token obrigatório (Bearer ou segredo no caminho) em tempo constante, loopback por padrão, allowlist de Origin, corpo limitado, sem sessões nem SSE e **sem escrita via HTTP nunca**. Os resultados trazem conteúdo estruturado, e um widget HTML autocontido renderiza capturas, doctor e devices. Fila FIFO e CLI com tabelas e sparklines em TTY e JSON em pipe.
- **Como faz:** dispatcher compartilhado entre stdio e HTTP que rejeita IDs duplicados, limita a fila e impede sobreposição de ferramentas de hardware. Negociação de versão. O widget não faz requisições externas e só usa `textContent`. A UI respeita `NO_COLOR`.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: SDK MCP Python, uvicorn.
  - Dados: nenhum.
  - Competências: MCP, segurança HTTP.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes de MCP Apps, MCP e UI. Caminhos: `harness/ruview/src/mcp-http.js`, `src/ui/console-widget.js`, `src/cli-ui.js`, `test/mcp-apps.test.mjs`, `docs/adr/ADR-375-ruview-mcp-apps-console-http-transport-and-terminal-ui.md`.
- **Riscos/limitações:** **o modo com segredo no caminho da URL pode vazar em logs** de proxy ou túnel. Sem rate limit.
- **Relevância para a plataforma (M16, M15, M13):** média-alta. Servidor MCP somente leitura sobre os casos de uso, com token em header, loopback e allowlist de Origin. **Não copiar o segredo na URL**, que viola a regra da plataforma.

#### OP-07 — Doctor estruturado com remediação

- **O que faz:** diagnóstico em 12 grupos (runtime, integridade do pacote, hosts, repositório, Rust, Python/esptool, firmware, serial, devices, remoto, servidor, kernel). Cada checagem retorna pass, warn, fail ou skip com uma ação de correção. O código de saída só é não zero com fail.
- **Como faz:** checks independentes. A integridade verifica o manifesto de proveniência. Via MCP, não sonda hardware nem rede.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Python ou PowerShell.
  - Dados: nenhum.
  - Competências: DevEx.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes do doctor e de manifesto corrompido. Caminhos: `harness/ruview/src/doctor.js`, `test/doctor.test.mjs`, `test/doctor-corrupt-manifest.test.mjs`, `docs/adr/ADR-372-structured-debugging-doctor.md`.
- **Riscos/limitações:** muitos skip podem esconder um ambiente incompleto.
- **Relevância para a plataforma (M16):** muito alta. Um `doctor.py` com grupos para Python 3.12/3.13 e venv, Node 22 e `npm.cmd`, presença do `.env` e de `SPATIAL_TOKEN` (sem imprimir), portas, Alembic no head, contrato exportado sincronizado com Zod, Playwright e Docker, com saída JSON e remediação.

#### OP-08 — Acesso a dispositivos do host e a hosts remotos (somente leitura)

- **O que faz:** descobre portas seriais e classifica por VID:PID. Captura só-recepção o UDP de nós CSI (vários formatos, CRC, perda por sequência, RSSI, espectro, análise opcional pelo kernel). Lê radares mmWave por UART, ESPHome API nativa (só endereços privados, sem comandos), RPLIDAR, relay de LiDAR do iPhone e monitor serial sem reset. Executa uma ferramenta somente leitura num host SSH configurado.
- **Como faz:** Node puro e um script Python fixo para serial. Os resultados carregam rótulo de evidência ("valores reportados pelo dispositivo, não claim de acurácia"). Exige grants via MCP. O SSH força BatchMode e host key estrita e nunca encaminha flash, treino ou calibração.
- **Requisitos para implementar:**
  - Hardware: dispositivos opcionais.
  - Software: pyserial (BSD), asyncio, aioesphomeapi (MIT).
  - Dados: streams ao vivo.
  - Competências: protocolos binários.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. **O e2e emula radar e LiDAR em pseudo-terminais e o ESP32 via UDP, e se declara SYNTHETIC.** **Na captura ESP32, o campo de evidência de topo diz MEASURED mesmo quando os pacotes trazem a flag de sintético** (só um booleano por nó distingue). Caminhos: `harness/ruview/src/devices/registry.js`, `esp32.js`, `mmwave.js`, `esphome.js`, `lidar.js`, `src/remote.js`, `test/e2e/devices.e2e.mjs`, `.github/workflows/ruview-device-e2e.yml`, `docs/adr/ADR-373-host-device-access-layer.md`.
- **Riscos/limitações:** o RPLIDAR gira o motor ao ler. Criptografia Noise do ESPHome não suportada.
- **Relevância para a plataforma (M01, M02, M04, M05, M14, M16):** baixa agora (BLOCKED) e alta como desenho futuro: porta de aquisição só-recepção com rótulo de evidência **por quadro** (sem o defeito acima) e emuladores pty/UDP para testes de contrato.

#### OP-09 — Flash de firmware verificado com evidência de boot

- **O que faz:** resolve o bundle por variante, **verifica cada imagem contra `SHA256SUMS`**, monta o argv do esptool, faz preflight do chip e só escreve com confirmação. Depois captura cerca de 15 s de log e só marca "validado em hardware" com callbacks CSI e sem panic.
- **Como faz:** pipeline plano → checksums → preflight → confirmação → escrita → evidência → resumo. O provisionamento de Wi-Fi fica fora, para que credenciais não passem pela harness.
- **Requisitos para implementar:**
  - Hardware: ESP32 com USB.
  - Software: esptool (GPL, processo externo).
  - Dados: bundles com checksums.
  - Competências: firmware.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Testes; o próprio catálogo admite que no CI o flash é provado só contra hardware falso. Caminhos: `harness/ruview/src/firmware.js`, `test/firmware.test.mjs`, `scripts/firmware-release-guard.sh`.
- **Riscos/limitações:** ação destrutiva.
- **Relevância para a plataforma (M16):** baixa como funcionalidade e alta como padrão para ações mutantes (migração, restore, purga): plano revisável, integridade, preflight, confirmação e evidência pós-ação.

#### OP-10 — Guidance com citação de fonte e "contributor brain" revisado

- **O que faz:** catálogo revisado por tópico, com maturidade, evidência, caminhos citados (conferidos num checkout real), comandos de validação e limitações. Inclui uma base de conhecimento JSONL com tipo de evidência, fonte (caminho:linha), tags e flag de revisão.
- **Como faz:** valida registros (slug, tamanho, caminho relativo sem traversal, ausência de segredos e de texto com cara de prompt-injection), busca por relevância e verifica fontes. Propostas entram como não revisadas.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: SQLite FTS5 ou rank_bm25.
  - Dados: registros curados.
  - Competências: gestão de conhecimento.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes e verificação no CI. O corpus tem só 5 registros. Caminhos: `harness/ruview/src/guidance.js`, `brain.js`, `brain/corpus/core.jsonl`, `test/brain.test.mjs`.
- **Riscos/limitações:** a verificação confere a linha, não o conteúdo.
- **Relevância para a plataforma (M16, M15):** alta e barata: `docs/knowledge/*.jsonl` citando caminho:linha, validado por pytest, mais uma ferramenta de "guidance".

#### OP-11 — Flywheel/Darwin de políticas do agente e agente noturno de pesquisa delimitado

- **O que faz:** mantém um "genoma" textual de políticas do agente avaliado por suítes de frases exigidas e proibidas, com fingerprint e replay "honest-null". O agente noturno divide a autoridade em jobs (coleta pública, proposta via API de LLM, score, issue, implementação declarativa, validação, no máximo um PR em rascunho).
- **Como faz:** verifica presença e ausência de frases e métricas de sucesso e custo. O replay depende de uma biblioteca externa.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: GitHub Actions; API de LLM paga ou proprietária no original.
  - Dados: suítes de avaliação.
  - Competências: engenharia de agentes.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. A avaliação é testada. **O agente noturno exige um segredo de API proprietária.** Caminhos: `harness/ruview/flywheel/gate.mjs`, `run.mjs`, `replay.mjs`, `genome.json`, `test/flywheel.test.mjs`, `.github/workflows/nightly-sota-agent.yml`, `docs/adr/ADR-284-bounded-nightly-sota-agent.md`.
- **Riscos/limitações:** "fitness" por presença de palavras é trivial de manipular.
- **Relevância para a plataforma (M16, M15, M12):** média-baixa. Aproveitável: testes "anchor" em pytest que garantem que `AGENTS.md` e `CLAUDE.md` mantêm as regras obrigatórias. Agente com LLM pago fica fora do custo zero.

#### OP-12 — Integração com hosts de agente: plugin Claude Code/Codex, skills, subagentes, manifesto de proveniência e painel ao vivo

- **O que faz:** (a) plugin com 10 skills, 7 comandos e 3 subagentes, com espelho Codex; (b) skills neutras de host com instalador; (c) manifesto SHA-256 verificado no empacotamento e no doctor; (d) painel ao vivo com nós, waterfall CSI e radar.
- **Como faz:** Markdown com frontmatter, smoke estrutural, scripts de manifesto e hooks de painel que chamam só o CLI em leitura.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: hosts de agente, Node.
  - Dados: nenhum.
  - Competências: autoria de skills.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. O painel e os hosts têm testes. Skills e comandos são documentação. **O smoke do plugin não roda no CI.** O plugin cita um PCK sem rótulo, contradizendo a harness. O MCP do plugin é lançado sem versão fixada. Caminhos: `plugins/ruview/.claude-plugin/plugin.json`, `plugins/ruview/skills`, `plugins/ruview/scripts/smoke.sh`, `harness/ruview/scripts/update-manifest.mjs`, `harness/ruview/.harness/manifest.json`, `harness/ruview/mod`, `docs/adr/ADR-377-ruview-live-claude-code-mod.md`.
- **Riscos/limitações:** supply chain e manifesto sem assinatura.
- **Relevância para a plataforma (M16, M15):** média-alta. Versionar skills e prompts para os fluxos do operador (bootstrap, check, export de contrato, registro em `PROGRESS.md`), com smoke em pytest e manifesto SHA-256.

#### OP-13 — SENSE-BRIDGE (`@ruvnet/rvagent`) e CLI TypeScript `ruview-cli`

- **O que faz:** servidor MCP com primitivas do servidor de sensoriamento:
  - janela CSI, presença, contagem e confiança;
  - FR e FC (null se indisponível) e pacote de vitais;
  - último scan BFLD, com escore de risco e classe;
  - inferência pontual de pose e contagem via cogs;
  - registry de módulos e treino em background com job persistente.

  As ferramentas de roadmap estão só catalogadas. O CLI é um cliente dos mesmos endpoints.
- **Como faz:** schema Zod único gera o JSON Schema. Cliente HTTP com timeout. Runner de cogs com **postura fail-open**. stdio por padrão e HTTP opt-in com Origin e token opcional.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: SDK MCP, Zod (no alvo, SDK MCP Python com Pydantic).
  - Dados: saída do servidor.
  - Competências: MCP.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 116 casos (o README diz 99). O CLI não tem testes. **O escore de risco de identidade sai numérico via MCP**, apesar de o script `verify` afirmar que esse campo nunca cruza a fronteira MCP. **O treino roda em background a partir do MCP.** Caminhos: `tools/ruview-mcp/src/index.ts`, `http-transport.ts`, `src/schemas/tools.ts`, `src/tools/`, `src/cog.ts`, `tools/ruview-mcp/tests`, `tools/ruview-cli/src`.
- **Riscos/limitações:** fail-open contrasta com o fail-closed da harness. Token HTTP opcional.
- **Relevância para a plataforma (M01, M02, M04, M05, M11, M12, M13, M15):** alta como catálogo. Ferramentas MCP somente leitura para presença, ocupação e entradas/saídas, sempre com L0. Vitais e pose como PLANNED/BLOCKED. Adotar fail-closed e token obrigatório.

#### OP-14 — Prova determinística, witness bundles e guardas de regressão

- **O que faz:**
  - **`verify`**: 9 fases (hash das features da pipeline v1 sobre sinal sintético semeado, varredura de geradores aleatórios em produção, testes Rust, binding PyO3, invariante de privacidade, presença de pacotes e imagens publicados).
  - **`prove.sh`**: hard gates INCOMPLETE e testes "anti-slop".
  - Provas de CIR e calibração contra hashes commitados, mais uma sonda que compara hash bruto e quantizado da FFT.
  - Witness bundles com logs, ADR, hashes, versões e um script de verificação.
  - Guarda de fix-markers (27 correções com padrões exigidos e proibidos), guarda de release de firmware e política de dados CSI.
- **Como faz:** hashing determinístico contra golden, grep, resumo por fase e workflows dedicados.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Bash/PowerShell, Python com numpy/scipy fixados, Docker.
  - Dados: sinal de referência.
  - Competências: reprodutibilidade, supply chain.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Workflows presentes (resultados não consultados). **O `verify` sai com 0 quando fases ficam em SKIP**, e o bundle não tem assinatura (o script de verificação confere sobretudo presença de arquivos). **O invariante de privacidade é checado por grep em apenas dois scripts.** Caminhos: `verify`, `scripts/prove.sh`, `archive/v1/data/proof/verify.py`, `scripts/verify-cir-proof.sh`, `scripts/verify-calibration-proof.sh`, `scripts/probe-fft-platform.py`, `scripts/generate-witness-bundle.sh`, `scripts/check_fix_markers.py`, `scripts/fix-markers.json`, `.github/workflows/verify-pipeline.yml`.
- **Riscos/limitações:** hash de float depende da plataforma.
- **Relevância para a plataforma (M15, M16, M12):** muito alta e direta. Golden hash do gerador sintético (semente fixa, valores quantizados, JSON canônico) no `check.ps1`, bundle de evidência por release **assinado** (cosign, minisign ou Ed25519), fix-markers com pytest e guarda contra commit de dados reais. **SKIP não pode virar PASS.** Ver também GV-18 e PY-07.

#### OP-15 — Simulação de firmware em QEMU, swarm multi-nó e injeção de falhas

- **O que faz:** roda o firmware com CSI mock em QEMU e valida o UART. Simula malha multi-nó com agregador e snapshots de VM. Injeta falhas pelo monitor e checa a saúde depois. Tem configurador de swarm por YAML (estrela, malha, linha, anel e presets) com oráculo de saúde coletiva, gerador de matriz NVS e CLI unificado.
- **Como faz:** scripts orquestram QEMU e validadores Python com códigos de saída padronizados.
- **Requisitos para implementar:**
  - Hardware: Linux.
  - Software: QEMU da Espressif, ESP-IDF, PyYAML.
  - Dados: CSI mock.
  - Competências: virtualização, caos.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `SYNTHETIC_OR_SIMULATED`. Chamados no CI, mas os validadores não têm testes próprios. Caminhos: `scripts/qemu-cli.sh`, `scripts/qemu-mesh-test.sh`, `scripts/qemu-chaos-test.sh`, `scripts/qemu_swarm.py`, `scripts/swarm_presets`, `scripts/swarm_health.py`, `scripts/inject_fault.py`, `.github/workflows/firmware-qemu.yml`, `.github/workflows/ruview-swarm-ci.yml`.
- **Riscos/limitações:** só Linux. O mock não representa RF.
- **Relevância para a plataforma (M16, M14):** média como padrão sem QEMU: "simulação de frota" sintética com presets YAML e injeção de falhas (latência, perda, nó offline, deriva de relógio), com oráculo em pytest/hypothesis. Ver também FW-14.

#### OP-16 — Benchmarks e reprodução independente de claims

- **O que faz:**
  - **wiflow-std**: reprodução de um modelo de pose de terceiros. O checkpoint publicado não reproduz as alegações (refutado como distribuído), o dataset tinha máscaras corrompidas, o modelo foi retreinado e se aproximou da alegação, e houve otimização edge (fp16, int8, ONNX Runtime).
  - **edge-latency**: budgets CLAIMED convertidos em MEASURED-on-host, com ressalvas.
  - **edge-skills**: verdade plantada e lista DATA-GATED.
  - CI de regressão (gate só de compilação e subconjunto informativo, sem gate de tempo).
  - Telemetria de uma sessão de campo e scripts diversos.
- **Como faz:** scripts com resultados em JSON e `RESULTS.md`, com comando e máquina registrados, e rótulos de grade (MEASURED, MEASURED-on-host, MEASURED-on-synthetic, REFUTED, CLAIMED, DATA-GATED).
- **Requisitos para implementar:**
  - Hardware: GPU para retreino.
  - Software: PyTorch, ONNX Runtime, pytest-benchmark.
  - Dados: dataset público (licença não verificada).
  - Competências: metodologia experimental.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNCLEAR`. A evidência é mista e nada foi medido em ESP32. **O arquivo de "baseline" de benchmark na raiz é telemetria de campo com ticks duplicados e não é referenciado pelo código**, como o próprio documento de pesquisa admite. Caminhos: `benchmarks/wiflow-std/RESULTS.md`, `benchmarks/wiflow-std/eval_repro.py`, `benchmarks/wiflow-std/onnx_bench.py`, `benchmarks/edge-latency/RESULTS.md`, `benchmarks/edge-skills/RESULTS.md`, `.github/workflows/bench-regression.yml`, `benchmark_baseline.json`, `docs/research/ruview-beyond-sota/03-benchmark-validation-methodology.md`.
- **Riscos/limitações:** números de host não valem para borda. O "baseline" tem nome enganoso.
- **Relevância para a plataforma (M11, M12, M02, M04, M05, M15):** alta pela metodologia "reproduzir antes de citar" como template de documentação, e pytest-benchmark informativo no CI, sem gate de tempo. Ver também ML-11.

#### OP-17 — Observabilidade: convenções semânticas OpenTelemetry e stack de monitoramento legado

- **O que faz:** (a) registro próprio de semconv (atributos de nó, fonte CSI, frames, presença, movimento; eventos de nó online/offline, presença, vitais, queda, erro MQTT, modelo carregado), schema versionado, **validação com OpenTelemetry Weaver no CI** e geração de constantes com checagem sem diff; (b) um stack Prometheus/Grafana/Fluentd com descoberta Kubernetes, mais de 30 alertas e um dashboard genérico.
- **Como faz:** registro YAML checado, binário Weaver com hash fixado e tracing com OTLP atrás de feature.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Weaver (Apache-2.0), opentelemetry-instrumentation-fastapi, prometheus-client, Prometheus/Grafana OSS.
  - Dados: telemetria.
  - Competências: OTel, SRE.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. As semconv são validadas no CI. **A configuração Prometheus referencia um arquivo de regras inexistente**, e os alertas usam métricas de domínio que não aparecem no código atual (o stack assume Kubernetes, Postgres e Redis). Caminhos: `semconv/registry/attributes.yaml`, `semconv/registry/events.yaml`, `semconv/schema/ruview-0.1.0.yaml`, `.github/workflows/semconv.yml`, `v2/crates/wifi-densepose-sensing-server/src/semconv.rs`, `monitoring/prometheus-config.yml`, `monitoring/alerting-rules.yml`, `logging/fluentd-config.yml`.
- **Riscos/limitações:** alertas que nunca disparariam. Semconv em estabilidade "development".
- **Relevância para a plataforma (M15, M16, M01, M07, M04):** alta e gratuita. Semconv próprias com source_type, evidence_level e validation_status obrigatórios em spans e eventos, validadas por Weaver no CI, e Prometheus/Grafana só em compose opcional. Não copiar o stack Kubernetes legado. Ver também SS-22.

#### OP-18 — Instalação, build e deploy

- **O que faz:** Makefile com alvos por perfil. `install.sh` com 8 perfis, detecção de sistema, toolchains e hardware Wi-Fi e recomendação de perfil. `deploy.sh` para AWS (Terraform, EKS, kubectl, Helm). Scripts de treino em GPU na nuvem, publicação no Hugging Face, rotação de token npm e release de firmware. Publicação npm com proveniência OIDC.
- **Como faz:** shell com detecção de ambiente.
- **Requisitos para implementar:**
  - Hardware: variável.
  - Software: Bash, Docker, CLIs de nuvem, Terraform, Helm.
  - Dados: artefatos.
  - Competências: DevOps.
- **Evidência e maturidade:** `PARTIAL` / `NONE`. Sem testes. **`deploy.sh` referencia diretórios `terraform/` e `k8s/` que não existem**, então está quebrado. Scripts de nuvem acoplados a um projeto específico. Caminhos: `Makefile`, `install.sh`, `deploy.sh`, `scripts/gcloud-train.sh`, `scripts/publish-huggingface.py`, `scripts/rotate-npm-token.sh`, `.github/workflows/ruview-npm-release.yml`.
- **Riscos/limitações:** nuvem paga. Secrets por manifest.
- **Relevância para a plataforma (M16):** média. Perfis com recomendação podem enriquecer o `bootstrap.ps1`. Proveniência gratuita de release com GitHub attestations. Ignorar deploy em nuvem paga.

#### OP-19 — Aplicações de sensoriamento em scripts sobre CSI ao vivo ou em replay

- **O que faz:** scripts autônomos para:
  - saúde: triagem de apneia com índice tipo AHI, estágios de sono, marcha e tremor, estresse por HRV;
  - ocupação e ambiente: contagem por min-cut, fingerprint de estados, mudança de objetos por nulos de subportadora;
  - RF: classificação de material e fingerprint de dispositivos multi-frequência, tomografia 2D por retroprojeção, radar passivo biestático, detecção através de parede, scanner RF;
  - outros: espectrograma com embedding, transformer de grafo, rede spiking com STDP e watcher de presença.
- **Como faz:** pipelines heurísticos (janelas, FFT, correlação, grafos, clustering, retroprojeção, aprendizado online) sobre o formato binário ou sobre gravações.
- **Requisitos para implementar:**
  - Hardware: 1+ ESP32.
  - Software: Node.js, Python.
  - Dados: streams ou gravações (não versionadas).
  - Competências: DSP RF, fisiologia.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `NONE`. Sem testes e sem referências cruzadas. Caminhos: `scripts/apnea-detector.js`, `scripts/sleep-monitor.js`, `scripts/stress-monitor.js`, `scripts/mincut-person-counter.js`, `scripts/room-fingerprint.js`, `scripts/material-detector.js`, `scripts/device-fingerprint.js`, `scripts/rf-tomography.js`, `scripts/passive-radar.js`, `scripts/through-wall-detector.js`.
- **Riscos/limitações:** aplicações de saúde sem validação. Riscos éticos no fingerprint de dispositivos e na detecção através de parede.
- **Relevância para a plataforma (M01, M02, M04, M05, M06, M08, M09, M10, M14):** média como catálogo de ideias, reimplementadas de forma independente sobre sinais sintéticos no esquema "planta e mede". Contagem por min-cut (M02) e fingerprint de estados (M08) são viáveis. M09 e M10 ficam BLOCKED.

#### OP-20 — Pontes, gateways e pipeline de dados de treino

- **O que faz:** shim HTTP que imita parte da API do servidor; ponte HomeKit (HAP-python) e watcher do C6; fusão mmWave + CSI de FC/FR; ponte UDP para um appliance externo; servidor de inferência por socket Unix; provisionamento NVS; gravador e relay UDP; **emissor UDP sintético no formato do firmware** e transcodificador com quarentena; coleta de verdade por câmera, alinhamento temporal, calibração câmera-sala e captura noturna de sala vazia; treino de contagem, export ONNX com paridade e validação de blueprints e do pipeline ESP32→MQTT→HA.
- **Como faz:** scripts de propósito único ligados por UDP, HTTP, MQTT, HAP ou sockets.
- **Requisitos para implementar:**
  - Hardware: dispositivos opcionais.
  - Software: HAP-python, paho-mqtt, MediaPipe, PyTorch, onnx.
  - Dados: gravações.
  - Competências: integração IoT.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. Há testes para calibração, formato de captura, HTTP do ground truth e visuais; a maioria das pontes não tem testes. Caminhos: `scripts/ruview-sensing-server.py`, `scripts/mmwave_fusion_bridge.py`, `scripts/provision.py`, `scripts/record-csi-udp.py`, `scripts/synth-csi-udp.py`, `scripts/collect-ground-truth.py`, `scripts/align-ground-truth.js`, `scripts/train-count.py`, `scripts/export-onnx.py`, `scripts/tests`.
- **Riscos/limitações:** credenciais Wi-Fi por linha de comando ficam no histórico. Câmera e biometria (LGPD). Appliance proprietário.
- **Relevância para a plataforma (M13, M12, M11, M04, M05, M02, M16):** média. Hooks MQTT/HA e HAP-python só com eventos sintéticos. O emissor sintético UDP inspira testes de contrato. A câmera fica BLOCKED.

#### OP-21 — Adaptador de hierarquia espacial externa com projeção semântica (Cognitum Spaces)

- **O que faz:** leitura paginada de sites, prédios, andares, espaços, zonas, entidades, eventos e alertas de um serviço externo, via binário instalado. Nunca aceita bearer nem API key direto e revalida a projeção.
- **Como faz:** limites estruturais, validação de IDs e **lista normalizada de campos proibidos** (CSI, CIR, tensores, gravações, pose, ondas vitais, identidade, biometria, rostos, embeddings). Via MCP exige grant e não permite escolher arquivo de credencial nem URL.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: Pydantic.
  - Dados: tenant externo.
  - Competências: minimização de dados.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testado. O serviço externo não foi exercitado. Caminhos: `harness/ruview/src/spaces.js`, `test/spaces.test.mjs`, `skills/cognitum-spaces.md`.
- **Riscos/limitações:** serviço proprietário. A deny-list por nome é contornável (allowlist seria mais forte).
- **Relevância para a plataforma (M15, M02, M03, M14):** alta pelo conceito de "projetor de saída" em todas as respostas e exportações (allowlist Pydantic, deny-list normalizada como defesa extra, limites de tamanho e profundidade). Ver também WM-22.

#### OP-22 — Relatórios de QE gerados por agentes e tutoriais

- **O que faz:** avaliação de qualidade por 8 agentes (score geral de 55/100, gate reprovado) com prioridades P0–P3 (rate limit contornável por cabeçalho de proxy, exceções vazando, JWT em URL de WebSocket, monolito, baixa cobertura, fallback para dados simulados no app MAT), e análises SFDIPOT. Tutoriais de pré-treino com appliance, tomografia simulada e cluster Pi 5 + NPU.
- **Como faz:** documentos com metodologia e priorização.
- **Requisitos para implementar:**
  - Hardware: Pi 5, NPU (tutoriais).
  - Software: variável.
  - Dados: variável.
  - Competências: QE.
- **Evidência e maturidade:** `DOC_ONLY` / `NONE`. **É um snapshot desatualizado**: o CI atual já roda os testes Rust apontados como ausentes, e o monolito cresceu. Foi produzido por agentes, não por auditoria independente. Caminhos: `docs/qe-reports/EXECUTIVE-SUMMARY.md`, `docs/qe-reports/02-security-review.md`, `docs/qe-reports/06-product-assessment-sfdipot.md`, `docs/tutorials/coherent-rf-tomography-backprojection.md`, `docs/tutorials/pi5-cluster-cognitive-rf-observer.md`.
- **Riscos/limitações:** achados obsoletos.
- **Relevância para a plataforma (M15, M16, M08, M14):** média. O formato SFDIPOT com P0–P3 pode estruturar o `SECURITY_REVIEW`. Lições diretas: não confiar em X-Forwarded-For sem proxy confiável, não expor exceções, nunca token em URL e nunca cair silenciosamente para dados simulados sem rótulo.

### 4.12 Python, legado v1, PRD/DDD/ADRs e documentação de produto

**Escopo.** São três camadas.

1. **`python/`**: wheel 2.x `wifi-densepose` (alias `ruview`, tombstone 1.99.0) via PyO3/maturin, com cerca de 217 funções de teste e fixtures golden de paridade com o Rust.
2. **`archive/v1` e `wifi_densepose/` na raiz**: monolito FastAPI legado, depreciado, com cerca de 570 testes. Só a prova determinística continua no CI. O shim da raiz aponta para um caminho que não existe mais.
3. **Documentação**: PRD do rvCSI, 9 modelos DDD, cerca de 319 ADRs, cerca de 145 arquivos de pesquisa, especificação SPARC v1 e material InvisPose.

O próprio corpus declara que o status das ADRs não é confiável (ADR-164: cerca de 70% nunca plenamente implementadas) e criou uma disciplina de honestidade (escada L0–L5, vocabulário de evidência, gates fail-closed), que é o material de maior valor.

| ID | Feature | Maturidade | Validação | Módulos |
| --- | --- | --- | --- | --- |
| PY-01 | Pacote Python wifi-densepose 2.x / ruview (PyO3) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M11, M12 |
| PY-02 | Extratores de sinais vitais (respiração e FC) | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M04, M05 |
| PY-03 | Camada BFLD e gate de PrivacyClass | PARTIAL | UNIT_TESTS_ONLY | M15, M08 |
| PY-04 | Cliente de telemetria (WS, MQTT, discovery HA, primitivas) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M13, M15, M01, M07, M09 |
| PY-05 | Extras AETHER e MERIDIAN | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M08, M12, M16 |
| PY-06 | MAT: detecção de sobreviventes e triagem START | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M01, M04, M05 |
| PY-07 | Prova determinística de pipeline ("Trust Kill Switch") | IMPLEMENTED_TESTED | SYNTHETIC_OR_SIMULATED | M15, M16 |
| PY-08 | Pipeline DSP de CSI legado v1 | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M06, M08, M16 |
| PY-09 | Sensoriamento por RSSI em hardware comum (v1) | IMPLEMENTED_TESTED | UNIT_TESTS_ONLY | M01, M06, M16, M04 |
| PY-10 | Servidor FastAPI legado v1 | PARTIAL | UNIT_TESTS_ONLY | M02, M03, M06, M15, M16 |
| PY-11 | Redes neurais v1 e referência DensePose-from-WiFi | PARTIAL | UNIT_TESTS_ONLY | M11, M12 |
| PY-12 | PRD e modelo de domínio rvCSI | DOC_ONLY | NONE | M12, M15, M16, M08 |
| PY-13 | Modelo de domínio RuvSense | PARTIAL | UNCLEAR | M01, M02, M08, M09, M11, M16 |
| PY-14 | Modelos de domínio CHCI e Deployment Platform | DOC_ONLY | NONE | M14, NONE |
| PY-15 | Governança de evidência (L0–L5, proveniência, gates fail-closed) | PARTIAL | UNCLEAR | M15, M16 |
| PY-16 | Privacidade operacional (privacy mode, classes, Veil, Soul Signature) | PARTIAL | UNCLEAR | M15, M13 |
| PY-17 | Integração HA/Matter e primitivas semânticas (ADR-115) | PARTIAL | UNIT_TESTS_ONLY | M13 |
| PY-18 | Aplicações de saúde, sono e ambiente (ADR-077) | IMPLEMENTED_UNTESTED | UNCLEAR | M09, M10, M06, M08, M07 |
| PY-19 | Programa de pesquisa SOTA | RESEARCH | SYNTHETIC_OR_SIMULATED | M02, M08, M16, M14 |
| PY-20 | Especificação histórica v1 (SPARC) e documento InvisPose | DOC_ONLY | NONE | M02, M03, M07, NONE |

#### PY-01 — Pacote Python wifi-densepose 2.x / ruview (bindings PyO3 sobre núcleo Rust)

- **O que faz:** distribui partes do núcleo Rust num wheel de ABI estável: tipos de pose (17 keypoints, pessoa, estimativa, bounding box com IoU), metadados de build, meta-pacote alias e um tombstone 1.99.0 que interrompe o import com guia de migração.
- **Como faz:** crate fora do workspace compilada por maturin e reexportada por uma fachada Python com stubs. Features viram extras pip. Os laços liberam o GIL. O CI compila, roda pytest e verifica um orçamento de tamanho. **Os tipos de pose só transportam dados; não há inferência no wheel.**
- **Requisitos para implementar:**
  - Hardware: qualquer CPU.
  - Software: Rust, PyO3, maturin, cibuildwheel, pytest, mypy.
  - Dados: nenhum.
  - Competências: FFI, empacotamento Python.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 217 testes (pose 28, keypoint 23). Maturidade declarada inconsistente: o docstring diz scaffold, o pyproject diz "Production/Stable" e a ADR continua Proposed. **Há dois manifestos para o mesmo nome de distribuição** (raiz 1.2.0 com scripts quebrados e `python/` 2.0.0). Caminhos: `python/Cargo.toml`, `python/pyproject.toml`, `python/src/lib.rs`, `python/src/bindings/pose.rs`, `python/wifi_densepose/__init__.py`, `python/ruview-meta/src/ruview/__init__.py`, `python/tombstone/src/wifi_densepose/__init__.py`, `.github/workflows/python-ci.yml`, `docs/adr/ADR-117-pip-wifi-densepose-modernization.md`.
- **Riscos/limitações:** o nome "pose" sugere inferência.
- **Relevância para a plataforma (M11, M12):** o padrão "domínio puro + fachada estável + extras opcionais + gate de tamanho/versão + tombstone para linhas legadas" serve para manter os contratos 1.0/1.1 ao lado do 2.0.0, em Python puro.

#### PY-02 — Extratores de sinais vitais (respiração e frequência cardíaca)

- **O que faz:** estima FR e FC por subportadora, com confiança, status e leitura combinada com qualidade, além de presets para a taxa do ESP32.
- **Como faz:** janela deslizante, combinação ponderada de subportadoras, passa-banda nas bandas fisiológicas públicas e pico espectral. Para FC, pico local de autocorrelação e filtragem contra vazamento respiratório, com confiança limitada pela evidência do primeiro estágio. Libera o GIL.
- **Requisitos para implementar:**
  - Hardware: nenhum para L0.
  - Software: scipy (butter, filtfilt, welch).
  - Dados: séries sintéticas com taxas conhecidas.
  - Competências: DSP biomédico, ética de dados de saúde.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 22 testes com senoides. O README admite que não estabelecem acurácia real. O status "Valid" é descrito como "grau clínico". Caminhos: `python/src/bindings/vitals.rs`, `python/tests/test_vitals.py`, `python/bench/test_bench_vitals.py`, `docs/adr/ADR-021-vital-sign-detection-rvdna-pipeline.md`.
- **Riscos/limitações:** sobreafirmação clínica. Movimento mascara o sinal. Dados de saúde (LGPD).
- **Relevância para a plataforma (M04, M05):** alta para o motor sintético: gerador com verdade e estimador próprio em numpy/scipy, L0, sem alegação clínica. Dados reais ficam PLANNED/BLOCKED. Ver também SV-16.

#### PY-03 — Camada BFLD (feedback de beamforming) e gate de PrivacyClass

- **O que faz:** superfície Python para quadros de beamforming (variantes HE e HT), com relatório agregado e enum de classe de privacidade de 4 níveis, além de predicados de elegibilidade por porta (rede, Matter, HomeKit).
- **Como faz:** valida dimensões contra a variante PHY e calcula amplitude média e coerência. As ADRs descrevem os invariantes (bruto nunca sai, embedding só em RAM, hash com chave por site e rotação diária).
- **Requisitos para implementar:**
  - Hardware: AP 802.11ac/ax e modo monitor.
  - Software: numpy, hmac/hashlib.
  - Dados: capturas de BFI.
  - Competências: 802.11, privacy by design.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. 19 testes de frame e relatório. **O próprio binding declara a ingestão como stub.** **O enum de classe é registrado, mas não é reexportado nem testado em Python**, apesar de o docstring mostrar um import direto. Caminhos: `python/src/bindings/bfld.rs`, `python/src/bindings/privacy_gate.rs`, `python/tests/test_bfld.py`, `docs/adr/ADR-118-bfld-beamforming-feedback-layer-for-detection.md`, `docs/adr/ADR-120-bfld-privacy-class-and-hash-rotation.md`, `docs/research/BFLD/`.
- **Riscos/limitações:** BFI permite reidentificação. Captura de terceiros tem implicações legais.
- **Relevância para a plataforma (M15, M08):** classes de privacidade com elegibilidade por porta de saída aplicadas aos adaptadores de REST, WS, export e automação, em Python puro. Captura de BFI fica BLOCKED. Ver também MB-11 a MB-13.

#### PY-04 — Cliente de telemetria Python (WebSocket, MQTT, discovery do HA e primitivas semânticas)

- **O que faz:** consome a telemetria do servidor (mensagens tipadas), assina tópicos MQTT de dados e de discovery, inspeciona entidades e oferece um listener tipado para 10 primitivas.
- **Como faz:** cliente asyncio com token opcional e limite de mensagem, **sem auto-reconexão por decisão de projeto**. Wrapper MQTT com matching próprio de curingas, isolamento de exceções de handler, TLS e senha fora de repr. Parser de discovery validado. Eventos imutáveis e imports preguiçosos.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: websockets, paho-mqtt, Mosquitto, HA.
  - Dados: mensagens.
  - Competências: asyncio, MQTT.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 64 testes de cliente mais 17 de robustez (JSON malformado, aninhamento profundo, strings enormes, byte nulo, injeção de tópico, senha fora de repr). Caminhos: `python/wifi_densepose/client/ws.py`, `mqtt.py`, `ha.py`, `primitives.py`, `python/tests/test_client_*.py`, `python/tests/test_security.py`.
- **Riscos/limitações:** primitivas derivadas de vitais são dados de saúde.
- **Relevância para a plataforma (M13, M15, M01, M07, M09):** alta. Publicação de eventos sintéticos em discovery do HA em dry-run, separando estados inferidos de biometria, e reprodução da bateria de testes hostis com pytest/hypothesis.

#### PY-05 — Extras AETHER e MERIDIAN (embeddings contrastivos e generalização entre ambientes)

- **O que faz:** AETHER extrai embeddings normalizados, gera pares aumentados, calcula perda contrastiva e salva/carrega pesos. MERIDIAN normaliza CSI de hardwares diferentes, codifica geometria de forma invariante à ordem, adapta a um ambiente novo e avalia o gap entre domínios.
- **Como faz:** NT-Xent/InfoNCE com cosseno. Formato de pesos com identificador e contagem de parâmetros (contra alocações gigantes). Reamostragem por perfil de hardware e pesos de baixo posto. **A paridade é verificada por fixtures golden** (SHA-256 e tolerância) contra o Rust.
- **Requisitos para implementar:**
  - Hardware: CPU (GPU para treino).
  - Software: PyTorch/numpy, scikit-learn, PEFT.
  - Dados: CSI multi-sala com split sem vazamento.
  - Competências: contrastivo, adaptação de domínio.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. AETHER 18 e MERIDIAN 13 testes, mais paridade em Rust. Os bindings documentam onde divergem da ADR. A ADR-185 está "Proposed". O wheel MERIDIAN excede o orçamento de tamanho. Caminhos: `python/src/bindings/aether.rs`, `meridian.rs`, `python/tests/test_aether.py`, `test_meridian.py`, `python/tests/golden/`, `docs/adr/ADR-185-python-p6-sota-bindings.md`.
- **Riscos/limitações:** re-ID é biometria.
- **Relevância para a plataforma (M08, M12, M16):** embeddings para fingerprints de ambiente e normalização com perfil de hardware sobre dados sintéticos, com **testes golden de paridade** como padrão. Re-ID de pessoa fica BLOCKED. Ver também ML-09 e ML-13.

#### PY-06 — MAT: detecção de sobreviventes em desastres e triagem START

- **O que faz:** registra um evento (9 tipos), zonas, ingestão de CSI e um ciclo de detecção, listando sobreviventes com triagem, prioridade, confiança e vitais.
- **Como faz:** força um ciclo não contínuo num runtime privado, de forma síncrona e sem segurar o GIL.
- **Requisitos para implementar:**
  - Hardware: rádios em campo.
  - Software: runtime assíncrono.
  - Dados: inexistentes publicamente.
  - Competências: protocolos de resgate.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. 7 testes. O exemplo declara que demonstra a API, não acurácia. Caminhos: `python/src/bindings/mat.rs`, `python/wifi_densepose/mat.py`, `python/tests/test_mat.py`, `python/examples/mat_triage.py`.
- **Riscos/limitações:** segurança de vida.
- **Relevância para a plataforma (M01, M04, M05):** baixa e BLOCKED. Ver MB-01 a MB-07.

#### PY-07 — Prova determinística de pipeline ("Trust Kill Switch")

- **O que faz:** um comando reprocessa um sinal de referência sintético pelo pipeline real e compara o SHA-256 das features com o hash publicado. Se o hash diverge entre plataformas, aceita tolerância relativa contra um vetor de referência. Inclui auditoria de geradores aleatórios fora dos testes e verificações extras de CIR e calibração.
- **Como faz:** gerador determinístico (3 antenas × 56 subportadoras, multipercurso fixo, modulações de respiração e caminhada) com parâmetros documentados num JSON de metadados. Bytes canônicos com hash e dependências numéricas fixadas num lock. Workflow a cada push relevante.
- **Requisitos para implementar:**
  - Hardware: CPU.
  - Software: numpy/scipy fixados, hashlib.
  - Dados: sinal sintético.
  - Competências: reprodutibilidade numérica.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `SYNTHETIC_OR_SIMULATED`. Hashes, vetor e workflow commitados. **Prova determinismo, não acurácia.** O fallback por tolerância existe porque o hash não era portátil. Caminhos: `archive/v1/data/proof/verify.py`, `generate_reference_signal.py`, `sample_csi_meta.json`, `expected_features.sha256`, `expected_features_reference.npz`, `archive/v1/requirements-lock.txt`, `.github/workflows/verify-pipeline.yml`, `docs/adr/ADR-011-python-proof-of-reality-mock-elimination.md`.
- **Riscos/limitações:** um "PASS" pode ser lido como validação real. Artefato grande.
- **Relevância para a plataforma (M15, M16):** **altíssima e sem custo**. "Golden replay" com cenários semeados, JSON canônico com SHA-256 e fallback `numpy.allclose` no `check.ps1`, mais auditoria estática que proíbe aleatoriedade fora do adaptador simulador, com o rótulo "prova de determinismo, não de acurácia". Ver também OP-14.

#### PY-08 — Pipeline DSP de CSI legado v1 (CSIProcessor, PhaseSanitizer, parsers)

- **O que faz:** pré-processa CSI, extrai features (amplitude, fase, correlação, Doppler, PSD) e detecta presença com confiança suavizada. Faz parsing de quadros ESP32, de sincronização e de formato Atheros.
- **Como faz:** limiar de ruído, janelamento, normalização, unwrap, z-score com interpolação, média móvel, Butterworth com filtfilt, Doppler por FFT das diferenças de fase em janela limitada, escore de movimento com EMA. **Os parsers lançam erro em vez de devolver aleatório** (correção da ADR-011).
- **Requisitos para implementar:**
  - Hardware: ESP32 ou NIC de pesquisa para dados reais.
  - Software: numpy/scipy.
  - Dados: CSI.
  - Competências: DSP RF.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Cerca de 570 testes no v1 (não executados). A ADR-011 inventariou placeholders aleatórios que foram removidos. A árvore está congelada e depreciada. Caminhos: `archive/v1/src/core/csi_processor.py`, `phase_sanitizer.py`, `archive/v1/src/hardware/csi_extractor.py`, `archive/v1/tests/unit/test_csi_processor_tdd.py`, `archive/v1/DEPRECATED.md`.
- **Riscos/limitações:** sem manutenção, limiares ad hoc.
- **Relevância para a plataforma (M01, M06, M08, M16):** alta como catálogo de técnicas públicas, reimplementadas do zero em numpy/scipy.

#### PY-09 — Sensoriamento por RSSI em hardware comum (coletores Windows, Linux, macOS e simulado)

- **O que faz:** coleta RSSI e ruído da interface Wi-Fi do próprio computador, extrai features e classifica o estado em ausente, presente parado ou ativo, com confiança e WS. **Declara explicitamente suportar só presença e movimento.**
- **Como faz:** coletores atrás de um protocolo (/proc e iw no Linux, `netsh` no Windows a cerca de 2 Hz, CoreWLAN no macOS) mais um simulador determinístico e ring buffer thread-safe. Features: média, variância, assimetria, curtose, IQR, potência por banda, frequência dominante e CUSUM. Classificação por regras com concordância opcional entre receptores. Ordem de fontes com fallback.
- **Requisitos para implementar:**
  - Hardware: qualquer notebook.
  - Software: numpy/scipy, ruptures (BSD-2).
  - Dados: RSSI rotulado.
  - Competências: séries temporais.
- **Evidência e maturidade:** `IMPLEMENTED_TESTED` / `UNIT_TESTS_ONLY`. Testes extensos e teste ao vivo no Windows com skip. Verificação comunitária citada sem artefato. **O servidor Rust atual não tem fonte RSSI para Linux** (regressão em relação ao v1). Caminhos: `archive/v1/src/sensing/rssi_collector.py`, `feature_extractor.py`, `classifier.py`, `backend.py`, `ws_server.py`, `archive/v1/tests/unit/test_sensing.py`, `docs/adr/ADR-013-feature-level-sensing-commodity-gear.md`.
- **Riscos/limitações:** taxa baixa e AGC limitam respiração e contagem.
- **Relevância para a plataforma (M01, M06, M16, M04):** primeira fonte "real" de custo zero (inclusive no Windows do usuário), como adaptador de laboratório PLANNED com evidência L1/L2 explícita. Ver também EH-20.

#### PY-10 — Servidor FastAPI legado v1 (REST/WS, autenticação, persistência e tarefas)

- **O que faz:** API de pose e ocupação (atual, análise, zonas, histórico, atividades, calibração), streams WS, health/ready/live/metrics, JWT, rate limit, CORS, CLI, configuração de domínio (saúde, varejo, segurança) e tarefas de backup, limpeza e monitoramento.
- **Como faz:** camadas FastAPI e SQLAlchemy assíncrono com fallback SQLite. As tarefas de backup cobrem banco, configuração, export e logs com retenção. Depois da ADR-011, os mocks ficam isolados e atrás de flag.
- **Requisitos para implementar:**
  - Hardware: servidor.
  - Software: FastAPI, SQLAlchemy, Redis, python-jose, passlib.
  - Dados: tabelas.
  - Competências: backend assíncrono.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Há testes de integração. **Carregamento de pesos comentado, atividade classificada pela norma de um tensor e segmentação placeholder.** Middlewares de autenticação e rate limit duplicados. **O shim da raiz aponta para um diretório inexistente e engole exceções devolvendo lista vazia.** Caminhos: `archive/v1/src/api/main.py`, `routers/pose.py`, `routers/stream.py`, `middleware/auth.py`, `archive/v1/src/database/models.py`, `archive/v1/src/tasks/backup.py`, `cleanup.py`, `archive/v1/src/services/pose_service.py`, `wifi_densepose/__init__.py`.
- **Riscos/limitações:** a ADR-011 registra um bypass histórico de autenticação por mock. CVEs históricos em python-jose. Código depreciado.
- **Relevância para a plataforma (M02, M03, M06, M15, M16):** checklist de lições: falhar explicitamente em vez de cair para mock, separar adaptador sintético de real, health/ready/live distintos, retenção e backup como casos de uso, audit log e middleware único.

#### PY-11 — Redes neurais v1 (tradução de modalidade + DensePose) e material de referência DensePose-from-WiFi

- **O que faz:** rede que traduz CSI para features visuais e cabeça DensePose (partes + UV). Em `references/`, uma reimplementação didática da arquitetura do artigo público "DensePose From WiFi" (CMU) com dados simulados.
- **Como faz:** encoder-decoder convolucional com atenção, FPN e ramos de segmentação e UV, com inicialização aleatória e sem checkpoint.
- **Requisitos para implementar:**
  - Hardware: GPU.
  - Software: PyTorch.
  - Dados: pares câmera–CSI com anotações densas (licenças a verificar).
  - Competências: visão computacional.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. Só a arquitetura (sem pesos, saída aleatória, como `DEPRECATED.md` confirma). **Em `references/`, um AP@50 do artigo é apresentado como "acurácia de detecção" de um código que roda com dados aleatórios.** Caminhos: `archive/v1/src/models/modality_translation.py`, `densepose_head.py`, `references/wifi_densepose_pytorch.py`, `references/script_4.py`, `references/wifi_densepose_results.csv`, `references/README.md`.
- **Riscos/limitações:** saída aleatória confundível com inferência.
- **Relevância para a plataforma (M11, M12):** baixa a média. M11 fica PLANNED/BLOCKED, e a tradução de modalidade fica registrada como pesquisa.

#### PY-12 — PRD e modelo de domínio rvCSI (runtime de sensoriamento RF na borda)

- **O que faz:** especifica uma plataforma de CSI agnóstica de hardware: ingestão multi-fonte, validação segura, esquema normalizado de frame, DSP, eventos, memória vetorial, SDK, CLI, MCP, replay e auditoria. **Os non-goals são explícitos**: sem identidade, sem diagnóstico médico, sem prova legal de ocupação e sem pose através de parede.
- **Como faz:** sete contextos encadeados (Captura → Validação → Sinal → Calibração → Evento → Memória/Agente). Invariantes:
  - nada atravessa sem status aceito ou degradado, e rejeitados vão para **quarentena**;
  - janelas de uma única fonte e sessão;
  - calibração com escore de estabilidade e versionamento, e cada detector declara a versão de calibração usada;
  - todo evento referencia ao menos uma janela de evidência, com confiança em [0,1];
  - embeddings rastreáveis e retenção por coleção.
- **Requisitos para implementar:**
  - Hardware: Raspberry Pi (para dados reais).
  - Software: no alvo, Pydantic, FastAPI, WS.
  - Dados: capturas para replay.
  - Competências: DDD, contratos, validação defensiva.
- **Evidência e maturidade:** `DOC_ONLY` / `NONE`. A implementação fica num submódulo vazio no clone. ADRs e PRD estão "Proposed". Caminhos: `docs/prd/rvcsi-platform-prd.md`, `docs/ddd/rvcsi-domain-model.md`, `docs/adr/ADR-095-rvcsi-edge-rf-sensing-platform.md`, `docs/adr/ADR-096-rvcsi-ffi-crate-layout.md`, `docs/adr/ADR-097-adopt-rvcsi-as-ruview-csi-runtime.md`.
- **Riscos/limitações:** sem código verificável.
- **Relevância para a plataforma (M12, M15, M16, M08):** muito alta e de custo zero. Adotar invariantes equivalentes com redação própria (quarentena, janela de fonte única, evento com evidência obrigatória, detector com versão de calibração, retenção por coleção) e manter non-goals explícitos no plano mestre.

#### PY-13 — Modelo de domínio RuvSense (multiestático, coerência, campo persistente, longitudinal)

- **O que faz:** especifica fusão multi-nó e multicanal, gate de coerência, rastreamento persistente com re-ID, campo persistente (baseline e perturbação, tomografia), tendências longitudinais e identidade entre cômodos.
- **Como faz:** DDD com agregados, eventos, ACLs, repositórios e invariantes (por exemplo, alerta de drift exige desvio sustentado por vários dias).
- **Requisitos para implementar:**
  - Hardware: malha ESP32.
  - Software: EWMA, z-score, CUSUM, Kalman.
  - Dados: gravações longas.
  - Competências: fusão de sensores.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. Os arquivos citados existem no crate de sinal (ver §4.1). A ADR-164 classifica as ADRs relacionadas como desatualizadas ou contraditas. Caminhos: `docs/ddd/ruvsense-domain-model.md`, `docs/adr/ADR-029-ruvsense-multistatic-sensing-mode.md`, `docs/adr/ADR-030-ruvsense-persistent-field-model.md`, `v2/crates/wifi-densepose-signal/src/ruvsense/`.
- **Riscos/limitações:** re-ID e saúde longitudinal são sensíveis.
- **Relevância para a plataforma (M01, M02, M08, M09, M11, M16):** alta para M08 e M16 (baseline com perturbação e drift sobre o gerador). Re-ID fica BLOCKED.

#### PY-14 — Modelos de domínio CHCI (imagem coerente do canal humano) e Deployment Platform (TV box Armbian)

- **O que faz:** CHCI especifica forma de onda, sincronização, processamento coerente e medição submilimétrica. Deployment Platform especifica gestão de appliances ARM, compilação cruzada, quiosque, ponte CSI e topologia.
- **Como faz:** documentos DDD.
- **Requisitos para implementar:**
  - Hardware: rádios coerentes, SDR, TV boxes.
  - Software: toolchains.
  - Dados: medições de laboratório.
  - Competências: rádio coerente, frota.
- **Evidência e maturidade:** `DOC_ONLY` / `NONE`. **O crate CHCI e os diretórios citados como código não existem.** Caminhos: `docs/ddd/chci-domain-model.md`, `docs/ddd/deployment-platform-domain-model.md`, `docs/adr/ADR-042-coherent-human-channel-imaging.md`, `docs/adr/ADR-046-android-tv-box-armbian-deployment.md`.
- **Riscos/limitações:** precisão submilimétrica sem evidência.
- **Relevância para a plataforma (M14, NONE):** baixa; apenas pesquisa futura.

#### PY-15 — Governança de evidência e honestidade (escada L0–L5, proveniência, gates fail-closed)

- **O que faz:** conjunto de políticas e contratos:
  - escada pública de evidência (simulação, replay, laboratório, sala/sujeito held-out, piloto multi-site, produção);
  - vocabulário MEASURED/CLAIMED/SYNTHETIC/DATA-GATED;
  - máquina de estados da fonte e propagação da flag sintética;
  - ocupação fail-closed;
  - gates de release de modelo, rotulagem honesta, eliminação de mocks e witness logs;
  - **autoauditoria do corpus de ADRs**;
  - espinha de certificados.
- **Como faz:** regras em ADRs convertidas em tipos e testes no v2. **Promover de nível exige artefato** (corpus de replay, protocolo de laboratório ou manifesto de split). Transições de estado puras. Auditoria do corpus por lentes de status, supersessão, contradição, lacunas e dependência de dados.
- **Requisitos para implementar:**
  - Hardware: nenhum para L0.
  - Software: Python (Enum, pytest), hashlib, PyNaCl.
  - Dados: manifestos de split, corpora de replay.
  - Competências: engenharia de evidência, metrologia.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. As ADRs alegam implementação inicial com testes no v2 (ver §4.8). A ADR-346 relata qualificação física (ver FW-03). O user-guide admite que a espinha não roda no servidor ao vivo. Pela ADR-164, o status é só indicativo. Caminhos: `docs/adr/ADR-282-ruview-ecosystem-positioning.md`, `ADR-295-source-provenance-state-machine.md`, `ADR-391-csi-analysis-synthetic-provenance.md`, `ADR-346-fail-closed-edge-occupancy-evidence.md`, `ADR-298-model-release-sanity-gates.md`, `ADR-160-edge-skill-library-honest-labeling.md`, `ADR-187-archive-v1-deprecation-honest-labeling.md`, `ADR-164-adr-corpus-gap-analysis.md`, `docs/adr/gap-analysis/`, `ADR-300-perception-substrate-program.md`, `CHANGELOG.md` (todos sob `docs/adr/` exceto o último).
- **Riscos/limitações:** volume de ADRs gera drift documental. O risco é reproduzir burocracia sem enforcement.
- **Relevância para a plataforma (M15, M16):** **altíssima e de custo zero**. Escada própria com "subir de nível exige artefato", enum de estado de fonte, invariantes fail-closed, gates de modelo em pytest, ledger encadeado e checador de claims, tudo com redação própria. Ver também GV-04.

#### PY-16 — Privacidade operacional (modo de privacidade, classes de dados, WiFi Veil e Soul Signature)

- **O que faz:** o modo de privacidade do servidor remove FC, FR e pose de REST, WS, gravações, MQTT e Matter, mantendo presença, contagem, zonas e primitivas. Há matriz de classes por cenário, pesquisa de contramedida (Veil), especificação de biometria RF passiva (Soul Signature) e propostas de aprendizado federado, DP-SGD e criptografia pós-quântica.
- **Como faz:** allowlist exata de chaves a remover (um campo biométrico novo precisa ser incluído na lista), classes por campo e hash com chave por site e época.
- **Requisitos para implementar:**
  - Hardware: nenhum para a política.
  - Software: projeção de campos em Python; Opacus e Flower só para pesquisa.
  - Dados: classificação de campos.
  - Competências: privacy by design, LGPD/GDPR.
- **Evidência e maturidade:** `PARTIAL` / `UNCLEAR`. O modo de privacidade está implementado no servidor (SS-15). Federado, DP e PQC estão "Proposed". **Soul Signature é especificação de pesquisa pré-implementação**, e Veil tem modelo de referência. Caminhos: `docs/user-guide.md`, `docs/adr/ADR-105-federated-csi-training.md`, `docs/adr/ADR-106-dp-sgd-and-primitive-isolation.md`, `docs/adr/ADR-108-kyber-post-quantum-key-exchange.md`, `docs/research/privacy-shield/`, `docs/research/soul/`.
- **Riscos/limitações:** o modo de privacidade não garante conformidade. **Soul Signature propõe reconhecimento sem consentimento no momento da captura.**
- **Relevância para a plataforma (M15, M13):** alta. Privacidade como política de projeção com allowlist exata em todas as portas de saída, testada por contrato. Registrar Soul Signature e re-ID como **BLOCKED** no plano mestre.

#### PY-17 — Integração Home Assistant / Matter e primitivas semânticas (ADR-115)

- **O que faz:** discovery MQTT com um dispositivo por nó, entidades brutas e 10 primitivas, disponibilidade, LWT, TLS e blueprints. Bridge Matter especificado, mas indisponível.
- **Como faz:** tópicos por nó e configs retidas.
- **Requisitos para implementar:**
  - Hardware: servidor doméstico.
  - Software: Mosquitto, HA, paho-mqtt; python-matter-server no futuro.
  - Dados: eventos.
  - Competências: HA, MQTT.
- **Evidência e maturidade:** `PARTIAL` / `UNIT_TESTS_ONLY`. A ADR afirma o MQTT entregue com 410 testes de biblioteca. **O binário rejeita as flags Matter.** O CHANGELOG avisa que configs retidas de entidades removidas ficam órfãs. Caminhos: `docs/adr/ADR-115-home-assistant-integration.md`, `ADR-116-cog-ha-matter-seed.md`, `ADR-122-bfld-ruview-ha-matter-exposure.md`, `ADR-126-ruview-native-ha-port-master.md` (todos sob `docs/adr/`), `docs/user-guide.md`, `python/wifi_densepose/client/primitives.py`.
- **Riscos/limitações:** automações acionadas por inferências não validadas.
- **Relevância para a plataforma (M13):** alta. Adaptador MQTT discovery publicando só estados L0 rotulados, com allowlist de entidades e limpeza de configs retidas. Ver HC-14.

#### PY-18 — Aplicações de saúde, sono e ambiente (ADR-077)

- **O que faz:** scripts de estágios de sono, apneia (índice tipo AHI), estresse por HRV, marcha e tremor, contador de pessoas, fingerprint de sala, objetos novos ou movidos, fingerprint de dispositivos, tomografia, radar passivo e detecção através de parede.
- **Como faz:** heurísticas em janelas de minutos, regras de pausa, espectro de HRV, clusterização e backprojection, ao vivo ou em replay, com aviso não médico.
- **Requisitos para implementar:**
  - Hardware: nós CSI.
  - Software: scipy.signal, scikit-learn.
  - Dados: referências clínicas (inexistentes no repositório).
  - Competências: medicina do sono, regulação.
- **Evidência e maturidade:** `IMPLEMENTED_UNTESTED` / `UNCLEAR`. Os scripts existem com avisos, sem testes nem validação. Caminhos: `docs/adr/ADR-077-novel-rf-sensing-applications.md`, `docs/adr/ADR-078-multifreq-mesh-applications.md`, `docs/readme-details.md`, `scripts/sleep-monitor.js`, `scripts/apnea-detector.js`.
- **Riscos/limitações:** risco alto de alegação médica indevida.
- **Relevância para a plataforma (M09, M10, M06, M08, M07):** média, apenas como roteiro. M09 e M10 continuam BLOCKED, no máximo com cenários sintéticos L0 para exercitar a UI. Ver OP-19.

#### PY-19 — Programa de pesquisa SOTA (docs/research e scripts numpy de referência)

- **O que faz:** cerca de 145 documentos de pesquisa:
  - contagem e fingerprint por RSSI;
  - saliência, Fresnel e posicionamento de antenas;
  - consistência entre enlaces e subtração ancorada em física;
  - re-ID cross-room e resultados negativos;
  - verticais;
  - sensoriamento topológico (min-cut), sensores quânticos e privacidade;
  - roadmap de produção.
- **Como faz:** um loop autônomo assistido por IA (cerca de 41 "ticks") gerou hipótese, método, resultado e scripts numpy, classificando resultados negativos por caminho de resolução.
- **Requisitos para implementar:**
  - Hardware: nenhum.
  - Software: numpy, scipy, scikit-learn.
  - Dados: sintéticos; capturas multi-sessão para reproduzir.
  - Competências: física de propagação, estatística rigorosa.
- **Evidência e maturidade:** `RESEARCH` / `SYNTHETIC_OR_SIMULATED`. **R8 relata contagem só por RSSI próxima da contagem por CSI, mas com acurácias perto do acaso, numa única sessão e split aleatório** (risco de vazamento temporal). Várias conclusões de 100% são sintéticas. Caminhos: `docs/research/sota-2026-05-22/00-summary.md`, `R8-rssi-only-count.md`, `R9-rssi-fingerprint-knn.md`, `R6-fresnel-forward-model.md`, `PRODUCTION-ROADMAP.md`, `docs/research/rf-topological-sensing/`, `docs/research/quantum-sensing/`, `examples/research-sota/`.
- **Riscos/limitações:** claims fortes sobre amostras fracas.
- **Relevância para a plataforma (M02, M08, M16, M14):** média-alta como fonte de ideias de custo zero (otimizador de posicionamento por Fresnel para M16, fingerprint RSSI com kNN para M08), sempre com avaliação por sessão e sala disjuntas e rótulo L0.

#### PY-20 — Especificação histórica v1 (plans/ SPARC) e documento "InvisPose" (references/)

- **O que faz:** especificação funcional e técnica original: coleta e processamento de CSI, inferência neural, tempo real, histórias de usuário para saúde (quedas, atividade), varejo (contagem, permanência) e segurança (intrusão), API, streaming, dashboard, app, dados e critérios de aceite, além de um plano de reconstrução da UI de pose.
- **Como faz:** documentos em fases prevendo uma stack web/ML pesada (FastAPI, PyTorch/TensorFlow, PostgreSQL, Redis, RabbitMQ/Celery, React, Kubernetes).
- **Requisitos para implementar:**
  - Hardware: roteadores 3×3 MIMO com OpenWRT com patch.
  - Software: stack genérica.
  - Dados: não aplicável.
  - Competências: engenharia de requisitos.
- **Evidência e maturidade:** `DOC_ONLY` / `NONE`. Histórico e superado. O README de `references/` traz citações sem fonte resolvível e trata o AP@50 do artigo como acurácia própria. Caminhos: `plans/overview.md`, `plans/phase1-specification/functional-spec.md`, `plans/phase1-specification/api-spec.md`, `plans/phase2-architecture/system-architecture.md`, `references/README.md`, `references/WiFi-DensePose-README.md`.
- **Riscos/limitações:** claims infladas e stack cara.
- **Relevância para a plataforma (M02, M03, M07, NONE):** baixa. As histórias de domínio podem inspirar personas e analytics, sem reaproveitar números ou arquitetura.

---

## 5. Matriz consolidada de requisitos

Esta seção agrega os requisitos das 259 features catalogadas na seção 4. A coluna "Custo/licença" indica se o item é gratuito/open-source (✔ livre), gratuito com ressalva (⚠) ou pago/proprietário (✖). A coluna "Situação na plataforma" segue a política atual: synthetic-native, sem hardware comprado e sem expansão de IA sem autorização.

### 5.1 Hardware

| Item | Features que exigem (exemplos) | Custo/licença | Situação na plataforma |
| --- | --- | --- | --- |
| Nenhum (CPU comum) | Maioria das bibliotecas: SV-01, SV-11, GV-01..08, WM-01, WM-07, WM-10..21, EH-12, EH-16, EH-18, EH-21 | ✔ | Viável já, em modo L0 |
| Notebook/PC com Wi-Fi (RSSI do host) | EH-20, PY-09, SS-20 | ✔ (equipamento existente) | PLANNED: adaptador de laboratório com nível de evidência próprio |
| ESP32-S3 / ESP32-C6 (CSI) | FW-01..14, EH-01, EH-14, SS-01, SV-23 | ✖ baixo custo (compra) | BLOCKED até decisão do proprietário |
| Roteador MediaTek MT7981 + OpenWrt com patch | FW-15, EH-17 | ✖ compra; patches GPL/BSD-3-Clause-Clear | BLOCKED |
| NIC de pesquisa (Intel 5300, AX210, Atheros) | SV-02 (razão conjugada), MB-08, ML-02 | ✖ compra | BLOCKED |
| Adaptador Wi-Fi com modo monitor e AP Wi-Fi 6 (BFI) | FW-16, MB-11, PY-03 | ✖; captura de terceiros com questões legais | BLOCKED |
| Radar mmWave (24/60 GHz) | FW-11, GV-10, UI-16 | ✖ baixo custo | BLOCKED |
| UWB, BLE 6.0 Channel Sounding, FMCW | WM-02, MB-04, WM-15 | ✖ | BLOCKED |
| Câmera/webcam (verdade de pose) | ML-15, UI-17, MB-16, WM-25 | ⚠ dispositivo comum, mas biometria | BLOCKED (biometria fora do escopo) |
| iPhone/iPad com LiDAR | HC-18 | ✖ | PLANNED/NOT_TESTED |
| Dispositivos de referência (cinta respiratória, oxímetro, ECG, PSG) | SV-18, GV-09, EH-06 | ✖ | BLOCKED (sem validação clínica) |
| GPU (treino de pose/contrastivo) | ML-01, ML-17, WM-25 | ✖ ou nuvem paga | PLANNED, só com autorização de IA |
| Raspberry Pi 5 / NPU | ML-15, ML-16, OP-22 | ✖ | Fora do escopo atual |
| Plataforma de PHY aberto (Zynq + AD9361) | FW-18, GV-17 | ✖ alto custo | BLOCKED |
| Hub Apple (HomePod/Apple TV), controlador Matter | HC-11, HC-12, SS-18 | ✖ | PLANNED opcional |

### 5.2 Software — backend Python (todos gratuitos)

| Biblioteca/ferramenta | Licença (pública) | Uso sugerido na plataforma | Features de referência |
| --- | --- | --- | --- |
| numpy, scipy | BSD | DSP do gerador e dos estimadores (filtros, FFT, Welch, autocorrelação, SVD, ISTA) | SV-02..08, SV-16, PY-02, PY-08, WM-07 |
| scikit-learn | BSD | Splits por grupo, baselines triviais, LDA/QDA, Lasso, HashingVectorizer | ML-04, GV-10, SS-11, HC-09 |
| statsmodels | BSD | Intervalo de Wilson | GV-08 |
| networkx | BSD | Min-cut, PageRank, grafos de cena e ontologia | SS-04, EH-10, WM-06 |
| filterpy | MIT | Kalman para trilhas | SV-10, MB-05, WM-12 |
| shapely | BSD | Zonas e paredes (gêmeo, posicionamento) | WM-13, WM-14 |
| pydantic | MIT | Contrato 2.0.0 aditivo, validadores fail-closed | SV-01, WM-01, FW-03 |
| FastAPI/Starlette (`TrustedHostMiddleware`) | MIT/BSD | Casos de uso, WS, Host allowlist | SS-14, GV-14 |
| SQLAlchemy, Alembic, SQLite (FTS5) | MIT / domínio público | Ledger append-only, ontologia, baselines, busca | GV-03, WM-10, WM-16, HC-06 |
| hashlib/hmac (stdlib), blake3 | PSF / CC0-Apache | Hash testemunha, witness, pseudônimos com chave | SV-01, GV-02, MB-12 |
| PyNaCl, cryptography | Apache-2.0 / BSD | Ed25519, AEAD, assinatura de certificados e exportações | GV-05, SV-21, HC-17, WM-17 |
| PyJWT, joserfc, Authlib, itsdangerous | MIT/BSD | OAuth/sessão server-side se houver multiusuário | GV-11..13 |
| aiomqtt / paho-mqtt + Mosquitto | BSD / EPL-EDL | Discovery do Home Assistant em dry-run | SS-16, HC-14, MB-15 |
| HAP-python, zeroconf | Apache-2.0 / LGPL | HomeKit opcional e mDNS | HC-11, HC-12, SS-21 |
| wasmtime-py, Extism | Apache-2.0 / BSD-3 | Plugins WASM assinados opcionais | HC-08, EH-01 |
| hnswlib, FAISS, sqlite-vec | Apache-2.0 / MIT / MIT-Apache | Fingerprints de ambiente (M08) | MB-20, ML-13, WM-17 |
| river, ruptures, nolds | BSD / BSD-2 / MIT | Drift, change-point/CUSUM, dinâmica não linear | ML-14, SV-17, SV-15 |
| dtaidistance, tslearn, POT | Apache-2.0 / BSD / MIT | DTW e transporte ótimo | SV-12, EH-03, EH-08 |
| onnxruntime, PyTorch, PEFT, MLflow | MIT / BSD-3 / Apache-2.0 / Apache-2.0 | Model Lab (somente com autorização de IA) | ML-01, ML-12, UI-06 |
| opentelemetry-python, prometheus-client, psutil, OpenTelemetry Weaver | Apache-2.0 / Apache-2.0 / BSD / Apache-2.0 | Telemetria com atributos de evidência e readiness real | SS-22, OP-17 |
| pytest, hypothesis, pytest-benchmark, Atheris | MIT / MPL-2.0 / BSD / Apache-2.0 | Testes de propriedade, determinismo, benchmarks informativos, fuzz | EH-12, FW-14, OP-16 |
| pre-commit, gitleaks, detect-secrets, cyclonedx-py, pip-audit, osv-scanner | MIT / MIT / Apache-2.0 / Apache-2.0 / Apache-2.0 / Apache-2.0 | Guardas de dados, segredos, SBOM e vulnerabilidades | GV-19, GV-20, GV-18 |
| Typer/Click, pyserial | MIT / BSD | CLI do operador e serial futura | OP-01, OP-08 |
| magpylib, pyroomacoustics | BSD-2 / MIT | Simulação física auxiliar | ML-20, WM-07 |

### 5.3 Software — frontend e ferramentas (gratuitos)

| Item | Licença | Uso sugerido | Features de referência |
| --- | --- | --- | --- |
| Zod (já usado), JSON Schema | MIT | Contrato único gerado do backend | Todas as de contrato |
| three.js / react-three-fiber / drei, deck.gl | MIT | Planta baixa, heatmaps e voxels sintéticos | UI-04, MB-16, WM-05 |
| Recharts / ECharts | MIT / Apache-2.0 | KPIs de ocupação, fila e permanência | EH-05 |
| cmdk, next-intl, driver.js, Serwist | MIT | Paleta, i18n pt-BR, onboarding, PWA | UI-07, UI-03 |
| Playwright + axe-core (já usados) | Apache-2.0 / MPL-2.0 | E2E e acessibilidade | UI-10 |
| Mermaid, D2 | MIT / MPL-2.0 | Diagramas como código | UI-20 |
| Home Assistant | Apache-2.0 | Destino de integração local | HC-14, UI-15 |
| ESP-IDF, esp-csi (referência pública) | Apache-2.0 | Firmware próprio futuro | FW-01 |
| esptool, QEMU (Espressif), tshark, scapy, FeitCSI | GPL | Apenas como executáveis externos, nunca linkados | FW-06, FW-14, FW-16, MB-08 |
| Vosk, whisper.cpp, Piper | Apache-2.0 / MIT / MIT | Voz local (fora do escopo, PLANNED) | HC-10 |

### 5.4 Dados

| Dado | Origem/licença | Features | Observação |
| --- | --- | --- | --- |
| Gerador sintético determinístico próprio | Próprio | Praticamente todas | Base do produto; L0_SYNTHETIC obrigatório |
| Parâmetros de materiais (ITU-R P.2040) | Público | WM-07 | Para o gerador físico |
| MM-Fi | CC BY-NC | ML-02, ML-17, WM-24, WM-25 | **Não comercial**: não usar em caminho comercial |
| NTU-Fi HumanID | CC BY 4.0 | FW-17 | Identificação de pessoas, fora de escopo |
| CSI-BFI-HAR | GPL-3.0 | FW-17 | Cuidado com licença |
| BFId | Acordo não comercial | FW-17 | Evitar |
| Widar3.0, dataset WiFlow (Kaggle) | Não verificadas | ML-02, ML-11 | Verificar antes de qualquer uso |
| Pesos no Hugging Face (RuView) | Declarados MIT; não verificados | ML-18, ML-13 | Não usar (exposição e licença) |
| Capturas próprias com consentimento e referência | Próprio | SV-18, GV-09 | BLOCKED até protocolo e autorização |

### 5.5 Competências

| Competência | Necessária para | Prioridade para a plataforma |
| --- | --- | --- |
| Modelagem de domínio (DDD), contratos versionados, serialização canônica | SV-01, WM-01, WM-10, PY-12 | Alta |
| Engenharia de evidência e metrologia (níveis, gates, Bland–Altman, IC de Wilson, bootstrap) | GV-03..08, ML-03..07, SV-18 | Alta |
| Privacy by design e LGPD (classes, pseudonimização, minimização, retenção) | SS-15, MB-11..13, WM-08, WM-17 | Alta |
| DSP clássico e estatística robusta/online | SV-02..08, SV-16, PY-08 | Alta (gerador e estimadores sintéticos) |
| Propagação RF (Friis, Fresnel, multi-wall, método das imagens) | WM-05, WM-07, WM-13, WM-14 | Média-alta |
| Fusão de sensores e rastreamento (variância inversa, Kalman, associação) | WM-11, WM-12, MB-05 | Média-alta |
| Segurança web e de API (OAuth/PKCE, DNS rebinding, tickets WS, CSP) | SS-14, GV-11..14, UI-03 | Alta |
| Criptografia aplicada (Ed25519, AEAD, cadeias de hash) | GV-01..02, HC-17, WM-17 | Média |
| Automação residencial (MQTT, discovery do HA, FSMs com histerese) | SS-16, SS-17, HC-04, HC-14 | Média |
| Observabilidade (OpenTelemetry, semconv, Prometheus) | SS-22, OP-17 | Média |
| ML com avaliação sem vazamento (somente com autorização) | ML-04, OP-05, FW-17 | Baixa no curto prazo |
| Firmware embarcado, OpenWrt, 802.11 | FW-*, EH-14..18 | Baixa (BLOCKED) |

### 5.6 Itens pagos, proprietários ou restritos a evitar

- APIs de fornecedores RF (Mist, NETGEAR, Origin AI, Plume e outros), por exigirem contrato comercial (SS-20, EH-19).
- Serviços Cognitum (OAuth, Spaces, Seed, API de completions), proprietários e com custo desconhecido (SS-23, WM-22, OP-11, OP-21).
- Nuvem paga para treino e distribuição (GCS, AWS/EKS), usados em OP-18 e HC-16.
- Certificação Matter (CSA) e programa MFi da Apple para produto comercial (SS-18, HC-11).
- Datasets não comerciais (MM-Fi, BFId) em qualquer caminho comercial.
- Assets Mixamo (termos Adobe) e imagens de CDNs de terceiros (UI-01, UI-18).

---

## 6. Alegações vs evidências

Esta tabela consolida as divergências encontradas entre o que README, ADRs, comentários ou interfaces afirmam e o que o código e os artefatos sustentam, com tom factual. A coluna "Situação" usa estes rótulos:

- **Divergente**: o código contradiz a alegação.
- **Não verificável**: não há artefato no repositório.
- **Doc à frente**: a documentação promete mais do que existe.
- **Doc atrás**: a documentação está defasada em relação ao código.
- **Consistente**: registro honesto, incluído porque serve de boa prática.

### 6.1 Capacidades e acurácia de sensoriamento

| # | Alegação (fonte) | Evidência observada | Situação |
| --- | --- | --- | --- |
| 1 | README raiz: respiração e FC "através de paredes", com precisões numéricas de respiração e ocupação, alcance e penetração em concreto | Nenhuma sessão MEASURED de vitais ou ocupação; o README do crate de vitais e a ADR-293 admitem fixtures sintéticas (SV-16, SV-18) | Divergente |
| 2 | README raiz/exemplos: o ESP32 de baixo custo detecta presença, movimento, respiração e FC através de paredes (`examples/README.md`) | Os scripts só leem valores já calculados pelo firmware; sem evidência de acurácia (UI-16, FW-02) | Não verificável |
| 3 | README raiz descreve FC por passa-banda e cruzamento por zero e respiração por fase envolvida | O crate usa autocorrelação e coerência; o servidor usa FIR + FFT; o firmware tem uma terceira implementação (SV-16, SS-05, FW-02) | Divergente |
| 4 | Expectativas de acurácia de vitais da ADR-021 | São metas, não medições | Doc à frente |
| 5 | Contagem de pessoas no firmware e no servidor | Heurística de capacidade de slots e escores com falsos positivos relatados; sem MAE (FW-02, SS-04, FW-03) | Não verificável |
| 6 | Guia MAT: taxas de sucesso por tipo de desastre, alcance e precisão de localização 2D/profundidade | Todos os testes usam senoides ou o dispositivo simulado (MB-01..04) | Não verificável |
| 7 | `wifi-densepose-ruvector`: TDoA com erro abaixo de alguns metros com 3+ pares | Só layouts sintéticos pequenos (MB-19) | Não verificável |
| 8 | Seleção de subportadoras melhora o SNR em vários dB | Valor de literatura, não medido no repositório (SV-03) | Não verificável |
| 9 | Respiração por RSSI no wifiscan | A taxa de varredura (cache de vários segundos) fica abaixo de Nyquist (EH-20) | Divergente (fisicamente implausível nesse caminho) |
| 10 | Point cloud descrita como "tomografia CSI" | Blobs gaussianos em posições fixas por ID de nó escalados por RSSI; batimento fixo em zero; pose stub (MB-17) | Divergente |
| 11 | Pose COCO-17 publicada pelo servidor | Esqueleto procedural modulado por escalares do sinal; nenhuma inferência no loop (SS-08) | Divergente |
| 12 | Localização por "pico do campo" | O próprio código declara que não é triangulação (SS-08) | Consistente |
| 13 | Exemplos médicos: "saída de hardware real" de pressão arterial com precisão em mmHg | Sem reprodutor; o próprio repositório registra PA sem contato via CSI como resultado negativo; "HRV" calculada sobre FC reportada (UI-16) | Divergente |
| 14 | Pasta "through-wall" do WiFlow | O README admite que não houve validação através de parede, entre salas ou entre dias; o script A/B sugere que o ganho pode ser vazamento temporal (UI-17) | Divergente |
| 15 | App mobile: ver através de paredes pelo celular | O app só exibe dados do servidor ou da simulação; RSSI do iOS e da Web é stub (UI-13) | Divergente |
| 16 | Model card: FC "através de roupas", estágios de sono, alerta de queda, contagem de 1–4 pessoas | Sem evidência quantitativa; o card admite PCK@20 de 2,5% sem câmera (ML-18) | Não verificável |
| 17 | `R8`: contagem só por RSSI retém quase toda a acurácia do CSI | Valores absolutos perto do acaso, numa única sessão, com split aleatório (PY-19) | Divergente (inferência fraca) |
| 18 | Manchetes do SOTA de pesquisa (ganhos de cobertura e detecção de intrusos) | Simulações numpy; o próprio README as classifica como física sintética (UI-19) | Consistente (rotulado) |
| 19 | Estudo MM-Fi: PCK@20 de cerca de 83% e micro int4 de cerca de 74% | Scripts de reprodução citados não existem no checkout; split aleatório in-domain (ML-17) | Não verificável |
| 20 | CHCI: medição submilimétrica | O crate e os diretórios citados como código não existem (PY-14) | Doc à frente |

### 6.2 Modelos, treino e ML

| # | Alegação (fonte) | Evidência observada | Situação |
| --- | --- | --- | --- |
| 21 | O README do sensing-server lista graph transformer, SONA, embeddings e sparse inference | Código re-exportado de outro crate; o campo de keypoints de modelo é sempre nulo fora de testes (SS-08, SS-10) | Doc à frente |
| 22 | O endpoint de carga de modelo marca o modelo como "carregado" | Só grava o id; o rótulo de UI passa para "inferência de modelo" sem inferência (SS-09) | Divergente |
| 23 | Ativação de perfil LoRA | Só registra log e devolve sucesso (SS-09) | Divergente |
| 24 | "Pipeline de treino real" in-server; endpoints de pretrain e LoRA | Alvos são pseudo-rótulos da mesma heurística do esqueleto; pretrain e LoRA reutilizam o job linear; o rank é só ecoado (SS-10) | Divergente |
| 25 | Treino offline com datasets públicos | Usa amostras sintéticas silenciosamente quando o dataset falta (SS-10) | Divergente |
| 26 | Salvar o contêiner no desligamento | Grava pesos recém-inicializados (SS-09) | Divergente |
| 27 | `wifi-densepose-nn`: três backends mais CUDA/TensorRT | Só ONNX e mock; o decode do tradutor devolve zeros (ML-12) | Doc à frente |
| 28 | Cog de pose: README diz runtime stub e encoder pré-treinado | O runtime carrega pesos treinados; os resultados registram encoder aleatório (ML-15) | Doc atrás |
| 29 | Cog de pose: confiança por quadro | Constante igual ao PCK@50 de validação (ML-15) | Divergente |
| 30 | Pose de produção | PCK@20 de cerca de 3% numa sessão de 30 minutos, contra meta de 35% (ML-15) | Consistente (documentado) |
| 31 | Cog de contagem: temperature scaling | A temperatura está no manifesto, mas nenhum código a aplica (ML-16) | Divergente |
| 32 | Cog de contagem: acurácia e K-fold | Split aleatório numa gravação contínua, violando o próprio protocolo anti-vazamento (ML-16, ML-04) | Divergente (metodologia) |
| 33 | Cog de contagem: "fusão limitada por min-cut" | Apenas truncamento por teto informado (ML-16) | Divergente |
| 34 | Cabeça de presença publicada com acurácia de triplet temporal | A ADR-298 registra que a cabeça é degenerada e que triplet é métrica de representação; o modelo publicado é rejeitado pelo loader de referência (ML-06, PY-15) | Divergente |
| 35 | Prova de treino (trust kill switch) | Não há hash esperado commitado (resultado SKIP); depende de feature fora do CI (ML-08) | Doc à frente |
| 36 | O README do crate de treino diz integração com crates ruvector | Só compila com a feature tch (ML-01) | Doc à frente |
| 37 | DDD de treino cita dataset Wi-Pose e adaptador de professor | Inexistentes; módulos apontados ficam em outro crate (ML-01) | Doc à frente |
| 38 | MERIDIAN: adaptação em tempo de teste | Gradiente falso anterior foi removido; sem ganho de PCK medido (ML-09) | Consistente (corrigido e declarado) |
| 39 | OccWorld elimina overhead de IPC | Sem bench, sem checkpoint treinado, sem consumidores (ML-19) | Não verificável |
| 40 | Gate de release de modelo | O workflow só testa o checker; uploads ao Hugging Face são manuais (ML-06) | Doc à frente |
| 41 | AetherArena: "infra completa" e "board vazio" | O leaderboard está vazio segundo o STATUS, mas o ledger já tem 4 resultados MM-Fi sem hash de prova por linha; não há fluxo de submissão (ML-07, WM-24) | Divergente |
| 42 | AetherArena: "resultados assinados" | Apenas cadeia SHA-256; Ed25519 é "próximo hardening" (WM-24) | Doc à frente |
| 43 | Encoder "fundacional/universal" | MLP de pooling com cerca de 40 mil parâmetros treinado só em dados sintéticos (WM-03) | Divergente (nomenclatura) |
| 44 | F1 = 1,0 em presença em salas e chipsets novos (ADR-273) | Mundo sintético separável por construção; a ADR admite (WM-04) | Consistente (rotulado) |
| 45 | Redução de tráfego de pelo menos 70% (ADR-280) | Simulação com 1 região quente entre 20 (WM-09) | Divergente (rotulada como medição) |
| 46 | ESP32 HIL fecha lacuna de dados reais | Sem saída capturada (WM-02) | Não verificável |
| 47 | Fusão "real" de N modalidades (ADR-311) | Só presença escalar por contêiner (WM-11) | Doc à frente |
| 48 | Contrafactual usa hipóteses da fusão | Dependência declarada não usada; validação circular (WM-18) | Doc à frente |
| 49 | Calibração LoRA por sala com grandes ganhos | Testes com dados aleatórios; números de dataset de terceiros não reproduzidos (WM-25) | Não verificável |
| 50 | WiFlow-STD de terceiros com PCK@20 muito alto | O checkpoint publicado não reproduz; o retreino reproduz aproximadamente (ML-11, OP-16) | Consistente (refutação documentada) |
| 51 | Benchmark HOMECORE vs HA | Scripts de reprodução inexistentes; endpoints comparados diferem (ML-22) | Não verificável |
| 52 | `references/`: acurácia de detecção de cerca de 87% | É o AP@50 publicado no artigo; o código roda com dados aleatórios (PY-11, PY-20, UI-01) | Divergente |
| 53 | Serviço de pose v1 | Carregamento de pesos comentado; atividade pela norma de tensor; segmentação placeholder (PY-10) | Divergente |
| 54 | Ganho de desempenho Python versus Rust | Tempos de Python aproximados, sem benchmark reprodutível (PY-19) | Não verificável |
| 55 | ML de escombros e vitais "baseado em ONNX" (MAT) | A feature de ONNX não existe no `Cargo.toml`; só o fallback por regras roda; não há modelos (MB-09) | Divergente |

### 6.3 Segurança, assinatura e privacidade

| # | Alegação (fonte) | Evidência observada | Situação |
| --- | --- | --- | --- |
| 56 | Verificação de assinatura Ed25519 de módulos WASM (README do firmware, RVF) | O firmware verifica um digest SHA-256 sobre (chave pública ‖ região), forjável por quem conhece a chave; o builder deixa a assinatura zerada; o boot log documenta a verificação desligada (EH-02, FW-04) | Divergente |
| 57 | Transporte QUIC "autenticado e cifrado" | Só transições de estado; a configuração padrão usa chave de teste embutida e nível que aceita não autenticados (EH-15) | Divergente |
| 58 | RuField: eventos de campo assinados | Sem a variável de seed, usa uma seed de desenvolvimento fixa no código, marcada nos metadados (SS-19) | Divergente (mitigado por rótulo) |
| 59 | Certificado de sala com assinatura | MAC simétrico declarado como placeholder, com comparação não constante no tempo (SV-21) | Consistente (declarado) |
| 60 | Witness chain como "envelope assinado" (ADR-319) | Hashes sem chave nem assinatura (GV-02) | Doc à frente |
| 61 | Raiz sintética limita a cadeia a L0 | Não imposto estruturalmente; o nível vem do chamador (GV-02) | Divergente |
| 62 | Atestação com Ed25519 "drop-in" | Só existe MAC BLAKE3 simétrico; nenhum signer Ed25519 implementa o trait (GV-01) | Doc à frente |
| 63 | Gate de consumidor de certificado de capacidade | Checa apenas a presença da assinatura, não a validade (GV-05) | Divergente (risco de uso incorreto) |
| 64 | Campo de falso positivo "por 24 h" no certificado | Carrega a FPR do ledger (GV-05) | Divergente (rótulo) |
| 65 | Ledger de evidência: "registros nunca são promovidos" | A desserialização de campos privados permite forjar níveis via JSON (GV-03) | Divergente (fora da API) |
| 66 | Invariante: escore de risco de identidade nunca cruza a fronteira MCP (`verify`) | O servidor MCP rvagent expõe o escore numérico; o `verify` só faz grep em dois scripts (OP-13, OP-14) | Divergente |
| 67 | SECURITY.md: UDP em loopback por padrão | O probe do modo auto abre em 0.0.0.0 por alguns segundos; o servidor de calibração da CLI usa 0.0.0.0 e CORS permissivo (SS-01, SS-23) | Divergente |
| 68 | Início de gravação | Usa id do cliente no caminho sem sanitização e com escopo de leitura; provável path traversal (SS-12) | Divergente (inferido por leitura) |
| 69 | Rotas DELETE de modelos e gravações | Sintaxe de parâmetro provavelmente incompatível com a versão do roteador; nenhum teste exercita DELETE (SS-09, SS-12) | Divergente (inferido) |
| 70 | Catálogo de borda com SHA-256 | Informa o hash, mas não o compara com valor fixado ou assinado (SS-22) | Doc à frente |
| 71 | HOMECORE: autenticação corrigida após auditoria | Corrigida, mas mantém um modo de migração que aceita qualquer token não vazio (GV-20) | Consistente com ressalva |
| 72 | API MAT | Sem autenticação; teste de integração diz cobrir a API mas não a toca (MB-07) | Divergente |
| 73 | nvsim-server | CORS curinga com fallback permissivo, sem autenticação, bind 0.0.0.0 no Docker (ML-20) | Divergente (postura) |
| 74 | Modo de privacidade remove biometria | Remove por nome de chave; estados inferidos de saúde continuam saindo (SS-15, HC-14) | Consistente com ressalva |
| 75 | UI web e HOMECORE: token protegido | Token em `localStorage`; no exemplo HOMECORE também por query string e com fallback literal; relay LiDAR com token na URL (UI-03, UI-14, HC-13, HC-18) | Divergente em relação às boas práticas |
| 76 | WiFi VEIL "protege você" | Números de um modelo sintético L0; firmware build-only com dezenas de TODO(hw) (FW-18, GV-16, GV-17) | Consistente (rotulado) com marketing acima da evidência |
| 77 | "Happiness vector" sem dados pessoais | Infere estado emocional de pessoas presentes (UI-19) | Divergente |
| 78 | Threat model do forecast: gate de dependências | Ferramentas de auditoria não estavam instaladas (GV-20) | Doc à frente |

### 6.4 Implementação versus documentação (stubs, órfãos, defasagem)

| # | Alegação (fonte) | Evidência observada | Situação |
| --- | --- | --- | --- |
| 79 | ADRs 029, 030, 134, 135, 304, 305, 317–321, 323, 368 "Proposed/planned" | Há código implementado e testado (§4.1, §4.8) | Doc atrás |
| 80 | ADR-164 | O próprio corpus estima cerca de 70% de ADRs não plenamente implementadas e status só indicativo (PY-15) | Consistente (autoauditoria) |
| 81 | ADR-135: escore e evento de deriva, flag de obsolescência | Não existem no código (SV-06) | Doc à frente |
| 82 | ADR-021: CUSUM e armazenamento em camadas com TTL | Só z-score e ring buffer (SV-17) | Doc à frente |
| 83 | Sanitização de fase "guiada por qualidade" | Cai no unwrap padrão (SV-02) | Doc à frente |
| 84 | Comentário do runner de prova de CIR ("não implementado") | CIR implementada e hash preenchido (SV-07) | Doc atrás |
| 85 | Documentação do Docker: modo auto falha sem hardware | O código serve simulado e promove depois (SS-02, SS-24) | Doc atrás |
| 86 | DDD do sensing-server | Aponta para módulos órfãos e rotas inexistentes (SS-09, SS-12) | Doc à frente |
| 87 | Motor governado (comentário de Cargo) | Só suprime amplitudes brutas; demais derivados saem sem governança (SS-07) | Doc à frente |
| 88 | Primitivas semânticas publicadas em HA, Matter e Apple | Só MQTT com configuração padrão; flags de zonas e limiares não chegam ao binário (SS-17) | Doc à frente |
| 89 | Ponte Matter / guia do HA "testado contra Matter" | Feature vazia; o binário rejeita as flags Matter (SS-18, HC-14, PY-17) | Divergente |
| 90 | Introspecção com casamento DTW | Biblioteca instanciada vazia (SS-13) | Doc à frente |
| 91 | CLI MAT: varredura, triagem e exportação | Sem flag de simulação, informa que não há hardware; dados fixos de demonstração (SS-23) | Doc à frente |
| 92 | "60 módulos WASM" carregáveis | Só dois conjuntos de entry points exportáveis (EH-01) | Divergente |
| 93 | Script de upload citado no README de edge modules | Não existe (EH-01) | Doc à frente |
| 94 | ADR-041 "validado em hardware" | Orçamentos por módulo continuam CLAIMED; medições são de host (EH-01, EH-12) | Divergente |
| 95 | Suporte a Intel 5300/Atheros/Linux no crate de hardware | Features sem código; leitura ao vivo retorna "indisponível" (EH-14, MB-08) | Doc à frente |
| 96 | "Sem dados mock" no crate de hardware | Parsers não fabricam dados, mas há cinco simuladores marcados SYNTHETIC (EH-16) | Consistente, com afirmação ampla demais |
| 97 | Desktop e firmware: upload WASM | Portas e formatos diferentes (EH-02, UI-12) | Divergente (provável incompatibilidade) |
| 98 | Identificador de pacote de saída WASM | Rótulos diferentes entre firmware e parser (EH-14, FW-01) | Divergente |
| 99 | wifiscan: unsafe proibido; atenção via biblioteca; "GNN" | Unsafe negado com módulo FFI liberado; dependência inexistente; implementação é Pearson + BFS (EH-20) | Doc à frente |
| 100 | Firmware: injeção de NDP e gestão de slots TDM | Placeholder sem chamadores; slots só carregados da NVS (FW-01, FW-08) | Doc à frente |
| 101 | Tabela de protocolos e orçamento de memória do README/DDD do firmware | Desatualizados em relação ao código e ao CI (FW-19) | Doc atrás |
| 102 | WASM tier 3 funcional | Fonte do interpretador baixada sem hash fixado; build sem WASM no relatório físico (FW-04) | Divergente |
| 103 | Extensões C6 (802.15.4, TWT, hibernação, HE-LTF) | 802.15.4 bloqueado, TWT nunca aceito, hibernação não medida, HE-LTF só em outra versão do IDF; "não pronto para release" (FW-10) | Doc à frente |
| 104 | MAT: rastreamento com ciclo de vida | O ciclo de varredura não chama o rastreador (MB-05) | Doc à frente |
| 105 | MAT: repositórios do DDD, perfil de escombros, TDoA/UWB, varredura por zona | Repositórios ausentes; perfil stub; TDoA/UWB não usados; buffer único compartilhado por zonas (MB-01, MB-04) | Doc à frente |
| 106 | MAT: flags portable, distributed, drone | Sem uso no código (MB-01) | Doc à frente |
| 107 | MAT: exemplo de início rápido | Falha por não inicializar o evento (MB-01) | Divergente |
| 108 | BFLD: sensoriamento por beamforming | Não decodifica BFI; matriz opaca; captura "Proposed"; pipeline não usado pelo servidor (MB-11, MB-12, PY-03) | Doc à frente |
| 109 | RuField "não ligado ao servidor" (doc do crate) | O servidor já o liga (MB-18, SS-19) | Doc atrás |
| 110 | Fusão multivista com atenção "aprendida" | Projeções identidade, sem treino (MB-21) | Divergente |
| 111 | Cog-ha-matter: broker embutido, limiares aprendidos, federação, OTA | Nada disso existe; o publisher sobe sem fonte de dados (HC-16) | Doc à frente |
| 112 | READMEs do HOMECORE (scaffold, contagem de testes, assinatura "futura") | Defasados em relação ao código, ora para mais, ora para menos (HC-01, HC-08, HC-13) | Doc atrás |
| 113 | HOMECORE automação: gatilhos, ações e formato YAML do README | Diferem do aceito; espera por gatilho é stub (HC-04) | Doc à frente |
| 114 | HOMECORE recorder: schema idêntico ao do HA e busca semântica | Subconjunto de quatro tabelas; "semântico" é hash sem semântica (HC-06) | Divergente |
| 115 | HOMECORE assist: índice HNSW, provedores de voz, runner de LLM | Varredura exata; provedores desabilitados; runner inexistente (HC-09, HC-10) | Doc à frente |
| 116 | Gateway do HOMECORE "não compilado" vs ADR "compilado e testado" | Afirmações inconsistentes entre si (HC-13) | Divergente |
| 117 | Desempenho declarado do HOMECORE | O README admite que não há benchmarks por crate (HC-01..06) | Não verificável |
| 118 | Blueprints e Lovelace | Dependem de entidades e atributos não publicados; contagem de entidades diverge (HC-15, UI-15) | Divergente |
| 119 | Guia HomePod: validado em C6 real | Sem testes, logs ou artefatos reproduzíveis (HC-12) | Não verificável |
| 120 | Observatório: módulos de painel e vitais "fisiologicamente acurados" | Seis módulos órfãos; vitais sintéticos (UI-08) | Divergente |
| 121 | Pose-fusion | CNN com pesos aleatórios; CSI do modo demo derivado do vídeo (UI-09) | Divergente |
| 122 | Demos three.js "guiadas por ESP32 real" | Esqueleto vem da câmera; amplitude sintetizada pela ponte (UI-18) | Divergente |
| 123 | Edge App Store: "60+ algoritmos" | 1 executa, 6 simulados, 1 só em malha (UI-11) | Divergente |
| 124 | Desktop: páginas "Done"; biblioteca de módulos | README diz WIP; avaliações e downloads fictícios (UI-12) | Divergente |
| 125 | SPA: aba Hardware com "CSI em tempo real"; métricas de desempenho | CSI aleatório; métricas de literatura fixas no HTML (UI-01) | Divergente |
| 126 | Diagrama de arquitetura de frontend | Mostra login e calibração inexistentes na SPA (UI-20) | Doc à frente |
| 127 | Pacote Python: tipos de pose de 17 pontos; status "Production/Stable" | Só contêineres sem inferência; ADR "Proposed"; docstring de scaffold (PY-01) | Divergente |
| 128 | Meta-pacote `ruview` com cliente de sensing exportado | O símbolo não é reexportado (PY-01) | Divergente |
| 129 | Shim Python da raiz e pyproject 1.2.0 | Aponta para diretório inexistente e scripts quebrados; dois manifestos com o mesmo nome (PY-01, PY-10) | Divergente |
| 130 | `deploy.sh` (Terraform/EKS) | Diretórios referenciados não existem (OP-18) | Divergente |
| 131 | Stack Prometheus/Grafana | Referencia arquivo de regras inexistente; métricas não existem no código atual (OP-17) | Divergente |
| 132 | Arquivo de "baseline" de benchmark na raiz | Telemetria de campo com duplicatas, sem referência no código (OP-16) | Divergente (nomenclatura) |
| 133 | Hook pré-saída do claim-check | Não existe nas configurações (OP-04) | Doc à frente |
| 134 | Versões fixadas de harness, plugin e guarda-chuva | Desalinhadas; MCP do plugin sem versão (OP-01, OP-12) | Divergente |
| 135 | Relatórios de QE: testes Rust fora do CI e tamanho do monolito | O CI atual já roda os testes; o monolito cresceu (OP-22) | Doc atrás |
| 136 | Numeração de ADRs (Veil, harness, ADR-150, ADR-263) | Referências inconsistentes e número duplicado (GV-16, OP-02) | Divergente |

### 6.5 Testes, CI e evidência

| # | Alegação (fonte) | Evidência observada | Situação |
| --- | --- | --- | --- |
| 137 | PROOF.md: workspace com milhares de testes e zero falhas | Não verificado (somente leitura); contagens estáticas não garantem que os testes passam | Não verificável |
| 138 | `verify`: "todas as fases passam" | Sai com código 0 mesmo com fases em SKIP (OP-14) | Divergente |
| 139 | Witness bundle autoverificável | O script de verificação confere sobretudo presença de arquivos e greps em resumos autodeclarados; sem assinatura (OP-14, GV-18) | Doc à frente |
| 140 | Captura ESP32 da harness rotulada MEASURED | Mantém o rótulo mesmo com pacotes marcados como sintéticos (OP-08) | Divergente |
| 141 | Fuzzing de parsers do firmware e matriz de 14 configurações | Três alvos de fuzz e subconjunto da matriz no CI (FW-14) | Doc à frente |
| 142 | Testes host do kernel adaptativo do firmware | Nenhum workflow os executa (FW-08) | Doc à frente |
| 143 | Testes de features do CI principal (`--no-default-features`) | Testes de tch, servidor HAP, Wasmtime, ruvector e reconhecedor semântico ficam de fora (ML-01, HC-08, HC-09, HC-11) | Consistente com ressalva |
| 144 | App mobile com centenas de testes e fluxos e2e | Jest fora do CI; arquivos Maestro com 0 bytes (UI-13) | Doc à frente |
| 145 | Relatório de testes da SPA "production-ready" | Revisão manual autodeclarada; só 5 arquivos de teste da SPA no CI (UI-01) | Doc à frente |
| 146 | Contagens de testes em READMEs e ADRs | Divergem das contagens atuais (para mais e para menos) em vários crates (WM-*, OP-13, HC-*) | Doc atrás |
| 147 | Experimentos de BFI | A aceitação (21/21) não se repetiu nas mesmas condições (0 e 1 relatórios) (FW-16) | Consistente (documentado) |
| 148 | LSTM/GRU de BFI/CSI aprendem marcha | Ridge estático empata e embaralhar a ordem temporal não reduz acurácia (FW-17) | Consistente (resultado negativo declarado) |
| 149 | Recuperação esparsa de subportadoras | Reconstrói pior do que não recuperar (EH-08) | Consistente (resultado negativo declarado) |
| 150 | HNSW quantizado supera float | Não superou com recall igual (MB-20) | Consistente (resultado negativo declarado) |
| 151 | Evidência em hardware real da frota (pareamento de quadros, ocupação fail-closed) | Medida, mas explicitamente sem alegação de acurácia (SV-23, FW-03) | Consistente |
| 152 | Dados de prova determinística | Declaradamente sintéticos; hashes provam determinismo, não acurácia (PY-07, SV-06) | Consistente |
| 153 | Tolerâncias FTM medidas em bancada (survey) | Dados brutos não localizados nesta análise (WM-15) | Não verificável |
| 154 | Evidência HTTPS de produção do Cognitum Spaces | Sem artefato verificável (WM-22) | Não verificável |
| 155 | Guarda de dados CSI: incidente ainda no tree | No clone raso, nenhuma captura rastreada; comentário provavelmente desatualizado (GV-19, OP-14) | Não verificável |

---

## 7. Mapeamento para os módulos M01–M16 da WiFi Spatial Intelligence Platform

O estado atual da plataforma foi lido (somente leitura) em `docs/REQUIREMENTS_TRACEABILITY.md` (catálogo M01–M16 v3.0 e gate integrado de 15/10/2026) e em `docs/FUNCTIONAL_SPEC.md` (versão 1, 15/10/2026). O espírito das recomendações abaixo é preservar L0_SYNTHETIC/IMPLEMENTED_SYNTHETIC, não alegar validação real e reimplementar de forma independente.

### 7.1 Visão geral

| Módulo | Referências principais no RuView | Maturidade no RuView | Estado na plataforma (rastreabilidade) | Direção sugerida |
| --- | --- | --- | --- | --- |
| M01 Presence | SV-04, SS-03, FW-03, EH-03, WM-11, WM-18, EH-20, PY-09 | Implementado e testado (heurístico); invariante medido em ESP32-C6; acurácia não medida | IMPLEMENTED_SYNTHETIC (domínio, agregados, dashboard; sem referência real) | Fortalecer com fusão por variância inversa e UNKNOWN, explicação contrafactual e gerador físico, tudo L0 |
| M02 Occupancy | SV-08, SS-04, ML-16, WM-11, WM-12, MB-05, EH-05, FW-03 | Implementado e testado (heurístico, eigenmodos); modelo aprendido quase degenerado | IMPLEMENTED_SYNTHETIC (contagens L0; contagem null preservada) | Contagem como distribuição com faixa e confiança; invariante presença → contagem; agregação por frescor |
| M03 Entries/exits | SV-10, WM-12, MB-05, EH-05 | Bibliotecas testadas; rastreador MAT não integrado; fluxo direcional sem dados | PARTIAL (deltas líquidos; sem cruzamentos individuais) | Trilhas pseudônimas com adjacência entre zonas no sintético, gerando eventos sem identidade |
| M04 Respiratory rate | SV-05, SV-16, SV-18, SS-05, FW-02, MB-02, PY-02 | Três implementações divergentes; sintético; nenhuma sessão MEASURED | BLOCKED (sem estimador) | Manter BLOCKED para dados reais; demonstrador sintético L0 só com decisão do proprietário; padrão de abstenção desde já |
| M05 Heart rate | SV-16, SS-05, FW-02, MB-02, PY-02 | Experimental, mais frágil que respiração; sintético | BLOCKED | Idem M04 |
| M06 Activity recognition | SV-03, SV-12, SS-11, EH-03..05, EH-09, FW-17 | Bibliotecas testadas; resultados negativos em BFI/CSI | PARTIAL (cenários de movimento; laboratório de movimento F3B IMPLEMENTED_SYNTHETIC; sentado/queda BLOCKED) | Espectrograma/BVP sintéticos e classificador simples avaliado com split por grupo e baseline |
| M07 Fall detection | FW-02, SV-22, SS-16, SS-17, EH-06, HC-14 | Sem validação; primitivas de saúde CLAIMED | BLOCKED | Manter BLOCKED; registrar protocolo de falso alarme e regra "auditar, não corrigir" (SV-22) |
| M08 RF fingerprints | SV-06, SV-08, SV-21, WM-13, WM-16, MB-20, ML-13, EH-20, FW-15 | Bibliotecas testadas com sintéticos; um registro MT7981 real | BLOCKED (sem CSI capturado) | Fingerprints sobre CSI do gerador físico, com baseline/deriva e certificado de sala L0 (decisão do proprietário); RSSI do host como laboratório |
| M09 Sleep quality | SV-15, SS-17, EH-06, EH-07, PY-18, OP-19 | Heurístico/pesquisa, sem validação | BLOCKED | Manter BLOCKED; política "só métricas e desvios, nunca diagnóstico" |
| M10 Apnea screening | SV-17, EH-06, PY-18, UI-16 | Heurístico, DATA-GATED | BLOCKED | Manter BLOCKED; no máximo "evento sinalizado" sintético rotulado |
| M11 17-keypoint pose | SV-10, SV-22, SS-08, ML-01, ML-03, ML-11, ML-15, UI-05, UI-17, PY-11 | Pose do servidor é procedural; cog com PCK@20 ≈ 3% | BLOCKED | Manter BLOCKED; adotar desde já métricas canônicas e contratos fail-closed |
| M12 Model lab/CSI/LoRA/RVF | ML-02..08, ML-21, OP-05, FW-17, WM-03, WM-04, SS-09, SS-10, EH-12, GV-08 | Infraestrutura de avaliação madura; treino fora do CI; modelos fracos | PARTIAL (`models` indisponível; laboratório F3B IMPLEMENTED_SYNTHETIC; jobs F4 PARTIAL) | Gates de split, baseline, release e claim; ledger de experimentos; witness do gerador |
| M13 Home automation/hooks | HC-04, HC-08, HC-14, SS-16, SS-17, MB-15, GV-06, GV-07, HC-11, HC-17 | MQTT/HA maduro com CI e broker real; HOMECORE alfa; Matter inexistente | Catálogo: UNVERIFIED; gate integrado: regras F5 PARTIAL em dry-run (`domain/rules.py`, `rule_contracts.py`, migração 0005, `automation-panel.tsx`); RBAC/consentimento/webhook pendentes | Discovery MQTT em dry-run, modos de execução limitados, gate por classe de risco e intents com recibos |
| M14 Multimodal RF world model | WM-01..09, WM-13, WM-18, SS-07, MB-21, EH-21, ML-19, ML-20 | Bibliotecas puras testadas; nada ligado ao runtime | PARTIAL (laboratório 2D sintético; sem fusão; F7) | Gerador físico, ontologia, gêmeo RF, Gaussianas e HAL como portas, todos L0 |
| M15 Governed evidence/privacy | GV-01..20, SS-02, SS-15, MB-11..13, MB-18, WM-08, WM-17, WM-21, OP-04, OP-14, PY-07, PY-15 | Espinha de governança testada, mas não ligada ao servidor ao vivo | PARTIAL (contratos, auth, auditoria e backup; consentimento, RBAC real e witness não implementados) | É o maior reaproveitamento conceitual (detalhado em 7.2) |
| M16 Operator onboarding/calibration | SV-06, SV-20, SS-06, SS-21, FW-06, FW-07, WM-14, WM-15, WM-20, MB-21, OP-07 | Bibliotecas testadas em sintético; onboarding USB com evidência física | PARTIAL (bootstrap e guias; calibração física e onboarding de dispositivos pendentes) | Assistente sintético: baseline, âncoras, GDOP/CRB, checador de configuração, doctor e OOD com certificado |

Relacionado à fase F6 (pacotes; `domain/packet_lab.py` em PARTIAL, offline): EH-14, EH-16, FW-01, FW-14 e SS-01 são as referências de parser que nunca fabrica dados, codec versionado com CRC e flag SYNTHETIC e fuzz de parsers.

### 7.2 Detalhamento por módulo

#### M01 — Presence

- **Referências RuView:** escore composto com EMA e histerese (SV-04); inferência por nó separada do agregado de sala, com debounce temporal (SS-03); invariante fail-closed (FW-03); fusão por variância inversa com UNKNOWN (WM-11); explicação contrafactual (WM-18); RSSI do host (EH-20, PY-09).
- **Maturidade lá:** heurísticas testadas; nenhuma acurácia medida contra referência.
- **Na plataforma hoje:** IMPLEMENTED_SYNTHETIC (presença e intervalos históricos L0; sem referência real).
- **Lacunas e oportunidades sem custo:** várias fontes sintéticas por zona fundidas por variância inversa, com UNKNOWN em conflito; separar inferência por nó de agregado de sala; gerador físico (WM-07) para presença com Doppler emergente. Tudo continua L0.

#### M02 — Occupancy

- **Referências RuView:** eigenmodos com limiar de Marchenko–Pastur (SV-08); min-cut e agregação por frescor (SS-04); formato de contagem como distribuição com faixa, confiança e fusão por produto de especialistas (ML-16); trilhas (WM-12, MB-05); KPIs de varejo e edifícios (EH-05).
- **Maturidade lá:** heurísticas testadas; modelo aprendido quase degenerado.
- **Na plataforma hoje:** IMPLEMENTED_SYNTHETIC (contagens e agregações L0; contagem null não é zero).
- **Lacunas e oportunidades:** emitir distribuição de contagem no contrato 2.0.0 (aditivo); invariante "presença falsa implica contagem zero" nos validadores; KPIs (fila, permanência) sobre eventos sintéticos.

#### M03 — Entries/exits

- **Referências RuView:** ciclo de vida de trilha (SV-10, MB-05) e rastreamento pseudônimo com bloqueio de transição entre zonas não adjacentes e recusa de atribuição ambígua (WM-12).
- **Maturidade lá:** bibliotecas testadas, não integradas.
- **Na plataforma hoje:** PARTIAL (variações líquidas, sem detectar cruzamentos individuais).
- **Lacunas e oportunidades:** com a verdade do gerador (que conhece entradas e saídas), implementar trilhas anônimas por zona com grafo de adjacência derivado de uma ontologia (WM-10) e gerar eventos de entrada/saída L0 avaliados contra a verdade. Re-identificação continua BLOCKED.

#### M04 — Respiratory rate

- **Referências RuView:** pipeline ADR-021 (SV-16), FFT com abstenção (SS-05), firmware (FW-02), MAT (MB-02), bindings (PY-02), Fresnel (SV-05) e avaliação graduada (SV-18).
- **Maturidade lá:** três implementações divergentes, validação só sintética, nenhuma sessão MEASURED.
- **Na plataforma hoje:** BLOCKED (nenhum estimador; dados, referência e estimador pendentes; F4).
- **Lacunas e oportunidades:** manter BLOCKED para dados reais. Se o proprietário decidir, um demonstrador puramente sintético (tons conhecidos no gerador, estimador numpy/scipy, erro contra a verdade) pode existir como laboratório L0, nunca como capacidade de produto. O padrão de abstenção (SS-05) e o grau de evidência no construtor (SV-18) podem entrar no contrato já.

#### M05 — Heart rate

- **Referências RuView:** as mesmas de M04, com o agravante de que a FC por CSI comercial é mais frágil.
- **Maturidade lá:** sintética e experimental.
- **Na plataforma hoje:** BLOCKED.
- **Lacunas e oportunidades:** idem M04, com prioridade menor.

#### M06 — Activity recognition

- **Referências RuView:** espectrograma e BVP (SV-03), gestos por DTW (SV-12, EH-03), classificador adaptativo (SS-11), verticais (EH-04, EH-05), aprendizado adaptativo (EH-09) e resultados negativos de LSTM/GRU (FW-17).
- **Maturidade lá:** bibliotecas testadas; sem consumidores ao vivo; evidência negativa em dados reais.
- **Na plataforma hoje:** PARTIAL. Os cenários de movimento não são predição. O laboratório de movimento F3B (`domain/motion.py`, `application/model_lab.py`) está IMPLEMENTED_SYNTHETIC, com sentado/queda/RF BLOCKED.
- **Lacunas e oportunidades:** classificador simples (scikit-learn) sobre features sintéticas, sempre com split por grupo/cenário, baseline trivial e gate de claim (ML-04, OP-05).

#### M07 — Fall detection

- **Referências RuView:** queda por "aceleração" de fase no firmware (FW-02), física de pose que não força pose prona a ficar em pé (SV-22), evento MQTT de queda (SS-16), escore de risco de queda (SS-17) e skills médicas (EH-06).
- **Maturidade lá:** sem validação; termos de saúde CLAIMED.
- **Na plataforma hoje:** BLOCKED (sem detector; dados e protocolo de falso alarme pendentes).
- **Lacunas e oportunidades:** manter BLOCKED. Registrar no plano um protocolo de falso alarme e a regra de segurança "sobreposições conservadoras com regressão por caso crítico" (MB-03).

#### M08 — RF fingerprints

- **Referências RuView:**
  - baseline de sala vazia (SV-06) e campo persistente (SV-08);
  - certificado de impressão da sala (SV-21) e gêmeo com delta (WM-13);
  - memória/anomalia (WM-16), ANN com gate de recall (MB-20) e embeddings (ML-13);
  - RSSI multi-BSSID (EH-20) e fase cruzada entre cadeias (FW-15).
- **Maturidade lá:** bibliotecas testadas; validação sintética.
- **Na plataforma hoje:** BLOCKED (sem CSI capturado; dataset e calibração pendentes).
- **Lacunas e oportunidades:** se o proprietário aceitar fingerprints **sintéticos**, um pipeline baseline → deriva → certificado L0 com hash e expiração é viável já (numpy, SQLite, sqlite-vec). A fonte RSSI do host fica como laboratório opcional com nível de evidência próprio.

#### M09 — Sleep quality

- **Referências RuView:** deriva longitudinal (SV-15), primitiva "dormindo" (SS-17), skills de sono (EH-06, EH-07) e scripts (PY-18, OP-19).
- **Maturidade lá:** heurístico/pesquisa.
- **Na plataforma hoje:** BLOCKED.
- **Lacunas e oportunidades:** manter BLOCKED. Adotar a política "só métricas e desvios, nunca diagnóstico" e "mínimo de dias antes de alertar" no plano mestre.

#### M10 — Apnea screening

- **Referências RuView:** anomalias vitais (SV-17), skills médicas (EH-06), scripts e dashboards (PY-18, UI-16).
- **Maturidade lá:** DATA-GATED.
- **Na plataforma hoje:** BLOCKED (sem diagnóstico).
- **Lacunas e oportunidades:** manter BLOCKED. Se houver demonstração, apenas "evento sinalizado" sintético com aviso, nunca índice clínico.

#### M11 — 17-keypoint pose

- **Referências RuView:** métricas canônicas (ML-03), contratos fail-closed e 409 tipado (SS-08), física de pose (SV-22), rastreador (SV-10), cog de pose (ML-15), port WiFlow e reprodução (ML-11).
- **Maturidade lá:** pose do servidor procedural; modelo do cog com PCK@20 ≈ 3%.
- **Na plataforma hoje:** BLOCKED.
- **Lacunas e oportunidades:** manter BLOCKED. Vale preparar as métricas com normalização explícita e um schema de observação canônica, e proibir visualização de esqueleto que não seja rotulada como ilustração sintética.

#### M12 — Model lab / CSI / LoRA / RVF

- **Referências RuView:**
  - protocolos de split e baseline (ML-04);
  - claim gate por procedência (ML-05) e gates de release (ML-06);
  - witness do scorer (ML-07) e ledger de benchmark (ML-21);
  - gate de treino (OP-05), harness de validação honesta (EH-12) e scorecard pelo pior domínio (GV-08);
  - metodologia de holdout selado (FW-17).
- **Maturidade lá:** infraestrutura de avaliação madura; treino fora do CI; modelos fracos.
- **Na plataforma hoje:** PARTIAL. `models` responde indisponível; laboratório F3B IMPLEMENTED_SYNTHETIC; jobs F4 (`application/experiment_jobs.py`, migração 0006) em PARTIAL, com vitais, pose e sono BLOCKED.
- **Lacunas e oportunidades:** transformar a governança em código Python: relatório de avaliação Pydantic, split agrupado obrigatório, baseline obrigatório, rótulo de procedência, ledger append-only de experimentos e gate de pior domínio no `check.ps1`. Treino real só com autorização de expansão de IA.

#### M13 — Home automation / local hooks

- **Referências RuView:**
  - motor de regras com modos limitados (HC-04) e templates seguros ou DSL fechada (HC-05);
  - plugins WASM assinados (HC-08) e discovery MQTT do HA (SS-16, HC-14, MB-15);
  - primitivas (SS-17);
  - gate por classe de risco (GV-06) e intents com recibos (GV-07);
  - witness (HC-17) e HomeKit opcional (HC-11).
- **Maturidade lá:** caminho MQTT/HA com CI contra broker real; HOMECORE alfa; Matter inexistente.
- **Na plataforma hoje:** o catálogo registra UNVERIFIED; o gate integrado registra regras F5 em PARTIAL dry-run (`domain/rules.py`, `rule_contracts.py`, migração 0005, `automation-panel.tsx`), com RBAC, consentimento e webhook pendentes.
- **Lacunas e oportunidades:** adaptador MQTT discovery em dry-run com entidades L0 rotuladas; modos single/restart/queued/parallel; gate que nega ações acima de conveniência com evidência L0; recibos encadeados por hash para cada decisão de regra.

#### M14 — Multimodal RF world model

- **Referências RuView:**
  - contrato de quadro nativo (WM-01) e adaptadores (WM-02);
  - Gaussianas RF (WM-05) e gerador físico (WM-07);
  - plano de privacidade (WM-08) e ontologia (WM-10);
  - gêmeo (WM-13) e contrafactual (WM-18);
  - HAL (EH-21), fusão multivista (MB-21) e motor governado (SS-07).
- **Maturidade lá:** bibliotecas puras testadas; nada ligado ao runtime.
- **Na plataforma hoje:** PARTIAL (laboratório 2D sintético, sem fusão; F7).
- **Lacunas e oportunidades:** gerador físico (método das imagens + Fresnel) e ontologia como primeiros passos; gêmeo com delta para alertas de mudança; tudo como portas e adaptadores, L0.

#### M15 — Governed evidence and privacy

- **Referências RuView (as mais numerosas):**
  - proveniência e não promoção: máquina de estados de proveniência (SS-02, UI-02) e escada L0–L5 com "subir exige artefato" (GV-04, PY-15);
  - governança de evidência: ledger por contexto (GV-03), certificados (GV-05), witness (GV-02, HC-17) e atestação de sensor (GV-01);
  - privacidade: classes de privacidade e rebaixamento monotônico (SS-07, MB-11..13), modo de privacidade com allowlist (SS-15, GV-15) e plano de propósito × zona × retenção (WM-08);
  - exportação e memória: evidência JSONL com proof tag que só baixa (WM-21) e memória criptografada com apagamento em cascata (WM-17);
  - verificação: claim-check (OP-04), golden replay (PY-07, OP-14) e guarda de dados CSI (GV-19).
- **Maturidade lá:** testada como biblioteca; não ligada ao servidor ao vivo.
- **Na plataforma hoje:** PARTIAL (contratos, auth, auditoria e backup; consentimento, RBAC real e witness não implementados).
- **Lacunas e oportunidades (custo zero):**
  1. enum único de evidência e classe de privacidade no contrato 2.0.0, compartilhado entre Pydantic e Zod;
  2. golden replay do gerador no `check.ps1`;
  3. claim-check em CI e pre-commit;
  4. ledger e witness append-only no SQLite com Ed25519 opcional;
  5. serializador central com allowlist de campos por classe;
  6. ConsentMode/propósito no contrato (EH-18, WM-08).

#### M16 — Operator onboarding / calibration / verification

- **Referências RuView:**
  - baseline de sala vazia e níveis de autoridade (SV-06, SS-06);
  - matrícula por âncoras com banco STALE (SV-20);
  - posicionamento com pontos cegos (WM-14) e checador de configuração por distâncias (WM-15);
  - OOD com certificado (WM-20) e GDI/Cramér-Rao (MB-21);
  - onboarding por desafio com verificação de evidência fresca (FW-07);
  - provisionamento seguro (FW-06) e doctor estruturado (OP-07).
- **Maturidade lá:** testada em sintético; onboarding USB com evidência física.
- **Na plataforma hoje:** PARTIAL (bootstrap e guias; calibração física e onboarding de dispositivos pendentes).
- **Lacunas e oportunidades:** assistente no dashboard sobre nós sintéticos (posicionar → GDOP/CRB → baseline → âncoras → verificação), checador "warn-only" de configuração e um `doctor.py` estruturado. Tudo rotulado L0, sem hardware.

---

## 8. Licenças, terceiros e restrições de reutilização

### 8.1 Licença do RuView

- O repositório declara `MIT OR Apache-2.0` (`NOTICE`, `v2/Cargo.toml` com `license.workspace`), mas o arquivo `LICENSE` da raiz contém só o texto MIT ("Copyright (c) 2024 rUv"), uma inconsistência menor.
- Licenças próprias por pacote:
  - crates `homecore*`: `MIT`;
  - `harness/ruview`, `harness/ruview-umbrella`, `harness/homecore`, `harness/ruview-kernel`, `harness/wifi-densepose-sar`, `harness/wifi-densepose-privshield`: MIT;
  - `tools/ruview-mcp` (`@ruvnet/rvagent`) e `tools/ruview-cli`: Apache-2.0;
  - `wifi-veil`: LICENSE-MIT e LICENSE-APACHE próprios;
  - `references/`: MIT (2025).
- `v2/crates/ruview-auth` **não declara licença** no `Cargo.toml` (`publish = false`), o que é uma ambiguidade a observar.
- O README do crate BFLD diz "MIT", em conflito com a declaração do workspace.

### 8.2 Material vendorizado e de terceiros

| Material | Licença | Observação |
| --- | --- | --- |
| Patch CSI mt76 MediaTek (`firmware/openwrt-wn586x3/patches/1001-...`) | BSD-3-Clause-Clear | Listado no `NOTICE`; sem concessão de patentes; não linkado aos crates |
| Demais patches OpenWrt (placa, mt76-vendor, CSIdump) | GPL-2.0 / Apache-2.0 (fontes modificadas) | Declarados fora da licença da raiz |
| Patches do driver MT7927 (`tools/bfi/driver`) | BSD-3-Clause-Clear | LICENSE no diretório |
| Port WiFlow-STD (`v2/crates/wifi-densepose-train/src/wiflow_std/`, `benchmarks/wiflow-std/upstream`) | Apache-2.0 (upstream) | **Trabalho derivado ausente do `NOTICE`**; exigiria atribuição em qualquer reuso |
| WASM3 (baixado em build) | MIT | Não vendorizado; download sem hash fixado de fork não oficial |
| Pacotes WASM em `ui/pose-fusion/pkg/` | MIT / MIT OR Apache-2.0 | Binários pré-compilados commitados |
| Submódulos `vendor/rufield`, `vendor/ruvector`, `vendor/midstream`, `vendor/rvcsi`, `v2/crates/worldgraph`, `v2/crates/ruview-swarm` | Não verificadas | Vazios no clone |
| Crates `ruvector-*`, `midstreamer-*` (crates.io), `@metaharness/*` (npm), `wifi-veil` (git) | Não verificadas | Mesma autoria ou externas |

### 8.3 Dependências e ferramentas de terceiros relevantes

- **Permissivas** (pelas declarações públicas): axum, tokio, serde, clap, rustfft, ndarray, nalgebra, rapier3d, burn, Candle, ort/ONNX Runtime, safetensors, blake3, sha2, ed25519-dalek, chacha20poly1305, rumqttc, mdns-sd, wasmtime, MiniJinja, sqlx, LVGL, three.js, Lit, React, Tauri, Expo, TensorFlow.js, MediaPipe, Playwright, axe-core, Gradio.
- **Copyleft, usadas como ferramentas externas**: esptool, QEMU (fork Espressif), tshark/Wireshark, scapy e FeitCSI (GPL), além de openwifi e nexmon (AGPL/GPL) como plataformas-alvo de pesquisa. O layout do parser FeitCSI foi derivado da leitura de código-fonte GPL (MB-08): uma reimplementação deve partir de documentação pública do formato e manter separação de processo.

### 8.4 Dados, modelos e serviços

- **Datasets:**
  - MM-Fi: CC BY-NC, não comercial; contamina modelos derivados e o leaderboard AetherArena.
  - NTU-Fi HumanID: CC BY 4.0.
  - CSI-BFI-HAR: GPL-3.0.
  - BFId: acordo não comercial.
  - Widar3.0 e dataset WiFlow (Kaggle): licenças não verificadas.
- **Modelos** no Hugging Face (`ruvnet/wifi-densepose-pretrained`, `ruvnet/wifi-densepose-mmfi-pose`): licença declarada MIT para pesos de um repositório, mas não verificada; checkpoints podem ter termos distintos do código.
- **Serviços proprietários**: Cognitum (OAuth, Spaces, Seed, API de completions), APIs de fornecedores RF, buckets de nuvem e Hugging Face Spaces (camada gratuita).
- **Marcas e programas**: HomeKit, Siri e HomePod são marcas da Apple, e produto comercial exige MFi; Matter exige certificação CSA para produto comercial; assets Mixamo seguem os termos da Adobe; Google Fonts (OFL-1.1).

### 8.5 Restrições de reutilização para a plataforma

1. **Não copiar** código, patches, formatos de fio, constantes, limiares, textos de documentação, skills ou prompts do RuView. A licença permissiva permitiria derivação **com atribuição**, mas a política da plataforma é implementação independente a partir de normas, artigos e técnicas públicas.
2. **Registrar** em `docs/ORIGINALITY_REGISTER.md` a exposição adicional causada por esta análise (12 áreas, leitura estática do commit `a1ca023`) e **não alegar clean-room estrita** nem originalidade jurídica absoluta.
3. **Não usar** datasets ou pesos não comerciais (MM-Fi, BFId, checkpoints derivados) em qualquer caminho comercial.
4. **Ferramentas GPL** podem ser usadas como executáveis externos, sem linkagem nem importação em código distribuído sem análise jurídica.
5. **Evitar** dependência operacional de serviços proprietários (Cognitum, APIs de fornecedores, nuvem paga), conforme o requisito de custo zero.
6. O RuView permanece apenas como **laboratório legado opcional** (`SPATIAL_LEGACY_LAB_ENABLED=false` por padrão), importado sob demanda e nunca como dependência obrigatória do produto novo.

---

## 9. Lacunas desta análise

Todas as contagens de teste são estáticas: **nenhum teste, benchmark, script ou binário foi executado** (regra de somente leitura), e os resultados de CI não foram consultados. Os pontos não explorados ou só amostrados, por área:

- **Sinal e vitais:**
  - `v2/crates/wifi-densepose-sensing-server/src/vital_signs.rs` (só o cabeçalho); `firmware/esp32-csi-node/main/edge_processing.c` e `csi_collector.c`; o `StreamingEngine` completo;
  - `wifi-densepose-ruvector` e crates `ruvector-*`/`midstreamer-*`; bindings Python de vitais e meridian; pipeline de prova v1 (`verify.py`, `generate_reference_signal.py`);
  - corpos completos de `field_model.rs`, `multistatic.rs`, `pose_tracker.rs`, `cir.rs`, `longitudinal.rs`; ADRs 136–138, 142, 143, 152, 154, 323 em detalhe; CLI de calibração e crates de certificação/OOD.
- **Servidor de sensoriamento:**
  - internos de `ruvsense` e de `wifi-densepose-aether`; submódulos vazios (worldgraph, rufield, ruvector, midstream);
  - `ruview-auth` e `ruview-cognitum-spaces`; calibração, hardware, MAT e BFLD como dependências;
  - `main.rs` inteiro (amostrado); trainer, dataset e pipeline RVF em detalhe; publisher e discovery MQTT; registro semconv;
  - `ui/` como consumidora; dezenas de ADRs; workflows de CI; cog-ha-matter e homecore-server na imagem Docker; legado v1; guias operacionais.
- **Edge e hardware:**
  - DSP dos tiers 0–2 do firmware, componente wasm3 e OTA; cadeia de build OpenWrt;
  - decodificadores de fornecedores e allowlist UDP no servidor; corpo algorítmico dos cerca de 65 módulos de borda e testes de vendor;
  - várias ADRs (041, 153, 264–269, 296 e outras); benchmarks de transporte e Realtek; helper Swift do macOS e adaptador Linux;
  - outros runtimes WASM do monorepo; decodificador Python legado; crate MAT por trás dos bindings.
- **Firmware:**
  - crates host correspondentes (hardware, mtk-bridge, bfld, wasm-edge, privshield); várias ADRs só por nome; scripts QEMU e de fase em detalhe;
  - LP-core, display, payloads da ponte de enxame, cenários do mock e API host WASM em detalhe;
  - pesquisa e HDL do WiFi Veil, harness e console; documentos adicionais de `bfi_learning`;
  - `release_bins` e corpus de fuzz (binários não inspecionados); patches de terceiros não lidos linha a linha.
- **ML e treino:**
  - crates `ruforecast` e `wifi-densepose-physics` em detalhe; consumo do aether no servidor;
  - calibração e Space do AetherArena; scripts de reprodução do WiFlow; scripts de treino reais dos artefatos entregues; bindings PyO3;
  - várias ADRs (015, 016, 020, 023, 024, 027, 031, 079, 100–103, 145–152, 155, 173, 175, 185, 291, 298, 348); pesquisa de sensores quânticos; benches;
  - repositórios externos no Hugging Face (não acessados); workflows de nvsim, forecast, bench e agente noturno.
- **MAT, BFLD, point cloud, RuField, RuVector:**
  - submódulo `vendor/rufield`; repositório `wifi-veil`; crate `wifi-densepose-privshield` (só parcialmente);
  - crates `ruvector-*`; dossiês de pesquisa BFLD e Soul; textos completos das ADRs 119–123, 141, 084, 156, 262, 031, 017; tutorial de tomografia coerente;
  - blueprints BFLD e workflow de integração MQTT; CLI, WASM e bindings Python do MAT; handlers, websocket e DTOs do MAT; resultados numéricos de benchmarks; comandos e skills do harness SAR.
- **World model:**
  - submódulos `ruview-swarm` e `worldgraph`; adaptadores da HAL; ledger `ruview-evidence`;
  - crates vizinhos (certify, policy, witness, attest, groundtruth, scorecard) lidos em outra área; certificado de calibração completo; HNSW interno; localização por campo;
  - scorer real do AetherArena e workflow; Space e fixtures; demo off-axis em detalhe; textos integrais das ADRs 301–315, 318–320, 149, 150, 381 (Apêndice A), 382; documentos de prova de capacidades; tokenizador, cabeças e pré-treino linha a linha.
- **Governança:**
  - corpo completo das ADRs 300–327, 271, 272, 282, 293, 295, 296, 299, 260; escadas de privacidade do BFLD e do RuField; assinatura do cog-ha-matter e de plugins;
  - dependências ontologia/OOD/calibração; implementação real do rebaixamento no motor; MQTT e Matter de privacidade; pesquisa do Veil;
  - threat model completo e crates de forecast; scripts de prova não executados; armazenamento de login e assinatura de cookies em detalhe; `NOTICE` versus esta área; licenças npm `@metaharness/*`.
- **HomeCore e integrações:**
  - textos completos das ADRs 115, 116, 125–133, 161, 162, 164, 165, 285; MQTT e primitivas do servidor (lidos só como interface); internos criptográficos do HAP e servidor de 1,5 mil linhas;
  - consultas do recorder; comandos WS completos; painéis da UI do HOMECORE; scripts Python HomeKit; código Swift do LiDAR; ferramentas e corpus do metaharness;
  - testes BFLD/HA; release checklist do cog; licenças efetivas no `Cargo.lock`/`package-lock.json`; benchmarks.
- **Interfaces:**
  - diagramas PNG grandes não abertos; CSS e HTML completos da SPA; `LiveDemoTab`, `PoseDetectionCanvas` e `SettingsPanel` só amostrados; runner manual de testes;
  - telas, WebView e triagem do mobile; views auxiliares e transportes do dashboard; descoberta, provisionamento e release do desktop;
  - scripts numpy de pesquisa; happiness vector e suíte médica em detalhe; demos three.js e WiFlow em detalhe; backends que definem o contrato; ADRs da área; workflows de Pages.
- **Operador de IA:**
  - metaharness homecore em detalhe; casos de teste individuais; agente noturno; prova v1 em detalhe;
  - scripts de física de pose, visual teacher, zero-shot e GCP; scripts remotos e resultados JSON do WiFlow; relatórios de QE e tutoriais completos;
  - ADRs 182, 263, 265, 298, 299, 372–378; exportador OTLP; pacotes externos `@ruvnet/ruview-kernel` e `@metaharness/*`; relay do LiDAR e marketplace; resultados de CI.
- **Python, legado e documentação:**
  - DDDs de sinal, treino, hardware, servidor e MAT (só cabeçalhos); a maior parte das cerca de 319 ADRs (só status); análise de lacunas do corpus;
  - pesquisa BFLD, privacy-shield, soul, quantum, topological, arena, neural, beyond-sota e ticks SOTA (só índices); scripts numpy de pesquisa; especificação SPARC (só cabeçalhos);
  - documentação, scripts e testes do v1 (estrutura e contagem); serviços e tarefas de monitoramento do v1; fixtures golden não conferidas; benches Python;
  - `CHANGELOG.md` (só as primeiras linhas); seções de QEMU, point cloud, OccWorld, treino, câmera e MERIDIAN do user-guide; `readme-details.md` (parcial); implementação do rvCSI (submódulo vazio).

