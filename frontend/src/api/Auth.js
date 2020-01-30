// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from './HttpCommon'

let currentUser = {
  username: 'Admin'
}

export default {

  getUser () {
    return currentUser
  },

  async login (user) {
    return Service.post('/user/login', user)
      .then(response => {
        return response.data
      })
      .catch(error => {
        return error.response.data
      })
  },

  async logout (user) {
    return Service.post('/user/logout', user)
      .then(response => {
        return response.data
      })
  }
}
