/** Sidebar navigation component */
"use client";

import { useState, useEffect } from "react";
import NavItem from "./nav-item";
import { navigationItems } from "../constants/navigation";
import { Menu, X } from "lucide-react";
import { useExecutiveSummary } from "@/lib/hooks/use-dashboard-data";
import { useThroughputData } from "@/lib/hooks/use-dashboard-data";

export default function Sidebar() {
  const [activeItem, setActiveItem] = useState("executive-summary");
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  
  const { data: executiveData, loading: executiveLoading } = useExecutiveSummary();
  
  const completionRate = executiveData?.completionRate || 0;
  
  const activeTasks = executiveData
    ? Math.max(0, (executiveData.planned || 0) - (executiveData.done || 0))
    : 0;
  
  const isLoading = executiveLoading;

  const sectionIdMap: Record<string, string> = {
    'executive-summary': 'executive-summary',
    'throughput': 'throughput-predictability',
    'quality': 'quality-rework',
    'ownership': 'ownership-distribution',
    'company-trend': 'company-level',
  };

  const navIdMap: Record<string, string> = {
    'executive-summary': 'executive-summary',
    'throughput-predictability': 'throughput',
    'quality-rework': 'quality',
    'ownership-distribution': 'ownership',
    'company-level': 'company-trend',
  };

  useEffect(() => {
    let observer: IntersectionObserver | null = null;
    let scrollTimeout: NodeJS.Timeout;
    const sections = Object.keys(sectionIdMap).map(key => ({
      navId: key,
      sectionId: sectionIdMap[key],
    }));

    const timeoutId = setTimeout(() => {
      const observerOptions = {
        root: null,
        rootMargin: '-100px 0px -60% 0px',
        threshold: [0, 0.1, 0.5, 1],
      };
      
      const observerCallback = (entries: IntersectionObserverEntry[]) => {
        clearTimeout(scrollTimeout);
        
        scrollTimeout = setTimeout(() => {
          let maxIntersection = 0;
          let activeSectionId = 'executive-summary';

          entries.forEach((entry) => {
            if (entry.isIntersecting && entry.intersectionRatio > maxIntersection) {
              maxIntersection = entry.intersectionRatio;
              activeSectionId = entry.target.id;
            }
          });

          if (maxIntersection === 0) {
            const scrollPosition = window.scrollY + 150;
            sections.forEach(({ sectionId }) => {
              const element = document.getElementById(sectionId);
              if (element) {
                const rect = element.getBoundingClientRect();
                const elementTop = rect.top + window.scrollY;
                const elementBottom = elementTop + rect.height;
                
                if (scrollPosition >= elementTop && scrollPosition < elementBottom) {
                  activeSectionId = sectionId;
                }
              }
            });
          }

          if (navIdMap[activeSectionId]) {
            setActiveItem(navIdMap[activeSectionId]);
          }
        }, 100);
      };

      observer = new IntersectionObserver(observerCallback, observerOptions);

      sections.forEach(({ sectionId }) => {
        const element = document.getElementById(sectionId);
        if (element) {
          observer!.observe(element);
        }
      });

      const checkInitialSection = () => {
        const scrollPosition = window.scrollY + 150;
        sections.forEach(({ sectionId, navId }) => {
          const element = document.getElementById(sectionId);
          if (element) {
            const rect = element.getBoundingClientRect();
            const elementTop = rect.top + window.scrollY;
            const elementBottom = elementTop + rect.height;
            
            if (scrollPosition >= elementTop && scrollPosition < elementBottom) {
              setActiveItem(navId);
            }
          }
        });
      };
      
      checkInitialSection();
    }, 500);

    return () => {
      clearTimeout(timeoutId);
      clearTimeout(scrollTimeout);
      if (observer) {
        sections.forEach(({ sectionId }) => {
          const element = document.getElementById(sectionId);
          if (element) {
            observer!.unobserve(element);
          }
        });
      }
    };
  }, []); // Run once on mount

  const handleNavClick = (itemId: string) => {
    setActiveItem(itemId);
    setIsMobileOpen(false);
    
    const sectionId = sectionIdMap[itemId] || itemId;
    
    // Small delay to ensure DOM is ready
    setTimeout(() => {
      const element = document.getElementById(sectionId);
      if (element) {
        const offset = 100; // Offset for fixed header
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    }, 100);
  };

  const toggleMobileMenu = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  return (
    <>
      {/* Mobile menu button*/}
      <button
        onClick={toggleMobileMenu}
        className="lg:hidden fixed top-6 left-6 z-50 w-10 h-10 rounded-lg bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-colors flex items-center justify-center"
        aria-label="Toggle menu"
      >
        {isMobileOpen ? (
          <X className="w-5 h-5 text-gray-700" />
        ) : (
          <Menu className="w-5 h-5 text-gray-700" />
        )}
      </button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/5 z-40"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0`}
        aria-label="Sidebar"
      >
        <div className="h-full flex flex-col overflow-y-auto">
          {/* Logo Section */}
          <div className="px-6 py-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
                <span className="text-white font-bold text-lg">E</span>
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-semibold text-gray-900 leading-tight">
                  eFiche
                </h2>
                <p className="text-xs text-gray-500 leading-tight">
                  Dashboard
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex px-6 py-4">
            <div className="space-y-1">
              {navigationItems.map((item) => (
                <NavItem
                  key={item.id}
                  item={item}
                  isActive={activeItem === item.id}
                  onClick={() => handleNavClick(item.id)}
                />
              ))}
            </div>
          </nav>

          {/* Quick Stats Section */}
          <div className="px-4 py-4 bg-blue-50 rounded-lg mx-6 flex flex-col mt-3.5">
            <p className="text-sm font-semibold text-blue-800 mb-3">
              Quick Stats
            </p>

            {/* Stats container */}
            <div className="flex flex-col space-y-2 w-full max-w-xs">
              {/* Completion Rate */}
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-600 mb-1">Completion Rate</p>
                {isLoading ? (
                  <p className="text-sm font-semibold text-blue-600 animate-pulse">...</p>
                ) : (
                  <p className="text-sm font-semibold text-blue-600">
                    {completionRate.toFixed(1)}%
                  </p>
                )}
              </div>

              {/* Active Tasks */}
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-600 mb-1">Active Tasks</p>
                {isLoading ? (
                  <p className="text-sm font-semibold text-blue-600 animate-pulse">...</p>
                ) : (
                  <p className="text-sm font-semibold text-blue-600">{activeTasks}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
