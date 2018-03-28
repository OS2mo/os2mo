<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    hide-footer 
    title="Ny medarbejder"
    ref="employeeCreate"
    lazy
  >
      <employee-picker 
        :org="org" 
        v-model="employee" 
        required
      />
    <form data-vv-scope="engagement">
      <h4>Engagement</h4>
      <mo-engagement-entry
        :org="org" 
        v-model="engagement" 
      />
    </form>
    <form data-vv-scope="association">
      <h4>Tilknytning</h4>
      <mo-association-entry 
        :org="org"
        v-model="association"
        :validity="engagement.validity"
        validity-hidden
      />
    </form>
    <form data-vv-scope="role">
      <h4>Rolle</h4>
      <mo-role-entry
        :org="org" 
        v-model="role" 
        :validity="engagement.validity"
        validity-hidden
      />
    </form>
    <form data-vv-scope="itSystem">
      <h4>IT systemer</h4>
      <mo-it-system-entry 
        v-model="itSystem" 
        :validity="engagement.validity"
        validity-hidden
      />
    </form>
    <form data-vv-scope="manager">
      <h4>Leder</h4>
      <mo-manager-entry 
        v-model="manager" 
        :validity="engagement.validity" 
        validity-hidden
      />
    </form>

    <div class="float-right">
      <button-submit 
        :on-click-action="createEmployee" 
        :is-disabled="(!employeeValid || !engagementValid)" 
        :is-loading="isLoading"
      />
    </div>
  </b-modal>
</template>

<script>
import Organisation from '../../api/Organisation'
import Employee from '../../api/Employee'
import { EventBus } from '../../EventBus'
import ButtonSubmit from '../../components/ButtonSubmit'
import MoAssociationEntry from '../MoAssociation/MoAssociationEntry'
import MoEngagementEntry from '../MoEngagement/MoEngagementEntry'
import MoRoleEntry from '../MoRole/MoRoleEntry'
import EmployeePicker from '../../components/EmployeePicker'
import MoItSystemEntry from '../MoItSystem/MoItSystemEntry'
import MoManagerEntry from '../MoManager/MoManagerEntry'

export default {
  $_veeValidate: {
    validator: 'new'
  },
  components: {
    ButtonSubmit,
    MoAssociationEntry,
    MoEngagementEntry,
    MoRoleEntry,
    EmployeePicker,
    MoItSystemEntry,
    MoManagerEntry
  },
  data () {
    return {
      employee: {},
      org: {},
      engagement: {},
      association: {},
      role: {},
      itSystem: {},
      manager: {},
      isLoading: false
    }
  },
  computed: {
    employeeValid () {
      return this.fields['employee-picker']
    },

    engagementValid () {
      return this.formValid('$engagement')
    }
  },
  created () {
    this.org = Organisation.getSelectedOrganisation()
  },
  mounted () {
    EventBus.$on('organisation-changed', newOrg => {
      this.org = newOrg
    })
    this.$root.$on('bv::modal::hidden', resetData => {
      Object.assign(this.$data, this.$options.data())
    })
  },
  methods: {
    formValid (scope) {
      // loop over all contents of the fields object and check if they exist and valid.
      return Object.keys(this.fields[scope]).every(field => {
        return this.fields[scope][field] && this.fields[scope][field].valid
      })
    },

    createEmployee () {
      let vm = this
      let create = []
      this.isLoading = true

      let forms = ['engagement', 'association', 'role', 'itSystem', 'manager']

      forms.forEach(form => {
        if (this.formValid('$' + form)) create.push(this[form])
      })

      Employee.create(this.employee.uuid, create)
        .then(response => {
          vm.isLoading = false
          vm.$refs.employeeCreate.hide()
          vm.$router.push({name: 'EmployeeDetail', params: {uuid: vm.employee.uuid}})
        })
        .catch(err => {
          console.log(err)
          vm.isLoading = false
        })
    }
  }
}
</script>
