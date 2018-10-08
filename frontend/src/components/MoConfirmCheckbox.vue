<template>
  <div 
    class="input-group alert" 
    :class="errors.has('confirm') ? 'alert-warning' : 'alert-success'"
  >
    <input 
      data-vv-as="checkbox" 
      :name="nameId" 
      type="checkbox" 
      v-validate="'required'" 
      v-model="confirm"
    >

    <h5>{{$t('alerts.error.CONFIRM_ENGAGEMENT_END_DATE', 
      {engagementName: entryName,
      orgName: entryOrgName, 
      endDate: $moment(entryDate).subtract(1, 'd').format('DD-MM-YYYY')})}}
    </h5>
  </div>
</template>

<script>
  /**
   * A confirm checkbox component.
   */

  export default {
    name: 'MoConfirmCheckbox',

      /**
       * Validator scope, sharing all errors and validation state.
       */
    inject: {
      $validator: '$validator'
    },

    props: {
      /**
       * Defines a entry date.
       */
      entryDate: [Date, String],

      /**
       * Defines a entry name.
       */
      entryName: String,

      /**
       * Defines a entry OrgName.
       */
      entryOrgName: String
    },

    data () {
      return {
      /**
       * The confirm component value.
       * Used to detect changes and restore the value.
       */
        confirm: false
      }
    },

    mounted () {
      /**
       * Called after the instance has been mounted.
       * When it change validate.
       */
      this.$validator.validate(this.nameId)
    },

    computed: {
      /**
       * Get default name.
       */
      nameId () {
        return 'confirm'
      }
    },

    watch: {
      /**
       * Whenever value change validate.
       */
      value () {
        this.confirm = false
        this.$validator.validate(this.nameId)
      }
    }
  }
</script>
