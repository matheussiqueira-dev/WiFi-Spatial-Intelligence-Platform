# Aquisição futura — protótipo offline F6

Estado: parser/simulador IMPLEMENTED_SYNTHETIC; hardware NOT_TESTED. Não abre
socket, não transmite comando, não lê dispositivo e não é firmware ESP32.
Interface própria formulada sem código upstream. Samples de teste não são CSI.

Envelope JSON UTF-8 até 8 KiB: schema_version=1.0, sensor_id virtual-packet-*,
sequence inteiro uint32, timestamp UTC, samples com 1..128 números finitos até
1e6 absoluto, evidence_level=L0_SYNTHETIC, modality=SYNTHETIC_TEST_SIGNAL,
checksum SHA-256 do JSON canônico sem checksum (sort_keys, separators compactos).
Campos extras são recusados. Parser exige autorização offline explícita por
chamada e allowlist virtual de até 32 fontes; não constitui autenticação física.
Rejeita sequência repetida/invertida, relógio regressivo, mais de 2 s futuro ou
60 s antigo. Clock injetável torna replay de fixture reproduzível. Hash sem chave
detecta corrupção, não prova identidade nem origem de dispositivo malicioso.

Testes: envelope válido, opt-in ausente, fonte não pareada, adulteração, replay,
limites, JSON malformado e 200 entradas de bytes pseudoaleatórios. Não equivale
a fuzzing exaustivo. Domínio sem HTTP/ORM/RuView. Este protocolo experimental não
foi conectado ao stream de observações espaciais: modalidades distintas não são
convertidas artificialmente em ocupação.

Próximo incremento de hardware depende de autorização específica: selecionar
placa/interface pública, documentar licença/SDK/firmware, autenticação pareada,
canal/timestamps, jitter e calibração. Antes de captura: consentimento por ambiente,
inventário de dispositivos autorizados, minimização e armazenamento local. Não há
alegação de compatibilidade física ESP32, coordenadas calibradas ou sinal RF real.
