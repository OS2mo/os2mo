import axios from 'axios'

/**
 * Defines the base url and headers for validate http calls
 */

const Validate = axios.create({
  baseURL: '/service/validate',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})

export default {
  cpr (cpr, org) {
    const payload = {
      'cpr_no': cpr,
      'org': {
        'uuid': org[0]
      }
    }
    return Validate
      .post('/cpr/', payload).then(r => {
        return true
      })
      .catch(r => {
        return false
      })
  }
}
