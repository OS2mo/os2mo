<template>
  <b-modal
    id="orgUnitRename"
    ref="orgUnitRename"
    size="lg"
    :title="$t('workflows.organisation.rename_unit')"
    @hidden="resetData"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="renameOrganisationUnit">
      <div class="form-row">
        <mo-organisation-unit-picker
          label="Enhed"
          class="col"
          v-model="original"
          required
        />
      </div>

      <div class="form-row">
        <mo-input
          v-model="rename.data.name"
          :label="$t('input_fields.new_name')"
          required
        />
      </div>

      <div class="form-row">
        <mo-date-picker-range
          class="col"
          v-model="rename.data.validity"
        />
      </div>

      <div class="alert alert-danger" v-if="compareName">
        {{$t('alerts.error.COMPARE_ORG_RENAME_NAMES')}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
/**
   * A organisation unit rename component.
   */

import OrganisationUnit from '@/api/OrganisationUnit'
import MoDatePickerRange from '@/components/MoDatePicker/MoDatePickerRange'
import MoOrganisationUnitPicker from '@/components/MoPicker/MoOrganisationUnitPicker'
import MoInput from '@/components/atoms/MoInput'
import ButtonSubmit from '@/components/ButtonSubmit'
import { mapGetters } from 'vuex'

export default {
  /**
       * Requesting a new validator scope to its children.
       */
  $_veeValidate: {
    validator: 'new'
  },

  components: {
    MoDatePickerRange,
    MoOrganisationUnitPicker,
    MoInput,
    ButtonSubmit
  },

  data () {
    return {
      /**
         * The rename, original, isLoading component value.
         * Used to detect changes and restore the value.
         */
      original: this.orgUnit,
      rename: {
        type: 'org_unit',
        data: {
          name: '',
          uuid: '',
          validity: {}
        }
      },
      isLoading: false
    }
  },

  computed: {
    /**
       * Get organisation unit
       */
    ...mapGetters({
      orgUnit: 'organisationUnit/GET_ORG_UNIT'
    }),

    /**
       * Loop over all contents of the fields object and check if they exist and valid.
       */
    formValid () {
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    },

    /**
       * Compare if the unit names are identical.
       * If then return false.
       */
    compareName () {
      if (this.rename.data.name && this.original.name) {
        if (this.original.name == null) return true
        if (this.rename.data.name === this.original.name) return true
      }
      return false
    }
  },

  watch: {
    /**
       * Whenever orgUnit changes, this function will run.
       */
    orgUnit: {
      handler (val) {
        this.original = val
        if (val) {
          this.rename.data.uuid = val.uuid
        }
      },
      deep: true
    },
    original (val) {
      this.rename.data.uuid = val && val.uuid
    }
  },

  mounted () {
    /**
       * After the entire view has been rendered.
       * Set original to orgUnit.
       */
    this.original = this.orgUnit
  },

  methods: {
    /**
       * Resets the data fields name and validity.
       */
    resetData () {
      this.rename.data.name = ''
      this.rename.data.uuid = this.original && this.original.uuid
      this.rename.data.validity = {}
    },

    /**
       * Rename a organisation unit and check if the data fields are valid.
       * Then throw a error if not.
       */
    renameOrganisationUnit (evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        vm.isLoading = true

        if (vm.compareName) {
          vm.isLoading = false
          return false
        }
        OrganisationUnit.rename(this.rename)
          .then(response => {
            vm.isLoading = false
            vm.$refs.orgUnitRename.hide()
          })
          .catch(err => {
            console.log(err)
            vm.isLoading = false
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
