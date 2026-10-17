# Protocolo SWF1 — quadros CSI autenticados

Status: `IMPLEMENTED_SYNTHETIC` (parser, receptor e simulador de transporte). Placa real:
**NOT_TESTED** — quadros sem a flag sintética são recusados (`hardware_not_tested`) até
a validação descrita em `RF_VALIDATION_PROTOCOL.md`. Implementação:
`apps/api/app/domain/csi_frame.py`; testes: `apps/api/tests/test_csi_frame.py`.

Especificação própria do projeto, escrita a partir de conceitos públicos de CSI do
ESP-IDF (canal, largura de banda, RSSI, I/Q por subportadora). Nenhum código de
firmware ou parser do RuView foi usado. Ver `ORIGINALITY_REGISTER.md`.

## Layout (little-endian)

| Offset | Tamanho | Campo | Regra |
| --- | --- | --- | --- |
| 0 | 4 | magic | `SWF1` |
| 4 | 1 | version | `1` |
| 5 | 1 | flags | bit 0 = sintético; demais bits devem ser 0 |
| 6 | 2 | header_length | `44` |
| 8 | 16 | device_id | UUID (bytes) do dispositivo pareado |
| 24 | 4 | sequence | estritamente crescente por dispositivo |
| 28 | 8 | timestamp_us | microssegundos desde 1970-01-01 UTC |
| 36 | 1 | channel | 1–233 |
| 37 | 1 | bandwidth | 0=20, 1=40, 2=80, 3=160 MHz |
| 38 | 1 | rssi_dbm | inteiro com sinal, −127 a 0 |
| 39 | 1 | noise_floor_dbm | inteiro com sinal, −127 a 0 |
| 40 | 2 | subcarriers | 1–512 |
| 42 | 2 | reserved | 0 |
| 44 | 4·n | I/Q | pares `int16 I, int16 Q` por subportadora |
| 44+4·n | 16 | tag | HMAC-SHA256(chave do dispositivo, bytes 0..44+4·n) truncado |

Tamanho total: 64 a 2108 bytes.

## Recepção

1. Tamanho, magic, versão e comprimento de cabeçalho.
2. Dispositivo pareado (até 32, chave de 32 bytes ou mais).
3. **Autenticação antes de confiar em qualquer outro campo** (comparação em tempo
   constante).
4. Bits reservados, contagem de subportadoras coerente com o tamanho, rádio e timestamp.
5. No receptor com estado: frescor (−2 s a +60 s), replay/ordem por sequência e recusa
   de hardware não testado.

Cada recusa tem um código fixo (`length`, `magic`, `version`, `unpaired`,
`authentication`, `reserved_bits`, `subcarriers`, `radio`, `timestamp`, `stale`,
`replay_or_out_of_order`, `hardware_not_tested`) contado pelo receptor, sem registrar o
conteúdo do quadro.

## Verificação

- Ida e volta exata, recusas estruturais e semânticas com tag válida.
- Fuzzing determinístico (20.000 mutações: inversão de bits, truncamento, extensão,
  emenda e ruído; mais 5.000 cabeçalhos aleatórios reassinados): só `FrameError`, nenhum
  quadro alterado aceito.
- Simulador de transporte com perda, duplicação, reordenação e corrupção: todo quadro
  aceito é idêntico ao original e as sequências aceitas são estritamente crescentes.

## Fora do escopo desta etapa

Não há listener UDP/serial exposto nem firmware gravado: compra de placa, gravação e
coleta exigem autorização explícita, pareamento físico e o protocolo de validação.
Recepção em rede, quando existir, deve ficar em loopback/rede privada por padrão.
