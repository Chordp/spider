import requests as rq
import json
import logging as log   
schoolId = '你学校id'
JxSignApi = {
    'login': 'https://fxgl.jx.edu.cn/{}/public/homeQd?loginName={}&loginType=0',
    'signInfo': 'https://fxgl.jx.edu.cn/{}/studentQd/pageStudentQdInfoByXh',
    'sign': 'https://fxgl.jx.edu.cn/{}/studentQd/saveStu',
    'isSign': 'https://fxgl.jx.edu.cn/{}/studentQd/studentIsQd',
    'studentInfo': 'https://fxgl.jx.edu.cn/{}/parameter/xxmc',
}
baiduMapApi = {
    'convert':'https://api.map.baidu.com/geoconv/v1/?coords={},{}&from=1&to=6&ak=80smLnoLWKC9ZZWNLL6i7boKiQeVNEbq',
    'quest':'https://api.map.baidu.com/?qt=rgc&x={}&y={}&dis_poi=100&poi_num=10&latest_admin=1&ie=utf-8&oue=1&fromproduct=jsapi&v=2.1&res=api'
}
def questMapInfo(lat,lng):
    try:
        r = rq.get(baiduMapApi['convert'].format(lng,lat))
        r = json.loads(r.content)
        if r['status'] == 0:
            r = r['result'][0]
            r = rq.get(baiduMapApi['quest'].format(r['x'],r['y']))
            r = json.loads(r.content)
            return r['content']
        return None
    except Exception as e:
        log.warning('百度地图转换坐标失败',e)
        return None
class jxSign(rq.Session):
    def __init__(self,schoolId,studentId):
        super().__init__()
        
        # self.headers = {
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        #     'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        #     'accept':'*/*'
        # }
        
        self.schollId = schoolId
        self.studentId = studentId
        self.name = '无名氏'
        try:
            self.get(JxSignApi['login'].format(schoolId,studentId))
        except Exception as e:
            log.warning("登录失败",e)
        try:
            r = self.signInfo()
            if r is not None:
                self.name =  r['data']['list'][0]['xm']
        except Exception as e:
            log.warning("查询学生姓名失败",e)
    def isLogin(self):
        return self.cookies['JSESSIONID']!=None
    def sign(self):
        if self.isLogin() is False:
            return "登录失败,无法进行签到"
        try:
            r = self.signInfo()
            if r is not None:
                data = r['data']['list'][0]
                lat,lng = data['lat'],data['lng']
                mapData = questMapInfo(lat,lng)
                signData = {
                    'province': mapData['address_detail']['province'],
                    'city': mapData['address_detail']['city'],
                    'district': mapData['address_detail']['district'],
                    'street': mapData['address_detail']['street'],
                    'xszt': 0,
                    'jkzk': 0,
                    'jkzkxq': None,
                    'sfgl': 1,
                    'gldd': None,
                    'mqtw': 0,
                    'mqtwxq':None, 
                    'zddlwz': mapData['address'],
                    'sddlwz': None,
                    'bprovince':mapData['address_detail']['province'],
                    'bcity': mapData['address_detail']['city'],
                    'bdistrict': mapData['address_detail']['district'],
                    'bstreet': mapData['address_detail']['street'],
                    'sprovince': mapData['address_detail']['province'],
                    'scity': mapData['address_detail']['city'],
                    'sdistrict': mapData['address_detail']['district'],
                    'lng': lng,
                    'lat': lat,
                    'sfby': 1
                }
                p = self.post(JxSignApi['sign'].format(self.schollId),data=signData)
                return json.loads(p.content)['msg']
            else:
                return '获取上次签到信息失败!!!'
        except Exception as e:
            log.warning(self.name,"签到失败",e)
    def signInfo(self,size = 1):
        if self.isLogin() is False:
            return None
        result = self.post(JxSignApi['signInfo'].format(self.schollId),data={'page': '1','size':size})
        return json.loads(result.content)
    def isSign(self):
        if self.isLogin() is False:
            return False 
        try:
            result = self.post(JxSignApi['isSign'].format(self.schollId))
            r = json.loads(result.content)['data']
            return bool(r)
        except Exception as e:
            log.warning(self.name,"查询签到状态失败",e)
            return False
    def studentInfo(self):
        if self.isLogin() is False:
            return None
        try:
            result = self.get(JxSignApi['studentInfo'].format(self.schollId))
            return json.loads(result.content)
        except Exception as e:
            log.warning(self.name,"查询学生信息失败",e)
            return None
data = {
    'sign_already':[],
    'sign_fail':[],
    'sign_success':[]
    }
def main():
    for id in ['学号1','学号2']:
        jx = jxSign(schoolId,id)
        if jx.isSign():
            print("已签到")
            data['sign_already'].append(jx.name)
            log.info(jx.name,"已签到")
        else:
            log.info(jx.name,"签到",jx.sign())
            
            if jx.isSign():
                data['sign_success'].append(jx.name)
            else:
                data['sign_fail'].append(jx.name)
    print(data)

def main_handler(event, context):
    data = {
        'sign_already':[],
        'sign_fail':[],
        'sign_success':[]
    }
    for id in ['学号1','学号2']:
            jx = jxSign(schoolId,id)
            if jx.isSign():
                print("已签到")
                data['sign_already'].append(jx.name)
                log.info(jx.name,"已签到")
            else:
                log.info(jx.name,"签到",jx.sign())
                
                if jx.isSign():
                    data['sign_success'].append(jx.name)
                else:
                    data['sign_fail'].append(jx.name)
    return json.dumps(data)