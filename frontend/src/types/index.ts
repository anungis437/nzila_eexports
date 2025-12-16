// Core entity types matching Django backend models

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'dealer' | 'broker' | 'buyer'
  phone?: string
  company?: string
  created_at: string
}

export interface Vehicle {
  id: number
  dealer: number
  dealer_name?: string
  make: string
  model: string
  year: number
  vin: string
  condition: 'new' | 'used_excellent' | 'used_good' | 'used_fair'
  mileage: number
  color: string
  fuel_type?: string
  transmission?: string
  price_cad: string
  price_xof?: string
  status: 'available' | 'reserved' | 'sold' | 'shipped' | 'delivered'
  description?: string
  location: string
  main_image?: string
  images?: VehicleImage[]
  created_at: string
  updated_at: string
}

export interface VehicleImage {
  id: number
  vehicle: number
  image: string
  is_primary: boolean
  order: number
  created_at: string
}

export interface Lead {
  id: number
  buyer: number
  buyer_name?: string
  vehicle: number
  vehicle_details?: Vehicle
  broker?: number
  broker_name?: string
  status: 'new' | 'contacted' | 'qualified' | 'negotiating' | 'converted' | 'lost'
  source: 'website' | 'referral' | 'broker' | 'direct'
  notes?: string
  created_at: string
  updated_at: string
  last_contacted?: string
}

export interface Deal {
  id: number
  lead?: number
  vehicle: number
  vehicle_details?: Vehicle
  buyer: number
  buyer_name?: string
  dealer: number
  dealer_name?: string
  broker?: number
  broker_name?: string
  status: 'pending_docs' | 'docs_verified' | 'payment_pending' | 'payment_received' | 'ready_to_ship' | 'shipped' | 'completed' | 'cancelled'
  agreed_price_cad: string
  agreed_price_xof?: string
  payment_method?: string
  payment_status: 'pending' | 'partial' | 'paid' | 'refunded'
  commission_cad?: string
  documents?: any[]
  notes?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface Commission {
  id: number
  deal: number
  deal_id?: number
  deal_details?: Deal
  recipient: User
  commission_type: 'broker' | 'dealer'
  amount_cad: string
  percentage: string
  status: 'pending' | 'approved' | 'paid' | 'cancelled'
  notes?: string
  created_at: string
  approved_at?: string
  paid_at?: string
}

export interface ShipmentUpdate {
  id: number
  shipment: number
  location: string
  status: string
  description?: string
  created_at: string
}

export interface Shipment {
  id: number
  deal: number
  deal_id: number
  tracking_number: string
  shipping_company: string
  origin_port: string
  destination_port: string
  destination_country?: string
  status: 'pending' | 'in_transit' | 'customs' | 'delivered' | 'delayed'
  estimated_departure?: string
  actual_departure?: string
  estimated_arrival?: string
  actual_arrival?: string
  notes?: string
  updates?: ShipmentUpdate[]
  vehicle_details?: {
    id: number
    year: number
    make: string
    model: string
    vin: string
    color: string
  }
  created_at: string
  updated_at: string
}

// Form types
export interface ShipmentFormData {
  deal?: number
  tracking_number: string
  shipping_company: string
  origin_port: string
  destination_port: string
  destination_country?: string
  status?: Shipment['status']
  estimated_departure?: string
  estimated_arrival?: string
  notes?: string
}

export interface VehicleFormData {
  make: string
  model: string
  year: number
  vin: string
  condition: Vehicle['condition']
  mileage: number
  color: string
  fuel_type?: string
  transmission?: string
  price_cad: string
  status: Vehicle['status']
  description?: string
  location: string
  main_image?: File | string
}

export interface LeadFormData {
  vehicle: number
  buyer: number
  broker?: number
  status: Lead['status']
  source: Lead['source']
  notes?: string
}

export interface DealFormData {
  vehicle: number
  buyer: number
  broker?: number
  agreed_price_cad: string
  payment_method?: string
  notes?: string
}

// Pagination
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// API Response types
export interface APIError {
  detail?: string
  message?: string
  [key: string]: any
}
