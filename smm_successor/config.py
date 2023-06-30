import os

import toml

CONFIG = toml.load(os.environ.get("SMM_CONF_PATH", "config.toml"))
