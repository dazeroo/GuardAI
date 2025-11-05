import { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Info,
  Loader2,
  Copy,
  Check,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
interface AnalysisResultItem {
  id: string;
  name: string;
  positive: boolean;
  weakness: boolean;
  interview: boolean;
  countermeasure?: string;
}

// // 초기 진단 항목의 타입 정의
// interface ChecklistItem {
//   id: string;
//   name: string;
//   countermeasure: string;
// }
interface ChecklistItem {
  id: string;
  name: string;
  countermeasure: string;
  interview?: string; // optional
  result?: string; // optional
}

export default function TechConsultingPanel() {
  // AI 추가 진단 결과를 각 탭(summary-db, summary-web, diagnosis-db, diagnosis-web)별로 독립적으로 저장하기 위한 state 
  // 각 탭의 고유 키(예: 'summary-db')를 사용하여 AI 결과를 객체 형태로 관리
  const [aiResults, setAiResults] = useState<{
    [key: string]: {
      threatAnalysis: string;
      yaraRule: string;
    };
  }>({});


  const [dbItems, setDbItems] = useState<ChecklistItem[]>([]);
  const [webItems, setWebItems] = useState<ChecklistItem[]>([]);

  const [dbSummaryResult, setDbSummaryResult] = useState<AnalysisResultItem[]>([]);
  const [webSummaryResult, setWebSummaryResult] = useState<AnalysisResultItem[]>([]);

  const [uploadedDBFile, setUploadedDBFile] = useState<File | null>(null);
  const [uploadedWebFile, setUploadedWebFile] = useState<File | null>(null);
  const [uploadedDBFileId, setUploadedDBFileId] = useState<string | null>(null);
  const [uploadedWebFileId, setUploadedWebFileId] = useState<string | null>(null);

  const [isDBDiagnosing, setDBDiagnosing] = useState(false);
  const [dbProgress, setDBProgress] = useState(0);
  const [isWebDiagnosing, setWebDiagnosing] = useState(false);
  const [webProgress, setWebProgress] = useState(0);

  const [isDBSummarizing, setDBSummarizing] = useState(false);
  const [dbSummaryProgress, setDBSummaryProgress] = useState(0);
  const [isWebSummarizing, setWebSummarizing] = useState(false);
  const [webSummaryProgress, setWebSummaryProgress] = useState(0);

  const [summaryDBSAI, setSummaryDBSAI] = useState({ show: false, loading: false });
  const [summaryWebAI, setSummaryWebAI] = useState({ show: false, loading: false });
  const [diagnosisDBSAI, setDiagnosisDBSAI] = useState({ show: false, loading: false });
  const [diagnosisWebAI, setDiagnosisWebAI] = useState({ show: false, loading: false });

  const [copiedField, setCopiedField] = useState<string | null>(null);

  const [summarySelectedTab, setSummarySelectedTab] = useState("db");
  const [diagnosisSelectedTab, setDiagnosisSelectedTab] = useState("db");

  const [summaryDBGenerated, setSummaryDBGenerated] = useState(false);
  const [summaryWebGenerated, setSummaryWebGenerated] = useState(false);
  const [diagnosisDBCompleted, setDiagnosisDBCompleted] = useState(false);
  const [diagnosisWebCompleted, setDiagnosisWebCompleted] = useState(false);

  const [summaryCheckedItems, setSummaryCheckedItems] = useState<{ [key: string]: { good: boolean; vulnerable: boolean; interview: boolean; } }>({});
  const [diagnosisCheckedItems, setDiagnosisCheckedItems] = useState<{ [key: string]: { good: boolean; vulnerable: boolean; interview: boolean; } }>({});
  
  const [siteUrl, setSiteUrl] = useState("");
  const [savedSiteUrl, setSavedSiteUrl] = useState("");
  
  const [dbAccount, setDbAccount] = useState("");
  const [savedDbAccount, setSavedDbAccount] = useState("");
  
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState({ title: "", message: "", type: "info" as "info" | "success" | "error" });

  useEffect(() => {
    const fetchChecklistItems = async () => {
      try {
        const response = await fetch("/routers/v2/tech/items");
        if (!response.ok) throw new Error("진단 항목 API 응답 오류");
        const data = await response.json();
        setDbItems(data.db);
        setWebItems(data.web);
      } catch (error) {
        console.error("진단 항목 로딩 실패:", error);
        showModalMessage("초기화 오류", "진단 항목 데이터를 불러오는 데 실패했습니다.", "error");
      }
    };
    fetchChecklistItems();
  }, []);

  const showModalMessage = (title: string, message: string, type: "info" | "success" | "error" = "info") => {
    setModalContent({ title, message, type });
    setShowModal(true);
    setTimeout(() => setShowModal(false), 3000);
  };
  
  const handleDBFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedDBFile(file);
      setSummaryDBGenerated(false);
      setUploadedDBFileId(null);
      setDbSummaryResult([]);
      setSummaryCheckedItems(prev => {
        const next = {...prev};
        Object.keys(next).forEach(key => key.startsWith('db-') && delete next[key]);
        return next;
      });

      const formData = new FormData();
      formData.append("file", file);
      formData.append("option", "db"); 

      try {
        const response = await fetch("/routers/v2/tech/summary/files/upload", { method: "POST", body: formData });
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "서버 응답이 올바르지 않습니다.");
        }
        const result = await response.json();
        setUploadedDBFileId(result.file_id);
        showModalMessage("DB 파일 업로드 성공", `${file.name} 파일이 업로드되었습니다.`, "success");
      } catch (error) {
        console.error("DB 파일 업로드 실패:", error);
        setUploadedDBFile(null);
        showModalMessage("업로드 실패", error instanceof Error ? error.message : "파일 업로드 중 오류가 발생했습니다.", "error");
      }
    }
  };

  const handleWebFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedWebFile(file);
      setSummaryWebGenerated(false);
      setUploadedWebFileId(null);
      setWebSummaryResult([]);
      setSummaryCheckedItems(prev => {
        const nextState = { ...prev };
        Object.keys(nextState).forEach(key => {
          if (key.startsWith('web-')) delete nextState[key];
        });
        return nextState;
      });

      const formData = new FormData();
      formData.append("file", file);
      formData.append("option", "web")

      try {
        const response = await fetch("/routers/v2/tech/summary/files/upload", { method: "POST", body: formData });
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "서버 응답이 올바르지 않습니다.");
        }
        const result = await response.json();
        setUploadedWebFileId(result.file_id);
        showModalMessage("WEB 파일 업로드 성공", `${file.name} 파일이 업로드되었습니다.`, "success");
      } catch (error) {
        console.error("WEB 파일 업로드 실패:", error);
        setUploadedWebFile(null);
        showModalMessage("업로드 실패", error instanceof Error ? error.message : "파일 업로드 중 오류가 발생했습니다.", "error");
      }
    }
  };

  const handleSummary = async () => {
    const isDbTab = summarySelectedTab === "db";
    const fileId = isDbTab ? uploadedDBFileId : uploadedWebFileId;
    
    if (!fileId) {
      showModalMessage("파일 업로드 필요", `${summarySelectedTab.toUpperCase()} 파일을 먼저 업로드해주세요.`, "error");
      return;
    }

    if (isDbTab) {
      setDBSummarizing(true);
      setDBSummaryProgress(20);
    } else {
      setWebSummarizing(true);
      setWebSummaryProgress(20);
    }

    try {
      const formData = new FormData();
      formData.append('file_id', fileId);
      formData.append('domain', isDbTab ? 'DB' : 'WEB');

      const response = await fetch("/routers/v2/tech/summary", { method: "POST", body: formData });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "서버에서 오류가 발생했습니다." }));
        throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
      }
      
      const result: AnalysisResultItem[] = await response.json();

      if (isDbTab) setDBSummaryProgress(70);
      else setWebSummaryProgress(70);
      
      const analysisResultForCheckboxes: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean; } } = {};
      
      result.forEach((backendItem) => {
        const key = `${isDbTab ? 'db' : 'web'}-${backendItem.id}`;
        analysisResultForCheckboxes[key] = {
          good: backendItem.positive,
          vulnerable: backendItem.weakness,
          interview: backendItem.interview,
        };
      });
      
      setSummaryCheckedItems((prev) => ({ ...prev, ...analysisResultForCheckboxes }));

      if (isDbTab) {
        setDbSummaryResult(result);
        setSummaryDBGenerated(true);
        setDBSummaryProgress(100);
      } else {
        setWebSummaryResult(result);
        setSummaryWebGenerated(true);
        setWebSummaryProgress(100);
      }
      showModalMessage(`${summarySelectedTab.toUpperCase()} 요약 완료`, "보고서 분석 및 요약이 완료되었습니다.", "success");
    } catch (error) {
      console.error("요약 처리 중 에러:", error);
      showModalMessage("요약 실패", error instanceof Error ? error.message : "분석 중 오류가 발생했습니다.", "error");
    } finally {
      if (isDbTab) setDBSummarizing(false);
      else setWebSummarizing(false);
    }
  };

  // const handleCopyText = async (text: string, fieldName: string) => {
  //   if (!text || text.trim() === "") {
  //       showModalMessage("복사 오류", "복사할 내용이 없습니다.", "error");
  //       return;
  //   }
  //   setCopiedField(fieldName);
  //   try {
  //       await navigator.clipboard.writeText(text);
  //       showModalMessage("복사 완료", "클립보드에 복사되었습니다.", "success");
  //       setTimeout(() => setCopiedField(null), 2000);
  //   } catch (err) {
  //       showModalMessage("복사 실패", "복사에 실패했습니다.", "error");
  //   }
  // };
  const handleCopyText = async (text: string, fieldName: string,) => {
    if (!text || text.trim() === "") {
      showModalMessage("복사 오류", "복사할 내용이 없습니다.", "error",);
      return;
    }

    // 복사 성공 표시를 먼저 보여줌
    setCopiedField(fieldName);
    
    try { // 가장 단순한 방법부터 시도
      await navigator.clipboard.writeText(text);
      showModalMessage("복사 완료", "복사되었습니다!", "success",
      );
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) { // 폴백: execCommand 사용
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
        
        if (successful) {showModalMessage("복사 완료", "복사되었습니다!", "success",
          );
          setTimeout(() => setCopiedField(null), 2000);
        } else {
          throw new Error('execCommand failed');
        }
      } catch (fallbackErr) {// 복사 실패 시 알림만 표시
        setCopiedField(null);
        showModalMessage("복사 실패", "복사에 실패했습니다. 브라우저가 복사를 지원하지 않습니다.", "error",
        );
      }
    }
  };

  // AI 생성 함수(handleGenerateSummaryAI, handleGenerateDiagnosisAI)를 하나로 통합
  const handleGenerateAI = async (tabType: "db" | "web", sectionType: "summary" | "diagnosis") => {
    const isCompleted = sectionType === 'summary'
        ? (tabType === "db" ? summaryDBGenerated : summaryWebGenerated)
        : (tabType === "db" ? diagnosisDBCompleted : diagnosisWebCompleted);

    if (!isCompleted) {
        const requiredAction = sectionType === 'summary' ? '보고서 요약' : '자동 진단';
        showModalMessage(`${requiredAction} 필요`, `${tabType.toUpperCase()} ${requiredAction}을 먼저 진행해주세요.`, "error");
        return;
    }
    
    // 로딩 상태를 설정하는 setter 함수를 동적으로 결정
    const setState = sectionType === 'summary' 
        ? (tabType === 'db' ? setSummaryDBSAI : setSummaryWebAI) 
        : (tabType === 'db' ? setDiagnosisDBSAI : setDiagnosisWebAI);
    setState({ show: false, loading: true });
    showModalMessage("AI 진단", "생성을 시작합니다...", "info");

    try {
        const ai_res = await fetch("/routers/v2/tech/ai", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tabType }),
        });

        if (!ai_res.ok) throw new Error(`HTTP error! status: ${ai_res.status}`);
        const ai_res_json = await ai_res.json();
        if (!ai_res_json || !ai_res_json.attack || !ai_res_json.yara) {
            throw new Error("AI 응답 데이터가 올바르지 않습니다.");
        }
        
        // 탭별로 결과를 저장하기 위해 키(e.g., 'summary-web')를 생성하고 해당 키에 결과를 저장
        const resultKey = `${sectionType}-${tabType}`;
        setAiResults(prev => ({
            ...prev,
            [resultKey]: {
                threatAnalysis: ai_res_json.attack,
                yaraRule: ai_res_json.yara,
            }
        }));

        setState({ show: true, loading: false });
        showModalMessage("AI 진단 완료", "생성이 완료되었습니다.", "success");
    } catch (error) {
        console.error("AI 진단 생성 중 오류 발생:", error);
        const errorMessage = error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
        setState({ show: false, loading: false });
        showModalMessage("AI 진단 실패", errorMessage, "error");
    }
  };

  // const getSummaryVulnerableItems = (tabType: "db" | "web") => {
  //   const summaryResult = tabType === "db" ? dbSummaryResult : webSummaryResult;
  //   return summaryResult
  //     .filter(item => item.weakness)
  //     .map(item => ({
  //       name: item.name,
  //       countermeasure: item.countermeasure || `${item.name}에 대한 보안 강화 방안 수립이 필요합니다.`,
  //     }));
  // };

  // '취약'/'인터뷰' 모두 'result' 내용 출력
  const getSummaryVulnerableItems = (tabType: "db" | "web") => {
    const vulnerableItems: Array<{ name: string; countermeasure: string; }> = [];
    const items = tabType === "db" ? dbItems : webItems;
    items.forEach((item) => {
      const key = `${tabType}-${item.id}`;
      const itemStatus = summaryCheckedItems[key];

      // '취약' 또는 '인터뷰' 항목을 포함
      if (itemStatus && (itemStatus.vulnerable || itemStatus.interview)) {
        let displayContent = "";
        displayContent = item.result || `${item.name} 항목에 대한 인터뷰가 필요합니다.`;
        vulnerableItems.push({
          name: item.name,
          countermeasure: displayContent, 
        });
      }
    });
    return vulnerableItems;
  };
  
  // const getDiagnosisVulnerableItems = (tabType: "db" | "web") => {
  //   const vulnerableItems: Array<{ name: string; countermeasure: string; }> = [];
  //   const items = tabType === "db" ? dbItems : webItems;
  //   items.forEach((item) => {
  //       const key = `${tabType}-${item.id}`;
  //       const itemStatus = diagnosisCheckedItems[key];
  //       if (itemStatus && (itemStatus.vulnerable || itemStatus.interview)) {
  //           vulnerableItems.push({
  //               name: item.name,
  //               countermeasure: item.countermeasure || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`,
  //           });
  //       }
  //   });
  //   return vulnerableItems;
  // };


