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
cron: 56 0,5,7,12,23 * * *
new Env('极速版10月2-1');
'''

# 可以改的参数
coupon_desc = ['极速版', '2-1']
args = 'key=8AC876FB1491F9FF454555697A177E99834FFFA50B758BE732E794AAAB5D4594942FB4E338DF7D16CF6B42D85705CC65_bingo,roleId=BA69EED36CE7E66BC944EC1DA1C37FA3661735FC2A45D4FFF435545070BE5C219F5A52EAF8E6A6FF50D5510BE60FC7C773D794F6036CDA45B2823A70CC8FA5012579CE474BA0E71D96FDFDF54DA7A68102A36FE046B3E58EDE975948C142D8500D95722F30A8E167AF49BEB11C2595244DD58CAFB1490197CE9F0B5B852594475D048C350A0A2EDC9006B686A80AD0B514CB12C2C1413D106AA998DAC51BA760_bingo,strengthenKey=19F512DCD8EE34ABE9C4FB4A92C2F42A47F123257053274DCE3A20DDBAF0E526_bingo'
starttime = 0
starttime_offset = 3
range_n = 25  # 线程个数25
log_list = []
atime = 0
content = []
log_host = os.environ["JDLITE_LOG"]
print("当前正在使用log server：" + str(log_host))
vip_pins = os.environ["JDLITE_VIP"].split("&")
other_pins = os.environ["JDLITE_OTHER"].split("&")


def get_cookies(pin_list=vip_pins, second_round=False):
    cookies_temp_arr = []
    env_cookies = os.environ["JD_COOKIE"].split('&')
    if len(pin_list) != 0:
        print("Selected Pins:" + str(pin_list))
        for env_cookie in env_cookies:
            for pin in pin_list:
                if str(pin) in str(env_cookie):
                    cookies_temp_arr.append(env_cookie)
                    break
    else:
        cookies_temp_arr = env_cookies
    cookies_arr = filter_cookies(cookies_temp_arr)
    if len(cookies_arr) == 0:
        if second_round:
            raise Exception("无有效Cookies，请检查。")
        else:
            print(str(pin_list) + "今日均已抢到券，来拉一把" + str(other_pins))
            cookies_arr = get_cookies(pin_list=other_pins, second_round=True)
    return cookies_arr


def filter_cookies(cookies_temp_arr):
    new_cookies_temp_arr = []
    for cookies_temp in cookies_temp_arr:
        NeedtoAdd = True
        if int(int(time.mktime(datetime.datetime.now().timetuple())) * 1000) < tomorrow_timestamp:
            try:
                url = f"https://wq.jd.com/activeapi/queryjdcouponlistwithfinance?state={1}&wxadd=1&filterswitch=1&_={int(time.time() * 1000)}&sceneval=2&g_login_type=1&callback=jsonpCBKB&g_ty=ls"
                headers = {
                    'authority': 'wq.jd.com',
                    "User-Agent": "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
                    'accept': '*/*',
                    'referer': 'https://wqs.jd.com/',
                    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'cookie': cookies_temp
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
        else:
            pass
        if NeedtoAdd:
            new_cookies_temp_arr.append(cookies_temp)
    return new_cookies_temp_arr


def get_log_list(num):
    global log_list
    try:
        for i in range(num):
            url = str(log_host) + "/log"
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
            print(time.strftime("%H:%M:%S")+"账号"+str(index + 1)+"："+str(res['subCodeMsg']))
            if '成功' in res['subCodeMsg']:
                content.append(f"账号{cookie[90:-1]}：{res['subCodeMsg']}")
        else:
            print(time.strftime("%H:%M:%S")+"账号"+str(index + 1)+"："+str(res['errmsg']))
    except:
        pass


def jdtime():
    url = 'http://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5'
    headers = {
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    try:
        index = 0
        while index < 3:
            res = requests.get(url=url, headers=headers, timeout=1).json()
            if 'currentTime2' in res:
                return int(res['currentTime2'])
            index += 1
        return int(round(time.time() * 1000))
    except:
        return int(round(time.time() * 1000))


def use_thread(cookie, index):
    tasks = list()
    for i in range(range_n):
        tasks.append(threading.Thread(target=qiang_quan, args=(cookie, index * 50 + i, index)))
    print(f'账号{index + 1}：等待抢券')
    while True:
        nowtime = jdtime()
        if nowtime >= starttime:
            for task in tasks:
                task.start()
            for task in tasks:
                task.join()
            break


if __name__ == '__main__':
    print(coupon_desc[0] + "抢" + coupon_desc[1] + "券开始！")
    try:
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_timestamp = int(time.mktime(today.timetuple()) * 1000)
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0,
                                                                                  microsecond=0)
        tomorrow_timestamp = int(int(time.mktime(tomorrow.timetuple()) * 1000) - 3600000)
        mycookies = get_cookies()
        print("本轮共有" + str(len(mycookies)) + "个cookies需要抢" + coupon_desc[0] + " " + coupon_desc[1] + "券")
        h = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H") + ":00:00"
        print("下一个整点是：", h)
        starttime = int(time.mktime(time.strptime(h, "%Y-%m-%d %H:%M:%S")) * 1000) - starttime_offset * 1000
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
            print(f'准备抢券，还差{int((starttime - int(time.time() * 1000)) / 1000)}秒')
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
