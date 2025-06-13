import axios from 'axios'

export class BaseRepository {
  protected client = axios.create({
    baseURL: process.env.baseUrl || '/v1',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  constructor() {
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Token ${token}`
      }
      return config
    })
  }
} 