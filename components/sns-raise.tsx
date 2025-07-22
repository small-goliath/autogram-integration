'use client';

import { useEffect, useState } from 'react';

interface Verification {
  username: string;
  link: string;
}

interface VerificationGroup {
  [username: string]: string[];
}

export default function SnsRaise() {
  const [verifications, setVerifications] = useState<VerificationGroup>({});
  const [userCount, setUserCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [verificationsRes, countRes] = await Promise.all([
          fetch('/backend/sns-raise/verifications'),
          fetch('/backend/sns-raise/users'),
        ]);

        if (!verificationsRes.ok) {
          throw new Error('인증 데이터를 불러오는데 실패했습니다');
        }
        if (!countRes.ok) {
          throw new Error('사용자 수를 불러오는데 실패했습니다');
        }

        const verificationsData: Verification[] = await verificationsRes.json();
        const countData = await countRes.json();

        const grouped: VerificationGroup = {};
        verificationsData.forEach(({ username, link }) => {
          if (!grouped[username]) {
            grouped[username] = [];
          }
          grouped[username].push(link);
        });

        setVerifications(grouped);
        setUserCount(countData.count);
      } catch (err) {
        setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 bg-muted rounded w-1/4 mb-6 animate-pulse"></div>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-card p-4 rounded-lg shadow animate-pulse">
            <div className="h-6 bg-muted rounded w-1/3 mb-4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded w-full"></div>
              <div className="h-4 bg-muted rounded w-5/6"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 text-destructive p-4 rounded-lg text-center">
        <p>데이터 로딩 오류: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-primary/10 border-l-4 border-primary text-black p-4 rounded-lg">
        <p className="text-lg font-semibold">
          현재 <span className="text-2xl font-bold">{userCount}</span>명의 사용자가 SNS 품앗이에 참여하고 있습니다.
        </p>
      </div>
      {Object.entries(verifications).map(([username, links]) => (
        <div key={username} className="bg-card p-4 sm:p-6 rounded-lg shadow-md">
          <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">{username}</h2>
          <ul className="space-y-3">
            {links.map((link, index) => (
              <li key={index}>
                <a
                  href={link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-foreground hover:text-primary transition-colors break-all"
                >
                  {link}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

