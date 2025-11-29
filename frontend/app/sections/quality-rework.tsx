"use client";

import { useState } from "react";
import SectionWrapper from "../components/section-wrapper";
import SectionHeader from "../components/section-header";
import QAVsFailedChart from "../components/qa-vs-failed-chart";
import LeadTimeTrendChart from "../components/lead-time-trend-chart";
import ReworkRatioChart from "../components/rework-ratio-chart";
import Modal from "../components/modal";
import { useQualityReworkData } from "@/lib/hooks/use-dashboard-data";
import { exportToCSV } from "@/lib/utils/export";

export default function Quality_Rework() {
  const { data, loading, error } = useQualityReworkData();
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);

  if (loading) {
    return (
      <SectionWrapper>
        <SectionHeader title="Quality & Rework" />
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </SectionWrapper>
    );
  }

  if (error) {
    return (
      <SectionWrapper>
        <SectionHeader title="Quality & Rework" />
        <div className="text-center py-8 text-red-500">Error: {error}</div>
      </SectionWrapper>
    );
  }

  const qaVsFailedData = data?.qaVsFailed || [];
  const leadTimeTrendData = data?.leadTimeTrend || [];
  const reworkRatioData = data?.reworkRatio || [];

  if (qaVsFailedData.length === 0 && leadTimeTrendData.length === 0 && reworkRatioData.length === 0) {
    return null;
  }

  const handleInfoClick = () => {
    setShowInfoModal(true);
  };

  const handleExportClick = () => {
    const allData = [
      ...qaVsFailedData.map(item => ({ ...item, chart: 'QA vs Failed' })),
      ...leadTimeTrendData.map(item => ({ ...item, chart: 'Lead Time Trend' })),
      ...reworkRatioData.map(item => ({ ...item, chart: 'Rework Ratio' })),
    ];
    exportToCSV(allData, 'quality-rework');
  };

  const handleMaximizeClick = () => {
    if (qaVsFailedData.length > 0 || leadTimeTrendData.length > 0 || reworkRatioData.length > 0) {
      setShowFullscreen(true);
    }
  };

  return (
    <>
      <SectionWrapper id="quality-rework">
        <SectionHeader
          title="Quality & Rework"
          onInfoClick={handleInfoClick}
          onExportClick={handleExportClick}
          onMaximizeClick={handleMaximizeClick}
        />
      <div className="space-y-4 sm:space-y-6 lg:space-y-8">
        {/* First Row: QA vs Failed and Lead Time Trend */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
          {/* QA vs Failed QA Chart */}
          {qaVsFailedData.length > 0 && (
            <div className="flex flex-col h-full">
              <h3 className="text-sm sm:text-base md:text-base font-bold text-gray-900 mb-1 sm:mb-1.5 flex items-center gap-2">
                <span className="w-0.5 sm:w-1 h-3 sm:h-4 bg-blue-600 rounded-full"></span>
                <span className="line-clamp-2 sm:line-clamp-1">QA vs Failed QA</span>
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-3 sm:mb-4 ml-2 sm:ml-3 line-clamp-2">Quality assurance execution and failure rates per week</p>
              <div className="bg-gray-50 rounded-lg p-3 sm:p-4 md:p-4 border border-gray-200/50 flex-1 min-h-[250px] sm:min-h-[300px] md:min-h-[350px]">
                <QAVsFailedChart data={qaVsFailedData} />
              </div>
            </div>
          )}
          
          {/* Lead Time Trend Chart */}
          {leadTimeTrendData.length > 0 && (
            <div className="flex flex-col h-full">
              <h3 className="text-sm sm:text-base md:text-base font-bold text-gray-900 mb-1 sm:mb-1.5 flex items-center gap-2">
                <span className="w-0.5 sm:w-1 h-3 sm:h-4 bg-blue-600 rounded-full"></span>
                <span className="line-clamp-2 sm:line-clamp-1">Lead Time Trend (weekly)</span>
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-3 sm:mb-4 ml-2 sm:ml-3 line-clamp-2">Average time from start to completion per week</p>
              <div className="bg-gray-50 rounded-lg p-3 sm:p-4 md:p-4 border border-gray-200/50 flex-1 min-h-[250px] sm:min-h-[300px] md:min-h-[350px]">
                <LeadTimeTrendChart data={leadTimeTrendData} />
              </div>
            </div>
          )}
        </div>
        
        {/* Second Row: Rework Ratio Chart (full width or centered) */}
        {reworkRatioData.length > 0 && (
          <div className="flex flex-col">
            <h3 className="text-sm sm:text-base md:text-base font-bold text-gray-900 mb-1 sm:mb-1.5 flex items-center gap-2">
              <span className="w-0.5 sm:w-1 h-3 sm:h-4 bg-blue-600 rounded-full"></span>
              <span className="line-clamp-2 sm:line-clamp-1">Rework Ratio (% of total)</span>
            </h3>
            <p className="text-xs sm:text-sm text-gray-500 mb-3 sm:mb-4 ml-2 sm:ml-3 line-clamp-2">Percentage of tasks requiring rework versus clean delivery</p>
            <div className="bg-gray-50 rounded-lg p-3 sm:p-4 md:p-4 border border-gray-200/50 min-h-[250px] sm:min-h-[300px] md:min-h-[350px]">
              <ReworkRatioChart data={reworkRatioData} />
            </div>
          </div>
        )}
      </div>
      </SectionWrapper>

      {/* Info Modal */}
      <Modal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="Quality & Rework - Information"
        size="md"
      >
        <div className="space-y-4 text-sm text-gray-700">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">QA vs Failed QA Chart</h3>
            <p className="mb-2">Tracks quality assurance execution and failure rates per week.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li><strong>QA Executed:</strong> Tasks that entered QA/testing status</li>
              <li><strong>Failed QA:</strong> Tasks that failed QA and returned to development</li>
              <li>Helps identify quality issues and testing effectiveness</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Lead Time Trend Chart</h3>
            <p className="mb-2">Shows average time from task creation to completion per week.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Target: ≤ 20 days</li>
              <li>Helps track delivery speed and identify bottlenecks</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Rework Ratio Chart</h3>
            <p className="mb-2">Percentage of tasks requiring rework versus clean delivery.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li><strong>Clean Delivery:</strong> Tasks completed without rework</li>
              <li><strong>Rework:</strong> Tasks that needed fixes after completion</li>
              <li>Target: ≤ 10% rework ratio</li>
            </ul>
          </div>
        </div>
      </Modal>

      {/* Fullscreen Modal - Show All Charts */}
      <Modal
        isOpen={showFullscreen}
        onClose={() => setShowFullscreen(false)}
        title="Quality & Rework - Full View"
        size="full"
      >
        <div className="space-y-8">
          {/* QA vs Failed Chart */}
          {qaVsFailedData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">QA vs Failed QA (per week)</h3>
              <div className="h-[500px]">
                <QAVsFailedChart data={qaVsFailedData} height={500} />
              </div>
            </div>
          )}
          {/* Lead Time Trend Chart */}
          {leadTimeTrendData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Lead Time Trend (weekly)</h3>
              <div className="h-[500px]">
                <LeadTimeTrendChart data={leadTimeTrendData} targetValue={20} height={500} />
              </div>
            </div>
          )}
          {/* Rework Ratio Chart */}
          {reworkRatioData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Rework Ratio (% of total)</h3>
              <div className="h-[500px]">
                <ReworkRatioChart data={reworkRatioData} height={500} />
              </div>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}
