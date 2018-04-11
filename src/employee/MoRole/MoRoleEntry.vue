<template>
  <div>
      <mo-date-picker-range v-model="role.validity" :initially-hidden="validityHidden"/>
      <div class="form-row">
        <organisation-unit-picker class="col" label="Vælg enhed" v-model="role.org_unit"/>
        <mo-facet-picker facet="role_type" v-model="role.role_type" required/>
      </div>
  </div>
</template>

<script>
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'

export default {
  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
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
