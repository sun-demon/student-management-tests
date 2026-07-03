#!/usr/bin/env bash
# Быстрый деплой на VPS (Ubuntu/Debian)
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/edumanage}"
REPO_URL="${REPO_URL:-}"

echo "==> Установка Docker (если нет)..."
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sh
  systemctl enable docker
  systemctl start docker
fi

mkdir -p "$APP_DIR"
if [ -n "$REPO_URL" ]; then
  git clone "$REPO_URL" "$APP_DIR" || (cd "$APP_DIR" && git pull)
else
  echo "Скопируйте проект в $APP_DIR вручную (scp/rsync)"
fi

cd "$APP_DIR"
docker compose build
docker compose up -d

echo ""
echo "Готово! Приложение на порту 5000."
echo "Откройте: http://YOUR_SERVER_IP:5000"
echo ""
echo "Для домена + HTTPS настройте nginx reverse proxy (см. deploy/nginx.conf.example)"