// // 취약, 인터뷰 하드 코딩  
//   const getDiagnosisVulnerableItems = (tabType: "db" | "web") => {
//     const vulnerableItems: Array<{ name: string; countermeasure: string; }> = [];
//     const items = tabType === "db" ? dbItems : webItems;
//     items.forEach((item) => {
//         const key = `${tabType}-${item.id}`;
//         const itemStatus = diagnosisCheckedItems[key];

//         // [수정됨] '취약' 또는 '인터뷰' 항목을 모두 포함하도록 되돌림
//         if (itemStatus && (itemStatus.vulnerable || itemStatus.interview)) {
//           
//             let displayContent = "";

//             // [수정됨] 상태에 따라 다른 내용을 할당
//             if (itemStatus.interview) {
//                 // '인터뷰' 상태일 경우, item.interview 내용을 사용
//                 // (item.interview 데이터가 없을 경우를 대비해 기본값 설정)
//                 displayContent = item.interview || `${item.name} 항목에 대한 인터뷰가 필요합니다.`;
//             } else if (itemStatus.vulnerable) {
//                 // '취약' 상태일 경우, item.countermeasure 내용을 사용
//                 displayContent = item.countermeasure || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`;
//             }

//             vulnerableItems.push({
//                 name: item.name,
//                 countermeasure: displayContent, // [수정됨] 위에서 할당된 내용을 출력
//             });
//         }
//     });
//     return vulnerableItems;
//   };

