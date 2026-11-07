<template>
  <span :class="['suggestion-tag', tagClass]">{{ suggestion }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  suggestion: { type: String, required: true }
})

const tagClass = computed(() => {
  if (['强力推荐', '优先研究'].includes(props.suggestion)) return 'tag-recommend'
  if (['可以做', '值得参考'].includes(props.suggestion)) return 'tag-ok'
  if (['信息不足', '生成失败'].includes(props.suggestion)) return 'tag-unknown'
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
.tag-unknown { background: #f0f0f0; color: #666; }
</style>
