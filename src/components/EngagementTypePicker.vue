<template>
  <div class="form-group col">
    <label v-if="!noLabel">{{label}}</label>
    <select 
      class="form-control col" 
      v-model="selected"
      @change="updateEngagementType()"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="etype in engagementTypes" 
        :key="etype.uuid"
        :value="etype"
      >
        {{etype.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'

export default {
  props: {
    value: Object,
    noLabel: Boolean
  },
  data () {
    return {
      label: 'Engagementstype',
      selected: {},
      engagementTypes: []
    }
  },
  watch: {
    org () {
      this.getEngagementTypes()
    }
  },
  created () {
    this.getEngagementTypes()
    this.selected = this.value
  },
  methods: {
    getEngagementTypes () {
      let vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.engagementTypes(org.uuid)
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
