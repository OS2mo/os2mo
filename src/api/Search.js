import { Service, HTTP } from './HttpCommon'

export default {
  /**
   * Get a list of all available facets
   * @param {String} orgUuid - organisation uuid
   * @returns {Array} a list of all available facets
   */
  employees (orgUuid, query) {
    query = query || ''
    return Service.get(`/o/${orgUuid}/e/?query=${query}`)
    .then(response => {
      return response.data.items
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  organisations (orgUuid, query) {
    query = query || ''
    return Service.get(`/o/${orgUuid}/ou/?query=${query}`)
    .then(response => {
      return response.data.items
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get a list of possible addresses based on search query
   * @param {String} query - the search query
   * @param {String} local - organisation uuid to limit search to the local area of the organisation
   * @returns {Array} A list of address suggestions based on search query
   */
  getGeographicalLocation (query, local) {
    return HTTP.get(`/addressws/geographical-location?local=${local}&vejnavn=${query}`)
    .then(response => {
      return response.data
    })
  }
}
