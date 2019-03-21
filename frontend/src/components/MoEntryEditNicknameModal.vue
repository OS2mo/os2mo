<template>
<div>
    <button class="row button" v-b-modal="nameId">
      <icon name="edit"/>
    </button>

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
      <div class="form-group">
        <mo-input-text
          :label="$t('input_fields.nickname')"
          v-model="nickname"
          required
        />
      </div>

      <div class="alert alert-danger" v-if="backendValidationError">
        {{$t('alerts.error.' + backendValidationError.error_key)}}
      </div>

      <div class="col">
        <div class="float-right">
          <button-submit :disabled="!formValid" :is-loading="isLoading"/>
        </div>
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
import { EventBus, Events } from '@/EventBus'
import { MoInputText } from '@/components/MoInput'
import ButtonSubmit from '@/components/ButtonSubmit'
import ValidateForm from '@/mixins/ValidateForm'
import ModalBase from '@/mixins/ModalBase'
import bModalDirective from 'bootstrap-vue/es/directives/modal/modal'
import { mapState, mapGetters } from 'vuex'
import { Employee } from '@/store/actions/employee'
import moment from 'moment'

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
    ...mapState({
      route: 'route'
    }),

    ...mapGetters({
      employee: Employee.getters.GET_EMPLOYEE
    }),

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
        type: 'employee',
        uuid: this.content.uuid,
        data: {
          validity: {
            from: moment().format('YYYY-MM-DD')
          },
          nickname: this.nickname
        }
      }
    }
  },

  created () {
    this.$store.dispatch(Employee.actions.SET_EMPLOYEE, this.$route.params.uuid)
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
            EventBus.$emit(Events.EMPLOYEE_CHANGED)
            this.isLoading = false
            this.$refs.editNickname.hide()
            this.$emit('submit')

            this.$store.commit('log/newWorkLog',
              { type: 'EMPLOYEE_EDIT',
                value: {
                  type: this.$tc(`shared.${this.payload.type}`, 1),
                  uuid: this.payload.uuid
                }
              },
              { root: true })
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
  .button {
    color: #aaa;
    background-color: #fff;
    border: none;
    text-decoration: none;
    display: inline-block;
    cursor: pointer;
  }
  .button :hover{
    color: #007bff;
  }
</style>
