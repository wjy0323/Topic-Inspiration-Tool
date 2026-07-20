<template>
  <div class="date-picker">
    <button class="dp-arrow" :disabled="!hasPrev" @click="goPrev">&#8249;</button>
    <input
      type="date"
      :value="modelValue"
      :max="todayStr"
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

function formatDate(str) {
  const d = new Date(str + 'T00:00:00')
  if (isNaN(d.getTime())) return str
  return d.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })
}

function onDateChange(e) {
  emit('update:modelValue', e.target.value)
}

function shift(days) {
  const d = new Date(props.modelValue + 'T00:00:00')
  if (isNaN(d.getTime())) return
  d.setDate(d.getDate() + days)
  emit('update:modelValue', d.toISOString().slice(0, 10))
}

const hasPrev = computed(() => true)
const hasNext = computed(() => props.modelValue < todayStr.value)

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
