<script setup>
import { ref } from 'vue'

const open = ref(false)
const navs = [
  { path: '/', label: '首页' },
  { path: '/questions', label: '题库' },
  { path: '/compose', label: '组卷' },
  { path: '/papers', label: '试卷' },
  { path: '/books', label: '资料库' },
  { path: '/review', label: '待审核' },
  { path: '/ingest', label: 'AI 拆解' },
  { path: '/settings', label: '设置' },
]
</script>

<template>
  <div class="layout">
    <aside class="sidebar" :class="{ open }" @click="open = false">
      <div class="logo">tiku-studio<small>题库 · 对纲 · 组卷</small></div>
      <nav class="nav">
        <router-link v-for="n in navs" :key="n.path" :to="n.path">{{ n.label }}</router-link>
      </nav>
    </aside>
    <div class="topbar">
      <button @click="open = !open">☰</button>
      <b>tiku-studio</b>
    </div>
    <main class="main" @click="open = false">
      <router-view />
    </main>
  </div>
</template>
