import requests
from lxml import etree
import os


class XHSpider():

    def __init__(self):
        # 默认第一页开始
        self.pn = 0
        # 默认URL
        self.url = 'http://www.xiaohuar.com/list-1-{0}.html'

        # 目录
        self.dir = '校花/'

        #刚开始就创建一个目录
        if not os.path.exists(self.dir):  # 如果文件夹不存在
            os.mkdir(self.dir)  # 创建文件夹

        # 添加请求头,模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }

    # 发起请求
    def loadpage(self):
        # 拼接请求地址
        req_url = self.url.format(self.pn)  # http://www.xiaohuar.com/list-1-0.html

        print(req_url)

        # 发起请求
        reponse = requests.get(url=req_url, headers=self.headers)

        # 取返回的内容
        content = reponse.text

        '''
        注意：如果发现用xpath插件在浏览器上能取到标签，但是在代码里面取不到
        最好把请求下来的源代码保存到代码，分析一下为什么取不到，有时候
        浏览器里面的源代码跟你在代码里面请求的源码可能稍微不一样。
        '''
        with open('xiaohua.html', 'w') as f:
            f.write(content)

        # 构造xpath解析对象
        html = etree.HTML(content)

        # 先取出这个页面所有div标签
        div_list = html.xpath('//div[contains(@class,"masonry_brick")]')

        for div in div_list:
            # 从从每个div标签取出详情页链接 .代表当前位置
            desc_url = div.xpath('.//div[@class="img"]//a/@href')[0]

            # 标题
            img_title = div.xpath('.//div[@class="img"]//img/@alt')[0]

            # 封面图片地址、这个地址好像没用。发现相册里面有这种图片
            img_url = div.xpath('.//div[@class="img"]//img/@src')[0]

            print(desc_url)

            #创建每个校花的文件夹
            folder = self.dir + img_title
            if not os.path.exists(folder):  # 如果文件夹不存在
                os.mkdir(folder)  # 创建文件夹

            #开始请求详情页，把标题传过去，后面有用
            self.loaddescpage(desc_url, img_title)

    # 详情页
    def loaddescpage(self, desc_url, img_title):
        # 发起请求
        reponse = requests.get(url=desc_url, headers=self.headers)

        # 取返回的内容
        content = reponse.text

        # 构造xpath解析对象
        html = etree.HTML(content)

        # 取出资料的前6个，她的空间这个栏目不要
        tr_list = html.xpath('//div[@class="infodiv"]//tbody/tr[position()<6]')

        info = ""
        for tr in tr_list:
            info += " ".join(tr.xpath('./td/text()'))  # 把每个取出来的列表拼接成字符串
            info += "\n"

        # 取出详细资料。注意的有点资料会有空的，做判空处理
        content = html.xpath('//div[@class="infocontent"]//text()')

        if content:  # 假如不为空
            content = "".join(content)  # 把详细资料拼接成字符串

        # 校花空间地址
        more = html.xpath('//span[@class="archive_more"]/a/@href')[0]
        print(info)
        print(content)
        print(more)

        # 个人信息
        info_dir = self.dir + img_title + "/" + img_title + "个人信息.txt"
        with open(info_dir, 'w') as f:
            f.write(info)
            f.write(content)

        #开始请求校花空间
        self.loadzone(more, img_title)

    # 校花空间提取
    def loadzone(self, more, img_title):
        # 发起请求
        reponse = requests.get(url=more, headers=self.headers)

        # 取返回的内容
        content = reponse.text

        # 构造xpath解析对象
        html = etree.HTML(content)
        # 取图片的地址列表
        big_imgs = html.xpath('//div[@class="inner"]//a/@href')

        # 做图片地址容错处理
        for big_img in big_imgs:
            if big_img.startswith('http') or big_img.endswith('.jpg'):
                if big_img.startswith('http'):
                    self.download(big_img, img_title)
                else:
                    self.download("http://www.xiaohuar.com" + big_img, img_title)

    # 图片下载
    def download(self, big_img, img_title):
        print('正在下载', big_img)
        # 发起请求
        reponse = requests.get(url=big_img, headers=self.headers)

        # 读取二进制内容
        content = reponse.content

        #图片地址
        img_dir = self.dir + img_title + "/" + big_img[-20::]

        # 保存到本地
        with open(img_dir, 'wb') as f:
            f.write(content)


if __name__ == "__main__":
    xhs = XHSpider()
    #这正确的逻辑应该自动提取下一页，然后自动加载，不过数据量不大。可以简单通过循环提取。
    for i in range(0, 44):
        print('爬取第%d页' % i)
        xhs.pn = i  # 把每页赋值给pn
        xhs.loadpage()

