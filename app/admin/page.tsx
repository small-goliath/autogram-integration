'use client';

import AdminDashboard from '@/components/admin/admin-dashboard';
import { FormEvent, useEffect, useState } from 'react';
import { toast } from 'sonner';

export default function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 컴포넌트 마운트 시 localStorage에서 인증 정보 확인
    const storedUsername = localStorage.getItem('admin_username');
    const storedApiKey = localStorage.getItem('admin_api_key');
    if (storedUsername && storedApiKey) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/admin/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, api_key: apiKey }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || '로그인에 실패했습니다.');
      }

      toast.success('로그인 성공!');
      localStorage.setItem('admin_username', username);
      localStorage.setItem('admin_api_key', apiKey);
      setIsAuthenticated(true);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      localStorage.removeItem('admin_username');
      localStorage.removeItem('admin_api_key');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_api_key');
    setIsAuthenticated(false);
    toast.info('로그아웃되었습니다.');
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
          <h1 className="text-2xl font-bold text-center text-primary">관리자 로그인</h1>
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label
                htmlFor="username"
                className="text-sm font-medium text-gray-700"
              >
                사용자 이름
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full px-3 py-2 mt-1 border rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label
                htmlFor="api-key"
                className="text-sm font-medium text-gray-700"
              >
                패스워드
              </label>
              <input
                id="api-key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                required
                className="w-full px-3 py-2 mt-1 border rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 font-medium text-white bg-primary rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50"
            >
              {loading ? '로그인 중...' : '로그인'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="space-y-8">
        <AdminDashboard />
      </div>
    </div>
  );
}
