import datetime
import json
import math
import random
import threading
import time
import os
import requests
requests.packages.urllib3.disable_warnings()

'''
cron: 56 8,11,14,17,19 * * *
new Env('极速版15-8');
'''

# 可以改的参数
coupon_desc = ['极速版', '15-8']
args = 'key=DDF1B71D0AF91A8547973CE5362A890F18C8E73AAC10BA9179CE5D2D745E95AC9AC125029761397270C947AC9F5E11CE_bingo,roleId=3FE9EECAAA41B666E4FFAF79F20E2112EC5A32B22271AD04523B3C66AE5807591E0DB913F0F40F86F97AAA49D12C568D47FEEE50418AD25C6B23D81C476A40CB07BCCE74C4EDAD2E0D1BCF515F06DECE783A16EA99A0959CAC63BDF9BD9A9037450AB25EE84616EF9E65486A529F6690F93EA6903FF6754FD22FD39B43821B0041487D3996E0CF72C487DD107C4D0F13EA507700B35B495859747F1E700186EA385A46F6ED361FE40B11663D21263EB1_bingo,strengthenKey=4C8818C1732D1A7B9733D611F28BD8B57923ADE220C9B60370F65B533E02E0F823A5E9624E2105020B0FB67EE3BFC671_bingo'
starttime = 0
delay_time = 0.2
range_n = 25  # 线程个数25
range_sleep = 0.01  # 间隔时间
log_list = []
atime = 0
content = []
log_host = "10.0.8.11:15899"

def check_coupon(mycookies, coupon_desc):
    new_mycookies = []
    for cookies in mycookies:
        NeedtoAdd = True
        try:
            url = f"https://wq.jd.com/activeapi/queryjdcouponlistwithfinance?state={1}&wxadd=1&filterswitch=1&_={int(time.time() * 1000)}&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls"
            headers = {
                'authority': 'wq.jd.com',
                "User-Agent": "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
                'accept': '*/*',
                'referer': 'https://wqs.jd.com/',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'cookie': cookies
            }
            res = requests.get(url, headers=headers, verify=False, timeout=10)
            res = json.loads(res.text.replace("try{ jsonpCBKB(", "").replace("\n);}catch(e){}", ""))
            coupon_list = res['coupon']['useable']
            for coupon in coupon_list:
                if coupon_desc[0] in str(coupon) and coupon_desc[1] in str(coupon) and tomorrow_timestamp >= int(
                        coupon['beginTime']) >= today_timestamp:
                    NeedtoAdd = False
        except:
            pass
        if NeedtoAdd:
            new_mycookies.append(cookies)
    return new_mycookies

def get_log_list(num):
    global log_list
    try:
        for i in range(num):
            url = "http://" + str(log_host) + "/log"
            res = requests.get(url=url).json()
            log_list.append(res)
    except:
        log_list = []
    return log_list


def randomString(e):
    t = "0123456789abcdef"
    a = len(t)
    n = ""
    for i in range(e):
        n = n + t[math.floor(random.random() * a)]
    return n


def Ua():
    UA = f'jdapp;iPhone;10.2.0;13.1.2;{randomString(40)};M/5.0;network/wifi;ADID/;model/iPhone8,1;addressid/2308460611;appBuild/167853;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1;'
    return UA


def qiang_quan(cookie, i, index):
    url = 'https://api.m.jd.com/client.action?functionId=lite_newBabelAwardCollection&client=wh5'
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        'origin': 'https://pro.m.jd.com',
        "Referer": "https://pro.m.jd.com/jdlite/active/3H885vA4sQj6ctYzzPVix4iiYN2P/index.html?lng=106.476617&lat=29.502674&sid=fbc43764317f538b90e0f9ab43c8285w&un_area=4_50952_106_0",
        "Cookie": cookie,
        "User-Agent": Ua()
    }

    body = json.dumps({"activityId": "vN4YuYXS1mPse7yeVPRq4TNvCMR",
                       "scene": "1",
                       "args": args,
                       "log": log_list[i]['log'],
                       "random": log_list[i]['random']}
                      )
    data = f"body={body}"
    try:
        res = requests.post(url=url, headers=headers, data=data).json()
        # print(res)
        if res['code'] == '0':
            #print(f"账号{index + 1}：{res['subCodeMsg']}")
            if '成功' in res['subCodeMsg']:
                content.append(f"账号{cookie[90:-1]}：{res['subCodeMsg']}")
        else:
            pass
            #print(f"账号{index + 1}：{res['errmsg']}")
    except:
        pass


def jdtime():
    url = 'http://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    try:
        res = requests.get(url=url, headers=headers, timeout=1).json()
        return int(res['currentTime2'])
    except:
        return 0


def use_thread(cookie, index):
    tasks = list()
    for i in range(range_n):
        tasks.append(threading.Thread(target=qiang_quan, args=(cookie, index * 50 + i, index)))
    print(f'账号{index + 1}：等待抢券')
    while True:
        # jdtime>=starttime时启动
        if jdtime() >= starttime:
            # starttime提前一秒，所以需要加上延迟
            time.sleep(delay_time)
            for task in tasks:
                task.start()
                time.sleep(range_sleep)
            for task in tasks:
                task.join()
            break


if __name__ == '__main__':
    print(coupon_desc[0] + "抢" + coupon_desc[1] + "券开始！")
    try:
        mycookies = os.environ["JD_COOKIE"].split('&')
        if len(mycookies) < 1:
            raise Exception("无有效Cookies，请检查")
        elif len(mycookies) > 6:
            mycookies = mycookies[:6]
        print("共有" + str(len(mycookies)) + "个Cookies准备执行")
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_timestamp = int(time.mktime(today.timetuple()) * 1000)
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_timestamp = int(int(time.mktime(tomorrow.timetuple()) * 1000) - 300)
        mycookies = check_coupon(mycookies, coupon_desc)
        if len(mycookies) < 1:
            raise Exception("所有Cookies今日均已抢到券，休息啦~")
        else:
            print("共有"+str(len(mycookies))+"个cookies需要抢"+coupon_desc[0]+" "+coupon_desc[1]+"券")
        h = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H") + ":00:00"
        #print("now time=", (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
        print("下一个整点是：", h)
        # mktime返回秒数时间戳
        starttime = int(time.mktime(time.strptime(h, "%Y-%m-%d %H:%M:%S")) * 1000) - 1000
        #print("time stamp=", starttime)
        while True:
            if starttime - int(time.time() * 1000) <= 180000:
                break
            else:
                if int(time.time() * 1000) - atime >= 30000:
                    atime = int(time.time() * 1000)
                    print(f'等待获取log中，还差{int((starttime - int(time.time() * 1000)) / 1000)}秒')
        get_log_list(len(mycookies) * 50)
        if len(log_list) != 0:
            print(f'{len(log_list)}条log获取完毕')
            threads = []
            for i in range(len(mycookies)):
                threads.append(
                    threading.Thread(target=use_thread, args=(mycookies[i], i))
                )
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        else:
            raise Exception("暂无可用log，请检查后端是不是炸了。。。")
        print("共计" + str(len(content)) + "/" + str(len(mycookies)) + "个帐号在本轮抢到券~")
        for c in content:
            print(str(c))
    except Exception as e:
        print(str(e))
