# 企业信息核验 (ApiCode：2001)

## 接口描述
支持各类型企业信息准确性校验，广泛应用于金融服务身份核实、互联网平台商家入驻资质审查、供应链上下游信息核实等场景，返回包括工商照面信息、上市信息、注销吊销信息、联系信息、企业坐标经纬度、开票信息、小微企业标识、企业规模、英文名来源、企查查行业等信息。

## 基本信息
*   **接口地址**: `https://api.qichacha.com/EnterpriseInfo/Verify`
*   **请求方式**: `GET`
*   **支持格式**: `JSON`
*   **请求示例**: `https://api.qichacha.com/EnterpriseInfo/Verify?key=AppKey&searchKey=xxxxxx`

## 请求参数

### 1. Headers 参数
| 名称 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `Token` | String | 是 | 验证加密值。Md5（`key`+`Timespan`+`SecretKey`）加密的**32位大写**字符串。 |
| `Timespan` | String | 是 | 精确到秒的Unix时间戳。 |

### 2. Query 参数
| 名称 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `key` | String | 是 | 应用APPKEY（在账号安全页面查询）。 |
| `searchKey` | String | 是 | 搜索关键词（统一社会信用代码、企业名称）。 |

## 返回参数 (Return)

| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `VerifyResult` | Int32 | 1 | 数据是否存在（1-存在，0-不存在） |
| `Data` | Object | - | 数据信息（详细字段见下表） |

### Data：数据信息
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `KeyNo` | String | 100 | 主键 |
| `Name` | String | 1000 | 企业名称 |
| `CreditCode` | String | 50 | 根据企业性质返回不同值（对中国境内企业（EntType=0/1/4/7/9/10/11）返回统一社会信用代码，对中国香港企业返回商业登记号码） |
| `OperName` | String | 1000 | 法定代表人 |
| `DesignatedRepresentativeList` | List\<Object\> | - | 委派代表列表 |
| `Status` | String | 100 | 登记状态 |
| `StartDate` | String | 50 | 成立日期（如"2022-01-01"） |
| `RegistCapi` | String | 50 | 注册资本（含单位） |
| `RegisteredCapital` | String | 50 | 注册资本数额 |
| `RegisteredCapitalUnit` | String | 50 | 注册资本单位 |
| `RegisteredCapitalCCY` | String | 50 | 注册资本币种 |
| `RealCapi` | String | 50 | 实缴资本（含单位） |
| `PaidUpCapital` | String | 50 | 实缴出资额数额 |
| `PaidUpCapitalUnit` | String | 50 | 实缴出资额单位 |
| `PaidUpCapitalCCY` | String | 50 | 实缴出资额币种 |
| `OrgNo` | String | 50 | 组织机构代码 |
| `No` | String | 200 | 根据企业性质返回不同值（对中国境内企业（EntType=0/1/4/7/9/10/11）返回工商注册号，对中国香港企业返回企业编号，对中国台湾企业返回企业编号） |
| `TaxNo` | String | 50 | 纳税人识别号 |
| `EconKind` | String | 100 | 企业类型 |
| `TermStart` | String | 50 | 营业期限开始日期（如"2022-01-01"） |
| `TermEnd` | String | 50 | 营业期限终止日期（如"2022-01-01"） |
| `TaxpayerType` | String | 32 | 纳税人资质 |
| `PersonScope` | String | 32 | 人员规模 |
| `InsuredCount` | String | 32 | 参保人数 |
| `CheckDate` | String | 50 | 核准日期（如"2022-01-01"） |
| `AreaCode` | String | 20 | 所属地区代码 |
| `Area` | Object | - | 所属地区对象 |
| `BelongOrg` | String | 500 | 登记机关 |
| `ImExCode` | String | 50 | 进出口企业代码 |
| `Industry` | Object | - | 国标行业对象 |
| `EnglishName` | String | 1000 | 英文名 |
| `Address` | String | 1000 | 注册地址 |
| `AddressPostalCode` | String | 50 | 注册地址邮编 |
| `AnnualAddress` | String | 1000 | 通信地址 |
| `AnnualAddressPostalCode` | String | 50 | 通信地址邮编 |
| `Scope` | String | 5000 | 经营范围 |
| `EntType` | String | 10 | 企业性质（0-大陆企业，1-社会组织，4-事业单位，7-医院，9-律师事务所，10-学校，11-机关单位，-1-其他） |
| `OrgCodeList` | List\<Object\> | - | 组织机构分类（经济类型）列表 |
| `ImageUrl` | String | 500 | 企业Logo地址 |
| `RevokeInfo` | Object | - | 注销吊销信息对象 |
| `OriginalName` | List\<Object\> | - | 曾用名列表 |
| `StockInfo` | Object | - | 上市信息对象 |
| `ContactInfo` | Object | - | 联系信息对象 |
| `LongLat` | Object | - | 经纬度对象 |
| `BankInfo` | Object | - | 开票信息对象 |
| `IsSmall` | String | 5 | 是否是小微企业（1-是，0-不是） |
| `Scale` | String | 10 | 企业规模（L-大型，M-中型，S-小型，XS-微型） |
| `QccIndustry` | Object | - | 企查查行业对象 |
| `IsOfficialEnglish` | String | 5 | 英文名来源（1-官方标识 ，0-非官方标识，-1-未标识） |

