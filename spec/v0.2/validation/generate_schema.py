#!/usr/bin/env python3
"""Generate the normative FPO v0.2 machine schema deterministically."""
from __future__ import annotations
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('FPO_SCHEMA_OUT', str(ROOT / 'runtime/schemas/fpo_records.schema.json')))

def ref(name: str): return {'$ref': f'#/$defs/{name}'}
def arr(items, *, min_items=0, unique=False):
    d={'type':'array','items':items}
    if min_items: d['minItems']=min_items
    if unique: d['uniqueItems']=True
    return d
def obj(props, required=(), *, additional=False):
    d={'type':'object','properties':props,'additionalProperties':additional}
    if required: d['required']=list(required)
    return d
def nullable(schema): return {'oneOf':[schema,{'type':'null'}]}
def enum(*xs): return {'type':'string','enum':list(xs)}
def s(min_len=1, max_len=None, pattern=None):
    d={'type':'string'}
    if min_len is not None: d['minLength']=min_len
    if max_len is not None: d['maxLength']=max_len
    if pattern: d['pattern']=pattern
    return d

id_s=s(pattern=r'^[A-Za-z0-9][A-Za-z0-9._:/-]{0,191}$')
ref_s=s(pattern=r'^[^\x00-\x1f]+$')
sha_s=s(pattern=r'^[a-f0-9]{64}$')
ts={'type':'string','format':'date-time'}
nonneg={'type':'number','minimum':0}
int_nonneg={'type':'integer','minimum':0}
checkpoint=enum('none','defined','designed','executed','accepted','closed')
risk_tier=enum('T0','T1','T2','T3')
terminal_disp=enum('completed','canceled','aborted','unsatisfiable','out_of_budget','safety_stop','out_of_scope')
operation_state=enum('prepared','submitted','running','waiting_input','waiting_authorization','succeeded','failed','rejected','timed_out','canceled','unknown')
effect_state=enum('intended','started','confirmed','failed','unknown','compensating','compensated','compensation_failed','forward_recovery_required')
blocker_status=enum('open','investigating','waiting','resolved','superseded')
evidence_status=enum('proposed','valid','superseded','contradicted','retracted')
unit_state=enum('pending','ready','running','blocked','succeeded','failed','skipped','superseded')
criterion_verdict=enum('PASS','FAIL','UNKNOWN','NOT_APPLICABLE')

actor=obj({
    'id': id_s,
    'role': enum('user','runtime','P1','P2','P3','P4','P5','P6','J1','J2','J3','capability','validator','researcher','system'),
    'authority': s(max_len=128),
    'trust_domain': s(max_len=128),
}, ('id','role','authority'))

extensions={'type':'object','patternProperties':{r'^[a-z0-9]+\.[A-Za-z0-9_.-]+$':{}},'additionalProperties':False}
record_envelope=obj({
    '$schema': s(min_len=1),
    'schema_name': {'const':'fpo.record'},
    'schema_version': {'const':'0.2'},
    'record_type': s(max_len=64),
    'record_id': id_s,
    'logical_id': id_s,
    'record_revision': {'type':'integer','minimum':1},
    'work_id': id_s,
    'base_state_revision': int_nonneg,
    'sequence': int_nonneg,
    'actor': actor,
    'created_at': ts,
    'bundle_id': id_s,
    'bundle_revision': s(max_len=64),
    'policy_revision': s(max_len=64),
    'sensitivity': enum('public','internal','confidential','restricted'),
    'retention_class': enum('ephemeral','work_standard','audit_required','legal_hold'),
    'source_refs': arr(ref_s, unique=True),
    'supersedes_refs': arr(ref_s, unique=True),
    'extensions': extensions,
    'payload': {'type':'object'},
}, ('schema_name','schema_version','record_type','record_id','logical_id','record_revision','work_id','base_state_revision','sequence','actor','created_at','bundle_id','bundle_revision','policy_revision','sensitivity','retention_class','payload'))

def variant(record_type: str, payload_def: str):
    return {'allOf':[ref('record_envelope'), {'type':'object','properties':{'record_type':{'const':record_type},'payload':ref(payload_def)}}]}

# Shared payload fragments
budget_metrics=obj({
    'attempts': nonneg, 'strategy_families': nonneg, 'wall_seconds': nonneg,
    'token_units': nonneg, 'monetary_units': nonneg, 'tool_calls': nonneg,
    'research_calls': nonneg, 'capability_calls': nonneg, 'effect_count': nonneg,
    'context_units': nonneg,
})
budget_envelope=obj({
    'limits': budget_metrics,
    'usage': budget_metrics,
    'soft_limit_action': enum('continue','suspend_for_review','suspend_for_approval','reduce_scope'),
    'hard_limit_action': enum('suspend_for_approval','terminate_out_of_budget','reduce_scope'),
    'deadline': nullable(ts),
    'override_approval_ref': nullable(ref_s),
}, ('limits','usage','soft_limit_action','hard_limit_action','deadline','override_approval_ref'))

payloads={}
payloads['payload_work_state']=obj({
    'checkpoint': checkpoint,
    'interrupt_ref': nullable(ref_s),
}, ('checkpoint','interrupt_ref'))

