# WiFi Spatial Intelligence Platform — Plano Mestre v4.0

**Atualizado:** 2026-10-15 (v4.0 acrescenta a seção 0A; seções 0–17 da v3 continuam vigentes)  
**Destino no IntelliJ:** `docs/PROJECT_MASTER_PLAN.md`  
**Repositório:** `matheussiqueira-dev/WiFi-Spatial-Intelligence-Platform`  
**Ambiente:** Windows / PowerShell / IntelliJ / Codex  
**Execução:** local-first, modo sintético inicial, **sem contratação de serviços pagos**  
**Natureza:** especificação executável, backlog, critérios de aceite e regras operacionais.

> **LEIA ANTES DE CODIFICAR.** Este documento substitui o plano v2.0 como referência normativa para a evolução do projeto. Os relatórios `docs/PROGRESS.md`, `docs/REQUIREMENTS_TRACEABILITY.md` e `docs/VERIFICATION_REPORT.md` registram fatos observados; nenhum status é validado somente por este plano. O usuário exige arquitetura própria e desenvolvimento *clean-room*: RuView é **referência de problemas e capacidades**, não dependência do produto final.

## 0. Princípios irrenunciáveis

1. **Originalidade verificável.** Não copiar/portar código, firmware, documentação expressiva, testes, nomes internos exclusivos, estrutura, algoritmos de implementação ou assets de RuView. Não remover avisos de licença de terceiros para reivindicar autoria. Uso de frameworks, fórmulas matemáticas públicas, normas e interfaces abertas é permitido conforme licenças e proveniência documentadas.
2. **Clean room de verdade, não cosmético.** Separar **especificação funcional** de **implementação**. Uma simples renomeação ou refatoração de RuView **não constitui** autoria independente. O histórico de exposição prévia ao código-fonte exige declarar a limitação de independência; se for necessária separação rigorosa, implementar por equipe/agente sem acesso ao código anterior, a partir de uma especificação funcional livre de detalhes proprietários. Não prometer “100% original” sem evidência jurídica/técnica.
3. **Produto independente.** Nenhum componente RuView (runtime, biblioteca, Docker image, SDK, plugin, modelo, formato interno) pode ser dependência obrigatória do sistema novo. A integração antiga F2, se existir, permanece **temporariamente isolada em laboratório legado**, desligada por padrão, apenas até migração segura, e deve ser removida do produto independente mediante validação dos novos provedores. Não copiar o pipeline upstream.
4. **Custo operacional obrigatório zero.** Sem serviços pagos, GPU em nuvem, licenças obrigatórias, assinatura de runtime ou hardware comprado sem nova decisão do usuário. O próprio Codex pode ter custo de acesso; não é dependência da plataforma.
5. **Privacidade e consentimento.** Sensing real somente em ambientes autorizados, com consentimento/aviso adequado, minimização, retenção e auditoria. Nada de vigilância clandestina, identificação biométrica por RF, rastreamento individual sem autorização, captura de credenciais ou bypass de controles de rede.
6. **Integridade científica.** Dados gerados = `L0_SYNTHETIC`. Dados gravados não viram automaticamente verdade validada. Resultados de presença, vitais, sono e pose devem informar evidência, incerteza e origem; não são diagnósticos clínicos nem alertas de segurança certificados.
7. **Proteger o que já funciona.** Antes de mudanças grandes, inventariar o MVP reportado, executar testes, registrar riscos, criar adaptadores e migrar em incrementos testáveis. Não apagar dados do usuário ou alterações não commitadas.
8. **Autonomia ampla, mas delimitada.** O agente está autorizado pelo usuário a operar no projeto local conforme a seção 3. Não é autorização para ignorar proteções do Codex, aprovar prompts por conta própria ou modificar recursos fora do workspace.

## 0A. Atualização v4.0 — produto completo primeiro, recorte regulatório por configuração

**Decisão do proprietário (15/10/2026):** construir todas as capacidades interessantes
que tenham funcionalidade real e decidir depois, por mercado, o que pode ser
comercializado. Para que essa decisão posterior seja configuração e não refatoração,
toda capacidade passa a ser registrada no **catálogo de capacidades**
(`apps/api/app/capabilities.py`, exposto em `GET /api/v1/capabilities`), com:

