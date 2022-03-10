import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
import os

cfg = dict()
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(BASE_DIR, "../"))


class Email(object):
    def read_config(self):
        config_path = os.path.join(BASE_DIR + "/config.json")
        with open(config_path, 'r') as f:
            email_config = json.load(f)

        cfg["mail_host"] = email_config.get("mail_host", "smtp.midea.com")
        cfg["mail_user"] = email_config.get("mail_user", "dev_mideapay@midea.com")
        cfg["mail_passwd"] = email_config.get("mail_passwd", "Mpay@202002")
        cfg["sender"] = email_config.get("sender", "dev_mideapay@midea.com")
        cfg["receivers"] = email_config.get("receivers", "xiongyc9@midea.com")
        cfg["subject"] = "支付退款自动化Allure测试报告"
        cfg["mysql_host"] = email_config.get("mysql_host", "10.16.157.93")
        cfg["mysql_user"] = email_config.get("mysql_user", "u_test_prd")
        cfg["mysql_passwd"] = email_config.get("mysql_passwd", "Mysql@Test*2018$")

    def send_mail(self, message_text):
        message = MIMEText(message_text, 'html', 'utf-8')
        message["From"] = Header(cfg["sender"], 'utf-8')
        message["To"] = Header(cfg["receivers"], 'utf-8')
        message["subject"] = Header(cfg["subject"], 'utf-8')

        try:
            smtp_obj = smtplib.SMTP_SSL(cfg["mail_host"])
            smtp_obj.connect(cfg["mail_host"], 465)
            smtp_obj.login(cfg["mail_user"], cfg["mail_passwd"])
            smtp_obj.sendmail(cfg["sender"], cfg["receivers"].split(','), message.as_string())
            print("Send email successful!")
        except smtplib.SMTPException:
            print("Error: Send email fail!")


if __name__ == "__main__":
    email_content_path = os.path.join(BASE_DIR + "/email_content")
    with open(email_content_path, 'r') as f:
        ec = f.read()
    email_url = ec[ec.find("<")+1 : ec.find(">")-1]
    email_contents = '''
    <p>支付退款自动化测试已完成，详见：</p>
    <p><a href={}>Allure测试报告</a></p>
    '''.format(email_url)

    Email().read_config()
    Email().send_mail(email_contents)
