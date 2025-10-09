<template>
  <div id="app">
    <!-- 无布局页面（如登录页）直接显示 -->
    <router-view v-if="isNoLayout" />
    
    <!-- 有布局的页面使用布局组件 -->
    <component v-else :is="currentLayout">
      <router-view v-if="isTopNav" />
    </component>
  </div>
  
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Layout from './components/Layout.vue'
import TopNavLayout from './layouts/TopNavLayout.vue'

const route = useRoute()
const isNoLayout = computed(() => route.meta && (route.meta as any).layout === 'none')
const isTopNav = computed(() => route.meta && (route.meta as any).layout === 'topnav')
const currentLayout = computed(() => isTopNav.value ? TopNavLayout : Layout)
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  overflow: hidden;
}

/* 全局样式优化 */
.el-card {
  border-radius: 16px;
  border: 1px solid var(--border-light);
  background: var(--bg-primary);
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-medium);
}

.el-button {
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.el-input__wrapper {
  border-radius: 10px;
  border: 1px solid var(--border-medium);
  transition: all 0.3s ease;
}

.el-input__wrapper:hover {
  border-color: var(--border-focus);
}

.el-input__wrapper.is-focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.el-table {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-light);
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>