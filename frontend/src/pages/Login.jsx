import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api/api";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { doLogin } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await login({ email, password });
      doLogin(res.data);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={submit} className="bg-white p-8 rounded-lg shadow-md w-80">
        <h1 className="text-2xl font-bold mb-6 text-center">Convoy</h1>
        <input
          type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border w-full p-2 rounded mb-3" required
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border w-full p-2 rounded mb-3" required
        />
        {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
        <button className="bg-blue-600 text-white w-full py-2 rounded hover:bg-blue-700">
          Log In
        </button>
        <p className="text-sm text-center mt-4 text-gray-600">
          Don't have an account?{" "}
          <Link to="/signup" className="text-blue-600 hover:underline">Sign Up</Link>
        </p>
      </form>
    </div>
  );
}