import { useState } from "react";
import { generateReply } from "../services/replyService";

function Reply() {
  const [analysisId, setAnalysisId] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const handleGenerate = async () => {
    if (!analysisId) {
      setError("Please enter Analysis ID.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setSaved(false);

      const data = await generateReply(
        Number(analysisId)
      );

      setReply(
        data?.draft_reply ||
          data?.reply?.draft_reply ||
          ""
      );
    } catch (err) {
      console.error("Reply Error:", err);

      setError(
        err?.response?.data?.detail ||
          "Failed to generate reply."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    if (!reply.trim()) {
      setError("Nothing to save.");
      return;
    }

    localStorage.setItem(
      "gst_litigation_reply",
      reply
    );

    setSaved(true);
    setError("");
  };

  const handleDownload = () => {
    if (!reply.trim()) {
      setError("Generate reply before downloading.");
      return;
    }

    const blob = new Blob([reply], {
      type: "text/plain;charset=utf-8",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "GST_SCN_Reply.txt";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

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
          GST Litigation Action
        </h1>

        <p
          style={{
            color: "#6b7280",
            marginTop: "8px",
          }}
        >
          Generate and manage the next action for the
          litigation case.
        </p>
      </div>

      {/* INPUT */}
      <div
        style={{
          background: "#ffffff",
          padding: "20px",
          borderRadius: "12px",
          boxShadow:
            "0 2px 10px rgba(0,0,0,0.06)",
          marginBottom: "20px",
        }}
      >
        <h3 style={{ marginTop: 0 }}>
          Analysis ID
        </h3>

        <div
          style={{
            display: "flex",
            gap: "12px",
            flexWrap: "wrap",
          }}
        >
          <input
            type="number"
            value={analysisId}
            onChange={(e) =>
              setAnalysisId(e.target.value)
            }
            placeholder="Enter Analysis ID"
            style={{
              padding: "12px",
              width: "220px",
              border:
                "1px solid #d1d5db",
              borderRadius: "7px",
            }}
          />

          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{
              padding: "12px 22px",
              background: loading
                ? "#93c5fd"
                : "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "7px",
              cursor: loading
                ? "not-allowed"
                : "pointer",
              fontWeight: "600",
            }}
          >
            {loading
              ? "Generating..."
              : "Generate Action"}
          </button>
        </div>

        {error && (
          <p
            style={{
              color: "#dc2626",
              marginTop: "15px",
            }}
          >
            {error}
          </p>
        )}

        {saved && (
          <p
            style={{
              color: "#16a34a",
              marginTop: "15px",
            }}
          >
            Reply saved successfully.
          </p>
        )}
      </div>

      {/* REPLY */}
      <div
        style={{
          background: "#ffffff",
          padding: "25px",
          borderRadius: "12px",
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
          Generated Reply / Action Draft
        </h2>

        <textarea
          value={reply}
          onChange={(e) => {
            setReply(e.target.value);
            setSaved(false);
          }}
          rows={25}
          placeholder="Generated reply will appear here..."
          style={{
            width: "100%",
            boxSizing: "border-box",
            padding: "15px",
            borderRadius: "8px",
            border:
              "1px solid #d1d5db",
            fontSize: "15px",
            lineHeight: "1.6",
            resize: "vertical",
          }}
        />

        <div
          style={{
            marginTop: "18px",
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
          }}
        >
          <button
            onClick={handleSave}
            style={{
              padding: "11px 20px",
              background: "#16a34a",
              color: "#ffffff",
              border: "none",
              borderRadius: "7px",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Save Draft
          </button>

          <button
            onClick={handleDownload}
            style={{
              padding: "11px 20px",
              background: "#ea580c",
              color: "#ffffff",
              border: "none",
              borderRadius: "7px",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Download Draft
          </button>
        </div>
      </div>
    </div>
  );
}

export default Reply;