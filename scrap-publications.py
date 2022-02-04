from pathlib import Path
from scholarly import ProxyGenerator
from scholarly import scholarly
import pandas as pd

# pg = ProxyGenerator()
# pg.FreeProxies()
# scholarly.use_proxy(pg)

p = Path('.')

candidates = {}
for f_path in p.iterdir():
    if f_path.suffix == '.txt':
        with open(f_path) as f:
            lines = f.readlines()
        for l in lines:
            cand = ' '.join(l.strip().split(' ')[:-3])
            tmp_d = candidates.setdefault(cand, {})
            s = int(f_path.name[7:-4])
            tmp_d.setdefault('sections', []).append(s)
            tmp_d[s] = True

for c, info in candidates.items():
    for s in [7, 22, 51, 55]:
        if not s in info:
            info[s] = False

query_results = {}
for c, info in candidates.items():
    if 'found' in info:
        continue
    print(f'looking at {c}')
    query_results[c] = []
    search_query = scholarly.search_author(c)
    done = False
    info['multiple results'] = False
    for auth in search_query:
        if done:
            info['multiple results'] = True
            break
        try:
            author = scholarly.fill(auth)
            query_results[c].append(author)
            n = author.get('name').lower().replace(' ', '')
            if len(set(c.lower().replace(' ', '')).difference(n))<4: # crude way to check if the author is there
                first = 6000
                last = 0
                for p in author.get('publications'):
                    year = p['bib'].get('pub_year')
                    first = int(year) if year and int(year)<first else first
                    last = int(year) if year and last<int(year) else last
                info['citations'] = author.get('citedby')
                info['website'] = author.get('homepage')
                info['email'] = author.get('email_domain')
                info['affiliation'] = author.get('affiliation')
                info['#publications'] = len(author.get('publications'))
                info['First publication'] = first
                info['Last publication'] = last
                done = True
        except Exception as e:
            print(f'Failed {c} with following error:')
            print(f'\t{e}')
    info['found'] = done
    print(c, info)

# pd_candidates = pd.DataFrame(candidates, index=['name'])
indices = ['sections', 7, 22, 51, 55, 'multiple results',
           'citations', 'website', 'email', 'affiliation',
           '#publications', 'First publication',
           'Last publication', 'found']
out = []
for n, info in candidates.items():
    if info['found'] and not info['multiple results']:
        out.append([n]+[info[k] for k in indices])

pd_candidates = pd.DataFrame(out, columns=['name']+indices)

pd_candidates.to_csv('7-22-51-55-less-dirty.csv')