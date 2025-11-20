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
      <button @click="router.push('/mis-resenas')" class="profile-btn">
        📝 Mis Reseñas
      </button>

      <button @click="router.push('/mis-favoritos')" class="profile-btn">
        ❤️ Sitios Favoritos
      </button>

      <button @click="logout(); toggleMenu();" class="profile-btn logout-btn">
        🚪 Cerrar Sesión
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
  align-items: center;
  gap: 18px;
  margin-top: 25px;
}

.profile-btn {
  width: 80%;
  max-width: 280px;
  background-color: #071a78;
  color: white;
  padding: 14px 20px;
  font-size: 1.05rem;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
  font-weight: 500;
  transition: 0.25s ease;
  box-shadow: 0 3px 6px rgba(0,0,0,0.15);
}

.profile-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.2);
  background-color: #0056b3;

}

.logout-btn {
  background-color: #8f0303;
}

.logout-btn:hover {
  background-color: #d40000;
}
</style>
