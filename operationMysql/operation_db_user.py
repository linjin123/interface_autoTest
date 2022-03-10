#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: linxy57
# @Date : 2021-11-22
# @Desc :db_user数据库操作



from common.common_db import OperationMysql

class OperationDbUser(object):
    '''
        operation of db user
    '''

    def __init__(self):
        self._mysql = OperationMysql("db_user")

    # 根据用户登录名查询用户ID
    def query_user_id_by_login_name(self, payer_login_name):
        sql = "select user_id from db_user.t_user_login where status = 1 " \
              "and login_name ='%s' and plat_id = 1 limit 1" % payer_login_name
        res = self._mysql.query(sql)
        if res:
            return res[0]["user_id"]
        else:
            return None

    def query_escrow_act_mapping(self, partner):
        res = self._mysql.query(
            'SELECT * FROM db_user.t_escrow_act_mapping WHERE partner = "%s" and act_type="21" and status="2"' % partner)
        if res:
            return res[0]
        else:
            return None




if __name__ == '__main__':
    operation_act = OperationDbUser()
    pay_total_no = "midea1"
    a = 1
    res = []
    while True:
        data = operation_act.query_user_id_by_login_name(pay_total_no)
        res.append(data)
        a = a+1
        if a > 10:
            break
    print(len(res))
    print(res)



