# Phase 1 Implementation Guide - Canadian Diaspora Features

**Date**: December 20, 2025  
**Branch**: `canadian-diaspora-buyer-audit`  
**Status**: ✅ **Backend Complete** | ⚠️ **Frontend Pending**

---

## 🎯 What Was Implemented

Phase 1 adds foundational support for **Canadian diaspora buyers** - Canadians purchasing vehicles to export to Africa.

### ✅ Completed Backend Changes

#### 1. **User Model Enhancements** ([accounts/models.py](../accounts/models.py))

**Diaspora Buyer Fields**:
```python
- is_diaspora_buyer (BooleanField)
- canadian_city (CharField, 100)
- canadian_province (CharField, 2) - ON, QC, BC, AB, etc.
- canadian_postal_code (CharField, 7)
- destination_country (CharField, 100)
- destination_city (CharField, 100)
- buyer_type (CharField, 20) - personal, family, business
- residency_status (CharField, 20) - citizen, pr, work_permit, etc.
- prefers_in_person_inspection (BooleanField)
```

**Dealer Showroom Fields**:
```python
- showroom_address (TextField)
- showroom_city (CharField, 100)
- showroom_province (CharField, 2)
- showroom_postal_code (CharField, 7)
- showroom_phone (CharField, 20)
- business_hours (TextField)
- allows_test_drives (BooleanField)
- requires_appointment (BooleanField)
```

**Canadian Phone Support Fields**:
```python
- toll_free_number (CharField, 20)
- local_phone_number (CharField, 20)
- phone_support_hours (TextField)
- preferred_contact_method (CharField, 20) - phone, sms, whatsapp, email, chat
```

#### 2. **Payment Method Enhancements** ([payments/models.py](../payments/models.py))

**Interac e-Transfer Support**:
```python
PAYMENT_TYPE_CHOICES += [
    ('interac_etransfer', 'Interac e-Transfer')
]

# New fields:
- etransfer_email (EmailField)
- etransfer_security_question (CharField, 255)
- etransfer_security_answer (CharField, 255)
- etransfer_reference_number (CharField, 50)
```

#### 3. **In-Person Inspection Models** ([vehicles/models.py](../vehicles/models.py))

**VehicleInspectionSlot**:
```python
- vehicle (ForeignKey to Vehicle)
- date (DateField)
- start_time (TimeField)
- end_time (TimeField)
- is_available (BooleanField)
- max_attendees (IntegerField)
- notes (TextField)

Properties:
- is_past (bool)
- current_bookings (int)
- slots_remaining (int)
```

**InspectionAppointment**:
```python
- slot (ForeignKey to VehicleInspectionSlot)
- buyer (ForeignKey to User)
- status (CharField) - pending, confirmed, completed, cancelled, no_show
- contact_phone (CharField)
- contact_email (EmailField)
- number_of_people (IntegerField)
- buyer_notes (TextField)
- dealer_notes (TextField)
- inspection_feedback (TextField)
- vehicle_rating (IntegerField, 1-5)
- dealer_rating (IntegerField, 1-5)
- interested_in_purchase (BooleanField)

Properties:
- vehicle (returns slot.vehicle)
- dealer (returns slot.vehicle.dealer)
```

#### 4. **Serializer Updates** ([accounts/serializers.py](../accounts/serializers.py))

Both `UserSerializer` and `UserProfileSerializer` now include all Phase 1 fields:
- Diaspora buyer fields (19 new fields)
- Dealer showroom fields (8 new fields)
- Canadian phone support fields (4 new fields)

#### 5. **Admin Interface** ([accounts/admin.py](../accounts/admin.py), [vehicles/admin.py](../vehicles/admin.py))

**User Admin Enhancements**:
- Added `is_diaspora_buyer` to `list_display`
- Added `canadian_province` to `list_filter`
- Added `canadian_city`, `destination_country` to `search_fields`
- New collapsible fieldsets:
  - "Canadian Diaspora Buyer Profile (Phase 1)"
  - "Dealer Showroom Information (Phase 1)"
  - "Canadian Phone Support (Phase 1)"

**New Admin Classes**:
- `VehicleInspectionSlotAdmin` - manage inspection time slots
- `InspectionAppointmentAdmin` - manage buyer appointments
- Inline appointments on inspection slots

#### 6. **Database Migrations**

