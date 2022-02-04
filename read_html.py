import re
import pandas as pd
from scholarly import scholarly
check_num = re.compile('\([0-9]+\)')

sections = [7, 21, 22, 51]
status = ['Admis', 'Concourir', 'Poursuivre']
table = {}

for year in [2020, 2021, 2022]:
    with open(f'Data/{year}.html') as f:
        html_doc = f.read()

    for section in sections:
        done = set()
        start = html_doc.find(f'Concours {section:02d}')
        while not '(CRCN)' in html_doc[start:].splitlines()[0]:
            start = html_doc[start+1:].find(f'Concours {section:02d}')+start+1
        stop = html_doc[start:].find('<h2>') + start
        lines = html_doc[start:stop].splitlines()
        curr_status = 'Admis'
        if 'details' in lines[1]:
            l_num = 2
            curr_status = 'Concourir'
        else:
            l_num = 3
        while l_num<len(lines)-2:
            l = lines[l_num]
            l_num += 1
            if curr_status == 'Admis':
                if 'table' in l:
                    curr_status = 'Concourir'
                    l_num += 1
                else:
                    start = l.find('<td>')+4
                    end = l.find('</td>')
                    name = l[start:stop]
                    name = name[:check_num.search(name).start()].strip()
                    info = table.setdefault(name, {})
                    info[f'{year} {section} section'] = True
                    info[f'{year} {section} Admissibility'] = curr_status
                    info[f'{year}'] = True
                    info.setdefault('Years', set()).add(year)
                    info.setdefault(f'{year} sections', set()).add(section)
            elif curr_status == 'Concourir':
                if 'details' in l:
                    curr_status = 'Poursuivre'
                    l_num += 1
                else:
                    name = l[:-5]
                    if not table.get(name, {}).get(f'{year} {section} Admissibility'):
                        info = table.setdefault(name, {})
                        info[f'{year} {section} section'] = True
                        info[f'{year} {section} Admissibility'] = curr_status
                        info[f'{year}'] = True
                        info.setdefault('Years', set()).add(year)
                        info.setdefault(f'{year} sections', set()).add(section)
            else:
                name = l[:-5]
                if not table.get(name, {}).get(f'{year} {section} Admissibility'):
                    info = table.setdefault(name, {})
                    info[f'{year} {section} section'] = True
                    info[f'{year} {section} Admissibility'] = curr_status
                    info[f'{year}'] = True
                    info.setdefault('Years', set()).add(year)
                    info.setdefault(f'{year} sections', set()).add(section)
                elif table[name][f'{year} {section} Admissibility'] != 'Admis':
                    table[name][f'{year} {section} Admissibility'] = curr_status


found = set()
query_results = {}
final_table = {}
for name, info in table.items():
    if info.get('Tried'):
        continue
    info['Tried'] = True
    info['found'] = False
    print(f'looking at {name}')
    query_results[name] = []
    search_query = scholarly.search_author(name)
    done = False
    info['multiple results'] = False
    for auth in search_query:
        if done:
            info['multiple results'] = True
            break
        try:
            author = scholarly.fill(auth)
            query_results[name].append(author)
            n = author.get('name').lower().replace(' ', '')
            if len(set(name.lower().replace(' ', '')).difference(n))<4: # crude way to check if the author is there
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
            print(f'Failed {name} with following error:')
            print(f'\t{e}')
    info['found'] = done
    if info['found'] and not info['multiple results']:
        final_table[name] = info.copy()
    print(name, info)

all_keys = set()
for n, d in final_table.items():
    all_keys.update(list(d.keys()))

all_keys = list(all_keys)
pd_table = []
for n, d in final_table.items():
    pd_table.append([n] + [d.get(k, False) for k in all_keys])

data = pd.DataFrame(pd_table, columns=['Name'] + all_keys)

data.to_json('complete.json')