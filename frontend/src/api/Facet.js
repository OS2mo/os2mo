// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "./HttpCommon"

const ClassDetails = {
  FULL_NAME: "full_name=1",
  // NCHILDREN: '',
  TOP_LEVEL_FACET: "top_level_facet=1",
  FACET: "facet=1",
}

export default {
  ClassDetails,

  /**
   * Get IT a list of available IT systems
   * @param {String} uuid - organisation uuid
   * @returns {Array} a list of options
   */
  itSystems(uuid) {
    return Service.get(`/o/${uuid}/it/`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Get a facet
   * @param {String} uuid - Uuid for the facet to get
   * @returns {Object} a facet object
   */
  get(uuid) {
    return Service.get(`/f/${uuid}/`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.log(error.response)
      })
  },

  /**
   * Get the children of a facet
   * @param {String} uuid - Uuid for current facet
   * @returns {Array} List of classes under the current facet
   */
  getChildren(uuid) {
    return Service.get(`/f/${uuid}/children`)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.log(error.response)
      })
  },
}
