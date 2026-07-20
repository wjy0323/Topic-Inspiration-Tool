<template>
  <div class="notes-list">
    <h3>📝 我的笔记</h3>
    <p v-if="!items.length" class="empty-hint">还没有写过笔记</p>
    <div v-for="item in items" :key="item.id" class="note-item" @click="toggleExpand(item.id)">
      <div class="note-info">
        <span class="note-name">{{ item.name_zh || item.name || item.id }}</span>
        <span class="note-text">{{ expandedId === item.id ? item.text : item.summary }}</span>
      </div>
      <span class="note-date">{{ item.date || '' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNotes } from '../composables/useNotes.js'

const { notesList } = useNotes()
const expandedId = ref(null)

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

const items = computed(() => {
  return [...notesList.value].sort((a, b) => (b.date || '').localeCompare(a.date || ''))
})
</script>

<style scoped>
.notes-list { margin-bottom: 32px; }
.notes-list h3 { margin: 0 0 12px 0; font-size: 16px; }
.empty-hint { color: #999; font-size: 14px; padding: 24px 0; text-align: center; }
.note-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 4px;
}
.note-item:hover { background: #fafafa; }
.note-info { display: flex; flex-direction: column; gap: 4px; min-width: 0; flex: 1; }
.note-name { font-weight: 600; font-size: 14px; }
.note-text { font-size: 13px; color: #666; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
.note-date { font-size: 11px; color: #bbb; flex-shrink: 0; }
</style>
