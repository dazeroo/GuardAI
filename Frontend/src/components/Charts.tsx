import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Checkbox } from "./ui/checkbox";
import { ScrollArea } from "./ui/scroll-area";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Copy, Check, Upload, ChevronDown, ChevronRight, Loader2, X, AlertCircle, CheckCircle, Clock } from "lucide-react";


// 기술 컨설팅 - DB 관련 데이터
const dbItems = [
  { 
    id: 1, 
    name: "DBMS 설정 중 일정 횟수의 로그인 실패 시 계정 잠금 정책에 대한 설정이 되어 있는지 점검", 
    vulnerable: false
  },
  { 
    id: 2, 
    name: "데이터베이스 접근 시 사용자 인증 및 권한 관리가 적절히 설정되어 있는지 점검", 
    vulnerable: true
  },
  { 
    id: 3, 
    name: "데이터베이스 중요 데이터에 대한 암호화 적용 여부 및 키 관리 체계 점검", 
    vulnerable: false
  },
  { 
    id: 4, 
    name: "데이터베이스 감사 로그 설정 및 보관 정책이 적절히 운영되고 있는지 점검", 
    vulnerable: true
  }
];

// 기술 컨설팅 - WEB 관련 데이터
const webItems = [
  { 
    id: 1, 
    name: "웹 애플리케이션의 입력값 검증 및 SQL 인젝션 방어 대책이 적용되어 있는지 점검", 
    vulnerable: true
  },
  { 
    id: 2, 
    name: "웹 서버 및 애플리케이션 서버의 보안 헤더 설정 및 취약점 패치 현황 점검", 
    vulnerable: false
  },
  { 
    id: 3, 
    name: "세션 관리 및 쿠키 보안 설정이 적절히 구현되어 있는지 점검", 
    vulnerable: true
  },
  { 
    id: 4, 
    name: "웹 애플리케이션의 파일 업로드 기능에 대한 보안 통제 방안 점검", 
    vulnerable: false
  }
];

// 관리 컨설팅 데이터 (세부 항목 포함)
const managementItems = [
  { 
    id: 1, 
    name: "프로젝트 일정 관리", 
    status1: true, 
    status2: false,
    subItems: [
      { id: "1-1", name: "일정 계획 수립", status1: true, status2: false },
      { id: "1-2", name: "마일스톤 관리", status1: false, status2: true },
      { id: "1-3", name: "진행률 추적", status1: true, status2: false }
    ]
  },
  { 
    id: 2, 
    name: "조직 구조 개편", 
    status1: false, 
    status2: true,
    subItems: [
      { id: "2-1", name: "조직도 분석", status1: false, status2: true },
      { id: "2-2", name: "역할 및 책임 정의", status1: true, status2: false },
      { id: "2-3", name: "보고 체계 수립", status1: false, status2: true }
    ]
  },
  { 
    id: 3, 
    name: "전략 기획 수립", 
    status1: true, 
    status2: true,
    subItems: [
      { id: "3-1", name: "비전 및 미션 수립", status1: true, status2: true },
      { id: "3-2", name: "SWOT 분석", status1: false, status2: true },
      { id: "3-3", name: "전략 로드맵", status1: true, status2: false }
    ]
  },
  { 
    id: 4, 
    name: "품질 관리 체계", 
    status1: false, 
    status2: false,
    subItems: [
      { id: "4-1", name: "품질 기준 정의", status1: false, status2: false },
      { id: "4-2", name: "검수 프로세스", status1: true, status2: false },
      { id: "4-3", name: "개선 방안 수립", status1: false, status2: true }
    ]
  },
  { 
    id: 5, 
    name: "리스크 평가 및 관리", 
    status1: true, 
    status2: false,
    subItems: [
      { id: "5-1", name: "리스크 식별", status1: true, status2: false },
      { id: "5-2", name: "영향도 분석", status1: false, status2: true },
      { id: "5-3", name: "대응 전략 수립", status1: true, status2: false }
    ]
  }
];

