import { useState } from "react";

function Metadata() {
  const [metadata, setMetadata] = useState(null);

  const extractMetadata = () => {
    // Dummy Data
    setMetadata({
      gstin: "05ABCDE1234F1Z5",
      pan: "ABCDE1234F",
      taxpayer: "ABC Pvt Ltd",
      section: "74",
      financialYear: "2023-24",
      noticeNumber: "SCN/2026/001",
      noticeDate: "01-08-2026",
      taxAmount: "₹2,45,000",
    });

    // Next Phase
    // axios.post("/api/v1/metadata")
  };

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>Metadata Extraction</h1>

      <p style={{ color: "#666" }}>
        Extract GST information from OCR text.
      </p>

      <br />

      <button
        onClick={extractMetadata}
        style={{
          padding: "12px 22px",
          background: "#2563eb",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "16px",
        }}
      >
        Extract Metadata
      </button>

      <br />
      <br />

      {metadata && (
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            background: "#fff",
            boxShadow: "0 2px 10px rgba(0,0,0,.1)",
          }}
        >
          <tbody>
            <tr>
              <td style={cellStyle}>GSTIN</td>
              <td style={cellStyle}>{metadata.gstin}</td>
            </tr>

            <tr>
              <td style={cellStyle}>PAN</td>
              <td style={cellStyle}>{metadata.pan}</td>
            </tr>

            <tr>
              <td style={cellStyle}>Taxpayer</td>
              <td style={cellStyle}>{metadata.taxpayer}</td>
            </tr>

            <tr>
              <td style={cellStyle}>GST Section</td>
              <td style={cellStyle}>{metadata.section}</td>
            </tr>

            <tr>
              <td style={cellStyle}>Financial Year</td>
              <td style={cellStyle}>{metadata.financialYear}</td>
            </tr>

            <tr>
              <td style={cellStyle}>Notice Number</td>
              <td style={cellStyle}>{metadata.noticeNumber}</td>
            </tr>

            <tr>
              <td style={cellStyle}>Notice Date</td>
              <td style={cellStyle}>{metadata.noticeDate}</td>
            </tr>

            <tr>
              <td style={cellStyle}>Tax Amount</td>
              <td style={cellStyle}>{metadata.taxAmount}</td>
            </tr>
          </tbody>
        </table>
      )}
    </div>
  );
}

const cellStyle = {
  border: "1px solid #ddd",
  padding: "12px",
};

export default Metadata;