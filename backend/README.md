```bash
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```


```bash
fastapi dev app/main.py
```