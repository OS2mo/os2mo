<template>
<div class="card card-margin">
  <div class="card-body">
    <b-tabs>
      <b-tab title="Arbejdslog" active> 
        <div 
          class="alert alert-success" 
          v-for="log in reverse(workLogs)" 
          v-bind:key="log.uuid" 
          role="alert"
        >
          {{log}}
        </div>   
      </b-tab>
      <b-tab title="Begivenheder">
        Begivenheder
      </b-tab>
      <b-tab title="Fejl">
        Fejl
      </b-tab>
    </b-tabs>
  </div>
</div>
</template>

<script>
  import { EventBus } from '../EventBus'
  export default {
    name: 'WorkLog',

    data () {
      return {
        workLogs: []
      }
    },

    mounted () {
      EventBus.$on('org-unit-create', org => {
        let msg = 'Organisationsenheden med UUID ' + org.uuid + ' er oprettet med success'
        this.workLogs.push(msg)
      })

      EventBus.$on('org-unit-rename', org => {
        let msg = 'Organisationsenheden med UUID ' + org.uuid + ' er omdøbt med success'
        this.workLogs.push(msg)
      })

      EventBus.$on('org-unit-move', org => {
        let msg = 'Organisationsenheden med UUID ' + org.uuid + ' er flyttet korrekt'
        this.workLogs.push(msg)
      })

      EventBus.$on('org-unit-end-date', org => {
        let msg = 'Organisationsenheden med UUID ' + org.uuid + ' er afsluttet korrekt'
        this.workLogs.push(msg)
      })
    },
    methods: {
      reverse (array) {
        return array.length ? array.slice().reverse() : array
      }
    }
  }
</script>

<style scoped>

.card-margin{
  margin-top: 2em;
  min-height: 150px;
}
 
</style>
