#! python
import re
import pandas as pd
from scholarly import scholarly
import urllib.request
import argparse
from pathlib import Path

def get_candidates(years_to_check, sections_to_check):
    result_page = "https://www.coudert.name/concours_cnrs_{year}.html"
    check_num = re.compile('\([0-9]+\)')
    table = {}
    for year in years_to_check:
        try:
            with urllib.request.urlopen(result_page.format(year=year)) as fp:
                mybytes = fp.read()
                html_doc = mybytes.decode("utf8")
        except Exception as e:
            print(f'The year {year} was probably not found.')
            print(f'Page requested: {result_page.format(year=year)}')
            print(f'The raise error: {e}')
            continue

        for section in sections_to_check:
            done = set()
            start = html_doc.find(f'Concours {section:02d}')
            while (not '(CRCN)' in html_doc[start:].splitlines()[0] and
                   start != -1):
                start = html_doc[start+1:].find(f'Concours {section:02d}')+start+1
            if start == -1:
                print(f'Section {section} was not found for year {year}.')
                print('It was therefore ignored.')
                continue
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
    return table


def get_stats_from_candidates(candidates, save_path=None):
    c_to_y = lambda year, author: sum([c for y, c in author['cites_per_year'].items()
                                      if y<=year])
    p_to_y = lambda year, nb_per_year: sum([n for y, n in nb_per_year.items()
                                            if y<=year])
    found = set()
    query_results = {}
    final_table = {}
    for name, info in candidates.items():
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
                 # crude way to check if the author is there
                if len(set(name.lower().replace(' ', '')).difference(n))<4:
                    first = 6000
                    last = 0
                    nb_per_year = {}
                    for p in author.get('publications'):
                        year = p['bib'].get('pub_year', 0)
                        if not int(year) in nb_per_year:
                            nb_per_year[int(year)] = 0
                        nb_per_year[int(year)] += 1
                        first = int(year) if year!=-1 and int(year)<first else first
                        last = int(year) if year and last<int(year) else last
                    info['citations'] = author.get('citedby')
                    for year in info['Years']:
                        info[f'citations {year}'] = c_to_y(year-1, author)
                        info[f'#publications {year}'] = p_to_y(year-1, nb_per_year)
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

    if save_path:
        if not isinstance(save_path, Path):
            save_path = Path(save_path)
        if not save_path.parent.exists():
            save_path.parent.mkdir(parents=True)
        data.to_json(save_path.with_suffix('.json'))
    return data


if __name__ == '__main__':
    description="""Scrape Google Scholar for CNRS applicants,
    only years from 2019 to 2022 are currently available.
    (from https://www.coudert.name/concours_cnrs_{year}.html)"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--sections', nargs='*', default=[7, 21, 22, 51],
                        type=int, help='Inform the sections to check')
    parser.add_argument('-y', '--years', nargs='*', default=[2020, 2021, 2022],
                        type=int, help='Inform the years to check')
    help_output = ('Output file, will create folder(s) if necessary, '+
                   'will always save as json')
    parser.add_argument('-o', '--output', default='Data.json',
                        type=Path, help=help_output)

    args = parser.parse_args()

    candidates = get_candidates(args.years, args.sections)

    get_stats_from_candidates(candidates, args.output)



















