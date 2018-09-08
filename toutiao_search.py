import requests
import json
import os,re

class toutiao():

    def __init__(self,headers,offset=0):
        self.offset = offset
        self.headers = headers

    def get_url_response(self,search,url):

        params = {
            'offset':self.offset,
            'format':'json',
            'keyword':search,
            'autoload':'true'
        }
        response = requests.get(url=url,params=params,headers=self.headers)

        return response.json()

    def get_innerpage(self,json):
        data = json.get('data')
        for i in data:
            if i.get('title') and i.get('tag_id'):
                title = i.get('title')
                innerpage_addr = 'https://www.toutiao.com/a{}'.format(i.get('tag_id'))
                innerpage = {
                    'title':title,
                    'innerpage_addr':innerpage_addr
                }
                yield innerpage
    
    def get_pic_addr(self,innerpage):
        for i in innerpage:
            title = i.get('title')
            innerpage_addr = i.get('innerpage_addr')

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
            yield pics


    def download_pic(self,pics):
        path = os.getcwd()
        # print(path)
        for i in pics:
            # print(i)
            title = i.get('title')
            image_list = i.get('pics_addr')

            dirpath = path + '\\pics\\' + title
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
            
            for num,j in enumerate(image_list):
                # print(j)
                response = requests.get(j,headers=self.headers)
                content = response.content
                with open(r'{}\{}.jpg'.format(dirpath,num),'wb') as f:
                    f.write(content)
            print('下载{}张图片，【tite】{}'.format(len(image_list),title))
                
                
        


if __name__ == '__main__':
    url = 'https://www.toutiao.com/search_content/?'

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
    json = tt.get_url_response(search='车模',url=url)
    innerpage = tt.get_innerpage(json)
    pics = tt.get_pic_addr(innerpage)
    tt.download_pic(pics)


    # print(type(data))
    # with open('chemo.json','w',encoding='utf-8') as f:
    #     json.dump(data,f,ensure_ascii=False)