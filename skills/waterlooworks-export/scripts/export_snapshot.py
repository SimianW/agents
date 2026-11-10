#!/usr/bin/env python3
"""Validate a complete browser capture and export three dated WaterlooWorks JSON files."""
import argparse
import json
import re
from pathlib import Path

ROW_KEYS = ('id', 'title', 'company', 'division', 'openings', 'city', 'level', 'apps', 'deadline', 'applied')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def indexed(records, label):
    require(isinstance(records, list), f'{label} must be an array')
    result = {}
    for record in records:
        require(isinstance(record, dict), f'{label}: record must be an object')
        require(all(k in record for k in ROW_KEYS), f'{label}: missing row fields')
        identifier = record['id']
        require(isinstance(identifier, str) and identifier.isdigit(), f'{label}: invalid string ID')
        require(identifier not in result, f'{label}: duplicate ID {identifier}')
        require(all(isinstance(record[k], str) for k in ROW_KEYS if k != 'applied'), f'{identifier}: row values must be strings')
        require(record['applied'] is None or type(record['applied']) is bool, f'{identifier}: invalid applied status')
        result[identifier] = record
    return result

def export(bundle, output_dir, stem, previous=None):
    require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', stem), 'Invalid output stem')
    count = bundle.get('expected')
    require(type(count) is int and count >= 0, 'expected must be a nonnegative integer')
    for key in ('startedAt', 'completedAt', 'sourceUrl', 'filters', 'timezone'):
        require(bool(bundle.get(key)), f'Missing capture metadata: {key}')
    rows = indexed(bundle.get('rows'), 'rows')
    details = indexed(bundle.get('details'), 'details')
    require(len(rows) == len(details) == count, 'Incomplete capture: count mismatch')
    require(rows.keys() == details.keys(), 'Row/detail ID sets differ')
    for identifier, record in details.items():
        require(all(record[k] == rows[identifier][k] for k in ROW_KEYS), f'{identifier}: row/detail mismatch')
        text = record.get('detail')
        require(isinstance(text, str) and re.search(r'\b' + re.escape(identifier) + r'\b', text), f'{identifier}: missing matching detail ID')
        require('JOB POSTING INFORMATION' in text and 'APPLICATION INFORMATION' in text, f'{identifier}: incomplete detail sections')
        require(isinstance(record.get('capturedAt'), str) and record['capturedAt'], f'{identifier}: missing capturedAt')
        require('pre' in record and (record['pre'] is None or type(record['pre']) is bool), f'{identifier}: invalid pre')
        links = record.get('links')
        require(isinstance(links, list) and all(isinstance(x, dict) and isinstance(x.get('href'), str) and isinstance(x.get('text'), str) for x in links), f'{identifier}: invalid links')
    if bundle.get('initialExpected', count) != count:
        require(bool(bundle.get('reconciliation')), 'Changed scope requires a reconciliation explanation')
    meta = {k: v for k, v in bundle.items() if k not in ('rows', 'details')}
    meta.update(count=count, unique_ids=len(details), method='Opened each job detail in authenticated browser UI',
                counts_note='List counts are per-page snapshots, not a simultaneous or external ATS count.',
                prescreening_note='pre records tab presence; questions were not necessarily captured.')
    if previous is not None:
        old = indexed(previous, 'previous')
        meta.update(new_ids=sorted(details.keys() - old.keys()),
                    no_longer_in_current_results=sorted(old.keys() - details.keys()),
                    application_count_changed=sum(details[k]['apps'] != old[k]['apps'] for k in details.keys() & old.keys()))
    output_dir = Path(output_dir)
    paths = [output_dir / f'{stem}-{kind}.json' for kind in ('source', 'rows', 'metadata')]
    require(not any(p.exists() for p in paths), 'Output already exists; choose a timestamped stem')
    payloads = [json.dumps(x, ensure_ascii=False, indent=2) + '\n' for x in (bundle['details'], bundle['rows'], meta)]
    output_dir.mkdir(parents=True, exist_ok=True)
    for path, payload in zip(paths, payloads):
        with path.open('x', encoding='utf-8') as handle:
            handle.write(payload)
    return paths

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('research'))
    parser.add_argument('--stem', required=True, help='For example waterlooworks-2026-09-20')
    parser.add_argument('--previous', type=Path)
    args = parser.parse_args()
    try:
        bundle = json.loads(args.capture.read_text(encoding='utf-8'))
        previous = json.loads(args.previous.read_text(encoding='utf-8')) if args.previous else None
        for path in export(bundle, args.output_dir, args.stem, previous):
            print(path)
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(1, f'Export failed: {exc}\n')

if __name__ == '__main__':
    main()
