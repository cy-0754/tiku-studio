import { createRouter, createWebHashHistory } from 'vue-router'

import Dashboard from './views/Dashboard.vue'
import Questions from './views/Questions.vue'
import Compose from './views/Compose.vue'
import Papers from './views/Papers.vue'
import PaperView from './views/PaperView.vue'
import Books from './views/Books.vue'
import Review from './views/Review.vue'
import Ingest from './views/Ingest.vue'
import Settings from './views/Settings.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/questions', component: Questions },
    { path: '/compose', component: Compose },
    { path: '/papers', component: Papers },
    { path: '/papers/:id', component: PaperView, props: true },
    { path: '/books', component: Books },
    { path: '/review', component: Review },
    { path: '/ingest', component: Ingest },
    { path: '/settings', component: Settings },
  ],
})
