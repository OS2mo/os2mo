<template>
    <div class="form-row">
      <div class="form-group col">
        <label :for="'contactchannel' + _uid">Adressetype</label>
        <select 
          class="form-control"
          :id="'contactchannel' + _uid"
          v-model="channel.type"
          @change="updateContactChannel()"
          required>
          <option disabled value="Vælg kontaktkanal">Vælg adressetype</option>
          <option 
            v-for="at in addressTypes" 
            :key="at.uuid"
            :value="at.uuid">
            {{at.name}}
          </option>
        </select>
      </div>

      <div class="form-group col">
        <label :for="'phoneno' + _uid">Telefonnr.</label>
        <input 
          type="text" 
          :id="'phoneno' + _uid"
          class="form-control"
          name="phone" 
          data-vv-as="Telefonnr."
          v-model="channel['contact-info']"
          @input="updateContactChannel()"
          v-validate="{ required: true, digits: 8}" 
        >
        <span v-show="errors.has('phone')" class="text-danger">{{ errors.first('phone') }}</span>
      </div>
    </div>
</template>

<script>
  import Facet from '../api/Facet'

  export default {
    props: {
      model: Object,
      orgUuid: String
    },
    data () {
      return {
        channel: {
          type: {},
          'contact-info': ''
        },
        addressTypes: []
      }
    },
    watch: {
      orgUuid () {
        this.getAddressTypes()
      }
    },
    created () {
      if (this.orgUuid) this.getAddressTypes()
    },
    methods: {
      getAddressTypes () {
        let vm = this
        Facet.addressTypes(this.orgUuid)
        .then(response => {
          vm.addressTypes = response
        })
      },

      updateContactChannel () {
        this.$emit('input', this.channel)
      }
    }
  }
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>