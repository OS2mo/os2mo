<template>
  <mo-select v-model="selected" :label="label" :options="facets" :required="required"/>
</template>

<script>
import Facet from '@/api/Facet'
import MoSelect from '@/components/atoms/MoSelect'

export default {
  name: 'MoFacetPicker',
  components: {
    MoSelect
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
  watch: {
    selected (val) {
      this.$emit('input', val)
    }
  },
  mounted () {
    this.getFacet()

    if (this.value) {
      this.selected = this.value
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