// // 취약항목만
//   const getDiagnosisVulnerableItems = (tabType: "db" | "web") => {
//     const vulnerableItems: Array<{ name: string; countermeasure: string; }> = [];
//     const items = tabType === "db" ? dbItems : webItems;
//     items.forEach((item) => {
//         const key = `${tabType}-${item.id}`;
//         const itemStatus = diagnosisCheckedItems[key];
//        // [수정됨] itemStatus.vulnerable가 true인 경우만 포함하도록 변경
//         if (itemStatus && itemStatus.vulnerable) { 
//             vulnerableItems.push({
//                 name: item.name,
//                 countermeasure: item.countermeasure || `${item.name}에 대한 보안 강화 방안을 수립하고 정기적인 점검을 실시해야 합니다.`,
//             });
//         }
//     });
//     return vulnerableItems;
//   };

// --- '취약'은 'countermeasure', '인터뷰'는 'interview' 내용 출력 ---
const getDiagnosisVulnerableItems = (tabType: "db" | "web") => {
    const vulnerableItems: Array<{ name: string; countermeasure: string; }> = [];
    const items = tabType === "db" ? dbItems : webItems;
    items.forEach((item) => {
      const key = `${tabType}-${item.id}`;
      const itemStatus = diagnosisCheckedItems[key];

      // '취약' 또는 '인터뷰' 항목을 포함
      if (itemStatus && (itemStatus.vulnerable || itemStatus.interview)) {
        let displayContent = "";
        // [V2 로직] 상태에 따라 다른 내용을 할당
        if (itemStatus.interview) {
          // '인터뷰' 상태일 경우, item.interview 내용을 사용
          displayContent = item.interview || `${item.name} 항목에 대한 인터뷰가 필요합니다.`;
        } else if (itemStatus.vulnerable) {
          // '취약' 상태일 경우, item.countermeasure 내용을 사용
          displayContent = item.countermeasure || `${item.name}에 대한 보안 강화 방안이 필요합니다.`;
        }
        vulnerableItems.push({
          name: item.name,
          countermeasure: displayContent, 
        });
      }
    });
    return vulnerableItems;
  };


  const handleSiteInput = async () => {
    const trimmedUrl = siteUrl.trim();
    if (!trimmedUrl) {
      showModalMessage("URL 입력 필요", "사이트 URL을 입력해주세요.", "error");
      return;
    }

    const urlPattern = /^https?:\/\/([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|(\d{1,3}\.){3}\d{1,3})(:\d+)?(\/.*)?$/;
    if (!urlPattern.test(trimmedUrl)) {
        showModalMessage("입력 형식 오류", "형식에 맞게 입력해주세요.", "error");
        return;
    }

    try {
      const response = await fetch("/routers/v2/tech/auto/web/targets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmedUrl }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "사이트 정보 저장에 실패했습니다.");
      }
      
      const result = await response.json();
      console.log("Saved site ID:", result.site_id);

      if (savedSiteUrl && savedSiteUrl !== trimmedUrl) {
        setDiagnosisWebCompleted(false);
        setWebDiagnosing(false);
        setWebProgress(0);
        const resetWebItems: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean } } = {};
        webItems.forEach((item) => {
          const key = `web-${item.id}`;
          resetWebItems[key] = { good: false, vulnerable: false, interview: false };
        });
        setDiagnosisCheckedItems((prev) => ({ ...prev, ...resetWebItems, }));
        setDiagnosisWebAI({ show: false, loading: false });
      }
      setSavedSiteUrl(trimmedUrl);
      showModalMessage("사이트 입력 완료", "사이트가 성공적으로 저장되었습니다.", "success");

    } catch (error) {
      console.error("사이트 저장 실패:", error);
      showModalMessage("입력 실패", error instanceof Error ? error.message : "사이트 정보 저장 중 오류가 발생했습니다.", "error");
    }
  };

  const handleWebDiagnosisReset = () => {
    setSiteUrl("");
    setSavedSiteUrl("");
    setDiagnosisWebCompleted(false);
    setWebDiagnosing(false);
    setWebProgress(0);
    const resetWebItems: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean } } = {};
    webItems.forEach((item) => {
        const key = `web-${item.id}`;
        resetWebItems[key] = { good: false, vulnerable: false, interview: false };
    });
    setDiagnosisCheckedItems((prev) => ({ ...prev, ...resetWebItems, }));
    setDiagnosisWebAI({ show: false, loading: false });
    showModalMessage("사이트 재입력 준비", "사이트 URL을 새로 입력해주세요.", "info");
  };

  // const handleDBDiagnosis = async () => {
  //   if (!savedDbAccount) {
  //       showModalMessage("정보 입력 필요", "DB 정보를 먼저 입력해주세요.", "error");
  //       return;
  //   }
  //   setDBDiagnosing(true);
  //   setDBProgress(15);
  //   showModalMessage("DB 자동 진단", "DB 자동 진단을 시작합니다...", "info");
  //   const steps = [35, 55, 80, 100];
  //   for (const p of steps) {
  //       await new Promise((r) => setTimeout(r, 400));
  //       setDBProgress(p);
  //   }
  //   const analysisResult: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean; } } = {};
  //   setDiagnosisDBCompleted(true);
  //   dbItems.forEach((item) => {
  //       const key = `db-${item.id}`;
  //       analysisResult[key] = { good: false, vulnerable: true, interview: false };
  //   });
  //   setDBDiagnosing(false);
  //   setDiagnosisCheckedItems((prev) => ({ ...prev, ...analysisResult }));
  //   showModalMessage("DB 진단 완료", "DB 진단이 완료되었습니다.", "success");
  // };
  const handleDBDiagnosis = async () => {
    if (!savedDbAccount) {
      showModalMessage("정보 입력 필요", "DB 정보를 먼저 입력해주세요.", "error");
      return;
    }
    setDBDiagnosing(true);
    setDBProgress(15);
    showModalMessage("DB 자동 진단", "DB 자동 진단을 시작합니다...", "info");
    const steps = [35, 55, 80, 100];
    for (const p of steps) {
      await new Promise((r) => setTimeout(r, 400));
      setDBProgress(p);
    }

    // 1. 요청하신 상태를 순서대로 정의한 배열
    const hardcodedStatuses = [
      { good: false, vulnerable: false, interview: true }, // 1. 인터뷰
      { good: false, vulnerable: false, interview: true }, // 2. 인터뷰
      { good: false, vulnerable: true, interview: false }, // 3. 취약
      { good: false, vulnerable: false, interview: true }, // 4. 인터뷰
      { good: false, vulnerable: false, interview: true }, // 5. 취약 -> 인터뷰
      { good: false, vulnerable: false, interview: true }, // 6. 양호 -> 인터뷰
      { good: true, vulnerable: false, interview: false }, // 7. 양호
      { good: true, vulnerable: false, interview: false }, // 8. 양호
      { good: false, vulnerable: false, interview: true }, // 9. 인터뷰
      { good: false, vulnerable: true, interview: false }, // 10. 취약
      { good: false, vulnerable: true, interview: false }, // 11. 취약
      { good: false, vulnerable: false, interview: true }, // 12. 취약 -> 인터뷰
      { good: false, vulnerable: false, interview: true }, // 13. 인터뷰
      { good: false, vulnerable: false, interview: true }, // 14. 인터뷰
      { good: false, vulnerable: false, interview: true }, // 15. 취약 -> 인터뷰
      { good: true, vulnerable: false, interview: false }, // 16. 양호 
      { good: false, vulnerable: true, interview: false }, // 17. 취약 
      { good: false, vulnerable: false, interview: true }, // 18. 취약 -> 인터뷰
      { good: false, vulnerable: false, interview: true }, // 19. 취약 -> 인터뷰
      { good: false, vulnerable: false, interview: true }, // 20. 인터뷰
      { good: false, vulnerable: false, interview: true }, // 21. 인터뷰
      { good: false, vulnerable: true, interview: false }, // 22. 취약
      { good: false, vulnerable: true, interview: false }, // 23. 취약
      { good: false, vulnerable: true, interview: false }  // 24. 취약 -> 인터뷰
    ];

    const analysisResult: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean; } } = {};
    setDiagnosisDBCompleted(true);
    
    // 2. dbItems를 순회하며 위 배열의 상태를 순서대로 적용
    dbItems.forEach((item, index) => {
        const key = `db-${item.id}`;

        if (index < hardcodedStatuses.length) {
            // 24개 항목까지는 정의된 상태를 적용
            analysisResult[key] = hardcodedStatuses[index];
        } else {
            // 25번째 항목부터는 기본값 (예: 인터뷰)으로 처리
            analysisResult[key] = { good: false, vulnerable: false, interview: true };
        }
    });

    // --- [디버깅 로그 추가] ---
    // '진단' 버튼 클릭 시 브라우저 콘솔(F12)에 이 객체의 내용이 출력됩니다.
    console.log("Setting diagnosis items:", analysisResult);
    // -------------------------

    setDBDiagnosing(false);
    setDiagnosisCheckedItems((prev) => ({ ...prev, ...analysisResult }));
    showModalMessage("DB 진단 완료", "DB 진단이 완료되었습니다.", "success");
  };

  const handleDbAccountInput = async () => {
    const trimmedDbAccount = dbAccount.trim();
    if (!trimmedDbAccount) {
        showModalMessage("DB 정보 필요", "DB 연결 정보를 입력해주세요.", "error");
        return;
    }
    
    const connectionStringRegex = /^(?<db_type>\w+):\/\/(?<username>[^:]+):(?<password>[^@]+)@(?<host>[^:/]+):(?<port>\d+)(?:\/(?<database>\w*))?$/;
    const match = trimmedDbAccount.match(connectionStringRegex);

    if (!match || !match.groups) {
        showModalMessage("입력 형식 오류", "형식에 맞게 입력해주세요.", "error");
        return;
    }
    
    const { db_type, username, password, host, port, database } = match.groups;

    const dbCredData = {
      db_type,
      host,
      port: parseInt(port, 10),
      database: database || null,
      username,
      password,
    };

    try {
      const response = await fetch("/routers/v2/tech/auto/db/credentials", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dbCredData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "DB 정보 저장에 실패했습니다.");
      }

      const result = await response.json();
      console.log("Saved credential ID:", result.cred_id);

      if (savedDbAccount && savedDbAccount !== trimmedDbAccount) {
        setDiagnosisDBCompleted(false);
        setDBDiagnosing(false);
        setDBProgress(0);
        const resetDBItems: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean } } = {};
        dbItems.forEach((item) => {
          const key = `db-${item.id}`;
          resetDBItems[key] = { good: false, vulnerable: false, interview: false };
        });
        setDiagnosisCheckedItems((prev) => ({ ...prev, ...resetDBItems, }));
        setDiagnosisDBSAI({ show: false, loading: false });
      }
      setSavedDbAccount(trimmedDbAccount);
      showModalMessage("DB 정보 입력 완료", "DB 정보가 성공적으로 저장되었습니다.", "success");

    } catch (error) {
       console.error("DB 정보 저장 실패:", error);
      showModalMessage("입력 실패", error instanceof Error ? error.message : "DB 정보 저장 중 오류가 발생했습니다.", "error");
    }
  };

  const handleDbDiagnosisReset = () => {
    setDbAccount("");
    setSavedDbAccount("");
    setDiagnosisDBCompleted(false);
    setDBDiagnosing(false);
    setDBProgress(0);
    const resetDBItems: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean } } = {};
    dbItems.forEach((item) => {
        const key = `db-${item.id}`;
        resetDBItems[key] = { good: false, vulnerable: false, interview: false };
    });
    setDiagnosisCheckedItems((prev) => ({ ...prev, ...resetDBItems }));
    setDiagnosisDBSAI({ show: false, loading: false });
    showModalMessage("DB 정보 재입력 준비", "DB 정보를 새로 입력해주세요.", "info");
  };
  
  const handleWebDiagnosis = async () => {
    if (!savedSiteUrl) {
      showModalMessage("URL 입력 필요", "사이트 URL을 먼저 입력해주세요.", "error");
      return;
    }
    setWebDiagnosing(true);
    setWebProgress(15);
    showModalMessage("WEB 자동 진단", "WEB 자동 진단을 시작합니다...", "info");
    
    try {
	const response = await fetch("/api/v2/scan", {
	    method: "POST",
	    headers: { "Content-Type": "application/json" },
	    body: JSON.stringify({ url: savedSiteUrl }),
	});

	setWebProgress(80);

	if (!response.ok) {
	    const errorData = await response.json().catch(() => ({ detail: "서버 응답이 올바르지 않습니다." }));
	    throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
	}

	const backendResult: { status: string; message: string; report_summary: { [key: string]: { status: string; description: string; details: any[] } } } = await response.json();

	console.log("백엔드 응답 전체:", backendResult);
	console.log("report_summary:", backendResult.report_summary)

	if (backendResult.status === 'error') {
	    throw new Error(backendResult.message);
	}

	const analysisResultForCheckboxes: { [key: string]: { good: boolean; vulnerable: boolean; interview: boolean; } } = {};

	webItems.forEach((item) => {
	    const key = `web-${item.id}`;
	    const matchingKey = Object.keys(backendResult.report_summary).find(k => k.includes(item.name)
	    );

	    if (matchingKey) {
		const testResult = backendResult.report_summary[matchingKey];
		const status = testResult.status;
		analysisResultForCheckboxes[key] = {
		    good: status === '양호',
                    vulnerable: status === '취약',
                    interview: status === '인터뷰',
		};
            } else {
		analysisResultForCheckboxes[key] = { good: false, vulnerable: false, interview: true };
            }
        });

        setDiagnosisWebCompleted(true);
        setDiagnosisCheckedItems((prev) => ({ ...prev, ...analysisResultForCheckboxes }));
        setWebProgress(100);
        showModalMessage("WEB 진단 완료", "WEB 진단이 완료되었습니다.", "success");

    } catch (error) {
        // 오류 처리
        console.error("WEB 진단 실패:", error);
        setWebProgress(0); // 오류 시 진행률 초기화
        showModalMessage("WEB 진단 실패", error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.", "error");

    } finally {
        setWebDiagnosing(false);
    }
  };
  
  // AIComponent가 탭별로 독립적인 데이터를 표시하도록 threatAnalysis와 yaraRule을 props로 직접 전달받도록 수정
  const AIComponent = ({
    aiState,
    tabType,
    sectionType,
    threatAnalysis,
    yaraRule,
  }: {
    aiState: { show: boolean; loading: boolean };
    tabType: "db" | "web";
    sectionType: "summary" | "diagnosis";
    threatAnalysis: string;
    yaraRule: string;
  }) => {
    return (
      <div className="border-t pt-4 flex-shrink-0 mt-4">
        <div className="flex items-center justify-between mb-4">
          <h3>AI 추가 진단</h3>
          <Button
            variant="outline"
            size="sm"
            // 통합된 handleGenerateAI 함수를 호출
            onClick={() => handleGenerateAI(tabType, sectionType)}
            disabled={aiState.loading}
            className="gap-2"
          >
            {aiState.loading && <Loader2 className="h-3 w-3 animate-spin" />}
            {aiState.loading ? "생성 중..." : "생성"}
          </Button>
        </div>
        <div className="grid grid-cols-1 gap-4">
          <div className="space-y-3">
            <h4>1. 추가 위협 예측</h4>
            <div className="border rounded-md p-3 bg-muted/30 text-sm min-h-[80px] flex items-center justify-center">
              {aiState.loading ? (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" /> 로딩중...
                </div>
              ) : aiState.show ? (
                // Props로 전달받은 threatAnalysis를 렌더링
                <div className="text-left w-full prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown
                    children={threatAnalysis}
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeSanitize]}
                  />
                </div>
              ) : (
                // Props로 전달받은 threatAnalysis를 렌더링
                <div className="text-muted-foreground">{threatAnalysis}</div>
              )}
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4>2. 추가 위협에 대한 YARA Rule 생성</h4>
              {aiState.show && (
                <Button
                  variant="ghost"
                  size="sm"
                  // Props로 전달받은 yaraRule을 복사
                  onClick={() => handleCopyText(yaraRule, `${sectionType}-${tabType}-yaraRule`)}
                  className="gap-1 h-8 px-2"
                >
                  {copiedField === `${sectionType}-${tabType}-yaraRule` ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                  복사
                </Button>
              )}
            </div>
             {/* YARA Rule 결과란에 세로/가로 스크롤을 적용 */}
             {/* max-h-[200px]로 최대 높이를 제한하고, overflow-auto로 내용이 넘칠 경우 스크롤을 생성 */}
             {/* flex, items-center, justify-center 클래스를 제거하여 내용이 좌측 상단부터 표시 */}
            <div className="border rounded-md bg-muted/30 text-sm min-h-[80px] max-h-[200px] overflow-auto">
                {aiState.loading ? (
                    <div className="flex items-center justify-center w-full h-full min-h-[64px] gap-2 text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    로딩중...
                    </div>
                ) : aiState.show ? (
                    <div className="p-3 text-left w-full prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                        children={yaraRule}
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeSanitize]}
                    />
                    </div>
                ) : (
                    <div className="flex items-center justify-center w-full h-full min-h-[64px] p-3 text-muted-foreground">
                    {yaraRule}
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
        <CardHeader><CardTitle>기술 컨설팅</CardTitle></CardHeader>
        <CardContent className="flex-1 flex flex-col">
          <Tabs defaultValue="summary" className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="summary" className="flex items-center gap-2">
                보고서 요약
                <TooltipProvider><Tooltip>
                  <TooltipTrigger asChild><span role="button" tabIndex={0} className="p-0 h-auto bg-transparent border-0 cursor-help" aria-label="정보 아이콘"><Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" /></span></TooltipTrigger>
                  <TooltipContent side="top"><p className="max-w-xs">요약이 필요한 진단 결과 보고서를 업로드하면 각 진단 항목의 취약 여부를 체크하고, 취약 항목과 대응 방안을 요약합니다.</p></TooltipContent>
                </Tooltip></TooltipProvider>
              </TabsTrigger>
              <TabsTrigger value="auto" className="flex items-center gap-2">
                자동 진단
                <TooltipProvider><Tooltip>
                  <TooltipTrigger asChild><span role="button" tabIndex={0} className="p-0 h-auto bg-transparent border-0 cursor-help" aria-label="정보 아이콘"><Info className="h-4 w-4 text-muted-foreground hover:text-foreground transition-colors" /></span></TooltipTrigger>
                  <TooltipContent side="top"><p className="max-w-xs">진단 옵션(DB/WEB)을 선택한 후, 진단이 필요한 DB 정보/사이트의 URL을 입력하면 각 항목의 취약 여부를 자동으로 진단하고, 취약 항목과 대응 방안을 요약합니다.</p></TooltipContent>
                </Tooltip></TooltipProvider>
              </TabsTrigger>
            </TabsList>
{/*요약*/}
            <TabsContent value="summary" className="flex-1 flex flex-col">
              <Tabs value={summarySelectedTab} onValueChange={setSummarySelectedTab} className="flex-1 flex flex-col">
                <TabsList className="w-full grid grid-cols-2">
                  <TabsTrigger value="db">DB</TabsTrigger>
                  <TabsTrigger value="web">WEB</TabsTrigger>
                </TabsList>
{/*summary-db tab*/}
                <TabsContent value="db" className="flex-1 flex flex-col">
                  <div className="min-h-[80px]">
                    <div className="flex gap-2 items-center justify-between">
                      <div className="flex-1 pl-3">
                        {uploadedDBFile ? (<p className="text-sm text-muted-foreground">[업로드된 DB 파일]  {uploadedDBFile.name}</p>) 
                        : (<p className="text-sm text-muted-foreground">DB 보고서 파일을 업로드하세요.</p>)}
                      </div>
                      <div className="flex gap-2 items-center">
                        <Button className="bg-black text-white hover:bg-gray-800 gap-2" asChild>
                          <label>{uploadedDBFile ? "보고서 재업로드" : "보고서 업로드"}<input type="file" accept=".xlsx,.xls" onChange={handleDBFileUpload} className="hidden" /></label>
                        </Button>
                        <Button onClick={handleSummary} disabled={isDBSummarizing || !uploadedDBFile} className="gap-2">
                          {isDBSummarizing && <Loader2 className="h-4 w-4 animate-spin" />}
                          {isDBSummarizing ? "요약 중..." : "요약"}
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1 min-h-0">
                    <ScrollArea className="h-[400px]">
                      <div className="space-y-1">
                        <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted sticky top-0">
                          <div>항목</div><div className="text-center">양호</div><div className="text-center">취약</div><div className="text-center">인터뷰</div>
                        </div>
                        {dbItems.map((item) => {
                          const key = `db-${item.id}`;
                          const itemStatus = summaryCheckedItems[key] || { good: false, vulnerable: false, interview: false };
                          return (
                            <div key={item.id} className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                              <div className="text-sm">{item.name}</div>
                              <div className="flex justify-center"><Checkbox checked={summaryDBGenerated && itemStatus.good} disabled={!summaryDBGenerated} /></div>
                              <div className="flex justify-center"><Checkbox checked={summaryDBGenerated && itemStatus.vulnerable} disabled={!summaryDBGenerated} /></div>
                              <div className="flex justify-center"><Checkbox checked={summaryDBGenerated && itemStatus.interview} disabled={!summaryDBGenerated} /></div>
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>
                  {summaryDBGenerated && (<div className="border-t pt-4 mt-4">
                    <h3 className="mb-3">인터뷰 및 취약 항목 ({getSummaryVulnerableItems("db").length}개)</h3>
                    <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                      <div className="grid grid-cols-2 gap-0 bg-muted flex-shrink-0 sticky top-0 divide-x border-b pr-[17px]">
                            <div className="p-3 font-medium">항목</div>
                            <div className="p-3 font-medium">인터뷰/대응 방안</div>
                        </div>
                      <div className="flex-1 overflow-y-auto min-h-[200px]">
                        {getSummaryVulnerableItems("db").length > 0 ? (getSummaryVulnerableItems("db").map((item, index) => (
                          <div key={index} className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"} divide-x border-b`}>
                            <div className="p-3 text-sm">{item.name}</div>
                            <div className="p-3 text-sm whitespace-pre-wrap">{item.countermeasure}</div>
                          </div>
                        ))) : (<div className="p-8 text-center text-muted-foreground">취약 항목이 발견되지 않았습니다.</div>)}
                      </div>
                    </div>
                  </div>)}
                  {/* AIComponent에 탭에 맞는 AI 결과(threatAnalysis, yaraRule)를 props로 전달 */}
                  {(() => {
                    const aiResult = aiResults['summary-db'] || { threatAnalysis: "생성 버튼을 눌러주세요.", yaraRule: "생성 버튼을 눌러주세요." };
                    return (
                      <AIComponent
                        aiState={summaryDBSAI}
                        tabType="db"
                        sectionType="summary"
                        threatAnalysis={aiResult.threatAnalysis}
                        yaraRule={aiResult.yaraRule}
                      />
                    );
                  })()}
                </TabsContent>
{/*summary-web tab*/}
                <TabsContent value="web" className="flex-1 flex flex-col">
                  <div className="min-h-[80px]">
                    <div className="flex gap-2 items-center justify-between">
                      <div className="flex-1 pl-3">
                        {uploadedWebFile ? (<p className="text-sm text-muted-foreground">[업로드된 WEB 파일]  {uploadedWebFile.name}</p>) 
                        : (<p className="text-sm text-muted-foreground">WEB 보고서 파일을 업로드하세요.</p>)}
                      </div>
                      <div className="flex gap-2 items-center">
                        <Button className="bg-black text-white hover:bg-gray-800 gap-2" asChild>
                          <label>{uploadedWebFile ? "보고서 재업로드" : "보고서 업로드"}<input type="file" accept=".xlsx,.xls" onChange={handleWebFileUpload} className="hidden" /></label>
                        </Button>
                        <Button onClick={handleSummary} disabled={isWebSummarizing || !uploadedWebFile} className="gap-2">
                          {isWebSummarizing && <Loader2 className="h-4 w-4 animate-spin" />}{isWebSummarizing ? "요약 중..." : "요약"}
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1 min-h-0">
                    <ScrollArea className="h-[400px]">
                      <div className="space-y-1">
                        <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted sticky top-0">
                          <div>항목</div><div className="text-center">양호</div><div className="text-center">취약</div><div className="text-center">인터뷰</div>
                        </div>
                        {webItems.map((item) => {
                          const key = `web-${item.id}`;
                          const itemStatus = summaryCheckedItems[key] || { good: false, vulnerable: false, interview: false };
                          return (
                            <div key={item.id} className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                              <div className="text-sm">{item.name}</div>
                              <div className="flex justify-center"><Checkbox checked={summaryWebGenerated && itemStatus.good} disabled={!summaryWebGenerated} /></div>
                              <div className="flex justify-center"><Checkbox checked={summaryWebGenerated && itemStatus.vulnerable} disabled={!summaryWebGenerated} /></div>
                              <div className="flex justify-center"><Checkbox checked={summaryWebGenerated && itemStatus.interview} disabled={!summaryWebGenerated} /></div>
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>
                  {summaryWebGenerated && (<div className="border-t pt-4 mt-4">
                    <h3 className="mb-3">인터뷰 및 취약 항목 ({getSummaryVulnerableItems("web").length}개)</h3>
                    <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                      <div className="grid grid-cols-2 gap-0 bg-muted flex-shrink-0 sticky top-0 divide-x border-b pr-[17px]">
                            <div className="p-3 font-medium">항목</div>
                            <div className="p-3 font-medium">인터뷰/대응 방안</div>
                        </div>
                      <div className="flex-1 overflow-y-auto min-h-[200px]">
                        {getSummaryVulnerableItems("web").length > 0 ? (getSummaryVulnerableItems("web").map((item, index) => (
                          <div key={index} className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"} divide-x border-b`}>
                            <div className="p-3 text-sm">{item.name}</div>
                            <div className="p-3 text-sm whitespace-pre-wrap">{item.countermeasure}</div>
                          </div>
                        ))) : (<div className="p-8 text-center text-muted-foreground">취약 항목이 발견되지 않았습니다.</div>)}
                      </div>
                    </div>
                  </div>)}
                  {/* AIComponent에 탭에 맞는 AI 결과(threatAnalysis, yaraRule)를 props로 전달*/}
                  {(() => {
                    const aiResult = aiResults['summary-web'] || { threatAnalysis: "생성 버튼을 눌러주세요.", yaraRule: "생성 버튼을 눌러주세요." };
                    return (
                      <AIComponent
                        aiState={summaryWebAI}
                        tabType="web"
                        sectionType="summary"
                        threatAnalysis={aiResult.threatAnalysis}
                        yaraRule={aiResult.yaraRule}
                      />
                    );
                  })()}
                </TabsContent>
              </Tabs>
            </TabsContent>

{/*auto-analysis*/}
            <TabsContent value="auto" className="flex-1 flex flex-col">
              <Tabs value={diagnosisSelectedTab} onValueChange={setDiagnosisSelectedTab} className="flex-1 flex flex-col">
                <TabsList className="w-full grid grid-cols-2">
                  <TabsTrigger value="db">DB</TabsTrigger>
                  <TabsTrigger value="web">WEB</TabsTrigger>
                </TabsList>
{/*auto-analysis-db tab*/}
                <TabsContent value="db" className="flex-1 flex flex-col">
                  <div className="min-h-[80px]">
                    <div className="flex gap-2 items-center justify-between">
                      <Input placeholder="DB 정보를 입력하세요. (db_type://user:password@host:port/database)" value={dbAccount} onChange={(e) => setDbAccount(e.target.value)} className="flex-1" />
                      <Button onClick={savedDbAccount ? handleDbDiagnosisReset : handleDbAccountInput} disabled={isDBDiagnosing}>{savedDbAccount ? "DB 정보 재입력" : "DB 정보 입력"}</Button>
                      <Button onClick={handleDBDiagnosis} disabled={isDBDiagnosing || !savedDbAccount} className="gap-2">
                        {isDBDiagnosing && <Loader2 className="h-4 w-4 animate-spin" />}{isDBDiagnosing ? "진단 중..." : "진단"}
                      </Button>
                    </div>
                    {savedDbAccount && (<p className="text-sm text-muted-foreground pl-3">[입력된 DB 정보]  {savedDbAccount}</p>)}
                  </div>
                  {isDBDiagnosing && (<div className="space-y-2"><p className="text-sm text-muted-foreground">DB 진단 중…</p><Progress value={dbProgress} /></div>)}
                  <div className="flex-1 min-h-0 mt-2">
                    <ScrollArea className="h-[400px]">
                      <div className="space-y-1">
                        <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted sticky top-0">
                          <div>항목</div><div className="text-center">양호</div><div className="text-center">취약</div><div className="text-center">인터뷰</div>
                        </div>
                        {dbItems.map((item) => {
                          const key = `db-${item.id}`;
                          const itemStatus = diagnosisCheckedItems[key] || { good: false, vulnerable: false, interview: false };
                          return (
                            <div key={item.id} className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                              <div className="text-sm">{item.name}</div>
                              <div className="flex justify-center"><Checkbox checked={diagnosisDBCompleted && itemStatus.good} disabled={!diagnosisDBCompleted} /></div>
                              <div className="flex justify-center"><Checkbox checked={diagnosisDBCompleted && itemStatus.vulnerable} disabled={!diagnosisDBCompleted} /></div>
                              <div className="flex justify-center"><Checkbox checked={diagnosisDBCompleted && itemStatus.interview} disabled={!diagnosisDBCompleted} /></div>
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>
                  {diagnosisDBCompleted && (<div className="border-t pt-4 mt-4">
                    <h3 className="mb-3">인터뷰 및 취약 항목 ({getDiagnosisVulnerableItems("db").length}개)</h3>
                    <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                      <div className="grid grid-cols-2 gap-0 bg-muted flex-shrink-0 sticky top-0 divide-x border-b pr-[17px]">
                            <div className="p-3 font-medium">항목</div>
                            <div className="p-3 font-medium">인터뷰/대응 방안</div>
                        </div>
                      <div className="flex-1 overflow-y-auto min-h-[200px]">
                        {getDiagnosisVulnerableItems("db").length > 0 ? (getDiagnosisVulnerableItems("db").map((item, index) => (
                          <div key={index} className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"} divide-x border-b`}>
                            <div className="p-3 text-sm">{item.name}</div>
                            <div className="p-3 text-sm whitespace-pre-wrap">{item.countermeasure}</div>
                          </div>
                        ))) : (<div className="p-8 text-center text-muted-foreground">취약 항목이 발견되지 않았습니다.</div>)}
                      </div>
                    </div>
                  </div>)}
                  {/* AIComponent에 탭에 맞는 AI 결과(threatAnalysis, yaraRule)를 props로 전달 */}
                  {(() => {
                    const aiResult = aiResults['diagnosis-db'] || { threatAnalysis: "생성 버튼을 눌러주세요.", yaraRule: "생성 버튼을 눌러주세요." };
                    return (
                      <AIComponent
                        aiState={diagnosisDBSAI}
                        tabType="db"
                        sectionType="diagnosis"
                        threatAnalysis={aiResult.threatAnalysis}
                        yaraRule={aiResult.yaraRule}
                      />
                    );
                  })()}
                </TabsContent>
{/*auto-analysis-web tab*/}
                <TabsContent value="web" className="flex-1 flex flex-col">
                  <div className="min-h-[80px]">
                    <div className="flex gap-2 items-center justify-between">
                      <Input placeholder="사이트 URL을 입력하세요. (https://example.com)" value={siteUrl} onChange={(e) => setSiteUrl(e.target.value)} className="flex-1" />
                      <Button onClick={savedSiteUrl ? handleWebDiagnosisReset : handleSiteInput} disabled={isWebDiagnosing}>{savedSiteUrl ? "사이트 재입력" : "사이트 입력"}</Button>
                      <Button onClick={handleWebDiagnosis} disabled={isWebDiagnosing || !savedSiteUrl} className="gap-2">
                        {isWebDiagnosing && <Loader2 className="h-4 w-4 animate-spin" />}{isWebDiagnosing ? "진단 중..." : "진단"}
                      </Button>
                    </div>
                    {savedSiteUrl && (<p className="text-sm text-muted-foreground pl-3">[입력된 사이트]  {savedSiteUrl}</p>)}
                  </div>
                  {isWebDiagnosing && (<div className="space-y-2"><p className="text-sm text-muted-foreground">WEB 진단 중…</p><Progress value={webProgress} /></div>)}
                  <div className="flex-1 min-h-0 mt-2">
                    <ScrollArea className="h-[400px]">
                      <div className="space-y-1">
                        <div className="grid grid-cols-4 gap-2 p-2 border-b font-medium bg-muted sticky top-0">
                          <div>항목</div><div className="text-center">양호</div><div className="text-center">취약</div><div className="text-center">인터뷰</div>
                        </div>
                        {webItems.map((item) => {
                          const key = `web-${item.id}`;
                          const itemStatus = diagnosisCheckedItems[key] || { good: false, vulnerable: false, interview: false };
                          return (
                            <div key={item.id} className="grid grid-cols-4 gap-2 p-2 border-b hover:bg-muted/50">
                              <div className="text-sm">{item.name}</div>
                              <div className="flex justify-center"><Checkbox checked={diagnosisWebCompleted && itemStatus.good} disabled={!diagnosisWebCompleted} /></div>
                              <div className="flex justify-center"><Checkbox checked={diagnosisWebCompleted && itemStatus.vulnerable} disabled={!diagnosisWebCompleted} /></div>
                              <div className="flex justify-center"><Checkbox checked={diagnosisWebCompleted && itemStatus.interview} disabled={!diagnosisWebCompleted} /></div>
                            </div>
                          );
                        })}
                      </div>
                    </ScrollArea>
                  </div>
                  {diagnosisWebCompleted && (<div className="border-t pt-4 mt-4">
                    <h3 className="mb-3">인터뷰 및 취약 항목 ({getDiagnosisVulnerableItems("web").length}개)</h3>
                    <div className="border rounded-lg overflow-hidden max-h-[500px] flex flex-col">
                      <div className="grid grid-cols-2 gap-0 bg-muted flex-shrink-0 sticky top-0 divide-x border-b pr-[17px]">
                            <div className="p-3 font-medium">항목</div>
                            <div className="p-3 font-medium">인터뷰/대응 방안</div>
                        </div>
                      <div className="flex-1 overflow-y-auto min-h-[200px]">
                        {getDiagnosisVulnerableItems("web").length > 0 ? (getDiagnosisVulnerableItems("web").map((item, index) => (
                          <div key={index} className={`grid grid-cols-2 gap-0 ${index % 2 === 0 ? "bg-white" : "bg-muted/20"} divide-x border-b`}>
                            <div className="p-3 text-sm">{item.name}</div>
                            <div className="p-3 text-sm whitespace-pre-wrap">{item.countermeasure}</div>
                          </div>
                        ))) : (<div className="p-8 text-center text-muted-foreground">취약 항목이 발견되지 않았습니다.</div>)}
                      </div>
                    </div>
                  </div>)}
                  {/* AIComponent에 탭에 맞는 AI 결과(threatAnalysis, yaraRule)를 props로 전달 */}
                  {(() => {
                    const aiResult = aiResults['diagnosis-web'] || { threatAnalysis: "생성 버튼을 눌러주세요.", yaraRule: "생성 버튼을 눌러주세요." };
                    return (
                      <AIComponent
                        aiState={diagnosisWebAI}
                        tabType="web"
                        sectionType="diagnosis"
                        threatAnalysis={aiResult.threatAnalysis}
                        yaraRule={aiResult.yaraRule}
                      />
                    );
                  })()}
                </TabsContent>
              </Tabs>
            </TabsContent>
          </Tabs>
        </CardContent>
{/*-----------------------*/}
      </Card>
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowModal(false)} />
          <Card className="relative w-80 shadow-lg border-2 animate-in fade-in-0 zoom-in-95 duration-300">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {modalContent.type === "success" && (<CheckCircle className="h-5 w-5 text-green-500" />)}
                  {modalContent.type === "error" && (<AlertCircle className="h-5 w-5 text-red-500" />)}
                  {modalContent.type === "info" && (<AlertCircle className="h-5 w-5 text-blue-500" />)}
                  <CardTitle className="text-base">{modalContent.title}</CardTitle>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setShowModal(false)} className="h-6 w-6 p-0"><X className="h-4 w-4" /></Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                <div><div className="font-medium">{modalContent.message}</div></div>
                <div className="pt-2 border-t"><div className="text-xs text-muted-foreground flex items-center gap-1"><Clock className="h-3 w-3" /> 방금 전</div></div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}
