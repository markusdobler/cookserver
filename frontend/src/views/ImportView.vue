<template>
  <div class="min-h-screen py-12">
    <div class="container mx-auto px-4">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-base01 mb-2">Cook Recipe Importer</h1>
        <p class="text-base00">Import recipes from any URL</p>
      </div>
      
      <ImportForm />
    </div>
  </div>
</template>

<script setup>
import ImportForm from '../components/import/ImportForm.vue'
</script>
