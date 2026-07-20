<template>
  <div class="date-picker">
    <button class="dp-arrow" :disabled="!hasPrev" @click="goPrev">&#8249;</button>
    <input
      type="date"
      :value="modelValue"
      :max="todayStr" :min="minDateStr"
      @change="onDateChange"
      class="dp-input"
    />
    <button class="dp-arrow" :disabled="!hasNext" @click="goNext">&#8250;</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, required: true },
  availableDates: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const todayStr = computed(() => {
  const d = new Date()
  return d.toISOString().slice(0, 10)
})

const minDateStr = computed(() => {
  if (props.availableDates.length === 0) return undefined
  const sorted = [...props.availableDates].sort()
  return sorted[0]
})

function onDateChange(e) {
  emit('update:modelValue', e.target.value)
}

function shift(days) {
  if (props.availableDates.length > 0) {
    const sorted = [...props.availableDates].sort()
    const idx = sorted.indexOf(props.modelValue)
    if (idx === -1) {
      const candidates = sorted.filter(d => days > 0 ? d > props.modelValue : d < props.modelValue)
      if (candidates.length === 0) return
      emit('update:modelValue', days > 0 ? candidates[0] : candidates[candidates.length - 1])
    } else {
      const newIdx = idx + days
      if (newIdx < 0 || newIdx >= sorted.length) return
      emit('update:modelValue', sorted[newIdx])
    }
  } else {
    const d = new Date(props.modelValue + 'T00:00:00')
    if (isNaN(d.getTime())) return
    d.setDate(d.getDate() + days)
    emit('update:modelValue', d.toISOString().slice(0, 10))
  }
}

const hasPrev = computed(() => {
  if (props.availableDates.length === 0) return true
  return props.availableDates.some(d => d < props.modelValue)
})
const hasNext = computed(() => {
  if (props.modelValue >= todayStr.value) return false
  if (props.availableDates.length === 0) return true
  return props.availableDates.some(d => d > props.modelValue)
})

function goPrev() { shift(-1) }
function goNext() { shift(1) }
</script>

<style scoped>
.date-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dp-arrow {
  width: 32px;
  height: 32px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  font-size: 18px;
  cursor: pointer;
  color: #555;
}
.dp-arrow:disabled {
  opacity: 0.3;
  cursor: default;
}
.dp-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}
</style>