- `group` (A–D, abaixo), `status` (vocabulário da seção 8) e `evidence_ceiling`
  (maior nível de evidência que a implementação atual consegue produzir);
- `regulatory`: etiquetas de enquadramento — `LGPD_PERSONAL`, `LGPD_SENSITIVE`
  (LGPD art. 11), `ANATEL_RADIO` (homologação se hardware rádio for vendido),
  `ANVISA_SAMD` (software como dispositivo médico, RDC 657/2022), `NONE`;
- `requires_hardware`, `requires_consent` e `profiles`: perfis em que a capacidade
  pode ficar ligada (`lab`, `commercial-br`). O perfil ativo vem de
  `SPATIAL_CAPABILITY_PROFILE` (padrão `lab`).

O catálogo é declaração de intenção e de enquadramento, **não parecer jurídico**.
Etiquetas regulatórias são hipóteses de trabalho a revisar com especialista antes de
qualquer venda. Uma capacidade só muda de status quando o código e a evidência mudam.

| Grupo | Escopo | Exemplos | Pré-requisito para dado real |
|---|---|---|---|
| A — Rede | Telemetria e planejamento da própria rede | diagnóstico do enlace, análise de canais, comparação de pontos, mapa por ponto | Nenhum além do computador (agente Windows) |
| B — Ambiente | Sensoriamento RF de presença/movimento | presença, ocupação, entradas/saídas, impressão RF do ambiente | CSI (ESP32-S3 ou placa compatível) + consentimento |
| C — Saúde/segurança | Sinais fisiológicos e eventos de risco | respiração, frequência cardíaca, queda, sono | CSI + protocolo de validação; enquadramento ANVISA antes de alegação clínica |
| D — Identificação | Reconhecer indivíduos | reidentificação por marcha/assinatura RF | **BLOCKED**: princípio 5 continua vigente; só reabre por decisão explícita, com consentimento ativo por pessoa cadastrada, finalidade documentada e revisão LGPD |

Regras v4: (1) grupo A é a prioridade de funcionalidade real imediata, pois não depende
de compra; (2) grupos B/C podem evoluir em `L0_SYNTHETIC`, mas nunca exibem status
`VALIDATED_REAL_DATA` sem o protocolo de `docs/RF_VALIDATION_PROTOCOL.md`;
(3) capacidade nova sem entrada no catálogo não é considerada entregue;
(4) nenhum perfil comercial liga capacidade com etiqueta `ANVISA_SAMD` ou do grupo D.
Varredura passiva de redes vizinhas (grupo A) envia somente agregados por canal;
SSID, BSSID e qualquer identificador de terceiros são descartados no host.

## 1. Baseline: fatos reportados versus fatos verificados

**Informado pelo Codex nas sessões anteriores (ainda requer reexecução):** branch local `feat/platform-foundation`, implementação local em grande parte não commitada; MVP com FastAPI, SQLite, dashboard Next.js, Observatory 2D, WebSocket, oito cenários, seis sensores virtuais, controles e eventos `L0_SYNTHETIC`; F2 consumindo streaming RuView simulado com adaptador, histórico e reconexão; relatórios de 83 testes backend, 7 web e 2 E2E, lint, types, builds e auditorias sem falhas naquela execução.

**Último bloqueio concreto:** `docs/PROJECT_MASTER_PLAN.md` estava ausente; o agente interrompeu reconciliação. Um comando de lint Python falhou (`exit 1`), um teste analytics foi editado, e havia pedido de confirmação para `docker run --rm wifi-spatial-backend-verification-py313`. **Nunca presuma que esse teste Python 3.13 concluiu.** Os “68 warnings” na UI também não tiveram sua origem confirmada.

**Primeira tarefa obrigatória:** ler estrutura local, `git status --short`, staged/unstaged, `docs/PROGRESS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/VERIFICATION_REPORT.md`, `docs/SECURITY_REVIEW.md`, `docs/RUVIEW_INTEGRATION.md`, README, AGENTS/CLAUDE quando presentes. Não substituir conteúdo real por este resumo; marcar discrepâncias.

