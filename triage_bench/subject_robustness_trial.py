"""Controlled subject-context challenges; no numerical or cause judgments."""
import copy
import json
import time
import urllib.error
import urllib.request
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import load,committed
from .hosted import encoded,redact
from .runner import NoRedirect,clean_api_key
from .profile import MODEL,profile_check
from .public_sentence_features import validate_reply,GlobalReplyError
from .excerpt_subject_trial import SOURCES as OLD_SOURCES,excerpt_context,note_prefix,check_reviews

PLAN=ROOT/'checkpoints/subject-robustness-plan-2026-10-06.json'
PROTOCOL=ROOT/'checkpoints/subject-robustness-protocol-2026-10-06.json'
RESULT=ROOT/'checkpoints/subject-robustness-results-2026-10-06.json'
CARDS=ROOT/'checkpoints/subject-robustness-cards-2026-10-06.json'
REFERENCES=ROOT/'checkpoints/subject-robustness-references-2026-10-06.json'
OUT=ROOT/'runs/subject-robustness/hosted-2026-10-06-v1'
ARMS=('full','prefix','excerpt')
SOURCES=OLD_SOURCES+('triage_bench/subject_robustness_trial.py','scripts/run_subject_robustness.py')
INSTRUCTIONS='Identify the subject of the EXACT sentence in the full note context. Select the observed service that the note uniquely identifies as the subject of this endorsed assertion. Resolve a pronoun only from an unambiguous antecedent in the note; a request to check a service can introduce that service as an antecedent. Select unresolved when the subject is not unique, is outside the observed inventory, or the sentence is not one endorsed assertion. Use only the note, not service health or incident causality. Exact sentence: '


def templates(a,b):
    return [
      ('explicit_name',[f'{a} has rising errors.'],0,a,{},'The target explicitly names one observed service.'),
      ('local_pronoun',[f'{a} has rising errors.','This service has enough recorded spans.'],1,a,{},'The preceding explicit assertion supplies the subject.'),
      ('request_anchor',[f'Investigate {b} next.','This service has enough recorded spans.'],1,b,{},'A direct request introduces its unique service under the fixed task definition.'),
      ('negated_anchor',[f'{a} does not show rising errors.','This service is healthy.'],1,a,{},'Negation changes the claim, not its named subject.'),
      ('explicit_switch',[f'{a} has rising errors.',f'{b} has rising latency.','This service has enough recorded spans.'],2,b,{},'The latest endorsed service assertion supplies the subject.'),
      ('quoted_interruption',[f'My current assessment concerns {a}.',f'The archived note says: "{b} is unhealthy."','The service in my current assessment is healthy.'],2,a,{'excerpt':'unresolved'},'The current assessment explicitly names the first service; the quotation does not replace it. The excerpt removes that current-assessment anchor.'),
      ('request_interruption',[f'My current assessment concerns {a}.',f'Please check {b} later.','The service in my current assessment is healthy.'],2,a,{'excerpt':'unresolved'},'The qualified current-assessment subject differs from a later requested check. The excerpt lacks that qualification anchor.'),
      ('question_interruption',[f'My current assessment concerns {a}.',f'Is {b} healthy?','The service in my current assessment has enough recorded spans.'],2,a,{'excerpt':'unresolved'},'The question does not name the explicitly qualified current-assessment service; truncation removes it.'),
      ('ambiguous_pair',[f'Either {a} or {b} is unhealthy.','This service is healthy.'],1,'unresolved',{},'The text does not select one of its two candidates.'),
      ('missing_anchor',['An incident is under investigation.','This service is healthy.'],1,'unresolved',{},'No service is identified.'),
      ('later_clarification',['This service is healthy.',f'The subject of the preceding assertion is {a}.'],0,a,{'prefix':'unresolved','excerpt':'unresolved'},'Only the full note contains the explicit later clarification.'),
      ('outside_inventory',['external-node is under review.','This service is healthy.'],1,'unresolved',{},'The named subject is outside the complete observed inventory.'),
      ('quoted_target',[f'{a} is under review.',f'The archived note says: "{b} is healthy."'],1,'unresolved',{},'The selected sentence attributes a quotation rather than endorsing that service-health assertion.'),
      ('compound_target',[f'{a} has errors and {b} is healthy.'],0,'unresolved',{},'The selected sentence contains two service assertions, outside the single endorsed assertion task.'),
      ('later_distractor',[f'{a} has rising errors.','This service is healthy.',f'A separate later check concerns {b}.'],1,a,{},'The later separate check does not change the earlier pronoun subject.')]


