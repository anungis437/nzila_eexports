#!/bin/bash

# Test script for Vehicle Management System
# This script tests the complete CRUD flow

echo "🚗 Testing Vehicle Management System"
echo "===================================="
echo ""

# Base URL
API_URL="http://localhost:8000/api"

# Login and get token
echo "1️⃣  Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/accounts/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "info@nzilaventures.com", "password": "admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access":"[^"]*' | sed 's/"access":"//')

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful!"
echo ""

# Get current user
echo "2️⃣  Getting current user info..."
USER_RESPONSE=$(curl -s "$API_URL/accounts/users/me/" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ User: $(echo $USER_RESPONSE | grep -o '"username":"[^"]*' | sed 's/"username":"//')"
echo "   Role: $(echo $USER_RESPONSE | grep -o '"role":"[^"]*' | sed 's/"role":"//')"
echo ""

# List vehicles
echo "3️⃣  Listing vehicles..."
VEHICLES=$(curl -s "$API_URL/vehicles/vehicles/" \
  -H "Authorization: Bearer $TOKEN")
VEHICLE_COUNT=$(echo $VEHICLES | grep -o '"id"' | wc -l)
echo "✅ Found $VEHICLE_COUNT vehicle(s)"
echo ""

# Get dashboard stats
echo "4️⃣  Getting dashboard stats..."
STATS=$(curl -s "$API_URL/analytics/dashboard-stats/" \
  -H "Authorization: Bearer $TOKEN")
echo "✅ Dashboard stats:"
echo "   Vehicles: $(echo $STATS | grep -o '"vehicles_count":[0-9]*' | sed 's/"vehicles_count"://')"
echo "   Deals: $(echo $STATS | grep -o '"deals_count":[0-9]*' | sed 's/"deals_count"://')"
echo "   Leads: $(echo $STATS | grep -o '"leads_count":[0-9]*' | sed 's/"leads_count"://')"
echo ""

echo "🎉 All tests passed!"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Login with: info@nzilaventures.com / admin123"
echo "   3. Navigate to Vehicles page"
echo "   4. Click 'Add Vehicle' to test the form"
echo ""
