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
4. Init and activate virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```
5. Install requirements
   ```bash
   pip install -r requirements.txt
   ```
6. Run `uvicorn smm_successor.server:app --reload` or `PYTHONPATH=$PYTHONPATH:${PWD} python smm_successor/server.py`
7. Open `http://127.0.0.1:8000/docs`

### Configuration

To run with a different config file:
```bash
SMM_CONF_PATH="/any/path/config.toml" uvicorn smm_successor.server:app --reload
```
