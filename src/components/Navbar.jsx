import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const Navbar = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setIsLoggedIn(true);
      setRole(payload.role);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-md py-4 px-6 flex justify-between items-center">
      <Link to="/" className="text-2xl font-bold text-indigo-600 hover:opacity-80">
        KiranaEasy 🛒
      </Link>

      <div className="flex gap-6 items-center text-sm font-medium">
        {isLoggedIn && role === "customer" && (
          <Link to="/cart" className="text-gray-700 hover:text-indigo-600 transition">
            🛍 View Cart
          </Link>
        )}

        {!isLoggedIn ? (
          <>
            <Link to="/login" className="text-gray-700 hover:text-indigo-600 transition">
              Login
            </Link>
            <Link to="/register" className="text-gray-700 hover:text-indigo-600 transition">
              Register
            </Link>
          </>
        ) : (
          <button
            onClick={handleLogout}
            className="bg-indigo-600 text-white px-4 py-1.5 rounded hover:bg-indigo-700 transition"
          >
            Logout
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
