
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// Asegúrate de crear el componente ListadoSitios.vue

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/sitios', // Ruta para el listado (a donde navega el "Ver todos")
      name: 'listado-sitios',
      component: () => import('../views/ListadoSitios.vue')
    },
    {
      path: '/sitios/:id', // Ruta para el detalle del sitio
      name: 'detalle-sitio',
      component: () => import('../views/DetalleSitio.vue')
    },
    {
      path: '/perfil',
      name: 'perfil-usuario',
      component: () => import('../views/PerfilView.vue')
    },
    {
      path: '/mis-favoritos',
      name: 'mis-favoritos',
      component: () => import('../views/FavoritosView.vue')
    },
    {
      path: '/mis-resenas',
      name: 'mis-resenas',
      component: () => import('../views/ResenasView.vue')
    }
    // ... otras rutas (About, Login, etc.)
  ]
})

export default router