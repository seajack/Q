// 现代化UI组件库
export { default as Button } from './Button.vue'
export { default as Card } from './Card.vue'
export { default as Input } from './Input.vue'
export { default as Badge } from './Badge.vue'
export { default as StatCard } from './StatCard.vue'
export { default as Progress } from './Progress.vue'
export { default as EmptyState } from './EmptyState.vue'

// 类型定义
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'success' | 'warning' | 'error'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  block?: boolean
  type?: 'button' | 'submit' | 'reset'
}

export interface CardProps {
  variant?: 'default' | 'elevated' | 'interactive'
  size?: 'sm' | 'md' | 'lg'
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  hover?: boolean
}

export interface InputProps {
  modelValue?: string | number
  label?: string
  placeholder?: string
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  error?: string
  help?: string
}

export interface BadgeProps {
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
}

export interface StatCardProps {
  value: number
  label: string
  description?: string
  icon?: any
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  trend?: {
    value: number
    type: 'up' | 'down' | 'neutral'
  }
  format?: 'number' | 'currency' | 'percentage'
}

export interface ProgressProps {
  percentage: number
  variant?: 'primary' | 'success' | 'warning' | 'error'
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean
  text?: string
  animated?: boolean
  striped?: boolean
}

export interface EmptyStateProps {
  title?: string
  description?: string
  icon?: 'document' | 'user' | 'calendar' | 'data' | 'folder' | string
}