#! /usr/bin/python3
import io
import re
import time
from google.cloud.vision import types
from google.cloud import vision
from hashlib import md5
from PIL import Image
from PIL import ImageGrab
import pytesseract


client = vision.ImageAnnotatorClient()

class Game(object):
    def __init__(self, x, y, width, height):

        ## The frame position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # 全螢幕參數版本
        self.question = tuple(
            map(lambda x: int(x), [
                self.x + 42,
                self.y + 515,
                self.x + 860,
                self.y + 860
                #self.x + self.width * 0.04636,
                #self.y + self.height * 0.321875,
                #self.x + self.width * 0.94923,
                #self.y + self.height * 0.5375
            ])
        )

        self.answers = []

        # 全螢幕參數版本
        ans_height = 100
        ans_displace = 135
        #ans_height = self.height * 0.0625
        #ans_displace = ans_height + self.width * 0.035

        # 全螢幕參數版本
        for i in range(4):
            ans = tuple(
                map(lambda x: int(x), [
                    self.x + 80,
                    self.y + 895 + i * (ans_displace),
                    self.x + 800,
                    self.y + 995 + i * (ans_displace)
                ])
            )
            self.answers.append(ans)

    def grab(self, x, y, width, height):
        img = ImageGrab.grab((x, y, width, height))
        return img

    def ishow(self, x, y, w, h):
        img = ImageGrab.grab((x, y, w, h))
        img.show()

    def show(self, image):
        image.show()

def grabtext(cordinate):
    img = ImageGrab.grab(cordinate)
    # Change to using google's vision api
    return _totext_g(img)

def _totext_g(img):
    name = '/tmp/%s.png' % md5(bytes(str(time.time()).encode())).hexdigest()
    img.save(name)

    with io.open(name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    return texts[0].description.replace('\n', '')

def _totext(image):
    # Image To Text Function
    # Image should be PIL.Image format
    t = pytesseract.image_to_string(image, lang='chi_tra+eng', config='')
    t = t.replace('\n', '')
    return re.sub(r'[-@#$%^&*()]', '', t).strip()
