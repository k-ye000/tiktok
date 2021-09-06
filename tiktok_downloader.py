import json
import os
import random
import re
from time import sleep

import requests
import selenium
from requests.models import Response
from selenium.webdriver import ActionChains, Chrome, ChromeOptions
from url_decode import urldecode

from geetest_verify.generate_array import generate_move_array
from geetest_verify.slide_img_position import Get_Slide_IMG_Position
from utils.user_agent_list import random_ua


class TiktokDownloader(object):
    def __init__(self, url=None):
        super().__init__()
        self.url = url
        self.slide_img_path = None

        self.options = ChromeOptions()
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"])
        # self.options.add_argument('--headless')

        self.browser = Chrome(
            executable_path='./utils/chromedriver.exe', options=self.options)

    def open_share_page(self):
        pattern = 'https://www.douyin.com/user/\w+'
        url = re.findall(pattern, self.url, re.S)[0]
        # url不为空则打开
        if url:
            self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                        })
                    """
            })
            self.browser.get(url)
            while True:
                check_height = self.browser.execute_script(
                    "return document.body.scrollHeight;")

                # 处理验证码
                while True:
                    try:
                        sleep(2)
                        img_src = self.browser.find_element_by_xpath(
                            '//*[@id="captcha-verify-image"]').get_attribute('src')
                        print(img_src)
                        self.slide_img_path = self.get_slide_bg(img_src)
                        print(self.slide_img_path)
                        if self.slide_img_path:
                            slide_position = int(Get_Slide_IMG_Position(
                                slide_img_path=self.slide_img_path).single_img_position()*340/552)-5
                            print(slide_position)
                            self.verify_signature(self.browser, slide_position)
                            os.remove('./static')
                        else:
                            continue
                    except Exception as e:
                        break

                # 处理可能出现的登录框
                try:
                    sleep(0.3)
                    alert_close = self.browser.find_element_by_xpath(
                        '//*[@id="login-pannel"]/div[2]/svg')
                    print('出现关闭按钮')
                    alert_close.click()
                except selenium.common.exceptions.NoSuchElementException:
                    pass

                # 处理弹出的页面调查框
                try:
                    sleep(0.3)
                    alert_survey = self.browser.find_element_by_xpath(
                        '/html/body/div[4]/div/svg')
                    alert_survey.click()
                except selenium.common.exceptions.NoSuchElementException:
                    pass

                self.browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                # 让页面加载
                sleep(2)
                check_height_end = self.browser.execute_script(
                    "return document.body.scrollHeight;")

                if check_height_end == check_height:
                    selenium_obj = self.browser.find_elements_by_xpath(
                        '//*[@id="root"]/div/div[2]/div/div[4]/div[1]/div[2]/ul/li/a')
                    return selenium_obj
            else:
                raise ValueError('url为空')

    def verify_signature(self, browser, position):
        position = position
        print(position)

        # 定位滑动按钮
        slide_btn = browser.find_element_by_xpath(
            '//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')

        # 绑定ActionChains
        action_chains = ActionChains(browser)

        # 点击按住滑动按钮
        action_chains.click_and_hold(on_element=slide_btn).perform()
        action_chains.pause(random.randint(1, 2) / 10)

        move_array = generate_move_array()
        move = 0
        for dis in move_array:
            # 检测鼠标轨迹和速度，人实际滑动鼠标时y轴不可能没有任何动作，这里要特别注意
            action_chains.move_by_offset(xoffset=dis, yoffset=2)
            move += dis
            if move > position:
                break
        action_chains.move_by_offset(xoffset=position - move, yoffset=-2)

        # 释放按钮
        action_chains.release()
        action_chains.perform()

    # 获取验证码图片
    def get_slide_bg(self, img_src):
        if img_src:
            response = requests.get(img_src)
            with open('./static/bg.png', 'ab') as f:
                f.write(response.content)
            return './static/bg.png'
        else:
            return False

    def video_downloader(self, url):
        headers = 'User-Agent:' + random_ua()
        renpose = requests.get(headers=headers, url=url).text
        reg = '<script id="RENDER_DATA" type="application/json">(.*?)</script></head><body'
        #视频地址就在video_detail中，发起请求即可获得视频文件
        video_detail = json.dumps(urldecode(re.findall(reg, Response, re.S)))
        print(video_url)


if __name__ == '__main__':
    url_list = ["https://www.douyin.com/user/MS4wLjABAAAA0CCvYct7vC1aX0rUHN-YWpZcZpgmfmkdip0AI08nsuNL8lXGtnZEnxSKVb8goiE4",
                # 'https://www.douyin.com/user/MS4wLjABAAAAVuSMDJfy_6WaxC3MqxWrR3WYRZ4kHlphZEvF01i_YpE',
                # "https://www.douyin.com/user/MS4wLjABAAAA4N4OrZzTSmCPp8vVAqCeyU215Kav2JgFv2Lfy4DNWRs",
                # "https://www.douyin.com/user/MS4wLjABAAAAaNbDazAnsmYWiwpID-nFYOanBVAVeGDjhOOI182c0A4_jpH-iOer_VuF_8Bn7Wya",
                # "https://www.douyin.com/user/MS4wLjABAAAAs1ClX0m7VzF04KCipOjLY6WSqtLjfDwBdd62iszZlCQ"
                ]
    for url in url_list:
        tt = TiktokDownloader(
            url=url)
        selenium_obj = tt.open_share_page()

        for a_obj in selenium_obj:
            video_url = a_obj.get_attribute('href')
            print(video_url)
            tt.video_downloader(url)

        print('共有%s条视频' % len(selenium_obj))
        tt.browser.close()
        tt.browser.quit()
