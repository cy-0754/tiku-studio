<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api.js'

const router = useRouter()
const textbooks = ref([])
const units = ref([])
const typeStats = ref({})
const qtypes = ref([])
const err = ref('')
const busy = ref(false)

const cfg = reactive({
  textbook_id: '', unit_from: 1, unit_to: 1, title: '',
  total_score: 100, duration_minutes: 60, include_extension: false, seed: '',
  counts: {}, per_type_score: {},
})

const textbook = computed(() => textbooks.value.find(b => b.id === Number(cfg.textbook_id)))

async function loadTextbook() {
  units.value = []; typeStats.value = {}
  if (!cfg.textbook_id) return
  const detail = await api.get(`/api/books/${cfg.textbook_id}`)
  units.value = detail.units
  if (!units.value.some(u => u.seq === cfg.unit_to)) cfg.unit_to = units.value[units.value.length - 1].seq
  typeStats.value = await api.get(`/api/questions/type-stats?textbook_id=${cfg.textbook_id}`)
}

function clampRange() {
  if (Number(cfg.unit_to) < Number(cfg.unit_from)) cfg.unit_to = cfg.unit_from
}

async function generate() {
  err.value = ''; busy.value = true
  try {
    const body = {
      textbook_id: Number(cfg.textbook_id), unit_from: Number(cfg.unit_from),
      unit_to: Number(cfg.unit_to), total_score: Number(cfg.total_score),
      duration_minutes: Number(cfg.duration_minutes),
      include_extension: cfg.include_extension,
      counts: Object.fromEntries(Object.entries(cfg.counts).filter(([, n]) => Number(n) > 0)),
      per_type_score: Object.fromEntries(Object.entries(cfg.per_type_score).filter(([, n]) => Number(n) > 0)),
    }
    if (cfg.title) body.title = cfg.title
    if (cfg.seed !== '') body.seed = Number(cfg.seed)
    const paper = await api.post('/api/papers', body)
    const warn = paper.config && paper.config.shortage && paper.config.shortage.length
    router.push(`/papers/${paper.id}${warn ? '?shortage=1' : ''}`)
  } catch (e) { err.value = e.message }
  busy.value = false
}

onMounted(async () => {
  qtypes.value = await api.get('/api/qtypes')
  textbooks.value = await api.get('/api/books/textbooks')
  if (textbooks.value.length) {
    cfg.textbook_id = textbooks.value[0].id
    await loadTextbook()
  }
})
</script>

<template>
  <h2>组卷</h2>
  <div v-if="!textbooks.length" class="warnbox">
    还没有课本纲。先把一本课本（或最小目录）拆解导入，才能按『单元范围 + 不超纲』组卷。见 <a href="#/ingest">AI 拆解</a>。
  </div>
  <div class="card" v-if="textbooks.length">
    <h3>① 范围（对纲：只抽已学单元内、不超纲的题）</h3>
    <div class="grid cols3">
      <label class="f"><span>教材纲</span>
        <select v-model="cfg.textbook_id" @change="loadTextbook">
          <option v-for="b in textbooks" :key="b.id" :value="b.id">{{ b.title }}</option>
        </select>
      </label>
      <label class="f"><span>从第几单元</span>
        <select v-model="cfg.unit_from" @change="clampRange">
          <option v-for="u in units" :key="u.id" :value="u.seq">{{ u.seq }}. {{ u.name }}</option>
        </select>
      </label>
      <label class="f"><span>到第几单元（当前进度）</span>
        <select v-model="cfg.unit_to">
          <option v-for="u in units" :key="u.id" :value="u.seq">{{ u.seq }}. {{ u.name }}</option>
        </select>
      </label>
    </div>
    <label class="f" style="display:flex;align-items:center;gap:8px">
      <input type="checkbox" v-model="cfg.include_extension" style="width:auto" />
      <span style="color:var(--ink)">包含提优拓展题（实验班等略超前于进度的题）</span>
    </label>
  </div>

  <div class="card" v-if="units.length">
    <h3>② 题型配额（留空 = 不出该题型）</h3>
    <div class="grid cols4">
      <label v-for="t in qtypes" :key="t" class="f">
        <span>{{ t }}（可用 {{ typeStats[t] || 0 }} 题）</span>
        <input type="number" min="0" v-model.number="cfg.counts[t]" placeholder="0" />
      </label>
    </div>
    <details style="margin-top:6px">
      <summary>高级：自定义每题分值 / 随机种子（固定种子可复现同一张卷）</summary>
      <div class="grid cols4" style="margin-top:8px">
        <label v-for="t in qtypes" :key="'s' + t" class="f">
          <span>{{ t }} 每题分</span>
          <input type="number" step="0.5" min="0" v-model.number="cfg.per_type_score[t]" placeholder="默认" />
        </label>
      </div>
      <label class="f" style="max-width:220px"><span>随机种子</span><input type="number" v-model.number="cfg.seed" placeholder="留空随机" /></label>
    </details>
  </div>

  <div class="card" v-if="units.length">
    <h3>③ 卷面</h3>
    <div class="grid cols4">
      <label class="f"><span>卷名（留空自动生成）</span><input v-model="cfg.title" :placeholder="textbook ? `${textbook.grade}年级${textbook.subject}${textbook.semester}` : ''" /></label>
      <label class="f"><span>总分</span><input type="number" v-model.number="cfg.total_score" /></label>
      <label class="f"><span>限时（分钟）</span><input type="number" v-model.number="cfg.duration_minutes" /></label>
    </div>
    <div v-if="err" class="errbox">{{ err }}</div>
    <button class="primary" :disabled="busy || !cfg.textbook_id" @click="generate">
      {{ busy ? '生成中…' : '生成试卷 →' }}
    </button>
    <p class="muted" style="margin-bottom:0">
      默认规格：满分 {{ cfg.total_score }} 分 · 限时 {{ cfg.duration_minutes }} 分钟 · 只抽已确认题目 · 分值按题型自动配平。
    </p>
  </div>
</template>
