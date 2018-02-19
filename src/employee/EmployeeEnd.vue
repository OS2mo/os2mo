<template>
<b-modal 
    id="employeeEnd" 
    size="lg" 
    hide-footer 
    title="Afslut medarbejder"
    ref="employeeEnd"
  >
  <div class="col">
      <div class="form-row">
        <date-picker label="Slutdato" v-model="validFrom"/>
      </div>
      <div class="float-right">
        <button-submit :on-click-action="endEmployee"/>
      </div>
  </div>
</b-modal>
</template>

<script>
  import DatePicker from '../components/DatePicker'
  import ButtonSubmit from '../components/ButtonSubmit'
  import Employee from '../api/Employee'

  export default {
    components: {
      DatePicker,
      ButtonSubmit
    },
    data () {
      return {
        validFrom: null,
        engagement: {}
      }
    },
    created: function () {},
    methods: {
      endEmployee () {
        let vm = this
        let terminate = {
          valid_from: this.validFrom
        }
        Employee.terminate(this.$route.params.uuid, terminate)
        .then(response => {
          vm.$refs.employeeEnd.hide()
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>