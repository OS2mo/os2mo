<i18n>
{
  "da": {
    "EMPLOYEE_CREATE": "Medarbejderen med UUID {uuid} er blevet oprettet.",
    "EMPLOYEE_EDIT": "Medarbejderen med UUID {uuid} er blevet redigeret.",
    "EMPLOYEE_LEAVE": "Medarbejderen med UUID {uuid} har fået tildelt orlov.",
    "EMPLOYEE_MOVE": "Medarbejderen med UUID {uuid} er blevet flyttet.",
    "EMPLOYEE_TERMINATE": "Medarbejderen med UUID {uuid} er afsluttet.",

    "ORGANISATION_CREATE": "Organisationsenheden med UUID {UUID} er blevet oprettet.",
    "ORGANISATION_EDIT": "Organisationsenheden med UUID {uuid} er blevet redigeret.",
    "ORGANISATION_RENAME": "Organisationsenheden med UUID {uuid} er blevet omdøbt.",
    "ORGANISATION_MOVE": "Organisationsenheden med UUID {uuid} er blevet flyttet",
    "ORGANISATION_TERMINATE": "Organisationsenheden med UUID {uuid} er blevet afsluttet."
  }
}
</i18n>

<template>
  <div class="wrapper">
    <div 
      class="alert alert-success mt-2" 
      v-for="log in reverse(worklogs)" 
      v-bind:key="log.uuid" 
      role="alert"
    >
    {{$t(log.type, {uuid: log.uuid})}}

    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'

  export default {
    name: 'MoWorklog',
    computed: {
      ...mapGetters({
        worklogs: 'log/getWorkLog'
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
