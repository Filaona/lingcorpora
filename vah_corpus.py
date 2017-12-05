import requests
from bs4 import BeautifulSoup
import csv
import sys
import argparse


def get_first_page(query, corpus, n_results):
    data = {'exact_word':	query,
            'op':	'Search',
            'form_build_id':	'form-hMOF3mG0n7lwL6LmHrPi9vZCcaLbsZmCAco4z8vALT4',
            'form_id': 'sw_exact_word_search_form'}
    params = {'q': 'search-words'}
    global session
    session = requests.Session()
    response = session.post('http://corpora.iliauni.edu.ge/', params=params, data=data)
    return response


def get_page(num):
    params = {'page': str(num),
              'q':	'search-words'}
    page = requests.get('http://corpora.iliauni.edu.ge/', params=params, cookies=session.cookies)
    return page


def get_results_page(page, left_list, center_list, right_list):
    soup = BeautifulSoup(page.text, 'lxml')
    table = soup.select('.result_table')[0]
    for sen in table.select('tr'):
        left_part = ''
        right_part = ''
        for word in sen.select('.left_side'):
            if word.string:
                left_part = left_part + ' ' + word.string
        for word in sen.select('.right_side'):
            if word.string:
                right_part = right_part + ' ' + word.string
        left_list.append(left_part)
        center_list.append(sen.select('.found_word')[0].string)
        right_list.append(right_part)
    return left_list, center_list, right_list


def get_results_first_page(first_page):
    left_list = []
    right_list = []
    center_list = []
    soup = BeautifulSoup(first_page.text, 'lxml')
    occur = soup.select('.mtavruli')[0].string
    occur = int(occur.split(' ')[2])
    table = soup.select('.result_table')[0]
    for sen in table.select('tr'):
        left_part = ''
        right_part = ''
        for word in sen.select('.left_side'):
            if word.string:
                left_part = left_part + ' ' + word.string
        for word in sen.select('.right_side'):
            if word.string:
                right_part = right_part + ' ' + word.string
        left_list.append(left_part)
        center_list.append(sen.select('.found_word')[0].string)
        right_list.append(right_part)
    return left_list, center_list, right_list, occur


def get_results(first_page, write, kwic, query, n_results):
    (left_list, center_list, right_list, occur) = get_results_first_page(first_page)
    num_page = (min(occur, n_results) + 9) // 10
    for i in range(1, num_page):
        page = get_page(i)
        (left_list, center_list, right_list) = get_results_page(page, left_list, center_list, right_list)
    s = [[left_list[i].strip(), center_list[i].strip(), right_list[i].strip()] for i in range(0, min(occur, n_results))]
    if not s:
        print('vah_search: nothing found for "%s"' % query)
    if not kwic:
        s = [[' '.join(x)] for x in s]
    if write:
        if not kwic:
            cols = ['index', 'results']
        else:
            cols = ['index', 'left', 'center', 'right']
        write_results(query, s, cols)
    return s


def write_results(query, results, cols):
    """
    write csv
    """
    not_allowed = '/\\?%*:|"<>'
    query = ''.join([x if x not in not_allowed else '_na_' for x in query])
    with open('vah_search_' + str(query) + '.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(cols)
        for i, x in enumerate(results):
            writer.writerow([i]+x)


def into_bool(x):
    if x == 'True':
        x = True
    else:
        x = False
    return x


def main(query, corpus, tag, n_results, kwic, write):
    kwic = into_bool(kwic)
    write = into_bool(write)
    n_results = int(n_results)
    first_page = get_first_page(query, corpus, n_results)
    results = get_results(first_page, write, kwic, query, n_results)
    return results


if __name__ == '__main__':
    args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('corpus', type=str)
    parser.add_argument('query', type=str)
    parser.add_argument('tag', type=str)
    parser.add_argument('n_results', type=str)
    parser.add_argument('kwic', type=str)
    parser.add_argument('write', type=str)
    args = parser.parse_args(args)
    print(args)
    main(**vars(args))
'''Georgian words: მე, დედა'''
