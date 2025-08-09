import { createRouter, createWebHistory } from 'vue-router'
import MachineList from '@/components/MachineList.vue'

const routes = [
  {
    path: '/',
    name: 'MachineList',
    component: MachineList,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
