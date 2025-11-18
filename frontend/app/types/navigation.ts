import { ReactNode } from "react";

export interface NavItemData {
  id: string;
  label: string;
  icon?: ReactNode;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

