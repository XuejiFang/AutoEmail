# smtplib 用于邮件的发信动作
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# email 用于构建邮件内容
from email.header import Header
from email.mime.application import MIMEApplication
import datetime
import linecache
import requests
import json
import time
from http.server import BaseHTTPRequestHandler
import  re
from datetime import datetime
import pytz
from PyPDF2 import PdfFileWriter, PdfFileReader
import os.path

# 获取天气
def get_weather_city(url):
    # open url and get return data
    r = requests.get(url)
    if r.status_code != 200:
        log.error("Can't get weather data!")

    # convert string to json
    info = json.loads(r.content.decode())

    # get useful data
    data = info['weatherinfo']
    city = data['city']
    temp1 = data['temp1']
    temp2 = data['temp2']
    weather = data['weather']
    return "{} {} {}~{}".format(city, weather, temp1, temp2)
def get_weather_wind(url):
    r = requests.get(url)
    if r.status_code != 200:
        log.error("Can't get weather data!")
    info = json.loads(r.content.decode())

    # get wind data
    data = info['weatherinfo']
    WD = data['WD']
    WS = data['WS']
    return "{}({})".format(WD, WS)

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

def CET(t):
    time = t
    today = str(time)
    Today = today[:10]

    d1 = datetime.strptime('2022-03-20','%Y-%m-%d')   # 第一个日期
    d2 = datetime.strptime(Today,'%Y-%m-%d')   # 第二个日期
    interval = d2 - d1                   # 两日期差距
    # interval.days                        # 具体的天数
    print(str(interval))

    # 开始页
    start = str(interval).split(' ')
    start_page = int(start[0])-1
    # 截止页
    end_page = start_page+1

    output = PdfFileWriter()
    pdf_file = PdfFileReader(open("cet-6.pdf", "rb"))
    pdf_pages_len = pdf_file.getNumPages()

    # 保存input.pdf中的1-5页到output.pdf
    for i in range(start_page, end_page):
        output.addPage(pdf_file.getPage(i))

    outputStream = open("CET/CET-6 "+str(Today)+".pdf", "wb")
    output.write(outputStream)

if __name__ == '__main__':
    weather = """**天气提醒**:  

    {} {}  
    {} {}  

    来源: 国家气象局
    """.format(
        get_weather_city('http://www.weather.com.cn/data/cityinfo/101270106.html'),
        get_weather_wind('http://www.weather.com.cn/data/sk/101270106.html'),
        get_weather_city('http://www.weather.com.cn/data/cityinfo/101020300.html'),
        get_weather_wind('http://www.weather.com.cn/data/sk/101020300.html')
    )


    # 获取今天（现在时间）
    tz = pytz.timezone('Asia/Shanghai')  # 东八区
    t = datetime.fromtimestamp(int(time.time()),
    pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S %Z%z')



    time = t
    today = str(time)
    Today = today[:10]
    day = int(Today[8:])

    CET(t)
    file_name = r"CET-6 " + str(Today) + ".pdf"


    # 获取文案
    words = linecache.getline('words.txt', day)



    data = get_data()
    title = []
    url = []
    item = ""
    for i in range(0, 10):
        title.append(data[i]['title'])
        url.append(data[i]['url'])
        item = item +"NO."+str(i+1)+" "+title[i]+'\n'+url[i]+'\n'

    body = weather+'\n'+'\n'+"**微博热搜("+today[:19]+")：**"+'\n'+item



    # 用于构建邮件头

    # 发信方的信息：发信邮箱，QQ 邮箱授权码
    from_addr = '1213719606@qq.com'
    password = 'gxipqdrqcaptbach'

    # 收信方邮箱
    to_addr = ['Jaggar.Fang@hotmail.com']
    to_addr2 = ['fangxueji@foxmail.com']
    # 发信服务器
    smtp_server = 'smtp.qq.com'

    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    #msg = MIMEText(body, 'plain', 'utf-8')
    textApart = MIMEText(body)
    msg = MIMEMultipart()

    # 邮件头信息
    msg['From'] = Header(from_addr)
    msg['To'] = ','.join(to_addr)
    msg['Subject'] = Header(Today+" "+words)

    pdfApart = MIMEApplication(open(file_name, 'rb').read())
    pdfApart.add_header('Content-Disposition', 'attachment', filename=file_name)

    msg.attach(textApart)
    msg.attach(pdfApart)

    # 开启发信服务，这里使用的是加密传输
    server=smtplib.SMTP_SSL(smtp_server)
    server.connect(smtp_server, 465)
    # 登录发信邮箱
    server.login(from_addr, password)
    # 发送邮件
    server.sendmail(from_addr, to_addr, msg.as_string())
    # server.sendmail(from_addr, to_addr2, msg.as_string())

    # 关闭服务器
    server.quit()
