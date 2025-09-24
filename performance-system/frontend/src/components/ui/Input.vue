<template>
  <div class="modern-form-group">
    <label v-if="label" :class="labelClasses" :for="inputId">
      {{ label }}
    </label>
    <div class="modern-form-input-wrapper">
      <input
        :id="inputId"
        :class="inputClasses"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
      />
      <div v-if="$slots.prefix || $slots.suffix" class="modern-form-input-addon">
        <slot name="prefix"></slot>
        <slot name="suffix"></slot>
      </div>
    </div>
    <div v-if="error" class="modern-form-error">
      {{ error }}
    </div>
    <div v-if="help && !error" class="modern-form-help">
      {{ help }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
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

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
  disabled: false,
  readonly: false,
  required: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
}>()

const inputId = ref(`input-${Math.random().toString(36).substr(2, 9)}`)
const isFocused = ref(false)

const labelClasses = computed(() => [
  'modern-form-label',
  {
    'modern-form-label-required': props.required
  }
])

const inputClasses = computed(() => [
  'modern-form-input',
  `modern-form-input-${props.size}`,
  {
    'modern-form-input-error': props.error,
    'modern-form-input-focused': isFocused.value
  }
])

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}
</script>

<style scoped>
.modern-form-input-wrapper {
  position: relative;
}

.modern-form-input-sm {
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--text-xs);
}

.modern-form-input-lg {
  padding: var(--spacing-4) var(--spacing-5);
  font-size: var(--text-base);
}

.modern-form-input-error {
  border-color: var(--semantic-error-500);
}

.modern-form-input-error:focus {
  border-color: var(--semantic-error-500);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.12);
}

.modern-form-input-focused {
  border-color: var(--brand-primary-500);
  box-shadow: var(--shadow-focus);
}

.modern-form-input-addon {
  position: absolute;
  right: var(--spacing-3);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  color: var(--text-tertiary);
}
</style>