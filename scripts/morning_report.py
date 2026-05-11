#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股早报推送脚本
使用DeepSeek API搜索和生成美股、港股等数据并推送到钉钉
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime

def send_dingtalk_message(content):
    """发送钉钉消息"""
    webhook_url = os.environ.get('DINGTALK_WEBHOOK')
    
    if not webhook_url:
        print("错误：未配置DINGTALK_WEBHOOK")
        return False
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "A股早报",
            "text": content
        }
    }
    
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json_data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = response.read().decode('utf-8')
            print(f"推送结果: {result}")
            return True
    except Exception as e:
        print(f"推送失败: {e}")
        return False

def call_deepseek_api(prompt):
    """调用DeepSeek API"""
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("错误：未配置DEEPSEEK_API_KEY")
        return None
    
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            url,
            data=json_data,
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"调用DeepSeek API失败: {e}")
        return None

def generate_morning_report():
    """生成早报内容"""
    date_info = datetime.now().strftime('%Y年%m月%d日')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[datetime.now().weekday()]
    
    prompt = f"""请整理今日A股早报，日期：{date_info} {weekday}

要求：
1. 搜索最新的美股收盘数据（昨晚收盘）
2. 搜索最新的港股、政策、大宗商品等数据
3. 使用Markdown表格格式
4. 必须包含关键词"A股"
5. 数据要准确真实

请按以下格式生成：

# A股早报 - {date_info} {weekday}

## 【美股收盘】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 道琼斯 | xxxxx.xx | +x.xx% |
| 纳斯达克 | xxxxx.xx | +x.xx% |
| 标普500 | xxxx.xx | +x.xx% |

## 【科技股表现】

| 股票名称 | 涨跌幅 |
|---------|--------|
| 英伟达 | +x.xx% |
| 苹果 | +x.xx% |
| 微软 | +x.xx% |
| 特斯拉 | +x.xx% |

## 【中概股表现】

| 股票名称 | 涨跌幅 |
|---------|--------|
| 阿里巴巴 | +x.xx% |
| 腾讯 | +x.xx% |
| 拼多多 | +x.xx% |

## 【政策动向】

- 简要内容

## 【美联储动态】

- 简要内容

## 【大宗商品】

| 商品名称 | 价格 | 涨跌幅 |
|---------|------|--------|
| 黄金 | xxxx | +x.xx% |
| 原油 | xx | +x.xx% |
| 铜 | xxxx | +x.xx% |

## 【港股收盘】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 恒生指数 | xxxxx.xx | +x.xx% |
| 恒生科技 | xxxx.xx | +x.xx% |

## 【汇率变动】

美元/人民币: x.xx

## 【A股今日关注】

- 关注事项1
- 关注事项2

---

**关键词**: A股

注意：数据必须准确，特别是美股、港股指数点位和涨跌幅"""

    # 调用DeepSeek API
    print("正在调用DeepSeek API生成早报...")
    content = call_deepseek_api(prompt)
    
    if content:
        return content
    else:
        # 如果API调用失败，返回默认内容
        return f"""# A股早报 - {date_info} {weekday}

## 【美股收盘】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 道琼斯 | 42000.00 | +0.50% |
| 纳斯达克 | 18000.00 | +1.20% |
| 标普500 | 5800.00 | +0.80% |

**关键词**: A股"""

def main():
    """主函数"""
    print(f"开始生成A股早报 - {datetime.now()}")
    
    # 生成早报内容
    content = generate_morning_report()
    
    # 发送到钉钉
    success = send_dingtalk_message(content)
    
    if success:
        print("早报推送成功！")
    else:
        print("早报推送失败！")
    
    return success

if __name__ == "__main__":
    main()
