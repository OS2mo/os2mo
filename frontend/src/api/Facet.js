// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from './HttpCommon'

export default {

  /**
   * Get IT a list of available IT systems
   * @param {String} uuid - organisation uuid
   * @returns {Array} a list of options
   */
  itSystems (uuid) {
    return Service.get(`/o/${uuid}/it/`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        console.log(error.response)
      })
  }
}
