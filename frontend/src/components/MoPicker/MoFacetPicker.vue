<template>
  <mo-select 
    v-model="selected" 
    :label="label" 
    :options="facets" 
    :required="required" 
    :disabled="isDisabled"
  />
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
      required: Boolean,
      preselectedUserKey: String
    },

    data () {
      return {
        selected: null,
        facets: [],
        label: ''
      }
    },

    computed: {
      isDisabled () {
        return this.preselectedUserKey !== undefined
      }
    },

    watch: {
      selected (val) {
        this.$emit('input', val)
      }
    },

    mounted () {
      this.getFacet()
      if (this.value && this.preselectedUserKey == null) {
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
            vm.selected = vm.preselectedUserKey ? vm.setPreselected()[0] : vm.selected
          })
      },

      setPreselected () {
        return this.facets.filter(data => {
          return data.user_key === this.preselectedUserKey
        })
      }
    }
  }
</script>
