# Roadmap de melhorias em sprints

## Premissas
- Você como Tech Lead define prioridade de negócio.
- Eu apoio execução técnica, propostas de arquitetura e implementação incremental.
- Cada sprint fecha com checklist de qualidade + demo curta do briefing.

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

## Sprint 2 (semana 2) — Qualidade de dados e observabilidade
**Objetivo:** confiabilidade de números e diagnóstico rápido de erro.

### Entregas
1. Metadados por seção no snapshot (`status`, `elapsed_ms`, `source`).
2. Regras de sanidade para variações extremas em ativos.
3. Relatório resumido de saúde diária (seções ok/empty/error).

### Critérios de pronto
- Snapshot com campos de monitoramento.
- Falhas de dados destacadas com sinalização explícita.

## Sprint 3 (semanas 3-4) — Evolução de inteligência de mercado
**Objetivo:** aumentar qualidade analítica para uso profissional.

### Entregas
1. Drivers do dia (curva 2s10s, VIX/MOVE, HY spread, DXY).
2. Score de notícias com recência + dedupe por evento.
3. Blocos de saída por persona: trader vs PM/CIO.

### Critérios de pronto
- Briefing com mais sinal e menos ruído.
- Narrativa separada por tipo de usuário.

## Sprint 4 (semanas 5-6) — Governança e escala
**Objetivo:** preparar produto para operação contínua.

### Entregas
1. Testes unitários para parsing e cálculos.
2. CI simples (lint + testes + smoke build).
3. Versionamento de schema de snapshot.

### Critérios de pronto
- Pipeline com validação automática a cada alteração.
- Menor risco de regressão.
