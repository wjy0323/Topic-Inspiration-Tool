<template>
  <article class="product-card" @click="$emit('click')">
    <div class="card-rank">{{ rank }}</div>
    <div class="card-image">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" loading="lazy" />
      <div v-else class="card-image-placeholder">📦</div>
    </div>
    <div class="card-body">
      <div class="card-header">
        <h3 class="card-name">{{ product.name_zh || product.name }}</h3>
        <span class="card-name-en">{{ product.name }}</span>
      </div>
      <p class="card-tagline">{{ product.tagline_zh }}</p>
      <div class="card-scores">
        <ScoreBar label="🎬 视频化" :score="product.scores?.video_suitability?.score || 0" />
        <ScoreBar label="🌱 小白友好" :score="product.scores?.beginner_friendly?.score || 0" />
        <ScoreBar label="🔥 热度" :score="product.scores?.popularity?.score || 0" />
      </div>
      <div class="card-footer">
        <SuggestionTag :suggestion="product.overall_suggestion || '谨慎考虑'" />
        <span class="card-votes">👍 {{ product.votes_count }}</span>
        <BookmarkButton
          :productId="product.id"
          :bookmarked="bookmarked"
          @toggle="$emit('toggle-bookmark')"
        />
      </div>
    </div>
  </article>
</template>

<script setup>
import ScoreBar from './ScoreBar.vue'
import SuggestionTag from './SuggestionTag.vue'
import BookmarkButton from './BookmarkButton.vue'

defineProps({
  product: { type: Object, required: true },
  rank: { type: Number, required: true },
  bookmarked: { type: Boolean, default: false }
})

defineEmits(['click', 'toggle-bookmark'])
</script>

<style scoped>
.product-card {
  display: flex;
  gap: 16px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}
.product-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.card-rank {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a2e;
  min-width: 40px;
  text-align: center;
  align-self: center;
}
.card-image {
  width: 160px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f5f5;
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
  font-size: 32px;
}
.card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}
.card-name-en {
  font-size: 12px;
  color: #999;
}
.card-tagline {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}
.card-scores {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.card-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
}
.card-votes {
  font-size: 13px;
  color: #999;
}
@media (max-width: 640px) {
  .product-card {
    flex-direction: column;
  }
  .card-image {
    width: 100%;
    height: 180px;
  }
  .card-rank {
    position: absolute;
    background: rgba(0,0,0,0.6);
    color: #fff;
    width: 32px;
    height: 32px;
    border-radius: 8px 0 8px 0;
    font-size: 16px;
    line-height: 32px;
  }
}
</style>
