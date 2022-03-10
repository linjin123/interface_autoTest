import sys
import pytest
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from common.logger import logger

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from common.shell import Shell
import os,sys

# 指定测试用例为当前文件夹下的 test_case 目录
test_dir = 'test_case'

if __name__ == "__main__":

    shell = Shell()  # 构建一个cmd运行

    xml_report_path = "--junitxml=./reports/report.xml"
    html_report_path = "--html=./reports/report.html"
    allure_report = "--alluredir=allure-results"

    args = ['-sv', test_dir, allure_report, xml_report_path, html_report_path]

    self_args = sys.argv[1:]

    # pytest.main(args)
    #
    for i in range(1):
    # #执行命令执行测试用例
        os.system(
    #         # "pytest test_case/01_test_B2C_trade/test_111014_quick_pay.py::test_b2cTrade_PC_pay --settings=settings_uat")
    #         "pytest test_case/04_test_V3_Wechat_data/test_111232_wechat_mini_program_single.py::test_pay --settings=settings_uat")
    # "pytest test_case/04_test_V3_Wechat_data/test_111231_wechat_mini_program_single.py::test_pay --settings=settings_uat"
    "pytest test_case/wechatAndAlipaySecretFreeWhithhold/test_trade_wechatpay_withhold_check.py::test_alipay_app_single_immediately_pay_success --settings=settings_uat" )

    #     )

    # cmd = 'allure generate %s -o %s --clean' % ("allure-results", "allure-report")
    #
    # try:
    #     shell.invoke(cmd)
    # except Exception:
    #     logger.error('执行用例失败，请检查环境配置')


    # os.system(
    #     "pytest test_case/test_pay_system_trade_refund.py::test_trade_refund --settings=settings_uat")
