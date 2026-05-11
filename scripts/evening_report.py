#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股晚报推送脚本
使用AkShare获取真实数据 + DeepSeek生成分析内容
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
        "max_tokens": 2000
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

def get_stock_data():
    """使用AkShare获取A股真实数据"""
    try:
        import akshare as ak
        
        print("正在获取指数数据...")
        # 获取上证指数
        sh_index = ak.stock_zh_index_spot_em(symbol="上证系列指数")
        sh_data = sh_index[sh_index['名称'] == '上证指数'].iloc[0]
        sh_price = float(sh_data['最新价'])
        sh_change = float(sh_data['涨跌幅'])
        
        # 获取深证成指和创业板指
        sz_index = ak.stock_zh_index_spot_em(symbol="深证系列指数")
        sz_data = sz_index[sz_index['名称'] == '深证成指'].iloc[0]
        sz_price = float(sz_data['最新价'])
        sz_change = float(sz_data['涨跌幅'])
        
        cy_data = sz_index[sz_index['名称'] == '创业板指'].iloc[0]
        cy_price = float(cy_data['最新价'])
        cy_change = float(cy_data['涨跌幅'])
        
        print("正在获取成交额...")
        # 获取成交额
        try:
            stock_info = ak.stock_zh_a_spot_em()
            amount = stock_info['成交额'].astype(float).sum() / 100000000  # 转换为亿
            amount_str = f"{amount/10000:.2f}万亿"
        except:
            amount_str = "数据获取失败"
        
        print("正在获取板块数据...")
        # 获取板块数据
        try:
            board_data = ak.stock_board_concept_name_em()
            board_data = board_data.sort_values('涨跌幅', ascending=False)
            
            top_boards = []
            for idx, row in board_data.head(5).iterrows():
                change_str = f"+{row['涨跌幅']:.2f}%" if row['涨跌幅'] >= 0 else f"{row['涨跌幅']:.2f}%"
                top_boards.append({
                    'name': row['板块名称'],
                    'change': change_str
                })
            
            bottom_boards = []
            for idx, row in board_data.tail(5).iterrows():
                change_str = f"+{row['涨跌幅']:.2f}%" if row['涨跌幅'] >= 0 else f"{row['涨跌幅']:.2f}%"
                bottom_boards.append({
                    'name': row['板块名称'],
                    'change': change_str
                })
        except Exception as e:
            print(f"获取板块数据失败: {e}")
            top_boards = None
            bottom_boards = None
        
        print("正在获取涨停股数据...")
        # 获取涨停股
        try:
            zt_data = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
            zt_count = len(zt_data)
            
            # 获取连板股
            lb_stocks = []
            for idx, row in zt_data.head(5).iterrows():
                lb_stocks.append({
                    'name': row['名称'],
                    'lb': row.get('连板数', '涨停'),
                    'sector': row.get('所属行业', '未知')
                })
        except Exception as e:
            print(f"获取涨停股数据失败: {e}")
            zt_count = 0
            lb_stocks = []
        
        return {
            'sh_price': sh_price,
            'sh_change': sh_change,
            'sz_price': sz_price,
            'sz_change': sz_change,
            'cy_price': cy_price,
            'cy_change': cy_change,
            'amount': amount_str,
            'top_boards': top_boards,
            'bottom_boards': bottom_boards,
            'zt_count': zt_count,
            'lb_stocks': lb_stocks
        }
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def generate_evening_report():
    """生成晚报内容"""
    date_info = datetime.now().strftime('%Y年%m月%d日')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekdays[datetime.now().weekday()]
    
    # 获取真实数据
    print("正在获取A股真实数据...")
    data = get_stock_data()
    
    if not data:
        # 如果获取失败，返回错误消息
        return f"""# A股晚报 - {date_info} {weekday}

**数据获取失败，请稍后重试**

**关键词**: A股"""
    
    # 格式化涨跌幅
    sh_change_str = f"+{data['sh_change']:.2f}%" if data['sh_change'] >= 0 else f"{data['sh_change']:.2f}%"
    sz_change_str = f"+{data['sz_change']:.2f}%" if data['sz_change'] >= 0 else f"{data['sz_change']:.2f}%"
    cy_change_str = f"+{data['cy_change']:.2f}%" if data['cy_change'] >= 0 else f"{data['cy_change']:.2f}%"
    
    # 使用DeepSeek生成板块原因分析
    print("正在调用DeepSeek生成分析内容...")
    
    board_analysis = ""
    if data['top_boards'] and data['bottom_boards']:
        top_board_names = [b['name'] for b in data['top_boards']]
        bottom_board_names = [b['name'] for b in data['bottom_boards']]
        
        analysis_prompt = f"""请简要分析以下A股板块涨跌原因（每条10字以内）：

涨幅前五：{', '.join(top_board_names)}
跌幅前五：{', '.join(bottom_board_names)}

请按以下格式回复（不要其他内容）：
涨幅板块原因：
1. 板块名：原因
2. 板块名：原因
...

跌幅板块原因：
1. 板块名：原因
2. 板块名：原因
..."""
        
        board_analysis = call_deepseek_api(analysis_prompt) or ""
    
    # 构建板块表格
    if data['top_boards']:
        top_board_rows = []
        for i, board in enumerate(data['top_boards'], 1):
            top_board_rows.append(f"| {i} | {board['name']} | {board['change']} | - |")
        top_board_table = "\n".join(top_board_rows)
    else:
        top_board_table = "| 1 | 数据获取失败 | - | - |"
    
    if data['bottom_boards']:
        bottom_board_rows = []
        for i, board in enumerate(data['bottom_boards'], 1):
            bottom_board_rows.append(f"| {i} | {board['name']} | {board['change']} | - |")
        bottom_board_table = "\n".join(bottom_board_rows)
    else:
        bottom_board_table = "| 1 | 数据获取失败 | - | - |"
    
    # 构建热门个股表格
    if data['lb_stocks']:
        lb_rows = []
        for i, stock in enumerate(data['lb_stocks'], 1):
            lb_rows.append(f"| {i} | {stock['name']} | {stock['lb']} | {stock['sector']} |")
        lb_table = "\n".join(lb_rows)
    else:
        lb_table = "| 1 | 数据获取失败 | - | - |"
    
    # 构建Markdown格式消息
    content = f"""# A股晚报 - {date_info} {weekday}

## 【A股指数】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 上证指数 | {data['sh_price']:.2f} | {sh_change_str} |
| 深证成指 | {data['sz_price']:.2f} | {sz_change_str} |
| 创业板指 | {data['cy_price']:.2f} | {cy_change_str} |

成交额: {data['amount']}

## 【板块表现】

### 涨幅前五板块

| 排名 | 板块名称 | 涨跌幅 | 原因 |
|-----|---------|--------|------|
{top_board_table}

### 跌幅前五板块

| 排名 | 板块名称 | 涨跌幅 | 原因 |
|-----|---------|--------|------|
{bottom_board_table}

## 【热门个股】

| 排名 | 股票名称 | 连板数/涨幅 | 板块 |
|-----|---------|------------|------|
{lb_table}

涨停股: 共{data['zt_count']}只

## 【龙虎榜机构动向】

| 类型 | 股票名称 | 金额 |
|-----|---------|------|
| 净买入 | 数据获取中 | - |
| 净卖出 | 数据获取中 | - |

## 【重要公告】

- 数据获取中...

## 【亚太市场】

| 指数名称 | 收盘点位 | 涨跌幅 |
|---------|---------|--------|
| 日经225 | 数据获取中 | - |
| 韩国KOSPI | 数据获取中 | - |
| 恒生指数 | 数据获取中 | - |

## 【明日关注】

- 关注市场热点持续性
- 观察成交量变化

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
