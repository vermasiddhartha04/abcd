import api from "../api/axios";

export const uploadDocument = async (caseId, file) => {
  const formData = new FormData();

  formData.append("case_id", caseId);
  formData.append("file", file);

  const response = await api.post("/uploads/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};
