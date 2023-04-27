import json
import threading
import time

import qrcode
import requests
import tkinter as tk
from PIL import ImageTk, Image

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
    return data


class QRCodeWindow:
    def __init__(self, data):
        self.data = data
        self.root = tk.Tk()
        self.root.title("QR Code")
        self.qr_code_image = self.make_qrcode(data)
        label = tk.Label(self.root, image=self.qr_code_image)
        label.pack()

    def make_qrcode(self, data):
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data["url"])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black")
        img = img.convert('RGB')
        img = ImageTk.PhotoImage(img)
        return img

    def verify_qr(self):
        while True:
            time.sleep(1) # 每秒轮询一次
            # 检查二维码状态
            token = self.data['key']
            requests.session()
            url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}&source=main-fe-header'
            resp = requests.get(url,headers=header)
            code = resp.json()
            print(code['data']['code'])
            if code['data']['code'] == 0:
                cookie = dict(resp.cookies)
                save_cookie(cookie)
                self.root.destroy()
                break


    def run(self):
        # 启动二维码验证线程
        t = threading.Thread(target=self.verify_qr)
        t.daemon = True
        t.start()
        self.root.mainloop()


def save_cookie(data):
    with open('test.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def run_main():
    data = get_qr_data()
    token = data['key']
    window = QRCodeWindow(data)
    window.run()
    test()



def test():
    with open('test.json', 'r') as f:
        cookie = dict(json.load(f))
        url = 'https://api.bilibili.com/x/web-interface/nav'
        test = requests.get(url, headers=header, cookies=cookie)
        print(test.text)


if __name__ == "__main__":
    run_main()