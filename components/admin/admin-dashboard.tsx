'use client';

import InstagramGroupManager from '@/components/admin/instagram-group-manager';
import SnsRaiseUserManager from '@/components/admin/sns-raise-user-manager';
import { InstagramCheckerManager } from '@/components/admin/instagram-admin-manager';

export default function AdminDashboard() {
  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <header className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-primary text-center">
          관리자 대시보드
        </h1>
      </header>
      <div className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <InstagramGroupManager />
          <SnsRaiseUserManager />
        </div>
        <div>
          <InstagramCheckerManager />
        </div>
      </div>
    </div>
  );
}
