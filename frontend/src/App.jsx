import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import GameDetail from './pages/GameDetail.jsx'
import GameList from './pages/GameList.jsx'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<GameList />} />
        <Route path="/games/:gameId" element={<GameDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
