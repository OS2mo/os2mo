import { HTTP, Service } from './HttpCommon'
import { EventBus } from '../EventBus'

let currentUser = {
  username: 'Admin'
}

export default {

  setUser (user) {
    return HTTP.get('/o')
      .then(response => {
        EventBus.$emit('login-success', user)
        currentUser = user
        return true
      })
  },

  getUser () {
    return currentUser
  },

  login (user) {
    return Service.post('/user/login', user)
      .then(response => {
        return response.data
      })
      .catch(error => {
        return error.response.data
      })
  },

  logout (user) {
    return Service.post('/user/logout', user)
    .then(response => {
      return response.data
    })
  }
}
