import axios, { AxiosInstance } from 'axios'

export class BaseRepository {
  protected client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: process.env.API_BASE_URL || '/api',
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }
} 