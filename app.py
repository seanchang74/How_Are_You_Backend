# -*-coding:utf-8-*-
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
from imgur_python import Imgur
from matplotlib import image
import urllib.request
from opencc import OpenCC
from cnsenti import Emotion
from imgur_python import Imgur
from final_version_transfer import transfer_img, load_image
from flask import Flask, request, redirect, url_for
app = Flask(__name__)
# cc
cc = OpenCC('tw2sp')
# cnsenti
emotion = Emotion()
# imgur setting
imgur_client = Imgur({'client_id': 'df49f569292a567',
                      "client_secret": "56f9a51456aeeed047448c8b1753e8b8e4fd0e72",
                      'account_username': 'ntuejcwang',
                     "access_token": '1fddc4c11d82df9142c6894ef1005871fcc7edc3'})

# ai image upload


def upload(file_name, file_path):
    description = 'Image description'
    # ai album_ids
    album = "tBuafXp"
    disable_audio = 0
    print("Uploading image... ")
    try:
        # imgur upload api
        response = imgur_client.image_upload(
            file_path, file_name, description, album, disable_audio)
        image_url = response['response']['data']['link']
        print(image_url)
        print("Done")
        return image_url

    except Exception as e:
        print(e)
        pass

# user image download


def download(file_name, file_url):
    try:

        image_path = "./img/user/{}".format(file_name)
        urllib.request.urlretrieve(file_url,
                                   image_path)
        myapp.info("download successful")
        return image_path
    except Exception as e:
        myapp.error("download failed")
        myapp.error(e)
        pass


def ai_upload(content_path, style):
    myapp.info("AI upload")
    try:
        url = {}
        num = 0
        style_path = "img/mood/"
        content_image = load_image(content_path)
        # print(style)
        # if-else
        if style == "恶":
            style_path += "disgusting/"
        elif style == "惊":
            style_path += "surprised/"
        elif style == "惧":
            style_path += "fear/"
        elif style == "怒":
            style_path += "anger/"
        elif style == "哀":
            style_path += "depression/"
        elif style == "乐":
            style_path += "happy/"
        elif style == "好":
            style_path += "great/"

        allfile = os.listdir(style_path)
        backup_path = style_path
        for file in allfile:
            style_path = backup_path
            style_path += file
            style_image = load_image(style_path)
            myapp.info("Start transfer")
            file_path = transfer_img(content_image, style_image)
            myapp.info("Start upload")
            url[str(num)] = upload(str(datetime.now()), file_path)
            myapp.info("End num {}".format(num))
            num += 1
        print(type(url))
        return url
    except Exception as e:
        myapp.error("Ai error: " + str(e))
        pass

# logging初始化


def setup_logger(logger_name, level=logging.INFO):
    myapp = logging.getLogger(logger_name)
    myapp.setLevel(level)

    # 设置格式
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

    # 控制台输出
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    # 滚动文件输出
    # rotatingHandler = logging.handlers.RotatingFileHandler(
    #     'log/mylog.log', maxBytes=5*1024*1024, backupCount=5)

    rotatingHandler = RotatingFileHandler(
        "log/flask.log", maxBytes=5*1024, backupCount=20)
    rotatingHandler.setFormatter(formatter)

    myapp.addHandler(streamHandler)
    myapp.addHandler(rotatingHandler)
# ================================================================================================================================


@app.route("/")
def hello():
    myapp.info("Hello Flask!")
    return "Hello Flask!"


@app.route('/submit', methods=['GET'])
def submit():
    try:
        myapp.info("submit")
        # download image from imgur
        imgur_path = download(request.args.get('file_name'),
                              request.args.get('file_url'))
        myapp.info(imgur_path)
        emotion_text = request.args.get('emotion_text')
        # 繁轉簡
        emotion_text = cc.convert(emotion_text)
        myapp.info(emotion_text)
        # print("get : emotion_text => ", emotion_text)
        return redirect(url_for('ai_handler', emotion_text=emotion_text, action="get", path=imgur_path))
    except Exception as e:
        myapp.error("submit error: " + str(e))
        pass


# 傳給AI處理
@app.route('/ai_handler/<action>')
def ai_handler(action):
    try:
        myapp.info("AI handle")
        # 情緒文字
        emotion_text = request.args.get('emotion_text')
        # 圖片路徑
        path = request.args.get('path')

        # 情緒分析結果
        result = emotion.emotion_count(emotion_text)
        del result["sentences"]
        del result["words"]
        myapp.info(result)
        # print(reversed(sorted(result.items(), key=lambda x: x[1])))
        result0 = sorted(result.items(), key=lambda x: x[1])[-1][0]
        # list1 = (path, result0)
        # print(list1)
        url = ai_upload(path, result0)
        # url = "url"
        myapp.info(url)
    except Exception as e:
        myapp.error("handle error: " + str(e))
        pass
    return url


@app.errorhandler(Exception)
def error(e):
    myapp.error(e)
    return '404 Not Found {}'.format(e)


if __name__ == '__main__':
    # app.logger.addHandler(handler)
    setup_logger("API_Backend")
    myapp = logging.getLogger('API_Backend')
    myapp.info("initialize success")
    app.run(host='0.0.0.0', port=5000)
