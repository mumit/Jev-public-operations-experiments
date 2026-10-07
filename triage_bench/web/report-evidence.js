'use strict';
const el=id=>document.getElementById(id), params=new URLSearchParams(location.search);
let overview, selected=params.get('source');
function show(source){
  selected=source.id;
  document.querySelectorAll('#sources button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.id===selected)));
  el('source-detail').hidden=false;
  el('source-category').textContent=source.publisher+' · '+source.allocation.replaceAll('_',' ')+' · '+(source.primary?'Primary comparison report':'Related / audit-only report');
  el('source-title').textContent=source.display_title;
  el('source-state').textContent=source.status==='available'?'Retained: extraction and identity checks passed.':'Not retained: '+source.failure_reason+' Its retrieved snapshot remains preserved.';
  el('publisher-link').href=source.url;
  const facts=[['Incident / report group',source.incident_group],['Role',source.primary?'Six planned claim slots; no model calls yet':'No additional model trials'],['Report stage',source.report_kind.replaceAll('_',' ')],['Publisher date',source.publisher_date_metadata||'Not supplied in recognized page metadata'],['Audit date',overview.audit_date]];
  el('source-facts').replaceChildren(...facts.flatMap(([key,value])=>{const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=value;return[dt,dd];}));
  const p=source.input_prefix;
  el('prefix').textContent=p?`The retained prefix contains ${p.included_blocks} of ${source.blocks} extracted blocks (${p.bytes.toLocaleString()} bytes); ${p.omitted_blocks} later blocks are excluded. This is a deterministic preparation preview, not a model result.`:'No input prefix was retained for this failed source. It will not enter the comparison.';
  el('provenance').textContent=JSON.stringify({source_id:source.id,final_url:source.final_url||null,status:source.status,error_type:source.error_type||null,raw_sha256:source.raw_sha256||null,normalized_sha256:source.normalized_sha256||null,input_prefix:source.input_prefix||null},null,2);
  const q=new URLSearchParams({allocation:el('allocation').value,source:selected});history.replaceState(null,'','/report-evidence?'+q);
  el('report-link').href='/study?'+new URLSearchParams({doc:'report-evidence',return:'/report-evidence?'+q});
}
function list(){
  const sources=overview.sources.filter(s=>el('allocation').value==='all'||s.allocation===el('allocation').value);
  el('sources').replaceChildren(...sources.map(s=>{const b=document.createElement('button'),label=document.createElement('strong'),meta=document.createElement('span');b.type='button';b.dataset.id=s.id;label.textContent=s.display_title;meta.textContent=s.publisher+' · '+(s.primary?'Primary':'Related / audit only')+' · '+(s.status==='available'?'Retained':'Failed check');b.append(label,meta);b.addEventListener('click',()=>show(s));return b;}));
  show(sources.find(s=>s.id===selected)||sources[0]);
}
el('allocation').addEventListener('change',list);
(async()=>{try{const response=await fetch('/api/report-evidence');if(!response.ok)throw new Error('Recorded source provenance is unavailable or inconsistent.');overview=await response.json();const allocation=params.get('allocation');if(['all','development','evaluation','audit_only'].includes(allocation))el('allocation').value=allocation;el('status').textContent=`${overview.verification.available_sources} of 12 reports retained · 10 whole incident/report groups · 0 new model calls · 0 independent reference reviews. ${overview.local_cache_available?'Local report snapshots are retained.':'This checkout contains public provenance; complete report snapshots are not bundled.'}`;list();}catch(error){el('status').textContent=error.message;}})();
