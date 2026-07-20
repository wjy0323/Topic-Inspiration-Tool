<template>
  <div class="app">
    <NavBar :currentView="currentView" @update:currentView="onViewChange" />
    <main class="app-main">
      <HomePage v-if="currentView === 'home'" />
      <Workspace v-else />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import NavBar from './components/NavBar.vue'
import HomePage from './components/HomePage.vue'
import Workspace from './components/Workspace.vue'

const currentView = ref(getInitialView())

function getInitialView() {
  // Support /workspace path
  if (window.location.pathname.endsWith('/workspace')) return 'workspace'
  return 'home'
}

function onViewChange(view) {
  currentView.value = view
  if (view === 'home') {
    history.replaceState(null, '', '/')
  } else {
    history.replaceState(null, '', '/workspace')
  }
}
</script>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
}
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: #f7f7f9;
  color: #333;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.app {
  min-height: 100vh;
}
.app-main {
  min-height: calc(100vh - 57px);
}
</style>
