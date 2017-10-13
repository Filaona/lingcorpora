from requests import get,post
from bs4 import BeautifulSoup
import re
import csv
import sys
import argparse
import unittest
import os




'''Available subcorporas:
subcorp': 'Maaleht',
              'subcorp': 'postimees_kokku',
              'subcorp': 'valga',
              'subcorp': 'le',
              'subcorp': 'luup',
              'subcorp': 'Kroonika',
              'subcorp': '1980_aja',
              'subcorp': '1970_aja',
              'subcorp': '1960_aja',
              'subcorp': '1950_aja',
              'subcorp': '1930_aja',
              'subcorp': '1910_aja',
              'subcorp': '1900_aja',
              'subcorp': '1890_aja',
              'subcorp': 'epl_1995',
              'subcorp': 'epl_1996',
              'subcorp': 'epl_1997',
              'subcorp': 'epl_1998',
              'subcorp': 'epl_1999',
              'subcorp': 'epl_2000',
              'subcorp': 'epl_2001',
              'subcorp': 'epl_2002',
              'subcorp': 'epl_2004',
              'subcorp': 'epl_2005',
              'subcorp': 'epl_2006',
              'subcorp': 'epl_2007',
              'subcorp': 'sloleht_1997',
              'subcorp': 'sloleht_1998',
              'subcorp': 'sloleht_1999',
              'subcorp': 'sloleht_2000',
              'subcorp': 'sloleht_2001',
              'subcorp': 'sloleht_2002',
              'subcorp': 'sloleht_2003',
              'subcorp': 'sloleht_2004',
              'subcorp': 'sloleht_2006',
              'subcorp': 'sloleht_2007',
              'subcorp': '1990_ilu_26_08_04',
              'subcorp': 'segailu_5_10_2008',
              'subcorp': '1980_ilu',
              'subcorp': '1970_ilu',
              'subcorp': '1960_ilu',
              'subcorp': '1950_ilu',
              'subcorp': '1930_ilu',
              'subcorp': '1910_ilu',
              'subcorp': '1900_ilu',
              'subcorp': '1890_ilu',
              'subcorp': '1980_tea',
              'subcorp': 'horisont',
              'subcorp': 'arvutitehnika',
              'subcorp': 'doktor',
              'subcorp': 'Eesti_Arst_2002',
              'subcorp': 'Eesti_Arst_2003',
              'subcorp': 'Eesti_Arst_2004',
              'subcorp': 'agraar',
              'subcorp': 'jututoad',
              'subcorp': 'uudisgrupid',
              'subcorp': 'foorumid',
              'subcorp': 'kommentaarid',
              'subcorp': 'riigikogu',
              'subcorp': '1980_muu',
              'subcorp': 'teadusartiklid',
              'subcorp': 'akp','''

def get_page(query, n_results):
    params = {'otsisona': query,
              'subcorp': '1990_ajalehed_26_08_04',
              'kontekst': '0',
              'lause_arv':	'0'}
    s = get('http://www.cl.ut.ee/korpused/kasutajaliides/konk.cgi.et', params=params)
    return s


def find_right_part(elem, right_part):
    right_part = right_part + elem.string + elem.next_sibling
    if elem.next_sibling.next_sibling.name != 'br':
        right_part = find_right_part(elem.next_sibling.next_sibling, right_part)
    return right_part


def find_left_part(elem, left_part):
    left_part = elem.previous_sibling + elem.string + left_part
    if elem.previous_sibling.previous_sibling.name != 'hr':
        left_part = find_left_part(elem.previous_sibling.previous_sibling, left_part)
    return left_part


def get_results(page, write, kwic, query, n_results):
    corpus = []
    left_list = []
    right_list = []
    center_list = []
    soup = BeautifulSoup(page.text, 'lxml')
    strong = soup.select('strong')
    if strong == []:
        print('eesti_search: nothing found for "%s"' % (query))
    else:
        for elem in strong:
            right_part = elem.next_sibling
            left_part = elem.previous_sibling
            center_part = elem.string
            if elem.next_sibling.next_sibling.name != 'br':
                right_part = find_right_part(elem.next_sibling.next_sibling, right_part)
            if elem.previous_sibling.previous_sibling.name != 'hr':
                left_part = find_left_part(elem.previous_sibling.previous_sibling, left_part)
            p = re.compile('[ .-:;,!?]')
            corpus.append(left_part.split('    ', maxsplit = 1)[0])
            left_list.append(left_part.split('    ', maxsplit = 1)[1])
            right_list.append(right_part[p.search(right_part).start():])
            center_list.append(center_part + right_part[0:p.search(right_part).start()])
            if len(left_list) > n_results:
                break
        if not kwic:
            temp = [left_list[i] + center_list[i] + right_list[i]
                 for i in range(min(len(left_list), n_results))]
            s = [[corpus[i], temp[i]]
                 for i in range(len(temp))]
        else:
            s = [[corpus[i], left_list[i].strip(), center_list[i], right_list[i].strip()]
                 for i in range(min(len(left_list), n_results))]
        if write:
            if not kwic:
                cols = ['index', 'corpus', 'results']
            else:
                cols = ['index', 'corpus', 'left', 'center', 'right']
            write_results(query, s, cols)
        return s



def write_results(query,results,cols):
    """
    write csv
    """
    not_allowed = '/\\?%*:|"<>'
    query = ''.join([x if x not in not_allowed else '_na_' for x in query])
    with open('eesti_search_' + str(query) + '.csv','w',encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(cols)
        for i,x in enumerate(results):
            writer.writerow([i]+x)



def for_bool(x):
    if x == 'True':
        x = True
    else:
        x = False
    return x


def main(query, corpus, tag, n_results, kwic, write):
    kwic = for_bool(kwic)
    write = for_bool(write)
    n_results = int(n_results)
    page = get_page(query, n_results)
    results = get_results(page, write, kwic, query, n_results)
    return results


if __name__ == '__main__':
    #unittest.main()
    args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', type=str)
    parser.add_argument('query', type=str)
    parser.add_argument('tag', type=bool)
    parser.add_argument('n_results', type=str)
    parser.add_argument('kwic', type=str)
    parser.add_argument('write', type=str)
    args = parser.parse_args(args)
    print(args)
    main(**vars(args))