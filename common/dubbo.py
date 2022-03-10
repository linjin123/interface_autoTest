import requests
from collections import OrderedDict

class dubbo(object):

    def __init__(self,facade=None,method=None,types=None,values=None):
        self.url = "http://10.16.155.85:8090/demo/rpc.htm"
        self.facade=facade
        self.method=method
        self.types=types
        self.values=values

    def dubbo_interface(self):
        # url="http://10.16.155.85:8090/demo/rpc.htm"
        data = OrderedDict()
        data["facade"]=self.facade
        data["method"] = self.method
        data["types"] = self.types
        data["values"] = self.values

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result


    #付款出账&渠道下单补单
    def RepairTradeFacade_payRepair_dubbo(self,tradeFlowNo):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.trade.facade.RepairTradeFacade'
        data["method"] = 'payRepair'
        data["types"] = '["java.lang.String"]'
        data["values"] = tradeFlowNo
        r = requests.post(self.url, data, verify=False)
        result = r.json()
        return result

    #交易流水补单
    def RepairTradeFacade_repairTradeFlow_dubbo(self,req):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.trade.facade.RepairTradeFacade'
        data["method"] = 'repairTradeFlow'
        data["types"] = '["com.mideaepay.escrow.trade.model.req.RepairTradeFlowReq"]'
        data["values"] = req

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result

    #网银对账单状态同步方法
    def RepairTradeFacade_arriveRepairForOnlinePay_dubbo(self,tradeFlowNo):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.trade.facade.RepairTradeFacade'
        data["method"] = 'arriveRepairForOnlinePay'
        data["types"] = '["java.lang.String"]'
        data["values"] = tradeFlowNo

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result

    #退款补单
    def RepairTradeFacade_refundRepair_dubbo(self,tradeFlowNo):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.trade.facade.RepairTradeFacade'
        data["method"] = 'refundRepair'
        data["types"] = '["java.lang.String"]'
        data["values"] = tradeFlowNo

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result

    # 银企预支付成功
    def RepairTradeFacade_bankEnterprisePreSuccessRepair_dubbo(self, tradeNo):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.trade.facade.RepairTradeFacade'
        data["method"] = 'bankEnterprisePreSuccessRepair'
        data["types"] = '["java.lang.String"]'
        data["values"] = tradeNo

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result

    #调用托管交易系统入账
    def cashReceiveFacade_receiveCash(self,values):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.trade.facade.CashReceiveFacade'
        data["method"] = 'receiveCash'
        data["types"] = '["com.mideaepay.escrow.trade.model.req.CashReceiveReq"]'
        data["values"] = values

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result

    # 修改托管收款流水状态为成功
    def ChannelCoreReverseTranFacade_modifyTranToSuccess(self,values):
        data = OrderedDict()
        data["facade"] = 'com.mideaepay.escrow.channel.core.facade.ChannelCoreReverseTranFacade'
        data["method"] = 'modifyTranToSuccess'
        data["types"] = ' ["com.mideaepay.escrow.channel.core.model.ChannelCoreReverseTran"]'
        data["values"] = values

        r = requests.post(self.url, data, verify=False)
        result = r.json()
        print(result)
        return result





if __name__=="__main__":

    #values = '[{"payeeBankAct":"01ac29b4a2b56f9a7d5c687b47501615546400443193713d3bf4c6df69bf9782","summary":"收款伴侣","tradeNo":"1094202112100000000206","channelProdName":"工行托管账户","sign":"497E2D1CA62FC619CA79B9B4BB96F25A","payerBankName":"","tranNo":"107612101001202112100000000707","payeeName":"团购一号","payeeBankName":"","payAmount":3,"payerName":"林振武","channelName":"工行托管账户","payerBankAct":"d7309f31abc568fdf61deb351ad024a07a57a5ce20769544f797e36bb9a1e294","receiveType":1,"channelId":10100101,"channelProdId":101001}]'

    #dubbo().cashReceiveFacade_receiveCash(values)
    values='[{"payeeBankAct":null,"curType":null,"payeeBankCode":null,"remark":null,"payerBankCode":null,"modifyTime":null,"channelTranNo":null,"payerBankAct":null,"paymentTime":"2021-12-10 18:00:00","receiveType":null,"channelId":null,"channelProdId":null,"amount":null,"channelProdName":null,"innerRemark":null,"payerBankName":null,"tranNo":"107612101001202112100000000206","bankAttach":null,"channelPaymentTime":null,"payeeBankName":null,"tradeFlowNo":"1094202112100000000194-100-01","createTime":null,"payeeRealName":null,"channelName":null,"payStatus":null,"payerRealName":null}]'
    dubbo().ChannelCoreReverseTranFacade_modifyTranToSuccess(values)

