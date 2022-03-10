#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File :
# @Author: xiongyc9
# @Date : 2021-11-22
# @Desc :db_act表数据库操作


from common.common_db import OperationMysql
import json

class OperationDbPartnerNotify(object):
    '''
        operation of db act
    '''

    def __init__(self):
        self._mysql = OperationMysql("db_partner_notify")

    # 根据订单号查询外部通知数据
    def query_out_notify_by_trade_no(self, trade_no):
        sql = "select * from t_out_notify where order_no ='%s' order by create_time desc" % trade_no
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None


    # 根据订单号查询退款外部通知数据
    def query_out_notify_list_by_trade_no(self, trade_no):
        sql = "select * from t_out_notify where order_no ='%s' order by create_time asc" % trade_no
        res = self._mysql.query(sql)
        return res


if __name__ == '__main__':
    notify_list = OperationDbPartnerNotify().query_out_notify_list_by_trade_no(1004202112150000001113579)
    inner_transfer_notify = notify_list[0]
    refund_arrival_notify = notify_list[1]
    print(inner_transfer_notify)
    print(refund_arrival_notify)