## 2. Objetivo do produto e fronteiras

Criar uma plataforma de sensoriamento espacial RF independente com coleta de dados consentida, processamento de sinais, classificação experimental de presença/movimento, mapas e analytics, modelos versionados, dashboard local e conectores físicos opcionais. Priorizar utilidade real, rastreabilidade e robustez, não semelhança estética nem interna com repositórios de referência.

**In scope agora:** simulação independente, eventos versionados, persistência, dashboards, testes, rotinas de captura e avaliação; analytics de presença/ocupação; arquitetura para ESP32 futuro. **In scope como pesquisa:** frequência respiratória/cardíaca, atividade, quedas, mapa RF, sono, apneia, 17 keypoints, RF multimodal, treinamento e plugins locais. **Out of scope até validação:** identificação individual, certificação médica, alegação de ver através de paredes como uma câmera, precisão clínica ou espacial sem dados de referência, vigilância sem consentimento.

## 3. Política de autonomia do Codex (aplicável ao workspace do projeto)

**Autorizadas sem solicitar confirmação repetitiva, desde que o ambiente de execução permita:**
- Ler/editar/criar/refatorar arquivos **dentro deste repositório**, incluindo documentação, testes, contratos e configs; executar testes, lint, typecheck, builds e scripts de diagnóstico.
- Instalar/atualizar dependências **gratuitas** do projeto usando lockfiles e gerenciadores existentes, após checar licença e segurança; criar venv/containers temporários e limpar apenas artefatos descartáveis criados pelo próprio agente.
- Executar `docker compose` local, `docker run --rm` para imagens do projeto, pytest, Playwright e verificações Python 3.13; reiniciar processos e reparar falhas, **sem apagar volumes persistentes**.
- Criar código e testes em pequenos incrementos; atualizar `docs/PROGRESS.md`, `docs/VERIFICATION_REPORT.md`, `docs/REQUIREMENTS_TRACEABILITY.md` e `docs/DECISIONS.md` ao final de cada marco.
- Repetir automaticamente comandos de teste cujo resultado falhou, após corrigir a causa, com limites razoáveis de tempo/recursos.

**Não autorizadas sem consentimento explícito adicional:**
- `git push`, publicação externa, criação de PR, tornar repositório público, deploy remoto, envio de amostras CSI ou dados pessoais para terceiros.
- `git reset --hard`, `git clean -fd`, `git checkout -- .`, apagar arquivos/volumes/bancos ou reescrever histórico; sobrescrever mudanças do usuário ou arquivos staged sem análise.
- Fazer compras, ativar serviços pagos, registrar cartão, criar contas externas, mudar permissões/segurança globais, instalar software global elevado, executar scripts desconhecidos de terceiros sem revisão.
- Ligar captura RF real ou transmitir comandos para dispositivos na rede sem verificar propriedade/autorização.
- Efetuar commits automaticamente **nesta fase**; preparar commits e sugerir divisão por escopo, mas aguardar autorização única do usuário para commitar. Push exige autorização separada.

**Como lidar com confirmações da ferramenta:** estas permissões documentam a intenção do usuário, mas **não alteram a política de aprovação do Codex/IntelliJ**. Se o IDE apresentar `Yes / Yes and don't ask again`, o usuário pode escolher a opção persistente apenas para prefixos confiáveis e restritos (ex.: comando exato de testes Docker). Não solicitar bypass geral ou `danger-full-access`. Se houver prompt para comando de baixo risco, informe a ação e prossiga tão logo o host autorize. Use presets de aprovação oficialmente suportados, jamais truques para suprimir guardrails.

## 4. Estratégia de separação clean-room e migração

