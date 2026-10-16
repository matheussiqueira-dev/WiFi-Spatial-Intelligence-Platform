# Pessoas, animais e reconhecimento RF — visual agora, pesquisa depois

15/10/2026, America/Fortaleza. Escopo escolhido pelo proprietário: avatares
articulados agora e pesquisa para reconhecimento real posteriormente. Subordinado
ao PROJECT_MASTER_PLAN v3.0, sem captura de rádio, compras ou serviço pago.

## Entrega visual independente

Observatory agora oferece perspectiva isométrica em SVG, corpos luminosos e rigs
articulados para pessoa (17 pontos), cão e gato. O operador seleciona pessoas,
cães, gatos ou elenco misto; pode desligar volume/articulação, voltar à planta 2D
e ampliar a cena em tela cheia. Preferência de movimento reduzido desativa a
articulação. Replay usa os eventos persistidos, com a mesma distinção de origem.

As posições continuam vindo do contrato existente, sem criar entidades ou
observações novas. Tipo de avatar é uma preferência visual local, não classe
detectada, identidade, massa, altura medida ou informação exportada. Selecionar
cães não converte a contagem histórica em contagem validada de cães. Rigs têm
dimensões ilustrativas e gait procedural por tick/cenário; não há predição de
articulações. Sem posições RuView compatíveis, nenhum corpo é inventado.

Código próprio: lib/scene-rig.ts, articulated-scene.tsx e observatory.tsx.
Nenhum asset, pipeline ou implementação de RuView foi copiado. Não foi instalada
biblioteca gráfica/ML; são SVG, React e matemática elementar. O resultado é uma
projeção isométrica, sem câmera orbitável/oclusão física de um motor 3D.

## Avaliação das fontes fornecidas

As páginas foram consultadas nesta execução. Números a seguir são declarações
dos autores nas fontes, não resultados reproduzidos por esta plataforma.

