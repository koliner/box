import json

import qrcode
import requests

url1 = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main_web"
header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 "
                  "Safari/537.36 Edg/112.0.1722.58"
}


def get_qr_data():
    results = requests.get(url1, headers=header)
    resulting = results.json()
    code = resulting["code"]
    qrcode_url = resulting['data']["url"]
    qrcode_key = resulting['data']['qrcode_key']
    data = {"code": code, "url": qrcode_url, 'key': qrcode_key}
    # print(data)
    return data


def make_qrcode(data):
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data["url"])
    qr.make(fit=True)
    # fill_color和back_color分别控制前景颜色和背景颜色，支持输入RGB色，注意颜色更改可能会导致二维码扫描识别失败
    img = qr.make_image(fill_color="black")
    img.show()


def save_cookie(data):
    with open('test.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def run_main():
    data = get_qr_data()
    token = data['key']
    make_qrcode(data)
    url2 = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}&source=main_web'
    client = requests.get(url2, headers=header)
    get = client.json()
    code_status = get['data']['code']
    print(get)
    while True:
        print(f'{code_status}')
        if code_status == 0:
            cookie = dict(client.cookies)
            save_cookie(cookie)
            break


def test():
    with open('test.json', 'r') as f:
        cookie = dict(json.load(f))
        url = 'https://api.bilibili.com/x/web-interface/nav'
        test = requests.get(url, headers=header, cookies=cookie)
        print(test.text)


if __name__ == "__main__":
    test()
# data = get_qr_data()
# token = data['key']
# make_qrcode(data)
# #url2 = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}&source=main_web'
# url2 = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}&source=main-fe-header'
# client = requests.get(url2, headers=header)
# get = client.json()
# code_status = get['data']['code']
# message = get['data']['message']
# #print(client)
# # print(f'{code_status}&{message}')
# while True:
#     client = requests.get(url2, headers=header)
#     get = client.json()
#     code_status = get['data']['code']
#     message = get['data']['message']
#     print(f'{code_status}&{message}')
#     if code_status == 0:
#         break
