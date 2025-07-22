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

export function InstagramCheckerManager() {
    const [checkers, setCheckers] = useState<CheckerAccount[]>([]);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    
    const [isLoading, setIsLoading] = useState(false);
    const [needs2FA, setNeeds2FA] = useState(false);

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
        setNeeds2FA(false);

        try {
            // Note: Login is not an admin-protected endpoint itself
            const res = await fetch('/api/sns-raise/instagram/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || '로그인에 실패했습니다.');
            }
            
            if (data.two_factor_required) {
                toast.info(data.message);
                setNeeds2FA(true);
            } else {
                toast.success(data.message);
                await registerChecker(username);
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '로그인 중 오류가 발생했습니다.';
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
        try {
            // Note: 2FA Login is not an admin-protected endpoint itself
            const res = await fetch('/api/sns-raise/instagram/login/2fa', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, verification_code: verificationCode }),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || '2FA 로그인에 실패했습니다.');
            }
            toast.success(data.message);
            await registerChecker(username);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '2FA 인증 중 오류가 발생했습니다.';
            toast.error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const registerChecker = async (currentUsername: string) => {
        toast.info(`${currentUsername} 계정을 체커로 등록합니다...`);
        try {
            const response = await fetchWithAdminAuth('/api/admin/checkers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: currentUsername }),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || '체커 등록에 실패했습니다.');
            }
            toast.success(`[${currentUsername}] 체커 등록이 완료되었습니다.`);
            // Reset form
            setUsername('');
            setPassword('');
            setVerificationCode('');
            setNeeds2FA(false);
            fetchCheckers(); // Refresh list
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : '체커 등록 중 오류가 발생했습니다.';
            toast.error(errorMessage);
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

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (needs2FA) {
            handleTwoFactorSubmit(e);
        } else {
            handleLogin(e);
        }
    }

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>인스타그램 체커 등록</CardTitle>
                    <CardDescription>
                        {needs2FA 
                            ? "2단계 인증 코드를 입력하여 로그인을 완료하세요." 
                            : "관리 작업을 위한 새 인스타그램 계정을 로그인하여 추가합니다."
                        }
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {!needs2FA && (
                            <>
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
                                        required
                                        disabled={isLoading}
                                    />
                                </div>
                            </>
                        )}
                        
                        {needs2FA && (
                            <div className="space-y-2">
                                <Label htmlFor="2fa-code">2단계 인증 코드</Label>
                                <Input
                                    id="2fa-code"
                                    value={verificationCode}
                                    onChange={(e) => setVerificationCode(e.target.value)}
                                    placeholder="123456"
                                    required
                                    disabled={isLoading}
                                />
                            </div>
                        )}
                        <Button type="submit" disabled={isLoading} className="w-full">
                            {isLoading ? '처리 중...' : (needs2FA ? '인증 및 등록' : '로그인 및 등록')}
                        </Button>
                    </form>
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
    );
}