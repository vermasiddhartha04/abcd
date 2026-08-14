import { useState } from "react";
import { getAnalysis } from "../services/analysisService";

function getRiskColor(risk) {
  if (risk === "High") return "#dc2626";
  if (risk === "Medium") return "#d97706";
  return "#16a34a";
}

function getStageLabel(stage) {
  const labels = {
    SCN: "Show Cause Notice",
    SCN_REPLY: "SCN Reply",
    OIO: "Order-in-Original",
    APPEAL: "Appeal",
    OIA: "Order-in-Appeal",
    FINAL: "Final Review",
    DRC_REVIEW: "DRC Review",
  };

  return labels[stage] || stage || "Not Available";
}

function Analysis() {
  const [metadataId, setMetadataId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runAnalysis = async () => {
    if (!metadataId) {
      setError("Please enter Metadata ID.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setAnalysis(null);

      const data = await getAnalysis(Number(metadataId));

      setAnalysis(data);
    } catch (err) {
      console.error("Analysis Error:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to generate analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  const currentStage =
    analysis?.current_stage ||
    analysis?.document_stage ||
    analysis?.document_type ||
    "N/A";

  const nextStage =
    analysis?.next_stage ||
    analysis?.action?.next_stage ||
    null;

  const actionType =
    analysis?.action_type ||
    analysis?.action?.action_type ||
    null;

  const actionLabel =
    analysis?.action_label ||
    analysis?.action?.action_label ||
    null;

  const sections = Array.isArray(analysis?.sections)
    ? analysis.sections
    : [];

  return (
    <div
      style={{
        padding: "30px",
        fontFamily: "Arial, sans-serif",
        background: "#f5f7fb",
        minHeight: "100vh",
      }}
    >
      <div style={{ marginBottom: "25px" }}>
        <h1
          style={{
            margin: 0,
            color: "#172033",
          }}
        >
          GST Litigation Analysis
        </h1>

        <p
          style={{
            color: "#6b7280",
            marginTop: "8px",
          }}
        >
          Analyse GST litigation documents and determine the
          next legal action.
        </p>
      </div>

      {/* INPUT */}
      <div
        style={{
          background: "#ffffff",
          padding: "20px",
          borderRadius: "12px",
          boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
          marginBottom: "25px",
        }}
      >
        <h3
          style={{
            marginTop: 0,
            color: "#172033",
          }}
        >
          Generate Analysis
        </h3>

        <div
          style={{
            display: "flex",
            gap: "12px",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <input
            type="number"
            value={metadataId}
            onChange={(e) => setMetadataId(e.target.value)}
            placeholder="Metadata ID"
            style={{
              padding: "11px",
              width: "180px",
              border: "1px solid #d1d5db",
              borderRadius: "7px",
              fontSize: "14px",
            }}
          />

          <button
            onClick={runAnalysis}
            disabled={loading}
            style={{
              padding: "11px 22px",
              background: loading ? "#93c5fd" : "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "7px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "600",
            }}
          >
            {loading ? "Analyzing..." : "Generate Analysis"}
          </button>
        </div>

        {error && (
          <p
            style={{
              color: "#dc2626",
              marginTop: "15px",
              marginBottom: 0,
            }}
          >
            {error}
          </p>
        )}
      </div>

      {loading && (
        <div
          style={{
            background: "#ffffff",
            padding: "30px",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <h3>AI Analysis in progress...</h3>

          <p style={{ color: "#6b7280" }}>
            Processing GST case information.
          </p>
        </div>
      )}

      {analysis && !loading && (
        <>
          {/* MAIN STATUS */}
          <div
            style={{
              background: "#111827",
              color: "#ffffff",
              padding: "25px",
              borderRadius: "14px",
              marginBottom: "20px",
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
                <p
                  style={{
                    margin: 0,
                    color: "#9ca3af",
                    fontSize: "13px",
                  }}
                >
                  CURRENT DOCUMENT STAGE
                </p>

                <h1 style={{ margin: "8px 0" }}>
                  {getStageLabel(currentStage)}
                </h1>
              </div>

              <div
                style={{
                  padding: "12px 18px",
                  background: getRiskColor(
                    analysis.risk_level
                  ),
                  borderRadius: "30px",
                  fontWeight: "700",
                }}
              >
                {analysis.risk_level || "Unknown"} Risk
              </div>
            </div>

            {nextStage && (
              <div
                style={{
                  marginTop: "20px",
                  paddingTop: "18px",
                  borderTop: "1px solid #374151",
                }}
              >
                <span style={{ color: "#9ca3af" }}>
                  Next Stage:{" "}
                </span>

                <strong>
                  {getStageLabel(nextStage)}
                </strong>
              </div>
            )}

            {actionLabel && (
              <div style={{ marginTop: "8px" }}>
                <span style={{ color: "#9ca3af" }}>
                  Recommended Action:{" "}
                </span>

                <strong>{actionLabel}</strong>
              </div>
            )}
          </div>

          {/* TOP CARDS */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "18px",
              marginBottom: "20px",
            }}
          >
            <InfoCard
              title="Analysis ID"
              value={`#${analysis.id ?? "N/A"}`}
            />

            <InfoCard
              title="Metadata ID"
              value={`#${analysis.metadata_id ?? "N/A"}`}
            />

            <InfoCard
              title="Document Type"
              value={analysis.document_type || "N/A"}
            />

            <InfoCard
              title="Risk Level"
              value={analysis.risk_level || "N/A"}
              valueColor={getRiskColor(
                analysis.risk_level
              )}
            />
          </div>

          {/* ACTION CARDS */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "18px",
              marginBottom: "20px",
            }}
          >
            <InfoCard
              title="Action Type"
              value={actionType || "N/A"}
            />

            <InfoCard
              title="Next Stage"
              value={getStageLabel(nextStage)}
            />

            <InfoCard
              title="Reply Required"
              value={
                analysis.reply_required ? "YES" : "NO"
              }
              valueColor={
                analysis.reply_required
                  ? "#dc2626"
                  : "#16a34a"
              }
            />

            <InfoCard
              title="Appeal Required"
              value={
                analysis.appeal_required ? "YES" : "NO"
              }
              valueColor={
                analysis.appeal_required
                  ? "#dc2626"
                  : "#16a34a"
              }
            />
          </div>

          {/* SECTIONS */}
          {sections.length > 0 && (
            <div
              style={{
                background: "#ffffff",
                padding: "25px",
                borderRadius: "12px",
                marginBottom: "20px",
                boxShadow:
                  "0 2px 10px rgba(0,0,0,0.06)",
              }}
            >
              <h2
                style={{
                  marginTop: 0,
                  color: "#172033",
                }}
              >
                Applicable GST Sections
              </h2>

              <div
                style={{
                  display: "flex",
                  gap: "10px",
                  flexWrap: "wrap",
                }}
              >
                {sections.map((section) => (
                  <span
                    key={section}
                    style={{
                      padding: "8px 14px",
                      background: "#eff6ff",
                      color: "#1d4ed8",
                      borderRadius: "20px",
                      fontWeight: "600",
                    }}
                  >
                    Section {section}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* SUMMARY */}
          <ContentCard
            title="AI Summary"
            content={
              analysis.summary ||
              "No summary available."
            }
          />

          {/* RECOMMENDATION */}
          <ContentCard
            title="Recommended Action"
            content={
              analysis.recommendation ||
              "No recommendation available."
            }
          />

          {/* WORKFLOW */}
          <div
            style={{
              background: "#ffffff",
              padding: "25px",
              borderRadius: "12px",
              marginBottom: "20px",
              boxShadow:
                "0 2px 10px rgba(0,0,0,0.06)",
            }}
          >
            <h2
              style={{
                marginTop: 0,
                color: "#172033",
              }}
            >
              Litigation Workflow
            </h2>

            <WorkflowStep
              label="SCN"
              active={currentStage === "SCN"}
            />

            <WorkflowLine />

            <WorkflowStep
              label="SCN Reply"
              active={
                currentStage === "SCN_REPLY" ||
                nextStage === "SCN_REPLY"
              }
            />

            <WorkflowLine />

            <WorkflowStep
              label="OIO"
              active={currentStage === "OIO"}
            />

            <WorkflowLine />

            <WorkflowStep
              label="Appeal"
              active={
                currentStage === "APPEAL" ||
                nextStage === "APPEAL"
              }
            />

            <WorkflowLine />

            <WorkflowStep
              label="OIA"
              active={
                currentStage === "OIA" ||
                nextStage === "OIA"
              }
            />

            <WorkflowLine />

            <WorkflowStep
              label="Final Review"
              active={
                currentStage === "FINAL" ||
                nextStage === "FINAL"
              }
            />
          </div>

          {/* ACTION BUTTON */}
          {(analysis.reply_required ||
            analysis.appeal_required ||
            actionType) && (
            <div
              style={{
                textAlign: "center",
                marginTop: "25px",
              }}
            >
              <button
                onClick={() =>
                  (window.location.href = "/reply")
                }
                style={{
                  padding: "13px 30px",
                  background: "#111827",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "15px",
                  fontWeight: "600",
                }}
              >
                {actionLabel || "Open Next Action"} →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function InfoCard({
  title,
  value,
  valueColor = "#172033",
}) {
  return (
    <div
      style={{
        background: "#ffffff",
        padding: "20px",
        borderRadius: "12px",
        boxShadow:
          "0 2px 10px rgba(0,0,0,0.06)",
      }}
    >
      <p
        style={{
          margin: 0,
          color: "#6b7280",
          fontSize: "13px",
        }}
      >
        {title}
      </p>

      <h2
        style={{
          margin: "8px 0 0",
          color: valueColor,
          fontSize: "20px",
        }}
      >
        {value}
      </h2>
    </div>
  );
}

function ContentCard({ title, content }) {
  return (
    <div
      style={{
        background: "#ffffff",
        padding: "25px",
        borderRadius: "12px",
        marginBottom: "20px",
        boxShadow:
          "0 2px 10px rgba(0,0,0,0.06)",
      }}
    >
      <h2
        style={{
          marginTop: 0,
          color: "#172033",
        }}
      >
        {title}
      </h2>

      <p
        style={{
          color: "#4b5563",
          lineHeight: "1.7",
          fontSize: "15px",
          whiteSpace: "pre-wrap",
        }}
      >
        {content}
      </p>
    </div>
  );
}

function WorkflowStep({ label, active }) {
  return (
    <div
      style={{
        padding: "14px 18px",
        borderRadius: "8px",
        background: active ? "#2563eb" : "#f3f4f6",
        color: active ? "#ffffff" : "#374151",
        fontWeight: "700",
        border: active
          ? "2px solid #1d4ed8"
          : "1px solid #e5e7eb",
      }}
    >
      {label}
    </div>
  );
}

function WorkflowLine() {
  return (
    <div
      style={{
        width: "2px",
        height: "18px",
        background: "#d1d5db",
        marginLeft: "20px",
      }}
    />
  );
}

export default Analysis;