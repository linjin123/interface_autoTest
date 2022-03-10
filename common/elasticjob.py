import json

import requests
import datetime
from common.logger import logger


# 定时任务平台
class elasticjob:
    def __init__(self, url, systemJob):
        self.url = url
        self.systemJob = systemJob
        send_data = {}
        send_data["name"] = systemJob
        headers = {'content-type': "application/json"}
        connetUrl = self.url["elasticjob_url"] + "/api/registry-center/connect"
        r = requests.post(connetUrl, data=json.dumps(send_data), headers=headers, verify=False)
        print(r)

    def jobTrigger(self, method):
        jobUrl = self.url["elasticjob_url"] + "/api/jobs/%s/trigger" % (method)
        r = requests.post(jobUrl, verify=False)
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("method : %s, time: %s" % (method, time))


if __name__ == '__main__':
    url = {"elasticjob_url": "http://10.16.157.96:20814"}
    # method = "ReverseAccountingJob"
    # system = "escrow-channe-task-schedule-job"
    # elasticjob = elasticjob(url, system)
    # elasticjob.jobTrigger(method)
    method = "refundQueryRepairProducerJob"
    system = "escrow-trade-job"
    elasticjob = elasticjob(url, system)
    elasticjob.jobTrigger(method)