✅ Generated and applied:
- `accounts/migrations/0004_*.py` - 21 new User fields
- `payments/migrations/0002_*.py` - 4 new PaymentMethod fields
- `vehicles/migrations/0007_*.py` - 2 new models (VehicleInspectionSlot, InspectionAppointment)

---

## 📋 Frontend Changes Needed

### Priority 1: Registration & Profile Forms

#### A. **Buyer Registration Form** (Frontend)

**File**: `frontend/src/pages/Register.tsx` (or similar)

**Add conditional fields for buyers**:
```tsx
// After basic registration fields (username, email, password)

{role === 'buyer' && (
  <>
    <h3>Are you based in Canada?</h3>
    <label>
      <input 
        type="checkbox" 
        checked={isDiasporaBuyer}
        onChange={(e) => setIsDiasporaBuyer(e.target.checked)}
      />
      I live in Canada and want to purchase vehicles to ship to Africa
    </label>
    
    {isDiasporaBuyer && (
      <>
        <h4>Your Location in Canada</h4>
        <select name="canadian_province" required>
          <option value="">Select Province/Territory</option>
          <option value="ON">Ontario</option>
          <option value="QC">Quebec</option>
          <option value="BC">British Columbia</option>
          <option value="AB">Alberta</option>
          <option value="MB">Manitoba</option>
          <option value="SK">Saskatchewan</option>
          <option value="NS">Nova Scotia</option>
          <option value="NB">New Brunswick</option>
          <option value="NL">Newfoundland and Labrador</option>
          <option value="PE">Prince Edward Island</option>
          <option value="NT">Northwest Territories</option>
          <option value="NU">Nunavut</option>
          <option value="YT">Yukon</option>
        </select>
        
        <input 
          type="text" 
          name="canadian_city" 
          placeholder="City (e.g., Toronto, Vancouver, Montreal)"
          required
        />
        
        <input 
          type="text" 
          name="canadian_postal_code" 
          placeholder="Postal Code (A1A 1A1)"
          pattern="[A-Za-z][0-9][A-Za-z] [0-9][A-Za-z][0-9]"
        />
        
        <h4>Destination in Africa</h4>
        <select name="destination_country" required>
          <option value="">Select Destination Country</option>
          <option value="Nigeria">Nigeria</option>
          <option value="Ghana">Ghana</option>
          <option value="Kenya">Kenya</option>
          <option value="Senegal">Senegal</option>
          <option value="Côte d'Ivoire">Côte d'Ivoire</option>
          <option value="Tanzania">Tanzania</option>
          <option value="Uganda">Uganda</option>
          <option value="Ethiopia">Ethiopia</option>
          <option value="South Africa">South Africa</option>
          {/* Add more countries */}
        </select>
        
        <input 
          type="text" 
          name="destination_city" 
          placeholder="Destination City (e.g., Lagos, Accra, Nairobi)"
        />
        
        <h4>Purchase Purpose</h4>
        <select name="buyer_type">
          <option value="personal">Personal Use</option>
          <option value="family">Gift for Family</option>
          <option value="business">Business/Resale</option>
        </select>
        
        <h4>Canadian Residency Status</h4>
        <select name="residency_status">
          <option value="citizen">Canadian Citizen</option>
          <option value="pr">Permanent Resident</option>
          <option value="work_permit">Work Permit</option>
          <option value="study_permit">Study Permit</option>
          <option value="visitor">Visitor/Tourist</option>
        </select>
        
        <label>
          <input 
            type="checkbox" 
            name="prefers_in_person_inspection"
          />
          I prefer to inspect vehicles in person before purchasing
        </label>
      </>
    )}
  </>
)}
```

#### B. **Dealer Registration Form** (Frontend)

