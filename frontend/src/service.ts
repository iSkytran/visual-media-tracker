import axios from 'axios';

const baseUrl = 'http://localhost:8000';

export class Service {
  fetchTime: string;

  constructor() {
    this.fetchTime = '';
  }

  async getShow() {
    const response =  await axios.get(baseUrl + '/shows');
    this.fetchTime = response.headers['Fetch-Time'];
    return response.data;
  }

  async getMovie() {
    const response =  await axios.get(baseUrl + '/movies');
    this.fetchTime = response.headers['Fetch-Time'];
    return response.data;
  }

  async getWebcomic() {
    const response =  await axios.get(baseUrl + '/webcomics');
    this.fetchTime = response.headers['Fetch-Time'];
    return response.data;
  }
}