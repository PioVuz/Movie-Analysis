#coding=utf-8
#Version=python3.6.0
#Tools:Pycharm 2017.3.2
__date__ = '2019/9/25 9:55'
__author__ = 'toaakira'
import requests
from lxml import etree
import time
import random
import pandas as pd
import jieba
import numpy as np
from wordcloud import WordCloud
from PIL import Image
class freesolo():
    def __init__(self):
        # 定义session,加载html
        self.session = requests.session()
        # 定义爬虫的header
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                        'Host': 'movie.douban.com', 'Upgrade-Insecure-Requests': '1'}
        # 定义proxies代理
        # self.proxies = {'http': 'http://123.207.111.68:38331', 'https': 'https://123.207.111.68:38331'}
        # 豆瓣登录地址
        self.url_login = 'https://accounts.douban.com/passport/login'
        # self.url_login = 'https://www.douban.com/accounts/login'
        # 豆瓣影评地址 例：徒手攀岩 30167509
        self.url_comment = 'https://movie.douban.com/subject/%d/comments?start=%d&limit=20&sort=new_score&status=P'

    def scrapy_(self):
        # 加载登陆界面url
        login_request = self.session.get(self.url_login, headers=self.headers)
        # 解析html
        selector = etree.HTML(login_request.content)
        post_data = {'ck': '',
                     'name': '18519788920',
                     'password': '1773822560',
                     'remember': 'false',
                     'ticket': ''}
        # post_data = {'source': 'None',  # 不需要改动
        #              'redir': 'https://www.douban.com',  # 不需要改动
        #              'form_email': '18519788920',  # 填账号
        #              'form_password': '1773822560',  # 填密码
        #              'login': '登录'}  # 不需要改动
        # 下面是获取验证码图片的链接 省略
        post = self.session.post(self.url_login, data=post_data)
        if post.status_code == 200:
            print('已登录豆瓣...', '返回码:', post.status_code)

        # 定义List存储用户名，评星，时间，评论文字
        users = []
        stars = []
        times = []
        comment_texts = []

        # 变更为指定影片生成词云
        movie = int(input('请输入你要采集的电影id：'))
        # 抓取300条
        for i in range(0, 20, 20):
            # 获取HTML
            data = self.session.get(self.url_comment % (movie, i), headers=self.headers)
            # 状态200代表成功：
            print('进度 --> 当前第 %d 条评论，Response Code：%s' % (i+1, data.status_code))
            # 睡眠0-1s方式封IP
            time.sleep(random.random())
            # 解析html
            selector = etree.HTML(data.text)
            # 使用xpath获取单页所有的评论
            comments = selector.xpath('//div[@class="comment"]')
            for comment in comments:
                # 获取用户名
                user = comment.xpath('.//h3/span[2]/a/text()')[0]
                # 获取评星
                star = comment.xpath('.//h3/span[2]/span[2]/@class')[0][7:8]
                # 获取时间
                data_time = comment.xpath('.//h3/span[2]/span[3]/@title')
                # 处理时间为空的特殊情况
                if len(data_time) != 0:
                    data_time = data_time[0]
                else:
                    data_time = None
                # 提取评论文字
                comment_text = comment.xpath('.//p/span/text()')[0].strip()
                # 添加进list
                users.append(user)
                stars.append(star)
                times.append(data_time)
                comment_texts.append(comment_text)
        # 使用字典包装
        comment_dic = {'user': users, 'star': stars, 'time': times, 'comments': comment_texts}
        comment_df = pd.DataFrame(comment_dic)                  # 转化成DataFrame格式
        comment_df.to_csv('./csv/scrapy_comments.csv')          # 保存数据
        comment_df['comments'].to_csv('./csv/comments.csv', index=False)     # 分词用csv
        print(comment_df)

    def jieba_(self):
        # 打开评论文件
        content = open('./csv/comments.csv', 'rb').read()
        # jieba分词
        word_list = jieba.cut(content)
        # 新建word
        words = []
        # 去除停用词相关
        for word in word_list:
            with open('./csv/停用词库.txt', 'r', encoding='utf-8') as f:
                meaningless_file = f.read().splitlines()
                if word not in meaningless_file:
                    words.append(word.replace(' ', ''))

        # 申明全局变量
        global word_cloud
        word_cloud = ', '.join(words)
        print('处理之后的评论词库：%s' % word_cloud)

    def word_cloud_(self):
        # 打开背景样图
        image_file = Image.open('./pics/sample.png', 'r')
        # 装载到numpy进行图片处理
        cloud_mask = np.array(image_file)
        # 定义word_cloud相关属性
        wc = WordCloud(background_color='white', mask=cloud_mask, font_path='./fonts/SimHei.ttf', max_words=300)  # 显示最大词数
        global word_cloud
        # 生成词云函数
        x = wc.generate(word_cloud)
        # 生成词云图片
        image = x.to_image()
        # 展示词云图片
        image.show()
        # 报存本地词云图片
        wc.to_file('./pics/word_cloud.png')


# 创建类对象
freesolo = freesolo()
# 抓取豆瓣影评
freesolo.scrapy_()
# jieba分词
# freesolo.jieba_()
# 生成词云
# freesolo.word_cloud_()

