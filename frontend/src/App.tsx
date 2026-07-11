import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { PipelineProvider } from './context/PipelineContext'
import { ThemeProvider } from './context/ThemeContext'
import { HomePage } from './pages/HomePage'
import { MuloPage } from './pages/MuloPage'
import { RecommenderPage } from './pages/RecommenderPage'
import { SiloPage } from './pages/SiloPage'
import { TrimmerPage } from './pages/TrimmerPage'
import './index.css'

export default function App() {
  return (
    <ThemeProvider>
      <PipelineProvider>
        <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="recommender" element={<RecommenderPage />} />
            <Route path="trimmer" element={<TrimmerPage />} />
            <Route path="silo" element={<SiloPage />} />
            <Route path="mulo" element={<MuloPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
        </BrowserRouter>
      </PipelineProvider>
    </ThemeProvider>
  )
}
