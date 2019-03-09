import requests
from lxml import etree
import os


class DouTuLaSpider():

    def __init__(self):
        # 默认第一页开始
        self.pn = 1
        # 默认URL
        self.url = 'https://www.doutula.com/photo/list/?page='

        # 添加请求头,模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }

    # 发起请求
    def loadpage(self):
        # 拼接请求地址
        req_url = self.url + str(self.pn)  # https://www.doutula.com/photo/list/?page=1

        print(req_url)

        # 发起请求
        reponse = requests.get(url=req_url, headers=self.headers)

        print('czx')
        # 用UTF-8进行编码
        content = reponse.content.decode('utf-8')

        # 构造xpath解析对象
        html = etree.HTML(content)

        # 先取出这个div下面的所有a标签
        a_list = html.xpath('//div[@class="page-content text-center"]//a')

        for a in a_list:
            # 在从当前的a标签取下面的img标签的data-original属性，取返回列表的第一个值。注意前面有个.
            img_url = a.xpath('./img/@data-original')[0]
            # 图片名字
            img_name = a.xpath('./img/@alt')[0]

            print(img_url)

            #下载图片
            self.loadimg(img_url, img_name)

    #发起图片请求
    def loadimg(self, img_url, img_name):
        folder = 'doutu'#本地文件夹名字
        if not os.path.exists(folder):#如果文件夹不存在
            os.mkdir(folder)#创建文件夹

        # 拼接本地图片路径
        path = folder + "/" + img_name + img_url[-4::]

        # 发起图片请求
        reponse = requests.get(url=img_url, headers=self.headers)

        # 图片二进制数据
        content = reponse.content

        #保存图片
        self.saveimg(path,content)

    #保存图片
    def saveimg(self,path,content):
        with open(path,'wb') as f:
            f.write(content)


if __name__ == "__main__":
    dtls = DouTuLaSpider()
    for i in range(2,100):
        print('爬取第%d页'%i)
        dtls.pn = i #把每页赋值给pn
        dtls.loadpage()
