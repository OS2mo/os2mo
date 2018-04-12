<template>
  <label class="form-check-label">
    <input class="form-check-input" type="checkbox" v-model="selected"/> 
    Søg i hele landet
  </label>
</template>


<script>
  export default {
    data () {
      return {
        selected: false
      }
    },
    watch: {
      selected (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
