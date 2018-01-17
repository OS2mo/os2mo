<template>
  <div class="card">
    <div class="card-body">
      <h4 class="card-title">
        <icon name="user-o"/>
        {{employee.name}} <span class="cpr">({{employee['user-key'] | CPRNumber}})</span>
      </h4>
      <div class="row">
        <div class="mr-auto">
        </div>
        <div>
          <button class="btn btn-outline-primary">
            <icon name="edit" />
          </button>
          <button class="btn btn-outline-primary">
            <icon name="eye" />
          </button>
          <button class="btn btn-outline-primary">
            <icon name="book" />
          </button>
        </div>
      </div>

      <ul class="nav nav-tabs">
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'EmployeeDetailEngagement' }">
            Engagement
          </router-link>
        </li>
        <li class="nav-item">
          <router-link class="nav-link" :to="{ name: 'EmployeeDetailContact' }">
            Kontakt
          </router-link>
        </li>
      </ul>

      <router-view/>
    </div>
  </div>
</template>

<script>
  import Employee from '../api/Employee'
  import '../filters/CPRNumber'

  export default {
    components: {
    },
    data () {
      return {
        employee: Object
      }
    },
    created () {
      this.getEmployee(this.$route.params.uuid)
    },
    methods: {
      getEmployee: function (uuid) {
        var vm = this
        Employee.getEmployee(uuid)
        .then(response => {
          vm.employee = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.router-link-active {
  color: #495057;
  background-color: #fff;
  border-color: #ddd #ddd #fff;
}

.cpr {
  color: #aaa
}

</style>
