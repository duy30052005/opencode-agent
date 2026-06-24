import urllib.request, json
from src.config import settings

token = settings.GITHUB_TOKEN.strip()

for owner in ['DarkKing335', 'duy30052005']:
    req = urllib.request.Request(
        f'https://api.github.com/repos/{owner}/opencode-agent',
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github.v3+json'}
    )
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read())
            print(f"✅ Found repo: {owner}/opencode-agent, Permissions: {data.get('permissions')}")
    except urllib.error.HTTPError as e:
        print(f"❌ Cannot access {owner}/opencode-agent: {e.code} {e.reason}")
