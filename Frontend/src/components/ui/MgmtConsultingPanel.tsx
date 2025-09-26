import React, { useState } from "react";
import * as XLSX from "xlsx";
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
  CheckCircle,
  X,
  AlertCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Info,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./tooltip";
import { toast } from "sonner";

// 구분 열 통합 및 진단결과 열 분리 구조
const summaryResults = [
  {
    id: 1,
    division: "ISMS-P", // 통합된 구분 열
    integratedAuth: "1. 관리체계 수립 및 운영", // 통합인증 열
    fields: [
      {
        name: "1.1 관리체계 기반마련",
        count: 6,
        rating: "Y",
        subItems: [
          { id: "1.1.1", name: "경영진의 참여", rating: "Y" },
          {
            id: "1.1.2",
            name: "최고책임자의 지정",
            rating: "P",
          },
          { id: "1.1.3", name: "조직 구성", rating: "Y" },
          { id: "1.1.4", name: "범위 설정", rating: "N" },
          { id: "1.1.5", name: "정책 수립", rating: "Y" },
          { id: "1.1.6", name: "자원 할당", rating: "P" },
        ],
      },
      {
        name: "1.2 위험관리",
        count: 4,
        rating: "P",
        subItems: [
          { id: "1.2.1", name: "정보자산 식별", rating: "Y" },
          {
            id: "1.2.2",
            name: "현황 및 흐름분석",
            rating: "P",
          },
          { id: "1.2.3", name: "위험 평가", rating: "N" },
          { id: "1.2.4", name: "보호대책 선정", rating: "P" },
        ],
      },
      {
        name: "1.3 관리체계 운영",
        count: 3,
        rating: "N",
        subItems: [
          { id: "1.3.1", name: "보호대책 구현", rating: "P" },
          { id: "1.3.2", name: "보호대책 공유", rating: "N" },
          { id: "1.3.3", name: "운영현황 관리", rating: "Y" },
        ],
      },
      {
        name: "1.4 관리체계 점검 및 개선",
        count: 3,
        rating: "Y",
        subItems: [
          {
            id: "1.4.1",
            name: "법적 요구사항 준수 검토",
            rating: "Y",
          },
          { id: "1.4.2", name: "관리체계 점검", rating: "P" },
          { id: "1.4.3", name: "관리체계 개선", rating: "Y" },
        ],
      },
    ],
  },
  {
    id: 2,
    division: "ISMS", // 통합된 구분 열
    integratedAuth: "2. 보호대책 요구사항", // 통합인증 열
    fields: [
      {
        name: "2.1 정책, 조직, 자산 관리",
        count: 3,
        rating: "P",
        subItems: [
          { id: "2.1.1", name: "정책의 유지관리", rating: "Y" },
          { id: "2.1.2", name: "조직의 유지관리", rating: "P" },
          { id: "2.1.3", name: "정보자산 관리", rating: "N" },
        ],
      },
      {
        name: "2.2 인적보안",
        count: 6,
        rating: "Y",
        subItems: [
          {
            id: "2.2.1",
            name: "주요 직무자 지정 및 관리",
            rating: "Y",
          },
          { id: "2.2.2", name: "직무 분리", rating: "P" },
          { id: "2.2.3", name: "보안 서약", rating: "Y" },
          {
            id: "2.2.4",
            name: "인식제고 및 교육훈련",
            rating: "N",
          },
          {
            id: "2.2.5",
            name: "퇴직 및 직무변경 관리",
            rating: "Y",
          },
          {
            id: "2.2.6",
            name: "보안 위반 시 조치",
            rating: "P",
          },
        ],
      },
      {
        name: "2.3 외부자 보안",
        count: 4,
        rating: "N",
        subItems: [
          {
            id: "2.3.1",
            name: "외부자 현황 관리",
            rating: "N",
          },
          {
            id: "2.3.2",
            name: "외부자 계약 시 보안",
            rating: "P",
          },
          {
            id: "2.3.3",
            name: "외부자 보안 이행 관리",
            rating: "N",
          },
          {
            id: "2.3.4",
            name: "외부자 계약 변경 및 만료 시 보안",
            rating: "Y",
          },
        ],
      },
      {
        name: "2.4 물리보안",
        count: 7,
        rating: "P",
        subItems: [
          { id: "2.4.1", name: "보호구역 지정", rating: "Y" },
          { id: "2.4.2", name: "출입통제", rating: "P" },
          { id: "2.4.3", name: "정보시스템 보호", rating: "Y" },
          { id: "2.4.4", name: "보호설비 운영", rating: "N" },
          {
            id: "2.4.5",
            name: "보호구역 내 작업",
            rating: "P",
          },
          {
            id: "2.4.6",
            name: "반출입 기기 통제",
            rating: "Y",
          },
          { id: "2.4.7", name: "업무환경 보안", rating: "P" },
        ],
      },
      {
        name: "2.5 인증 및 권한 관리",
        count: 6,
        rating: "Y",
        subItems: [
          {
            id: "2.5.1",
            name: "사용자 계정 관리",
            rating: "Y",
          },
          { id: "2.5.2", name: "사용자 식별", rating: "P" },
          { id: "2.5.3", name: "사용자 인증", rating: "Y" },
          { id: "2.5.4", name: "비밀번호 관리", rating: "N" },
          {
            id: "2.5.5",
            name: "특수 계정 및 권한 관리",
            rating: "Y",
          },
          { id: "2.5.6", name: "접근권한 검토", rating: "P" },
        ],
      },
      {
        name: "2.6 접근통제",
        count: 7,
        rating: "N",
        subItems: [
          { id: "2.6.1", name: "네트워크 접근", rating: "N" },
          { id: "2.6.2", name: "정보시스템 접근", rating: "P" },
          {
            id: "2.6.3",
            name: "응용프로그램 접근",
            rating: "Y",
          },
          {
            id: "2.6.4",
            name: "데이터베이스 접근",
            rating: "N",
          },
          {
            id: "2.6.5",
            name: "무선 네트워크 접근",
            rating: "P",
          },
          { id: "2.6.6", name: "원격접근 통제", rating: "N" },
          {
            id: "2.6.7",
            name: "인터넷 접속 통제",
            rating: "Y",
          },
        ],
      },
      {
        name: "2.7 암호화 적용",
        count: 2,
        rating: "P",
        subItems: [
          { id: "2.7.1", name: "암호정책 적용", rating: "P" },
          { id: "2.7.2", name: "암호키 관리", rating: "N" },
        ],
      },
      {
        name: "2.8 정보시스템 도입 및 개발 보안",
        count: 6,
        rating: "Y",
        subItems: [
          {
            id: "2.8.1",
            name: "보안 요구사항 정의",
            rating: "Y",
          },
          {
            id: "2.8.2",
            name: "보안 요구사항 검토 및 시험",
            rating: "P",
          },
          {
            id: "2.8.3",
            name: "시험과 운영 환경 분리",
            rating: "Y",
          },
          {
            id: "2.8.4",
            name: "시험 데이터 보안",
            rating: "N",
          },
          {
            id: "2.8.5",
            name: "소스 프로그램 관리",
            rating: "Y",
          },
          { id: "2.8.6", name: "운영환경 이관", rating: "P" },
        ],
      },
      {
        name: "2.9 시스템 및 서비스 운영관리",
        count: 7,
        rating: "N",
        subItems: [
          { id: "2.9.1", name: "변경관리", rating: "N" },
          {
            id: "2.9.2",
            name: "성능 및 장애관리",
            rating: "P",
          },
          {
            id: "2.9.3",
            name: "백업 및 복구관리",
            rating: "Y",
          },
          {
            id: "2.9.4",
            name: "로그 및 접속기록 관리",
            rating: "N",
          },
          {
            id: "2.9.5",
            name: "로그 및 접속기록 점검",
            rating: "P",
          },
          { id: "2.9.6", name: "시간 동기화", rating: "Y" },
          {
            id: "2.9.7",
            name: "정보자산의 재사용 및 폐기",
            rating: "N",
          },
        ],
      },
      {
        name: "2.10 시스템 및 서비스 보안관리",
        count: 9,
        rating: "P",
        subItems: [
          {
            id: "2.10.1",
            name: "보안시스템 운영",
            rating: "Y",
          },
          { id: "2.10.2", name: "클라우드 보안", rating: "P" },
          { id: "2.10.3", name: "공개서버 보안", rating: "N" },
          {
            id: "2.10.4",
            name: "전자거래 및 핀테크 보안",
            rating: "P",
          },
          { id: "2.10.5", name: "정보전송 보안", rating: "Y" },
          {
            id: "2.10.6",
            name: "업무용 단말기기 보안",
            rating: "P",
          },
          {
            id: "2.10.7",
            name: "보조저장매체 관리",
            rating: "N",
          },
          { id: "2.10.8", name: "패치관리", rating: "P" },
          { id: "2.10.9", name: "악성코드 통제", rating: "Y" },
        ],
      },
      {
        name: "2.11 사고 예방 및 대응",
        count: 5,
        rating: "Y",
        subItems: [
          {
            id: "2.11.1",
            name: "사고 예방 및 대응체계 구축",
            rating: "Y",
          },
          {
            id: "2.11.2",
            name: "취약점 점검 및 조치",
            rating: "P",
          },
          {
            id: "2.11.3",
            name: "이상행위 분석 및 모니터링",
            rating: "Y",
          },
          {
            id: "2.11.4",
            name: "사고 대응 훈련 및 개선",
            rating: "N",
          },
          {
            id: "2.11.5",
            name: "사고 대응 및 복구",
            rating: "Y",
          },
        ],
      },
      {
        name: "2.12 재해복구",
        count: 2,
        rating: "N",
        subItems: [
          {
            id: "2.12.1",
            name: "재해·재난 대비 안전조치",
            rating: "N",
          },
          {
            id: "2.12.2",
            name: "재해 복구 시험 및 개선",
            rating: "P",
          },
        ],
      },
    ],
  },
  {
    id: 3,
    division: "", // 빈 값으로 ISMS와 병합
    integratedAuth: "3. 개인정보 처리단계별 요구사항", // 통합인증 열
    fields: [
      {
        name: "3.1 개인정보 수집 시 보호조치",
        count: 7,
        rating: "P",
        subItems: [
          {
            id: "3.1.1",
            name: "개인정보 수집.이용",
            rating: "P",
          },
          {
            id: "3.1.2",
            name: "개인정보의 수집 제한",
            rating: "Y",
          },
          {
            id: "3.1.3",
            name: "주민등록번호 처리 제한",
            rating: "N",
          },
          {
            id: "3.1.4",
            name: "민감정보 및 고유식별정보의 처리 제한",
            rating: "P",
          },
          {
            id: "3.1.5",
            name: "간접수집 보호조치",
            rating: "Y",
          },
          {
            id: "3.1.6",
            name: "영상정보처리기기 설치·운영",
            rating: "N",
          },
          {
            id: "3.1.7",
            name: "마케팅 목적의 개인정보 수집.이용",
            rating: "P",
          },
        ],
      },
      {
        name: "3.2 개인정보 보유 및 이용 시 보호조치",
        count: 5,
        rating: "Y",
        subItems: [
          {
            id: "3.2.1",
            name: "개인정보 현황관리",
            rating: "Y",
          },
          {
            id: "3.2.2",
            name: "개인정보 품질보장",
            rating: "P",
          },
          {
            id: "3.2.3",
            name: "이용자 단말기 접근 보호",
            rating: "Y",
          },
          {
            id: "3.2.4",
            name: "개인정보 목적 외 이용 및 제공",
            rating: "N",
          },
          { id: "3.2.5", name: "가명정보 처리", rating: "Y" },
        ],
      },
      {
        name: "3.3 개인정보 제공 시 보호조치",
        count: 4,
        rating: "N",
        subItems: [
          {
            id: "3.3.1",
            name: "개인정보 제3자 제공",
            rating: "N",
          },
          {
            id: "3.3.2",
            name: "개인정보 처리 업무 위탁",
            rating: "P",
          },
          {
            id: "3.3.3",
            name: "영업의 양수 등에 따른 개인정보의 이전",
            rating: "Y",
          },
          {
            id: "3.3.4",
            name: "개인정보의 국외이전",
            rating: "N",
          },
        ],
      },
      {
        name: "3.4 개인정보 파기 시 보호조치",
        count: 2,
        rating: "P",
        subItems: [
          { id: "3.4.1", name: "개인정보의 파기", rating: "P" },
          {
            id: "3.4.2",
            name: "처리목적 달성 후 보유 시 조치",
            rating: "N",
          },
        ],
      },
      {
        name: "3.5 정보주체 권리보호",
        count: 3,
        rating: "Y",
        subItems: [
          {
            id: "3.5.1",
            name: "개인정보처리방침 공개",
            rating: "Y",
          },
          {
            id: "3.5.2",
            name: "정보주체 권리보장",
            rating: "P",
          },
          {
            id: "3.5.3",
            name: "정보주체에 대한 통지",
            rating: "Y",
          },
        ],
      },
    ],
  },
];

