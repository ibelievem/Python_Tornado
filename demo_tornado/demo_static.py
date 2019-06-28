# @__author__ = "周朋飞"

#引入需要的模块
import os,json

import tornado.web #第二种引入方式
from tornado.web import RequestHandler

from tornado.ioloop import IOLoop
# import tornado.ioloop #第二种引入方式

from tornado.httpserver import HTTPServer

#定义数据处理类型
class IndexHandler(tornado.web.RequestHandler):

    # 添加一个处理get请求方式的方法
    def get(self):
        # 返回字符串的方式，在分离开发模式下，比较常用，
        # 经常用于返回JSON字符串，和前端进行ajax交互
        resalt = {
            "data": None,
            "msg": "返回成功",
            "code": 200}
        message = "参数"
        users = [
            {'name':"aa"},
            {'name':'bb'},
            {'name':'cc'},

        ]
        ma_age = 125
        resalt['data'] =users
        self.finish(resalt)

class ParmsHandler(RequestHandler):
    '''
    参数传递
    '''
    # def get(self):
    #
    #     name = self.get_query_argument('name')
    #     # name = self.get_argument('name')
    #     print("get参数：",name)
    #     self.render('index.html')

    def post(self):
        '''
        #接收参数
        :return:
        '''

        info = self.get_argument('name')
        passw = self.get_argument('pass')

        resalt = {
    "data": None,
    "msg": "返回成功",
    "code": 200
                }
        if info and passw:
            resalt['data'] = "登录成功"
            print("请求发送成功！")
            self.finish(resalt)



if __name__ == "__main__":

    #构建webapp
    app = tornado.web.Application([
        #路由配置
        (r'/',IndexHandler,),
        (r'/parms',ParmsHandler),
    ],
        #网页模板文件夹配置
        template_path = os.path.join(os.path.dirname(__file__),'templates'),
        #静态文件夹配置
        static_path = os.path.join(os.path.dirname(__file__),'static'),
        debug=True,
    )
    #监听端口


    print('server is starting...')
    http_server = HTTPServer(app)
    http_server.listen(8899)
    #启动轮询监听
    IOLoop.current().start()