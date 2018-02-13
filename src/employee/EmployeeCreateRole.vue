<template>
  <div>
      <h4>Rolle</h4>
      <date-start-end v-model="role.validity" initially-hidden/>
      <div class="form-row">
        <organisation-unit-picker 
          class="col" 
          label="Vælg enhed"
          v-model="role.org_unit"
        />
        <role-picker 
        :org="org" 
        v-model="role.role_type"
        />
      </div>
  </div>
</template>

<script>
import DateStartEnd from '../components/DatePickerStartEnd'
import OrganisationUnitPicker from '../components/OrganisationUnitPicker'
import RolePicker from '../components/RolePicker'

export default {
  components: {
    DateStartEnd,
    OrganisationUnitPicker,
    RolePicker
  },
  props: {
    value: Object,
    org: {
      type: Object,
      required: true
    },
    validity: Object
  },
  data () {
    return {
      role: {
        type: 'role',
        validity: {}
      }
    }
  },
  watch: {
    role (newVal, oldVal) {
      this.$emit('input', newVal)
    },

    validity (newVal) {
      this.role.validity = newVal
    }
  },
  methods: {
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
