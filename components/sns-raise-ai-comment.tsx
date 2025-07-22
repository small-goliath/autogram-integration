'use client';

import { useState, FormEvent, useEffect } from 'react';
import { toast } from 'sonner';

interface InstagramGroup {
  id: number;
  type: string;
}

export default function SnsRaiseAIComment() {
  const [username, setUsername] = useState('');
  const [groupId, setGroupId] = useState<string>('');
  const [instagramGroups, setInstagramGroups] = useState<InstagramGroup[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchGroups = async () => {
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
      } catch (error) {
        toast.error(error instanceof Error ? error.message : '그룹 로드 중 오류가 발생했습니다.');
      }
    };
    fetchGroups();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !groupId) {
      toast.warning('인스타그램 계정과 계정 타입을 모두 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('/backend/sns-raise/consumers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, group_id: parseInt(groupId) }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || '신청에 실패했습니다.');
      }

      toast.success('AI 자동 댓글 받기 신청이 완료되었습니다!');
      setUsername('');
      setGroupId(instagramGroups.length > 0 ? String(instagramGroups[0].id) : '');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : '신청 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-card p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold text-primary mb-4">신청하기</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
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
          {loading ? '신청 중...' : '신청하기'}
        </button>
      </form>
    </div>
  );
}
