import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AdminLayout } from './components/admin/AdminLayout'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { PipelineProvider } from './context/PipelineContext'
import { ThemeProvider } from './context/ThemeContext'
import { AdminOverviewPage } from './pages/AdminOverviewPage'
import { AdminUsersPage } from './pages/AdminUsersPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { MuloPage } from './pages/MuloPage'
import { RecommenderPage } from './pages/RecommenderPage'
import { SiloPage } from './pages/SiloPage'
import { TrimmerPage } from './pages/TrimmerPage'
import './index.css'

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <PipelineProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Layout />}>
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<RegisterPage />} />
                <Route element={<ProtectedRoute />}>
                  <Route index element={<HomePage />} />
                  <Route path="recommender" element={<RecommenderPage />} />
                  <Route path="trimmer" element={<TrimmerPage />} />
                  <Route path="silo" element={<SiloPage />} />
                  <Route path="mulo" element={<MuloPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Route>
              </Route>
              <Route element={<ProtectedRoute />}>
                <Route path="admin" element={<AdminLayout />}>
                  <Route index element={<AdminOverviewPage />} />
                  <Route path="users" element={<AdminUsersPage />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
        </PipelineProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
