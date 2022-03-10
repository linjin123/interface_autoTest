#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: linxy57
# @Date : 2021-12-07
# @Desc :db_escrow_act数据库操作


from common.common_db import OperationMysql


class OperationDbEscrowAct(object):
    '''
        operation of db_escrow_act
    '''

    def __init__(self):
        self._mysql = OperationMysql("db_escrow_act")

    # 根据商户号及交易类型查询账户号
    def query_act_by_partner_and_act_type(self, partner, act_type):
        sql = 'SELECT * FROM db_escrow_act.`t_act` WHERE user_id="%s" AND act_type = "%s"' % (partner, act_type)
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None

    # 根据托管交易流水号查询账务流水
    def query_act_history_by_trade_flow_no(self, trade_flow_no):
        sql = 'SELECT * FROM db_escrow_act.t_act_history WHERE trade_flow_no = "%s"' % trade_flow_no
        res = self._mysql.query(sql)
        if res:
            return res[0]
        else:
            return None
