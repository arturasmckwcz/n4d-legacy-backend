From rootdirectory of the project execute
```
source .venv/bin/activate
docker exec alfred python3 manage.py seed_data
PYTEST_DISABLE_PLUGIN_AUTOLOAD=True ALFRED_API_URL=http://localhost:8000 python3 -m pytest tests_e2e/
```
