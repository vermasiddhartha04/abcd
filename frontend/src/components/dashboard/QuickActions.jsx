import { useNavigate } from "react-router-dom";

function QuickActions() {
  const navigate = useNavigate();

  return (
    <div className="quick-actions">

      <h2>Quick Actions</h2>

      <button onClick={() => navigate("/cases")}>
        Create Case
      </button>

      <button onClick={() => navigate("/upload")}>
        Upload PDF
      </button>

      <button onClick={() => navigate("/ocr")}>
        OCR
      </button>

      <button onClick={() => navigate("/metadata")}>
        Metadata
      </button>

      <button onClick={() => navigate("/analysis")}>
        Analysis
      </button>

      <button onClick={() => navigate("/reply")}>
        Reply
      </button>

    </div>
  );
}

export default QuickActions;
