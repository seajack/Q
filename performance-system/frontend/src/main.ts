import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/tailwind.css'
import './styles/theme.css'
import './styles/transitions.css'
import './newui/styles/brand.css'
import { initPassiveEvents } from './utils/passive-events'

// 初始化被动事件监听器
initPassiveEvents()

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局注册Element Plus组件
app.use(ElementPlus)

app.use(createPinia())
app.use(router)

app.mount('#app')