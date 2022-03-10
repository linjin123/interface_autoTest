# @Author: linxy57
# @Time: 2021/12/9 10:18
# @Desc: 公用枚举

from enum import Enum


class CommonEnum(object):
    # 托管账户类型
    # 适用范围：db_escrow_act.t_act(act_type)
    class EscrowActType(Enum):
        PRIMARY = 20  # 主账户
        TRADE = 21  # 交易户
        PRIVATE = 22  # 托管-对私-现金户

    # 支付状态
    # 适用范围：db_order.t_trade(pay_status)
    class PayStatusEnum(Enum):
        WAITING_PAY = 1  # 未支付
        PAYING = 2  # 支付中
        SUCCESS = 3  # 支付成功
        FAIL = 4  # 支付失败
        EXCEPTION = 5  # 异常
        PRE_PAY_SUCCESS = 6  # 预支付成功

    # 支付单内部状态
    # 适用范围：db_escrow_trade.t_trade(pay_inner_status)
    class PayInnerStatusEnum(Enum):
        NORMAL = 1  # 正常
        CANCEL = 2  # 作废
        REEXCHANGE = 3  # 退汇
        MAYBE_REPEAT_RECEIVE = 4  # 疑似重复收款
        CASH_ARRIVED = 5  # 资金已到账

    # 到账状态
    # 适用范围：db_order.t_trade(arrival_status)、db_order.t_refund(arrival_status)
    class ArrivalStatusEnum(Enum):
        WAIT_PAY = 1  # 未支付
        PROCESSING = 2  # 到账中
        RECEIVED = 3  # 已到账

    # 订单状态
    # 适用范围：db_order.t_refund(refund_status)
    class OrderStatusEnum(Enum):
        WAITING_PAY = 1  # 待支付
        PAYING = 2  # 支付中
        SUCCESS = 3  # 支付成功
        FAIL = 4  # 支付失败
        EXCEPTION = 5  # 支付异常
        REFUNDING = 6  # 退款中
        REFUND_SUCCESS = 7  # 退款成功
        TRADE_OVER = 8  # 交易完成
        CLOSE = 9  # 关闭

    # 内部到账状态
    # 适用范围：db_order.t_refund(inner_arrival_status)
    class InnerArrivalStatusEnum(Enum):
        WAIT_PAY = 1  # 未出款
        PAYMENT_SUCCESS = 2  # 支付系统出款成功
        ESCROW_RECEIVED = 3  # 托管系统出款成功
        ALL_RECEIVED = 99  # 出款完成


    # 交易流水内部状态
    # 适用范围：db_escrow_trade.t_trade_flow(pay_inner_status)
    class TradeFlowInnerStatusEnum(Enum):
        NORMAL = 1  # 正常
        CANCEL = 2  # 作废
        REEXCHANGE = 3  # 退汇
        ACCOUNT_REDUCED = 4  # 账户已出账
        CHANNEL_ACCEPTED = 5  # 渠道已受理
        CHANNEL_SUCCESS = 6  # 渠道受理成功
        CHANNEL_FAIL = 7  # 渠道受理失败
        CASH_ARRIVED = 8  # 资金已到账
        WAITING_PLACE_GATEWAY_ORDER = 9  # 待下网关单

    # 交易单类型
    # 适用范围：db_escrow_act.t_act_history(trade_type)
    class TradeTypeEnum(Enum):
        CASH_RECEIVE = 1  # 线下收款
        DISTRIBUTE = 2  # 普通付款
        SAL_DISTRIBUTE = 3  # 工资付款
        TRANSFER_IN = 4  # 转入交易
        TRANSFER_OUT = 5  # 转出交易
        REFUND = 6  # 退汇
        MANUAL = 7  # 人工调账
        SETTLE = 8  # 结算
        PAY_TRADE = 9  # 支付
        REFUND_TRADE = 10  # 退款
        ALLOCATE_TRADE = 11  # 调拨
        REPEAT_PAY_REFUND_TRADE = 12  # 重复支付退款
        MANUAL_ADJUST = 13  # 人工调拨
        SETTLE_TOTAL_FEE = 14  # 结算汇总手续费
        CASH_REDUCE = 15  # 扣款交易
        REMIT_ATTESTATION = 16  # 打款认证
        INNER_REFUND = 17  # 内部退款

    # 交易流水类型
    # 适用范围：db_escrow_act.t_act_history(trade_flow_type)
    class TradeFlowTypeEnum(Enum):
        RECEIVE = 1  # 收款
        PAY = 2  # 付款
        REEXCHANGE = 3  # 退汇
        REFUND = 4  # 退款
        ONLINE_PAY = 5  # 网银付款
        PROFIT = 6  # 分账
        ONLINE_REFUND = 7  # 网银退款
        QUICK_PAY = 8  # 快捷付款
        QUICK_REFUND = 9  # 快捷退款
        BANK_ENTERPRISE_PAY = 10  # 银企支付
        BANK_ENTERPRISE_REFUND = 11  # 银企退款
        FREEZE_TRADE = 12  # 交易金额冻结
        UNFREEZE_TRADE = 13  # 交易金额解冻
        CREDIT_PAY = 14  # 信贷支付
        CREDIT_REFUND = 15  # 信贷退款
        E_CNY_EBANK_PAY = 16  # 数字人民币网银支付
        E_CNY_EBANK_REFUND = 17  # 数字人民币网银退款
        E_CNY_QUICK_PAY = 18  # 数字人民币快捷支付
        E_CNY_QUICK_REFUND = 19  # 数字人民币快捷退款

    # 账务流水类型
    # 适用范围：
    class DcTypeEnum(Enum):
        ADD = 1  # 加款
        SUB = 2  # 减款

    # 收款类型枚举
    # 适用范围：
    class ReceiveTypeEnum(Enum):
        RECEIVE = 1  # 收款
        REVERSE = 2  # 冲正
        REFUND_TRADE = 3  # 退款
        REPEAT_PAY_REFUND_TRADE = 4  # 重复支付退款
        INNER_REFUND_TRADE = 5  # 内部退款

    # 关联订单类型
    # 适用范围：db_escrow_trade.t_trade(rele_order_type)
    class ReleOrderTypeEnum(Enum):
        ReleOrderType = 1  # B2C交易
        REFUND_ORDER = 5  # 退款
        REPEAT_PAY_REFUND = 15  # 重复支付退款
        BATCH_B2C_TRADE_ORDER = 42  # 合单支付
        B2C_GUARANTEE_TRADE_ORDER = 49  # B2C担保交易
        B2C_GUARANTEE_MERGE_TRADE_ORDER = 50  # B2C担保合并交易


    # 内转到账状态
    # 适用范围：db_partner_notify.t_out_notify(content（arrival_status）)
    class NotifyArrivalStatus(Enum):
        WAIT_PAY = 1  # 未支付
        PAYMENT_PROCESSING =2  # 到账中
        PAYMENT_RECEIVED =3  # 已到账

    # 通知状态
    # 适用范围：db_partner_notify.t_out_notify(notify_status)
    class NotifyStatus(Enum):
        INIT = 0  # 初始态
        SUCCESS = 1  # 通知成功

