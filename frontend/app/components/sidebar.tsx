"use client";

import { useState, useEffect } from "react";
import NavItem from "./nav-item";
import { navigationItems } from "../constants/navigation";
import { Menu, X } from "lucide-react";
import { useExecutiveSummary } from "@/lib/hooks/use-dashboard-data";
import { useThroughputData } from "@/lib/hooks/use-dashboard-data";

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

export default function Sidebar() {
  const [activeItem, setActiveItem] = useState("executive-summary");
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  
  const { data: executiveData, loading: executiveLoading } = useExecutiveSummary();
  
  const completionRate = executiveData?.completionRate || 0;
  
  const activeTasks = executiveData
    ? Math.max(0, (executiveData.planned || 0) - (executiveData.done || 0))
    : 0;
  
  const isLoading = executiveLoading;

  useEffect(() => {
    let observer: IntersectionObserver | null = null;
    let scrollTimeout: NodeJS.Timeout;
    let rafId: number | null = null;
    const sections = Object.keys(sectionIdMap).map(key => ({
      navId: key,
      sectionId: sectionIdMap[key],
    }));

    const findActiveSection = (): string => {
      const scrollPosition = window.scrollY;
      const viewportHeight = window.innerHeight;
      const offset = 150;
      const checkPoint = scrollPosition + offset;

      let activeSectionId = 'executive-summary';
      let minDistance = Infinity;
      let maxVisibleRatio = 0;

      sections.forEach(({ sectionId }) => {
        const element = document.getElementById(sectionId);
        if (!element) return;

        const rect = element.getBoundingClientRect();
        const elementTop = rect.top + scrollPosition;
        const elementBottom = elementTop + rect.height;
        const elementHeight = rect.height;

        const visibleTop = Math.max(0, rect.top);
        const visibleBottom = Math.min(viewportHeight, rect.bottom);
        const visibleHeight = Math.max(0, visibleBottom - visibleTop);
        const visibleRatio = visibleHeight / elementHeight;

        if (checkPoint >= elementTop && checkPoint < elementBottom) {
          const distance = Math.abs(checkPoint - (elementTop + elementHeight / 2));
          if (distance < minDistance) {
            minDistance = distance;
            activeSectionId = sectionId;
          }
        }

        if (visibleRatio > maxVisibleRatio && visibleRatio > 0.1) {
          maxVisibleRatio = visibleRatio;
          if (minDistance === Infinity) {
            activeSectionId = sectionId;
          }
        }
      });

      return activeSectionId;
    };

    const updateActiveSection = () => {
      const activeSectionId = findActiveSection();
      if (navIdMap[activeSectionId]) {
        setActiveItem(navIdMap[activeSectionId]);
      }
    };

    const handleScroll = () => {
      if (rafId) {
        cancelAnimationFrame(rafId);
      }
      rafId = requestAnimationFrame(() => {
        updateActiveSection();
      });
    };

    const observerOptions = {
      root: null,
      rootMargin: '-100px 0px -50% 0px',
      threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
    };

    const observerCallback = (entries: IntersectionObserverEntry[]) => {
      clearTimeout(scrollTimeout);
      
      scrollTimeout = setTimeout(() => {
        let maxIntersection = 0;
        let activeSectionId = 'executive-summary';

        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const ratio = entry.intersectionRatio;
            if (ratio > maxIntersection) {
              maxIntersection = ratio;
              activeSectionId = entry.target.id;
            }
          }
        });

        if (maxIntersection > 0.1) {
          if (navIdMap[activeSectionId]) {
            setActiveItem(navIdMap[activeSectionId]);
          }
        } else {
          updateActiveSection();
        }
      }, 50);
    };

    const setupObserver = () => {
      observer = new IntersectionObserver(observerCallback, observerOptions);

      sections.forEach(({ sectionId }) => {
        const element = document.getElementById(sectionId);
        if (element) {
          observer!.observe(element);
        }
      });
    };

    const init = () => {
      updateActiveSection();
      setupObserver();
      window.addEventListener('scroll', handleScroll, { passive: true });
    };

    const timeoutId = setTimeout(init, 100);

    return () => {
      clearTimeout(timeoutId);
      clearTimeout(scrollTimeout);
      if (rafId) {
        cancelAnimationFrame(rafId);
      }
      window.removeEventListener('scroll', handleScroll);
      if (observer) {
        sections.forEach(({ sectionId }) => {
          const element = document.getElementById(sectionId);
          if (element) {
            observer!.unobserve(element);
          }
        });
      }
    };
  }, []);

  const handleNavClick = (itemId: string) => {
    setActiveItem(itemId);
    setIsMobileOpen(false);
    
    const sectionId = sectionIdMap[itemId] || itemId;
    
    setTimeout(() => {
      const element = document.getElementById(sectionId);
      if (element) {
        const offset = 100;
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
      <button
        onClick={toggleMobileMenu}
        className="md:hidden fixed top-4 left-4 sm:top-6 sm:left-6 z-50 w-10 h-10 rounded-lg bg-white border border-gray-200 shadow-sm hover:bg-gray-50 transition-colors flex items-center justify-center"
        aria-label="Toggle menu"
      >
        {isMobileOpen ? (
          <X className="w-5 h-5 text-gray-700" />
        ) : (
          <Menu className="w-5 h-5 text-gray-700" />
        )}
      </button>

      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/5 z-40"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 md:w-72 lg:w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0`}
        aria-label="Sidebar"
      >
        <div className="h-full flex flex-col overflow-y-auto">
          <div className="px-4 sm:px-6 py-4 sm:py-6">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
                <span className="text-white font-bold text-base sm:text-lg">E</span>
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-base sm:text-lg font-semibold text-gray-900 leading-tight">
                  eFiche
                </h2>
                <p className="text-xs text-gray-500 leading-tight">
                  Dashboard
                </p>
              </div>
            </div>
          </div>

          <nav className="flex px-4 sm:px-6 py-3 sm:py-4">
            <div className="space-y-1 w-full">
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

          <div className="px-3 sm:px-4 py-3 sm:py-4 bg-blue-50 rounded-lg mx-3 sm:mx-4 md:mx-6 flex flex-col mt-2 sm:mt-3.5">
            <p className="text-xs sm:text-sm font-semibold text-blue-800 mb-2 sm:mb-3">
              Quick Stats
            </p>

            <div className="flex flex-col space-y-2 w-full max-w-xs">
              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-600 mb-1">Completion Rate</p>
                {isLoading ? (
                  <p className="text-xs sm:text-sm font-semibold text-blue-600 animate-pulse">...</p>
                ) : (
                  <p className="text-xs sm:text-sm font-semibold text-blue-600">
                    {completionRate.toFixed(1)}%
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <p className="text-xs text-gray-600 mb-1">Active Tasks</p>
                {isLoading ? (
                  <p className="text-xs sm:text-sm font-semibold text-blue-600 animate-pulse">...</p>
                ) : (
                  <p className="text-xs sm:text-sm font-semibold text-blue-600">{activeTasks}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
