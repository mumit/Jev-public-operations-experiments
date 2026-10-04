"""Failure-inclusive repeat scoring; no inference or threshold fitting."""
import json
from pathlib import Path
from .paths import ROOT
from .public_data import sha
from .hosted import encoded
from .public_rca_trial import normalize
from .public_rca_stages import load
from .public_repeat_trial import ARMS,ROUNDS,check,DATA


def verified_rows(protocol_path,folder,complete=False):
    protocol=load(protocol_path);planned=check(protocol);folder=Path(folder);summary=load(folder/'summary.json')
    if summary['protocol_sha256']!=sha(Path(protocol_path).read_bytes()) or summary['planned']!=len(planned):raise ValueError('Replay summary differs from protocol.')
    for name,digest in summary['evidence_sha256'].items():
        if name not in {'requests.json','responses.jsonl'} or sha((folder/name).read_bytes())!=digest:raise ValueError('Replay evidence changed.')
    if set(summary['evidence_sha256'])!={'requests.json','responses.jsonl'}:raise ValueError('Missing replay evidence fingerprint.')
    requests=load(folder/'requests.json')
    if requests!=planned or any(sha(encoded(r['body']))!=r['request_sha256'] for r in requests):raise ValueError('Recorded replay requests changed.')
    rows=[json.loads(line) for line in (folder/'responses.jsonl').read_text().splitlines()]
    if len(rows)>len(planned):raise ValueError('Too many replay rows.')
    for row,request in zip(rows,planned):
        if any(row.get(k)!=v for k,v in request.items() if k!='body'):raise ValueError('Replay identity join changed.')
        if row['status'] not in {'ok','error'}:raise ValueError('Unknown replay status.')
        if row['status']=='ok':
            choice,probabilities,confidence=normalize(row['raw_response'],request['body']['questions']['cause']['criteria'])
            if (choice,probabilities,confidence)!=(row['choice'],row['probabilities'],row.get('provider_confidence')):raise ValueError('Replay normalization changed.')
    failed=sum(r['status']!='ok' for r in rows);completed=len(rows)==len(planned) and not failed
    if (summary['attempted'],summary['failed'],summary['unattempted'],summary['status'])!=(len(rows),failed,len(planned)-len(rows),'completed' if completed else 'incomplete_or_failed'):raise ValueError('Replay denominator changed.')
    if complete and not completed:raise ValueError('Complete replay evidence required.')
    return protocol,rows


def displayed(row,threshold):
    return row is not None and row['status']=='ok' and row['choice']!='insufficient_evidence' and row['probabilities'][row['choice']]>=threshold


def assess(protocol,rows,references,original):
    actual={r['id']:r for r in rows};metrics={};cases=[]
    for case in protocol['cases']:
        identifier=case['id'];target=references[identifier]['target'];result={**case,'target':target,'arms':{}}
        for arm in ARMS:
            threshold=protocol['thresholds'][arm];old=original[(identifier,arm)];repeats=[]
            for round_number in range(1,ROUNDS+1):
                row=actual.get(f'{identifier}::{arm}::r{round_number}')
                ok=row is not None and row['status']=='ok';choice=row['choice'] if ok else 'missing'
                repeats.append({'round':round_number,'choice':choice,'correct':ok and choice==target,'displayed':displayed(row,threshold),
                    'probability':row['probabilities'][choice] if ok else None,'status':row['status'] if row else 'missing'})
            complete=all(r['status']=='ok' for r in repeats)
            result['arms'][arm]={'original':{'choice':old['choice'],'probability':old['probabilities'][old['choice']],'correct':old['choice']==target,'displayed':displayed(old,threshold)},
                'repeats':repeats,'choice_stable':complete and len({r['choice'] for r in repeats})==1,
                'display_stable':complete and len({r['displayed'] for r in repeats})==1,
                'matches_original_choice':complete and all(r['choice']==old['choice'] for r in repeats),
                'wrong_displayed':sum(r['displayed'] and not r['correct'] for r in repeats)}
        cases.append(result)
    for arm in ARMS:
        per_round=[]
        for number in range(1,ROUNDS+1):
            rs=[c['arms'][arm]['repeats'][number-1] for c in cases]
            per_round.append({'round':number,'cases':len(cases),'correct':sum(r['correct'] for r in rs),'displayed':sum(r['displayed'] for r in rs),
                'wrong_displayed':sum(r['displayed'] and not r['correct'] for r in rs),'withheld':sum(not r['displayed'] for r in rs),'failed_or_missing':sum(r['status']!='ok' for r in rs)})
        metrics[arm]={'distinct_cases':len(cases),'response_slots':len(cases)*ROUNDS,'choice_stable_cases':sum(c['arms'][arm]['choice_stable'] for c in cases),
            'display_stable_cases':sum(c['arms'][arm]['display_stable'] for c in cases),'matches_original_choice_cases':sum(c['arms'][arm]['matches_original_choice'] for c in cases),
            'wrong_displayed_responses':sum(c['arms'][arm]['wrong_displayed'] for c in cases),'per_round':per_round}
    comparisons=[]
    for number in range(1,ROUNDS+1):
        for old,new in [('compact','named'),('named','explained')]:
            comparisons.append({'round':number,'comparison':new+'_vs_'+old,
                'fixes':[c['id'] for c in cases if not c['arms'][old]['repeats'][number-1]['correct'] and c['arms'][new]['repeats'][number-1]['correct']],
                'regressions':[c['id'] for c in cases if c['arms'][old]['repeats'][number-1]['correct'] and not c['arms'][new]['repeats'][number-1]['correct']]})
    failed=sum(r['failed_or_missing'] for m in metrics.values() for r in m['per_round'])
    named=metrics['named'];reasons=[]
    if failed:reasons.append('Failed or missing replay responses.')
    if named['wrong_displayed_responses']:reasons.append('A named-input displayed recommendation is wrong.')
    if named['choice_stable_cases']!=len(cases):reasons.append('Named choices vary across new rounds.')
    if named['display_stable_cases']!=len(cases):reasons.append('Named display decisions vary across new rounds.')
    if any(c['arms']['named']['original']['correct'] and not all(r['correct'] for r in c['arms']['named']['repeats']) for c in cases):reasons.append('Named loses an originally correct service selection.')
    return {'schema':'public-repeat-assessment-1','distinct_cases':len(cases),'distinct_groups':len({c['group'] for c in cases}),
        'response_slots':len(cases)*len(ARMS)*ROUNDS,'failed_or_missing':failed,'metrics':metrics,'cases':cases,'comparisons':comparisons,
        'research_gate':{'passed':not reasons,'reasons':reasons,'meaning':'Author-set repeatability diagnostic, not operational validation; reserve remains unconsumed.'}}


def score(protocol_path,folder):
    protocol,rows=verified_rows(protocol_path,folder);references={};original={}
    for split in ('calibration','evaluation'):
        references.update({r['id']:r for r in load(ROOT/DATA/f'{split}.references.json')})
        source=ROOT/f'runs/public-format/{split}-2026-10-03-v1/responses.jsonl'
        for line in source.read_text().splitlines():
            r=json.loads(line);original[(r['case_id'],r['arm'])]=r
    result=assess(protocol,rows,references,original)
    result['evidence']={'protocol_sha256':sha(Path(protocol_path).read_bytes()),'summary_sha256':sha((Path(folder)/'summary.json').read_bytes())}
    return result
