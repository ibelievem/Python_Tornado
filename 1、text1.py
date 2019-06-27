import tornado.web
import tornado.ioloop


#定义处理类型
class IndexHandler(tornado.web.RequestHandler):
    #添加一个处理get请求方式的方法
    def get(self):
        #向响应中，添加数据
        self.write('我叫徐伟松')

if __name__ == '__main__':
    #创建一个应用对象
    app = tornado.web.Application([(r'/',IndexHandler)])
    #绑定一个监听端口
    app.listen(8888)
    #启动web程序，开始监听端口的连接
    tornado.ioloop.IOLoop.current().start()



# write()
# 封装响应信息，写响应信息的一个方法

# current()
# 返回当前线程的IOLoop实例对象

# start()
# 启动IOLoop实力对象的IO循环，开启监听
