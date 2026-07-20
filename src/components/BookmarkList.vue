<template>
  <div class="bookmark-list">
    <h3>⭐ 我的收藏</h3>
    <p v-if="!items.length" class="empty-hint">还没有收藏任何产品</p>
    <div v-else v-for="item in items" :key="item.id" class="bm-item">
      <div class="bm-info">
        <span class="bm-name">{{ item.name_zh || item.name || item.id }}</span>
        <span class="bm-date">{{ item.date || '' }}</span>
      </div>
      <button @click="toggleBookmark(item.id)" class="bm-remove">取消收藏</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBookmarks } from '../composables/useBookmarks.js'

const { bookmarkList, toggleBookmark } = useBookmarks()

const items = computed(() => {
  // Sort by date descending so newest bookmarks appear first
  return [...bookmarkList.value].sort((a, b) => (b.date || '').localeCompare(a.date || ''))
})
</script>

<style scoped>
.bookmark-list { margin-bottom: 32px; }
.bookmark-list h3 { margin: 0 0 12px 0; font-size: 16px; }
.empty-hint { color: #999; font-size: 14px; padding: 24px 0; text-align: center; }
.bm-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 4px;
}
.bm-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bm-name { font-size: 14px; font-weight: 500; }
.bm-date { font-size: 11px; color: #999; }
.bm-remove {
  background: none;
  border: 1px solid #fce4ec;
  color: #c62828;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 12px;
  flex-shrink: 0;
}
.bm-remove:hover { background: #fce4ec; }
</style>
