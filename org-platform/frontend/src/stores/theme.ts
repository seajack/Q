import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 从本地存储获取主题设置，默认为浅色主题
  const theme = ref(localStorage.getItem('org-platform-theme') || 'light')
  
  // 切换主题
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }
  
  // 设置特定主题
  function setTheme(newTheme: 'light' | 'dark') {
    theme.value = newTheme
  }
  
  // 监听主题变化，更新文档根元素的类名和本地存储
  watch(theme, (newTheme) => {
    // 更新文档根元素的类名
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark-theme')
    } else {
      document.documentElement.classList.remove('dark-theme')
    }
    
    // 保存到本地存储
    localStorage.setItem('org-platform-theme', newTheme)
  }, { immediate: true })
  
  return {
    theme,
    toggleTheme,
    setTheme,
    isDark: () => theme.value === 'dark'
  }
})