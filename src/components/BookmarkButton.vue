<template>
  <button
    :class="['bookmark-btn', { bookmarked }]"
    :title="bookmarked ? '取消收藏' : '收藏'"
    @click.stop="$emit('toggle')"
  >
    {{ bookmarked ? '⭐' : '☆' }}
  </button>
</template>

<script setup>
defineProps({
  bookmarked: { type: Boolean, default: false }
})
defineEmits(['toggle'])
</script>

<style scoped>
.bookmark-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 4px;
}
.bookmark-btn:hover {
  transform: scale(1.2);
}
.bookmark-btn.bookmarked {
  color: #f5a623;
}
</style>
