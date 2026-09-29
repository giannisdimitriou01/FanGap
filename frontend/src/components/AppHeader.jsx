import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }) =>
  `text-sm ${isActive ? 'text-slate-50' : 'text-slate-400 hover:text-slate-200'}`

export default function AppHeader() {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <NavLink to="/" className="text-lg font-semibold tracking-tight text-slate-50">
          FanGap
        </NavLink>
        <nav className="flex gap-5">
          <NavLink to="/" className={linkClass} end>
            Games
          </NavLink>
          <NavLink to="/leaderboard" className={linkClass}>
            Leaderboard
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
