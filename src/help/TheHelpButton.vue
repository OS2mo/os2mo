<template>
  <router-link :to="{ name: 'Help'}">
    <button 
      type="button" 
      aria-label="Hjælp"
      class="btn btn-link text-white" 
      v-shortkey.once="['h']" 
      @shortkey="$router.push({name: 'Help'})"
    >
      <icon name="question-circle"/>
    </button>
  </router-link>
</template>
