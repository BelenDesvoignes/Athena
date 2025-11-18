<template>
  <div class="favoritos-page">
    <header class="page-header">
      <h1>⭐ Mis Sitios Favoritos</h1>
      <p class="subtitle">Aquí encontrarás todos los lugares que has marcado como preferidos.</p>
    </header>

    <main class="favoritos-main">
      <div v-if="isLoading" class="status-message loading-box">
        Cargando tus sitios favoritos...
      </div>

      <div v-else-if="error" class="error-message message-box">
        ❌ Error al cargar favoritos: {{ errorMessage }}
        <p v-if="errorStatusCode === 401">
          Por favor, <router-link to="/login">inicia sesión</router-link>.
        </p>
      </div>

      <div v-else-if="sites.length > 0" class="list-grid">
        <SiteCard
          v-for="site in sites"
          :key="site.id"
          :site="site"
        />
      </div>

      <div v-else class="empty-message message-box">
        Aún no agregaste sitios a tus favoritos.
        <p>¡Explorá el portal y marcá tus preferidos!</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SiteCard from '@/components/SiteCard.vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const sites = ref([]);
const isLoading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const errorStatusCode = ref(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const fetchFavorites = async () => {
  if (!authStore.isLoggedIn) {
    router.push('/login');
    return;
  }

  isLoading.value = true;
  error.value = false;
  errorMessage.value = '';
  errorStatusCode.value = null;

  try {
    const response = await fetch(`${API_BASE_URL}/v1/user/favorites`, {
      headers: {
        'Content-Type': 'application/json',
        ...authStore.authHeader,
      },
    });

    if (response.status === 401) {
      authStore.logout();
      errorStatusCode.value = 401;
      errorMessage.value = 'Tu sesión ha expirado.';
      error.value = true;
      return;
    }

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    sites.value = data.data || [];

  } catch (err) {
    console.error('Error cargando favoritos:', err);
    errorMessage.value = err.message;
    error.value = true;

  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchFavorites);
</script>

<style scoped>
.favoritos-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}
.page-header h1 {
  color: #3f51b5;
  font-size: 2.2em;
  margin-bottom: 5px;
}
.subtitle {
  color: #666;
  font-size: 1.1em;
}

.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  padding: 20px 0;
}

@media (min-width: 768px) {
  .list-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .list-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.message-box {
  text-align: center;
  padding: 30px;
  border-radius: 8px;
  margin-top: 20px;
  font-size: 1.1em;
}
.loading-box {
  color: #3f51b5;
  font-weight: bold;
}
.error-message {
  background-color: #ffe0e0;
  color: #cc0000;
  border: 1px solid #ff9999;
}
.empty-message {
  background-color: #f7f7f7;
  color: #555;
  border: 1px solid #ddd;
}
.empty-message p {
  margin-top: 10px;
  font-style: italic;
  color: #888;
}
.error-message a {
  color: #3f51b5;
  font-weight: bold;
}
</style>
