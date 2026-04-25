# README

- For Dev Mode
```bash
fastapi dev app/main.py
```
- for production Mode
```bash
fastapi run app/main.py
```


```bash
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```