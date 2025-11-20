<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import BackButton from '@/components/BackButton.vue'

const authStore = useAuthStore()
const router = useRouter()

if (!authStore.isLoggedIn) {
  router.push('/')
}
</script>

<template>
  <div class="profile-container">
    <BackButton />
    <div class="profile-header">
      <img
        :src="authStore.user.imageUrl"
        alt="Foto de usuario"
        class="profile-avatar"
      />

      <h2 class="profile-name">{{ authStore.user.name }}</h2>

      <p class="profile-email">{{ authStore.user.email }}</p>
    </div>

    <hr class="divider"/>

    <div class="profile-actions">
      <button @click="router.push('/mis-resenas')" class="sidebar-link">
        Mis Reseñas
      </button>

      <button @click="router.push('/mis-favoritos')" class="sidebar-link">
        Sitios Favoritos
      </button>
    </div>

  </div>
</template>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 480px;
  margin: auto;
}

.profile-header {
  text-align: center;
  margin-bottom: 25px;
}

.profile-avatar {
  width: 110px;
  height: 110px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #0d055c;
  box-shadow: 0 0 4px rgba(0,0,0,0.2);
}

.profile-name {
  margin-top: 12px;
  font-size: 1.4rem;
  color: #212121;
}

.profile-email {
  font-size: 0.95rem;
  color: #666;
}

.divider {
  margin: 20px 0;
  border: none;
  border-top: 1px solid #ddd;
}

.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.profile-btn {
  background-color: #0d055c;
  color: white;
  padding: 14px 18px;
  font-size: 1.1rem;
  border-radius: 10px;
  border: none;
  text-align: center;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.profile-btn:hover {
  opacity: 0.85;
}
</style>