def prepare():
    packets,_=check_reviews();cards=[];refs={}
    for i,p in enumerate(p for p in packets if p['wording']=='plain'):
        assert 'external-node' not in p['services']
        for j in range(15):
            pair=(p['services'][0],p['services'][-1]);a,b=pair if (i+j)%2==0 else pair[::-1]
            family,lines,target,subject,overrides,reason=templates(a,b)[j]
            note='\n'.join(lines);identifier='RSC-'+sha(encoded({'source':p['id'],'family':family,'note':note}))[:12]
            card={'id':identifier,'source_note':p['id'],'dataset':p['dataset'],'family':family,'note':note,'services':p['services'],
                  'candidates':[{'id':'s'+str(k+1).zfill(2),'text':text} for k,text in enumerate(lines)],'sentence':'s'+str(target+1).zfill(2)}
            refs[identifier]={'source_subject':subject,'visible_subjects':{arm:overrides.get(arm,subject) for arm in ARMS},'reason':reason}
            cards.append(card)
    if len(cards)!=135 or len(refs)!=135:raise ValueError('Challenge count changed.')
    for path,value in ((CARDS,cards),(REFERENCES,refs)):
        with path.open('x') as f:f.write(json.dumps(value,indent=2)+'\n')
    return {'cards':len(cards),'families':15,'source_recordings':9,'human_reviews':0,'independent_reviews':0}


def context(p,arm):
    if arm=='full':return p['note']
    if arm=='prefix':return note_prefix(p,p['sentence'])
    if arm=='excerpt':return excerpt_context(p,p['sentence'])['note']
    raise ValueError('Unknown robustness context.')


def body(p,arm):
    sentence=next(c['text'] for c in p['candidates'] if c['id']==p['sentence'])
    criteria={s:'The unique assertion subject in the note is '+s+'.' for s in p['services']}
    criteria['unresolved']='The note does not identify one endorsed assertion with a unique observed service.'
    return {'model':MODEL,'state':json.dumps({'note':context(p,arm),'observed_services':p['services']},separators=(',',':')),
            'questions':{p['sentence']+'_subject':{'type':'choice','instructions':INSTRUCTIONS+sentence,'criteria':criteria}}}


def plan(profile):
    profile_check(profile);old=load(ROOT/'checkpoints/excerpt-subject-plan-2026-10-06.json')
    if any(profile[k]!=old[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Keep the recorded profile.')
    cards=load(CARDS);refs=load(REFERENCES)
    if len(cards)!=135 or set(refs)!={c['id'] for c in cards}:raise ValueError('Controlled challenge allocation changed.')
    record={'schema':'subject-robustness-plan-1','model':MODEL,'endpoint':profile['endpoint'],'context_tokens':profile['context_tokens'],
      'authorization':'User authorized staged context, robustness and complete-workflow research and continuation until blocked on 2026-10-06.',
      'candidate':'excerpt','arms':list(ARMS),'cards':135,'families':15,'source_recordings':9,'rounds':3,'maximum_calls':1215,'maximum_answers':1215,'maximum_request_bytes':79840,
      'input_policy':'Constructed text on observed service inventories from nine inspected recordings. No measurements, cause labels, proposals, reference services or family tags enter wire bodies. Identical one-subject question and complete options in all arms; only note context differs. Full includes the whole note, prefix ends at the target, excerpt applies the frozen complete-name rule. All calls unconditional, rotated by card, arm and round; no retries or answer repair.',
      'reference_policy':'Assistant-authored source-subject and context-visible-subject references are separate and frozen before calls. The qualified current-assessment subject is not replaced by a quotation, later requested check or question. Direct requests can introduce ordinary unqualified pronouns. Quoted targets, compound targets, outside-inventory subjects and genuine ambiguity are unresolved under the fixed single-assertion question. Later clarification supplies a full-note subject, but is unavailable to prefix/excerpt; removing current-assessment anchors likewise makes excerpt subjects unresolved. Never reward lucky unsupported guesses as context-correct.',
      'metrics':'For every application/family/round retain full denominators, context-visible correctness, original-source correctness, unresolved precision, probability>=0.70 eligibility, confident unsupported/wrong resolutions, known-source coverage, input-visible-known coverage, losses/gains versus fresh full and prefix controls, quarantine, actual cost and all raw replies. This is a subject-only challenge; eligibility is not a numerical verdict or analyst recommendation.',
      'gate':'For every application/family/round require complete calls and all context-visible subjects correct, zero eligible unsupported/wrong resolutions, >=90% eligible correct resolution on context-visible unique subjects when any exist, and no eligible correct original-source resolution loss versus the contemporary full-note comparator. An information-removal loss can fail this gate even when unresolved is correct for the reduced input. Only excerpt is the candidate; no operational, independent-review or protected-data promotion.',
      'limits':'The same assistant wrote the notes and policy references; zero human/independent reviews. These constructed challenges are not authentic reports or new recordings. Family repetitions and repeated calls are correlated. No numerical truth, cause accuracy, anomaly detection or telecom reliability inference.',
      'sources':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (CARDS,REFERENCES)}}
    with PLAN.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'status':'planned','maximum_calls':1215,'maximum_answers':1215}


