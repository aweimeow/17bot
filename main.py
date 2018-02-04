import re
import time
import random
import string
from multiprocessing.dummy import Pool as ThreadPool

from ocr import Game, grabtext
from keywords import keywords
from searchengine import answer


def _main(results=None):

    if results is None:
        # 全螢幕時使用的參數
        #game = Game(1660, 0, 906, 1600)
        # 有 Wifi 熱點分享使用的參數
        game = Game(1660, 50, 900, 1550)

        #game.ishow(game.x, game.y, game.x + game.width, game.y + game.height)
        #game.ishow(*game.question)
        #game.ishow(*game.answers[0])
        #game.ishow(*game.answers[1])
        #game.ishow(*game.answers[2])
        #game.ishow(*game.answers[3])

        positionqueue = [game.question]
        positionqueue.extend(game.answers)

        input('【按下 Enter 開始自動辨識！】')

    ts = time.time()

    if results is None:
        # Using Multi-Thread to Get Question and answer
        pool = ThreadPool(5)
        results = pool.map(grabtext, positionqueue)
        print(results)

    question = results[0]
    answers = []

    # カタカナ 50 character filter out
    katakana_filter = "アイウエオカキクケコサシスセソタチツテトナニヌネノ" \
                      "ハヒフヘホマミムメモヤユヨラリルレロワヲン"

    for ans in results[1:]:
        tmp = re.sub("^[ABCcD][﹒.][ ']*", '', ans)
        answers.append(re.sub("[%s]" % katakana_filter, '', tmp))

    # Filter same word in answers
    while True:
        first_char = answers[0][0]

        if first_char in string.ascii_letters:
            break

        if all(map(lambda x: x[0] == first_char, answers)):
            answers = list(map(lambda x: x[1:], answers))
        else:
            break

    # Filter same word in answers
    while True:
        last_char = answers[0][-1]

        if last_char in string.ascii_letters:
            break

        if all(map(lambda x: x[-1] == last_char, answers)):
            answers = list(map(lambda x: x[:-1], answers))
        else:
            break

    reverse_flag, keywordlist = keywords(question)
    ans = answer(reverse_flag, keywordlist, answers)

    if len(ans) == 1:
        for i, key in enumerate(answers):
            if ans[0] in key:
                print('\n答案是：%s. %s\n' % (chr(65 + i), key))
                break
    else:
        candicate = []
        for a in ans:
            for i, key in enumerate(answers):
                if a in key:
                    candicate.append('%s. %s' % (chr(65 + i), key))

        print('\n找不到答案，隨便幫你猜一個：%s\n' % random.choice(candicate))

    te = time.time()
    print('Total Cost: %s' % (te - ts))

if __name__ == '__main__':
    while True:
        _main()
