import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { BarChart3, Mail, ArrowLeft, CheckCircle2 } from 'lucide-react';

export const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden font-sans">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 z-10 border border-slate-100">
        <div className="text-center mb-6">
          <div className="inline-flex w-12 h-12 rounded-xl bg-blue-600 text-white items-center justify-center mb-3 shadow-lg shadow-blue-500/30">
            <BarChart3 className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Reset Password</h2>
          <p className="text-xs text-gray-500 mt-1">
            Enter your email to receive password recovery instructions
          </p>
        </div>

        {submitted ? (
          <div className="text-center py-4">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-gray-900">Recovery Instructions Sent</h3>
            <p className="text-xs text-gray-500 mt-1">
              If an account exists for <span className="font-semibold text-gray-700">{email}</span>, you will receive password reset instructions.
            </p>
            <Link
              to="/login"
              className="mt-6 inline-flex items-center text-xs font-semibold text-blue-600 hover:underline"
            >
              <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Back to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-9 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-lg shadow-md transition"
            >
              Send Recovery Link
            </button>

            <div className="text-center pt-2">
              <Link
                to="/login"
                className="inline-flex items-center text-xs font-medium text-gray-500 hover:text-gray-900"
              >
                <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Return to login
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
