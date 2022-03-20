# smtplib 用于邮件的发信动作
import smtplib
from email.mime.text import MIMEText
# email 用于构建邮件内容
from email.header import Header
import datetime
import linecache
import requests
import json
import time
from http.server import BaseHTTPRequestHandler
import  re
from datetime import datetime
import pytz

# 获取天气
def getweather():
    r_sh = requests.get("http://www.weather.com.cn/data/sk/101020100.html")
    r_sh.encoding = 'utf-8'
    r_cd = requests.get("http://www.weather.com.cn/data/sk/101270101.html")
    r_cd.encoding = 'utf-8'

    weather_sh = str(r_sh.json()['weatherinfo']['city']) + " " + str(r_sh.json()['weatherinfo']['WD']) + " " + str(
        r_sh.json()['weatherinfo']['temp'])
    weather_cd = str(r_cd.json()['weatherinfo']['city']) + " " + str(r_cd.json()['weatherinfo']['WD']) + " " + str(
        r_cd.json()['weatherinfo']['temp'])

    return weather_sh, weather_cd

# 获取微博热搜
def get_data():
    """微博热搜
    Args:
        params (dict): {}
    Returns:
        json: {title: 标题, url: 地址, num: 热度数值, hot: 热搜等级}
    """

    data = []
    response = requests.get("https://weibo.com/ajax/side/hotSearch")
    data_json = response.json()['data']['realtime']
    jyzy = {
        '电影': '影',
        '剧集': '剧',
        '综艺': '综',
        '音乐': '音'
    }

    for data_item in data_json:
        hot = ''
        # 如果是广告，则不添加
        if 'is_ad' in data_item:
            continue
        if 'flag_desc' in data_item:
            hot = jyzy.get(data_item['flag_desc'])
        if 'is_boom' in data_item:
            hot = '爆'
        if 'is_hot' in data_item:
            hot = '热'
        if 'is_fei' in data_item:
            hot = '沸'
        if 'is_new' in data_item:
            hot = '新'

        dic = {
            'title': data_item['note'],
            'url': 'https://s.weibo.com/weibo?q=%23' + data_item['word'] + '%23',
            'num': data_item['num'],
            'hot': hot
        }
        data.append(dic)

    return data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = get_data()
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        return

if __name__ == '__main__':
    # 获取今天（现在时间）
    tz = pytz.timezone('Asia/Shanghai')  # 东八区
    t = datetime.fromtimestamp(int(time.time()),
    pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S %Z%z')

    time = t
    today = str(time)
    Today = today[:10]
    day = int(Today[8:])

    # 获取文案
    words = linecache.getline('words.txt', day)

    [weather_sh, weather_cd] = getweather()

    data = get_data()
    title = []
    url = []
    item = ""
    for i in range(0, len(data)):
        title.append(data[i]['title'])
        url.append(data[i]['url'])
        item = item +"NO."+str(i+1)+" "+title[i]+'\n'+url[i]+'\n'

    body = "今日天气："+'\n'+weather_cd+'\n'+weather_sh+'\n'+'\n'+"微博热搜("+today[:19]+")："+'\n'+item



    # 用于构建邮件头

    # 发信方的信息：发信邮箱，QQ 邮箱授权码
    from_addr = '1213719606@qq.com'
    password = 'gxipqdrqcaptbach'

    # 收信方邮箱
    to_addr = '2901003755@qq.com'

    # 发信服务器
    smtp_server = 'smtp.qq.com'

    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    msg = MIMEText(body, 'plain', 'utf-8')

    # 邮件头信息
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header(Today+" "+words)



    # 开启发信服务，这里使用的是加密传输
    server=smtplib.SMTP_SSL(smtp_server)
    server.connect(smtp_server, 465)
    # 登录发信邮箱
    server.login(from_addr, password)
    # 发送邮件
    server.sendmail(from_addr, to_addr, msg.as_string())
    # 关闭服务器
    server.quit()
