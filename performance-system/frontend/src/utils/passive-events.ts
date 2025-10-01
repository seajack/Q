/**
 * 修复被动事件监听器警告
 * 为滚动阻塞事件添加passive选项
 */

export function addPassiveEventListeners() {
  // 为所有滚动相关事件添加passive选项
  const passiveEvents = [
    'touchstart',
    'touchmove', 
    'touchend',
    'wheel',
    'mousewheel'
  ]

  // 重写addEventListener方法
  const originalAddEventListener = EventTarget.prototype.addEventListener
  
  EventTarget.prototype.addEventListener = function(
    type: string,
    listener: EventListenerOrEventListenerObject,
    options?: boolean | AddEventListenerOptions
  ) {
    // 如果是滚动相关事件且没有指定passive选项，则添加passive: true
    if (passiveEvents.includes(type)) {
      if (typeof options === 'boolean') {
        options = { capture: options, passive: true }
      } else if (typeof options === 'object') {
        options = { ...options, passive: true }
      } else {
        options = { passive: true }
      }
    }
    
    return originalAddEventListener.call(this, type, listener, options)
  }
}

// 在应用启动时调用
export function initPassiveEvents() {
  if (typeof window !== 'undefined') {
    addPassiveEventListeners()
  }
}
