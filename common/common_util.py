import requests, unittest
import json, time
import uuid, random
import hashlib, re
from collections import OrderedDict
from common.config import Config

config = Config()


class data_init():
    '''数据初始化'''
    def __init__(self):
        URL = "URL"
        self.base_url = config.getConfigData(URL, 'base_url')
        self.sign_url = self.base_url + '/rsa/getSign.htm'
        # self.sign_url = self.base_url + '/ rsa / sign.get.htm'
        self.checkSign_url = self.base_url + '/rsa/checkSign.htm'
        self.encode_url = self.base_url + '/aes/encode.htm'
        self.decode_url = self.base_url + '/aes/decode.htm'

    def get_AES(self, aes_source, aes_key):
        aes_data = {"source": "%s" % aes_source, "key": "%s" % aes_key}
        # print(aes_data)
        r = requests.post(self.encode_url, aes_data)
        result = r.json()
        print(result)
        return result["encode_value"]

    def token_time(self):
        now_time = time.time()
        token_time = time.strftime("%Y%m%d%H%M%S", time.localtime(now_time))
        return token_time

    def req_seq_number(self):
        '''动态请求序列号'''
        seq_number = str(uuid.uuid4())
        return seq_number.replace('-', '')

    def req_seq_no(self):
        '''动态请求序列号'''
        seq_number = str(uuid.uuid4())
        return seq_number.replace('-', '')

    def Md5_to_Paramar(self, sign_str):
        '''生成待加密的密码'''
        md5 = hashlib.md5()
        self.sign_str = str(sign_str)
        sign_bytes_utf8 = self.sign_str.encode(encoding="utf-8")
        md5.update(sign_bytes_utf8)
        sign_md5 = md5.hexdigest()
        return sign_md5

    def get_plain_text(self, send_data):
        od = sorted(send_data.items(), key=lambda item: item[0])
        ret_str = ''
        for index in range(od.__len__()):
            if od[index][1] == '':
                pass
            else:
                ret_str += "%s=%s&" % (od[index][0], od[index][1])
        if ret_str.__len__() > 1:
            ret_str = ret_str[:-1]
        return ret_str

    def get_sign(self, send_sign):
        """将排序后的字段发送到RSA"""
        self.sign_data = self.Md5_to_Paramar(send_sign)
        send_data = {"source": "%s" % self.sign_data}
        r = requests.post(self.sign_url, send_data)
        result = r.json()
        return result['sign']

    def get_sign_no_sort(self, sign_data):
        print("self.sign_url", self.sign_url)
        # print("sign_data",sign_data)
        r = requests.post(self.sign_url, sign_data)
        result = r.json()
        return result['sign']

    # def getBg_sign(self, sign_data):
    #     print("sign_data", sign_data)
    #     sign_url = "https://bg.mideaepayuat.com/MD5OrTWSignExceptBlank.json"
    #     r = requests.post(sign_url, sign_data)
    #     result = r.json()
    #     return result['sign']

    def serial_no(self):
        num = random.randint(1, 99)
        serial_no = "mpaytest" + time.strftime("%Y%m%d%H%M%S") + str(num)
        return serial_no

    def serial_Sub_no(self):
        num = random.randint(1, 99)
        serial_no = "mpaytestSubBatch" + time.strftime("%Y%m%d%H%M%S") + str(num)
        return serial_no

    def serial_Bath_no(self):
        num = random.randint(1, 99)
        serial_no = "mpaytestBatch" + time.strftime("%Y%m%d%H%M%S") + str(num)
        return serial_no

    def refund_no(self):
        num = random.randint(1, 99)
        refund_no = "mpaytestrefund" + time.strftime("%Y%m%d%H%M%S") + str(num)
        return refund_no

    def Get_return_cookies(self):
        url = 'https://www.mideaepay.com/index.htm'
        userLogin = '13510182222'
        send_data = {"userLogin": "%s" % userLogin,
                     "self.UM_distinctid": "1624683a538a74-06952d48f2e883-3f3c5501-100200-1624683a53944e",
                     'self.fp_ver': '3.4.2',
                     "self.Js_page_resize_close_clicked": "true",
                     'self.ctrlPort': '65000',
                     'self.bgmideaepayjsessionid': '431f210aa8c44415bb1389d0e7633bf0',
                     "self.CNZZDATA1260019095": '803108807-1522496585-%7C1523956510',
                     "self.pay1payjsessionid": '0c60723d6bef4934971783afc6021db0',
                     "self.BSFIT_OkLJUJ": '8YIEHL5L9SX779XZ',
                     "self.checkPortSuccess": '1'}
        r = requests.get(url, send_data, verify=False)
        self.cookies = r.cookies
        return self.cookies

    def get_pay_pwd(self, paypwd, salt, paykey):
        # 获取支付密码 (md5(md5(密码明文 + salt) + si))
        password = paypwd + salt
        first = data_init().Md5_to_Paramar(password)
        secon = first + paykey
        paypwd = data_init().Md5_to_Paramar(secon)
        return paypwd

    def sub_orders_json_to_string(self, send_data):
        """
        Functions:
            合单交易时，将OperationYaml.getData_payData获取的列表类型的sub_orders转换为字符串类型
        Parameters:
            send_data: OperationYaml.getData_payData获取的send_data数据
        Returns:
            sub_orders_string: 字符串类型的sub_orders,如：'[{"order1":"1"},{"order2":"2"}]'
        """

        sub_order_list = send_data["sub_orders"]
        sub_orders_string = json.dumps(sub_order_list, ensure_ascii=False)
        return sub_orders_string

    def sub_orders_string_to_json(self, send_data):
        """
        Functions:
            合单交易时，将字符串类型的sub_orders转换为列表类型
        Parameters:
            send_data: 合单支付时发送的参数数据
        Returns:
            sub_orders_json: 子单列表,如：[{"order1":"1"},{"order2":"2"}]
        """

        sub_order_string = send_data["sub_orders"]
        sub_orders_json = json.loads(sub_order_string)
        return sub_orders_json


if __name__ == "__main__":
    # data_init().req_seq_number()
    data_init().get_AES("6229882000123081", "6fb834c72a25c2c2")
