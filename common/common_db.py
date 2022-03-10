#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : common_db.py
# @Author: xiangling
# @Date : 2018-9-10 
# @Desc :
import pymysql
import json

from pymysql import OperationalError

from common.config import Config
config = Config()
from common.logger import logger

class OperationMysql:
        #连接数据库
        def __init__(self,db):
            self.db = db
            # DB = "DB"
            # self.conn = pymysql.connect(
            #         host = config.getConfigData(DB,'host'),
            #         port = int(config.getConfigData(DB,'port')),
            #         user = config.getConfigData(DB,'user'),
            #         passwd = config.getConfigData(DB,'passwd'),
            #         charset = config.getConfigData(DB,'charset'),
            #         db = db,
            #         autocommit=True,
            #         cursorclass = pymysql.cursors.DictCursor,
            #     )
            # self.cur = self.conn.cursor()
        def connect_db(self):
            DB = "DB"
            self.conn = pymysql.connect(
                host=config.getConfigData(DB, 'host'),
                port=int(config.getConfigData(DB, 'port')),
                user=config.getConfigData(DB, 'user'),
                passwd=config.getConfigData(DB, 'passwd'),
                charset=config.getConfigData(DB, 'charset'),
                db=self.db,
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor,
            )
            self.cur = self.conn.cursor()

        # def __del__(self):
        #     self.cur.close()
        #     self.conn.close()
            #print("common db del.....")

        def _reCon(self):
            """
            @Author:xiongyc9
            Functions:
                在对数据进行操作前，判断是否连接了数据库
            """

            while True:
                try:
                    self.conn.ping()
                    break
                except (OperationMysql, OperationalError) as err:
                    self.conn.ping(True)
                    logger.error(err)

        # 查询数据
        def query(self, sql):

            try:
                self.connect_db()
                self.cur.execute(sql)
                #result = self.cur.fetchone()
                result = self.cur.fetchall()
                #result = json.dumps(result)
                self.conn.commit()
                return result
            except:
                print("查询失败")
            finally:
                self.cur.close()
                self.conn.close()

        #更新或者删除数据
        def update(self,sql):

            try:
                self.connect_db()
                self.cur.execute(sql)
                self.conn.commit()
            except:
                self.conn.rollback()
                print("更新失败")
            finally:
                self.cur.close()
                self.conn.close()



if __name__ == '__main__':
    # op_mysql = OperationMysql("db_order")
    # res = op_mysql.query("select trade_no,out_trade_no,partner from t_trade where partner = '1000011005' limit 3")
    # print(res.__getitem__(1))
    # res=OperationMysql("db_order").query('SELECT trade_no FROM db_order.t_trade where out_trade_no="202110221719441"')
    # trade_no=res[0]["trade_no"]
    # print(res[0]["trade_no"])
    # db_escrow_channel=OperationMysql("db_escrow_channel")
    # OperationMysql("db_escrow_channel").update('UPDATE db_escrow_channel.t_credit_pay_tran SET pay_status=1 WHERE trade_no="%s"'%trade_no)
    pay_total_no = '1021202111210000001278'
    act_history_sql = 'select user_id,act_type,tran_amount,dc_type,user_remark,trade_msg from t_act_history where pay_no = "%s"' % pay_total_no
    db_act = OperationMysql("db_act")
    act_history = db_act.query(act_history_sql)
    print(len(act_history))

