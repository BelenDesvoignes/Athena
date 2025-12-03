<template>
  <div class="site-detail-page">
    <div v-if="isLoading" class="status-message">
      Cargando detalles del sitio...
    </div>
    <div v-else-if="error" class="status-message error">
      ❌ {{ errorMessage }}
    </div>
    <section v-else-if="site" class="site-content">
      <BackButton />
      <header class="detail-header">
        <h1>{{ site.name }}</h1>
        <p class="location-info">📍 {{ site.city }}, {{ site.province }}</p>
        <div v-if="site.average_rating" class="rating-badge">
          ⭐ {{ Number(site.average_rating || 0).toFixed(1) }} ({{ totalReviews || 0 }} Reseñas)
        </div>
      </header>

      <hr>

      <div class="main-info-grid">
        <div class="image-container">
          <div class="cover-wrapper">
            <img :src="site.cover_image?.url || site.cover_image || '/default-cover.jpg'"
              :alt="site.cover_image?.title || site.name" class="site-cover-image" @click="openByIndex(0)">
            <button class="expand-button cover" @click.stop="openByIndex(0)">🔍</button>
          </div>
        </div>

        <div class="description-section">
          <h2>Descripción Breve</h2>
          <p>{{ site.short_description }}</p>

          <RouterLink
            v-for="tag in site.tags"
            :key="tag.id"
            :to="{
              path: '/sitios',
              query: { tags: tag.id }
            }"
            class="tag-badge">
            {{ tag.name }}
          </RouterLink>


          <div class="action-buttons">
            <!-- Botón de Favorito: Ahora SIEMPRE visible, llama a handleFavoriteAction -->
            <button
              @click="handleFavoriteAction"
              :class="['favorite-button', { 'is-favorite': isFavorite }]"
              :title="isFavorite ? 'Remover de Favoritos' : 'Marcar como Favorito'"
            >
              <span class="heart-icon">{{ isFavorite ? '❤️' : '🤍' }}</span>
              {{ isFavorite ? 'En Favoritos' : 'Añadir a Favoritos' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="site.images && site.images.length > 1" class="gallery-section">
        <div class="gallery-scroll">
          <div class="image-wrapper" v-for="(img, idx) in nonCoverImages" :key="img.id">
            <img :src="img.url" class="gallery-image" :alt="img.alt_text" @click="openByIndex(idx + 1)">
            <button class="expand-btn" @click.stop="openByIndex(idx + 1)">🔍</button>
          </div>
        </div>
      </div>

      <hr>

      <section class="full-description-section">
        <h2>Detalle del Sitio</h2>

        <div>
          <p>
            {{ site.short_description }}
          </p>
          <p>
            {{ showFull ? site.description : None }}
          </p>
        </div>

        <button v-if="site.description" @click="toggleDescription" class="ver-mas-btn">
          {{ showFull ? 'Ver menos' : 'Ver más' }}
        </button>
      </section>


      <hr>
      <section class="map-section">
        <div class="map-card">
          <h3 class="map-title">📍 Ubicación</h3>
          <div id="site-map" class="map-container" style="height: 300px; width: 100%; border-radius: 12px;"></div>

        </div>
      </section>
      <hr>

      <section class="reviews-list">
        <h2>Últimas Reseñas</h2>
        <div v-if="reviewsFeatureDisabled" class="reviews-disabled-msg">
          ✖️ Las reseñas están desactivadas temporalmente.
        </div>
        <div v-else>
          <button v-if="userReview==null" class="write-review-btn" @click="handleWriteReview">
            ✍️ Escribir reseña
          </button>
          <button v-else class="write-review-btn" @click="handleWriteReview">
            ✍️ Editar mi reseña
          </button>

          <div v-if="showReviewModal" class="review-modal-overlay" @click="closeReviewModal">
            <div class="review-modal" @click.stop>

              <div class="review-modal-header">
                <h3 v-if="userReview==null">✍️ Escribir reseña</h3>
                <h3 v-else>✍️ Editar reseña</h3>
                <button class="close-btn" @click="closeReviewModal">✕</button>
              </div>

              <div class="review-modal-body">
                <label class="input-label">Calificación</label>
                <select  v-model="newReview.rating" class="input-select">
                  <option v-if="userReview==null" disabled value="">Selecciona…</option>
                  <option v-if="userReview!=null" :value="userReview.rating">{{ userReview.rating }} ⭐ (actual)</option>
                  <option v-for="n in 5" :key="n" :value="n">{{ n }} ⭐</option>
                </select>

                <label class="input-label">Comentario</label>
                <textarea v-if="userReview==null" v-model="newReview.content" class="input-textarea" rows="4"
                  placeholder="Escribe tu experiencia..."></textarea>
                  <textarea v-if="userReview!=null" v-model="newReview.content" class="input-textarea" rows="4">${{ userReview.comment }}</textarea>
              </div>

              <div class="review-modal-footer">
                <button class="primary-btn" @click="submitReviewModal">Enviar reseña</button>
                <button class="secondary-btn" @click="closeReviewModal">Cancelar</button>
              </div>

            </div>
          </div>

          <div v-if="isLoadingReviews" class="status-message">
            Cargando reseñas...
          </div>

          <!-- Error -->
          <div v-else-if="reviewsError" class="status-message error">
            ❌ {{ reviewsErrorMessage }}
          </div>

          <!-- Lista de reseñas -->
          <div v-else-if="reviews.length > 0" class="review-item" v-for="review in reviews" :key="review.id">
            <div class="review-header">
              <strong>
                <section>
                  {{ review.user_info?.nombre || 'Usuario Anónimo' }}

                  <button v-if="authStore.isLoggedIn &&
                    parseInt(review.user_id) === parseInt(authStore.userId)" class="modal-delete"
                    @click.stop="deleteReview(review.id)" aria-label="Eliminar">
                    🗑️
                  </button>
                </section>
              </strong>
              <span>⭐ {{ review.rating }}/5</span>
              <section>Comentario: {{ review.comment }}</section>
              <small class="review-date">{{ new Date(review.created_at).toLocaleDateString() }}</small>
            </div>
            <br></br>
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

          <!-- Sin reseñas -->
          <p v-if="totalReviews.length < 1" class="empty-message">
            Este sitio aún no tiene reseñas.
          </p>
        </div>
      </section>
    </section>

    <!-- Modal de Galería -->
    <div v-if="isModalOpen" class="image-modal" @click="closeModal">
      <button class="modal-close" @click.stop="closeModal" aria-label="Cerrar">✕</button>

      <button class="modal-nav left" @click.stop="prevImage" aria-label="Anterior">◀</button>
      <div class="modal-inner" @click.stop>
        <img :src="currentImage.url" class="modal-image" :alt="currentImage.alt_text" />
        <div class="modal-counter">{{ currentIndex + 1 }} / {{ imagesList.length }}</div>
      </div>
      <button class="modal-nav right" @click.stop="nextImage" aria-label="Siguiente">▶</button>
    </div>

    <!-- Modal de Aviso de Login/Redirección (AHORA SOLO AVISA) -->
    <div v-if="showLoginPrompt" class="login-modal-overlay">
        <div class="login-modal-content">
            <h3 class="text-xl font-bold">Inicia Sesión Requerido</h3>
            <p class="mt-2 text-gray-700 font-bold">
                Para marcar este sitio como favorito, necesitas iniciar sesión.
            </p>
            <p class="mt-2 text-gray-700 text-sm">
                Por favor, utiliza el botón "Iniciar Sesión con Google".
            </p>
            <div class="mt-4 flex justify-end gap-3">  <!-- Este botón ahora solo cierra el modal, sin intentar redireccionar -->
                <button @click="showLoginPrompt = false" class="btn-primary">
                    Entendido
                </button>
            </div>
        </div>
    </div>


     <div v-if="showLoginPrompt" class="login-modal-overlay">
        <div class="login-modal-content">
            <h3 class="text-xl font-bold">Inicia Sesión Requerido</h3>
            <p class="mt-2 text-gray-700 font-bold">
                Para marcar este sitio como favorito, necesitas iniciar sesión.
            </p>
            <p class="mt-2 text-gray-700 text-sm">
                Por favor, utiliza el botón "Iniciar Sesión con Google".
            </p>
            <div class="mt-4 flex justify-end gap-3">  <!-- Este botón ahora solo cierra el modal, sin intentar redireccionar -->
                <button @click="showLoginPrompt = false" class="btn-primary">
                    Entendido
                </button>
            </div>
        </div>
    </div>
  </div>

   <div v-if="showLoginPromptReseña" class="login-modal-overlay">
        <div class="login-modal-content">
            <h3 class="text-xl font-bold">Inicia Sesión Requerido</h3>
            <p class="mt-2 text-gray-700 font-bold">
                Para escribir una reseña, necesitas iniciar sesión.
            </p>
            <p class="mt-2 text-gray-700 text-sm">
                Por favor, utiliza el botón "Iniciar Sesión con Google".
            </p>
            <div class="mt-4 flex justify-end gap-3">  <!-- Este botón ahora solo cierra el modal, sin intentar redireccionar -->
                <button @click="showLoginPromptReseña = false" class="btn-primary">
                    Entendido
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted,defineExpose, nextTick, onBeforeUnmount, computed } from 'vue';
import { parseQuery, useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import BackButton from "@/components/BackButton.vue";
import "leaflet/dist/leaflet.css";

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


const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const { token } = storeToRefs(authStore);
const showFull = ref(false);
const toggleDescription = () => {
  showFull.value = !showFull.value;
};

const site = ref(null);
const isLoading = ref(true);
const error = ref(false);
const errorMessage = ref('');
const isFavorite = ref(false); 
const showLoginPrompt = ref(false);

const siteId = route.params.id;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const userReview = ref(null);
const reviewRating = ref(5);
const reviewContent = ref("");
const newReview = ref({
  rating: reviewRating.value,
  content: reviewContent.value
});
const reviews = ref([]);
const totalReviews = ref(0);
const isLoadingReviews = ref(true);
const reviewsError = ref(false);
const reviewsErrorMessage = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const perPage = 25;
const showReviewModal = ref(false);
const showLoginPromptReseña = ref(false); 
const isModalOpen = ref(false);
const currentIndex = ref(0);
const imagesList = ref([]);

const currentImage = computed(() => imagesList.value[currentIndex.value] || { url: '', alt_text: '' });
const nonCoverImages = computed(() => {
  if (!site.value || !site.value.images) return [];
  return site.value.images
    .filter(i => !i.is_cover)
    .map(i => ({
      ...i,
      alt_text: i.title || `Imagen del sitio ${site.value.name}`
    }));
});



const handleFavoriteAction = () => {
    if (!token.value) {
        
        showLoginPrompt.value = true;
    } else {
        
        toggleFavorite();
    }
};

function openByIndex(idx) {
  buildImagesListIfNeeded();
  if (!imagesList.value.length) return;
  if (idx < 0) idx = 0;
  if (idx >= imagesList.value.length) idx = imagesList.value.length - 1;
  currentIndex.value = idx;
  isModalOpen.value = true;
}

function buildImagesListIfNeeded() {
  if (!site.value) return;
  if (imagesList.value.length > 0) return;

  const list = [];

  if (site.value.cover_image) {
    list.push({
      url: site.value.cover_image.url || site.value.cover_image,
      alt_text: site.value.cover_image.title || site.value.name
    });
  }

  if (site.value.images && site.value.images.length) {
    for (const img of site.value.images) {
      if (!img.is_cover) {
        list.push({
          url: img.url,
          alt_text: img.title || site.value.name
        });
      }
    }
  }

  imagesList.value = list;
}
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchReviews();
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchReviews();
  }
};

