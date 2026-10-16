# Analytics histórico e playback — API 1.0 / contrato nativo 2.0

15/10/2026. Todas as rotas exigem o Bearer local. Não colocar token em URL, storage
do navegador ou variável NEXT_PUBLIC. Endpoints disponíveis no OpenAPI local.

| Rota | Comportamento |
| --- | --- |
| GET /api/v1/analytics | Resumo completo da seleção e páginas de buckets/intervalos/transições |
| GET /api/v1/analytics/replay | Eventos canônicos ordenados e segment_id, modo REPLAY |
| GET /api/v1/analytics/export.csv | Agregações da página em CSV com evidence_level |
| POST /api/v1/analytics/reports | Body com os mesmos filtros; grava snapshot e retorna UUID |
| GET /api/v1/analytics/reports | Lista de snapshots (limit/offset), até 100 retidos |
| GET /api/v1/analytics/reports/{id} | Snapshot JSON persistido, 404 se ausente |

Filtros: start/end UTC explícito [start,end), bucket=minute/five_minutes/hour/day,
room_id=living-room, source_id=native-01/simulator-01/ruview-01 opcional,
scenario e segment_id opcionais. limit 1–200, offset 0–10.000, gap_seconds 1–60
(padrão 5). Máximo 31 dias e 10.000 eventos por seleção; exceder retorna 422,
sem resultado truncado disfarçado. Datas sem timezone/futuras/invertidas são
rejeitadas. UI exibe no fuso local; janelas sempre ancoradas em UTC, sem ambiguidade DST.

Snapshot tem summary de toda seleção; buckets, intervals e transitions paginados
com items/total/limit/offset. Exportar JSON na UI salva esse envelope, CSV salva
apenas a página de buckets, não todo o banco. Usar paginação para export completo.
Retenção/exclusão dos eventos pode mudar resultados recalculados; snapshots
persistidos não dependem de recomputação e são removidos na exclusão sintética.

Replay coleta páginas com fim UTC fixo, até 10.000 frames, sem mudar o estado da
sessão ao vivo. O cliente oferece play/pause/seek/velocidade; lacunas >2 s são
comprimidas visualmente, nunca alteram os timestamps ou agregados. Mudanças de
filtro exigem Consultar histórico; a seleção aplicada fica ligada aos exports.

Novo trecho é atribuído em start/resume. Legado sem segment_id não recebe sessão
inventada. Intervalos entre eventos consecutivos do mesmo trecho/fonte usam o
estado anterior; gap acima do limite ou tick não crescente gera unknown. Sem
intervalo antes do primeiro/depois do último evento. Somar fontes sobrepostas
não representa tempo exclusivo de uma sala; separar source_id para essa análise.

Entradas/saídas = deltas líquidos entre contagens conhecidas com continuidade,
sem identificar ocupantes ou provar cruzamentos. Fração de presença e ocupação
média são por amostra. Ausência de confiança/modelo/sinal continua null. Métricas
de fila usam processamento observado do software; nenhuma qualidade RF é medida.
Definições dos quantis e taxa em DECISIONS.md. Contratos antigos permanecem aceitos.
