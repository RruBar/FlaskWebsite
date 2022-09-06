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
def home():
    cols,results=get_weather(weather_url)

    index_dict={
        "首頁開頭":"Hi，我叫何柏融，歡迎來到我的個人網站逛逛<br>既然都來了不訪再多看看我的作品😀",
        "聯繫信箱":" hbr199320xy@gmail.com",
        "自我介紹開頭":"關於<strong>我</strong>的事情<br>你/妳可以先知道的是",
        "自我介紹內文":"<h3>目前技能大致大概如下<h3><br>"
                 "<h3><strong style='color:black'>Python:</strong></h3>"
                 "<ul>"
                 "<li>Flask及相關工具(SQLAlchemy 、WTForm)</li>"
                 "<li>爬蟲相關套件(bs4、selenium)</li>"
                 "<li>API串接(如Line Bot)</li>"
                 "<li>GUI相關工具(Tkinter)</li>"
                 "</ul>"
                 "<h3><strong style='color:black'>Html/Css:</strong></h3>基礎架構調整以及Bootstrap模板套用<br>"
                 "<h3><strong style='color:black'>MySQL:</strong></h3>基礎CRUD(可參考作品影片)",
    }
    html_root=flask.render_template("index.html",index=index_dict,cols=cols,results=results,locate_index=True)
    return html_root

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
   app.run(port=8080,debug=True,host='0.0.0.0')
