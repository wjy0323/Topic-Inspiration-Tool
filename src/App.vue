<template>
  <div>
    <NavBar currentView="home" />
    <div style="padding:20px;display:flex;gap:16px;flex-wrap:wrap;">
      <ScoreBar label="🎬 视频化" :score="4" />
      <ScoreBar label="🌱 小白友好" :score="5" />
      <ScoreBar label="🔥 热度" :score="3" />
      <SuggestionTag suggestion="强力推荐" />
      <SuggestionTag suggestion="可以做" />
      <SuggestionTag suggestion="谨慎考虑" />
      <BookmarkButton :bookmarked="false" />
      <BookmarkButton :bookmarked="true" />
    </div>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
import ScoreBar from './components/ScoreBar.vue'
import SuggestionTag from './components/SuggestionTag.vue'
import BookmarkButton from './components/BookmarkButton.vue'
</script>
