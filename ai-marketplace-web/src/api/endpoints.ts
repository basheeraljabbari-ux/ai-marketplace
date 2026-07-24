import { api } from './client'
import type { AuthTokens, Category, CategoryField, Listing, ListingImage, User, UserMe } from '@/types'

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
  getPublic: (userId: string) =>
