import { useState } from "react";

function OCR() {
  const [ocrText, setOcrText] = useState("");

  const handleRunOCR = () => {
    // Temporary Dummy OCR Result
    setOcrText(`
SHOW CAUSE NOTICE

GSTIN : 05ABCDE1234F1Z5

Taxpayer Name : ABC Pvt Ltd

Section : 74

Financial Year : 2023-24

Notice No : SCN/2026/001

Date : 01-08-2026

Tax Amount : Rs. 2,45,000

Reply required within 30 days.
    `);

    // Next Phase
    // axios.post("/api/v1/ocr")
  };

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>OCR Processing</h1>

      <p style={{ color: "#666" }}>
        Extract text from uploaded GST documents.
      </p>

      <br />

      <button
        onClick={handleRunOCR}
        style={{
          padding: "12px 22px",
          background: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "16px",
        }}
      >
        Run OCR
      </button>

      <br />
      <br />

      <textarea
        value={ocrText}
        readOnly
        rows={18}
        style={{
          width: "100%",
          padding: "15px",
          fontSize: "15px",
          borderRadius: "10px",
          border: "1px solid #ccc",
          resize: "vertical",
        }}
      />

      <br />
      <br />

      <button
        onClick={() => navigator.clipboard.writeText(ocrText)}
        style={{
          padding: "10px 18px",
          background: "#16a34a",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
        }}
      >
        Copy OCR Text
      </button>
    </div>
  );
}

export default OCR;