<template>
  <div class="form-group col">
    <label>Stillingsbetegnelse</label>
    <select 
      class="form-control col" 
      v-model="selectedTitle"
      @change="updatejobFunctions()">
      <option disabled>Stillingsbetegnelse</option>
      <option 
        v-for="title in jobFunctions" 
        v-bind:key="title.uuid"
        :value="title">
          {{title.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'

export default {
  props: {
    value: Object,
    orgUuid: String
  },
  data () {
    return {
      selectedTitle: '',
      jobFunctions: []
    }
  },
  watch: {
    orgUuid () {
      this.getjobFunctions()
    }
  },
  methods: {
    getjobFunctions () {
      let vm = this
      Facet.jobFunctions(this.orgUuid)
        .then(response => {
          vm.jobFunctions = response
        })
    },

    updatejobFunctions () {
      this.$emit('input', this.selectedTitle)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>