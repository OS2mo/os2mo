import { Service } from './HttpCommon'

export default {
  /**
   * Get a list of all available facets
   * @param {String} orgUuid - organisation uuid
   * @returns {Array} a list of all available facets
   */
  getAll (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/`)
    .then(response => {
      return response.data
    })
  },

  organisationUnitTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/ou/`)
    .then(response => {
      return response.data
    })
  },

  addressTypes (orgUuid) {
    return Service.get(`/o/${orgUuid}/f/address/`)
    .then(response => {
      return response.data
    })
  }
}
