<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    title="Ny medarbejder"
    ref="employeeCreate"
    hide-footer 
    lazy
  >
    <form @submit.stop.prevent="createEmployee()">
    <employee-picker v-model="employee" required/>
      <h5>Engagement</h5>
      <mo-engagement-entry v-model="engagement"/>

      <h5>Tilknytninger</h5>
      <mo-add-many v-model="association" :entry-component="entry.engagement"/>
      
      <h5>Roller</h5>
      <mo-add-many v-model="role" :entry-component="entry.role"/>

      <h5>IT systemer</h5>
      <mo-add-many v-model="itSystem" :entry-component="entry.it"/>

      <h5>Leder</h5>
      <mo-add-many v-model="manager" :entry-component="entry.manager"/>

    <div class="float-right">
      <button-submit :is-disabled="!formValid" :is-loading="isLoading" />
    </div>
    </form>
  </b-modal>
</template>

<script>
import Employee from '../../api/Employee'
import ButtonSubmit from '../../components/ButtonSubmit'
import MoAddMany from '../../components/MoAddMany'
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
    MoAddMany,
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
      engagement: {},
      association: [],
      role: [],
      itSystem: [],
      manager: [],
      isLoading: false,
      entry: {
        engagement: MoEngagementEntry,
        role: MoRoleEntry,
        it: MoItSystemEntry,
        manager: MoManagerEntry
      }
    }
  },
  computed: {
    formValid () {
      // loop over all contents of the fields object and check if they exist and valid.
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    }
  },
  mounted () {
    this.$root.$on('bv::modal::hidden', resetData => {
      Object.assign(this.$data, this.$options.data())
    })
  },
  methods: {
    createEmployee () {
      let vm = this
      this.isLoading = true
      let create = [].concat(this.engagement, this.association, this.role, this.itSystem, this.manager)

      Employee.create(this.employee.uuid, create)
        .then(response => {
          vm.isLoading = false
          vm.$refs.employeeCreate.hide()
          vm.$router.push({name: 'EmployeeDetail', params: {uuid: vm.employee.uuid}})
        })
    }
  }
}
</script>
