import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signup, getErrorMessage } from "../api/api";
import { useAuth } from "../context/AuthContext";

const ROLES = ["Fleet Manager", "Driver", "Safety Officer", "Financial Analyst"];

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState(ROLES[0]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { doLogin } = useAuth();
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await signup({ name, email, password, role });
      doLogin(res.data);
      navigate("/");
    } catch (err) {
      setError(getErrorMessage(err, "Signup failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={submit} className="bg-white p-8 rounded-lg shadow-md w-80">
        <h1 className="text-2xl font-bold mb-6 text-center">Convoy</h1>
        <input
          type="text" placeholder="Full name" value={name}
          onChange={(e) => setName(e.target.value)}
          className="border w-full p-2 rounded mb-3" required
        />
        <input
          type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border w-full p-2 rounded mb-3" required
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border w-full p-2 rounded mb-3" required minLength={6}
        />
        <select
          value={role} onChange={(e) => setRole(e.target.value)}
          className="border w-full p-2 rounded mb-3 bg-white"
        >
          {ROLES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
        <button
          disabled={loading}
          className="bg-blue-600 text-white w-full py-2 rounded hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? "Creating account..." : "Sign Up"}
        </button>
        <p className="text-sm text-center mt-4 text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">Log In</Link>
        </p>
      </form>
    </div>
  );
}