1. Criar `docs/ORIGINALITY_REGISTER.md` com (a) requisitos formulados pelo proprietário; (b) fontes públicas não-código (artigos, normas, docs de APIs); (c) componentes terceiros e licenças; (d) exposição prévia a RuView; (e) compromissos de implementação independente.
2. Criar `docs/FUNCTIONAL_SPEC.md` em linguagem neutra, com entradas/saídas observáveis e critérios de aceite, **sem termos/estruturas próprias do RuView**.
3. Congelar interface da integração legada F2 como *legacy compatibility laboratory*, desativada por padrão. Seus testes podem servir para regressão de comportamento externo, mas não como base para copiar implementação. Mantenha atribuição e avisos até remover dependência.
4. Inventariar origem e licença dos arquivos existentes. Identificar o que foi escrito especificamente no projeto e o que foi derivado/gerado com dependências upstream. Não alegar originalidade plena retroativamente.
5. Implementar motor independente contra a especificação funcional, com testes formulados por comportamento e medidas físicas de referência. Não fazer traduções de código Rust/Python do upstream.
6. Introduzir provider novo `synthetic-native` como padrão. Migração gradual por feature flags: old provider apenas em ambiente de comparação interno; ao eliminar dependências, remover adapter/código upstream após verificar impacto e licenças.
7. Incluir `docs/THIRD_PARTY_NOTICES.md` e revisar LICENSE do projeto; documentar autoria humana/assistida por IA com honestidade. Um parecer jurídico seria necessário se a exigência for exclusividade patrimonial estrita.

## 5. Arquitetura alvo — monólito modular hexagonal

**Motivo:** o estágio local não justifica operar microsserviços. Hexagonal + DDD por bounded contexts permite posterior extração de serviços de alto throughput.

```text
RF emitters / authorized receivers / synthetic generator
                 ↓
Adapters (source: synthetic, ESP32 future, radar future)
                 ↓
Acquisition + clock alignment + quality / calibration
                 ↓
Signal Processing Core (segmentation, filtering, feature extraction)
                 ↓
Inference / Analytics (pluggable models + uncertainty)
                 ↓
Domain events + provenance + policy decision point
          ↙                      ↘
Durable storage / aggregates     Streaming gateway
          ↘                      ↙
                   FastAPI
                      ↓
           Next.js Observatory UI
```

**Bounded contexts e vocabulário próprio:**
- `Acquisition`: `MeasurementFrame`, `SourceEndpoint`, `CaptureSession`, `ClockReference`.
- `SignalQuality`: `QualityWindow`, `InterferenceAssessment`, `CalibrationProfile`.
- `SpatialState`: `SpaceZone`, `OccupancyEstimate`, `MotionEpisode`, `TransitionEvent`.
- `Inference`: `ModelArtifact`, `InferenceRun`, `PredictionSet`, `UncertaintyEnvelope`.
- `ObservationEvidence`: `EvidenceRecord`, `ValidationRun`, `SourceProvenance`, `ReferenceDataset`.
- `Automation`: `LocalRule`, `RuleEvaluation`, `ActionDispatch`.
- `Governance`: `ConsentGrant`, `RetentionPolicy`, `AccessPrincipal`, `AuditTrail`.

Use terminologia funcional própria, não uma renomeação mecânica dos nomes de RuView. Domínio desacoplado de HTTP, ORM, React e bibliotecas RF.

**Stack preferida:** Next.js + React + TypeScript strict + Tailwind + Recharts + Three.js opcional; FastAPI + Pydantic v2 + SQLAlchemy + Alembic; SQLite com WAL/backup para etapa local; NumPy/SciPy e PyTorch ou ONNX Runtime **somente quando houver um modelo compatível de licença adequada**. Comunicação WebSocket autenticada, contratos JSON Schema compartilhados. Docker Compose local e scripts PowerShell nativos. Rust opcional apenas após benchmark justificar partes críticas.

**Estrutura sugerida (adapte ao código local em vez de reorganizar por estética):**
```text
apps/web/src/{app,features,components,lib}
apps/api/app/{domain,application,ports,adapters,api,infra}
packages/contracts
services/{simulator,signal-lab,model-lab}
tests/{contract,integration,e2e}
docs/{architecture,validation,security,adr}
scripts/{dev,verify,backup}
```

## 6. Contratos e invariantes de dados

