import { useCart } from "../context/CartContext";
import API from "../services/api";

const Cart = () => {
  const { cart, removeFromCart, clearCart } = useCart();

  const handlePlaceOrder = async () => {
    try {
      const items = cart.map((item) => ({
        product_id: item.id,
        quantity: item.quantity || 1,
      }));

      await API.post("/place-order", { items });
      alert("Order placed successfully!");
      clearCart();
    } catch (err) {
      alert(err.response?.data?.error || "Order failed");
    }
  };

  return (
    <div>
      <h2>Your Cart</h2>

      {cart.length === 0 ? (
        <p>No items in cart.</p>
      ) : (
        <>
          <ul>
            {cart.map((item) => (
              <li key={item.id} style={{ marginBottom: "10px" }}>
                <img src={item.image_url} alt={item.name} width="80" height="80" />
                <strong> {item.name} </strong> — ₹{item.price} x {item.quantity}
                <button onClick={() => removeFromCart(item.id)} style={{ marginLeft: "10px" }}>
                  Remove
                </button>
              </li>
            ))}
          </ul>

          <button onClick={handlePlaceOrder} style={{ marginTop: "20px" }}>
            Place Order
          </button>
        </>
      )}
    </div>
  );
};

export default Cart;
