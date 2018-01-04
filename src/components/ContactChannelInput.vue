<template>
    <div class="form-row">
      <div class="form-group col">
        <label for="">Kontaktkanal</label>
        <select 
          class="form-control" 
          id="" 
          v-model="channel.type"
          @change="updateContactChannel()"
          required>
          <option disabled value="">Vælg kontaktkanal</option>
          <option 
            v-for="channel in contactChannels" 
            :key="channel.uuid"
            :value="channel">
            {{channel.name}}
          </option>
        </select>
      </div>

      <div class="form-group col">
        <label for="">Telefonnr</label>
        <input 
          type="text" 
          class="form-control"
          name="phone" 
          placeholder=""
          v-model="channel['contact-info']"
          @input="updateContactChannel()"
          v-validate="{ required: true, digits: 8}" 
        >
        <span v-show="errors.has('phone')" class="text-danger">{{ errors.first('phone') }}</span>
      </div>

      <div class="form-group col">
        <label for="">Egenskaber</label>
        <select 
          class="form-control" 
          id="" 
          v-model="channel.visibility"
          @change="updateContactChannel()"
          required>
          <option 
            disabled 
            value="">Vælg egenskaber</option>
          <option
            v-for="property in contactChannelProperties" 
            :key="property.uuid"
            :value="property">
            {{property.name}}
          </option>
        </select>
      </div>

      <!-- <div class="form-group">
        <button class="btn btn-primary">
          <icon name="minus"/>
        </button>
      </div> -->
    </div>
</template>

<script>
  import Property from '../api/Property'

  export default {
    props: ['value'],
    data () {
      return {
        channel: {
          type: {},
          'contact-info': '',
          visibility: {}
        },
        contactChannels: [],
        contactChannelProperties: []
      }
    },
    created: function () {
      this.getContactChannels()
      this.getContactChannelProperties()
    },
    methods: {
      getContactChannels: function () {
        var vm = this
        Property.getContactChannels().then(function (response) {
          vm.contactChannels = response
        })
      },

      getContactChannelProperties: function () {
        var vm = this
        Property.getContactChannelProperties().then(function (response) {
          vm.contactChannelProperties = response
        })
      },

      updateContactChannel: function () {
        this.$emit('input', this.channel)
      }
    }
  }
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>