// 취약점 상세 데��터
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
  const [showSummaryCompleteModal, setShowSummaryCompleteModal] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState({
    title: "",
    message: "",
    type: "info" as "info" | "success" | "error",
  });
  const [openFields, setOpenFields] = useState<string[]>([]);
  // 1. 상태 및 데이터 구조 준비
  const [hasExcelData, setHasExcelData] = useState(false);
  const [parsedExcelData, setParsedExcelData] = useState<
    typeof summaryResults
  >([]);
  // 상태 관리 및 데이터 업데이트: 엑셀에서 추출한 취약점 데이터를 저장할 새로운 상태 변수
  const [
    dynamicVulnerabilityDetails,
    setDynamicVulnerabilityDetails,
  ] = useState<
    Array<{
      id: number;
      vulnerability: string;
      countermeasure: string;
    }>
  >([]);

  const showModalMessage = (
    title: string,
    message: string,
    type: "info" | "success" | "error" = "info",
  ) => {
    setModalContent({ title, message, type });
    setShowModal(true);
    setTimeout(() => setShowModal(false), 2000);
  };

  const toggleField = (fieldName: string) => {
    setOpenFields((prev) =>
      prev.includes(fieldName)
        ? prev.filter((name) => name !== fieldName)
        : [...prev, fieldName],
    );
  };

  // 2. 엑셀 데이터 처리 및 매핑 로직
  const processExcelData = (
    file: File,
  ): Promise<typeof summaryResults> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const data = e.target?.result;
          if (!data) {
            throw new Error("파일 데이터를 읽을 수 없습니다.");
          }

          const workbook = XLSX.read(data, { type: "binary" });
          if (
            !workbook.SheetNames ||
            workbook.SheetNames.length === 0
          ) {
            throw new Error("엑셀 파일에 시트가 없습니다.");
          }

          const worksheet =
            workbook.Sheets[workbook.SheetNames[0]];

          // XLSX.utils.sheet_to_json(worksheet, { header: 1 })을 사용하여 헤더를 포함한 모든 데이터를 배열로 가져오기
          const jsonData = XLSX.utils.sheet_to_json(worksheet, {
            header: 1,
          }) as any[][];

          if (!jsonData || jsonData.length === 0) {
            console.warn("엑셀 파일이 비어있습니다.");
            toast.error(
              "엑셀 파일이 비어있습니다. 데이터가 있는 파일을 업로드해주세요.",
            );
            // 원본 데이터 불변성 유지: summaryResults의 깊은 복사본을 생성
            const newSummaryResults = JSON.parse(
              JSON.stringify(summaryResults),
            );
            resolve({
              summaryData: newSummaryResults,
              vulnerabilityData: [],
            });
            return;
          }

          // 엑셀 데이터 처리 로직 수정: 헤더 행 찾기 - "진단결과", "항목", "개선방안" 열 모두 찾기
          let headerRowIndex = -1;
          let diagnosisColumnIndex = -1;
          let itemColumnIndex = -1;
          let countermeasureColumnIndex = -1;

          for (
            let i = 0;
            i < Math.min(10, jsonData.length);
            i++
          ) {
            const row = jsonData[i];
            if (!row || !Array.isArray(row)) continue;

            for (let j = 0; j < row.length; j++) {
              const cellValue = String(row[j] || "").trim();
              if (cellValue.includes("진단결과")) {
                headerRowIndex = i;
                diagnosisColumnIndex = j;
              }
              if (cellValue.includes("항목")) {
                itemColumnIndex = j;
              }
              if (cellValue.includes("개선방안")) {
                countermeasureColumnIndex = j;
              }
            }

            // 모든 필요한 열을 찾았으면 중단
            if (
              diagnosisColumnIndex !== -1 &&
              itemColumnIndex !== -1 &&
              countermeasureColumnIndex !== -1
            ) {
              break;
            }
          }

          // 필수 열들을 찾지 못할 경우
          if (
            headerRowIndex === -1 ||
            diagnosisColumnIndex === -1
          ) {
            console.warn(
              '엑셀 파일에서 "진단결과" 컬럼을 찾을 수 없습니다. 기본 데이터를 사용합니다.',
            );
            toast.error(
              '엑셀 파일에 "진단결과" 컬럼이 없습니다. 파일에 "진단결과", "항목", "개선방안" 컬럼이 포함된 ISMS-P 현황 분석 보고서를 업로드해주세요.',
            );
            // 기본 summaryResults의 복사본을 반환하여 기본 테이블을 표시
            const newSummaryResults = JSON.parse(
              JSON.stringify(summaryResults),
            );
            resolve({
              summaryData: newSummaryResults,
              vulnerabilityData: [],
            });
            return;
          }

          // 선택적 컬럼들에 대한 경고 메시지
          if (itemColumnIndex === -1) {
            console.warn(
              '엑셀 파일에서 "항목" 컬럼을 찾을 수 없습니다. 취약점 항목 추출이 제한됩니다.',
            );
            toast.warning(
              '"항목" 컬럼이 없어 취약점 항목 추출이 제한됩니다.',
            );
          }

          if (countermeasureColumnIndex === -1) {
            console.warn(
              '엑셀 파일에서 "개선방안" 컬럼을 찾을 수 없습니다. 대응방안 추출이 제한됩니다.',
            );
            toast.warning(
              '"개선방안" 컬럼이 없어 대응방안 추출이 제한됩니다.',
            );
          }

          // 엑셀 데이터 임시 저장: 업로드된 엑셀 파일의 진단결과 열 값만 저장할 임시 배열 생성
          const ratingValues: string[] = [];
          const newVulnerabilityDetails: Array<{
            id: number;
            vulnerability: string;
            countermeasure: string;
          }> = [];
          let vulnerabilityIdCounter = 1;

          // rating 값 추출 및 취약점 데이터 추출: 헤더 행 바로 다음 행부터 시작하여 엑셀 데이터의 각 행을 순회
          for (
            let i = headerRowIndex + 1;
            i < jsonData.length;
            i++
          ) {
            const row = jsonData[i];
            if (
              row &&
              row[diagnosisColumnIndex] !== undefined &&
              row[diagnosisColumnIndex] !== null
            ) {
              const ratingValue = String(
                row[diagnosisColumnIndex],
              )
                .trim()
                .toUpperCase();
              if (
                ratingValue &&
                ["Y", "P", "N"].includes(ratingValue)
              ) {
                ratingValues.push(ratingValue);

                // 진단결과가 'N'인 경우 취약점 데이터로 추출
                if (ratingValue === "N") {
                  const vulnerability =
                    itemColumnIndex !== -1 &&
                    row[itemColumnIndex]
                      ? String(row[itemColumnIndex]).trim()
                      : "";
                  const countermeasure =
                    countermeasureColumnIndex !== -1 &&
                    row[countermeasureColumnIndex]
                      ? String(
                          row[countermeasureColumnIndex],
                        ).trim()
                      : "";

                  // 빈 값이 아닌 경우에만 추가
                  if (vulnerability && countermeasure) {
                    newVulnerabilityDetails.push({
                      id: vulnerabilityIdCounter++,
                      vulnerability: vulnerability,
                      countermeasure: countermeasure,
                    });
                  }
                }
              }
            }
          }

          // 원본 데이터 불변성 유지: summaryResults의 깊은 복사본을 생성
          const newSummaryResults = JSON.parse(
            JSON.stringify(summaryResults),
          );

          // 데이터 순차 매핑: newSummaryResults의 모든 field와 subItem을 순서대로 순회
          let ratingIndex = 0;

          for (const group of newSummaryResults) {
            for (const field of group.fields) {
              // 1. 부모 항목에 진단 결과 표시하지 않기: field.rating에는 "-"를 할당
              field.rating = "-";

              // 2. 하위 항목에만 진단 결과 표시하기: subItems rating 순차 할당
              if (field.subItems) {
                for (const subItem of field.subItems) {
                  if (ratingIndex < ratingValues.length) {
                    subItem.rating = ratingValues[ratingIndex];
                    ratingIndex++;
                  }
                }
              }
            }
          }

          console.log(
            `엑셀 파일 처리 완료: ${ratingValues.length}개의 rating 값이 매핑되었습니다.`,
          );
          console.log(
            `취약점 데이터 추출 완료: ${newVulnerabilityDetails.length}개의 취약점이 발견되었습니다.`,
          );

          // processExcelData 함수가 최종적으로 객체를 반환하도록 수정
          resolve({
            summaryData: newSummaryResults,
            vulnerabilityData: newVulnerabilityDetails,
          });
        } catch (error) {
          console.error("엑셀 파일 처리 중 오류:", error);
          toast.error(
            "엑셀 파일 처리 중 오류가 발생했습니다. 파일 형식을 확인해주세요.",
          );
          // 오류 발생시에도 기본 데이터 구조를 반환
          const newSummaryResults = JSON.parse(
            JSON.stringify(summaryResults),
          );
          resolve({
            summaryData: newSummaryResults,
            vulnerabilityData: [],
          });
        }
      };

      reader.onerror = () => {
        console.error("파일 읽기 오류");
        toast.error(
          "파일 읽기 중 오류가 발생했습니다. 파일이 손상되었을 수 있습니다.",
        );
        // 파일 읽기 오류시에도 기본 데이터 구조를 반환
        const newSummaryResults = JSON.parse(
          JSON.stringify(summaryResults),
        );
        resolve({
          summaryData: newSummaryResults,
          vulnerabilityData: [],
        });
      };

      reader.readAsBinaryString(file);
    });
  };

  const startSummary = async () => {
    setUploading(true);
    setProgress(15);
    showModalMessage(
      "보고서 요약",
      "보고서 요약을 시작합니다...",
      "info",
    );

    const steps = [35, 55, 80, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setProgress(p);
    }

    setUploading(false);
    setSummaryGenerated(true);
    setShowSummaryCompleteModal(true);
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
      // 파일 확장자 검증
      const fileName = file.name.toLowerCase();
      if (
        !fileName.endsWith(".xlsx") &&
        !fileName.endsWith(".xls")
      ) {
        showModalMessage(
          "파일 형식 오류",
          "엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.",
          "error",
        );
        return;
      }

      setUploadedFile(file);
      showModalMessage(
        "파일 업로드",
        `${file.name} 파일이 업로드되었습니다!`,
        "success",
      );

      try {
        // handleFileUpload 함수에서 processExcelData가 반환한 객체를 받아 처리
        const processedData = await processExcelData(file);

        // summaryData는 parsedExcelData 상태에, vulnerabilityData는 dynamicVulnerabilityDetails 상태에 각각 저장
        setParsedExcelData(processedData.summaryData);
        setDynamicVulnerabilityDetails(
          processedData.vulnerabilityData,
        );

        // 파일이 성공적으로 처리되었으므로 setHasExcelData(true) 호출
        setHasExcelData(true);

        // 보고서 요약 프로세스 시작
        await startSummary();
      } catch (error) {
        console.error("엑셀 파일 처리 실패:", error);
        showModalMessage(
          "파일 처리 오류",
          "엑셀 파일 처리 중 오류가 발생했습니다.",
          "error",
        );
      }
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
              <TabsTrigger
                value="summary"
                className="flex items-center gap-2"
              >
                보고서 요약
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className="p-0 h-auto cursor-help inline-flex">
                      <Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                    </span>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="max-w-xs">
                      진단을 원하시는 기업의 ISMS-P 현황 분석
                      보고서를 업로드하면 각 진단 항목을 ISMS,
                      ISMS-P의 만족 여부를 확인하고, 취약 항목과
                      그 대응 방안을 제시합니다.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TabsTrigger>
              <TabsTrigger
                value="auto"
                className="flex items-center gap-2"
              >
                자동 진단
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className="p-0 h-auto cursor-help inline-flex">
                      <Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" />
                    </span>
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    <p className="max-w-xs">
                      진단이 필요한 기업의 내규 지침서를
                      업로드하면 ISMS, ISMS-P의 항목을 자동으로
                      진단하고, 취약 항목과 대응방안을
                      요약합니다.
                    </p>
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
                    보고서 요약 중…
                  </p>
                  <Progress value={progress} />
                </div>
              ) : !summaryGenerated ? (
                <div className="space-y-4">
                  <div className="text-center py-8 space-y-2">
                    <p className="text-muted-foreground">
                      보고서를 업로드하면 자동으로 요약해
                      드립니다.
                    </p>
                  </div>
                  <div className="flex justify-center">
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
                      <label>
                        ISMS-P 현황 분석 보고서 업로드
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

                  {/* 테이블 구조 */}
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

                          {/* 테이블 내용 */}
                          <tbody className="bg-white">
                            {(hasExcelData
                              ? parsedExcelData
                              : summaryResults
                            ).map((group, groupIndex) => {
                              return (
                                <React.Fragment key={group.id}>
                                  {/* 카테고리 헤더 행 */}
                                  <tr
                                    className={`hover:bg-muted/30 border-b`}
                                  >
                                    {/* ISMS-P열 */}
                                    <td
                                      rowSpan={
                                        group.fields.length +
                                        1 +
                                        group.fields
                                          .filter(
                                            (f) =>
                                              f.subItems &&
                                              openFields.includes(
                                                f.name,
                                              ),
                                          )
                                          .reduce(
                                            (acc, f) =>
                                              acc +
                                              (f.subItems
                                                ?.length || 0),
                                            0,
                                          )
                                      }
                                      className="p-3 border-r text-center font-medium text-sm"
                                    >
                                      ISMS-P
                                    </td>

                                    {/* ISMS열 */}
                                    <td
                                      rowSpan={
                                        group.fields.length +
                                        1 +
                                        group.fields
                                          .filter(
                                            (f) =>
                                              f.subItems &&
                                              openFields.includes(
                                                f.name,
                                              ),
                                          )
                                          .reduce(
                                            (acc, f) =>
                                              acc +
                                              (f.subItems
                                                ?.length || 0),
                                            0,
                                          )
                                      }
                                      className="p-3 border-r text-center font-medium text-sm"
                                    >
                                      {groupIndex === 2
                                        ? "-"
                                        : "ISMS"}
                                    </td>

                                    {/* 통합인증 열 */}
                                    <td
                                      rowSpan={
                                        group.fields.length +
                                        1 +
                                        group.fields
                                          .filter(
                                            (f) =>
                                              f.subItems &&
                                              openFields.includes(
                                                f.name,
                                              ),
                                          )
                                          .reduce(
                                            (acc, f) =>
                                              acc +
                                              (f.subItems
                                                ?.length || 0),
                                            0,
                                          )
                                      }
                                      className="p-3 border-r text-sm font-medium align-top"
                                    >
                                      {group.integratedAuth}
                                    </td>
                                  </tr>

                                  {/* 세부 항목들 */}
                                  {group.fields.map(
                                    (field, fieldIndex) => (
                                      <React.Fragment
                                        key={fieldIndex}
                                      >
                                        {field.subItems &&
                                        field.subItems.length >
                                          0 ? (
                                          <React.Fragment>
                                            {/* 메인 항목 행 */}
                                            <tr
                                              className={`${groupIndex % 2 === 0 ? "bg-muted/5" : "bg-muted/15"} border-b hover:bg-muted/25`}
                                            >
                                              <td
                                                className="p-3 border-r text-sm pl-4 text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                                                onClick={() =>
                                                  toggleField(
                                                    field.name,
                                                  )
                                                }
                                              >
                                                <div className="flex items-center gap-2">
                                                  {openFields.includes(
                                                    field.name,
                                                  ) ? (
                                                    <ChevronDown className="h-4 w-4" />
                                                  ) : (
                                                    <ChevronRight className="h-4 w-4" />
                                                  )}
                                                  {field.name}(
                                                  {field.count})
                                                </div>
                                              </td>
                                              <td className="p-3 text-center">
                                                {/* 1,2,3번 그룹 모든 항목들은 rating 표시하지 않음 */}
                                                {!field.name.startsWith(
                                                  "1.",
                                                ) &&
                                                !field.name.startsWith(
                                                  "2.",
                                                ) &&
                                                !field.name.startsWith(
                                                  "3.",
                                                ) ? (
                                                  <div
                                                    className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                                      field.rating ===
                                                      "P"
                                                        ? "bg-yellow-500"
                                                        : field.rating ===
                                                            "Y"
                                                          ? "bg-green-500"
                                                          : "bg-red-500"
                                                    }`}
                                                  >
                                                    {
                                                      field.rating
                                                    }
                                                  </div>
                                                ) : (
                                                  <span className="text-muted-foreground text-sm">
                                                    -
                                                  </span>
                                                )}
                                              </td>
                                            </tr>
                                            {/* 세부 항목들 (조건부 렌더링) */}
                                            {openFields.includes(
                                              field.name,
                                            ) &&
                                              field.subItems.map(
                                                (subItem) => (
                                                  <tr
                                                    key={
                                                      subItem.id
                                                    }
                                                    className={`${groupIndex % 2 === 0 ? "bg-muted/10" : "bg-muted/20"} border-b hover:bg-muted/30`}
                                                  >
                                                    <td className="p-3 border-r text-sm pl-8 text-muted-foreground">
                                                      {
                                                        subItem.name
                                                      }
                                                    </td>
                                                    <td className="p-3 text-center">
                                                      <div
                                                        className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                                          subItem.rating ===
                                                          "P"
                                                            ? "bg-yellow-500"
                                                            : subItem.rating ===
                                                                "Y"
                                                              ? "bg-green-500"
                                                              : "bg-red-500"
                                                        }`}
                                                      >
                                                        {
                                                          subItem.rating
                                                        }
                                                      </div>
                                                    </td>
                                                  </tr>
                                                ),
                                              )}
                                          </React.Fragment>
                                        ) : (
                                          <tr
                                            className={`${groupIndex % 2 === 0 ? "bg-muted/5" : "bg-muted/15"} border-b hover:bg-muted/25`}
                                          >
                                            <td className="p-3 border-r text-sm pl-4 text-muted-foreground">
                                              {field.name}(
                                              {field.count})
                                            </td>
                                            <td className="p-3 text-center">
                                              {/* 1,2,3번 그룹 모든 항목들은 rating 표시하지 않음 */}
                                              {!field.name.startsWith(
                                                "1.",
                                              ) &&
                                              !field.name.startsWith(
                                                "2.",
                                              ) &&
                                              !field.name.startsWith(
                                                "3.",
                                              ) ? (
                                                <div
                                                  className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                                    field.rating ===
                                                    "P"
                                                      ? "bg-yellow-500"
                                                      : field.rating ===
                                                          "Y"
                                                        ? "bg-green-500"
                                                        : "bg-red-500"
                                                  }`}
                                                >
                                                  {field.rating}
                                                </div>
                                              ) : (
                                                <span className="text-muted-foreground text-sm">
                                                  -
                                                </span>
                                              )}
                                            </td>
                                          </tr>
                                        )}
                                      </React.Fragment>
                                    ),
                                  )}
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
                    <h3 className="mb-3">
                      취약 항목 | 대응방안
                    </h3>
                    <div className="w-full">
                      <ScrollArea className="h-[300px] w-full">
                        <div className="border rounded-lg overflow-hidden min-w-full">
                          <div className="sticky top-0 bg-muted/80 backdrop-blur-sm z-10">
                            <div className="grid grid-cols-2 gap-0 border-b">
                              <div className="p-4 border-r font-medium text-sm">
                                취약 항목
                              </div>
                              <div className="p-4 font-medium text-sm">
                                대응방안
                              </div>
                            </div>
                          </div>
                          <div className="bg-white">
                            {/* UI 렌더링 수정: 동적 vulnerabilityDetails 배열 사용 */}
                            {(hasExcelData
                              ? dynamicVulnerabilityDetails
                              : vulnerabilityDetails
                            ).length > 0 ? (
                              (hasExcelData
                                ? dynamicVulnerabilityDetails
                                : vulnerabilityDetails
                              ).map((item, index) => (
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
                              ))
                            ) : (
                              <div className="p-8 text-center text-muted-foreground">
                                취약점이 발견되지 않았습니다.
                              </div>
                            )}
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
                  <div className="flex justify-start">
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

                  {/* 보고서요약과 동일한 테이블 구조 */}
                  <div className="flex-1 min-h-0">
                    <div className="border rounded-lg overflow-hidden h-[500px]">
                      <ScrollArea className="h-full w-full">
                        <table className="w-full border-collapse">
                          {/* 동일한 테이블 헤더 구조 */}
                          <thead className="sticky top-0 bg-muted/80 backdrop-blur-sm z-10">
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
                            <tr>
                              <th className="p-3 border-r border-b font-medium text-center text-sm min-w-[100px]">
                                ISMS-P
                              </th>
                              <th className="p-3 border-r border-b font-medium text-center text-sm min-w-[100px]">
                                ISMS
                              </th>
                            </tr>
                          </thead>

                          {/* 동일한 테이블 내용 - 보고서 요약 탭과 완전히 동일한 구조 */}
                          <tbody className="bg-white">
                            {(hasExcelData
                              ? parsedExcelData
                              : summaryResults
                            ).map((group, groupIndex) => {
                              return (
                                <React.Fragment key={group.id}>
                                  {/* 카테고리 헤더 행 */}
                                  <tr
                                    className={`hover:bg-muted/30 border-b`}
                                  >
                                    {/* ISMS-P열 */}
                                    <td
                                      rowSpan={
                                        group.fields.length +
                                        1 +
                                        group.fields
                                          .filter(
                                            (f) =>
                                              f.subItems &&
                                              openFields.includes(
                                                f.name,
                                              ),
                                          )
                                          .reduce(
                                            (acc, f) =>
                                              acc +
                                              (f.subItems
                                                ?.length || 0),
                                            0,
                                          )
                                      }
                                      className="p-3 border-r text-center font-medium text-sm"
                                    >
                                      ISMS-P
                                    </td>

                                    {/* ISMS열 */}
                                    <td
                                      rowSpan={
                                        group.fields.length +
                                        1 +
                                        group.fields
                                          .filter(
                                            (f) =>
                                              f.subItems &&
                                              openFields.includes(
                                                f.name,
                                              ),
                                          )
                                          .reduce(
                                            (acc, f) =>
                                              acc +
                                              (f.subItems
                                                ?.length || 0),
                                            0,
                                          )
                                      }
                                      className="p-3 border-r text-center font-medium text-sm"
                                    >
                                      {groupIndex === 2
                                        ? "-"
                                        : "ISMS"}
                                    </td>

                                    {/* 통합인증 열 */}
                                    <td
                                      rowSpan={
                                        group.fields.length +
                                        1 +
                                        group.fields
                                          .filter(
                                            (f) =>
                                              f.subItems &&
                                              openFields.includes(
                                                f.name,
                                              ),
                                          )
                                          .reduce(
                                            (acc, f) =>
                                              acc +
                                              (f.subItems
                                                ?.length || 0),
                                            0,
                                          )
                                      }
                                      className="p-3 border-r text-sm font-medium align-top"
                                    >
                                      {group.integratedAuth}
                                    </td>
                                  </tr>

                                  {/* 세부 항목들 */}
                                  {group.fields.map(
                                    (field, fieldIndex) => (
                                      <React.Fragment
                                        key={fieldIndex}
                                      >
                                        {field.subItems &&
                                        field.subItems.length >
                                          0 ? (
                                          <React.Fragment>
                                            {/* 메인 항목 행 */}
                                            <tr
                                              className={`${groupIndex % 2 === 0 ? "bg-muted/5" : "bg-muted/15"} border-b hover:bg-muted/25`}
                                            >
                                              <td
                                                className="p-3 border-r text-sm pl-4 text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
                                                onClick={() =>
                                                  toggleField(
                                                    field.name,
                                                  )
                                                }
                                              >
                                                <div className="flex items-center gap-2">
                                                  {openFields.includes(
                                                    field.name,
                                                  ) ? (
                                                    <ChevronDown className="h-4 w-4" />
                                                  ) : (
                                                    <ChevronRight className="h-4 w-4" />
                                                  )}
                                                  {field.name}(
                                                  {field.count})
                                                </div>
                                              </td>
                                              <td className="p-3 text-center">
                                                {/* 1,2,3번 그룹 모든 항목들은 rating 표시하지 않음 */}
                                                {!field.name.startsWith(
                                                  "1.",
                                                ) &&
                                                !field.name.startsWith(
                                                  "2.",
                                                ) &&
                                                !field.name.startsWith(
                                                  "3.",
                                                ) ? (
                                                  <div
                                                    className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                                      field.rating ===
                                                      "P"
                                                        ? "bg-yellow-500"
                                                        : field.rating ===
                                                            "Y"
                                                          ? "bg-green-500"
                                                          : "bg-red-500"
                                                    }`}
                                                  >
                                                    {
                                                      field.rating
                                                    }
                                                  </div>
                                                ) : (
                                                  <span className="text-muted-foreground text-sm">
                                                    -
                                                  </span>
                                                )}
                                              </td>
                                            </tr>
                                            {/* 세부 항목들 (조건부 렌더링) */}
                                            {openFields.includes(
                                              field.name,
                                            ) &&
                                              field.subItems.map(
                                                (subItem) => (
                                                  <tr
                                                    key={
                                                      subItem.id
                                                    }
                                                    className={`${groupIndex % 2 === 0 ? "bg-muted/10" : "bg-muted/20"} border-b hover:bg-muted/30`}
                                                  >
                                                    <td className="p-3 border-r text-sm pl-8 text-muted-foreground">
                                                      {
                                                        subItem.name
                                                      }
                                                    </td>
                                                    <td className="p-3 text-center">
                                                      <div
                                                        className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                                          subItem.rating ===
                                                          "P"
                                                            ? "bg-yellow-500"
                                                            : subItem.rating ===
                                                                "Y"
                                                              ? "bg-green-500"
                                                              : "bg-red-500"
                                                        }`}
                                                      >
                                                        {
                                                          subItem.rating
                                                        }
                                                      </div>
                                                    </td>
                                                  </tr>
                                                ),
                                              )}
                                          </React.Fragment>
                                        ) : (
                                          <tr
                                            className={`${groupIndex % 2 === 0 ? "bg-muted/5" : "bg-muted/15"} border-b hover:bg-muted/25`}
                                          >
                                            <td className="p-3 border-r text-sm pl-4 text-muted-foreground">
                                              {field.name}(
                                              {field.count})
                                            </td>
                                            <td className="p-3 text-center">
                                              {/* 1,2,3번 그룹 모든 항목들은 rating 표시하지 않음 */}
                                              {!field.name.startsWith(
                                                "1.",
                                              ) &&
                                              !field.name.startsWith(
                                                "2.",
                                              ) &&
                                              !field.name.startsWith(
                                                "3.",
                                              ) ? (
                                                <div
                                                  className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-xs font-medium ${
                                                    field.rating ===
                                                    "P"
                                                      ? "bg-yellow-500"
                                                      : field.rating ===
                                                          "Y"
                                                        ? "bg-green-500"
                                                        : "bg-red-500"
                                                  }`}
                                                >
                                                  {field.rating}
                                                </div>
                                              ) : (
                                                <span className="text-muted-foreground text-sm">
                                                  -
                                                </span>
                                              )}
                                            </td>
                                          </tr>
                                        )}
                                      </React.Fragment>
                                    ),
                                  )}
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
                        <div className="border rounded-lg overflow-hidden">
                          <table className="w-full border-collapse">
                            <thead className="sticky top-0 z-10">
                              <tr>
                                <th className="p-3 border-b border-r font-medium text-left text-sm">
                                  취약 항목
                                </th>
                                <th className="p-3 border-b font-medium text-left text-sm">
                                  대응방안
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {(hasExcelData
                                ? dynamicVulnerabilityDetails
                                : vulnerabilityDetails
                              ).length > 0 ? (
                                (hasExcelData
                                  ? dynamicVulnerabilityDetails
                                  : vulnerabilityDetails
                                ).map((item, index) => (
                                  <tr
                                    key={item.id}
                                    className={`${index % 2 === 0 ? "bg-white" : "bg-muted/10"} hover:bg-muted/20 border-b transition-colors`}
                                  >
                                    <td className="p-4 border-r text-sm leading-relaxed">
                                      {item.vulnerability}
                                    </td>
                                    <td className="p-4 text-sm leading-relaxed">
                                      {item.countermeasure}
                                    </td>
                                  </tr>
                                ))
                              ) : (
                                <tr>
                                  <td colSpan={2} className="p-8 text-center text-muted-foreground">
                                    취약점이 발견되지 않았습니다.
                                  </td>
                                </tr>
                              )}
                            </tbody>
                          </table>
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
                  {modalContent.type === "success" && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                  {modalContent.type === "error" && (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                  {modalContent.type === "info" && (
                    <Clock className="h-5 w-5 text-blue-500" />
                  )}
                  <CardTitle className="text-base">
                    {modalContent.title}
                  </CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="font-medium">
                    {modalContent.message}
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

      {/* 진단 완료 모달 */}
      {showDiagnosisCompleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowDiagnosisCompleteModal(false)}
          />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <CardTitle className="text-base">
                    자동 진단 완료
                  </CardTitle>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    setShowDiagnosisCompleteModal(false)
                  }
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="font-medium">
                    자동 진단이 완료되었습니다.
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

      {/* 보고서 요약 완료 모달 */}
      {showSummaryCompleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setShowSummaryCompleteModal(false)}
          />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <CardTitle className="text-base">
                    보고서 요약 완료
                  </CardTitle>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    setShowSummaryCompleteModal(false)
                  }
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div>
                  <div className="font-medium">
                    보고서 요약이 완료되었습니다.
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
    </>
  );
}
