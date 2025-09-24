# app/services/runtime_store.py
from cachetools import TTLCache

# 30분 TTL, 최대 100개 보관 (데모용·메모리 저장)
db_creds = TTLCache(maxsize=100, ttl=60*30)     # {cred_id: DBCredIn}
web_targets = TTLCache(maxsize=100, ttl=60*30)  # {site_id: str}
