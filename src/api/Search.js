import { Service } from './HttpCommon'

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
      return response.data
    })
  },

  organisations (orgUuid, query) {
    query = query || ''
    return Service.get(`/o/${orgUuid}/ou/?query=${query}`)
    .then(response => {
      return response.data
    })
  }
}
