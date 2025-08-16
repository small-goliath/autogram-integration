"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Menu } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export const Navbar = () => {
  const pathname = usePathname();
  const [producerCount, setProducerCount] = useState<number | null>(null);
  const [consumerCount, setConsumerCount] = useState<number | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
    { name: "지난주 현황", href: "/last-week-status" },
    { name: "SNS 키우기 품앗이 현황", href: "/sns-raise" },
    {
      name: "[AI] 자동 댓글 받기 신청",
      href: "/sns-raise/ai-comment",
      count: consumerCount,
      isBeta: true,
    },
    {
      name: "[AI] 자동 댓글 달기 신청",
      href: "/sns-raise/ai-comment-producer",
      count: producerCount,
      isBeta: true,
    },
    { name: "인스타 언팔검색기", href: "/unfollow-checker" }
  ];

  return (
    <header className="p-4 flex flex-col md:flex-row justify-between items-center gap-4 border-b">
      <div className="w-full flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-[#5a67d8]">
          Autogram
        </Link>
        <div className="md:hidden">
          <Button variant="ghost" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            <Menu />
          </Button>
        </div>
      </div>
      <nav
        className={cn(
          "flex-col md:flex-row md:flex items-center gap-2",
          isMenuOpen ? "flex w-full" : "hidden"
        )}
      >
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className="w-full"
            onClick={() => setIsMenuOpen(false)}
          >
            <Button
              variant={pathname === item.href ? "secondary" : "ghost"}
              className={cn(
                "rounded-md w-full justify-start",
                pathname === item.href && "text-[#5a67d8]"
              )}
            >
              {item.name}
              {(item as any).isBeta && (
                <span className="ml-2 bg-yellow-200 text-yellow-800 text-xs font-semibold px-2 py-0.5 rounded-full">
                  Beta
                </span>
              )}
              {item.count !== undefined && item.count !== null && (
                <span className="ml-2 bg-blue-500 text-white text-xs font-semibold px-2 py-1 rounded-full">
                  {item.count}명
                </span>
              )}
            </Button>
          </Link>
        ))}
      </nav>
    </header>
  );
};
