import { ReactNode } from "react";

interface SectionWrapperProps {
  children: ReactNode;
  className?: string;
  id?: string;
}

export default function SectionWrapper({
  children,
  className = "",
  id,
}: SectionWrapperProps) {
  return (
    <section
      id={id}
      className={`bg-white rounded-xl shadow-md p-6 lg:p-8 transition-shadow hover:shadow-lg ${className}`}
    >
      {children}
    </section>
  );
}