### 嵌套对象说明

#### DesignatedRepresentativeList：委派代表
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `PartnerName` | String | 1000 | 合伙人名称 |
| `DelegatedName` | String | 1000 | 委派代表名称 |

#### Area：所属地区
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `Province` | String | 32 | 省份 |
| `City` | String | 32 | 城市 |
| `County` | String | 32 | 区域 |

#### Industry：国标行业
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `IndustryCode` | String | 32 | 行业门类code |
| `Industry` | String | 200 | 行业门类描述 |
| `SubIndustryCode` | String | 32 | 行业大类code |
| `SubIndustry` | String | 200 | 行业大类描述 |
| `MiddleCategoryCode` | String | 32 | 行业中类code |
| `MiddleCategory` | String | 200 | 行业中类描述 |
| `SmallCategoryCode` | String | 32 | 行业小类code |
| `SmallCategory` | String | 200 | 行业小类描述 |

#### OrgCodeList：组织机构分类（经济类型）
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `PrimaryCode` | String | 50 | 一级分类Code |
| `SecondaryCode` | String | 50 | 二级分类Code |

#### RevokeInfo：注销吊销信息
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `CancelDate` | String | 50 | 注销日期（如"2022-01-01"） |
| `CancelReason` | String | 2000 | 注销原因 |
| `RevokeDate` | String | 50 | 吊销日期（如"2022-01-01"） |
| `RevokeReason` | String | 2000 | 吊销原因 |

#### OriginalName：曾用名
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `Name` | String | 1000 | 曾用名 |
| `ChangeDate` | String | 50 | 变更日期（如"2022-01-01"） |

#### StockInfo：上市信息
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `StockNumber` | String | 32 | 股票代码（若A股和港股同时存在，优先返回A股代码） |
| `StockType` | String | 10 | 上市类型（A股、港股、美股、新三板、新四板） |

#### ContactInfo：联系信息
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `WebSiteList` | List\<String\> | - | 网址列表 |
| `Email` | String | 200 | 邮箱 |
| `MoreEmailList` | List\<Object\> | - | 更多邮箱列表 |
| `Tel` | String | 100 | 联系电话 |
| `MoreTelList` | List\<Object\> | - | 更多电话列表 |

##### MoreEmailList：更多邮箱
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `Email` | String | 200 | 邮箱 |
| `Source` | String | 1000 | 来源（如"互联网"） |

##### MoreTelList：更多电话
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `Tel` | String | 100 | 电话 |
| `Source` | String | 1000 | 来源（如"互联网"） |

#### LongLat：经纬度
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `Longitude` | String | 32 | 经度 |
| `Latitude` | String | 32 | 纬度 |

#### BankInfo：开票信息
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `Bank` | String | 500 | 开户行 |
| `BankAccount` | String | 100 | 开户行账号 |
| `Name` | String | 1000 | 企业名称 |
| `CreditCode` | String | 50 | 企业税号 |
| `Address` | String | 1000 | 企业地址 |
| `Tel` | String | 100 | 电话号码 |

#### QccIndustry：企查查行业
| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `AName` | String | 200 | 一级分类名称 |
| `BName` | String | 200 | 二级分类名称 |
| `CName` | String | 200 | 三级分类名称 |
| `DName` | String | 200 | 四级分类名称 |

## JSON返回示例

