export default {
  computed: {
    currentDateValidity () {
      return this.disabledToTodaysDate
    },

    /**
     * Disabled dates to todays date for the date picker.
     */
    disabledToTodaysDate () {
      return {
        'from': new Date().toISOString().substring(0, 10)
      }
    }
  }
}