function closeModal() {
  isModalOpen.value = false;
}

function nextImage() {
  if (!imagesList.value.length) return;
  currentIndex.value = (currentIndex.value + 1) % imagesList.value.length;
}

function prevImage() {
  if (!imagesList.value.length) return;
  currentIndex.value = (currentIndex.value - 1 + imagesList.value.length) % imagesList.value.length;
}

function onKeydown(e) {
  if (!isModalOpen.value) return;
  if (e.key === 'Escape') closeModal();
  if (e.key === 'ArrowRight') nextImage();
  if (e.key === 'ArrowLeft') prevImage();
}

function handleWriteReview() {
  if (!token.value) {
        // Si no está autenticado, muestra el modal y pide iniciar sesión
        showLoginPromptReseña.value = true;
    } else {
       if (userReview.value != null) {
          newReview.value.rating = userReview.value.rating;
          newReview.value.content = userReview.value.comment;
        } else {
          reviewRating.value = 5;
          reviewContent.value = "";
  }

  showReviewModal.value = true;
}}

function closeLoginPromptReseña() {
  showLoginPrompt.value = false;
}
function closeReviewModal() {
  showReviewModal.value = false;
}

async function submitReviewModal() {
  if (!newReview.value.rating || !newReview.value.content) {
    alert("Completa todos los campos.");
    return;
  }

  await submitReview()

  showReviewModal.value = false;

  newReview.value.rating = "";
  newReview.value.content = "";
}
function cancelReview() {
  showReviewModal.value = false;
  newReview.value.rating = "";
  newReview.value.content = "";
}

