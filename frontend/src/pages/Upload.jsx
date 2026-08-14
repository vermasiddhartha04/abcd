import { useRef, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function Upload() {
  const fileInputRef = useRef(null);

  const [caseId] = useState(1);
  const [selectedFile, setSelectedFile] = useState(null);

  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  // ==========================================================
  // FILE SELECT
  // ==========================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    setError("");
    setMessage("");
    setResult(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setSelectedFile(null);
      setError("Only PDF files are allowed.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setSelectedFile(null);
      setError("File size must be less than 20 MB.");
      return;
    }

    setSelectedFile(file);
  };

  // ==========================================================
  // DRAG & DROP
  // ==========================================================

  const handleDrop = (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];

    setError("");
    setMessage("");
    setResult(null);

    if (!file) {
      return;
    }

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Only PDF files are allowed.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError("File size must be less than 20 MB.");
      return;
    }

    setSelectedFile(file);
  };

  // ==========================================================
  // ONE CLICK:
  //
  // UPLOAD
  //   ↓
  // OCR
  //   ↓
  // METADATA
  //   ↓
  // ANALYSIS
  //   ↓
  // REPLY / ACTION
  // ==========================================================

  const handleUploadAndAnalyze = async () => {
    setError("");
    setMessage("");
    setResult(null);

    if (!selectedFile) {
      setError("Please select or drop a PDF document first.");
      return;
    }

    setProcessing(true);

    try {
      // ======================================================
      // STEP 1 — UPLOAD
      // ======================================================

      setMessage("Uploading document...");

      const formData = new FormData();

      formData.append("case_id", caseId);
      formData.append("file", selectedFile);

      const uploadResponse = await fetch(
        `${API_BASE_URL}/uploads/`,
        {
          method: "POST",
          body: formData,
        }
      );

      const uploadData = await uploadResponse.json();

      console.log("UPLOAD RESPONSE:", uploadData);

      if (!uploadResponse.ok) {
        throw new Error(
          uploadData.detail ||
            uploadData.error ||
            "Document upload failed."
        );
      }

      const uploadId = uploadData.id;

      if (!uploadId) {
        throw new Error(
          "Upload succeeded but Upload ID was not returned."
        );
      }

      // ======================================================
      // STEP 2 — PROCESS EVERYTHING
      // ======================================================

      setMessage(
        "Document uploaded. Running OCR, metadata extraction, analysis and action generation..."
      );

      const processResponse = await fetch(
        `${API_BASE_URL}/process/${uploadId}`,
        {
          method: "POST",
        }
      );

      const processData = await processResponse.json();

      console.log("PROCESS RESPONSE:", processData);

      if (!processResponse.ok) {
        throw new Error(
          processData.detail ||
            processData.error ||
            "Document processing failed."
        );
      }

      if (!processData.success) {
        throw new Error(
          "Document processing was not successful."
        );
      }

      // ======================================================
      // FINAL RESULT
      // ======================================================

      setResult({
        ...processData,
        upload: uploadData,
      });

      setMessage(
        "Document processed successfully. Complete litigation report generated."
      );
    } catch (err) {
      console.error("DOCUMENT PROCESSING ERROR:", err);

      setError(
        err.message ||
          "Something went wrong while processing the document."
      );
    } finally {
      setProcessing(false);
    }
  };

  // ==========================================================
  // RESET
  // ==========================================================

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setMessage("");
    setError("");
    setProcessing(false);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // ==========================================================
  // FORMAT MONEY
  // ==========================================================

  const formatAmount = (value) => {
    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      return "Not Available";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
      return value;
    }

    return `₹${number.toLocaleString("en-IN")}`;
  };

  // ==========================================================
  // COPY TEXT
  // ==========================================================

  const copyText = async (text, successMessage) => {
    if (!text) {
      return;
    }

    try {
      await navigator.clipboard.writeText(text);

      setMessage(successMessage);
    } catch (err) {
      console.error(err);

      setError(
        "Copy failed. Please copy the text manually."
      );
    }
  };

  // ==========================================================
  // DOWNLOAD REPLY
  // ==========================================================

  const downloadReply = () => {
    const reply =
      result?.reply?.draft_reply || "";

    if (!reply) {
      setError("No draft reply is available.");
      return;
    }

    const blob = new Blob([reply], {
      type: "text/plain;charset=utf-8",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "GST_Litigation_Draft_Reply.txt";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  // ==========================================================
  // WORKFLOW
  // ==========================================================

  const documentType =
    result?.document?.document_type ||
    result?.analysis?.document_type ||
    result?.metadata?.document_type ||
    "Unknown";

  const currentStage =
    result?.document?.current_stage ||
    documentType;

  const nextStage =
    result?.document?.next_stage ||
    result?.analysis?.next_stage ||
    null;

  const actionLabel =
    result?.document?.action_label ||
    result?.analysis?.action_label ||
    "Review Document";

  const risk =
    result?.analysis?.risk_level ||
    "Unknown";

  const riskColor =
    risk === "High"
      ? "#dc2626"
      : risk === "Medium"
      ? "#d97706"
      : "#16a34a";

  const metadata = result?.metadata || {};
  const analysis = result?.analysis || {};
  const reply = result?.reply || null;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "30px",
        fontFamily: "Arial, sans-serif",
        boxSizing: "border-box",
      }}
    >
      {/* =====================================================
          HEADER
      ====================================================== */}

      <div
        style={{
          textAlign: "center",
          marginBottom: "30px",
        }}
      >
        <h1
          style={{
            fontSize: "48px",
            margin: "0 0 5px",
            color: "#111827",
          }}
        >
          GST Litigation AI
        </h1>

        <p
          style={{
            color: "#6b7280",
            fontSize: "18px",
            margin: 0,
          }}
        >
          Upload one GST document and automatically generate
          the complete litigation report.
        </p>
      </div>

      {/* =====================================================
          UPLOAD CARD
      ====================================================== */}

      {!result && (
        <div
          style={{
            maxWidth: "1050px",
            margin: "0 auto",
            background: "#ffffff",
            padding: "35px",
            borderRadius: "14px",
            boxShadow:
              "0 4px 18px rgba(0,0,0,0.08)",
          }}
        >
          <h2
            style={{
              textAlign: "center",
              marginTop: 0,
              color: "#111827",
            }}
          >
            Upload GST Document
          </h2>

          <p
            style={{
              textAlign: "center",
              color: "#6b7280",
            }}
          >
            Supported documents: SCN, OIO, Appeal,
            OIA and other GST-related PDF documents.
          </p>

          {/* DROP AREA */}

          <div
            onDragOver={(event) =>
              event.preventDefault()
            }
            onDrop={handleDrop}
            onClick={() =>
              !processing &&
              fileInputRef.current?.click()
            }
            style={{
              marginTop: "25px",
              border: "2px dashed #2563eb",
              borderRadius: "12px",
              padding: "45px 25px",
              textAlign: "center",
              background: "#eff6ff",
              cursor: processing
                ? "not-allowed"
                : "pointer",
            }}
          >
            <div
              style={{
                fontSize: "45px",
                marginBottom: "10px",
              }}
            >
              📄
            </div>

            <h3
              style={{
                margin: "5px 0",
                color: "#1d4ed8",
              }}
            >
              Drop your PDF here
            </h3>

            <p
              style={{
                color: "#6b7280",
              }}
            >
              or click here to choose a PDF
            </p>

            <input
              ref={fileInputRef}
              id="gst-file-input"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              style={{
                display: "none",
              }}
            />
          </div>

          {/* SELECTED FILE */}

          {selectedFile && (
            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                background: "#f9fafb",
                borderRadius: "10px",
                border:
                  "1px solid #e5e7eb",
              }}
            >
              <strong>
                Selected Document
              </strong>

              <p
                style={{
                  marginBottom: "5px",
                }}
              >
                {selectedFile.name}
              </p>

              <small
                style={{
                  color: "#6b7280",
                }}
              >
                {(selectedFile.size / 1024).toFixed(
                  2
                )}{" "}
                KB
              </small>
            </div>
          )}

          {/* INFO */}

          <p
            style={{
              textAlign: "center",
              color: "#777",
              fontSize: "13px",
              marginTop: "15px",
            }}
          >
            PDF only | Maximum size: 20 MB
          </p>

          {/* ONE BUTTON */}

          <div
            style={{
              textAlign: "center",
              marginTop: "25px",
            }}
          >
            <button
              onClick={handleUploadAndAnalyze}
              disabled={
                processing || !selectedFile
              }
              style={{
                padding: "15px 35px",
                background:
                  processing || !selectedFile
                    ? "#9ca3af"
                    : "#2563eb",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                cursor:
                  processing || !selectedFile
                    ? "not-allowed"
                    : "pointer",
                fontSize: "17px",
                fontWeight: "700",
              }}
            >
              {processing
                ? "Processing Document..."
                : "Upload & Analyze Document"}
            </button>
          </div>
        </div>
      )}

      {/* =====================================================
          STATUS
      ====================================================== */}

      {(message || error) && (
        <div
          style={{
            maxWidth: "1050px",
            margin: "20px auto",
            padding: "15px 20px",
            borderRadius: "8px",
            background: error
              ? "#fee2e2"
              : "#dcfce7",
            color: error
              ? "#991b1b"
              : "#166534",
          }}
        >
          {error || message}
        </div>
      )}

      {/* =====================================================
          COMPLETE REPORT
      ====================================================== */}

      {result && (
        <div
          style={{
            maxWidth: "1200px",
            margin: "25px auto",
          }}
        >
          {/* REPORT HEADER */}

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
                justifyContent:
                  "space-between",
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
                  }}
                >
                  DOCUMENT TYPE
                </p>

                <h1
                  style={{
                    margin:
                      "6px 0 0",
                  }}
                >
                  {documentType}
                </h1>
              </div>

              <div
                style={{
                  background: riskColor,
                  padding: "12px 22px",
                  borderRadius: "30px",
                  fontWeight: "700",
                }}
              >
                {risk} Risk
              </div>
            </div>

            <div
              style={{
                marginTop: "20px",
                borderTop:
                  "1px solid #374151",
                paddingTop: "18px",
              }}
            >
              <strong>
                Current Stage:
              </strong>{" "}
              {currentStage}

              {"  →  "}

              <strong>
                Next Stage:
              </strong>{" "}
              {nextStage || "Final Review"}
            </div>

            <div
              style={{
                marginTop: "10px",
              }}
            >
              <strong>
                Required Action:
              </strong>{" "}
              {actionLabel}
            </div>
          </div>

          {/* CASE INFORMATION */}

          <ReportCard title="Case & Document Information">
            <InfoGrid
              items={[
                ["Upload ID", result.upload_id],
                [
                  "OCR Result ID",
                  result.ocr_result_id,
                ],
                [
                  "Metadata ID",
                  result.metadata_id,
                ],
                [
                  "Analysis ID",
                  result.analysis_id,
                ],
                [
                  "Reply ID",
                  result.reply_id ||
                    "Not Required",
                ],
                [
                  "GSTIN",
                  metadata.gstin,
                ],
                [
                  "PAN",
                  metadata.pan,
                ],
                [
                  "Taxpayer",
                  metadata.taxpayer_name,
                ],
                [
                  "Notice Number",
                  metadata.notice_number,
                ],
                [
                  "Document Type",
                  metadata.document_type,
                ],
              ]}
            />
          </ReportCard>

          {/* FINANCIAL */}

          <ReportCard title="GST Financial Details">
            <InfoGrid
              items={[
                [
                  "Financial Year",
                  metadata.financial_year,
                ],
                [
                  "Tax Period",
                  metadata.tax_period,
                ],
                [
                  "Tax Proposed",
                  formatAmount(
                    metadata.tax_amount
                  ),
                ],
                [
                  "Interest",
                  formatAmount(
                    metadata.interest
                  ),
                ],
                [
                  "Penalty",
                  formatAmount(
                    metadata.penalty
                  ),
                ],
              ]}
            />
          </ReportCard>

          {/* SECTIONS */}

          <ReportCard title="Applicable GST Sections">
            <div
              style={{
                display: "flex",
                gap: "10px",
                flexWrap: "wrap",
              }}
            >
              {(analysis.sections ||
                String(
                  metadata.section || ""
                )
                  .split(",")
                  .map((x) => x.trim())
                  .filter(Boolean)
              ).map((section) => (
                <span
                  key={section}
                  style={{
                    padding:
                      "9px 16px",
                    background:
                      "#eff6ff",
                    color:
                      "#1d4ed8",
                    borderRadius:
                      "20px",
                    fontWeight:
                      "700",
                  }}
                >
                  Section {section}
                </span>
              ))}
            </div>
          </ReportCard>

          {/* SUMMARY */}

          <ReportCard title="AI Analysis Summary">
            <p
              style={{
                lineHeight: "1.7",
                color: "#374151",
                margin: 0,
              }}
            >
              {analysis.summary ||
                "No summary available."}
            </p>
          </ReportCard>

          {/* RECOMMENDATION */}

          <ReportCard title="Recommended Action">
            <p
              style={{
                lineHeight: "1.7",
                color: "#374151",
                margin: 0,
              }}
            >
              {analysis.recommendation ||
                "No recommendation available."}
            </p>
          </ReportCard>

          {/* ACTION STATUS */}

          <ReportCard title="Litigation Action">
            <InfoGrid
              items={[
                [
                  "Action Type",
                  analysis.action_type ||
                    result.document
                      ?.action_type ||
                    "Not Available",
                ],
                [
                  "Action Label",
                  actionLabel,
                ],
                [
                  "Current Stage",
                  currentStage,
                ],
                [
                  "Next Stage",
                  nextStage ||
                    "Final Review",
                ],
                [
                  "Reply Required",
                  analysis.reply_required
                    ? "YES"
                    : "NO",
                ],
                [
                  "Appeal Required",
                  analysis.appeal_required
                    ? "YES"
                    : "NO",
                ],
              ]}
            />
          </ReportCard>

          {/* REPLY */}

          {reply?.draft_reply && (
            <ReportCard title="Generated SCN Reply">
              <textarea
                value={reply.draft_reply}
                readOnly
                rows={22}
                style={{
                  width: "100%",
                  boxSizing:
                    "border-box",
                  padding: "15px",
                  border:
                    "1px solid #d1d5db",
                  borderRadius: "8px",
                  fontSize: "14px",
                  lineHeight: "1.6",
                  resize: "vertical",
                }}
              />

              <div
                style={{
                  display: "flex",
                  gap: "10px",
                  marginTop: "15px",
                  flexWrap: "wrap",
                }}
              >
                <button
                  onClick={() =>
                    copyText(
                      reply.draft_reply,
                      "Draft reply copied successfully."
                    )
                  }
                  style={buttonStyle(
                    "#2563eb"
                  )}
                >
                  Copy Reply
                </button>

                <button
                  onClick={downloadReply}
                  style={buttonStyle(
                    "#16a34a"
                  )}
                >
                  Download Reply
                </button>
              </div>
            </ReportCard>
          )}

          {/* WORKFLOW */}

          <ReportCard title="GST Litigation Workflow">
            <Workflow
              currentStage={currentStage}
              nextStage={nextStage}
            />
          </ReportCard>

          {/* ACTION */}

          <div
            style={{
              textAlign: "center",
              marginTop: "25px",
            }}
          >
            <div
              style={{
                fontSize: "20px",
                fontWeight: "700",
                marginBottom: "15px",
                color: "#111827",
              }}
            >
              {actionLabel}
            </div>

            <button
              onClick={() =>
                copyText(
                  JSON.stringify(
                    result,
                    null,
                    2
                  ),
                  "Complete report copied."
                )
              }
              style={buttonStyle(
                "#111827"
              )}
            >
              Copy Complete Report
            </button>

            <button
              onClick={handleReset}
              style={{
                ...buttonStyle(
                  "#6b7280"
                ),
                marginLeft: "10px",
              }}
            >
              Process Another Document
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ==========================================================
// REPORT CARD
// ==========================================================

