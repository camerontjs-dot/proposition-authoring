"""Report physically cached review measurements; never fabricate missing cells."""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import sys


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inconsistent(row: dict) -> list[str]:
    errors = []
    state = row['class']
    if state == 'AMBIGUOUS' and (len(row['alternatives']) < 2 or row['children']):
        errors.append('AMBIGUITY_WITHOUT_TWO_UNSELECTED_READINGS')
    if state == 'ATOMIC' and len(row['children']) != 1:
        errors.append('ATOMIC_WITHOUT_ONE_COMPLETE_CHILD')
    if state == 'ALL_OF' and len(row['children']) < 2:
        errors.append('ALL_OF_WITHOUT_TWO_CHILDREN')
    if row['unresolved'] != (state == 'UNRESOLVED_REVIEW'):
        errors.append('UNRESOLVED_FLAG_MISMATCH')
    return errors


def main() -> None:
    root = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[2]).resolve()
    r2_stage = root / 'research-repo/research/claim_structure_vnext_s0_r2_20261002'
    expected = json.loads((r2_stage / 'CONTROL-EXPECTATIONS.json').read_text())['classes']
    input_rows = {r['id']: r for r in map(json.loads, (r2_stage / 'targeted.jsonl').read_text().splitlines())}
    r2 = root / 's0-r2-execution'
    r3 = root / 's0-r3-execution'
    if not (r2 / 'EXECUTION.json').is_file() or not (r3 / 'EXECUTION.json').is_file():
        raise RuntimeError('execution incomplete; do not emit a terminal summary')
    result = {'schema': 's0-review-measurement-summary', 'r2': [], 'r3': [],
              'public_semantic_accuracy': 'NOT_MEASURED_NO_QUALIFIED_GOLD',
              'proposer_or_shadow_authority_metrics': 'NOT_RUN',
              'basis': 'Physical raw request/response cache. Constructed-control class expectations were frozen before inference. Class correctness does not establish content correctness.'}
    for model in sorted(r2.iterdir()):
        if not model.is_dir():
            continue
        measurements = []
        for case_id, source in input_rows.items():
            annotation = model / f'{case_id}.annotation.json'
            call_receipt = model / f'{case_id}.receipt.json'
            if not call_receipt.is_file():
                measurements.append({'id': case_id, 'status': 'NOT_RUN', 'group': source['provenance']})
                continue
            status = json.loads(call_receipt.read_text())['status']
            row = {'id': case_id, 'status': status, 'group': source['provenance']}
            if annotation.is_file():
                data = json.loads(annotation.read_text())
                row.update(judged_class=data['class'], consistency_errors=inconsistent(data), annotation_sha256=sha(annotation))
                if case_id in expected:
                    row.update(expected_class=expected[case_id], class_correct=data['class'] == expected[case_id])
            measurements.append(row)
        replay = []
        for cid in ['R01', 'C03']:
            original = model / f'{cid}.annotation.json'
            repeat = model / f'{cid}-replay.annotation.json'
            replay.append({'id':cid, 'status':'MEASURED' if original.is_file() and repeat.is_file() else 'FAILED_OR_NOT_RUN', 'canonical_annotation_identical':sha(original) == sha(repeat) if original.is_file() and repeat.is_file() else None})
        by_class = {}
        for state in ['ATOMIC', 'ALL_OF', 'AMBIGUOUS', 'NON_ALL_OF']:
            cells = [r for r in measurements if r.get('expected_class') == state]
            by_class[state] = {'class_correct':sum(r.get('class_correct', False) for r in cells) if cells else None, 'valid_outputs':len(cells), 'planned_controls':sum(v == state for v in expected.values())}
        result['r2'].append({'model':model.name, 'rows':measurements, 'control_results_by_expected_class':by_class,
                             'judged_class_counts_by_group':{group:dict(collections.Counter(r['judged_class'] for r in measurements if r['group'] == group and 'judged_class' in r)) for group in ['public_pre_existing', 'public_replay_anchor', 'synthetic_adversarial_control']},
                             'control_class_correct':sum(r.get('class_correct', False) for r in measurements) if any('class_correct' in r for r in measurements) else None, 'planned_controls':len(expected),
                             'internal_consistency_failures':sum(bool(r.get('consistency_errors')) for r in measurements),
                             'replay':replay})
    execution = json.loads((r3 / 'EXECUTION.json').read_text())
    for model in sorted({r['model'] for r in execution['cells']}):
        for format_name in ['original_schema', 'json_only', 'reversed_class_enum']:
            cells = [r for r in execution['cells'] if r['model'] == model and r['format'] == format_name]
            result['r3'].append({'model':model, 'format':format_name, 'cells':cells,
                                 'class_correct':sum(r.get('class_correct', False) for r in cells) if any(r['status'] == 'VALID_OUTPUT' for r in cells) else None, 'planned_controls':3,
                                 'valid_outputs':sum(r['status'] == 'VALID_OUTPUT' for r in cells),
                                 'internal_consistency_failures':sum(bool(r.get('consistency_errors')) for r in cells)})
    changes = []
    for model in sorted({r['model'] for r in execution['cells']}):
        for cid in ['C01', 'C03', 'C04']:
            cells = {r['format']:r for r in execution['cells'] if r['model'] == model and r['id'] == cid}
            base = cells.get('original_schema', {}).get('judged_class')
            for format_name in ['json_only', 'reversed_class_enum']:
                altered = cells.get(format_name, {}).get('judged_class')
                changes.append({'model':model, 'id':cid, 'altered_format':format_name, 'original_class':base, 'altered_class':altered, 'class_changed':base != altered if base is not None and altered is not None else None})
    result['format_class_changes'] = changes
    for stage_id in ['r4', 'r5']:
        directory = root / f's0-{stage_id}-execution'
        executed = json.loads((directory / 'EXECUTION.json').read_text())
        summaries = []
        for model in sorted({r['model'] for r in executed['calls']}):
            calls = [r for r in executed['calls'] if r['model'] == model]
            valid = [r for r in calls if r['status'] == 'VALID_OUTPUT']
            summary = {'model':model, 'valid_outputs':len(valid), 'planned_controls':4 if stage_id == 'r4' else 2, 'calls':calls}
            if stage_id == 'r4':
                summary['class_correct'] = sum(r['class_correct'] for r in valid) if valid else None
                summary['per_expected_class'] = {r['expected_class']:{'class_correct':r['class_correct'], 'id':r['id']} for r in valid}
            else:
                summary['typed_component_match'] = sum(r['witness_correct'] for r in valid) if valid else None
                summary['semantic_qualification'] = 'NOT_ESTABLISHED_BY_COMPONENT_MATCH'
            summaries.append(summary)
        result[stage_id] = summaries
    result['artifact_identities'] = {'r2_execution_sha256':sha(r2 / 'EXECUTION.json'), 'r3_execution_sha256':sha(r3 / 'EXECUTION.json'), 'r4_execution_sha256':sha(root / 's0-r4-execution/EXECUTION.json'), 'r5_execution_sha256':sha(root / 's0-r5-execution/EXECUTION.json'),
                                     'r2_corpus_sha256':sha(r2_stage / 'targeted.jsonl'),
                                     'r2_prompt_sha256':sha(r2_stage / 'PROMPT.txt'), 'r2_config_sha256':sha(r2_stage / 'CONFIG.json'),
                                     'r3_prompt_sha256':sha(root / 'research-repo/research/claim_structure_vnext_s0_r3_20261002/PROMPT.txt'),
                                     'r3_config_sha256':sha(root / 'research-repo/research/claim_structure_vnext_s0_r3_20261002/CONFIG.json')}
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'r2':[{'model':r['model'], 'class_correct':r['control_class_correct'], 'controls':r['planned_controls'], 'consistency_failures':r['internal_consistency_failures'], 'replay':r['replay']} for r in result['r2']],
                      'r3':[{k:r[k] for k in ('model', 'format', 'class_correct', 'planned_controls', 'valid_outputs', 'internal_consistency_failures')} for r in result['r3']],
                      'format_class_changes':changes}, indent=2))


if __name__ == '__main__':
    main()
