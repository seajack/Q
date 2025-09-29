<template>
  <div id="app" :class="{ 'dark-theme': themeStore.isDark() }">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from './stores/theme'
import { onMounted } from 'vue'

const themeStore = useThemeStore()

// 在组件挂载时初始化主题
onMounted(() => {
  // 主题存储中的 watch 会自动应用保存的主题
  console.log('当前主题:', themeStore.theme)
})
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
  background-color: var(--bg);
  color: var(--text);
  overflow: hidden;
  transition: background-color 0.3s, color 0.3s;
}
</style>