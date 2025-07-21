import dynamic from 'next/dynamic';

const AdminDashboard = dynamic(
  () => import('@/components/admin/admin-dashboard'),
  { ssr: false }
);

export default function AdminPage() {
  return <AdminDashboard />;
}
