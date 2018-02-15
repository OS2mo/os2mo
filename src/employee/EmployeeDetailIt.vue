<template>
  <div>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">System</th>
          <th scope="col">Brugernavn</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td>{{d.name}}</td>
          <td>{{d.user_name}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
          <td>
            <mo-edit :uuid="uuid" :content="d" type="it"/>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../api/Employee'
  import MoEdit from './MoEdit/MoEdit'

  export default {
    components: {
      MoEdit
    },
    props: {
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        details: []
      }
    },
    created () {
      this.getDetails()
    },
    methods: {
      getDetails () {
        var vm = this
        Employee.getItDetails(this.uuid)
        .then(response => {
          vm.details = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>