def check_plan():
    committed(PLAN);p=load(PLAN)
    if p['schema']!='subject-robustness-plan-1' or p['maximum_calls']!=1215 or p['maximum_answers']!=1215 or p['arms']!=list(ARMS):raise ValueError('Robustness task/budget changed.')
    for n,digest in {**p['sources'],**p['evidence']}.items():
        if sha((ROOT/n).read_bytes())!=digest:raise ValueError('Robustness source/evidence changed: '+n)
    return p


def requests():
    check_plan();cards=load(CARDS);jobs=[]
    for n in (1,2,3):
        shift=n-1
        for i,p in enumerate(cards[shift:]+cards[:shift]):
            start=(i+shift)%3
            for arm in ARMS[start:]+ARMS[:start]:
                request=body(p,arm)
                jobs.append({'id':p['id']+'::subject-robustness::'+arm+'::r'+str(n),'card_id':p['id'],'arm':arm,'phase':'text','sentence':p['sentence'],'round':n,'request_sha256':sha(encoded(request)),'body':request})
    return jobs


def expected_protocol():
    jobs=requests()
    return {'schema':'subject-robustness-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'references_sha256':sha(REFERENCES.read_bytes()),
      'references':load(REFERENCES),'planned_calls':len(jobs),'planned_answers':len(jobs),'largest_request_bytes':max(len(encoded(j['body'])) for j in jobs),
      'contexts':{p['id']:excerpt_context(p,p['sentence']) for p in load(CARDS)},'requests':[{k:v for k,v in j.items() if k!='body'} for j in jobs]}


def freeze():
    p=check_plan();record=expected_protocol()
    if record['planned_calls']!=p['maximum_calls'] or record['largest_request_bytes']>p['maximum_request_bytes']:raise ValueError('Challenge budget/wire cap exceeded.')
    with PROTOCOL.open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
    return {'planned_calls':record['planned_calls'],'planned_answers':record['planned_answers']}


def check():
    p=check_plan();committed(PROTOCOL)
    if load(PROTOCOL)!=expected_protocol():raise ValueError('Exact robustness protocol changed.')
    return p,requests()

