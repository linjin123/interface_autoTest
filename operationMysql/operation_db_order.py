import datetime
from common.common_db import OperationMysql


class OperationDbOrder(object):
    # def __init__(self, db):
    #     self.op_mysql = OperationMysql(db)
    def __init__(self):
        self.op_mysql = OperationMysql("db_order")

    # 查询合单订单信息
    def query_main_trade_detail(self, trade_no):
        res = self.op_mysql.query('SELECT * FROM db_order.`t_main_trade` WHERE trade_no = "%s"' % trade_no)
        if res:
            return res[0]
        else:
            return None

    # 查询交易订单信息
    def query_trade_detail(self, out_trade_no, partner):
        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE out_trade_no = "%s" and partner = "%s"' % (out_trade_no, partner))
        if res:
            trade_detail = res[0]
            return trade_detail
        else:
            return None

    # 查询交易订单信息
    def query_trade_list_by_main_trade_no(self, main_trade_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE main_trade_no = "%s"' % main_trade_no)
        if res:
            return res
        else:
            return None

    # 根据三级业务类型查询交易单
    def query_trade_by_business_type(self, business_type1, business_type2, business_type3):

        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE business_type1="%s" AND business_type2="%s" AND business_type3="%s" '
            ' AND arrival_status=3 AND trade_status=3 AND market_amount>=1 '
            'AND have_refund_amount<=0 and out_trade_no like "mpaytest2%%"  '
            'ORDER BY create_time DESC LIMIT 1' % (business_type1, business_type2, business_type3))
        if res:
            return res[0]
        else:
            return None

    # 根据三级业务类型和交易类型查询交易单
    def query_trade_by_business_type_and_trade_type(self, business_type1, business_type2, business_type3,guarantee_type):

        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE business_type1="%s" AND business_type2="%s" AND business_type3="%s" '
            ' AND arrival_status=3 AND trade_status=3 AND market_amount>=1 '
            'AND have_refund_amount<=0 and out_trade_no like "mpaytest2%%"  and guarantee_type="%s"'
            'ORDER BY create_time DESC LIMIT 1' % (business_type1, business_type2, business_type3,guarantee_type))
        if res:
            return res[0]
        else:
            return None

    # 根据三级业务类型查询交易订单（不含营销金额）
    def query_trade_by_business_types_no_market(self, except_value, sysdate, confirm_receive_status):
        business_type1 = except_value["business_type1"]
        business_type2 = except_value["business_type2"]
        business_type3 = except_value["business_type3"]
        guarantee_type = except_value["guarantee_type"]
        arrival_status = except_value["origi_arrival_status"]

        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE business_type1="%s" '
            'AND business_type2="%s" AND business_type3="%s" AND trade_status= 3 '
            'AND arrival_status="%s" AND have_refund_amount = 0 AND out_trade_no LIKE "mpaytest%%"'
            'AND pay_time LIKE "%s" AND guarantee_type= "%s" AND confirm_receive_status = "%s"LIMIT 1' % (
                business_type1, business_type2, business_type3, arrival_status, sysdate, guarantee_type, confirm_receive_status))
        if res:
            return res[0]
        else:
            return None

        # 根据三级业务类型查询交易订单（不含营销金额）

    def query_trade_by_confirm_receive_status_no_market(self, except_value, sysdate):
        business_type1 = except_value["business_type1"]
        business_type2 = except_value["business_type2"]
        business_type3 = except_value["business_type3"]
        guarantee_type = except_value["guarantee_type"]
        arrival_status = except_value["origi_arrival_status"]
        confirm_receive_status = except_value["confirm_receive_status"]
        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE business_type1="%s" '
            'AND business_type2="%s" AND business_type3="%s" AND trade_status= 3 '
            'AND arrival_status="%s" AND have_refund_amount = 0 AND out_trade_no LIKE "mpaytest%%"'
            'AND pay_time LIKE "%s" AND guarantee_type= "%s" AND confirm_receive_status = "%s"LIMIT 1' % (
                business_type1, business_type2, business_type3, arrival_status, sysdate, guarantee_type,
                confirm_receive_status))
        if res:
            return res[0]
        else:
            return None

    # 根据三级业务类型查询昨天的交易订单（不含营销金额）
    def query_trade_by_business_types_and_last_date_no_market(self, except_value, sure_receive_time):
        business_type1 = except_value["business_type1"]
        business_type2 = except_value["business_type2"]
        business_type3 = except_value["business_type3"]
        guarantee_type = except_value["guarantee_type"]
        confirm_receive_status = except_value["confirm_receive_status"]
        arrival_status = except_value["origi_arrival_status"]
        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_trade WHERE business_type1="%s" '
            'AND business_type2="%s" AND business_type3="%s" AND trade_status= 3 '
            'AND arrival_status="%s" AND have_refund_amount = 0 AND out_trade_no LIKE "mpaytest%%"'
            'AND sure_receive_time LIKE "%s" AND guarantee_type= "%s" AND confirm_receive_status = "%s"LIMIT 1' % (
                business_type1, business_type2, business_type3, arrival_status, sure_receive_time, guarantee_type,
                confirm_receive_status))
        if res:
            return res[0]
        else:
            return None

    # 通过trade_no查询订单表数据
    def query_trade_detail_by_trade_no(self, trade_no):
        sql = "SELECT * FROM db_order.t_trade WHERE trade_no = '%s';" % trade_no
        res = self.op_mysql.query(sql)
        if res:
            trade_detail = res[0]
            return trade_detail
        else:
            return None

    # 通过trade_no修改订单表交易时间
    def update_pay_time_by_trade_no(self, trade_no, pay_time):
        self.op_mysql.update('UPDATE db_order.`t_trade` SET pay_time = "%s" where trade_no = "%s"' % (pay_time, trade_no))

    # 通过trade_no修改订单表交易时间
    def update_pay_time_by_main_trade_no(self, main_trade_no, pay_time):
        self.op_mysql.update('UPDATE db_order.`t_trade` SET pay_time = "%s" where main_trade_no = "%s"' % (pay_time, main_trade_no))

    # 查询退款单
    def query_refund_trade_by_refund_no(self, refund_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_refund WHERE refund_no="%s"' % refund_no)
        if res:
            return res[0]
        else:
            return None

    # 通过退款外部订单号+商户号查询退款订单
    def query_refund_trade_by_out_trade_no(self, out_trade_no, partner):
        res = self.op_mysql.query(
            'SELECT * FROM db_order.t_refund WHERE out_trade_no="%s" and partner = "%s"' % (out_trade_no, partner))
        if res:
            return res[0]
        else:
            return None

    # 通过原交易订单号查询所有退款订单
    def query_refund_list_by_origi_trade_no(self, origi_trade_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_order.`t_refund` WHERE origi_trade_no = "%s" and refund_status = 3' % origi_trade_no)
        return res

    # 通过out_trade_no查询trade_no
    def query_trade_no_by_out_trade_no(self, out_trade_no):
        sql = "select trade_no from db_order.t_trade where out_trade_no = '%s'" % out_trade_no
        res = self.op_mysql.query(sql)
        if res:
            trade_no = res[0]["trade_no"]
            return trade_no
        else:
            return None

        # 通过out_trade_no查询trade_no

    def query_trade_info_by_out_trade_no(self, out_trade_no):
        sql = "select * from db_order.t_trade where out_trade_no = '%s'" % out_trade_no
        res = self.op_mysql.query(sql)
        if res:

            return res[0]
        else:
            return None

    # 通过trade_no查询pay_total_no
    def query_pay_total_no_by_trade_no(self, trade_no):
        sql = "select pay_total_no from db_order.t_trade where trade_no='%s' limit 1" % trade_no
        res = self.op_mysql.query(sql)
        if res:
            trade_no = res[0]["pay_total_no"]
            return trade_no
        else:
            return None

    # 通过trade_no查询main_trade_no
    def query_main_trade_no_by_trade_no(self, trade_no):
        sql = "select main_trade_no from db_order.t_trade where trade_no='%s' limit 1" % trade_no
        res = self.op_mysql.query(sql)
        if res:
            main_trade_no = res[0]["main_trade_no"]
            return main_trade_no
        else:
            return None


    def query_repeat_pay_refund_no_by_trade_no(self, trade_no):
        sql = "select * from db_order.t_repeat_pay_refund where origi_trade_no='%s' limit 1" % trade_no
        res = self.op_mysql.query(sql)
        if res:
            results = res[0]
            return results
        else:
            return None

    #关单
    def close_Order_trade_by_trade_no(self,trade_no):
        self.op_mysql.update(
            'UPDATE db_order.t_trade set trade_status = 9,close_time=NOW(),modify_time =NOW()  where out_trade_no ="%s"'%trade_no)

    #根据交易订单号查询关单退款表
    def query_inner_refund_by_trade_no(self,trade_no):
        sql = "select * from db_order.t_inner_refund where origi_trade_no='%s' limit 1" % trade_no
        res = self.op_mysql.query(sql)
        return res
        # if res:
        #     results = res[0]
        #     return results
        # else:
        #     return None

    # 通过trade_no修改确认收货状态和时间
    def update_confirm_receive_status_by_trade_no(self, trade_no):
        self.op_mysql.update('UPDATE db_order.`t_trade` SET confirm_receive_status = 1 ,close_time=NOW() where trade_no = "%s"' % ( trade_no))



if __name__ == '__main__':
    db_order = OperationDbOrder("db_order")
    trade_no = '10011010077091202111260000000923'
    result = db_order.query_main_trade_no_by_trade_no(trade_no)
    print(result)
