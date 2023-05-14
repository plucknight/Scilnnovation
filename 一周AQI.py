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
    url = 'http://113.140.66.226:8024/sxAQIWeb/ashx/getCity_7DayAQI.ashx?cityName=610400'
    response = requests.get(url, headers = headers)
    data = []
    context = json.loads(response.text)
    #print(context)
    da = []
    for i in range(0, 7):
        data.append(context[i].get("TIMEPOINT"))
        data.append(context[i].get("AQI"))
        data.append(context[i].get("PRIMARYPOLLUTANT"))
        data.append(context[i].get("QUALITY"))
    for i in range(0, 28, 4):
        da.append(data[i:i+4])
    return da

def saveData():
    datalist = get_page()
    savepath = ".\\一周AQI数据.xls"
    data = []
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)
    # 添加一个叫实时数据的工作表，cell_overwrite_ok=True代表可以覆盖已有数据
    sheet = book.add_sheet('近一周AQI变化', cell_overwrite_ok=True)
    col = ("日期", "AQI", "首要污染物", "空气质量级别")
    for i in range(0, 4):
        sheet.write(0, i, col[i])
    for i in range(0, 7):
        for j in range(0, 4):
            sheet.write(i+1, j, datalist[i][j])
    print(datalist)
    # 打开数据库连接
    db = pymysql.connect(host='localhost', user='root', password='0000', database='fogdata')
    # 创建游标对象
    cursor = db.cursor();
    # # 删除之前数据
    dele = "delete from weekAQI"
    cursor.execute(dele)
    # 插入实时数据
    for q in range(0, 7):
        sql = """insert into weekAQI values('%s',%s)""" % \
                  (datalist[q][0], datalist[q][1])
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
    #实际每隔一天重新读取一次数据
    '''
    saveData()
    schedule.every().day.at("00:00").do(saveData)
    while True:
        schedule.run_pending()
        time.sleep(1)
    '''
