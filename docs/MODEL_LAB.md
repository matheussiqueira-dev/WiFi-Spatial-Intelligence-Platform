# Baseline espacial sintético — F3B

Geometria virtual de um único ponto, sem RF. Não é classificador de atividade
humana validado. walking/stationary são trajetórias sintéticas; sitting,
possible_fall, fingerprints, vitais e pose estão unsupported. Evidência L0.

Dataset virtual-motion-v1: 24 sessões, 8 por split train/validation/test, 4 janelas
de 8 pontos por sessão; uma janela por sessão tem lacuna deliberada para rejeição.
Seeds e espaçamentos/ticks distinguem sessões/configurações. Rótulo de referência
não entra no preditor; somente velocidade média geométrica derivada dos pontos.
Parâmetros são ajustados apenas no train; validation/test ficam separados. JSON
com checksum reproduz dataset; modelo JSON contém versão/features/limiar/margem.
Artefatos ignorados junto ao SQLite, nunca carregados de caminho fornecido pelo
cliente. O gerador e o baseline compartilham domínio sintético: avaliação mede
essa tarefa artificial, não generalização para pessoas, ambientes ou sensores.

Rotas Bearer: POST /api/v1/model-lab/runs {seed: 0..100000}; GET na mesma rota
com limit 1..100/offset 0..100; GET /api/v1/model-lab/runs/{UUID}. Nenhum upload
ou parâmetro de execução arbitrário. Uma execução por processo, 96 janelas,
até 100 registros; capacidade esgotada recusa novo run sem apagar os existentes.
Métricas, parâmetros e splits são snapshots duráveis em migration 0004. Logs não
contêm token; UI apresenta matriz, suporte, rejeição, predições/qualidade e export.
Períodos em segundos relativos virtuais, não timestamps de medição.

Janelas com gap >2 s, timestamp repetido/invertido ou <3 pontos retornam unknown.
Margem de 10% ao redor do limiar também rejeita. Accuracy é somente entre aceitos;
rejection_rate usa total; falso positivo walking sobre stationary usa suporte
stationary. Denominador vazio vira null. Confusion matrix inclui coluna unknown.
Retenção de runs requer revisão offline explícita; nenhuma exclusão automática.

## Fila local CPU — incremento F4

POST /api/v1/model-lab/jobs aceita o mesmo seed. GET /jobs/{id} consulta status;
POST /jobs/{id}/cancel pede cancelamento cooperativo. Um worker/CPU, duas vagas
de espera, até 100 jobs duráveis. Preparação/treino/persistência marcam etapas
reais (10/40/80%), não estimativa de tempo. Cancelamento é checado antes do treino
e antes de persistir; depois da fronteira de persistência o job pode completar,
sem alegar rollback. Shutdown pede cancelamento e aguarda trabalho em curso.
Restart marca trabalhos incompletos como interrupted, sem reexecutar ocultamente.
Erros expostos são códigos sanitizados. UI permite enfileirar/cancelar/consultar
status durante a sessão, e abrir resultados persistidos depois de recarregar.
Modelos/datasets são JSON internos com hash; sem upload arbitrário, ONNX/LoRA/RVF.
Registro e pipeline CPU são locais/sintéticos; pesquisa clínica F4 segue BLOCKED.
