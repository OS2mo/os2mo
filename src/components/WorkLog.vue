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
      EventBus.$on('organisation-unit-create', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er oprettet med success'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-rename', org => {
        console.log(org)
        let msg = 'Organisationsenheden med UUID ' + org + ' er omdøbt med success'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-move', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er flyttet korrekt'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-terminate', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er afsluttet korrekt'
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
