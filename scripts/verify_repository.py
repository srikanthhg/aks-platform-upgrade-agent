from __future__ import annotations
import ast,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];REQUIRED=['backend/main.py','backend/worker.py','backend/Dockerfile','backend/tests','frontend/package.json','frontend/Dockerfile','infra/main.bicep','.github/workflows/ci.yml','docker-compose.yml','README.md'];errors=[]
for relative in REQUIRED:
    if not (ROOT/relative).exists():errors.append(f'Missing required path: {relative}')
for path in (ROOT/'backend').rglob('*.py'):
    try:ast.parse(path.read_text(),filename=str(path))
    except SyntaxError as exc:errors.append(str(exc))
if errors:print('\n'.join(errors));sys.exit(1)
print('Repository verification passed.')
