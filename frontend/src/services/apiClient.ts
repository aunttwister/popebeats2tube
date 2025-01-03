import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // Replace with your API base URL
  headers: {
    'Content-Type': 'application/json'
  },
});

// Add a request interceptor to include the JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt'); // Adjust as per your token storage mechanism
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;