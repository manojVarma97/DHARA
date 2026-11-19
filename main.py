from datetime import date
from uuid import uuid4
import hashlib
import hmac
import json

from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .db import get_db
from .models import Product, DeliverySlot, Order, OrderItem
from .schemas import OrderIn, QuoteIn
from .config import (
    RAZORPAY_WEBHOOK_SECRET,
    OUTSIDE_VZM_DELIVERY_FEE_PAISE,
)

app = FastAPI(title="Dhara Water API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your real frontend domain before production.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_vzm(city: str) -> bool:
    return city.strip().lower() in {"vzm", "vizianagaram", "vizianagaram urban"}

def price_cart(db: Session, items):
    result = []
    subtotal = 0
    for item in items:
        product = db.get(Product, item.sku)
        if not product or not product.active:
            raise HTTPException(400, f"Unknown or inactive product SKU: {item.sku}")
        line_total = product.price_paise * item.quantity
        subtotal += line_total
        result.append({
            "sku": product.sku,
            "name": product.name,
            "quantity": item.quantity,
            "unit_price_paise": product.price_paise,
            "line_total_paise": line_total,
        })
    return result, subtotal

@app.get("/health")
def health():
    return {"status": "ok", "service": "dhara-api"}

@app.get("/api/products")
def products(db: Session = Depends(get_db)):
    rows = db.scalars(select(Product).where(Product.active == True).order_by(Product.price_paise.desc())).all()
    return [{"sku": p.sku, "name": p.name, "price_paise": p.price_paise,
             "price_rupees": p.price_paise / 100} for p in rows]

@app.post("/api/orders/quote")
def quote(payload: QuoteIn, db: Session = Depends(get_db)):
    items, subtotal = price_cart(db, payload.items)
    free = is_vzm(payload.city)
    fee = 0 if free else (int(OUTSIDE_VZM_DELIVERY_FEE_PAISE) if OUTSIDE_VZM_DELIVERY_FEE_PAISE else None)
    pending = fee is None
    return {
        "items": items,
        "subtotal_paise": subtotal,
        "subtotal_rupees": subtotal / 100,
        "free_delivery": free,
        "delivery_fee_paise": fee,
        "delivery_fee_pending": pending,
        "total_paise": None if pending else subtotal + fee,
        "total_rupees": None if pending else (subtotal + fee) / 100,
        "currency": "INR",
    }

@app.get("/api/delivery-slots")
def delivery_slots(delivery_date: date, db: Session = Depends(get_db)):
    slots = db.scalars(select(DeliverySlot).where(DeliverySlot.active == True).order_by(DeliverySlot.start_time)).all()
    result = []
    for slot in slots:
        booked = db.scalar(
            select(func.count(Order.id)).where(
                Order.delivery_date == delivery_date,
                Order.delivery_slot_id == slot.id,
                Order.order_status != "CANCELLED",
            )
        ) or 0
        result.append({
            "id": slot.id, "name": slot.name,
            "start_time": slot.start_time.isoformat(),
            "end_time": slot.end_time.isoformat(),
            "capacity": slot.capacity, "booked": booked,
            "available": max(0, slot.capacity - booked),
        })
    return result

@app.post("/api/orders")
def create_order(payload: OrderIn, db: Session = Depends(get_db)):
    items, subtotal = price_cart(db, payload.items)
    free = is_vzm(payload.city)
    fee = 0 if free else (int(OUTSIDE_VZM_DELIVERY_FEE_PAISE) if OUTSIDE_VZM_DELIVERY_FEE_PAISE else None)
    if fee is None:
        raise HTTPException(422, "Delivery fee outside VZM is not configured. Contact Dhara to confirm delivery charge.")
    if payload.delivery_date < date.today():
        raise HTTPException(422, "Delivery date cannot be in the past.")
    if not payload.delivery_slot_id:
        raise HTTPException(422, "Select a delivery slot.")
    slot = db.scalar(select(DeliverySlot).where(DeliverySlot.id == payload.delivery_slot_id).with_for_update())
    if not slot or not slot.active:
        raise HTTPException(422, "Selected delivery slot is unavailable.")
    booked = db.scalar(
        select(func.count(Order.id)).where(
            Order.delivery_date == payload.delivery_date,
            Order.delivery_slot_id == slot.id,
            Order.order_status != "CANCELLED",
        )
    ) or 0
    if booked >= slot.capacity:
        raise HTTPException(409, "This delivery slot is full. Please choose another slot.")
    code = "DH" + payload.delivery_date.strftime("%y%m%d") + "-" + uuid4().hex[:6].upper()
    order = Order(
        order_code=code, customer_name=payload.customer_name,
        phone=payload.phone, city=payload.city, address=payload.address,
        subtotal_paise=subtotal, delivery_fee_paise=fee,
        total_paise=subtotal + fee, free_delivery=free,
        delivery_fee_pending=False, payment_status="PENDING",
        order_status="AWAITING_PAYMENT", delivery_date=payload.delivery_date,
        delivery_slot_id=slot.id,
    )
    order.items = [
        OrderItem(sku=i["sku"], product_name=i["name"], quantity=i["quantity"],
                  unit_price_paise=i["unit_price_paise"], line_total_paise=i["line_total_paise"])
        for i in items
    ]
    db.add(order)
    db.commit()
    db.refresh(order)
    return {
        "order_code": order.order_code,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "subtotal_paise": order.subtotal_paise,
        "delivery_fee_paise": order.delivery_fee_paise,
        "total_paise": order.total_paise,
        "delivery_date": str(order.delivery_date),
        "delivery_slot": slot.name,
        "message": "Order created. Payment integration must be configured before accepting live payments.",
    }

@app.get("/api/orders")
def list_orders(limit: int = 100, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 500))
    rows = db.scalars(select(Order).order_by(Order.created_at.desc()).limit(limit)).all()
    return [{
        "order_code": o.order_code, "customer_name": o.customer_name,
        "phone": o.phone, "city": o.city, "total_paise": o.total_paise,
        "payment_status": o.payment_status, "order_status": o.order_status,
        "delivery_date": str(o.delivery_date),
    } for o in rows]

@app.get("/api/orders/{order_code}")
def get_order(order_code: str, db: Session = Depends(get_db)):
    o = db.scalar(select(Order).where(Order.order_code == order_code))
    if not o:
        raise HTTPException(404, "Order not found")
    return {
        "order_code": o.order_code, "customer_name": o.customer_name,
        "phone": o.phone, "city": o.city, "address": o.address,
        "items": [{"sku": i.sku, "name": i.product_name, "quantity": i.quantity,
                   "unit_price_paise": i.unit_price_paise, "line_total_paise": i.line_total_paise}
                  for i in o.items],
        "total_paise": o.total_paise, "payment_status": o.payment_status,
        "order_status": o.order_status, "delivery_date": str(o.delivery_date),
    }

@app.post("/api/payments/razorpay/webhook")
async def razorpay_webhook(request: Request, x_razorpay_signature: str | None = Header(default=None)):
    raw = await request.body()
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(503, "Razorpay webhook secret is not configured")
    if not x_razorpay_signature:
        raise HTTPException(400, "Missing Razorpay signature")
    expected = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode("utf-8"), raw, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, x_razorpay_signature):
        raise HTTPException(400, "Invalid Razorpay webhook signature")
    payload = json.loads(raw.decode("utf-8"))
    # TODO: persist idempotently; map Razorpay order_id to Dhara order.
    # Only accept payment.captured/order.paid and verify the associated order.
    return {"received": True, "event": payload.get("event"), "signature_verified": True,
            "business_update": "Not implemented yet; no order is marked PAID by this scaffold."}
