import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import Upload from "./pages/Upload";
import OCR from "./pages/OCR";
import Metadata from "./pages/Metadata";
import Analysis from "./pages/Analysis";
import Reply from "./pages/Reply";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Default Route */}
        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

        {/* Case Management */}
        <Route
          path="/cases"
          element={<Cases />}
        />

        {/* Upload */}
        <Route
          path="/upload"
          element={<Upload />}
        />

        {/* OCR */}
        <Route
          path="/ocr"
          element={<OCR />}
        />

        {/* Metadata */}
        <Route
          path="/metadata"
          element={<Metadata />}
        />

        {/* AI Analysis */}
        <Route
          path="/analysis"
          element={<Analysis />}
        />

        {/* AI Reply */}
        <Route
          path="/reply"
          element={<Reply />}
        />

        {/* 404 */}
        <Route
          path="*"
          element={
            <div
              style={{
                textAlign: "center",
                marginTop: "80px",
                fontFamily: "Arial",
              }}
            >
              <h1>404</h1>
              <h2>Page Not Found</h2>
            </div>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;