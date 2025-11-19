"use client";

import { useState } from "react";
import SectionWrapper from "../components/section-wrapper";
import SectionHeader from "../components/section-header";
import KPICard from "../components/kpi-card";
import Modal from "../components/modal";
import { BarChart3, Clock, Repeat, Calendar, CalendarCheck } from "lucide-react";
import { useExecutiveSummary } from "@/lib/hooks/use-dashboard-data";
import { exportToCSV } from "@/lib/utils/export";

export default function ExecutiveSummary() {
  const { data, loading, error } = useExecutiveSummary();
  const [showInfoModal, setShowInfoModal] = useState(false);

  if (loading) {
    return (
      <SectionWrapper>
        <SectionHeader
          title="Executive Summary"
          showActions={false}
        />
        <div className="text-center py-8 text-gray-500">Loading...</div>
      </SectionWrapper>
    );
  }

  if (error) {
    return (
      <SectionWrapper>
        <SectionHeader
          title="Executive Summary"
          showActions={false}
        />
        <div className="text-center py-8 text-red-500">Error: {error}</div>
      </SectionWrapper>
    );
  }

  if (!data) {
    return null;
  }

  const completionRate = data?.completionRate || 0;
  const avgLeadTime = data?.avgLeadTime || 0;
  const reworkRatio = data?.reworkRatio || 0;
  const planned = data?.planned || 0;
  const done = data?.done || 0;

  const handleInfoClick = () => {
    setShowInfoModal(true);
  };

  const handleExportClick = () => {
    const exportData = [{
      'Completion Rate (%)': completionRate,
      'Average Lead Time (days)': avgLeadTime,
      'Rework Ratio (%)': reworkRatio,
      'Planned': planned,
      'Done': done,
    }];
    exportToCSV(exportData, 'executive-summary');
  };

  return (
    <>
      <SectionWrapper id="executive-summary">
        <SectionHeader
          title="Executive Summary"
          showActions={true}
          onInfoClick={handleInfoClick}
          onExportClick={handleExportClick}
        />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5 lg:gap-6">
        <KPICard
          label="Completion Rate"
          value={`${completionRate.toFixed(1)}%`}
          icon={BarChart3}
          variant="success"
          target={{
            text: "Target ≤ 80%",
            met: completionRate >= 80,
          }}
        />

        <KPICard
          label="Avg Lead Time (days)"
          value={avgLeadTime.toFixed(1)}
          icon={Clock}
          variant="success"
          target={{
            text: "Target ≤ 20",
            met: avgLeadTime <= 20,
          }}
        />

        <KPICard
          label="Rework Ratio"
          value={`${reworkRatio}%`}
          icon={Repeat}
          variant="success"
          target={{
            text: "Target ≤ 10%",
            met: reworkRatio <= 10,
          }}
        />

        <KPICard
          label="Planned"
          value={planned.toString()}
          icon={Calendar}
          variant="default"
        />

        <KPICard
          label="Done"
          value={done.toString()}
          icon={CalendarCheck}
          variant="default"
        />
      </div>
      </SectionWrapper>

      {/* Info Modal */}
      <Modal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="Executive Summary - Information"
        size="md"
      >
        <div className="space-y-4 text-sm text-gray-700">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Completion Rate</h3>
            <p className="mb-2">Percentage of tasks completed out of those planned over the last 12 weeks.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Target: ≥ 80%</li>
              <li>Calculated as: (Total Done / Total Planned) × 100</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Average Lead Time</h3>
            <p className="mb-2">Average number of days from task creation to completion over the last 6 months.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Target: ≤ 20 days</li>
              <li>Measures delivery speed</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Rework Ratio</h3>
            <p className="mb-2">Percentage of tasks that required rework after completion.</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 ml-2">
              <li>Target: ≤ 10%</li>
              <li>Indicates quality of initial delivery</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Planned & Done</h3>
            <p className="mb-2">Shows all planned and completed tasks within the selected date range period.</p>
          </div>
        </div>
      </Modal>
    </>
  );
}
