<template>
  <span :class="['suggestion-tag', tagClass]">{{ suggestion }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  suggestion: { type: String, required: true }
})

const tagClass = computed(() => {
  if (props.suggestion === '强力推荐') return 'tag-recommend'
  if (props.suggestion === '可以做') return 'tag-ok'
  return 'tag-caution'
})
</script>

<style scoped>
.suggestion-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.tag-recommend {
  background: #e8f5e9;
  color: #2e7d32;
}
.tag-ok {
  background: #fff3e0;
  color: #e65100;
}
.tag-caution {
  background: #fce4ec;
  color: #c62828;
}
</style>
