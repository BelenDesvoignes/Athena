<template>
  <button @click="goBack" class="back-btn">
    ⬅️ Volver
  </button>
</template>

<script>
export default {
  name: "BackButton",
  methods: {
    goBack() {
      if (window.history.length > 1) {
        this.$router.back()
      } else {
        this.$router.push(this.fallbackRoute)
      }
    }
  },
  props: {
    fallbackRoute: {
      type: String,
      default: "/"
    }
  }
}
</script>

<style scoped>
.back-btn {
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  background-color: #071a78;
  color: white;
  font-size: 15px;
  transition: 0.2s;
}

.back-btn:hover {
  background-color: #0056b3;
}
</style>
