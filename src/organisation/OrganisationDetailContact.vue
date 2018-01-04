<template>
    <table class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Kontaktkanal</th>
          <th scope="col">Beskrivelse</th>
          <th scope="col">Egenskaber</th>
          <th scope="col">Relateret adresse</th>
          <th scope="col">Startdato</th>
          <th scope="col">Slutdato</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="contact in contactsFuture" v-bind:key="contact.uuid" style="color:#bbb">
          <td>{{contact.type.name}}</td>
          <td>{{contact['contact-info']}}</td>
          <td>{{contact.visibility.name}}</td>
          <td>{{contact.location.vejnavn}}</td>
          <td>{{contact['valid-from']}}</td>
          <td>{{contact['valid-to']}}</td>
        </tr>

        <tr v-for="contact in contacts" v-bind:key="contact.uuid">
          <td>{{contact.type.name}}</td>
          <td>{{contact['contact-info']}}</td>
          <td>{{contact.visibility.name}}</td>
          <td>{{contact.location.vejnavn}}</td>
          <td>{{contact['valid-from']}}</td>
          <td>{{contact['valid-to']}}</td>
        </tr>

        <tr v-for="contact in contactsPast" v-bind:key="contact.uuid" style="color:#bbb">
          <td>{{contact.type.name}}</td>
          <td>{{contact['contact-info']}}</td>
          <td>{{contact.visibility.name}}</td>
          <td>{{contact.location.vejnavn}}</td>
          <td>{{contact['valid-from']}}</td>
          <td>{{contact['valid-to']}}</td>
        </tr>
      </tbody>
    </table>
</template>

<script>
  import Organisation from '../api/Organisation'

  export default {
    components: {},
    data () {
      return {
        contacts: [],
        contactsPast: [],
        contactsFuture: []
      }
    },
    created: function () {
      this.getContactChannels()
    },
    methods: {
      getContactChannels: function () {
        var vm = this
        Organisation.getContactDetails('456362c4-0ee4-4e5e-a72c-751239745e62', this.$route.params.uuid)
        .then(response => {
          vm.contacts = response
        })
        Organisation.getContactDetails('456362c4-0ee4-4e5e-a72c-751239745e62', this.$route.params.uuid, 'past')
        .then(response => {
          vm.contactsPast = response
        })
        Organisation.getContactDetails('456362c4-0ee4-4e5e-a72c-751239745e62', this.$route.params.uuid, 'future')
        .then(response => {
          vm.contactsFuture = response
        })
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>