def run(profile):
    p,jobs=check();profile_check(profile)
    if any(profile[k]!=p[k] for k in ('model','endpoint','context_tokens')):raise ValueError('Subject robustness profile changed.')
    key=clean_api_key(profile.get('api_key',''))
    if not key:raise ValueError('Server-side key required.')
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.mkdir()
    (OUT/'requests.json').write_text(json.dumps(jobs,indent=2)+'\n');rows=[];reason=None
    opener=urllib.request.build_opener(NoRedirect())
    with (OUT/'responses.jsonl').open('x') as stream:
        for job in jobs:
            row={k:v for k,v in job.items() if k!='body'};start=time.perf_counter()
            try:
                request=urllib.request.Request(profile['endpoint'],data=encoded(job['body']),headers={'Content-Type':'application/json','Authorization':'Bearer '+key},method='POST')
                with opener.open(request,timeout=30) as response:content=response.read(1048577)
                if len(content)>1048576:raise ValueError('Oversized response.')
                raw=json.loads(content);row['raw_response']=redact(raw,key)
                if not isinstance(raw,dict) or raw.get('model')!=MODEL:raise GlobalReplyError('checkpoint_mismatch')
                row.update(validate_reply(raw,job['body'],p['context_tokens']))
                tokens=row['usage'].get('input_tokens')
                if isinstance(tokens,bool) or not isinstance(tokens,int) or not 1<=tokens<=p['context_tokens']:raise GlobalReplyError('usage_or_context_failure')
            except urllib.error.HTTPError as error:
                reason='provider_http_'+str(error.code);row.update(status='error',error=reason);error.close()
            except (GlobalReplyError,OSError,ValueError,KeyError,TypeError) as error:
                reason='request_or_validation_failure';row.update(status='error',error=type(error).__name__)
            row=redact(row,key);row['latency_ms']=(time.perf_counter()-start)*1000;rows.append(row);stream.write(json.dumps(row)+'\n');stream.flush()
            print(f"Subject robustness {len(rows)}/{len(jobs)} {row['arm']} round {row['round']} {row['status']}",flush=True)
            if reason:break
    summary={'schema':'subject-robustness-hosted-1','planned_calls':len(jobs),'attempted_calls':len(rows),'failed':sum(r['status']=='error' for r in rows),
        'unattempted_calls':len(jobs)-len(rows),'status':'completed' if len(rows)==len(jobs) and not reason else 'incomplete_or_failed',
        'stopped_reason':reason,'protocol_sha256':sha(PROTOCOL.read_bytes()),'files':{n:sha((OUT/n).read_bytes()) for n in ('requests.json','responses.jsonl')}}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');return summary


