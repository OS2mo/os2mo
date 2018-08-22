<template>
  <b-modal 
    id="employeeCreate" 
    size="lg" 
    :title="$t('workflows.employee.new_employee')"
    ref="employeeCreate"
    hide-footer 
    no-close-on-backdrop
    @hidden="resetData"
    lazy
  >
    <form @submit.stop.prevent="createEmployee">
      <mo-cpr v-model="employee"/>

      <h5 class="mt-3">{{$t('workflows.employee.labels.engagement')}}</h5>
      <mo-engagement-entry v-model="engagement"/>

      <mo-add-many class="btn-address" v-model="address" :entry-component="entry.address" :label="$tc('workflows.employee.labels.address', 2)" validity-hidden/>

      <mo-add-many class="btn-association" v-model="association" :entry-component="entry.association" :label="$tc('workflows.employee.labels.association', 2)" validity-hidden/>
      
      <mo-add-many class="btn-role" v-model="role" :entry-component="entry.role" :label="$tc('workflows.employee.labels.role', 2)" validity-hidden/>

      <mo-add-many class="btn-itSystem" v-model="itSystem" :entry-component="entry.it" :label="$tc('workflows.employee.labels.it_system', 2)" validity-hidden/>

      <mo-add-many class="btn-manager" v-model="manager" :entry-component="entry.manager" :label="$tc('workflows.employee.labels.manager')" validity-hidden/>

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

    <div class="float-right">
      <button-submit :is-loading="isLoading" />
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
import MoAddressEntry from '@/components/MoEntry/MoAddressEntry'

export default {
  $_veeValidate: {
    validator: 'new'
  },
  components: {
    ButtonSubmit,
    MoCpr,
    MoAddMany,
    MoAddressEntry,
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
      address: [],
      association: [],
      role: [],
      itSystem: [],
      manager: [],
      isLoading: false,
      backendValidationError: null,
      entry: {
        address: MoAddressEntry,
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
  methods: {
    resetData () {
      Object.assign(this.$data, this.$options.data())
    },

    createEmployee (evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        this.isLoading = true
        let create = [].concat(this.address, this.association, this.role, this.itSystem, this.manager)

        create.forEach(e => {
          if (!e.validity) {
            e.validity = this.engagement.validity
          }
        })
        create.push(this.engagement)

        let newEmployee = {
          name: this.employee.name,
          cpr_no: this.employee.cpr_no,
          org: this.$store.state.organisation
        }

        Employee.new(newEmployee)
          .then(employeeUuid => {
            vm.isLoading = false
            if (employeeUuid.error) {
              vm.backendValidationError = employeeUuid.error_key
              return
            }
            Employee.create(employeeUuid, create)
              .then(response => {
                vm.isLoading = false
                if (response.error) {
                  vm.backendValidationError = response.error_key
                } else {
                  vm.$refs.employeeCreate.hide()
                  vm.$router.push({name: 'EmployeeDetail', params: {uuid: employeeUuid}})
                }
              })
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
