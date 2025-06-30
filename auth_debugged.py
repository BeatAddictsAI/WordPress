import os
import stripe
import ssl
from functools import wraps
from flask import request, jsonify

print("🔐 auth.py loaded")

stripe.api_key = os.getenv("STRIPE_SECRET")
PLATINUM_PRICE_ID = os.getenv("PLATINUM_PRICE_ID")

def get_customer_tier(customer_id):
    print(f"🔎 Checking tier for customer: {customer_id}")
    try:
        subs = stripe.Subscription.list(customer=customer_id, status='active', limit=1)
        if subs is None or not subs.data:
            print("❌ No active subscriptions found or subscription object is None.")
            return "free"

        price_id = subs.data[0]["items"]["data"][0]["price"]["id"]
        print(f"💳 Stripe price_id = {price_id}")

        if price_id == PLATINUM_PRICE_ID:
            return "platinum"
        return "pro"

    except Exception as e:
        print("⚠️ Stripe check failed:", e)
        return "free"

def requires_tier(required):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            customer_id = request.json.get("customer_id")
            if not customer_id:
                return jsonify({"error": "Missing customer_id"}), 400

            user_tier = get_customer_tier(customer_id)
            print(f"✅ Detected tier: {user_tier} (requires: {required})")

            tiers = ["free", "pro", "platinum"]
            if tiers.index(user_tier) >= tiers.index(required):
                return f(*args, **kwargs)
            else:
                return jsonify({"error": f"{required} tier required"}), 403
        return wrapper
    return decorator
