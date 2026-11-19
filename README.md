# Node-RED starter flow

The imported flow exposes `POST /dhara/order-notification` and formats a customer confirmation message.

Example:
```json
{
  "phone": "919876543210",
  "order_code": "DH261119-ABC123",
  "total_rupees": 220,
  "delivery_date": "2026-11-20",
  "slot_name": "Morning",
  "payment_status": "PAID"
}
```

This flow does not yet send a WhatsApp message. Add an HTTP Request node using Meta WhatsApp Cloud API, configure the access token as a Node-RED credential/environment secret, and use an approved WhatsApp template for business-initiated messages outside the customer service window. Protect the Node-RED editor and webhook with authentication or a reverse proxy.
