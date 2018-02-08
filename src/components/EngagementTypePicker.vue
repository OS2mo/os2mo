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
        v-bind:key="etype.uuid"
        :value="etype"
      >
        {{etype.name}}
      </option>
    </select>
  </div>
</template>

<script>
import Facet from '../api/Facet'

export default {
  props: {
    value: Object,
    preselected: String,
    noLabel: Boolean,
    org: {
      type: Object,
      required: true
    }
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
  methods: {
    getEngagementTypes () {
      let vm = this
      Facet.engagementTypes(this.org.uuid)
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
