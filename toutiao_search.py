import requests
import json
import os,re
import logging
import random
import time
import math
from mythread import MyThread


logging.basicConfig(level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s - %(threadName)s - %(lineno)d - %(funcName)s - %(message)s")

def sleep(func):
    def wait(*args, **kwargs):
        random_num = random.random() * 3
        # logging.info('执行函数{}，等待{}秒'.format(func.__name__,random_num))
        time.sleep(random_num)
        f = func(*args, **kwargs)
        return f
    return wait

class toutiao():

    def __init__(self,headers,count=20):
        self.headers = headers
        self.count = count

    @sleep
    def get_url_response(self,offset,search):
        url = 'https://www.toutiao.com/search_content/?'
        params = {
            'offset':offset,
            'format':'json',
            'keyword':search,
            'autoload':'true',
            'count':offset + self.count
        }
        response = requests.get(url=url,params=params,headers=self.headers)
        logging.info(response.url)

        return response.json()

    @sleep
    def get_innerpage(self,json):
        data = json.get('data')
        innerpagelist = []
        for i in data:
            if i.get('title') and i.get('tag_id'):
                title = i.get('title')
                innerpage_addr = 'https://www.toutiao.com/a{}'.format(i.get('tag_id'))
                innerpage = {
                    'title':title,
                    'innerpage_addr':innerpage_addr
                }
                innerpagelist.append(innerpage)

        return innerpagelist

    @sleep
    def get_pic_addr(self,innerpagelist):
        picslist = []
        for i in innerpagelist:
            title = i.get('title')
            innerpage_addr = i.get('innerpage_addr')
            logging.info('【title】{}，【innerpage_addr】{}'.format(title,innerpage_addr))

            response = requests.get(innerpage_addr,headers=headers)
            text = response.text

            data = re.sub(r'\\','',text)
            pics_addr_list1 = re.findall(r'"url":"(http.*?)"',data,re.S) #网页类型1
            pics_addr_list2 = re.findall(r'&quot;(http.*?)&quot',data,re.S) #网页类型2
            pics_addr_list_temp = list(set(pics_addr_list1 + pics_addr_list2))

            pics_addr_list= []
            pic_id_list = []
            for i in pics_addr_list_temp:
                pic_id = re.findall(r'/(\w*)$',i)
                if pic_id not in pic_id_list:
                    pic_id_list.append(pic_id)
                    pics_addr_list.append(i)

            pics = {
                    'title':title,
                    'pics_addr':pics_addr_list
                }
            # print(pics)
            picslist.append(pics)
            # print(picslist)

        return picslist

    @sleep
    def download_one_pic(self,dirpath,url,num):
        response = requests.get(url,headers=self.headers)
        content = response.content
        with open(r'{}\{}.jpg'.format(dirpath,num),'wb') as f:
            f.write(content)

    def download_pic(self,picslist):
        resultlist = []
        # print(picslist)
        path = os.getcwd()
        # print(path)
        for i in picslist:
            # print(i)
            title = i.get('title')
            title_dir = re.sub('[^\u4E00-\u9FA5,:，：]','',title) #标题中只保留中文
            image_list = i.get('pics_addr')

            dirpath = path + '\\pics\\' + title_dir
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            # print(image_list)
            for num,url in enumerate(image_list):
                self.download_one_pic(dirpath,url,num)
                logging.info('【title】{},第【{}】图，【URL】{}'.format(title,num,url))
                
            result = '【tite】{1}，下载{0}张图片，'.format(len(image_list),title)
            resultlist.append(result)
            # logging.info(result)
        return result
    
    def download_pic_once(self,offset,search):
        response_json = self.get_url_response(offset,search)
        innerpagelist = self.get_innerpage(response_json)
        picslist = self.get_pic_addr(innerpagelist)
        result = self.download_pic(picslist)
        return result

    def multiple_download_pic(self,offset,search):
        threads = []
        for i in range(offset):
            offset = i * self.count
            t = MyThread(func=self.download_pic_once,args=(offset,search),name=i + 1)
            threads.append(t)

        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
                

            



if __name__ == '__main__':
    search= input('请输入您想下载的图片关键字：')
    offset = abs(math.ceil(int(input('请输入您想下载的图片种数：')) / 20)) #此处的20与count一致

    headers = {
            'accept': 'application/json, text/javascript',
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'zh-CN,zh;q=0.9',
            'content-type':'application/x-www-form-urlencoded',
            'referer':'https://www.toutiao.com/search/?keyword=%E8%BD%A6%E6%A8%A1',
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'x-requested-with':'XMLHttpRequest'
        }
    
    tt = toutiao(headers=headers)
    tt.multiple_download_pic(offset=offset,search=search)


    # print(type(data))
    # with open('chemo.json','w',encoding='utf-8') as f:
    #     json.dump(data,f,ensure_ascii=False)