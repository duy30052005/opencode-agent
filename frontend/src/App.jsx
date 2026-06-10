import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'

// Lazy loaded routes for performance (Task 14)
const GetStarted = lazy(() => import('./components/pages/GetStarted'))
const ActiveWorkspace = lazy(() => import('./components/pages/ActiveWorkspace'))
const HistoryPage = lazy(() => import('./components/pages/HistoryPage'))
const AnalyticsPage = lazy(() => import('./components/pages/AnalyticsPage'))
const SettingsPage = lazy(() => import('./components/pages/SettingsPage'))
const SuccessResult = lazy(() => import('./components/pages/SuccessResult'))
const StatusPage = lazy(() => import('./components/pages/StatusPage'))

// Fallback loader
const PageLoader = () => (
  <div className="w-full h-full flex items-center justify-center">
    <div className="w-8 h-8 rounded-full border-4 border-surface-container border-t-primary animate-spin" />
  </div>
)

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<GetStarted />} />
          <Route path="/workspace" element={<ActiveWorkspace />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/status" element={<StatusPage />} />
        </Route>
        {/* Full screen overlay (no SideNav) */}
        <Route path="/success" element={<SuccessResult />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
