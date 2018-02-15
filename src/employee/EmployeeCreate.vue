<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    hide-footer 
    title="Ny medarbejder"
    ref="employeeCreate"
  >

    <employee-picker :org="org" v-model="employee"/>
    <employee-create-engagement :org="org" v-model="engagement"/>
    <employee-create-association :org="org" v-model="association" :validity="engagement.validity"/>
    <employee-create-role :org="org" v-model="role" :validity="engagement.validity"/>
    <h4>IT systemer</h4>
    <mo-it-system v-model="itSystem" :validity="engagement.validity"/>

    <div class="float-right">
      <button-submit @click.native="createEmployee" :is-loading="isLoading"/>
    </div>
  </b-modal>

</template>

<script>
import Organisation from '../api/Organisation'
import Employee from '../api/Employee'
import { EventBus } from '../EventBus'
import ButtonSubmit from '../components/ButtonSubmit'
import EmployeeCreateAssociation from './EmployeeCreateAssociation'
import EmployeeCreateEngagement from './EmployeeCreateEngagement'
import EmployeeCreateRole from './EmployeeCreateRole'
import EmployeePicker from '../components/EmployeePicker'
import MoItSystem from './MoItSystem/MoItSystem'

export default {
  components: {
    ButtonSubmit,
    EmployeeCreateAssociation,
    EmployeeCreateEngagement,
    EmployeeCreateRole,
    EmployeePicker,
    MoItSystem
  },
  data () {
    return {
      employee: {},
      org: {},
      engagement: {},
      association: {},
      role: {},
      itSystem: {},
      isLoading: false
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
    createEmployee () {
      let vm = this
      let create = []
      this.isLoading = true

      if (Object.keys(this.engagement).length > 0) {
        create.push(this.engagement)
      }

      if (Object.keys(this.association).length > 0) {
        create.push(this.association)
      }

      if (Object.keys(this.role).length > 0) {
        create.push(this.role)
      }

      if (Object.keys(this.itSystem).length > 0) {
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
