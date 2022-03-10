import requests
import hashlib
class Method_class():
    '''生成待加密的密码'''
    def Generate_MD5(self,MD5_value):
        MD5=hashlib.md5()
        value=str(MD5_value)
        encoding_value=value.encode(encoding="utf-8")
        MD5.update(encoding_value)
        sign_md5 = MD5.hexdigest()[8:-8]
        return sign_md5
    '''加密'''
    def Encryption(self,key,value):
        url="http://10.16.89.233:20001/aes/encode.htm"
        payload = {'source': value, 'key': key}
        ret = requests.get(url, params=payload, verify=False)
        return ret.json()['encode_value']

    def sign(self):
        url = "http://10.16.89.233:20001/rsa/sign.htm"
        r = requests.post(url,)
        # ret = requests.get(url,params=payload, verify=False)
        #print(r.json())


if __name__ == '__main__':
    aa= Method_class()
    bb='out_trade_no=no123456789&out_trade_time=20160230151618&partner=2000000109&req_seq_number=no123456&key=721107dd774c106746a0508e0cf8f646'
    print(aa.Generate_MD5(bb))



