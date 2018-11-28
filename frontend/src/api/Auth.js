import Service from './HttpCommon'

let currentUser = {
  username: 'Admin'
}

export default {

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
