<template>
  <div>
    <label v-if="!noLabel">{{label}}</label>

    <div class="input-group">
      <input
        :name="nameId"
        :data-vv-as="label"
        v-model="cprNo"
        class="form-control"
        type="text"
        maxlength="10"
        v-validate="{digits: 10, required: true, cpr: orgUuid}"
      />

      <button
        type="button"
        class="btn btn-outline-primary"
        @click="cprLookup()"
        :disabled="errors.has(nameId) || !cprNo"
        v-show="!isLoading">
        <icon name="search"/>
      </button>

      <mo-loader v-show="isLoading"/>
    </div>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>

    <div class="alert alert-danger" v-if="backendValidationError">
      {{$t('alerts.error.' + backendValidationError.error_key, backendValidationError)}}
    </div>
  </div>
</template>

<script>
/**
 * cpr search component.
 */

import Search from '@/api/Search'
import MoLoader from '@/components/atoms/MoLoader'
import { mapGetters } from 'vuex'
import { Organisation } from '@/store/actions/organisation'

export default {
  name: 'MoCprSearch',

  /**
   * Validator scope, sharing all errors and validation state.
   */
  inject: {
    $validator: '$validator'
  },

  components: {
    MoLoader
  },

  props: {
    /**
     * This boolean property defines a label if it does not have one.
     */
    noLabel: Boolean,

    /**
     * Defines a default label name.
     */
    label: { type: String, default: 'CPR nummer' },

    /**
     * This boolean property requires a valid cpr number.
     */
    required: Boolean
  },

  data () {
    return {
      /**
       * The nameId, cprNo, isloading, backendValidationError component value.
       * Used to detect changes and restore the value.
       */
      nameId: 'cpr-search',
      cprNo: '',
      isLoading: false,
      backendValidationError: null
    }
  },

  watch: {
    /**
     * Whenever cprNo change update.
     */
    cprNo () {
      this.$emit('input', {})
    }
  },

  computed: {
    /**
     * Get worklog message.
     */
    ...mapGetters({
      orgUuid: Organisation.getters.GET_UUID
    })
  },

  methods: {
    /**
     * Lookup cpr number and check if the data fields are valid.
     * Then throw a error if not.
     */
    cprLookup () {
      let vm = this
      vm.isLoading = true
      return Search.cprLookup(this.cprNo)
        .then(response => {
          vm.isLoading = false
          if (response.error) {
            vm.backendValidationError = response
          } else {
            vm.backendValidationError = null
            this.$emit('input', response)
          }
        })
    }
  }
}
</script>
