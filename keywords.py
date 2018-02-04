#! /usr/bin/python3
import re
import jieba
import jieba.posseg as pseg

jieba.enable_parallel(8)
jieba.set_dictionary('dict.txt.big')
jieba.initialize()

def keywords(question):

    # Script will use this List to search google engine
    search_list = []

    # black_list = ['請問', '以下', '可以', '為何', '為什麼',
    #               '下列', '下述', '何者', '為真', '為非']

    # If question string contains following words, then is a reverse quesion
    reverse_list = ['並非', '不是', '為非', '何者非', '沒有', '不同', '無關']
    reverse_flag = any(map(lambda x: x in question, reverse_list))

    word_flag = ['n', 'nr', 'ns', 'nt', 'nz', 'nrt', 'm', 'd', 'a']

    # liar question discrimination
    delimeters = [',', '，', '。']
    if any(map(lambda x: x in question, delimeters)):
        delimeter = next(filter(lambda x: x in question, delimeters))

        # Get 2 part of sentence
        first, last = question.split(delimeter)

        first_words = [word for word, flag in pseg.cut(first) if 'n' in flag]
        last_words = [word for word, flag in pseg.cut(last) if 'n' in flag]

        # last sentence have very less keyword, then it won't be liar question
        if len(last_words) > 1 and set(first_words) & set(last_words):
            question = last

    # Bracket start character
    char_start = '「『《〈〔【"“〝‘く'
    # Bracket end charcter
    char_end = '」』》〉〕】"”〞’'

    bracket_rule = '[%s](.*?)[%s]' % (char_start, char_end)

    pattern = re.findall(bracket_rule, question)
    if pattern:
        search_list.extend(pattern)

        for keyword in pattern:
            jieba.add_word(keyword)
            jieba.suggest_freq(keyword, True)

    for word in pattern:
        question = question.replace(word, '')

    words = pseg.cut(question)

    for word, flag in words:
        print(word, flag)
        if flag in word_flag and word not in search_list:
            if flag == 'm' and len(word) < 2:
                continue
            search_list.append(word)

    return (reverse_flag, search_list)

def split_ans(answer):
    " Split answer for matching search results "
    key = []

    words = pseg.cut(answer)
    for word, flag in words:
        if 'n' in flag:
            key.append(word)

    return key

if __name__ == '__main__':
    #q = '請問豬的平均體脂肪率是多少?'
    q = '創造社是中華民國早期的一個左翼作家組織,請問以下何者並非其中成員?习习'
    #q = '2018台北國際動漫節在2/1開跑,請問今年是第幾屆?'
    #q = '卡通人物《加菲貓》最喜歡吃的《食物》是什麼？'
    print(' '.join(keywords(q)[1]))
