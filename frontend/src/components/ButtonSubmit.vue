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
  /**
   * A button submit component.
   */

  import MoLoader from '@/components/atoms/MoLoader'
  export default {
    components: {
      MoLoader
    },

    props: {
      /**
       * This boolean property disable the button.
       */
      isDisabled: Boolean,

      /**
       * This boolean property defines the loading.
       */
      isLoading: Boolean,

      /**
       * This Function defines a click action.
       */
      onClickAction: Function
    }
  }
</script>
