import { NavLink, Outlet } from 'react-router-dom'

function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export default function Layout() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-md bg-teal-700" />
            <div className="leading-tight">
              <div className="text-sm font-semibold text-slate-900">PartitionFinder</div>
              <div className="text-xs text-slate-500">Modern UI</div>
            </div>
          </div>

          <nav className="flex items-center gap-2">
            <NavLink
              to="/"
              className={({ isActive }) =>
                cx(
                  'rounded-md px-3 py-2 text-sm font-medium',
                  isActive ? 'bg-teal-50 text-teal-800' : 'text-slate-700 hover:bg-slate-100',
                )
              }
              end
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/new/upload"
              className={({ isActive }) =>
                cx(
                  'rounded-md px-3 py-2 text-sm font-medium',
                  isActive ? 'bg-teal-50 text-teal-800' : 'text-slate-700 hover:bg-slate-100',
                )
              }
            >
              New analysis
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-slate-500">
          PartitionFinder 2.1.1 • UI + API wrapper
        </div>
      </footer>
    </div>
  )
}
