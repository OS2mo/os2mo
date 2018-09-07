export let baseURL = process.env.BASE_URL ?
  process.env.BASE_URL.replace(/\/+$/, '') : 'http://localhost:8080'
