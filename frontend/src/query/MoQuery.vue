<template>
  <div class="card col">
    <div class="card-body d-flex flex-column">
      <h4 class="card-title">
        <icon name="exchange-alt"/>
        {{$tc('shared.query', 2)}}
      </h4>
      <span v-for="link in links" :key="link">
        <icon name="download"/>
      <a :href="link.url">{{link.label}}</a>
      </span>
    </div>
  </div>
</template>

<script>
  export default {
    components: {
    },
    computed: {
    },
    data () {
      return {
        links: [
          {
            label: 'Alle lederfunktioner',
            url: 'Alle_lederfunktioner'
          },
          {
            label: 'Alle BK stilling email',
            url: 'AlleBK-stilling-email'
          },
          {
            label: 'Ballerup org inkl medarbejdere',
            url: 'Ballerup_org_incl-medarbejdere'
          },
          {
            label: 'SD-løn organisation med PNR',
            url: 'SD-løn org med Pnr'
          }
        ]
      }
    }
  }
</script>

<style scoped>

</style>
