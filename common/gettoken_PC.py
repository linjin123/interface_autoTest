import requests
import json,time
import uuid,random
import hashlib,re
from common.common_util import data_init
from collections import OrderedDict
from common.logger import logger

class GetToken():
    def get_token(url, send_data):
        # url = 'https://in.mideaepayuat.com/gateway.htm'
        url = url["B2C_trade_url"]
        req_seq_number = data_init().req_seq_number()
        partner = send_data["partner"]
        plat_id = '1'
        login_name = send_data["payer_login_name"]
        token_time = data_init().token_time()
        '''获取token'''
        token_data = OrderedDict()
        token_data["service"] = "auth_token"
        token_data["version"] = "3.0.0"
        token_data["req_seq_no"] = "%s" % req_seq_number
        token_data["partner"] = "%s" % partner
        token_data["input_charset"] = "UTF-8"
        token_data["language"] = "ZH-CN"
        token_data["sign_type"] = "MD5_RSA_TW"
        token_data["terminal_type"] = send_data["terminal_type"]
        token_data["login_name"] = "%s" % login_name
        token_data["token_time"] = "%s" % token_time
        token_data["ip"] = "127.0.0.1"
        token_data["session_id"] = "869169037622936"

        token_data["sign"] = data_init().get_sign_no_sort(token_data)
        r = requests.post(url, token_data, verify=False)
        result = r.json()
        token = result['token']
        logger.info(token)
        return (token, token_time)


if __name__ == '__main__':
    gettoken = GetToken()
    gettoken.get_token()
