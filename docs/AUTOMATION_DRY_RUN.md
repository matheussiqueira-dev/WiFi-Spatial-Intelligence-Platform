# Regras locais — DSL restrita, somente dry-run

POST /api/v1/automation/rules exige Bearer e body {name,field,threshold}.
field=presence testa igualdade booleana (threshold 0/1); field=occupancy testa
contagem >= threshold inteiro 0..20. Não aceita expressões, scripts, URL, ação,
pickle ou extensões. Nome tem 1..60 caracteres e é renderizado como texto React.
Cada regra tem UUID/versão 1, fica ativa até POST /rules/{id}/revoke.
GET /rules lista até 20; GET /decisions aceita limit 1..200/offset 0..1000.

Cada evento novo persistido avalia regras ativas na mesma transação SQLite;
inserção duplicada não cria decisão duplicada. Resultado inclui rule_id/event_id,
matched, UTC, L0_SYNTHETIC, DRY_RUN e dispatched=false. Nunca aciona serviço ou
dispositivo. Contagem desconhecida não satisfaz predicado de ocupação. Revogação
drena fila sob lock de controle; depois da resposta não há decisão pendente da
regra revogada. Criação/revogação auditadas, histórico preservado.

Limites: 20 regras totais (inclusive revogadas), 1.000 decisões. Ao atingir teto,
novas decisões deixam de ser registradas e status/UI alertam capacidade atingida;
não implica condição avaliada nem ação executada. Sem expurgo automático.
Excluir eventos sintéticos não revoga regras nem apaga decisões nesta versão;
referências antigas podem deixar de ter evento no histórico por retenção/exclusão.
IDs não pessoais e L0 não substituem política de dados se houver captura futura.

F5 continua parcial: sem consentimento físico, Home Assistant ou plugins. Criar e
revogar regras exige papel `operator` ou `admin`; `viewer` só consulta (ADR-015).
Qualquer destino externo exigirá nova autorização/allowlist/auth e consentimento.
