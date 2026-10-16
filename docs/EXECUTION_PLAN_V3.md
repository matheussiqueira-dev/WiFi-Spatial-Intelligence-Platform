# Plano detalhado de execução local — WiFi Spatial Intelligence Platform

Data: 15/10/2026, America/Fortaleza. Versão deste roteiro: 1.0.
Documento operacional subordinado ao [Plano Mestre v3.0](PROJECT_MASTER_PLAN.md).
Este roteiro organiza a continuação; não substitui o mestre nem comprova execução.

## 1. Comando único para começar

Execute esta linha no PowerShell, com o Codex CLI instalado e autenticado:

```powershell
codex -C "C:\Users\mathe\Documents\Programação\WiFi-Spatial-Intelligence-Platform" "Leia integralmente docs/EXECUTION_PLAN_V3.md e os documentos obrigatórios nele listados. Execute o backlog local autorizado na ordem definida, começando pela reconciliação do estado atual. Implemente, teste, corrija e registre evidências após cada marco; não pare apenas em planejamento. Preserve todas as alterações locais e staged. Não faça commit, push, publicação, operações destrutivas, compras ou sensoriamento real. Respeite os gates, as aprovações do host e os bloqueios demonstráveis. Ao terminar, apresente o relatório de entrega definido neste roteiro."
```

O comando abre uma sessão interativa no checkout existente e usa o modelo e as
permissões configurados pelo usuário. Não cria worktree, altera política de
aprovação ou inicia captura física. A sintaxe `codex -C <diretório> <prompt>` foi
conferida no `codex --help` instalado. O comando não foi disparado ao criar este MD.

Alternativamente, dentro de uma sessão Codex já aberta neste repositório, envie:

> Execute integralmente docs/EXECUTION_PLAN_V3.md, lendo antes o mestre v3.0 e os registros atuais. Avance pelo trabalho local autorizado, com implementação, testes e evidências; preserve WIP e staged; sem commit, push, ações destrutivas, despesas ou captura real. Respeite os critérios de avanço e registre bloqueios demonstráveis.

Um comando inicia a execução, mas não garante que limites da sessão, ferramentas,
dados, permissões ou hardware estejam disponíveis. Em interrupção, registrar o
ponto exato e retomar pelo mesmo roteiro, sem reiniciar o projeto ou duplicar trabalho.

## 2. Objetivo e ordem de autoridade

Consolidar a operação segura do MVP independente, fechar pendências de F0R/F1R/F2R
e F3A, implementar o baseline experimental F3B e avançar pelos marcos locais
seguintes apenas quando seus pré-requisitos e autorizações estiverem satisfeitos.
Entregar funcionalidades completas entre domínio, API, SQLite, contratos e UI.

Ler integralmente, antes de alterar código:

1. `AGENTS.md` e instruções aplicáveis da pasta pai, quando existentes.
2. `docs/PROJECT_MASTER_PLAN.md`, caminho normativo único.
3. `CLAUDE.md` e `README.md`.
4. `docs/PROGRESS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`,
   `docs/VERIFICATION_REPORT.md` e `docs/TECHNICAL_REPORT_V3.md`.
5. `docs/SECURITY_REVIEW.md`, `docs/WARNINGS_TRIAGE.md`,
   `docs/DATA_RETENTION_AND_BACKUP.md` e `docs/ANALYTICS_API.md`.
6. `docs/FUNCTIONAL_SPEC.md`, `docs/ORIGINALITY_REGISTER.md`,
   `docs/THIRD_PARTY_NOTICES.md`, `docs/DECISIONS.md` e `docs/RUVIEW_INTEGRATION.md`.

Se o mestre estiver ausente, for v2 ou não contiver clean-room/F0R/F1R/F2R,
registrar a divergência. Continuar somente correções técnicas independentes de
requisitos novos. Não tratar `docs/docs/PROJECT_MASTER_PLAN.md` como fonte vigente.
Se o mestre tiver evoluído além da v3, reconciliar o conteúdo e registrar diferenças.
Requisitos propostos neste roteiro são escolhas de implementação, não citações
inventadas do mestre. Em conflito, aplicar instruções atuais do usuário e mestre.

## 3. Baseline documental a reconfirmar

Os números abaixo pertencem à execução registrada, não são resultados desta próxima sessão.

