<template>
  <div class="reviews-page">
    <BackButton />
    <header class="page-header">
      <h1>📝 Mis Reseñas</h1>
      <p class="subtitle">Aquí puedes ver todas tus reseñas y su estado de aprobación.</p>
    </header>

    <main class="reviews-main">
      <div v-if="reviewsFeatureDisabled" class="reviews-disabled-msg">
          ✖️ Las reseñas están desactivadas temporalmente.
      </div>
      <div v-else>
        <div v-if="isLoading" class="status-message loading-box">
          Cargando tus reseñas...
        </div>

        <div v-else-if="error" class="error-message message-box">
          ❌ Error al cargar reseñas: **{{ errorMessage }}**
          <p v-if="errorStatusCode === 401">
            Por favor, inicia sesión nuevamente.
          </p>
        </div>

        <div v-else-if="reviews.length > 0" class="list-grid">
          <div v-for="review in reviews" :key="review.id" class="review-card">
            <section>
              <h3 class="review-title">Reseña del sitio: {{ review.site_name }}</h3>
        <button @click="openEditReviewModal(review)" class="edit-btn">
          ✏️ Editar
        </button>

        <button @click="deleteReview(review)" class="modal-delete">
          🗑️ Eliminar
        </button>
            </section>

            <p class="review-rating">⭐ {{ review.rating }} / 5</p>
            <p class="review-comment">Comentario: {{ review.comment }}</p>
            <p class="review-status" :class="{
              pendiente: review.status === 'PENDIENTE',
              aprobada: review.status === 'APROBADA',
              rechazada: review.status === 'RECHAZADA'
            }">
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
          <p>¡Explora sitios y comparte tu experiencia!</p>
        </div>
      </div>

<div v-if="showReviewModal" class="review-modal-overlay" @click="closeReviewModal">
  <div class="review-modal" @click.stop>

    <!-- Header -->
    <div class="review-modal-header">
      <h3 v-if="!userReview">✍️ Escribir reseña</h3>
      <h3 v-else>✍️ Editar reseña</h3>
      <button class="close-btn" @click="closeReviewModal">✕</button>
    </div>

    <!-- Body -->
    <div class="review-modal-body">
      <label class="input-label">Calificación</label>
      <select v-model="newReview.rating" class="input-select">
        <option disabled value="">Selecciona…</option>
        <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
      </select>
      <label class="input-label">Comentario</label>
      <textarea v-model="newReview.content" class="input-textarea" rows="4"></textarea>
    </div>


        <div class="pagination" v-if="totalPages > 1">
          <button class="page-button" :disabled="currentPage <= 1" @click="prevPage()">
            Anterior
          </button>

          <span>Página {{ currentPage }} de {{ totalPages }}</span>

          <button class="page-button" :disabled="currentPage >= totalPages" @click="nextPage()">
            Siguiente
          </button>
        </div>

    <!-- Footer -->
    <div class="review-modal-footer">
      <button class="primary-btn" @click="submitReview">
        {{ userReview ? "Actualizar reseña" : "Enviar reseña" }}
      </button>
      <button class="secondary-btn" @click="closeReviewModal">Cancelar</button>
    </div>

  </div>
</div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from '@/stores/auth';
import { useRouter } from "vue-router";
import BackButton from '@/components/BackButton.vue';

const reviewsFeatureDisabled = ref(false);

async function fetchReviewsFlag() {
  try {
    const response = await fetch(`${API_BASE_URL}/flags/reviews`);
    const data = await response.json();
    reviewsFeatureDisabled.value = data.disabled;
  } catch (err) {
    console.error("Error obteniendo flag de reseñas:", err);
  }
}

const authStore = useAuthStore();
const router = useRouter();

const showLoginPromptReseña = ref(false);
const reviews = ref([]);
const isLoading = ref(true);
const error = ref(null);
const errorMessage = ref("");
const errorStatusCode = ref(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


const showReviewModal = ref(false);
const userReview = ref(null); 
const newReview = ref({
  rating: "",
  content: "",
  id:""
});


const currentPage = ref(1);
const totalPages = ref(1);
const perPage = 25;

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
        Authorization: authStore.authHeader.Authorization,
      }
    });

    if (response.status === 401) {
      errorMessage.value = "Tu sesión ha expirado.";
      errorStatusCode.value = 401;
      error.value = true;
      authStore.logout();
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }


    const data = await response.json();
    console.log("Fetched reviews data:", data);
    reviews.value = data.reviews || [];
    console.log("Reviews data length:", data.data);
    console.log("Reviews set to:", reviews.value);
  } catch (err) {
    console.error("Fetch error for reviews:", err);
    errorMessage.value = err.message;
    error.value = true;
  } finally {
    isLoading.value = false;
  }


};

function get_reseña(id_reseña) {
  return reviews.value.find(r => r.id == id_reseña);
}


function closeReviewModal() {
  showReviewModal.value = false;
}
const submitReview = async () => {
  if (!authStore.isLoggedIn) return;

  const aEditar = get_reseña(userReview.value.id)
  const url = `${API_BASE_URL}/sites/${aEditar.site_id}/reviews/${userReview.value.id}`  

  const method = "PUT";

  try {
    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: authStore.authHeader.Authorization,
      },
      body: JSON.stringify({
        site_id: aEditar.site_id,
        rating: newReview.value.rating,
        comment: newReview.value.content,
      })
    });

    if (!res.ok) throw new Error("Error guardando la reseña");
    await fetchReviews();
    closeReviewModal();
  } catch (err) {
    alert(err.message);
  }
};

