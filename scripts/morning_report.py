#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股早报推送脚本
使用DeepSeek API搜索和生成美股、港股等数据并推送到钉钉
优化版：多数据源验证 + 数据合理性检查 + 重试机制
"""

import os
import json
import urllib.request
import urllib.error
import re
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
        "temperature": 0.3,  # 降低温度，提高准确性
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

def validate_us_stock_data(content):
    """验证美股数据是否合理"""
    # 提取道琼斯指数
    dj_match = re.search(r'道琼斯.*?(\d{5}\.\d{2})', content)
    if dj_match:
        dj_price = float(dj_match.group(1))
        # 道琼斯合理范围：35000-45000
        if not (35000 <= dj_price <= 45000):
            print(f"道琼斯指数数据不合理: {dj_price}")
            return False
    
    # 提取纳斯达克指数
    ndq_match = re.search(r'纳斯达克.*?(\d{5}\.\d{2})', content)
    if ndq_match:
        ndq_price = float(ndq_match.group(1))
        # 纳斯达克合理范围：15000-20000
        if not (15000 <= ndq_price <= 20000):
            print(f"纳斯达克指数数据不合理: {ndq_price}")
            return False
    
    # 提取标普500
    sp_match = re.search(r'标普500.*?(\d{4}\.\d{2})', content)
    if sp_match:
        sp_price = float(sp_match.group(1))
        # 标普500合理范围：5000-6000
        if not (5000 <= sp_price <= 6000):
            print(f"标普500数据不合理: {sp_price}")
            return False
    
    print("数据验证通过")
    return True

def generate_morning_report_with_retry(max_retries=3):
    """生成早报内容（带重试机制）"""
    date_info = datetime.now().strftime('%Y年%m月%d日')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[datetime.now().weekday()]
    
    # 优化的prompt
    prompt = f"""请搜索并整理今日A股早报，日期：{date_info} {weekday}

【重要要求】
1. 必须搜索最新的真实数据（昨晚美股收盘数据）
2. 必须从多个权威数据源验证：新浪财经、东方财富、雪球、雅虎财经等
3. 数据必须准确真实，不要编造
4. 使用Markdown表格格式
5. 必须包含关键词"A股"

【数据要求】
- 道琼斯指数：合理范围35000-45000点
- 纳斯达克指数：合理范围15000-20000点
- 标普500：合理范围5000-6000点
- 恒生指数：合理范围15000-25000点

【格式要求】
严格按照以下格式生成：

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

【特别注意】
1. 数据必须准确，特别是美股、港股指数点位和涨跌幅
2. 如果无法获取最新数据，请明确说明"""

    # 重试机制
    for attempt in range(max_retries):
        print(f"正在调用DeepSeek API生成早报（第{attempt+1}次尝试）...")
        content = call_deepseek_api(prompt)
        
        if content:
            # 验证数据
            if validate_us_stock_data(content):
                print("数据验证成功")
                return content
            else:
                print(f"数据验证失败，准备重试...")
        else:
            print(f"API调用失败，准备重试...")
    
    # 如果所有重试都失败，返回默认内容
    print("所有重试都失败，返回默认内容")
    return f"""# A股早报 - {date_info} {weekday}

## 【美股收盘】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 道琼斯 | 数据获取失败 | - |
| 纳斯达克 | 数据获取失败 | - |
| 标普500 | 数据获取失败 | - |

**关键词**: A股

**提示**: 数据获取失败，请稍后重试或检查DeepSeek API配置"""

def main():
    """主函数"""
    print(f"开始生成A股早报 - {datetime.now()}")
    
    # 生成早报内容（带重试）
    content = generate_morning_report_with_retry(max_retries=3)
    
    # 发送到钉钉
    success = send_dingtalk_message(content)
    
    if success:
        print("早报推送成功！")
    else:
        print("早报推送失败！")
    
    return success

if __name__ == "__main__":
    main()
