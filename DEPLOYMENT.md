# GitHub Actions 部署指南

## 第一步：创建GitHub仓库

1. 打开浏览器，访问 https://github.com
2. 登录您的GitHub账号（如果没有，点击 "Sign up" 注册一个免费账号）
3. 点击右上角的 "+" 号，选择 "New repository"
4. 填写仓库信息：
   - Repository name: `a-stock-daily-report`
   - Description: `A股早晚报自动推送系统`
   - 选择 "Public" 或 "Private"（建议选Public）
   - **不要**勾选 "Add a README file"
   - **不要**勾选 "Add .gitignore"
   - **不要**选择 License
5. 点击 "Create repository"

## 第二步：上传文件到GitHub

### 方式1：使用网页上传（推荐，最简单）

1. 在刚创建的仓库页面，点击 "uploading an existing file"
2. 打开文件夹：`C:\Users\21893\Desktop\stock\github-actions-a-stock`
3. 将以下文件/文件夹拖拽到上传区域：
   - `.github` 文件夹
   - `scripts` 文件夹
   - `README.md`
   - `.gitignore`
4. 在 "Commit changes" 区域：
   - 标题：`Initial commit: A股日报推送系统`
   - 描述：（可选）添加一些说明
5. 点击 "Commit changes"

### 方式2：使用Git命令行（如果您熟悉Git）

```bash
# 进入项目目录
cd C:\Users\21893\Desktop\stock\github-actions-a-stock

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: A股日报推送系统"

# 设置主分支
git branch -M main

# 添加远程仓库（替换为您的用户名）
git remote add origin https://github.com/您的用户名/a-stock-daily-report.git

# 推送到GitHub
git push -u origin main
```

## 第三步：配置Secrets

1. 在仓库页面，点击 "Settings" 标签
2. 在左侧菜单，找到 "Secrets and variables"，点击 "Actions"
3. 点击 "New repository secret"
4. 填写：
   - Name: `DINGTALK_WEBHOOK`
   - Value: `https://oapi.dingtalk.com/robot/send?access_token=b35aa21f218ab9c2d28ae448470eeea2205574a544a8a14d58061c386d2491d4`
5. 点击 "Add secret"

## 第四步：启用GitHub Actions

1. 在仓库页面，点击 "Actions" 标签
2. 如果看到提示 "Workflows aren't being run on this repository"，点击 "I understand my workflows, go ahead and enable them"
3. 您会看到两个workflow：
   - `A股早报推送`
   - `A股晚报推送`

## 第五步：测试

### 手动触发测试

1. 在 "Actions" 标签页
2. 点击左侧的 "A股晚报推送"
3. 点击右侧的 "Run workflow" 按钮
4. 选择 "Branch: main"
5. 点击绿色的 "Run workflow" 按钮
6. 等待几秒钟，刷新页面，会看到一个新的运行记录
7. 点击运行记录，查看 "send-evening-report" job
8. 展开查看详细日志
9. 检查钉钉群是否收到消息

### 检查定时任务

- 早报：每天北京时间8:30自动执行
- 晚报：每天北京时间15:30自动执行
- 注意：GitHub Actions可能有1-5分钟的延迟

## 常见问题

### Q1: Actions没有执行？

**检查清单**：
1. 仓库是否是Public？（Private仓库也可以，但需要确认Actions已启用）
2. Settings -> Actions -> General -> Actions permissions 是否选择了 "Allow all actions and reusable workflows"
3. 检查workflow文件语法是否正确

### Q2: 执行失败？

**排查步骤**：
1. 点击失败的运行记录
2. 查看详细日志
3. 常见错误：
   - `DINGTALK_WEBHOOK` 未配置或配置错误
   - Python脚本执行错误
   - 网络问题

### Q3: 钉钉没收到消息？

**检查清单**：
1. Webhook地址是否正确
2. 消息是否包含关键词 "A股"
3. 钉钉机器人是否被禁用
4. 查看Actions日志中的推送结果

### Q4: 如何修改推送时间？

编辑 `.github/workflows/morning_report.yml` 或 `evening_report.yml`：

```yaml
on:
  schedule:
    - cron: '30 0 * * 1-5'  # 修改这里
```

Cron格式：`分 时 日 月 周`
- UTC时间 = 北京时间 - 8小时
- 早报8:30 = UTC 0:30
- 晚报15:30 = UTC 7:30

### Q5: 如何修改推送内容？

编辑 `scripts/morning_report.py` 或 `scripts/evening_report.py`，修改 `generate_morning_report()` 或 `generate_evening_report()` 函数中的内容。

## 进阶配置

### 添加数据源

当前脚本是示例数据，要获取真实数据，可以：

1. **使用搜索API**：
   - 集成百度搜索API
   - 或使用其他金融数据API

2. **修改脚本**：
   ```python
   # 在脚本中添加数据获取逻辑
   import requests
   
   def get_stock_data():
       # 调用API获取数据
       response = requests.get('API_URL')
       return response.json()
   ```

3. **添加依赖**：
   在workflow文件中添加：
   ```yaml
   - name: Install dependencies
     run: |
       pip install requests beautifulsoup4
   ```

### 添加通知

可以在脚本中添加失败通知：
- 发送邮件
- 推送到其他平台
- 记录日志

## 维护

### 更新代码

1. 修改本地文件
2. 提交并推送到GitHub：
   ```bash
   git add .
   git commit -m "Update: 修改说明"
   git push
   ```
3. GitHub Actions会自动使用最新代码

### 监控运行状态

1. 定期查看Actions标签页
2. 检查是否有失败的运行
3. 查看日志排查问题

## 成本

- GitHub Actions免费额度：每月2000分钟
- 本项目每次运行约1-2分钟
- 每月约60次运行（早报+晚报，工作日）
- 完全在免费额度内

## 安全建议

1. **保护Secrets**：
   - 不要在代码中硬编码Webhook地址
   - 定期更换Webhook token

2. **限制权限**：
   - 如果仓库是Public，考虑使用Private仓库
   - 定期检查Actions权限设置

3. **监控异常**：
   - 定期检查Actions运行记录
   - 发现异常立即处理

## 支持

如有问题，请：
1. 查看GitHub Actions日志
2. 检查本文档的常见问题部分
3. 在仓库中创建Issue

---

**祝您使用愉快！**
