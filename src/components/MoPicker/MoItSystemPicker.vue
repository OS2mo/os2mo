<template>
  <div class="form-group col">
    <label :for="nameId">{{$tc('shared.it_system', 2)}}</label>
    <select 
      :name="nameId"
      :id="nameId"
      :data-vv-as="label"
      class="form-control col" 
      v-model="selected"
      @change="updateSelectedItSystem()"
      v-validate="{ required: true }">
      <option disabled>{{label}}</option>
      <option 
        v-for="it in itSystems" 
        v-bind:key="it.uuid"
        :value="it.uuid">
          {{it.name}}
      </option>
    </select>
    <span
      v-show="errors.has(nameId)" 
      class="text-danger"
    >
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
import Facet from '@/api/Facet'
import { EventBus } from '@/EventBus'

export default {
  name: 'MoItSystemPicker',
  props: {
    value: Object,
    preselected: String
  },
  inject: {
    $validator: '$validator'
  },
  data () {
    return {
      selected: {},
      itSystems: []
    }
  },
  computed: {
    nameId () {
      return 'it-system-picker-' + this._uid
    }
  },
  mounted () {
    EventBus.$on('organisation-changed', () => {
      this.getItSystems()
    })
  },
  created () {
    this.selected = this.preselected
    this.getItSystems()
  },
  beforeDestroy () {
    EventBus.$off(['organisation-changed'])
  },
  methods: {
    getItSystems () {
      var vm = this
      let org = this.$store.state.organisation
      if (org.uuid === undefined) return
      Facet.itSystems(org.uuid)
        .then(response => {
          vm.itSystems = response
        })
    },

    updateSelectedItSystem () {
      let data = {
        uuid: this.selected
      }
      this.$emit('input', data)
    }
  }
}
</script>
