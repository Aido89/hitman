# Контент-завод Hitman

Конвейер от темы до публикации, всё на своём железе:

```
тема (topics.md / Piratex)
  └─▶ «Мультик» в Claude Code: сценарий → голос → ролик (Remotion) → проверка в Telegram
        └─▶ publish.py: ролик в social-pipeline/media + слот расписания
              └─▶ n8n (вебхук hitman-publish) ─▶ Postiz ─▶ YouTube / TikTok / Instagram / Telegram
```

| Цех | Где |
|---|---|
| Сценарий и сборка ролика | скилл `.claude/skills/multik` (основа: artemiimillier/skill-multik, MIT) |
| Очередь и расписание | `content-factory/publish.py`, `schedule.json`, `channels.json` |
| Раздача файлов | сервис `media` в `social-pipeline/docker-compose.yml` |
| Публикация | n8n + Postiz, см. `social-pipeline/README.md` |

## Как пользоваться

1. Поднять `social-pipeline` (локально или на сервере), подключить каналы в Postiz,
   получить API-ключ и id каналов.
2. `cp content-factory/channels.example.json content-factory/channels.json` и вписать id.
3. Открыть Claude Code в корне репозитория и написать **«Мультик»** (или «Мультик про Ingress»).
   Первый запуск проведёт по настройке: стиль, герой, голос, окружение (Node, ffmpeg, `npm i`).
4. Claude покажет сценарий, соберёт ролик, пришлёт на проверку. После вашего «публикуй» он вызовет:

```bash
python3 content-factory/publish.py multik/out/<slug>.mp4 --title "..." \
  --caption-file multik/films/<slug>/description.txt \
  --caption-kk-file multik/films/<slug>/description.kk.txt
```

Ролик займёт ближайший свободный слот (`schedule.json`: по умолчанию 12:30 и 19:00 для 9:16,
20:00 для 16:9, время Алматы) и уйдёт в Postiz. Посмотреть очередь можно в календаре Postiz,
а локальный учёт лежит в `content-factory/state.json`.

Флаги: `--dry-run` (показать без отправки), `--now` (сразу), `--format 9x16|16x9`.

## Локально или на сервере

- **Локально (мак):** `MEDIA_BASE_URL` по умолчанию `http://media`, Postiz скачивает ролик внутри docker-сети.
  YouTube, TikTok и Telegram работают. Instagram требует, чтобы видео было доступно из интернета,
  поэтому для него нужен сервер.
- **Сервер:** задайте `MEDIA_DOMAIN` в `social-pipeline/.env`, Caddy выдаст ролики по
  `https://<MEDIA_DOMAIN>/`, и поставьте `MEDIA_BASE_URL=https://<MEDIA_DOMAIN>`.
  Рендер можно оставить на маке: `FACTORY_N8N_URL=https://<N8N_DOMAIN>`, но тогда ролик надо
  положить на сервер (rsync в `social-pipeline/media/`). Проще всего держать весь завод на одном сервере.
