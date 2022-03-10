#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : read_data.py 
# @Author: xiangling
# @Date : 2018-10-8 
# @Desc : 读取yml文件数据，参数1：yml存放路径
import os
import yaml


class OperationYaml:
    def getData(yamlPath):
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        root_path = os.path.abspath(os.path.join(BASE_DIR, "../"))
        # print(BASE_DIR)
        # print(root_path)
        yamlpath = os.path.join(root_path + yamlPath)
        # open方法打开直接读出来
        f = open(yamlpath, 'r', encoding='UTF-8')
        cfg = f.read()
        d = yaml.load(cfg, Loader=yaml.FullLoader)  # 用load方法转字典

        array = []  # 每条案例对应的测试数据信息
        desc = []  # 每条案例对应的描述信息

        for i in range(0, len(d)):
            for value in d[i].values():
                childarray = []
                childarray.append(value['send_data'])
                childarray.append(value['except'])
                desc.append(value['desc'])
                array.append(tuple(childarray))

        return array, desc

    def getData_payData(yamlPath):
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        root_path = os.path.abspath(os.path.join(BASE_DIR, "../"))
        # print(BASE_DIR)
        # print(root_path)
        yamlpath = os.path.join(root_path + yamlPath)
        # open方法打开直接读出来
        f = open(yamlpath, 'r', encoding='UTF-8')
        cfg = f.read()
        d = yaml.load(cfg, Loader=yaml.FullLoader)  # 用load方法转字典

        array = []  # 每条案例对应的测试数据信息
        desc = []  # 每条案例对应的描述信息

        for i in range(0, len(d)):
            for value in d[i].values():
                childarray = []
                childarray.append(value['send_data'])
                childarray.append(value['pay_data'])
                childarray.append(value['except'])
                desc.append(value['desc'])
                array.append(tuple(childarray))

        return array, desc