def verified_rows():
    p,jobs=check();summary=load(OUT/'summary.json')
    if summary['schema']!='subject-robustness-hosted-1' or summary['protocol_sha256']!=sha(PROTOCOL.read_bytes()) or set(summary['files'])!={'requests.json','responses.jsonl'}:raise ValueError('Subject robustness run identity changed.')
    for n,digest in summary['files'].items():
        if sha((OUT/n).read_bytes())!=digest:raise ValueError('Subject robustness run file changed.')
    if load(OUT/'requests.json')!=jobs:raise ValueError('Subject robustness saved requests changed.')
    rows=[json.loads(line) for line in (OUT/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(jobs):raise ValueError('Extra review responses.')
    for r,j in zip(rows,jobs):
        if any(r.get(k)!=v for k,v in j.items() if k!='body') or r['status'] not in ('ok','ok_with_review','error'):raise ValueError('Subject robustness response identity changed.')
        if r['status']!='error':
            validated=validate_reply(r['raw_response'],j['body'],p['context_tokens'])
            if any(r.get(k)!=v for k,v in validated.items()):raise ValueError('Subject robustness normalized answer changed.')
        if isinstance(r.get('latency_ms'),bool) or not isinstance(r.get('latency_ms'),(float,int)) or r['latency_ms']<0:raise ValueError('Invalid recorded latency.')
    complete=len(rows)==len(jobs) and not any(r['status']=='error' for r in rows)
    if (summary['planned_calls'],summary['attempted_calls'],summary['failed'],summary['unattempted_calls'],summary['status'])!=(len(jobs),len(rows),sum(r['status']=='error' for r in rows),len(jobs)-len(rows),'completed' if complete else 'incomplete_or_failed'):
        raise ValueError('Subject robustness run denominators changed.')
    if not complete or summary['stopped_reason']:raise ValueError('Complete review calls required; preserve failure and stop.')
    return rows



def assess(cards,refs,rows):
    index={(r['card_id'],r['arm'],r['round']):r for r in rows};outcomes=[];panels={}
    for p in cards:
        ref=refs[p['id']]
        for n in (1,2,3):
            for arm in ARMS:
                r=index.get((p['id'],arm,n),{});a=r.get('answers',{}).get(p['sentence']+'_subject')
                quarantined=p['sentence'] in r.get('quarantined_sentences',[])
                choice=a['choice'] if a and not quarantined else 'unavailable'
                probability=a['probabilities'][a['choice']] if a and not quarantined else None
                eligible=choice not in ('unresolved','unavailable') and probability>=.70
                visible=ref['visible_subjects'][arm];original=ref['source_subject']
                outcomes.append({'card_id':p['id'],'dataset':p['dataset'],'family':p['family'],'arm':arm,'round':n,'choice':choice,'probability':probability,
                  'visible_reference':visible,'source_reference':original,'visible_correct':choice==visible,'source_correct':choice==original,
                  'eligible':eligible,'unsupported_eligible':eligible and choice!=visible,'wrong_source_eligible':eligible and choice!=original,
                  'safe_source_eligible':eligible and choice==original and choice==visible,'known_source':original!='unresolved','known_visible':visible!='unresolved',
                  'quarantined':quarantined,'complete':r.get('status') in ('ok','ok_with_review')})
    for dataset in sorted({p['dataset'] for p in cards}):
        panels[dataset]={}
        for family in ['all']+sorted({p['family'] for p in cards}):
            arms={};gate=[]
            for arm in ARMS:
                rounds=[]
                for n in (1,2,3):
                    rr=[o for o in outcomes if o['dataset']==dataset and (family=='all' or o['family']==family) and o['arm']==arm and o['round']==n]
                    value={k:sum(o[k] for o in rr) for k in ('visible_correct','source_correct','eligible','unsupported_eligible','wrong_source_eligible','safe_source_eligible','known_source','known_visible','quarantined')}
                    value.update(round=n,denominator=len(rr),complete=all(o['complete'] for o in rr),withheld=sum(not o['eligible'] for o in rr),
                      correct_visible_eligible=sum(o['eligible'] and o['visible_correct'] for o in rr),
                      predicted_unresolved=sum(o['choice']=='unresolved' for o in rr),correct_unresolved=sum(o['choice']=='unresolved' and o['visible_reference']=='unresolved' for o in rr),
                      unresolved_opportunities=sum(o['visible_reference']=='unresolved' for o in rr))
                    rounds.append(value)
                arms[arm]=rounds
            for i in range(3):
                a=arms['excerpt'][i];b=arms['full'][i]
                candidate=[o for o in outcomes if o['dataset']==dataset and (family=='all' or o['family']==family) and o['round']==i+1 and o['arm']=='excerpt']
                comparator={(o['card_id']):o for o in outcomes if o['arm']=='full' and o['round']==i+1}
                losses=sum(comparator[o['card_id']]['safe_source_eligible'] and not o['safe_source_eligible'] for o in candidate)
                gate.append(bool(a['complete'] and b['complete'] and a['visible_correct']==a['denominator'] and a['unsupported_eligible']==0 and a['wrong_source_eligible']==0 and (not a['known_visible'] or a['correct_visible_eligible']/a['known_visible']>=.9) and losses==0))
            panels[dataset][family]={'arms':arms,'candidate_passes_by_round':gate,'candidate_passes':all(gate)}
    paired=[]
    for dataset in panels:
        for comparator_arm in ('full','prefix'):
            for n in (1,2,3):
                aa=[o for o in outcomes if o['dataset']==dataset and o['arm']=='excerpt' and o['round']==n]
                bb={o['card_id']:o for o in outcomes if o['dataset']==dataset and o['arm']==comparator_arm and o['round']==n}
                paired.append({'dataset':dataset,'comparator':comparator_arm,'round':n,
                    'source_display_gains':sum(o['safe_source_eligible'] and not bb[o['card_id']]['safe_source_eligible'] for o in aa),
                    'source_display_losses':sum(bb[o['card_id']]['safe_source_eligible'] and not o['safe_source_eligible'] for o in aa)})
    costs={arm:{'calls':sum(r['arm']==arm for r in rows),'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in rows if r['arm']==arm),'summed_latency_seconds':sum(r['latency_ms'] for r in rows if r['arm']==arm)/1000} for arm in ARMS}
    return {'outcomes':outcomes,'panels':panels,'paired':paired,'costs':costs,'candidate_passes':all(p['candidate_passes'] for pp in panels.values() for p in pp.values())}


def score():
    rows=verified_rows();cards=load(CARDS);refs=load(REFERENCES)
    return {'schema':'subject-robustness-results-1','calls':len(rows),'raw_answers':sum(len(r.get('raw_response',{}).get('answers',{})) for r in rows),
      'valid_answers':sum(len(r.get('answers',{})) for r in rows),'human_reviews':0,'independent_reviews':0,'new_recordings':0,
      'protocol_sha256':sha(PROTOCOL.read_bytes()),'run_summary_sha256':sha((OUT/'summary.json').read_bytes()),**assess(cards,refs,rows)}
