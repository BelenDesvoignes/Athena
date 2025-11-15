<script setup>
import { RouterView, useRouter } from 'vue-router'
import { ref } from 'vue'
import { GoogleLogin } from 'vue3-google-login'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const callback = async (response) => {
  console.log("Respuesta de Google recibida. Procesando login en Pinia Store...")
  await authStore.loginWithGoogle(response)
}

const logout = () => {
  const confirmar = window.confirm("¿Estás seguro de que querés cerrar sesión?")
  if (confirmar) {
    authStore.logout()
    router.push('/')
  }
}
</script>

<template>
  <div id="app-wrapper">

    <header class="main-header">

      <div class="header-left">
        <button @click="toggleMenu" class="menu-hamburguer-btn" aria-label="Abrir Menú">
          <span class="icon-line"></span>
          <span class="icon-line"></span>
          <span class="icon-line"></span>
        </button>
        <span class="menu-label">Menú</span>
      </div>

      <div class="header-center">
        <img src="@/assets/athena-logo.png" alt="Logo de Athena" class="app-logo" @click="router.push('/')">
      </div>

      <div class="header-right">
        <div v-if="authStore.isLoggedIn" class="user-avatar-placeholder">
          <img
            :src="authStore.user.imageUrl"
            alt="Foto de perfil"
            width="40"
            height="40"
            style="border-radius: 50%; cursor: pointer;"
            @click="router.push('/profile')"
          />
        </div>
        <div v-else class="google-login-btn-wrapper">
          <GoogleLogin :callback="callback" />
        </div>
      </div>

    </header>

    <aside :class="['sidebar', { 'is-open': isMenuOpen }]">
      <button @click="toggleMenu" class="close-menu-btn">✖️</button>

      <nav class="sidebar-nav">
        <button @click="router.push('/'); toggleMenu();" class="sidebar-link">Inicio</button>
        <button @click="router.push('/sitios'); toggleMenu();" class="sidebar-link">Listado de Sitios</button>

        <template v-if="authStore.isLoggedIn">
          <hr>
          <button @click="router.push('/perfil'); toggleMenu();" class="sidebar-link">
            Perfil
          </button>

          <button @click="router.push('/mis-resenas'); toggleMenu();" class="sidebar-link">
            Mis Reseñas
          </button>

          <button @click="router.push('/mis-favoritos'); toggleMenu();" class="sidebar-link">
            Sitios Favoritos
          </button><button @click="logout(); toggleMenu();" class="sidebar-link logout-link">Cerrar Sesión</button>
        </template>
      </nav>
    </aside>

    <div v-if="isMenuOpen" @click="toggleMenu" class="menu-overlay"></div>

    <RouterView />
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap');

#app-wrapper {
  font-family: 'Inter', sans-serif;
  color: #373b3f;
}

.auth-bar, .user-info {
  display: none !important;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #0d055c;
  color: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 100px;
}

.menu-hamburguer-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.icon-line {
  display: block;
  width: 25px;
  height: 3px;
  background-color: white;
  border-radius: 2px;
}

.menu-label {
  font-weight: bold;
  font-size: 1.1em;
  display: none;
}

.header-center {
  flex-grow: 1;
  text-align: center;
}

.app-logo {
  height: 55px;
  max-width: 200px;
  cursor: pointer;
}

.header-right {
  min-width: 100px;
  display: flex;
  justify-content: flex-end;
}

.sidebar {
 position: fixed;
  top: 0;
  left: -380px;
  width: 280px;
  height: 100%;
  background-color: #f8f8f8;
  box-shadow: 2px 0 5px rgba(0,0,0,0.5);
  transition: left 0.3s ease;
  z-index: 1010;
  padding: 20px;
  display: block;
}

.sidebar.is-open {
  left: 0;
}

.close-menu-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  color: #0a0c51;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 40px;
}

.sidebar-nav hr {
  width: 100%;
  border: none;
  border-top: 1px solid var(--vt-c-divider-light-2, #f2f2f2);
  margin: 10px 0;
}

.sidebar-link {
  background: none;
  border: none;
  text-align: left;
  padding: 10px 15px;
  font-size: 1.1em;
  cursor: pointer;
  color: var(--vt-c-indigo, #2c3e50);
  transition: background-color 0.2s;
  border-radius: 5px;
  width: 100%;
}

.sidebar-link:hover {
  background-color: var(--vt-c-white-mute, #f2f2f2);
}

.logout-link {
  color: #dc3545;
  font-weight: bold;
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 1005;
}
</style>
