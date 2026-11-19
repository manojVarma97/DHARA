CREATE TABLE IF NOT EXISTS products (
  sku TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  price_paise INTEGER NOT NULL CHECK (price_paise >= 0),
  active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS delivery_slots (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  capacity INTEGER NOT NULL DEFAULT 20 CHECK (capacity > 0),
  active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
  id BIGSERIAL PRIMARY KEY,
  order_code TEXT NOT NULL UNIQUE,
  customer_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  city TEXT NOT NULL,
  address TEXT NOT NULL,
  subtotal_paise INTEGER NOT NULL,
  delivery_fee_paise INTEGER,
  total_paise INTEGER,
  free_delivery BOOLEAN NOT NULL DEFAULT FALSE,
  delivery_fee_pending BOOLEAN NOT NULL DEFAULT FALSE,
  payment_status TEXT NOT NULL DEFAULT 'PENDING',
  order_status TEXT NOT NULL DEFAULT 'AWAITING_PAYMENT',
  delivery_date DATE NOT NULL,
  delivery_slot_id BIGINT REFERENCES delivery_slots(id),
  razorpay_order_id TEXT UNIQUE,
  razorpay_payment_id TEXT UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  sku TEXT NOT NULL REFERENCES products(sku),
  product_name TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_paise INTEGER NOT NULL,
  line_total_paise INTEGER NOT NULL
);

INSERT INTO products (sku,name,price_paise) VALUES
('W20','20 Litre',11000),
('W5','5 Litre',6000),
('W2','2 Litre',3000),
('W15','1.5 Litre',2000),
('W1','1 Litre',2000),
('W500','500 ML',1000)
ON CONFLICT (sku) DO UPDATE SET name=EXCLUDED.name, price_paise=EXCLUDED.price_paise;

INSERT INTO delivery_slots (name,start_time,end_time,capacity) VALUES
('Morning','09:00','12:00',20),
('Midday','12:00','15:00',20),
('Afternoon','15:00','18:00',20),
('Evening','18:00','21:00',20)
ON CONFLICT (name) DO NOTHING;
