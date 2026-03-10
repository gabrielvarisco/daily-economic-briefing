#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   Scripts/sync_branch.sh [branch_base]
# Exemplo:
#   Scripts/sync_branch.sh main

BASE_BRANCH="${1:-main}"
CURRENT_BRANCH="$(git branch --show-current)"

if [[ -z "${CURRENT_BRANCH}" ]]; then
  echo "[sync] Não foi possível detectar branch atual."
  exit 1
fi

if [[ "${CURRENT_BRANCH}" == "${BASE_BRANCH}" ]]; then
  echo "[sync] Você está na branch base (${BASE_BRANCH}). Troque para a branch da PR antes de rodar."
  exit 1
fi

echo "[sync] Branch atual: ${CURRENT_BRANCH}"
echo "[sync] Base: ${BASE_BRANCH}"

echo "[sync] Fetch remoto..."
git fetch origin

echo "[sync] Rebase em origin/${BASE_BRANCH}..."
git rebase "origin/${BASE_BRANCH}"

echo "[sync] Rodando testes unitários..."
python -m unittest discover -s tests -p "test_*.py" -v

echo "[sync] Push com segurança..."
git push --force-with-lease origin "${CURRENT_BRANCH}"

echo "[sync] OK: branch sincronizada, testada e enviada sem conflito pendente local."
