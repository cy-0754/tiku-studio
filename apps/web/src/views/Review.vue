<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api.js'
import QuestionCard from '../components/QuestionCard.vue'

const qtypes = ref([])
const drafts = ref([])
const suspects = ref([])
const tab = ref('draft')
const err = ref('')

async function load() {
  err.value = ''
  try {
    drafts.value = (await api.get('/api/questions?status=draft&page_size=200')).items
    suspects.value = (await api.get('/api/questions?scope_status=suspect&page_size=200')).items
  } catch (e) { err.value = e.message }
}

onMounted(async () => {
  qtypes.value = await api.get('/api/qtypes')
  await load()
})
</script>

<template>
  <h2>待审核</h2>
  <div class="warnbox">
    拆解产物一律先进入这里，<b>确认后</b>才会进入组卷池。「疑似超纲」是对纲校验判定的：知识点不在绑定课本纲内
    （可能是版本不符，也可能是教辅有意安排的提优题）。逐条处理：确认 / 标为提优 / 驳回 / 删除。
  </div>
  <div class="btnrow" style="margin-bottom:12px">
    <button :class="{ primary: tab === 'draft' }" @click="tab = 'draft'">待确认（{{ drafts.length }}）</button>
    <button :class="{ primary: tab === 'suspect' }" @click="tab = 'suspect'">疑似超纲（{{ suspects.length }}）</button>
  </div>
  <div v-if="err" class="errbox">{{ err }}</div>
  <p v-if="tab === 'draft' && !drafts.length" class="muted">没有待确认的题目。</p>
  <p v-if="tab === 'suspect' && !suspects.length" class="muted">没有疑似超纲的题目。</p>
  <template v-if="tab === 'draft'">
    <QuestionCard v-for="q in drafts" :key="q.id" :q="q" :qtypes="qtypes" @changed="load" />
  </template>
  <template v-else>
    <QuestionCard v-for="q in suspects" :key="q.id" :q="q" :qtypes="qtypes" @changed="load" />
  </template>
</template>
