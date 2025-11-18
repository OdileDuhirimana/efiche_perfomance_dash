import React from "react";
import { NavItemData } from "../types/navigation";
import {
  House,
  TrendingUp,
  Users,
  ChevronRight,
  Activity,
  ChartNoAxesColumn
} from "lucide-react";

export const navigationItems: NavItemData[] = [
  {
    id: "executive-summary",
    label: "Executive Summary",
    icon: <House className="w-4 h-4" />,
    rightIcon: <ChevronRight className="w-4 h-4" />,
  },
  {
    id: "throughput",
    label: "Throughput & Predictability",
    icon: <ChartNoAxesColumn className="w-4 h-4" />,
    rightIcon: <ChevronRight className="w-4 h-4" />,
  },
  {
    id: "quality",
    label: "Quality & Rework",
    icon: <TrendingUp className="w-4 h-4" />,
    rightIcon: <ChevronRight className="w-4 h-4" />,
  },
  {
    id: "ownership",
    label: "Ownership & Distribution",
    icon: <Users className="w-4 h-4" />,
    rightIcon: <ChevronRight className="w-4 h-4" />,
  },
  {
    id: "company-trend",
    label: "Company-Level Trend",
    icon: <Activity className="w-4 h-4" />,
    rightIcon: <ChevronRight className="w-4 h-4" />,
  },
];
