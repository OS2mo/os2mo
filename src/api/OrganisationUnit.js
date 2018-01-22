import {HTTP} from './HttpCommon'

export default {

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Object} organisation unit object
   */
  getOrganisationUnit (uuid) {
    return HTTP.get(`/ou/${uuid}`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  },

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Array} organisation unit children
   */
  getOrganisationUnitChildren (uuid) {
    return HTTP.get(`/ou/${uuid}/children`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  }
}
