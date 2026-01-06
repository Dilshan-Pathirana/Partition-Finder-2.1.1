import { useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import ConfigurePage from './pages/Configure'
import DashboardPage from './pages/Dashboard'
import MonitorPage from './pages/Monitor'
import ResultsPage from './pages/Results'
import RunPage from './pages/Run'
import UploadPage, { type UploadState } from './pages/Upload'
import { defaultConfigState, type ConfigState } from './state/newAnalysis'

export default function App() {
  const [upload, setUpload] = useState<UploadState>({ folder: '', alignmentPreview: null })
  const [config, setConfig] = useState<ConfigState>(defaultConfigState)

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />

        <Route path="/new/upload" element={<UploadPage state={upload} onChange={setUpload} />} />
        <Route
          path="/new/config"
          element={<ConfigurePage folder={upload.folder} state={config} onChange={setConfig} />}
        />
        <Route path="/new/run" element={<RunPage />} />

        <Route path="/jobs/:id/monitor" element={<MonitorPage />} />
        <Route path="/jobs/:id/results" element={<ResultsPage />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
