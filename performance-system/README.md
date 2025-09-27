# 绩效考核系统

## 📋 项目简介

绩效考核系统是一个基于Vue.js + Django的现代化绩效考核管理平台，支持完整的考核流程管理、职级权重配置、任务生成和评分统计功能。

## 🚀 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- 现代浏览器

### 启动系统

#### 1. 启动组织架构系统
```bash
# 后端
cd org-platform/backend
python manage.py runserver 8000

# 前端
cd org-platform/frontend
npm run dev
# 访问: http://localhost:3002
```

#### 2. 启动绩效考核系统
```bash
# 后端
cd performance-system/backend
python manage.py runserver 8001

# 前端
cd performance-system/frontend
npm run dev
# 访问: http://localhost:3001
```

## 📚 文档目录

### 📖 用户文档
- **[使用说明文档](PERFORMANCE_SYSTEM_USER_GUIDE.md)** - 完整的用户操作指南
- **[API接口文档](API_DOCUMENTATION.md)** - 详细的API接口说明
- **[部署指南](DEPLOYMENT_GUIDE.md)** - 系统部署和配置指南

### 🔧 技术文档
- **[技术文档](TECHNICAL_DOCUMENTATION.md)** - 系统架构和技术实现
- **[数据库设计](TECHNICAL_DOCUMENTATION.md#数据库设计)** - 数据表结构和关系
- **[前端组件架构](TECHNICAL_DOCUMENTATION.md#前端组件架构)** - Vue组件设计

## 🎯 核心功能

### 1. 考核周期管理
- 创建和管理考核周期
- 设置考核时间和状态
- 关联考核规则和指标

### 2. 考核规则配置
- **本部门上级评下级** - 部门内部上下级评价
- **全公司上级评下级** - 跨部门上级评价下级
- **同级互评** - 同级别员工相互评价
- **下级评上级** - 下级评价上级

### 3. 职级权重配置
- **高层正职** (董事长/总经理) - 权重 1.8
- **高层副职** (副总经理) - 权重 1.6
- **中层正职** (部门经理) - 权重 1.2
- **中层副职** (部门副经理) - 权重 1.1
- **基层正职** (主管) - 权重 1.0
- **普通员工** - 权重 0.9

### 4. 任务自动生成
- 根据考核规则自动生成任务
- 支持手动分配特殊任务
- 生成唯一考核码

### 5. 评分管理
- 在线评分界面
- 权重自动计算
- 评价意见记录

### 6. 数据导出
- Excel格式考核码导出
- 考核结果统计导出
- 支持打印分发

## 🏗️ 系统架构

### 技术栈
- **前端**: Vue.js 3 + TypeScript + Element Plus
- **后端**: Django + Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **构建工具**: Vite

### 系统交互
```
组织架构系统 (3002) ←→ 绩效考核系统 (3001)
        ↓                    ↓
    员工/部门数据        考核任务/评分
        ↓                    ↓
    共享数据库 (PostgreSQL)
```

## 📊 数据流程

### 考核流程
1. **系统准备** - 组织架构设置，员工信息录入
2. **规则配置** - 设置考核规则和职级权重
3. **周期创建** - 创建考核周期，关联规则和指标
4. **任务生成** - 系统自动生成考核任务
5. **执行考核** - 评价人进行评分
6. **结果统计** - 系统计算加权评分，生成结果

### 权重应用
```python
# 权重自动计算示例
evaluator_weight = 1.8  # 董事长权重
original_score = 80    # 原始评分
weighted_score = 80 * 1.8 = 144  # 加权评分
```

## 🔧 开发指南

### 项目结构
```
performance-system/
├── backend/                 # Django后端
│   ├── evaluations/         # 考核应用
│   ├── performance_system/  # 项目配置
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
│   └── package.json       # Node依赖
└── docs/                  # 文档目录
```

### 开发命令
```bash
# 后端开发
cd backend
python manage.py runserver 8001
python manage.py migrate
python manage.py createsuperuser

# 前端开发
cd frontend
npm run dev
npm run build
npm run test
```

## 🚀 部署指南

### 开发环境
- 本地开发，使用SQLite数据库
- 前后端分离，独立启动

### 生产环境
- Docker容器化部署
- Nginx反向代理
- PostgreSQL数据库
- SSL证书配置

详细部署说明请参考 [部署指南](DEPLOYMENT_GUIDE.md)

## 📈 功能特性

### 用户界面
- 响应式设计，支持移动端
- 现代化UI，基于Element Plus
- 直观的操作流程

### 数据管理
- 完整的CRUD操作
- 数据验证和错误处理
- 批量操作支持

### 系统集成
- 与组织架构系统无缝集成
- 实时数据同步
- API接口标准化

### 扩展性
- 模块化设计
- 插件化架构
- 易于定制和扩展

## 🔒 安全特性

### 数据安全
- 输入验证和过滤
- SQL注入防护
- XSS攻击防护

### 访问控制
- 基于角色的权限管理
- 会话安全管理
- API访问控制

## 📞 技术支持

### 联系方式
- **技术支持**: support@example.com
- **用户手册**: [使用说明文档](PERFORMANCE_SYSTEM_USER_GUIDE.md)
- **API文档**: [API接口文档](API_DOCUMENTATION.md)

### 问题反馈
- 提交GitHub Issue
- 查看项目文档
- 联系技术支持

## 📝 更新日志

### v1.0.0 (2025-09-27)
- 初始版本发布
- 完整的考核流程管理
- 职级权重配置功能
- 数据导出功能

### 计划功能
- 移动端支持
- 高级报表功能
- 工作流引擎
- 消息通知系统

## 📄 许可证

本项目采用MIT许可证，详情请查看LICENSE文件。

---

*最后更新: 2025年9月27日*