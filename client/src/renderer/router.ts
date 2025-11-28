import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('./views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/LoginView.vue'),
  },
  {
    path: '/library',
    name: 'Library',
    component: () => import('./views/LibraryView.vue'),
  },
  {
    path: '/game/:id',
    name: 'GameDetail',
    component: () => import('./views/GameDetailView.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/SettingsView.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
