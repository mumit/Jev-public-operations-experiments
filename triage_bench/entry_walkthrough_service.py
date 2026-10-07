"""Serve frozen tasks; participant progress never reaches the server."""
import copy
from . import entry_walkthrough as t

class EntryWalkthrough:
    def __init__(self):self.cache={}
    def verified(self,preview=False):
        paths=[t.PLAN,t.PACK,t.PROTOCOL,*(t.ROOT/n for n in (*t.SOURCES,*t.UI_SOURCES)),*(t.ROOT/n for n in t.load(t.PLAN)['evidence_sha256'])]
        signature=tuple((str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in paths if p.exists())
        key=bool(preview)
        if key not in self.cache or self.cache[key][0]!=signature:
            if t.PROTOCOL.exists():identity=t.verify()
            elif preview:t.check_pack();identity={'protocol_sha256':'draft_preview'}
            else:raise ValueError('The participant interface has not been frozen.')
            self.cache[key]=(signature,identity)
        return self.cache[key][1]
    def pack(self,preview=False):
        try:identity=self.verified(preview)
        except (OSError,ValueError,KeyError):return {'available':False,'error':'The frozen walkthrough is not available yet.'}
        pack=copy.deepcopy(t.load(t.PACK));pack.pop('references')
        for task in pack['tasks']:
            for key in ('family','recorded_reply','source_card'):task.pop(key,None)
        return {'available':True,**pack,'protocol_sha256':identity['protocol_sha256'],'pack_sha256':t.sha(t.PACK.read_bytes()),'mode':'assistant_preview' if preview else 'participant','server_writes':0}
    def references(self,preview=False):
        self.verified(preview)
        return {'references':t.load(t.PACK)['references'],'origin':'Assistant-authored entry references, not independent analyst review.'}
