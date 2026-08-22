import api from "../api/axios";

export const processDocument = async (uploadId) => {
  if (!uploadId) {
    throw new Error("Upload ID is required.");
  }

  try {
    const response = await api.post(`/process/${uploadId}`);

    return response.data;
  } catch (error) {
    console.error("Document processing failed:", error);

    const message =
      error?.response?.data?.error ||
      error?.response?.data?.detail ||
      error?.message ||
      "Document processing failed.";

    throw new Error(message);
  }
};