payloads['payload_work_control']=obj({
    'lifecycle_state': enum('active','suspended','canceling','terminated','archived'),
    'terminal_disposition': nullable(terminal_disp),
    'reason': s(max_len=4096),
    'resume_condition_ref': nullable(ref_s),
    'resume_owner': nullable(s(max_len=128)),
    'resume_expiry': nullable(ts),
    'resume_default_action': nullable(s(max_len=256)),
    'latest_user_event_ref': nullable(ref_s),
    'active_approval_refs': arr(ref_s, unique=True),
    'active_operation_refs': arr(ref_s, unique=True),
    'unresolved_effect_refs': arr(ref_s, unique=True),
    'autonomy_budget': budget_envelope,
}, ('lifecycle_state','terminal_disposition','reason','resume_condition_ref','resume_owner','resume_expiry','resume_default_action','latest_user_event_ref','active_approval_refs','active_operation_refs','unresolved_effect_refs','autonomy_budget'))

source_item=obj({
    'item_id': id_s, 'text': s(max_len=20000), 'source_ref': ref_s,
    'kind': enum('request','constraint','preference','attachment','context','amendment','other'),
}, ('item_id','text','source_ref','kind'))
payloads['payload_source_request']=obj({
    'request_text': s(max_len=100000),
    'source_items': arr(source_item, min_items=1),
    'attachment_refs': arr(ref_s, unique=True),
    'supersedes_ref': nullable(ref_s),
}, ('request_text','source_items','attachment_refs','supersedes_ref'))

payloads['payload_work_admission']=obj({
    'source_request_refs': arr(ref_s,min_items=1,unique=True),
    'admissible': {'type':'boolean'},
    'finite': {'type':'boolean'},
    'criteria_identifiable': {'type':'boolean'},
    'effects_bounded': {'type':'boolean'},
    'observable': {'type':'boolean'},
    'single_checkpoint_meaningful': {'type':'boolean'},
    'context_retrievable': {'type':'boolean'},
    'capability_feasible': {'type':'boolean'},
    'risk_tier': risk_tier,
    'reasons': arr(s(max_len=4096)),
    'split_proposals': arr(s(max_len=4096)),
    'required_external_runtime': arr(s(max_len=256)),
    'terminal_recommendation': nullable(terminal_disp),
}, ('source_request_refs','admissible','finite','criteria_identifiable','effects_bounded','observable','single_checkpoint_meaningful','context_retrievable','capability_feasible','risk_tier','reasons','split_proposals','required_external_runtime','terminal_recommendation'))

requirement=obj({
    'requirement_id': id_s,
    'kind': enum('must','should'),
    'text': s(max_len=10000),
    'source_item_refs': arr(ref_s,min_items=1,unique=True),
    'acceptance_claim_ids': arr(id_s,unique=True),
    'applicability_condition': nullable(s(max_len=4096)),
}, ('requirement_id','kind','text','source_item_refs','acceptance_claim_ids'))
assumption=obj({
    'assumption_id': id_s,
    'statement': s(max_len=10000),
    'basis_refs': arr(ref_s,unique=True),
    'impact': enum('low','moderate','high','critical'),
    'reversibility': enum('reversible','partially_reversible','irreversible'),
    'status': enum('adopted','needs_validation','invalidated','resolved','blocked'),
    'validation_route_ref': nullable(ref_s),
    'recheck_condition': nullable(s(max_len=4096)),
}, ('assumption_id','statement','basis_refs','impact','reversibility','status','validation_route_ref'))
coverage=obj({
    'source_item_ref': ref_s,
    'disposition': enum('must','should','design_discretion','out_of_scope','unresolved_blocker','superseded_by_amendment'),
    'target_ref': nullable(ref_s),
    'rationale': s(max_len=4096),
}, ('source_item_ref','disposition','target_ref','rationale'))
rejected=obj({'text':s(max_len=10000),'rationale':s(max_len=4096)},('text','rationale'))
fidelity=obj({
    'required':{'type':'boolean'}, 'reason':s(max_len=4096), 'review_ref':nullable(ref_s),
    'adoption_status':enum('not_required','pending','adopted','rejected'),
},('required','reason','review_ref','adoption_status'))
payloads['payload_work_definition']=obj({
    'source_request_refs':arr(ref_s,min_items=1,unique=True),
    'amendment_refs':arr(ref_s,unique=True),
    'admission_ref':nullable(ref_s),
    'objective':s(max_len=20000),
    'requirements':arr(requirement,min_items=1),
    'out_of_scope':arr(s(max_len=4096)),
    'design_discretion':arr(s(max_len=4096)),
    'assumptions':arr(assumption),
    'decision_priorities':arr(s(max_len=4096),min_items=1),
    'unacceptable_tradeoffs':arr(s(max_len=4096)),
    'risk_tier':risk_tier,
    'required_human_gates':arr(s(max_len=4096)),
    'coverage':arr(coverage,min_items=1),
    'rejected_interpretations':arr(rejected),
    'unresolved_items':arr(s(max_len=4096)),
    'fidelity_review':fidelity,
}, ('source_request_refs','amendment_refs','objective','requirements','out_of_scope','design_discretion','assumptions','decision_priorities','unacceptable_tradeoffs','risk_tier','required_human_gates','coverage','rejected_interpretations','unresolved_items','fidelity_review'))