const deleteReview = async (review) => {
  try {
    const authStore = useAuthStore();

    if (!authStore.isLoggedIn) {
      alert("Debes iniciar sesión para eliminar una reseña.");
      return;
    }

    const authorizationToken = authStore.authHeader.Authorization;
    if (!authorizationToken) {
      alert("Error: No se encontró el token de autenticación.");
      return;
    }

    const response = await fetch(`${API_BASE_URL}/sites/${review.site_id}/reviews/${review.id}`, {
      method: "DELETE",
      headers: {
        "Authorization": authorizationToken,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Error eliminando reseña:", data);
      alert(data.msg || data.error || JSON.stringify(data));
      return;
    }

    alert("Reseña eliminada con éxito ✔️");

    
    currentPage.value = 1;
    await fetchReviews();

  } catch (error) {
    console.error("❌ Error en deleteReview:", error);
    alert("Error de conexión o inesperado al eliminar la reseña.");
  }
}


const openEditReviewModal = (review) => {
  userReview.value = review;
  newReview.value.rating = review.rating;
  newReview.value.content = review.comment;
  showReviewModal.value = true;
};



const formatDate = (dateStr) => {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString();
};

onMounted(() => {
  fetchReviewsFlag();
  fetchReviews();
});
</script>

<style scoped>
.reviews-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* -------- HEADER -------- */
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

/* -------- GRID LIST -------- */
.list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 25px;
  padding: 20px 0;
}

/* -------- REVIEW CARD -------- */
.review-card {
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #ddd;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.review-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.review-title {
  font-size: 1.3em;
  font-weight: bold;
  color: #3f51b5;
}

/* -------- RATING -------- */
.review-rating {
  margin-top: 8px;
  font-size: 1.1em;
  color: #444;
  font-weight: bold;
}

/* -------- COMMENT -------- */
.review-comment {
  margin-top: 12px;
  font-size: 1.05em;
  color: #333;
  padding: 10px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #eee;
  line-height: 1.5;
  display: block;
  overflow: auto;
}

/* -------- STATUS -------- */
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
  font-size: 0.95em;
  background: #ffe5e5;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ffbfbf;
}

/* -------- DATE -------- */
.review-date {
  font-size: 0.9em;
  color: #777;
  margin-top: 12px;
}

/* -------- CONTENT -------- */
.review-content {
  margin-top: 10px;
  color: #444;
  line-height: 1.5;
}

/* -------- MESSAGE BOXES -------- */
.message-box {
  text-align: center;
  padding: 30px;
  border-radius: 8px;
  margin-top: 20px;
  font-size: 1.1em;
}

.review-modal-overlay {
  /* Fija el modal en la ventana */
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* Fondo semi-transparente */
  background: rgba(0, 0, 0, 0.6);
  /* Centrado */
  display: flex;
  justify-content: center;
  align-items: center;
  /* Asegura que esté por encima de todo */
  z-index: 1000;
}

.review-modal {
  background: white;
  padding: 25px;
  border-radius: 10px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  /* Animación de entrada */
  transform: scale(1);
  transition: transform 0.2s ease-out;
}

/* Encabezado */
.review-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.review-modal-header h3 {
  margin: 0;
  color: #3f51b5;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  color: #666;
  transition: color 0.15s;
}

.close-btn:hover {
  color: #333;
}

/* Cuerpo del Modal */
.review-modal-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-label {
  font-weight: bold;
  color: #444;
  margin-bottom: 5px;
}

.input-select, .input-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1em;
  box-sizing: border-box; /* Importante para el padding */
}

/* Pie de página */
.review-modal-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.primary-btn, .secondary-btn {
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  transition: background 0.2s;
}

.primary-btn {
  background: #3f51b5;
  color: white;
  border: none;
}

.primary-btn:hover {
  background: #2d3d9b;
}

.secondary-btn {
  background: #e0e0e0;
  color: #333;
  border: 1px solid #ccc;
}

.secondary-btn:hover {
  background: #ccc;
}

/* Estilos de Botones de Reseña */
.review-card section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.edit-btn, .delete-btn {
  padding: 6px 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: bold;
  transition: background 0.2s;
}

.edit-btn {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
}

.edit-btn:hover {
  background: #ffe098ff;
  transform: scale(1.1)
}


.edit-btn:active {
  transform: scale(0.9);
}


.modal-delete {
  background: rgba(255, 255, 255, 0.8);
  border: none;
  font-size: 18px;
  padding: 5px 8px;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s, transform 0.2s;
}

.modal-delete:hover {
  background: rgba(255, 0, 0, 0.3);
  transform: scale(1.1);
}

.modal-delete:active {
  transform: scale(0.9);
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

/* -------- BUTTONS -------- */
.btn-primary {
  background: #3f51b5;
  color: white;
  border: none;
  padding: 10px 18px;
  font-size: 1em;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.btn-primary:hover {
  background: #2d3d9b;
}


/* -------- LOGIN MODAL -------- */
.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.login-modal-content {
  background: white;
  padding: 25px 30px;
  border-radius: 12px;
  max-width: 420px;
  width: 90%;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.reviews-disabled-msg {
  text-align: center;
  padding: 12px 16px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  font-size: 14px;
  color: #8c6d1f;
  margin-bottom: 16px;
}
</style>
