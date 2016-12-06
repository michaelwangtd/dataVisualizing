# -*- encoding:utf-8 -*-

from SimilarCompanies627 import loadData
from collections import OrderedDict
import numpy as np
import json


def getProductCompanyList(filePath):
    productCompanyList = []
    fr = open(filePath,'r',encoding='utf-8')
    while True:
        line = fr.readline().strip()
        if line:
            productCompanyList.append(line)
        else:
            break
    return productCompanyList


def createProductCompanyDict(companyList,resourceFilePath):
    # 初始化产品公司字典
    productCompanyDic = {}
    for item in companyList:
        productCompanyDic[item] = []
    # 信息归类
    jsonList = loadData.loadData(resourceFilePath)
    for i in range(len(jsonList)):
        if jsonList[i]['startup']['name']:
            if jsonList[i]['startup']['name'] in productCompanyDic.keys():
                # 这里增加对vcName判断的逻辑
                if jsonList[i]['vc']['name']:
                    if jsonList[i]['event']['investRound'] and jsonList[i]['event']['investRound'] not in ['未透露','未知','不明确']:
                        productCompanyDic[jsonList[i]['startup']['name']].append(jsonList[i])
    return productCompanyDic


def getInvestTimeDict(recordList):
    # 初始化投资时间字典
    investTimeDic = {}
    for i in range(len(recordList)):
        if recordList[i]['event']['investTime']:
            investTime = recordList[i]['event']['investTime'].replace('.','')
            if investTime not in investTimeDic.keys():
                investTimeDic[investTime] = []
            if investTime in investTimeDic.keys():
                investTimeDic[investTime].append(recordList[i])
    return investTimeDic


