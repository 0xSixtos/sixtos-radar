"""Public feed monitor. No paid APIs or external dependencies."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

FEEDS = {
    'Hugging Face · IA': 'https://huggingface.co/blog/feed.xml',
    'Ethereum · Web3': 'https://blog.ethereum.org/feed.xml',
    'ElizaOS · IA/Web3': 'https://github.com/elizaOS/eliza/releases.atom',
    'Coinbase AgentKit · agentes y wallets': 'https://github.com/coinbase/agentkit/releases.atom',
}
NS = {'a': 'http://www.w3.org/2005/Atom'}
STATE = Path('state.json')
UTC = timezone.utc

def date(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        result = parsedate_to_datetime(value)
    if result.tzinfo is None:
        raise ValueError('Fecha sin zona horaria')
    return result.astimezone(UTC)

def parse(data, source):
    root = ET.fromstring(data)
    atom = root.tag.endswith('}feed')
    entries = root.findall('a:entry', NS) if atom else root.findall('./channel/item')
    result = []
    for item in entries:
        if atom:
            title = item.findtext('a:title', namespaces=NS)
            url = next((n.get('href') for n in item.findall('a:link', NS)
                        if n.get('rel', 'alternate') == 'alternate'), None)
            stamp = item.findtext('a:published', namespaces=NS) or item.findtext('a:updated', namespaces=NS)
        else:
            title, url, stamp = (item.findtext(n) for n in ('title', 'link', 'pubDate'))
        if not title or not url or not stamp or not url.startswith('https://'):
            continue
        try:
            published = date(stamp).isoformat()
        except (ValueError, TypeError, OverflowError):
            continue
        title = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', title))).strip()
        parts = urllib.parse.urlsplit(url)
        url = urllib.parse.urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), '', ''))
        result.append(dict(id=hashlib.sha256(url.encode()).hexdigest(), title=title,
                           url=url, source=source, published=published))
    return result

def fetch(pair):
    source, url = pair
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'SixtosRadar/1.0'})
        with urllib.request.urlopen(request, timeout=18) as response:
            body = response.read(3_000_001)
        if len(body) > 3_000_000:
            raise ValueError('Feed demasiado grande')
        return parse(body, source), None
    except Exception as error:
        print(f'Fuente no disponible: {source} ({type(error).__name__})', file=sys.stderr)
        return [], source

def save(state):
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    temp.replace(STATE)

def send(message):
    target = urllib.parse.urlsplit(os.environ.get('DISCORD_WEBHOOK_URL', ''))
    if target.scheme != 'https' or target.hostname != 'discord.com' or not target.path.startswith('/api/webhooks/'):
        raise ValueError('Configura DISCORD_WEBHOOK_URL con el webhook oficial del canal')
    url = urllib.parse.urlunsplit((target.scheme, target.netloc, target.path, 'wait=true', ''))
    body = json.dumps({'content': message[:1900], 'allowed_mentions': {'parse': []}, 'flags': 4}).encode()
    request = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json', 'User-Agent': 'SixtosRadar/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise RuntimeError('Discord no confirmó el envío')
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'Discord devolvió HTTP {error.code}; mensaje pendiente') from None
    except urllib.error.URLError:
        raise RuntimeError('No se pudo conectar con Discord; mensaje pendiente') from None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    now = datetime.now(UTC)
    local = now.astimezone(ZoneInfo('America/Mexico_City'))
    today = local.date().isoformat()
    state = json.loads(STATE.read_text()) if STATE.exists() else {'seen': {}, 'daily': {}, 'digest': ''}
    items, failed = {}, []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for entries, error in pool.map(fetch, FEEDS.items()):
            items.update({item['id']: item for item in entries})
            if error:
                failed.append(error)
    if len(failed) == len(FEEDS):
        raise RuntimeError('Ninguna fuente respondió; no se enviará un resumen vacío')
    recent = sorted((item for item in items.values()
                     if now - timedelta(hours=24) <= date(item['published']) <= now),
                    key=lambda item: item['published'], reverse=True)
    if args.dry_run:
        print(json.dumps({'sources_ok': len(FEEDS)-len(failed), 'failed': failed, 'recent': recent}, ensure_ascii=False, indent=2))
        return
    if not os.environ.get('DISCORD_WEBHOOK_URL'):
        raise ValueError('Falta el secreto DISCORD_WEBHOOK_URL; no se ha enviado nada')
    sent = state['daily'].get(today, 0)
    for item in recent:
        if item['id'] in state['seen'] or sent >= 3:
            continue
        title = item['title'].replace('@', '＠').replace('`', '')[:400]
        send(f"🔎 **Novedad: {item['source']}**\n{title}\n"
             f"**Fecha original:** {item['published']}\n**Fuente:** <{item['url']}>\n"
             '**Cobertura en X:** no medida.\n'
             '**Idea para contenido:** explica qué cambia, para quién sirve y si ya está disponible.\n'
             '**Estado editorial:** titular original; lee la fuente antes de redactar un tuit.')
        state['seen'][item['id']] = now.isoformat()
        sent += 1
        state['daily'][today] = sent
        save(state)
    if local.hour >= 9 and state.get('digest') != today:
        lines = [f'🗞️ **Radar IA + Web3 · {today}**', 'Novedades de las últimas 24 horas:']
        if not recent:
            lines.append('No se encontraron anuncios recientes en las fuentes disponibles.')
        for item in recent[:5]:
            lines.append(f"• {item['source']}: {item['title'][:130]}\n<{item['url']}>")
        if failed:
            lines.append('Cobertura parcial: no respondieron ' + ', '.join(failed))
        lines.append('Titulares originales. No mide tendencias ni genera resúmenes con IA.')
        send('\n'.join(lines))
        state['digest'] = today
        save(state)
    cutoff = now - timedelta(days=7)
    state['seen'] = {k: v for k, v in state['seen'].items() if date(v) >= cutoff}
    state['daily'] = {k: v for k, v in state['daily'].items() if k >= cutoff.date().isoformat()}
    save(state)
    print(f'Fuentes: {len(FEEDS)-len(failed)}/{len(FEEDS)}; novedades: {len(recent)}; avisos hoy: {sent}')

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Radar detenido: {error}', file=sys.stderr)
        sys.exit(1)
