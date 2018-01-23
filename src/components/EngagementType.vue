<template>
  <div class="form-group col">
    <label>Engagementstype</label>
    <select class="form-control col" id="">
      <option>Engagementstype</option>
      <option 
        v-for="etype in engagementTypes" 
        v-bind:key="etype.uuid"
      >
        {{etype.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Property from '../api/Property'
/**
 * Engagement Type Picker component
 */
export default {
  props: {
    /**
     * @model
     */
    value: String
  },
  data () {
    return {
      /**
       * The engagement types
       * @private
       */
      engagementTypes: []
    }
  },
  created () {
    this.getEngagementTypes()
  },
  methods: {
    getEngagementTypes: function () {
      var vm = this
      Property.getEngagementTypes()
      .then(response => {
        vm.engagementTypes = response
      })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>