// AI 섹션 샘플 데이터
const aiSampleTexts = {
  threatAnalysis: `현재 시스템에서 발견된 취약점들을 기반으로 다음과 같은 추가 위협이 예측됩니다:

1. SQL 인젝션 공격을 통한 데이터베이스 침해
2. 웹 애플리케이션 입력값 검증 우회를 통한 악성 코드 삽입
3. 세션 하이재킹을 통한 사용자 계정 탈취
4. 파일 업로드 취약점을 악용한 웹셸 설치

이러한 위협들은 현재 발견된 취약점들과 연계되어 더 큰 보안 위험을 초래할 수 있습니다.`,
  
  yaraRule: `rule Malicious_WebShell_Detection
{
    meta:
        description = "Detects potential web shell uploads"
        author = "Gaurd AI Security Team"
        date = "2024-01-15"
        version = "1.0"
        
    strings:
        $php_exec = "exec(" nocase
        $php_system = "system(" nocase
        $php_shell = "shell_exec(" nocase
        $jsp_runtime = "Runtime.getRuntime()" nocase
        $asp_shell = "WScript.Shell" nocase
        
    condition:
        any of them and filesize < 100KB
}`
};

// 취약점 상세 데이터 (관리 컨설팅용)
const vulnerabilityDetails = [
  {
    id: 1,
    vulnerability: "일정 계획 수립이 미흡함",
    countermeasure: "체계적인 일정 계획 수립 방법론 도입 및 정기적인 검토 체계 구축",
    certification: "ISMS"
  },
  {
    id: 2,
    vulnerability: "마일스톤 관리 체계 부족",
    countermeasure: "주요 마일스톤 설정 및 진행 상황 모니터링 시스템 구축",
    certification: "ISMS"
  },
  {
    id: 3,
    vulnerability: "조직도 분석 절차 미비",
    countermeasure: "조직 구조 분석을 위한 표준화된 절차 및 도구 도입",
    certification: "-"
  },
  {
    id: 4,
    vulnerability: "SWOT 분석 방법론 부재",
    countermeasure: "전략적 SWOT 분석 프레임워크 구축 및 정기적 업데이트 체계 마련",
    certification: "ISMS"
  },
  {
    id: 5,
    vulnerability: "품질 기준 정의 부족",
    countermeasure: "명확한 품질 기준 및 측정 지표 정의, 품질 관리 매뉴얼 작성",
    certification: "-"
  },
  {
    id: 6,
    vulnerability: "리스크 대응 전략 미흡",
    countermeasure: "리스크 평가 매트릭스 구축 및 단계별 대응 전략 수립",
    certification: "ISMS"
  }
];

