"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export const Navbar = () => {
  const pathname = usePathname();
  const [producerCount, setProducerCount] = useState<number | null>(null);
  const [consumerCount, setConsumerCount] = useState<number | null>(null);

  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const [producerRes, consumerRes] = await Promise.all([
          fetch("/api/sns-raise/producers"),
          fetch("/api/sns-raise/consumers"),
        ]);

        if (!producerRes.ok || !consumerRes.ok) {
          throw new Error("Failed to fetch user counts");
        }

        const producerData = await producerRes.json();
        const consumerData = await consumerRes.json();

        setProducerCount(producerData.count);
        setConsumerCount(consumerData.count);
      } catch (error) {
        console.error(error);
        setProducerCount(0);
        setConsumerCount(0);
      }
    };

    fetchCounts();
  }, []);

  const navItems = [
    { name: "공지사항", href: "/notice" },
    { name: "SNS 키우기 품앗이 현황", href: "/sns-raise" },
    {
      name: "[AI] 자동 댓글 받기 신청",
      href: "/sns-raise/ai-comment",
      count: consumerCount,
    },
    {
      name: "[AI] 자동 댓글 달기 신청",
      href: "/sns-raise/ai-comment-producer",
      count: producerCount,
    },
    { name: "인스타 언팔검색기", href: "/unfollow-checker" },
  ];

  return (
    <header className="p-4 flex flex-col sm:flex-row justify-between items-center gap-4 border-b">
      <div className="flex items-center gap-4">
        <nav className="flex items-center gap-2">
          {navItems.map((item) => (
            <Link key={item.name} href={item.href}>
              <Button
                variant={pathname === item.href ? "secondary" : "ghost"}
                className={cn(
                  "rounded-md",
                  pathname === item.href && "text-[#5a67d8]"
                )}
              >
                {item.name}
                {item.count !== undefined && item.count !== null && (
                  <span className="ml-2 bg-blue-500 text-white text-xs font-semibold px-2 py-1 rounded-full">
                    {item.count}명
                  </span>
                )}
              </Button>
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
};
