import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from triage_bench import report_source_audit as audit


class ReportSourceTests(unittest.TestCase):
    def test_article_boundary_and_inline_spacing(self):
        raw = ('<h1>Report</h1><nav><p>Wrong navigation</p></nav>'
               '<div class="article-content"><p>The <strong>API</strong> recovered, '
               'but requests remained delayed. ' + 'Evidence. '*12 + '</p>'
               '<table><tr><td>13:43 UTC</td><td>Partial recovery</td></tr></table>'
               '<script>Invented cause</script></div><footer><p>Wrong footer</p></footer>').encode()
        text = '\n'.join(b['text'] for b in audit.extract(raw, 'Cloudflare')['blocks'])
        self.assertIn('The API recovered, but requests remained delayed.', text)
        self.assertIn('13:43 UTC Partial recovery', text)
        self.assertNotIn('Wrong', text)
        self.assertNotIn('Invented', text)

    def test_fail_closed_on_missing_or_ambiguous_container(self):
        for raw in (b'<p>Not an article</p>', b'<main></main><main></main>'):
            with self.assertRaises(ValueError):
                audit.extract(raw, 'AWS')

    def test_prefix_keeps_whole_blocks_and_does_not_skip(self):
        blocks = [{'text':'Recovered, except API.'}, {'text':'é'*20}, {'text':'Later.'}]
        prefix = audit.input_prefix(blocks, budget=30)
        self.assertEqual(prefix['text'], 'Recovered, except API.')
        self.assertEqual(prefix['included_blocks'], 1)
        self.assertEqual(prefix['omitted_blocks'], 2)
        with self.assertRaises(ValueError):
            audit.input_prefix(blocks, budget=2)

    def test_incident_cannot_cross_allocations(self):
        catalog = audit.load_catalog()
        changed = copy.deepcopy(catalog)
        changed['sources'][5]['allocation'] = 'evaluation'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'catalog.json'
            path.write_text(json.dumps(changed))
            with patch.object(audit, 'CATALOG', path), self.assertRaisesRegex(ValueError, 'crosses'):
                audit.load_catalog()

    def test_official_urls_only(self):
        catalog = audit.load_catalog()
        for url in ('http://blog.cloudflare.com/example', 'https://example.org/report',
                    'https://blog.cloudflare.com/example?answer=yes'):
            changed = copy.deepcopy(catalog)
            changed['sources'][0]['url'] = url
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/'catalog.json'
                path.write_text(json.dumps(changed))
                with patch.object(audit, 'CATALOG', path), self.assertRaises(ValueError):
                    audit.load_catalog()

    def test_audit_is_once_only_before_network_access(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)/'cache'
            cache.mkdir()
            with patch.object(audit, 'CACHE', cache), patch.object(audit, 'AUDIT', Path(directory)/'audit.json'), patch.object(audit.urllib.request, 'urlopen') as network:
                with self.assertRaisesRegex(ValueError, 'Preserve'):
                    audit.audit()
                network.assert_not_called()
