/**
 * Ownership & Distribution section
 * Displays:
 * - Task Load by Assignee (task count per team member)
 * - Execution Success by Assignee (completion rate, target: ≥75%)
 * - Detailed Performance Breakdown (individual success rates)
 */
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

  // Don't show section if no data
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
    // Show all charts in fullscreen
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          {/* Task Load Chart */}
          {taskLoadData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
                <span className="w-1 h-4 bg-blue-600 rounded-full"></span>
                Task Load by Assignee
              </h3>
              <p className="text-sm text-gray-500 mb-4 ml-3">Number of tasks assigned to each team member</p>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200/50 flex-1">
                <TaskLoadChart data={taskLoadData} />
              </div>
            </div>
          )}
          {/* Execution Success Chart */}
          {executionSuccessData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-base font-bold text-gray-900 mb-1 flex items-center gap-2">
                <span className="w-1 h-4 bg-blue-600 rounded-full"></span>
                Execution Success by Assignee
              </h3>
              <p className="text-sm text-gray-500 mb-4 ml-3">Completion rate percentage per team member</p>
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200/50 flex-1">
                <ExecutionSuccessChart data={executionSuccessData} />
              </div>
            </div>
          )}
        </div>
      </SectionWrapper>
      
      {/* Detailed Performance Breakdown */}
      {performanceData.length > 0 && (
        <SectionWrapper>
          <div className="mb-8 pb-4 border-b border-gray-200">
            <h2 className="text-xl lg:text-2xl font-bold text-gray-900 mb-2 tracking-tight">
              Detailed Performance Breakdown
            </h2>
            <p className="text-sm text-gray-600">
              Individual execution success rates
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 lg:gap-6">
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

      {/* Info Modal */}
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

      {/* Fullscreen Modal - Show All Charts */}
      <Modal
        isOpen={showFullscreen}
        onClose={() => setShowFullscreen(false)}
        title="Ownership & Distribution - Full View"
        size="full"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Task Load Chart */}
          {taskLoadData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Task Load by Assignee</h3>
              <div className="h-[500px]">
                <TaskLoadChart data={taskLoadData} height={500} />
              </div>
            </div>
          )}
          {/* Execution Success Chart */}
          {executionSuccessData.length > 0 && (
            <div className="flex flex-col">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Execution Success by Assignee</h3>
              <div className="h-[500px]">
                <ExecutionSuccessChart data={executionSuccessData} targetValue={75} height={500} />
              </div>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
}