| Área | Último registro | Confirmação necessária |
| --- | --- | --- |
| Mestre | v3.0, SHA-256 `2dd0b492dd94bff52cb9eb2d22a9de5fa116c367405755a90493595c3ce36ad7` | Ler conteúdo atual e calcular hash; mudança exige reconciliação, não sobrescrita |
| Git | `feat/platform-foundation`, HEAD `27674175866b0d0e20b10ddee30ab33268134d84`; IDE staged; produto untracked | Inventariar staged, unstaged e untracked novamente; contagens são mutáveis |
| Backend | 111 testes Windows e 111 Python 3.13 aprovados | Reexecutar no código atual |
| Web | 10 testes; lint, tipos e build aprovados | Reexecutar no código atual |
| E2E | 2 nativos no último check; 3 incluindo legado em execução anterior | Revalidar nativo e legado separadamente sem confundir skips com passes |
| Persistência | 24 payloads, replay e relatório preservados após restart Docker | Nova evidência com banco isolado e contagem observada |
| Produto | synthetic-native, analytics API/SQLite, replay/export/snapshots | Não recriar o que já funciona; testar e corrigir lacunas |
| Pendências | WinError 10054, browsers/leitor de tela, rate limit/CSP/auditoria | Reproduzir e classificar; não declarar correção só por editar |
| IDE | Histórico menciona 68 warnings; usuário mostrou indicador de 69 | Fonte/lista individual ainda não obtida; quantidade não comprova causa |

## 4. Regras invariáveis de execução

- Preservar FastAPI/SQLite/Next.js, dados existentes, `.idea/.gitignore` staged e WIP.
- Não executar reset/clean/rebase destrutivo, descarte, stage automático, commit ou push.
- Não apagar bancos ou volumes para preparar testes. Não parar processos alheios.
- Usar venv Python, `npm.cmd`, lockfiles e dependências gratuitas com licença verificada.
- Não versionar `.env`, tokens, logs, SQLite, dumps, datasets sensíveis ou modelos runtime.
- Manter token no backend/memória do frontend; WS autentica no primeiro frame.
- Produto padrão sem RuView obrigatório; laboratório legado off e atribuições preservadas.
- Domínio sem HTTP/ORM/UI; DI por portas úteis, migrações aditivas e contratos compatíveis.
- Todo dado gerado permanece `L0_SYNTHETIC`, inclusive dados usados em treino/avaliação.
- Separar ground truth de predictions; desconhecido permanece null/unknown.
- Não copiar upstream nem afirmar clean-room estrita após exposição anterior.
- Não publicar, instalar serviços globais, ativar hardware, enviar dados ou contratar serviços.
- Não reduzir testes, esconder exceções, adicionar skips arbitrários ou relaxar segurança para obter verde.
- Mudança de escopo ou dependência exige decisão registrada, não reorganização estética.

## 5. Método para cada item

1. Identificar requisito e evidência anterior; inspecionar código e dependências.
2. Reproduzir falha ou escrever teste observável antes da implementação.
3. Registrar Red quando existir; implementar incremento mínimo completo.
4. Executar teste específico, depois testes afetados e gates do marco.
5. Integrar contrato, persistência, API e UI quando a funcionalidade exigir.
6. Conferir diffs e estado Git; preservar mudanças que não pertençam ao item.
7. Registrar comando, data/fuso, ambiente, exit code, duração e resultado real.
8. Atualizar progresso, rastreabilidade, verificação e decisões pertinentes.
9. Avançar somente após corrigir P0/P1 relacionados; continuar tarefas independentes
   quando houver bloqueio externo em um item.

P0: perda de dados/segredos/falsa evidência real. P1: regressão, incompatibilidade
ou recuperação quebrada. P2: acessibilidade/desempenho/avisos. P3: cosmético.

## 6. Marco A — Reconciliação e recuperação F0R

### A1. Inventário antes de editar

Executar comandos de leitura, sem imprimir configurações secretas:

```powershell
git status --porcelain=v1
git diff --stat
git diff --cached --stat
git ls-files --others --exclude-standard
git branch --show-current
git rev-parse HEAD
Get-FileHash docs/PROJECT_MASTER_PLAN.md -Algorithm SHA256
```

Inventariar versões, scripts, Docker disponível, portas e bases de verificação.
Comparar documentação atual com o código; não assumir que árvore sem diff de
rastreados esteja limpa quando o produto inteiro é untracked.

### A2. Recuperar baseline executável

