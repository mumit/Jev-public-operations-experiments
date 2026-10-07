"""Frozen entry tasks and conservative export scoring; no inference or human-data writes."""
import copy,json,math
from .paths import ROOT
from .public_data import sha
from .public_rca_stages import committed,load
from . import optional_question_trial as previous
from .optional_question_policy import decision

PLAN=ROOT/'checkpoints/entry-walkthrough-plan-2026-10-06.json'
PACK=ROOT/'checkpoints/entry-walkthrough-pack-2026-10-06.json'
PROTOCOL=ROOT/'checkpoints/entry-walkthrough-protocol-2026-10-06.json'
FIELDS=('service','channel','kind','polarity','window')
SOURCES=('triage_bench/entry_walkthrough.py','scripts/entry_walkthrough.py')
UI_SOURCES=('triage_bench/entry_walkthrough_service.py','triage_bench/web/entry-walkthrough.html','triage_bench/web/entry-walkthrough.js','triage_bench/web/entry-walkthrough.css')
# Post-result, purposeful usability samples. Fixed before participant activity.
SELECTION=(('Train Ticket','explicit_magnitude',1,'entry'),('Online Boutique','omitted_service',2,'assisted'),('Train Ticket','omitted_channel',1,'assisted'),('Online Boutique','vague_comparison',2,'entry'),('Online Boutique','explicit_magnitude',2,'assisted'),('Train Ticket','omitted_service',1,'entry'),('Online Boutique','omitted_channel',2,'entry'),('Train Ticket','vague_comparison',1,'assisted'))

def replies(entry):
    return {'service':'This claim concerns '+entry['service']+'.','channel':'Use the cpu metric channel.' if entry['channel']=='cpu' else 'Use the mem metric channel.',
      'kind':'Use material absolute scaled magnitude of at least 3.0.' if entry['kind']=='magnitude' else 'Use positive signed scaled change greater than zero.',
      'polarity':'Check the asserted condition, rather than its negation.' if entry['polarity']=='assert' else 'Check the negation of the condition.',
      'window':'Compare before-incident observations with after-incident observations.'}

def reconstruct():
    packets=load(previous.data.DATA/'inputs.json');oldrefs={r['id']:r for r in load(previous.data.DATA/'references.json')}
    rows=[json.loads(x) for x in (previous.output()/'responses.jsonl').read_text().splitlines()];jobs={j['id']:j for j in load(previous.output()/'requests.json')}
    tasks=[];references=[]
    for ordinal,(dataset,family,variant,condition) in enumerate(SELECTION,1):
        p=next(p for p in packets if (p['dataset'],p['family'],p['variant'])==(dataset,family,variant));service=next(iter(p['inventory']))
        kind='direction' if variant==2 and family in ('omitted_service','omitted_channel') else 'magnitude'
        entry={'service':service,'channel':'cpu','kind':kind,'polarity':'assert','window':'before_incident_vs_after_incident'}
        row=next(r for r in rows if r['card_id']==p['id'] and r['round']==1);suggestion=decision(row,'first_question');job=jobs[row['id']]
        tasks.append({'id':'ENT-'+str(ordinal).zfill(2),'source_card':p['id'],'dataset':dataset,'text':p['text'],'inventory':p['inventory'],'condition':condition,'source_replies':replies(entry),'suggestion':suggestion if condition=='assisted' else None,'recorded_reply':{'job_id':row['id'],'request_sha256':job['request_sha256'],'response_sha256':sha(json.dumps(row,sort_keys=True).encode()),'round':1},'family':family})
        references.append({'id':tasks[-1]['id'],'fields':entry,'needed':oldrefs[p['id']]['needed'],'origin':'Assistant-authored full entry and scripted clarification under the declared task; not independent review.'})
    inventory={'northstar-radio-service':['cpu','mem'],'northstar-transport-service':['cpu','mem']}
    practice=[]
    for n,text,entry,needed in [(1,'For northstar-radio-service, memory has material scaled change between the before-incident and after-incident windows.',{'service':'northstar-radio-service','channel':'mem','kind':'magnitude','polarity':'assert','window':'before_incident_vs_after_incident'},[]),(2,'The primary service has positive signed CPU change between the before-incident and after-incident windows. The service name is missing.',{'service':'northstar-transport-service','channel':'cpu','kind':'direction','polarity':'assert','window':'before_incident_vs_after_incident'},['service'])]:
        practice.append({'id':'PRACTICE-'+str(n),'dataset':'Northstar Telecom practice','text':text,'inventory':inventory,'condition':'practice','source_replies':replies(entry),'suggestion':None,'reference':{'fields':entry,'needed':needed}})
    return {'schema':'entry-walkthrough-pack-1','tasks':tasks,'references':references,'practice':practice,'participant_records':0,'provider_calls':0,'new_recordings':0}

