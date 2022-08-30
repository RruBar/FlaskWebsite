# 測試 請透過
# http://127.0.0.1:5000/
# http://127.0.0.1:5000/html
# 在 python 執行檔的目錄下，創建 templates/ 資料夾
# 本程式.py
# templates/data1.html
# templates/data2.html
import datetime
import smtplib
import requests
import flask     # pip install flask
#  SSL  處理，  https    SSSSSS 就需要加上以下2行
import ssl
ssl._create_default_https_context = ssl._create_unverified_context    # 因.urlopen發生問題，將ssl憑證排除


app = flask.Flask(__name__,static_url_path='/static')
weather_url="https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314"

def get_weather(url:str):
    response = requests.get(url)
    data=response.json()
    data=data["records"]["location"]
    cols=["縣市","現在天氣","氣溫","降雨機率"]
    results=[]
    for i in data:
        now_weather=i["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        low_temp=i["weatherElement"][2]["time"][0]["parameter"]["parameterName"]
        high_temp=i["weatherElement"][4]["time"][0]["parameter"]["parameterName"]
        rain_percent=i["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        results.append([i["locationName"],now_weather,f"{low_temp}~{high_temp}度",f"{rain_percent}%"])
    return cols,results

@app.route("/")
def fun1():
    cols,results=get_weather(weather_url)

    index_dict={
        "首頁開頭":"現在都用冨樫老師的推特<br>來當作持續學習的勉勵",
        "聯繫信箱":" hbr199320xy@gmail.com",
        "自我介紹開頭":"關於<strong>我</strong>的事情<br>你/妳可以先知道的是",
        "自我介紹內文":"三十而立的話，那我應該還在學爬?<br>目前正值字面意思上的二八年華，會的東西大概如下<br>"
                 "Python還在慢慢學；Html/Css程度可讓我套這模板<br>SQL、NoSQL都還要再多學學；雖有去leetcode寫題目，但多還是被洗臉QQ",
        "底部標題":"很高興妳/你能來造訪我的網站!<br>再次<strong>感謝</strong>您"
    }
    html_root=flask.render_template("index.html",index=index_dict,cols=cols,results=results,locate_index=True)
    return html_root

@app.route("/index.html")
def index():
    cols,results=get_weather(weather_url)

    index_dict={
        "首頁開頭":"現在都用冨樫老師的推特<br>來當作持續學習的勉勵",
        "聯繫信箱":" hbr199320xy@gmail.com",
        "自我介紹開頭":"關於<strong>我</strong>的事情<br>你/妳可以先知道的是",
        "自我介紹內文":"三十而立的話，那我應該還在學爬?<br>目前正值字面意思上的二八年華，會的東西大概如下<br>"
                 "Python還在慢慢學；Html/Css程度可讓我套這模板<br>SQL、NoSQL都還要再多學學；雖有去leetcode寫題目，但多還是被洗臉QQ",
    }
    html_index=flask.render_template("index.html",index=index_dict,cols=cols,results=results,locate_index=True)
    return html_index
@app.route("/contact.html",methods=["GET","POST"])
def contact():
    if flask.request.method == "POST":
        name=flask.request.form['name']
        email=flask.request.form['email']
        message=flask.request.form['message']
        my_email = "hbr199320xy@gmail.com"
        password = "yexygujqzqirarkc"
        with smtplib.SMTP_SSL("smtp.gmail.com",timeout=120) as connect:
            connect.login(user=my_email,password=password)
            connect.sendmail(from_addr=my_email,
                             to_addrs=my_email,
                             msg=f"Subject:有人寄信給你囉~\n\n"
                                 f"留訊者:{name}\nE-mail:{email}\n"
                                 f"留言內容:{message}".encode("utf-8"))
        return flask.render_template("contact.html",msg_sent=True,locate_index=False)
    return flask.render_template("contact.html",msg_sent=False,locate_index=False)

@app.route("/blog.html")
def blog():
    html_blog=flask.render_template("blog.html",locate_index=False)
    return html_blog

@app.route("/blog-detail.html")
def blog_detail():
    html_blog_detail=flask.render_template("blog-detail.html",locate_index=False)
    return html_blog_detail

@app.route("/project-detail.html")
def project_detail():
    html_project_detail=flask.render_template("project-detail.html",locate_index=False)
    return html_project_detail



if __name__ == '__main__':
   app.run(port=80,debug=True,host='0.0.0.0')
