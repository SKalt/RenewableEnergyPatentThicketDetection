# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 14:11:31 2015

@author: steven
"""

#%% import block
from lxml import html
import urllib3 as ul
HTTP = ul.PoolManager()
ul.disable_warnings()
from io import BytesIO
#from ExploreElement import explore_element
import pandas as pd
import time
import string
#%% function definitions
def iterate_pages():
    """
    Iterates through the patent cases on dockets.justia.com.
    """
    temp_time = time.time()
    output = []
    init_url = "https://dockets.justia.com/browse/noscat-10/nos-830?page={}"

    # get first page
    page = HTTP.request('GET', init_url)
    tree = html.parse(BytesIO(page.data))
    # get total number of cases
    number_cases_xpath = '//*[@id="main-content"]/div/div/div/section/div/' + \
    'div[@class="float-left clear margint-20 marginb-20"]/text()'
    number_cases = tree.xpath(number_cases_xpath)[0].strip().split('of')[1]
    number_cases = int(''.join([i for i in number_cases if i.isnumeric()]))
    number_pages = int(number_cases / 10) + 1
    # iterate through all pages of cases
    page_generator = (init_url.format(str(i)) for i in range(1, number_pages))
    for url in page_generator:
        output += get_case_details(tree)
        page = HTTP.request('GET', url)
        tree = html.parse(BytesIO(page.data))
    print(time.time()-temp_time)
    return(output)
    # testing materials
    # second-to-last page to test while loop
    # next_page_link = '//*[@class="paginator clear"]/a/text()'
    # while 'next' in tree.xpath(next_page_link):
    #init_url = "https://dockets.justia.com/browse/noscat-10/nos-830?page=4750"
    # xpath to get the total number of cases
    # TODO add threading
    # TODO add streaming?

def get_case_details(page_tree):
    """
    From a patent suits page of dockets.justia.com, this function returns a
    list of dictionaries of case details: "title", "url", "date",
    "cause_of_action"
    """
    output = []
    # define xpaths
    case_divs = '//*[@id="search-results"]/div[@class="result"]'
    case_url = './a[@class="case-name"]/@href'
    case_names_xpath = './a[@class="case-name"]/text()' #
    case_abstract_xpath = './div[@class="abstract"]/div' #
    case_date_xpath = './div[@class="gray paddingb-5 size-09"]/time/@datetime'
    div_titles = './strong/text()'
    for case in page_tree.xpath(case_divs):
        # get details with sure xpaths
        case_details = {"title" : case.xpath(case_names_xpath)}
        case_details["date"] = case.xpath(case_date_xpath)
        case_details["url"] = case.xpath(case_url)
        # get details which may have variable xpaths
        case_abstract = case.xpath(case_abstract_xpath)
        for i in case_abstract:
            if i.xpath(div_titles)[0].lower() == 'cause of action':
                case_details["cause_of_action"] = i.xpath('./text()')
        output.append(case_details)
    return(output)
    
ET_AL = []
# create a global list in which to record cases with
# 'et al' in the title

def remove_corpisms(corp_string):
    """
    Takes company suffixes out of a corporate name split into separate words.
    Returns a cleaned string of the company name.
    """
    punctuation_remover = ''.maketrans('', '', string.punctuation)
    corp_words = corp_string.translate(punctuation_remover)
    corp_words = corp_words.strip().upper().split()
    corpisms = ['LLC', 'PTY', 'PLC', 'UNIVERSITE', 'INC', 'AS', 'LLP',
                'COMPNY', 'LIMITED', 'PLLC', 'INCORPORATION', 'GMBH', 'AB',
                'UNIVERSITY', 'KABUSHIKI', 'LP', 'KABUSHIKA', 'KABUHSIKI',
                'LTDA', 'PC', 'MBH', 'INTERNATIONALAG', 'UNIVERSTIY', 'CORP',
                'SPA', 'CO', 'INTERNATIONAL', 'CORPORATION', 'SA',
                'INCORPORATED', 'LTD', 'INTERNATIONALE', 'ET', 'AL',
                'COMPANY', 'CORP', 'SL']
                 #original corpisms list
#    corpisms = ['Inc.', 'Inc.,', 'Inc',
#                'Corporation', 'Corporation,', 'Corporation)',
#                'Co.', 'Co.,', 'Co',
#                'Corp.', 'Corp.,', 'Corp ',
#                'Company', 'Company,', 'Compny',
#                'Incorporated', 'Incorporation',
#                'P.C.', 'P.L.C.', 'PLC.',
#                'Kabushiki', 'Kabushika', 'Kabuhsiki',
#                'S.A.', 'S.A.,',
#                'a.s.','A/S', 'A/S,', 'AS',
#                'S.p.A.', 'S.p.A..', 'S.P.A.',
#                'LLP', 'LLP.', 'LP',
#                'Ltd.', 'Ltda.', 'Ltd.,',
#                'LLC', 'PLLC', 'LLC.',
#                'GmbH', 'GmbH.', 'mbH',
#                'University', 'Universtiy', 'Universite',
#                'Limited', 'Limited,', 'limited',
#                'Pty', 'Pty.', 'Pty.,',
#                'International', 'Internationale', 'International,'
#                'AG', 'AB', 'SL','et al', 'et al.']
    for suffix in corpisms:
        if suffix in corp_words:
            corp_words.remove(suffix)
    corp_string = ' '.join(corp_words)
    return(corp_string)

def split_title(case):
    """
    Splits a title into plaintiff and defendant, then writes an
    edge to the global edgelist. This function then stores each in a list
    to be expanded with other litigants.  This list is stored with a date in
    a list of cases, El1.
    """
    # check if there are multiple litigants
    title = case["title"][0].strip().lower()
    if 'et al' or 'et al.' in title:
        ET_AL.append(title)
    title = title.split()
    vs = ['v', 'versus', 'vs', 'vs.', 'v.']
    if len([v for v in vs if v in title]) == 0:
        print(title)
    for v in vs:
        if v in title:
            litigants = case["title"][0].split(v)
            litigants = [i.upper().strip() for i in litigants]
            litigants = [remove_corpisms(corp) for corp in litigants]
            return(tuple(litigants)) # always of length 2
#%% execution block
while __name__ == "__main__":
    OUTPUT = iterate_pages()
    OUTPUT_GENERATOR = (i for i in OUTPUT)
    EDGELIST = []
    for CASE in OUTPUT_GENERATOR:
        EDGELIST.append(split_title(CASE))
    EDGELIST_TSV = pd.DataFrame(EDGELIST)
    EDGELIST_TSV.columns = ['Source', 'Target']
    EDGELIST_TSV.to_csv('JustiaPatentLitigationEdgelist.tsv', sep='\t')
    