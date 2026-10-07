<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { api } from '../api.js'
import QuestionCard from '../components/QuestionCard.vue'

const qtypes = ref([])
const textbooks = ref([])
const units = ref([])
const kps = ref([])
const items = ref([])
const total = ref(0)
const err = ref('')
const loading = ref(false)

const f = reactive({
  textbook_id: '', unit_id: '', q_type: '', difficulty: '', kp: '',
  scope_status: '', status: '', q: '', page: 1,
})
const PAGE_SIZE = 20

async function loadRefs() {
  qtypes.value = await api.get('/api/qtypes')
  textbooks.value = await api.get('/api/books/textbooks')
}
async function loadUnits() {
  units.value = []; kps.value = []
  if (!f.textbook_id) return
  const detail = await api.get(`/api/books/${f.textbook_id}`)
  units.value = detail.units
  kps.value = (await api.get(`/api/questions/knowledge-points?textbook_id=${f.textbook_id}`))
    .map(k => ({ ...k, label: `${k.unit_seq}·${k.name}` }))
}
async function load() {
  loading.value = true; err.value = ''
  try {
    const p = new URLSearchParams()
    for (const [k, v] of Object.entries(f)) if (v !== '' && v != null) p.set(k, v)
    p.set('page_size', PAGE_SIZE)
    const data = await api.get(`/api/questions?${p}`)
    items.value = data.items; total.value = data.total
  } catch (e) { err.value = e.message }
  loading.value = false
}

watch(() => f.textbook_id, loadUnits)
onMounted(async () => { await loadRefs(); await load() })
</script>

<template>
  <h2>题库</h2>
  <div class="card">
    <div class="grid cols3">
      <label class="f"><span>教材纲（课本）</span>
        <select v-model="f.textbook_id">
          <option value="">全部</option>
          <option v-for="b in textbooks" :key="b.id" :value="b.id">{{ b.title }}</option>
        </select>
      </label>
      <label class="f"><span>单元</span>
        <select v-model="f.unit_id">
          <option value="">全部</option>
          <option v-for="u in units" :key="u.id" :value="u.id">{{ u.seq }}. {{ u.name }}</option>
        </select>
      </label>
      <label class="f"><span>知识点</span>
        <select v-model="f.kp">
          <option value="">全部</option>
          <option v-for="k in kps" :key="k.name + k.unit_id" :value="k.name">{{ k.label }}</option>
        </select>
      </label>
      <label class="f"><span>题型</span>
        <select v-model="f.q_type"><option value="">全部</option><option v-for="t in qtypes" :key="t" :value="t">{{ t }}</option></select>
      </label>
      <label class="f"><span>难度</span>
        <select v-model="f.difficulty"><option value="">全部</option><option :value="1">基础</option><option :value="2">中等</option><option :value="3">提优</option></select>
      </label>
      <label class="f"><span>状态 / 范围</span>
        <div class="btnrow">
          <select v-model="f.status" style="flex:1">
            <option value="">状态：全部</option><option value="confirmed">已确认</option>
            <option value="draft">待审核</option><option value="rejected">已驳回</option>
          </select>
          <select v-model="f.scope_status" style="flex:1">
            <option value="">范围：全部</option><option value="ok">范围内</option>
            <option value="extension">提优拓展</option><option value="suspect">疑似超纲</option>
          </select>
        </div>
      </label>
    </div>
    <label class="f"><span>搜索题干 / 答案</span><input v-model="f.q" placeholder="如：分与合、tǔ、进位" @keyup.enter="f.page = 1; load()" /></label>
    <div class="btnrow">
      <button class="primary" @click="f.page = 1; load()">查询</button>
      <button @click="Object.assign(f, { textbook_id: '', unit_id: '', q_type: '', difficulty: '', kp: '', scope_status: '', status: '', q: '', page: 1 }); loadUnits()">重置</button>
      <span class="muted">共 {{ total }} 题</span>
    </div>
  </div>

  <div v-if="err" class="errbox">{{ err }}</div>
  <div v-if="loading" class="muted">加载中…</div>
  <template v-for="q in items" :key="q.id">
    <QuestionCard :q="q" :qtypes="qtypes" @changed="load" />
  </template>
  <div class="btnrow" v-if="total > PAGE_SIZE">
    <button :disabled="f.page <= 1" @click="f.page--; load()">上一页</button>
    <span class="muted">第 {{ f.page }} 页 / 共 {{ Math.ceil(total / PAGE_SIZE) }} 页</span>
    <button :disabled="f.page >= Math.ceil(total / PAGE_SIZE)" @click="f.page++; load()">下一页</button>
  </div>
</template>
