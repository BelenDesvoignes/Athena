<script setup>
import { RouterView, useRouter } from 'vue-router'
import { onMounted } from 'vue'
import { GoogleLogin } from 'vue3-google-login'
import { useAuthStore } from '@/stores/auth'; // Importar el store

const authStore = useAuthStore();
const router = useRouter();

// onMounted ya no es necesario aquí, el store se inicializa con localStorage.
onMounted(() => {
  // Aseguramos que el router esté disponible si el usuario hace clic en el botón
  // y que el store ya cargó los datos.
});

// 🔹 Callback: Simplemente llama a la acción del store
const callback = async (response) => {
  console.log("Respuesta de Google recibida. Procesando login en Pinia Store...");
  await authStore.loginWithGoogle(response);
}

// 🔹 Cerrar sesión: Simplemente llama a la acción del store
const logout = () => {
  // No usamos window.confirm, pero mantengo la funcionalidad requerida por las instrucciones anteriores.
  const confirmar = window.confirm("¿Estás seguro de que querés cerrar sesión?");
  if (confirmar) {
    authStore.logout();
    // Opcional: redirigir después de cerrar sesión
    // router.push('/'); 
  }
}
</script>

<template>
  <div id="app-wrapper">
    <!-- Navbar/Header de autenticación -->
    <div class="auth-bar">
      <!-- Si NO hay sesión iniciada (usando store) -->
      <div v-if="!authStore.isLoggedIn">
        <GoogleLogin :callback="callback" />
      </div>

      <!-- Si HAY sesión iniciada (usando store) -->
      <div v-else class="user-info">
        <!-- Usar authStore.user en lugar de userProfile local -->
        <img :src="authStore.user.imageUrl" alt="Foto de perfil" width="50" style="border-radius: 50%;" />
        <h3>Bienvenido/a, {{ authStore.user.name }}!</h3>
        <p style="color: gray; font-size: 0.9em;">ID: {{ authStore.userId }}</p>

        <button class="btn">Perfil</button>
        <button class="btn">Mis reseñas</button>
        <!-- Usar router para ir a la vista de favoritos -->
        <button class="btn" @click="router.push('/favorites')">Favoritos</button> 
        <button @click="logout" class="btn">Cerrar sesión</button>
      </div>
    </div>

    <!-- Contenido principal -->
    <RouterView />
  </div>
</template>

<style>
/* ... (Estilos existentes) ... */
#app-wrapper {
  font-family: 'Inter', sans-serif;
  color: #2c3e50;
}

.auth-bar {
  padding: 10px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: flex-end; /* Alinear a la derecha */
}

.btn {
  padding: 7px 15px;
  font-size: 1.1em;
  font-weight: bold;
  color: #555;
  background-color: white;
  border: 2px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  margin: 5px;
}

.btn:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>