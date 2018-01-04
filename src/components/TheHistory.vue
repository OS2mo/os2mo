<template>
  <div>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Dato</th>
          <th scope="col">Sektion</th>
          <th scope="col">Handling</th>
          <th scope="col">Objekt</th>
          <th scope="col">Ændringer aktive fra</th>
          <th scope="col">Udført af</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="h in history" v-bind:key="h.date">
          <td>{{h.date | moment("DD-MM-YYYY")}}</td>
          <td>{{h.section}}</td>
          <td>{{h.action}}</td>
          <td>{{h.object}}</td>
          <td>{{h.from | moment("DD-MM-YYYY")}}</td>
          <td>{{h.changedBy}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import Employee from '../api/Employee'

  export default {
    data () {
      return {
        history: []
      }
    },
    created: function () {
      this.getHistory()
    },
    methods: {
      getHistory () {
        var vm = this
        Organisation.getHistory(this.$route.params.uuid)
        .then(function (response) {
          vm.history = response
        })
      },

      getEmployeeName (uuid) {
        return Employee.getEmployee(uuid)
        .then(response => {
          return response.name
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>