import json, time, urllib.request, urllib.parse
from pathlib import Path

CLIENT_ID = "Ov23likG74Dmy0Ohf6cL"                 
TOKEN_CACHE = Path.home() / ".opencode" / "github_token.json"

def _post(url: str, data: dict) -> dict:
  body = urllib.parse.urlencode(data).encode()
  req = urllib.request.Request(url, data=body, headers={"Accept": "application/json"})
  with urllib.request.urlopen(req) as r:
      return json.loads(r.read())

def _device_login() -> str:
    # 1. request a device + user code
    dev = _post("https://github.com/login/device/code",
                {"client_id": CLIENT_ID, "scope": "repo"})
    print(f"\n  Open {dev['verification_uri']} and enter code: {dev['user_code']}\n")

    # 2. poll until the user authorizes
    interval = dev.get("interval", 5)
    while True:
      time.sleep(interval)
      res = _post("https://github.com/login/oauth/access_token", {
            "client_id": CLIENT_ID,
            "device_code": dev["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
      })
      if "access_token" in res:
          return res["access_token"]
      if res.get("error") == "authorization_pending":
          continue
      if res.get("error") == "slow_down":
          interval += 5
          continue
      raise RuntimeError(f"Login failed: {res.get('error')}")

def get_user_token() -> str:
    """Return token from .env first, then cached token, or run device login."""
    # Priority 1: GITHUB_TOKEN from .env (fastest, no browser needed)
    try:
        from src.config import settings
        env_token = settings.GITHUB_TOKEN.strip()
        if env_token:
            return env_token
    except Exception:
        pass

    # Priority 2: cached token from previous device login
    if TOKEN_CACHE.exists():
        try:
            return json.loads(TOKEN_CACHE.read_text())["access_token"]
        except Exception:
            pass

    # Priority 3: interactive device login
    token = _device_login()
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(json.dumps({"access_token": token}))
    return token