import { useEffect, useState } from "react";
import API from "../services/api";

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [role, setRole] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const payload = JSON.parse(atob(token.split(".")[1]));
    setRole(payload.role);

    fetchOrders(payload.role);
  }, []);

  const fetchOrders = async (role) => {
    const endpoint = role === "shop_owner" ? "/all-orders" : "/my-orders";
    try {
      const res = await API.get(endpoint);
      setOrders(res.data);
    } catch (err) {
      alert("Could not fetch orders");
    }
  };

  return (
    <div>
      <h2>{role === "shop_owner" ? "All Orders" : "My Orders"}</h2>
      {orders.map((o) => (
        <div key={o.order_id} style={{ border: "1px solid #ccc", marginBottom: "1rem", padding: "10px" }}>
          <p><b>Order ID:</b> {o.order_id}</p>
          <p><b>Date:</b> {o.order_date}</p>
          <p><b>Total:</b> ₹{o.total_amount}</p>
          {role === "shop_owner" && (
            <>
              <p><b>Customer:</b> {o.customer_name} ({o.customer_email})</p>
            </>
          )}
          <ul>
            {o.items.map((item, idx) => (
              <li key={idx}>
                {item.name} - ₹{item.price} x {item.quantity}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default Orders;
