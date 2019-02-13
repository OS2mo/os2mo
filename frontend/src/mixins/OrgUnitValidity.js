export default {
  computed: {
    orgUnitValidity () {
      if (this.entry.org_unit || this.entry.validity) {
        if (this.entry.org_unit.validity < this.entry.validity) {
          this.entry.org_unit.validity = this.entry.validity
        }
        return this.entry.org_unit.validity
      }
    }
  }
}
