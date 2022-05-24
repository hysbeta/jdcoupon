import json
import threading
import time
import requests
import datetime
import os


url = ''
mycookies = [

]

debug = 1
range_sleep = 0.1  # 间隔时间
delay_time = 0.2
range_n = 20
starttime = 0


PUSH_PLUS_TOKEN = ''
title = '京东抢券成功'
content = []
if "PUSH_PLUS_TOKEN" in os.environ and len(os.environ["PUSH_PLUS_TOKEN"]) > 1:
    PUSH_PLUS_TOKEN = os.environ["PUSH_PLUS_TOKEN"]

def dopost(ck, index, i):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": ck,
        "charset": "UTF-8",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/11.0.0;build/97235;",
        "accept-encoding": "gzip,deflate",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    #print('url------------'+str(url))
    res = requests.post(url=url, headers=headers, timeout=30).json()
    if '成功' in str(res['subCodeMsg']):
        content.append(f"账号{ck[90:-1]}：{res['subCodeMsg']}")
    print(str(datetime.datetime.now())+'-京东账号'+str(index)+'-thread-'+str(i)+':'+str(res['subCodeMsg']))



def jdtime():
    url = 'http://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:

        res = requests.get(url=url, headers=headers, timeout=1).json()
        return int(res['currentTime2'])
    except:
        return int(round(time.time() * 1000))



def use_thread(cookie,index):
    tasks = list()
    for i in range(range_n):
        tasks.append(threading.Thread(target=dopost, args=(cookie, index, i+1)))
    while True:
        if jdtime() >= starttime or debug == 1:
            time.sleep(delay_time)
            for task in tasks:
                task.start()
                time.sleep(range_sleep)
            for task in tasks:
                task.join()
            break

# push推送
def push_plus_bot(title, content):
    try:
        print("\n")
        if not PUSH_PLUS_TOKEN:
            print("PUSHPLUS服务的token未设置!!\n取消推送")
            return
        print("PUSHPLUS服务启动")
        url = 'http://pushplus.plus/send'
        data = {
            "token": PUSH_PLUS_TOKEN,
            "title": title,
            "content": content
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
            print(response)

    except Exception as e:
        print(e)

if __name__ == '__main__':

    print('准备...')
    h = (datetime.datetime.now()+datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H")   +":00:00"
    print ("now time=",datetime.datetime.now() )

    #strptime函数根据指定的格式把一个时间字符串解析为时间元组，返回struct_time对象,
    #mktime返回秒数时间戳
    starttime =int( time.mktime(time.strptime(h, "%Y-%m-%d %H:%M:%S")) * 1000) - 1000
    if len(mycookies) != 0:
        threads = []
        for i in range(len(mycookies)):
            threads.append(
                threading.Thread(target=use_thread, args=(mycookies[i],i+1))
            )
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    #发送通知
    if '成功' in str(content):
        push_plus_bot(title, content)
    else:
        print('抢券失败')