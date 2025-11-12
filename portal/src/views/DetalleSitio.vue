<template>
  <div class="site-detail-page">
    
    <div v-if="isLoading" class="status-message">
      Cargando detalles del sitio...
    </div>

    <div v-else-if="error" class="status-message error">
      ❌ {{ errorMessage }}
    </div>

    <section v-else-if="site" class="site-content">
      
      <header class="detail-header">
        <h1>{{ site.name }}</h1>
        <p class="location-info">📍 {{ site.city }}, {{ site.province }}</p>
        <div v-if="site.average_rating" class="rating-badge">
          ⭐ {{ site.average_rating.toFixed(1) }} ({{ site.review_count || 0 }} Reseñas)
        </div>
      </header>
      
      <div class="main-info-grid">
        <div class="image-container">
          <img :src="site.image_url || '/default-cover.jpg'" :alt="site.name" class="site-cover-image">
        </div>
        
        <div class="description-section">
          <h2>Descripción</h2>
          <p>{{ site.short_description }}</p>

          <div v-if="site.tags && site.tags.length" class="tags-section">
            <span v-for="tag in site.tags" :key="tag.id" class="tag-badge">{{ tag.name }}</span>
          </div>
          
          <div class="action-buttons">
             <button 
              @click="toggleFavorite" 
              :class="{ 'is-favorite': isFavorite }" 
              :disabled="!authStore.isLoggedIn" 
              class="btn-favorite"
            >
              {{ isFavorite ? '❤️ Quitar de Favoritos' : '🤍 Agregar a Favoritos' }}
              <span v-if="!authStore.isLoggedIn" class="login-prompt"> (Inicia sesión)</span>
            </button>
            
            <button @click="navigateToReviews" class="btn-reviews">
              ✍️ Ver Reseñas
            </button>
          </div>
        </div>
      </div>
      
      <section class="reviews-list">
        <h2>Últimas Reseñas</h2>
        <p>Esta sección cargará las reseñas usando GET /sites/{{ site.id }}/reviews.</p>
      </section>

    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; 

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const site = ref(null);
const isLoading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const isFavorite = ref(false);

const siteId = route.params.id;


const API_BASE_URL = 'http://localhost:5000/api';

const fetchSiteDetail = async () => {
    isLoading.value = true;
    error.value = false;
    errorMessage.value = '';

    try {
        const url = `${API_BASE_URL}/sites/${siteId}`;
        const response = await fetch(url);
        
        if (response.status === 404) {
            errorMessage.value = `Sitio con ID ${siteId} no encontrado.`;
            error.value = true;
            return;
        }
        if (!response.ok) {
            throw new Error(`Error al obtener el sitio. Código: ${response.status}`);
        }
        
        const data = await response.json();
        // Tomamos data.data si tu backend usa ese formato
        site.value = data.data || data;

        // Estado de favorito
        if (site.value.is_favorite !== undefined) {
            isFavorite.value = site.value.is_favorite;
        }
        
    } catch (err) {
        console.error('Error al cargar detalle del sitio:', err);
        errorMessage.value = `Hubo un error de red o del servidor: ${err.message}`;
        error.value = true;
    } finally {
        isLoading.value = false;
    }
};

const toggleFavorite = async () => {
    if (!authStore.isLoggedIn) {
        alert("Debes iniciar sesión para marcar un sitio como favorito.");
        router.push('/login');
        return;
    }

    const method = isFavorite.value ? 'DELETE' : 'PUT';
    const url = `${API_BASE_URL}/sites/${siteId}/favorite`;

    const initialState = isFavorite.value;
    isFavorite.value = !initialState; // Optimistic update

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...authStore.authHeader
            }
        });

        if (response.status === 204) {
            // Éxito, no hacer nada
        } else if (response.status === 401) {
            alert("Tu sesión ha expirado.");
            authStore.logout();
            isFavorite.value = initialState;
        } else {
            isFavorite.value = initialState;
            throw new Error(`Error en la API: Código ${response.status}`);
        }

    } catch (err) {
        isFavorite.value = initialState;
        alert(`Fallo al gestionar el favorito: ${err.message}`);
    }
};

const navigateToReviews = () => {
    router.push({ name: 'reviews-list', params: { siteId } });
};

onMounted(() => {
    if (siteId) fetchSiteDetail();
    else {
        errorMessage.value = 'ID del sitio no especificado en la URL.';
        error.value = true;
        isLoading.value = false;
    }
});
</script>

<style scoped>
.site-detail-page {
  padding: 15px;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  text-align: center;
  margin-bottom: 20px;
}

.site-cover-image {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.description-section {
  padding: 15px 0;
}

.tags-section {
  margin-top: 15px;
}

.tag-badge {
  display: inline-block;
  background-color: #e0e0e0;
  color: #555;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.9em;
  margin-right: 5px;
}

.action-buttons button {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 10px;
  transition: background-color 0.2s;
}

.btn-favorite {
  background-color: #f0f0f0;
}
.btn-favorite.is-favorite {
  background-color: #ffcccc;
  color: #e30000;
}
.btn-reviews {
  background-color: #3f51b5;
  color: white;
}

@media (min-width: 768px) {
  .main-info-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 30px;
  }
  .detail-header {
    text-align: left;
  }
}
</style>
