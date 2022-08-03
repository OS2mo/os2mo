// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

export default {
  /**
   * Requesting a new validator scope to its children
   */
  inject: {
    $validator: "$validator",
  },
  computed: {
    /**
     * Loop over all contents of the fields object and check if they exist and valid.
     */
    formValid() {
      return Object.keys(this.fields).every((field) => {
        return this.fields[field] && this.fields[field].valid
      })
    },
  },
}
