"""
v0.1
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import os
import json
from aip import AipSpeech
import time
import requests
from pathlib import Path
from playsound import playsound
import geopy.distance

class GoHome(toga.App):

    def startup(self):

        main_box = toga.Box()
        
        button = toga.Button(
            "回家!",
            on_press=self.navigation,
            #字体大小和按钮设置的非常大以方便老人
            style=Pack(font_size=100,padding=50,width=500,height=500))
        main_box.add(button)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        

        
    def navigation(self):
        #从下面两个百度官方网址获取tts和导航的Keys    Get keys for tts and navigation from the following Baidu websties
        #https://lbsyun.baidu.com/index.php?title=%E9%A6%96%E9%A1%B5
        #https://ai.baidu.com/
        self.APP_ID = 'your own key'
        self.API_KEY = 'your own key'
        self.SECRET_KEY = 'your own key'
        self.ak = 'your own key'

        client = AipSpeech(self.APP_ID,self.API_KEY,self.SECRET_KEY)

        #获取设备的GPS地址  Obtain GPS cordinates
        #从下面网址获取Key  Get keys from the following Ipstack webstie
        #https://ipstack.com/
        send_url = 'http://api.ipstack.com/check?access_key='+ 'your own key'
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        latitude = geo_json['latitude']
        longitude = geo_json['longitude']

        origin = str(longitude)+ ',' + str(latitude)
        destination = 'your chosen destination'

        route_url = 'https://api.map.baidu.com/directionlite/v1/walking?origin='+origin+'&destination='+destination+'&ak='+self.ak+'&coord_type=wgs84'
        response = requests.get(route_url)
        answer = response.json()
        #获取导航信息  Obtain key information such as distance, duration, direction, instruction, path, start location (long+lat), and end location (long+lat)
        steps = answer['result']['routes'][0]['steps']

        i = 0
        for path_i in steps:
            while os.path.exists('audio%s.wav' % i):
                i += 1
            path_i['instruction'] = path_i['instruction'].replace('<b>', '')
            path_i['instruction'] = path_i['instruction'].replace('</b>', '')
            result = client.synthesis(path_i['instruction'], 'zh', 1, {
                    'vol': 5,
                    'per': 0,
                    'spd': 5,
                    'pit': 5,
                    'aue': 6,
            })

            with open('audio%s.wav' % i, 'wb') as f:
                f.write(result)

            while True:
                #更新GPS坐标        Update GPS cordinates
                send_url_update = 'http://api.ipstack.com/check?access_key='+ 'your own key'
                geo_req_update = requests.get(send_url_update)
                geo_json_update = json.loads(geo_req_update.text)
                latitude_update = geo_json_update['latitude']
                longitude_update = geo_json_update['longitude']
                
                origin_update_reverse = str(latitude_update)+ ',' + str(longitude_update)
                
                path = path_i['path'].split(';')
                stop_point = path[-1].split(',')
                sp_long = stop_point[0]
                sp_lat = stop_point[-1]
                stop_point_reverse = sp_lat + ',' + sp_long
                #计算导航中与下一个cordinate的距离
                #需要经纬度反转 distance.distance usage, pair of (lat, lon) tuples
                distance = geopy.distance.geodesic(origin_update_reverse, stop_point_reverse).km
                #如果与下一个cordinate距离大于5米，继续播报当前导航；如果小于等于5米，播报下一则导航
                if distance > 0.005:
                    time.sleep(2) 
                    audio = Path().cwd() / ('audio%s.wav' % i)
                    playsound(audio)
                else:
                    break


def main():
    return GoHome()
