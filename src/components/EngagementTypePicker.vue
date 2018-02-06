<template>
  <div class="form-group col">
    <label v-if="!noLabel">Engagementstype</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateEngagementType()"
    >
      <option disabled>Engagementstype</option>
      <option 
        v-for="etype in engagementTypes" 
        v-bind:key="etype.uuid"
        :value="etype.uuid"
      >
        {{etype.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Property from '../api/Property'

export default {
  props: {
    value: String,
    preselected: String,
    noLabel: Boolean
  },
  data () {
    return {
      selected: {},
      engagementTypes: []
    }
  },
  created () {
    this.getEngagementTypes()
    this.selectedType = this.preselected
  },
  methods: {
    getEngagementTypes: function () {
      var vm = this
      Property.getEngagementTypes()
      .then(response => {
        vm.engagementTypes = response
      })
    },

    updateEngagementType () {
      this.$emit('input', this.selected)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>