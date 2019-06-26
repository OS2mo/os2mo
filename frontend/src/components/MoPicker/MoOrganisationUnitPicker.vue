<template>
  <div class="form-group">
    <label :for="nameId">{{ label }}</label>
    <input
      :name="nameId"
      :id="nameId"
      :data-vv-as="label"
      :ref="nameId"
      type="text"
      class="form-control"
      autocomplete="off"
      :placeholder="label"
      v-model="orgName"
      @click.stop="toggleTree()"
      v-validate="validations"
    >

    <div class="mo-input-group" v-show="showTree">
      <mo-tree-view v-model="selectedSuperUnitUuid"
                    :at-date="validity && validity.from"/>
    </div>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
/**
 * A organisation unit picker component.
 */

import OrganisationUnit from '@/api/OrganisationUnit'
import MoTreeView from '@/components/MoTreeView/MoTreeView'
import { mapGetters } from 'vuex'
import { Organisation } from '@/store/actions/organisation'

export default {
  name: 'MoOrganisationUnitPicker',

  components: {
    MoTreeView
  },

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  props: {
    /**
     * Create two-way data bindings with the component.
     */
    value: Object,

    /**
     * Defines a default label name.
     */
    label: String,

    /**
     * This boolean property disable the value.
     */
    isDisabled: Boolean,

    /**
     * This boolean property requires a valid name.
     */
    required: Boolean,

    /**
     * An object of the validities, used for validation
     */
    validity: {
      type: [Object, undefined],
      required: false
    },

    /**
     * An object of additional validations to be performed
     */
    extraValidations: Object
  },

  data () {
    return {
      /**
       * The selectedSuperUnitUuid, showTree, orgName component value.
       * Used to detect changes and restore the value.
       */
      selectedSuperUnitUuid: null,
      showTree: false,
      orgName: null,
      orgUnitUuid: null
    }
  },

  computed: {
    /**
     * Get organisation uuid.
     */
    ...mapGetters({
      orgUuid: Organisation.getters.GET_UUID
    }),

    /**
     * Get name `org-unit`.
     */
    nameId () {
      return 'org-unit-' + this._uid
    },

    /**
     * When its not disable, make it required.
     */
    isRequired () {
      if (this.isDisabled) return false
      return this.required
    },

    validations () {
      let validations = {
        required: this.orgName !== null ? this.required : this.orgName,
        orgunit: [this.validity, this.orgUnitUuid]
      }
      if (this.extraValidations) {
        validations = { ...validations, ...this.extraValidations }
      }
      return validations
    }
  },

  watch: {
    /**
     * Whenever selectedSuperUnit change, update newVal.
     */
    async selectedSuperUnitUuid (newVal) {
      if (!newVal) {
        return
      }

      let unit = await OrganisationUnit.get(newVal, this.validity && this.validity.from)

      this.orgName = unit.name
      this.orgUnitUuid = unit.uuid
      this.$validator.validate(this.nameId)
      this.$refs[this.nameId].blur()
      this.showTree = false

      this.$emit('input', unit)
    },

    async validity (newVal, oldVal) {
      if (this.orgUnitUuid) {
        let unit = await OrganisationUnit.get(this.orgUnitUuid, newVal && newVal.from)

        if (!unit) {
          this.showTree = false
          this.orgName = null
          this.orgUnitUuid = null
          this.$emit('input', null)
        }
      }
    }
  },

  mounted () {
    /**
     * Called after the instance has been mounted.
     * Set selectedSuperUnitUuid as value.
     */
    this.selectedSuperUnitUuid = this.value ? this.value.uuid : this.selectedSuperUnitUuid
  },

  methods: {
    /**
     * Get selected oraganisation unit.
     */
    getSelectedOrganistionUnit () {
      this.orgUnit = OrganisationUnit.getSelectedOrganistionUnit()
    },

    /**
     * Set showTree to not show.
     */
    toggleTree () {
      this.showTree = !this.showTree
    }
  }
}
</script>

<style scoped>
  .form-group {
    position: relative;
  }
  .mo-input-group {
    z-index: 999;
    background-color: #fff;
    width: 100%;
    padding: 0.375rem 0.75rem;
    position: absolute;
    border: 1px solid #ced4da;
    border-radius: 0 0 0.25rem;
    transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
  }
</style>
