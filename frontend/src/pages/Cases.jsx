import { useEffect, useState } from "react";
import { getCases } from "../services/caseService";

function Cases() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadCases = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getCases();

      setCases(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading cases:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to load cases."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, []);

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial, sans-serif",
        background: "#f5f7fb",
        minHeight: "100vh",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "20px",
          flexWrap: "wrap",
        }}
      >
        <div>
          <h1
            style={{
              margin: 0,
              color: "#172033",
            }}
          >
            Case Management
          </h1>

          <p style={{ color: "#6b7280" }}>
            GST litigation cases and current status.
          </p>
        </div>

        <button
          onClick={loadCases}
          style={{
            padding: "11px 20px",
            background: "#2563eb",
            color: "#ffffff",
            border: "none",
            borderRadius: "7px",
            cursor: "pointer",
            fontWeight: "600",
          }}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            background: "#fef2f2",
            color: "#b91c1c",
            borderRadius: "8px",
          }}
        >
          {error}
        </div>
      )}

      <div
        style={{
          marginTop: "25px",
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "15px",
        }}
      >
        <Stat
          title="Total Cases"
          value={cases.length}
        />

        <Stat
          title="Pending"
          value={
            cases.filter(
              (item) =>
                String(item.status || "")
                  .toLowerCase()
                  .includes("pending")
            ).length
          }
        />

        <Stat
          title="In Review"
          value={
            cases.filter(
              (item) =>
                String(item.status || "")
                  .toLowerCase()
                  .includes("review")
            ).length
          }
        />
      </div>

      <div
        style={{
          marginTop: "25px",
          background: "#ffffff",
          borderRadius: "12px",
          boxShadow:
            "0 2px 10px rgba(0,0,0,0.06)",
          overflowX: "auto",
        }}
      >
        {loading ? (
          <div style={{ padding: "30px" }}>
            Loading cases...
          </div>
        ) : cases.length === 0 ? (
          <div style={{ padding: "30px" }}>
            No cases found.
          </div>
        ) : (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead>
              <tr
                style={{
                  background: "#111827",
                  color: "#ffffff",
                }}
              >
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Case No</th>
                <th style={thStyle}>GSTIN</th>
                <th style={thStyle}>Taxpayer</th>
                <th style={thStyle}>Notice Type</th>
                <th style={thStyle}>FY</th>
                <th style={thStyle}>Status</th>
              </tr>
            </thead>

            <tbody>
              {cases.map((item) => (
                <tr key={item.id}>
                  <td style={tdStyle}>
                    {item.id}
                  </td>

                  <td style={tdStyle}>
                    {item.case_no || "-"}
                  </td>

                  <td style={tdStyle}>
                    {item.gstin || "-"}
                  </td>

                  <td style={tdStyle}>
                    {item.taxpayer_name || "-"}
                  </td>

                  <td style={tdStyle}>
                    {item.notice_type || "-"}
                  </td>

                  <td style={tdStyle}>
                    {item.financial_year || "-"}
                  </td>

                  <td style={tdStyle}>
                    <span
                      style={{
                        padding: "6px 10px",
                        borderRadius: "15px",
                        background:
                          "#eff6ff",
                        color: "#1d4ed8",
                        fontWeight: "600",
                      }}
                    >
                      {item.status || "-"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div
      style={{
        background: "#ffffff",
        padding: "20px",
        borderRadius: "10px",
        boxShadow:
          "0 2px 8px rgba(0,0,0,0.05)",
      }}
    >
      <p
        style={{
          margin: 0,
          color: "#6b7280",
        }}
      >
        {title}
      </p>

      <h2
        style={{
          margin: "8px 0 0",
          color: "#172033",
        }}
      >
        {value}
      </h2>
    </div>
  );
}

const thStyle = {
  padding: "13px",
  textAlign: "left",
  whiteSpace: "nowrap",
};

const tdStyle = {
  padding: "12px",
  borderBottom: "1px solid #e5e7eb",
  whiteSpace: "nowrap",
};

export default Cases;