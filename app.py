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
    db = pymysql.connect(host='localhost', user='de', password='123', database='test')
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
    if pre[0]==2:
        rate=2
        adv="一般"
    if pre[0]==1:
        rate=3
        adv="较差"
    if pre[0]==3:
        rate=4
        adv="严重"
    return render_template("index.html",realtime=res[0],
    wind_dir=res[11],humidity=res[10],windspeed=res[12],aqi=res[1],real=realtime_json,
    rank=rate,guide=adv)

#定义app在5000端口运行
if __name__ == '__main__':

    from gevent import pywsgi

    server = pywsgi.WSGIServer(('0.0.0.0',5000),app)
    server.serve_forever()

app.run(debug=True)
