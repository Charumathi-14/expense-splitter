import urllib.request, urllib.error
url = 'http://127.0.0.1:8000/api/groups/1/balance/'
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        print('STATUS', r.status)
        text = r.read(40000).decode('utf-8', errors='replace')
        print(text[:8000])
except urllib.error.HTTPError as e:
    print('HTTP ERROR', e.code)
    body = e.read().decode('utf-8', errors='replace')
    print(body[:8000])
except Exception as e:
    print('ERROR', type(e).__name__, e)
