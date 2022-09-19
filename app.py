	# -*-coding:utf-8-*-
import webbrowser
from imgur_python import Imgur
from matplotlib import image
from os import path
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
        print("download successful")
        return image_path
    except Exception as e:

        print(e)
        pass

def ai_upload(content_path, style):
    style_path = "img/mood/"
    content_image = load_image(content_path)
    print(style)
    #if-else
    if style == "恶":
        style_path += "disgusting/girl.jpg"
    elif style == "惊":
        style_path += "surprised/firework.jpg"
    elif style == "惧":
        style_path += "fear/depression.jpg"
    elif style == "怒":
        style_path += "anger/anger.jpg"
    elif style == "哀":
        style_path += "depression/ghost_town.jpg"
    elif style == "乐":
        style_path += "happy/bird.jpg"
    elif style == "好":
        style_path += "great/cool.jpg"
    style_image = load_image(style_path)
    file_path = transfer_img(content_image, style_image)
    url = upload("Test 2", file_path)
    return url
# ================================================================================================================================


@app.route("/")
def hello():
    return "Hello Flask!"


@app.route('/submit', methods=['GET'])
def submit():
    try:
        # download image from imgur
        imgur_path = download(request.args.get('file_name'),
                              request.args.get('file_url'))
        emotion_text = request.args.get('emotion_text')
        # 繁轉簡
        emotion_text = cc.convert(emotion_text)
        print("get : emotion_text => ", emotion_text)
        return redirect(url_for('ai_handler', emotion_text=emotion_text, action="get", path=imgur_path))
    except Exception as e:
        print('here')
        pass	


# 傳給AI處理
@app.route('/ai_handler/<action>')
def ai_handler(action):
    cc = OpenCC('s2twp')
    # 情緒文字
    emotion_text = request.args.get('emotion_text')
    # 圖片路徑
    path = request.args.get('path')

    # 情緒分析結果
    result = emotion.emotion_count(emotion_text)
    del result["sentences"]
    del result["words"]
    print(result)
    # print(reversed(sorted(result.items(), key=lambda x: x[1])))
    result0 = sorted(result.items(), key=lambda x: x[1])[-1][0]
    print(type(path))
    # list1 = (path, result0)
    # print(list1)
    url = ai_upload(path,result0)
    return url


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
