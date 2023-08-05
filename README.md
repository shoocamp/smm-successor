# SMM Successor

## How to run

1. Copy `config.example.toml` to `config.toml`
2. Update `config.toml`
3. Run `mongodb`
    ```bash
    docker run -d --name local-mongo \
        -p 27017:27017 \
        -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
        -e MONGO_INITDB_ROOT_PASSWORD=secret \
        mongo
    ```
4. Run redis
   ```bash
   docker run -d -p 6379:6379 --name local-redis redis
   ```
5. Init and activate virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```
6. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
7. Run Celery worker
   ```bash
   celery -A smm_successor.tasks worker --loglevel=info
   ```
8. Run `uvicorn smm_successor.server:app --reload` or `PYTHONPATH=$PYTHONPATH:${PWD} python smm_successor/server.py`
9. Open `http://127.0.0.1:8000/docs`

### Configuration

To run with a different config file:
```bash
SMM_CONF_PATH="/any/path/config.toml" uvicorn smm_successor.server:app --reload
```
