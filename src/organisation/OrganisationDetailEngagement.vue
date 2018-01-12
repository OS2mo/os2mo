<template>
  <div>
    <table class="table table-striped" v-show="!isLoading">
      <thead>
        <tr>
          <th scope="col">Navn</th>
          <th scope="col">Stillingsbetegnelse</th>
          <th scope="col">Engagementstype</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="e in engagementsFuture" v-bind:key="e.uuid" style="color:#bbb">
          <td>{{e['person-name']}}</td>
          <td>{{e['job-title'].name}}</td>
          <td><span v-if="e.type">{{e.type.name}}</span></td>
          <td>{{e['valid-from']}}</td>
          <td>{{e['valid-to']}}</td>
        </tr>

        <tr v-for="e in engagements" v-bind:key="e.uuid">
          <td>{{e['person-name']}}</td>
          <td>{{e['job-title'].name}}</td>
          <td><span v-if="e.type">{{e.type.name}}</span></td>
          <td>{{e['valid-from']}}</td>
          <td>{{e['valid-to']}}</td>
        </tr>

        <tr v-for="e in engagementsPast" v-bind:key="e.uuid" style="color:#bbb">
          <td>{{e['person-name']}}</td>
          <td>{{e['job-title'].name}}</td>
          <td><span v-if="e.type">{{e.type.name}}</span></td>
          <td>{{e['valid-from']}}</td>
          <td>{{e['valid-to']}}</td>
        </tr>
      </tbody>
    </table>

    <loading v-show="isLoading"/>
  </div>
</template>

<script>
  import Organisation from '../api/Organisation'
  import Loading from '../components/Loading'

  export default {
    components: {
      Loading
    },
    data () {
      return {
        engagements: [],
        engagementsPast: [],
        engagementsFuture: [],
        isLoading: true
      }
    },
    created: function () {
      this.getEngagements()
    },
    methods: {
      getEngagements: function () {
        var vm = this
        Organisation.getEngagementDetails(this.$route.params.uuid)
        .then(response => {
          vm.engagements = response
          vm.isLoading = false
        })
        Organisation.getEngagementDetails(this.$route.params.uuid, 'past')
        .then(response => {
          vm.engagementsPast = response
        })
        Organisation.getEngagementDetails(this.$route.params.uuid, 'future')
        .then(response => {
          vm.engagementsFuture = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>