"use client";

import { useState } from "react";
import SectionWrapper from "../components/section-wrapper";
import SectionHeader from "../components/section-header";
import CompanyTrendChart from "../components/company-trend-chart";
import Modal from "../components/modal";
import { useCompanyTrend } from "@/lib/hooks/use-dashboard-data";
import { exportToCSV } from "@/lib/utils/export";

export default function Company_Level_Trend() {
  const { data, loading, error } = useCompanyTrend(6);
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);

  if (loading) {
    return (
      <SectionWrapper>
        <SectionHeader title="Company-Level Trend (6 months)" />
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </SectionWrapper>
    );
  }

  if (error) {
    return (
      <SectionWrapper>
        <SectionHeader title="Company-Level Trend (6 months)" />
        <div className="text-center py-8 text-red-500">Error: {error}</div>
      </SectionWrapper>
    );
  }

  const companyTrendData = data || [];

  if (companyTrendData.length === 0) {
    return null;
  }

  const handleInfoClick = () => {
    setShowInfoModal(true);
  };

  const handleExportClick = () => {
    exportToCSV(companyTrendData, 'company-level-trend');
  };

  const handleMaximizeClick = () => {
    setShowFullscreen(true);
  };

  return (
    <>
      <SectionWrapper id="company-level">
        <SectionHeader
          title="Company-Level Trend (6 months)"
          onInfoClick={handleInfoClick}
          onExportClick={handleExportClick}
          onMaximizeClick={handleMaximizeClick}
        />
      <div>
        <h3 className="text-xs sm:text-sm md:text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
          <span className="w-0.5 sm:w-1 h-3 sm:h-4 bg-blue-600 rounded-full"></span>
          Monthly Completion Rate & Average Lead Time
        </h3>
        <p className="text-xs sm:text-sm text-gray-500 mb-3 sm:mb-4 md:mb-6 ml-2 sm:ml-3">Company-wide performance trends over the past 6 months</p>
        <div className="bg-gray-50 rounded-lg p-2 sm:p-3 md:p-4 border border-gray-200/50">
          <CompanyTrendChart data={companyTrendData} height={500} />
        </div>
      </div>
      </SectionWrapper>

      <Modal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="Company-Level Trend - Information"
        size="md"
      >
        <div className="space-y-4 text-sm text-gray-700">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Monthly Completion Rate & Average Lead Time</h3>
            <p className="mb-2">Shows company-wide performance trends over the past 6 months.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li><strong>Completion Rate:</strong> Percentage of tasks completed out of those planned</li>
              <li><strong>Average Lead Time:</strong> Average days from task creation to completion</li>
              <li>Helps track overall team performance and identify long-term trends</li>
            </ul>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={showFullscreen}
        onClose={() => setShowFullscreen(false)}
        title="Company-Level Trend (6 months)"
        size="full"
      >
        <div className="h-[60vh] sm:h-[70vh] md:h-[80vh]">
          <CompanyTrendChart data={companyTrendData} height={700} />
        </div>
      </Modal>
    </>
  );
}
