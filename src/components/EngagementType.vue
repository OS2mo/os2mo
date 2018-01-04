<template>
  <div class="form-group col">
    <label>Engagementstype</label>
    <select class="form-control col" id="">
      <option>Engagementstype</option>
      <option v-for="etype in engagementTypes" v-bind:key="etype.uuid">{{etype.name}}</option>
    </select>
  </div>
</template>

<script>
import Property from '../api/Property'
export default {
  props: {
    value: String
  },
  data () {
    return {
      engagementTypes: []
    }
  },
  created () {
    this.getEngagementTypes()
  },
  methods: {
    getEngagementTypes: function () {
      var vm = this
      Property.getEngagementTypes().then(function (response) {
        vm.engagementTypes = response
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>