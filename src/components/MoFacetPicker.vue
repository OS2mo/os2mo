<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
      :name="facet"
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
      v-show="errors.has(facet)" 
      class="text-danger"
    >
      {{ errors.first(facet) }}
    </span>
  </div>
</template>

<script>
import Facet from '../api/Facet'
import { EventBus } from '../EventBus'

export default {
  name: 'MoFacetPicker',
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    facet: {
      type: String,
      required: true
    },
    required: Boolean,
    noLabel: Boolean
  },
  data () {
    return {
      selected: {},
      facets: [],
      label: ''
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
  beforeDestroy () {
    EventBus.$off(['organisation-changed'])
  },
  methods: {
    getFacet () {
      var vm = this
      let org = this.$store.state.organisation
      if (org.uuid === undefined) return
      Facet.getFacet(org.uuid, this.facet)
        .then(response => {
          vm.facets = response.data.items
          vm.label = response.user_key
        })
    },

    updateSelectedRoleTypes () {
      this.$emit('input', this.selected)
    }
  }
}
</script>
