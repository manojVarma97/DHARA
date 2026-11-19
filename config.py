import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://dhara_user:dhara_password@localhost:5432/dhara",
)
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
OUTSIDE_VZM_DELIVERY_FEE_PAISE = os.getenv("OUTSIDE_VZM_DELIVERY_FEE_PAISE", "")
