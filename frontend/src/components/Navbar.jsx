import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, doLogout } = useAuth();
  const navigate = useNavigate();

  const logout = () => {
    doLogout();
    navigate("/login");
  };

  const links = [
    ["/", "Dashboard"],
    ["/vehicles", "Vehicles"],
    ["/drivers", "Drivers"],
    ["/trips", "Trips"],
    ["/maintenance", "Maintenance"],
  ];

  return (
    <nav className="bg-white shadow px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <span className="font-bold text-lg text-blue-600">Convoy</span>
        {links.map(([path, label]) => (
          <Link key={path} to={path} className="text-gray-600 hover:text-blue-600 text-sm font-medium">
            {label}
          </Link>
        ))}
      </div>
      <div className="flex items-center gap-3 text-sm">
        <span className="text-gray-500">{user?.name}</span>
        <button onClick={logout} className="text-red-600 hover:underline">Log Out</button>
      </div>
    </nav>
  );
}