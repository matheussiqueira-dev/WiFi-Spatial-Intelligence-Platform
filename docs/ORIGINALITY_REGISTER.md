# Registro de origem e limites de independência

## Protocolo SWF1 de quadros CSI — 17/10/2026

Layout, autenticação e receptor escritos para este projeto a partir de conceitos
públicos de CSI do ESP-IDF. Exposição registrada: RUVIEW_FEATURES_ANALYSIS.md descreve
em alto nível que o firmware RuView envia UDP binário little-endian com tipo no
cabeçalho e hash BLAKE3 nos contratos; nenhum arquivo de firmware/parser RuView foi
reaberto nesta entrega e nenhum trecho foi transcrito. O SWF1 difere por desenho
(tipo único, HMAC-SHA256 por dispositivo, recusa de hardware não testado), mas a
exposição prévia impede alegar clean-room estrita.

## Apresentação articulada — 15/10/2026

Rigs humanos/quadrúpedes, projeção SVG, cores/controles implementados por geometria
procedural própria. Screenshot fornecido usado como direção visual; nenhum asset,
shader, código ou pipeline RuView copiado. Estrutura de 17 pontos é representação
visual convencional, não saída de modelo ou implementação de sensing.
Leitura adicional de fontes públicas: model cards HF pretrained/MM-Fi, benchmarks,
guia de usuário e README signal do RuView; ESP-CSI e MMPose docs. Exposição continua
explicitamente registrada; não alegar clean-room estrita. Pesos/scripts remotos
não baixados nem executados. Revisões/licenças em PEOPLE_ANIMALS_RF_RESEARCH.md.

## Exposição adicional — 15/10/2026, evolução enterprise

Nesta entrega foi reaproveitado o clone local temp_ruview, remote
matheussiqueira-dev/RuView e HEAD a1ca023ee872683d160250d47ae3d4d228af55a0.
Releitura de README, NOTICE, manifestos Cargo e fronteiras do servidor de sensing
(seleção de origem, payload e tarefa simulada). A análise extensa existente na
raiz foi preservada e recebeu adendo funcional, sem transcrever código upstream.
Isso mantém a limitação de exposição; não certifica clean-room estrita.
Mudanças novas de transporte/contratos/UI decorrem de falhas e testes locais,
não de adaptação do pipeline RuView. Nenhum runtime de referência obrigatório.

dashboard.html foi adaptado do template do plugin productivity/task-management,
com atribuição preservada neste registro e referências de fonte remota removidas.
É ferramenta auxiliar de desenvolvimento; não é código autoral exclusivo nem
parte necessária do runtime Next.js. Não foi executado/servido nesta entrega.

15/10/2026, plano normativo v3.0. HEAD 2767417; branch feat/platform-foundation;
árvore local dirty, majoritariamente não rastreada. Não houve commit/push.

## Requisitos e implementação nova

- Fonte funcional: solicitações do proprietário, mestre v3.0 e FUNCTIONAL_SPEC.
- `app/domain/acquisition.py`: implementação nova de cenas geométricas sintéticas
  com caminhos triangulares, contagens e perturbações pseudoaleatórias. Usa somente
  biblioteca padrão e matemática elementar. Não modela rádio nem traduz pipeline
  de terceiro. Testes novos foram escritos por comportamento antes da implementação
  (quatro falhas Red observadas: domínio ausente e laboratório ligado).
- `app/adapters/native.py`, `ports/clock.py`, `application/read_history.py`,
  `ports/history.py`, `adapters/history.py`: tradução de contrato próprio, relógio
  injetável e fronteiras HTTP/SQLite. Contrato 2.0.0 aditivo; legados 1.0/1.1 preservados.
- Analytics, replay e manutenção foram desenvolvidos nesta continuação para os
  requisitos locais. Não foram portados de código de referência externo.

## Exposição prévia e limite clean-room

O agente responsável já leu o adaptador legado e registros da inspeção anterior
de fonte upstream durante a integração F2. Portanto **não há separação rigorosa
de equipes nem certificação de originalidade jurídica/clean-room estrita**.
O domínio novo foi formulado contra requisitos neutros e não importa código
legado. Uma exigência de isolamento rigoroso exigiria implementador sem essa
exposição, comparação independente e eventual revisão jurídica. Não alegar
originalidade absoluta nem exclusividade patrimonial a partir deste registro.

## Laboratório histórico preservado

`app/ruview.py`, fixtures oficiais, schemas 1.1, Compose/launchers/teste E2E oficiais
e RUVIEW_INTEGRATION são compatibilidade histórica, não motor próprio.
Flag SPATIAL_LEGACY_LAB_ENABLED=false por padrão; import somente na composição
do laboratório após opt-in. Sem imagem/SDK/modelo externo obrigatório no Compose
normal. Atribuições/digest/licença declarada MIT permanecem no guia histórico.
Nenhum arquivo foi apagado ou renomeado para disfarçar sua origem.

## Inventário e limitações de autoria

Git ainda não contém commits da implementação, portanto não prova autoria de cada
linha pré-existente. Código local anterior é preservado como origem declarada do
projeto, sem certificação retroativa. Fixtures oficiais são dados de integração
atribuídos; não são usados para definir trajetórias do motor nativo. Modelos, CSI,
firmware e assets de referência não foram copiados para o produto novo.

Dependências e licenças: THIRD_PARTY_NOTICES.md. O próprio Codex é ferramenta de
desenvolvimento, não dependência de runtime ou garantia de custo de acesso zero.
