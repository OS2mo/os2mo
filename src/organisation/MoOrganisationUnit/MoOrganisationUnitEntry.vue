<template>
  <div>
      <date-start-end v-model="entry.validity"/>

      <div class="form-row">
      <div class="form-group col">
        <label for="">Navn</label>
        <input 
          v-model="entry.name" 
          data-vv-as="Navn"
          type="text" 
          class="form-control"
          name="unit-name"
          v-validate="{required: true}"
        >
            <span
              v-show="errors.has('unit-name')" 
              class="text-danger"
            >
              {{ errors.first('unit-name') }}
          </span>
      </div>
      
      <mo-facet-picker 
        facet="org_unit_type" 
        v-model="entry.org_unit_type"
        required
      />
      </div>
      
      <organisation-unit-picker 
        v-model="entry.parent"
        :is-disabled="disableOrgUnitPicker"
      />
  </div>
</template>

<script>
import DateStartEnd from '../../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../../components/OrganisationUnitPicker'
import MoFacetPicker from '../../components/MoFacetPicker'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    MoFacetPicker
  },
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object,
    disableOrgUnitPicker: Boolean
  },
  data () {
    return {
      entry: {
        name: '',
        validity: {}
      }
    }
  },
  watch: {
    entry: {
      handler (newVal) {
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
