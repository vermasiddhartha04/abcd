import api from "../api/axios";

export const getAnalysis = async (metadataId) => {
  const response = await api.post(
    `/analysis/${metadataId}`
  );

  return response.data;
};