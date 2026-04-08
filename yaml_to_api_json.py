#!/usr/bin/env python3
"""Convert palo_alto_log_generator.yaml → palo_alto_log_generator_api.json

Reads the workflow YAML source of truth and produces the flat API JSON
that can be deployed via `dtctl apply -f`.
"""
import json
import yaml
import sys
import os

def convert(yaml_path, json_path):
    with open(yaml_path, 'r') as f:
        doc = yaml.safe_load(f)

    wf = doc['workflow']

    api = {
        'title': wf['title'],
        'description': wf['description'].strip(),
        'schemaVersion': doc.get('workflow', {}).get('schemaVersion', 3),
        'isPrivate': False,
        'triggerType': 'Scheduler',
        'trigger': wf['trigger'],
        'tasks': {},
    }

    # If schemaVersion is at top-level of workflow section
    if 'schemaVersion' in wf:
        api['schemaVersion'] = wf['schemaVersion']
    else:
        api['schemaVersion'] = 3

    for task_name, task in wf['tasks'].items():
        api_task = {
            'name': task['name'],
            'description': task.get('description', '').strip(),
            'action': task['action'],
            'input': task['input'],
            'position': task['position'],
            'predecessors': task.get('predecessors', []),
        }
        if 'conditions' in task:
            api_task['conditions'] = task['conditions']
        api['tasks'][task_name] = api_task

    with open(json_path, 'w', newline='\n') as f:
        json.dump(api, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f'Wrote {json_path}')

if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    yaml_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base, 'network-security', 'palo-alto', 'workflows',
        'palo_alto_log_generator.yaml')
    json_path = sys.argv[2] if len(sys.argv) > 2 else yaml_path.replace('.yaml', '_api.json')
    convert(yaml_path, json_path)
