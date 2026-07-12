import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const login = (data) => api.post("/auth/login", data);
export const getVehicles = () => api.get("/vehicles");
export const getAvailableVehicles = () => api.get("/vehicles/available");
export const createVehicle = (data) => api.post("/vehicles", data);
export const getDrivers = () => api.get("/drivers");
export const getAvailableDrivers = () => api.get("/drivers/available");
export const createDriver = (data) => api.post("/drivers", data);
export const getTrips = () => api.get("/trips");
export const createTrip = (data) => api.post("/trips", data);
export const dispatchTrip = (id) => api.post(`/trips/${id}/dispatch`);
export const completeTrip = (id, data) => api.post(`/trips/${id}/complete`, data);
export const cancelTrip = (id) => api.post(`/trips/${id}/cancel`);
export const createMaintenance = (data) => api.post("/maintenance", data);
export const closeMaintenance = (id) => api.post(`/maintenance/${id}/close`);
export const getKpis = () => api.get("/dashboard/kpis");

export default api;