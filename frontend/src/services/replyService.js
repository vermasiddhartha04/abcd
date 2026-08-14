import api from "../api/axios";

export const generateReply = async (analysisId) => {
  const response = await api.post(`/reply/${analysisId}`);
  return response.data;
};