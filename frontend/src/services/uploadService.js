import api from "../api/axios";

export const uploadDocument = async (caseId, file) => {
  if (!caseId) {
    throw new Error("Case ID is required.");
  }

  if (!file) {
    throw new Error("Please select a document.");
  }

  const formData = new FormData();

  formData.append("case_id", String(caseId));
  formData.append("file", file);

  try {
    const response = await api.post("/uploads/", formData);

    return response.data;
  } catch (error) {
    console.error("Document upload failed:", error);

    const message =
      error?.response?.data?.error ||
      error?.response?.data?.detail ||
      error?.message ||
      "Document upload failed.";

    throw new Error(message);
  }
};