import { useState } from "react";
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
import { Input } from "./input";
import { Checkbox } from "./checkbox";
import { Progress } from "./progress";
import { Separator } from "./separator";
import { Alert, AlertDescription, AlertTitle } from "./alert";
import { ScrollArea } from "./scroll-area";
import {
  Upload,
  Copy,
  Check,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
  Loader2,
  Info,
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip";
import { toast } from "sonner";

// DB 체크리스트 데이터 (50개 항목)
const dbItems = [
  {
    id: 1,
    name: "DB 접근 제어",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 2,
    name: "DB 권한 관리",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 3,
    name: "데이터 암호화",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 4,
    name: "DB 감사 로그",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 5,
    name: "백업 및 복구",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 6,
    name: "DB 서버 보안 설정",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 7,
    name: "사용자 계정 관리",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 8,
    name: "패스워드 정책",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 9,
    name: "DB 연결 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 10,
    name: "데이터 마스킹",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 11,
    name: "SQL 인젝션 방어",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 12,
    name: "테이블 접근 권한",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 13,
    name: "뷰 권한 관리",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 14,
    name: "저장 프로시저 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 15,
    name: "트리거 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 16,
    name: "인덱스 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 17,
    name: "파티션 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 18,
    name: "시스템 권한",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 19,
    name: "객체 권한",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 20,
    name: "롤 기반 접근제어",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 21,
    name: "DB 모니터링",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 22,
    name: "성능 모니터링",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 23,
    name: "용량 관리",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 24,
    name: "임시 테이블 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 25,
    name: "로그 파일 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 26,
    name: "아카이브 로그 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 27,
    name: "리두 로그 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 28,
    name: "언두 세그먼트 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 29,
    name: "테이블스페이스 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 30,
    name: "DB 링크 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 31,
    name: "시노님 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 32,
    name: "시퀀스 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 33,
    name: "클러스터 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 34,
    name: "파티션 테이블 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 35,
    name: "인덱스 파티션 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 36,
    name: "구체화된 뷰 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 37,
    name: "패키지 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 38,
    name: "함수 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 39,
    name: "타입 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 40,
    name: "자바 소스 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 41,
    name: "XML 스키마 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 42,
    name: "디렉토리 객체 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 43,
    name: "외부 테이블 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 44,
    name: "스케줄러 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 45,
    name: "큐 테이블 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 46,
    name: "Advanced Queuing 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 47,
    name: "스트림 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 48,
    name: "리소스 관리자 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 49,
    name: "데이터 가드 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 50,
    name: "RAC 보안 설정",
    status: { good: false, vulnerable: false, dangerous: true },
  },
];

// WEB 체크리스트 데이터 (50개 항목)
const webItems = [
  {
    id: 1,
    name: "웹 입력값 검증",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 2,
    name: "보안 헤더 설정",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 3,
    name: "세션 관리",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 4,
    name: "파일 업로드 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 5,
    name: "HTTPS 적용",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 6,
    name: "XSS 방어",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 7,
    name: "CSRF 방어",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 8,
    name: "클릭재킹 방어",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 9,
    name: "SQL 인젝션 방어",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 10,
    name: "인증 시스템",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 11,
    name: "권한 관리",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 12,
    name: "쿠키 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 13,
    name: "로그인 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 14,
    name: "패스워드 정책",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 15,
    name: "계정 잠금 정책",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 16,
    name: "다중 인증",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 17,
    name: "API 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 18,
    name: "웹서비스 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 19,
    name: "Ajax 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 20,
    name: "JSON 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 21,
    name: "XML 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 22,
    name: "웹소켓 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 23,
    name: "CORS 설정",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 24,
    name: "CSP 정책",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 25,
    name: "HSTS 설정",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 26,
    name: "서버 정보 숨김",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 27,
    name: "에러 페이지 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 28,
    name: "디렉토리 리스팅 방지",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 29,
    name: "백업 파일 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 30,
    name: "로그 파일 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 31,
    name: "웹 방화벽 설정",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 32,
    name: "DDoS 방어",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 33,
    name: "Rate Limiting",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 34,
    name: "캐시 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 35,
    name: "CDN 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 36,
    name: "로드밸런서 보안",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 37,
    name: "프록시 보안",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 38,
    name: "리버스 프록시 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 39,
    name: "SSL/TLS 설정",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 40,
    name: "인증서 관리",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 41,
    name: "인증서 검증",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 42,
    name: "암호화 통신",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 43,
    name: "보안 프로토콜",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 44,
    name: "네트워크 보안",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 45,
    name: "방화벽 설정",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 46,
    name: "침입 탐지",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 47,
    name: "침입 방지",
    status: { good: false, vulnerable: true, dangerous: false },
  },
  {
    id: 48,
    name: "보안 모니터링",
    status: { good: false, vulnerable: false, dangerous: true },
  },
  {
    id: 49,
    name: "로그 분석",
    status: { good: true, vulnerable: false, dangerous: false },
  },
  {
    id: 50,
    name: "보안 감사",
    status: { good: false, vulnerable: true, dangerous: false },
  },
];

// AI 추가진단 샘플 텍스트
const aiSampleTexts = {
  threatAnalysis:
    "추가 위협 공격에 대해 안내해드립니다. 자세한 내용을 확인하고 싶으시면 생성을 눌러주세요.",
  yaraRule: "공격을 방어할 수 있는 Yara Rule을 추천드립니다. 자세한 내용을 확인하고 싶으시면 생성을 눌러주세요.",
};

// 취약점 대응방안 데이터
const vulnerabilityCountermeasures = {
  db: {
    1: "계정 잠금 정책 설정: 연속 로그인 실패 횟수 제한 및 계정 잠금 시간 설정",
    2: "사용자 인증 강화: 다단계 인증(MFA) 도입 및 권한 세분화 관리",
    3: "데이터 암호화 적용: 민감 데이터에 대한 암호화 정책 수립 및 키 관리 시스템 구축",
    4: "감사 로그 정책 수립: 로그 수집 범위 확대 및 정기적 모니터링 체계 구축",
    5: "백업 보안 강화: 백업 데이터 암호화 및 정기적 복구 테스트 실시",
    6: "DB 서버 보안 설정: 불필요한 서비스 제거 및 보안 패치 정기 적용",
    7: "사용자 계정 관리 강화: 최소 권한 원칙 적용 및 정기적 권한 검토",
    8: "패스워드 정책 강화: 복잡도 요구사항 설정 및 정기적 변경 강제",
    9: "DB 연결 보안 강화: SSL/TLS 암호화 연결 적용 및 방화벽 설정",
    10: "데이터 마스킹 적용: 민감 정보에 대한 마스킹 처리 및 접근 로그 관리",
    11: "SQL 인젝션 방어: 매개변수화 쿼리 적용 및 입력값 검증 강화",
    12: "테이블 접근 권한 관리: 세분화된 권한 설정 및 정기적 권한 검토",
    13: "뷰 권한 관리 강화: 뷰 기반 접근 제어 및 민감 정보 보호",
    14: "스토어드 프로시저 보안: 권한 최소화 및 보안 검토 프로세스 구축",
    15: "트리거 보안 관리: 트리거 실행 권한 제한 및 보안 감사",
    16: "인덱스 보안 설정: 민감 정보 인덱스 보호 및 접근 제어",
    17: "파티션 보안 관리: 데이터 분할 및 접근 권한 세분화",
    18: "클러스터 보안 설정: 노드 간 통신 암호화 및 인증 강화",
    19: "복제 보안 강화: 마스터-슬레이브 통신 보안 및 데이터 동기화 보호",
    20: "샤딩 보안 관리: 샤드 간 보안 통신 및 데이터 분산 보호",
  },
  web: {
    1: "입력값 검증 강화: SQL 인젝션 방어를 위한 매개변수화 쿼리 적용 및 입력값 검증 로직 강화",
    2: "보안 헤더 설정: Content-Security-Policy, X-Frame-Options 등 보안 헤더 적용",
    3: "세션 보안 강화: 세션 타임아웃 설정 및 안전한 쿠키 정책 적용",
    4: "파일 업로드 보안: 파일 확장자 검증, 악성 파일 스캔 및 업로드 크기 제한",
    5: "XSS 방어 ��화: 출력값 인코딩 및 CSP 정책 적용",
    6: "CSRF 방어 적용: CSRF 토큰 검증 및 SameSite 쿠키 설정",
    7: "인증 보안 강화: 강력한 인증 메커니즘 및 계정 잠금 정책 적용",
    8: "권한 관리 개선: RBAC 모델 적용 및 최소 권한 원칙 준수",
    9: "API 보안 강화: API 인증/인가 및 Rate Limiting 적용",
    10: "암호화 통신 적용: HTTPS 강제 적용 및 TLS 설정 최적화",
    11: "에러 처리 보안: 민감 정보 노출 방지 및 사용자 친화적 에러 메시지",
    12: "로깅 보안 강화: 보안 이벤트 로깅 및 실시간 모니터링 구축",
    13: "취약점 스캔 정기화: 정기적 보안 스캔 및 취약점 패치 관리",
    14: "보안 테스트 강화: 침투 테스트 및 보안 코드 리뷰 정기 실시",
    15: "Third-party 보안: 외부 라이브러리 보안 검증 및 정기 업데이트",
    16: "배포 보안 강화: 안전한 배포 프로세스 및 롤백 체계 구축",
    17: "모니터링 강화: 실시간 보안 모니터링 및 이상 탐지 시스템 구축",
    18: "백업 보안 적용: 웹 데이터 백업 암호화 및 복구 절차 정립",
    19: "네트워크 보안: 방화벽 설정 최적화 및 네트워크 분할 적용",
    20: "컨테이너 보안: 컨테이너 이미지 보안 검증 및 런타임 보안 적용",
    21: "클라우드 보안: 클라우드 보안 설정 최적화 및 IAM 정책 관리",
    22: "DevSecOps 적용: 개발 프로세스에 보안 검토 통합",
    23: "CORS 설정 최적화: 적절한 CORS 정책 설정 및 도메인 제한",
    24: "CSP 정책 강화: 콘텐츠 보안 정책 세밀 설정 및 인라인 스크립트 제한",
    25: "HSTS 적용: HTTP Strict Transport Security 헤더 설정",
    26: "서버 정보 숨김: 서버 정보 헤더 제거 및 기술 스택 정보 보호",
    27: "에러 페이지 보안: 커스텀 에러 페이지 적용 및 민감 정보 노출 방지",
    28: "디렉토리 리스팅 방지: 웹 서버 디렉토리 브라우징 비활성화",
    29: "백업 파일 보안: 웹 루트에서 백업 파일 제거 및 접근 차단",
    30: "로그 파일 보안: 로그 파일 접근 제한 및 민감 정보 로깅 방지",
    31: "웹 방화벽 설정: WAF 규칙 최적화 및 공격 패턴 차단",
    32: "DDoS 방어 강화: DDoS 탐지 및 완화 솔루션 적용",
    33: "Rate Limiting 적용: API 및 리소스 접근 속도 제한 설정",
    34: "캐시 보안 강화: 민감 정보 캐싱 방지 및 캐시 헤더 설정",
    35: "CDN 보안 설정: CDN 보안 설정 최적화 및 원본 서버 보호",
    36: "로드밸런서 보안: 로드밸런서 보안 설정 및 건강 상태 검사 보안",
    37: "프록시 보안 강화: 프록시 서버 보안 설정 및 헤더 검증",
    38: "리버스 프록시 보안: 리버스 프록시 보안 설정 및 백엔드 서버 보호",
    39: "SSL/TLS 설정 강화: 최신 TLS 버전 적용 및 약한 암호화 방식 제거",
    40: "인증서 관리 강화: 인증서 자동 갱신 및 만료 모니터링 구축",
    41: "인증서 검증 강화: 인증서 체인 검증 및 OCSP 스테이플링 적용",
    42: "암호화 통신 강화: 엔드투엔드 암호화 및 Perfect Forward Secrecy 적용",
    43: "보안 프로토콜 적용: 최신 보안 프로토콜 적용 및 레거시 프로토콜 제거",
    44: "네트워크 보안 강화: 네트워크 세분화 및 마이크로 세그멘테이션 적용",
    45: "방화벽 설정 최적화: 차세대 방화벽 적용 및 규칙 정기 검토",
    46: "침입 탐지 시스템: IDS/IPS 적용 및 실시간 위협 탐지",
    47: "침입 방지 강화: 행위 기반 탐지 및 자동 차단 메커니즘 구축",
    48: "보안 모니터링 강화: SIEM 솔루션 적용 및 보안 대시보드 구축",
    49: "로그 분석 자동화: 로그 분석 자동화 및 이상 행위 패턴 탐지",
    50: "보안 감사 정기화: 정기적 보안 감사 및 컴플라이언스 점검 실시",
  },
};

export default function TechConsultingPanel() {
  const [uploadedDBFile, setUploadedDBFile] =
    useState<File | null>(null);
  const [uploadedWebFile, setUploadedWebFile] =
    useState<File | null>(null);

  // 각 탭별 독립적인 진단 로딩 상태
  const [isDBDiagnosing, setDBDiagnosing] = useState(false);
  const [dbProgress, setDBProgress] = useState(0);
  const [isWebDiagnosing, setWebDiagnosing] = useState(false);
  const [webProgress, setWebProgress] = useState(0);

  // 각 탭별 독립적인 요약 로딩 상태
  const [isDBSummarizing, setDBSummarizing] = useState(false);
  const [dbSummaryProgress, setDBSummaryProgress] = useState(0);
  const [isWebSummarizing, setWebSummarizing] = useState(false);
  const [webSummaryProgress, setWebSummaryProgress] = useState(0);

  // AI 추가진단 상태를 각 탭별로 완전 분리
  const [summaryDBSAI, setSummaryDBSAI] = useState({
    show: false,
    loading: false,
  });
  const [summaryWebAI, setSummaryWebAI] = useState({
    show: false,
    loading: false,
  });
  const [diagnosisDBSAI, setDiagnosisDBSAI] = useState({
    show: false,
    loading: false,
  });
  const [diagnosisWebAI, setDiagnosisWebAI] = useState({
    show: false,
    loading: false,
  });

  const [copiedField, setCopiedField] = useState<string | null>(
    null,
  );

  // 각 섹션별 독립적인 탭 상태
  const [summarySelectedTab, setSummarySelectedTab] =
    useState("db");
  const [diagnosisSelectedTab, setDiagnosisSelectedTab] =
    useState("db");

  // 각 탭별 독립적인 완료 상태
  const [summaryDBGenerated, setSummaryDBGenerated] =
    useState(false);
  const [summaryWebGenerated, setSummaryWebGenerated] =
    useState(false);
  const [diagnosisDBCompleted, setDiagnosisDBCompleted] =
    useState(false);
  const [diagnosisWebCompleted, setDiagnosisWebCompleted] =
    useState(false);

  // 각 섹션별 독립적인 체크박스 상태
  const [summaryCheckedItems, setSummaryCheckedItems] =
    useState<{
      [key: string]: {
        good: boolean;
        vulnerable: boolean;
        dangerous: boolean;
      };
    }>({});
  const [diagnosisCheckedItems, setDiagnosisCheckedItems] =
    useState<{
      [key: string]: {
        good: boolean;
        vulnerable: boolean;
        dangerous: boolean;
      };
    }>({});
  const [siteUrl, setSiteUrl] = useState("");
  const [savedSiteUrl, setSavedSiteUrl] = useState("");
  
  // DB 계정 관련 상태
  const [dbAccount, setDbAccount] = useState("");
  const [savedDbAccount, setSavedDbAccount] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState({
    title: "",
    message: "",
    type: "info" as "info" | "success" | "error",
  });

  const showModalMessage = (
    title: string,
    message: string,
    type: "info" | "success" | "error" = "info",
  ) => {
    setModalContent({ title, message, type });
    setShowModal(true);
    setTimeout(() => setShowModal(false), 2000);
  };

  // 탭별 요약 로딩 함수
  const startDBSummary = async () => {
    setDBSummarizing(true);
    setDBSummaryProgress(10);
    // demo 로딩 진행
    const steps = [25, 45, 70, 90, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setDBSummaryProgress(p);
    }
    setDBSummarizing(false);
  };

  const startWebSummary = async () => {
    setWebSummarizing(true);
    setWebSummaryProgress(10);
    // demo 로딩 진행
    const steps = [25, 45, 70, 90, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setWebSummaryProgress(p);
    }
    setWebSummarizing(false);
  };

  const handleDBFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedDBFile(file);
      
      // DB 요약 관련 상태 초기화
      setSummaryDBGenerated(false);
      setDBSummarizing(false);
      setDBSummaryProgress(0);
      
      // DB 체크박스 상태 초기화
      const resetDBItems: { [key: string]: { good: boolean; vulnerable: boolean; dangerous: boolean } } = {};
      dbItems.forEach((item) => {
        const key = `db-${item.id}`;
        resetDBItems[key] = { good: false, vulnerable: false, dangerous: false };
      });
      
      setSummaryCheckedItems((prev) => ({
        ...prev,
        ...resetDBItems,
      }));

      // AI 추가진단 상태 초기화
      setSummaryDBSAI({ show: false, loading: false });

      showModalMessage(
        "DB 파일 업로드",
        `DB 파일 ${file.name}이 업로드되었습니다!`,
        "success",
      );
    }
  };

  const handleWebFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedWebFile(file);
      
      // WEB 요약 관련 상태 초기화
      setSummaryWebGenerated(false);
      setWebSummarizing(false);
      setWebSummaryProgress(0);
      
      // WEB 체크박스 상태 초기화
      const resetWebItems: { [key: string]: { good: boolean; vulnerable: boolean; dangerous: boolean } } = {};
      webItems.forEach((item) => {
        const key = `web-${item.id}`;
        resetWebItems[key] = { good: false, vulnerable: false, dangerous: false };
      });
      
      setSummaryCheckedItems((prev) => ({
        ...prev,
        ...resetWebItems,
      }));

      // AI 추가진단 상태 초기화
      setSummaryWebAI({ show: false, loading: false });

      showModalMessage(
        "WEB 파일 업로드",
        `WEB 파일 ${file.name}이 업로드되었습니다!`,
        "success",
      );
    }
  };

  const handleSummary = async () => {
    const currentFile =
      summarySelectedTab === "db"
        ? uploadedDBFile
        : uploadedWebFile;
    if (!currentFile) {
      showModalMessage(
        "파일 업로드 필요",
        `${summarySelectedTab.toUpperCase()} 파일을 먼저 업로드해주세요.`,
        "error",
      );
      return;
    }

    // 현재 선택된 탭에 따라 해당 탭의 로딩 시작
    if (summarySelectedTab === "db") {
      await startDBSummary();
    } else {
      await startWebSummary();
    }

    // 현재 선택된 탭에 따라 해당 탭만 요약 완료 처리
    const analysisResult: {
      [key: string]: {
        good: boolean;
        vulnerable: boolean;
        dangerous: boolean;
      };
    } = {};

    if (summarySelectedTab === "db") {
      // DB 탭만 처리
      setSummaryDBGenerated(true);
      dbItems.forEach((item) => {
        const key = `db-${item.id}`;
        analysisResult[key] = item.status;
      });
      showModalMessage(
        "DB 요약 완료",
        "DB 요약이 완료되었습니다.",
        "success",
      );
    } else {
      // WEB 탭만 처리
      setSummaryWebGenerated(true);
      webItems.forEach((item) => {
        const key = `web-${item.id}`;
        analysisResult[key] = item.status;
      });
      showModalMessage(
        "WEB 요약 완료",
        "WEB 요약이 완료되었습니다.",
        "success",
      );
    }

    // 기존 데이터와 병합
    setSummaryCheckedItems((prev) => ({
      ...prev,
      ...analysisResult,
    }));
  };

  const handleCopyText = async (
    text: string,
    fieldName: string,
  ) => {
    if (!text || text.trim() === "") {
      showModalMessage(
        "복사 오류",
        "복사할 내용이 없습니다.",
        "error",
      );
      return;
    }

    // 복사 성공 표시를 먼저 보여줌
    setCopiedField(fieldName);
    
    try {
      // 가장 단순한 방법부터 시도
      await navigator.clipboard.writeText(text);
      showModalMessage(
        "복사 완료",
        "복사되었습니다!",
        "success",
      );
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
          showModalMessage(
            "복사 완료",
            "복사되었습니다!",
            "success",
          );
          setTimeout(() => setCopiedField(null), 2000);
        } else {
          throw new Error('execCommand failed');
        }
      } catch (fallbackErr) {
        // 복사 실패 시 알림만 표시
        setCopiedField(null);
        showModalMessage(
          "복사 실패",
          "복사에 실패했습니다. 브라우저가 복사를 지원하지 않습니다.",
          "error",
        );
      }
    }
  };

  // 보고서 요약 탭의 AI 추가진단 생성
  const handleGenerateSummaryAI = async (
    tabType: "db" | "web",
  ) => {
    // 해당 탭의 요약이 생성되지 않았으면 에러 메시지
    const isGenerated =
      tabType === "db"
        ? summaryDBGenerated
        : summaryWebGenerated;
    if (!isGenerated) {
      showModalMessage(
        "보고서 요약 필요",
        `${tabType.toUpperCase()} 보고서 요약을 먼저 진행해주세요.`,
        "error",
      );
      return;
    }

    if (tabType === "db") {
      setSummaryDBSAI({ show: false, loading: true });
    } else {
      setSummaryWebAI({ show: false, loading: true });
    }

    showModalMessage("AI 진단", "생성을 시작합니다...", "info");

    const ai_res = await fetch("/api/ai/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ tabType }), // tabType을 JSON 형식으로 전송
    });

    // HTTP 상태 코드 확인
    if (!ai_res.ok) {
      throw new Error(`HTTP error! status: ${ai_res.status}`);
    }

    const ai_res_json = await ai_res.json();

    // 응답 데이터 검증
    if (!ai_res_json || !ai_res_json.attack || !ai_res_json.yara) {
      throw new Error("AI 응답 데이터가 올바르지 않습니다.");
    }

    // AI 응답을 샘플 텍스트에 적용
    aiSampleTexts.threatAnalysis = ai_res_json.attack;
    aiSampleTexts.yaraRule = ai_res_json.yara;


    if (tabType === "db") {
      setSummaryDBSAI({ show: true, loading: false });
    } else {
      setSummaryWebAI({ show: true, loading: false });
    }

    
    showModalMessage(
      "AI 진단 완료",
      "생성이 완료되었습니다.",
      "success",
    );
  };

  // 자동 진단 탭의 AI 추가진단 생성
  const handleGenerateDiagnosisAI = async (
    tabType: "db" | "web",
  ) => {
    // 해당 탭의 진단이 완료되지 않았으면 에러 메시지
    const isCompleted =
      tabType === "db"
        ? diagnosisDBCompleted
        : diagnosisWebCompleted;
    if (!isCompleted) {
      showModalMessage(
        "자동 진단 필요",
        `${tabType.toUpperCase()} 자동 진단을 먼저 진행해주세요.`,
        "error",
      );
      return;
    }

    if (tabType === "db") {
      setDiagnosisDBSAI({ show: false, loading: true });
    } else {
      setDiagnosisWebAI({ show: false, loading: true });
    }

    showModalMessage("AI 진단", "생성을 시작합니다...", "info");

    const ai_res = await fetch("/api/ai/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ tabType }), // tabType을 JSON 형식으로 전송
    });

    // HTTP 상태 코드 확인
    if (!ai_res.ok) {
      throw new Error(`HTTP error! status: ${ai_res.status}`);
    }

    const ai_res_json = await ai_res.json();

    // 응답 데이터 검증
    if (!ai_res_json || !ai_res_json.attack || !ai_res_json.yara) {
      throw new Error("AI 응답 데이터가 올바르지 않습니다.");
    }

    // AI 응답을 샘플 텍스트에 적용
    aiSampleTexts.threatAnalysis = ai_res_json.attack;
    aiSampleTexts.yaraRule = ai_res_json.yara;

    if (tabType === "db") {
      setDiagnosisDBSAI({ show: true, loading: false });
    } else {
      setDiagnosisWebAI({ show: true, loading: false });
    }

    showModalMessage(
      "AI 진단 완료",
      "생성이 완료되었습니다.",
      "success",
    );
  };

  // 취약한 항목들과 대응방안을 가져오는 함수 (보고서 요약용)
  const getSummaryVulnerableItems = (tabType: "db" | "web") => {
    const vulnerableItems: Array<{
      name: string;
      countermeasure: string;
    }> = [];

    if (tabType === "db") {
      dbItems.forEach((item) => {
        const key = `db-${item.id}`;
        const itemStatus = summaryCheckedItems[key];
        if (
          itemStatus &&
          (itemStatus.vulnerable || itemStatus.dangerous)
        ) {
          vulnerableItems.push({
            name: item.name,
            countermeasure:
              vulnerabilityCountermeasures.db[
                item.id as keyof typeof vulnerabilityCountermeasures.db
              ] || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`,
          });
        }
      });
    } else {
      webItems.forEach((item) => {
        const key = `web-${item.id}`;
        const itemStatus = summaryCheckedItems[key];
        if (
          itemStatus &&
          (itemStatus.vulnerable || itemStatus.dangerous)
        ) {
          vulnerableItems.push({
            name: item.name,
            countermeasure:
              vulnerabilityCountermeasures.web[
                item.id as keyof typeof vulnerabilityCountermeasures.web
              ] || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`,
          });
        }
      });
    }

    return vulnerableItems;
  };

  // 취약한 항목들과 대응방안을 가져오는 함수 (자동 진단용)
  const getDiagnosisVulnerableItems = (
    tabType: "db" | "web",
  ) => {
    const vulnerableItems: Array<{
      name: string;
      countermeasure: string;
    }> = [];

    if (tabType === "db") {
      dbItems.forEach((item) => {
        const key = `db-${item.id}`;
        const itemStatus = diagnosisCheckedItems[key];
        if (
          itemStatus &&
          (itemStatus.vulnerable || itemStatus.dangerous)
        ) {
          vulnerableItems.push({
            name: item.name,
            countermeasure:
              vulnerabilityCountermeasures.db[
                item.id as keyof typeof vulnerabilityCountermeasures.db
              ] || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`,
          });
        }
      });
    } else {
      webItems.forEach((item) => {
        const key = `web-${item.id}`;
        const itemStatus = diagnosisCheckedItems[key];
        if (
          itemStatus &&
          (itemStatus.vulnerable || itemStatus.dangerous)
        ) {
          vulnerableItems.push({
            name: item.name,
            countermeasure:
              vulnerabilityCountermeasures.web[
                item.id as keyof typeof vulnerabilityCountermeasures.web
              ] || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`,
          });
        }
      });
    }

    return vulnerableItems;
  };

  const handleSiteInput = () => {
    if (!siteUrl.trim()) {
      showModalMessage(
        "URL 입력 필요",
        "사이트 URL을 입력해주세요.",
        "error",
      );
      return;
    }
    
    // 기존 URL과 다른 경우에만 진단 결과 초기화
    if (savedSiteUrl && savedSiteUrl !== siteUrl.trim()) {
      // WEB 진단 관련 상태 초기화
      setDiagnosisWebCompleted(false);
      setWebDiagnosing(false);
      setWebProgress(0);
      
      // WEB 체크박스 상태 초기화
      const resetWebItems: { [key: string]: { good: boolean; vulnerable: boolean; dangerous: boolean } } = {};
      webItems.forEach((item) => {
        const key = `web-${item.id}`;
        resetWebItems[key] = { good: false, vulnerable: false, dangerous: false };
      });
      
      setDiagnosisCheckedItems((prev) => ({
        ...prev,
        ...resetWebItems,
      }));

      // AI 추가진단 상태 초기화
      setDiagnosisWebAI({ show: false, loading: false });
    }
    
    // 사이트 URL을 저장
    setSavedSiteUrl(siteUrl.trim());
    showModalMessage(
      "사이트 입력 완료",
      "사이트가 입력되었습니다.",
      "success",
    );
  };

  // WEB 자동진단 사이트 재입력 함수
  const handleWebDiagnosisReset = () => {
    // 사이트 URL 입력 상태로 되돌림
    setSiteUrl(savedSiteUrl || "");
    setSavedSiteUrl("");
    
    // WEB 진단 관련 상태 초기화
    setDiagnosisWebCompleted(false);
    setWebDiagnosing(false);
    setWebProgress(0);
    
    // WEB 체크박스 상태 초기화
    const resetWebItems: { [key: string]: { good: boolean; vulnerable: boolean; dangerous: boolean } } = {};
    webItems.forEach((item) => {
      const key = `web-${item.id}`;
      resetWebItems[key] = { good: false, vulnerable: false, dangerous: false };
    });
    
    setDiagnosisCheckedItems((prev) => ({
      ...prev,
      ...resetWebItems,
    }));

    // AI 추가진단 상태 초기화
    setDiagnosisWebAI({ show: false, loading: false });

    showModalMessage(
      "사이트 재입력 준비",
      "사이트 URL을 새로 입력해주세요.",
      "success",
    );
  };

  // DB 진단 함수
  const handleDBDiagnosis = async () => {
    if (!savedDbAccount) {
      showModalMessage(
        "계정 입력 필요",
        "DB 계정을 먼저 입력해주세요.",
        "error",
      );
      return;
    }

    setDBDiagnosing(true);
    setDBProgress(15);
    showModalMessage(
      "DB 자동 진단",
      "DB 자동 진단을 시작합니다...",
      "info",
    );

    const steps = [35, 55, 80, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setDBProgress(p);
    }

    // DB 탭 진단 완료 처리
    const analysisResult: {
      [key: string]: {
        good: boolean;
        vulnerable: boolean;
        dangerous: boolean;
      };
    } = {};

    setDiagnosisDBCompleted(true);
    dbItems.forEach((item) => {
      const key = `db-${item.id}`;
      analysisResult[key] = item.status;
    });

    setDBDiagnosing(false);
    // 기존 데이터와 병합
    setDiagnosisCheckedItems((prev) => ({
      ...prev,
      ...analysisResult,
    }));

    showModalMessage(
      "DB 진단 완료",
      "DB 진단이 완료되었습니다.",
      "success",
    );
  };

  // DB 계정 입력 함수
  const handleDbAccountInput = () => {
    if (!dbAccount.trim()) {
      showModalMessage(
        "계정 입력 필요",
        "DB 계정을 입력해주세요.",
        "error",
      );
      return;
    }
    
    // 기존 계정과 다른 경우에만 진단 결과 초기화
    if (savedDbAccount && savedDbAccount !== dbAccount.trim()) {
      // DB 진단 관련 상태 초기화
      setDiagnosisDBCompleted(false);
      setDBDiagnosing(false);
      setDBProgress(0);
      
      // DB 체크박스 상태 초기화
      const resetDBItems: { [key: string]: { good: boolean; vulnerable: boolean; dangerous: boolean } } = {};
      dbItems.forEach((item) => {
        const key = `db-${item.id}`;
        resetDBItems[key] = { good: false, vulnerable: false, dangerous: false };
      });
      
      setDiagnosisCheckedItems((prev) => ({
        ...prev,
        ...resetDBItems,
      }));

      // AI 추가진단 상태 초기화
      setDiagnosisDBSAI({ show: false, loading: false });
    }
    
    // DB 계정을 저장
    setSavedDbAccount(dbAccount.trim());
    showModalMessage(
      "계정 입력 완료",
      "계정이 입력되었습니다.",
      "success",
    );
  };

  // DB 자동진단 계정 재입력 함수
  const handleDbDiagnosisReset = () => {
    // 계정 입력 상태로 되돌림
    setDbAccount(savedDbAccount || "");
    setSavedDbAccount("");
    
    // DB 진단 관련 상태 초기화
    setDiagnosisDBCompleted(false);
    setDBDiagnosing(false);
    setDBProgress(0);
    
    // DB 체크박스 상태 초기화
    const resetDBItems: { [key: string]: { good: boolean; vulnerable: boolean; dangerous: boolean } } = {};
    dbItems.forEach((item) => {
      const key = `db-${item.id}`;
      resetDBItems[key] = { good: false, vulnerable: false, dangerous: false };
    });
    
    setDiagnosisCheckedItems((prev) => ({
      ...prev,
      ...resetDBItems,
    }));

    // AI 추가진단 상태 초기화
    setDiagnosisDBSAI({ show: false, loading: false });

    showModalMessage(
      "계정 재입력 준비",
      "DB 계정을 새로 입력해주세요.",
      "success",
    );
  };

  // WEB 진단 함수
  const handleWebDiagnosis = async () => {
    if (!savedSiteUrl) {
      showModalMessage(
        "URL 입력 필요",
        "사이트 URL을 먼저 입력해주세요.",
        "error",
      );
      return;
    }

    setWebDiagnosing(true);
    setWebProgress(15);
    showModalMessage(
      "WEB 자동 진단",
      "WEB 자동 진단을 시작합니다...",
      "info",
    );

    const steps = [35, 55, 80, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setWebProgress(p);
    }

    // WEB 탭 진단 완료 처리
    const analysisResult: {
      [key: string]: {
        good: boolean;
        vulnerable: boolean;
        dangerous: boolean;
      };
    } = {};

    setDiagnosisWebCompleted(true);
    webItems.forEach((item) => {
      const key = `web-${item.id}`;
      analysisResult[key] = item.status;
    });

    setWebDiagnosing(false);
    // 기존 데이터와 병합
    setDiagnosisCheckedItems((prev) => ({
      ...prev,
      ...analysisResult,
    }));

    showModalMessage(
      "WEB 진단 완료",
      "WEB 진단이 완료되었습니다.",
      "success",
    );
  };

  // AI 진단 컴포넌트 (재사용 가능)
  const AIComponent = ({
    aiState,
    tabType,
    sectionType,
  }: {
    aiState: { show: boolean; loading: boolean };
    tabType: "db" | "web";
    sectionType: "summary" | "diagnosis";
  }) => {
    const handleGenerate = () => {
      if (sectionType === "summary") {
        handleGenerateSummaryAI(tabType);
      } else {
        handleGenerateDiagnosisAI(tabType);
      }
    };

    return (
      <div className="border-t pt-4 flex-shrink-0">
        <div className="flex items-center justify-between mb-4">
          <h3>AI 추가진단</h3>
          <Button
            variant="outline"
            size="sm"
            onClick={handleGenerate}
            disabled={aiState.loading}
            className="gap-2"
          >
            {aiState.loading && (
              <Loader2 className="h-3 w-3 animate-spin" />
            )}
            {aiState.loading ? "생성 중..." : "생성"}
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {/* 1. 추가 위협 예측 */}
          <div className="space-y-3">
            <h4>1. 추가 위협 예측</h4>
            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px] flex items-center justify-center">
              {aiState.loading ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  로딩중...
                </div>
              ) : aiState.show ? (
                <div className="text-left w-full">
                  {aiSampleTexts.threatAnalysis}
                </div>
              ) : (
                <div className="text-muted-foreground">
                  생성 버튼을 눌러주세요.
                </div>
              )}
            </div>
          </div>

          {/* 2. 추가 위협에 대한 YARA Rule 생성 */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4>2. 추가 위협에 대한 YARA Rule 생성</h4>
              {aiState.show && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    handleCopyText(
                      aiSampleTexts.yaraRule,
                      `${sectionType}-${tabType}-yaraRule`,
                    )
                  }
                  className="gap-1 h-8 px-2"
                >
                  {copiedField ===
                  `${sectionType}-${tabType}-yaraRule` ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                  복사
                </Button>
              )}
            </div>
            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px] flex items-center justify-center">
              {aiState.loading ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  로딩중...
                </div>
              ) : aiState.show ? (
                <div className="text-left w-full">
                  {aiSampleTexts.yaraRule}
                </div>
              ) : (
                <div className="text-muted-foreground">
                  생성 버튼을 눌러주세요.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };
  return (
    <>
      <Card className="flex flex-col h-full">
        <CardHeader>
          <CardTitle>기술 컨설팅</CardTitle>
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
                      <p className="max-w-xs">요약이 필요한 진단 결과 보고서를 업로드하면 각 진단 항목의 취약 여부를 체크하고, 취약점과 대응방안을 요약합니다.</p>
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
                      <p className="max-w-xs">진단 옵션(DB/WEB)을 선택한 후, 진단이 필요한 DB 계정/사이트의 URL을 입력하면 각 항목의 취약 여부를 자동으로 진단하고, 취약점과 대응방안을 요약합니다.</p>
                    </TooltipContent>
                  </Tooltip>
                </TabsTrigger>
              </TabsList>

            {/* 보고서 요약 */}
            <TabsContent
              value="summary"
              className="flex-1 flex flex-col space-y-4"
            >
              {/* DB/WEB 탭 선택 */}
              <Tabs
                value={summarySelectedTab}
                onValueChange={setSummarySelectedTab}
                className="w-full"
              >
                <TabsList className="w-full grid grid-cols-2">
                  <TabsTrigger value="db">DB</TabsTrigger>
                  <TabsTrigger value="web">WEB</TabsTrigger>
                </TabsList>
              </Tabs>

              {/* DB 탭 - 업로드된 파일 표시 + 버튼들 */}
              {summarySelectedTab === "db" && (
                <div className="flex gap-2 items-center justify-between">
                  <div className="flex-1">
                    {uploadedDBFile ? (
                      <p className="text-sm text-muted-foreground">
                        업로드된 DB 파일: {uploadedDBFile.name}
                      </p>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        DB 보고서 파일을 업로드해주세요.
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2 items-center">
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
                      <label>
                        {uploadedDBFile
                          ? "보고서 재업로드"
                          : "보고서 업로드"}
                        <input
                          type="file"
                          accept=".xlsx,.xls"
                          onChange={handleDBFileUpload}
                          className="hidden"
                        />
                      </label>
                    </Button>
                    <Button
                      onClick={handleSummary}
                      disabled={isDBSummarizing || !uploadedDBFile}
                      className="gap-2"
                    >
                      {isDBSummarizing && <Loader2 className="h-4 w-4 animate-spin" />}
                      {isDBSummarizing ? "요약 중..." : "요약"}
                    </Button>
                  </div>
                </div>
              )}

              {/* WEB 탭 - 업로드된 파일 표시 + 버튼들 */}
              {summarySelectedTab === "web" && (
                <div className="flex gap-2 items-center justify-between">
                  <div className="flex-1">
                    {uploadedWebFile ? (
                      <p className="text-sm text-muted-foreground">
                        업로드된 WEB 파일: {uploadedWebFile.name}
                      </p>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        WEB 보고서 파일을 업로드해주세요.
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2 items-center">
                    <Button
                      variant="outline"
                      className="gap-2"
                      asChild
                    >
                      <label>
                        {uploadedWebFile
                          ? "보고서 재업로드"
                          : "보고서 업로드"}
                        <input
                          type="file"
                          accept=".xlsx,.xls"
                          onChange={handleWebFileUpload}
                          className="hidden"
                        />
                      </label>
                    </Button>
                    <Button
                      onClick={handleSummary}
                      disabled={isWebSummarizing || !uploadedWebFile}
                      className="gap-2"
                    >
                      {isWebSummarizing && <Loader2 className="h-4 w-4 animate-spin" />}
                      {isWebSummarizing ? "요약 중..." : "요약"}
                    </Button>
                  </div>
                </div>
              )}

              {/* DB 탭 로딩 상태 */}
              {summarySelectedTab === "db" && isDBSummarizing && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    DB 요약 생성 중…
                  </p>
                  <Progress value={dbSummaryProgress} />
                </div>
              )}

              {/* WEB 탭 로딩 상태 */}
              {summarySelectedTab === "web" && isWebSummarizing && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    WEB 요약 생성 중…
                  </p>
                  <Progress value={webSummaryProgress} />
                </div>
              )}

              {/* DB 탭 내용 */}
              {summarySelectedTab === "db" && (
                <>
              <div className="flex-1 min-h-0">
              <ScrollArea className="max-h-[400px] mt-4 border rounded-md overflow-y-auto">
                <div className="space-y-1">
                  {/* 헤더 */}
                  <header className="sticky top-0 bg-background z-50 border-b border-border">
                    <div className="grid grid-cols-4 gap-2 p-3 font-medium text-sm bg-muted">
                      <div className="text-left">항목</div>
                      <div className="text-center">양호</div>
                      <div className="text-center">취약</div>
                      <div className="text-center">위험</div>
                    </div>
                  </header>

                  {/* DB 항목들 */}
                  <div className="divide-y divide-border">
                    {dbItems.map((item) => {
                      const key = `db-${item.id}`;
                      const itemStatus =
                        summaryCheckedItems[key] || {
                          good: false,
                          vulnerable: false,
                          dangerous: false,
                        };

                      return (
                        <div
                          key={item.id}
                          className="grid grid-cols-4 gap-2 min-h-[48px] items-center p-3 text-sm leading-tight hover:bg-muted/30 transition-colors"
                        >
                          {/* 항목명 */}
                          <div className="text-left">{item.name}</div>

                          {/* Good */}
                          <div className="flex justify-center">
                            <Checkbox
                              checked={summaryDBGenerated && itemStatus.good}
                              disabled={!summaryDBGenerated}
                            />
                          </div>

                          {/* Vulnerable */}
                          <div className="flex justify-center">
                            <Checkbox
                              checked={summaryDBGenerated && itemStatus.vulnerable}
                              disabled={!summaryDBGenerated}
                            />
                          </div>

                          {/* Dangerous */}
                          <div className="flex justify-center">
                            <Checkbox
                              checked={summaryDBGenerated && itemStatus.dangerous}
                              disabled={!summaryDBGenerated}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </ScrollArea>
            </div>


                  {/* 취약점 대응방안 표 */}
                  {summaryDBGenerated && (
                      <div className="border-t pt-4">
                        <h3 className="mb-3">
                          취약점 대응방안 ({getSummaryVulnerableItems("db").length}개)
                        </h3>
                        <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                          <div className="grid grid-cols-2 gap-0 bg-muted/50 flex-shrink-0">
                            <div className="p-3 border-r font-medium">
                              취약점
                            </div>
                            <div className="p-3 font-medium">
                              대응방안
                            </div>
                          </div>
                          <div className="flex-1 overflow-y-auto min-h-[200px]">
                            {getSummaryVulnerableItems("db").length > 0 ? (
                              getSummaryVulnerableItems("db").map((item, index) => (
                                <div
                                  key={index}
                                  className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"}`}
                                >
                                  <div className="p-3 border-r border-b text-sm">
                                    {item.name}
                                  </div>
                                  <div className="p-3 border-b text-sm">
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
                      </div>
                    )}

                  {/* DB AI 추가진단 섹션 */}
                  <AIComponent
                    aiState={summaryDBSAI}
                    tabType="db"
                    sectionType="summary"
                  />
                </>
              )}

              {/* WEB 탭 내용 */}
              {summarySelectedTab === "web" && (
                <>
              <div className="flex-1 min-h-0">
              <ScrollArea className="max-h-[400px] mt-4 border rounded-md overflow-y-auto">
                    <div className="space-y-0">
                      {/* 헤더 (sticky) */}
                      <header className="sticky top-0 z-50 bg-background border-b border-border">
                        <div className="grid grid-cols-4 gap-2 p-3 font-medium text-sm text-center">
                          <div className="text-left">항목</div>
                          <div>양호</div>
                          <div>취약</div>
                          <div>위험</div>
                        </div>
                      </header>

                      {/* WEB 항목들 */}
                      <div className="divide-y divide-border">
                        {webItems.map((item) => {
                          const key = `web-${item.id}`;
                          const itemStatus =
                            summaryCheckedItems[key] || {
                              good: false,
                              vulnerable: false,
                              dangerous: false,
                            };

                          return (
                            <div
                              key={item.id}
                              className="grid grid-cols-4 gap-2 min-h-[48px] items-center p-3 text-sm leading-tight hover:bg-muted/30 transition-colors"
                            >
                              {/* 항목 이름 */}
                              <div className="text-left">{item.name}</div>

                              {/* Good */}
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={summaryWebGenerated && itemStatus.good}
                                  disabled={!summaryWebGenerated}
                                />
                              </div>

                              {/* Vulnerable */}
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={summaryWebGenerated && itemStatus.vulnerable}
                                  disabled={!summaryWebGenerated}
                                />
                              </div>

                              {/* Dangerous */}
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={summaryWebGenerated && itemStatus.dangerous}
                                  disabled={!summaryWebGenerated}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </ScrollArea>
                  </div>

                  {/* 취약점 대응방안 표 */}
                  {summaryWebGenerated && (
                      <div className="border-t pt-4">
                        <h3 className="mb-3">
                          취약점 대응방안 ({getSummaryVulnerableItems("web").length}개)
                        </h3>
                        <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                          <div className="grid grid-cols-2 gap-0 bg-muted/50 flex-shrink-0">
                            <div className="p-3 border-r font-medium">
                              취약점
                            </div>
                            <div className="p-3 font-medium">
                              대응방안
                            </div>
                          </div>
                          <div className="flex-1 overflow-y-auto min-h-[200px]">
                            {getSummaryVulnerableItems("web").length > 0 ? (
                              getSummaryVulnerableItems("web").map((item, index) => (
                                <div
                                  key={index}
                                  className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"}`}
                                >
                                  <div className="p-3 border-r border-b text-sm">
                                    {item.name}
                                  </div>
                                  <div className="p-3 border-b text-sm">
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
                      </div>
                    )}

                  {/* WEB AI 추가진단 섹션 */}
                  <AIComponent
                    aiState={summaryWebAI}
                    tabType="web"
                    sectionType="summary"
                  />
                </>
              )}
            </TabsContent>

            {/* 자동 진단 */}
            <TabsContent
              value="auto"
              className="flex-1 flex flex-col space-y-4"
            >
              {/* DB/WEB 탭 */}
              <Tabs
                value={diagnosisSelectedTab}
                onValueChange={setDiagnosisSelectedTab}
                className="flex-1 flex flex-col"
              >
                <TabsList className="w-full grid grid-cols-2">
                  <TabsTrigger value="db">DB</TabsTrigger>
                  <TabsTrigger value="web">WEB</TabsTrigger>
                </TabsList>

                {/* DB 탭 내용 */}
                <TabsContent value="db" className="flex-1 flex flex-col space-y-4 mt-4">
                  {/* DB 계정 입력 + 진단 버튼 */}
                  <div className="flex gap-2">
                    <Input
                      placeholder="DB 계정을 입력하세요 (ID:PW)"
                      value={dbAccount}
                      onChange={(e) => setDbAccount(e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={savedDbAccount ? handleDbDiagnosisReset : handleDbAccountInput}
                      disabled={isDBDiagnosing}
                    >
                      {savedDbAccount
                        ? "계정 재입력"
                        : "계정 입력"}
                    </Button>
                    <Button
                      onClick={handleDBDiagnosis}
                      disabled={isDBDiagnosing || !savedDbAccount}
                      className="gap-2"
                    >
                      {isDBDiagnosing && <Loader2 className="h-4 w-4 animate-spin" />}
                      {isDBDiagnosing ? "진단 중..." : "진단"}
                    </Button>
                  </div>

                  {/* 입력된 DB 계정 표시 */}
                  {savedDbAccount && (
                    <p className="text-sm text-muted-foreground">
                      입력된 계정: {savedDbAccount}
                    </p>
                  )}

                  {/* DB 탭 로딩 상태 */}
                  {isDBDiagnosing && (
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        DB 진단 중…
                      </p>
                      <Progress value={dbProgress} />
                    </div>
                  )}

              <div className="flex-1 min-h-0">
              <ScrollArea className="max-h-[400px] mt-4 border rounded-md overflow-y-auto">
                <div className="space-y-1">
                  <header className="sticky top-0 bg-background z-50 border-b border-border">
                  <div className="grid grid-cols-4 gap-2 p-3 font-medium text-sm bg-muted">
                    <div className="text-left">항목</div>
                    <div className="text-center">양호</div>
                    <div className="text-center">취약</div>
                    <div className="text-center">위험</div>
                  </div>
                </header>

                        {/* DB 항목들 */}
                        {dbItems.map((item) => {
                          const key = `db-${item.id}`;
                          const itemStatus =
                            diagnosisCheckedItems[key] || {
                              good: false,
                              vulnerable: false,
                              dangerous: false,
                            };
                          return (
                            <div
                              key={item.id}
                              className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50"
                            >
                              <div className="text-sm">
                                {item.name}
                              </div>
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={
                                    diagnosisDBCompleted &&
                                    itemStatus.good
                                  }
                                  disabled={
                                    !diagnosisDBCompleted
                                  }
                                />
                              </div>
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={
                                    diagnosisDBCompleted &&
                                    itemStatus.vulnerable
                                  }
                                  disabled={
                                    !diagnosisDBCompleted
                                  }
                                />
                              </div>
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={
                                    diagnosisDBCompleted &&
                                    itemStatus.dangerous
                                  }
                                  disabled={
                                    !diagnosisDBCompleted
                                  }
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>

                  {/* 취약점 대응방안 표 */}
                  {diagnosisDBCompleted && (
                      <div className="border-t pt-4">
                        <h3 className="mb-3">
                          취약점 대응방안 ({getDiagnosisVulnerableItems("db").length}개)
                        </h3>
                        <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                          <div className="grid grid-cols-2 gap-0 bg-muted/50 flex-shrink-0">
                            <div className="p-3 border-r font-medium">
                              취약점
                            </div>
                            <div className="p-3 font-medium">
                              대응방안
                            </div>
                          </div>
                          <div className="flex-1 overflow-y-auto min-h-[200px]">
                            {getDiagnosisVulnerableItems("db").length > 0 ? (
                              getDiagnosisVulnerableItems("db").map((item, index) => (
                                <div
                                  key={index}
                                  className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"}`}
                                >
                                  <div className="p-3 border-r border-b text-sm">
                                    {item.name}
                                  </div>
                                  <div className="p-3 border-b text-sm">
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
                      </div>
                    )}

                  {/* DB AI 추가진단 섹션 */}
                  <AIComponent
                    aiState={diagnosisDBSAI}
                    tabType="db"
                    sectionType="diagnosis"
                  />
                </TabsContent>

                {/* WEB 탭 내용 */}
                <TabsContent value="web" className="flex-1 flex flex-col space-y-4 mt-4">
                  {/* 사이트 URL 입력 + 진단 버튼 */}
                  <div className="flex gap-2">
                    <Input
                      placeholder="사이트 URL을 입력하세요 (https://example.com)"
                      value={siteUrl}
                      onChange={(e) => setSiteUrl(e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      onClick={savedSiteUrl ? handleWebDiagnosisReset : handleSiteInput}
                      disabled={isWebDiagnosing}
                    >
                      {savedSiteUrl
                        ? "사이트 재입력"
                        : "사이트 입력"}
                    </Button>
                    <Button
                      onClick={handleWebDiagnosis}
                      disabled={isWebDiagnosing || !savedSiteUrl}
                      className="gap-2"
                    >
                      {isWebDiagnosing && <Loader2 className="h-4 w-4 animate-spin" />}
                      {isWebDiagnosing ? "진단 중..." : "진단"}
                    </Button>
                  </div>

                  {/* 입력된 사이트 URL 표시 */}
                  {savedSiteUrl && (
                    <p className="text-sm text-muted-foreground">
                      입력된 사이트: {savedSiteUrl}
                    </p>
                  )}

                  {/* WEB 탭 로딩 상태 */}
                  {isWebDiagnosing && (
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        WEB 진단 중…
                      </p>
                      <Progress value={webProgress} />
                    </div>
                  )}

                <div className="flex-1 min-h-0">
                <ScrollArea className="max-h-[400px] mt-4 border rounded-md overflow-y-auto">
                  <div className="space-y-1">
                    <header className="sticky top-0 bg-background z-50 border-b border-border">
                    <div className="grid grid-cols-4 gap-2 p-3 font-medium text-sm bg-muted">
                      <div className="text-left">항목</div>
                      <div className="text-center">양호</div>
                      <div className="text-center">취약</div>
                      <div className="text-center">위험</div>
                    </div>
                  </header>

                        {/* WEB 항목들 */}
                        {webItems.map((item) => {
                          const key = `web-${item.id}`;
                          const itemStatus =
                            diagnosisCheckedItems[key] || {
                              good: false,
                              vulnerable: false,
                              dangerous: false,
                            };
                          return (
                            <div
                              key={item.id}
                              className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50"
                            >
                              <div className="text-sm">
                                {item.name}
                              </div>
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={
                                    diagnosisWebCompleted &&
                                    itemStatus.good
                                  }
                                  disabled={
                                    !diagnosisWebCompleted
                                  }
                                />
                              </div>
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={
                                    diagnosisWebCompleted &&
                                    itemStatus.vulnerable
                                  }
                                  disabled={
                                    !diagnosisWebCompleted
                                  }
                                />
                              </div>
                              <div className="flex justify-center">
                                <Checkbox
                                  checked={
                                    diagnosisWebCompleted &&
                                    itemStatus.dangerous
                                  }
                                  disabled={
                                    !diagnosisWebCompleted
                                  }
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>

                  {/* 취약점 대응방안 표 */}
                  {diagnosisWebCompleted && (
                      <div className="border-t pt-4">
                        <h3 className="mb-3">
                          취약점 대응방안 ({getDiagnosisVulnerableItems("web").length}개)
                        </h3>
                        <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                          <div className="grid grid-cols-2 gap-0 bg-muted/50 flex-shrink-0">
                            <div className="p-3 border-r font-medium">
                              취약점
                            </div>
                            <div className="p-3 font-medium">
                              대응방안
                            </div>
                          </div>
                          <div className="flex-1 overflow-y-auto min-h-[200px]">
                            {getDiagnosisVulnerableItems("web").length > 0 ? (
                              getDiagnosisVulnerableItems("web").map((item, index) => (
                                <div
                                  key={index}
                                  className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"}`}
                                >
                                  <div className="p-3 border-r border-b text-sm">
                                    {item.name}
                                  </div>
                                  <div className="p-3 border-b text-sm">
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
                      </div>
                    )}

                  {/* WEB AI 추가진단 섹션 */}
                  <AIComponent
                    aiState={diagnosisWebAI}
                    tabType="web"
                    sectionType="diagnosis"
                  />
                </TabsContent>
              </Tabs>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* 알림 모달 - 화면 가운데 */}
      {showModal && modalContent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* 배경 오버레이 */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setShowModal(false)}
          />

          {/* 모달 카드 */}
          <Card className="relative w-full max-w-md shadow-xl border rounded-lg animate-in fade-in-0 zoom-in-95 duration-300 bg-white z-50">
            <CardHeader className="pb-3 border-b flex flex-col items-center gap-3">
              {/* 타입별 아이콘 */}
              {modalContent.type === "success" && (
                <CheckCircle className="h-8 w-8 text-green-600" />
              )}
              {modalContent.type === "error" && (
                <AlertCircle className="h-8 w-8 text-red-600" />
              )}
              {modalContent.type === "info" && (
                <AlertCircle className="h-8 w-8 text-blue-600" />
              )}

              {/* 제목 */}
              <CardTitle className="text-2xl font-bold text-center">
                {modalContent.title}
              </CardTitle>

              {/* 닫기 버튼 */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowModal(false)}
                className="absolute top-3 right-3 h-8 w-8 p-0 flex items-center justify-center"
              >
                <X className="h-4 w-4 text-gray-500 hover:text-gray-700" />
              </Button>
            </CardHeader>

            <CardContent className="flex items-center justify-center py-8">
              <p className="text-center text-gray-800 text-base">
                {modalContent.message}
              </p>
            </CardContent>

            <div className="pt-2 border-t flex items-center gap-2 text-sm text-gray-400 justify-center pb-4">
              <Clock className="h-4 w-4" />
              방금 전
            </div>
          </Card>
        </div>
      )}

    </>
  );
}