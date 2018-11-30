export default {
  /**
   * Requesting a new validator scope to its children
   */
  inject: {
    $validator: '$validator'
  },
  data () {
    return {
      test: 'some value'
    }
  },
  computed: {
    /**
     * Loop over all contents of the fields object and check if they exist and valid.
     */
    formValid () {
      return Object.keys(this.fields).every(field => {
        return this.fields[field] && this.fields[field].valid
      })
    }
  }
}
