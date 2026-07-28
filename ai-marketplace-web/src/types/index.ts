export interface User {
  id: string
  full_name: string
  avatar_url: string | null
  city_id: string | null
  rating_avg: number
  rating_count: number
  /* True for sellers with 3+ completed sales and a rating >= 4.0 (or no ratings yet). */
  is_verified_seller: boolean
  created_at: string
}

export interface UserMe extends User {
  email: string
  phone: string | null
  is_verified: boolean
  preferred_language: string
  role: string
}

export interface CategoryField {
  key: string
  label_ar: string
  /* Optional: categories seeded before label_en existed only carry label_ar. */
  label_en?: string
  type: 'text' | 'number' | 'select'
  required?: boolean
  filterable?: boolean
  searchable?: boolean
  options?: string[]
  min?: number
  max?: number
}

export interface Category {
  id: string
  parent_id: string | null
  name_ar: string
  name_en: string
  slug: string
  icon_url: string | null
}

export interface City {
  id: string
  country_id: string
  name_ar: string
  name_en: string
}

export interface ListingImage {
  id: string
  thumbnail_url: string | null
  optimized_url: string | null
  original_url: string
  sort_order: number
}

export interface Listing {
  id: string
  seller_id: string
  category_id: string | null
  city_id: string | null
  title: string
  description: string | null
  price: number | null
  currency: string
  condition: string | null
  status: 'draft' | 'active' | 'sold' | 'expired' | 'removed'
  attributes: Record<string, unknown>
  view_count: number
  is_ai_generated: boolean
  images: ListingImage[]
  published_at: string | null
  /* Last time the seller used a free bump; null if never. Gates the 48h bump cooldown. */
  last_bumped_at: string | null
  created_at: string
}

/* A category the AI thought likely but wasn't confident enough to auto-assign.
   Only ever returned to the listing's owner (or an admin). */
export interface CategorySuggestion {
  slug: string
  category_id: string
  name_en: string
  /* 0-1; rendered as a percentage on the quick-pick buttons. */
  confidence: number
}

export interface PriceInsight {
  category_id: string
  condition: string | null
  count: number
  min_price: number | null
  avg_price: number | null
  max_price: number | null
}

export interface BumpResult {
  id: string
  published_at: string | null
  last_bumped_at: string | null
  next_bump_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export type ListingCondition = 'new' | 'used_like_new' | 'used_good' | 'used_fair'

export const CONDITION_LABELS: Record<ListingCondition, string> = {
  new: 'New',
  used_like_new: 'Used - Like New',
  used_good: 'Used - Good',
  used_fair: 'Used - Fair',
}
