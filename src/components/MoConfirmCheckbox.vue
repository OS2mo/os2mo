<template>
  <div class="input-group alert" :class="errors.has('confirm') ? 'alert-warning' : 'alert-success'">
    <input :name="nameId" type="checkbox" v-validate="'required'" v-model="confirm">
    <h5>{{$t('alerts.error.CONFIRM_ENGAGEMENT_END_DATE', 
      {engagementName: entryName,
      orgName: entryOrgName, 
      endDate: $moment(entryDate).subtract(1, 'd').format('DD-MM-YYYY')})}}
    </h5>
  </div>
</template>

<script>

export default {
  name: 'MoConfirmCheckbox',
  inject: {
    $validator: '$validator'
  },
  props: {
    entryDate: [Date, String],
    entryName: String,
    entryOrgName: String
  },
  data () {
    return {
      confirm: false
    }
  },
  mounted () {
    this.$validator.validate(this.nameId)
  },
  computed: {
    nameId () {
      return 'confirm'
    }
  },
  watch: {
    value () {
      this.confirm = false
      this.$validator.validate(this.nameId)
    }
  }
}
</script>