| Fonte | O que oferece | Fronteira importante |
| --- | --- | --- |
| [Encoder pretrained](https://huggingface.co/ruvnet/wifi-densepose-pretrained) | encoder v2 de 8 features para embedding 128D; card declara MIT | 82,3% é métrica temporal de triplets, não acurácia de presença/vitais/pose; card retrata headline v1 de presença |
| [Pose MM-Fi](https://huggingface.co/ruvnet/wifi-densepose-mmfi-pose) | CSI amplitude [3,114,10] para 17×2 keypoints; card relata 82,69% torso-PCK@20 random_split | modelo e dataset declarados CC BY-NC 4.0; não adotado na demo comercial; protocolo in-domain não garante nova sala |
| [Benchmark do cog](https://github.com/ruvnet/RuView/blob/main/docs/benchmarks/pose-estimation-cog.md) | registro do primeiro treino pareado, PCK@20 3,0%; timings de carregamento | esse cog e o benchmark MM-Fi são modelos distintos; startup/health não prova precisão ao vivo |
| [Guia de operação](https://github.com/ruvnet/RuView/blob/main/docs/user-guide.md) | escopo de sensores, execução e modos | demonstração animada não estabelece origem real de cada valor |
| [Signal crate](https://github.com/ruvnet/RuView/blob/main/v2/crates/wifi-densepose-signal/README.md) | contexto de processamento de sinais | biblioteca descrita/testada não equivale a pipeline todo validado |
| [ESP-CSI oficial](https://github.com/espressif/esp-csi) | aquisição CSI, exemplos e interfaces públicas | usar só aquisição local autorizada; não habilitar exemplos de cloud automaticamente |
| [MMPose animal](https://mmpose.readthedocs.io/en/latest/model_zoo/animal_2d_keypoint.html) | pose animal baseada em imagens e datasets próprios | pode servir como referência visual/rotulagem futura autorizada; não transforma CSI em pose animal |

Metadados conferidos na API pública do Hugging Face, sem baixar pesos ou executar
Python remoto:

- `ruvnet/wifi-densepose-pretrained`: revisão
  `98b29a35f962996d6e8207e4f46818dedb5764d5`; público, não gated; license=mit.
  Arquivos listados incluem csi-embed-v2.safetensors, csi-embed-v2-int4.bin,
  métricas v2, presença head e adaptadores por nó. Candidato opcional de laboratório.
- `ruvnet/wifi-densepose-mmfi-pose`: revisão
  `39f46e583081a577bddd72f239690281ec11644b`; público, não gated;
  license=cc-by-nc-4.0. Arquivos incluem pose_mmfi_best.pt e variantes edge.
  Leitura de referência; não incluir pesos no produto comercial.

API de metadados: `https://huggingface.co/api/models/<repo-id>`. Revisões da
pesquisa não são novas dependências de runtime. Atualização futura exige revisar
licença, proveniência, hash, compatibilidade e avaliação de segurança do loader.

## Roteiro executável de pesquisa

| Marco | Trabalho necessário | Aceite / bloqueio |
| --- | --- | --- |
| R0 — contrato de observação | especificar fonte real, frequência, antenas, subportadoras, relógio, qualidade, consentimento e missing data | contrato aditivo; rejeitar dados incompatíveis; não mudar L0 retroativamente |
| R1 — aquisição controlada | dono autoriza dispositivo/sala e teste; coletar localmente com sessão e referência sincronizada | framing, perdas, taxa e jitter observados; hardware não disponível continua NOT_TESTED |
| R2 — presença/movimento | baseline estatístico próprio e comparação com encoder MIT opcional em laboratório isolado | inferência recebe somente features disponíveis; sem inventar vitais/contagem para preencher oito entradas |
| R3 — pessoa × pet × vazio | sessões rotuladas com pessoas/cães/gatos, múltiplos tamanhos, ambientes e situações simultâneas; regra unknown para fora da distribuição | métricas por classe, matriz, falsos positivos e rejeição; split por sessão/sala/sujeito; sem assumir que modelo humano cobre animais |
| R4 — pose humana | pipeline independente e pesos/dados de licença adequada; referência pareada consentida; calibração | schema de articulações com visibilidade/incerteza, PCK/MPJPE por protocolo e sala; localização corporal não equivale a identidade |
| R5 — pose animal | topologia por espécie, dados pareados e protocolos específicos de bem-estar/rotulagem | validação por espécie e porte; não reutilizar os 17 pontos humanos como anatomia animal |
| R6 — módulos avançados | respiração/coração, queda, world model, mesh e fusão em pesquisas separadas | referência apropriada, causalidade temporal, abstenção e testes fora do ambiente; sem uso clínico ou alertas certificados |

Custos zero nesta etapa: ferramentas locais e pesquisa documental. Hardware só
se já disponível/autorizado; nenhum pedido de compra. Não adicionar assinatura de
inferência, GPU remota ou conta comercial. Pesos third-party, se um dia avaliados,
ficam opcionais no laboratório, sem virar dependência obrigatória do motor próprio.

## Como avaliar as linhas da tabela RuView

Faixas de bandpass e zero-crossings descrevem famílias de processamento, não
garantem frequência cardíaca/respiratória correta. Precisam de amostragem,
fase/qualidade, janela, remoção de artefatos e sinal de referência adequados.
Uma feature de entrada chamada heart_rate não pode ser preenchida com número
inventado e depois anunciada como resultado do encoder.

Throughput de embeddings, cold-start de cog, latência de queda, alcance através
de parede, preço BOM e treinamento em GPU são contextuais. Cada um exige seu
próprio ambiente, definição e benchmark; nenhum número foi transferido para os
cards da plataforma. Point cloud com câmera/mmWave requer esses sensores e
sincronização; um mapa animado não substitui os dados. O catálogo de cogs não
assegura que cada módulo esteja integrado, gratuito ou validado para uso comercial.

Próxima tarefa concreta: R0 como especificação, depois inventário de dispositivo
disponível e autorização para R1. Nenhuma captura ou loader foi ativado aqui.
