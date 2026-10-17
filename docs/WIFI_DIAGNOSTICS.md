# Diagnóstico Wi-Fi com computador e roteador

Este módulo mede o enlace informado pelo Windows. Não requer equipamento novo,
conta externa ou serviço pago. Funciona com o HUAWEI BE3 sem instalar firmware.
A placa do computador determina o padrão negociado: neste host foi observado
802.11ac, mesmo com um roteador anunciado como Wi-Fi 7.

## Operação

Com a stack local iniciada e `.env` configurado pelo bootstrap:

```powershell
docker compose up --build --detach --wait
.\scripts\dev\start-wifi-monitor.ps1 -Background -GatewayProbes
# Para encerrar apenas este coletor:
.\scripts\dev\stop-wifi-monitor.ps1
```

Por padrão o coletor usa o `SPATIAL_TOKEN` (admin). Para menor privilégio, emita um token
de **Operação** em Perfis de acesso e defina `$env:SPATIAL_AGENT_TOKEN` na sessão antes de
iniciar o coletor; o valor é lido só do ambiente, nunca de argumentos ou logs (ADR-015).

Abra `http://127.0.0.1:3000/dashboard#network`, conecte com o token local e acompanhe
**Diagnóstico Wi-Fi real**. A coleta acontece a cada 15 segundos; a interface
consulta a API a cada 10 segundos. O coletor deve executar no Windows: o contêiner
Linux não acessa a interface Wi-Fi do host. Não foi instalado serviço ou autostart;
após reiniciar o computador, execute o comando de início novamente.

Sem `-GatewayProbes`, só são lidos os atributos do enlace. Com a opção, são enviadas
três sondas ICMP de até um segundo ao único gateway IPv4 privado da interface Wi-Fi.
Nenhuma sonda é enviada à Internet. O coletor não dispara varredura nem sonda dispositivos; com `-ChannelSurvey` lê apenas a lista passiva do Windows (abaixo).
Múltiplas interfaces conectadas/gateways ambíguos causam abstenção, sem escolher
um alvo arbitrário. O parser suporta saída de `netsh` em português e inglês.

## Ocupação de canais (opt-in, desde 15/10/2026)

```powershell
.\scripts\dev\start-wifi-monitor.ps1 -Background -GatewayProbes -ChannelSurvey
```

A cada 60 segundos o coletor lê `netsh wlan show networks mode=bssid`, ou seja, a
lista que o Windows **já obteve** em suas varreduras passivas; não dispara varredura,
não se conecta e não sonda redes de terceiros. No próprio host, cada rede é reduzida a
banda, canal, sinal (%) e utilização do canal (BSS Load, quando anunciada) e agregada
por canal. SSID, BSSID, autenticação e taxas são descartados antes do envio.

`GET /api/v1/network/channel-plan?hours=1&location=` calcula, por banda, um índice de
interferência para os canais candidatos sem DFS (2,4 GHz: 1/6/11; 5 GHz: 36–48 e
149–165), com sobreposição de ±4 canais em 2,4 GHz e bloco de 80 MHz em 5 GHz. Uma
rede é descontada no canal atual (o próprio roteador). A recomendação só sugere troca
quando a diferença é ≥ 0,5 do índice; 6 GHz é apenas listado. Nada é alterado no
roteador. Limites: 20.000 varreduras armazenadas, 2.000 por consulta, janela de 24 h.
Tabela `channel_surveys`, migração aditiva `0008`.

## Uso diário

1. Deixe o computador no local de trabalho e observe sinal, latência e falhas ICMP.
2. Dê um nome ao ponto, por exemplo `Escritorio`; as próximas amostras usam esse nome.
3. Mova o computador, defina outro ponto e acumule leituras em condições comparáveis.
4. Compare os pontos e exporte CSV de até 24 horas. O arquivo inclui todas as
   amostras da consulta, independentemente da página visível.

O nome do ponto é informado manualmente; não existe localização espacial por RF.
Amostras de pontos diferentes podem refletir horários, carga e condições diferentes.
A recomendação de canal (seção acima) é apenas sugestão; o roteador nunca é reconfigurado.

## Tendência, alertas e avaliação dos pontos (desde 17/10/2026)

- `GET /api/v1/network/health` traz séries por hora (15–240 min) das últimas 2–24 h e
  compara a **última hora** com as horas anteriores do mesmo filtro. Alertas
  consultivos: sinal médio caiu ≥ 15 pontos; latência p95 ≥ 2× a base e ≥ base + 20 ms;
  sondas sem resposta ≥ 5% (com ≥ 10 enviadas); ≥ 3 desconexões; coletor parado.
  Sem leituras suficientes (5 de sinal, 10 respostas, 10 sondas), a resposta lista a
  abstenção em vez de alertar. Nenhuma causa é presumida.
