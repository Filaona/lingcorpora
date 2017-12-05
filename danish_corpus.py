import requests
from bs4 import BeautifulSoup
import csv
import sys
import argparse
import re


def get_first_page(query):
    params = {'query': query,
              'search': 'Search',
              'tag': 'lemma'}
    global session
    session = requests.Session()
    response = session.get('http://ordnet.dk/korpusdk_en/concordance/action', params=params)
    return response


def get_page(num):
    params = {'page': num}
    page = requests.get('http://ordnet.dk/korpusdk_en/concordance/result/navigate',
                        params=params, cookies=session.cookies)
    return page


def get_results_page(page, left_list, center_list, right_list):
    soup = BeautifulSoup(page.text, 'lxml')
    punc = re.compile("[.-:\";,!?']")
    p = soup.select('.conc_table')[0]
    for sen in p.select('tr[onmouseover]'):
        left_part = ''
        right_part = ''
        for word in sen.select('.left-context-cell'):
            left_part = left_part + ' ' + word.select('a')[0].string
        for word in sen.select('.right-context-cell'):
            right_part = right_part + ' ' + word.select('a')[0].string
        center_part = sen.select('.conc_match')[0].a.string
        left_list.append(left_part)
        if punc.search(center_part):
            center_list.append(center_part[0:punc.search(center_part).start()])
            right_list.append(center_part[punc.search(center_part).start():] + right_part)
        else:
            center_list.append(center_part)
            right_list.append(right_part)
    return left_list, center_list, right_list


def get_results_first_page(first_page):
    left_list = []
    right_list = []
    center_list = []
    punc = re.compile("[.-:;\",!?']")
    soup = BeautifulSoup(first_page.text, 'lxml')
    occur = soup.select('.value')[0].string
    occur = int(occur[(occur.find('of') + 2):(occur.find('occur'))].strip())
    if occur > 49:
        occur = occur - 1
    table = soup.select('.conc_table')[0]
    for sen in table.select('tr[onmouseover]'):
        left_part = ''
        right_part = ''
        for word in sen.select('.left-context-cell'):
            left_part = left_part + ' ' + word.select('a')[0].string
        for word in sen.select('.right-context-cell'):
            right_part = right_part + ' ' + word.select('a')[0].string
        center_part = sen.select('.conc_match')[0].a.string
        left_list.append(left_part)
        if punc.search(center_part):
            center_list.append(center_part[0:punc.search(center_part).start()])
            right_list.append(center_part[punc.search(center_part).start():] + right_part)
        else:
            center_list.append(center_part)
            right_list.append(right_part)
    return left_list, center_list, right_list, occur


def get_results(first_page, write, kwic, query, n_results):
    (left_list, center_list, right_list, occur) = get_results_first_page(first_page)
    if min(occur, n_results) > 49:
        num_page = min(occur, n_results) // 50 + 1
    else:
        num_page = 1
    for i in range(2, num_page + 1):
        page = get_page(i)
        left_list, center_list, right_list = get_results_page(page, left_list, center_list, right_list)
    s = [[left_list[i].strip(), center_list[i].strip(), right_list[i].strip()] for i in range(0, min(occur, n_results))]
    if not s:
        print('danish_search: nothing found for "%s"' % query)
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
    with open('danish_search_' + str(query) + '.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(cols)
        for i,x in enumerate(results):
            writer.writerow([i]+x)


def into_bool(x):
    if x == 'True':
        x = True
    else:
        x = False
    return x


def main(corpus, query, tag, n_results, kwic, write):
    kwic = into_bool(kwic)
    write = into_bool(write)
    n_results = int(n_results)
    first_page = get_first_page(query)
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
    main(**vars(args))
