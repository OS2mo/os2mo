import axios from 'axios'

export const HTTP = axios.create({
  // baseURL: 'http://localhost:8080',
  baseURL: '/mo',
  headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, PUT'
  }
})
