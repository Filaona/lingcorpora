from requests import get,post
from bs4 import BeautifulSoup
import re
import csv
import sys
import argparse
import unittest
import os

def get_page():
    params = {'otsisona': 'keele',
              'subcorp': '1990_ajalehed_26_08_04',
              'kontekst': '0',
              'lause_arv':	'0'}
    s = get('http://www.cl.ut.ee/korpused/kasutajaliides/konk.cgi.et?', params=params)
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




def get_results(page,query,kwic, write):
    corpus = []
    left_list = []
    right_list = []
    center_list = []
    corpus = []
    soup = BeautifulSoup(page.text, 'lxml')

    for elem in (soup.select('strong')):
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
    s = [[corpus[i], left_list[i].strip(), center_list[i], right_list[i].strip()]
         for i in range(len(left_list))]
    if not s:
        print('eesti_search: nothing found for "%s"' % (query))
    if not kwic:
        s = [[' '.join(x)] for x in s]
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
    #not_allowed = '/\\?%*:|"<>'
    #query = ''.join([x if x not in not_allowed else '_na_' for x in query])
    with open('eesti_search_' + str(query) + '.csv','w',encoding='iso-8859-15') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(cols)
        for i,x in enumerate(results):
            writer.writerow([i]+x)


class TestMethods(unittest.TestCase):
    def test1(self):
        self.assertEqual(('<Response [200]>'), str(get_page(query='bezug', n_results='100', corpus='kern')))

    def test2(self):
        self.assertIs(list, type(get_results(page=get_page(query='bezug',corpus='kern',n_results='100'),
                                             write=False, kwic=True,query='bezug', n_results='100')))

    def test3(self):
        r = main('Mutter',kwic=False,write=True)
        filelist = os.listdir()
        self.assertIn('deu_search_Mutter.csv',filelist)
        os.remove('deu_search_Mutter.csv')


def main(query, corpus='kern', tag=False, n_results=10, kwic=True, write=False):
    page = get_page(query, corpus, n_results)
    results = get_results(page, write, kwic, query, n_results)
    return results


if __name__ == '__main__':
    '''unittest.main()
    args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', type=str)
    parser.add_argument('query', type=str)
    parser.add_argument('tag', type=bool)
    parser.add_argument('n_results', type=int)
    parser.add_argument('kwic', type=bool)
    parser.add_argument('write', type=bool)
    args = parser.parse_args(args)
    main(**vars(args))'''

    page = get_page()
    get_results(page,'keele',True, True)




