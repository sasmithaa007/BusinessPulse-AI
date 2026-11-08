import React, { useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Download, Database } from 'lucide-react';
import { datasetsApi } from '../api/datasets';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const DatasetExplorer: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'explorer'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.endsWith('.csv')) {
        setError('Only .csv files are supported.');
        return;
      }
      if (selected.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit.');
        return;
      }
      setError(null);
      setFile(selected);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await datasetsApi.upload(formData);
      setPreviewData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to parse and upload CSV.');
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadSample = () => {
    const csvContent =
      'customer_code,name,email,customer_type,signup_date,status,segment,lifetime_value\n' +
      'CUST-DEMO-01,Aditi Verma,aditi.verma@example.com,individual,2024-01-10,active,premium,45000\n' +
      'CUST-DEMO-02,Vikram Rao,vikram.rao@example.com,business,2024-02-14,active,enterprise,120000\n' +
      'CUST-DEMO-03,Neha Sen,neha.sen@example.com,individual,2024-03-01,churned,basic,3200\n';
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'sample_businesspulse_dataset.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Header and Download Template Action */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-gray-900">Dataset Ingestion & Quality Hub</h2>
            <p className="text-xs text-gray-500">
              Upload customer or transaction CSV datasets for schema validation and missing-value audit
            </p>
          </div>
        </div>
        <button
          onClick={handleDownloadSample}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-lg transition"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Download Sample CSV Template</span>
        </button>
      </div>

      {/* Upload Zone */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 text-center space-y-4">
        <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 hover:border-blue-400 transition-colors flex flex-col items-center">
          <UploadCloud className="w-12 h-12 text-blue-600 mb-3" />
          <h3 className="text-sm font-bold text-gray-800">Select or Drag CSV to Ingest</h3>
          <p className="text-xs text-gray-400 mt-1 max-w-sm">
            Strict UTF-8 CSV validation. Column types, duplicate rows, and nulls are scored automatically.
          </p>

          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="hidden"
            id="csv-file-input"
          />
          <label
            htmlFor="csv-file-input"
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg cursor-pointer transition shadow-sm"
          >
            {file ? file.name : 'Browse Local Files'}
          </label>
        </div>

        {file && (
          <div className="flex items-center justify-center space-x-3 text-xs text-gray-600">
            <FileText className="w-4 h-4 text-blue-600" />
            <span className="font-semibold text-gray-800">{file.name}</span>
            <span>({(file.size / 1024).toFixed(1)} KB)</span>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded shadow-sm disabled:opacity-50"
            >
              {uploading ? 'Analyzing...' : 'Execute Ingestion & Validation'}
            </button>
          </div>
        )}
      </div>

      {/* Uploaded Quality Assessment Result */}
      {previewData && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <h3 className="text-base font-bold text-gray-900">
                Dataset Ingested: {previewData.filename || 'Uploaded File'}
              </h3>
            </div>
            <span className="text-xs font-bold px-2.5 py-0.5 bg-emerald-50 text-emerald-700 rounded-full">
              Schema Validated
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-[10px] uppercase font-bold text-gray-400">Total Rows</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">
                {previewData.row_count || previewData.rows || 0}
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-[10px] uppercase font-bold text-gray-400">Columns</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">
                {previewData.column_count || previewData.columns?.length || 0}
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-[10px] uppercase font-bold text-gray-400">Duplicate Rows</div>
              <div className="text-lg font-bold text-emerald-600 mt-0.5">
                {previewData.duplicate_rows ?? 0}
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="text-[10px] uppercase font-bold text-gray-400">Missing Nulls</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">
                {previewData.missing_values_count ?? 0}
              </div>
            </div>
          </div>

          {/* First 10 Rows Preview Table */}
          {previewData.preview && previewData.preview.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                First 10 Ingested Rows Preview
              </h4>
              <div className="overflow-x-auto border border-gray-100 rounded-lg">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-gray-50 text-gray-600 border-b border-gray-100">
                    <tr>
                      {Object.keys(previewData.preview[0]).map((k) => (
                        <th key={k} className="p-2.5">
                          {k}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {previewData.preview.slice(0, 10).map((row: any, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {Object.values(row).map((val: any, cidx: number) => (
                          <td key={cidx} className="p-2.5 whitespace-nowrap text-gray-700">
                            {String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
