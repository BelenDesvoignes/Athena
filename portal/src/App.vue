<script setup>
import { RouterView } from 'vue-router';
import { ref, computed, onMounted } from 'vue'; 
import { GoogleLogin } from 'vue3-google-login'
import { jwtDecode } from 'jwt-decode';

onMounted(() => {
  const savedProfile = localStorage.getItem('userProfile');
  if (savedProfile) {
    userProfile.value = JSON.parse(savedProfile);
  }
});


const userProfile = ref(null)
 
const callback = (response) => {
  console.log("Handle the response", response)
 
  if (response?.credential) {
    try {
      const decoded = jwtDecode(response.credential)
      console.log('Decoded JWT:', decoded)
 
      const profile = {
        name: decoded.name,
        email: decoded.email,
        imageUrl: decoded.picture,
      }

      // 👉 Guardar en memoria reactiva
      userProfile.value = profile

      // 👉 Guardar en localStorage para persistencia
      localStorage.setItem('userProfile', JSON.stringify(profile))

    } catch (error) {
      console.error('Failed to decode JWT:', error)
    }
  }
}

const logout = () => {
  const confirmar = window.confirm("¿Estás seguro de que querés cerrar sesión?");
  if (confirmar) {
    userProfile.value = null;
    localStorage.removeItem('userProfile');
  }
};


</script>

<template>
  <div id="app-wrapper">
    <!-- Aquí iría cualquier layout fijo (Navbar, Footer) -->

     <!--Muestro el inicio de sesion si no hay ninguna sesion iniciada-->
      <div v-if="!userProfile">
        <GoogleLogin :callback="callback"/>
      </div>

      <!--Muestro info basica y navegacion para cuando hay una sesion iniciada-->
      <div v-else="userProfile" class="user-info">
          <img :src="userProfile.imageUrl" alt="Foto de perfil" width="50" style="border-radius: 50%; margin-top: 10px;"/>
          <h3>Bienvenido/a, {{ userProfile.name }}!</h3>

          <button class="btn">Perfil</button>
          <button class="btn">Mis reseñas</button>
          <button class="btn">Favoritos</button>
          <button @click="logout" class="btn">Cerrar sesión</button>
      </div>

    <!-- 🔑 CLAVE: Aquí se inyecta el contenido de la ruta / -->
    <RouterView /> 
  </div>
</template>

<style>

#app-wrapper {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.google-login {
  margin-top: 25px;
}

.google-login button {
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

.google-login button:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.google-login img {
  width: 20px;
  height: 20px;
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
  align-items: center; /* centra verticalmente */
  gap: 10px; /* espacio entre elementos */
}

.user-info img {
  border-radius: 50%;
  margin-top: 0; /* elimina el margen que tenías */
}
</style>