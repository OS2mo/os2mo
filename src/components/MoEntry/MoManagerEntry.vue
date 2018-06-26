<template>
  <div>
    <div class="form-row">
      <mo-organisation-unit-search
        v-model="entry.org_unit" 
        label="Angiv enhed" 
        class="col"
        required
      />
      <mo-address-picker v-model="entry.address" :org-unit="entry.org_unit" class="col"/>
    </div> 
    <div class="form-row">
      <mo-facet-picker 
        facet="manager_type" 
        v-model="entry.manager_type" 
        required
      />
      <mo-facet-picker 
        facet="manager_level" 
        v-model="entry.manager_level"
        required
      />
    </div>

    <mo-add-many v-model="entry.responsibility" :entry-component="facetPicker" has-initial-entry small-buttons/>
    
    <mo-date-picker-range v-model="entry.validity" :initially-hidden="validityHidden"/> 
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitSearch from '@/components/MoOrganisationUnitSearch/MoOrganisationUnitSearch'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoAddressPicker from '@/components/MoPicker/MoAddressPicker'
import MoAddMany from '@/components/MoAddMany/MoAddMany'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitSearch,
    MoFacetPicker,
    MoAddressPicker,
    MoAddMany
  },
  props: {
    value: Object,
    validityHidden: Boolean
  },
  data () {
    return {
      entry: {
        validity: {}
      },
      test: {}
    }
  },
  computed: {
    datePickerHidden () {
      return this.validity != null
    },

    facetPicker () {
      return {
        components: { MoFacetPicker },
        data () { return { val: null } },
        watch: { val (newVal) { this.$emit('input', newVal) } },
        template: `<div class="form-row"><mo-facet-picker facet="responsibility" v-model="val" required/></div>`
      }
    }
  },
  watch: {
    entry: {
      handler (newVal) {
        newVal.type = 'manager'
        this.$emit('input', newVal)
      },
      deep: true
    }
  },
  created () {
    this.entry = this.value
  }
}
</script>
