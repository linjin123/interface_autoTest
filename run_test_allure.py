import os,sys
import unittest
import pytest
import requests
from common.logger import logger

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from common.shell import Shell


# 指定测试用例为当前文件夹下的 interface 目录

#test_dir = 'interface'
#test_dir = 'test_case/test_01002_B2C_Trade_Query.py'
#discover = unittest.defaultTestLoader.discover(test_dir, pattern='test_*.py')


if __name__ == "__main__":

    shell = Shell() # 构建一个cmd运行

    xml_report_path = "--junitxml=./reports/report.xml"

    html_report_path = "--html=./reports/report.html"

    allure_report = "--alluredir=allure-results"

    # 定义测试集
    #allure_list = '--allure_features=01_B2C交易'

    # args = ['-s', '-v','-m=pay','test_case/04_test_V3_Wechat_data/',xml_report_path,html_report_path,allure_report]
    #
    #
    # self_args = sys.argv[1:]
    # pytest.main(args)

    # pytest.main(["-m","B2C_refund",html_report_path])  #执行mark标记的测试用例

    #pytest.main(['-s', '-v','test_case/01_test_B2C_trade/test_01005_B2C_Trade_H5_Balance.py'])

    os.system("pytest -s -v test_case/ --junitxml=./reports/report.xml "
              " --html=./reports/report.html --alluredir=allure-results --clean-alluredir --settings=settings_uat")

    cmd = 'allure generate %s -o %s --clean' % ("allure-results", "allure-report")

    try:
        shell.invoke(cmd)
    except Exception:
        logger.error('执行用例失败，请检查环境配置')


