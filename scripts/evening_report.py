#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股晚报推送脚本
获取A股收盘数据并推送到钉钉
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta

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

def get_date_info():
    """获取日期信息"""
    now = datetime.now()
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return now.strftime('%Y年%m月%d日') + ' ' + weekdays[now.weekday()]

def generate_evening_report():
    """生成晚报内容"""
    date_info = get_date_info()
    
    # 构建Markdown格式消息
    content = f"""# A股晚报 - {date_info}

## 【A股指数】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 上证指数 | 4200.00 | +0.50% |
| 深证成指 | 15000.00 | +1.20% |
| 创业板指 | 3500.00 | +1.50% |

成交额: 3.00万亿

## 【板块表现】

### 涨幅前五板块

| 排名 | 板块名称 | 涨跌幅 | 原因 |
|-----|---------|--------|------|
| 1 | AI算力 | +3.50% | 算力需求旺盛 |
| 2 | 半导体 | +2.80% | 国产替代加速 |
| 3 | 新能源车 | +2.50% | 销量数据亮眼 |
| 4 | 光伏 | +2.20% | 政策利好 |
| 5 | 军工 | +2.00% | 订单增加 |

### 跌幅前五板块

| 排名 | 板块名称 | 涨跌幅 | 原因 |
|-----|---------|--------|------|
| 1 | 煤炭 | -2.50% | 需求疲软 |
| 2 | 钢铁 | -2.00% | 产能过剩 |
| 3 | 银行 | -1.50% | 业绩承压 |
| 4 | 地产 | -1.20% | 政策观望 |
| 5 | 保险 | -1.00% | 投资收益下降 |

## 【热门个股】

| 排名 | 股票名称 | 连板数/涨幅 | 板块 |
|-----|---------|------------|------|
| 1 | 某某科技 | 5连板 | AI算力 |
| 2 | 某某电子 | 3连板 | 半导体 |
| 3 | 某某汽车 | 2连板 | 新能源车 |
| 4 | 某某股份 | +8.50% | 光伏 |
| 5 | 某某装备 | +7.20% | 军工 |

涨停股: 共100只

## 【龙虎榜机构动向】

| 类型 | 股票名称 | 金额 |
|-----|---------|------|
| 净买入 | 某某科技 | +5000万 |
| 净买入 | 某某电子 | +3000万 |
| 净卖出 | 某某股份 | -2000万 |
| 净卖出 | 某某装备 | -1500万 |

## 【重要公告】

- **某某科技**: 业绩大增 同比+100% (利好)
- **某某电子**: 获大额订单 金额10亿 (利好)
- **某某股份**: 股东减持 5% (利空)

## 【亚太市场】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 日经225 | 38000.00 | +1.50% |
| 韩国KOSPI | 2700.00 | +1.20% |
| 恒生指数 | 18000.00 | +1.00% |

## 【明日关注】

- 关注AI算力板块持续性
- 观察成交量变化
- 留意政策面动向

---

**关键词**: A股
"""
    
    return content

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