validation_method_payload=obj({
    'method_id':id_s,'method_revision':s(max_len=64),
    'claim_ids':arr(id_s,min_items=1,unique=True),
    'description':s(max_len=20000),
    'procedure_ref':nullable(ref_s),
    'object_scope':arr(ref_s,min_items=1),
    'environment_constraints':arr(s(max_len=4096)),
    'expected_strength':enum('supporting','substantial','conclusive'),
    'change_reason':nullable(s(max_len=4096)),
    'equivalence_evidence_refs':arr(ref_s,unique=True),
    'independent_support_required':{'type':'boolean'},
    'status':enum('proposed','adopted','superseded','rejected'),
},('method_id','method_revision','claim_ids','description','procedure_ref','object_scope','environment_constraints','expected_strength','equivalence_evidence_refs','independent_support_required','status'))
payloads['payload_validation_method']=validation_method_payload

failure_route=obj({
    'route_id':id_s,'condition':s(max_len=10000),
    'route':enum('none','defined','designed','executed','active_blocker'),
    'required_evidence_claims':arr(id_s,unique=True),
},('route_id','condition','route','required_evidence_claims'))
plan_unit=obj({
    'unit_id':id_s,'objective':s(max_len=10000),'owner_stage':enum('P3'),
    'dependencies':arr(id_s,unique=True),'preconditions':arr(s(max_len=4096)),
    'input_refs':arr(ref_s,unique=True),'target_refs':arr(ref_s,unique=True),
    'capability_class':s(max_len=256),'binding_constraints':arr(s(max_len=4096)),
    'logical_intent_id':id_s,
    'expected_artifact_refs':arr(ref_s,unique=True),'expected_claim_ids':arr(id_s,unique=True),
    'effect_intent_refs':arr(ref_s,unique=True),'validation_hook_refs':arr(ref_s,unique=True),
    'retry_policy':s(max_len=10000),'stop_conditions':arr(s(max_len=4096)),
    'failure_routes':arr(failure_route),
    'compensation_hook_ref':nullable(ref_s),'forward_recovery_hook_ref':nullable(ref_s),
},('unit_id','objective','owner_stage','dependencies','preconditions','target_refs','capability_class','logical_intent_id','expected_artifact_refs','expected_claim_ids','effect_intent_refs','validation_hook_refs','retry_policy','stop_conditions','failure_routes'))
payloads['payload_execution_plan']=obj({
    'definition_ref':ref_s,'design_revision':s(max_len=64),
    'validation_method_refs':arr(ref_s,min_items=1,unique=True),
    'units':arr(plan_unit,min_items=1),
    'integration_claim_ids':arr(id_s,unique=True),
    'budget_allocation_ref':ref_s,
    'environment_revision_refs':arr(ref_s,unique=True),
},('definition_ref','design_revision','validation_method_refs','units','integration_claim_ids','budget_allocation_ref'))

payloads['payload_plan_unit_state']=obj({
    'plan_ref':ref_s,'unit_id':id_s,'state':unit_state,
    'attempt_refs':arr(ref_s,unique=True),'operation_refs':arr(ref_s,unique=True),
    'effect_refs':arr(ref_s,unique=True),'adopted_result_refs':arr(ref_s,unique=True),
    'blocked_by_refs':arr(ref_s,unique=True),'target_revision_refs':arr(ref_s,unique=True),
    'last_event_ref':nullable(ref_s),
},('plan_ref','unit_id','state','attempt_refs','operation_refs','effect_refs','adopted_result_refs','blocked_by_refs','target_revision_refs','last_event_ref'))

hypothesis=obj({'hypothesis_id':id_s,'statement':s(max_len=10000),'status':enum('possible','supported','weakened','rejected','confirmed'),'evidence_refs':arr(ref_s,unique=True)},('hypothesis_id','statement','status','evidence_refs'))
payloads['payload_blocker']=obj({
    'kind':s(max_len=128),'status':blocker_status,'scope':s(max_len=256),'blocks_core':{'type':'boolean'},
    'source_stage':s(max_len=64),'affected_revision_refs':arr(ref_s,unique=True),
    'symptom':s(max_len=20000),'hypotheses':arr(hypothesis),
    'earliest_unrepaired_error':nullable(s(max_len=10000)),
    'root_cause':nullable(s(max_len=10000)),
    'contributing_factors':arr(s(max_len=4096)),'detection_gap':nullable(s(max_len=10000)),
    'dependency_blocker_refs':arr(ref_s,unique=True),'attempt_refs':arr(ref_s,unique=True),
    'strategy_families_tried':arr(s(max_len=256),unique=True),'progress_claims':arr(ref_s,unique=True),
    'required_evidence_claim_ids':arr(id_s,unique=True),'required_capability_classes':arr(s(max_len=256),unique=True),
    'required_approval_refs':arr(ref_s,unique=True),'resume_condition_ref':nullable(ref_s),
    'resume_owner':nullable(s(max_len=128)),'resume_expiry':nullable(ts),'resume_default_action':nullable(s(max_len=256)),
    'next_normal_authority':enum('P1','P2','P3','P4','P5','P6','runtime'),
    'rollback_checkpoint':checkpoint,'resolution_evidence_refs':arr(ref_s,unique=True),
    'terminal_recommendation':nullable(terminal_disp),
},('kind','status','scope','blocks_core','source_stage','affected_revision_refs','symptom','hypotheses','contributing_factors','dependency_blocker_refs','attempt_refs','strategy_families_tried','progress_claims','required_evidence_claim_ids','required_capability_classes','required_approval_refs','resume_condition_ref','next_normal_authority','rollback_checkpoint','resolution_evidence_refs','terminal_recommendation'))
payloads['payload_blocker_set']=obj({
    'active_blocker_refs':arr(ref_s,unique=True),'blocking_count':int_nonneg,'waiting_count':int_nonneg,
    'scope_summary':arr(s(max_len=4096)),'last_p5_decision_ref':nullable(ref_s),
},('active_blocker_refs','blocking_count','waiting_count','scope_summary','last_p5_decision_ref'))
payloads['payload_progress_claim']=obj({
    'blocker_ref':ref_s,'claim_id':id_s,
    'before_state':s(max_len=10000),'after_state':s(max_len=10000),
    'newly_adopted_refs':arr(ref_s,unique=True),'invalidated_refs':arr(ref_s,unique=True),
    'cost_delta':nonneg,'risk_delta':s(max_len=4096),'debt_delta':s(max_len=4096),'scope_divergence':s(max_len=4096),
    'strategy_family':s(max_len=256),'material_difference':s(max_len=10000),
    'net_material':{'type':'boolean'},'rationale':s(max_len=10000),
},('blocker_ref','claim_id','before_state','after_state','newly_adopted_refs','invalidated_refs','cost_delta','risk_delta','debt_delta','scope_divergence','strategy_family','material_difference','net_material','rationale'))

