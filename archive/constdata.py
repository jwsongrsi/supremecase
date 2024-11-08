import requests
import pprint
import json
import xmltodict
import math
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

### open.law.go.kr ###

        #행정규칙   유권해석      정보      공정       금융      방통    토지     권익      고용      환경       산재     자치법규
label = ['rule', 'interpret', 'private', 'trade', 'finance', 'cast', 'land', 'right', 'employ', 'nature', 'industy', 'ordin', 'supreme', 'constitution']

###################### 입력창 #####################
mydata = 'constitution' #가져오려는 api 데이터 (label 참조)
maxnum = 10000 #한 파일당 최대 개수 (100의 배수)

court = '헌법재판소'
###################################################

target_num = label.index(mydata)
targetlist = ['admrul', 'expc', 'ppc', 'ftc', 'fsc', 'kcc', 'oclt', 'acr', 'eiac', 'ecc', 'iaciac', 'ordin', 'prec', 'detc']
#totalCnts =  [ 19847,   7702,  1548,  7245,   552,   811,    23,    448,   118,    266,    934,     141659] #2023.12.13 기준 

firstDict_list = ['AdmRulSearch', 'Expc', 'Ppc', 'Ftc', 'Fsc', 'Kcc', 'Oclt', 'Acr', 'Eiac', 'Ecc', 'Iaciac', 'OrdinSearch', 'PrecSearch', 'DetcSearch']
firstDict_info = ['AdmRulService'] + [item + 'Service' for item in firstDict_list[1:11]] + ['LawService', 'PrecService', 'DetcService']

#데이터 총 개수
target = targetlist[target_num] 

url = 'https://www.law.go.kr/DRF/lawSearch.do'
params = {'OC': 'dev', 'target': target, 'type': 'XML', 'display': 1, 'page': 1, 'sort': 'dasc', 'curt': court}
headers = {'Host': 'www.law.go.kr', 'Referer': 'https://bigcase.ai/', 'Content-Type': 'application/json'}

response = requests.get(url, params=params, headers=headers)
xmlData = response.text
jsonStr = json.dumps(xmltodict.parse(xmlData), indent = 4)
jsontext = json.loads(jsonStr)

totalCnt = int(jsontext[firstDict_list[target_num]]['totalCnt'])
print(totalCnt)

#반복횟수 
loopCnt = math.floor(totalCnt/maxnum)+1

#함수 실행 

start_page = 1

for loop in tqdm(range(start_page, loopCnt+1)):

    Lists = [[] for _ in range(len(targetlist))]
    Serials = [[] for _ in range(len(targetlist))]
    Infos = [[] for _ in range(len(targetlist))]

    i = target_num

    def allLists ():
        target = targetlist[i] 
        pages = math.floor(totalCnt / 100) + 1

        if loopCnt > 1:
            first_page = (loop - 1)*(maxnum/100) + 1 

            if loop == loopCnt:
                last_page = pages
            else:
                last_page = first_page + (maxnum/100)-1

        else:
            first_page = 1
            last_page = pages 
        
        for k in tqdm(range(int(first_page), int(last_page) + 1)):
            
            url = 'https://www.law.go.kr/DRF/lawSearch.do'
            params = {'OC': 'dev', 'target': target, 'type': 'XML', 'display': 100, 'page': k, 'sort': 'dasc', 'curt': court}
            headers = {'Host': 'www.law.go.kr', 'Referer': 'https://bigcase.ai/', 'Content-Type': 'application/json'}

            response = requests.get(url, params=params, headers=headers)
            xmlData = response.text
            jsonStr = json.dumps(xmltodict.parse(xmlData), indent = 4)
            jsontext = json.loads(jsonStr)
            
            jsontext = jsontext[firstDict_list[i]]
            
            if target == 'ordin':
                scdict = 'law'   
            else:
                scdict = target
        
            jsontext = jsontext['Detc']
            
            Lists[i] = Lists[i] + jsontext

    def allSerials():
        target = targetlist[i] 
        for k in range(0, len(Lists[i])):
            
            if target == 'admrul':
                serialtext = '행정규칙일련번호'
            elif target == 'expc':
                serialtext = '법령해석례일련번호'
            elif target == 'ordin':
                serialtext = '자치법규ID'
            elif target == 'law':
                serialtext = '법령ID'
            elif target == 'prec':
                serialtext = '판례일련번호' #판례일련번호
            elif target == 'detc':
                serialtext = '헌재결정례일련번호'
            else:
                serialtext = '결정문일련번호'
                
            serial = Lists[i][k][serialtext]
            Serials[i].append(serial)
                
    def allInfos ():
        
        for k in tqdm(range(0, len(Serials[i]))): 
            
            url = 'https://www.law.go.kr/DRF/lawService.do'
            params = {'OC': 'dev', 'target': target, 'type': 'XML', 'ID': int(Serials[i][k])}
            headers = {'Host': 'www.law.go.kr', 'Referer': 'https://bigcase.ai/', 'Content-Type': 'application/json'}

            response = requests.get(url, params=params, headers=headers)
            xmlData = response.text
            jsonStr = json.dumps(xmltodict.parse(xmlData), indent = 4)
            jsontext = json.loads(jsonStr)

            jsontext = jsontext[firstDict_info[i]]

            jsontext_final = {
                'ID': 0,
                '사건번호': jsontext['사건번호'],
                '종국일자': jsontext['종국일자'], 
                '판시사항': jsontext['판시사항'],
                '결정요지': jsontext['결정요지']
            }
            
            #print(jsontext_final)
            Infos[i] = Infos[i] + [jsontext_final]

    allLists()        
    allSerials()
    allInfos()
    
    def jsonize():
        path = 'C:/Users/sdsdf/supreme_infos/'
       # with open(path + mydata + '_list%d.json' %loop, "w", encoding='utf-8') as json_file: 
        #    json.dump(Lists[target_num], json_file, ensure_ascii=False, indent=4)
            
        with open(path + mydata + '_info%d.json' %loop, "w", encoding='utf-8') as json_file:
            json.dump(Infos[target_num], json_file, ensure_ascii=False, indent=4)
            
    jsonize()
