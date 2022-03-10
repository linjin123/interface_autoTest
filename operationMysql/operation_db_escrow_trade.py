import time

from common.common_db import OperationMysql
import pymysql
from common.config import Config

config = Config()


class OperationDbEscrowTrade(object):
    def __init__(self):
        #     self.db = db
        self.op_mysql = OperationMysql("db_escrow_trade")

    # 根据托管交易流水号查询托管交易流水
    def query_trade_flow(self, trade_flow_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_escrow_trade.t_trade_flow WHERE trade_flow_no="%s"' % trade_flow_no)
        if res:
            return res[0]
        else:
            return None

    #
    def update_trade_flow(self, trade_flow_no):
        res = self.op_mysql.update(
            'UPDATE db_escrow_trade.t_trade_flow SET pay_inner_status = 5 WHERE trade_flow_no="%s"' % trade_flow_no)

    # 根据托管交易总单号查询托管交易总单
    def query_pay_total_order(self, pay_total_no):
        res = OperationMysql("db_escrow_trade").query(
            'SELECT * FROM db_escrow_trade.`t_trade` WHERE trade_no="%s"' % pay_total_no)
        if res:
            return res[0]
        else:
            return None

    # 根据原托管交易总单号查询托管交易退款总单
    def query_pay_total_by_origi_pay_total_no(self, origi_pay_total_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_escrow_trade.`t_trade` WHERE origi_trade_no= "%s"' % origi_pay_total_no)
        return res

    # 根据托管交易总单号查询托管交易流水列表
    def query_pay_flow_list_by_pay_total_no(self, pay_total_no):
        res = self.op_mysql.query('SELECT * FROM db_escrow_trade.`t_trade_flow` WHERE trade_no = "%s" and trade_flow_type = 7' % pay_total_no)
        return res

    # 根据交易订单号查询托管交易单号(托管总单号)
    def query_trade_no_by_rele_order_no(self, rele_order_no):
        res = self.op_mysql.query(
            'SELECT trade_no FROM db_escrow_trade.`t_trade` WHERE rele_order_no= "%s"' % rele_order_no)
        return res

    # 根据交托管总单号查询托管重复支付退款流水
    def query_pay_flow_by_pay_total_no(self, pay_total_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_escrow_trade.`t_trade` WHERE trade_no = "%s" and origi_trade_no = "%s" ' % (pay_total_no,pay_total_no))
        return res

if __name__ == '__main__':
    # res = OperationDbEscrowTrade().query_trade_flow('1021202111120000002407-100-02')
    # print(res)
    # OperationDbEscrowTrade().update_trade_flow('1021202111120000002407-100-02')
    # time.sleep(5)
    # res = OperationDbEscrowTrade().query_trade_flow('1021202111120000002407-100-02')
    # print(res)
    a = OperationDbEscrowTrade().query_trade_no_by_rele_order_no("10011000011005202112230000001627")
    c = a[0]["trade_no"]
    print(a[0]["trade_no"])
    b = OperationDbEscrowTrade().query_pay_total_order(c)
    print(b)