def plan():
    previous.verify()
    evidence=(previous.PLAN,previous.protocol_path(),previous.result_path(),*(previous.data.DATA/n for n in ('inputs.json','references.json','manifest.json')),*(previous.output()/n for n in ('requests.json','responses.jsonl','summary.json')))
    p={'schema':'entry-walkthrough-plan-1','authorization':'On 2026-10-06 the user accepted a short entry walkthrough and volunteered to try it. Earlier continuation, major-step commits and public source/evidence publication remain authorized; participant exports are private and are never published automatically.',
       'task':'Two practice tasks, eight exploratory entry tasks; four entry-alone and four assisted in fixed ABBA BAAB order. Each of complete wording, omitted service, omitted channel and vague comparison appears once per condition. Both conditions use two cases per application. Selection is purposeful after model-result exposure, not random or held-out. Distinct wording and catalogs do not eliminate carryover.',
       'evidence':'Reuse inspected frozen optional statements and uniformly round-one replies. Add assistant-authored full entry references and field-specific scripted source replies. No fresh text transfer, measurement, recording, inference, numerical verdict or protected data. The failed first-question model gates remain failed.',
       'procedure':'Practice is separate and excluded. Participant explicitly starts exploratory tasks. All five fields start blank; suggestions never fill fields or ask the source automatically. Both conditions can explicitly request the same field-specific source replies. Record submit or withhold once per task; no scored answer feedback until the eight tasks finish. Keep all attempts, unresolved tasks, incorrect fields, guesses without required source clarification and software interruptions.',
       'recording':'Local browser storage and explicit private JSON download only. No personal name, server POST, provider call or automatic upload. Record selections, requested fields, final disposition, foreground-page time, wall time and optional usefulness comments. Foreground time is a browser proxy, not measured cognitive effort. One self-declared participant, unblinded conditions and assistant-authored references support descriptive usability only, not causal benefit, independent language judgment or production reliability.',
       'freeze':'Commit authoring source and plan before task-pack preparation. Commit pack before browser QA. QA uses a separate assistant_preview mode excluded by the participant validator. Freeze exact task/reference and interface hashes, then commit protocol before enabling participant start. Never substitute QA records for human entries. Existing executed study producers remain unchanged.',
       'source_sha256':{n:sha((ROOT/n).read_bytes()) for n in SOURCES},'evidence_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in evidence}}
    with PLAN.open('x') as f:f.write(json.dumps(p,indent=2)+'\n')
    return {'tasks':8,'practice':2,'provider_calls':0,'participant_records':0}

def check_plan():
    committed(PLAN);p=load(PLAN)
    for n,d in {**p['source_sha256'],**p['evidence_sha256']}.items():
        if sha((ROOT/n).read_bytes())!=d:raise ValueError('Walkthrough dependency changed: '+n)
    return p

def prepare():
    check_plan();pack=reconstruct()
    with PACK.open('x') as f:f.write(json.dumps(pack,indent=2)+'\n')
    return {'tasks':8,'practice':2,'provider_calls':0}

def check_pack():
    check_plan();committed(PACK);p=load(PACK)
    if p!=reconstruct():raise ValueError('Walkthrough pack changed.')
    return p

def freeze():
    check_pack();p={'schema':'entry-walkthrough-protocol-1','plan_sha256':sha(PLAN.read_bytes()),'pack_sha256':sha(PACK.read_bytes()),'ui_sha256':{n:sha((ROOT/n).read_bytes()) for n in UI_SOURCES},'task_order':[t['id'] for t in load(PACK)['tasks']],'conditions':[t['condition'] for t in load(PACK)['tasks']],'preview_is_participant':False,'provider_calls':0}
    with PROTOCOL.open('x') as f:f.write(json.dumps(p,indent=2)+'\n')
    return {'status':'frozen','tasks':8,'provider_calls':0}

def verify():
    p=check_pack();committed(PROTOCOL);r=load(PROTOCOL)
    if r['schema']!='entry-walkthrough-protocol-1' or r['plan_sha256']!=sha(PLAN.read_bytes()) or r['pack_sha256']!=sha(PACK.read_bytes()) or r['ui_sha256']!={n:sha((ROOT/n).read_bytes()) for n in UI_SOURCES} or r['task_order']!=[t['id'] for t in p['tasks']] or r['conditions']!=[t['condition'] for t in p['tasks']]:raise ValueError('Walkthrough protocol or interface changed.')
    return {'status':'verified','tasks':8,'practice':2,'provider_calls':0,'participant_records':0,'protocol_sha256':sha(PROTOCOL.read_bytes())}

def entry_outcome(record,reference):
    fields=record['fields'];missing=[k for k in FIELDS if fields.get(k) is None];matches=fields==reference['fields'];requested={q['field'] for q in record['questions']};ungrounded=[k for k in reference['needed'] if k not in requested]
    return {'submitted':record['disposition']=='submit','withheld':record['disposition']=='withhold','fields_match':matches,'missing_fields':missing,'unclarified_fields':ungrounded,'grounded_correct':record['disposition']=='submit' and matches and not ungrounded,'wrong_entry':record['disposition']=='submit' and not matches,'guessed_match':record['disposition']=='submit' and matches and bool(ungrounded),'unnecessary_questions':sum(q['field'] not in reference['needed'] for q in record['questions'])}

def validate_export(export,allow_preview=False):
    identity=verify();pack=load(PACK)
    if export.get('schema')!='entry-walkthrough-export-1' or export.get('protocol_sha256')!=identity['protocol_sha256'] or export.get('pack_sha256')!=sha(PACK.read_bytes()):raise ValueError('Export protocol identity differs.')
    mode=export.get('mode')
    if mode not in ('participant','assistant_preview') or mode=='assistant_preview' and not allow_preview:raise ValueError('Software preview cannot supply participant evidence.')
    if any(export.get(k)!=0 for k in ('provider_calls','server_writes','automatic_field_entries')) or not isinstance(export.get('session_id'),str) or len(export['session_id'])>80:raise ValueError('Invalid export provenance.')
    records=export.get('records');refs={r['id']:r for r in pack['references']}
    if not isinstance(records,list) or len(records)>8:raise ValueError('Invalid task denominator.')
    outcomes=[]
    def duration(x):return isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x) and 0<=x<=604800000
    for i,r in enumerate(records):
        task=pack['tasks'][i]
        if not isinstance(r,dict) or r.get('id')!=task['id'] or r.get('condition')!=task['condition'] or r.get('disposition') not in ('submit','withhold'):raise ValueError('Task order or condition changed.')
        fields=r.get('fields')
        if not isinstance(fields,dict) or set(fields)!=set(FIELDS):raise ValueError('Five explicit fields required.')
        allowed={'service':list(task['inventory']),'channel':task['inventory'].get(fields['service'],[]),'kind':['magnitude','direction'],'polarity':['assert','deny'],'window':['before_incident_vs_after_incident']}
        if any(v is not None and (not isinstance(v,str) or v not in allowed[k]) for k,v in fields.items()) or r['disposition']=='submit' and any(v is None for v in fields.values()):raise ValueError('Invalid explicit selection.')
        if not duration(r.get('elapsed_ms')) or not duration(r.get('foreground_ms')) or r['foreground_ms']>r['elapsed_ms']+1000:raise ValueError('Invalid browser timing.')
        qs=r.get('questions')
        if not isinstance(qs,list) or len(qs)>100 or any(not isinstance(q,dict) or q.get('field') not in FIELDS or not duration(q.get('at_ms')) or q['at_ms']>r['elapsed_ms']+1000 for q in qs):raise ValueError('Invalid clarification events.')
        if r.get('usefulness') not in (None,'helped','neutral','interrupted','not_used') or not isinstance(r.get('comment',''),str) or len(r.get('comment',''))>2000 or not isinstance(r.get('interruptions'),int) or isinstance(r.get('interruptions'),bool) or r['interruptions']<0:raise ValueError('Invalid participant observations.')
        outcomes.append({'id':r['id'],'condition':r['condition'],**entry_outcome(r,refs[r['id']]),'elapsed_ms':r['elapsed_ms'],'foreground_ms':r['foreground_ms'],'interruptions':r['interruptions'],'questions':len(qs),'usefulness':r.get('usefulness'),'comment':r.get('comment','')})
    panels=[]
    for condition in ('entry','assisted'):
        os=[o for o in outcomes if o['condition']==condition]
        panels.append({'condition':condition,'assigned_tasks':4,'recorded_tasks':len(os),'unrecorded_tasks':4-len(os),'grounded_correct':sum(o['grounded_correct'] for o in os),'wrong_entry':sum(o['wrong_entry'] for o in os),'guessed_matches':sum(o['guessed_match'] for o in os),'withheld':sum(o['withheld'] for o in os),'questions':sum(o['questions'] for o in os),'unnecessary_questions':sum(o['unnecessary_questions'] for o in os),'foreground_ms':sum(o['foreground_ms'] for o in os),'elapsed_ms':sum(o['elapsed_ms'] for o in os)})
    return {'schema':'entry-walkthrough-assessment-1','mode':mode,'self_declared_participants':int(mode=='participant' and bool(records)),'independent_reviews':0,'assigned_tasks':8,'recorded_tasks':len(records),'unrecorded_tasks':8-len(records),'complete':len(records)==8,'panels':panels,'outcomes':outcomes,'provider_calls':0,'server_writes':0,'limits':'One unblinded exploratory walkthrough with assistant-authored task references; descriptive observations, not a causal benefit estimate. Export attribution and browser timing are self-reported, not independently verified.'}
