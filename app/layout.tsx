import { Navbar } from "@/components/navbar";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";
import { headers } from 'next/headers';

const inter = Inter({ subsets: ["latin"] });
const userName = `${process.env.NEXT_PUBLIC_PROFILE_NAME}`;
const webUri = `${process.env.NEXT_PUBLIC_WEB_URI}`;
const webDescription = `${process.env.NEXT_PUBLIC_WEB_DESCRIPTION}`;

export const metadata: Metadata = {
  title: "Autogram",
  description: "SNS 자동화 도구",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const heads = headers();
  const pathname = heads.get('next-url') || '';
  const isAdminPage = pathname.startsWith('/admin');

  return (
    <html lang="ko">
      <head>
      <meta property="og:url" content={webUri} />
        <meta property="og:title" content={userName} />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="/profile.png" />
        <meta property="og:description" content={webDescription} />
      </head>

      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          {!isAdminPage && <Navbar />}
          <main className={`flex-grow ${!isAdminPage ? 'container mx-auto p-4' : ''}`}>
            {children}
          </main>
        </div>
        <Toaster richColors />
      </body>
    </html>
  );
}
