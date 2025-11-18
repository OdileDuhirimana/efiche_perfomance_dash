/**
 * Main page layout component
 * Renders the dashboard with sidebar navigation and scroll-to-top button
 */
import DashboardLayout from "./sections/dashboard";
import Sidebar from "./components/sidebar";
import ScrollToTop from "./components/scroll-to-top";

export default function PageLayout() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <DashboardLayout/>
      <ScrollToTop />
    </div>
  );
}
