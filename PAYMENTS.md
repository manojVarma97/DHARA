# Razorpay integration checklist

- Create Razorpay account and obtain test keys first.
- Create Razorpay Orders on the backend only; never expose the secret key to React or Node-RED.
- Store the Razorpay order ID against the Dhara order.
- Verify checkout signature on the backend.
- Verify webhook signature over the exact raw request body using HMAC-SHA256.
- Process `payment.captured` / `order.paid` idempotently.
- Match the event to a pending Dhara order and update status only after successful verification.
- Never mark paid based on a screenshot, query parameter or browser redirect alone.

The starter includes webhook signature verification but intentionally does not mark orders paid yet; mapping and idempotent database updates must be implemented and tested before live use.
