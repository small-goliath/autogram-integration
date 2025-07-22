'use client';

import { FormEvent, useEffect, useState } from 'react';
import { toast } from 'sonner';

interface InstagramGroup {
  id: number;
  type: string;
}

interface LoginResponse {
  message: string;
  two_factor_required?: boolean;
  detail?: string;
}

export default function SnsRaiseAICommentProducer() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [groupId, setGroupId] = useState<string>('');
  const [instagramGroups, setInstagramGroups] = useState<InstagramGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [twoFactorRequired, setTwoFactorRequired] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');

  useEffect(() => {
    const fetchGroups = async () => {
      console.log("인스타그램 그룹 목록을 가져옵니다.");
      try {
        const res = await fetch('/backend/sns-raise/groups');
        if (!res.ok) {
          throw new Error('인스타그램 그룹을 불러오는데 실패했습니다.');
        }
        const data: InstagramGroup[] = await res.json();
        setInstagramGroups(data);
        if (data.length > 0) {
          setGroupId(String(data[0].id));
        }
        console.log("인스타그램 그룹 목록을 성공적으로 가져왔습니다:", data);
      } catch (error) {
        console.error("그룹 로드 중 오류가 발생했습니다:", error);
        toast.error(error instanceof Error ? error.message : '그룹 로드 중 오류가 발생했습니다.');
      }
    };
    fetchGroups();
  }, []);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim() || !groupId) {
      toast.warning('아이디, 비밀번호, 계정 타입을 모두 입력해주세요.');
      return;
    }
    setIsLoggingIn(true);
    setLoading(true);
    console.log(`[${username}] AI 댓글 생산자 등록 및 로그인 시도 (그룹 ID: ${groupId})`);
    try {
      const res = await fetch('/backend/sns-raise/producers/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, group_id: parseInt(groupId) }),
      });
      const data: LoginResponse = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '로그인에 실패했습니다.');
      }
      
      if (data.two_factor_required) {
        console.log(`[${username}] 2단계 인증 필요`);
        toast.info(data.message);
        setTwoFactorRequired(true);
      } else {
        console.log(`[${username}] AI 댓글 생산자 등록 및 로그인 성공`);
        toast.success(data.message);
        setUsername('');
        setPassword('');
        setGroupId(instagramGroups.length > 0 ? String(instagramGroups[0].id) : '');
      }
    } catch (err) {
      console.error(`[${username}] AI 댓글 생산자 로그인 오류:`, err);
      toast.error(err instanceof Error ? err.message : '로그인 중 오류가 발생했습니다.');
    } finally {
      setIsLoggingIn(false);
      setLoading(false);
    }
  };

  const handleTwoFactorSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!verificationCode.trim()) {
      toast.warning('2FA 코드를 입력해주세요.');
      return;
    }
    setIsLoggingIn(true);
    setLoading(true);
    console.log(`[${username}] AI 댓글 생산자 2단계 인증 시도`);
    try {
      const res = await fetch('/backend/sns-raise/producers/login/2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, verification_code: verificationCode, group_id: parseInt(groupId) }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '2FA 로그인에 실패했습니다.');
      }
      console.log(`[${username}] AI 댓글 생산자 2단계 인증 성공`);
      toast.success(data.message);
      setTwoFactorRequired(false);
      setUsername('');
      setPassword('');
      setVerificationCode('');
      setGroupId(instagramGroups.length > 0 ? String(instagramGroups[0].id) : '');
    } catch (err) {
      console.error(`[${username}] AI 댓글 생산자 2단계 인증 오류:`, err);
      toast.error(err instanceof Error ? err.message : '2FA 인증 중 오류가 발생했습니다.');
    } finally {
      setIsLoggingIn(false);
      setLoading(false);
    }
  };

  return (
    <div className="bg-card p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold text-primary mb-4">신청하기</h2>
      {!twoFactorRequired ? (
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-foreground mb-1">
              인스타그램 계정 (아이디)
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="예: my_instagram_id"
              className="w-full border p-2 rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
              disabled={loading}
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-foreground mb-1">
              비밀번호
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="인스타그램 비밀번호"
              className="w-full border p-2 rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
              disabled={loading}
              required
            />
          </div>
          <div>
            <label htmlFor="groupType" className="block text-sm font-medium text-foreground mb-1">
              계정 타입
            </label>
            <select
              id="groupType"
              value={groupId}
              onChange={(e) => setGroupId(e.target.value)}
              className="w-full border p-2 rounded-md bg-input text-foreground focus:ring-2 focus:ring-primary"
              disabled={loading}
              required
            >
              {instagramGroups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.type}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
            disabled={loading}
          >
            {isLoggingIn ? '로그인 중...' : '신청하기'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleTwoFactorSubmit} className="space-y-4">
          <h3 className="text-xl font-semibold text-primary mb-2">2단계 인증(2FA)</h3>
          <p className="text-muted-foreground mb-4 text-sm">인증 앱(또는 SMS)에서 생성된 6자리 코드를 입력해주세요.</p>
          <input
            type="text"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            placeholder="인증 코드 6자리"
            className="w-full border p-2 rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
            disabled={isLoggingIn}
            maxLength={6}
            required
          />
          <button
            type="submit"
            className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
            disabled={isLoggingIn}
          >
            {isLoggingIn ? '인증 중...' : '인증'}
          </button>
        </form>
      )}
    </div>
  );
}
