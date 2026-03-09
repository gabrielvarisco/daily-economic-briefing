# daily-economic-briefing

Briefing diário de mercado com foco em Brasil, EUA, macro global e cripto, com saída em Telegram e relatório HTML.

## Diagnóstico profissional
Foi adicionada uma análise técnica e de produto com recomendações priorizadas em:
- confiabilidade operacional,
- qualidade de dados,
- evolução analítica,
- governança e escala.

Veja em: `docs/professional_improvements.md`.

## Roadmap em sprints
Plano de execução incremental em: `docs/sprint_roadmap.md`.

## Instalação rápida (local)
1. Crie e ative um ambiente virtual.
2. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure variáveis:
   ```bash
   export TELEGRAM_TOKEN="<seu_token>"
   export CHAT_ID="<seu_chat_id>"
   ```
4. Execute:
   ```bash
   python main.py
   ```

## Rodar via GitHub Actions (YAML)
O workflow principal é `.github/workflows/daily.yml` e usa os secrets:
- `TELEGRAM_TOKEN`
- `CHAT_ID`

No GitHub, configure em:
`Settings -> Secrets and variables -> Actions`.

## Observações de rede (yfinance)
Se sua rede bloquear Yahoo (proxy/403), ajuste:
- `YF_RETRIES` (default: `3`)
- `YF_RETRY_PAUSE` (default: `1.0`)
- `YF_TIMEOUT` (default: `15`)

Exemplo para rede restrita:
```bash
export YF_RETRIES=1
export YF_TIMEOUT=8
```
