import { HTTP, Service } from './HttpCommon'

export default {

  /**
   * Get a list of organisation unit types.
   * @returns {Array} A list of the different organisation unit types
   */
  getOrganisationUnitTypes () {
    return HTTP.get('/org-unit/type')
    .then(response => {
      return response.data
    })
  },

  /**
   * Get the contact channel types
   * @returns {Array} A list of the different contact channel types
   */
  getContactChannels () {
    return Service.get('/f/address')
    .then(response => {
      return response.data
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
  },

  /**
   * Get a list of contact channel properties
   * @returns {Array} a list of contact channel properties
   */
  getContactChannelProperties () {
    return this.getProperty('contact', 'properties')
  },

  /**
   * Get a list of job titles
   * @returns {Array} A list of job titles
   */
  getEngagementTitles () {
    return this.getProperty('engagement', 'job-title')
  },

  /**
   * Get a list of enagement types
   * @returns A list of engagement types
   */
  getEngagementTypes () {
    return this.getProperty('engagement', 'type')
  },

  /**
  * Get a list of absence types
  * @returns A list of absence types
  */
  getAbsenceTypes () {
    return this.getProperty('absence', 'type')
  },

  /**
   * Base call for retrieving properties
   * @param {String} roleType - the role type
   * @param {String} facet - the facet, or property
   * @returns A list of requested properties
   */
  getProperty (roleType, facet) {
    return HTTP.get(`/role-types/${roleType}/facets/${facet}/classes/`)
    .then(response => {
      return response.data
    })
  }
}
