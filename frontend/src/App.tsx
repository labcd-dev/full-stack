import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { UserThemeSync } from './components/UserThemeSync'
import { AdminLayout } from './components/admin/AdminLayout'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { PipelineProvider } from './context/PipelineContext'
import { ThemeProvider } from './context/ThemeContext'
import { AdminOverviewPage } from './pages/AdminOverviewPage'
import { AdminMonitoringPage } from './pages/AdminMonitoringPage'
import { AdminErrorsPage } from './pages/AdminErrorsPage'
import { AdminPlansPage } from './pages/AdminPlansPage'
import { AdminProjectDetailPage } from './pages/AdminProjectDetailPage'
import { AdminProjectsPage } from './pages/AdminProjectsPage'
import { AdminSurveyPage } from './pages/AdminSurveyPage'
import { AdminUsersPage } from './pages/AdminUsersPage'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { ProfilePage } from './pages/ProfilePage'
import { ProjectDetailPage } from './pages/ProjectDetailPage'
import { ProjectsPage } from './pages/ProjectsPage'
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
        <UserThemeSync />
        <PipelineProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<Layout />}>
                <Route path="login" element={<LoginPage />} />
                <Route path="register" element={<RegisterPage />} />
                <Route element={<ProtectedRoute />}>
                  <Route index element={<HomePage />} />
                  <Route path="projects" element={<ProjectsPage />} />
                  <Route path="projects/:projectId" element={<ProjectDetailPage />} />
                  <Route path="recommender" element={<RecommenderPage />} />
                  <Route path="trimmer" element={<TrimmerPage />} />
                  <Route path="silo" element={<SiloPage />} />
                  <Route path="mulo" element={<MuloPage />} />
                  <Route path="profile" element={<ProfilePage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Route>
              </Route>
              <Route element={<ProtectedRoute />}>
                <Route path="admin" element={<AdminLayout />}>
                  <Route index element={<AdminOverviewPage />} />
                  <Route path="monitoring" element={<AdminMonitoringPage />} />
                  <Route path="errors" element={<AdminErrorsPage />} />
                  <Route path="plans" element={<AdminPlansPage />} />
                  <Route path="users" element={<AdminUsersPage />} />
                  <Route path="projects" element={<AdminProjectsPage />} />
                  <Route path="projects/:projectId" element={<AdminProjectDetailPage />} />
                  <Route path="survey" element={<AdminSurveyPage />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
        </PipelineProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
