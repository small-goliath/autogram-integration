import React from 'react';

export const metadata = {
  title: 'Admin - Autogram',
  description: 'Admin dashboard for Autogram',
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        {children}
      </body>
    </html>
  );
}
