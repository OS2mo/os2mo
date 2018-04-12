<template>
  <div>
  <loading v-show="isLoading"/>
  <button 
    :disabled="isDisabled" 
    type="submit" 
    class="btn btn-primary" 
    v-show="!isLoading"
  >
    <icon name="check"/>
  </button>
  </div>
</template>

<script>
import Loading from './Loading'
export default {
  components: {
    Loading
  },
  props: {
    isDisabled: Boolean,
    isLoading: Boolean,
    onClickAction: Function
  }
}
</script>
