import numpy as np  
import matplotlib.pyplot as plt  
from sklearn.cluster import KMeans 
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_blobs   #生成数据函数  
from sklearn import metrics
import pandas as pd
import json
from flask import Flask, render_template, request, jsonify
import pymysql
from datetime import date, datetime

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def sort(pre):
    df=pd.read_csv("train.csv")
    df['Date']=pd.to_datetime(df['Date'])
    df.sort_values(by=['Date'],inplace=True,ascending=True)
    dataset=np.array(df)
    data=dataset[:,1]
    X=data.reshape(-1, 1)
    kmeans = KMeans(n_clusters=4).fit(X)
    c=kmeans.labels_
    pre=np.array([[pre]])
    pre.reshape(-1,1)
    return kmeans.predict(pre)
#创建Flask对象app并初始化
app = Flask(__name__)

#通过python装饰器的方法定义路由地址
@app.route("/")
#定义方法 用jinjia2引擎来渲染页面，并返回一个index.html页面
def root():
    db = pymysql.connect(host='localhost', user='root', password='0000', database='fogdata')
    cursor = db.cursor()
    cursor.execute("select * from realtime")
    fields=cursor.description           #获取字段名
    res=cursor.fetchone()
    print(res)
    col_list=[]
    for i in fields:
       col_list.append(i[0])
    realtime={}
    for i in range(1,len(col_list)):
        realtime[col_list[i]] = res[i]
    realtime_json= json.dumps(realtime, ensure_ascii=False)
    print(realtime_json)
    pre =sort(res[8])
    print(pre)
    rate=1
    adv="良好"
    if pre[0]==0:
        rate=1
        adv="良好"
    if pre[0]==2:
        rate=2
        adv="一般"
    if pre[0]==1:
        rate=3
        adv="较差"
    if pre[0]==3:
        rate=4
        adv="严重"
    #查询weekaqi
    cursor.execute("select * from weekaqi")
    result=cursor.fetchall()
    fields=cursor.description           #获取字段名
    col_list2=[]
    temp={}
    week={}                     #一周aqi数据
    for i in fields:
       col_list2.append(i[0])
    for x in range(0,7):
        for y in range(0,2):
           temp[col_list2[y]] = result[x][y]
        week[x]=temp
        temp={}
    week_json= json.dumps(week, ensure_ascii=False)
    #查询24past数据
    cursor.execute("select * from 24hours")
    result=cursor.fetchall()
    fields=cursor.description           #获取字段名
    col_list3=[]
    temp={}
    data24={}                     #一周aqi数据
    for i in fields:
       col_list3.append(i[0])
    print(result[0],result[1])
    for x in range(0,len(result)):
        for y in range(0,7):
           temp[col_list3[y]] = result[x][y]
        data24[x]=temp
        temp={}
    day_json= json.dumps(data24, cls=ComplexEncoder)
    print(day_json)
    cursor.close()
    return render_template("index.html",realtime=res[0],
    wind_dir=res[11],humidity=res[10],windspeed=res[12],aqi=('%.0f'%res[1]),real=realtime_json,
    rank=rate,guide=adv,aqi7=week_json,past24=day_json)

#定义app在5000端口运行
if __name__ == '__main__':

    from gevent import pywsgi

    server = pywsgi.WSGIServer(('0.0.0.0',5000),app)
    server.serve_forever()

app.run(debug=True)
