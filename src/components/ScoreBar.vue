<template>
  <div class="score-bar">
    <span class="score-label">{{ label }}</span>
    <span class="score-stars">
      <span v-for="i in 5" :key="i" :class="{ filled: i <= score, empty: i > score }">
        {{ i <= score ? '★' : '☆' }}
      </span>
    </span>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  score: { type: Number, required: true }
})
</script>

<style scoped>
.score-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.score-label {
  color: #888;
  min-width: 80px;
}
.score-stars {
  color: #f5a623;
  letter-spacing: 2px;
}
.empty {
  color: #ddd;
}
</style>
