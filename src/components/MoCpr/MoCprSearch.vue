<template>
  <div>
    <label v-if="!noLabel">{{label}}</label>
    <div class="input-group">
      <input 
        :name="nameId" 
        :data-vv-as="label"
        v-model="cprNo" 
        class="form-control" 
        type="text" 
        maxlength="10"
        v-validate="{digits: 10, required}" 
      />

      <button 
        type="button" 
        class="btn btn-outline-primary" 
        @click="cprLookup()" 
        :disabled="errors.has(nameId)" 
        v-show="!isLoading">
        <icon name="search"/>
      </button>

      <mo-loader v-show="isLoading"/>
    </div>

    <span v-show="errors.has(nameId)" class="text-danger">
      {{ errors.first(nameId) }}
    </span>
  </div>
</template>

<script>
import Search from '@/api/Search'
import MoLoader from '@/components/atoms/MoLoader'

export default {
  name: 'MoCprSearch',
  inject: {
    $validator: '$validator'
  },
  components: {
    MoLoader
  },
  props: {
    noLabel: Boolean,
    label: {type: String, default: 'CPR nummer'},
    required: Boolean
  },
  data () {
    return {
      nameId: 'cpr-search',
      cprNo: '',
      isLoading: false
    }
  },
  watch: {
    cprNo () {
      this.$emit('input', {})
    }
  },
  methods: {
    cprLookup () {
      let vm = this
      vm.isLoading = true
      return Search.cprLookup(this.cprNo)
        .then(response => {
          this.$emit('input', response)
          vm.isLoading = false
        })
    }
  }
}
</script>
