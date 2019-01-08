<template>
  <mo-select
    v-model="selected"
    :label="$t('input_fields.'+facetData.user_key)"
    :options="sortedOptions"
    :required="required"
    :disabled="isDisabled"
  />
</template>

<script>
/**
 * A facet picker component.
 */

import sortBy from 'lodash.sortby'
import MoSelect from '@/components/atoms/MoSelect'

export default {
  name: 'MoFacetPicker',

  components: {
    MoSelect
  },

  props: {
    value: Object,
    facet: { type: String, required: true },
    required: Boolean,
    preselectedUserKey: String
  },

  data () {
    return {
      selected: null
    }
  },

  computed: {
    facetData () {
      return this.$store.getters['facet/GET_FACET'](this.facet)
    },
    sortedOptions () {
      let data = this.$store.getters['facet/GET_FACET'](this.facet)
      return sortBy(data.classes, 'name')
    },
    isDisabled () {
      return this.preselectedUserKey !== undefined
    }
  },

  watch: {
    /**
     * Whenever selected change, update val.
     */
    selected (val) {
      this.$emit('input', val)
    },

    facetData (val) {
      this.selected = this.preselectedUserKey ? this.setPreselected()[0] : this.selected
    }
  },

  created () {
    this.$store.dispatch('facet/SET_FACET', this.facet)
  },

  mounted () {
    this.selected = this.preselectedUserKey ? this.setPreselected()[0] : this.selected

    if (this.value && this.preselectedUserKey == null) {
      this.selected = this.value
    }
  },

  methods: {
    setPreselected () {
      if (!this.facetData.classes) return [undefined]
      return this.facetData.classes.filter(data => {
        return data.user_key === this.preselectedUserKey
      })
    }
  }
}
</script>
