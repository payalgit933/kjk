import { useEffect, useState } from "react";
import API from "../services/api";
import { useCart } from "../context/CartContext";
import { Link } from "react-router-dom";

const Products = () => {
  const [products, setProducts] = useState([]);
  const [userRole, setUserRole] = useState("");
  const { addToCart, cart } = useCart();
  const [message, setMessage] = useState("");

  const [form, setForm] = useState({
    name: "",
    category: "",
    price: "",
    stock: "",
    image_url: "",
  });

  useEffect(() => {
    fetchProducts();
    getRoleFromToken();
  }, []);

  const fetchProducts = async () => {
    const res = await API.get("/products");
    setProducts(res.data);
  };

  const getRoleFromToken = () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    const payload = JSON.parse(atob(token.split(".")[1]));
    setUserRole(payload.role);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      await API.post("/products", form);
      alert("Product added");
      setForm({ name: "", category: "", price: "", stock: "", image_url: "" });
      fetchProducts();
    } catch (err) {
      alert("Failed to add product");
    }
  };

  const handleAddToCart = (product) => {
    addToCart(product);
    setMessage(`${product.name} added to cart!`);
    console.log("Added to cart:", product);
    console.log("Cart after adding:", cart);
    setTimeout(() => setMessage(""), 1200);
  };

  const handleDelete = async (id) => {
    try {
      await API.delete(`/products/${id}`);
      fetchProducts();
    } catch (err) {
      alert("Failed to delete product");
    }
  };

  return (
    <div>
      <h2>Products</h2>
      <Link to="/cart">🛒 View Cart</Link>
      {message && <p style={{ color: "green", fontWeight: "bold" }}>{message}</p>}

      {userRole === "shop_owner" && (
        <form onSubmit={handleAddProduct}>
          <h3>Add Product</h3>
          <input name="name" placeholder="Name" value={form.name} onChange={handleChange} required /><br />
          <input name="category" placeholder="Category" value={form.category} onChange={handleChange} required /><br />
          <input name="price" type="number" placeholder="Price" value={form.price} onChange={handleChange} required /><br />
          <input name="stock" type="number" placeholder="Stock" value={form.stock} onChange={handleChange} required /><br />
          <input name="image_url" placeholder="Image URL" value={form.image_url} onChange={handleChange} required /><br />
          <button type="submit">Add Product</button>
        </form>
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginTop: "2rem" }}>
        {products.map((p) => (
          <div key={p.id} style={{ border: "1px solid gray", padding: "10px", width: "200px" }}>
            <img src={p.image_url} alt={p.name} width="100%" height="100" style={{ objectFit: "cover" }} />
            <h4>{p.name}</h4>
            <p>{p.category}</p>
            <p>₹{p.price}</p>
            <p>Stock: {p.stock}</p>

            {userRole === "customer" && (
              <button onClick={() => handleAddToCart(p)}>Add to Cart</button>
            )}

            {userRole === "shop_owner" && (
              <button onClick={() => handleDelete(p.id)}>Delete</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Products;
