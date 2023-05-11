import json
import os
import threading
import tkinter as tk
import qrcode
import requests
from PIL import ImageTk

url1 = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main_web"
header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 "
                  "Safari/537.36 Edg/112.0.1722.58"
}


def get_qr_data():  # 获取二维码数据
    results = requests.get(url1, headers=header)
    resulting = results.json()
    code = resulting["code"]
    qrcode_url = resulting['data']["url"]
    qrcode_key = resulting['data']['qrcode_key']
    data = {"code": code, "url": qrcode_url, 'key': qrcode_key}
    return data


def make_qrcode(data):  # 生成二维码
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


def load_json(data):  # 读取json文件
    if isinstance(data, str):
        # 如果数据是字符串，则使用 json.loads() 函数将其转换为 Python 对象
        return json.loads(data)
    else:
        # 如果数据是文件对象，则使用 json.load() 函数将其转换为 Python 对象
        return dict(json.load(data))


def save_ini(data, ini):  # 保存cookie
    id = ini['data']['mid']
    file_path = os.getcwd() + '\\config\\'
    file_path_cookie = os.path.join(file_path, f"{id}.json")
    file_path_user = os.path.join(file_path, f"{id}.ini")
    with open(file_path_cookie, 'w+') as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()
    with open(file_path_user, 'w+') as f:
        f.write(f'{ini}')
        f.close()


def run_main():  # 主函数
    data = get_qr_data()
    window = QRCodeWindow(data)
    window.run()
    # test()


def verify_cookie(reback):  # 验证cookie
    cookies = load_json(reback)
    url = 'https://api.bilibili.com/x/web-interface/nav'
    resp = requests.session().get(url, headers=header, cookies=cookies)
    get_status = resp.json()
    resp.close()
    print(get_status)
    if get_status['message'] == '0':
        print('cookie未失效')
    else:
        print('cookie失效')


class QRCodeWindow:  # 二维码窗口
    def __init__(self, data):
        self.data = data
        self.root = tk.Tk()
        self.root.title("QR Code")
        self.qr_code_image = make_qrcode(data)
        label = tk.Label(self.root, image=self.qr_code_image)
        label.pack()

    def verify_qr(self):
        while True:
            # time.sleep(1) # 每秒轮询一次
            # 检查二维码状态
            token = self.data['key']
            # requests.session()
            url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={token}' \
                  f'&source=main-fe-header'
            resp = requests.get(url, headers=header)
            code = resp.json()
            print(code['data']['code'])
            if code['data']['code'] == 0:
                url = 'https://api.bilibili.com/x/web-interface/nav'
                get_ini = requests.get(url, headers=header, cookies=resp.cookies)
                ini = get_ini.json()
                cookie = dict(resp.cookies)
                save_ini(cookie, ini)
                self.root.destroy()
                break

    def land(self):
        dir_path = os.getcwd() + '\\config\\'  # 文件夹路径
        file_suffix = ".json"
        file_names = os.listdir(dir_path)  # 获取文件夹下的所有文件和文件夹的名称
        if not file_names:
            self.tread()
        else:
            for file_name in file_names:
                if file_name.endswith(file_suffix):
                    file_path = os.path.join(dir_path, file_name)
                    content = open(file_path, 'r')
                    reback = content.read()
                    if reback == '':
                        self.tread()
                    else:
                        verify_cookie(reback)

    def tread(self):
        t = threading.Thread(target=self.verify_qr)
        t.daemon = True
        t.start()
        self.root.mainloop()

    def run(self):
        self.land()


if __name__ == "__main__":
    run_main()
