<template>
  <div>
    <mo-cpr-search v-model="result" required/>

    <mo-cpr-result v-model="result"/>
  </div>
</template>

<script>
  import MoCprSearch from './MoCprSearch'
  import MoCprResult from './MoCprResult'

  export default {
    name: 'MoCpr',

    components: {
      MoCprSearch,
      MoCprResult
    },

    data () {
      return {
        result: {}
      }
    },

    watch: {
      result (val) {
        this.$emit('input', val)
      }
    }
  }
</script>
