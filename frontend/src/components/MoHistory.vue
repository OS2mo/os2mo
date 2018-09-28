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
  /**
   * A history component.
   */

  import OrganisationUnit from '@/api/OrganisationUnit'
  import Employee from '@/api/Employee'
  import '@/filters/Date'

  export default {
    props: {
      /**
       * Defines a required uuid.
       */
      uuid: {
        type: String,
        required: true
      },

      /**
       * Defines a required type - employee or organisation unit.
       */
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
      /**
       * The history component value.
       * Used to detect changes and restore the value.
       */
        history: []
      }
    },

    methods: {
      /**
       * Reload history.
       */
      reloadHistory (val) {
        if (val) this.getHistory()
      },

      /**
       * Switch between organisation and employee getHistory.
       */
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

      /**
       * Get organisation unit history.
       */
      getOrgUnitHistory (uuid) {
        let vm = this
        OrganisationUnit.history(uuid)
          .then(response => {
            vm.history = response
          })
      },

      /**
       * Get employee history.
       */
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
