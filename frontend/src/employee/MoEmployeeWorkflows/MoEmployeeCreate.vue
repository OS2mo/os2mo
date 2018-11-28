<template>
  <b-modal
    id="employeeCreate"
    size="lg"
    :title="$t('workflows.employee.new_employee')"
    ref="employeeCreate"
    @hidden="$store.dispatch('employeeCreate/resetFields')"
    hide-footer
    no-close-on-backdrop
    lazy
  >
    <form @submit.stop.prevent="createEmployee">
      <mo-cpr v-model="employee"/>

      <h5 class="mt-3">{{$t('workflows.employee.labels.engagement')}}</h5>
      <mo-engagement-entry v-model="engagement"/>

      <mo-add-many
        class="btn-address mt-3"
        v-model="address"
        :entry-component="entry.address"
        :label="$tc('workflows.employee.labels.address', 2)"
        validity-hidden
      />

      <mo-add-many
        class="btn-association mt-3"
        v-model="association"
        :entry-component="entry.association"
        :label="$tc('workflows.employee.labels.association', 2)"
        validity-hidden
      />

      <mo-add-many
        class="btn-role mt-3"
        v-model="role"
        :entry-component="entry.role"
        :label="$tc('workflows.employee.labels.role', 2)"
        validity-hidden
      />

      <mo-add-many
        class="btn-itSystem mt-3"
        v-model="itSystem"
        :entry-component="entry.it"
        :label="$tc('workflows.employee.labels.it_system', 2)"
        validity-hidden
      />

      <mo-add-many
        class="btn-manager mt-3"
        v-model="manager"
        :entry-component="entry.manager"
        :label="$tc('workflows.employee.labels.manager')"
        validity-hidden
      />

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
/**
   * A employee create component.
   */

import { mapFields } from 'vuex-map-fields'
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
  /**
       * Requesting a new validator scope to its children.
       */
  $_veeValidate: {
    validator: 'new'
  },

  components: {
    ButtonSubmit,
    MoCpr,
    MoAddMany,
    MoEngagementEntry
  },

  data () {
    return {
      /**
        * The isLoading component value.
        * Used to detect changes and restore the value.
        */
      isLoading: false,

      /**
        * The entry - address, association, role, it, manager component.
        * Used to add MoAddressEntry, MoAssociationEntry, MoRoleEntry,
        * MoItSystemEntry, MoManagerEntry component in `<mo-add-many/>`.
        */
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
    /**
       * Get mapFields from vuex store.
       */
    ...mapFields('employeeCreate', [
      'employee',
      'engagement',
      'address',
      'association',
      'role',
      'itSystem',
      'manager',
      'backendValidationError'
    ]),

    /**
       * Loop over all contents of the fields object and check if they exist and valid.
       */
    formValid () {
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    }
  },

  methods: {
    /**
       * Create a employee and check if the data fields are valid.
       * Then throw a error if not.
       */
    createEmployee (evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        this.isLoading = true

        this.$store.dispatch('employeeCreate/CREATE_EMPLOYEE')
          .then(employeeUuid => {
            if (employeeUuid.error) {
              vm.isLoading = false
              vm.backendValidationError = employeeUuid.error_key
            } else {
              vm.$refs.employeeCreate.hide()
              vm.$router.push({ name: 'EmployeeDetail', params: { uuid: employeeUuid } })
              vm.isLoading = false
            }
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