import L from "leaflet";
import "leaflet/dist/leaflet.css";


delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});




const map = ref(null);
const mapLoaded = ref(false);
function loadMap() {
  if (!site.value || mapLoaded.value) return;

  const lat = site.value.latitude;
  const lng = site.value.longitude;
  if (!lat || !lng) {
    console.warn("⚠ Este sitio no tiene coordenadas");
    return;
  }



  map.value = L.map("site-map").setView([lat, lng], 15);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors",
    }).addTo(map.value);

const tooltipText = `
    <strong>${site.value.name}</strong><br>
    ${site.value.short_description || ""}
  `;

  
  L.marker([lat, lng])
    .addTo(map.value)
    .bindTooltip(tooltipText, {
      permanent: false,  
      direction: "top",
    });
  mapLoaded.value = true;
}

const toggleFavorite = async () => {
    if (!token.value) {
        console.warn('Acción bloqueada: El usuario debe iniciar sesión para marcar favoritos.');
        return;
    }

    const isAdding = !isFavorite.value;
    const action = isAdding ? 'POST' : 'DELETE';
    const previousFavoriteState = isFavorite.value;

    
    const url = `${API_BASE_URL}/sites/${siteId}/favorite`;

    try {
       
        isFavorite.value = isAdding;

        const response = await fetch(url, { 
            method: action,
            headers: {
                'Authorization': `Bearer ${token.value}`,
                
            },
           
            // body: JSON.stringify({ site_id: siteId })
        });

        if (!response.ok) {
            
            isFavorite.value = previousFavoriteState;
            const errorData = await response.json().catch(() => ({}));
            console.error(`Error al ${isAdding ? 'añadir' : 'remover'} favorito:`, errorData.message || response.statusText);
        }

    } catch (err) {
        isFavorite.value = previousFavoriteState;
        console.error('Error de red al actualizar favoritos:', err);
    }
};

