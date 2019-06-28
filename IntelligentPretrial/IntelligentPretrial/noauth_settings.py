import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 服务器调试模式, 值为False时不自动重启服务器
DEBUG = False

# 登录认证
AUTH = False

# 变更自动重启
AUTORELOAD = False

# cookie secret key
COOKIE_SECRET = '@fuj*qpgm0v6wf*j6@_nv$s168vk_uro(=l8th$*ux^jxf&(ia'

# 是否开启csrf攻击防范
XSRF_COOKIES = False

# 允许访问的HOST配置
ALLOWED_HOSTS = []

# 模块配置
MODULES = [
    "microserver.addons.swagger",
    "microserver.addons.smsauth",
    "questionaire.handlers",
    "calculator.handlers",
    "lawdocument.handlers",
    "smsauth",
    "docdispose.handlers",
]

# 缓存
CACHES = {}

# 命令配置
COMMANDS = []

# 数据库配置
DATABASES = {
    "es": {
        "timeout" : 60,
        "type" : "es",
        "http_auth" : [
            "python",
            "XK3cFTp0Noci"
        ],
        "hosts" : [
            "web.aegis-info.com:9200",
            "web2.aegis-info.com:9200"
        ]
    },
    "mongodb": {
        "host": "mongo.aegis-info.com",
        "port": 10040,
        "user":"tag",
        "password":"tag@qd2018",
        "db":"tag"
    },
    "mongodb_test": {
        "host": "192.168.11.99",
        "port": 9933,
        "replicaset": True
    },
    "intelligent": {
    "host":"49.4.14.38",
    "port":27018,
    "user":"intelligent",
    "password":"intelligent@Aegis",
    "db":"intelligent"
    },
    "mysql":{
        "host":"49.4.14.38",
        "port": 3306,
        "user":"root",
        "passwd":"shield",
        "database": "tag"
    },
    "hwmysql":{
        "host":"dev.database.aegis-info.com",
        "port": 4000,
        "user":"hw-tag",
        "passwd":"!Hwtag@2018QD#)(*",
        "database": "tag"
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "redis_max_connection": 50,
        "db":0
    },
    "redis_product": {
        "host": "redis1.aegis-info.com",
        "port": 6379,
        "redis_max_connection": 50,
        "db": 0,
        "password": "Aegis@2018"
    }
}

# 静态文件目录
STATIC = ""

# 模板文件目录
TEMPLATE = ""

# 算法模型目录
DATA = ""

# 每页大小
PAGE_SIZE = 10

# 分页展示数量
PAGE_SHOW = 10

# 接口文档配置
SWAGGER = dict(
    SWAGGER_UI_ADDRESS = "http://192.168.11.88:8100/swagger", # swagger ui 访问地址
    SWAGGER_URL = "/IntelligentPretrial/docs",                           # 项目swagger接口文档访问路径
    SWAGGER_INDEX_URL = "/IntelligentPretrial/docs/index.yml",           # 项目swagger接口文档首页访问地址
    SWAGGER_INDEX_FILENAME = "index.yml",               # 项目swagger接口文档首页文件名
    SWAGGER_PROJECT_NAME = "智能预审2.0接口文档",                   # 接口文档项目名称
    SWAGGER_BASE_URL = "http://192.168.11.88:8100",         # 项目swagger接口文档访问地址
    SWAGGER_MODULES = [
        "questionaire.handlers",
        "calculator.handlers",
        "lawdocument.handlers",
        "docdispose.handlers",
        "smsauth"
    ],
)

USERAUTH = {
    "slat": "intelligentpretrial",
    # "login_expires_days": None, # None表示关闭浏览器就退出登录
    "login_expires": 60*60*24*7, # 登录过期时间，以秒为单位
    # "csrf_expires_days": None, # None表示关闭浏览器就退出登录
    "csrf_expires": 60*60*2, # csrf token 过期时间，以秒为单位
    "ip_limit": True,
    "include_locations": ["江苏省南京市", "北京市", "辽宁省", "吉林省"]
}

PROXY = dict(
    proxyHost = "http-dyn.abuyun.com",
    proxyPort = "9020",
    proxyUser = "H25L1J4U0LY1M07D",
    proxyPass = "0DC2B6112B115C2E",
)

# SMS_URL = "http://180.96.14.78:8041/api/sms/send_message"
SMS_URL = "http://qa.py.api.aegis-info.com/api/sms/send_message"