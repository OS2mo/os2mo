// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from './HttpCommon'

export default {
  /**
   * Get a class
   * @param {String} uuid - Uuid for the class to get
   * @returns {Object} a class object
   */
  get (uuid) {
    return Service.get(`/c/${uuid}/`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  /**
   * Get the children of an class
   * @param {String} uuid - Uuid for current class
   * @returns {Array} List of classes under the current class
   */
  getChildren (uuid) {
    return Service.get(`/c/${uuid}/children`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  /**
   * Get an class' parent tree
   * @param {Array|String} uuids - Uuid for the class to get parents for
   * @returns {Array} Tree structure of class' parents
   */
  getAncestorTree (uuids) {
    if (!(uuids instanceof Array)) {
      uuids = [uuids]
    }

    const params = new URLSearchParams()

    for (const uuid of uuids) {
      params.append('uuid', uuid)
    }

    return Service.get('/c/ancestor-tree?' + params.toString())
      .then(response => {
        return response.data
      })
  },
}
