#!/usr/bin/env python3
"""Контент-завод Hitman: готовый ролик -> очередь публикаций (n8n -> Postiz -> соцсети).

  python3 content-factory/publish.py multik/out/pod.mp4 --title "Что такое Pod" \
      --caption-file multik/films/pod/description.txt --caption-kk-file multik/films/pod/description.kk.txt
  --dry-run   показать, что уйдёт, ничего не копируя и не отправляя
  --now       опубликовать сразу, без слота расписания
  --format    9x16 | 16x9 (по умолчанию определяется через ffprobe)

Что делает:
  1. копирует MP4 в social-pipeline/media/ (его раздаёт сервис media из docker-compose);
  2. берёт каналы для формата из content-factory/channels.json;
  3. занимает ближайший свободный слот из content-factory/schedule.json (учёт в state.json);
  4. шлёт POST в вебхук n8n hitman-publish.

Настройки (переменные окружения или social-pipeline/.env):
  FACTORY_N8N_URL   адрес n8n, по умолчанию http://localhost:5678
  MEDIA_BASE_URL    откуда Postiz скачает ролик, по умолчанию http://media (имя сервиса в docker-сети)
  PIPELINE_WEBHOOK_TOKEN  токен вебхука
Только стандартная библиотека Python 3.9+.
"""
import argparse, datetime as dt, json, os, re, shutil, subprocess, sys, urllib.error, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
FACTORY = ROOT / 'content-factory'
PIPELINE = ROOT / 'social-pipeline'
MEDIA_DIR = PIPELINE / 'media'
STATE = FACTORY / 'state.json'


def die(msg):
    print(f'ошибка: {msg}', file=sys.stderr)
    sys.exit(1)


def load_env():
    env = {}
    f = PIPELINE / '.env'
    if f.exists():
        for line in f.read_text(encoding='utf-8').splitlines():
            m = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$', line)
            if m and not line.lstrip().startswith('#'):
                env[m.group(1)] = m.group(2).strip().strip('"\'')
    env.update({k: v for k, v in os.environ.items() if k in (
        'FACTORY_N8N_URL', 'MEDIA_BASE_URL', 'PIPELINE_WEBHOOK_TOKEN')})
    return env


def read_json(path, default=None):
    if not path.exists():
        if default is not None:
            return default
        die(f'нет файла {path.relative_to(ROOT)} (скопируйте из {path.name.replace(".json", ".example.json")})')
    return json.loads(path.read_text(encoding='utf-8'))


def detect_format(video):
    if not shutil.which('ffprobe'):
        die('нет ffprobe: установите ffmpeg или укажите --format 9x16|16x9')
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height', '-of', 'json', str(video)],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)['streams'][0]
    return '9x16' if s['height'] > s['width'] else '16x9'


def slugify(text):
    text = re.sub(r'[^\w-]+', '-', text.lower(), flags=re.UNICODE).strip('-')
    return text[:60] or 'video'


def next_slot(schedule, fmt, booked, now):
    """Ближайший свободный слот: schedule = {"timezone": "...", "slots": {"9x16": ["19:00"], ...}, "days": [0..6]}."""
    tz = ZoneInfo(schedule.get('timezone', 'Asia/Almaty'))
    times = schedule.get('slots', {}).get(fmt) or schedule.get('slots', {}).get('default') or ['19:00']
    days = set(schedule.get('days', range(7)))
    min_gap = dt.timedelta(minutes=schedule.get('min_lead_minutes', 30))
    local_now = now.astimezone(tz)
    taken = set(booked)
    for d in range(0, 60):
        day = (local_now + dt.timedelta(days=d)).date()
        if day.weekday() not in days:
            continue
        for t in sorted(times):
            hh, mm = map(int, t.split(':'))
            slot = dt.datetime(day.year, day.month, day.day, hh, mm, tzinfo=tz)
            key = f'{fmt}@{slot.isoformat()}'
            if slot - local_now >= min_gap and key not in taken:
                return slot, key
    die('нет свободных слотов на 60 дней вперёд, проверьте schedule.json')


def build_payload(args, fmt, video_url, channels, publish_at):
    cap_ru = Path(args.caption_file).read_text(encoding='utf-8').strip() if args.caption_file else (args.caption or '')
    cap_kk = Path(args.caption_kk_file).read_text(encoding='utf-8').strip() if args.caption_kk_file else ''
    if not cap_ru and not cap_kk:
        die('нужна подпись: --caption-file, --caption или --caption-kk-file')
    return {
        'video_url': video_url,
        'title': args.title or cap_ru.split('\n')[0][:100],
        'caption_ru': cap_ru,
        'caption_kz': cap_kk,
        'publish_at': publish_at.isoformat() if publish_at else None,
        'channels': channels,
        'format': fmt,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video')
    ap.add_argument('--title')
    ap.add_argument('--caption')
    ap.add_argument('--caption-file')
    ap.add_argument('--caption-kk-file')
    ap.add_argument('--format', choices=['9x16', '16x9'])
    ap.add_argument('--now', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.is_file():
        die(f'нет файла {args.video}')
    env = load_env()
    fmt = args.format or detect_format(video)

    channels_cfg = read_json(FACTORY / 'channels.json')
    channels = [c for c in channels_cfg.get(fmt, []) if c.get('id') and not c['id'].startswith('<')]
    if not channels:
        die(f'в content-factory/channels.json нет каналов для формата {fmt}; id берутся из GET /api/public/v1/integrations в Postiz')

    state = read_json(STATE, default={'booked': [], 'published': []})
    publish_at, slot_key = (None, None) if args.now else next_slot(
        read_json(FACTORY / 'schedule.json'), fmt, state['booked'], dt.datetime.now(dt.timezone.utc))

    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    media_name = f'{stamp}-{slugify(video.stem)}.mp4'
    base = env.get('MEDIA_BASE_URL', 'http://media').rstrip('/')
    payload = build_payload(args, fmt, f'{base}/{media_name}', channels, publish_at)

    when = publish_at.strftime('%d.%m %H:%M (%Z)') if publish_at else 'сразу'
    print(f'формат {fmt}, публикация: {when}, каналы: {", ".join(c["provider"] for c in channels)}')
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    token = env.get('PIPELINE_WEBHOOK_TOKEN')
    if not token:
        die('нет PIPELINE_WEBHOOK_TOKEN в social-pipeline/.env')
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, MEDIA_DIR / media_name)

    url = env.get('FACTORY_N8N_URL', 'http://localhost:5678').rstrip('/') + '/webhook/hitman-publish'
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method='POST',
                                 headers={'Content-Type': 'application/json', 'X-Pipeline-Token': token})
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            res = json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        die(f'n8n ответил HTTP {e.code}: {e.read()[:500].decode("utf-8", "replace")}')
    except urllib.error.URLError as e:
        die(f'n8n недоступен по {url}: {e.reason}')

    if slot_key:
        state['booked'].append(slot_key)
    state['published'].append({'file': media_name, 'format': fmt, 'title': payload['title'],
                               'publish_at': payload['publish_at'], 'queued_at': dt.datetime.now().isoformat()})
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    print('в очереди:', json.dumps(res, ensure_ascii=False)[:500])


if __name__ == '__main__':
    main()
