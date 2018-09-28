<template>
  <mo-select 
    v-model="selected" 
    :label="label" 
    :options="orderedListOptions" 
    :required="required" 
    :disabled="isDisabled"
  />
</template>

<script>
  /**
   * A facet picker component.
   */

  import Facet from '@/api/Facet'
  import MoSelect from '@/components/atoms/MoSelect'

  export default {
    name: 'MoFacetPicker',

    components: {
      MoSelect
    },

    props: {
      /**
       * Create two-way data bindings with the component.
       */
      value: Object,

      /**
       * Defines a required facet.
       */
      facet: {type: String, required: true},

      /**
       * This boolean property requires a selected value.
       */
      required: Boolean,

      /**
       * Defines a preselectedUserKey.
       */
      preselectedUserKey: String
    },

    data () {
      return {
        /**
         * The selected, facets, label component value.
         * Used to detect changes and restore the value.
         */
        selected: null,
        facets: [],
        label: ''
      }
    },

    computed: {
      /**
       * Disabled value if its undefined.
       */
      isDisabled () {
        return this.preselectedUserKey !== undefined
      },

      orderedListOptions () {
        return this.facets.slice().sort((a, b) => {
          if (a.name < b.name) {
            return -1
          }
          if (a.name > b.name) {
            return 1
          }
          return 0
        })
      }
    },

    watch: {
      /**
       * Whenever selected change, update val.
       */
      selected (val) {
        this.$emit('input', val)
      }
    },

    mounted () {
      /**
       * Called after the instance has been mounted.
       * Set selected as value.
       */
      this.getFacet()
      if (this.value && this.preselectedUserKey == null) {
        this.selected = this.value
      }
    },

    methods: {
      /**
       * Get a facet.
       */
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

      /**
       * Set a preselected value.
       */
      setPreselected () {
        return this.facets.filter(data => {
          return data.user_key === this.preselectedUserKey
        })
      }
    }
  }
</script>