payloads['payload_delegated_operation']=obj({
    'logical_intent_id':id_s,'dispatch_id':id_s,'attempt_id':id_s,'remote_operation_id':nullable(id_s),
    'plan_unit_id':id_s,'owner_stage':enum('P3','P5'),
    'capability_id':id_s,'capability_revision':s(max_len=64),'binding_ref':ref_s,
    'dispatch_payload_ref':ref_s,'dispatch_payload_sha256':sha_s,
    'state':operation_state,'provider_sequence':int_nonneg,'deadline':nullable(ts),'lease_expires_at':nullable(ts),
    'cancel_requested_at':nullable(ts),'cancel_acknowledged':{'type':'boolean'},
    'input_request_ref':nullable(ref_s),'auth_request_ref':nullable(ref_s),
    'partial_artifact_refs':arr(ref_s,unique=True),'evidence_refs':arr(ref_s,unique=True),'effect_refs':arr(ref_s,unique=True),
    'return_ref':nullable(ref_s),'return_sha256':nullable(sha_s),'adoption_status':enum('pending','adopted','rejected','superseded'),
    'target_revision_ref':ref_s,'error_summary':nullable(s(max_len=20000)),
},('logical_intent_id','dispatch_id','attempt_id','remote_operation_id','plan_unit_id','owner_stage','capability_id','capability_revision','binding_ref','dispatch_payload_ref','dispatch_payload_sha256','state','provider_sequence','deadline','lease_expires_at','cancel_requested_at','cancel_acknowledged','input_request_ref','auth_request_ref','partial_artifact_refs','evidence_refs','effect_refs','return_ref','return_sha256','adoption_status','target_revision_ref','error_summary'))

payloads['payload_evidence']=obj({
    'claim_id':id_s,'criterion_id':nullable(id_s),'method_id':id_s,'method_revision':s(max_len=64),
    'object_ref':ref_s,'object_revision':s(max_len=128),'design_revision':s(max_len=128),
    'plan_revision':nullable(s(max_len=128)),'environment_ref':ref_s,'environment_revision':s(max_len=128),
    'observed_at':ts,'freshness_policy':s(max_len=10000),'expires_at':nullable(ts),
    'producer_id':id_s,'verifier_id':nullable(id_s),'trust_domain':s(max_len=256),
    'source_lineage':arr(s(max_len=4096),min_items=1),'coverage':enum('full','partial','sample','counterexample','diagnostic'),
    'independence_basis':s(max_len=10000),'independence_group':nullable(s(max_len=256)),
    'status':evidence_status,'supersedes_refs':arr(ref_s,unique=True),'contradiction_refs':arr(ref_s,unique=True),
    'raw_observation_refs':arr(ref_s,min_items=1,unique=True),'adopted_by':nullable(enum('P4','P5')),
},('claim_id','criterion_id','method_id','method_revision','object_ref','object_revision','design_revision','environment_ref','environment_revision','observed_at','freshness_policy','expires_at','producer_id','verifier_id','trust_domain','source_lineage','coverage','independence_basis','status','supersedes_refs','contradiction_refs','raw_observation_refs','adopted_by'))

payloads['payload_criteria_verdict']=obj({
    'criterion_id':id_s,'verdict':criterion_verdict,'evidence_refs':arr(ref_s,unique=True),
    'method_refs':arr(ref_s,unique=True),'object_revision_refs':arr(ref_s,unique=True),
    'coverage_complete':{'type':'boolean'},'freshness_ok':{'type':'boolean'},'conflict_status':enum('none','resolved','unresolved'),
    'independence_satisfied':{'type':'boolean'},'rationale':s(max_len=10000),
},('criterion_id','verdict','evidence_refs','method_refs','object_revision_refs','coverage_complete','freshness_ok','conflict_status','independence_satisfied','rationale'))