Executar `scripts/verify/check.ps1`. Reproduzir falhas atuais antes de corrigir.
Lint já corrigido deve receber regressão, não uma falha artificial. Revalidar
UTC/DST, precisão submilissegundo e teardown WS. Se faltar dependência, usar
bootstrap/lockfile após revisão; não recriar ambiente funcional sem necessidade.

### A3. Triagem de warnings

Obter diagnósticos de Ruff/ESLint/TypeScript/build e, se acessível, export da IDE.
Separar número da IDE de warnings de CLI e erros runtime. Para cada item registrar
origem, arquivo/linha, reprodução, impacto, correção ou justificativa. Sem lista
real da IDE, manter `UNVERIFIED`; não inventar 69 descrições nem desativar inspeções.

**Aceite A:** baseline atual identificado, falhas reais classificadas, WIP intacto,
comandos documentados e nenhuma alegação baseada apenas em contagem histórica.

## 7. Marco B — Recuperação, logs e operação F1R

### B1. Backup recorrente sem alterações globais

Reutilizar `app/maintenance.py` e `scripts/backup/backup.ps1`/`restore.ps1`.
Proposta de implementação local: rotina opt-in de backup por intervalo, desligada
por padrão, com origem explícita, destino dentro do workspace, exclusão mútua,
cancelamento limpo e último sucesso/erro consultável sem caminhos/segredos sensíveis.
Adicionar parâmetros ao launcher existente ou wrapper próprio, conforme inspeção.
Não registrar tarefa global Windows silenciosamente nem iniciar daemon permanente.

Definir política operacional documentada: sugerir snapshot diário e antes de
migração, executar apenas ao habilitar rotina; preservar no mínimo sete snapshots
e todos dos últimos 30 dias conforme a política existente. Declarar que backup no
mesmo disco não cobre perda do dispositivo. Não executar prune/expurgo em dados
de uso nesta implementação; testes de retenção usam somente fixtures dedicadas.

Testar backup durante escrita, integridade, hashes dos payloads, exclusão de
execuções sobrepostas, falha de destino, cancelamento, hold e restauração para
arquivo novo. Snapshot inválido nunca permite expurgo ou substituição do banco.

### B2. Retenção e logs

Confirmar os limites atuais de eventos/relatórios e logs Python/Docker. Testar
rotação, preservação de auditoria e recusa de destino inadequado. Nenhum token
pode aparecer em mensagem de erro. Registrar política, responsável e comando
de verificação de recuperação. Disponibilidade da rotina não equivale a backup
recorrente ativo: só marcar ativo após observar ciclos reais no ambiente opt-in.

### B3. WinError 10054 e cancelamento

Reproduzir em banco/portas isolados: encerramento normal, cliente abortado,
reconexão, parada do pipeline e cancelamento no shutdown. Mapear pilha, camada e
versões. Usar espera por condição com prazo; não adicionar sleeps arbitrários.
Corrigir a causa quando controlável. Não silenciar globalmente o event loop nem
trocar política Windows apenas para esconder mensagem. Se for comportamento
externo residual, documentar frequência em amostra finita e impacto observado;
não afirmar ausência absoluta de intermitência após poucas repetições.

**Aceite B:** backup/restore verificáveis, rotina opt-in testada, retenção segura,
sem expurgo de uso e cancelamento/reconexão com resultados explícitos.

## 8. Marco C — Segurança local F1R

### C1. Limites de requisição

Implementar rate limit local limitado em memória, configurável e testável por
relógio injetado, sem serviço externo. Separar tentativas de autenticação,
operações de escrita e leituras; definir valores em ADR como decisões de projeto.
Não usar token bruto como chave/log, não confiar em X-Forwarded-For arbitrário.
Incluir TTL/limite de entradas e esclarecer restrição a um worker no MVP.
429 deve informar Retry-After e preservar demais validações de auth/origem.

Testar esgotamento, recuperação temporal, memória limitada, abuso de chaves,
isolamento das classes e funcionamento de dashboard/replay sob uso normal.

### C2. Auditoria de negativas

Cobrir Bearer ausente/inválido, origem negada, primeiro frame WS inválido/timeout,
limite de conexões e bloqueios de operação. Registrar tipo, UTC, resultado e ID
de correlação não pessoal. Não guardar Authorization, primeiro frame, token, query
sensível ou payload integral. Evitar amplificação: trilha limitada/agregada com
política de retenção, sem deixar tentativas maliciosas encherem disco indefinidamente.
Adicionar testes que procurem sentinelas de segredo nos logs/auditoria.

