import { useEffect, useState } from "react";
import StatCard from "../components/dashboard/StatCard";
import RecentCases from "../components/dashboard/RecentCases";
import QuickActions from "../components/dashboard/QuickActions";

function Dashboard() {
  const [stats, setStats] = useState({
    totalCases: 0,
    pendingCases: 0,
    highRisk: 0,
    uploadedPdfs: 0,
    ocrProcessed: 0,
    repliesGenerated: 0,
  });

  useEffect(() => {
    /*
      Current backend dashboard API integration can be added
      once its exact response schema is confirmed.

      For now values remain zero instead of fake hard-coded
      production numbers.
    */
  }, []);

  return (
    <div
      style={{
        padding: "30px",
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
          GST Litigation AI Dashboard
        </h1>

        <p
          style={{
            color: "#6b7280",
            marginTop: "8px",
          }}
        >
          Overview of GST litigation cases, documents and
          actions.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(190px, 1fr))",
          gap: "18px",
          marginTop: "25px",
        }}
      >
        <StatCard
          title="Total Cases"
          value={stats.totalCases}
          color="#2563eb"
        />

        <StatCard
          title="Pending Cases"
          value={stats.pendingCases}
          color="#f59e0b"
        />

        <StatCard
          title="High Risk"
          value={stats.highRisk}
          color="#dc2626"
        />

        <StatCard
          title="Uploaded PDFs"
          value={stats.uploadedPdfs}
          color="#16a34a"
        />

        <StatCard
          title="OCR Processed"
          value={stats.ocrProcessed}
          color="#9333ea"
        />

        <StatCard
          title="Replies Generated"
          value={stats.repliesGenerated}
          color="#0891b2"
        />
      </div>

      <div style={{ marginTop: "30px" }}>
        <RecentCases />
      </div>

      <div style={{ marginTop: "30px" }}>
        <QuickActions />
      </div>
    </div>
  );
}

export default Dashboard;