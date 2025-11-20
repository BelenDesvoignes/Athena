import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { checkPortalStatus } from "../services/portalFlags.js"

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
    path: "/mantenimiento",
    name: "Mantenimiento",
    component: () => import("../views/Mantenimiento.vue")
    },
    {
    path: '/mis-resenas',
    name: 'mis-resenas',
    component: () => import('../views/ResenasView.vue')
    },
    {
      path: "/403",
      name: "403",
      component: () => import('../views/Error403.vue')
    },
    {
      path: "/500",
      name: "500",
      component: () => import('../views/Error500.vue')
    },
    // 404 (debe ir al final SIEMPRE)
    {
      path: "/:pathMatch(.*)*",
      name: "404",
      component: () => import('../views/Error404.vue')
    }

    // ... otras rutas (About, Login, etc.)
  ]
  
})


router.beforeEach(async (to, from, next) => {
  if (to.name === "Mantenimiento") {
    const status = await checkPortalStatus()

    if (!status.maintenance) {
      next({ name: "home" })
    } else {
      next()
    }
    return
  }

  const status = await checkPortalStatus()

  if (status.maintenance) {
    next({ name: "Mantenimiento" })
  } else {
    next()
  }
})

export default router
