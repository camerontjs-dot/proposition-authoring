"""One-shot complete-contract annotation diagnostic; no semantic authority."""
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


def main() -> None:
    stage = pathlib.Path(__file__).resolve().parent
    out = pathlib.Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    freeze = json.loads((stage / 'INPUT-FREEZE.json').read_text())
    for name, digest in freeze['sha256'].items():
        if sha((stage / name).read_bytes()) != digest:
            raise RuntimeError(f'frozen input drift: {name}')
    config = json.loads((stage / 'CONFIG.json').read_text())
    schema = json.loads((stage / 'SCHEMA.json').read_text())
    rows = [json.loads(line) for line in (stage / 'controls.jsonl').read_text().splitlines()]
    expected = json.loads((stage / 'CONTROL-EXPECTATIONS.json').read_text())['classes']
    prompt_template = (stage / 'PROMPT.txt').read_text()
    with urllib.request.urlopen(config['provider_base_url'] + '/api/version', timeout=15) as response:
        version = json.load(response)['version']
    with urllib.request.urlopen(config['provider_base_url'] + '/api/tags', timeout=15) as response:
        tags = json.load(response)['models']
    if version != config['runtime_version']:
        raise RuntimeError('provider version drift')
    receipt = {'schema':'s0-contract-closure-execution-r4', 'subject_commit':subprocess.check_output(['git', '-C', str(stage), 'rev-parse', 'HEAD'], text=True).strip(),
               'input_freeze_sha256':sha((stage / 'INPUT-FREEZE.json').read_bytes()), 'runtime_version':version, 'models':config['models'], 'calls':[], 'guaranteed_determinism':False}
    for model in config['models']:
        if next(m for m in tags if m['name'] == model['name'])['digest'] != model['digest']:
            raise RuntimeError('model drift')
        model_dir = out / model['name'].replace(':', '-')
        model_dir.mkdir()
        for row in rows:
            prompt = prompt_template.replace('{{CASE_JSON}}', json.dumps({k:row[k] for k in ('id', 'root', 'authorized_context')}, sort_keys=True, ensure_ascii=False)).replace('{{SCHEMA_JSON}}', json.dumps(schema, sort_keys=True, ensure_ascii=False))
            request = {'model':model['name'], 'prompt':prompt, 'format':schema, 'stream':False, 'keep_alive':config['keep_alive'], 'options':config['options']}
            if 'thinking' in model['capabilities']:
                request['think'] = config['think']
            request_bytes = json.dumps(request, sort_keys=True, ensure_ascii=False).encode()
            (model_dir / f"{row['id']}.request.json").write_bytes(request_bytes)
            cell = {'id':row['id'], 'model':model['name'], 'expected_class':expected[row['id']], 'status':'FAILED', 'request_sha256':sha(request_bytes)}
            start = time.monotonic()
            try:
                http_request = urllib.request.Request(config['provider_base_url'] + '/api/generate', request_bytes, {'Content-Type':'application/json'})
                with urllib.request.urlopen(http_request, timeout=config['timeout_seconds']) as response:
                    response_bytes = response.read()
                (model_dir / f"{row['id']}.response.json").write_bytes(response_bytes)
                cell['response_sha256'] = sha(response_bytes)
                raw = json.loads(response_bytes)
                annotation = json.loads(raw['response'])
                jsonschema.validate(annotation, schema)
                if annotation['id'] != row['id'] or not raw.get('done') or raw.get('done_reason') == 'length':
                    raise ValueError('wrong identity or incomplete/truncated completion')
                errors = []
                if annotation['class'] == 'AMBIGUOUS' and (not annotation['first_reading'].strip() or not annotation['second_reading'].strip() or annotation['first_reading'].strip() == annotation['second_reading'].strip()):
                    errors.append('AMBIGUITY_WITHOUT_TWO_DISTINCT_READINGS')
                if annotation['class'] != 'AMBIGUOUS' and annotation['second_reading'].strip():
                    errors.append('UNSELECTED_ALTERNATIVE_IN_NONAMBIGUOUS_CLASS')
                if not annotation['first_reading'].strip():
                    errors.append('MISSING_CONTENT_BASIS')
                annotation_bytes = (json.dumps(annotation, sort_keys=True, ensure_ascii=False) + '\n').encode()
                (model_dir / f"{row['id']}.annotation.json").write_bytes(annotation_bytes)
                cell.update(status='VALID_OUTPUT', judged_class=annotation['class'], class_correct=annotation['class'] == cell['expected_class'], consistency_errors=errors, annotation_sha256=sha(annotation_bytes))
            except Exception as error:
                if isinstance(error, urllib.error.HTTPError):
                    (model_dir / f"{row['id']}.http-error.bin").write_bytes(error.read())
                cell.update(error_type=type(error).__name__, error=str(error))
            cell['elapsed_seconds'] = round(time.monotonic() - start, 3)
            receipt['calls'].append(cell)
            (model_dir / f"{row['id']}.receipt.json").write_text(json.dumps(cell, indent=2, sort_keys=True) + '\n')
            print(json.dumps({key:cell.get(key) for key in ('model', 'id', 'status', 'judged_class', 'class_correct', 'consistency_errors', 'elapsed_seconds')}), flush=True)
    receipt['artifact_sha256'] = {str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    (out / 'EXECUTION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
