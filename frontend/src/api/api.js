import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const signup = (data) => api.post("/auth/signup", data);
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
export const getMaintenance = () => api.get("/maintenance");
export const closeMaintenance = (id) => api.post(`/maintenance/${id}/close`);
export const getKpis = () => api.get("/dashboard/kpis");

// FastAPI returns `detail` as a plain string for HTTPException,
// but as an ARRAY of {type, loc, msg, input} objects for pydantic
// validation errors (422). Rendering that array directly in JSX
// crashes React ("Objects are not valid as a React child"), so
// every caller should go through this helper instead of reading
// err.response.data.detail directly.
export const getErrorMessage = (err, fallback = "Something went wrong") => {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        if (typeof d === "string") return d;
        const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : d.loc;
        return field ? `${field}: ${d.msg}` : d.msg;
      })
      .join(", ");
  }
  return fallback;
};

export default api;