payloads['payload_effect']=obj({
    'effect_id':id_s,'logical_intent_id':id_s,'plan_unit_id':id_s,
    'effect_class':enum('read_only','idempotent','compensatable','pivot','irreversible'),'state':effect_state,
    'target_ref':ref_s,'target_revision_before':s(max_len=256),'target_revision_after':nullable(s(max_len=256)),
    'approval_ref':nullable(ref_s),'preconditions':arr(s(max_len=4096)),
    'idempotency_key':nullable(s(max_len=512)),'reconcile_method':s(max_len=10000),
    'compensation_plan_ref':nullable(ref_s),'forward_recovery_plan_ref':nullable(ref_s),
    'dependency_effect_refs':arr(ref_s,unique=True),'outcome_evidence_refs':arr(ref_s,unique=True),
    'failure_summary':nullable(s(max_len=20000)),
},('effect_id','logical_intent_id','plan_unit_id','effect_class','state','target_ref','target_revision_before','target_revision_after','approval_ref','preconditions','idempotency_key','reconcile_method','compensation_plan_ref','forward_recovery_plan_ref','dependency_effect_refs','outcome_evidence_refs','failure_summary'))

security_scope=obj({
    'tools':arr(s(max_len=256),unique=True),'data':arr(s(max_len=256),unique=True),'paths':arr(s(max_len=1024),unique=True),
    'network':arr(s(max_len=1024),unique=True),'secret_handles':arr(s(max_len=256),unique=True),
},('tools','data','paths','network','secret_handles'))
operational_profile=obj({
    'health':enum('healthy','degraded','unhealthy','unknown'),'availability_checked_at':ts,
    'cost_class':s(max_len=64),'latency_class':s(max_len=64),
    'supports_cancel':{'type':'boolean'},'supports_stream':{'type':'boolean'},'supports_reconcile':{'type':'boolean'},
    'idempotency_support':s(max_len=128),
},('health','availability_checked_at','cost_class','latency_class','supports_cancel','supports_stream','supports_reconcile','idempotency_support'))
fitness=obj({'risk_ceiling':risk_tier,'quality_class':s(max_len=128),'eval_refs':arr(ref_s,unique=True)},('risk_ceiling','quality_class','eval_refs'))
payloads['payload_capability_entry']=obj({
    'capability_id':id_s,'capability_revision':s(max_len=64),'kind':enum('agent','tool','harness','service','human'),
    'provider_identity':s(max_len=512),'registry_trust_ref':ref_s,
    'provides':arr(s(max_len=256),min_items=1,unique=True),'accepts':arr(s(max_len=256),unique=True),'returns':arr(s(max_len=256),unique=True),
    'side_effect_profile':s(max_len=256),'security_scope':security_scope,'operational_profile':operational_profile,
    'fitness':fitness,'compatibility':arr(s(max_len=256),unique=True),'fallback_capability_refs':arr(ref_s,unique=True),
    'binding_ref':ref_s,'status':enum('active','degraded','disabled','revoked'),
},('capability_id','capability_revision','kind','provider_identity','registry_trust_ref','provides','accepts','returns','side_effect_profile','security_scope','operational_profile','fitness','compatibility','fallback_capability_refs','binding_ref','status'))

payloads['payload_approval']=obj({
    'approval_id':id_s,'grantor_id':id_s,'status':enum('granted','revoked','expired','consumed'),
    'scope':arr(s(max_len=4096),min_items=1),'target_refs':arr(ref_s,unique=True),'revision_constraints':arr(s(max_len=256)),
    'allowed_effect_classes':arr(enum('read_only','idempotent','compensatable','pivot','irreversible'),unique=True),
    'conditions':arr(s(max_len=4096)),'valid_from':ts,'expires_at':nullable(ts),'revocation_ref':nullable(ref_s),
},('approval_id','grantor_id','status','scope','target_refs','revision_constraints','allowed_effect_classes','conditions','valid_from','expires_at','revocation_ref'))

payloads['payload_resource_budget']=obj({
    'budget_id':id_s,'scope_ref':ref_s,'budget':budget_envelope,'measured_at':ts,
},('budget_id','scope_ref','budget','measured_at'))

artifact_entry=obj({
    'artifact_id':id_s,'path_or_uri':ref_s,'sha256':nullable(sha_s),'media_type':nullable(s(max_len=256)),
    'revision':s(max_len=128),'source_unit_refs':arr(id_s,unique=True),'adoption_status':enum('pending','adopted','rejected','superseded'),
},('artifact_id','path_or_uri','sha256','media_type','revision','source_unit_refs','adoption_status'))
payloads['payload_artifact_manifest']=obj({
    'manifest_id':id_s,'target_revision':s(max_len=128),'artifacts':arr(artifact_entry,min_items=1),
    'integration_claim_ids':arr(id_s,unique=True),'environment_revision_refs':arr(ref_s,unique=True),
},('manifest_id','target_revision','artifacts','integration_claim_ids','environment_revision_refs'))

payloads['payload_control_event']=obj({
    'event_type':enum('pause','resume','cancel','amendment','approval_grant','approval_revoke','budget_override','external_condition'),
    'issued_by':id_s,'scope':arr(s(max_len=4096)),'effective_at':ts,
    'amendment_ref':nullable(ref_s),'approval_ref':nullable(ref_s),'reason':s(max_len=10000),
},('event_type','issued_by','scope','effective_at','amendment_ref','approval_ref','reason'))

