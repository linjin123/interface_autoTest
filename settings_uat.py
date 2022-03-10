#配置URL信息
#[URL]
in_url = "https://in.mideaepayuat.com"
cashier_url = "https://cashier.mideaepayuat.com"
callback_url = "https://callback.mideaepayuat.com"
mch_url =  "https://mch.mideaepayuat.com"
m_url =  "https://m.mideaepayuat.com"
notify_url =  "https://notify.mideaepayuat.com"
wallet_url =  "https://wallet.mideaepayuat.com"
www_url =  "https://www.mideaepayuat.com"
sign_url = "https://sign.mideaepayuat.com/rsa/getSign.htm"
base_url = "https://sign.mideaepayuat.com"
elasticjob_url="https://elasticjob.mideaepayuat.com"


# url=test_url()
#商户接入url
# partnerin_url = url.in_url
#PC收银台url
# cashier_url = url.cashier_url
#个人端url
# personal_url = url.www_url
#H5钱包url
# mobile_url = url.m_url
# elasticjob_url=url.elasticjob_url
#接口

#===============B2C交易查询接口=================================
B2C_trade_query_url = in_url + '/trade/b2cTradeQuery.htm'

#===============B2C交易==========================================
#B2C交易接入收银台接口(H5、PC收银台)
B2C_trade_url = in_url + '/gateway.htm'
#获取si、pwdkey、salt地址（PC收银台）
GetPayPwdKey_url = cashier_url + '/getSaltOfPayPwd.json'
#获取密码地址，需要替换personal-web下personal-control-3.2.3.jar（PC收银台）
Get_genPwd_url = www_url + '/security/common/genPwd.htm'
#支付地址（PC收银台）
Pay_url = cashier_url + '/directPay.json'
Pay_ebank_url = cashier_url + '/eBank.json'
#注销（PC收银台）
Logout_url =cashier_url +  '/logout.htm'
#获取paykey地址(H5收银台)
Get_PayPwdKey_H5_url = m_url + '/common/getPayPwdKey.htm'
#支付地址（H5收银台）
Pay_H5_url = m_url + '/mallPay/payAll.htm'


#===================B2C交易退款=====================================
#B2C_refund_url= partnerin_url + '/trade/b2cRefund.htm'
B2C_refund_url=in_url + '/gateway.htm'
#===================B2C交易退款查单=====================================
B2C_refund_query_url= in_url + '/trade/b2cRefundQuery.htm'

#测试个人用户(登录名、密码、user_id)
test_user_1= {'login_name':'18780030001','password':'112233','user_id':'900260007'}
#测试商户(商户号、平台号)
test_partner_1 = {'partner':'1000011005','plat_id':'1'}

#助贷支付地址
zhudai='http://m.mideaepayuat.com/getThirdCreditQuota.htm'


#DB数据库配置信息
# [DB]
host = "10.16.157.93"
port = "3306"
user = "u_test_prd"
passwd = "Mysql@Test*2018$"
db = "db"
charset = "utf8"


# [SIT]

