import unittest
from unittest.mock import patch
import radar

class RadarTests(unittest.TestCase):
    def test_rss_canonical_link_and_date(self):
        entries = radar.parse(b'''<rss><channel><item><title>A &amp; B</title>
        <link>https://EXAMPLE.org/news/?utm_source=test</link>
        <pubDate>Tue, 20 Oct 2026 12:00:00 GMT</pubDate></item>
        <item><title>Sin fecha</title><link>https://example.org/missing</link></item>
        </channel></rss>''', 'RSS')
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['title'], 'A & B')
        self.assertEqual(entries[0]['url'], 'https://example.org/news')
        self.assertEqual(entries[0]['published'], '2026-10-20T12:00:00+00:00')

    def test_atom_uses_original_publication_not_update(self):
        entries = radar.parse(b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <title>Release</title><link rel="self" href="https://example.org/api"/>
        <link rel="alternate" href="https://example.org/release"/>
        <published>2026-10-19T10:00:00Z</published><updated>2026-10-20T10:00:00Z</updated>
        </entry></feed>''', 'Atom')
        self.assertEqual(entries[0]['url'], 'https://example.org/release')
        self.assertEqual(entries[0]['published'], '2026-10-19T10:00:00+00:00')

    def test_rejects_non_discord_destinations(self):
        with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'https://example.org/api/webhooks/secret'}):
            with self.assertRaisesRegex(ValueError, 'webhook oficial'):
                radar.send('test')

    def test_no_accidental_mentions_and_confirmed_delivery(self):
        from unittest.mock import MagicMock
        import json
        response = MagicMock()
        response.__enter__.return_value.status = 200
        with patch.dict('os.environ', {'DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/id/test'}):
            with patch('urllib.request.urlopen', return_value=response) as request:
                radar.send('test @everyone')
                body = json.loads(request.call_args.args[0].data)
                self.assertEqual(body['allowed_mentions'], {'parse': []})
                self.assertTrue(request.call_args.args[0].full_url.endswith('?wait=true'))

class ConfigurationTests(unittest.TestCase):
    def test_fork_resets_inherited_state(self):
        original = {'instance': 'alice/radar', 'seen': {'old': 'stamp'}, 'daily': {'date': 3}, 'digest': 'date'}
        fork = radar.instance_state(original, 'bob/radar')
        self.assertEqual(fork['instance'], 'bob/radar')
        self.assertEqual(fork['seen'], {})
        self.assertEqual(fork['daily'], {})
        self.assertEqual(fork['digest'], '')
        self.assertIs(radar.instance_state(original, 'alice/radar'), original)

    def test_keyword_filters(self):
        config = {'include_keywords': ['wallet', 'agent'], 'exclude_keywords': ['giveaway']}
        self.assertTrue(radar.matches({'title': 'New AGENT wallet'}, config))
        self.assertFalse(radar.matches({'title': 'Agent giveaway'}, config))
        self.assertFalse(radar.matches({'title': 'Other topic'}, config))

    def test_custom_timezone_and_invalid_config(self):
        import json
        import tempfile
        from pathlib import Path
        config = radar.load_config()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'config.json'
            config.update(timezone='Europe/Madrid', digest_time='08:30')
            target.write_text(json.dumps(config))
            self.assertEqual(radar.load_config(target)['digest_time'], '08:30')
            config['digest_time'] = '25:00'
            target.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, 'HH:MM'):
                radar.load_config(target)
            config['digest_time'] = '08:30'
            config['feeds'] = {'private': 'https://user:password@example.org/feed'}
            target.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, 'sin credenciales'):
                radar.load_config(target)

    def test_timezone_switches_dates_across_midnight(self):
        from datetime import datetime, timezone
        from zoneinfo import ZoneInfo
        moment = datetime(2026, 10, 20, 1, 0, tzinfo=timezone.utc)
        self.assertEqual(moment.astimezone(ZoneInfo('America/Mexico_City')).date().isoformat(), '2026-10-19')
        self.assertEqual(moment.astimezone(ZoneInfo('Europe/Madrid')).date().isoformat(), '2026-10-20')

if __name__ == '__main__':
    unittest.main()
