<template>
<div>
  <button class="btn btn-outline-danger" v-b-modal="nameId">
    <icon name="ban" />
  </button>

  <b-modal
    class="mo-terminate-entry-dialog"
    :id="nameId"
    ref="functionTerminate"
    size="md"
    :title="title"
    @hidden="onHidden"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="terminate">
      <mo-input-date
        class="from-date"
        :label="$t('input_fields.end_date')"
        :valid-dates="validDates"
        v-model="validity.to"
        required
      />

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError.error_key, backendValidationError)}}
      </div>

      <div class="float-right">
        <button-submit :disabled="!formValid" :is-loading="isLoading"/>
      </div>
    </form>
  </b-modal>
</div>
</template>

<script>
/**
 * Terminate an entry, e.g. an association or engagement.
 */

import Service from '@/api/HttpCommon'
import { MoInputDate } from '@/components/MoInput'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'
import bModalDirective from 'bootstrap-vue/es/directives/modal/modal'
import moment from 'moment'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoInputDate,
    ButtonSubmit
  },

  directives: {
    'b-modal': bModalDirective
  },

  props: {
    type: {
      type: String,
      required: true
    },
    content: {
      type: Object,
      required: true
    }
  },

  data () {
    return {
      validity: {},
      backendValidationError: null,
      isLoading: false
    }
  },

  computed: {
    title () {
      let terminate = this.$t('common.terminate')
      let type = this.$tc('shared.' + this.type, 1)

      return `${terminate} ${type}`
    },

    nameId () {
      return 'moTerminate' + this._uid
    },

    payload () {
      return {
        type: this.type,
        uuid: this.content.uuid,
        validity: this.validity
      }
    },

    /**
     * Check if the organisation date are valid.
     */
    validDates () {
      return {
        from: moment().format('YYYY-MM-DD'),
        to: this.content.validity.to
      }
    }
  },

  methods: {
    onHidden () {
      Object.assign(this.$data, this.$options.data())
    },

    /**
     * Terminate a organisation unit and check if the data fields are valid.
     * Then throw a error if not.
     */
    terminate (evt) {
      evt.preventDefault()
      if (this.formValid) {
        this.isLoading = true

        return Service.post('/details/terminate', this.payload)
          .then(response => {
            this.isLoading = false
            this.$refs.functionTerminate.hide()
            this.$emit('submit')

            this.$store.commit('log/newWorkLog',
              { type: 'FUNCTION_TERMINATE',
                value: {
                  type: this.$tc(`shared.${this.type}`, 1),
                  uuid: this.payload.uuid,
                  date: this.payload.validity.to
                }
              },
              { root: true })
          })
          .catch(err => {
            this.backendValidationError = err.response.data
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>
