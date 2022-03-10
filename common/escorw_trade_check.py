import logging
import time
from operationMysql.operation_db_escrow_channel import OperationDbEscrowChannel
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
from common.elasticjob import elasticjob
from common.dubbo import dubbo


class EscrowTradeCheck(object):
    def __init__(self):
        self.elasticjob_url = {"elasticjob_url": "http://10.16.157.96:20814"}

    def check_receive_pay_flow(self, trade_no, receive_pay_flow_no):
        # 查询托管交易收款流水
        receive_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(receive_pay_flow_no)
        # step-01判断托管交易收款流水是否存在，存在进入step-02
        if receive_pay_flow_list:
            tran_no = receive_pay_flow_list['pos_no']
            trade_flow_no = receive_pay_flow_list['trade_flow_no']
            receive_pay_inner_status = receive_pay_flow_list['pay_inner_status']
            # step-02判断托管交易收款流水内部状态为“渠道已受理”才去修改状态
            if receive_pay_inner_status == 5:
                # 修改托管渠道流水为交易成功
                OperationDbEscrowChannel().update_ebank_tran(tran_no)
                # 触发escrow-trade-job:支付补单，托管渠道收款流水内部状态为渠道受理成功
                elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("payRepairProducerJob")
                # dubbo().RepairTradeFacade_payRepair_dubbo(trade_flow_no)
            elif receive_pay_inner_status == 6:
                logging.info('托管渠道收款流水内部状态为"渠道受理成功",交易订单号 %s' % trade_no)
            else:
                raise RuntimeError('托管渠道收款流水内部状态异常,交易订单号 %s' % trade_no)
        else:
            raise RuntimeError('支付下单异常,交易订单号 %s' % trade_no)
        time.sleep(5)
        receive_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(receive_pay_flow_no)
        receive_pay_status = receive_pay_flow_list['pay_status']
        receive_pay_inner_status = receive_pay_flow_list['pay_inner_status']
        loop_count = 0
        # 判断托管交易收款流水状态是否为“支付成功”+内部状态是否为“渠道受理成功”
        while (receive_pay_status != 3 or receive_pay_inner_status != 6) and loop_count < 10:
            time.sleep(10)
            receive_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(receive_pay_flow_no)
            receive_pay_status = receive_pay_flow_list['pay_status']
            receive_pay_inner_status = receive_pay_flow_list['pay_inner_status']
            loop_count += 1
        if loop_count == 10:
            raise RuntimeError('更新托管交易收款流水内部状态异常,交易订单号 %s' % trade_no)
        return True

    def check_profit_pay_flow(self, trade_no, profit_pay_flow_no):
        # 查询托管交易分账流水
        profit_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
        profit_pay_inner_status = profit_pay_flow_list['pay_inner_status']
        pos_no = profit_pay_flow_list['pos_no']
        trade_flow_no = profit_pay_flow_list['trade_flow_no']
        # 判断托管交易分账流水内部状态是否为“渠道受理成功”（pay_inner_status=6）
        while profit_pay_inner_status != 6:
            # 内部状态为“渠道已受理”
            if profit_pay_inner_status == 5:
                # 查询托管渠道付款流水
                pay_tran_list = OperationDbEscrowChannel().query_pay_tran(pos_no)
                pay_tran_pay_status = pay_tran_list['pay_status']
                # 修改托管渠道付款流水为交易成功
                while pay_tran_pay_status != 1:
                    OperationDbEscrowChannel().update_pay_tran(pos_no)
                    pay_tran_list = OperationDbEscrowChannel().query_pay_tran(pos_no)
                    pay_tran_pay_status = pay_tran_list['pay_status']
            # 内部状态为“账户已出账”
            elif profit_pay_inner_status == 4:
                # 触发escrow-trade-job的付款补单任务
                elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("payRepairProducerJob")
                # dubbo().RepairTradeFacade_payRepair_dubbo(trade_flow_no)
                logging.info('内部状态为“账户已出账”')
                time.sleep(5)
                profit_pay_inner_status = \
                    OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)[
                        'pay_inner_status']
                loop_count = 0
                while profit_pay_inner_status != 5 and loop_count < 5:
                    time.sleep(5)
                    profit_pay_inner_status = \
                        OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)[
                            'pay_inner_status']
                    loop_count += 1
                if loop_count == 5:
                    raise RuntimeError('更新托管交易分账流水内部状态异常,交易订单号 %s' % trade_no)
                # 查询托管渠道付款流水
                pay_tran_list = OperationDbEscrowChannel().query_pay_tran(pos_no)
                pay_tran_pay_status = pay_tran_list['pay_status']
                # 修改托管渠道付款流水为交易成功
                while pay_tran_pay_status != 1:
                    OperationDbEscrowChannel().update_pay_tran(pos_no)
                    pay_tran_list = OperationDbEscrowChannel().query_pay_tran(pos_no)
                    pay_tran_pay_status = pay_tran_list['pay_status']
            # 内部状态为“正常”
            elif profit_pay_inner_status == 1:
                loop_count = 0
                while profit_pay_inner_status != 1 and loop_count < 5:
                    time.sleep(3)
                    profit_pay_inner_status = \
                        OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)[
                            'pay_inner_status']
                    loop_count += 1
                if loop_count == 5:
                    raise RuntimeError('中间账户没钱了！')
            else:
                raise RuntimeError('非法状态')
            # 触发escrow-trade-job的付款补单任务
            elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("payRepairProducerJob")
            # dubbo().RepairTradeFacade_payRepair_dubbo(trade_flow_no)
            time.sleep(5)
            profit_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
            profit_pay_inner_status = profit_pay_flow_list['pay_inner_status']
        return True
