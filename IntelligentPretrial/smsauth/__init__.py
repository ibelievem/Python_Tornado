# @Time    : 2018/7/19 12:19
# @Author  : Niyoufa
from microserver.addons.smsauth.handlers import *

handlers = [
    (r"/intelligentpretrial/smsauth/exists", UserExistsHandler),
    (r"/intelligentpretrial/checkcode/mobile/checkcode", SmsMobileCheckCode),
    (r"/intelligentpretrial/smsauth/register", RegisterHandler),
    (r"/intelligentpretrial/smsauth/login", LoginHandler),
    (r"/intelligentpretrial/smsauth/logout", SmsLogoutHandler),
    (r"/intelligentpretrial/smsauth/userinfo", SmsCurrentLoginUserInfoHandler),
]