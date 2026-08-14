import api from "../api/axios";

export const getCases = async () => {
  const response = await api.get("/cases/");
  return response.data;
};

export const createCase = async (data) => {
  const response = await api.post("/cases/", data);
  return response.data;
};