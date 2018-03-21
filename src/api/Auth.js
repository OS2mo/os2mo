import { HTTP } from './HttpCommon'
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
  }
}
