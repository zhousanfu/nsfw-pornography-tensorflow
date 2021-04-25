import requests
from lxml import etree
import re
import json
import random



def get_urls(url):
    
    headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }
    try:
        req = requests.get(url, headers=headers, timeout=5)
    except:
        pass
    # =====重定向跳转网址获取=====
    # reditList = r.history#可以看出获取的是一个地址序列
    # print(f'获取重定向的历史记录：{reditList}')
    # print(f'获取第一次重定向的headers头部信息：{reditList[0].headers}')
    # print(f'获取重定向最终的url：{reditList[len(reditList)-1].headers["location"]}')
    listurls = []
    try:
        html = etree.HTML(req.text)
        meta_urls = html.xpath('//meta/@content')
        jump_urls = re.findall(r'http.+', meta_urls[len(meta_urls)-1])
        if len(jump_urls) > 0:
            website = re.findall(r'.*/', str(jump_urls[0]))[0]
            req = requests.get(jump_urls[0])
            if len(re.findall(r"(?=https.*).*jpg", req.text)) > 0:
                listurls = re.findall(r"(?=https.*).*jpg", req.text)
                # listurls = random.sample(listurls, 3)
            elif len(re.findall(r"/.*jpg", req.text)) > 0:
                listurls = []
                for i in re.findall(r"/.*jpg", req.text):
                    listurls.append(website + str(i))
                # listurls = random.sample(listurls, 3)
    except:
        pass


    try:
        if len(re.findall(r"(?=https.*).*jpg", req.text)) > 0:
            listurls = re.findall(r"(?=https.*).*jpg", req.text)
            # listurls = random.sample(listurls, 3)
    except:
        pass

    return listurls



if __name__ == "__main__":
    data_txt = pd.read_table('测试网站.txt', sep='\t', header=None).values.tolist()

    for url in data_txt:
        listurls = get_urls(str(url[0]))
        print('网站=', url[0], '图片url:', len(listurls))
