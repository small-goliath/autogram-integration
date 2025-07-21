import SnsRaiseAICommentProducer from '@/components/sns-raise-ai-comment-producer';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: '[AI] 자동 댓글 달기 신청',
  description: 'AI를 통해 주기적으로 신규 피드에 댓글과 좋아요를 달 수 있습니다.',
};

export default function SnsRaiseAICommentProducerPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">AI 자동 댓글 달기 신청</h1>
      <div className="bg-card p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-2xl font-semibold text-primary mb-4">AI 자동 댓글 기능이란?</h2>
        <p className="text-muted-foreground mb-4">
          AI 자동 댓글 기능은 인스타그램 신규 피드에 AI가 자동으로 댓글을 달고 좋아요를 눌러주는 서비스입니다.
          이 기능을 통해 다른 사용자들의 피드에 자동으로 상호작용하여, 본인의 계정 활동성을 높이고 더 많은 사용자에게 노출될 기회를 얻을 수 있습니다.
        </p>
        <h2 className="text-2xl font-semibold text-primary mb-4">이점</h2>
        <ul className="list-disc list-inside text-muted-foreground space-y-2">
          <li><span className="font-medium text-foreground">계정 활성화:</span> 주기적인 댓글과 좋아요로 계정의 활동 지수를 높여 인스타그램 알고리즘에 긍정적인 영향을 줍니다.</li>
          <li><span className="font-medium text-foreground">노출 증대:</span> 활발한 활동은 탐색 탭 노출 및 팔로워 증가에 기여합니다.</li>
          <li><span className="font-medium text-foreground">시간 절약:</span> 수동으로 댓글을 달고 좋아요를 누르는 시간을 절약하여 콘텐츠 제작에 집중할 수 있습니다.</li>
          <li><span className="font-medium text-foreground">자연스러운 상호작용:</span> AI가 생성하는 자연스러운 댓글로 실제 사용자들과의 상호작용을 유도합니다.</li>
        </ul>
        <div className="mt-6 p-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700">
          <p className="font-bold">중요: 신청 후 <a href="https://instagram.com/gangggi_e_you" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">@gangggi_e_you</a> 또는 <a href="https://instagram.com/doto.ri_" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">@doto.ri_</a>에게 승인 받으셔야합니다.</p>
        </div>
      </div>
      <SnsRaiseAICommentProducer />
    </div>
  );
}

