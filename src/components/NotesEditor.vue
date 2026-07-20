<template>
  <div class="notes-editor">
    <h4>📝 我的笔记</h4>
    <textarea
      :value="noteText"
      @input="onInput"
      placeholder="记录你的想法、拍摄思路、注意事项..."
      class="notes-textarea"
      rows="5"
    ></textarea>
    <span class="notes-saved">{{ saved ? '✅ 已自动保存' : '💾 正在保存...' }}</span>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useNotes } from '../composables/useNotes.js'

const props = defineProps({
  productId: { type: String, required: true },
  productMeta: { type: Object, default: () => ({}) }
})

const { getNote, saveNote } = useNotes()
const noteText = ref('')
const saved = ref(true)
let saveTimer = null

onMounted(() => {
  noteText.value = getNote(props.productId)
})

// When the product changes (prev/next navigation), reload the note
watch(() => props.productId, (newId) => {
  noteText.value = getNote(newId)
  saved.value = true
})

function onInput(e) {
  noteText.value = e.target.value
  saved.value = false
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveNote(props.productId, noteText.value, props.productMeta)
    saved.value = true
  }, 500)
}
</script>

<style scoped>
.notes-editor h4 { margin: 0 0 8px 0; font-size: 15px; }
.notes-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}
.notes-textarea:focus { outline: none; border-color: #1a1a2e; }
.notes-saved { font-size: 11px; color: #aaa; }
</style>
