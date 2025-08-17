import axios from 'axios';
const api = axios.create({ baseURL: 'http://localhost:5175' });
export const getProject = () => api.get('/project').then(r=>r.data);
export const getProxyUrl = (shotId: string) => `http://localhost:5175/proxies/${shotId}`;
export const getShots = () => fetch('http://localhost:5175/shots').then(r=>r.json());
export const getProxyStatus = (shotId: string) => fetch(`http://localhost:5175/proxies/${shotId}/status`).then(r=>r.json());