- A tabela de pontos é ordenada do melhor para o pior com a avaliação Bom (sinal ≥ 70%
  e perda < 5%), Regular (≥ 45% e < 15%), Fraco ou Sem dados. Heurística para comparar
  cômodos da mesma casa, não teste de velocidade.
- Webhook local (opcional): com `SPATIAL_ALERT_WEBHOOK_URL` (IP literal de loopback ou
  rede privada, sem DNS) e `SPATIAL_ALERT_WEBHOOK_SECRET` (≥ 32 caracteres), a API
  avalia os alertas por ponto a cada `SPATIAL_ALERT_WEBHOOK_INTERVAL_SECONDS` e envia
  `alert.raised`/`alert.cleared` por POST. O receptor confere
  `X-Spatial-Signature: sha256=HMAC(secret, "<X-Spatial-Timestamp>.<corpo>")` e deve
  recusar timestamps antigos. Sem redirect e sem proxy; falhas são registradas (até 1.000
  entregas, sem corpo) e repetidas no ciclo seguinte. O estado ativo fica em memória:
  após reinício, alertas ainda ativos são reenviados (entrega pelo menos uma vez).
- `DELETE /api/v1/network/history?confirm=ERASE[&location=…]` apaga medições e
  varreduras (de um ponto ou todas); a auditoria guarda só o fato. Exporte antes.

## Interpretação e limites

- Sinal é qualidade percentual fornecida pelo Windows, não RSSI medido em dBm.
- RX/TX são taxas negociadas do enlace, não velocidade da Internet.
- ICMP sem resposta pode indicar limitação do roteador. Não prova perda do Wi-Fi,
  falha da operadora ou ausência de Internet.
- Transição de conectado para desconectado só é contada entre amostras do mesmo
  coletor e ponto com intervalo de até 45 segundos. Quedas menores podem escapar.
- Após 45 segundos sem coleta, o painel indica coletor desatualizado. Computador
  suspenso, coletor parado e API indisponível são lacunas, não quedas de rede.
- Percentual conectado é fração de amostras com estado conhecido, não SLA temporal.
  Lacunas internas maiores que 45 segundos são mostradas sem extrapolação.
- Média/p95 usam apenas respostas ICMP recebidas. P95 é o percentil empírico inferior;
  poucas respostas não permitem concluir estabilidade. Alertas de sinal abaixo de
  40% ou sondas sem resposta acima de 20% são heurísticas de interface.

## Contrato, privacidade e persistência

API autenticada em `/api/v1/network`: `config`, `samples`, `report`, `export.csv`.
Credencial fica na memória; o agente lê `.env` internamente e só entrega a um
endpoint HTTP de loopback com porta explícita, sem proxy ou redirecionamento.
Não são enviados SSID, BSSID/MAC, senha, IP do gateway, conteúdo de tráfego ou saída
bruta do PowerShell/netsh. Nomes de pontos são dados locais escolhidos pelo operador.

SQLite usa tabelas próprias `network_samples` e `network_configuration`, migração
aditiva `0007_network`. Limites: 100.000 amostras, 20 nomes de pontos, janela máxima
de 24 horas e 10.000 amostras por consulta/exportação, 200 por página na API.
Ao atingir capacidade, a gravação é recusada; não há expurgo automático nem exclusão
do histórico para preparar demonstrações. Com 15 segundos, 100.000 amostras equivalem
a aproximadamente 17 dias de coleta contínua. Arquivamento/expurgo dedicado é pendente.

`runtime/wifi-monitor-status.json` contém somente PID, contadores e horário UTC.
O lock impede duas instâncias contínuas; o script de parada valida a identidade do
processo e solicita encerramento cooperativo. Lock órfão exige inspeção manual.
Falhas de entrega não são reenviadas: tornam-se lacunas. Relógio deve estar correto;
API aceita amostras de até 120 segundos atrás e tolera 5 segundos de adiantamento.

Telemetria de host é `HOST_NETWORK_TELEMETRY / L2_LIVE_UNVALIDATED`: informação
operacional sem validação independente. O token autentica o escritor local, sem
atestar a veracidade física do payload. Fixtures automatizadas só entram em bases
isoladas de teste. O domínio espacial continua `L0_SYNTHETIC`, com sensores virtuais;
nenhum valor deste módulo alimenta pessoas/animais, poses, sinais vitais ou CSI.

Referências técnicas: [netsh WLAN](https://learn.microsoft.com/en-us/windows/win32/nativewifi/netsh-wlan),
[Ping.Send](https://learn.microsoft.com/en-us/dotnet/api/system.net.networkinformation.ping.send).
