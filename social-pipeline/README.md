# Автопубликация роликов Hitman (n8n + Postiz)

Конвейер для своего сервера: готовый ролик (сделанный Claude, Codex или вручную) отправляется
одним запросом в n8n, n8n отдаёт его в Postiz, а Postiz публикует его в YouTube/Shorts, TikTok,
Instagram Reels, Telegram и другие площадки, сразу или по расписанию.

```
Claude / Codex / скрипт ──POST──▶ n8n (вебхук) ──API──▶ Postiz ──▶ YouTube, TikTok, Instagram, Telegram…
```

Всё работает на своём сервере: Postiz (AGPL-3.0), n8n (Sustainable Use License, бесплатно для своих задач),
Temporal, PostgreSQL, Redis, Caddy (автоматический HTTPS).

## 1. Запуск

Нужно: Linux-сервер с Docker и Compose v2, **от 4 ГБ RAM**, два поддомена с A-записями на сервер,
открытые порты 80 и 443.

```bash
cd social-pipeline
cp .env.example .env
# заполнить домены и сгенерировать секреты: openssl rand -hex 32
docker compose up -d
docker compose ps        # postiz стартует 1-2 минуты
```

1. Откройте `https://<POSTIZ_DOMAIN>`, зарегистрируйте свой аккаунт.
2. В `.env` поставьте `POSTIZ_DISABLE_REGISTRATION=true` и выполните `docker compose up -d postiz`.
3. В Postiz: **Settings → Public API**, скопируйте ключ в `POSTIZ_API_KEY`, затем `docker compose up -d n8n`.
4. Откройте `https://<N8N_DOMAIN>`, создайте владельца, затем импортируйте workflow:
   `docker compose exec n8n n8n import:workflow --input=/workflows/publish-video.json`
   и включите его (Active) в интерфейсе.

### Попробовать локально (на маке, без доменов)

```bash
cp .env.example .env   # домены можно не трогать, секреты заполнить
docker compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

Postiz: http://localhost:4007, n8n: http://localhost:5678. Webhook: `http://localhost:5678/webhook/hitman-publish`.
Площадки с OAuth (YouTube, TikTok, Instagram) локально подключаются только если в их приложении
разрешён redirect на `http://localhost:4007`; Telegram работает и так.

## 2. Ключи площадок

Без своего «приложения разработчика» площадку подключить нельзя. Ключи кладутся в `.env`,
после чего нужно выполнить `docker compose up -d postiz` и подключить канал в интерфейсе Postiz (Add Channel).
Redirect URI для всех площадок: `https://<POSTIZ_DOMAIN>/integrations/social/<провайдер>`
(точное значение Postiz показывает при подключении, сверяйтесь с docs.postiz.com/providers).

| Площадка | Где взять ключи | Ограничения до проверки |
|---|---|---|
| YouTube | console.cloud.google.com: YouTube Data API v3, OAuth client (Web) | пока приложение не прошло проверку, видео загружаются приватными; квота ~6 загрузок в день |
| TikTok | developers.tiktok.com: Login Kit + Content Posting API | до аудита посты публикуются только как приватные (SELF_ONLY) |
| Instagram | developers.facebook.com: приложение типа Business; аккаунт Business/Creator | Reels через Graph API; для чужих аккаунтов нужен App Review |
| Telegram | @BotFather: создать бота, добавить его админом в канал | нет |
| VK, Threads и др. | см. docs.postiz.com/providers | |

> Имена переменных для YouTube, TikTok и Facebook взяты из официального compose Postiz.
> Для Instagram (без Facebook), Telegram, Threads и VK проверьте имена в docs.postiz.com
> перед заполнением: они могли измениться.

## 3. Публикация ролика

Узнайте ID подключённых каналов:

```bash
curl -s -H "Authorization: $POSTIZ_API_KEY" https://<POSTIZ_DOMAIN>/api/public/v1/integrations
```

Отправьте ролик (видео должно лежать по публичной ссылке, например на aidyn.stream):

```bash
curl -X POST https://<N8N_DOMAIN>/webhook/hitman-publish \
  -H "X-Pipeline-Token: $PIPELINE_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://aidyn.stream/media/k8s-01-vertical.mp4",
    "title": "Kubernetes за 60 секунд: что такое Pod",
    "caption_ru": "Pod — минимальная единица в Kubernetes… #devops #kubernetes",
    "caption_kz": "Pod — Kubernetes-тегі ең кіші бірлік… #devops",
    "publish_at": "2026-11-22T19:00:00+05:00",
    "channels": [
      {"id": "<id YouTube>",  "provider": "youtube"},
      {"id": "<id TikTok>",   "provider": "tiktok"},
      {"id": "<id Instagram>","provider": "instagram"},
      {"id": "<id Telegram>", "provider": "telegram"}
    ]
  }'
```

Без `publish_at` ролик уходит сразу. Вертикальные (9:16) ролики отправляйте в TikTok, Reels и Shorts,
горизонтальные (16:9) в YouTube и Telegram: это два разных запроса с разными `video_url` и `channels`.

Workflow (`n8n/publish-video.json`) делает так: проверяет токен, загружает видео в Postiz
(`/upload-from-url`), собирает пост с подписью RU + KZ и настройками каждой площадки
и создаёт его через `/posts`. Настройки площадок (`settings`) лежат в узле «Собрать пост»;
если Postiz ругается на поле, сверьте его с docs.postiz.com/public-api.

## 4. Подключение Claude

У Postiz есть MCP-сервер и CLI, а в n8n можно добавить узел **MCP Server Trigger**,
так что Claude сможет сам вызывать публикацию. Самый простой путь сейчас: Claude вызывает вебхук выше.

## Обслуживание

- Обновление: `docker compose pull && docker compose up -d`
- Бэкап: тома `postiz-postgres-data`, `n8n-postgres-data`, `postiz-uploads`, `n8n-data`
- Логи: `docker compose logs -f postiz n8n`
