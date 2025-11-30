"use client";

import { useState } from "react";
import SectionWrapper from "../components/section-wrapper";
import SectionHeader from "../components/section-header";
import TaskLoadChart from "../components/task-load-chart";
import ExecutionSuccessChart from "../components/execution-success-chart";
import PerformanceCard from "../components/performance-card";
import Modal from "../components/modal";
import { useOwnershipData } from "@/lib/hooks/use-dashboard-data";
import { exportToCSV } from "@/lib/utils/export";

export default function Ownership_Distribution() {
  const { data, loading, error } = useOwnershipData();
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);

  if (loading) {
    return (
      <>
        <SectionWrapper>
          <SectionHeader title="Ownership & Distribution" />
          <div className="text-center py-8 text-gray-500">Loading...</div>
        </SectionWrapper>
      </>
    );
  }

  if (error) {
    return (
      <>
        <SectionWrapper>
          <SectionHeader title="Ownership & Distribution" />
          <div className="text-center py-8 text-red-500">Error: {error}</div>
        </SectionWrapper>
      </>
    );
  }

  const taskLoadData = data?.taskLoad || [];
  const executionSuccessData = data?.executionSuccess || [];
  const performanceData = data?.performanceData || [];

  if (taskLoadData.length === 0 && executionSuccessData.length === 0 && performanceData.length === 0) {
    return null;
  }

  const handleInfoClick = () => {
    setShowInfoModal(true);
  };

  const handleExportClick = () => {
    const allData = [
      ...taskLoadData.map(item => ({ ...item, chart: 'Task Load' })),
      ...executionSuccessData.map(item => ({ ...item, chart: 'Execution Success' })),
      ...performanceData.map(item => ({ ...item, chart: 'Performance' })),
    ];
    exportToCSV(allData, 'ownership-distribution');
  };

  const handleMaximizeClick = () => {
    if (taskLoadData.length > 0 || executionSuccessData.length > 0) {
      setShowFullscreen(true);
    }
  };

  return (
    <>
      <SectionWrapper id="ownership-distribution">
        <SectionHeader
          title="Ownership & Distribution"
          onInfoClick={handleInfoClick}
          onExportClick={handleExportClick}
          onMaximizeClick={handleMaximizeClick}
        />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 md:gap-6 lg:gap-8">
          {taskLoadData.length > 0 && (
            <div className="flex flex-col h-full">
              <h3 className="text-xs sm:text-sm md:text-base font-bold text-gray-900 mb-1 sm:mb-1.5 flex items-center gap-2">
                <span className="w-0.5 sm:w-1 h-3 sm:h-4 bg-blue-600 rounded-full"></span>
                <span className="line-clamp-2 sm:line-clamp-1">Task Load by Assignee</span>
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-2 sm:mb-3 md:mb-4 ml-2 sm:ml-3 line-clamp-2">Number of tasks assigned to each team member</p>
              <div className="bg-gray-50 rounded-lg p-2 sm:p-3 md:p-4 border border-gray-200/50 flex-1 min-h-[200px] sm:min-h-[250px] md:min-h-[300px] lg:min-h-[350px]">
                <TaskLoadChart data={taskLoadData} />
              </div>
            </div>
          )}
          {executionSuccessData.length > 0 && (
            <div className="flex flex-col h-full">
              <h3 className="text-xs sm:text-sm md:text-base font-bold text-gray-900 mb-1 sm:mb-1.5 flex items-center gap-2">
                <span className="w-0.5 sm:w-1 h-3 sm:h-4 bg-blue-600 rounded-full"></span>
                <span className="line-clamp-2 sm:line-clamp-1">Execution Success by Assignee</span>
              </h3>
              <p className="text-xs sm:text-sm text-gray-500 mb-2 sm:mb-3 md:mb-4 ml-2 sm:ml-3 line-clamp-2">Completion rate percentage per team member</p>
              <div className="bg-gray-50 rounded-lg p-2 sm:p-3 md:p-4 border border-gray-200/50 flex-1 min-h-[200px] sm:min-h-[250px] md:min-h-[300px] lg:min-h-[350px]">
                <ExecutionSuccessChart data={executionSuccessData} />
              </div>
            </div>
          )}
        </div>
      </SectionWrapper>
      
      {performanceData.length > 0 && (
        <SectionWrapper>
          <div className="mb-4 sm:mb-6 md:mb-8 pb-3 sm:pb-4 border-b border-gray-200">
            <h2 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-gray-900 mb-1 sm:mb-2 tracking-tight">
              Detailed Performance Breakdown
            </h2>
            <p className="text-xs sm:text-sm text-gray-600">
              Individual execution success rates
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-5 lg:gap-6">
            {performanceData.map((member) => (
              <PerformanceCard
                key={member.name}
                name={member.name}
                successRate={member.successRate}
              />
            ))}
          </div>
        </SectionWrapper>
      )}

      <Modal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="Ownership & Distribution - Information"
        size="md"
      >
        <div className="space-y-4 text-sm text-gray-700">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Task Load by Assignee</h3>
            <p className="mb-2">Shows the number of tasks assigned to each team member over the selected period.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Helps identify workload distribution across the team</li>
              <li>Useful for balancing work assignments</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Execution Success by Assignee</h3>
            <p className="mb-2">Displays completion rate percentage for each team member.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Target: ≥ 75% success rate</li>
              <li>Shows individual performance metrics</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Detailed Performance Breakdown</h3>
            <p className="mb-2">Individual execution success rates for each team member.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Shows success rate percentage</li>
            </ul>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={showFullscreen}
        onClose={() => setShowFullscreen(false)}
        title="Ownership & Distribution - Full View"
        size="full"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          {taskLoadData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-3 sm:mb-4">Task Load by Assignee</h3>
              <div className="h-[400px] sm:h-[500px]">
                <TaskLoadChart data={taskLoadData} height={500} />
              </div>
            </div>
          )}
          {executionSuccessData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-3 sm:mb-4">Execution Success by Assignee</h3>
              <div className="h-[400px] sm:h-[500px]">
                <ExecutionSuccessChart data={executionSuccessData} targetValue={75} height={500} />
              </div>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}
