# 企业模糊搜索 (ApiCode：886)

## 接口描述
通过搜索关键字（如企业名、人名、产品名、地址、电话、经营范围等）获取匹配搜索条件的企业，每次请求返回最多5条记录，返回结果包括但不限于企业名称、法定代表人名称、企业状态、成立日期、统一社会信用代码、注册号等信息。

## 计费信息
*   **单价**: 0.10元/次
*   **套餐**:
    *   免费试用：20次
    *   标准套餐：1,000.00元 / 10000次
    *   高级套餐：5,000.00元 / 50000次
*   **限制**: 需企业实名用户使用，本接口需提供应用场景审核。

## 基本信息
*   **接口地址**: `https://api.qichacha.com/FuzzySearch/GetList`
*   **请求方式**: `GET`
*   **支持格式**: `JSON`
*   **请求示例**: `https://api.qichacha.com/FuzzySearch/GetList?key=AppKey&searchKey=XXXXXX`

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
| `searchKey` | String | 是 | 搜索关键词（支持企业名、人名、产品名、地址、电话、经营范围等）。 |
| `pageIndex` | String | 否 | 页码，默认第1页。 |

## 返回参数 (Return)

| 名称 | 类型 | 长度 | 描述 |
| :--- | :--- | :--- | :--- |
| `KeyNo` | String | 100 | 主键 |
| `Name` | String | 1000 | 企业名称 |
| `CreditCode` | String | 50 | 统一社会信用代码（查询企业为中国香港企业时，返回商业登记号码） |
| `StartDate` | String | 50 | 成立日期（如"2012-07-10"） |
| `OperName` | String | 1000 | 法定代表人姓名 |
| `Status` | String | 100 | 状态（如"存续"） |
| `No` | String | 200 | 注册号（查询企业为中国香港企业时，返回企业编号） |
| `Address` | String | 1000 | 注册地址 |

## JSON返回示例

```json
{
    "Paging": {
        "PageSize": 5,
        "PageIndex": 1,
        "TotalRecords": 1
    },
    "Result": [
        {
            "KeyNo": "xxxxxxxxxxx",
            "Name": "xxxxxxx",
            "CreditCode": "xxxxxxxxxxx",
            "StartDate": "2012-07-10",
            "OperName": "xx",
            "Status": "存续",
            "No": "xxxxxxxxxxxxx",
            "Address": "xxxxxxxxxxxxxx室"
        }
    ],
    "Status": "200",
    "Message": "查询成功",
    "OrderNumber": "FUZZYSEARCH2021012016353715836099"
}
```

---
*文档生成时间: 2024-05-24*