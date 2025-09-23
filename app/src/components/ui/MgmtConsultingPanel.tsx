import React, { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "./card";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "./tabs";
import { Button } from "./button";
import { Progress } from "./progress";
import { Checkbox } from "./checkbox";
import { ScrollArea } from "./scroll-area";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./collapsible";
import {
  CheckCircle,
  X,
  AlertCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Info,
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip";
import { toast } from "sonner";

// 구분 열 통합 및 진단결과 열 분리 구조
const summaryResults = [
  {
    id: 1,
    division: "ISMS-P", // 통합된 구분 열
    integratedAuth: "1. 관리체계 수립 및 운영", // 통합인증 열
    fields: [
      { name: "1.1 관리체계 기반마련", count: 6, rating: "Y" },
      { name: "1.2 위험관리", count: 4, rating: "P" },
      { name: "1.3 관리체계 운영", count: 3, rating: "N" },
      { name: "1.4 관리체계 점검 및 개선", count: 3, rating: "Y" },
    ],
  },
  {
    id: 2,
    division: "ISMS", // 통합된 구분 열
    integratedAuth: "2. 보호대책 요구사항", // 통합인증 열
    fields: [
      { name: "2.1 정책, 조직, 자산 관리", count: 3, rating: "P" },
      { name: "2.2 인적보안", count: 6, rating: "Y" },
      { name: "2.3 외부자 보안", count: 4, rating: "N" },
      { name: "2.4 물리보안", count: 7, rating: "P" },
      { name: "2.5 인증 및 권한 관리", count: 6, rating: "Y" },
      { name: "2.6 접근통제", count: 7, rating: "N" },
      { name: "2.7 암호화 적용", count: 2, rating: "P" },
      { name: "2.8 정보시스템 도입 및 개발 보안", count: 6, rating: "Y" },
      { name: "2.9 시스템 및 서비스 운영관리", count: 7, rating: "N" },
      { name: "2.10 시스템 및 서비스 보안관리", count: 9, rating: "P" },
      { name: "2.11 사고 예방 및 대응", count: 5, rating: "Y" },
      { name: "2.12 재해복구", count: 2, rating: "N" },
    ],
  },
  {
    id: 3,
    division: "", // 빈 값으로 ISMS와 병합
    integratedAuth: "3. 개인정보 처리단계별 요구사항", // 통합인증 열
    fields: [
      { name: "3.1 개인정보 수집 시 보호조치", count: 7, rating: "P" },
      { name: "3.2 개인정보 보유 및 이용 시 보호조치", count: 5, rating: "Y" },
      { name: "3.3 개인정보 제공 시 보호조치", count: 3, rating: "N" },
      { name: "3.4 개인정보 파기 시 보호조치", count: 4, rating: "P" },
      { name: "3.5 정보주체 권리보호", count: 3, rating: "Y" },
    ],
  },
];

// 취약점 상세 데이터
const vulnerabilityDetails = [
  {
    id: 1,
    vulnerability: "개인정보 수집 절차 미흡",
    countermeasure:
      "개인정보 수집 시 명시적 동의 절차 및 최소 수집 원칙 적용",
  },
  {
    id: 2,
    vulnerability: "개인정보 파기 정책 부재",
    countermeasure:
      "개인정보 보유기간 만료 시 자동 파기 시스템 구축",
  },
  {
    id: 3,
    vulnerability: "정보주체 권리보장 체계 미비",
    countermeasure:
      "개인정보 열람, 정정·삭제 요구 처리 절차 수립",
  },
  {
    id: 4,
    vulnerability: "개인정보 제공 현황 관리 부족",
    countermeasure:
      "제3자 제공 현황 관리 대장 작성 및 정기 점검",
  },
  {
    id: 5,
    vulnerability: "암호화 적용 범위 미흡",
    countermeasure:
      "개인정보 및 중요 데이터 암호화 정책 수립 및 적용",
  },
  {
    id: 6,
    vulnerability: "접근권한 관리 체계 부족",
    countermeasure:
      "사용자별 접근권한 설정 및 정기적 권한 검토 체계 구축",
  },
  {
    id: 7,
    vulnerability: "보안 교육 실시 미흡",
    countermeasure:
      "정기적 보안 교육 계획 수립 및 교육 이수 현황 관리",
  },
  {
    id: 8,
    vulnerability: "물리적 보안 통제 부족",
    countermeasure: "보안구역 설정 및 출입통제 시스템 강화",
  },
];

export default function MgmtConsultingPanel() {
  const [isUploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [summaryGenerated, setSummaryGenerated] =
    useState(false);
  const [diagnosisGenerated, setDiagnosisGenerated] =
    useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(
    null,
  );
  const [diagnosisFile, setDiagnosisFile] =
    useState<File | null>(null);
  const [
    showDiagnosisCompleteModal,
    setShowDiagnosisCompleteModal,
  ] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState({
    title: "",
    message: "",
    type: "info" as "info" | "success" | "error",
  });
  const [openItems, setOpenItems] = useState<number[]>([]);

  const showModalMessage = (
    title: string,
    message: string,
    type: "info" | "success" | "error" = "info",
  ) => {
    setModalContent({ title, message, type });
    setShowModal(true);
    setTimeout(() => setShowModal(false), 2000);
  };

  const toggleItem = (itemId: number) => {
    setOpenItems((prev) =>
      prev.includes(itemId)
        ? prev.filter((id) => id !== itemId)
        : [...prev, itemId],
    );
  };

  const startUpload = async () => {
    setUploading(true);
    setProgress(15);
    showModalMessage(
      "요약 생성",
      "요약 생성을 시작합니다...",
      "info",
    );

    const steps = [35, 55, 80, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setProgress(p);
    }

    setUploading(false);
    setSummaryGenerated(true);
    showModalMessage(
      "요약 완료",
      "요약이 완료되었습니다.",
      "success",
    );
  };

  const startDiagnosis = async () => {
    setUploading(true);
    setProgress(15);
    showModalMessage(
      "자동 진단",
      "자동 진단을 시작합니다...",
      "info",
    );

    const steps = [35, 55, 80, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setProgress(p);
    }

    setUploading(false);
    setDiagnosisGenerated(true);
    setShowDiagnosisCompleteModal(true);
  };

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      showModalMessage(
        "파일 업로드",
        `${file.name} 파일이 업로드되었습니다!`,
        "success",
      );
      await startUpload();
    }
  };

  const handleDiagnosisFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      setDiagnosisFile(file);
      showModalMessage(
        "파일 업로드",
        `${file.name} 파일이 업로드되었습니다!`,
        "success",
      );
      await startDiagnosis();
    }
  };

  const handleDownloadReport = () => {
    const csvData = [
      ["ISMS-P", "ISMS", "통합인증", "분야(인증 개수)", "진단결과"],
      ...summaryResults.flatMap((group, groupIndex) =>
        group.fields.map((field, fieldIndex) => [
          fieldIndex === 0 && group.division === "ISMS-P" ? "○" : "",
          fieldIndex === 0 && group.division === "ISMS" ? "○" : "",
          fieldIndex === 0 ? group.integratedAuth : "",
          `${field.name}(${field.count})`,
          field.rating === "P"
            ? "부분준수"
            : field.rating === "Y"
          
              ? "준수"
              : "미준수",
        ]),
      ),
    ];

    const csvContent = csvData
      .map((row) => row.map((field) => `"${field}"`).join(","))
      .join("\\n");

    const BOM = "\\uFEFF";
    const csvWithBOM = BOM + csvContent;

    const blob = new Blob([csvWithBOM], {
      type: "text/csv;charset=utf-8;",
    });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `Guard_AI_자동진단보고서_${new Date().toISOString().slice(0, 10)}.csv`,
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <Card className="flex flex-col h-full">
        <CardHeader>
          <CardTitle>관리 컨설팅</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          <Tabs
            defaultValue="summary"
            className="flex-1 flex flex-col"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="summary" className="flex items-center gap-2">
                보고서 요약
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button type="button" className="p-0 h-auto bg-transparent border-0 cursor-help">
                      <Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="max-w-xs">진단을 원하시는 기업의 ISMS-P 현황 분석 보고서를 업로드하면 각 진단 항목을 ISMS, ISMS-P의 만족 여부를 확인하고, 취약점과 그 대응 방안을 제시합니다.</p>
                  </TooltipContent>
                </Tooltip>
              </TabsTrigger>
              <TabsTrigger value="auto" className="flex items-center gap-2">
                자동 진단
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button type="button" className="p-0 h-auto bg-transparent border-0 cursor-help">
                      <Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="max-w-xs">진단이 필요한 기업의 내규 지침서를 업로드하면 ISMS, ISMS-P의 항목을 자동으로 진단하고, 취약점과 대응방안을 요약합니다.</p>
                  </TooltipContent>
                </Tooltip>
              </TabsTrigger>
            </TabsList>

            {/* 보고서 요약 */}
            <TabsContent
              value="summary"
              className="flex-1 flex flex-col space-y-4"
            >
              {isUploading ? (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    요약 생성 중…
                  </p>
                  <Progress value={progress} />
                </div>
              ) : !summaryGenerated ? (
                <div className="space-y-4">
                  <div className="text-center py-8 text-muted-foreground">
                    보고서를 업로드하면 자동으로 요약해
                    드립니다.
                  </div>
                  <div className="flex justify-center">
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
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
              ) : null}

              {summaryGenerated && (
                <div className="flex-1 flex flex-col space-y-4">
                  <div className="flex justify-start">
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
                      <label>
                        보고서 재업로드
                        <input
                          type="file"
                          accept=".xlsx,.xls"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                      </label>
                    </Button>
                  </div>

                  {uploadedFile && (
                    <p className="text-sm text-muted-foreground">
                      업로드된 파일: {uploadedFile.name}
                    </p>
                  )}

                  {/* 첨부 이미지와 일치하는 새로운 테이블 구조 */}
                  <div className="flex-1 min-h-0">
                    <div className="border rounded-lg overflow-hidden h-[500px]">
                      <ScrollArea className="h-full w-full">
                        <table className="w-full border-collapse">
                          {/* 테이블 헤더 - 2단계 구조 */}
                          <thead className="sticky top-0 bg-muted/80 backdrop-blur-sm z-10">
                            {/* 첫 번째 헤더 행 */}
                            <tr>
                              <th 
                                colSpan={2}
                                className="p-3 border-r border-b font-medium text-center text-sm min-w-[200px]"
                              >
                                구분
                              </th>
                              <th 
                                rowSpan={2}
                                className="p-3 border-r border-b font-medium text-center text-sm min-w-[200px] align-middle"
                              >
                                통합인증
                              </th>
                              <th 
                                rowSpan={2}
                                className="p-3 border-r border-b font-medium text-center text-sm min-w-[300px] align-middle"
                              >
                                분야(인증 개수)
                              </th>
                              <th 
                                rowSpan={2}
                                className="p-3 border-b font-medium text-center text-sm min-w-[100px] align-middle"
                              >
                                진단결과
                              </th>
                            </tr>
                          </thead>
                          
                          {/* 테이블 내용 */}
                          <tbody className="bg-white">
                            {summaryResults.map((group, groupIndex) => {
                              return (
                                <React.Fragment key={group.id}>
                                  {/* 카테고리 헤더 행 */}
                                  <tr className={`hover:bg-muted/30 border-b`}>
                                    {/* ISMS-P열 */}
                                    <td 
                                      className="p-3 border-r text-center font-medium text-sm">
                                      ISMS-P
                                    </td>
                                    
                                    {/* ISMS열 */}
                                    <td className="p-3 border-r text-center font-medium text-sm">
                                      ISMS
                                    </td>
                                    
                                    {/* 통합인증 열 */}
                                    <td 
                                      rowSpan={group.fields.length + 1}
                                      className="p-3 border-r text-sm font-medium align-top"
                                    >
                                      {group.integratedAuth}
                                    </td>
                                    
                                    {/* 분야(인증 개수) 열 - 빈 칸 */}
                                    <td className="p-3 border-r text-center">
                                    </td>
                                    
                                    {/* 진단결과 열 - 빈 칸 */}
                                    <td className="p-3 text-center">
                                    </td>
                                  </tr>
                                  
                                  {/* 세부 항목들 */}
                                  {group.fields.map((field, fieldIndex) => (
                                    <tr 
                                      key={fieldIndex}
                                      className={`${groupIndex % 2 === 0 ? "bg-muted/5" : "bg-muted/15"} border-b hover:bg-muted/25`}
                                    >
                                      {/* ISMS-P 열 - 빈 칸 */}
                                      <td className="p-3 border-r text-center">
                                      </td>
                                      
                                      {/* ISMS 열 - 빈 칸 */}
                                      <td className="p-3 border-r text-center">
                                      </td>
                                      
                                      {/* 통합인증 열은 rowspan으로 이미 처리됨 */}
                                      
                                      {/* 분야(인증 개수) 열 */}
                                      <td className="p-3 border-r text-sm pl-4 text-muted-foreground">
                                        {field.name}({field.count})
                                      </td>
                                      
                                      {/* 진단결과 열 */}
                                      <td className="p-3 text-center">
                                        <div
                                          className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                            field.rating === "P"
                                              ? "bg-yellow-500"
                                              : field.rating === "Y"
                                                ? "bg-green-500"
                                                : "bg-red-500"
                                          }`}
                                        >
                                          {field.rating}
                                        </div>
                                      </td>
                                    </tr>
                                  ))}
                                </React.Fragment>
                              );
                            })}
                          </tbody>
                        </table>
                      </ScrollArea>
                    </div>
                  </div>

                  {/* 취약점 대응방안 */}
                  <div className="border-t pt-4">
                    <h3 className="mb-3">취약점 대응방안</h3>
                    <div className="w-full">
                      <ScrollArea className="h-[300px] w-full">
                        <div className="border rounded-lg overflow-hidden min-w-full">
                          <div className="sticky top-0 bg-muted/80 backdrop-blur-sm z-10">
                            <div className="grid grid-cols-2 gap-0 border-b">
                              <div className="p-4 border-r font-medium text-sm">
                                취약점
                              </div>
                              <div className="p-4 font-medium text-sm">
                                대응방안
                              </div>
                            </div>
                          </div>
                          <div className="bg-white">
                            {vulnerabilityDetails.map((item, index) => (
                              <div
                                key={item.id}
                                className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/10"} hover:bg-muted/20 border-b transition-colors`}
                              >
                                <div className="p-4 border-r text-sm leading-relaxed">
                                  {item.vulnerability}
                                </div>
                                <div className="p-4 text-sm leading-relaxed">
                                  {item.countermeasure}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </ScrollArea>
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* 자동 진단 */}
            <TabsContent
              value="auto"
              className="flex-1 flex flex-col space-y-4"
            >
              {isUploading ? (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    자동 진단 수행 중…
                  </p>
                  <Progress value={progress} />
                </div>
              ) : !diagnosisGenerated ? (
                <div className="space-y-4">
                  <div className="text-center py-8 text-muted-foreground">
                    지침서를 업로드하면 자동 진단해드립니다.
                  </div>
                  <div className="flex justify-center">
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
                      <label>
                        지침서 업로드
                        <input
                          type="file"
                          accept=".xlsx,.xls"
                          onChange={handleDiagnosisFileUpload}
                          className="hidden"
                        />
                      </label>
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col space-y-4">
                  <div className="flex gap-2">
                    <Button
                      onClick={handleDownloadReport}
                      variant="outline"
                      className="gap-2"
                    >
                      자동진단 보고서 다운로드
                    </Button>
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
                      <label>
                        지침서 재업로드
                        <input
                          type="file"
                          accept=".xlsx,.xls"
                          onChange={handleDiagnosisFileUpload}
                          className="hidden"
                        />
                      </label>
                    </Button>
                  </div>

                  {diagnosisFile && (
                    <p className="text-sm text-muted-foreground">
                      업로드된 파일: {diagnosisFile.name}
                    </p>
                  )}

                  {/* 자동 진단 결과도 동일한 테이블 구조 사용 */}
                  <div className="flex-1 min-h-0">
                    <div className="border rounded-lg overflow-hidden h-[400px]">
                      <ScrollArea className="h-full w-full">
                        <table className="w-full border-collapse">
                          <thead className="sticky top-0 bg-muted/80 backdrop-blur-sm z-10">
                            {/* 첫 번째 헤더 행 */}
                            <tr>
                              <th 
                                colSpan={2}
                                className="p-3 border-r border-b font-medium text-center text-sm min-w-[200px]"
                              >
                                구분
                              </th>
                              <th 
                                rowSpan={2}
                                className="p-3 border-r border-b font-medium text-center text-sm min-w-[200px] align-middle"
                              >
                                통합인증
                              </th>
                              <th 
                                rowSpan={2}
                                className="p-3 border-r border-b font-medium text-center text-sm min-w-[300px] align-middle"
                              >
                                분야(인증 개수)
                              </th>
                              <th 
                                rowSpan={2}
                                className="p-3 border-b font-medium text-center text-sm min-w-[100px] align-middle"
                              >
                                진단결과
                              </th>
                            </tr>
                            {/* 두 번째 헤더 행 */}
                            <tr>
                              <th className="p-3 border-r border-b font-medium text-center text-sm min-w-[100px]">
                                ISMS-P
                              </th>
                              <th className="p-3 border-r border-b font-medium text-center text-sm min-w-[100px]">
                                ISMS
                              </th>
                            </tr>
                          </thead>
                          
                          <tbody className="bg-white">
                            {summaryResults.map((group, groupIndex) => {
                              return (
                                <React.Fragment key={group.id}>
                                  <tr className={`${groupIndex % 2 === 0 ? "bg-white" : "bg-muted/20"} hover:bg-muted/30 border-b`}>
                                    <td className="p-3 border-r text-center font-medium text-sm">
                                      {group.division === "ISMS-P" ? "○" : ""}
                                    </td>
                                    
                                    <td className="p-3 border-r text-center font-medium text-sm">
                                      {group.division === "ISMS" ? "○" : ""}
                                    </td>
                                    
                                    <td 
                                      rowSpan={group.fields.length + 1}
                                      className="p-3 border-r text-sm font-medium align-top"
                                    >
                                      {group.integratedAuth}
                                    </td>
                                    
                                    <td className="p-3 border-r text-center">
                                    </td>
                                    
                                    <td className="p-3 text-center">
                                    </td>
                                  </tr>
                                  
                                  {group.fields.map((field, fieldIndex) => (
                                    <tr 
                                      key={fieldIndex}
                                      className={`${groupIndex % 2 === 0 ? "bg-muted/5" : "bg-muted/15"} border-b hover:bg-muted/25`}
                                    >
                                      <td className="p-3 border-r text-center">
                                      </td>
                                      
                                      <td className="p-3 border-r text-center">
                                      </td>
                                      
                                      <td className="p-3 border-r text-sm pl-4 text-muted-foreground">
                                        {field.name}({field.count})
                                      </td>
                                      
                                      <td className="p-3 text-center">
                                        <div
                                          className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                            field.rating === "P"
                                              ? "bg-yellow-500"
                                              : field.rating === "Y"
                                                ? "bg-green-500"
                                                : "bg-red-500"
                                          }`}
                                        >
                                          {field.rating}
                                        </div>
                                      </td>
                                    </tr>
                                  ))}
                                </React.Fragment>
                              );
                            })}
                          </tbody>
                        </table>
                      </ScrollArea>
                    </div>
                  </div>

                  {/* 취약점 대응방안 - 자동 진단 탭에 추가 */}
                  <div className="border-t pt-4">
                    <h3 className="mb-3">취약점 대응방안</h3>
                    <div className="w-full">
                      <ScrollArea className="h-[300px] w-full">
                        <div className="border rounded-lg overflow-hidden min-w-full">
                          <div className="sticky top-0 bg-muted/80 backdrop-blur-sm z-10">
                            <div className="grid grid-cols-2 gap-0 border-b">
                              <div className="p-4 border-r font-medium text-sm">
                                취약점
                              </div>
                              <div className="p-4 font-medium text-sm">
                                대응방안
                              </div>
                            </div>
                          </div>
                          <div className="bg-white">
                            {vulnerabilityDetails.map((item, index) => (
                              <div
                                key={item.id}
                                className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/10"} hover:bg-muted/20 border-b transition-colors`}
                              >
                                <div className="p-4 border-r text-sm leading-relaxed">
                                  {item.vulnerability}
                                </div>
                                <div className="p-4 text-sm leading-relaxed">
                                  {item.countermeasure}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </ScrollArea>
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* 로딩 모달 */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {modalContent.type === "success" && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {modalContent.type === "error" && <AlertCircle className="h-5 w-5 text-red-500" />}
                  {modalContent.type === "info" && <Clock className="h-5 w-5 text-blue-500" />}
                  <CardTitle className="text-base">{modalContent.title}</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="font-medium">{modalContent.message}</div>
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

      {/* 진단 완료 모달 */}
      {showDiagnosisCompleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowDiagnosisCompleteModal(false)} />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <CardTitle className="text-base">자동 진단 완료</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowDiagnosisCompleteModal(false)}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="font-medium">자동 진단이 완료되었습니다.</div>
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
    </>
  );
}