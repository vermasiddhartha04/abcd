function Navbar() {
  return (
    <header
      style={{
        height: "64px",
        background: "#ffffff",
        borderBottom:
          "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 25px",
        boxSizing: "border-box",
      }}
    >
      <div>
        <strong
          style={{
            color: "#172033",
            fontSize: "18px",
          }}
        >
          GST Litigation Management
        </strong>
      </div>

      <div
        style={{
          color: "#6b7280",
          fontSize: "14px",
        }}
      >
        SCN → Reply → OIO → Appeal → OIA
      </div>
    </header>
  );
}

export default Navbar;