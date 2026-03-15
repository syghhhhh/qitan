import requests
import time
import hashlib
import json
from dotenv import load_dotenv
import os

# 加载.env文件（默认查找当前目录）
load_dotenv()

#  请求参数
appKey = os.getenv("QICHACHA_KEY")
secretKey = os.getenv("QICHACHA_SECRETKEY")
encode = 'utf-8'

def get_headers():
    # Http请求头设置
    timespan = str(int(time.time()))
    token = appKey + timespan + secretKey
    hl = hashlib.md5()
    hl.update(token.encode(encoding=encode))
    token = hl.hexdigest().upper()
    print('MD5加密后为 ：' + token)
    return {'Token': token,'Timespan':timespan}


def base_request():
    #设置请求Url-请自行设置Url
    reqInterNme = "http://api.qichacha.com/XXXXXX"
    paramStr = "keyword=企查查科技有限公司"
    url = reqInterNme + "?key=" + appKey + "&" + paramStr
    headers = get_headers()
    response = requests.get(url, headers=headers)

    #结果返回处理
    print(response.status_code)
    resultJson = json.dumps(str(response.content, encoding = encode))
    # convert unicode to chinese
    resultJson = resultJson.encode(encode).decode("unicode-escape")
    print(resultJson)


def fuzzy_search(searchKey, save_json_path=None):
    """
    接口: 企业模糊搜索, 地址： https://api.qichacha.com/FuzzySearch/GetList
    本地文档: api_qichacha\document\fuzzy_search.md
    传入参数: 搜索关键词（支持企业名、人名、产品名、地址、电话、经营范围等）
    """
    start_time = time.time()
    reqInterNme = "https://api.qichacha.com/FuzzySearch/GetList"
    paramStr = f"searchKey={searchKey}"
    url = reqInterNme + "?key=" + appKey + "&" + paramStr
    headers = get_headers()
    response = requests.get(url, headers=headers)

    #结果返回处理
    print(response.status_code)
    
    # 修改这里：直接解析JSON响应为字典
    resultJson = response.json()  # 直接获取JSON字典
    
    # 如果需要查看格式化后的JSON字符串，可以这样打印
    print(json.dumps(resultJson, ensure_ascii=False, indent=2))
    
    if save_json_path:
        # 保存为json文件
        with open(save_json_path, "w", encoding=encode) as f:
            json.dump(resultJson, f, ensure_ascii=False, indent=2)
    
    print(f"[企业模糊搜索接口] 耗时：{time.time() - start_time}s")
    return resultJson


def enterprise_info_verify(searchKey, save_json_path=None):
    """
    接口: 企业信息核验, 地址： https://api.qichacha.com/EnterpriseInfo/Verify
    本地文档: api_qichacha\document\enterprise_info_verify.md
    传入参数: 搜索关键词（统一社会信用代码、企业名称,名称不能是简称,必须是完整准确的公司名称）
    """
    start_time = time.time()
    reqInterNme = "https://api.qichacha.com/EnterpriseInfo/Verify"
    paramStr = f"searchKey={searchKey}"
    url = reqInterNme + "?key=" + appKey + "&" + paramStr
    headers = get_headers()
    response = requests.get(url, headers=headers)

    #结果返回处理
    print(response.status_code)
    
    # 修改这里：直接解析JSON响应为字典
    resultJson = response.json()  # 直接获取JSON字典
    
    # 如果需要查看格式化后的JSON字符串，可以这样打印
    print(json.dumps(resultJson, ensure_ascii=False, indent=2))
    
    if save_json_path:
        # 保存为json文件
        with open(save_json_path, "w", encoding=encode) as f:
            json.dump(resultJson, f, ensure_ascii=False, indent=2)
    
    print(f"[企业信息核验接口] 耗时：{time.time() - start_time}s")
    return resultJson
    

def get_info_v0_0_3(searchKey):
    start_time = time.time()
    resultJson = fuzzy_search(searchKey, fr"H:\qitan\api_qichacha\test_result\[企业模糊搜索]{searchKey}.json")
    
    # 确保fuzzy_search返回的是字典类型
    if isinstance(resultJson, str):
        resultJson = json.loads(resultJson)
    
    accurate_name = resultJson.get("Result")[0].get("Name")
    ret_info = enterprise_info_verify(accurate_name, fr"H:\qitan\api_qichacha\test_result\[企业信息核验]{accurate_name}.json")
    print(f"[v0.0.3版本获取信息接口] 耗时：{time.time() - start_time}s")
    return ret_info


if __name__ == "__main__":
    # fuzzy_search("万达动漫", "[企业模糊搜索]万达动漫.json")
    
    # enterprise_info_verify("北京万达动漫有限公司", "[企业信息核验]北京万达动漫有限公司.json")
    
    get_info_v0_0_3("山东中网盾数字")
    
    