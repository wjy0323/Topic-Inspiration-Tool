<template>
  <div class="data-export">
    <h3><Database :size="18" /> 数据管理</h3>
    <div class="export-options">
      <label><input type="radio" v-model="scope" value="all" /> 全部数据</label>
      <label><input type="radio" v-model="scope" value="bookmarks" /> 仅收藏</label>
      <label><input type="radio" v-model="scope" value="notes" /> 仅笔记</label>
    </div>
    <div class="export-actions">
      <button class="btn-export" @click="doExport"><Download :size="15" /> 导出 JSON</button>
      <button class="btn-clear" @click="confirmClear"><Trash2 :size="15" /> 清空数据</button>
    </div>
    <p v-if="clearConfirm" class="clear-confirm">
      <AlertTriangle :size="14" /> 确定要清空所有本地数据吗？此操作不可撤销。
      <span class="clear-actions">
        <button @click="doClear">确认清空</button>
        <button @click="clearConfirm = false">取消</button>
      </span>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Database, Download, Trash2, AlertTriangle } from '@lucide/vue'
import { useBookmarks } from '../composables/useBookmarks.js'
import { useNotes } from '../composables/useNotes.js'

const { bookmarkList } = useBookmarks()
const { notesList } = useNotes()

const scope = ref('all')
const clearConfirm = ref(false)

function doExport() {
  const data = {}
  if (scope.value === 'all' || scope.value === 'bookmarks') {
    data.bookmarks = bookmarkList.value
  }
  if (scope.value === 'all' || scope.value === 'notes') {
    data.notes = notesList.value.reduce((acc, n) => {
      acc[n.id] = n.text
      return acc
    }, {})
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `qiuzhi-export-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function confirmClear() {
  clearConfirm.value = true
}

function doClear() {
  localStorage.clear()
  clearConfirm.value = false
  window.location.reload()
}
</script>

<style scoped>
.data-export h3 { margin: 0 0 12px 0; font-size: 16px; display: flex; align-items: center; gap: 6px; }
.export-options { display: flex; gap: 16px; margin-bottom: 16px; font-size: 14px; }
.export-options label { cursor: pointer; display: flex; align-items: center; gap: 4px; }
.export-actions { display: flex; gap: 8px; }
.btn-export, .btn-clear {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-export { background: #1a1a2e; color: #fff; }
.btn-export:hover { opacity: 0.9; }
.btn-clear { background: #fff; color: #c62828; border: 1px solid #c62828; }
.btn-clear:hover { background: #fff5f5; }
.clear-confirm {
  font-size: 13px;
  color: #c62828;
  margin-top: 12px;
  line-height: 2;
}
.clear-actions { margin-left: 8px; }
.clear-actions button {
  margin-left: 6px;
  padding: 4px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  background: #fff;
  font-size: 12px;
}
.clear-actions button:first-child { background: #c62828; color: #fff; border-color: #c62828; }
</style>
