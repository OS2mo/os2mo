<template>
  <div>
    <button class="btn btn-outline-primary" v-b-modal.theHistory>
      <icon name="book" />
    </button>

    <b-modal 
      id="theHistory" 
      size="lg" 
      title="Historik"
      @change="reloadHistory"
      hide-footer 
      lazy
    >
      <table class="table table-striped">
        <thead>
          <tr>
            <th scope="col">Dato</th>
            <th scope="col">Sektion</th>
            <th scope="col">Handling</th>
            <th scope="col">Udført af</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in history" v-bind:key="h.date">
            <td>{{h.from | date}}</td>
            <td>{{h.life_cycle_code}}</td>
            <td>{{h.action}}</td>
            <td>{{h.user_ref}}</td>
          </tr>
        </tbody>
      </table>
     </b-modal>
  </div>
</template>

<script>
  import OrganisationUnit from '@/api/OrganisationUnit'
  import Employee from '@/api/Employee'
  import '@/filters/Date'

  export default {
    props: {
      uuid: {
        type: String,
        required: true
      },
      type: {
        type: String,
        required: true,
        validator (value) {
          if (value === 'ORG_UNIT' || value === 'EMPLOYEE') return true
          console.warn('Type must be either ORG_UNIT or EMPLOYEE')
          return false
        }
      }
    },
    data () {
      return {
        history: []
      }
    },
    methods: {
      reloadHistory (val) {
        if (val) this.getHistory()
      },

      getHistory () {
        switch (this.type) {
          case 'ORG_UNIT':
            this.getOrgUnitHistory(this.uuid)
            break
          case 'EMPLOYEE':
            this.getEmployeeHistory(this.uuid)
            break
        }
      },

      getOrgUnitHistory (uuid) {
        let vm = this
        OrganisationUnit.history(uuid)
          .then(response => {
            vm.history = response
          })
      },

      getEmployeeHistory (uuid) {
        let vm = this
        Employee.history(uuid)
          .then(response => {
            vm.history = response
          })
      }
    }
  }
</script>
