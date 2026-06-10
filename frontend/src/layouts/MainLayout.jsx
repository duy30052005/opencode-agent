import { Outlet } from 'react-router-dom'
import SideNav from '../components/layout/SideNav'
import Toast from '../components/ui/Toast'

export default function MainLayout() {
  return (
    <div className="bg-background text-on-surface font-body-base antialiased h-screen w-screen overflow-hidden flex selection:bg-primary selection:text-on-primary relative">
      <SideNav />
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        <Outlet />
      </div>
      <Toast />
    </div>
  )
}
