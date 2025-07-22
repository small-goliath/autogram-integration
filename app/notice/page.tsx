import { NextPage } from 'next';
import Image from 'next/image';

const NoticePage: NextPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center mb-6">☆ 공지 확인 바랍니다 ☆</h1>

        <section className="mb-6 text-center">
          <h2 className="text-2xl font-semibold mb-3">참여하기</h2>
          <p className="mb-4">
            <a
              href="https://open.kakao.com/o/ggp7Gqsh"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:text-blue-700 underline text-lg"
            >
              카카오톡 오픈채팅 참여 링크
            </a>
          </p>
          <div className="flex justify-center">
            <Image
              src="/SNS_raise_QR.png"
              alt="카카오톡 오픈채팅 QR 코드"
              width={200}
              height={200}
              className="rounded-lg"
            />
          </div>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">닉네임 통일</h2>
          <p className="text-lg">인스타: 실명 @인스타아이디</p>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">광고/상업글</h2>
          <p className="mb-2">
            광고/상업글은 방장 개인톡으로 문의 후 허락받으시기 바랍니다. 문의 없는 상업 광고 글과 비속어 사용, 어그로는 강퇴 대상입니다.
          </p>
          <p className="font-semibold">주로 아래 내용 승인:</p>
          <ul className="list-disc list-inside ml-4">
            <li>협업 콘텐츠 생성</li>
            <li>광고 제의</li>
            <li>팀 단위 활동 혹은 혜택 쉐어</li>
          </ul>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">광고비 공유</h2>
          <p className="mb-2">&quot;이 금액이 잘받는 걸까요?&quot; 와 같은 질문은 금지합니다.</p>
          <p>릴스/콘텐츠 퀄리티/팔로워 수 등 다양한 요건이 반영되는 조건입니다. 일감을 나눠주시는 건 괜찮으나 분란을 일으키진 말아주세요.</p>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">SNS 교육자료 공유</h2>
          <p>우리의 성장을 위한 자료 등은 언제든 편하게 던져주세요. 다만 &quot;유료강의 열렸습니다&quot; 등의 영리활동은 금합니다.</p>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">친목</h2>
          <p>불필요한 친목 권장합니다ㅋㅋ 인맥 늘려나가는 방입니다. 단, 너무 사적인 대화는 다른방을 뚫어서 하는 것도 권장합니다.</p>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">글 모아쓰기</h2>
          <p>글 모아쓰기 필수! 연속 메세지는 자제해주세요. 한 메세지에 하고자하는 내용을 최대한 담아주세요!</p>
        </section>

        <section className="mb-6 p-4 border-l-4 border-red-500 bg-red-50">
          <h2 className="text-2xl font-semibold mb-3 text-red-800">(중요) 기본 매너</h2>
          <p className="mb-2">
            여러분, 우린 다 큰 성인입니다. 본인의 의견을 너무 내세울 필요도 없고, 남이 맘에 안든다고 공격할 필요도 없습니다. 그리고 자신의 위치나 능력으로 으시댈 필요도 전혀 없습니다. 배려와 매너있는 말투 부탁드립니다.
          </p>
          <p>
            매력적인 남녀분들이 모여 있기에 사적인 접근은 가급적 금해주세요. 성인남녀의 만남에 있어서 제한할 생각은 없습니다. 다만 과도한 관심으로 인하여 민원 발생시 바로 강퇴시키겠습니다.
          </p>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">품앗이 규칙</h2>
          <p className="mb-2">일주일의 기준은 <span className="font-bold">월요일부터 일요일까지</span>입니다.</p>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>본인 업로드 분에 대한 퀄리티는 알아서</li>
            <li><span className="font-bold text-red-600">2주간 업로드 없을 시 강퇴</span></li>
            <li><span className="font-bold text-red-600">1주간 댓글품앗이 없을 시 강퇴</span></li>
            <li><span className="font-bold text-red-600">허위로 한 척 체크 시 강퇴</span></li>
          </ul>
        </section>
        
        <section className="mb-6">
          <h2 className="text-2xl font-semibold mb-3">댓글 및 참여 규칙</h2>
          <ul className="list-disc list-inside ml-4 space-y-2">
            <li>댓글 퀄리티 체크는 하지 않지만, 성의 없는 이모티콘만 다는 댓글은 지양합니다.</li>
            <li>주제에 맞는 댓글을 달아주세요.</li>
            <li>리스토리 필수 (리스토리 후 삭제/친한친구 해놓고 삭제/카톡 본인에게 보내기 활용 가능)</li>
            <li>팔로우는 자유</li>
            <li>최소 업로드: 주 2회 / 최대 업로드: 주 3회</li>
            <li>초대 불가능</li>
            <li>상업용 계정(ex: 회사계정) 참여 불가</li>
          </ul>
        </section>

        <footer className="text-center mt-8">
          <p className="text-lg font-semibold">모두 자신의 계정에 만족하는 그날까지 화이팅!</p>
        </footer>
      </div>
    </div>
  );
};

export default NoticePage;
