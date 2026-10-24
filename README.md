## 电商订单自动化测试项目
- 一个基于 Django 后端的电商订单系统接口自动化测试项目，覆盖了用户、商品、订单全流程的接口测试，还做了高并发压测和持续集成，用来练手接口测试和工程化的东西。

## 技术栈

- **后端**：Django + Django REST Framework + JWT 认证
- **测试框架**：pytest + requests
- **测试报告**：pytest-html + Allure
- **并发压测**：Locust
- **持续集成**：GitHub Actions
- **数据库**：SQLite3

## 项目亮点

1. **业务比较完整**：从用户注册登录，到商品查询，再到订单的下单、支付、取消、退款，整个电商订单的状态流转都覆盖了，不是只有一两个接口的 demo。
2. **自动化用例比较全**：一共 35 个用例，正常功能、边界值、异常场景、权限越权都测到了，本地跑通过率 100%。
3. **做了高并发验证**：用 Locust 做了 50 并发、上万次请求的压测，验证了高并发场景下不会出现超卖，接口幂等性也没问题。
4. **幂等控制做了两层保障**：业务层先做前置校验，数据库层加了唯一索引兜底，避免高并发下重复下单，是工业里常用的方案。
5. **搭了 CI 持续集成**：基于 GitHub Actions 搭了流水线，每次提交代码都会自动跑一遍所有测试用例，生成测试报告，不用每次手动跑，省很多事。
6. **双格式测试报告**：pytest-html 和 Allure 两种报告都有，结果看得清楚，也方便追溯问题。

## 本地运行步骤

### 1. 安装依赖

```
pip install -r requirements.txt
```

### 2. 启动后端服务

```
cd system
python manage.py runserver
```

### 3. 执行自动化测试

```
# 生成 html 报告
pytest --html=reports/report.html --self-contained-html

# 生成 Allure 报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 4. 并发压测

```
locust -f locustfile.py
```

浏览器打开 Locust 控制台，设置并发数和地址就能开始压测。

## 项目目录

```
ecommerce-order-test/
├── api_test/                # 接口自动化测试用例
│   ├── testcases/           # 测试用例
│   └── reports/             # 测试报告
├── system/                  # Django 后端项目
│   ├── ecommerce/           # 主项目配置
│   ├── users/               # 用户模块
│   ├── goods/               # 商品模块
│   └── orders/              # 订单模块
├── locustfile.py            # 并发压测脚本
├── requirements.txt         # 依赖清单
└── README.md
```
