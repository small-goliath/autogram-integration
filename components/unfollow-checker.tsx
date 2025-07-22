'use client';

import Image from 'next/image';
import { FormEvent, useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';
import { AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";

interface Unfollower {
  username: string;
  profile_pic_url: string;
}

interface StatusResponse {
  logged_in: boolean;
  username: string | null;
}

interface LoginResponse {
  message: string;
  two_factor_required?: boolean;
  detail?: string;
}

interface CheckStatusResponse {
  status: 'idle' | 'processing' | 'completed' | 'error';
  message?: string;
  unfollowers?: Unfollower[];
  last_updated?: number;
}

export default function UnfollowChecker() {
  const [loginStatus, setLoginStatus] = useState<StatusResponse>({ logged_in: false, username: null });
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [checkUsername, setCheckUsername] = useState('');
  
  const [results, setResults] = useState<Unfollower[] | null>(null);
  const [lastChecked, setLastChecked] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [twoFactorRequired, setTwoFactorRequired] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');

  const [checkpointError, setCheckpointError] = useState<{ title: string; description: string; url: string } | null>(null);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  useEffect(() => {
    if (checkUsername) {
      console.log(`[${checkUsername}] 언팔로워 확인 상태 폴링 시작`);
      pollStatus();
    }
    return () => {
      console.log(`[${checkUsername}] 언팔로워 확인 상태 폴링 중지`);
      stopPolling();
    }
  }, [checkUsername]);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!loginUsername.trim() || !loginPassword.trim()) {
      toast.warning('아이디와 비밀번호를 모두 입력해주세요.');
      return;
    }
    setIsLoggingIn(true);
    setCheckpointError(null);
    console.log(`[${loginUsername}] 로그인 시도`);
    try {
      const res = await fetch('/api/sns-raise/instagram/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: loginUsername, password: loginPassword }),
      });
      const data: LoginResponse = await res.json();
      if (!res.ok) {
        const errorDetail = data.detail || '로그인에 실패했습니다.';
        if (errorDetail.includes("체크포인트")) {
            const urlMatch = errorDetail.match(/(https?:\/\/[^\s]+)/);
            setCheckpointError({
                title: "인스타그램 보안 인증 필요",
                description: "계정 보호를 위해 본인 인증이 필요합니다. 아래 '인증 페이지로 이동' 버튼을 눌러 브라우저에서 인증을 완료한 후, 다시 로그인을 시도해주세요.",
                url: urlMatch ? urlMatch[0] : 'https://www.instagram.com'
            });
        } else {
            throw new Error(errorDetail);
        }
        return;
      }
      
      if (data.two_factor_required) {
        console.log(`[${loginUsername}] 2단계 인증 필요`);
        toast.info(data.message);
        setTwoFactorRequired(true);
      } else {
        console.log(`[${loginUsername}] 로그인 성공`);
        toast.success(data.message);
        setLoginStatus({ logged_in: true, username: loginUsername });
        setCheckUsername(loginUsername);
        setLoginUsername('');
        setLoginPassword('');
      }
    } catch (err) {
      console.error(`[${loginUsername}] 로그인 오류:`, err);
      if (!checkpointError) {
        toast.error(err instanceof Error ? err.message : '로그인 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleTwoFactorSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!verificationCode.trim()) {
      toast.warning('2FA 코드를 입력해주세요.');
      return;
    }
    setIsLoggingIn(true);
    console.log(`[${loginUsername}] 2단계 인증 시도`);
    try {
      const res = await fetch('/api/sns-raise/instagram/login/2fa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: loginUsername, verification_code: verificationCode }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '2FA 로그인에 실패했습니다.');
      }
      console.log(`[${loginUsername}] 2단계 인증 성공`);
      toast.success(data.message);
      setLoginStatus({ logged_in: true, username: loginUsername });
      setCheckUsername(loginUsername);
      setTwoFactorRequired(false);
      setLoginUsername('');
      setLoginPassword('');
      setVerificationCode('');
    } catch (err) {
      console.error(`[${loginUsername}] 2단계 인증 오류:`, err);
      toast.error(err instanceof Error ? err.message : '2FA 인증 중 오류가 발생했습니다.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = async () => {
    console.log(`[${loginStatus.username}] 로그아웃 시도`);
    try {
      const res = await fetch('/api/instagram/logout', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '로그아웃에 실패했습니다.');
      }
      console.log(`[${loginStatus.username}] 로그아웃 성공`);
      toast.success(data.message);
      setResults(null);
      setLastChecked(null);
      setCheckUsername('');
      setLoginStatus({ logged_in: false, username: null });
    } catch (err) {
      console.error(`[${loginStatus.username}] 로그아웃 오류:`, err);
      toast.error(err instanceof Error ? err.message : '로그아웃 중 오류가 발생했습니다.');
    }
  };

  const pollStatus = async () => {
    if (!checkUsername) return;
    // console.log(`[${checkUsername}] 상태 확인 API 호출`);
    try {
      const res = await fetch(`/api/sns-raise/unfollowers/${checkUsername}`);
      if (!res.ok) {
        console.warn(`[${checkUsername}] 상태 확인 API 응답 오류: ${res.status}`);
        return;
      }
      
      const data: CheckStatusResponse = await res.json();
      // console.log(`[${checkUsername}] 현재 상태: ${data.status}`);

      switch (data.status) {
        case 'processing':
          setLoading(true);
          setLoadingMessage(data.message || '데이터를 처리 중입니다...');
          if (!pollingRef.current) {
            pollingRef.current = setInterval(pollStatus, 5000);
          }
          break;
        case 'completed':
          console.log(`[${checkUsername}] 언팔로워 확인 완료. ${data.unfollowers?.length || 0}명 발견.`);
          stopPolling();
          setLoading(false);
          setLoadingMessage('');
          setResults(data.unfollowers || []);
          setLastChecked(data.last_updated || null);
          toast.success(`총 ${data.unfollowers?.length || 0}명의 맞팔하지 않는 사용자를 찾았습니다.`);
          break;
        case 'error':
          console.error(`[${checkUsername}] 언팔로워 확인 중 오류 발생: ${data.message}`);
          stopPolling();
          setLoading(false);
          setLoadingMessage('');
          toast.error(data.message || '알 수 없는 오류가 발생했습니다.');
          break;
        case 'idle':
        default:
          stopPolling();
          setLoading(false);
          break;
      }
    } catch (err) {
      console.error(`[${checkUsername}] 상태 폴링 중 예외 발생:`, err);
    }
  };

  const handleCheck = async (e: FormEvent) => {
    e.preventDefault();
    console.log(`[${checkUsername}] 언팔로워 확인 시작`);
    setLoading(true);
    setResults(null);
    setLastChecked(null);
    setLoadingMessage('언팔로워 확인 작업을 시작합니다...');

    try {
      const res = await fetch(`/api/sns-raise/unfollowers/${checkUsername}`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '작업을 시작하는데 실패했습니다.');
      }
      console.log(`[${checkUsername}] 언팔로워 확인 작업 백그라운드에서 시작됨`);
      toast.info(data.message);
      stopPolling();
      pollingRef.current = setInterval(pollStatus, 5000);
    } catch (err) {
      console.error(`[${checkUsername}] 언팔로워 확인 시작 오류:`, err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      setLoading(false);
      setLoadingMessage('');
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <>
      <AlertDialog open={!!checkpointError} onOpenChange={() => setCheckpointError(null)}>
          <AlertDialogContent>
              <AlertDialogHeader>
                  <AlertDialogTitle>{checkpointError?.title}</AlertDialogTitle>
                  <AlertDialogDescription>
                      {checkpointError?.description}
                  </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                  <AlertDialogAction onClick={() => setCheckpointError(null)}>닫기</AlertDialogAction>
                  <AlertDialogAction asChild>
                      <a href={checkpointError?.url} target="_blank" rel="noopener noreferrer">인증 페이지로 이동</a>
                  </AlertDialogAction>
              </AlertDialogFooter>
          </AlertDialogContent>
      </AlertDialog>

      <div className="space-y-8">
        {loginStatus.logged_in ? (
          <div className="bg-card p-4 sm:p-6 rounded-lg shadow-md text-center">
            <p className="mb-4">
              <span className="font-bold text-primary">{loginStatus.username}</span>계정으로 로그인되어 있습니다.
            </p>
            <button onClick={handleLogout} className="bg-destructive text-destructive-foreground px-4 py-2 rounded-md hover:bg-destructive/90 transition-colors">
              로그아웃
            </button>
          </div>
        ) : (
          <div className="bg-card p-4 sm:p-6 rounded-lg shadow-md">
            {!twoFactorRequired ? (
              <>
                <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">인스타그램 로그인</h2>
                <p className="text-muted-foreground mb-4 text-sm">언팔로워를 확인하려면 인스타그램 계정으로 로그인해야 합니다. 비밀번호는 서버에 저장되지 않습니다.</p>
                <form onSubmit={handleLogin} className="space-y-4">
                  <input
                    type="text"
                    value={loginUsername}
                    onChange={(e) => setLoginUsername(e.target.value)}
                    placeholder="인스타그램 아이디"
                    className="w-full border p-2 rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
                    disabled={isLoggingIn}
                  />
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="비밀번호"
                    className="w-full border p-2 rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
                    disabled={isLoggingIn}
                  />
                  <button
                    type="submit"
                    className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                    disabled={isLoggingIn}
                  >
                    {isLoggingIn ? '로그인 중...' : '로그인'}
                  </button>
                </form>
              </>
            ) : (
              <>
                <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">2단계 인증(2FA)</h2>
                <p className="text-muted-foreground mb-4 text-sm">인증 앱(또는 SMS)에서 생성된 6자리 코드를 입력해주세요.</p>
                <form onSubmit={handleTwoFactorSubmit} className="space-y-4">
                  <input
                    type="text"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    placeholder="인증 코드 6자리"
                    className="w-full border p-2 rounded-md bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
                    disabled={isLoggingIn}
                    maxLength={6}
                  />
                  <button
                    type="submit"
                    className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                    disabled={isLoggingIn}
                  >
                    {isLoggingIn ? '인증 중...' : '인증'}
                  </button>
                </form>
              </>
            )}
          </div>
        )}

        {loginStatus.logged_in && (
          <div className="bg-card p-4 sm:p-6 rounded-lg shadow-md">
            <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">언팔로워 확인</h2>
            <form onSubmit={handleCheck} className="mb-6 flex flex-col sm:flex-row gap-2">
              <button
                type="submit"
                className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                disabled={loading}
              >
                {loading ? '확인 중...' : '확인'}
              </button>
            </form>

            {loading && (
              <div className="text-center">
                <p className="text-muted-foreground animate-pulse">{loadingMessage}</p>
              </div>
            )}

            {results && (
              <div>
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-semibold">
                    <span className="font-bold text-primary">{results.length}</span>명의 맞팔하지 않는 사용자:
                  </h3>
                  {lastChecked && (
                    <p className="text-sm text-muted-foreground">
                      마지막 확인: {formatTimestamp(lastChecked)}
                    </p>
                  )}
                </div>
                {results.length > 0 ? (
                  <ul className="space-y-2 max-h-96 overflow-y-auto p-3 bg-muted/50 rounded-md">
                    {results.map((user) => (
                      user && user.username && (
                        <li key={user.username} className="flex items-center justify-between p-2 hover:bg-muted rounded-md transition-colors">
                          <div className="flex items-center gap-3">
                            {user.profile_pic_url && (
                              <Image
                                src={user.profile_pic_url}
                                alt={`${user.username}의 프로필 사진`}
                                width={40}
                                height={40}
                                className="rounded-full"
                              />
                            )}
                            <span className="font-medium">{user.username}</span>
                          </div>
                          <a
                            href={`https://instagram.com/${user.username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary hover:underline"
                          >
                            프로필 보기
                          </a>
                        </li>
                      )
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted-foreground text-center p-4">
                    축하합니다! 모든 사용자가 맞팔로우하고 있습니다.
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}