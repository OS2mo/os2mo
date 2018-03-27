<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    hide-footer 
    title="Ny medarbejder"
    ref="employeeCreate"
    lazy
  >
    <employee-picker :org="org" v-model="employee" required/>
    
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
      validity-hidden
    />
    <h4>Rolle</h4>
    <mo-role-entry
      :org="org" 
      v-model="role" 
      :validity="engagement.validity"
      @is-valid="isRoleValid"
      validity-hidden
    />
    <h4>IT systemer</h4>
    <mo-it-system-entry 
      v-model="itSystem" 
      :validity="engagement.validity"
      @is-valid="isItSystemValid"
      validity-hidden
    />
    <h4>Leder</h4>
    <mo-manager-entry 
      v-model="manager" 
      :validity="engagement.validity" 
      @is-valid="isManagerValid"
      validity-hidden
    />

    <div class="float-right">
      <button-submit 
        :on-click-action="createEmployee" 
        :is-disabled="isDisabled" 
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
      isLoading: false,
      valid: {
        engagement: false,
        association: false,
        role: false,
        itSystem: false,
        manager: false
      }
    }
  },
  computed: {
    isDisabled () {
      let emp = Object.keys(this.employee).length > 0
      let ass = Object.keys(this.association).length > 2
      let role = Object.keys(this.role).length > 3
      let it = Object.keys(this.itSystem).length > 3
      let man = Object.keys(this.manager).length > 2
      return (!emp || !this.valid.engagement ||
              (ass ? !this.valid.association : false) ||
              (role ? !this.valid.role : false) ||
              (it ? !this.valid.itSystem : false) ||
              (man ? !this.valid.manager : false))
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
    isEngagementValid (val) {
      this.valid.engagement = val
    },

    isAssociationValid (val) {
      this.valid.association = val
    },

    isRoleValid (val) {
      this.valid.role = val
    },

    isItSystemValid (val) {
      this.valid.itSystem = val
    },

    isManagerValid (val) {
      this.valid.manager = val
    },

    createEmployee () {
      let vm = this
      let create = []
      this.isLoading = true

      if (this.valid.engagement) create.push(this.engagement)
      if (this.valid.association) create.push(this.association)
      if (this.valid.role) create.push(this.role)
      if (this.valid.itSystem) create.push(this.itSystem)
      if (this.valid.manager) create.push(this.manager)

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
