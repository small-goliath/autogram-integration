'use client';

import { FormEvent, useEffect, useState } from 'react';
import { toast } from 'sonner';

interface SnsRaiseUser {
  id: number;
  username: string;
}

export default function SnsRaiseUserManager() {
  const [users, setUsers] = useState<SnsRaiseUser[]>([]);
  const [newUser, setNewUser] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    console.log("SNS 품앗이 사용자 목록을 가져옵니다.");
    try {
      const res = await fetch('/api/sns-raise/users');
      if (!res.ok) throw new Error('사용자를 불러오는데 실패했습니다');
      const data = await res.json();
      setUsers(data.details); // data.details를 users 상태로 설정
      console.log("SNS 품앗이 사용자 목록을 성공적으로 가져왔습니다:", data.details);
    } catch (err) {
      console.error("SNS 품앗이 사용자 목록을 가져오는데 실패했습니다:", err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const addUser = async (e: FormEvent) => {
    e.preventDefault();
    if (!newUser.trim()) return;
    setLoading(true);
    console.log(`SNS 품앗이 사용자 추가를 시도합니다: ${newUser}`);
    try {
      const res = await fetch(`/api/admin/users/${newUser}`, {
        method: 'POST',
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '사용자를 추가하는데 실패했습니다');
      }
      console.log(`SNS 품앗이 사용자 "${newUser}"을(를) 성공적으로 추가했습니다.`);
      toast.success(`사용자 "${newUser}"이(가) 성공적으로 추가되었습니다!`);
      setNewUser('');
      await fetchUsers();
    } catch (err) {
      console.error(`SNS 품앗이 사용자 "${newUser}" 추가 실패:`, err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (username: string) => {
    console.log(`SNS 품앗이 사용자 삭제를 시도합니다: ${username}`);
    try {
      const res = await fetch(`/api/admin/users/${username}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '사용자를 삭제하는데 실패했습니다');
      }
      console.log(`SNS 품앗이 사용자 "${username}"을(를) 성공적으로 삭제했습니다.`);
      toast.success(`사용자 "${username}"이(가) 성공적으로 삭제되었습니다!`);
      await fetchUsers();
    } catch (err) {
      console.error(`SNS 품앗이 사용자 "${username}" 삭제 실패:`, err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    }
  };

  return (
    <div className="bg-card p-4 sm:p-6 rounded-lg shadow-md">
      <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">SNS 품앗이 사용자 관리</h2>
      <form onSubmit={addUser} className="mb-4 flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          value={newUser}
          onChange={(e) => setNewUser(e.target.value)}
          placeholder="새 사용자 아이디"
          className="border p-2 rounded-md flex-grow bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
          disabled={loading}
        >
          {loading ? '추가 중...' : '사용자 추가'}
        </button>
      </form>
      <div className="space-y-2">
        {users.map((user) => (
          <div key={user.id} className="flex justify-between items-center p-3 bg-muted/50 rounded-md">
            <span className="font-medium">{user.username}</span>
            <button onClick={() => deleteUser(user.username)} className="bg-destructive text-destructive-foreground px-3 py-1 rounded-md text-sm hover:bg-destructive/90 transition-colors">
              삭제
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