- `schema_version`, `event_id` idempotente, UTC time, sensor/source ID, room/zone ID, source modality, source provenance, evidence level, event type, measurement typed payload, algorithm/model version, quality measures, uncertainty, retention classification.
- Evidência: `L0_SYNTHETIC`, `L1_RECORDED_UNVALIDATED`, `L2_LIVE_UNVALIDATED`, `L3_REFERENCE_VALIDATED` (introduzir mapeamento compatível com contratos legados existentes e migração versionada; nunca quebrar eventos gravados).
- `ground_truth` sintético fica isolado de `predictions` e não pode ser usado como inferência para autoavaliar o próprio simulador.
- Não inventar frequências cardíacas, respiração, poses ou contagem de pessoas. Payload nulo/unknown quando evidência insuficiente.
- Proteger eventos sensíveis, definir IDs não pessoais por padrão, minimizar retenção de frames brutos.
- Versionar mudanças de schema e testar compatibilidade com SQLite existente e WebSocket.

## 7. Roadmap executável e critérios de aceite

### F0R — Auditoria e recuperação do baseline (bloqueio imediato)
**Tarefas:** instalar este MD; ler relatórios locais; identificar staged/unstaged, comparar testes reportados com execução atual; reproduzir falha lint Python; validar alterações de `apps/api/tests/test_analytics.py`; executar teste isolado Python 3.13 se imagem já existir e recurso local permitir; classificar warnings de IDE; mapear RuView incorporado e dependências originais; inventariar dados persistidos e backup.

**Aceite:** `docs/VERIFICATION_REPORT.md` contém comandos, exit code, ambiente, data, logs resumidos e problemas; `docs/REQUIREMENTS_TRACEABILITY.md` referencia arquivos/testes; nenhum dado existente perdido. Se a etapa requer confirmação host, sinalizar ação exata.

### F1R — Segurança, recuperação e estabilização
**Tarefas:** corrigir lint/deprecações TestClient/httpx (se confirmadas), backup SQLite consistente + restore em banco temporário, retenção/expurgo de eventos, origem e autorização de WebSocket, CORS restrito, proteção dos endpoints de escrita, CSP e segredos, timeout e cancelamento de streams, reconexão com backoff. Testes Chrome/Firefox/WebKit conforme instalação; acessibilidade teclado/foco/axe + inspeção manual assistiva quando disponível.

**Aceite:** todos os gates existentes passam; teste de restauração preserva payload; nenhum endpoint sensível aberto por padrão; falhas e browsers não executáveis documentados como `BLOCKED`, não como `PASS`.

### F2R — Especificação original e extração da dependência RuView
**Tarefas:** `ORIGINALITY_REGISTER`, `FUNCTIONAL_SPEC`, ADR da separação, inventário de licenças, novo contrato próprio, simulador independente determinístico, adapter legado isolado/desabilitado, testes de comparação comportamental não derivados do código-fonte. Substituir rótulos de UI que impliquem capacidades RuView como autoria do novo motor.

**Aceite:** modo padrão funciona sem instalar/rodar RuView; `docker compose` sem serviço RuView obrigatório; dashboard e eventos próprios operacionais; dependências restantes isoladas/documentadas.

### F3A — Advanced Spatial Analytics (próxima funcionalidade principal)
**API/serviços:** janelas 1 min/5 min/1 h/dia, séries históricas com timezone explícito, ocupação estimada por zona, duração de presença, agregações e transições; ingestão idempotente; ordenação temporal; intervalos de ausência; filtros por cenário/ambiente/sensor/provedor; cursores/paginação; exportação CSV/JSON com dados sintéticos explicitamente marcados; limites de consulta.

**UI:** dashboard analytics com taxa de eventos, ocupação no tempo, dwell estimado, eventos de entrada/saída apenas quando tecnicamente distinguíveis, timeline com filtros e playback 2D; estado vazio/erro e incerteza claramente exibidos.

**Testes:** datasets fixos com resultados esperados; reordenação e duplicação de eventos; timezones, DST, janelas limites, desconexão, ausência de frames, backpressure; backend + web + E2E sem stubs enganosos.

**Aceite:** usuário escolhe cenário, vê eventos normalizados e persistidos, filtra período, reproduz histórico e exporta dataset reproduzível. Nenhuma identidade inventada.

### F3B — Motion & RF baseline research
**Tarefas:** extrair features temporais com janelamento; classificador baseline treinável em dados sintéticos separados; classes `walking`, `sitting`, `stationary`, `unknown`, `possible_fall` apenas se sinais pertinentes; RF fingerprint baseline, comparação de distribuição e anomalia de ambiente, sem afirmar qual objeto mudou. Registrar matriz de confusão, falso positivo, rejeição por baixa qualidade.

