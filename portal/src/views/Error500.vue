<template>
  <div class="error-page">
    <h1>500</h1>
    <p>Ocurrió un error inesperado en el servidor.</p>
    <BackButton />
  </div>
</template>

<script setup>
import BackButton from '@/components/BackButton.vue';
</script>

<style scoped>
.error-page {
  text-align: center;
  padding: 60px 20px;
}
h1 {
  font-size: 80px;
  margin-bottom: 20px;
}
</style>
