<template>
  <div class="form-group col">
    <label>Stillingsbetegnelse</label>
    <select class="form-control col" id="">
      <option>Stillingsbetegnelse</option>
      <option v-for="title in engagementTitles" v-bind:key="title.uuid">{{title.name}}</option>
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
      engagementTitles: []
    }
  },
  created () {
    this.getEngagementTitles()
  },
  methods: {
    getEngagementTitles: function () {
      var vm = this
      Property.getEngagementTitles().then(function (response) {
        vm.engagementTitles = response
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>