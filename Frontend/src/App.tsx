import { Toaster } from "./components/ui/sonner";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./components/ui/tooltip";
import { Info } from "lucide-react";
// 새로 만든(또는 이미 만든) 패널 컴포넌트 불러오기
import TechConsultingPanel from "./components/ui/TechConsultingPanel";
import MgmtConsultingPanel from "./components/ui/MgmtConsultingPanel";

export default function App() {
  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-full mx-auto">
          {/* 헤더(그대로 유지) */}
          <div className="mb-8">
            <h1 className="mb-2">Gaurd AI 로고 | AI 기반 보안 컨설팅 및 위협 탐지</h1>
            <p className="text-muted-foreground">
              Gaurd AI 통합 컨설팅 보고서는 크게 기술 컨설팅 서비스와 관리 컨설팅 서비스가 있습니다.
              <br /><br />
              각 서비스에서는 보고서 요약 기능과 자동 진단 기능을 제공하고 있습니다.
            </p>
          </div>

          {/* 본문: 2단 그리드 레이아웃 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 왼쪽: 기술 컨설팅 */}
            <TechConsultingPanel />

            {/* 오른쪽: 관리 컨설팅 */}
            <MgmtConsultingPanel />
          </div>
        </div>

        <Toaster />
      </div>
    </TooltipProvider>
  );
}