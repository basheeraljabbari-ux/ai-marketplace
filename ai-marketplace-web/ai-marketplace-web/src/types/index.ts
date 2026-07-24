export interface User {
  id: string
  full_name: string
  avatar_url: string | null
  city_id: string | null
  rating_avg: number
  rating_count: number
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
  created_at: string
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
