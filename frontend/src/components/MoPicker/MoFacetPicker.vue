<template>
  <mo-input-select
    class="col"
    v-model="internalValue"
    :label="labelText"
    :options="sortedOptions"
    :required="required"
  />
</template>

<script>
/**
 * A facet picker component.
 */

import sortBy from 'lodash.sortby'
import { MoInputSelect } from '@/components/MoInput'
import { Facet } from '@/store/actions/facet'

export default {
  name: 'MoFacetPicker',

  components: {
    MoInputSelect
  },

  props: {
    value: Object,
    facet: { type: String, required: true },
    required: Boolean,
  },

  data () {
    return {
      internalValue: null
    }
  },

  computed: {
    facetData () {
      return this.$store.getters[Facet.getters.GET_FACET](this.facet)
    },
    sortedOptions () {
      return sortBy(this.facetData.classes, 'name')
    },
    labelText () {
      return this.facetData.user_key ? this.$t(`input_fields.${this.facetData.user_key}`) : ''
    },
    preselected () {
      let preselected = null
      if (!this.facetData.classes) return preselected

      return preselected
    }
  },

  watch: {
    /**
     * Whenever selected change, update val.
     */
    internalValue (val) {
      this.$emit('input', val)
    },

    facetData (val) {
      this.setInternalValue()
    }
  },

  created () {
    this.$store.dispatch(Facet.actions.SET_FACET, this.facet)
  },

  mounted () {
    this.setInternalValue()

    if (this.value) {
      this.internalValue = this.value
    }
  },

  methods: {
    setInternalValue () {
      if (this.preselected) {
        this.internalValue = this.preselected
      }
    }
  }
}
</script>
