#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AES加解密工具类
# @author yetc
# @date 2018-10-19
#
# 依赖：pycrypto, pymysql
# AES 1000;MD5 1007;工资1021

import sys
import pymysql

from Crypto.Cipher import AES
from Crypto.Hash import MD5
from binascii import a2b_hex, b2a_hex

# KMI数据库连接信息，需要从此库中查询并获取KEY
_kmi_db_ip = "10.16.89.232"  # 10.16.89.232
_kmi_db_port = 3306
_kmi_db = "db_kmi"
_kmi_user = "root"
_kmi_psw = "123456"
_core_slave_conn = pymysql.connect(_kmi_db_ip, _kmi_user, _kmi_psw, _kmi_db, _kmi_db_port, charset="utf8")
_sec_cursor = _core_slave_conn.cursor()

# 默认的AES key
_default_aes_key = "abf72629c980f9a7"


def _get_sec_key(sec_key_id):
    _sec_cursor.execute("SELECT aes_key from db_kmi.t_seckeyinfo WHERE sec_key_id=%d" % sec_key_id)
    return _sec_cursor.fetchone()[0]


def _get_md5_keys(sec_key_id):
    _sec_cursor.execute("SELECT pri_key, aes_key from db_kmi.t_seckeyinfo WHERE sec_key_id=%d" % sec_key_id)
    return _sec_cursor.fetchone()


class MideaMd5:

    _md5_salt = None

    def __init__(self, sec_key_id):
        md5_keys = _get_md5_keys(sec_key_id)
        key_of_salt = Aes(_default_aes_key).decrypt(md5_keys[1])  # 从数据库表中aes_key字段中解密得到加密salt值的AES秘钥
        self._md5_salt = Aes(key_of_salt).decrypt(md5_keys[0])  # 解密数据库表中pri_key得到salt值

    def md5(self, context):
        plain = context + "&key=%s" % self._md5_salt
        return MideaMd5.md5_without_salt(plain)

    @staticmethod
    def md5_without_salt(context):
        return b2a_hex(MD5.new(context.encode("UTF-8")).digest()).decode()


class MideaAes:

    # 加解密使用的Aes对象
    _aes = None

    def __init__(self, sec_key_id):
        aes_key = Aes(_default_aes_key).decrypt(_get_sec_key(sec_key_id))
        self._aes = Aes(aes_key)

    def encrypt(self, plain):
        return self._aes.encrypt(plain)

    def decrypt(self, cipher):
        return self._aes.decrypt(cipher)


class Aes:

    _instance = None

    def __init__(self, key, mode=AES.MODE_ECB):
        self._instance = AES.new(key, mode, b'0000000000000000')

    def encrypt(self, plain):
        # 增加PKCS5Padding补位
        block = AES.block_size
        pad = lambda s: s + (block - len(s) % block) * chr(block - len(s) % block).encode()

        enc_byte = self._instance.encrypt(pad(plain.encode()))
        return b2a_hex(enc_byte).decode()

    def decrypt(self, cipher):
        # 去除PKCS5Padding补位
        unpad = lambda s: s[0:-s[-1]]

        dec_byte = self._instance.decrypt(a2b_hex(cipher))
        return unpad(dec_byte).decode()


if __name__ == "__main__":

    _mode = sys.argv[1].upper() if len(sys.argv) > 1 else ""
    _param = sys.argv[2] if len(sys.argv) > 2 else ""
    _key = sys.argv[3] if len(sys.argv) > 3 else ""

    _str = "-----------------------------------\nResult: "
    if _mode == "E":
        print(_str + Aes(1000).encrypt(_param))
    elif _mode == "D":
        print(_str + Aes(1000).decrypt(_param))
    elif _mode == "MD5":
        print(_str + MideaMd5(1007).md5(_param))
    else:
        print("OPTIONS: <e/d> <input parameter>")

    # # test codes for aes enc/dec
    # plain = '1'
    # cipher = MideaAes(1000).encrypt(plain)
    # print("cipher:%s  %s" % (cipher, cipher == "c4cbb752164049338c0d3620871c373d"))
    #
    # print("plain text:%s  %s" % (MideaAes(1000).decrypt(cipher), plain == "1"))
    #
    # # test md5
    # md5_value = MideaMd5(1007).md5("1")
    # print("md5:%s %s" % (md5_value, md5_value == "4a76f8d1fadacbbad964dc72a0942ed6"))