### C3. CSP compatível com Next.js

Inspecionar `next.config.ts`, renderização, hidratação e builds nativo/Docker.
Comparar nonce por requisição com hashes estáticos antes de escolher. Documentar
impacto em cache, rendering e standalone; não supor que retirar unsafe-inline
isoladamente preserve Next. Se adotar nonce, propagar corretamente para scripts
e verificar que muda por resposta; se usar hashes, verificá-los a cada build.
Restringir connect-src à API/WS configurados, sem ampliar para wildcard.

Validar CSP em produção com API real, navegação, estilos, hidratação, analytics,
downloads e WS, além de teste negativo de script sem autorização. Não declarar
CSP estrita se alguma exceção inline continuar necessária e documentada.

**Aceite C:** controles ativos com testes negativos, sem vazamento de segredo ou
regressão E2E; limitações de localhost e um worker explícitas. LAN/TLS/multiusuário
continuam fora da implantação autorizada, mesmo que haja código preparatório.

## 9. Marco D — Compatibilidade e acessibilidade F1R

Conferir executáveis reais antes de marcar navegador disponível. Instalar browsers
Playwright apenas pelo fluxo de dependências local autorizado, se viável; não
instalar leitor de tela global. Acrescentar projetos Firefox/WebKit à configuração
com seleção explícita dos instalados, sem esconder falha de browser prometido.

Testar autenticação, controles, histórico, analytics, replay, export e snapshots
em cada browser executável. Verificar teclado, foco após erro/modal, labels,
regiões ARIA, zoom, contraste e 320 px. Usar axe e inspeção visual; leitor de tela
manual somente quando disponível, com registro de roteiro e resultado humano.
Se indisponível, registrar `BLOCKED` e seguir outras tarefas.

**Aceite D:** matriz browser × fluxo com PASS/FAIL/BLOCKED reais. Nenhuma alegação
de conformidade WCAG integral apenas porque axe passou.

## 10. Marco E — Procedência e arquitetura F2R

Revalidar domínio sem imports HTTP/ORM/RuView e startup sem carregar app.ruview.
Verificar dependências e Compose padrão: somente API/web necessários. Exercitar
contratos antigos 1.0/1.1 e novo 2.0; migrações preservam payloads e provenance.

Atualizar inventário por componente: origem declarada, licença, versão/digest,
finalidade e presença no runtime padrão ou laboratório. Especificação neutra,
registro de originalidade e ADR devem acompanhar cada componente novo.
Não copiar algoritmo/testes upstream nem apagar atribuição por renomeação.

Revisão independente estrita exige pessoa/equipe sem exposição anterior e não
é simulada pelo mesmo implementador. Preparar pacote neutro de requisitos e
evidências; manter ressalva aberta até revisão efetiva. Não remover arquivos
legados nesta rodada: preservar laboratório desligado e compatibilidade.

**Aceite E:** independência operacional reproduzida; limite clean-room registrado,
sem transformar declaração de autoria em certificação jurídica.

## 11. Marco F — Fechamento e evolução controlada da F3A

Revalidar a entrega existente antes de ampliar escopo:

- Janelas UTC de 1 min/5 min/hora/dia; timezone local/DST somente na apresentação.
- Ordenação determinística, IDs idempotentes, início inclusivo/fim exclusivo exato.
- Sem extrapolar intervalos; desconexões/segmentos/lacunas viram unknown.
- Contagens desconhecidas preservadas; deltas líquidos não são cruzamentos pessoais.
- Filtros, limites, paginação, replay, CSV/JSON e snapshots usando API/SQLite reais.
- UI com vazio, erro, carregamento, seleção aplicada e export correspondente.
- Gravação antes da publicação, backpressure e métricas reais de software.

Corrigir lacunas reproduzidas com testes backend, contrato TS e E2E. Não criar
sensores/zonas falsos para preencher filtros que o contrato agregado não suporta.
Exibir limitações e origem atual; evoluir schema aditivamente se houver observação
por nó virtual de fato implementada.

Cursores/rollups/export completo são melhorias condicionadas à necessidade de
volume. Antes de implementar, medir fixture fixa e registrar tempo/memória/ambiente.
Preservar offset existente; eventual cursor precisa ordenação timestamp+ID,
seleção estável, fim fixo e tratamento documentado de retenção. Não marcar essa
otimização como requisito já entregue nem introduzir migração sem evidência.

