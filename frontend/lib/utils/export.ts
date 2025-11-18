/**
 * Data export utilities
 * Provides CSV export functionality for dashboard charts
 */

export interface ExportableData {
  [key: string]: any;
}

/**
 * Export data array to CSV file
 * Automatically handles CSV escaping (commas, quotes, newlines)
 * Downloads file with format: {filename}_YYYY-MM-DD.csv
 */
export function exportToCSV(data: ExportableData[], filename: string) {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  // Extract all unique keys from data objects as CSV headers
  const headers = Array.from(
    new Set(data.flatMap(obj => Object.keys(obj)))
  );

  // Build CSV rows with proper escaping
  const csvContent = [
    headers.join(','),
    ...data.map(row =>
      headers.map(header => {
        const value = row[header];
        if (value === null || value === undefined) return '';
        const stringValue = String(value);
        // Escape values containing commas, quotes, or newlines
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  // Create download link and trigger download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

