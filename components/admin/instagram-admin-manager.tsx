"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { fetchWithAdminAuth } from "@/lib/utils";
import { FormEvent, useEffect, useState } from 'react';
import { toast } from 'sonner';

interface CheckerAccount {
    id: number;
    username: string;
}

interface LoginResponse {
    message: string;
    two_factor_required?: boolean;
    detail?: string;
}

export function InstagramCheckerManager() {
    const [checkers, setCheckers] = useState<CheckerAccount[]>([]);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [twoFactorRequired, setTwoFactorRequired] = useState(false);
    const [verificationCode, setVerificationCode] = useState('');

    const fetchCheckers = async () => {
        try {
            const response = await fetchWithAdminAuth('/api/admin/checkers');
            if (!response.ok) {
                throw new Error('체커 계정을 불러오는데 실패했습니다.');
            }
            const data = await response.json();
            setCheckers(data);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
            toast.error(errorMessage);
        }
    };

    useEffect(() => {
        fetchCheckers();
    }, []);

    const handleLogin = async (e: FormEvent) => {
        e.preventDefault();
        if (!username.trim() || !password.trim()) {
            toast.warning('아이디와 비밀번호를 모두 입력해주세요.');
            return;
        }
        setIsLoading(true);
        toast.info(`${username} 계정을 체커로 등록 및 로그인합니다...`);
        try {
            const response = await fetchWithAdminAuth('/api/admin/checkers/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data: LoginResponse = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || '체커 등록에 실패했습니다.');
            }

            if (data.two_factor_required) {
                toast.info(data.message);
                setTwoFactorRequired(true);
            } else {
                toast.success(data.message);
                setUsername('');
                setPassword('');
                fetchCheckers();
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '체커 등록 중 오류가 발생했습니다.';
            toast.error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTwoFactorSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!verificationCode.trim()) {
            toast.warning('2FA 코드를 입력해주세요.');
            return;
        }
        setIsLoading(true);
        toast.info(`[${username}] 2단계 인증을 시도합니다...`);
        try {
            const response = await fetchWithAdminAuth('/api/admin/checkers/login/2fa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, verification_code: verificationCode }),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || '2FA 로그인에 실패했습니다.');
            }
            toast.success(data.message);
            setTwoFactorRequired(false);
            setUsername('');
            setPassword('');
            setVerificationCode('');
            fetchCheckers();
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '2FA 인증 중 오류가 발생했습니다.';
            toast.error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('이 체커 계정을 정말 삭제하시겠습니까?')) {
            return;
        }
        
        setIsLoading(true);
        try {
            const response = await fetchWithAdminAuth(`/api/admin/checkers/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || '계정 삭제에 실패했습니다.');
            }
            
            toast.success('계정이 성공적으로 삭제되었습니다.');
            fetchCheckers(); // Refresh list
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
            toast.error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>인스타그램 체커 등록</CardTitle>
                        <CardDescription>
                            관리 작업을 위한 새 인스타그램 계정을 추가합니다.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {!twoFactorRequired ? (
                            <form onSubmit={handleLogin} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="username">인스타그램 사용자 이름</Label>
                                    <Input
                                        id="username"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="인스타그램 계정"
                                        required
                                        disabled={isLoading}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="password">비밀번호</Label>
                                    <Input
                                        id="password"
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="인스타그램 비밀번호"
                                        required
                                        disabled={isLoading}
                                    />
                                </div>
                                <Button type="submit" disabled={isLoading} className="w-full">
                                    {isLoading ? '처리 중...' : '등록'}
                                </Button>
                            </form>
                        ) : (
                            <form onSubmit={handleTwoFactorSubmit} className="space-y-4">
                                <h3 className="text-lg font-semibold">2단계 인증(2FA)</h3>
                                <p className="text-sm text-muted-foreground">
                                    인증 앱(또는 SMS)에서 생성된 6자리 코드를 입력해주세요.
                                </p>
                                <div className="space-y-2">
                                    <Label htmlFor="verificationCode">인증 코드</Label>
                                    <Input
                                        id="verificationCode"
                                        value={verificationCode}
                                        onChange={(e) => setVerificationCode(e.target.value)}
                                        placeholder="인증 코드 6자리"
                                        maxLength={6}
                                        required
                                        disabled={isLoading}
                                    />
                                </div>
                                <Button type="submit" disabled={isLoading} className="w-full">
                                    {isLoading ? '인증 중...' : '인증 및 등록'}
                                </Button>
                            </form>
                        )}
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>등록된 체커 계정</CardTitle>
                        <CardDescription>현재 관리 중인 인스타그램 계정 목록입니다.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>사용자 이름</TableHead>
                                    <TableHead className="text-right">작업</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {checkers.length > 0 ? (
                                    checkers.map((checker) => (
                                        <TableRow key={checker.id}>
                                            <TableCell>{checker.id}</TableCell>
                                            <TableCell className="font-medium">{checker.username}</TableCell>
                                            <TableCell className="text-right">
                                                <Button
                                                    variant="destructive"
                                                    size="sm"
                                                    onClick={() => handleDelete(checker.id)}
                                                    disabled={isLoading}
                                                >
                                                    삭제
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={3} className="text-center">
                                            등록된 체커 계정이 없습니다.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>
        </>
    );
}
