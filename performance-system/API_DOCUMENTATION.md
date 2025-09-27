# 绩效考核系统 API 接口文档

## 📋 目录

1. [基础信息](#基础信息)
2. [认证方式](#认证方式)
3. [考核周期 API](#考核周期-api)
4. [考核任务 API](#考核任务-api)
5. [评分管理 API](#评分管理-api)
6. [职级权重 API](#职级权重-api)
7. [手动分配 API](#手动分配-api)
8. [数据导出 API](#数据导出-api)
9. [错误处理](#错误处理)

---

## 🔧 基础信息

### 基础URL
- **绩效考核系统**: `http://localhost:8001/api/`
- **组织架构系统**: `http://localhost:8000/api/`

### 请求格式
- **Content-Type**: `application/json`
- **Accept**: `application/json`

### 响应格式
```json
{
  "count": 100,
  "next": "http://api.example.com/items/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 🔐 认证方式

### Session认证
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

### 响应
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

---

## 📅 考核周期 API

### 获取考核周期列表
```http
GET /api/cycles/
```

#### 查询参数
- `page` - 页码 (默认: 1)
- `page_size` - 每页数量 (默认: 20)
- `search` - 搜索关键词
- `status` - 状态筛选
- `ordering` - 排序字段

#### 响应示例
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "2025年第一季度考核",
      "description": "第一季度绩效考核",
      "start_date": "2025-01-01",
      "end_date": "2025-03-31",
      "status": "active",
      "evaluation_rule_name": "全公司上级评下级",
      "evaluation_indicators": [
        {
          "id": 1,
          "name": "工作业绩",
          "weight": 40
        }
      ],
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 创建考核周期
```http
POST /api/cycles/
Content-Type: application/json

{
  "name": "2025年第一季度考核",
  "description": "第一季度绩效考核",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "evaluation_rule": 1,
  "evaluation_indicators": [1, 2, 3]
}
```

### 获取考核周期详情
```http
GET /api/cycles/{id}/
```

### 更新考核周期
```http
PUT /api/cycles/{id}/
Content-Type: application/json

{
  "name": "2025年第一季度考核（更新）",
  "status": "completed"
}
```

### 删除考核周期
```http
DELETE /api/cycles/{id}/
```

### 生成考核任务
```http
POST /api/cycles/{id}/generate_tasks/
```

#### 响应示例
```json
{
  "message": "成功生成 17 个考核任务",
  "tasks_count": 17,
  "tasks": [
    {
      "id": 1,
      "evaluator": "曹操",
      "evaluatee": "刘备",
      "evaluation_code": "ABC123"
    }
  ]
}
```

---

## 📋 考核任务 API

### 获取考核任务列表
```http
GET /api/tasks/
```

#### 查询参数
- `cycle` - 考核周期ID
- `evaluator` - 评价人ID
- `evaluatee` - 被评价人ID
- `status` - 任务状态
- `page` - 页码
- `page_size` - 每页数量

#### 响应示例
```json
{
  "count": 17,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "cycle": {
        "id": 1,
        "name": "2025年第一季度考核"
      },
      "evaluator": {
        "id": 1,
        "name": "曹操",
        "position": "董事长"
      },
      "evaluatee": {
        "id": 2,
        "name": "刘备",
        "position": "总经理"
      },
      "status": "pending",
      "evaluation_code": "ABC123",
      "created_at": "2025-01-01T00:00:00Z",
      "assigned_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 根据考核码获取任务
```http
GET /api/tasks/by-code/{code}/
```

#### 响应示例
```json
{
  "id": 1,
  "cycle": {
    "id": 1,
    "name": "2025年第一季度考核"
  },
  "evaluator": {
    "id": 1,
    "name": "曹操",
    "position": "董事长"
  },
  "evaluatee": {
    "id": 2,
    "name": "刘备",
    "position": "总经理"
  },
  "indicators": [
    {
      "id": 1,
      "name": "工作业绩",
      "description": "工作成果和业绩表现",
      "weight": 40
    }
  ],
  "status": "pending"
}
```

### 提交任务评分
```http
POST /api/tasks/{id}/submit_scores/
Content-Type: application/json

{
  "scores": [
    {
      "indicator_id": 1,
      "score": 85,
      "comment": "工作表现优秀"
    },
    {
      "indicator_id": 2,
      "score": 90,
      "comment": "能力突出"
    }
  ]
}
```

#### 响应示例
```json
{
  "message": "评分提交成功",
  "scores_count": 2,
  "evaluator_weight": 1.8,
  "weighted_scores": [
    {
      "indicator_id": 1,
      "score": 85,
      "weighted_score": 153.0
    }
  ]
}
```

---

## 📊 评分管理 API

### 获取评分记录
```http
GET /api/scores/
```

#### 查询参数
- `task` - 任务ID
- `evaluator` - 评价人ID
- `evaluatee` - 被评价人ID

### 创建评分记录
```http
POST /api/scores/
Content-Type: application/json

{
  "task": 1,
  "indicator": 1,
  "score": 85,
  "comment": "工作表现优秀"
}
```

### 更新评分记录
```http
PUT /api/scores/{id}/
Content-Type: application/json

{
  "score": 90,
  "comment": "工作表现非常优秀"
}
```

### 删除评分记录
```http
DELETE /api/scores/{id}/
```

---

## ⚖️ 职级权重 API

### 获取权重配置列表
```http
GET /api/position-weights/
```

#### 响应示例
```json
{
  "count": 9,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "position_id": 1,
      "position_name": "董事长",
      "position_level": 13,
      "weight": 1.80,
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### 创建权重配置
```http
POST /api/position-weights/
Content-Type: application/json

{
  "position_id": 1,
  "position_name": "董事长",
  "position_level": 13,
  "weight": 1.80,
  "is_active": true
}
```

### 更新权重配置
```http
PUT /api/position-weights/{id}/
Content-Type: application/json

{
  "weight": 1.90,
  "is_active": true
}
```

### 批量更新权重
```http
POST /api/position-weights/bulk-update/
Content-Type: application/json

{
  "weights": [
    {
      "position_id": 1,
      "position_name": "董事长",
      "position_level": 13,
      "weight": 1.80,
      "is_active": true
    },
    {
      "position_id": 2,
      "position_name": "总经理",
      "position_level": 13,
      "weight": 1.80,
      "is_active": true
    }
  ]
}
```

#### 响应示例
```json
{
  "message": "成功更新 2 个职级权重",
  "updated_count": 2
}
```

### 获取默认权重配置
```http
GET /api/position-weights/default-weights/
```

#### 响应示例
```json
{
  "positions": [
    {
      "position_id": 1,
      "position_name": "董事长",
      "position_level": 13,
      "suggested_weight": 1.80,
      "current_weight": null
    }
  ],
  "total_positions": 9
}
```

---

## 👥 手动分配 API

### 获取手动分配列表
```http
GET /api/manual-assignments/
```

#### 查询参数
- `cycle` - 考核周期ID
- `evaluator` - 评价人ID
- `evaluatee` - 被评价人ID

### 创建手动分配
```http
POST /api/manual-assignments/
Content-Type: application/json

{
  "cycle": 1,
  "evaluator": 1,
  "evaluatee": 2,
  "reason": "特殊考核需求"
}
```

### 更新手动分配
```http
PUT /api/manual-assignments/{id}/
Content-Type: application/json

{
  "reason": "更新后的考核需求"
}
```

### 删除手动分配
```http
DELETE /api/manual-assignments/{id}/
```

### 生成手动分配任务
```http
POST /api/manual-assignments/{id}/generate_task/
```

---

## 📤 数据导出 API

### 导出考核码Excel
```http
GET /api/cycles/{id}/export-codes/
```

#### 响应
- **Content-Type**: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Content-Disposition**: `attachment; filename="evaluation_codes.xlsx"`

### 导出考核结果Excel
```http
GET /api/cycles/{id}/export-results/
```

#### 查询参数
- `format` - 导出格式 (excel, csv)
- `include_comments` - 是否包含评价意见

---

## ❌ 错误处理

### 错误响应格式
```json
{
  "error": "错误描述",
  "code": "ERROR_CODE",
  "details": {
    "field": "具体错误信息"
  }
}
```

### 常见错误码

#### 400 Bad Request
```json
{
  "error": "请求参数错误",
  "code": "INVALID_PARAMETERS",
  "details": {
    "name": "名称不能为空"
  }
}
```

#### 404 Not Found
```json
{
  "error": "资源不存在",
  "code": "NOT_FOUND",
  "details": {
    "resource": "考核周期不存在"
  }
}
```

#### 500 Internal Server Error
```json
{
  "error": "服务器内部错误",
  "code": "INTERNAL_ERROR",
  "details": {
    "message": "数据库连接失败"
  }
}
```

### 业务错误码

#### 考核任务相关
- `TASK_NOT_FOUND` - 考核任务不存在
- `TASK_ALREADY_COMPLETED` - 任务已完成
- `INVALID_EVALUATION_CODE` - 考核码无效
- `TASK_GENERATION_FAILED` - 任务生成失败

#### 权重配置相关
- `WEIGHT_CONFIG_NOT_FOUND` - 权重配置不存在
- `INVALID_WEIGHT_VALUE` - 权重值无效
- `POSITION_NOT_FOUND` - 职位不存在

#### 评分相关
- `SCORE_OUT_OF_RANGE` - 评分超出范围
- `INDICATOR_NOT_FOUND` - 指标不存在
- `SCORE_ALREADY_SUBMITTED` - 评分已提交

---

## 🔍 搜索和过滤

### 通用查询参数
- `search` - 全文搜索
- `ordering` - 排序字段
- `page` - 页码
- `page_size` - 每页数量

### 排序示例
```http
GET /api/cycles/?ordering=-created_at
GET /api/tasks/?ordering=evaluator__name
```

### 搜索示例
```http
GET /api/cycles/?search=第一季度
GET /api/tasks/?search=曹操
```

---

## 📝 使用示例

### 完整考核流程API调用

#### 1. 创建考核周期
```bash
curl -X POST http://localhost:8001/api/cycles/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2025年第一季度考核",
    "description": "第一季度绩效考核",
    "start_date": "2025-01-01",
    "end_date": "2025-03-31",
    "evaluation_rule": 1,
    "evaluation_indicators": [1, 2, 3]
  }'
```

#### 2. 生成考核任务
```bash
curl -X POST http://localhost:8001/api/cycles/1/generate_tasks/
```

#### 3. 获取考核任务
```bash
curl -X GET "http://localhost:8001/api/tasks/?cycle=1"
```

#### 4. 提交评分
```bash
curl -X POST http://localhost:8001/api/tasks/1/submit_scores/ \
  -H "Content-Type: application/json" \
  -d '{
    "scores": [
      {
        "indicator_id": 1,
        "score": 85,
        "comment": "工作表现优秀"
      }
    ]
  }'
```

#### 5. 导出考核码
```bash
curl -X GET http://localhost:8001/api/cycles/1/export-codes/ \
  -o evaluation_codes.xlsx
```

---

## 🔧 开发工具

### API测试工具
- **Postman** - 图形化API测试
- **curl** - 命令行API测试
- **HTTPie** - 友好的命令行HTTP客户端

### API文档工具
- **Django REST Framework** - 自动生成API文档
- **Swagger UI** - 交互式API文档
- **ReDoc** - 美观的API文档

### 监控和调试
- **Django Debug Toolbar** - 开发环境调试
- **Django Logging** - 日志记录
- **Performance Monitoring** - 性能监控

---

*API文档版本: v1.0.0*  
*最后更新: 2025年9月27日*
