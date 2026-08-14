import { NavLink } from "react-router-dom";

function Sidebar() {
  const links = [
    {
      label: "Dashboard",
      path: "/dashboard",
    },
    {
      label: "Cases",
      path: "/cases",
    },
    {
      label: "Upload Document",
      path: "/upload",
    },
    {
      label: "OCR",
      path: "/ocr",
    },
    {
      label: "Metadata",
      path: "/metadata",
    },
    {
      label: "Analysis",
      path: "/analysis",
    },
    {
      label: "Reply / Action",
      path: "/reply",
    },
  ];

  return (
    <aside
      style={{
        width: "240px",
        minHeight: "100vh",
        background: "#111827",
        color: "#ffffff",
        padding: "20px 12px",
        boxSizing: "border-box",
      }}
    >
      <h2
        style={{
          padding: "0 12px",
          marginBottom: "25px",
        }}
      >
        GST Litigation AI
      </h2>

      <nav>
        {links.map((link) => (
          <NavLink
            key={link.path}
            to={link.path}
            style={({ isActive }) => ({
              display: "block",
              padding: "12px",
              marginBottom: "6px",
              borderRadius: "7px",
              textDecoration: "none",
              color: "#ffffff",
              background: isActive
                ? "#2563eb"
                : "transparent",
              fontWeight: isActive
                ? "700"
                : "500",
            })}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;