```json
{
    "Status": "200",
    "Message": "【有效请求】查询成功",
    "OrderNumber": "ENTERPRISEINFO2023040110353488211611",
    "Result": {
        "VerifyResult": 1,
        "Data": {
            "KeyNo": "xxxxxxxxxxx73bc2120479d31",
            "Name": "xxxx有限责任公司",
            "CreditCode": "9111xxxxxxxxxxxx82Q",
            "OperName": "xxx",
            "DesignatedRepresentativeList": [
                {
                    "PartnerName": "xxx股权投资有限公司",
                    "DelegatedName": "xxx"
                }
            ],
            "Status": "存续（在营、开业、在册）",
            "StartDate": "2010-03-03",
            "RegistCapi": "185000万元",
            "RegisteredCapital": "185000",
            "RegisteredCapitalUnit": "万",
            "RegisteredCapitalCCY": "CNY",
            "RealCapi": "185000万元",
            "PaidUpCapital": "185000",
            "PaidUpCapitalUnit": "万",
            "PaidUpCapitalCCY": "CNY",
            "OrgNo": "xxxx8508-x",
            "No": "xxxxxxxx012660422",
            "TaxNo": "9xxxxxxxxxx85082Q",
            "EconKind": "有限责任公司（自然人投资或控股）",
            "TermStart": "2010-03-03",
            "TermEnd": "2025-05-01",
            "TaxpayerType": "一般纳税人",
            "PersonScope": "10000以上",
            "InsuredCount": "81",
            "CheckDate": "2022-07-20",
            "AreaCode": "110108",
            "Area": {
                "Province": "北京市",
                "City": "北京市",
                "County": "海淀区"
            },
            "BelongOrg": "北京市海淀区市场监督管理局",
            "ImExCode": "11xxxxxxxxxx082",
            "Industry": {
                "IndustryCode": "M",
                "Industry": "科学研究和技术服务业",
                "SubIndustryCode": "75",
                "SubIndustry": "科技推广和应用服务业",
                "MiddleCategoryCode": "751",
                "MiddleCategory": "技术推广服务",
                "SmallCategoryCode": "7519",
                "SmallCategory": "其他技术推广服务"
            },
            "EnglishName": "Xiaomi Inc.",
            "Address": "北京市海淀区西xxxxxxxxxxx号",
            "AddressPostalCode": "100085",
            "AnnualAddress": "北京市朝阳区xxxxxxxx号",
            "AnnualAddressPostalCode": "100085",
            "Scope": "技术开发；货物进出口、技术进出口、代理进出口；销售通讯设备、厨房用品、卫生用品（含个人护理用品）、日用杂货、化妆品、医疗器械Ⅰ类、Ⅱ类、避孕器具、玩具、体育用品、文化用品、服装鞋帽、钟表眼镜、针纺织品、家用电器、家具（不从事实体店铺经营）、花、草及观赏植物、不再分装的包装种子、照相器材、工艺品、礼品、计算机、软件及辅助设备、珠宝首饰、食用农产品、宠物食品、电子产品、摩托车、电动车、自行车及零部件、智能卡、五金交电（不从事实体店铺经营）、建筑材料（不从事实体店铺经营）；维修仪器仪表；维修办公设备；承办展览展示活动；会议服务；筹备、策划、组织大型庆典；设计、制作、代理、发布广告；摄影扩印服务；文艺演出票务代理、体育赛事票务代理、展览会票务代理、博览会票务代理；手机技术开发；手机生产、手机服务；从事互联网文化活动；出版物零售；出版物批发；销售第三类医疗器械；销售食品；零售药品；广播电视节目制作；经营电信业务。（市场主体依法自主选择经营项目，开展经营活动；从事互联网文化活动、出版物批发、出版物零售、销售食品、经营电信业务、广播电视节目制作、零售药品、销售第三类医疗器械以及依法须经批准的项目，经相关部门批准后依批准的内容开展经营活动；不得从事国家和本市产业政策禁止和限制类项目的经营活动。）",
            "EntType": "0",
            "OrgCodeList": [
                {
                    "PrimaryCode": "100100",
                    "SecondaryCode": "100101"
                }
            ],
            "ImageUrl": "https://image.qcc.com/logo/xxxxxxxxxxxx20479d31.jpg",
            "RevokeInfo": {
                "CancelDate": "2022-09-01",
                "CancelReason": "决议解散",
                "RevokeDate": "2023-01-21",
                "RevokeReason": "《中华人民共和国公司法》第二百一十一条第一款"
            },
            "OriginalName": [
                {
                    "Name": "xxxx有限责任公司",
                    "ChangeDate": "2013-07-30"
                }
            ],
            "StockInfo": {
                "StockNumber": "xxxxxx",
                "StockType": "新三板"
            },
            "ContactInfo": {
                "WebSiteList": [
                    "http://www.xxxx.com"
                ],
                "Email": "xxxxxxxxxxx@xxxx.com",
                "MoreEmailList": [
                    {
                        "Email": "xxxxxxxxx@xx.com",
                        "Source": "2021年报"
                    }
                ],
                "Tel": "010-6xxxxxxxxxx6",
                "MoreTelList": [
                    {
                        "Tel": "010-6xxxxxxxx8",
                        "Source": "2021年报"
                    },
                    {
                        "Tel": "40xxxxxxxx88",
                        "Source": "互联网"
                    }
                ]
            },
            "LongLat": {
                "Longitude": "116.321582690887",
                "Latitude": "40.062387328797"
            },
            "BankInfo": {
                "Bank": "xxxx有限公司xxxxx支行",
                "BankAccount": "xxxxxxxxxxxxx6962",
                "Name": "xxxx有限责任公司",
                "CreditCode": "xxxxxxxxxxxxx1385082Q",
                "Address": "北京市海淀区西xxxxxxxxxxxxxxxx号",
                "Tel": "010-6xxxxxxxx6"
            },
            "IsSmall": "0",
            "Scale": "L",
            "QccIndustry": {
                "AName": "消费",
                "BName": "文娱传媒",
                "CName": "出版",
                "DName": "报纸杂志"
            },
            "IsOfficialEnglish": "1"
        }
    }
}
```

---
*文档生成时间: 2024-05-24*