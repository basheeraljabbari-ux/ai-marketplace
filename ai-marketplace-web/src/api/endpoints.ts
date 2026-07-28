import { api } from './client'
import type { AuthTokens, BumpResult, Category, CategoryField, CategorySuggestion, City, Listing, ListingImage, PriceInsight, User, UserMe } from '@/types'

// ---------- Auth ----------
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post<AuthTokens>('/auth/register', data).then((r) => r.data),

  login: (data: { email: string; password: string }) =>
    api.post<AuthTokens>('/auth/login', data).then((r) => r.data),
}

// ---------- Users ----------
export const usersApi = {
  me: () => api.get<UserMe>('/users/me').then((r) => r.data),
  updateMe: (data: Partial<UserMe>) => api.put<UserMe>('/users/me', data).then((r) => r.data),

  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<UserMe>('/users/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },

  getPublic: (userId: string) => api.get<User>(`/users/${userId}`).then((r) => r.data),
  getListings: (userId: string, page = 1, limit = 20) =>
    api.get<Listing[]>(`/users/${userId}/listings`, { params: { page, limit } }).then((r) => r.data),
}

// ---------- Categories ----------
export const categoriesApi = {
  list: (parentId?: string) =>
    api.get<Category[]>('/categories', { params: parentId ? { parent_id: parentId } : {} }).then((r) => r.data),

  attributesSchema: (categoryId: string) =>
    api.get<{ category_id: string; fields: CategoryField[] }>(`/categories/${categoryId}/attributes-schema`).then((r) => r.data),
}

// ---------- Geo ----------
export const geoApi = {
  cities: () => api.get<City[]>('/cities').then((r) => r.data),
}

// ---------- Listings ----------
export interface SearchParams {
  q?: string
  city_id?: string
  category_id?: string
  price_min?: number
  price_max?: number
  condition?: string
  page?: number
  limit?: number
  // Dynamic per-category attribute filters, keyed by the field's `key` in the
  // category's attributesSchema. The backend treats any param outside the fixed
  // set above as an attribute filter, so no key needs declaring here.
  [attribute: string]: string | number | undefined
}

export const listingsApi = {
  search: (params: SearchParams) =>
    api.get<{ listing_ids: string[]; total: number; page: number }>('/listings', { params }).then((r) => r.data),

  get: (id: string) => api.get<Listing>(`/listings/${id}`).then((r) => r.data),

  // Current user's own listings across ALL statuses, with full data (images, last_bumped_at).
  // Distinct from usersApi.getListings() which is public and active-only.
  mine: () => api.get<Listing[]>('/listings/mine').then((r) => r.data),

  create: (data: Partial<Listing> & { title: string; condition: string }) =>
    api.post<Listing>('/listings', data).then((r) => r.data),

  update: (id: string, data: Partial<Listing>) => api.put<Listing>(`/listings/${id}`, data).then((r) => r.data),

  updateStatus: (id: string, status: string) =>
    api.patch<Listing>(`/listings/${id}/status`, { status }).then((r) => r.data),

  remove: (id: string) => api.delete(`/listings/${id}`),

  uploadImage: (id: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ListingImage>(`/listings/${id}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },

  aiGenerate: (imageUrls: string[], condition: string, listingId?: string) =>
    api.post<{ job_id: string; status: string; listing_id: string | null }>('/listings/ai-generate', {
      image_urls: imageUrls, condition, listing_id: listingId,
    }).then((r) => r.data),

  aiGenerateStatus: (jobId: string) =>
    api.get<{ job_id: string; status: string; listing_id: string | null }>(`/listings/ai-generate/${jobId}/status`).then((r) => r.data),

  priceInsight: (params: { category_id: string; condition?: string; exclude_listing_id?: string }) =>
    api.get<PriceInsight>('/listings/price-insight', { params }).then((r) => r.data),

  bump: (id: string) => api.post<BumpResult>(`/listings/${id}/bump`).then((r) => r.data),

  // Owner/admin only. Empty when the AI was confident enough to assign the category
  // itself, or when the listing predates the suggestions column.
  categorySuggestions: (id: string) =>
    api.get<CategorySuggestion[]>(`/listings/${id}/category-suggestions`).then((r) => r.data),
}

// ---------- Favorites ----------
export const favoritesApi = {
  list: () => api.get('/favorites').then((r) => r.data),
  add: (listingId: string) => api.post(`/favorites/${listingId}`),
  remove: (listingId: string) => api.delete(`/favorites/${listingId}`),
}

// ---------- Admin ----------
export interface AdminStats {
  total_users: number
  total_listings: number
  active_listings: number
  listings_today: number
  top_categories: { name: string; count: number }[]
}
export interface AdminUser {
  id: string
  email: string
  full_name: string
  role: string
  is_banned: boolean
  is_verified: boolean
  created_at: string
}

export const adminApi = {
  stats: () => api.get<AdminStats>('/admin/stats').then((r) => r.data),

  listUsers: (page = 1, limit = 50) =>
    api.get<AdminUser[]>('/admin/users', { params: { page, limit } }).then((r) => r.data),

  banUser: (userId: string, isBanned: boolean, reason?: string) =>
    api.patch<AdminUser>(`/admin/users/${userId}/ban`, { is_banned: isBanned, reason }).then((r) => r.data),

  listListings: (status?: string, page = 1, limit = 50) =>
    api.get<Listing[]>('/admin/listings', { params: { status, page, limit } }).then((r) => r.data),

  removeListing: (listingId: string, reason?: string) =>
    api.delete(`/admin/listings/${listingId}`, { params: { reason } }),

  createCategory: (data: { name_ar: string; name_en: string; slug: string; parent_id?: string; attributes_schema?: object }) =>
    api.post<Category>('/admin/categories', data).then((r) => r.data),
}

// ---------- Messaging ----------
export const messagingApi = {
  listConversations: () => api.get('/conversations').then((r) => r.data),
  startConversation: (listingId: string) => api.post('/conversations', { listing_id: listingId }).then((r) => r.data),
  listMessages: (conversationId: string) => api.get(`/conversations/${conversationId}/messages`).then((r) => r.data),
  sendMessage: (conversationId: string, content: string) =>
    api.post(`/conversations/${conversationId}/messages`, { content, message_type: 'text' }).then((r) => r.data),
}