const fetchSiteDetail = async () => {
  isLoading.value = true;
  error.value = false;
  errorMessage.value = '';

  try {
    const url = `${API_BASE_URL}/sites/${siteId}`;
    const headers = {};

  
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`;
    }

    const response = await fetch(url, { headers });

    if (response.status === 404) {
      errorMessage.value = `Sitio con ID ${siteId} no encontrado.`;
      error.value = true;
      return;
    }
    if (!response.ok) {
      throw new Error(`Error al obtener el sitio. Código: ${response.status}`);
    }

    const data = await response.json();
    site.value = data.data || data;

    imagesList.value = [];
    buildImagesListIfNeeded();

    await nextTick();
    setTimeout(loadMap, 50);

    
    if (site.value.is_favorite !== undefined) {
      isFavorite.value = site.value.is_favorite;
    }

  } catch (err) {
    errorMessage.value = `Hubo un error de red o del servidor: ${err.message}`;
    error.value = true;
  } finally {
    isLoading.value = false;
  }
};



const fetchUserInfo = async (userId) => {
  const url = `${API_BASE_URL}/internal/users/${userId}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      return null;
    }

    const user_info = await response.json();

    return user_info;

  } catch (err) {
    return null;
  }
};

const deleteReview = async (reviewId) => {
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

    const response = await fetch(`${API_BASE_URL}/sites/${siteId}/reviews/${reviewId}`, {
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


const submitReview = async () => {
  try {
    const authStore = useAuthStore();

    if (!authStore.isLoggedIn) {
      alert("Debes iniciar sesión para enviar una reseña.");
      return;
    }

    const authorizationToken = authStore.authHeader.Authorization;
    if (!authorizationToken) {
      alert("Error: No se encontró el token de autenticación.");
      return;
    }

    const payload = {
      rating: parseInt(newReview.value.rating),
      site_id: parseInt(siteId),
      comment: newReview.value.content,

    };

    let url, method;

    if (!userReview.value) {
      
      url = `${API_BASE_URL}/sites/${siteId}/reviews`;
      method = "POST";
    } else if(userReview.value!=null) {
      url = `${API_BASE_URL}/sites/${siteId}/reviews/${userReview.value.id}`;
      method = "PUT";

    }

    const response = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": authorizationToken
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Error creando/editando reseña:", data);
      alert(data.msg || data.error || JSON.stringify(data));
      return;
    }

    alert(
      !userReview.value
        ? "Reseña creada con éxito ✔️"
        : "Reseña editada con éxito ✨"
    );

    
    showReviewModal.value = false;


  } catch (error) {
    console.error("❌ Error en submitReview:", error);
    alert("Error de conexión o inesperado al enviar la reseña.");
  }
    currentPage.value = 1;
    await fetchReviews();
};




const fetchCheckReview = async () => {
  if (!authStore.isLoggedIn) {
    showLoginPromptReseña.value = true;
    return;
  }

  const url = `${API_BASE_URL}/sites/${siteId}/reviews/check`;
  const method = "GET";
  const response = fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: authStore.authHeader.Authorization,
    }
  })
  return response;
};


