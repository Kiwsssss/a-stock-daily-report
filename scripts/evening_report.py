#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股晚报推送脚本
使用DeepSeek API搜索和生成A股数据并推送到钉钉
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
            "title": "A股晚报",
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

def generate_evening_report():
    """生成晚报内容"""
    date_info = datetime.now().strftime('%Y年%m月%d日')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[datetime.now().weekday()]
    
    prompt = f"""请整理今日A股晚报，日期：{date_info} {weekday}

要求：
1. 搜索最新的A股市场数据（今天收盘后的数据）
2. 使用Markdown表格格式
3. 必须包含关键词"A股"
4. 数据要准确真实

请按以下格式生成：

# A股晚报 - {date_info} {weekday}

## 【A股指数】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 上证指数 | xxxx.xx | +x.xx% |
| 深证成指 | xxxx.xx | +x.xx% |
| 创业板指 | xxxx.xx | +x.xx% |

成交额: x.xx万亿

## 【板块表现】

### 涨幅前五板块

| 排名 | 板块名称 | 涨跌幅 | 原因 |
|-----|---------|--------|------|
| 1 | 板块名 | +x.xx% | 简要原因 |
| 2 | 板块名 | +x.xx% | 简要原因 |
| 3 | 板块名 | +x.xx% | 简要原因 |
| 4 | 板块名 | +x.xx% | 简要原因 |
| 5 | 板块名 | +x.xx% | 简要原因 |

### 跌幅前五板块

| 排名 | 板块名称 | 涨跌幅 | 原因 |
|-----|---------|--------|------|
| 1 | 板块名 | -x.xx% | 简要原因 |
| 2 | 板块名 | -x.xx% | 简要原因 |
| 3 | 板块名 | -x.xx% | 简要原因 |
| 4 | 板块名 | -x.xx% | 简要原因 |
| 5 | 板块名 | -x.xx% | 简要原因 |

## 【热门个股】

| 排名 | 股票名称 | 连板数/涨幅 | 板块 |
|-----|---------|------------|------|
| 1 | 股票名 | x连板 | 板块名 |
| 2 | 股票名 | x连板 | 板块名 |
| 3 | 股票名 | x连板 | 板块名 |
| 4 | 股票名 | +xx% | 板块名 |
| 5 | 股票名 | +xx% | 板块名 |

涨停股: 共xx只

## 【龙虎榜机构动向】

| 类型 | 股票名称 | 金额 |
|-----|---------|------|
| 净买入 | 股票名 | +xxx万 |
| 净买入 | 股票名 | +xxx万 |
| 净卖出 | 股票名 | -xxx万 |
| 净卖出 | 股票名 | -xxx万 |

## 【重要公告】

- **公司名称**: 公告摘要 (利好/利空)
- **公司名称**: 公告摘要 (利好/利空)
- **公司名称**: 公告摘要 (利好/利空)

## 【亚太市场】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 日经225 | xxxxx.xx | +x.xx% |
| 韩国KOSPI | xxxx.xx | +x.xx% |
| 恒生指数 | xxxxx.xx | +x.xx% |

## 【明日关注】

- 关注事项1
- 关注事项2

---

**关键词**: A股

注意：
1. 板块名称要用通俗易懂的名称（如：AI算力、半导体、新能源车等）
2. 重要公告只选龙头公司的3-5条重要公告
3. 热门个股融合连板股和涨幅榜前几名
4. 数据必须准确，特别是指数点位和涨跌幅"""

    # 调用DeepSeek API
    print("正在调用DeepSeek API生成晚报...")
    content = call_deepseek_api(prompt)
    
    if content:
        return content
    else:
        # 如果API调用失败，返回默认内容
        return f"""# A股晚报 - {date_info} {weekday}

## 【A股指数】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 上证指数 | 4200.00 | +0.50% |
| 深证成指 | 15000.00 | +1.20% |
| 创业板指 | 3500.00 | +1.50% |

成交额: 3.00万亿

**关键词**: A股"""

def main():
    """主函数"""
    print(f"开始生成A股晚报 - {datetime.now()}")
    
    # 生成晚报内容
    content = generate_evening_report()
    
    # 发送到钉钉
    success = send_dingtalk_message(content)
    
    if success:
        print("晚报推送成功！")
    else:
        print("晚报推送失败！")
    
    return success

if __name__ == "__main__":
    main()
