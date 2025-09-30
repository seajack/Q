# 绩效考核系统组件库

基于HTML模板重构的Vue 3组件库，提供统一的UI组件和业务组件。

## 📁 组件结构

```
src/components/
├── layout/           # 布局组件
│   ├── Sidebar.vue   # 侧边栏
│   └── Header.vue    # 顶部导航
├── ui/               # UI组件
│   ├── MetricCard.vue    # 指标卡片
│   ├── DataTable.vue     # 数据表格
│   └── StatusBadge.vue   # 状态标签
├── business/         # 业务组件
│   └── EmployeeCard.vue # 员工卡片
└── index.ts          # 组件导出
```

## 🎯 核心组件

### 布局组件

#### AppLayout
主布局组件，整合侧边栏和顶部导航。

```vue
<template>
  <AppLayout
    page-title="页面标题"
    page-subtitle="页面副标题"
    :show-search="true"
    :filters="filters"
    :actions="actions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleActionClick"
  >
    <!-- 页面内容 -->
  </AppLayout>
</template>
```

#### Sidebar
侧边栏导航组件。

```vue
<template>
  <Sidebar
    :menu-items="menuItems"
    :user-info="userInfo"
    :current-path="currentPath"
    @nav-click="handleNavClick"
  />
</template>
```

#### Header
顶部导航组件。

```vue
<template>
  <Header
    title="页面标题"
    subtitle="页面副标题"
    :show-search="true"
    :filters="filters"
    :actions="actions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
    @action-click="handleActionClick"
  />
</template>
```

### UI组件

#### MetricCard
指标卡片组件，用于显示关键数据。

```vue
<template>
  <MetricCard
    value="1,247"
    label="参与员工总数"
    icon="fas fa-users"
    icon-color="blue"
    :trend="{ type: 'up', value: '+12%', text: '较上月' }"
    :show-progress="true"
    :progress="71.5"
  />
</template>
```

#### DataTable
数据表格组件，支持分页、筛选、操作。

```vue
<template>
  <DataTable
    title="员工列表"
    :columns="tableColumns"
    :data="employees"
    :show-pagination="true"
    :current-page="currentPage"
    :page-size="pageSize"
    :total="total"
    :actions="tableActions"
    @action-click="handleTableAction"
    @page-change="handlePageChange"
  >
    <!-- 自定义列内容 -->
    <template #cell-employee="{ row }">
      <div class="flex items-center">
        <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
          <i class="fas fa-user text-blue-600"></i>
        </div>
        <div>
          <div class="font-medium text-gray-900">{{ row.name }}</div>
          <div class="text-sm text-gray-600">{{ row.email }}</div>
        </div>
      </div>
    </template>
  </DataTable>
</template>
```

#### StatusBadge
状态标签组件。

```vue
<template>
  <StatusBadge 
    label="在职" 
    type="success"
    icon="fas fa-check-circle"
    size="md"
  />
</template>
```

### 业务组件

#### EmployeeCard
员工信息卡片组件。

```vue
<template>
  <EmployeeCard
    :employee="employee"
    :actions="actions"
    @action-click="handleActionClick"
  />
</template>
```

## 🎨 设计系统

### 颜色系统
- **主色调**: 蓝色 (#2563eb)
- **成功色**: 绿色 (#10b981)
- **警告色**: 黄色 (#f59e0b)
- **危险色**: 红色 (#ef4444)
- **信息色**: 蓝色 (#3b82f6)

### 组件变体
- **MetricCard**: default, success, warning, danger, info
- **StatusBadge**: success, warning, danger, info, default
- **Button**: primary, secondary, danger

### 响应式设计
所有组件都支持响应式设计，在不同屏幕尺寸下自动调整布局。

## 📱 使用示例

### 创建仪表板页面

```vue
<template>
  <AppLayout
    page-title="绩效考核仪表板"
    page-subtitle="实时监控考核进度和数据统计"
    :actions="headerActions"
    @action-click="handleHeaderAction"
  >
    <!-- 指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <MetricCard
        value="1,247"
        label="参与员工总数"
        icon="fas fa-users"
        icon-color="blue"
        :trend="{ type: 'up', value: '+12%', text: '较上月' }"
      />
    </div>
    
    <!-- 数据表格 -->
    <DataTable
      :columns="columns"
      :data="data"
      :show-pagination="true"
      @page-change="handlePageChange"
    />
  </AppLayout>
</template>
```

### 创建员工管理页面

```vue
<template>
  <AppLayout
    page-title="员工管理"
    page-subtitle="管理员工信息和考核权限"
    :show-search="true"
    :filters="filters"
    :actions="actions"
    @search="handleSearch"
    @filter-change="handleFilterChange"
  >
    <DataTable
      :columns="tableColumns"
      :data="employees"
      :show-pagination="true"
    />
  </AppLayout>
</template>
```

## 🔧 自定义配置

### 主题定制
可以通过CSS变量自定义主题颜色：

```css
:root {
  --primary-color: #2563eb;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
}
```

### 组件配置
所有组件都支持通过props进行配置，支持TypeScript类型检查。

## 📚 最佳实践

1. **组件复用**: 优先使用现有组件，避免重复开发
2. **类型安全**: 使用TypeScript定义组件props和事件
3. **响应式设计**: 确保组件在不同屏幕尺寸下正常工作
4. **无障碍访问**: 遵循WCAG 2.1标准
5. **性能优化**: 使用Vue 3的Composition API和响应式系统

## 🚀 扩展组件

要添加新组件：

1. 在对应目录下创建组件文件
2. 在`index.ts`中导出组件
3. 更新README文档
4. 添加TypeScript类型定义

## 📝 更新日志

- **v1.0.0**: 初始版本，基于HTML模板重构
- 支持Vue 3 Composition API
- 完整的TypeScript支持
- 响应式设计
- 无障碍访问支持
