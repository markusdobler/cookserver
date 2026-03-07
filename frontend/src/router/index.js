import { createRouter, createWebHistory } from 'vue-router'
import ImportView from '../views/ImportView.vue'

const routes = [
  {
    path: '/',
    name: 'import',
    component: ImportView
  }
  // Future routes can be added here:
  // { path: '/manual', name: 'manual', component: ManualView },
  // { path: '/files', name: 'files', component: FilesView },
  // { path: '/content/:id', name: 'content', component: ContentView }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_PATH || '/'),
  routes
})

export default router
