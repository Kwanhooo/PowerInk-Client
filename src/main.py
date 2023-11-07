#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import time
import requests
from PIL import Image
from io import BytesIO
import netifaces as ni


# 获取无线网络接口的MAC地址
def get_mac_address(interface='wlan0'):
    try:
        mac = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']
        return mac.replace(":", "")
    except ValueError as e:
        print("未找到网络接口:", e)
        return None


# 下载图片的函数
def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            print("下载图片失败。状态码:", response.status_code)
            return None
    except requests.RequestException as e:
        print("下载图片出错:", e)
        return None


# 将图片显示在电子纸上的函数
def display_image(epd, image_path):
    try:
        frame_image = Image.open(image_path)
        epd.display(epd.getbuffer(frame_image))
        time.sleep(2)  # 将图片显示2秒钟
    except IOError as e:
        print("显示图片时出错:", e)


# 清屏并优雅退出的函数
def clear_exit(epd):
    epd.init()
    epd.Clear()
    epd.sleep()
    epd4in2_V2.epdconfig.module_exit()


# 主循环
def main():
    picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
    libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
    if os.path.exists(libdir):
        sys.path.append(libdir)

    from waveshare_epd import epd4in2_V2

    epd = epd4in2_V2.EPD()
    epd.init()
    epd.Clear()

    mac_address = get_mac_address()
    if not mac_address:
        print("无法获取MAC地址。")
        sys.exit(1)

    try:
        while True:
            url = f"https://api.ink.0xcafebabe.cn/device/getCommand/{mac_address}"
            print("正在请求URL:", url)
            response = requests.get(url)
            print("响应:", response.text)

            if response.status_code == 200:
                json_response = response.json()
                if json_response['code'] == 0:
                    if json_response['data']['type'] == 1:
                        command = json_response['data']['command']
                        print("从以下地址下载图片:", command)
                        image = download_image(command)

                        if image:
                            image_path = '/home/ink/frame.bmp'
                            image.save(image_path)
                            display_image(epd, image_path)
                    elif json_response['data']['type'] == 0:
                        # 当type为0时，不进行任何操作
                        print("Type为0, 不执行任何操作。")
            else:
                print("获取命令失败。状态码:", response.status_code)

            time.sleep(10)

    except IOError as e:
        print("发生了IO错误:", e)
        clear_exit(epd)

    except KeyboardInterrupt:
        print("ctrl + c: 清空并退出")
        clear_exit(epd)
        sys.exit()


if __name__ == "__main__":
    main()
