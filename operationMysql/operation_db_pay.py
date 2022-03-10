from common.common_db import OperationMysql

class OperationDbPay(object):

    def __init__(self):
        self.op_mysql = OperationMysql("db_pay")


    def get_pay_flow(self,pay_total_no):
        # pay_total_no=self.get_pay_total_no(out_trade_no)["pay_total_no"]
        res = self.op_mysql.query('SELECT pay_flow_no FROM db_pay.t_pay_flow  WHERE pay_total_no="%s"'% pay_total_no)

        if res:
            return res
        else:
            return None




    def query_pay_total_by_trade_no(self,trade_no):
        sql = "SELECT * FROM db_pay.t_pay_total WHERE rele_order_no  = '%s';" % trade_no
        res = self.op_mysql.query(sql)
        if res:
            return res[0]
        else:
            return None

    def query_origi_pay_total_by_trade_no(self,refund_no):
        sql = "SELECT * FROM db_pay.t_pay_total WHERE origi_rele_order_no = '%s';" % refund_no
        res = self.op_mysql.query(sql)
        if res:
            return res[0]
        else:
            return None

    def query_pay_total_by_refund_no(self,refund_no):
        sql = "SELECT * FROM db_pay.t_pay_total WHERE refund_no = '%s';" % refund_no
        res = self.op_mysql.query(sql)
        if res:
            return res[0]
        else:
            return None

    def query_pay_flow_by_trade_no(self,trade_no):
        sql = "SELECT * FROM db_pay.t_pay_flow where pay_total_no = '%s';" % trade_no
        res = self.op_mysql.query(sql)
        if res:
            return res
        else:
            return None

    # 通过pay_total_no查询流水号
    def query_pay_flow_no_by_pay_total_no(self, pay_total_no):
        sql = "SELECT pay_flow_no FROM db_pay.t_pay_flow WHERE pay_total_no = '%s' order by " \
                              "pay_flow_no asc" % pay_total_no
        res = OperationMysql("db_pay").query(sql)
        if res:
            return res
        else:
            return None

    # 通过pay_total_no查询pos_no
    def query_pos_no_by_pay_total_no(self, pay_total_no):
        sql = "SELECT pos_no FROM db_pay.t_pay_flow WHERE pay_total_no = '%s' limit 1 " % pay_total_no
        res = OperationMysql("db_pay").query(sql)
        if res:
            return res[0]["pos_no"]
        else:
            return None

    # 根据支付总单号查询重复支付退款流水
    def query_pay_flow_by_pay_total_no(self, pay_total_no):
        sql = "SELECT * FROM db_pay.t_pay_flow WHERE pay_total_no = '%s' and origi_pay_total_no = '%s' limit 1 " % (pay_total_no,pay_total_no)
        res = OperationMysql("db_pay").query(sql)
        if res:
            return res[0]
        else:
            return None

    # 根据总单号查询支付流水
    def query_pay_flows_by_pay_total_no(self,pay_total_no):
        sql = "SELECT * FROM db_pay.t_pay_flow where pay_total_no = '%s';" % pay_total_no
        res = self.op_mysql.query(sql)
        if res:
            return res[0]
        else:
            return None




if __name__ == '__main__':
    a = '1021202112240000004085'
    b = OperationDbPay().query_pay_flows_by_pay_total_no(a)
    print(b)
    print(type(b))
    print(len(b))