**Aceite:** cada predição identificada com modelo, versão, referência e limitação. Avaliações sintéticas nunca divulgadas como acurácia real.

### F4 — Laboratório de IA e modelos experimentais
**Tarefas:** registro e checksum de modelos próprios/de terceiros; licença; datasets rotulados, versionamento, train/val/test por sessão/participante quando aplicável; job queue com recursos limitados; métricas de presença, atividades, vitais e pose; ONNX quando compatível; RVF/LoRA apenas caso especificação/licença permita implementação independente, sem forçar formatos exclusivos upstream.

**Pesquisa:** estimativa de respiração/HR, 17 keypoints, queda e sono/apneia **não diagnósticos**. Desabilitar alegações clínicas e alertas críticos até validar contra referências adequadas.

**Aceite:** um pipeline reproduzível de baseline demonstra treino, inferência e avaliação; resultados com incerteza e evidência, não apenas gráfico animado.

### F5 — Automações locais e governança
**Tarefas:** regras por evento com DSL limitada e execução sandbox; webhook local autenticado e allowlist; audit trail, RBAC local, autorização por ambiente, consentimento, retenção, export/delete; integração com Home Assistant apenas via protocolos públicos; plugins Wasm assinados opcionais com políticas de capability.

**Aceite:** criar e revogar automação; simular trigger; logs seguros; sem execução arbitrária de código.

### F6 — Hardware readiness
**Tarefas:** documentação ESP32 CSI de interfaces públicas; protocolos abertos e própria implementação de firmware sem copiar RuView; teste parser/fuzzing; pairing e autorização de dispositivo, integridade, timestamp, canal e sensor placements; loopback/rede privada por padrão; projeto de calibração e procedimento de segurança. Nenhuma compra ou flashing sem autorização.

**Aceite:** simulador de pacotes reproduz bordas e falhas de transporte; hardware real aparece como `NOT_TESTED` até ser conectado.

### F7 — Validação RF real/multimodal
**Pré-requisitos:** ESP32 autorizado + pessoas informadas/consentidas, coleta ética, labels de referência, revisão de segurança, plano de experimento. Comparar CSI vs verdade de referência, precisão presença/ocupação/atividade, latência, falsos alarmes, domínio cruzado entre salas e orientação; mmWave/UWB opcional, calibrar coordenadas e relógios. Não prometer RF through-wall imaging com fidelidade de câmera.

**Aceite:** relatórios reproduzíveis e limites dos sensores publicados; qualquer alegação de desempenho deriva de medições reais controladas.

## 8. Módulos de produto (16) — inventário obrigatório

| ID | Módulo | Etapa principal | Estado inicial a verificar |
|---|---|---|---|
| M01 | Presence | F3A | Synthetic/reportado |
| M02 | Occupancy | F3A | Synthetic/reportado |
| M03 | Entries/exits | F3A | Experimental |
| M04 | Respiratory rate | F4 | Pesquisa |
| M05 | Heart rate | F4 | Pesquisa |
| M06 | Activity recognition | F3B | Pendente |
| M07 | Fall detection | F3B/F4 | Pesquisa |
| M08 | RF environment fingerprints | F3B | Pendente |
| M09 | Sleep quality | F4 | Pesquisa |
| M10 | Apnea screening | F4 | Pesquisa não clínica |
| M11 | 17-keypoint pose | F4 | Pesquisa |
| M12 | Model lab, CSI, LoRA/RVF | F4 | Experimental |
| M13 | Home automation / local hooks | F5 | Pendente |
| M14 | Multimodal RF world model | F7 | Pendente |
| M15 | Governed evidence and privacy | F0R/F5 | Parcial a auditar |
| M16 | Operator onboarding/calibration/verification | F5/F6 | Independente, sem copiar MetaHarness |

Status admissíveis: `UNVERIFIED`, `PARTIAL`, `IMPLEMENTED_SYNTHETIC`, `INTEGRATED_LEGACY`, `VALIDATED_REAL_DATA`, `BLOCKED`. A matriz deve apontar path do código, teste, comando, resultado, lacunas e prioridade.

