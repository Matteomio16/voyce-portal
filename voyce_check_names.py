import requests
BASE='https://voycecommunity.eu'
url=BASE+'/our-teams'
r=requests.get(url, timeout=20)
r.raise_for_status()
html = r.text
for name in ['Carlo Casabona','Isabel Tang','Sylvio Baxter','Eugenia Prete','Matthew Morrone']:
    print(name, 'FOUND' if name in html else 'MISSING')
