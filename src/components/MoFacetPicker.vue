<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
      name="role-picker"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedRoleTypes()"
      v-validate="{ required: required }"
    >
      <option disabled>{{label}}</option>
      <option 
        v-for="f in facets" 
        v-bind:key="f.uuid"
        :value="f">
          {{f.name}}
      </option>
    </select>
    <span
      v-show="errors.has('role-picker')" 
      class="text-danger"
    >
      {{ errors.first('role-picker') }}
    </span>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import Organisation from '../api/Organisation'
import { EventBus } from '../EventBus'

export default {
  name: 'MoFacetPicker',
  props: {
    value: Object,
    facet: {
      type: String,
      required: true
    },
    required: Boolean,
    noLabel: Boolean,
    label: {
      type: String,
      default: 'Rolle'
    }
  },
  data () {
    return {
      selected: {},
      facets: []
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getFacet()
    })
  },
  created () {
    this.getFacet()
    this.selected = this.value
  },
  methods: {
    getFacet () {
      var vm = this
      let org = Organisation.getSelectedOrganisation()
      if (org.uuid === undefined) return
      Facet.getFacet(org.uuid, this.facet)
      .then(response => {
        vm.facets = response
      })
    },

    updateSelectedRoleTypes () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
