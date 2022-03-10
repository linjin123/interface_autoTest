#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : get_data.py 
# @Author: xiangling
# @Date : 2018-9-13 
# @Desc :
from common.common_db import OperationMysql
from collections import OrderedDict

class get_data:
    #获取用户余额
    def trade_no(self,partner,out_trade_no):
        query_sql = "select trade_no from db_order.t_trade where partner = %s and out_trade_no = %s" %(partner, out_trade_no)
        op_msql = OperationMysql("db_order")
        trade_no = op_msql.query(query_sql)
        trade_no = trade_no[0]
        trade_no = trade_no['act_balance']
        return  trade_no

    def user_balance(self,user_id):
        query_sql = "select act_balance from t_act where user_id = %s" % user_id
        op_msql = OperationMysql("db_act")
        act_balance = op_msql.query(query_sql)
        act_balance = act_balance[0]
        act_balance = act_balance['act_balance']
        return  act_balance

    #获取商户交易账户余额
    def partner_balance(self,user_id,act_type):
        query_sql = "select act_balance from t_act where user_id = %s and act_type = %s" % (user_id,act_type)
        op_msql = OperationMysql("db_act")
        act_balance = op_msql.query(query_sql)
        act_balance = act_balance[0]
        act_balance = act_balance['act_balance']
        return  act_balance

    #通过订单号获取订单状态、金额、支付总单号
    def trade_order(self,trade_no):
        query_sql = "select trade_status,pay_amount,pay_total_no from t_trade where trade_no='%s'" % trade_no
        op_msql = OperationMysql("db_order")
        data = op_msql.query(query_sql)
        data = data[0]
        trade_status =data['trade_status']
        pay_amount = data['pay_amount']
        pay_total_no = data['pay_total_no']
        return trade_status,pay_amount,pay_total_no

    #通过支付总单号获取支付金额、支付总单状态
    def pay_total(self,pay_total_no):
        query_sql ="select amount,pay_status from t_pay_total where pay_total_no ='%s'" % pay_total_no
        op_msql = OperationMysql("db_pay")
        data = op_msql.query(query_sql)
        data = data[0]
        amount =data['amount']
        pay_status = data['pay_status']
        return amount,pay_status

    #根据支付总单号获取账务流水
    def act_history(self,pay_no):
        query_sql = "select user_id,act_type,dc_type,tran_amount from db_act.t_act_history where pay_no = '%s'" % pay_no
        op_msql = OperationMysql("db_act")
        data = op_msql.query(query_sql)
        return data
    #根据订单号查询商户通知
    def out_notify(self,order_no):
        query_sql ="select * from t_out_notify where order_no ='%s'" % order_no
        op_msql = OperationMysql("db_partner_notify")
        data = op_msql.query(query_sql)
        return data

    # 根据登录名称查询用户ID
    def get_user_id(self, payer_login_name):
        query_sql = "select user_id from db_user.t_user_login where status = 1 and login_name ='%s' limit 1" % payer_login_name
        op_msql = OperationMysql("db_user")
        data = op_msql.query(query_sql)
        return data


if __name__ == '__main__':
    #get_data().user_balance('900260007')
    #a=get_data().partner_balance(1000011005,11)
    #trade_status, pay_amount, pay_total_no = get_data().trade_order(10011000000021201707170000000072)
    #amount, pay_status=get_data().pay_total(1021201707170000000076)
    # user_id,act_type,dc_type,tran_amount=get_data().act_history(1021201707170000000076)
    # print(user_id, act_type, dc_type, tran_amount)
    trade_no = '10011010077091202111210000002164'
    a = get_data().trade_order(trade_no)[2]
    print(type(a))
    print(a)

