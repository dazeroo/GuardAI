import logo from './assets/logo.png';
import { Toaster } from "./components/ui/sonner";
import { TooltipProvider } from "./components/ui/tooltip";
import TechConsultingPanel from "./components/ui/TechConsultingPanel";
import MgmtConsultingPanel from "./components/ui/MgmtConsultingPanel";

export default function App() {
  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-full mx-auto">
          {/* 헤더 */}
          <div className="mb-8">
            <div className="flex items-center gap-x-4 mb-2">
              <img src={logo} alt="Guard AI 로고" className="h-[130px]" />
              <h1 className="text-[45px] font-bold">[GUARD AI] AI 기반 보안 컨설팅 및 위협 탐지</h1>
            </div>
            <p className="text-muted-foreground mt-7 pl-8">
              Gaurd AI 통합 보안 컨설팅 서비스는 크게 기술 컨설팅 서비스와 관리 컨설팅 서비스가 있습니다.
              <br /> 
              각 서비스에서는 보고서 요약 기능과 자동 진단 기능을 제공하고 있습니다.
            </p>
          </div>

          {/* 본문: 2단 그리드 레이아웃 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TechConsultingPanel />
            <MgmtConsultingPanel />
          </div>
        </div>

        <Toaster />
      </div>
    </TooltipProvider>
  );
}