#! /usr/bin/python3
import re
from keywords import split_ans
from hanziconv import HanziConv
from googlesearch import google

def answer(reverse_flag, keywords, answers):
    # keywords: Question keywords list
    # answers: list contains answers

    match = {key: 0 for key in answers}

    results = search(keywords)
    #num_dict1 = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5,'
    #             '六': '6', '七': '7', '八': '8', '九': '9'}
    #num_dict2 = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五',
    #             '6': '六', '7': '七', '8': '八', '9': '九'}

    for key in match:
        tra_words = split_ans(key)
        sim_words = list(map(HanziConv.toSimplified, tra_words))

        for result in results:
            simplified = HanziConv.toSimplified(key)

            # Match Traditional Chinese and Simplified Chinese
            match[key] += result.description.count(key)
            match[key] += result.description.count(simplified)

            # If keyword in title, then this keyword may be the answer
            if key in result.name or simplified in result.name:
                match[key] += 2

            # Split answer to keyword for searching
            for word in tra_words + sim_words:
                match[key] += result.description.count(word) * 0.5

    if '' in match:
        match.pop('')

    print(match)

    if not reverse_flag:
        for ans in sorted(match, key=match.get, reverse=True):
            if match[ans] > 20:
                continue
            if match[ans] != 0:
                return [ans]
            else:
                return list(filter(lambda x: match[x] == 0, match.keys()))
    else:
        for ans in sorted(match, key=match.get, reverse=False):
            if match[ans] == 0:
                return list(filter(lambda x: match[x] == 0, match.keys()))
            else:
                return [ans]

def search(keywords):
    # Keywords should be list format or string

    if type(keywords) is list:
        query = ' '.join(keywords)
    else:
        query = keywords

    print('Search Pattern: %s' % query)

    return google.search(query)