## 9. Gargalos típicos e contramedidas

| Risco | Contramedida | Evidência |
|---|---|---|
| Frames CSI em alto volume estouram RAM/SQLite | bounded queues, downsampling, agregados, armazenamento de arrays segregado | testes de carga e memória |
| WebSocket trava UI em alta frequência | throttling/batching, visualizador desacoplado | FPS e latência medidos |
| Streams duplicados/reconexão reprocessam eventos | IDs idempotentes, offsets e de-dup | testes de reconexão |
| Clock drift entre sensores | monotonic clock + correção explícita/uncertainty | teste com relógios desalinhados |
| Modelos overfit ao simulador | holdouts por ambiente/sessão, comparar com dados reais | protocolos de validação |
| Modelos pesados degradam laptop | lazy load, CPU inference, limites de memória | benchmarks locais |
| Sensoriamento invasivo | opt-in, zona consentida, minimização e TTL | testes de permissão/retention |
| Dependência do upstream impede independência | contrato próprio, adapter legado off, inventário de licenças | boot sem upstream |
| Auditoria perde integridade por expurgo | retention controls + audit metadata + backups seguros | teste de restauração |
| APIs expostas em LAN | bind loopback, tokens, WS auth, origin checks | testes negativos de segurança |

## 10. TDD e qualidade de engenharia

Para toda feature: **Red → Green → Refactor**, com teste observável antes de alterar produção quando apropriado. Testes unitários de domínio (sem infraestrutura), integração API/SQLite/WS, contrato TS/Python, E2E Playwright, propriedades de preservação/ordenamento e benchmark de eventos. TypeScript `strict`, Python tipos + lint e checagem estática conforme stack, sem usar `Any` indiscriminadamente. DI por portas explícitas; abstrações apenas onde há mais de uma implementação real ou isolamento útil de testes.

**Gates obrigatórios:** `git status` revisado; linters, typechecks, testes, build, E2E local e Docker, acessibilidade automatizada, revisão de segredos, auditoria de dependências gratuita; resultados com exit code, versões, data. Não alegar “zero vulnerabilidades” quando auditoria não rodou ou não tinha rede. Continuar a implementação após falha corrigível; reportar bloqueios reais.

**Prioridade de risco:** P0 perda de dados, exposição de credenciais/usuários, falso L3; P1 regressão funcional, incompatibilidade de esquema, backup quebrado; P2 acessibilidade, desempenho, avisos; P3 cosmético. Não aumentar escopo avançado enquanto P0/P1 abertos.

## 11. Dados, SQLite, backup, retenção e migrações

SQLite local: usar migrations Alembic, WAL quando apropriado e mecanismo de backup consistente. Escrever `scripts/backup/backup.ps1`, `restore.ps1` com **destino separado** e modo de verificação antes de substituir qualquer banco ativo. Testar restauração em banco temporário e comparar contagem/hash dos eventos canônicos. Criar política de retenção e auditoria proporcional, nunca remover dados não sintéticos sem autorização e regra. Segredos no `.env` ignorado. Não vazar tokens em logs. Exportações sintéticas só incluem IDs fictícios.

## 12. Segurança, acessibilidade e escopo de rede

Manter painel e API ligados ao `127.0.0.1`; negar origens não autorizadas; autenticação para leitura sensível, alterações e WS; limitar tamanho de payload/rate; sanitizar logs; proteger cookies/sessões caso existam; dependências fixadas no lock. Implantação LAN, pública ou multiusuário é **projeto separado**, sujeito a autenticação/autorizações completas, TLS, threat model, revisão LGPD e aprovação do proprietário. Testar WCAG 2.2 AA pragmática: teclado, foco, contraste, landmarks, rótulos, estados ARIA, mobilidade e leitores de tela quando disponíveis.

## 13. Workflow de execução Windows / IntelliJ

