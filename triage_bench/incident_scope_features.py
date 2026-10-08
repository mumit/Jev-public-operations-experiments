"""Explicit section selection; preserve original claims and question wording."""
import json
from .publisher_report_features import request as original_request

ARMS=('full','selected_full','selected_section')

def select(blocks,inventory,selection):
    if not isinstance(selection,str) or not selection:
        raise ValueError('Select exactly one incident before checking a claim.')
    matches=[s for s in inventory if s['id']==selection]
    if len(matches)!=1:raise ValueError('The selected incident is unavailable or ambiguous.')
    chosen=matches[0]
    indices=[*range(inventory[0]['start']),*range(chosen['start'],chosen['end'])]
    return chosen,indices,'\n\n'.join(blocks[i]['text'] for i in indices)

def request(packet,arm):
    if arm not in ARMS:raise ValueError('Unknown input arm.')
    report=packet['scoped_report'] if arm=='selected_section' else packet['report']
    body=original_request({'report':report,'claim':packet['claim']})
    if arm!='full':
        if not packet.get('selected_incident'):raise ValueError('An explicit incident selection is required.')
        state=json.loads(body['state']);state['selected_incident']=packet['selected_incident']
        body['state']=json.dumps(state,ensure_ascii=False,sort_keys=True)
    return body
