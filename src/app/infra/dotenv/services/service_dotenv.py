from functools import lru_cache
from src.app.infra.dotenv.entities.dotenv import DotEnv


@lru_cache(maxsize=1)
def get_service_dotenv() -> DotEnv:
    return DotEnv()
