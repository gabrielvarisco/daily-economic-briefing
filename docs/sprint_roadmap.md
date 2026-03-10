# Roadmap de melhorias em sprints

## Premissas
- Você como Tech Lead define prioridade de negócio.
- Eu apoio execução técnica, propostas de arquitetura e implementação incremental.
- Cada sprint fecha com checklist de qualidade + demo curta do briefing.

<<<<<<< HEAD
=======
## Status consolidado
- ✅ Sprint 1 concluída.
- ✅ Sprint 2 concluída.
- 🟡 Sprint 3 concluída parcialmente (personas ainda pendente).
- ✅ Sprint 4 concluída.

>>>>>>> 39bafce (Update CI workflows and refresh sprint roadmap)
## Sprint 1 (semana 1) — Confiabilidade base (P0)
**Objetivo:** reduzir risco operacional e eliminar duplicação crítica.

### Entregas
1. Unificar orquestração das seções em módulo único (`Scripts/pipeline.py`).
2. Logging estruturado JSON com `run_id`, seção e tempo de execução.
3. Retry com backoff no envio para Telegram (429/5xx).
4. Dedupe de blocos enviados para evitar duplicação em retries.

### Critérios de pronto
- Execução `main.py` e `build_site.py` usando o mesmo pipeline.
- Logs legíveis para troubleshooting operacional.

<<<<<<< HEAD
=======
### Status
✅ Concluída.

>>>>>>> 39bafce (Update CI workflows and refresh sprint roadmap)
## Sprint 2 (semana 2) — Qualidade de dados e observabilidade
**Objetivo:** confiabilidade de números e diagnóstico rápido de erro.

### Entregas
1. Metadados por seção no snapshot (`status`, `elapsed_ms`, `source`).
2. Regras de sanidade para variações extremas em ativos.
3. Relatório resumido de saúde diária (seções ok/empty/error).

### Critérios de pronto
- Snapshot com campos de monitoramento.
- Falhas de dados destacadas com sinalização explícita.

<<<<<<< HEAD
=======
### Status
✅ Concluída.

>>>>>>> 39bafce (Update CI workflows and refresh sprint roadmap)
## Sprint 3 (semanas 3-4) — Evolução de inteligência de mercado
**Objetivo:** aumentar qualidade analítica para uso profissional.

### Entregas
1. Drivers do dia (curva 2s10s, VIX/MOVE, HY spread, DXY).
2. Score de notícias com recência + dedupe por evento.
3. Blocos de saída por persona: trader vs PM/CIO.

### Critérios de pronto
- Briefing com mais sinal e menos ruído.
- Narrativa separada por tipo de usuário.

<<<<<<< HEAD
=======
### Status
🟡 Parcialmente concluída (pendente: blocos por persona).

>>>>>>> 39bafce (Update CI workflows and refresh sprint roadmap)
## Sprint 4 (semanas 5-6) — Governança e escala
**Objetivo:** preparar produto para operação contínua.

### Entregas
1. Testes unitários para parsing e cálculos.
2. CI simples (lint + testes + smoke build).
3. Versionamento de schema de snapshot.

### Critérios de pronto
- Pipeline com validação automática a cada alteração.
- Menor risco de regressão.
<<<<<<< HEAD
=======

### Status
✅ Concluída.

## Próxima sprint (semana 7) — Backlog pendente priorizado
**Objetivo:** fechar lacunas analíticas e melhorar robustez operacional.

### Itens planejados
1. Implementar blocos de saída por persona (trader e PM/CIO) com template dedicado.
2. Adicionar fallback textual quando fontes de mercado retornarem vazio, sem quebrar narrativa.
3. Criar validação de schema do snapshot em CI para impedir regressões de contrato.
4. Incluir monitoramento de duração total do pipeline com alerta para execução lenta.

### Critérios de pronto
- Saída por persona ativável por configuração.
- Snapshot validado automaticamente no CI.
- Execuções lentas reportadas em log de saúde.
>>>>>>> 39bafce (Update CI workflows and refresh sprint roadmap)
