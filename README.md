# SMM Successor

## How to run

1. Copy `config.example.toml` to `config.toml`
2. Update `config.toml`
3. Run `docker-compose run -d`
4. Open `http://0.0.0.0:8000/docs`

### Configuration

To run with a different config file:
```bash
SMM_CONF_PATH="/any/path/config.toml" uvicorn smm_successor.server:app --reload
```
