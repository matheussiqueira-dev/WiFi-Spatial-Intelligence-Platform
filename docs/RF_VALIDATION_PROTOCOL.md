# Protocolo proposto de validação física — F7 BLOCKED

Nenhuma captura foi autorizada/executada nesta rodada. Nenhuma métrica real está
preenchida. Este documento prepara o experimento; não prova validação RF.

Pré-condições: autorização do proprietário do dispositivo e do ambiente, pessoas
informadas e consentidas, possibilidade de recusa/retirada, finalidade e período
explícitos, referência adequada, revisão de segurança/privacidade e hardware
calibrado. Não comprar/flashear/transmitir sem autorização específica.

Pergunta inicial: presença/ocupação em uma sala autorizada, sem identidade nem
biometria. Registrar disposição dos sensores/coordenadas, canais, taxas, relógios,
calibração e interferências. Separar sessões/ambientes/participantes por split
antes do treino; reservar sala/configuração independente para domínio cruzado.

Referência: contagem e episódios anotados por observador autorizado com relógio
sincronizado, sem exigir câmera. Definir tolerância temporal e incerteza antes
de coletar. Medir perdas/alinhamento e declarar intervalos sem referência como
unknown. Avaliar presença (precisão/recall/FPR por suporte), ocupação (MAE e
distribuição do erro), latência/p95, rejeição e limites por sala/orientação.
Usar intervalos de confiança adequados às sessões, sem tratar frames correlatos
como participantes independentes. Denominador zero é indisponível.

Minimização: IDs aleatórios não pessoais; separar consentimento de amostras,
guardar localmente com acesso controlado e retenção definida pelo protocolo
aprovado. Não transmitir datasets a terceiros. Backup e retirada devem respeitar
cópias/exports e decisões de retenção. Plano de exclusão só após autorização.

Evidência gravada inicial L1_RECORDED_UNVALIDATED; transmissão autorizada não
implica L3. Contrato real exigirá evolução validada antes de ingestão; o produto
atual permanece L0. L3 só após confronto com referência e relatório reproduzível.
Vitais, sono, apneia, quedas e pose requerem protocolos próprios e referência
adequada; não são diagnóstico, alerta certificado ou imagem através de paredes.

Pendências impeditivas: autorização, hardware, consentimento, referência e
calibração. Responsável por liberar experimento: proprietário e participantes.
