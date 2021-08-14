import requests
import json
import re
from requests.api import post
from selenium import webdriver
import time


def autopost(url, cookie, content, title):
    '''使用selenium模拟发送消息以减小工作量'''
    # 声明一个谷歌配置对象
    opts = webdriver.ChromeOptions()    
    # 设置成无头
    opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')
    # 设置开发者模式，防止被检测出来 ↓
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 隐藏日志信息
    opts.add_experimental_option('excludeSwitches', ['enable-logging'])
    # 注入配置对象
    wd = webdriver.Chrome(options=opts)
    #设置cookie
    wd.get(url)
    wd.delete_all_cookies()
    for dict in cookie.split(';'):
        name =  dict.split('=', 1)[0]
        value = dict.split('=',1)[1]
        #去除所有空格防止干扰
        cookie = {'name':name.replace(' ',''),'value':value.replace(' ','')}
        try:
            wd.add_cookie(cookie)
        #设置报错信息，找寻错误点
        except Exception as e:
            print(name)
            print(e)
    wd.get(url)
    #通过js输入文本内容
    js='document.getElementById("ueditor_replace").innerHTML="<p>%s</p>"'%content
    wd.execute_script(js)
    wd.implicitly_wait(5)
    #发送文本
    post_button = wd.find_element_by_class_name('poster_submit')
    post_button.click()
    print('该贴已完成：%s'%title)
    #关闭当前页面，释放资源
    wd.close()

def post(url,cookie):
    '''自动水贴的主要程序'''
    #设置请求头
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': '%s'%cookie,
        'Host': 'tieba.baidu.com',
        'Pragma': 'no-cache',
        'Referer': 'https://tieba.baidu.com/index.html',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'
    }

    response = requests.get(url,headers = header)

    #re似乎是通过换行符寻找匹配
    #此处将\n \r全部删除以求得粗略匹配结果
    infos = response.text.replace('\n','')
    infos = infos.replace('\r','')
    #粗略搜索
    find_info = re.compile('<a rel="noreferrer" href="(.*?)data-field')
    #找到帖名
    find_title = re.compile('title="(.*?)"')
    #找到链接
    find_link = re.compile('/p/(.*?)"')
    #找到发帖者
    find_name = re.compile('title="主题作者:(.*?)"')

    #粗略定位内容
    infos_rough = re.findall(find_info, infos)
    #从本地读取已发帖子
    title_list = []
    with open('title_list.txt','r') as f:
        title_list = f.readlines()
    #筛选出暗炎之主的帖子并回复
    num = 0  #统计成功回帖次数
    for info in infos_rough:
        if '/p/' in info:
            title = re.findall(find_title,info)[0]
            link = re.findall(find_link,info)[0]
            name = re.findall(find_name, info)[0]
            if '暗炎之主' in name and title+'\n' not in title_list:
                reallink = 'https://tieba.baidu.com/p/' + link
                title_list.append(title)
                try:
                    autopost(reallink, cookie, '暗炎之主，请和我缔结契约吧！',title)
                    num += 1
                except Exception as e:
                    print("未知错误：%s"%e)

    #将本次发过的贴子名储存在本地
    with open('title_list.txt', 'w') as f:
        for title in title_list:
            if '\n' in title:
                f.write(title)
            else:
                f.write(title+'\n')
    #返回发帖成功次数
    return num

order = 0
url = 'https://tieba.baidu.com/f?kw=%E6%9D%A8%E8%B6%85%E8%B6%8A&ie=utf-8'
url = url+'&pn=%d'%(50*order)
cookie = 'BAIDU_WISE_UID=wapp_1628763749778_775; BAIDUID_BFESS=AD908E02FCF0EDBB0FB0DFB1CBA04744:FG=1; __yjs_duid=1_b9d9c0cbc9b985c1085523ee50db05511628763763286; BDUSS=B0UnpvaFViS2Z0RE1EflVlOWl2SmhWbWNSa0NYM0k3YjVwNkVkbVlISkxoRHhoSVFBQUFBJCQAAAAAAQAAAAEAAAAc9-BI0LDN9dXm0dvfuQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEv3FGFL9xRhSz; BDUSS_BFESS=B0UnpvaFViS2Z0RE1EflVlOWl2SmhWbWNSa0NYM0k3YjVwNkVkbVlISkxoRHhoSVFBQUFBJCQAAAAAAQAAAAEAAAAc9-BI0LDN9dXm0dvfuQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEv3FGFL9xRhSz; STOKEN=9de63a89c9d044b358640ba253dc0935e9a1e77ed93cdcf840e3e28e0aa500cd; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1628763981; 5517670172_FRSVideoUploadTip=1; video_bubble5517670172=1; USER_JUMP=-1; st_key_id=17; BAIDUID=AA88B1E1EE9FC4BF5D679552792F65D6:FG=1; wise_device=0; bdshare_firstime=1628764182127; rpln_guide=1; tb_as_data=6a5fe493dc60bf880a20b481892296b4261c07529742a912f6b01eddd728c1f4eeb6db639d68cb83afcfc2e05cbfbdc298fe422a4dbfad0616f6b3f1d63d24a27e9eccb6215a8005de235f0783ff4fdfc85ae09668acfeb21648a3e4d783cbc27b99e4c30c212bc8204ea5ff7c28da6d; Hm_lpvt_98b9d8c2fd6608d564bf2ac2ae642948=1628854150; st_data=3781904af57a1a5f2f45e623f14a270377ecf61a72670aaa478fffb8963d292635bf1acb251f5e554aa79dcc43a50575b753773f7a83f80d183fea3a77d82416f0805b34f7e8a7d6102819004d9a522e362ee16c6cde3b5ed1d7dfa57bfebd90b35173a563e51e2f1402f922909147a3cc0aa762d5691c71d9644efd78cd4a83; st_sign=e76a2312; ab_sr=1.0.1_ZjkwZjQ1MzM1YmIwNjAyYTZmNDQ5MjcyZTQ2MzM5NWFlMzdmZDkzYzVlNjBkOTU5MDRjYmNkMmI0ZDVkZmNlMjQwMDM0ZGM5NmUyNmM1Mzc2ZTZkYTQwMTRjOTM3ZWZkYjI3MjJlYTZlMDA0NDY5MWRlOWVlYmIzYWJkYTg2MTg4ODBmYmU2NTg0MTVjMWE2MTJkMTg3YjQ1Zjg3MmY1Yw=='

num = 0
while order < 3:
    num += post(url,cookie)
    order += 1
print('本次共回复%d个帖子'%num)