#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiongyc9
# @Date : 2021-11-22
# @Desc :db_bank_act表数据库操作


from common.common_db import OperationMysql

class OperationDbBankAct(object):
    '''
        operation of db bank act
    '''

    def __init__(self):
        self._mysql = OperationMysql("db_bank_act")

    # 根据支付总单号查询银行账务流水
    def query_bank_act_by_pay_total_no(self, pay_total_no):
        sql = 'SELECT dc_type,tran_amount,inner_remark,trade_msg from db_bank_act.t_bank_history  WHERE pay_no = "%s" limit 10' % pay_total_no
        res = self._mysql.query(sql)
        if res:
            return res
        else:
            return None




if __name__ == '__main__':
    operation_act = OperationDbBankAct()
    pay_total_no = "1021202111210000000369"
    data = operation_act.query_bank_act_by_pay_total_no(pay_total_no)
    print(len(data))



