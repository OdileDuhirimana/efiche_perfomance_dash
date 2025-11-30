import DashboardLayout from "./sections/dashboard";
import Sidebar from "./components/sidebar";
import ScrollToTop from "./components/scroll-to-top";

export default function PageLayout() {
  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <Sidebar />
      <DashboardLayout/>
      <ScrollToTop />
    </div>
  );
}