**Aceite F:** cenário → evento persistido → filtro → agregado → replay → export
→ relatório → reinício/reabertura funciona sem mocks e preserva L0.

## 12. Marco G — F3B: baseline experimental completo

### G1. Viabilidade e dados

Escrever especificação funcional neutra das features disponíveis. O gerador
geométrico atual não mede RF: não derivar CSI, frequência cardíaca ou fingerprints
de posições e chamar isso medição. Escolher uma tarefa distinguível nos dados;
classes sem informação suficiente devem ficar unknown/unsupported.

Preparar datasets sintéticos versionados com seeds, sessões e checksum; separar
train/validation/test por sessão e configuração antes de qualquer ajuste.
Não reutilizar amostras do mesmo trecho entre splits. Ground truth fica apenas
no dataset de referência, sem entrada direta no classificador ou ID do cenário.
Se sitting não for distinguível de stationary, documentar e rejeitar/combinar
somente com decisão explícita; não fabricar um sinal que prove a hipótese.

### G2. Domínio, treino e avaliação

Criar portas de extração/modelo e casos de uso em bounded contexts pertinentes,
mantendo a composição existente. Implementar baseline CPU local reproduzível,
com biblioteca gratuita somente se necessária/licenciada. Modelo deve registrar
versão, hash, features, dataset, splits, seed, parâmetros e limitação L0.

Testar janelamento e bordas, lacunas, baixa qualidade, rejeição unknown,
determinismo e vazamento entre splits. Produzir matriz de confusão, suporte por
classe, falsos positivos e taxa de rejeição; denominadores nulos não viram zero
de desempenho. Não estipular acurácia obtida antes de rodar a avaliação.

RF fingerprint só avança com modalidade e features pertinentes. Se apenas houver
geometria virtual, manter subitem RF `BLOCKED` e executar o baseline espacial
sintético viável, sem afirmar mudança de objeto físico. possible_fall só com
sinais pertinentes e protocolo; caso contrário permanece indisponível.

### G3. Integração real

Persistir metadados de modelo/runs/avaliações por migração aditiva; artefatos
binários/datasets ficam ignorados e referenciados por caminho seguro/checksum.
Criar contratos Pydantic/Zod e endpoints autenticados para consultar modelo,
executar avaliação limitada e consultar resultados paginados. Validar IDs,
parâmetros e caminhos; não aceitar pickle/modelo arbitrário enviado pelo cliente.

UI deve mostrar modelo, origem, versão, evidência, classe/rejeição, período,
qualidade e avaliação observada. Não substituir a cena original por predição.
Treino/avaliação possuem limites, cancelamento e progresso quando demorados.
E2E usa dataset fixo e API/SQLite real: executar run → persistir → abrir avaliação
→ recarregar → confirmar mesmo resultado e rótulo sintético.

**Aceite G:** pipeline reproduzível de baseline espacial sintético integrado;
nenhuma acurácia real ou detecção clínica alegada. Subitens RF sem dados ficam
explicitamente bloqueados, sem impedir entrega independente do baseline viável.

## 13. Marcos seguintes — avanço condicionado ao mestre

Executar tarefas locais viáveis na ordem abaixo após os marcos anteriores e sem
P0/P1 abertos. Não fingir conclusão de fase porque uma tela ou contrato existe.

| Fase | Trabalho local detalhado | Testes/aceite | Dependência que limita conclusão |
| --- | --- | --- | --- |
| F4 | Evoluir registro de modelos/datasets, checksums/licenças, splits, fila CPU limitada, cancelamento e histórico de avaliação; reutilizar G, evitar segundo laboratório paralelo | Treino/inferência/avaliação reproduzíveis, limites de recursos, falhas/cancelamento e resultado persistido na UI | Vitais/sono/apneia/pose dependem de modelo/dados adequados; ONNX/LoRA/RVF só com utilidade e licença comprovadas |
| F5 | Regras locais com DSL declarativa restrita, validação/versionamento, dry-run e revogação; autorização por ação, retenção e auditoria; sem eval/exec | Regra criada → evento sintético → decisão auditada → revogação impede nova ação; payload inválido e abuso recusados | Entrega inicial em dry-run; webhook/Home Assistant real somente com autorização do destino, allowlist, auth e consentimento aplicáveis |
| F6 | Especificar interface pública própria de aquisição, simulador de pacotes e parser robusto; pairing/consentimento, timestamps, qualidade e calibração documentados | Fixtures malformadas, limites/fuzzing, relógio fora de ordem, replay e autorização; operação sem conectar dispositivo | Hardware NOT_TESTED; compra, flashing e transmissão a dispositivo exigem autorização específica |
| F7 | Preparar protocolo de estudo, consentimento, labels, métricas, armazenamento minimizado e limites de publicação | Revisão documental do protocolo; sem tabela de desempenho preenchida antes do experimento | Captura/validação física BLOCKED até autorização, hardware, pessoas informadas e referência; não executar pelo comando inicial |

