import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from triage_bench import cross_report_audit as a

class CrossAuditTests(unittest.TestCase):
 def test_full_prose_table_and_code_remain_without_nested_duplicates(self):
  raw=b'<h1>Title</h1><div class="article-content"><p>Whole paragraph '+b'x'*120+b'</p><ul><li>List item</li></ul><pre><code>route add PREFIX</code></pre><table><tr><td>Cell one</td><td>Cell two</td></tr></table><aside><p>Excluded navigation</p></aside><p>Final paragraph</p></div>'
  article=a.extract(raw);self.assertEqual([b['tag'] for b in article['blocks']],['p','li','pre','tr','p'])
  self.assertIn('route add PREFIX',a.text(article));self.assertIn('Cell one',a.text(article));self.assertNotIn('Excluded navigation',a.text(article))
 def test_ambiguous_container_stops_preparation(self):
  with self.assertRaises(ValueError):a.extract(b'<h1>Title</h1><div class="article-content">a</div><div class="article-content">b</div>')
 def test_http_failure_is_once_only_and_retains_source(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);plan=root/'plan.json';plan.write_text(json.dumps({'sources':[{'id':'one','url':'https://blog.cloudflare.com/report'}]}))
   with patch.object(a,'PLAN',plan),patch.object(a,'AUDIT',root/'audit.json'),patch.object(a,'CACHE',root/'cache'),patch.object(a,'committed'),patch('urllib.request.urlopen',side_effect=HTTPError('https://blog.cloudflare.com/report',404,'missing',{},None)) as fetch:
    r=a.audit();self.assertEqual(fetch.call_count,1);self.assertFalse(r['preparation_eligible']);self.assertEqual(r['sources'][0]['reason'],'source_http_404')
    self.assertEqual(r['new_provider_calls'],0)
    with self.assertRaises(ValueError):a.audit()
