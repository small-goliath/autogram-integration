'use client';

import { FormEvent, useEffect, useState } from 'react';
import { toast } from 'sonner';

interface InstagramGroup {
  id: number;
  type: string;
}

export default function InstagramGroupManager() {
  const [groups, setGroups] = useState<InstagramGroup[]>([]);
  const [newGroup, setNewGroup] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchGroups = async () => {
    console.log("인스타그램 그룹 목록을 가져옵니다.");
    try {
      const res = await fetch('/api/sns-raise/groups');
      if (!res.ok) throw new Error('그룹을 불러오는데 실패했습니다');
      const data = await res.json();
      setGroups(data);
      console.log("인스타그램 그룹 목록을 성공적으로 가져왔습니다:", data);
    } catch (err) {
      console.error("인스타그램 그룹 목록을 가져오는데 실패했습니다:", err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const addGroup = async (e: FormEvent) => {
    e.preventDefault();
    if (!newGroup.trim()) return;
    setLoading(true);
    console.log(`인스타그램 그룹 추가를 시도합니다: ${newGroup}`);
    try {
      const res = await fetch('/api/admin/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: newGroup }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '그룹을 추가하는데 실패했습니다');
      }
      console.log(`인스타그램 그룹 "${newGroup}"을(를) 성공적으로 추가했습니다.`);
      toast.success(`그룹 "${newGroup}"이(가) 성공적으로 추가되었습니다!`);
      setNewGroup('');
      await fetchGroups();
    } catch (err) {
      console.error(`인스타그램 그룹 "${newGroup}" 추가 실패:`, err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const deleteGroup = async (groupId: number, type: string) => {
    console.log(`인스타그램 그룹 삭제를 시도합니다: ${type} (ID: ${groupId})`);
    try {
      const res = await fetch(`/api/admin/groups/${groupId}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || '그룹을 삭제하는데 실패했습니다');
      }
      console.log(`인스타그램 그룹 "${type}"을(를) 성공적으로 삭제했습니다.`);
      toast.success(`그룹 "${type}"이(가) 성공적으로 삭제되었습니다!`);
      await fetchGroups();
    } catch (err) {
      console.error(`인스타그램 그룹 "${type}" 삭제 실패:`, err);
      toast.error(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    }
  };

  return (
    <div className="bg-card p-4 sm:p-6 rounded-lg shadow-md">
      <h2 className="text-xl sm:text-2xl font-bold text-primary mb-4">인스타그램 그룹 관리</h2>
      <form onSubmit={addGroup} className="mb-4 flex flex-col sm:flex-row gap-2">
        <input
          type="text"
          value={newGroup}
          onChange={(e) => setNewGroup(e.target.value)}
          placeholder="새 그룹 타입"
          className="border p-2 rounded-md flex-grow bg-input text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary"
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
          disabled={loading}
        >
          {loading ? '추가 중...' : '그룹 추가'}
        </button>
      </form>
      <div className="space-y-2">
        {groups.map((group) => (
          <div key={group.id} className="flex justify-between items-center p-3 bg-muted/50 rounded-md">
            <span className="font-medium">{group.type}</span>
            <button
              onClick={() => deleteGroup(group.id, group.type)}
              className="bg-destructive text-destructive-foreground px-3 py-1 rounded-md text-sm hover:bg-destructive/90 transition-colors"
            >
              삭제
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