unit_projection=obj({
    'unit_id':id_s,'state':unit_state,'adopted_result_refs':arr(ref_s,unique=True),
    'operation_refs':arr(ref_s,unique=True),'effect_refs':arr(ref_s,unique=True),'last_event_ref':nullable(ref_s),
},('unit_id','state','adopted_result_refs','operation_refs','effect_refs','last_event_ref'))
payloads['payload_current_projection']=obj({
    'state_revision':int_nonneg,'current_commit_id':id_s,
    'work_state_ref':ref_s,'work_control_ref':ref_s,'source_request_ref':ref_s,
    'definition_ref':nullable(ref_s),'design_ref':nullable(ref_s),'execution_plan_ref':nullable(ref_s),
    'unit_state_refs':arr(ref_s,unique=True),'unit_states':arr(unit_projection),'active_blocker_set_ref':nullable(ref_s),
    'open_operation_refs':arr(ref_s,unique=True),'unresolved_effect_refs':arr(ref_s,unique=True),
    'evidence_index_refs':arr(ref_s,unique=True),'active_approval_refs':arr(ref_s,unique=True),
    'budget_ref':nullable(ref_s),'artifact_manifest_ref':nullable(ref_s),
    'open_obligations':arr(s(max_len=10000)),'recent_event_refs':arr(ref_s,unique=True),'archive_refs':arr(ref_s,unique=True),
},('state_revision','current_commit_id','work_state_ref','work_control_ref','source_request_ref','definition_ref','design_ref','execution_plan_ref','unit_state_refs','unit_states','active_blocker_set_ref','open_operation_refs','unresolved_effect_refs','evidence_index_refs','active_approval_refs','budget_ref','artifact_manifest_ref','open_obligations','recent_event_refs','archive_refs'))

payloads['payload_ledger_event']=obj({
    'event_type':s(max_len=128),'summary':s(max_len=20000),'fact_refs':arr(ref_s,unique=True),
    'decision_refs':arr(ref_s,unique=True),'supersedes_refs':arr(ref_s,unique=True),
    'rationale':s(max_len=20000),'hidden_reasoning_included':{'const':False},
},('event_type','summary','fact_refs','decision_refs','supersedes_refs','rationale','hidden_reasoning_included'))

payloads['payload_terminal_settlement']=obj({
    'disposition':terminal_disp,'achievement_checkpoint':checkpoint,
    'definition_ref':nullable(ref_s),'execution_plan_ref':nullable(ref_s),'artifact_manifest_ref':nullable(ref_s),
    'criteria_verdict_refs':arr(ref_s,unique=True),'open_blocker_refs':arr(ref_s,unique=True),
    'inflight_operation_refs':arr(ref_s,unique=True),'unsettled_effect_refs':arr(ref_s,unique=True),
    'known_limitations':arr(s(max_len=10000)),'remaining_obligations':arr(s(max_len=10000)),
    'handoff_ref':nullable(ref_s),'retention_summary':s(max_len=10000),'settled_at':ts,
},('disposition','achievement_checkpoint','definition_ref','execution_plan_ref','artifact_manifest_ref','criteria_verdict_refs','open_blocker_refs','inflight_operation_refs','unsettled_effect_refs','known_limitations','remaining_obligations','handoff_ref','retention_summary','settled_at'))

digest_entry=obj({'ref':ref_s,'sha256':sha_s},('ref','sha256'))
payloads['payload_commit']=obj({
    'commit_id':id_s,'parent_commit_id':nullable(id_s),'expected_state_revision':int_nonneg,'new_state_revision':int_nonneg,
    'record_digests':arr(digest_entry,min_items=1),'projection_ref':ref_s,'projection_sha256':sha_s,
    'authority_decision_ref':ref_s,'status':{'const':'committed'},
},('commit_id','parent_commit_id','expected_state_revision','new_state_revision','record_digests','projection_ref','projection_sha256','authority_decision_ref','status'))

# Trusted outbound task message. It is immutable, schema-valid, digest-bound by the delegated_operation record,
# and carries no authority to mutate FPO Control State.
dispatch_packet=obj({
    '$schema':s(min_len=1),'schema_name':{'const':'fpo.dispatch_packet'},'schema_version':{'const':'0.2'},
    'message_type':{'const':'dispatch_packet'},'dispatch_id':id_s,'work_id':id_s,
    'logical_intent_id':id_s,'attempt_id':id_s,'plan_unit_id':id_s,'owner_stage':enum('P3','P5'),
    'capability_id':id_s,'capability_revision':s(max_len=64),'binding_ref':ref_s,
    'definition_ref':ref_s,'plan_ref':ref_s,'target_revision_ref':ref_s,'policy_revision':s(max_len=64),
    'objective':s(max_len=20000),'input_refs':arr(ref_s,unique=True),'constraint_refs':arr(ref_s,unique=True),
    'allowed_effect_refs':arr(ref_s,unique=True),'approval_refs':arr(ref_s,unique=True),
    'required_artifact_contracts':arr(s(max_len=4096),unique=True),
    'required_evidence_claim_ids':arr(id_s,unique=True),
    'return_schema':{'const':'fpo.capability_return@0.2'},'deadline':nullable(ts),'created_at':ts,
    'extensions':extensions,
},('schema_name','schema_version','message_type','dispatch_id','work_id','logical_intent_id','attempt_id','plan_unit_id','owner_stage','capability_id','capability_revision','binding_ref','definition_ref','plan_ref','target_revision_ref','policy_revision','objective','input_refs','constraint_refs','allowed_effect_refs','approval_refs','required_artifact_contracts','required_evidence_claim_ids','return_schema','deadline','created_at'))

