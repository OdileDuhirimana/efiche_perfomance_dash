/**
 * Throughput & Predictability section
 * Displays:
 * - Planned vs Done chart (12-week rolling window)
 * - Weekly Flow chart (Done, In Progress, Carry Over tasks)
 */
"use client";

import { useState } from "react";
import SectionWrapper from "../components/section-wrapper";
import SectionHeader from "../components/section-header";
import PlannedVsDoneChart from "../components/planned-vs-done-chart";
import WeeklyFlowChart from "../components/weekly-flow-chart";
import Modal from "../components/modal";
import { useThroughputData } from "@/lib/hooks/use-dashboard-data";
import { exportToCSV } from "@/lib/utils/export";

export default function Throughput_Predicatibility() {
  const { data, loading, error } = useThroughputData(12);
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);

  if (loading) {
    return (
      <SectionWrapper>
        <SectionHeader title="Throughput & Predictability" />
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </SectionWrapper>
    );
  }

  if (error) {
    return (
      <SectionWrapper>
        <SectionHeader title="Throughput & Predictability" />
        <div className="text-center py-8 text-red-500">Error: {error}</div>
      </SectionWrapper>
    );
  }

  const plannedVsDoneData = data?.plannedVsDone || [];
  const weeklyFlowData = data?.weeklyFlow || [];

  // Don't show section if no data
  if (plannedVsDoneData.length === 0 && weeklyFlowData.length === 0) {
    return null;
  }

  const handleInfoClick = () => {
    setShowInfoModal(true);
  };

  const handleExportClick = () => {
    const allData = [
      ...plannedVsDoneData.map(item => ({ ...item, chart: 'Planned vs Done' })),
      ...weeklyFlowData.map(item => ({ ...item, chart: 'Weekly Flow' })),
    ];
    exportToCSV(allData, 'throughput-predictability');
  };

  const handleMaximizeClick = () => {
    // Show all charts in fullscreen
    if (plannedVsDoneData.length > 0 || weeklyFlowData.length > 0) {
      setShowFullscreen(true);
    }
  };

  return (
    <>
      <SectionWrapper id="throughput-predictability">
        <SectionHeader
          title="Throughput & Predictability"
          onInfoClick={handleInfoClick}
          onExportClick={handleExportClick}
          onMaximizeClick={handleMaximizeClick}
        />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
        {/* Planned vs Done Chart */}
        {plannedVsDoneData.length > 0 && (
          <div className="flex flex-col">
            <h3 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
              <span className="w-1 h-4 bg-blue-600 rounded-full"></span>
              Planned vs Done (12-week Rolling)
            </h3>
            <p className="text-sm text-gray-500 mb-4 ml-3">Tasks planned versus tasks completed per week</p>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200/50 flex-1">
              <PlannedVsDoneChart data={plannedVsDoneData} />
            </div>
          </div>
        )}
        {/* Weekly Flow Chart */}
        {weeklyFlowData.length > 0 && (
          <div className="flex flex-col">
            <h3 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
              <span className="w-1 h-4 bg-blue-600 rounded-full"></span>
              Weekly Flow (Done / In Progress / Carry-Over)
            </h3>
            <p className="text-sm text-gray-500 mb-4 ml-3">Task status distribution across weeks</p>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200/50 flex-1">
              <WeeklyFlowChart data={weeklyFlowData} />
            </div>
          </div>
        )}
      </div>
      </SectionWrapper>

      {/* Info Modal */}
      <Modal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="Throughput & Predictability - Information"
        size="md"
      >
        <div className="space-y-4 text-sm text-gray-700">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Planned vs Done Chart</h3>
            <p className="mb-2">Shows the comparison between tasks planned and tasks completed over a 12-week rolling period.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li><strong>Planned:</strong> Total tasks in active sprints during each week</li>
              <li><strong>Done:</strong> Tasks marked as completed during each week</li>
              <li>Helps identify planning accuracy and completion trends</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Weekly Flow Chart</h3>
            <p className="mb-2">Displays task status distribution across weeks showing work in progress.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li><strong>Done:</strong> Tasks completed during the week</li>
              <li><strong>In Progress:</strong> Tasks currently being worked on</li>
              <li><strong>Carry Over:</strong> Tasks from previous week still active</li>
            </ul>
          </div>
        </div>
      </Modal>

      {/* Fullscreen Modal - Show All Charts */}
      <Modal
        isOpen={showFullscreen}
        onClose={() => setShowFullscreen(false)}
        title="Throughput & Predictability - Full View"
        size="full"
      >
        <div className="space-y-8">
          {/* Planned vs Done Chart */}
          {plannedVsDoneData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Planned vs Done (12-week Rolling)</h3>
              <div className="h-[500px]">
                <PlannedVsDoneChart data={plannedVsDoneData} height={500} />
              </div>
            </div>
          )}
          {/* Weekly Flow Chart */}
          {weeklyFlowData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Weekly Flow (Done / In Progress / Carry-Over)</h3>
              <div className="h-[500px]">
                <WeeklyFlowChart data={weeklyFlowData} height={500} />
              </div>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}