1. Começar no diretório raiz do Git atual. Confirmar `Test-Path .\docs\PROJECT_MASTER_PLAN.md` e registrar versão deste plano.
2. Ler todos os documentos existentes e não substituir arquivos de progresso com status idealizado.
3. `git status --porcelain=v1`; inventariar alterações não rastreadas e staged (incluindo arquivos `.idea`), preservar tudo.
4. Inspecionar `pyproject.toml`, `package.json`, Compose e scripts de desenvolvimento; descobrir comandos válidos antes de rodar.
5. Verificar novamente erro Python lint e compatibilidade 3.13. Com imagem verificada, comando **permitido como intenção do usuário**: `docker run --rm wifi-spatial-backend-verification-py313`; se a ferramenta perguntar, selecionar autorização para este prefixo restrito é escolha do usuário.
6. Fazer inventário IP e reduzir dependência upstream; estabelecer suite baseline.
7. Implementar F0R → F1R → F2R → F3A em pequenos blocos. Não prender o fluxo esperando relatórios de fases futuras.
8. Atualizar docs após cada bloco. Documentar quando testes não puderem rodar (razão e risco).
9. Manter servidor rodando somente se necessário; não iniciar captura real sem consentimento.
10. Criar relatório final com arquivos alterados, teste/exits, riscos residuais, próxima tarefa exata; não fazer commit/push por padrão.

## 14. Arquivos de acompanhamento (obrigatórios)

- `docs/PROGRESS.md`: última etapa implementada de fato, data, arquivos e pendência próxima.
- `docs/REQUIREMENTS_TRACEABILITY.md`: matriz M01–M16 e testes por requisito.
- `docs/VERIFICATION_REPORT.md`: comandos, versões, logs curtos, tempo, resultados, limitações.
- `docs/SECURITY_REVIEW.md`: superfícies de ataque e itens corrigidos/pendentes.
- `docs/WARNINGS_TRIAGE.md`: listar os 68 warnings somente se tiver fonte real; não inventar itens.
- `docs/ORIGINALITY_REGISTER.md`: fontes, licenças e independência.
- `docs/FUNCTIONAL_SPEC.md`: requisitos sem código-fonte externo.
- `docs/DECISIONS.md` ou `docs/adr/`: escolhas e trade-offs.
- `README.md`: instalação sem custo, comandos locais, limites de simulação, como testar.

## 15. Checklist da próxima execução

- [ ] Plano v3 presente em `docs/PROJECT_MASTER_PLAN.md`.
- [ ] Baseline atual auditado sem mexer no staged da IDE.
- [ ] Falha de Python lint reproduzida e corrigida com testes.
- [ ] Teste Python 3.13 executado ou marcado BLOCKED com motivo.
- [ ] 68 warnings classificados por origem quando houver logs.
- [ ] Backup/restore comprovado sem substituir banco ativo.
- [ ] Inventário de origem/terceiros feito e modo legado desativado por padrão.
- [ ] Simulador próprio executa sem RuView e gera L0.
- [ ] F3A implementada de ponta a ponta (API, UI, storage, testes).
- [ ] Tests/lint/types/build/E2E executados e resultado registrado.
- [ ] Nenhum commit/push/deploy, dado real ou despesa não autorizada.

## 16. Critério de entrega desta etapa

A entrega é aceita quando: (a) o MVP existente não regrediu; (b) o modo padrão não depende de RuView e há rastreabilidade do clean-room; (c) F3A fornece analytics históricos e playback acionados por dados persistidos e API real; (d) a suíte de testes passa ou falhas residuais são classificadas com evidências; (e) segurança, privacidade, backup e procedência têm testes; (f) os relatórios são consistentes com a execução. **Nenhum dado sintético é reportado como medição real**.

## 17. Comando de continuidade para próximas sessões

> Leia integralmente `docs/PROJECT_MASTER_PLAN.md` e os arquivos de progresso e verificação. Faça auditoria do estado local e execute a primeira tarefa ainda não concluída na ordem F0R → F1R → F2R → F3A → F3B → F4 → F5 → F6 → F7. Tenha autonomia para edições e testes locais gratuitos no workspace, sem pedir confirmação repetida para ações de baixo risco; respeite aprovações impostas pelo host. Não faça push, commits, operações destrutivas, despesas ou sensing real sem autorização específica. Trabalhe em código e testes, valide e atualize evidências ao concluir cada marco. Não pare apenas no planejamento.
