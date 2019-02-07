<template>
  <b-modal
    id="orgUnitCreate"
    size="lg"
    :title="$t('workflows.organisation.create_unit')"
    ref="orgUnitCreate"
    @hidden="resetData"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="createOrganisationUnit">
      <mo-organisation-unit-entry
        v-model="entry"
        :creating-date="true"
      />

      <h5 class="mt-3">{{$tc('workflows.employee.labels.address', 2)}}</h5>
      <mo-org-unit-address-entry
        class="mt-3"
        v-model="postAddress"
        preselected-type="AdressePost"
        validity-hidden
        required
      />

      <div class="mt-3 form-row">
        <mo-org-unit-address-entry
          class="col"
          v-model="phone"
          preselected-type="Telefon"
          validity-hidden
          required
        />

        <mo-facet-picker
          class="col"
          facet="address_property"
          v-model="phone.visibility"
          preselectedType
          required
        />
      </div>

      <mo-add-many
        class="mt-3"
        :entry-component="addressEntry"
        :label="$tc('workflows.employee.labels.other_addresses')"
        v-model="addresses"
        validity-hidden
      />

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</template>

<script>
/**
 * A organisation unit create component
 */

import OrganisationUnit from '@/api/OrganisationUnit'
import ButtonSubmit from '@/components/ButtonSubmit'
import { MoOrganisationUnitEntry, MoOrgUnitAddressEntry } from '@/components/MoEntry'
import MoFacetPicker from '@/components/MoPicker/MoFacetPicker'
import MoAddMany from '@/components/MoAddMany/MoAddMany'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'

export default {
  name: 'OrganisationUnitCreate',
  mixins: [ValidateForm, ModalBase],

  components: {
    ButtonSubmit,
    MoOrganisationUnitEntry,
    MoOrgUnitAddressEntry,
    MoFacetPicker,
    MoAddMany
  },

  data () {
    return {
      /**
       * The entry, postAddress, phone, addresses, isLoading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      entry: {
        validity: {}
      },
      addresses: [],
      postAddress: {},
      phone: {
        visibility: {}
      },
      isLoading: false,
      backendValidationError: null,

      /**
       * The addressEntry component.
       * Used to add MoAddressEntry component in `<mo-add-many/>`.
       */
      addressEntry: MoOrgUnitAddressEntry
    }
  },

  methods: {
    /**
     * Resets the data fields.
     */
    resetData () {
      Object.assign(this.$data, this.$options.data())
    },

    /**
     * Create a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    createOrganisationUnit (evt) {
      evt.preventDefault()
      if (this.formValid) {
        let vm = this
        this.isLoading = true

        this.addresses.push(this.postAddress, this.phone)
        this.addresses.forEach(a => {
          if (!a.validity) {
            a.validity = this.entry.validity
          }
          a.org = this.$store.getters['organisation/GET_ORGANISATION']
        })
        this.entry.details = this.addresses

        OrganisationUnit.create(this.entry)
          .then(response => {
            vm.isLoading = false
            if (response.error) {
              vm.backendValidationError = response.error_key
            } else {
              vm.$refs.orgUnitCreate.hide()
            }
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