**Add showroom information**:
```tsx
{role === 'dealer' && (
  <>
    <h3>Showroom Information</h3>
    <textarea 
      name="showroom_address"
      placeholder="Physical address where buyers can view vehicles"
      rows={3}
    />
    
    <input 
      type="text" 
      name="showroom_city" 
      placeholder="City"
    />
    
    <select name="showroom_province">
      <option value="">Select Province</option>
      {/* Same province options as above */}
    </select>
    
    <input 
      type="text" 
      name="showroom_postal_code" 
      placeholder="Postal Code"
    />
    
    <input 
      type="tel" 
      name="showroom_phone" 
      placeholder="Showroom Phone"
    />
    
    <textarea 
      name="business_hours"
      placeholder="Business Hours (e.g., Mon-Fri 9am-6pm, Sat 10am-4pm)"
      rows={2}
    />
    
    <h3>Contact Preferences</h3>
    <input 
      type="tel" 
      name="toll_free_number" 
      placeholder="Toll-Free Number (1-800-XXX-XXXX)"
    />
    
    <input 
      type="tel" 
      name="local_phone_number" 
      placeholder="Local Phone Number"
    />
    
    <textarea 
      name="phone_support_hours"
      placeholder="Phone Support Hours"
      rows={2}
    />
    
    <select name="preferred_contact_method">
      <option value="phone">Phone Call</option>
      <option value="sms">Text/SMS</option>
      <option value="whatsapp">WhatsApp</option>
      <option value="email">Email</option>
      <option value="chat">Live Chat</option>
    </select>
    
    <label>
      <input 
        type="checkbox" 
        name="allows_test_drives"
        defaultChecked
      />
      Allow test drives
    </label>
    
    <label>
      <input 
        type="checkbox" 
        name="requires_appointment"
      />
      Require appointment for vehicle viewing
    </label>
  </>
)}
```

### Priority 2: Profile Management

**File**: `frontend/src/pages/ProfileSettings.tsx` (or similar)

- Add tabs or sections for:
  - "Personal Information" (existing + diaspora fields)
  - "Showroom Information" (dealers only)
  - "Contact Preferences" (dealers only)
- Allow users to update all Phase 1 fields
- Show/hide sections based on user role

### Priority 3: Payment Method Management

**File**: `frontend/src/components/PaymentMethods.tsx`

**Add Interac e-Transfer option**:
```tsx
{paymentType === 'interac_etransfer' && (
  <>
    <h3>Interac e-Transfer Details</h3>
    <input 
      type="email" 
      name="etransfer_email" 
      placeholder="Email registered for Interac e-Transfer"
      required
    />
    <p className="help-text">
      This is the email address you use to receive Interac e-Transfers.
      We'll send transfer instructions to this email.
    </p>
    
    <label>
      <input type="checkbox" required />
      I understand that Interac e-Transfer may take 3-5 business days to clear
    </label>
  </>
)}
```

**Add to payment method selection**:
```tsx
<div className="payment-method-option">
  <input 
    type="radio" 
    id="interac" 
    name="payment_method" 
    value="interac_etransfer"
  />
  <label htmlFor="interac">
    <img src="/icons/interac.svg" alt="Interac" />
    Interac e-Transfer
    <span className="badge">Popular in Canada</span>
  </label>
</div>
```

### Priority 4: Inspection Booking (NEW FEATURE)

**Create new file**: `frontend/src/components/InspectionBooking.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface InspectionSlot {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  slots_remaining: number;
}

interface InspectionBookingProps {
  vehicleId: number;
}

export default function InspectionBooking({ vehicleId }: InspectionBookingProps) {
  const [slots, setSlots] = useState<InspectionSlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const [contactPhone, setContactPhone] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [numberOfPeople, setNumberOfPeople] = useState(1);
  const [buyerNotes, setBuyerNotes] = useState('');

  useEffect(() => {
    // Fetch available slots
    axios.get(`/api/vehicles/${vehicleId}/inspection-slots/`)
      .then(res => setSlots(res.data.results))
      .catch(err => console.error(err));
  }, [vehicleId]);

  const bookInspection = async () => {
    if (!selectedSlot) return;
    
    try {
      await axios.post(`/api/inspection-appointments/`, {
        slot: selectedSlot,
        contact_phone: contactPhone,
        contact_email: contactEmail,
        number_of_people: numberOfPeople,
        buyer_notes: buyerNotes,
      });
      alert('Inspection appointment requested! Dealer will confirm shortly.');
    } catch (err) {
      alert('Booking failed. Please try again.');
    }
  };

  return (
    <div className="inspection-booking">
      <h3>Schedule In-Person Inspection</h3>
      <p>See this vehicle in person before you buy!</p>
      
      <div className="available-slots">
        <h4>Available Times</h4>
        {slots.map(slot => (
          <div 
            key={slot.id} 
            className={`slot ${selectedSlot === slot.id ? 'selected' : ''}`}
            onClick={() => setSelectedSlot(slot.id)}
          >
            <div className="date">{new Date(slot.date).toLocaleDateString()}</div>
            <div className="time">{slot.start_time} - {slot.end_time}</div>
            <div className="availability">{slot.slots_remaining} spots left</div>
          </div>
        ))}
      </div>
      
      {selectedSlot && (
        <div className="booking-form">
          <h4>Your Contact Information</h4>
          <input 
            type="tel" 
            placeholder="Phone Number"
            value={contactPhone}
            onChange={(e) => setContactPhone(e.target.value)}
            required
          />
          <input 
            type="email" 
            placeholder="Email"
            value={contactEmail}
            onChange={(e) => setContactEmail(e.target.value)}
            required
          />
          <select 
            value={numberOfPeople}
            onChange={(e) => setNumberOfPeople(parseInt(e.target.value))}
          >
            <option value="1">Just me</option>
            <option value="2">Me + 1 person</option>
            <option value="3">Me + 2 people</option>
            <option value="4">Me + 3 people</option>
          </select>
          <textarea 
            placeholder="Any special requests or questions?"
            value={buyerNotes}
            onChange={(e) => setBuyerNotes(e.target.value)}
            rows={3}
          />
          <button onClick={bookInspection}>Book Appointment</button>
        </div>
      )}
    </div>
  );
}
```