RBAC e consentimento preparatórios não autorizam abrir servidor na LAN ou internet.
Revisão jurídica/assistiva por terceiros não pode ser inventada nem substituída por
outro teste automático. Não enviar dados/mensagens a terceiros ao preparar pacotes.

## 14. Catálogo de comandos existentes

Executar a partir da raiz. Não encadear todos cegamente: verificar cada exit code
e corrigir a causa antes de prosseguir. Conferir assinaturas dos scripts no estado
atual antes de executar; exemplos abaixo correspondem à inspeção deste roteiro.

| Objetivo | Comando |
| --- | --- |
| Gate principal Windows | `& scripts/verify/check.ps1` |
| Gate sem browser, insuficiente para declarar E2E | `& scripts/verify/check.ps1 -SkipE2E` |
| Backend específico | `& apps/api/.venv/Scripts/python.exe -m pytest apps/api/tests/test_analytics.py -q` |
| Lint Python | `& apps/api/.venv/Scripts/python.exe -m ruff check apps/api scripts/verify` |
| Formatação Python sem editar | `& apps/api/.venv/Scripts/python.exe -m ruff format --check apps/api scripts/verify` |
| Contratos após mudança intencional | `& apps/api/.venv/Scripts/python.exe scripts/verify/export_contract.py` |
| Lint web | `npm.cmd run lint` |
| TypeScript | `npm.cmd run typecheck` |
| Testes web | `npm.cmd run test:web` |
| Build normal | `npm.cmd run build` |
| Build próprio para E2E | `npm.cmd run build:e2e` |
| E2E com build apropriado | `npm.cmd run test:e2e` |
| E2E analytics direcionado | `npm.cmd run test:e2e --workspace apps/web -- --grep analytics:` |
| E2E e persistência Docker nativos | `& scripts/verify/docker-e2e.ps1` |
| Persistência Docker sem browser | `& scripts/verify/docker-e2e.ps1 -SkipBrowser` |
| Laboratório legado opt-in | `& scripts/verify/check.ps1 -RuView -RuViewHttpPort 4970 -RuViewWsPort 4971` |
| Build atualizado Python 3.13 | `docker build --build-arg PYTHON_VERSION=3.13 --build-arg PYTHON_DIGEST=<digest 3.13 do Dockerfile.verify> -f apps/api/Dockerfile.verify -t wifi-spatial-backend-verification-py313 .` |
| Ruff/testes/auditorias Python 3.13 | `docker run --rm wifi-spatial-backend-verification-py313` |
| Auditoria npm | `npm.cmd audit --json` |
| Inventário ambiente/browser | `node scripts/verify/inventory.mjs` |
| Inventário licenças Python | `& apps/api/.venv/Scripts/python.exe scripts/verify/license_inventory.py` |
| Smoke backup/restore com fixture | `& apps/api/.venv/Scripts/python.exe scripts/verify/maintenance_smoke.py` |

Portas registradas: nativo E2E 4310/4810; Docker nativo 4400/4900;
legado alternativo 4970/4971. Verificar disponibilidade e proprietário atual.
Não reutilizar servidor/banco de uso; adaptar runner para novas portas somente
com configuração consistente em API, frontend, CORS, CSP e testes.

Reconstruir a imagem 3.13 após alterações relevantes: tag existente não prova
que o código atual foi testado. Auditoria sem rede é BLOCKED, nunca zero problemas.
Redigir evidências sem tokens; traces brutos podem conter credenciais e ficam
ignorados, com acesso restrito, sem anexação pública automática.

## 15. Gates de marco e encerramento

