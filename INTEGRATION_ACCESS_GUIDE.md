# 集成管理功能访问指南

## 🚀 快速访问

### 1. 启动服务

**后端服务 (端口 8000)**
```bash
cd org-platform/backend
python manage.py runserver 0.0.0.0:8000
```

**前端服务 (端口 3000)**
```bash
cd org-platform/frontend
npm run dev
```

### 2. 访问地址

- **前端应用**: http://localhost:3000
- **集成管理**: http://localhost:3000/integration-management
- **后端API**: http://localhost:8000

### 3. 登录信息

- **用户名**: admin
- **密码**: admin123

## 📋 功能页面

### 集成管理主页
- **路径**: `/integration-management`
- **功能**: 集成管理概览、快速导航、统计信息

### 集成仪表板
- **路径**: `/integration-dashboard`
- **功能**: 系统状态监控、性能图表、活动日志

### 集成系统管理
- **路径**: `/integration-systems`
- **功能**: 第三方系统配置、连接测试、健康监控

### API网关管理
- **路径**: `/api-gateways`
- **功能**: API路由配置、限流设置、性能监控

### 数据同步管理
- **路径**: `/data-sync-rules`
- **功能**: 同步规则配置、字段映射、日志查看

## 🎯 示例数据

系统已预置以下示例数据：

### 集成系统
1. **绩效考核系统** - Token认证
2. **OA办公系统** - 基础认证
3. **财务系统** - API Key认证

### API网关
1. **主网关** - 统一API入口
2. **绩效考核API代理** - GET /api/performance/*
3. **OA系统API代理** - POST /api/oa/*

### 数据同步规则
1. **员工数据同步** - 实时同步到绩效考核系统
2. **部门数据同步** - 批量同步到绩效考核系统

## 🔧 功能特性

### 集成系统管理
- ✅ 多系统类型支持
- ✅ 多种认证方式
- ✅ 连接测试功能
- ✅ 健康状态监控

### API网关
- ✅ 动态路由配置
- ✅ 请求限流控制
- ✅ 响应缓存机制
- ✅ 数据转换功能

### 数据同步
- ✅ 实时/批量/定时同步
- ✅ 字段映射配置
- ✅ 数据清洗规则
- ✅ 数据校验机制

### 监控告警
- ✅ 系统健康监控
- ✅ 性能指标分析
- ✅ 错误日志记录
- ✅ 告警通知机制

## 🚨 故障排除

### 常见问题

**1. 页面无法访问**
- 检查前端服务是否启动 (端口 3000)
- 检查后端服务是否启动 (端口 8000)
- 检查防火墙设置

**2. API调用失败**
- 检查后端服务状态
- 查看浏览器控制台错误
- 检查网络连接

**3. 数据加载失败**
- 检查数据库连接
- 查看后端日志
- 确认数据初始化

### 调试方法

**前端调试**
```bash
# 查看前端日志
cd org-platform/frontend
npm run dev
```

**后端调试**
```bash
# 查看后端日志
cd org-platform/backend
python manage.py runserver 0.0.0.0:8000 --verbosity=2
```

**数据库检查**
```bash
# 检查数据库
cd org-platform/backend
python manage.py shell
>>> from organizations.integration_models import IntegrationSystem
>>> IntegrationSystem.objects.all()
```

## 📞 技术支持

如果遇到问题，请检查：

1. **服务状态** - 确保前后端服务正常运行
2. **网络连接** - 确保端口未被占用
3. **数据初始化** - 运行 `python manage.py init_integration_data`
4. **日志信息** - 查看控制台错误信息

---

**集成管理功能已准备就绪！请访问 http://localhost:3000/integration-management 开始使用。**
