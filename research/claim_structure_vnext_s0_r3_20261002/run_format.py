"""Frozen format-only diagnostic; do not repair or retry any cell."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

import jsonschema


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def consistency(row: dict) -> list[str]:
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
    stage = pathlib.Path(__file__).resolve().parent
    baseline = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    freeze = json.loads((stage / 'INPUT-FREEZE.json').read_text())
    for name, digest in freeze['sha256'].items():
        if sha((stage / name).read_bytes()) != digest:
            raise RuntimeError(f'frozen drift: {name}')
    if not (baseline / 'EXECUTION.json').is_file():
        raise RuntimeError('predecessor execution incomplete')
    original = json.loads((stage / 'SCHEMA.json').read_text())
    reversed_schema = json.loads((stage / 'SCHEMA-REVERSED.json').read_text())
    config = json.loads((stage / 'CONFIG.json').read_text())
    controls = [json.loads(line) for line in (stage / 'controls.jsonl').read_text().splitlines()]
    expected = json.loads((stage / 'CONTROL-EXPECTATIONS.json').read_text())['classes']
    receipt = {'schema': 's0-format-diagnostic-r3',
               'subject_commit': subprocess.check_output(['git', '-C', str(stage), 'rev-parse', 'HEAD'], text=True).strip(),
               'input_freeze_sha256': sha((stage / 'INPUT-FREEZE.json').read_bytes()),
               'predecessor_execution_sha256': sha((baseline / 'EXECUTION.json').read_bytes()),
               'cells': [], 'guaranteed_determinism': False}
    with urllib.request.urlopen('http://127.0.0.1:11434/api/version', timeout=15) as response:
        version = json.load(response)['version']
    with urllib.request.urlopen('http://127.0.0.1:11434/api/tags', timeout=15) as response:
        tags = json.load(response)['models']
    if version != config['runtime_version']:
        raise RuntimeError('runtime drift')
    for model in config['models']:
        if next(m for m in tags if m['name'] == model['name'])['digest'] != model['digest']:
            raise RuntimeError('model drift')
        label = model['name'].replace(':', '-')
        model_out = out / label
        model_out.mkdir()
        for case in controls:
            base_request = (baseline / label / f"{case['id']}.request.json").read_bytes()
            base_response_path = baseline / label / f"{case['id']}.response.json"
            if not base_response_path.is_file():
                receipt['cells'].append({'model': model['name'], 'id': case['id'], 'format': 'original_schema', 'status': 'FAILED_PREDECESSOR'})
                continue
            response_bytes = base_response_path.read_bytes()
            request = json.loads(base_request)
            # Reconstruct the expected envelope independently, before using baseline bytes.
            prompt = (stage / 'PROMPT.txt').read_text().replace('{{ANNOTATION}}', (stage / 'ANNOTATION.md').read_text()).replace('{{CASE_JSON}}', json.dumps({k:case[k] for k in ('id', 'root', 'authorized_context')}, sort_keys=True, ensure_ascii=False))
            if request['prompt'] != prompt or request['options'] != config['options'] or request['format'] != original:
                raise RuntimeError('baseline request does not match frozen diagnostic')
            for format_name, response_format in [('original_schema', original), ('json_only', 'json'), ('reversed_class_enum', reversed_schema)]:
                cell = {'model': model['name'], 'id': case['id'], 'format': format_name, 'expected_class': expected[case['id']], 'status': 'FAILED'}
                cell_id = f"{case['id']}-{format_name}"
                start = time.monotonic()
                request['format'] = response_format
                request_bytes = json.dumps(request, sort_keys=True, ensure_ascii=False).encode()
                (model_out / f'{cell_id}.request.json').write_bytes(request_bytes)
                cell['request_sha256'] = sha(request_bytes)
                try:
                    if format_name != 'original_schema':
                        http_request = urllib.request.Request('http://127.0.0.1:11434/api/generate', request_bytes, {'Content-Type': 'application/json'})
                        with urllib.request.urlopen(http_request, timeout=config['timeout_seconds']) as response:
                            response_bytes = response.read()
                    (model_out / f'{cell_id}.response.json').write_bytes(response_bytes)
                    cell['response_sha256'] = sha(response_bytes)
                    raw = json.loads(response_bytes)
                    row = json.loads(raw['response'])
                    jsonschema.validate(row, original)
                    if row['id'] != case['id'] or not raw.get('done') or raw.get('done_reason') == 'length':
                        raise ValueError('wrong row or incomplete output')
                    annotation_bytes = (json.dumps(row, sort_keys=True, ensure_ascii=False) + '\n').encode()
                    (model_out / f'{cell_id}.annotation.json').write_bytes(annotation_bytes)
                    cell.update(status='VALID_OUTPUT', judged_class=row['class'], class_correct=row['class'] == expected[case['id']], consistency_errors=consistency(row), annotation_sha256=sha(annotation_bytes))
                except Exception as error:
                    if isinstance(error, urllib.error.HTTPError):
                        (model_out / f'{cell_id}.http-error.bin').write_bytes(error.read())
                    cell.update(error_type=type(error).__name__, error=str(error))
                cell['elapsed_seconds'] = round(time.monotonic() - start, 3)
                receipt['cells'].append(cell)
                (model_out / f'{cell_id}.receipt.json').write_text(json.dumps(cell, indent=2, sort_keys=True) + '\n')
                print(json.dumps({key:cell.get(key) for key in ('model', 'id', 'format', 'status', 'judged_class', 'class_correct', 'consistency_errors', 'elapsed_seconds')}), flush=True)
    receipt['artifact_sha256'] = {str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    (out / 'EXECUTION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
