# @Time    : 2018/7/30
# @Author  : Dongrj

import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
from email.utils import parseaddr, formataddr
from tornado.escape import utf8
import os

smtp_server = 'smtp.exmail.qq.com'
user = "support@aegis-data.cn"
password = "Asdf1234!"
from_mail = 'support@aegis-data.cn'
body = '感谢您的咨询，附件中是您所需的{subject}文件，请查阅。'

def formatAddr(address):
    name, addr = parseaddr(address)
    return formataddr((Header(name, 'utf-8').encode('utf-8'), addr))

def send_email(to_mail, subject, body=body, attachment=''):

    msg = MIMEMultipart()
    msg['From'] = formatAddr('擎盾法律人工智能 <%s>' % from_mail)
    msg['To'] = to_mail
    msg['Subject'] = Header(subject, 'utf-8')

    msg.attach(MIMEText(body.format(subject=subject), 'plain', 'utf-8'))
    if attachment:
        with open(attachment, 'rb') as f:
            mime = MIMEBase('application', 'octet-stream')
            mime.set_payload(f.read())
        encoders.encode_base64(mime)
        mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
        msg.attach(mime)
    try:
        smtp = smtplib.SMTP_SSL(smtp_server, port=465)
        smtp.login(user, password)
        smtp.sendmail(from_mail, to_mail, msg.as_string())
        smtp.quit()
    except smtplib.SMTPException as e:
        print('Error: %s' % e)
