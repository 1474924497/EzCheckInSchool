import json
import time
import random
import requests

# 获取response.json dict
with open('./response.json', 'r', encoding='utf8')as fp:
    response_json = json.load(fp)
    college_all = response_json['data']['collegeAll']
    major_all = response_json['data']['majorAll']
    class_all = response_json['data']['classAll']

# 输入Secrets
stu_name = input()
stu_id = input()
dept_text = input()
sc_url = input()


def main():
    """
    主函数
    """
    # 获取学院、专业和班级信息
    try:
        info = dept_text.split('-', 3)
        college_name = info[0]
        major_name = info[1]
        class_name = info[2]
    except IndexError:
        print_info_error()
        exit(1)

    # 获取deptId
    try:
        for college in college_all:
            if college['name'] == college_name:
                college_id = college['deptId']
                break
        for major in major_all:
            if (major['name'] == major_name) & (major['parentId'] == college_id):
                major_id = major['deptId']
                break
        for class_ in class_all:
            if (class_['name'] == class_name) & (class_['parentId'] == major_id):
                class_id = class_['deptId']
                break
    except NameError:
        print_info_error()
        exit(1)
    # 时间判断 Github Actions采用国际标准时
    hms = update_time()
    if (hms[0] >= 6) & (hms[0] < 8):
        template_id = "clockSign1"
        customer_app_type_rule_id = 146
    elif (hms[0] >= 12) & (hms[0] < 14):
        template_id = "clockSign2"
        customer_app_type_rule_id = 147
    elif (hms[0] >= 21) & (hms[0] <= 22):
        template_id = "clockSign3"
        customer_app_type_rule_id = 148
    else:
        print("现在是%d点%d分，将打卡早间档测试" % (hms[0], hms[1]))
        template_id = "clockSign1"
        customer_app_type_rule_id = 146

    # 随机温度(36.2~36.5)
    a = random.uniform(36.2, 36.5)
    temperature = round(a, 1)

    check_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"

    check_json = {
        "businessType": "epmpics",
        "method": "submitUpInfoSchool",
        "jsonData": {
            "deptStr": {
                "deptid": class_id,
                "text": dept_text
            },
            "areaStr": {"streetNumber": "", "street": "旺草镇", "district": "绥阳县", "city": "遵义市", "province": "贵州省",
                        "town": "", "pois": "小旺草村旺草镇人民小学", "lng": 113.544407 + random.random() / 10000,
                        "lat": 34.831014 + random.random() / 10000, "address": "绥阳县旺草镇小旺草村旺草镇人民小学",
                        "text": "贵州省-遵义市", "code": ""},
            "reportdate": round(time.time() * 1000),
            "customerid": 43,
            "deptid": class_id,
            "source": "app",
            "templateid": template_id,
            "stuNo": stu_id,
            "username": stu_name,
            "userid": round(time.time()),
            "updatainfo": [
                {
                    "propertyname": "temperature",
                    "value": temperature
                },
                {
                    "propertyname": "symptom",
                    "value": "无症状"
                }
            ],
            "customerAppTypeRuleId": customer_app_type_rule_id,
            "clockState": 0
        },
    }

    # 提交打卡与结果判定
    flag = 0
    for i in range(1, 10):
        hms = update_time()
        response = requests.post(check_url, json=check_json)
        if response.status_code == 200:
            flag = 1
            break
        else:
            time.sleep(60)
    print(response.text)
    time_msg = str(hms[0]) + '时' + str(hms[1]) + '分' + str(hms[0]) + '秒'
    if flag == 1:
        if response.json()["msg"] == '成功':
            msg = time_msg + '时' + "打卡成功"
        else:
            msg = time_msg + "打卡异常"
    else:
        msg = time_msg + "网络错误打卡失败"

    print(msg)

    # 微信通知
    title = msg
    result = json.dumps(response.json(), sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
    content = f"""
    ```
    {result}
    ```

    """
    data = {
        "text": title,
        "desp": content
    }
    requests.post(sc_url, data=data)


def print_info_error():
    """
    打印 个人信息错误
    """
    print('请检查你填写的学院、专业、班级信息！')
    print('见完美校园健康打卡页面')
    print('如 理学院-应用物理学-应物1901')


def update_time():
    return [(time.localtime().tm_hour + 8) % 24,
            time.localtime().tm_min,
            time.localtime().tm_sec]


if __name__ == '__main__':
    main()
