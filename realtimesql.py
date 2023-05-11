import pymysql
import re
import requests
import json
import xlwt
import time
import schedule
from datetime import datetime

#ts = time.time()
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
        'Cookie': 'ASP.NET_SessionId = ujphwvajts4ufgxsrpe3tqkc'
}
headers1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    'Cookie': 'Hm_lvt_fd8bd7e3cafffdfe92d0bdbc68de70f1=1669964373; Hm_lpvt_fd8bd7e3cafffdfe92d0bdbc68de70f1=1669964373; __gads=ID=b31936f18d2dbef3-226c1f36b2d8003d:T=1669964373:RT=1669964373:S=ALNI_Ma7S65eyuWUF1Ju1gxzBC53HELfcg; __gpi=UID=00000b884f21c71a:T=1669964373:RT=1669964373:S=ALNI_MbWJNZRlXdZrbyLubjOPXk_VT2GvQ'
}

def get_page():
    url = 'http://113.140.66.226:8024/sxAQIWeb/PageCity.aspx?cityCode=NjEwNDAw'
    response = requests.get(url, headers = headers)
    data = []
    #dt = datetime.fromtimestamp(ts)
    #data.append(str(dt))
    try:
        if response.status_code == 200:
            response.encoding = 'utf-8'
            html = response.text
            #print(html)
            #获取当前时间(准确到小时)
            time = re.findall('<span id="ctl00_ContentPlaceHolder1_labTime">(.*?)</span>', html, re.S)
            #print('当前时间'+str(time))
            data.append(time)
            #获取当前aqi
            aqi = re.findall('<span id="ctl00_ContentPlaceHolder1_labAQI" class="zk_c">(\d+)</span>', html, re.S)
            #print('AQI'+str(aqi))
            data.append(aqi)
            #获取污染名称
            levelname = re.findall('<span id="ctl00_ContentPlaceHolder1_labLevelName">(\w+)</span>', html, re.S)
            #print('天气状况'+str(levelname))
            data.append(levelname)
            #获取污染等级
            level = re.findall('<span id="ctl00_ContentPlaceHolder1_labLevel">(\w+)</span>', html, re.S)
            #print('天气等级：'+str(level))
            data.append(level)
            #首要污染物
            mainindex = re.findall('<span id="ctl00_ContentPlaceHolder1_labMainIndex">(.*?)</span>', html, re.S)
            #print('首要污染物：'+str(mainindex))
            data.append(mainindex)
    except:
        print('数据获取失败！')
    '''
    url2 = 'https://www.tianqi24.com/xianyang/'
    response2 = requests.get(url=url2, headers=headers1)
    try:
        if response2.status_code == 200:
            response2.encoding = 'utf-8'
            inf = response2.text
            #空气湿度
            humid = re.findall('<div class="info"><span>(\w+)</span>', inf, re.S)
            data.append(humid)
            #风向
            wind = re.findall('<div class="info"><span>湿度 39%</span><span>(\w+)</span>', inf, re.S)
            data.append(wind)
    except:
        print('数据2获取失败！')
    '''
    #获取实时浓度信息
    url3 = 'http://113.140.66.226:8024/sxAQIWeb/ashx/getDistrict_24Nd.ashx?cityCode=610400'
    response3 = requests.get(url=url3, headers=headers)
    page = response3.text
    #info是list类型
    info = json.loads(page)
    #info是dict类型=
    #print('实时浓度信息：' + info[24])
    data.append(info[24].get("SO2"))
    data.append(info[24].get("NO2"))
    data.append(info[24].get("CO"))
    data.append(info[24].get("O3"))
    data.append(info[24].get("PM10"))
    data.append(info[24].get("PM2_5"))

    url2 = 'https://www.tianqi24.com/xianyang/'
    response2 = requests.get(url=url2, headers=headers1)
    try:
        if response2.status_code == 200:
            response2.encoding = 'utf-8'
            inf = response2.text
            # print(inf)
            # 当前时间
            time = re.findall('<div class="mainright">.*?<text id="nowHour">(?P<time>.*?)</text>', inf, re.S)
            data.append(time)
            # 空气湿度
            humid = re.findall('<div class="info">.*?<span>湿度 (?P<humid>.*?)</span>.*?</div>', inf, re.S)
            # print(humid)
            data.append(humid)
            # 风向
            wind = re.findall('<div class="info">.*?<span>.*?</span>.*?<span>(?P<wind>.*?)</span>.*?</div>', inf, re.S)
            # print(wind)
            data.append(wind)
            # 风速
            speed = re.findall('<dd>风速： (?P<speed>.*?) <i>.*?</i></dd>', inf, re.S)
            # print(speed)
            data.append(speed)
            # 能见度
            sight = re.findall('<dd title="咸阳能见度">能见度： (\d+) <i>km</i></dd>', inf, re.S)
            # print(sight)
            data.append(sight)
            # print(data)
    except:
        print('数据获取失败！')
    return data

def saveData():
    datalist = get_page()
    savepath = ".\\实时数据.xls"
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    #添加一个叫实时数据的工作表，cell_overwrite_ok=True代表可以覆盖已有数据
    sheet = book.add_sheet('实时数据', cell_overwrite_ok=True)
    col = ("当前时间", "AQI", "天气状况", "天气等级", "首要污染物", "SO2浓度"
        "(微克/立方米)", "NO2浓度(微克/立方米)", "CO浓度(毫克/立方米)", "O3浓度(微克/立方米)", "PM10"
        "浓度(微克/立方米)", "PM2.5浓度(微克/立方米)","当前时间", "湿度", "风向", "风速", "能见度(km)")
    for i in range(0, 16):
        sheet.write(0, i, col[i])#输出表头到excel第一行
    data = datalist
    for j in range(0, 16):
        sheet.write(1, j, data[j])
    print(data)
    # 打开数据库连接
    db = pymysql.connect(host='localhost', user='root', password='0000', database='fogdata')
    # 创建游标对象
    cursor = db.cursor();
    #删除之前数据
    dele="delete from realtime"
    cursor.execute(dele)
    #插入实时数据
    time = datetime.strptime(data[0][0], '%Y-%m-%d %H 时')
    sql="""insert into realtime values('%s',%s,'%s','%s',%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s')"""%\
          (time,data[1][0],data[3][0],data[4][0],data[5],data[6],\
           data[7],data[8],data[10],data[9],data[12][0],data[13][0],data[14][0],data[15][0])
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
        print("ok")
    except pymysql.Error as e:
        print(e.args[0], e.args[1])
        # 如果发生错误则回滚
        db.rollback()

    # 关闭数据库连接
    db.close()
    book.save(savepath)
    print("save..")

if __name__ == "__main__":
    saveData()
'''
    schedule.every().hour.at(":00").do(saveData)
    while True:
        schedule.run_pending()
        time.sleep(1)
        (date,aqi,haze_level,main_pollution,so2,no2,co,o3,pm2,pm10)
'''