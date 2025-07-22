"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useEffect, useMemo, useState } from "react";

interface Request {
  username: string;
  link: string;
}

interface UserSummary {
  username: string;
  count: number;
}

export default function LastWeekStatusPage() {
  const [requests, setRequests] = useState<Request[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        const response = await fetch("/api/last-week/requests");
        if (!response.ok) {
          throw new Error("Failed to fetch last week's requests");
        }
        const data = await response.json();
        setRequests(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "An unknown error occurred"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRequests();
  }, []);

  const filteredRequests = useMemo(() => {
    if (!filter) return requests;
    return requests.filter((request) =>
      request.username.toLowerCase().includes(filter.toLowerCase())
    );
  }, [requests, filter]);

  const userSummary: UserSummary[] = useMemo(() => {
    const counts: Record<string, number> = {};
    filteredRequests.forEach((request) => {
      counts[request.username] = (counts[request.username] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([username, count]) => ({ username, count }))
      .sort((a, b) => b.count - a.count);
  }, [filteredRequests]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  return (
    <main className="container mx-auto p-4 grid gap-4 md:grid-cols-3">
      <div className="md:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle>사용자별 요청 수</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead className="text-right">Count</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {userSummary.map((user) => (
                  <TableRow key={user.username}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell className="text-right">{user.count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
      <div className="md:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>지난주 품앗이 현황</CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              type="text"
              placeholder="본인의 닉네임을 입력해주세요."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="mb-4"
            />
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead>Link</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRequests.map((request, index) => (
                  <TableRow key={index}>
                    <TableCell>{request.username}</TableCell>
                    <TableCell>
                      <a
                        href={request.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                      >
                        {request.link}
                      </a>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
