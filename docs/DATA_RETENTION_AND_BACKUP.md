# Política local de retenção e recuperação

## Rotina recorrente opt-in — roteiro v3

SPATIAL_BACKUP_ENABLED=false por padrão. Habilitar explicitamente na API local
com SPATIAL_BACKUP_DESTINATION=runtime/backups e
SPATIAL_BACKUP_INTERVAL_SECONDS=86400 (mínimo 60). Executa snapshot imediato após
migração e depois pelo intervalo enquanto a API estiver aberta. Nenhuma tarefa
global instalada. GET /api/v1/governance/status informa enabled/running,
successes/last_success UTC/last_error sanitizado. Ciclos reais observados somente
em fixtures nesta execução; não declarar proteção recorrente ativa no banco de uso.
Lock exclusivo por destino impede sobreposição e não é roubado após crash;
operador deve verificar processo antes de tratar lock obsoleto. Encerramento
aguarda cópia em curso. Nunca chama prune/retain automaticamente. Hold permanece.
Responsável: proprietário local. Snapshot diário e pré-migração recomendados.
Mesmo disco não protege contra perda física; cópia externa depende do operador.

15/10/2026. Dados atuais exclusivamente L0_SYNTHETIC. Operação por proprietário
local do workspace; não há serviço público, papéis multiusuário ou captura real.

Eventos: últimos SPATIAL_RETENTION_EVENTS, padrão 10.000, limites 100–100.000.
Relatórios: últimos 100 snapshots. Exclusão sintética exige sessão parada e também
remove relatórios derivados; auditoria permanece. Backups/exports antigos são
cópias separadas e não são apagados implicitamente pela exclusão no dashboard.

## Backup e restore

Utilizar scripts/backup/backup.ps1 e restore.ps1 ou o módulo app.maintenance com
o venv. Backup usa sqlite3.Connection.backup (inclui WAL consistente), verifica
PRAGMA integrity_check e grava recibo SHA-256. Guardar em runtime/backups, fora do
Git. Frequência proposta: uma cópia diária antes do uso e antes de migração ou
expurgo; o operador executa, não há tarefa global/scheduler instalado.

Restore verifica checksum/integridade e exige destino novo, sem arquivo ou
sidecars existentes. Não altera banco ativo; validar contagens/payloads antes de
qualquer decisão de substituição, que permanece fora do script. Testes usam bases
temporárias; nenhum histórico de uso foi apagado para executar verificações.

Snapshots: conservar ao menos sete e todos os últimos 30 dias. `prune` é operação
explícita de manutenção: só considera snapshot-*.db com manifesto reconhecido e
hash íntegro, nunca arquivo de auditoria ou banco de uso. Diretório e recibos devem
ser privados. Copiar apenas artefatos necessários, sem .env, logs ou tokens.

## Auditoria e proteção

90 dias mínimos. `retain` exige --confirm-offline e aplicação parada. Antes de
apagar controles antigos elegíveis, produz backup consistente e arquivo JSON
verificado por SHA-256. Eventos security.* e audit.* não são expurgados por esse
comando. Arquivo irmão do banco com extensão .hold bloqueia expurgo (ex.: spatial.hold).
Qualquer exceção legal/consentimento/dado real requer decisão específica: não há
autorização geral para apagar dados pessoais ou evidência protegida.

Não há endpoint de expurgo irrestrito. Proteção é lógica e operacional: quem tem
escrita direta no disco pode alterar banco/recibos. Não se alega trilha inviolável.
Os eventos de autenticação negada existentes não são todos persistidos na tabela
de auditoria; extensão para trilha completa de segurança é pendência explícita.

## Logs

Backend spatial/uvicorn: arquivo application.log junto ao banco, rotação 1 MiB ×
seis arquivos (ativo + cinco cópias). Docker API/web/legado: json-file 2 MiB × três.
Launchers mantêm logs de startup em artifacts; traces Playwright podem conter
credenciais de teste e continuam locais/ignorados. Logs de desenvolvimento Next.js
ficam no terminal do operador; não há coleta externa. Não registrar segredo ou
payload de autenticação. Expurgo de logs de uso fora dessas rotações exige revisão
do operador; nenhum controle de segurança do Windows foi alterado.
