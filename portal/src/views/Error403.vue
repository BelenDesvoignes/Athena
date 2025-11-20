<template>
  <div class="error-page">
    <h1>403</h1>
    <p>No tienes permiso para acceder a esta página.</p>
    <button @click="$router.push('/')">Ir al inicio</button>
  </div>
</template>

<style scoped>
.error-page {
  text-align: center;
  padding: 60px 20px;
}
h1 {
  font-size: 80px;
  margin-bottom: 20px;
}
button {
  padding: 8px 16px;
  border-radius: 8px;
  background: #071a78;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background: #0a239d;
}
</style>

