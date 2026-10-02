"""Execute the frozen cold-review protocol once; preserve failures without retry."""
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


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.load(response)


def main() -> None:
    stage = pathlib.Path(__file__).resolve().parent
    out = pathlib.Path(sys.argv[1]).resolve()
    # A run is an immutable one-shot directory. Existing partial runs are evidence.
    out.mkdir(parents=True, exist_ok=False)
    inventory = json.loads((stage / 'INPUT-FREEZE.json').read_text())
    for name, digest in inventory['sha256'].items():
        if sha((stage / name).read_bytes()) != digest:
            raise RuntimeError(f'frozen input drift: {name}')
    subject = subprocess.check_output(['git', '-C', str(stage), 'rev-parse', 'HEAD'], text=True).strip()
    config = json.loads((stage / 'CONFIG.json').read_text())
    schema = json.loads((stage / 'SCHEMA.json').read_text())
    inputs = [json.loads(line) for line in (stage / 'targeted.jsonl').read_text().splitlines()]
    prompt_template = (stage / 'PROMPT.txt').read_text()
    rule = (stage / 'ANNOTATION.md').read_text()
    runtime = get_json('http://127.0.0.1:11434/api/version')
    tags = get_json('http://127.0.0.1:11434/api/tags')['models']
    if runtime['version'] != config['runtime_version']:
        raise RuntimeError('provider version drift')
    for model in config['models']:
        current = next(row for row in tags if row['name'] == model['name'])
        if current['digest'] != model['digest']:
            raise RuntimeError('model identity drift')
    receipt = {'schema': 's0-cold-review-execution-r2', 'subject_commit': subject,
               'input_freeze_sha256': sha((stage / 'INPUT-FREEZE.json').read_bytes()),
               'provider': 'local_ollama', 'runtime': runtime, 'models': config['models'],
               'guaranteed_determinism': False, 'calls': [], 'failures': []}
    (out / 'preflight.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    for model in config['models']:
        model_dir = out / model['name'].replace(':', '-')
        model_dir.mkdir()
        sequence = [(row, False) for row in inputs]
        sequence += [(row, True) for row in inputs if row['id'] in config['replay_ids']]
        for row, replay in sequence:
            call_id = row['id'] + ('-replay' if replay else '')
            case = {key: row[key] for key in ('id', 'root', 'authorized_context')}
            prompt = prompt_template.replace('{{ANNOTATION}}', rule).replace('{{CASE_JSON}}', json.dumps(case, ensure_ascii=False, sort_keys=True))
            request = {'model': model['name'], 'prompt': prompt, 'format': schema,
                       'stream': False, 'keep_alive': config['keep_alive'],
                       'options': config['options']}
            if 'thinking' in model['capabilities']:
                request['think'] = config['think']
            request_bytes = json.dumps(request, sort_keys=True, ensure_ascii=False).encode()
            (model_dir / f'{call_id}.request.json').write_bytes(request_bytes)
            record = {'id': row['id'], 'replay': replay, 'model': model['name'],
                      'request_sha256': sha(request_bytes), 'status': 'FAILED'}
            start = time.monotonic()
            try:
                http_request = urllib.request.Request('http://127.0.0.1:11434/api/generate', request_bytes, {'Content-Type': 'application/json'})
                with urllib.request.urlopen(http_request, timeout=config['timeout_seconds']) as response:
                    response_bytes = response.read()
                (model_dir / f'{call_id}.response.json').write_bytes(response_bytes)
                record['raw_response_sha256'] = sha(response_bytes)
                response_data = json.loads(response_bytes)
                record['done_reason'] = response_data.get('done_reason')
                annotation = json.loads(response_data['response'])
                jsonschema.validate(annotation, schema)
                if annotation['id'] != row['id'] or not response_data.get('done') or response_data.get('done_reason') == 'length':
                    raise ValueError('wrong row, incomplete or truncated response')
                annotation_bytes = (json.dumps(annotation, sort_keys=True, ensure_ascii=False) + '\n').encode()
                (model_dir / f'{call_id}.annotation.json').write_bytes(annotation_bytes)
                record['annotation_sha256'] = sha(annotation_bytes)
                record['response_content_sha256'] = sha(response_data['response'].encode())
                record['class'] = annotation['class']
                record['status'] = 'VALID_OUTPUT'
            except Exception as error:
                if isinstance(error, urllib.error.HTTPError):
                    (model_dir / f'{call_id}.http-error.bin').write_bytes(error.read())
                record['error_type'] = type(error).__name__
                record['error'] = str(error)
                receipt['failures'].append({'model': model['name'], 'call': call_id, 'error_type': type(error).__name__})
            record['elapsed_seconds'] = round(time.monotonic() - start, 3)
            receipt['calls'].append(record)
            (model_dir / f'{call_id}.receipt.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
            print(json.dumps({key: record.get(key) for key in ('model', 'id', 'replay', 'status', 'class', 'elapsed_seconds')}), flush=True)
    receipt['artifact_sha256'] = {str(path.relative_to(out)): sha(path.read_bytes()) for path in sorted(out.rglob('*')) if path.is_file()}
    (out / 'EXECUTION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
