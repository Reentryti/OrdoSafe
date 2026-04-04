import api from "@/api/http";

// Doctor endpoints
export async function getOrdonnances(params = {}) {
  return api.get("/api/v1/doctor/ordonnances/", { params });
}

export async function getOrdonnance(id) {
  return api.get(`/api/v1/doctor/ordonnances/${id}/`);
}

export async function createOrdonnance(data) {
  return api.post("/api/v1/doctor/ordonnances/create/", data);
}

export async function updateOrdonnance(id, data) {
  return api.put(`/api/v1/doctor/ordonnances/${id}/update/`, data);
}

export async function deleteOrdonnance(id) {
  return api.delete(`/api/v1/doctor/ordonnances/${id}/delete/`);
}

export async function signOrdonnance(id) {
  return api.post(`/api/v1/doctor/ordonnances/${id}/sign/`);
}

// Pharmacist endpoints
export async function searchOrdonnances(params) {
  return api.get("/api/v1/pharmacist/search/", { params });
}

export async function getPharmacistOrdonnance(id) {
  return api.get(`/api/v1/pharmacist/ordonnances/${id}/`);
}

export async function validateOrdonnance(id) {
  return api.post(`/api/v1/pharmacist/ordonnances/${id}/validate/`);
}

export async function reportOrdonnance(id, reason) {
  return api.post(`/api/v1/pharmacist/ordonnances/${id}/report/`, { reason });
}

export async function blockOrdonnance(id) {
  return api.post(`/api/v1/pharmacist/ordonnances/${id}/block/`);
}
