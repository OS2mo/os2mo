<template>
<div>
  <div v-b-modal="nameId">
    <icon name="edit" class="icon"/>
  </div>

  <b-modal
    :id="nameId"
    ref="editNickname"
    size="md"
    :title="title"
    @hidden="onHidden"
    hide-footer
    lazy
    no-close-on-backdrop
  >
    <form @submit.stop.prevent="editNickname">
      <mo-input-text
        :label="$t('input_fields.nickname')"
        v-model="nickname"
        required
      />

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError.error_key)}}
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
 * Edit a nickname entry.
 */

import Service from '@/api/Employee'
import { MoInputText } from '@/components/MoInput'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'
import bModalDirective from 'bootstrap-vue/es/directives/modal/modal'

export default {
  mixins: [ValidateForm, ModalBase],

  components: {
    MoInputText,
    ButtonSubmit
  },

  directives: {
    'b-modal': bModalDirective
  },

  props: {
    content: {
      type: Object,
      required: true
    }
  },

  data () {
    return {
      nickname: undefined,
      backendValidationError: null,
      isLoading: false
    }
  },

  computed: {
    title () {
      let edit = this.$t('common.edit')
      let type = this.$tc('common.nickname')
      return `${edit} ${type}`
    },

    nameId () {
      return 'moEditNickname' + this._uid
    },

    payload () {
      return {
        type: this.type,
        nickname: this.nickname
      }
    }
  },

  methods: {
    onHidden () {
      Object.assign(this.$data, this.$options.data())
    },

    /**
     * Edit a nickname and check if the data fields are valid.
     * Then throw a error if not.
     */
    editNickname (evt) {
      evt.preventDefault()
      if (this.formValid) {
        this.isLoading = true

        return Service.edit(this.payload)
          .then(response => {
            this.isLoading = false
            this.$refs.editNickname.hide()
            this.$emit('submit')
          })
          .catch(err => {
            this.isLoading = false
            this.backendValidationError = err.response.data
          })
      } else {
        this.$validator.validateAll()
      }
    }
  }
}
</script>

<style scoped>
  .icon :hover{
    color: #007bff;
    cursor: pointer;
  }
</style>
