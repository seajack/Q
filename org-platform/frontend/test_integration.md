# 前端集成测试步骤

## 1. 启动前端开发服务器

```bash
cd e:\code\Q\org-platform\frontend
npm run dev
```

## 2. 添加路由配置

在 `src/router/index.ts` 中添加：

```typescript
{
  path: '/intelligence',
  name: 'IntelligentAnalysis',
  component: () => import('@/views/IntelligentAnalysis.vue'),
  meta: { title: '智能分析', requiresAuth: true }
}
```

## 3. 添加导航菜单

在主导航中添加智能分析入口：

```vue
<el-menu-item index="/intelligence">
  <el-icon><BrainCircuit /></el-icon>
  <span>智能分析</span>
</el-menu-item>
```

## 4. 测试功能点

### 4.1 界面加载测试
- [ ] 页面正常加载
- [ ] 概览卡片显示
- [ ] 分析结果展示
- [ ] 建议列表显示

### 4.2 交互功能测试
- [ ] 刷新分析按钮
- [ ] 导出报告按钮
- [ ] 视图切换功能
- [ ] 建议详情查看

### 4.3 数据获取测试
- [ ] API调用成功
- [ ] 数据正确显示
- [ ] 错误处理正常
- [ ] 加载状态显示

## 5. 响应式测试

### 5.1 桌面端测试
- [ ] 1920x1080 分辨率
- [ ] 1366x768 分辨率
- [ ] 布局正常显示

### 5.2 移动端测试
- [ ] 手机竖屏 (375x667)
- [ ] 手机横屏 (667x375)
- [ ] 平板 (768x1024)

## 6. 浏览器兼容性测试

- [ ] Chrome (最新版)
- [ ] Firefox (最新版)
- [ ] Edge (最新版)
- [ ] Safari (如果是Mac)

## 7. 性能测试

### 7.1 加载性能
- [ ] 首次加载时间 < 3秒
- [ ] 数据刷新时间 < 2秒
- [ ] 页面切换流畅

### 7.2 内存使用
- [ ] 内存使用合理
- [ ] 无内存泄漏
- [ ] 长时间使用稳定

## 8. 错误处理测试

### 8.1 网络错误
- [ ] 断网情况处理
- [ ] 超时情况处理
- [ ] 服务器错误处理

### 8.2 数据错误
- [ ] 空数据处理
- [ ] 异常数据处理
- [ ] 格式错误处理
