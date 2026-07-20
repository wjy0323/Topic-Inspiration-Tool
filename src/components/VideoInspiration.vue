<template>
  <div class="video-inspiration">
    <h4>🎥 视频创作灵感</h4>
    <div class="vi-card">
      <div class="vi-field">
        <span class="vi-label">标题灵感</span>
        <span class="vi-value vi-title">{{ inspiration?.title_idea || '—' }}</span>
      </div>
      <div class="vi-field">
        <span class="vi-label">切入角度</span>
        <span class="vi-value">{{ inspiration?.angle || '—' }}</span>
      </div>
      <div class="vi-field">
        <span class="vi-label">拍摄建议</span>
        <span class="vi-value">{{ inspiration?.shooting_tips || '—' }}</span>
      </div>
      <div class="vi-field">
        <span class="vi-label">目标观众</span>
        <span class="vi-value">{{ inspiration?.target_audience || '—' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  inspiration: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.video-inspiration { margin-bottom: 20px; }
.video-inspiration h4 { margin: 0 0 12px 0; font-size: 15px; }
.vi-card {
  background: linear-gradient(135deg, #f0f4ff, #faf5ff);
  border: 1px solid #e0d8f0;
  border-radius: 10px;
  padding: 16px;
}
.vi-field { margin-bottom: 10px; }
.vi-field:last-child { margin-bottom: 0; }
.vi-label {
  display: block;
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.vi-value { font-size: 14px; color: #333; line-height: 1.5; }
.vi-title { font-size: 16px; font-weight: 700; color: #1a1a2e; }
</style>
