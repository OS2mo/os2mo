<template>
  <div class="form-row">
    <div v-show="hidden">
      <button class="btn btn-link" @click="hidden=false">
        Vælg anden dato
      </button>
    </div>
    <mo-date-picker 
      label="Startdato"
      v-model="validFrom"
      v-show="!hidden"
      :disabled-from="validTo"
      @input="updateDate()"
      required
    />

    <mo-date-picker 
      label="Slutdato"
      v-model="validTo"
      v-show="!hidden"
      :disabled-to="validFrom"
      @input="updateDate()"
    />
  </div>
</template>

<script>
  import MoDatePicker from './MoDatePicker'

  export default {
    components: {
      MoDatePicker
    },
    props: {
      value: Object,
      initiallyHidden: Boolean
    },
    data () {
      return {
        validFrom: null,
        validTo: null,
        hidden: false
      }
    },
    watch: {
      value: {
        handler (newVal) {
          if (this.hidden) {
            this.validFrom = newVal.from
            this.validTo = newVal.to
          }
        },
        deep: true
      }
    },
    created () {
      this.hidden = this.initiallyHidden
      if (this.value !== undefined) {
        this.validFrom = this.value.from
        this.validTo = this.value.to
      }
    },
    methods: {
      updateDate () {
        let obj = {
          from: null,
          to: null
        }
        if (this.validFrom) {
          obj.from = this.validFrom
        }

        if (this.validTo) {
          obj.to = this.validTo
        }

        this.$emit('input', obj)
      }
    }
  }
</script>
