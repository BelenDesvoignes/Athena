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

      <hr>

      <div class="main-info-grid">
        <div class="image-container">
          <div class="cover-wrapper">
            <img
              :src="site.cover_image?.url || site.cover_image || '/default-cover.jpg'"
              :alt="site.cover_image?.title || site.name"
              class="site-cover-image"
              @click="openByIndex(0)"
            >
            <button class="expand-button cover" @click.stop="openByIndex(0)">🔍</button>
          </div>
        </div>

        <div class="description-section">
          <h2>Descripción Breve</h2>
          <p>{{ site.short_description }}</p>

          <div v-if="site.tags && site.tags.length" class="tags-section">
            <span v-for="tag in site.tags" :key="tag.id" class="tag-badge">{{ tag.name }}</span>
          </div>

          <div class="action-buttons"></div>
        </div>
      </div>

      <div v-if="site.images && site.images.length > 1" class="gallery-section">
        <div class="gallery-scroll">
          <div
            class="image-wrapper"
            v-for="(img, idx) in nonCoverImages"
            :key="img.id"
          >
            <img
              :src="img.url"
              class="gallery-image"
              :alt="img.alt_text"
              @click="openByIndex(idx + 1)"
            >
            <button class="expand-btn" @click.stop="openByIndex(idx + 1)">🔍</button>
          </div>
        </div>
      </div>

      <hr>

      <section class="full-description-section">
        <h2>Detalle del Sitio</h2>
        <p>{{ site.description || site.short_description }}</p>
      </section>

      <hr>

      <section class="reviews-list">
        <h2>Últimas Reseñas</h2>
        <p>Esta sección cargará las reseñas usando GET /sites/{{ site.id }}/reviews.</p>
      </section>

    </section>

    <div v-if="isModalOpen" class="image-modal" @click="closeModal">
      <button class="modal-close" @click.stop="closeModal" aria-label="Cerrar">✕</button>

      <button class="modal-nav left" @click.stop="prevImage" aria-label="Anterior">◀</button>
      <div class="modal-inner" @click.stop>
        <img :src="currentImage.url" class="modal-image" :alt="currentImage.alt_text" />
        <div class="modal-counter">{{ currentIndex + 1 }} / {{ imagesList.length }}</div>
      </div>
      <button class="modal-nav right" @click.stop="nextImage" aria-label="Siguiente">▶</button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
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
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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
    site.value = data.data || data;

    imagesList.value = [];
    buildImagesListIfNeeded();

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

onMounted(() => {
  if (siteId) fetchSiteDetail();
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
  background: rgba(255,255,255,0.9);
  border: 1px solid #ccc;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  z-index: 5;
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

@media (min-width: 768px) {
  .site-content > .detail-header {
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
  background-color: rgba(0,0,0,0.7);
  color: white;
  border: none;
  padding: 6px 10px;
  font-size: 0.85em;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.expand-btn:hover {
  background-color: rgba(0,0,0,0.85);
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.85);
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
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
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
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
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
  background: rgba(0,0,0,0.45);
  color: #fff;
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 0.9rem;
}
</style>
