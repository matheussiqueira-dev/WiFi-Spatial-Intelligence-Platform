# Triagem de avisos e falhas — 15/10/2026

HEAD 2767417, feat/platform-foundation, dirty. Evidências de comandos no relatório
de verificação. A lista original de 68 warnings da IDE não está disponível: origem
e classificação individual UNVERIFIED. Não foram inventados 68 itens.

| Evidência observada | Classe / risco | Ação / situação |
| --- | --- | --- |
| Starlette TestClient usando httpx depreciado | dependência de teste / baixo | Instalado httpx2 2.13.1 conforme código instalado e [documentação oficial](https://starlette.dev/testclient/); locks regenerados. Suítes seguintes sem esse aviso |
| Ruff E501 nas fixtures SQL e código novo | lint / bloqueia gate | Reproduzido exit 1; corrigido por quebra de linhas/formatação, sem desativar regra |
| Zod rejeitando UTC +00:00 | contrato / P1 corrigido | Schema analytics aceita Z ou offset zero; offsets não UTC continuam rejeitados |
| safeExtend rejeitando troca de literais no TypeScript | tipos / P1 corrigido | Novo schema nativo composto de campos e refinamento próprio, sem cast/any |
| Playwright status ambíguo (carregamento/resultado) | teste / corrigido | Nome acessível específico para resultado; fluxo passou além desse ponto |
| Overflow em 320 px | UI / P2 corrigido | Grade mobile minmax(0,1fr), controles em duas colunas; E2E direcionado passou |
| npm encaminhando --grep ao workspace incorretamente | comando / corrigido | Usar npm.cmd run test:e2e --workspace apps/web -- --grep analytics:; tentativa anterior sem testes registrada como falha |
| NO_COLOR ignorado por FORCE_COLOR | ambiente CLI / informativo | Sem efeito funcional; não suprimir falhas nem alterar políticas globais |
| pip instalado como root em Dockerfile.verify | build descartável / informativo | Container de verificação; produção continua non-root. Sem instalação global Windows |
| ConnectionResetError WinError 10054 após interrupção de stream | runtime Windows / residual recorrente em testes de fechamento forçado | Observado também no MVP nativo; recuperação passou. Não ocultado. Investigar se ocorrer fora dos testes de falha |
| CancelledError no teardown WebSocket em Python 3.13 | sincronização de teste / corrigido | Execução revelou 110 pass/1 fail; teste agora fecha socket e exige liberação dos assinantes antes do teardown, sem suprimir exceções |
| julianday arredondando limites submilissegundo | persistência / P1 corrigido | Red retornou zero em vez de um evento; comparação usa epoch inteiro em microssegundos via UDF SQLite determinística; regressão passou |
| Porta 4860 ocupada | operação / preservada | Nenhum processo encerrado; verificação permite 4970/4971 |
| Python/tsx invisíveis no sandbox, ENOMEM em uv_os_get_passwd | ambiente / resolvido por execução autorizada | Repetido fora do sandbox; nenhum bypass de controle do SO |

Compatibilidade: Chromium instalado. Firefox/WebKit e NVDA não encontrados no
Windows: BLOCKED para execução/validação manual, não aprovados por inferência.
Python 3.13 validado em Docker, não instalado globalmente no Windows. Contagens
exatas e limites temporais das imagens estão em VERIFICATION_REPORT.
