<template>
  <div class="maintenance-page">
    <div class="card">
      <h1>⚠️ Portal en mantenimiento</h1>
      <p v-if="message && message.length">{{ message }}</p>
      <p v-else>El portal se encuentra temporalmente en mantenimiento. Volvé en unos minutos.</p>
      <div class="meta">
        <small>Si creés que esto es un error, contactá al administrador.</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { checkPortalStatus } from "../services/portalFlags";

const message = ref("");

onMounted(async () => {
  const st = await checkPortalStatus();
  if (st && st.message) message.value = st.message;
});
</script>

<style scoped>
.maintenance-page {
  min-height: 80vh;
  display:flex;
  justify-content:center;
  align-items:center;
  padding: 20px;
}
.card {
  max-width:760px;
  width:100%;
  background: #fff;
  padding: 28px;
  border-radius: 10px;
  box-shadow: 0 6px 24px rgba(2,6,23,0.08);
  text-align:center;
}
h1 { margin-bottom: 12px; }
.meta { margin-top: 18px; color: #666; }
</style>
