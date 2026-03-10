# daily-economic-briefing

Briefing diário de mercado com foco em Brasil, EUA, macro global e cripto.
O projeto gera:
- mensagens para Telegram,
- snapshot histórico em JSON (com metadata de execução),
- relatório HTML.

## Estrutura principal
- `main.py`: pipeline completo com envio Telegram.
- `build_site.py`: geração silenciosa de snapshot + HTML (sem envio).
- `Scripts/pipeline.py`: orquestração central das seções.
- `Scripts/logging_utils.py`: logging estruturado (JSON).
- `.github/workflows/daily.yml`: execução diária no GitHub Actions.
- `.github/workflows/tests.yml`: testes unitários no CI.

## Instalação local
1. Criar ambiente virtual.
2. Instalar dependências:

```bash
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente (Telegram):

```bash
export TELEGRAM_TOKEN="<seu_token>"
export CHAT_ID="<seu_chat_id>"
```

## Execução
### Rodar briefing completo (com envio Telegram)
```bash
python main.py
```

### Rodar apenas geração de snapshot + HTML
```bash
python build_site.py
```

## Testes
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## GitHub Actions
O workflow principal usa os secrets:
- `TELEGRAM_TOKEN`
- `CHAT_ID`

Configurar em:
`Settings -> Secrets and variables -> Actions`.

## Variáveis úteis de operação
### Telegram
- `DRY_RUN_TELEGRAM=1` (não envia mensagem, só simula envio)
- `TELEGRAM_RETRIES` (retries de envio)

### Mercado (yfinance)
- `YF_RETRIES` (default `3`)
- `YF_RETRY_PAUSE` (default `1.0`)
- `YF_TIMEOUT` (default `15`)

Exemplo para rede restrita:
```bash
export YF_RETRIES=1
export YF_TIMEOUT=8
```

## Documentação adicional
- Diagnóstico e melhorias: `docs/professional_improvements.md`
- Roadmap em sprints: `docs/sprint_roadmap.md`


## Observabilidade no snapshot
O snapshot diário inclui `schema_version`, métricas por seção (`status`, `elapsed_ms`, `source`) e `health_report` consolidado da execução.


## Fluxo rápido para evitar conflitos na PR
Em vez de resolver conflito arquivo por arquivo na web, rode localmente:

```bash
Scripts/sync_branch.sh main
```

Esse comando faz:
1. `git fetch origin`
2. `git rebase origin/main` na sua branch atual
3. roda testes unitários
4. `git push --force-with-lease`

Se houver conflito, você resolve **uma vez localmente**, continua o rebase e roda o script de novo.
