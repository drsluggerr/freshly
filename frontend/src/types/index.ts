export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  role: 'admin' | 'editor' | 'viewer'
  household_id?: number
  created_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export type UnitType = 'oz' | 'lb' | 'g' | 'kg' | 'fl_oz' | 'cup' | 'ml' | 'L' | 'item' | 'serving'

export type ItemCategory =
  | 'produce'
  | 'dairy'
  | 'meat'
  | 'seafood'
  | 'bakery'
  | 'frozen'
  | 'canned'
  | 'dry_goods'
  | 'beverages'
  | 'snacks'
  | 'condiments'
  | 'spices'
  | 'other'

export interface InventoryItem {
  id: number
  name: string
  category: ItemCategory
  quantity: number
  unit: UnitType
  original_quantity?: number
  barcode?: string
  purchase_date: string
  expiration_date?: string
  opened_date?: string
  location_id?: number
  price?: number
  currency?: string
  is_opened: boolean
  is_wasted: boolean
  waste_reason?: string
  wasted_date?: string
  notes?: string
  brand?: string
  store?: string
  image_url?: string
  added_by?: number
  household_id?: number
  created_at: string
  updated_at?: string
}

export interface InventoryItemCreate {
  name: string
  category: ItemCategory
  quantity: number
  unit: UnitType
  barcode?: string
  expiration_date?: string
  location_id?: number
  price?: number
  notes?: string
  brand?: string
  store?: string
}

export interface Receipt {
  id: number
  uploaded_by_id: number
  household_id?: number
  merchant_name?: string
  merchant_address?: string
  purchase_date?: string
  total_amount?: number
  tax_amount?: number
  currency: string
  receipt_number?: string
  payment_method?: string
  image_url?: string
  image_path?: string
  ocr_provider?: string
  processing_time_ms?: number
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  processing_error?: string
  is_duplicate: boolean
  duplicate_of_id?: number
  is_processed: boolean
  items_added: boolean
  created_at: string
  updated_at?: string
  line_items: ReceiptLineItem[]
}

export interface ReceiptLineItem {
  id: number
  receipt_id: number
  description: string
  quantity: number
  unit_price?: number
  total_price?: number
  matched_product_id?: number
  confidence_score?: number
  user_corrected_name?: string
  category?: string
  created_at: string
}

export interface MealSuggestion {
  name: string
  description: string
  ingredients_from_inventory: string[]
  additional_ingredients?: string[]
  prep_time: number
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface ShoppingList {
  id: number
  household_id?: number
  created_by_id: number
  name: string
  store?: string
  status: 'active' | 'completed' | 'archived'
  generated_from_meal_plan: boolean
  meal_plan_id?: number
  created_at: string
  updated_at?: string
  completed_at?: string
  items: ShoppingListItem[]
}

export interface ShoppingListItem {
  id: number
  shopping_list_id: number
  name: string
  quantity: number
  unit?: string
  category?: string
  aisle?: string
  estimated_price?: number
  actual_price?: number
  store?: string
  is_purchased: boolean
  purchased_at?: string
  is_staple: boolean
  notes?: string
  already_have_warning: boolean
  inventory_item_id?: number
  created_at: string
  updated_at?: string
}

export interface WasteStats {
  total_wasted_items: number
  total_value_wasted: number
  waste_by_category: Array<{
    category: string
    count: number
    total_value: number
  }>
  most_wasted_items: Array<{
    name: string
    count: number
  }>
  waste_reasons: Array<{
    reason: string
    count: number
  }>
}

export interface SpendingStats {
  total_spent: number
  spending_by_category: Array<{
    category: string
    total: number
    count: number
  }>
  spending_timeline: Array<{
    date: string
    total: number
  }>
}
