<template>
  <div class="game-detail-view">
    <h1>Game Detail</h1>
    <!-- TODO: Implement game detail page with download/launch buttons -->
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';

const route = useRoute();
const gameId = route.params.id;

// TODO: Fetch game details
</script>

<style scoped>
.game-detail-view {
  padding: 20px;
}
</style>
