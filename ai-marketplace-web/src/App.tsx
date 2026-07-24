import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
import { ToastProvider } from '@/components/common/Toast'

import { HomePage } from '@/pages/HomePage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { SearchPage } from '@/pages/SearchPage'
import { ListingDetailPage } from '@/pages/ListingDetailPage'
import { SellerProfilePage } from '@/pages/SellerProfilePage'
import { CreateListingPage } from '@/pages/CreateListingPage'
import { EditListingPage } from '@/pages/EditListingPage'
import { MyListingsPage } from '@/pages/MyListingsPage'
import { FavoritesPage } from '@/pages/FavoritesPage'
import { MessagesPage } from '@/pages/MessagesPage'

import { AdminLayout } from '@/pages/admin/AdminLayout'
import { AdminOverviewPage } from '@/pages/admin/AdminOverviewPage'
import { AdminUsersPage } from '@/pages/admin/AdminUsersPage'
import { AdminListingsPage } from '@/pages/admin/AdminListingsPage'
import { AdminCategoriesPage } from '@/pages/admin/AdminCategoriesPage'

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/listing/:id" element={<ListingDetailPage />} />
              <Route path="/seller/:id" element={<SellerProfilePage />} />
              <Route path="/create" element={<ProtectedRoute><CreateListingPage /></ProtectedRoute>} />
              <Route path="/my-listings" element={<ProtectedRoute><MyListingsPage /></ProtectedRoute>} />
              <Route path="/my-listings/:id/edit" element={<ProtectedRoute><EditListingPage /></ProtectedRoute>} />
              <Route path="/favorites" element={<ProtectedRoute><FavoritesPage /></ProtectedRoute>} />
              <Route path="/messages" element={<ProtectedRoute><MessagesPage /></ProtectedRoute>} />
              <Route path="/messages/:conversationId" element={<ProtectedRoute><MessagesPage /></ProtectedRoute>} />

              <Route path="/admin" element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
                <Route index element={<AdminOverviewPage />} />
                <Route path="users" element={<AdminUsersPage />} />
                <Route path="listings" element={<AdminListingsPage />} />
                <Route path="categories" element={<AdminCategoriesPage />} />
              </Route>
            </Routes>
          </Layout>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  )
}
