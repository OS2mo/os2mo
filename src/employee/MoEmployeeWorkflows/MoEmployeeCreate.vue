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
      <mo-cpr v-model="employee"/>

      <h5>{{$t('workflows.employee.labels.engagement')}}</h5>
      <mo-engagement-entry v-model="engagement"/>

      <h5>{{$tc('workflows.employee.labels.association', 2)}}</h5>
      <mo-add-many v-model="association" :entry-component="entry.association"/>
      
      <h5>{{$tc('workflows.employee.labels.role', 2)}}</h5>
      <mo-add-many v-model="role" :entry-component="entry.role"/>

      <h5>{{$tc('workflows.employee.labels.it_system', 2)}}</h5>
      <mo-add-many v-model="itSystem" :entry-component="entry.it"/>

      <h5>{{$tc('workflows.employee.labels.manager', 1)}}</h5>
      <mo-add-many v-model="manager" :entry-component="entry.manager"/>

    <div class="float-right">
      <button-submit :is-disabled="!formValid" :is-loading="isLoading" />
    </div>
    </form>
  </b-modal>
</template>

<script>
import Employee from '@/api/Employee'
import ButtonSubmit from '@/components/ButtonSubmit'
import MoCpr from '@/components/MoCpr/MoCpr'
import MoAddMany from '@/components/MoAddMany/MoAddMany'
import MoAssociationEntry from '@/components/MoEntry/MoAssociationEntry'
import MoEngagementEntry from '@/components/MoEntry/MoEngagementEntry'
import MoRoleEntry from '@/components/MoEntry/MoRoleEntry'
import MoItSystemEntry from '@/components/MoEntry/MoItSystemEntry'
import MoManagerEntry from '@/components/MoEntry/MoManagerEntry'

export default {
  $_veeValidate: {
    validator: 'new'
  },
  components: {
    ButtonSubmit,
    MoCpr,
    MoAddMany,
    MoAssociationEntry,
    MoEngagementEntry,
    MoRoleEntry,
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
        association: MoAssociationEntry,
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

      let newEmployee = {
        name: this.employee.name,
        cpr_no: this.employee.cpr_no,
        org: this.$store.state.organisation
      }

      Employee.new(newEmployee)
        .then(employeeUuid => {
          Employee.create(employeeUuid, create)
            .then(response => {
              vm.isLoading = false
              vm.$refs.employeeCreate.hide()
              vm.$router.push({name: 'EmployeeDetail', params: {uuid: employeeUuid}})
            })
        })
    }
  }
}
</script>
