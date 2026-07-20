<template>
  <div class="workspace">
    <BookmarkList />
    <NotesList />
    <DataExport />
  </div>
</template>

<script setup>
import BookmarkList from './BookmarkList.vue'
import NotesList from './NotesList.vue'
import DataExport from './DataExport.vue'
</script>

<style scoped>
.workspace { max-width: 720px; margin: 0 auto; padding: 20px 16px; }
</style>
