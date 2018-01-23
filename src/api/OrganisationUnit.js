import { HTTP, Service} from './HttpCommon'

export default {

  /**
   * Get an organisation unit
   * @param {String} uuid - organisation unit uuid
   * @returns {Object} organisation unit object
   */
  getOrganisationUnit (uuid) {
    return Service.get(`/ou/${uuid}`)
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
  getChildren (uuid) {
    return Service.get(`/ou/${uuid}/children`)
    .then(response => {
      return response.data
    })
    .catch(e => {
      console.log(e)
    })
  }
}
