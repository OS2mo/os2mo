<template>
  <div class="input-group alert" :class="errors.has('cpr-result') ? 'alert-warning' : 'alert-success'" v-show="showAlert">
    <input data-vv-as="checkbox" :name="nameId" type="checkbox" v-validate="'required'" v-model="cprApproved">
    <h5>{{value.name}}</h5>
  </div>
</template>

<script>

export default {
  name: 'MoCprResult',
  inject: {
    $validator: '$validator'
  },
  props: {
    value: Object
  },
  data () {
    return {
      cprApproved: false
    }
  },
  mounted () {
    this.$validator.validate(this.nameId)
  },
  computed: {
    nameId () {
      return 'cpr-result'
    },
    showAlert () {
      return Object.keys(this.value).length > 0
    }
  },
  watch: {
    value () {
      this.cprApproved = false
      this.$validator.validate(this.nameId)
    }
  }
}
</script>
