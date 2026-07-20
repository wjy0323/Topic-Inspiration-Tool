<template>
  <Teleport to="body">
    <div v-if="product" class="detail-overlay" @click.self="$emit('close')">
      <div class="detail-panel">
        <button class="detail-close" @click="$emit('close')" title="关闭">✕</button>

        <div class="detail-image">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
          <div v-else class="detail-image-placeholder">📦</div>
        </div>

        <div class="detail-content">
          <h2>{{ product.name_zh || product.name }}</h2>
          <p class="detail-name-en">{{ product.name }}</p>
          <p class="detail-desc">{{ product.description_zh }}</p>

          <div class="detail-meta">
            <span>👍 {{ product.votes_count }} 票</span>
            <a :href="product.url" target="_blank" rel="noopener">🔗 ProductHunt</a>
            <a v-if="product.website" :href="product.website" target="_blank" rel="noopener">🌐 官网</a>
            <SuggestionTag :suggestion="product.overall_suggestion || '谨慎考虑'" />
            <BookmarkButton
              :productId="product.id"
              :bookmarked="bookmarked"
              @toggle="$emit('toggle-bookmark')"
            />
          </div>

          <p class="detail-overall"><strong>综合建议：</strong>{{ product.overall_reason }}</p>

          <ScoreDetail :scores="product.scores" />
          <VideoInspiration :inspiration="product.video_inspiration" />
          <NotesEditor :productId="product.id" :productMeta="noteMeta" />
        </div>

        <div class="detail-nav">
          <button @click="$emit('prev')" :disabled="!hasPrev">‹ 上一个</button>
          <button @click="$emit('next')" :disabled="!hasNext">下一个 ›</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import ScoreDetail from './ScoreDetail.vue'
import VideoInspiration from './VideoInspiration.vue'
import NotesEditor from './NotesEditor.vue'
import SuggestionTag from './SuggestionTag.vue'
import BookmarkButton from './BookmarkButton.vue'

const props = defineProps({
  product: { type: Object, default: null },
  bookmarked: { type: Boolean, default: false },
  hasPrev: { type: Boolean, default: true },
  hasNext: { type: Boolean, default: true },
  currentDate: { type: String, default: '' }
})

defineEmits(['close', 'prev', 'next', 'toggle-bookmark'])

const noteMeta = computed(() => {
  if (!props.product) return {}
  return {
    name_zh: props.product.name_zh || '',
    name: props.product.name || '',
    date: props.currentDate
  }
})
</script>

<style scoped>
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 16px;
  overflow-y: auto;
}
.detail-panel {
  background: #fff;
  border-radius: 16px;
  max-width: 760px;
  width: 100%;
  position: relative;
  overflow: hidden;
}
.detail-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0,0,0,0.5);
  color: #fff;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  z-index: 10;
}
.detail-image {
  background: #f5f5f5;
  min-height: 200px;
}
.detail-image img {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
  display: block;
}
.detail-image-placeholder {
  width: 100%;
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
}
.detail-content { padding: 24px; }
.detail-content h2 { margin: 0; font-size: 22px; }
.detail-name-en { color: #999; font-size: 13px; margin: 4px 0 12px; }
.detail-desc { font-size: 14px; line-height: 1.7; color: #444; }
.detail-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin: 16px 0;
  font-size: 13px;
}
.detail-meta a { color: #1a73e8; text-decoration: none; }
.detail-overall {
  background: #fffde7;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}
.detail-nav {
  display: flex;
  justify-content: space-between;
  padding: 0 24px 24px;
}
.detail-nav button {
  padding: 8px 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}
.detail-nav button:hover:not(:disabled) { background: #f5f5f5; }
.detail-nav button:disabled { opacity: 0.3; cursor: default; }

@media (max-width: 640px) {
  .detail-overlay { padding: 0; }
  .detail-panel { border-radius: 0; max-width: 100%; min-height: 100vh; }
  .detail-content { padding: 16px; }
  .detail-nav { padding: 0 16px 16px; }
}
</style>