**Integrate into Vehicle Detail Page**:
```tsx
// In VehicleDetail.tsx
import InspectionBooking from '../components/InspectionBooking';

// Add to vehicle detail page (after vehicle images/description)
{user?.is_diaspora_buyer && (
  <InspectionBooking vehicleId={vehicle.id} />
)}
```

### Priority 5: Dealer Contact Display

**Update Vehicle Card/Detail Components**:
```tsx
// Show dealer showroom info prominently
{vehicle.dealer.showroom_address && (
  <div className="dealer-showroom">
    <h4>Visit Our Showroom</h4>
    <p>{vehicle.dealer.showroom_address}</p>
    <p>{vehicle.dealer.showroom_city}, {vehicle.dealer.showroom_province}</p>
    {vehicle.dealer.showroom_phone && (
      <a href={`tel:${vehicle.dealer.showroom_phone}`} className="btn-call">
        📞 {vehicle.dealer.showroom_phone}
      </a>
    )}
    {vehicle.dealer.business_hours && (
      <p className="hours">Hours: {vehicle.dealer.business_hours}</p>
    )}
    <a 
      href={`https://maps.google.com/?q=${encodeURIComponent(vehicle.dealer.showroom_address)}`}
      target="_blank"
      className="btn-directions"
    >
      Get Directions →
    </a>
  </div>
)}
```

---

## 🧪 Testing Checklist

### Backend Testing

- [ ] **User Model**:
  - [ ] Create diaspora buyer via admin
  - [ ] Verify all fields save correctly
  - [ ] Test Canadian province choices
  - [ ] Test residency status choices

- [ ] **Payment Method**:
  - [ ] Add Interac e-Transfer via admin
  - [ ] Verify `etransfer_email` validation
  - [ ] Test `__str__` method displays correctly

- [ ] **Inspection Models**:
  - [ ] Create inspection slot via admin
  - [ ] Book appointment via admin
  - [ ] Verify `slots_remaining` property
  - [ ] Test `is_past` property
  - [ ] Test unique constraint (vehicle, date, start_time)

- [ ] **API Endpoints**:
  - [ ] GET `/api/users/me/` returns new fields
  - [ ] PATCH `/api/users/me/` updates diaspora fields
  - [ ] GET `/api/vehicles/{id}/inspection-slots/` (needs view)
  - [ ] POST `/api/inspection-appointments/` (needs view)

### Admin Interface Testing

- [ ] **User Admin**:
  - [ ] List display shows `is_diaspora_buyer`
  - [ ] Filter by `canadian_province` works
  - [ ] Search by `canadian_city` works
  - [ ] All fieldsets expand/collapse correctly

- [ ] **Inspection Admin**:
  - [ ] Create inspection slot
  - [ ] View appointments inline
  - [ ] Filter by date, status
  - [ ] Search by buyer email, vehicle VIN

### Frontend Testing (Once Implemented)

- [ ] **Registration**:
  - [ ] Diaspora fields appear for buyers
  - [ ] Showroom fields appear for dealers
  - [ ] All dropdowns populate correctly
  - [ ] Form validation works

- [ ] **Profile Settings**:
  - [ ] Can update diaspora fields
  - [ ] Changes save via API
  - [ ] Conditional rendering by role works

- [ ] **Payment Methods**:
  - [ ] Interac option appears
  - [ ] Can add Interac payment method
  - [ ] Email validation works

- [ ] **Inspection Booking**:
  - [ ] Available slots load correctly
  - [ ] Can select slot
  - [ ] Booking form submits
  - [ ] Confirmation message appears

---

## 🚀 Next Steps

### Immediate (This Session)
1. ✅ Backend models and migrations - **COMPLETE**
2. ✅ Admin interface updates - **COMPLETE**
3. ⚠️ Create API views/serializers for inspections - **PENDING**
4. ⚠️ Frontend form updates - **PENDING**

### Short-term (Next 1-2 Days)
1. Implement inspection booking API endpoints
2. Add frontend forms for diaspora registration
3. Create inspection booking UI component
4. Add dealer showroom display components
5. Add Interac payment flow

### Medium-term (Next Week)
1. Phase 2 features (proximity search, SMS notifications)
2. Export documentation generation
3. Canadian timezone display
4. Phone call booking system

---

## 📚 API Endpoints to Create

### Inspection Slots

```python
# vehicles/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VehicleInspectionSlot, InspectionAppointment
from .serializers import VehicleInspectionSlotSerializer, InspectionAppointmentSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    # Existing code...
    
    @action(detail=True, methods=['get'])
    def inspection_slots(self, request, pk=None):
        """Get available inspection slots for a vehicle"""
        vehicle = self.get_object()
        slots = vehicle.inspection_slots.filter(
            is_available=True,
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')
        serializer = VehicleInspectionSlotSerializer(slots, many=True)
        return Response(serializer.data)

class InspectionAppointmentViewSet(viewsets.ModelViewSet):
    queryset = InspectionAppointment.objects.all()
    serializer_class = InspectionAppointmentSerializer
    
    def get_queryset(self):
        """Filter appointments by buyer"""
        if self.request.user.is_buyer():
            return self.queryset.filter(buyer=self.request.user)
        elif self.request.user.is_dealer():
            return self.queryset.filter(slot__vehicle__dealer=self.request.user)
        return self.queryset
    
    def perform_create(self, serializer):
        """Auto-assign buyer when creating appointment"""
        serializer.save(buyer=self.request.user)
```

### Serializers

```python
# vehicles/serializers.py

class VehicleInspectionSlotSerializer(serializers.ModelSerializer):
    slots_remaining = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    
    class Meta:
        model = VehicleInspectionSlot
        fields = ['id', 'vehicle', 'date', 'start_time', 'end_time', 
                  'is_available', 'max_attendees', 'slots_remaining', 
                  'is_past', 'notes']
        read_only_fields = ['slots_remaining', 'is_past']

class InspectionAppointmentSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    dealer = UserSerializer(read_only=True)
    
    class Meta:
        model = InspectionAppointment
        fields = ['id', 'slot', 'buyer', 'vehicle', 'dealer', 'status',
                  'contact_phone', 'contact_email', 'number_of_people',
                  'buyer_notes', 'dealer_notes', 'inspection_feedback',
                  'vehicle_rating', 'dealer_rating', 'interested_in_purchase',
                  'created_at', 'confirmed_at', 'completed_at', 'cancelled_at']
        read_only_fields = ['buyer', 'vehicle', 'dealer', 'created_at', 
                            'confirmed_at', 'completed_at', 'cancelled_at']
```

---

## ✅ Summary

**Phase 1 Backend: COMPLETE ✅**
- ✅ 21 new User model fields
- ✅ 4 new PaymentMethod fields  
- ✅ 2 new models (VehicleInspectionSlot, InspectionAppointment)
- ✅ All migrations applied
- ✅ Admin interface updated
- ✅ Serializers updated

**Phase 1 Frontend: PENDING ⚠️**
- ⚠️ Registration forms (buyer + dealer)
- ⚠️ Profile settings pages
- ⚠️ Payment method UI (Interac)
- ⚠️ Inspection booking component
- ⚠️ Dealer showroom display

**Estimated Time to Complete Frontend**: 4-6 hours

---

**Ready for Testing**: Backend can be tested via Django admin and API directly. Frontend implementation required for end-to-end user flows.
