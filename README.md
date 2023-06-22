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
4. Run `uvicorn smm_successor.server:app --reload`
5. Open `http://127.0.0.1:8000/docs`