# Untrusted provider message: deliberately does not permit control-like fields.
capability_return=obj({
    '$schema':s(min_len=1),'schema_name':{'const':'fpo.capability_return'},'schema_version':{'const':'0.2'},
    'message_type':{'const':'capability_return'},'return_id':id_s,'work_id':id_s,
    'logical_intent_id':id_s,'dispatch_id':id_s,'attempt_id':id_s,'remote_operation_id':nullable(id_s),
    'provider_identity':s(max_len=512),'capability_id':id_s,'capability_revision':s(max_len=64),
    'provider_sequence':int_nonneg,'operation_state':operation_state,'partial':{'type':'boolean'},
    'observed_definition_ref':ref_s,'observed_plan_ref':ref_s,'observed_target_revision_ref':ref_s,'observed_policy_revision':s(max_len=64),
    'artifact_refs':arr(ref_s,unique=True),'evidence_candidate_refs':arr(ref_s,unique=True),'effect_update_refs':arr(ref_s,unique=True),
    'diagnostic_facts':arr(s(max_len=10000)),'error_summary':nullable(s(max_len=20000)),'created_at':ts,
    'extensions':extensions,
},('schema_name','schema_version','message_type','return_id','work_id','logical_intent_id','dispatch_id','attempt_id','remote_operation_id','provider_identity','capability_id','capability_revision','provider_sequence','operation_state','partial','observed_definition_ref','observed_plan_ref','observed_target_revision_ref','observed_policy_revision','artifact_refs','evidence_candidate_refs','effect_update_refs','diagnostic_facts','error_summary','created_at'))

record_map={
    'work_state':'payload_work_state','work_control':'payload_work_control','source_request':'payload_source_request',
    'work_admission':'payload_work_admission','work_definition':'payload_work_definition','validation_method':'payload_validation_method',
    'execution_plan':'payload_execution_plan','plan_unit_state':'payload_plan_unit_state','blocker_set':'payload_blocker_set',
    'blocker':'payload_blocker','progress_claim':'payload_progress_claim','delegated_operation':'payload_delegated_operation',
    'evidence':'payload_evidence','criteria_verdict':'payload_criteria_verdict','effect':'payload_effect',
    'capability_entry':'payload_capability_entry','approval':'payload_approval','resource_budget':'payload_resource_budget',
    'artifact_manifest':'payload_artifact_manifest','control_event':'payload_control_event','current_projection':'payload_current_projection',
    'ledger_event':'payload_ledger_event','terminal_settlement':'payload_terminal_settlement','commit':'payload_commit',
}

defs={
    'id':id_s,'ref':ref_s,'sha256':sha_s,'timestamp':ts,'checkpoint':checkpoint,'risk_tier':risk_tier,
    'terminal_disposition':terminal_disp,'operation_state':operation_state,'effect_state':effect_state,
    'blocker_status':blocker_status,'evidence_status':evidence_status,'unit_state':unit_state,
    'criterion_verdict':criterion_verdict,'actor':actor,'record_envelope':record_envelope,'dispatch_packet':dispatch_packet,'capability_return':capability_return,
}
defs.update(payloads)
for name,payload in record_map.items(): defs[name]=variant(name,payload)

# Cross-field invariants that are safe to enforce at the individual-record layer.
def payload_rule(if_props, then_props, *, then_required=(), else_props=None, else_required=()):
    rule={
        'if': {'properties': {'payload': {'properties': if_props, 'required': list(if_props)}}},
        'then': {'properties': {'payload': {'properties': then_props}}},
    }
    if then_required:
        rule['then']['properties']['payload']['required']=list(then_required)
    if else_props is not None:
        rule['else']={'properties': {'payload': {'properties': else_props}}}
        if else_required:
            rule['else']['properties']['payload']['required']=list(else_required)
    return rule

def add_rule(record_name, rule):
    defs[record_name]['allOf'].append(rule)

# Achievement and Work Control consistency.
add_rule('work_state', payload_rule(
    {'checkpoint': {'const':'closed'}},
    {'interrupt_ref': {'type':'null'}},
))
add_rule('work_control', payload_rule(
    {'lifecycle_state': {'enum':['terminated','archived']}},
    {'terminal_disposition': terminal_disp},
))
add_rule('work_control', payload_rule(
    {'lifecycle_state': {'enum':['active','suspended','canceling']}},
    {'terminal_disposition': {'type':'null'}},
))
add_rule('work_control', payload_rule(
    {'lifecycle_state': {'const':'suspended'}},
    {
      'resume_condition_ref': ref_s,
      'resume_owner': s(max_len=128),
      'resume_expiry': ts,
      'resume_default_action': s(max_len=256),
    },
    then_required=('resume_condition_ref','resume_owner','resume_expiry','resume_default_action'),
))
add_rule('work_control', payload_rule(
    {'lifecycle_state': {'enum':['active','canceling','terminated','archived']}},
    {
      'resume_condition_ref': {'type':'null'},
      'resume_owner': {'type':'null'},
      'resume_expiry': {'type':'null'},
      'resume_default_action': {'type':'null'},
    },
))

