<template>
  <button
    :class="['bookmark-btn', { bookmarked }]"
    :title="bookmarked ? '取消收藏' : '收藏'"
    @click.stop="$emit('toggle')"
  >
    <Star :size="20" :fill="bookmarked ? '#f5a623' : 'none'" />
  </button>
</template>

<script setup>
import { Star } from '@lucide/vue'
defineProps({
  bookmarked: { type: Boolean, default: false },
  productId: { type: String, default: '' }
})
defineEmits(['toggle'])
</script>

<style scoped>
.bookmark-btn {
  background: none;
  border: none;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 4px;
  color: #ccc;
}
.bookmark-btn:hover {
  transform: scale(1.15);
}
.bookmark-btn.bookmarked {
  color: #f5a623;
}
</style>
