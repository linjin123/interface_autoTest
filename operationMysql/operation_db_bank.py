from common.common_db import OperationMysql

class OperationDbBank(object):
    '''
        operation of db bank
    '''
    def __init__(self):
        self._mysql = OperationMysql("db_bank")

    def query_ebank_tran_by_trade_no(self, trade_no):
        sql = "SELECT * FROM db_bank.t_ebank_tran WHERE trade_no = '%s';" % trade_no
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None

    #通过交易订单号查询渠道pos流水号(网银流水表)
    def query_tran_no_by_trade_no(self, trade_no):
        sql = "SELECT tran_no FROM db_bank.t_ebank_tran WHERE trade_no = '%s';" % trade_no
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None


    def query_ebank_tran_by_pay_total_no(self, pay_total_no):
        sql = "SELECT * FROM db_bank.t_ebank_tran WHERE trade_no = '%s';" % pay_total_no
        res = self._mysql.query(sql)
        if res:
            result = res[0]
            return result
        else:
            return None



        #通过交易订单号查询渠道pos流水号(渠道流水表)
    def query_tran_no_by_pay_flow_no(self, pay_flow_no):
        sql = "SELECT tran_no FROM db_bank.t_bank_tran WHERE pay_item_no = '%s';" % pay_flow_no
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None

    #修改渠道流水表的订单支付状态

    def update_ebank_tran_status_by_trade_no(self,trade_no,pay_status):
        if str(pay_status).upper() == "SUCCESS":
            status = 1
        elif str(pay_status).upper() == "FAIL":
            status = 3
        elif str(pay_status).upper() == "TO_PAY":
            status = 0
        else:
            return None
        sql = "UPDATE db_bank.t_ebank_tran SET pay_status = '%s' WHERE trade_no = '%s';" %(status, trade_no)
        res = self._mysql.update(sql)
        if res:
            result = res[0]
            return result
        else:
            return None

    # 修改渠道流水表的重复支付订单支付状态
    def update_bank_tran_status_by_trade_no(self, pos_no):
        sql = "UPDATE db_bank.t_bank_tran SET pay_status = 1 WHERE tran_no = '%s';" % pos_no
        res = self._mysql.update(sql)
        if res:
            result = res[0]
            return result
        else:
            return None

    # 更新银行接口流水为支付成功
    def update_db_bank_by_pos_no(self, pos_no):
        sql = 'UPDATE db_bank.t_ebank_tran SET pay_status=1 WHERE tran_no="%s"' % pos_no
        res = self._mysql.update(sql)
        if res:
            return res
        else:
            return None

    #更新渠道流水表支付状态为成功
    def update_bank_tran_by_pay_total_no(self, pay_total_no):
        sql = "update  db_bank.t_bank_tran set  pay_status=1 WHERE pay_total_no = '%s';" % pay_total_no
        print("sql",sql)
        res = self._mysql.update(sql)


    # 查询渠道流水支付状态
    def query_bank_tran_by_pay_total_no(self, pay_total_no):
        sql = "select * from   db_bank.t_bank_tran  WHERE pay_total_no = '%s';" % pay_total_no
        print("sql", sql)
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None



if __name__ == '__main__':
    # operation_bank = OperationDbBank()
    # trans_number = "10011000011005202111190000000763"
    #
    # states = ["TO_PAY", "SUCCESS", "FAIL"] # 0 1 3
    # origin_status = operation_bank.query_ebank_tran_by_trade_no(trans_number)
    # print("before test, status is {0}".format(origin_status))
    # for st in  states:
    #     cur_status = operation_bank.query_ebank_tran_by_trade_no(trans_number)
    #     print("begin test, this case we want to set status to {0} and check. cur status is {1}".format(st, cur_status))
    #     #success = 1 ,fail = 3
    #     operation_bank.update_ebank_tran_status_by_trade_no(trans_number, st)
    #     cur_status = operation_bank.query_ebank_tran_by_trade_no(trans_number)
    #     print("====  over ===  cur status is {0}".format(cur_status))

    a = OperationDbBank().query_tran_no_by_trade_no("10011000011005202111190000000763")
    print(a)