def getInvestRoundDic(recordList,roundDic):
    for i in range(len(recordList)):
        if recordList[i]['event']['investRound'] and recordList[i]['event']['investRound'] not in ['不明确']:
            # if recordList[i]['event']['investRound'] in roundDic.keys():
            #     roundDic[recordList[i]['event']['investRound']].appen(recordList[i])
            if recordList[i]['event']['investRound'] in ['种子轮']:
                roundDic['种子轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['天使轮']:
                roundDic['天使轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['Pre-A轮','A轮','A+轮', '新三板']:
                roundDic['A轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['Pre-B轮','B轮','B+轮']:
                roundDic['B轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['C轮','战略投资','并购']:
                roundDic['C轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['D轮']:
                roundDic['D轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['E轮']:
                roundDic['E轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['F轮','F轮-上市前']:
                roundDic['F轮'].append(recordList[i])
            if recordList[i]['event']['investRound'] in ['IPO上市','IPO上市后']:
                roundDic['IPO轮'].append(recordList[i])
    return roundDic


def getOrderedInvestTimeDic(investTimeDic):
    # 初始化有序字典
    orderedInvestTimeDic = OrderedDict()
    for key in sorted(investTimeDic.keys(),reverse = True):
        orderedInvestTimeDic[key] = []
        # 遍历对应时间值的列表
        for item in investTimeDic[key]:
            if item['vc']['name']:
                vcName = item['vc']['name']
            # else:
            #     vcName = '未知'
                orderedInvestTimeDic[key].append(vcName)
    return orderedInvestTimeDic


def getRelationList(orderedList):
    relationList = []
    for i in range(len(orderedList) - 1):
        for j in range(len(orderedList[i])):
            for k in range(len(orderedList[i + 1])):
                relationList.append((orderedList[i][j], orderedList[i + 1][k]))
    return relationList


def getVcCompanyEdgeList(orderedVcDic):
    # 将有序字典转变为有序列表
    orderedVcList = []
    for key,value in orderedVcDic.items():
        orderedVcList.append(value)
    # print(len(orderedInvestTimeList),orderedInvestTimeList)
    # 套用循环实现图中“边”关系
    if orderedVcList:
        relationList = getRelationList(orderedVcList)
        return relationList


def ouput2Csv(vcCompanyEdgeList):
    outputFilePath = 'D:\\workstation\\zhizhugraph\\resultset' + '\\' + 'vcEdge_sankey.csv'
    fw = open(outputFilePath,'w',encoding='utf-8')
    fw.write('vcCompany1,vcCompany2' + '\n')
    for item in vcCompanyEdgeList:
        outputLine = item[0] + ',' + item[1]
        fw.write(outputLine + '\n')
    fw.close()


def initRoundDic():
    roundDic = OrderedDict()
    keyList = ['种子轮','天使轮','A轮','B轮','C轮','D轮','E轮','F轮','IPO轮']
    for item in keyList:
        roundDic[item] = []
    return roundDic


def getVcInfoDic(investRoundDic):
    vcInfoDic = OrderedDict()
    for key,value in investRoundDic.items():
        if value:
            vcInfoDic[key] = []
            for item in value:
                if item['vc']['name'] :
                    vcName = key + '|' + item['vc']['name'].replace('\xa0',' ')
                    vcInfoDic[key].append(vcName)
    return vcInfoDic


def getNodeDic(vcCompanyEdgeList):
    nodeDic = {}
    # 定义“左”，“右”两个列表
    leftList = []
    rightList = []
    # 将vcCompanyEdgeList中的vc公司存储到对应列表中
    for item in vcCompanyEdgeList:
        leftList.append(item[0])
        rightList.append(item[1])
    # 获取“点”的种类
    allNodeList = list(set(leftList + rightList))
    for node in allNodeList:
        nodeValue = leftList.count(node) > rightList.count(node) and leftList.count(node) or rightList.count(node)
        name = node
        type = node.split('|')[0]
        nodeDic[node] = [name,type,nodeValue]
    return nodeDic


def getEdgeDic(vcCompanyEdgeList):
    edgeDic = {}
    setVcCompanyEdgeList = list(set(vcCompanyEdgeList))
    for item in setVcCompanyEdgeList:
        source = item[1]
        target = item[0]
        value = vcCompanyEdgeList.count(item)
        key = target + '_' + source
        edgeDic[key] = [source, target, value]
    return edgeDic


def initNodeDic():
    dic = {}
    dic['name'] = ''
    dic['type'] = ''
    dic['value'] = ''
    dic['itemStyle'] = {}
    dic['itemStyle']['normal'] = {}
    dic['itemStyle']['normal']['color'] = '#D40404'
    dic['label'] = {}
    dic['label']['normal'] = {}
    dic['label']['normal']['position'] = 'right'
    return dic


def initEdgeDic():
    dic = {}
    dic['source'] = ''
    dic['target'] = ''
    dic['value'] = ''
    dic['lineStyle'] = {}
    dic['lineStyle']['normal'] = {}
    dic['lineStyle']['normal']['color'] = None
    dic['lineStyle']['normal']['opacity'] = 0.05
    return dic


def getNodeJsonList(nodeDic):
    nodeJsonList = []
    for key,value in nodeDic.items():
        # 初始化node字典
        initNode = initNodeDic()
        initNode['name'] = value[0]
        initNode['type'] = value[1]
        initNode['value'] = value[2]
        # 将字典转化成json格式
        jsonNode = json.dumps(initNode,ensure_ascii=False)
        nodeJsonList.append(jsonNode)
    return nodeJsonList


def getEdgeJsonList(edgeDic):
    edgeJsonList = []
    for key,value in edgeDic.items():
        initEdge = initEdgeDic()
        initEdge['source'] = value[0]
        initEdge['target'] = value[1]
        initEdge['value'] = value[2]
        jsonEdge = json.dumps(initEdge,ensure_ascii=False)
        edgeJsonList.append(jsonEdge)
    return edgeJsonList




if __name__ == '__main__':

    vcCompanyEdgeList = []
    # 获取产品公司列表
    productCompanyList = getProductCompanyList('company_name_list.txt')
    # 【筛选】相关记录信息，存储到字典并返回
    productCompanyDic = createProductCompanyDict(productCompanyList,'investEvents_20161019121629.txt')
    # 遍历字典
    i = 1
    for key,value in productCompanyDic.items():
        # 初始化轮次字典
        roundDic = initRoundDic()
        # 针对某一公司的记录，按照轮次归类
        investRoundDic = getInvestRoundDic(value,roundDic)
        # 获取vc信息字段列表
        vcInfoDic = getVcInfoDic(investRoundDic)
        # 输出关于产品的vc字典列表
        # if len(vcInfoDic) != 1:
        print(i,key,'[',len(vcInfoDic),']',str(vcInfoDic))
        # 获取vc公司“边”列表
        companyEdgeList = getVcCompanyEdgeList(vcInfoDic)
        if companyEdgeList:
            print(i,'边列表长度:',len(companyEdgeList),str(companyEdgeList))
            vcCompanyEdgeList.extend(companyEdgeList)
        i += 1

    # # 将vc公司“边”列表输出
    # # 这样的输出效果不理想，要对vc“边”的关系进一步进行处理
    # ouput2Csv(vcCompanyEdgeList)    # 默认输出路径还是resultSet

    print(len(vcCompanyEdgeList),vcCompanyEdgeList)
    print('开始生成“点”，“边”文件:')
    # 获取“点”字典
    nodeDic = getNodeDic(vcCompanyEdgeList)

    # 获取“边”字典
    edgeDic = getEdgeDic(vcCompanyEdgeList)
    print(len(nodeDic))
    print(len(edgeDic))

    # 数据组装成json格式
    nodeJsonList = getNodeJsonList(nodeDic)
    edgeJsonList = getEdgeJsonList(edgeDic)
    # 这里为了方便可以直接输出出来
    print(nodeJsonList)
    print(edgeJsonList)

    data = ''
    for item in nodeJsonList:
        data = data + item + ','
    print('data',data)

    links = ''
    for item in edgeJsonList:
        links = links + item + ','
    print('links',links)






