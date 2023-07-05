"""

   ┏┓   ┏┓ + +
  ┏┛┻━━━┛┻┓ + +
  ┃   ━   ┃ ++ + + +
  ┃ ████━████  ┃+
  ┃       ┃ +
  ┃   ┻   ┃ + +
  ┗━┓   ┏━┛
    ┃   ┃ + + + +
    ┃   ┃ +   神兽保佑,代码无bug
    ┃   ┃ +
    ┃   ┗━━━┓ + +
    ┃       ┣┓
    ┃       ┏┛
    ┗┓┓┏━┳┓┏┛ + + + +
     ┃┫┫ ┃┫┫
     ┗┻┛ ┗┻┛+ + + +

Create Time: 2023/7/4

"""

# app/services/cache_service.py

import json
from typing import Any, Optional
from redis import Redis


from fastapi.encoders import jsonable_encoder

def set_to_cache(redis_db: Redis, key: str, value: Any) -> None:
    value_to_store = jsonable_encoder(value)  # Convert to a JSON-serializable format
    redis_db.set(key, json.dumps(value_to_store))

def get_from_cache(redis_db: Redis, key: str) -> Optional[Any]:
    result = redis_db.get(key)
    if result:
        return json.loads(result)  # No need to decode this, it's just a list/dict/number/string
    return None

def delete_from_cache(redis_db: Redis, user_id: int, data_type: str) -> None:
    key_pattern = f"user:{user_id}:{data_type}:*"
    for key in redis_db.scan_iter(match=key_pattern):
        redis_db.delete(key)




