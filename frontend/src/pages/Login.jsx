import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../services/authService";

const Login = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const submit = async (e) => {
    e.preventDefault();

    try {
      const data = await login(email, password);

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      navigate("/dashboard");
    } catch (err) {
      alert("Login Failed");
      console.error(err);
    }
  };

  return (
    <div
      style={{
        padding: 40,
      }}
    >
      <h1>GST Litigation AI</h1>

      <form onSubmit={submit}>
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
          />
        </div>

        <br />

        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
          />
        </div>

        <br />

        <button type="submit">
          Login
        </button>
      </form>
    </div>
  );
};

export default Login;