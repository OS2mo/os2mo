export default {
  computed: {
    orgUnitValidity () {
      if (this.entry.org_unit) {
        return this.entry.org_unit.validity
      }
    }
  }
}
