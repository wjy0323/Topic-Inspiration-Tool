<template>
  <div class="score-bar" :class="{ compact }">
    <span class="score-label">
      <component v-if="icon" :is="icon" :size="compact ? 13 : 14" class="score-icon" />
      {{ label }}
    </span>
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
  score: { type: Number, required: true },
  compact: { type: Boolean, default: false },
  icon: { type: Object, default: null }
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
  display: flex;
  align-items: center;
  gap: 4px;
  color: #888;
  min-width: 80px;
}
.score-icon {
  flex-shrink: 0;
  stroke-width: 2;
}
.compact .score-label {
  min-width: auto;
  font-size: 12px;
}
.score-stars {
  color: #f5a623;
  letter-spacing: 2px;
}
.empty {
  color: #ddd;
}
</style>
