# Especificação funcional independente

## Adendo de apresentação — estruturas humanas e animais

O operador escolhe visualização articulada isométrica ou planta 2D. Na cena
articulada escolhe pessoa, cão, gato ou elenco misto, volume e articulação; pode
ampliar em tela cheia e sair por Esc. Preferência de movimento reduzido desativa
articulação. Os controles não alteram contratos, contagem, origem, posições ou
histórico. Rigs são procedurais e seus pontos não são inferência/predição.
Não desenhar avatar quando a fonte não contém posições compatíveis. Aplicar as
mesmas regras ao replay. A classificação real de espécies/pose continua pesquisa.

Versão 1, 15/10/2026. Requisitos do proprietário e mestre v3.0, sem código externo.

O operador local autenticado configura uma cena virtual de 8 × 6 m com seis nós
virtuais, 0–20 ocupantes, velocidade 0,25×–4× e semente. O gerador produz verdade
sintética, nunca predição ou propagação física de rádio. Suportar sala vazia,
presença estacionária, movimento, entrada, saída, perturbação, perda de pacotes e
desconexão. Mesma configuração/tick reproduz medidas; UUID/horário não são seed.

Iniciar, pausar, continuar, parar e reiniciar devem respeitar transições explícitas.
Uma pausa/parada concluída impede novas gravações da sessão. Eventos são validados,
persistidos e só depois publicados. Falha de persistência impede sucesso visual.
Histórico mantém seus payloads, IDs e proveniência após reiniciar a API.

Todo evento nativo contém versão, UUID, UTC, fonte, sala, origem de geração,
presença/contagem/posições de verdade sintética, privacidade sintética, modelo e
confiança nulos. Classificação fixa L0_SYNTHETIC. Não há identidade individual,
biometria, CSI próprio, sinais vitais ou modelo científico executado.

As análises recebem intervalo UTC [início,fim), sala e fonte/cenário/trecho opcionais.
Intervalo máximo 31 dias, até 10.000 eventos e páginas de até 200. Janelas de 1 min,
5 min, 1 h e dia são ancoradas em UTC. A UI converte horários para o fuso do cliente.
Ordenar por timestamp e UUID; deduplicar UUID. Média de ocupação é por amostra.
Intervalos com lacuna acima do limite, tick não crescente ou mudança de trecho
não permitem inferir entrada/saída. Contagem null não é zero; deltas são variações
líquidas, sem detectar cruzamentos individuais. Nenhuma extrapolação antes/depois
das observações. Ausência de observação é unknown, não sala vazia.

Playback utiliza exclusivamente eventos persistidos: play/pause/seek/velocidade,
proveniência e aviso REPLAY, sem comandar a sessão ao vivo. Posições só são
desenhadas quando fazem parte da verdade sintética do contrato. Relatórios salvos
permanecem no SQLite; JSON/CSV exportam páginas com limites e evidência explícitos.

Aceite: cenários reproduzíveis em testes puros; contrato Python/TS; API real com
SQLite; controles/WS/autorização; agregados conferidos por fixtures; replay e
exportação em navegador real; restauração preservando payload; modo padrão sem
serviço externo. Screenshots e testes não equivalem a validação física/clínica.
