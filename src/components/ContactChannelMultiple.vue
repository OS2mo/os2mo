<template>
  <div>
    <component 
      v-for="(channel, key) in contactChannels" 
      v-bind:is="channel" 
      v-bind:key="key" 
      v-model="channelData[key]"
      @change="updateContactChannel()"
    />

    {{channelData}}
    
    <button 
      type="button" 
      class="btn btn-primary" 
      v-on:click="addContactChannel()"
      :disabled="contactChannels.length > channelData.length" 
    >
      <icon name="plus"/>
    </button>
  </div>
</template>

<script>
  import ContactChannel from './ContactChannelInput'

  export default {
    components: {
      ContactChannel
    },
    data () {
      return {
        contactChannels: ['ContactChannel'],
        channelData: []
      }
    },
    created: function () {},
    methods: {
      addContactChannel: function () {
        this.contactChannels.push('ContactChannel')
      },

      removeContactChannel: function () {

      },

      updateContactChannel: function () {
        console.log(this.channelData)
        this.$emit('input', this.channelData)
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>