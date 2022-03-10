#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiongyc9
# @Date : 2021-11-22
# @Desc :db_act表数据库操作


from common.common_db import OperationMysql

class OperationDbAct(object):
    '''
        operation of db act
    '''

    def __init__(self):
        self._mysql = OperationMysql("db_act")
    # 根据支付总单号查询账务流水
    def query_act_history_by_pay_total_no(self, pay_total_no):
        sql = 'SELECT user_id,act_type,tran_amount,dc_type,user_remark,trade_msg from db_act.t_act_history WHERE pay_no = "%s" ' \
              'and trade_time > DATE_ADD(NOW(),INTERVAL -2 DAY) order by trade_time,pay_flow_no asc limit 10' % pay_total_no
        res = self._mysql.query(sql)
        if res:
            return res
        else:
            return None

    def get_act_history(self, pay_no):
        print("0000000000000000",pay_no)
        res = OperationMysql("db_act").query(
            'SELECT dc_type,tran_amount,inner_remark,trade_msg,pay_flow_type FROM db_act.t_act_history WHERE pay_no= "%s"' % pay_no)
        if res:
            return res
        else:
            return None






if __name__ == '__main__':
    operation_act = OperationDbAct()
    pay_total_no = "1021202112190000001064"
    data = operation_act.get_act_history(pay_total_no)
    print(len(data))




