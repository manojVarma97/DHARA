# Dhara Water Automation

Open-source starter platform for Dhara Water: WhatsApp ordering, product catalogue, Razorpay payment integration, delivery-slot booking and an admin dashboard.

## Stack
- React + Vite frontend
- Python FastAPI backend
- PostgreSQL database
- Node-RED automation
- Docker Compose deployment
- Meta WhatsApp Cloud API and Razorpay as external commercial services

## Business configuration
| Product | Price |
|---|---:|
| 20 Litre | ₹110 |
| 5 Litre | ₹60 |
| 2 Litre | ₹30 |
| 1.5 Litre | ₹20 |
| 1 Litre | ₹20 |
| 500 ML | ₹10 |

Free delivery is configured for `VZM` / `Vizianagaram`. Delivery fee outside VZM is intentionally left unconfigured. The API returns `delivery_fee_pending=true` rather than inventing a charge.

Four default delivery windows are seeded:
- 09:00–12:00
- 12:00–15:00
- 15:00–18:00
- 18:00–21:00

Slot capacity defaults to 20 orders per slot/day and can be changed in the database.

## Quick start (Docker)
1. Copy `.env.example` to `.env` and change every secret/password.
2. Run `docker compose up --build -d`.
3. API docs: `http://localhost:8000/docs`
4. Admin frontend: `http://localhost:8080`
5. Node-RED: `http://localhost:1880` (protect it before exposing publicly).

The first startup seeds products and delivery slots.

## GitHub setup
Create a **private** GitHub repository named `dhara-water-automation`, then:

```bash
git init
git add .
git commit -m "Initial Dhara Water platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dhara-water-automation.git
git push -u origin main
```

## API endpoints
- `GET /health`
- `GET /api/products`
- `POST /api/orders/quote`
- `POST /api/orders`
- `GET /api/orders`
- `GET /api/orders/{order_code}`
- `GET /api/delivery-slots?delivery_date=YYYY-MM-DD`

## Quote example
```json
{
  "customer_name": "Test Customer",
  "phone": "919876543210",
  "city": "Vizianagaram",
  "address": "Sample address",
  "items": [{"sku": "W20", "quantity": 2}]
}
```
Expected subtotal and total: ₹220, free delivery.

## Important implementation boundaries
This is a runnable MVP foundation, not a production-certified payment or WhatsApp integration.
- Orders are created with `PENDING` payment status. No order is marked paid merely because the customer returns from a checkout page.
- Razorpay order creation and webhook signature verification must be configured before accepting live payments. The backend includes a safe webhook verification endpoint scaffold.
- WhatsApp Cloud API credentials and Meta webhook verification must be configured. Node-RED flow is a starter integration flow.
- Outside-VZM delivery fee is not configured.
- Slot booking is capacity-checked in the backend. For high-concurrency production use, use a database transaction/row lock or atomic reservation query; the MVP implementation uses a transaction and row-level lock.
- Configure HTTPS, backups, firewall, admin authentication, rate limiting, monitoring and secret management before public launch.

## Security
Never commit `.env`, access tokens, Razorpay secrets, database passwords, private keys or customer data. Use a private repository during development. Configure secrets on the VPS separately.

## License
MIT. See `LICENSE`.
