<template>
  <div class="form-group col">
    <label>Stillingsbetegnelse</label>
    <select 
      class="form-control col" 
      v-model="selectedTitle"
      @change="updateSelectedTitle()">
      <option disabled>Stillingsbetegnelse</option>
      <option 
        v-for="title in engagementTitles" 
        v-bind:key="title.uuid"
        :value="title.uuid">
          {{title.name}}
      </option>
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
      selectedTitle: '',
      engagementTitles: []
    }
  },
  created () {
    this.getEngagementTitles()
  },
  methods: {
    getEngagementTitles () {
      var vm = this
      Property.getEngagementTitles().then(function (response) {
        vm.engagementTitles = response
      })
    },

    updateSelectedTitle () {
      this.$emit('input', this.selectedTitle)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>