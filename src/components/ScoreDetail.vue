<template>
  <div class="score-detail">
    <h4>📊 详细评估</h4>
    <div v-for="dim in dimensions" :key="dim.key" class="score-detail-item">
      <div class="sd-header">
        <span class="sd-label">{{ dim.label }}</span>
        <span class="sd-score">{{ '★'.repeat(scores[dim.key]?.score || 0) }}{{ '☆'.repeat(5 - (scores[dim.key]?.score || 0)) }}</span>
      </div>
      <p class="sd-reason">{{ scores[dim.key]?.reason || '暂无分析' }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  scores: { type: Object, default: () => ({}) }
})

const dimensions = [
  { key: 'video_suitability', label: '🎬 视频化程度' },
  { key: 'beginner_friendly', label: '🌱 小白友好度' },
  { key: 'popularity', label: '🔥 热度' }
]
</script>

<style scoped>
.score-detail { margin-bottom: 20px; }
.score-detail h4 { margin: 0 0 12px 0; font-size: 15px; }
.score-detail-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 8px;
}
.sd-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.sd-label { font-weight: 600; font-size: 14px; }
.sd-score { color: #f5a623; font-size: 14px; }
.sd-reason { margin: 0; font-size: 13px; color: #666; line-height: 1.6; }
</style>
