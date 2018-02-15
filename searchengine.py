#! /usr/bin/python3
import re
from keywords import split_ans
from hanziconv import HanziConv
from googlesearch import google

def answer(reverse_flag, question, search_keywords, answers):
    # keywords: Question keywords list
    # answers: list contains answers

    match = {key: 0 for key in answers}
    distance = {key: [] for key in answers}

    results = search(search_keywords)

    print('\n\033[92m《搜尋引擎標題結果》\033[0m\n')
    for result in results:
        print('  %s' % result.name)

    print('\n\033[92m《抓取關鍵字重要訊息》\033[0m')

    for key in match:
        # Only pick up word not fully equal to answers,
        # Or it will calculate duplicated.
        tra_words = [word for word in split_ans(key) if word not in match]
        sim_words = list(map(HanziConv.toSimplified, tra_words))

        for result in results:
            simplified = HanziConv.toSimplified(key)

            fully_related = False

            # If keyword in title, then this keyword may be the answer
            if key in result.name or simplified in result.name:
                print('  \033[91m【重要】我發現 『%s』 在標題列\033[0m' % key)
                match[key] += 2
                fully_related = True

            # Match Traditional Chinese and Simplified Chinese
            match[key] += result.description.count(key) * (2 if fully_related else 1)

            # Sometimes, character same after simplified, so pass
            if key != simplified:
                match[key] += result.description.count(simplified) * (4 if fully_related else 1)

            # Split answer to keyword for searching
            for word in tra_words + sim_words:
                match[key] += result.description.count(word) * 0.5 * len(word)

            for keyword in search_keywords:
                sim_keyword = HanziConv.toSimplified(keyword)
                sim_key = HanziConv.toSimplified(key)
                desc = result.description

                if keyword in desc and key in desc:
                    distance[key].append(abs(desc.index(keyword) - desc.index(key)))

                if sim_keyword in desc and sim_key in desc:
                    distance[key].append(abs(desc.index(sim_keyword) - desc.index(sim_key)))

    ### If value is smallest, then according description in google result,
    ### target answer is most probability to be right answer

    # drop no related answer
    distance = {k: v for k, v in distance.items() if len(v) > 0}

    print(distance)

    # Only when have 2 entry, this may be work
    if len(distance.keys()) >= 2:
        # Get distance list, smallest value means most probably answer
        distance = {k: sum(v) / (1 + len(v)) for k, v in distance.items()}

        # Get max value, for calculate deviation
        max_distance = max(distance.values())
        distance = {k: max_distance - v for k, v in distance.items()}

        # Get max value again, doing formulation
        max_distance = max(distance.values())
        max_score_in_distance_calc = max(match.values()) * 0.6

        for key, value in distance.items():
            match[key] += value * max_score_in_distance_calc / max_distance

    if '' in match:
        match.pop('')

    print('\n\033[92m《關鍵字配對結果》\033[0m')
    print('  %s' % match)

    if not reverse_flag:
        for ans in sorted(match, key=match.get, reverse=True):
            if match[ans] > 20:
                if ans in search_keywords:
                    print('  \033[91m我找到 %s 同時出現在關鍵字，這可能不是答案。\033[0m' % ans)
                    continue
                else:
                    return [ans]
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

    print('\033[94mSearch Pattern: %s\033[0m' % query)

    return google.search(query)
