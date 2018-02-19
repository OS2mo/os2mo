<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    hide-footer 
    title="Ny medarbejder"
    ref="employeeCreate"
  >
    <div class="form-row">
      <employee-picker :org="org" v-model="employee"/>
    </div>
    <h4>Engagement</h4>
    <mo-engagement-entry
      :org="org" 
      v-model="engagement" 
      @is-valid="isEngagementValid"
    />
    <h4>Tilknytning</h4>
    <mo-association-entry 
      :org="org"
      v-model="association"
      :validity="engagement.validity"
      @is-valid="isAssociationValid"
    />
    <h4>Rolle</h4>
    <mo-role-entry
      :org="org" 
      v-model="role" 
      :validity="engagement.validity"
    />
    <h4>IT systemer</h4>
    <mo-it-system-entry v-model="itSystem" :validity="engagement.validity"/>

    <div class="float-right">
      <button-submit :on-click-action="createEmployee" :is-disabled="isDisabled" :is-loading="isLoading"/>
    </div>
  </b-modal>

</template>

<script>
import Organisation from '../api/Organisation'
import Employee from '../api/Employee'
import { EventBus } from '../EventBus'
import ButtonSubmit from '../components/ButtonSubmit'
import MoAssociationEntry from './MoAssociation/MoAssociationEntry'
import MoEngagementEntry from './MoEngagement/MoEngagementEntry'
import MoRoleEntry from './MoRole/MoRoleEntry'
import EmployeePicker from '../components/EmployeePicker'
import MoItSystemEntry from './MoItSystem/MoItSystemEntry'

export default {
  components: {
    ButtonSubmit,
    MoAssociationEntry,
    MoEngagementEntry,
    MoRoleEntry,
    EmployeePicker,
    MoItSystemEntry
  },
  data () {
    return {
      employee: {},
      org: {},
      engagement: {},
      association: {},
      role: {},
      itSystem: {},
      isLoading: false,
      valid: {
        engagement: false,
        association: false,
        role: false
      }
    }
  },
  computed: {
    isDisabled () {
      let emp = Object.keys(this.employee).length > 0
      let ass = Object.keys(this.association).length > 2
      let role = Object.keys(this.role).length > 2
      return (!emp || !this.valid.engagement || (ass ? !this.valid.association : false) || (role ? !this.valid.role : false))
    }
  },
  created () {
    this.org = Organisation.getSelectedOrganisation()
  },
  mounted () {
    EventBus.$on('organisation-changed', newOrg => {
      this.org = newOrg
    })
  },
  methods: {
    isEngagementValid (val) {
      this.valid.engagement = val
    },

    isAssociationValid (val) {
      this.valid.association = val
    },

    isRoleValid (val) {
      this.valid.association = val
    },

    createEmployee () {
      let vm = this
      let create = []
      this.isLoading = true

      if (Object.keys(this.engagement).length === 5) {
        create.push(this.engagement)
      }

      if (Object.keys(this.association).length === 5) {
        create.push(this.association)
      }

      if (Object.keys(this.role).length === 4) {
        create.push(this.role)
      }

      if (Object.keys(this.itSystem).length === 3) {
        create.push(this.itSystem)
      }

      Employee.create(this.employee.uuid, create)
      .then(response => {
        vm.isLoading = false
        vm.$refs.employeeCreate.hide()
      })
      .catch(err => {
        console.log(err)
        vm.isLoading = false
      })
    }
  }
}
</script>
