/**
 * 日期时间格式化工具函数
 */

/**
 * 格式化日期时间
 * @param date 日期字符串或Date对象
 * @param format 格式化模式，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的日期字符串
 */
export function formatDateTime(date: string | Date, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期（不包含时间）
 * @param date 日期字符串或Date对象
 * @returns 格式化后的日期字符串
 */
export function formatDate(date: string | Date): string {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间（不包含日期）
 * @param date 日期字符串或Date对象
 * @returns 格式化后的时间字符串
 */
export function formatTime(date: string | Date): string {
  return formatDateTime(date, 'HH:mm:ss')
}

/**
 * 相对时间格式化（如：2小时前、3天前）
 * @param date 日期字符串或Date对象
 * @returns 相对时间字符串
 */
export function formatRelativeTime(date: string | Date): string {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)
  
  if (years > 0) return `${years}年前`
  if (months > 0) return `${months}个月前`
  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  if (seconds > 0) return `${seconds}秒前`
  
  return '刚刚'
}

/**
 * 智能时间格式化（根据时间远近选择不同格式）
 * @param date 日期字符串或Date对象
 * @returns 智能格式化后的时间字符串
 */
export function formatSmartTime(date: string | Date): string {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  // 如果是今天，显示时间
  if (days === 0) {
    return formatTime(date)
  }
  
  // 如果是昨天，显示"昨天 HH:mm"
  if (days === 1) {
    return `昨天 ${formatTime(date)}`
  }
  
  // 如果是一周内，显示"X天前"
  if (days < 7) {
    return `${days}天前`
  }
  
  // 如果是一年内，显示"MM-DD HH:mm"
  if (days < 365) {
    return formatDateTime(date, 'MM-DD HH:mm')
  }
  
  // 超过一年，显示完整日期时间
  return formatDateTime(date, 'YYYY-MM-DD HH:mm')
}
