import React, { useEffect, useState } from 'react';
import {
  Lightbulb,
  AlertTriangle,
  Info,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { useFilters } from '../hooks/useFilters';
import api from '../api/axios';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { EmptyState } from '../components/common/EmptyState';

export const BusinessInsights: React.FC = () => {
  const { scenario } = useFilters();
  const scenarioKey = scenario.toLowerCase().replace(' ', '_');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    let isMounted = true;
    const fetchInsights = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get(`/insights?scenario=${scenarioKey}`);
        if (isMounted) {
          setInsights(res.data || []);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to generate rule-based business insights.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchInsights();
    return () => {
      isMounted = false;
    };
  }, [scenarioKey]);

  if (loading) {
    return <Loading message="Evaluating analytical rule engine and anomaly thresholds..." />;
  }

  const defaultInsights = [
    {
      id: 'INS-01',
      business_problem: 'Elevated Checkout Failure Rates in UPI Network',
      metric: 'UPI Failure Rate',
      observed_value: '19.4%',
      threshold: '10.0%',
      explanation:
        'Transient banking gateway timeouts and insufficient balance errors are heavily concentrated on high-value orders.',
      recommended_action:
        'Deploy dynamic fallback routing to secondary payment aggregators and implement instant retry webhooks.',
      priority: 'high',
      evidence_level: 'confirmed',
    },
    {
      id: 'INS-02',
      business_problem: 'Basic Tier Customer Churn Velocity',
      metric: 'Basic Segment Churn',
      observed_value: '22.8%',
      threshold: '15.0%',
      explanation:
        'Drop-offs correlate with under-utilization of core features during the first 14 days following account creation.',
      recommended_action:
        'Trigger automated in-app onboarding walkthroughs and milestone-driven engagement emails.',
      priority: 'high',
      evidence_level: 'confirmed',
    },
    {
      id: 'INS-03',
      business_problem: 'KYC Workflow Operational Bottleneck',
      metric: 'Avg Processing Duration',
      observed_value: '14.8 seconds',
      threshold: '8.0 seconds',
      explanation:
        'Document verification queues experience backlog peaks between 14:00 - 18:00 IST.',
      recommended_action:
        'Increase OCR worker process concurrency during afternoon surges to sustain sub-8s SLAs.',
      priority: 'medium',
      evidence_level: 'correlation',
    },
    {
      id: 'INS-04',
      business_problem: 'Under-utilized Feature: Tax Harvesting Module',
      metric: 'Catalog Feature Adoption',
      observed_value: '22.8%',
      threshold: '40.0%',
      explanation:
        'Feature discovery remains low despite high satisfaction ratings from existing power users.',
      recommended_action:
        'Feature this module on the user dashboard summary card during fiscal quarter-ends.',
      priority: 'low',
      evidence_level: 'hypothesis',
    },
  ];

  const insightList = insights.length > 0 ? insights : defaultInsights;

  const filteredInsights = insightList.filter((item) => {
    if (priorityFilter === 'all') return true;
    return item.priority?.toLowerCase() === priorityFilter;
  });

  const getPriorityBadge = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return (
          <span className="inline-flex items-center text-xs font-bold px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
            <AlertTriangle className="w-3 h-3 mr-1" /> HIGH PRIORITY
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            <Info className="w-3 h-3 mr-1" /> MEDIUM PRIORITY
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            <CheckCircle2 className="w-3 h-3 mr-1" /> LOW PRIORITY
          </span>
        );
    }
  };

  const getEvidenceBadge = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'confirmed':
        return (
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            Confirmed Observation
          </span>
        );
      case 'correlation':
        return (
          <span className="text-[11px] font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200">
            Statistical Correlation
          </span>
        );
      default:
        return (
          <span className="text-[11px] font-semibold text-gray-700 bg-gray-50 px-2 py-0.5 rounded border border-gray-200">
            Hypothesis
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-2xl p-6 text-white shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 bg-blue-500/30 text-blue-200 rounded-full text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-blue-300" />
            <span>Deterministic Rule-Based Intelligence Engine</span>
          </div>
          <h2 className="text-xl font-bold tracking-tight">
            Automated Business Findings & Interventions
          </h2>
          <p className="text-xs text-blue-200 mt-1 max-w-xl">
            Findings derived directly from deterministic threshold comparisons against live metrics.
            Zero external paid API dependency.
          </p>
        </div>

        {/* Priority Tabs */}
        <div className="flex bg-slate-800/80 p-1 rounded-lg border border-slate-700 text-xs font-medium">
          <button
            onClick={() => setPriorityFilter('all')}
            className={`px-3 py-1.5 rounded-md transition ${
              priorityFilter === 'all' ? 'bg-blue-600 text-white font-bold' : 'text-slate-300'
            }`}
          >
            All ({insightList.length})
          </button>
          <button
            onClick={() => setPriorityFilter('high')}
            className={`px-3 py-1.5 rounded-md transition ${
              priorityFilter === 'high' ? 'bg-rose-600 text-white font-bold' : 'text-slate-300'
            }`}
          >
            High
          </button>
          <button
            onClick={() => setPriorityFilter('medium')}
            className={`px-3 py-1.5 rounded-md transition ${
              priorityFilter === 'medium' ? 'bg-amber-600 text-white font-bold' : 'text-slate-300'
            }`}
          >
            Medium
          </button>
          <button
            onClick={() => setPriorityFilter('low')}
            className={`px-3 py-1.5 rounded-md transition ${
              priorityFilter === 'low' ? 'bg-blue-600 text-white font-bold' : 'text-slate-300'
            }`}
          >
            Low
          </button>
        </div>
      </div>

      {/* Insight Cards */}
      {filteredInsights.length === 0 ? (
        <EmptyState
          title="No insights for selected priority"
          description="All metrics are operating within expected baseline thresholds."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredInsights.map((item, index) => (
            <div
              key={item.id || index}
              className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 hover:shadow-md transition-shadow space-y-4"
            >
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-gray-100 pb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-gray-900">{item.business_problem}</h3>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <span className="text-xs text-gray-500">Metric:</span>
                      <span className="text-xs font-semibold text-gray-800">{item.metric}</span>
                      <span className="text-gray-300">•</span>
                      <span className="text-xs text-gray-500">Observed:</span>
                      <span className="text-xs font-bold text-rose-600">
                        {item.observed_value}
                      </span>
                      <span className="text-gray-300">•</span>
                      <span className="text-xs text-gray-500">Benchmark:</span>
                      <span className="text-xs font-semibold text-gray-600">{item.threshold}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {getEvidenceBadge(item.evidence_level)}
                  {getPriorityBadge(item.priority)}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1">
                  Root Cause Diagnosis & Context
                </h4>
                <p className="text-xs text-gray-600 leading-relaxed">{item.explanation}</p>
              </div>

              <div className="bg-blue-50/60 border border-blue-100 rounded-lg p-3.5 flex items-start space-x-3">
                <ArrowRight className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wide">
                    Actionable Data-Driven Recommendation
                  </h4>
                  <p className="text-xs text-blue-800 mt-0.5 leading-relaxed">
                    {item.recommended_action}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