function ReportCard({ title, children }) {
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
          color: "#111827",
        }}
      >
        {title}
      </h2>

      {children}
    </div>
  );
}

// ==========================================================
// INFO GRID
// ==========================================================

function InfoGrid({ items }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "15px",
      }}
    >
      {items.map(
        ([label, value], index) => (
          <div
            key={`${label}-${index}`}
            style={{
              padding: "15px",
              background:
                "#f9fafb",
              borderRadius: "8px",
              border:
                "1px solid #e5e7eb",
            }}
          >
            <div
              style={{
                color: "#6b7280",
                fontSize: "12px",
                marginBottom: "6px",
                textTransform:
                  "uppercase",
                fontWeight: "700",
              }}
            >
              {label}
            </div>

            <div
              style={{
                color: "#111827",
                fontWeight: "600",
                wordBreak:
                  "break-word",
              }}
            >
              {value ??
                "Not Available"}
            </div>
          </div>
        )
      )}
    </div>
  );
}

// ==========================================================
// WORKFLOW
// ==========================================================

function Workflow({
  currentStage,
  nextStage,
}) {
  const stages = [
    "SCN",
    "SCN_REPLY",
    "OIO",
    "APPEAL",
    "OIA",
    "FINAL",
  ];

  const activeIndex =
    stages.indexOf(currentStage);

  const nextIndex =
    stages.indexOf(nextStage);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        flexWrap: "wrap",
      }}
    >
      {stages.map(
        (stage, index) => {
          const active =
            index === activeIndex;

          const next =
            index === nextIndex;

          return (
            <div
              key={stage}
              style={{
                display: "flex",
                alignItems:
                  "center",
                gap: "8px",
              }}
            >
              <div
                style={{
                  padding:
                    "10px 14px",
                  borderRadius:
                    "20px",
                  background:
                    active
                      ? "#2563eb"
                      : next
                      ? "#dbeafe"
                      : "#f3f4f6",
                  color:
                    active
                      ? "#ffffff"
                      : "#374151",
                  fontWeight:
                    "700",
                  border:
                    active
                      ? "2px solid #1d4ed8"
                      : "1px solid #e5e7eb",
                }}
              >
                {stage.replace(
                  "_",
                  " "
                )}
              </div>

              {index <
                stages.length -
                  1 && (
                <span
                  style={{
                    color:
                      "#9ca3af",
                    fontWeight:
                      "700",
                  }}
                >
                  →
                </span>
              )}
            </div>
          );
        }
      )}
    </div>
  );
}

// ==========================================================
// BUTTON STYLE
// ==========================================================

function buttonStyle(
  background
) {
  return {
    padding:
      "11px 20px",
    background,
    color: "#ffffff",
    border: "none",
    borderRadius: "7px",
    cursor: "pointer",
    fontWeight: "700",
  };
}

export default Upload;