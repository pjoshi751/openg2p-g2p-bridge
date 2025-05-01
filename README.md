## Run Bridge server

```
> cd openg2p-g2p-bridge-api
> gunicorn "main:app" --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```
