# 组织架构与绩效考核管理系统

## 项目简介

本项目是一个完整的企业级组织架构与绩效考核管理系统，采用前后端分离架构，支持组织架构管理、员工管理、职位管理、绩效考核等核心功能。

## 技术栈

### 后端技术
- **框架**: Django 5.2.1 + Django REST Framework
- **数据库**: SQLite（可切换至MySQL/PostgreSQL）
- **语言**: Python 3.11+
- **API文档**: DRF自动生成

### 前端技术
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4

## 系统功能

### 组织架构中台系统
- ✅ **部门管理**：支持树形结构的部门组织架构
- ✅ **职位管理**：自定义职位级别体系，支持两维度管理
  - 管理层级：高层、中层、基层
  - 职位类型：正职、副职、助理、员工
- ✅ **员工管理**：完整的员工信息管理，支持用户账号自动创建
- ✅ **权限管理**：基于Django用户系统的权限控制

### 绩效考核系统
- ✅ **考核管理**：支持多种考核类型和周期
- ✅ **评分体系**：灵活的评分标准和权重配置
- ✅ **结果统计**：考核结果的统计分析和报表生成
- ✅ **流程管理**：完整的考核流程管控

## 项目结构

```
org-per/
├── org-platform/           # 组织架构中台系统
│   ├── backend/            # Django后端
│   │   ├── organizations/  # 组织架构应用
│   │   ├── org_platform/  # 项目配置
│   │   └── manage.py      # Django管理脚本
│   └── frontend/          # Vue前端
│       ├── src/           # 源代码
│       ├── public/        # 静态资源
│       └── package.json   # 依赖配置
├── performance-system/     # 绩效考核系统
│   ├── backend/           # Django后端
│   └── frontend/          # Vue前端
├── docs/                  # 项目文档
└── README.md             # 项目说明
```

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Git

### 后端启动

1. **克隆项目**
```bash
git clone https://gitee.com/seajack/org-per.git
cd org-per
```

2. **创建虚拟环境**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **安装依赖**
```bash
cd org-platform/backend
pip install -r requirements.txt
```

4. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **创建超级用户**
```bash
python manage.py createsuperuser
```

6. **启动后端服务**
```bash
python manage.py runserver 127.0.0.1:8001
```

### 前端启动

1. **安装依赖**
```bash
cd org-platform/frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

### 访问系统
- 前端地址：http://localhost:3000
- 后端API：http://127.0.0.1:8001/api/
- 管理后台：http://127.0.0.1:8001/admin/

## 核心特性

### 职位级别体系

本系统创新性地采用两维度职位级别管理：

**管理层级维度**：
- 高层：公司高级管理层
- 中层：部门管理层
- 基层：基础管理和员工层

**职位类型维度**：
- 高层正职(13) → 高层副职(12) → 高层助理(11)
- 中层正职(9) → 中层副职(8) → 中层助理(7)
- 基层正职(4) → 基层副职(3) → 基层助理(2) → 员工(1)

### 数据模型设计

- **部门模型**：支持无限层级的树形结构
- **职位模型**：双维度职位级别管理
- **员工模型**：完整的员工档案管理
- **用户系统**：与Django用户系统无缝集成

### API接口

所有接口遵循RESTful设计原则：
- GET /api/departments/ - 获取部门列表
- POST /api/positions/ - 创建职位
- PUT /api/employees/{id}/ - 更新员工信息
- DELETE /api/departments/{id}/ - 删除部门

## 开发指南

### 代码规范
- 后端遵循Django最佳实践
- 前端使用TypeScript严格模式
- 统一使用ESLint和Prettier代码格式化

### 测试
```bash
# 后端测试
cd org-platform/backend
python manage.py test

# 前端测试
cd org-platform/frontend
npm run test
```

### 构建部署
```bash
# 前端构建
cd org-platform/frontend
npm run build

# 后端生产环境配置
# 请修改settings.py中的生产环境配置
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目地址：https://gitee.com/seajack/org-per
- 问题反馈：通过Gitee Issues提交

## 更新日志

### v1.0.0 (2025-09-23)
- ✅ 完成组织架构中台系统基础功能
- ✅ 实现双维度职位级别管理体系
- ✅ 完成员工管理和用户账号集成
- ✅ 实现绩效考核系统框架
- ✅ 完成前后端分离架构搭建

---

**感谢使用组织架构与绩效考核管理系统！**