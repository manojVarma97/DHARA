import React, { useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_BASE || '/api';
const money = (paise) => paise == null ? 'Pending' : new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:2}).format(paise/100);

export default function App() {
  const [products,setProducts] = useState([]);
  const [orders,setOrders] = useState([]);
  const [error,setError] = useState('');
  const [loading,setLoading] = useState(true);

  async function load() {
    setLoading(true); setError('');
    try {
      const [p,o] = await Promise.all([
        fetch(`${API}/products`).then(r=>{if(!r.ok) throw new Error('Products API unavailable'); return r.json()}),
        fetch(`${API}/orders`).then(r=>{if(!r.ok) throw new Error('Orders API unavailable'); return r.json()})
      ]);
      setProducts(p); setOrders(o);
    } catch(e) { setError(`${e.message}. Check that the API and database are running.`); }
    finally { setLoading(false); }
  }
  useEffect(()=>{load()},[]);

  const totalOrders = orders.length;
  const paidOrders = orders.filter(o=>o.payment_status==='PAID').length;
  const pendingOrders = orders.filter(o=>o.payment_status==='PENDING').length;

  return <main className="shell">
    <header className="top">
      <div><div className="eyebrow">DHARA WATER · OPERATIONS</div><h1>Order dashboard</h1><p>Manage catalogue and monitor customer orders.</p></div>
      <button onClick={load}>↻ Refresh</button>
    </header>
    {error && <div className="error">{error}</div>}
    <section className="stats">
      <article><span>Total orders</span><strong>{totalOrders}</strong></article>
      <article><span>Paid orders</span><strong>{paidOrders}</strong></article>
      <article><span>Payment pending</span><strong>{pendingOrders}</strong></article>
    </section>
    <section className="panel">
      <div className="section-head"><div><h2>Product catalogue</h2><p>Configured Dhara selling prices</p></div></div>
      <div className="products">{products.map(p=><div className="product" key={p.sku}><div><b>{p.name}</b><small>{p.sku}</small></div><strong>{money(p.price_paise)}</strong></div>)}</div>
    </section>
    <section className="panel">
      <div className="section-head"><div><h2>Recent orders</h2><p>Latest 100 orders</p></div></div>
      {loading ? <p>Loading orders…</p> : <div className="table-wrap"><table><thead><tr><th>Order ID</th><th>Customer</th><th>City</th><th>Total</th><th>Payment</th><th>Delivery</th></tr></thead>
      <tbody>{orders.map(o=><tr key={o.order_code}><td>{o.order_code}</td><td>{o.customer_name}<small>{o.phone}</small></td><td>{o.city}</td><td>{money(o.total_paise)}</td><td><span className={`pill ${o.payment_status.toLowerCase()}`}>{o.payment_status}</span></td><td>{o.delivery_date}</td></tr>)}</tbody></table>
      {!orders.length && <p className="empty">No orders yet. Orders will appear here when the ordering API is connected.</p>}</div>}
    </section>
    <footer>Dhara Water · Self-hosted starter · Payment integration must be completed before live transactions.</footer>
  </main>;
}
