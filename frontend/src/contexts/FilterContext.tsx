import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type Scenario = 'FinTech' | 'SaaS' | 'Developer Tools';
export type DateRange = 'last7' | 'last30' | 'last90' | 'last6months' | 'lastYear' | 'allTime' | 'custom';

export interface CustomDateRange {
  from: string;
  to: string;
}

interface FilterContextValue {
  scenario: Scenario;
  setScenario: (s: Scenario) => void;
  dateRange: DateRange;
  setDateRange: (r: DateRange) => void;
  customDateRange: CustomDateRange;
  setCustomDateRange: (r: CustomDateRange) => void;
  getEffectiveDateRange: () => { from: Date; to: Date };
}

const FilterContext = createContext<FilterContextValue | null>(null);

function computeRange(range: DateRange, custom: CustomDateRange): { from: Date; to: Date } {
  const to = new Date();
  const from = new Date();
  switch (range) {
    case 'last7':
      from.setDate(to.getDate() - 7);
      break;
    case 'last30':
      from.setDate(to.getDate() - 30);
      break;
    case 'last90':
      from.setDate(to.getDate() - 90);
      break;
    case 'last6months':
      from.setMonth(to.getMonth() - 6);
      break;
    case 'lastYear':
      from.setFullYear(to.getFullYear() - 1);
      break;
    case 'allTime':
      from.setFullYear(2020, 0, 1);
      break;
    case 'custom':
      return {
        from: custom.from ? new Date(custom.from) : new Date(2020, 0, 1),
        to: custom.to ? new Date(custom.to) : new Date(),
      };
    default:
      from.setDate(to.getDate() - 30);
  }
  return { from, to };
}

export function FilterProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenario] = useState<Scenario>('SaaS');
  const [dateRange, setDateRange] = useState<DateRange>('last30');
  const [customDateRange, setCustomDateRange] = useState<CustomDateRange>({ from: '', to: '' });

  const getEffectiveDateRange = useCallback(() => {
    return computeRange(dateRange, customDateRange);
  }, [dateRange, customDateRange]);

  return (
    <FilterContext.Provider
      value={{
        scenario,
        setScenario,
        dateRange,
        setDateRange,
        customDateRange,
        setCustomDateRange,
        getEffectiveDateRange,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilterContext(): FilterContextValue {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error('useFilterContext must be used within FilterProvider');
  return ctx;
}