function aprobadas(reviewsList){
  return reviewsList.filter(review => review.status === 'APROBADA');
}



const fetchReviews = async () => {
  isLoadingReviews.value = true;
  reviewsError.value = false;
  reviewsErrorMessage.value = '';
  try {
    const url = `${API_BASE_URL}/sites/${siteId}/reviews?page=${currentPage.value}&per_page=${perPage}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Error al obtener reseñas. Código: ${response.status}`);
    }

    const data = await response.json();
    totalPages.value = data.total_pages || 1;
    totalReviews.value = data.total_reviews || 0;
    const reviewsData = data.reviews || [];

    for (const review of reviewsData) {
      if (review.user_id) {
        review.user_info = await fetchUserInfo(review.user_id);
      } else {
        review.user_info = null;
      }
      if (userReview.value==null && parseInt(review.user_info.id) == parseInt(authStore.userId)) {
        userReview.value = review;
      }
    }
    const check = await fetchCheckReview();
    if (check) {
      const checkData = await check.json();
      if (checkData.review) {
        userReview.value = checkData.review;
      }
    }

    console.log(userReview.value);
    reviews.value = reviewsData;
    reviews.value = aprobadas(reviews.value);


  } catch (err) {
    console.error('🔥 Error al cargar reseñas:', err);
    reviewsErrorMessage.value = err.message;
    reviewsError.value = true;
  } finally {
    isLoadingReviews.value = false;
  }
};
onMounted(() => {

  fetchReviewsFlag();
  if (siteId) {
    fetchSiteDetail();
    fetchReviews();
  }
  else {
    errorMessage.value = 'ID del sitio no especificado en la URL.';
    error.value = true;
    isLoading.value = false;
  }
  window.addEventListener('keydown', onKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown);
});


</script>

<style scoped>

.login-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9990; /* Detrás del modal de imágenes */
}

.login-modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
}

.login-modal-content h3 {
    color: #071a78;
    margin-top: 0;
}

.btn-primary {
  background-color: #071a78;
  color: white;
  padding: 8px 15px;
  border-radius: 6px;
  font-weight: 600;
  transition: background-color 0.2s;
}
.btn-primary:hover {
    background-color: #0033aa;
}

.btn-cancel {
  background-color: #e0e0e0;
  color: #333;
  padding: 8px 15px;
  border-radius: 6px;
  font-weight: 600;
  transition: background-color 0.2s;
}
.btn-cancel:hover {
    background-color: #ccc;
}
/* Fin Estilos Modal Login */


/* Estilos existentes */

.site-detail-page {
  padding: 15px;
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  text-align: left;
  margin-bottom: 20px;
}

.rating-badge {
  display: inline-block;
  margin-top: 10px;
}

.site-cover-image {
  width: 100%;
  height: auto;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
  cursor: zoom-in;
}

.cover-wrapper {
  position: relative;
  display: block;
}

.expand-button.cover {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #ccc;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  z-index: 5;
}
.map-container {
  height: 300px;
  width: 100%;
  border-radius: 12px;
}


.page-button {
    background-color: #f4f4f4;
    border: 1px solid #cfcfcf;
    border-radius: 6px;
    color: #444;
    padding: 6px 14px;
    font-size: 14px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: 0.2s;
}


.page-button:hover {
    background-color: #e5e5e5;
}

.page-button.active {
    background-color: #dcdcdc;
    border-color: #b6b6b6;
    font-weight: bold;
}

.page-button:disabled {
    background-color: #f0f0f0;
    color: #999;
    border-color: #ddd;
    cursor: not-allowed;
    opacity: 0.7;
}