export function Charts() {
  const [siteUrl, setSiteUrl] = useState("");
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [openItems, setOpenItems] = useState<number[]>([]);
  const [showTechSummaryAI, setShowTechSummaryAI] = useState(false);
  const [showTechDiagnosisAI, setShowTechDiagnosisAI] = useState(false);
  const [showMgmtSummaryAI, setShowMgmtSummaryAI] = useState(false);

  const [loadingSection, setLoadingSection] = useState<string | null>(null);
  const [showResultPopup, setShowResultPopup] = useState(false);
  const [showLoadPopup, setShowLoadPopup] = useState(false);
  const [showVulnerabilityModal, setShowVulnerabilityModal] = useState(false);
  const [showNotificationModal, setShowNotificationModal] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");
  const [diagnosisResult, setDiagnosisResult] = useState<{
    section: string;
    vulnerabilities: number;
    total: number;
    status: 'success' | 'warning' | 'error';
  } | null>(null);

  const showNotification = (message: string) => {
    setNotificationMessage(message);
    setShowNotificationModal(true);
    setTimeout(() => setShowNotificationModal(false), 2000);
  };

  const handleCopyText = async (text: string, fieldName: string) => {
    if (!text || text.trim() === "") {
      showNotification("복사할 내용이 없습니다.");
      return;
    }

    // 복사 성공 표시를 먼저 보여줌
    setCopiedField(fieldName);
    
    try {
      // 가장 단순한 방법부터 시도
      await navigator.clipboard.writeText(text);
      showNotification("복사되었습니다!");
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      // 폴백: execCommand 사용
      try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'absolute';
        textArea.style.left = '-9999px';
        textArea.style.top = '0';
        document.body.appendChild(textArea);
        
        textArea.select();
        textArea.setSelectionRange(0, 99999);
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          showNotification("복사되었습니다!");
          setTimeout(() => setCopiedField(null), 2000);
        } else {
          throw new Error('execCommand failed');
        }
      } catch (fallbackErr) {
        // 복사 실패 시 알림만 표시
        setCopiedField(null);
        showNotification("복사에 실패했습니다. 브라우저가 복사를 지원하지 않습니다.");
      }
    }
  };

  const handleSiteInput = () => {
    if (siteUrl.trim() === "") {
      showNotification("사이트 URL을 입력해주세요.");
      return;
    }
    showNotification("사이트가 입력되었습니다.");
  };

  const handleLoadDiagnosticItems = () => {
    if (siteUrl.trim() === "") {
      showNotification("사이트 URL을 먼저 입력해주세요.");
      return;
    }
    setShowLoadPopup(true);
  };



  const handleDiagnose = async (section: string) => {
    setLoadingSection(section);
    showNotification("진단을 시작합니다...");
    
    // 진단 시뮬레이션 (2-4초)
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 2000));
    
    // 무작위 진단 결과 생성
    let total, vulnerabilities;
    if (section.includes("기술 컨설팅")) {
      total = dbItems.length + webItems.length;
      vulnerabilities = Math.floor(Math.random() * total * 0.6) + 1;
    } else {
      total = managementItems.length + managementItems.reduce((acc, item) => acc + item.subItems.length, 0);
      vulnerabilities = Math.floor(Math.random() * total * 0.4) + 1;
    }
    
    const percentage = (vulnerabilities / total) * 100;
    const status = percentage > 50 ? 'error' : percentage > 25 ? 'warning' : 'success';
    
    setDiagnosisResult({
      section,
      vulnerabilities,
      total,
      status
    });
    
    setLoadingSection(null);
    setShowResultPopup(true);
    showNotification("진단이 완료되었습니다!");
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      showNotification(`${file.name} 파일이 업로드되었습니다!`);
    }
  };

  const toggleItem = (itemId: number) => {
    setOpenItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  return (
    <div className="space-y-6 relative">
      {/* 상단 섹션: 기술 컨설팅과 관리 컨설팅 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 기술 컨설팅 섹션 */}
        <div className="h-[800px] flex flex-col">
          <h2 className="mb-2">기술 컨설팅</h2>
          
          {/* 메인 탭 구조 */}
          <div className="flex-1 min-h-0 overflow-hidden">
            <Tabs defaultValue="summary" className="w-full h-full flex flex-col">
              <TabsList className="grid grid-cols-2 flex-shrink-0 rounded-b-none border-b-0">
                <TabsTrigger value="summary" className="rounded-b-none data-[state=active]:border-b-0">보고서 요약</TabsTrigger>
                <TabsTrigger value="diagnosis" className="rounded-b-none data-[state=active]:border-b-0">자동 진단</TabsTrigger>
              </TabsList>
              
              <TabsContent value="summary" className="flex-1 min-h-0 overflow-hidden mt-0">
                <Card className="h-full flex flex-col rounded-t-none border-t-0">
                  <CardContent className="flex-1 flex flex-col min-h-0 p-6 space-y-4">
                    {/* 보고서 파일 업로드 */}
                    <div className="space-y-3 flex-shrink-0">
                      <div className="flex items-center gap-2">
                        <Input 
                          placeholder="보고서 파일 선택 (Excel)"
                          readOnly
                          value={uploadedFile ? uploadedFile.name : ""}
                          className="flex-1"
                        />
                        <Button variant="outline" className="gap-2" asChild>
                          <label>
                            보고서 업로드
                            <input
                              type="file"
                              accept=".xlsx,.xls"
                              onChange={handleFileUpload}
                              className="hidden"
                            />
                          </label>
                        </Button>
                      </div>
                    </div>
                    
                    {/* 진단옵션 탭 */}
                    <div className="flex-1 min-h-0 overflow-hidden">
                      <Tabs defaultValue="db-summary" className="w-full h-full flex flex-col">
                        <TabsList className="grid grid-cols-2 flex-shrink-0">
                          <TabsTrigger value="db-summary">DB</TabsTrigger>
                          <TabsTrigger value="web-summary">WEB</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="db-summary" className="flex-1 min-h-0 overflow-hidden">
                          <ScrollArea className="h-full">
                            <div className="space-y-4 pb-4">
                              <div className="space-y-1">
                                <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted">
                                  <div>항목</div>
                                  <div className="text-center">양호</div>
                                  <div className="text-center">취약</div>
                                  <div className="text-center">인터뷰</div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">DB 접근 제어</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">DB 권한 관리</div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">데이터 암호화</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">DB 감사 로그</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                              </div>
                            </div>
                          </ScrollArea>
                        </TabsContent>
                        
                        <TabsContent value="web-summary" className="flex-1 min-h-0 overflow-hidden">
                          <ScrollArea className="h-full">
                            <div className="space-y-4 pb-4">
                              <div className="space-y-1">
                                <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted">
                                  <div>항목</div>
                                  <div className="text-center">양호</div>
                                  <div className="text-center">취약</div>
                                  <div className="text-center">인터뷰</div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">웹 입력값 검증</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">보안 헤더 설정</div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">세션 관리</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">파일 업로드 보안</div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                              </div>
                            </div>
                          </ScrollArea>
                        </TabsContent>
                      </Tabs>
                    </div>
                    
                    {/* AI 추가진단 섹션 */}
                    <div className="border-t pt-4 flex-shrink-0">
                      <div className="flex items-center justify-between mb-4">
                        <h3>AI 추가진단</h3>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => {
                              setShowTechSummaryAI(true);
                              showNotification("생성이 완료되었습니다.");
                            }}
                            className="gap-2"
                          >
                            생성
                          </Button>
                        </div>
                      </div>
                      {showTechSummaryAI && (
                        <div className="grid grid-cols-1 gap-4">
                          {/* 1. 추가 위협 예측 */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4>1. 추가 위협 예측</h4>
                            </div>
                            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px]">
                              {aiSampleTexts.threatAnalysis}
                            </div>
                          </div>

                          {/* 2. 추가 위협에 대한 YARA Rule 생성 */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4>2. 추가 위협에 대한 YARA Rule 생성</h4>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyText(aiSampleTexts.yaraRule, 'summary-yaraRule')}
                                className="gap-1 h-8 px-2"
                              >
                                {copiedField === 'summary-yaraRule' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                                복사
                              </Button>
                            </div>
                            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px]">
                              {aiSampleTexts.yaraRule}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="diagnosis" className="flex-1 min-h-0 overflow-hidden mt-0">
                <Card className="h-full flex flex-col rounded-t-none border-t-0">
                  <CardContent className="flex-1 flex flex-col min-h-0 p-6 space-y-4">

                    
                    <div className="flex-1 min-h-0 overflow-hidden">
                      <Tabs defaultValue="db" className="w-full h-full flex flex-col">
                        <TabsList className="grid grid-cols-2 flex-shrink-0 mb-4">
                          <TabsTrigger value="db">DB</TabsTrigger>
                          <TabsTrigger value="web">WEB</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="db" className="flex-1 min-h-0 overflow-hidden mt-0">
                          <div className="h-full flex flex-col">
                            {/* DB 탭 진단 버튼 */}
                            <div className="flex justify-end mb-4 flex-shrink-0">
                              <Button 
                                onClick={() => handleDiagnose("기술 컨설팅")}
                                disabled={loadingSection === "기술 컨설팅"}
                                className="gap-2"
                              >
                                {loadingSection === "기술 컨설팅" && <Loader2 className="h-4 w-4 animate-spin" />}
                                {loadingSection === "기술 컨설팅" ? "진단 중..." : "진단"}
                              </Button>
                            </div>
                            
                            <ScrollArea className="h-full flex-1">
                              <div className="space-y-4 pb-4">
                                {/* DB 항목들 */}
                                <div className="space-y-1">
                                  <div className="grid grid-cols-2 gap-2 p-2 border-b font-medium bg-muted">
                                    <div>항목</div>
                                    <div className="text-center">취약</div>
                                  </div>
                                  {dbItems.map((item) => (
                                    <div key={item.id} className="grid grid-cols-2 gap-2 p-2 border-b hover:bg-muted/50">
                                      <div className="text-sm">
                                        {item.name}
                                      </div>
                                      <div className="flex justify-center">
                                        <Checkbox defaultChecked={item.vulnerable} />
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </ScrollArea>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="web" className="flex-1 min-h-0 overflow-hidden mt-0">
                          <div className="h-full flex flex-col space-y-4">
                            {/* 사이트 입력 필드와 WEB 탭 진단 버튼 */}
                            <div className="space-y-2 flex-shrink-0">
                              <label htmlFor="site-url-web" className="text-sm">사이트 URL:</label>
                              <div className="flex gap-2">
                                <Input
                                  id="site-url-web"
                                  placeholder="https://example.com"
                                  value={siteUrl}
                                  onChange={(e) => setSiteUrl(e.target.value)}
                                  className="flex-1"
                                />
                                <Button onClick={handleSiteInput} variant="outline">
                                  사이트 입력
                                </Button>
                                <Button onClick={handleLoadDiagnosticItems} variant="outline">
                                  진단항목 불러오기
                                </Button>
                                <Button 
                                  onClick={() => handleDiagnose("기술 컨설팅")}
                                  disabled={loadingSection === "기술 컨설팅"}
                                  className="gap-2 flex-shrink-0"
                                >
                                  {loadingSection === "기술 컨설팅" && <Loader2 className="h-4 w-4 animate-spin" />}
                                  {loadingSection === "기술 컨설팅" ? "진단 중..." : "진단"}
                                </Button>
                              </div>
                            </div>
                            
                            <ScrollArea className="h-full flex-1">
                              <div className="space-y-4 pb-4">
                                {/* WEB 항목들 */}
                                <div className="space-y-1">
                                  <div className="grid grid-cols-2 gap-2 p-2 border-b font-medium bg-muted">
                                    <div>항목</div>
                                    <div className="text-center">취약</div>
                                  </div>
                                  {webItems.map((item) => (
                                    <div key={item.id} className="grid grid-cols-2 gap-2 p-2 border-b hover:bg-muted/50">
                                      <div className="text-sm">
                                        {item.name}
                                      </div>
                                      <div className="flex justify-center">
                                        <Checkbox defaultChecked={item.vulnerable} />
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </ScrollArea>
                          </div>
                        </TabsContent>
                      </Tabs>
                    </div>
                    
                    {/* AI 추가진단 섹션 */}
                    <div className="border-t pt-4 flex-shrink-0">
                      <div className="flex items-center justify-between mb-4">
                        <h3>AI 추가진단</h3>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => {
                              setShowTechDiagnosisAI(true);
                              showNotification("생성이 완료되었습니다.");
                            }}
                            className="gap-2"
                          >
                            생성
                          </Button>
                        </div>
                      </div>
                      {showTechDiagnosisAI && (
                        <div className="grid grid-cols-1 gap-4">
                          {/* 1. 추가 위협 예측 */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4>1. 추가 위협 예측</h4>
                            </div>
                            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px]">
                              {aiSampleTexts.threatAnalysis}
                            </div>
                          </div>

                          {/* 2. 추가 위협에 대한 YARA Rule 생성 */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4>2. 추가 위협에 대한 YARA Rule 생성</h4>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyText(aiSampleTexts.yaraRule, 'yaraRule')}
                                className="gap-1 h-8 px-2"
                              >
                                {copiedField === 'yaraRule' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                                복사
                              </Button>
                            </div>
                            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px]">
                              {aiSampleTexts.yaraRule}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* 관리 컨설팅 섹션 */}
        <div className="h-[800px] flex flex-col">
          <h2 className="mb-2">관리 컨설팅</h2>
          
          {/* 메인 탭 구조 */}
          <div className="flex-1 min-h-0 overflow-hidden">
            <Tabs defaultValue="summary" className="w-full h-full flex flex-col">
              <TabsList className="grid grid-cols-2 flex-shrink-0 rounded-b-none border-b-0">
                <TabsTrigger value="summary" className="rounded-b-none data-[state=active]:border-b-0">보고서 요약</TabsTrigger>
                <TabsTrigger value="diagnosis" className="rounded-b-none data-[state=active]:border-b-0">자동 진단</TabsTrigger>
              </TabsList>
              
              <TabsContent value="summary" className="flex-1 min-h-0 overflow-hidden mt-0">
                <Card className="h-full flex flex-col rounded-t-none border-t-0">
                  <CardContent className="flex-1 flex flex-col min-h-0 p-6 space-y-4">
                    {/* ISMS-P 현황 분석 보고서 업로드 */}
                    <div className="space-y-3 flex-shrink-0">
                      <div className="flex items-center gap-2">
                        <Input 
                          placeholder="ISMS-P 현황 분석 보고서 업로드 (Excel)"
                          readOnly
                          value={uploadedFile ? uploadedFile.name : ""}
                          className="flex-1"
                        />
                        <Button variant="outline" className="gap-2" asChild>
                          <label>
                            업로드
                            <input
                              type="file"
                              accept=".xlsx,.xls"
                              onChange={handleFileUpload}
                              className="hidden"
                            />
                          </label>
                        </Button>
                      </div>
                    </div>
                    
                    {/* 진단옵션 탭 */}
                    <div className="flex-1 min-h-0 overflow-hidden">
                      <Tabs defaultValue="isms-summary" className="w-full h-full flex flex-col">
                        <TabsList className="grid grid-cols-2 flex-shrink-0">
                          <TabsTrigger value="isms-summary">ISMS</TabsTrigger>
                          <TabsTrigger value="isms-p-summary">ISMS-P</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="isms-summary" className="flex-1 min-h-0 overflow-hidden">
                          <ScrollArea className="h-full">
                            <div className="space-y-4 pb-4">
                              <div className="space-y-1">
                                <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted">
                                  <div>항목</div>
                                  <div className="text-center">양호</div>
                                  <div className="text-center">취약</div>
                                  <div className="text-center">위험</div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">정보보안 정책</div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">접근통제 관리</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">암호화 적용</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">보안사고 대응</div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                              </div>
                            </div>
                          </ScrollArea>
                        </TabsContent>
                        
                        <TabsContent value="isms-p-summary" className="flex-1 min-h-0 overflow-hidden">
                          <ScrollArea className="h-full">
                            <div className="space-y-4 pb-4">
                              <div className="space-y-1">
                                <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted">
                                  <div>항목</div>
                                  <div className="text-center">양호</div>
                                  <div className="text-center">취약</div>
                                  <div className="text-center">위험</div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">개인정보 보호정책</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">개인정보 처리 현황</div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">개인정보 파기</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                </div>
                                <div className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                                  <div className="text-sm">정보주체 권리보장</div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                  <div className="flex justify-center"><Checkbox defaultChecked /></div>
                                  <div className="flex justify-center"><Checkbox /></div>
                                </div>
                              </div>
                            </div>
                          </ScrollArea>
                        </TabsContent>
                      </Tabs>
                    </div>
                    
                    {/* AI 추가진단 섹션 */}
                    <div className="border-t pt-4 flex-shrink-0">
                      <div className="flex items-center justify-between mb-4">
                        <h3>AI 추가진단</h3>
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => {
                              setShowMgmtSummaryAI(true);
                              showNotification("생성이 완료되었습니다.");
                            }}
                            className="gap-2"
                          >
                            생성
                          </Button>
                        </div>
                      </div>
                      {showMgmtSummaryAI && (
                        <div className="grid grid-cols-1 gap-4">
                          {/* 1. 추가 위협 예측 */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4>1. 추가 위협 예측</h4>
                            </div>
                            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px]">
                              {aiSampleTexts.threatAnalysis}
                            </div>
                          </div>

                          {/* 2. 추가 위협에 대한 YARA Rule 생성 */}
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4>2. 추가 위협에 대한 YARA Rule 생성</h4>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyText(aiSampleTexts.yaraRule, 'mgmt-summary-yaraRule')}
                                className="gap-1 h-8 px-2"
                              >
                                {copiedField === 'mgmt-summary-yaraRule' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                                복사
                              </Button>
                            </div>
                            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px]">
                              {aiSampleTexts.yaraRule}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="diagnosis" className="flex-1 min-h-0 overflow-hidden mt-0">
                <Card className="h-full flex flex-col rounded-t-none border-t-0">
                  <CardContent className="flex-1 flex flex-col min-h-0 p-6">
                    <div className="flex-1 min-h-0 overflow-hidden">
                      <ScrollArea className="h-full">
                        <div className="space-y-1">
                          <div className="grid grid-cols-3 gap-2 p-2 border-b font-medium bg-muted">
                            <div>항목</div>
                            <div className="text-center">ISMS</div>
                            <div className="text-center">ISMS-P</div>
                          </div>
                          {managementItems.map((item) => (
                            <div key={item.id} className="space-y-1">
                              <Collapsible
                                open={openItems.includes(item.id)}
                                onOpenChange={() => toggleItem(item.id)}
                              >
                                <div className="grid grid-cols-3 gap-2 p-2 border-b hover:bg-muted/50">
                                  <CollapsibleTrigger asChild>
                                    <div className="flex items-center gap-2 text-sm cursor-pointer">
                                      {openItems.includes(item.id) ? (
                                        <ChevronDown className="h-4 w-4" />
                                      ) : (
                                        <ChevronRight className="h-4 w-4" />
                                      )}
                                      {item.name}
                                    </div>
                                  </CollapsibleTrigger>
                                  <div></div>
                                  <div></div>
                                </div>
                                <CollapsibleContent className="space-y-1">
                                  {item.subItems.map((subItem) => (
                                    <div key={subItem.id} className="grid grid-cols-3 gap-2 p-2 border-b hover:bg-muted/30 bg-muted/10">
                                      <div className="text-sm text-muted-foreground pl-8">
                                        {subItem.name}
                                      </div>
                                      <div className="flex justify-center">
                                        <Checkbox defaultChecked={subItem.status1} />
                                      </div>
                                      <div className="flex justify-center">
                                        <Checkbox defaultChecked={subItem.status2} />
                                      </div>
                                    </div>
                                  ))}
                                </CollapsibleContent>
                              </Collapsible>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </div>
                    <div className="flex justify-center pt-4 flex-shrink-0">
                      <Button 
                        onClick={() => handleDiagnose("관리 컨설팅")}
                        disabled={loadingSection === "관리 컨설팅"}
                        className="gap-2"
                      >
                        {loadingSection === "관리 컨설팅" && <Loader2 className="h-4 w-4 animate-spin" />}
                        {loadingSection === "관리 컨설팅" ? "진단 중..." : "진단"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>

      {/* 진단 결과 팝업 - 화면 가운데 */}
      {showResultPopup && diagnosisResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* 배경 오버레이 */}
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowResultPopup(false)} />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {diagnosisResult.status === 'success' && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {diagnosisResult.status === 'warning' && <AlertCircle className="h-5 w-5 text-yellow-500" />}
                  {diagnosisResult.status === 'error' && <AlertCircle className="h-5 w-5 text-red-500" />}
                  <CardTitle className="text-base">진단 완료</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowResultPopup(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-muted-foreground">진단 섹션</div>
                  <div className="font-medium">{diagnosisResult.section}</div>
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <div className="text-sm text-muted-foreground">취약점</div>
                    <div 
                      className="text-lg font-medium text-red-600 cursor-pointer hover:underline"
                      onClick={() => {
                        setShowVulnerabilityModal(true);
                        setShowResultPopup(false);
                      }}
                    >
                      {diagnosisResult.vulnerabilities}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">전체 항목</div>
                    <div className="text-lg font-medium">{diagnosisResult.total}</div>
                  </div>
                </div>
                
                <div>
                  <div className="text-sm text-muted-foreground mb-1">위험도</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        diagnosisResult.status === 'success' ? 'bg-green-500' :
                        diagnosisResult.status === 'warning' ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${Math.min((diagnosisResult.vulnerabilities / diagnosisResult.total) * 100, 100)}%` }}
                    />
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {Math.round((diagnosisResult.vulnerabilities / diagnosisResult.total) * 100)}% 취약점 발견
                  </div>
                </div>

                <div className="pt-2 border-t">
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    방금 전
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 진단항목 불러오기 완료 팝업 - 화면 가운데 */}
      {showLoadPopup && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* 배경 오버레이 */}
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowLoadPopup(false)} />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <CardTitle className="text-base">진단항목 불러오기 완료</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowLoadPopup(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-muted-foreground">상태</div>
                  <div className="font-medium text-green-600">진단항목을 불러왔습니다.</div>
                </div>
                
                <div>
                  <div className="text-sm text-muted-foreground">사이트 URL</div>
                  <div className="font-medium text-sm break-all">{siteUrl}</div>
                </div>

                <div className="pt-2 border-t">
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    방금 전
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 취약점 상세 모달 - 화면 가운데 */}
      {showVulnerabilityModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* 배경 오버레이 */}
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowVulnerabilityModal(false)} />
          <Card className="relative w-full max-w-[600px] max-h-[80vh] shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300 flex flex-col">
            <CardHeader className="pb-3 flex-shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  <CardTitle className="text-base">취약점 상세 정보</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowVulnerabilityModal(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0 flex-1 flex flex-col min-h-0">
              <div className="flex flex-col h-full space-y-4">
                <div className="flex-shrink-0">
                  <div className="text-sm text-muted-foreground">관리 컨설팅 진단 결과</div>
                  <div className="font-medium">발견된 취약점 및 대응방안</div>
                </div>
                
                <div className="border rounded-lg overflow-hidden">
                  <div className="grid grid-cols-3 gap-0 bg-muted/50 border-b">
                    <div className="p-3 border-r font-medium">취약점</div>
                    <div className="p-3 border-r font-medium">대응방안</div>
                    <div className="p-3 font-medium text-center">세부인증</div>
                  </div>
                  <ScrollArea className="max-h-[300px]">
                    {vulnerabilityDetails.slice(0, diagnosisResult?.vulnerabilities || 6).map((item, index) => (
                      <div key={item.id} className={`grid grid-cols-3 gap-0 border-b last:border-b-0 ${index % 2 === 0 ? 'bg-white' : 'bg-muted/20'}`}>
                        <div className="p-3 border-r text-sm">
                          {item.vulnerability}
                        </div>
                        <div className="p-3 border-r text-sm">
                          {item.countermeasure}
                        </div>
                        <div className="p-3 text-sm text-center">
                          {item.certification}
                        </div>
                      </div>
                    ))}
                  </ScrollArea>
                </div>

                <div className="pt-2 border-t flex-shrink-0">
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    방금 전
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 알림 모달 - 화면 가운데 */}
      {showNotificationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* 배경 오버���이 */}
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowNotificationModal(false)} />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <CardTitle className="text-base">알림</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowNotificationModal(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="font-medium">{notificationMessage}</div>
                </div>

                <div className="pt-2 border-t">
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    방금 전
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}