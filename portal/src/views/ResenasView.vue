<template>
  <div class="reviews-page">
    <BackButton />
    <header class="page-header">
      <h1>📝 Mis Reseñas</h1>
      <p class="subtitle">Aquí puedes ver todas tus reseñas y su estado de aprobación.</p>
    </header>

    <main class="reviews-main">

      <div v-if="isLoading" class="status-message loading-box">
        Cargando tus reseñas...
      </div>

      <div v-else-if="error" class="error-message message-box">
        ❌ Error al cargar reseñas: **{{ errorMessage }}**
        <p v-if="errorStatusCode === 401">
          Por favor, <router-link to="/login">inicia sesión</router-link>.
        </p>
      </div>

      <div v-else-if="reviews.length > 0" class="list-grid">
        <div 
          v-for="review in reviews" 
          :key="review.id" 
          class="review-card"
        >
          <h3 class="review-title">Reseña del sitio #{{ review.site_id }}</h3>

          <p class="review-rating">⭐ {{ review.rating }} / 5</p>

          <p 
            class="review-status" 
            :class="{
              pendiente: review.status === 'PENDIENTE',
              aprobada: review.status === 'APROBADA',
              rechazada: review.status === 'RECHAZADA'
            }"
          >
            Estado: {{ review.status }}
          </p>

          <p v-if="review.rejection_reason" class="review-rejection">
            Motivo de rechazo: {{ review.rejection_reason }}
          </p>

          <p class="review-date">
            Publicada el {{ formatDate(review.created_at) }}
          </p>

          <p class="review-content">
            {{ review.content }}
          </p>
        </div>
      </div>

      <div v-else class="empty-message message-box">
        Aún no escribiste reseñas.
        <p>Explora sitios y comparte tu experiencia.</p>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";
import BackButton from '@/components/BackButton.vue';

const authStore = useAuthStore();
const router = useRouter();

const reviews = ref([]);
const isLoading = ref(true);
const error = ref(null);
const errorMessage = ref("");
const errorStatusCode = ref(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const fetchReviews = async () => {
  if (!authStore.isLoggedIn) {
    router.push("/login");
    return;
  }

  isLoading.value = true;
  error.value = null;
  errorMessage.value = "";

  const url = `${API_BASE_URL}/me/reviews`;

  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...authStore.authHeader,
      },
    });

    if (response.status === 401) {
      authStore.logout();
      errorMessage.value = "Tu sesión ha expirado.";
      errorStatusCode.value = 401;
      error.value = true;
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    reviews.value = data.data || [];

  } catch (err) {
    console.error("Fetch error for reviews:", err);
    errorMessage.value = err.message;
    error.value = true;
  } finally {
    isLoading.value = false;
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
};

onMounted(() => {
  fetchReviews();
});
</script>

<style scoped>
.reviews-page {
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

.review-card {
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #ddd;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.review-title {
  font-size: 1.3em;
  font-weight: bold;
  color: #3f51b5;
}

.review-rating {
  margin-top: 8px;
  font-size: 1.1em;
  color: #444;
}

.review-status {
  font-weight: bold;
  margin-top: 10px;
}

.review-status.pendiente {
  color: orange;
}

.review-status.aprobada {
  color: green;
}

.review-status.rechazada {
  color: red;
}

.review-rejection {
  margin-top: 5px;
  color: #c00;
  font-style: italic;
}

.review-date {
  font-size: 0.9em;
  color: #777;
  margin: 10px 0;
}

.review-content {
  margin-top: 10px;
  color: #444;
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
</style>
