"""Read-only reconstruction and original replies for the completed value test."""
import json
from . import ambiguity_value_trial as t
from .public_rca_stages import load
from .paths import ROOT

class AmbiguityValueStudy:
    def __init__(self):self.cache=None
    def verified(self):
        paths=[t.PLAN,t.protocol_path(),t.result_path(),*(t.data.DATA/n for n in ('inputs.json','references.json','manifest.json')),*(t.output()/n for n in ('requests.json','responses.jsonl','summary.json')),*(ROOT/n for n in t.SOURCES),*(ROOT/n for n in load(t.PLAN)['evidence_sha256'])]
        stamp=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths)
        if self.cache is None or self.cache[0]!=stamp:
            r=t.verify();ps=load(t.data.DATA/'inputs.json');rs=load(t.data.DATA/'references.json');rows=[json.loads(s) for s in (t.output()/'responses.jsonl').read_text().splitlines()];jobs=load(t.output()/'requests.json')
            self.cache=(stamp,r,ps,rs,rows,jobs)
        return self.cache[1:]
    def overview(self):
        r,ps,*_=self.verified()
        totals={}
        for method in ('jev','rules'):
            os=[o for o in r['outcomes'] if o['method']==method]
            totals[method]={k:sum(int(o[k]) for o in os) for k in ('correct_display','canonical_question','unnecessary_question','missed_clarification','silent_miss','withheld')}
            totals[method].update(opportunities=len(os),needed_questions=sum(bool(o['needed']) for o in os))
        return {'available':True,'candidate_passes':r['candidate_passes'],'actual_calls':r['actual_calls'],'valid_answers':r['valid_answers'],'input_tokens':r['input_tokens'],'summed_latency_ms':r['summed_latency_ms'],'totals':totals,'panels':r['panels'],'paired':r['paired'],'cards':[{k:p[k] for k in ('id','dataset','family','pair','variant','category','text')} for p in ps],'new_recordings':0,'human_reviews':0,'independent_reviews':0,'provider_calls_on_page':0}
    def card(self,identifier,reveal=False):
        r,ps,refs,rows,jobs=self.verified();p=next((p for p in ps if p['id']==identifier),None)
        if p is None:raise ValueError('Unknown fresh statement.')
        result={'packet':p,'reference':next(x for x in refs if x['id']==identifier) if reveal else None,'rounds':[]}
        for n in (1,2,3):
            row=next((x for x in rows if x['card_id']==identifier and x['round']==n),None);job=next(x for x in jobs if x['card_id']==identifier and x['round']==n)
            predictions={m:next(o['prediction'] for o in r['outcomes'] if o['id']==identifier and o['round']==n and o['method']==m) for m in ('jev','rules')}
            result['rounds'].append({'round':n,'predictions':predictions,'row':row,'request':job['body'],'request_sha256':job['request_sha256'],'outcomes':{m:next(o for o in r['outcomes'] if o['id']==identifier and o['round']==n and o['method']==m) for m in ('jev','rules')} if reveal else None})
        return result