# Admission and Blocker lifecycle consistency.
add_rule('work_admission', payload_rule(
    {'admissible': {'const':True}},
    {
      'finite': {'const':True}, 'criteria_identifiable': {'const':True},
      'effects_bounded': {'const':True}, 'observable': {'const':True},
      'single_checkpoint_meaningful': {'const':True}, 'context_retrievable': {'const':True},
      'capability_feasible': {'const':True}, 'risk_tier': {'enum':['T0','T1','T2']},
    },
))
add_rule('blocker', payload_rule(
    {'status': {'const':'waiting'}},
    {
      'resume_condition_ref': ref_s,
      'resume_owner': s(max_len=128),
      'resume_expiry': ts,
      'resume_default_action': s(max_len=256),
    },
    then_required=('resume_condition_ref','resume_owner','resume_expiry','resume_default_action'),
))
add_rule('blocker', payload_rule(
    {'status': {'const':'resolved'}},
    {'resolution_evidence_refs': {'type':'array','minItems':1}},
))

# Delegated Return binding and wait/unknown metadata.
add_rule('delegated_operation', payload_rule(
    {'return_ref': {'type':'null'}},
    {'return_sha256': {'type':'null'}},
    else_props={'return_sha256': sha_s},
    else_required=('return_sha256',),
))
add_rule('delegated_operation', payload_rule(
    {'state': {'const':'waiting_input'}},
    {'input_request_ref': ref_s}, then_required=('input_request_ref',),
))
add_rule('delegated_operation', payload_rule(
    {'state': {'const':'waiting_authorization'}},
    {'auth_request_ref': ref_s}, then_required=('auth_request_ref',),
))
add_rule('delegated_operation', payload_rule(
    {'state': {'const':'unknown'}},
    {'error_summary': s(max_len=20000)}, then_required=('error_summary',),
))

# Evidence / Verdict machine guards.
add_rule('evidence', payload_rule(
    {'status': {'const':'valid'}},
    {'adopted_by': {'type':'string','enum':['P4','P5']}}, then_required=('adopted_by',),
))
add_rule('criteria_verdict', payload_rule(
    {'verdict': {'const':'PASS'}},
    {
      'evidence_refs': {'type':'array','minItems':1},
      'coverage_complete': {'const':True},
      'freshness_ok': {'const':True},
      'conflict_status': {'const':'none'},
      'independence_satisfied': {'const':True},
    },
))

# Effect recovery preconditions.
add_rule('effect', payload_rule(
    {'effect_class': {'const':'idempotent'}},
    {'idempotency_key': s(max_len=512)}, then_required=('idempotency_key',),
))
add_rule('effect', payload_rule(
    {'effect_class': {'const':'compensatable'}},
    {'compensation_plan_ref': ref_s}, then_required=('compensation_plan_ref',),
))
add_rule('effect', payload_rule(
    {'effect_class': {'enum':['pivot','irreversible']}},
    {'forward_recovery_plan_ref': ref_s}, then_required=('forward_recovery_plan_ref',),
))
add_rule('effect', payload_rule(
    {'effect_class': {'const':'irreversible'}},
    {'approval_ref': ref_s}, then_required=('approval_ref',),
))
add_rule('effect', payload_rule(
    {'state': {'const':'confirmed'}},
    {
      'target_revision_after': s(max_len=256),
      'outcome_evidence_refs': {'type':'array','minItems':1},
    },
    then_required=('target_revision_after','outcome_evidence_refs'),
))
add_rule('effect', payload_rule(
    {'state': {'const':'unknown'}},
    {'failure_summary': s(max_len=20000)}, then_required=('failure_summary',),
))

# Approval and terminal settlement consistency.
add_rule('approval', payload_rule(
    {'status': {'const':'revoked'}},
    {'revocation_ref': ref_s}, then_required=('revocation_ref',),
))
add_rule('terminal_settlement', payload_rule(
    {'disposition': {'const':'completed'}},
    {
      'achievement_checkpoint': {'const':'closed'},
      'criteria_verdict_refs': {'type':'array','minItems':1},
      'open_blocker_refs': {'type':'array','maxItems':0},
      'inflight_operation_refs': {'type':'array','maxItems':0},
      'unsettled_effect_refs': {'type':'array','maxItems':0},
    },
))
add_rule('terminal_settlement', payload_rule(
    {'disposition': {'enum':['canceled','aborted','unsatisfiable','out_of_budget','safety_stop','out_of_scope']}},
    {'achievement_checkpoint': {'enum':['none','defined','designed','executed','accepted']}},
))

schema={
    '$schema':'https://json-schema.org/draft/2020-12/schema',
    '$id':'urn:fpo:v0.2:fpo-records',
    'title':'Fluid Progress Orchestration v0.2 Records and Boundary Messages',
    'description':'Machine-authoritative immutable records, trusted outbound dispatch packets, and untrusted capability return messages for the FPO v0.2 Architectural Hardening Candidate.',
    'oneOf':[ref(name) for name in record_map] + [ref('dispatch_packet'), ref('capability_return')],
    '$defs':defs,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(OUT, 'written', len(OUT.read_text(encoding='utf-8').splitlines()), 'lines', len(record_map), 'record types')