| Gate | Condição |
| --- | --- |
| Integridade | Staged/WIP/dados preservados; migrations e restore exercitados em bases isoladas |
| Qualidade | Ruff lint/format, backend, ESLint, TS, web e build aprovados no código entregue |
| Compatibilidade | Python 3.13 executado; browsers com PASS/FAIL/BLOCKED individual |
| Produto | E2E API real/SQLite nativo; legado opt-in revalidado quando fronteira afetada |
| Persistência | Reinício real preserva payloads e novos registros duráveis relevantes |
| Segurança | Negativas auth/origem/limites e sentinelas de segredo testadas; auditorias executadas |
| Evidência | L0 preservado, null/unknown e limites de modelos visíveis na UI e exports |
| Documentação | Progresso/matriz/verificação/ADRs refletem código e comandos realmente executados |

Rodar testes específicos por incremento. Executar gates integrados ao fechar cada
marco material e ao final; não repetir toda suíte sem mudança ou falha nova que
justifique. A criação deste MD não exige rodar a suíte do produto e não é validação
de nenhuma implementação futura.

## 16. Registro de evidências e retomada

Após cada marco atualizar:

- `docs/PROGRESS.md`: entrega real, arquivos, última execução e próxima tarefa exata.
- `docs/REQUIREMENTS_TRACEABILITY.md`: requisito → código → teste → comando →
  resultado → lacuna → prioridade/responsável; manter M01–M16 coerentes com v3.
- `docs/VERIFICATION_REPORT.md`: data/fuso, versões, exit/duração, falha inicial,
  correção e reexecução; distinguir código testado de alterações posteriores.
- `docs/DECISIONS.md`: decisões de limites, CSP, modelos, splits e compatibilidade.
- Guias de segurança, warnings, backup, API e README conforme impacto real.

Registro mínimo por tarefa:

```text
ID / requisito:
Estado: UNVERIFIED | PARTIAL | IMPLEMENTED_SYNTHETIC | INTEGRATED_LEGACY | BLOCKED
Arquivos e comportamento:
Comando / ambiente / data / exit code / duração:
Falha reproduzida e correção:
Evidência observada / limitações:
Próxima ação / dependência / responsável:
```

`VALIDATED_REAL_DATA` só pode ser usado após protocolo real autorizado e evidências
adequadas; não é um resultado possível do modo sintético desta rodada.

Ao encontrar bloqueio: registrar erro/comando exato e dependência, não tentar
bypass. Continuar itens independentes. Se faltar informação essencial, pedir
somente essa informação. Limite de sessão não conclui fase: salvar checkpoint com
ID em andamento, testes pendentes e primeiro comando seguro de retomada.

## 17. Relatório final obrigatório

Entregar síntese e documento técnico atualizado com:

1. Versão/hash atual do mestre e divergências encontradas.
2. Arquivos alterados/criados e funcionalidades efetivamente implementadas.
3. Estado de cada fase F0R–F7 e M01–M16, com escopo sintético explícito.
4. Evidência de independência operacional e limite da separação clean-room.
5. Comandos, versões, testes/lint/tipos/build/E2E/auditorias com resultados reais.
6. Falhas, avisos, regressões, browsers indisponíveis e testes não executados.
7. Backup/restore/retenção e estado da rotina recorrente (inativa/opt-in/observada).
8. Git staged/unstaged/untracked atual, sem confundir ausência de diff com árvore limpa.
9. Pendências priorizadas, bloqueios demonstráveis e primeira próxima tarefa.
10. Confirmação de ausência de commit/push, descarte, captura real e despesas.

Não concluir toda a plataforma porque os marcos locais passaram. Separar entrega
funcional, pesquisa sintética, validação de hardware e dependências humanas.

## 18. Checklist do executor

- [ ] Li o mestre atual integralmente e confirmei versão/seções.
- [ ] Preservei Git, dados, configurações e staged da IDE.
- [ ] Reconciliei o baseline real em vez de repetir números históricos.
- [ ] Executei A → B → C → D → E → F e corrigi P0/P1 aplicáveis.
- [ ] Entreguei G com modelo/dataset/avaliação/UI reais ou demonstrei bloqueio.
- [ ] Avancei F4/F5/F6 somente no escopo local viável e autorizado.
- [ ] Mantive F7 físico bloqueado e subitens sem dados honestamente indisponíveis.
- [ ] Rodei gates pertinentes e registrei falhas/skips/bloqueios sem mascarar.
- [ ] Atualizei os documentos após cada marco, com checkpoint de retomada.
- [ ] Entreguei relatório final; não fiz commit, push, descarte ou captura real.
