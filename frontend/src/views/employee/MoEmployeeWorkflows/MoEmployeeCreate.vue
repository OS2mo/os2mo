<template>
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
</template>

<script>
/**
 * A employee create component.
 */

import { mapFields } from 'vuex-map-fields'
import ButtonSubmit from '@/components/ButtonSubmit'
import MoCpr from '@/components/MoCpr'
import MoAddMany from '@/components/MoAddMany/MoAddMany'
import ValidateForm from '@/mixins/ValidateForm'
import { MoEmployeeAddressEntry, MoAssociationEntry, MoEngagementEntry, MoRoleEntry, MoItSystemEntry, MoManagerEntry } from '@/components/MoEntry'
import store from './_store/employeeCreate.js'

const STORE_KEY = '$_employeeCreate'

export default {
  mixins: [ValidateForm],

  components: {
    ButtonSubmit,
    MoCpr,
    MoAddMany,
    MoEngagementEntry
  },
  props: {
    show: {
      type: Boolean,
      default: false
    }
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
        address: MoEmployeeAddressEntry,
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
    ...mapFields(STORE_KEY, [
      'employee',
      'engagement',
      'address',
      'association',
      'role',
      'itSystem',
      'manager',
      'organisation',
      'backendValidationError'
    ])
  },
  beforeCreate () {
    if (!(STORE_KEY in this.$store._modules.root._children)) {
      this.$store.registerModule(STORE_KEY, store)
    }
  },
  beforeDestroy () {
    this.$store.unregisterModule(STORE_KEY)
  },

  watch: {
    show (val) {
      if (!val) {
        this.onHidden()
      }
    }
  },

  methods: {
    /**
     * Create a employee and check if the data fields are valid.
     * Then throw a error if not.
     */
    setOrganisation () {
      this.organisation = this.$store.getters['organisation/get']
    },
    createEmployee (evt) {
      this.setOrganisation()
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        this.isLoading = true

        this.$store.dispatch(`${STORE_KEY}/CREATE_EMPLOYEE`)
          .then(employeeUuid => {
            vm.isLoading = false
            if (employeeUuid.error) {
              vm.backendValidationError = employeeUuid.error_key
            } else {
              vm.$emit('submitted')
              vm.$router.push({ name: 'EmployeeDetail', params: { uuid: employeeUuid } })
            }
          })
      } else {
        this.$validator.validateAll()
      }
    },

    onHidden () {
      this.$store.dispatch(`${STORE_KEY}/resetFields`)
    }
  }
}
</script>