.login-warning {
  text-align: center;
  padding: 20px;
  margin: 25px auto;
  background: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  max-width: 450px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.login-text {
  font-size: 1.1rem;
  margin-bottom: 15px;
  color: #333;
}

.login-btn {
  background: #2563eb;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.25s ease, transform 0.15s ease;
}

.login-btn:hover {
  background: #1e4fc9;
}

.login-btn:active {
  transform: scale(0.97);
}

.description-section {
  padding: 0;
}

.full-description-section {
  margin-top: 20px;
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

/* Estilos para el botón de favorito */
.action-buttons {
  margin-top: 20px;
}

.favorite-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgb(107, 106, 106);
  background-color: rgb(167, 165, 165);
  color: #333;
}

.favorite-button:hover {
  opacity: 0.8;
  transform: translateY(-2px);

}

.favorite-button.is-favorite {
  background-color: #af6868; /* Rojo para favorito */
  color: white;
  border-color: #ff4d4d;
}

.heart-icon {
  font-size: 1.2em;
  transition: transform 0.3s;
}

.favorite-button.is-favorite .heart-icon {
  animation: pulse 0.5s ease-out;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.15);
  }

  100% {
    transform: scale(1);
  }
}

.login-tip {
  font-style: italic;
  color: #666;
  font-size: 0.9em;
}


.review-form-section {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #ececec;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.review-form h3 {
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

/* ---- Botón principal ---- */
.write-review-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #ccc;
  background-color: white;
  color: #333;
}

.write-review-btn:hover {
  opacity: 0.8;
  transform: translateY(-2px);

}

/* ---- Overlay oscuro ---- */
.review-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9998;
  animation: fadeIn 0.3s ease;
}

/* ---- Caja del modal ---- */
.review-modal {
  width: 380px;
  background: #ffffff;
  border-radius: 14px;
  padding: 18px 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
  animation: popIn 0.25s ease;
}

/* ---- Header del modal ---- */
.review-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.review-modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  transition: 0.2s;
}

.close-btn:hover {
  color: #000;
  transform: scale(1.15);
}

/* ---- Cuerpo ---- */
.review-modal-body {
  margin-top: 15px;
}

.input-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #444;
}

.input-select,
.input-textarea {
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
  transition: 0.2s;
  margin-bottom: 15px;
}

.input-select:focus,
.input-textarea:focus {
  border-color: #4e8cff;
  box-shadow: 0 0 0 3px rgba(78, 140, 255, 0.2);
  outline: none;
}

/* ---- Footer ---- */
.review-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Botones del modal */
.primary-btn {
  background: #1f62ff;
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

.primary-btn:hover {
  background: #174ecc;
}

.secondary-btn {
  background: #e0e0e0;
  color: #333;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.secondary-btn:hover {
  background: #c9c9c9;
}

/* ---- Animaciones ---- */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.92);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}




@media (min-width: 768px) {
  .site-content>.detail-header {
    margin-bottom: 30px;
  }

  .main-info-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 40px;
  }

  .detail-header {
    text-align: left;
  }
}

.gallery-section {
  width: 100%;
  margin-top: 20px;
}

.gallery-scroll {
  display: flex;
  flex-direction: row;
  overflow-x: auto !important;
  gap: 12px;
  padding: 10px 0;
  white-space: nowrap;
}

.image-wrapper {
  position: relative;
  display: inline-block;
}

.gallery-image {
  width: 220px;
  height: 150px;
  flex-shrink: 0;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: #eee;
  cursor: zoom-in;
}

.expand-btn {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 6px 10px;
  font-size: 0.85em;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.expand-btn:hover {
  background-color: rgba(0, 0, 0, 0.85);
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-inner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 95%;
  max-height: 95%;
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

.modal-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 10px;
  object-fit: contain;
}

.modal-nav {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10000;
  font-size: 18px;
}

.modal-nav.left {
  left: 18px;
}

.modal-nav.right {
  right: 18px;
}

.modal-close {
  position: fixed;
  top: 18px;
  right: 18px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  z-index: 10000;
  font-size: 18px;
}

.modal-counter {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 0.9rem;


  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }

  .modal-content {
    background: white;
    padding: 20px;
    width: 350px;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
    animation: fadeIn 0.2s ease;
  }

  .modal-actions {
    margin-top: 15px;
    display: flex;
    justify-content: space-between;
  }

  .cancel-btn {
    background: #ccc;
  }

  .write-review-btn {
    margin-top: 15px;
    background: #2a73ff;
    color: white;
    border-radius: 6px;
    padding: 10px 16px;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }

    to {
      opacity: 1;
      transform: scale(1);
    }
  }

}

.ver-mas-btn {
  margin-top: 10px;
  background: none;
  color: #0077cc;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.ver-mas-btn:hover {
  text-decoration: underline;
}

.reviews-disabled-msg {
  padding: 12px 16px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  font-size: 14px;
  color: #8c6d1f;
  margin-bottom: 16px;
}


</style>

