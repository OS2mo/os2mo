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
        <tr>
          <th scope="col">Fortid</th>
        </tr>
        <tr v-for="d in detailsPast" v-bind:key="d.uuid">
          <td>{{d.name}}</td>
          <td>{{d.user_name}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>

        <tr>
          <th scope="col">Nutid</th>
        </tr>
        <tr v-for="d in details" v-bind:key="d.uuid">
          <td>{{d.name}}</td>
          <td>{{d.user_name}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
          <td>
            <!-- <mo-edit :uuid="uuid" :content="d" type="it"/> -->
          </td>
        </tr>

        <tr>
          <th scope="col">Fremtid</th>
        </tr>
        <tr v-for="d in detailsFuture" v-bind:key="d.uuid">
          <td>{{d.name}}</td>
          <td>{{d.user_name}}</td>
          <td>{{d.validity.from | moment('DD-MM-YYYY')}}</td>
          <td>{{d.validity.to | moment('DD-MM-YYYY')}}</td>
        </tr>
        </tbody>
    </table>
  </div>
</template>


<script>
  import Employee from '../../api/Employee'

  export default {
    components: {
    },
    props: {
      uuid: {
        type: String,
        required: true
      }
    },
    data () {
      return {
        details: [],
        detailsPast: [],
        detailsFuture: []
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
        Employee.getItDetails(this.uuid, 'past')
        .then(response => {
          vm.detailsPast = response
        })
        Employee.getItDetails(this.uuid, 'future')
        .then(response => {
          vm.detailsFuture = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

th{
  background-color: #ffffff;
}

</style>