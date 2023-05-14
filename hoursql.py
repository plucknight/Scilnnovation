import requests
import json
import xlwt
import schedule
import time
import pymysql
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0',
    'Cookie': 'ASP.NET_SessionId = ujphwvajts4ufgxsrpe3tqkc'
}

def get_page():
    url = 'http://113.140.66.226:8024/sxAQIWeb/ashx/getDistrict_24Nd.ashx?cityCode=610400'
    response = requests.get(url, headers = headers)
    data = []
    context = json.loads(response.text)
    #print(context)
    da = []
    for i in range(0, 24):
        data.append(context[i].get("TIMEPOINT"))
        data.append(context[i].get("SO2"))
        data.append(context[i].get("NO2"))
        data.append(context[i].get("CO"))
        data.append(context[i].get("O3"))
        data.append(context[i].get("PM10"))
        data.append(context[i].get("PM2_5"))
    for i in range(0, len(data), 7):
        da.append(data[i:i+7])
    return da

def saveData():
    datalist = get_page()
    savepath = ".\\24H污染物数据.xls"
    data = []
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    # 添加一个叫实时数据的工作表，cell_overwrite_ok=True代表可以覆盖已有数据
    sheet = book.add_sheet('近一周AQI变化', cell_overwrite_ok=True)
    col = ("Date",  "SO2", "NO2", "CO", "O3", "PM10", "PM2.5")
    for i in range(0, 7):
        sheet.write(0, i, col[i])
    for i in range(0, 24):
        for j in range(0, 7):
            #data[i][j] = datalist[i][j]
            sheet.write(i+1, j, datalist[i][j])
    print(datalist[0])
    # 打开数据库连接
    db = pymysql.connect(host='localhost', user='root', password='0000', database='fogdata')
    # 创建游标对象
    cursor = db.cursor();
    # # 删除之前数据
    dele = "delete from 24hours"
    cursor.execute(dele)
    # 插入实时数据
    for i in range(0, 24):
      time = datetime.strptime(datalist[i][0], '%Y/%m/%d %H:%M:%S')
      sql = """insert into 24hours values('%s',%s,%s,%s,%s,%s,%s)""" % \
              (time, datalist[i][1], datalist[i][2], datalist[i][3], datalist[i][4], datalist[i][6],datalist[i][5])
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


if __name__=="__main__":
    #测试用
    saveData()
    #实际每隔一小时重新读取一次数据
    '''
    saveData()
    schedule.every().hour.at(":00").do(saveData)
    while True:
        schedule.run_pending()
        time.sleep(1)
    '''
