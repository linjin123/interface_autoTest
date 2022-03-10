#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: linxy57
# @Date : 2021-11-22
# @Desc :db_user数据库操作



from common.common_db import OperationMysql

class OperationDbSettle(object):
    '''
        operation of db user
    '''

    def __init__(self):
        self._mysql = OperationMysql("db_settle")

    # 根据用户登录名查询用户ID
    def query_user_id_by_login_name(self, trade_no):
        sql = "select * from t_settle_data where  order_no='%s' and settle_flag=2" % trade_no
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None


if __name__ == '__main__':
    operation_act = OperationDbSettle()
    trade_no = "10011000000021202101160000000017"
    a = 1
    res = []
    # while True:
    data = operation_act.query_user_id_by_login_name(trade_no)
        # res.append(data)
        # a = a+1
        # if a > 10:
        #     break
    # print(len(res))
    print(data)



