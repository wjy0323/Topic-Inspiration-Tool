<template>
  <article class="product-card" @click="$emit('click')">
    <div class="card-rank">{{ rank }}</div>
    <div class="card-image">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" loading="lazy" />
      <div v-else class="card-image-placeholder"><Image :size="48" /></div>
    </div>
    <div class="card-body">
      <div class="card-title">
        <span class="card-name-en">{{ product.name }}</span>
        <span class="card-sep">·</span>
        <span class="card-name">{{ product.name_zh || product.name }}</span>
      </div>
      <div v-if="product.intro_zh" class="card-highlight">
        <span class="highlight-label"><ScrollText :size="13" /> 产品简介</span>
        <p class="highlight-text">{{ product.intro_zh }}</p>
      </div>
      <div class="card-scores">
        <ScoreBar label="视频化" :icon="Video" :score="product.scores?.video_suitability?.score || 0" compact />
        <ScoreBar label="小白友好" :icon="Sprout" :score="product.scores?.beginner_friendly?.score || 0" compact />
        <ScoreBar label="热度" :icon="Flame" :score="product.scores?.popularity?.score || 0" compact />
      </div>
      <div class="card-bottom">
        <div class="bottom-left">
          <BookmarkButton
            :productId="product.id"
            :bookmarked="bookmarked"
            @toggle="$emit('toggle-bookmark')"
          />
          <button class="note-btn" @click.stop="$emit('open-notes')" title="写笔记">
            <FilePen :size="14" /> 写笔记
          </button>
        </div>
        <div class="bottom-right">
          <span class="card-votes"><ThumbsUp :size="13" /> {{ product.votes_count || 0 }}</span>
          <button class="detail-btn" @click.stop="$emit('click')">完整拆解 <ArrowRight :size="14" /></button>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup>
import { ScrollText, Video, Sprout, Flame, FilePen, ThumbsUp, ArrowRight, Image } from '@lucide/vue'
import ScoreBar from './ScoreBar.vue'
import BookmarkButton from './BookmarkButton.vue'

defineProps({
  product: { type: Object, required: true },
  rank: { type: Number, required: true },
  bookmarked: { type: Boolean, default: false }
})

defineEmits(['click', 'toggle-bookmark', 'open-notes'])
</script>

<style scoped>
.product-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}
.product-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

/* ── Rank badge ── */
.card-rank {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 2;
  background: rgba(26, 26, 46, 0.78);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 0 0 10px 0;
  letter-spacing: 0.5px;
}

/* ── Image ── */
.card-image {
  width: 100%;
  height: 220px;
  background: #f5f5f5;
  flex-shrink: 0;
  overflow: hidden;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}

/* ── Body ── */
.card-body {
  padding: 14px 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

/* ── Title ── */
.card-title {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}
.card-name-en {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
}
.card-sep {
  color: #ccc;
  font-size: 16px;
}
.card-name {
  font-size: 17px;
  font-weight: 600;
  color: #333;
}

/* ── Highlight ── */
.card-highlight {
  background: linear-gradient(135deg, #fef9e7, #fef3c7);
  border-radius: 6px;
  padding: 10px 12px;
}
.highlight-label {
  font-size: 12px;
  font-weight: 700;
  color: #b45309;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}
.highlight-label:not(:first-child) {
  margin-top: 8px;
}
.highlight-text {
  margin: 0;
  font-size: 13px;
  color: #92400e;
  line-height: 1.6;
}

/* ── Scores ── */
.card-scores {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
  padding: 4px 0;
}

/* ── Bottom bar ── */
.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
.bottom-left,
.bottom-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.note-btn {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
}
.note-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}
.card-votes {
  font-size: 13px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 3px;
}
.detail-btn {
  background: #1a1a2e;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 5px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
}
.detail-btn:hover {
  background: #333;
}

/* ── Responsive ── */
@media (max-width: 640px) {
  .card-image {
    height: 180px;
  }
  .card-body {
    padding: 12px 12px 10px;
    gap: 8px;
  }
  .card-name-en {
    font-size: 16px;
  }
  .card-name {
    font-size: 15px;
  }
  .card-scores {
    gap: 10px;
  }
  .detail-btn {
    padding: 5px 10px;
    font-size: 12px;
  }
}
</style>
