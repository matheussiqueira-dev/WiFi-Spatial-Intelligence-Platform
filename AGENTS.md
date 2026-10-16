# Instruções do repositório

1. Leia integralmente `docs/PROJECT_MASTER_PLAN.md` quando existir, além de
   `CLAUDE.md` e `docs/PROGRESS.md`. Não invente conteúdo do documento mestre ausente.
2. Antes de editar, confira Git e arquivos existentes. Preserve alterações locais,
   inclusive arquivos de IDE já staged. Não use reset, clean ou rebase destrutivos.
3. Continue a arquitetura FastAPI/SQLite/Next.js deste MVP. Não reinicie o projeto.
4. Dados gerados são sempre `L0_SYNTHETIC`; sensores são virtuais. Não apresente
   simulação como sensoriamento real, inferência ou validação científica/clínica.
5. Não utilize serviços pagos. Commit e push exigem autorização explícita atual.
6. Python por ambiente virtual; npm pelo lockfile; em PowerShell use `npm.cmd`.
7. Não versione `.env`, runtime, SQLite, logs, tokens ou dumps. Credenciais do
   frontend ficam em memória; conexões WebSocket autenticam no primeiro frame.
8. Verifique lint, tipos, testes, build e integração com API real; use
   `scripts/verify/check.ps1`. Nunca marque algo concluído apenas por criar arquivos.
9. Servidores de teste usam portas e bases isoladas. Não encerre processos alheios,
   não apague histórico de uso para preparar testes e não desative controles do SO.
10. Mantenha documentação e registro de progresso com evidências e pendências.

Estas instruções complementam as regras da pasta pai e as instruções do usuário.
