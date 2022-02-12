import datetime
import pickle
from time import sleep
import webbrowser
from selenium import webdriver
from lxml import etree
import requests as rq
import hashlib as hl
import re
opt = webdriver.EdgeOptions()
opt.add_experimental_option('excludeSwitches', ['enable-automation'])
opt.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 
# opt.add_argument('headless')

browser = webdriver.Edge(options=opt)
 
browser.get('https://member.ic.net.cn')
browser.implicitly_wait(10)
browser.get('https://www.ic.net.cn')

try:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)
except:
    print('cookies 没找到')
browser.get('https://member.ic.net.cn/login.php')
if browser.current_url == 'https://member.ic.net.cn/member/member_index.php':
    print('已经登录,无需登录')
else:
    browser.find_element_by_class_name('loginTab3').click()

    weixin = browser.find_element_by_xpath("//*[@id='div_wechatLoginQRCode']/iframe")

    browser.switch_to.frame(weixin)
    browser.implicitly_wait(10)
    a = browser.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div[1]/img').get_attribute('src')
    webbrowser.open(a)
    while True:
        if browser.current_url == 'https://member.ic.net.cn/member/member_index.php':
            break
        sleep(1)
    print('登录成功')
    pickle.dump(browser.get_cookies(), open('cookies.pkl', 'wb'))   # 保存cookies
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => false
    })
  """
})
# browser.get('https://www.ic.net.cn/search/STM32F103C8T6.html')
# browser.refresh()
# browser.implicitly_wait(10)

# data = etree.HTML(browser.page_source)
# data = data.xpath(f'//*[@id="resultList"]/li/div[2]/a')
# for i in data:
#     print(i.text.strip())
# # browser.find_element_by_id('resultList')
# sleep(10)

req = rq.session()
req.headers = {
    'user-agent': 'shabi'
}
def sct(cookie):
    md5 = hl.md5(cookie.encode()).hexdigest()
    md5_a = md5[:15]
    md5_b = md5[17:]
    sha1 = hl.sha1((md5_a+'Qi'+md5_b).encode()).hexdigest()
    req.cookies.set('ICNet[sct]', sha1)
for cookie in browser.get_cookies():
    if cookie['name'] == 'ICNet[sct]':
        # sct(cookie['value'])
        continue
    req.cookies.set(cookie['name'], cookie['value'])
# if  "ICNet[sct]" not in req.cookies.keys():
fuck = {
    'rnns':'rnns/[\d\D]*="([A-Za-z0-9]+)"',
    'rind':'rind=/[\d\D]*/([1-9]\d*)/[\d\D]*;',
}
def cuoda(source):
    data = {}
    cookie = req.cookies['ICNet[sct]']
    try:
        for (name,item) in fuck.items():
            match = re.search(item,source)
            if match:
                data[name]=match.group(1)
                print(name,match.group(1))
        md5 = hl.md5(cookie.encode()).hexdigest()
        md5_a = md5[:int(data['rind'])]
        md5_b = md5[int(data['rind'])+len(data['rnns']):]
        sha1 = hl.sha1((md5_a+data['rnns']+md5_b).encode()).hexdigest()
        req.cookies.set('ICNet[sct]', None)
        # t = datetime.datetime.now() + datetime.timedelta(days=30)
        # req.cookies['expires'] = t.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # req.cookies['path'] = '/'
        # req.cookies['domain'] = 'ic.net.cn'
        req.cookies.set('ICNet[sct]', sha1)

    except:
        print('正则失败?')
while True:
    try:
        input()
        text = req.get('https://www.ic.net.cn/search/STM32F103C8T6.html').text
        cuoda(text)
        print(req.get('https://www.ic.net.cn/search/STM32F103C8T6.html').text)
    except Exception as e:
        print(e)
        pass
#     if "ICNet[sct]" in req.cookies.keys():
#         sct(req.cookies['ICNet[sct]'])
# a = req.get('https://www.ic.net.cn/search/STM32F103C8T6.html')
# print(a.text)


# print(a.text)