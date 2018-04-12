<template>
  <div class="form-group col">
    <label>{{label}}</label>
    <select 
      :name="nameId"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="$emit('input', selected)"
      v-validate="{ required: required }"
    >
      <option disabled>{{label}}</option>
      <option v-for="facet in facets" :key="facet.uuid" :value="facet">
          {{facet.name}}
      </option>
    </select>
    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
import Facet from '@/api/Facet'

export default {
  name: 'MoFacetPicker',
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    facet: {type: String, required: true},
    required: Boolean
  },
  data () {
    return {
      selected: null,
      facets: [],
      label: ''
    }
  },
  computed: {
    nameId () {
      return 'mo-facet-picker-' + this._uid
    }
  },
  mounted () {
    this.getFacet()

    if (this.value) {
      this.selected = this.value
      this.$validator.validate(this.nameId)
    }
  },
  methods: {
    getFacet () {
      let vm = this
      let org = this.$store.state.organisation
      if (org.uuid === undefined) return
      Facet.getFacet(org.uuid, this.facet)
        .then(response => {
          vm.facets = response.data.items
          vm.label = response.user_key
        })
    }
  }
}
</script>
