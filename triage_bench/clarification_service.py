"""Read-only inspection of original and instruction-focused clarification evidence."""
import copy,json
from . import clarification_trial as original,clarification_focus_trial as focused
from .clarification_features import decision,parser,compose
from .public_data import sha
from .hosted import encoded
from .public_sentence_features import validate_reply
from .public_rca_stages import committed

def snapshot(t):
    """Check this committed stage locally; full historical replay belongs to the CLI."""
    for path in (t.PLAN,t.protocol_path(),t.result_path()):committed(path)
    plan=t.load(t.PLAN);protocol=t.load(t.protocol_path());result=t.load(t.result_path());summary=t.load(t.output()/'summary.json')
    for name,digest in {**plan['source_sha256'],**plan['evidence_sha256']}.items():
        if sha((t.ROOT/name).read_bytes())!=digest:raise ValueError('Clarification dependency changed.')
    if protocol['plan_sha256']!=sha(t.PLAN.read_bytes()) or result['protocol_sha256']!=sha(t.protocol_path().read_bytes()) or summary['protocol_sha256']!=result['protocol_sha256'] or result['run_summary_sha256']!=sha((t.output()/'summary.json').read_bytes()):raise ValueError('Clarification stage identity changed.')
    for folder,files in ((t.data.DATA,protocol['data_sha256']),(t.output(),summary['files'])):
        for name,digest in files.items():
            if sha((folder/name).read_bytes())!=digest:raise ValueError('Clarification saved bytes changed.')
    packets={p['id']:p for p in t.load(t.data.DATA/'inputs.json')};jobs=t.load(t.output()/'requests.json');rows=[json.loads(line) for line in (t.output()/'responses.jsonl').read_text().splitlines()]
    if protocol['requests']!=[{k:v for k,v in j.items() if k!='body'} for j in jobs] or len(rows)!=len(jobs) or len(jobs)!=result['actual_calls'] or summary['status']!='completed':raise ValueError('Clarification denominator changed.')
    for row,job in zip(rows,jobs):
        body=t.request(packets[job['card_id']]) if t is original else t.request(packets[job['card_id']],job['arm'])
        if body!=job['body'] or sha(encoded(body))!=job['request_sha256'] or any(row.get(k)!=v for k,v in job.items() if k!='body'):raise ValueError('Clarification exact request changed.')
        normalized=validate_reply(row['raw_response'],body,plan['context_tokens'])
        if any(row.get(k)!=v for k,v in normalized.items()):raise ValueError('Clarification normalized reply changed.')
    refs={r['id']:r for r in t.load(t.data.DATA/'references.json')};index={(r['card_id'],r['round'],r.get('arm','jev')):r for r in rows}
    for o in result['outcomes']:
        labels=parser(packets[o['id']]);prediction={'labels':labels,'displayed':True,'minimum_score':None,**compose(labels)} if o['method']=='parser' else decision(index.get((o['id'],o['round'],o['method'])))
        if prediction!=o['prediction'] or any(o[k]!=v for k,v in original.assessment(prediction,refs[o['id']]).items()):raise ValueError('Clarification saved outcome changed.')
    return result


class ClarificationStudy:
    def __init__(self,root):self.root=root;self._cache={}
    def trial(self,phase):
        if phase not in ('original','focused'):raise ValueError('Unknown clarification stage.')
        return original if phase=='original' else focused
    def verified(self,phase='focused'):
        t=self.trial(phase)
        paths=[t.PLAN,t.protocol_path(),t.result_path(),*(self.root/n for n in t.SOURCES),*(self.root/n for n in t.load(t.PLAN)['evidence_sha256']),*t.data.DATA.rglob('*'),*t.output().rglob('*')]
        sig=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.is_file())
        if phase not in self._cache or self._cache[phase][0]!=sig:self._cache[phase]=(sig,snapshot(t))
        return self._cache[phase][1]
    def overview(self,phase='focused'):
        t=self.trial(phase)
        try:r=copy.deepcopy(self.verified(phase))
        except (OSError,ValueError,KeyError):return {'available':False,'error':'This stage needs its committed result and restored evidence.'}
        r.pop('outcomes');r['cards']=[{k:p[k] for k in ('id','dataset','family','variant','text')} for p in t.load(t.data.DATA/'inputs.json')]
        return {'available':True,'phase':phase,'candidate':'jev' if phase=='original' else 'focused','methods':['jev'] if phase=='original' else ['focused','control'],**r}
    def card(self,identifier,reveal=False,phase='focused'):
        t=self.trial(phase);result=self.verified(phase)
        try:p=next(p for p in t.load(t.data.DATA/'inputs.json') if p['id']==identifier)
        except StopIteration as e:raise ValueError('Unknown clarification statement.') from e
        raw=[r for r in map(json.loads,(t.output()/'responses.jsonl').read_text().splitlines()) if r['card_id']==identifier]
        methods=['jev'] if phase=='original' else ['focused','control'];plabels=parser(p)
        return {**p,'phase':phase,'responses':raw,'decisions':{m:{str(n):decision(next((r for r in raw if r['round']==n and (phase=='original' or r['arm']==m)),None)) for n in (1,2,3)} for m in methods},'parser':{'labels':plabels,**compose(plabels)},'jobs':[j for j in t.load(t.output()/'requests.json') if j['card_id']==identifier],
          'reference':next(r for r in t.load(t.data.DATA/'references.json') if r['id']==identifier) if reveal else None,
          'outcomes':[o for o in result['outcomes'] if o['id']==identifier] if reveal else None,
          'provider_calls':0,'server_writes':0,'human_review_recorded':False}
