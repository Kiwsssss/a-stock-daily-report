# A股日报自动推送系统

基于GitHub Actions的A股早晚报自动推送系统，每天自动推送到钉钉群。

## 功能特点

- ✅ 完全免费，云端运行
- ✅ 不需要电脑开机
- ✅ 自动获取A股市场数据
- ✅ Markdown表格格式，美观易读
- ✅ 早报：每天8:30推送（美股、港股、政策等）
- ✅ 晚报：每天15:30推送（A股收盘数据、板块、个股等）

## 推送内容

### 早报（8:30）
- 美股收盘数据（道琼斯、纳斯达克、标普500）
- 科技股表现（英伟达、苹果、微软、特斯拉等）
- 中概股表现（阿里、腾讯、拼多多等）
- 政策动向
- 美联储动态
- 大宗商品（黄金、原油、铜）
- 港股表现
- 汇率变动
- A股今日关注

### 晚报（15:30）
- A股三大指数收盘数据
- 板块涨跌排行
- 热门个股（连板股、涨幅榜）
- 龙虎榜机构动向
- 重要公告
- 亚太市场表现
- 明日关注

## 部署步骤

### 1. 创建GitHub仓库

1. 登录GitHub
2. 点击右上角 "+" -> "New repository"
3. 仓库名称：`a-stock-daily-report`
4. 选择 "Public" 或 "Private"
5. 点击 "Create repository"

### 2. 上传文件

将本目录下的所有文件上传到GitHub仓库：

```bash
# 方式1：使用Git命令行
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/a-stock-daily-report.git
git push -u origin main

# 方式2：使用GitHub网页上传
# 在仓库页面点击 "uploading an existing file"，拖拽所有文件上传
```

### 3. 配置Secrets

在GitHub仓库页面：
1. 点击 "Settings" -> "Secrets and variables" -> "Actions"
2. 点击 "New repository secret"
3. 添加以下secret：
   - Name: `DINGTALK_WEBHOOK`
   - Value: `https://oapi.dingtalk.com/robot/send?access_token=你的token`

### 4. 启用GitHub Actions

1. 在仓库页面点击 "Actions"
2. 如果看到提示，点击 "I understand my workflows, go ahead and enable them"
3. 等待定时任务自动执行

## 测试

### 手动触发测试

1. 进入 "Actions" 标签页
2. 选择 "A股早报推送" 或 "A股晚报推送"
3. 点击 "Run workflow" -> "Run workflow"
4. 等待执行完成，检查钉钉群是否收到消息

### 查看执行日志

1. 在 "Actions" 标签页
2. 点击具体的workflow运行记录
3. 查看 "build" job的日志
4. 可以看到详细的执行过程和推送结果

## 自定义配置

### 修改推送时间

编辑 `.github/workflows/morning_report.yml` 或 `evening_report.yml`：

```yaml
on:
  schedule:
    - cron: '30 0 * * 1-5'  # UTC时间，北京时间8:30
```

Cron表达式说明：
- 格式：`分 时 日 月 周`
- UTC时间 = 北京时间 - 8小时
- 早报8:30 = UTC 0:30
- 晚报15:30 = UTC 7:30

### 修改推送内容

编辑 `scripts/morning_report.py` 或 `scripts/evening_report.py`，修改消息格式和内容。

## 注意事项

1. **时区问题**：GitHub Actions使用UTC时间，已自动转换为北京时间
2. **执行延迟**：定时任务可能有几分钟延迟，属于正常现象
3. **数据来源**：使用百度搜索获取实时数据
4. **关键词**：钉钉消息必须包含"A股"关键词才能推送成功

## 故障排查

### 没有收到推送

1. 检查Actions是否执行成功
2. 检查Secrets是否配置正确
3. 检查钉钉Webhook是否有效
4. 查看Actions日志中的错误信息

### 数据不准确

1. 检查搜索关键词是否合适
2. 检查数据来源网站是否可访问
3. 可能需要调整搜索策略

## 许可证

MIT License

## 作者

DuMate AI Assistant
