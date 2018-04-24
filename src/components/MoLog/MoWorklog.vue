<template>
  <div class="wrapper">
    <div 
      class="alert alert-success" 
      v-for="log in reverse(workLogs)" 
      v-bind:key="log.uuid" 
      role="alert"
    >
      {{log}}
    </div>
  </div>
</template>

<script>
  import { EventBus } from '../../EventBus'
  export default {
    name: 'MoWorklog',

    data () {
      return {
        workLogs: []
      }
    },

    mounted () {
      EventBus.$on('organisation-unit-create', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er oprettet med success.'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-rename', org => {
        console.log(org)
        let msg = 'Organisationsenheden med UUID ' + org + ' er omdøbt med success.'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-move', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er flyttet korrekt.'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-terminate', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er afsluttet korrekt.'
        this.workLogs.push(msg)
      })

      EventBus.$on('organisation-unit-edit', org => {
        let msg = 'Organisationsenheden med UUID ' + org + ' er blevet redigeret.'
        this.workLogs.push(msg)
      })

      EventBus.$on('employee-create', emp => {
        let msg = 'Medarbejderen med UUID ' + emp + ' er blevet oprettet.'
        this.workLogs.push(msg)
      })

      EventBus.$on('employee-leave', emp => {
        let msg = 'Medarbejderen med UUID ' + emp + ' har fået tildelt orlov.'
        this.workLogs.push(msg)
      })

      EventBus.$on('employee-move', emp => {
        let msg = 'Medarbejderen med UUID ' + emp + ' er blevet flyttet.'
        this.workLogs.push(msg)
      })

      EventBus.$on('employee-terminate', emp => {
        let msg = 'Medarbejderen med UUID ' + emp + ' er afsluttet korrekt.'
        this.workLogs.push(msg)
      })

      EventBus.$on('employee-edit', emp => {
        let msg = 'Medarbejderen med UUID ' + emp + ' er blevet redigeret.'
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
.wrapper {
  max-height: 10rem;
  overflow-y: auto;
}
</style>
