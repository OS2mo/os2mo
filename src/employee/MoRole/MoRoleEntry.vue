<template>
  <div>
      <date-start-end v-model="role.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="role.org_unit"
        />
        <mo-facet-picker facet="role_type" v-model="role.role_type" label="Rolle"/>
      </div>
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
  props: {
    value: Object,
    validity: Object,
    validityHidden: Boolean
  },
  data () {
    return {
      role: {
        validity: {}
      }
    }
  },
  watch: {
    role: {
      handler (newVal) {
        newVal.type = 'role'
        this.$emit('input', newVal)
        let valid = false
        if (Object.keys(newVal).length >= 4 && newVal.validity.from !== undefined) valid = true
        this.$emit('is-valid', valid)
      },
      deep: true
    },

    validity (newVal) {
      this.role.validity = newVal
    }
  },
  created () {
    this.role = this.value
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
