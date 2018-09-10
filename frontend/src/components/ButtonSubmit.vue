<template>
  <div>
    <mo-loader v-show="isLoading"/>

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
  import MoLoader from '@/components/atoms/MoLoader'
  export default {
    components: {
      MoLoader
    },

    props: {
      isDisabled: Boolean,
      isLoading: Boolean,
      onClickAction: Function
    }
  }
</script>
