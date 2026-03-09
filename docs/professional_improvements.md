# Análise profissional do repositório (finanças + engenharia)

## Visão executiva
O projeto já entrega valor: consolida ativos BR/EUA/crypto, gera narrativa diária e publica em Telegram + HTML. A base é funcional para uso pessoal e _desk note_ rápida. Porém, para padrão profissional (uso recorrente, rastreabilidade e escalabilidade), recomendo priorizar 4 frentes:

1. **Confiabilidade operacional** (observabilidade, retries e fail-fast em pontos críticos).
2. **Governança de dados de mercado** (qualidade, latência, versionamento e reconciliação).
3. **Arquitetura e manutenção** (redução de duplicação e configuração centralizada).
4. **Evolução analítica** (indicadores macro/risco mais robustos e métricas de acurácia).

---

## Diagnóstico técnico e de produto

### 1) Arquitetura
- Há duplicação relevante entre `main.py` e `build_site.py` na montagem das seções e no _safe wrapper_; isso aumenta risco de divergência funcional e retrabalho em manutenção.  
- O projeto usa múltiplos scripts especializados (bom para clareza), mas falta uma camada de orquestração única com contrato de entrada/saída por seção.

**Evidências**: mesmas importações, lógica de `_safe_section` e construção de seções em ambos os arquivos.【F:main.py†L6-L85】【F:build_site.py†L1-L50】

### 2) Qualidade de dados e metodologia
- A ingestão de preços depende integralmente de `yfinance` e de chamadas sequenciais; para ambiente profissional, isso pede fallback de provedor e marcação de qualidade (ex.: `source`, `stale_age`, `market_session`).
- O score de notícias é 100% heurístico por palavras-chave, o que é ótimo como MVP, mas suscetível a _headline noise_ e viés semântico.

**Evidências**: download via `yf.download` com retries simples e retorno vazio em falhas; scoring por listas de keywords/negative keywords.【F:Scripts/asset_analyzer.py†L48-L76】【F:Scripts/news_market.py†L25-L55】【F:Scripts/news_market.py†L137-L160】

### 3) Observabilidade e risco operacional
- Logging é feito com `print`, sem níveis (`INFO/WARN/ERROR`), sem correlação de execução e sem métricas de sucesso por seção.
- Envio para Telegram não possui backoff por status code (429/5xx) nem idempotência para evitar duplicação em reprocessamento.

**Evidências**: tratamento de exceções com `print` e envio direto com `requests.post` único por batch.【F:main.py†L29-L51】【F:main.py†L118-L124】

### 4) Entrega de valor financeiro
- A lógica atual de regime de risco já captura sinais táticos (SPY/BTC/VIX), o que é positivo para comunicação executiva diária.
- Falta um bloco de **“drivers do dia”** baseado em decomposição mais profissional: taxa real implícita, surpresa de dados macro, inclinação de curva, spreads de crédito e breadth de mercado.

**Evidências**: regime simplificado por score discreto e narrativa textual de sessão; cards resumidos por regex na camada HTML.【F:Scripts/market_take.py†L26-L52】【F:Scripts/html_report.py†L151-L170】

---

## Melhorias recomendadas (priorizadas)

## P0 (0–2 semanas): estabilizar produção
1. **Unificar orquestração**
   - Criar um módulo único (ex.: `Scripts/pipeline.py`) com:
     - registro das seções;
     - execução com timeout por seção;
     - retorno padronizado (`status`, `duration_ms`, `content`).
2. **Logging estruturado**
   - Trocar `print` por `logging` em JSON; incluir `run_id`, `section`, `elapsed_ms`.
3. **Hardening no Telegram**
   - Backoff exponencial para 429/5xx;
   - checksum do conteúdo por bloco para evitar reenvio duplicado em retries.
4. **README operacional**
   - Incluir setup, variáveis de ambiente, rotina de execução e troubleshooting.

## P1 (2–6 semanas): qualidade analítica
1. **Camada de dados com validação**
   - Salvar metadados por ativo (`timestamp`, sessão, provedor, timezone).
   - Regras de sanidade: `abs(daily_change)`, gaps e outliers por z-score.
2. **Melhorar metodologia de notícias**
   - Separar relevância por classe de ativo (equity, juros, FX, commodities, crypto).
   - Adicionar penalização de notícia repetida por evento e prioridade por recência.
3. **Risk dashboard mais institucional**
   - incluir MOVE, HY spread, 2s10s, DXY real broad, breadth NYSE/Nasdaq.

## P2 (6–12 semanas): governança e escala
1. **Testes e CI**
   - unit tests para parsers/regex e cálculos de retornos;
   - _smoke test_ diário com fixture offline.
2. **Versionamento de snapshots**
   - esquema com versão (`schema_version`) e validação (pydantic/jsonschema).
3. **Camada de distribuição**
   - além de Telegram/HTML, publicar API JSON para consumo de outros canais.

---

## Roadmap sugerido (produto financeiro)
- **Q1**: robustez operacional + reprodutibilidade (P0 completo).
- **Q2**: ganho de qualidade de sinal e redução de ruído (P1 completo).
- **Q3**: escalar para múltiplos perfis de audiência (gestor macro, equity, tesouraria).

---

## KPI para medir se melhorou
1. **Taxa de execução sem falha**: alvo > 99% em 30 dias.
2. **Latência total do briefing**: alvo < 120s.
3. **Cobertura de dados válidos por seção**: alvo > 95%.
4. **Precision de notícias úteis (avaliação humana)**: alvo > 80%.
5. **Tempo de recuperação após falha (MTTR)**: alvo < 15 min.

---

## Recomendações de negócios (olhar de mercado)
- Criar duas saídas de relatório:
  1. **Trader view (rápida)**: regime, variações-chave, eventos do dia.
  2. **PM/CIO view (estratégica)**: cenários, riscos de cauda, posicionamento sugerido.
- Integrar calendário macro com _event risk scoring_ (FOMC/Copom/CPI/NFP) para antecipar volatilidade e ajustar tom da narrativa.
- Introduzir “convicção do sinal” (baixa/média/alta) para evitar overconfidence em dias de dados fracos.
