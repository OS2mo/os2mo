<template>
  <div>
  <loading v-show="isLoading"/>
  <button type="button" class="btn btn-primary" v-show="!isLoading">
    <icon name="check"/>
  </button>
  </div>
</template>

<script>
import Loading from './Loading'
export default {
  components: {
    Loading
  },
  props: {
    isLoading: Boolean
  },
  data () {
    return {}
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
